insert_session = """
INSERT INTO sessions (user_id, session_uuid, mode_id)
VALUES
    (:user_id, :uuid, :mode_id)
"""

insert_message = """
INSERT INTO messages(
    session_id, role, message_text)
    VALUES (
        (SELECT session_id
        FROM sessions
        WHERE session_uuid = :uuid),
        :role,
        :message)
"""

insert_lit = """
INSERT INTO literature (
    name)
    VALUES ( 
        :name)
"""

insert_lit_content = """
INSERT INTO literature_contents (
    literature_id, page_number, text, embedding)
    VALUES (
        (SELECT id
        FROM literature
        WHERE name = :name), 
        :page_number, 
        :text, 
        :embedding)
"""

select_lit_id = """
SELECT lc.id, text
FROM literature_contents lc
left join literature l on l.id = lc.literature_id
"""

update_embedding = """
UPDATE literature_contents
SET embedding = :embedding
WHERE id = :id;
"""

select_sources = """
SELECT l.name,
       lc.text
FROM literature_contents lc
LEFT JOIN literature l ON l.id = lc.literature_id
WHERE (lc.embedding <=> :emb) < 0.42 -- фильтрация по косинусному расстоянию
ORDER BY lc.embedding <=> :emb
"""