-- Удаление базы, если она уже существует
DROP DATABASE IF EXISTS "Assistant_db";

-- Создание новой базы
CREATE DATABASE "Assistant_db" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'ru';

-- Подключение к базе
\connect "Assistant_db"

-- Создание расширения
CREATE EXTENSION IF NOT EXISTS vector;

-- Настройки сессии
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Создание схемы
CREATE SCHEMA public;
ALTER SCHEMA public OWNER TO pg_database_owner;
COMMENT ON SCHEMA public IS 'standard public schema';

-- Таблицы и последовательности
CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE SEQUENCE public.users_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
ALTER TABLE public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE public.users ADD CONSTRAINT users_username_key UNIQUE (username);

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    role_name character varying(10) NOT NULL,
    role_desc character varying(50) DEFAULT ''::character varying NOT NULL
);
CREATE SEQUENCE public.roles_role_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;
ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);
ALTER TABLE public.roles ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);

CREATE TABLE public.modes (
    mode_id integer NOT NULL,
    name character varying(50) NOT NULL
);
CREATE SEQUENCE public.modes_mode_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.modes_mode_id_seq OWNED BY public.modes.mode_id;
ALTER TABLE ONLY public.modes ALTER COLUMN mode_id SET DEFAULT nextval('public.modes_mode_id_seq'::regclass);
ALTER TABLE public.modes ADD CONSTRAINT modes_pkey PRIMARY KEY (mode_id);

CREATE TABLE public.sessions (
    user_id integer,
    session_id integer NOT NULL,
    session_uuid character varying(50) NOT NULL,
    mode_id integer,
    date_start timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
CREATE SEQUENCE public.sessions_session_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.sessions_session_id_seq OWNED BY public.sessions.session_id;
ALTER TABLE ONLY public.sessions ALTER COLUMN session_id SET DEFAULT nextval('public.sessions_session_id_seq'::regclass);
ALTER TABLE public.sessions ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);
ALTER TABLE public.sessions ADD CONSTRAINT sessions_session_uuid_key UNIQUE (session_uuid);

CREATE TABLE public.messages (
    message_id integer NOT NULL,
    session_id integer,
    role integer,
    date_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    message_text text NOT NULL
);
CREATE SEQUENCE public.messages_message_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.messages_message_id_seq OWNED BY public.messages.message_id;
ALTER TABLE ONLY public.messages ALTER COLUMN message_id SET DEFAULT nextval('public.messages_message_id_seq'::regclass);
ALTER TABLE public.messages ADD CONSTRAINT messages_pkey PRIMARY KEY (message_id);

CREATE TABLE public.literature (
    id integer NOT NULL,
    name character varying,
    checked boolean DEFAULT false
);
COMMENT ON COLUMN public.literature.name IS 'Название источника';
CREATE SEQUENCE public.literature_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.literature_id_seq OWNED BY public.literature.id;
ALTER TABLE ONLY public.literature ALTER COLUMN id SET DEFAULT nextval('public.literature_id_seq'::regclass);
ALTER TABLE public.literature ADD CONSTRAINT literature_pkey PRIMARY KEY (id);

CREATE TABLE public.literature_contents (
    id integer NOT NULL,
    literature_id integer,
    page_number integer,
    text text,
    embedding public.vector(312)
);
COMMENT ON COLUMN public.literature_contents.text IS 'Текст страницы или фрагмента';
CREATE SEQUENCE public.literature_contents_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER SEQUENCE public.literature_contents_id_seq OWNED BY public.literature_contents.id;
ALTER TABLE ONLY public.literature_contents ALTER COLUMN id SET DEFAULT nextval('public.literature_contents_id_seq'::regclass);
ALTER TABLE public.literature_contents ADD CONSTRAINT literature_contents_pkey PRIMARY KEY (id);
CREATE INDEX literature_contents_literature_id_idx ON public.literature_contents USING btree (literature_id);

-- Связи
ALTER TABLE public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
ALTER TABLE public.sessions
    ADD CONSTRAINT sessions_mode_id_fkey FOREIGN KEY (mode_id) REFERENCES public.modes(mode_id);
ALTER TABLE public.messages
    ADD CONSTRAINT messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id);
ALTER TABLE public.messages
    ADD CONSTRAINT messages_role_fkey FOREIGN KEY (role) REFERENCES public.roles(role_id);
ALTER TABLE public.literature_contents
    ADD CONSTRAINT literature_contents_literature_id_fkey FOREIGN KEY (literature_id) REFERENCES public.literature(id) ON DELETE CASCADE;

-- Начальные данные
INSERT INTO users (username, password_hash)
    VALUES ('admin', 'admin');

INSERT INTO roles (role_name, role_desc)
    VALUES ('user', 'Пользователь'),
           ('bot', 'Ассистент');

INSERT INTO modes (name)
    VALUES ('Gemma2'),
           ('RAG');
