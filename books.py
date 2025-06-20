import os
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
import ollama
from sentence_transformers import SentenceTransformer
from config import *
from connector import run_query
import queries
import PyPDF2

pytesseract.pytesseract.tesseract_cmd = tess_path

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "rubert-tiny2")

if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH, exist_ok=True)
    SentenceTransformer("cointegrated/rubert-tiny2").save(MODEL_PATH)

transformer = SentenceTransformer(MODEL_PATH)

def get_embedding(text: str):
    return transformer.encode(text).tolist()

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([[0,0],[maxWidth-1,0],[maxWidth-1,maxHeight-1],[0,maxHeight-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def find_page_contour(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    page_contour = None
    max_area = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 10000:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4 and area > max_area:
                page_contour = approx
                max_area = area
    return page_contour


def find_vertical_split_line(warped):
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=warped.shape[0]*0.5, maxLineGap=20)
    if lines is None:
        return None
    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        if 85 < angle < 95:  # почти вертикальная линия
            vertical_lines.append(line[0])
    if not vertical_lines:
        return None
    # Ищем линию максимально близкую к центру по X
    img_center = warped.shape[1] // 2
    vertical_lines.sort(key=lambda l: abs((l[0] + l[2])//2 - img_center))
    best_line = vertical_lines[0]
    x_split = (best_line[0] + best_line[2]) // 2
    return x_split


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def extract_text_from_scanned_pages(pdf_path):
    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    results = []
    for i, pil_img in enumerate(images, 1):
        img = np.array(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        page_contour = find_page_contour(img)
        if page_contour is None:
            pages_to_ocr = [img]
        else:
            warped = four_point_transform(img, page_contour.reshape(4, 2))
            split_x = find_vertical_split_line(warped)
            if split_x is None or split_x < 50 or split_x > warped.shape[1] - 50:
                # Нет разделительной линии или слишком близко к краям — одна страница
                pages_to_ocr = [warped]
            else:
                margin = 10
                left_img = warped[:, :max(split_x - margin, 0)]
                right_img = warped[:, min(split_x + margin, warped.shape[1]):]
                if left_img.shape[1] < 50 or right_img.shape[1] < 50:
                    pages_to_ocr = [warped]  # На случай очень узких частей — считаем одной страницей
                else:
                    pages_to_ocr = [left_img, right_img]

        for j, page_img in enumerate(pages_to_ocr, 1):
            processed_img = preprocess_image(cv2.cvtColor(page_img, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(processed_img, lang="eng+rus+math", config="--oem 3")
            response = ollama.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': parser_instructions},
                    {'role': 'user', 'content': text},
                ],
                options={'temperature': 0}
            )
            results.append(response['message']['content'])
    return results


def parse_pages(pdf_path):
    file_obj = open(pdf_path, 'rb')
    pdfReader = PyPDF2.PdfReader(file_obj)

    text = []
    for page in pdfReader.pages:
        item = page.extract_text()
        item = item.replace('\n', '')
        text.append(item)

    file_obj.close()
    return text


def chunk_text(text, max_tokens=128):
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    from nltk.tokenize import sent_tokenize
    texts_split = []
    for page in text:
        sentences = sent_tokenize(page)
        chunks = []
        current_chunk = ""
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = len(sentence.split())  # простая оценка
            if current_tokens + sentence_tokens > max_tokens:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens

        if current_chunk:
            chunks.append(current_chunk.strip())
        texts_split.append(chunks)
    return texts_split


def insert_processes(texts_split, name):
    run_query(queries.insert_lit, {'name': name})
    for i in range(len(texts_split)):
        for chunk in texts_split[i]:
            embedding = get_embedding(chunk)
            run_query(queries.insert_lit_content, {'name': name, 'page_number': i+1, 'text': chunk, 'embedding': embedding})


def parse_text_LLM_check(pdf_path):
    text = extract_text_from_scanned_pages(pdf_path)
    texts_split = chunk_text(text)
    name = os.path.basename(pdf_path)
    insert_processes(texts_split, name)


def parse_text(pdf_path):
    text = parse_pages(pdf_path)
    texts_split = chunk_text(text)
    name = os.path.basename(pdf_path)
    insert_processes(texts_split, name)
