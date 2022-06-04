--
-- PostgreSQL database dump
--

-- Dumped from database version 10.21
-- Dumped by pg_dump version 10.21

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: category_id; Type: TYPE; Schema: public; Owner: sbis
--

CREATE TYPE public.category_id AS ENUM (
    'office',
    'department',
    'staff'
);


ALTER TYPE public.category_id OWNER TO sbis;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: organisation; Type: TABLE; Schema: public; Owner: sbis
--

CREATE TABLE public.organisation (
    id integer NOT NULL,
    "ParentId" integer,
    "Name" text NOT NULL,
    "Type" integer NOT NULL
);


ALTER TABLE public.organisation OWNER TO sbis;

--
-- Data for Name: organisation; Type: TABLE DATA; Schema: public; Owner: sbis
--

COPY public.organisation (id, "ParentId", "Name", "Type") FROM stdin;
1	\N	Офис в Санкт-Петербурге	1
2	1	Отдел разработки	2
3	2	Иванов	3
4	2	Сидоров	3
5	1	Отдел тестирования	2
6	5	Петров	3
7	\N	Офис в Москве	1
8	7	Аналитический отдел	2
9	8	Винтиков	3
10	8	Шпунтиков	3
11	7	Отдел продаж	2
12	11	Отдел обслуживания корпоративных клиентов	2
13	12	Белова	3
14	12	Крылова	3
16	11	Отдел обслуживания физ лиц	2
17	16	Петрова	3
18	16	Иванова	3
19	7	Тех. поддержка	2
20	19	Морозов	3
\.


--
-- Name: organisation organisation_pkey; Type: CONSTRAINT; Schema: public; Owner: sbis
--

ALTER TABLE ONLY public.organisation
    ADD CONSTRAINT organisation_pkey PRIMARY KEY (id);


--
-- Name: parentid_type_idx; Type: INDEX; Schema: public; Owner: sbis
--

CREATE INDEX parentid_type_idx ON public.organisation USING btree ("ParentId", "Type");


--
-- Name: organisation organisation_ParentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sbis
--

ALTER TABLE ONLY public.organisation
    ADD CONSTRAINT "organisation_ParentId_fkey" FOREIGN KEY ("ParentId") REFERENCES public.organisation(id);


--
-- PostgreSQL database dump complete
--
