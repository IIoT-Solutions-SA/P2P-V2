--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:ZtJiI9yJtrYz6iJCcrgPyA==$0nVhO0md6CbfZ2Hg7Uz2QAK6JerDnZW/FbjU6Vqp97g=:L+a+69ZZrvlifguDAWyumf6hAdcbsTvB7E1vvqCuUlc=';

--
-- User Configurations
--








--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

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
-- PostgreSQL database dump complete
--

--
-- Database "p2p_sandbox" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

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
-- Name: p2p_sandbox; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE p2p_sandbox WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE p2p_sandbox OWNER TO postgres;

\connect p2p_sandbox

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
-- Name: forumcategorytype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.forumcategorytype AS ENUM (
    'AUTOMATION',
    'QUALITY_MANAGEMENT',
    'MAINTENANCE',
    'ARTIFICIAL_INTELLIGENCE',
    'IOT',
    'GENERAL'
);


ALTER TYPE public.forumcategorytype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: file_metadata_v2; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_metadata_v2 (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    file_id character varying NOT NULL,
    original_filename character varying NOT NULL,
    content_type character varying NOT NULL,
    file_size integer NOT NULL,
    content_hash character varying NOT NULL,
    storage_type character varying NOT NULL,
    storage_path character varying NOT NULL,
    category character varying NOT NULL,
    user_id uuid,
    organization_id uuid,
    is_public boolean NOT NULL,
    is_active boolean NOT NULL,
    extra_metadata character varying
);


ALTER TABLE public.file_metadata_v2 OWNER TO postgres;

--
-- Name: forum_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_categories (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    description character varying,
    category_type public.forumcategorytype NOT NULL,
    color_class character varying NOT NULL,
    is_active boolean NOT NULL,
    sort_order integer NOT NULL,
    topics_count integer NOT NULL,
    posts_count integer NOT NULL
);


ALTER TABLE public.forum_categories OWNER TO postgres;

--
-- Name: forum_post_likes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_post_likes (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL
);


ALTER TABLE public.forum_post_likes OWNER TO postgres;

--
-- Name: forum_posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_posts (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    content text NOT NULL,
    topic_id uuid NOT NULL,
    author_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    parent_post_id uuid,
    is_best_answer boolean NOT NULL,
    is_deleted boolean NOT NULL,
    edited_at timestamp without time zone,
    likes_count integer NOT NULL,
    replies_count integer NOT NULL
);


ALTER TABLE public.forum_posts OWNER TO postgres;

--
-- Name: forum_topic_likes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_topic_likes (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    topic_id uuid NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL
);


ALTER TABLE public.forum_topic_likes OWNER TO postgres;

--
-- Name: forum_topic_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_topic_views (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    topic_id uuid NOT NULL,
    user_id uuid,
    organization_id uuid NOT NULL,
    ip_address character varying,
    user_agent character varying
);


ALTER TABLE public.forum_topic_views OWNER TO postgres;

--
-- Name: forum_topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.forum_topics (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    title character varying NOT NULL,
    content text NOT NULL,
    excerpt character varying NOT NULL,
    author_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    category_id uuid NOT NULL,
    is_pinned boolean NOT NULL,
    is_locked boolean NOT NULL,
    has_best_answer boolean NOT NULL,
    best_answer_post_id uuid,
    views_count integer NOT NULL,
    posts_count integer NOT NULL,
    likes_count integer NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    last_post_id uuid,
    last_post_author_id uuid
);


ALTER TABLE public.forum_topics OWNER TO postgres;

--
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    name character varying(255) NOT NULL,
    name_arabic character varying(255),
    description character varying(2000),
    email character varying(255) NOT NULL,
    phone_number character varying(20),
    website character varying(255),
    address_line_1 character varying(255),
    address_line_2 character varying(255),
    city character varying(100),
    state_province character varying(100),
    postal_code character varying(20),
    country character varying(2) NOT NULL,
    industry_type character varying(50) NOT NULL,
    company_size character varying(50),
    registration_number character varying(100),
    tax_id character varying(100),
    logo_url character varying(500),
    banner_url character varying(500),
    status character varying(50) NOT NULL,
    trial_ends_at timestamp with time zone,
    subscription_tier character varying(50) NOT NULL,
    max_users integer NOT NULL,
    max_use_cases integer NOT NULL,
    max_storage_gb integer NOT NULL,
    allow_public_use_cases boolean NOT NULL,
    require_use_case_approval boolean NOT NULL
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- Name: user_invitations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_invitations (
    id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    email character varying(255) NOT NULL,
    token character varying(255) NOT NULL,
    organization_id uuid NOT NULL,
    invited_role character varying(50) NOT NULL,
    invited_by uuid NOT NULL,
    status character varying(50) NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    job_title character varying(100),
    department character varying(100),
    personal_message character varying(1000),
    expires_at timestamp with time zone NOT NULL,
    accepted_at timestamp with time zone
);


ALTER TABLE public.user_invitations OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    phone_number character varying(20),
    profile_picture_url character varying(500),
    role character varying(50) NOT NULL,
    status character varying(50) NOT NULL,
    organization_id uuid NOT NULL,
    supertokens_user_id character varying(255) NOT NULL,
    bio character varying(1000),
    job_title character varying(100),
    department character varying(100),
    email_notifications_enabled boolean DEFAULT true NOT NULL,
    forum_notifications_enabled boolean DEFAULT true NOT NULL,
    message_notifications_enabled boolean DEFAULT true NOT NULL,
    email_verified boolean NOT NULL,
    email_verified_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
1a40770b6cc7
\.


--
-- Data for Name: file_metadata_v2; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.file_metadata_v2 (id, created_at, updated_at, file_id, original_filename, content_type, file_size, content_hash, storage_type, storage_path, category, user_id, organization_id, is_public, is_active, extra_metadata) FROM stdin;
\.


--
-- Data for Name: forum_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_categories (id, created_at, updated_at, name, description, category_type, color_class, is_active, sort_order, topics_count, posts_count) FROM stdin;
44474700-2de8-401e-b358-24a60eec8e02	2025-05-11 08:56:02.699057	2025-08-08 08:56:02.699064	Automation	Discussion about automation in manufacturing	AUTOMATION	bg-blue-100	t	0	42	126
de242d70-661a-4745-a26b-f78f3ad4f6f0	2025-05-11 08:56:02.699219	2025-08-08 08:56:02.699221	Quality Management	Discussion about quality management in manufacturing	QUALITY_MANAGEMENT	bg-green-100	t	1	38	114
e77a1a87-e37c-45f5-ba2e-db9c35553685	2025-05-11 08:56:02.699256	2025-08-08 08:56:02.699257	Maintenance	Discussion about maintenance in manufacturing	MAINTENANCE	bg-yellow-100	t	2	29	87
da5b57d4-fd26-40f6-ae54-0f40013b6874	2025-05-11 08:56:02.699285	2025-08-08 08:56:02.699286	Artificial Intelligence	Discussion about artificial intelligence in manufacturing	ARTIFICIAL_INTELLIGENCE	bg-purple-100	t	3	25	75
24ff8bc8-9a65-4281-81ef-a6d445667f53	2025-05-11 08:56:02.699312	2025-08-08 08:56:02.699313	Internet of Things	Discussion about internet of things in manufacturing	IOT	bg-orange-100	t	4	22	66
220d8e26-baf4-4ac6-8546-30095faa5dc8	2025-05-11 08:56:02.699338	2025-08-08 08:56:02.699339	General Discussion	Discussion about general discussion in manufacturing	GENERAL	bg-gray-100	t	5	10	30
\.


--
-- Data for Name: forum_post_likes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_post_likes (id, created_at, updated_at, post_id, user_id, organization_id) FROM stdin;
\.


--
-- Data for Name: forum_posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_posts (id, created_at, updated_at, content, topic_id, author_id, organization_id, parent_post_id, is_best_answer, is_deleted, edited_at, likes_count, replies_count) FROM stdin;
\.


--
-- Data for Name: forum_topic_likes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_topic_likes (id, created_at, updated_at, topic_id, user_id, organization_id) FROM stdin;
\.


--
-- Data for Name: forum_topic_views; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_topic_views (id, created_at, updated_at, topic_id, user_id, organization_id, ip_address, user_agent) FROM stdin;
\.


--
-- Data for Name: forum_topics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.forum_topics (id, created_at, updated_at, title, content, excerpt, author_id, organization_id, category_id, is_pinned, is_locked, has_best_answer, best_answer_post_id, views_count, posts_count, likes_count, last_activity_at, last_post_id, last_post_author_id) FROM stdin;
\.


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organizations (id, created_at, updated_at, is_deleted, deleted_at, name, name_arabic, description, email, phone_number, website, address_line_1, address_line_2, city, state_province, postal_code, country, industry_type, company_size, registration_number, tax_id, logo_url, banner_url, status, trial_ends_at, subscription_tier, max_users, max_use_cases, max_storage_gb, allow_public_use_cases, require_use_case_approval) FROM stdin;
550e8400-e29b-41d4-a716-446655440001	2024-08-09 08:56:02.575963+00	2025-07-10 08:56:02.575971+00	f	\N	Advanced Electronics Co.	شركة الإلكترونيات المتقدمة	Leading electronics manufacturing company specializing in AI-powered quality inspection systems and smart manufacturing solutions.	info@advanced-electronics.sa	+966-11-456-7890	https://advanced-electronics.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	51-200	CR-1010123456	300123456700003	\N	\N	active	\N	standard	10	50	10	t	f
550e8400-e29b-41d4-a716-446655440002	2024-08-09 08:56:02.599752+00	2025-07-10 08:56:02.599762+00	f	\N	Gulf Plastics Industries	صناعات البلاستيك الخليجية	Major plastics manufacturer implementing predictive maintenance and IoT solutions for enhanced operational efficiency.	contact@gulf-plastics.com	+966-13-234-5678	https://gulf-plastics.com	Industrial Area, Dammam	\N	Dammam	Eastern Province	31421	SA	manufacturing	201-500	CR-1013234567	300234567800003	\N	\N	active	\N	professional	100	1000	200	t	f
550e8400-e29b-41d4-a716-446655440003	2024-08-09 08:56:02.599861+00	2025-07-10 08:56:02.599863+00	f	\N	Saudi Steel Works	أعمال الصلب السعودية	Integrated steel manufacturing facility utilizing advanced automation and robotic systems for increased productivity.	admin@saudi-steel.sa	+966-14-345-6789	https://saudi-steel.sa	Industrial Area, Yanbu	\N	Yanbu	Al Madinah Region	46455	SA	manufacturing	501-1000	CR-1014345678	300345678900003	\N	\N	active	\N	professional	200	2000	500	t	f
550e8400-e29b-41d4-a716-446655440004	2024-08-09 08:56:02.599929+00	2025-07-10 08:56:02.59993+00	f	\N	Arabian Food Processing	معالجة الأغذية العربية	Food processing company implementing smart inventory management and quality control systems for enhanced food safety.	info@arabian-food.sa	+966-12-456-7890	https://arabian-food.sa	Industrial Area, Jeddah	\N	Jeddah	Makkah Region	21442	SA	manufacturing	101-200	CR-1012456789	300456789000003	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-446655440005	2024-08-09 08:56:02.599991+00	2025-07-10 08:56:02.599992+00	f	\N	Precision Manufacturing Ltd	شركة التصنيع الدقيق المحدودة	Precision engineering company specializing in high-tech manufacturing solutions and advanced automation systems.	contact@precision-mfg.sa	+966-11-567-8901	https://precision-mfg.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11623	SA	manufacturing	51-100	CR-1011567890	300567890100003	\N	\N	active	\N	standard	25	200	50	t	f
550e8400-e29b-41d4-a716-446655440006	2024-08-09 08:56:02.600051+00	2025-07-10 08:56:02.600052+00	f	\N	Eco-Green Industries	الصناعات الإيكولوجية الخضراء	Sustainable manufacturing company focusing on green technologies and energy-efficient production processes.	info@eco-green.sa	+966-11-678-9012	https://eco-green.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	energy	11-50	CR-1011678901	300678901200003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-446655440007	2024-08-09 08:56:02.600108+00	2025-07-10 08:56:02.600109+00	f	\N	Future Tech Manufacturing	تصنيع التقنيات المستقبلية	Technology-driven manufacturing company implementing AI, IoT, and blockchain solutions for Industry 4.0 transformation.	hello@future-tech.sa	+966-11-789-0123	https://future-tech.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	technology	51-200	CR-1011789012	300789012300003	\N	\N	active	\N	standard	10	50	10	t	f
550e8400-e29b-41d4-a716-446655440008	2024-08-09 08:56:02.60017+00	2025-07-10 08:56:02.600171+00	f	\N	Secure Supply Co.	شركة التوريد الآمن	Supply chain and logistics company utilizing advanced tracking systems and smart inventory management solutions.	info@secure-supply.sa	+966-11-890-1234	https://secure-supply.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	logistics	11-50	CR-1011890123	300890123400003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-446655440009	2024-08-09 08:56:02.600366+00	2025-07-10 08:56:02.600371+00	f	\N	Pharma Excellence Ltd	شركة التميز الدوائي المحدودة	Pharmaceutical manufacturing company implementing AI-powered quality inspection and automated production systems.	contact@pharma-excellence.sa	+966-12-901-2345	https://pharma-excellence.sa	Industrial Area, Mecca	\N	Mecca	Makkah Region	21955	SA	healthcare	101-200	CR-1012901234	300901234500003	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-44665544000a	2024-08-09 08:56:02.600452+00	2025-07-10 08:56:02.600453+00	f	\N	Safety First Industries	صناعات السلامة أولاً	Industrial safety equipment manufacturer focusing on smart monitoring systems and predictive safety analytics.	safety@safety-first.sa	+966-11-012-3456	https://safety-first.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	11-50	CR-1011012345	300012345600003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-44665544000b	2024-08-09 08:56:02.60051+00	2025-07-10 08:56:02.600511+00	f	\N	Eastern Industries	الصناعات الشرقية	Diversified industrial conglomerate implementing digital transformation across multiple manufacturing sectors.	info@eastern-industries.sa	+966-13-123-4567	https://eastern-industries.sa	Industrial Area, Dammam	\N	Dammam	Eastern Province	31421	SA	manufacturing	1000+	CR-1013123456	300123456700004	\N	\N	active	\N	professional	500	5000	1000	t	f
550e8400-e29b-41d4-a716-44665544000c	2024-08-09 08:56:02.600562+00	2025-07-10 08:56:02.600562+00	f	\N	Red Sea Food Processing	معالجة أغذية البحر الأحمر	Seafood processing company utilizing advanced cold chain management and AI-powered quality control systems.	info@redsea-food.sa	+966-12-234-5678	https://redsea-food.sa	Industrial Area, Jeddah	\N	Jeddah	Makkah Region	21442	SA	manufacturing	51-100	CR-1012234567	300234567800004	\N	\N	active	\N	standard	25	200	50	t	f
550e8400-e29b-41d4-a716-44665544000d	2024-08-09 08:56:02.600709+00	2025-07-10 08:56:02.60071+00	f	\N	Capital Manufacturing Hub	مركز التصنيع الرأسمالي	Manufacturing hub providing shared smart manufacturing facilities and Industry 4.0 technologies to SMEs.	hub@capital-mfg.sa	+966-11-345-6789	https://capital-mfg.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	201-500	CR-1011345678	300345678900004	\N	\N	active	\N	professional	100	1000	200	t	f
550e8400-e29b-41d4-a716-44665544000e	2024-08-09 08:56:02.600763+00	2025-07-10 08:56:02.600763+00	f	\N	North Riyadh Logistics	لوجستيات شمال الرياض	Logistics and warehousing company implementing smart inventory management and automated material handling systems.	ops@north-riyadh-logistics.sa	+966-11-456-7890	https://north-riyadh-logistics.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	13241	SA	logistics	101-200	CR-1011456789	300456789000004	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-44665544000f	2024-08-09 08:56:02.60086+00	2025-07-10 08:56:02.600862+00	f	\N	South Valley Industries	صناعات الوادي الجنوبي	Multi-sector manufacturing company specializing in process optimization and energy-efficient production technologies.	contact@south-valley.sa	+966-17-567-8901	https://south-valley.sa	Industrial Area, Abha	\N	Abha	Aseer Region	62521	SA	manufacturing	51-200	CR-1017567890	300567890100004	\N	\N	active	\N	standard	10	50	10	t	f
09b1b525-4760-4ed0-bde5-1b34e5f352a8	2025-07-25 08:56:02.600943+00	2025-08-08 08:56:02.600943+00	f	\N	Innovation Startup Ltd	شركة الابتكار الناشئة المحدودة	Emerging technology startup exploring AI and IoT solutions for manufacturing.	hello@innovation-startup.sa	+966-11-000-0000	\N	Business District, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	technology	1-10	\N	\N	\N	\N	trial	2025-09-08 08:56:02.600941+00	basic	5	25	5	t	f
1083df28-49e4-41fb-9068-ae97846424c9	2025-07-25 08:56:02.600996+00	2025-08-08 08:56:02.600997+00	f	\N	Green Manufacturing Co	شركة التصنيع الأخضر	Sustainable manufacturing company testing eco-friendly production methods.	info@green-mfg.sa	+966-11-000-0000	\N	Business District, Jeddah	\N	Jeddah	Makkah Region	11564	SA	energy	11-50	\N	\N	\N	\N	trial	2025-09-08 08:56:02.600995+00	standard	15	100	25	t	f
\.


--
-- Data for Name: user_invitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_invitations (id, created_at, updated_at, email, token, organization_id, invited_role, invited_by, status, first_name, last_name, job_title, department, personal_message, expires_at, accepted_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, created_at, updated_at, is_deleted, deleted_at, email, first_name, last_name, phone_number, profile_picture_url, role, status, organization_id, supertokens_user_id, bio, job_title, department, email_notifications_enabled, forum_notifications_enabled, message_notifications_enabled, email_verified, email_verified_at) FROM stdin;
450e8400-e29b-41d4-a716-446655440001	2024-11-09 08:56:02.640153+00	2025-07-23 08:56:02.640154+00	f	\N	sarah.ahmed@advanced-electronics.sa	Sarah	Ahmed	+966-17-655-1245	\N	member	active	550e8400-e29b-41d4-a716-446655440001	st-2031b48e74994d1e	Experienced production engineer specializing in smart manufacturing and IoT sensor integration.	Production Engineer	Manufacturing Operations	t	t	t	t	2025-05-18 08:56:02.640142+00
450e8400-e29b-41d4-a716-446655440002	2025-05-26 08:56:02.640451+00	2025-07-28 08:56:02.640452+00	f	\N	mohammed.rashid@precision-mfg.sa	Mohammed	Al-Rashid	+966-17-713-4898	\N	member	active	550e8400-e29b-41d4-a716-446655440005	st-5b203ff3e2af4d8f	IoT and automation specialist with 8+ years experience implementing industrial sensor networks.	IoT Specialist	Technology Solutions	t	t	t	t	2025-06-27 08:56:02.640448+00
450e8400-e29b-41d4-a716-446655440003	2024-11-26 08:56:02.640518+00	2025-08-02 08:56:02.64052+00	f	\N	fatima.hassan@arabian-food.sa	Fatima	Hassan	+966-14-243-4910	\N	member	active	550e8400-e29b-41d4-a716-446655440004	st-8c4d1d11d0164726	Quality control expert specializing in AI-powered inspection systems for food processing.	Quality Manager	Quality Assurance	t	t	t	t	2024-09-17 08:56:02.640517+00
450e8400-e29b-41d4-a716-446655440004	2024-11-14 08:56:02.640578+00	2025-07-24 08:56:02.640579+00	f	\N	ahmed.alzahrani@south-valley.sa	Ahmed	Al-Zahrani	+966-13-658-4333	\N	admin	active	550e8400-e29b-41d4-a716-44665544000f	st-0e3af9a0a7be424c	Factory owner and entrepreneur focused on digital transformation and team development.	Factory Owner	Executive Management	t	t	t	t	2025-07-06 08:56:02.640577+00
450e8400-e29b-41d4-a716-446655440005	2025-05-22 08:56:02.640631+00	2025-08-07 08:56:02.640631+00	f	\N	mohammed.shahri@gulf-plastics.com	Mohammed	Al-Shahri	+966-13-886-8484	\N	member	active	550e8400-e29b-41d4-a716-446655440002	st-1c62e91b2efc482b	Operations manager with proven track record in predictive maintenance and cost reduction.	Operations Manager	Operations	t	t	t	t	2025-06-10 08:56:02.640629+00
450e8400-e29b-41d4-a716-446655440006	2025-02-15 08:56:02.640679+00	2025-07-18 08:56:02.64068+00	f	\N	fatima.otaibi@eastern-industries.sa	Fatima	Al-Otaibi	+966-14-410-9736	\N	admin	active	550e8400-e29b-41d4-a716-44665544000b	st-4e4828d845024214	Factory owner specializing in electrical equipment manufacturing and smart inventory systems.	Factory Owner	Executive Management	t	t	t	t	2025-06-25 08:56:02.640678+00
450e8400-e29b-41d4-a716-446655440007	2024-11-27 08:56:02.64073+00	2025-07-24 08:56:02.64073+00	f	\N	khalid.ghamdi@pharma-excellence.sa	Khalid	Al-Ghamdi	+966-12-510-9368	\N	member	active	550e8400-e29b-41d4-a716-446655440009	st-0e5adc61fa7140c3	Quality engineer with expertise in AI-powered quality inspection for pharmaceutical packaging.	Quality Engineer	Quality Control	t	t	t	t	2024-08-09 08:56:02.640729+00
450e8400-e29b-41d4-a716-446655440008	2025-05-14 08:56:02.640782+00	2025-08-01 08:56:02.640782+00	f	\N	ahmed.rasheed@saudi-steel.sa	Ahmed	Al-Rasheed	+966-13-879-2133	\N	member	active	550e8400-e29b-41d4-a716-446655440003	st-7d46d26cbfb746c5	Plant manager overseeing steel production operations with focus on automation and robotics.	Plant Manager	Manufacturing Operations	t	t	t	t	2024-12-24 08:56:02.64078+00
450e8400-e29b-41d4-a716-446655440009	2025-02-12 08:56:02.64083+00	2025-08-06 08:56:02.640831+00	f	\N	sarah.mansouri@eco-green.sa	Sarah	Al-Mansouri	+966-12-586-9992	\N	member	active	550e8400-e29b-41d4-a716-446655440006	st-112eac20b92c4829	Sustainability-focused quality engineer implementing green manufacturing practices.	Quality Engineer	Quality Assurance	t	t	t	t	2025-06-29 08:56:02.640829+00
450e8400-e29b-41d4-a716-44665544000a	2025-03-31 08:56:02.640876+00	2025-07-29 08:56:02.640876+00	f	\N	mohammed.zahrani@future-tech.sa	Mohammed	Al-Zahrani	+966-13-444-5598	\N	member	active	550e8400-e29b-41d4-a716-446655440007	st-7dc824f1c5034586	Operations director leading Industry 4.0 transformation initiatives and digital innovation.	Operations Director	Operations	t	t	t	t	2024-08-11 08:56:02.640875+00
450e8400-e29b-41d4-a716-44665544000b	2024-12-01 08:56:02.640922+00	2025-08-06 08:56:02.640923+00	f	\N	noura.alsaud@secure-supply.sa	Noura	Al-Saud	+966-14-276-5762	\N	member	active	550e8400-e29b-41d4-a716-446655440008	st-9472915c3c794e17	Innovation leader driving smart logistics and supply chain technology adoption.	Innovation Lead	Research & Development	t	t	t	t	2025-06-10 08:56:02.640922+00
450e8400-e29b-41d4-a716-44665544000c	2024-09-10 08:56:02.640968+00	2025-07-26 08:56:02.640969+00	f	\N	omar.harthi@safety-first.sa	Omar	Al-Harthi	+966-12-932-6259	\N	member	active	550e8400-e29b-41d4-a716-44665544000a	st-3345b6da681b44c2	Technical director specializing in industrial safety systems and predictive analytics.	Technical Director	Engineering	t	t	t	t	2024-09-17 08:56:02.640967+00
450e8400-e29b-41d4-a716-44665544000d	2025-06-25 08:56:02.641013+00	2025-07-23 08:56:02.641014+00	f	\N	maryam.dosari@redsea-food.sa	Maryam	Al-Dosari	+966-14-687-8021	\N	member	active	550e8400-e29b-41d4-a716-44665544000c	st-10356c8e5e9d4707	Sustainability manager focusing on eco-friendly food processing and cold chain optimization.	Sustainability Manager	Sustainability	t	t	t	t	2024-09-09 08:56:02.641012+00
450e8400-e29b-41d4-a716-44665544000e	2025-01-15 08:56:02.641058+00	2025-07-14 08:56:02.641059+00	f	\N	aisha.mutairi@capital-mfg.sa	Aisha	Al-Mutairi	+966-11-978-2695	\N	member	pending	550e8400-e29b-41d4-a716-44665544000d	st-556ee1ec82e64c7c	Quality manager promoting shared manufacturing excellence across SME community.	Quality Manager	Quality Assurance	t	t	t	f	\N
450e8400-e29b-41d4-a716-44665544000f	2025-05-06 08:56:02.641104+00	2025-07-24 08:56:02.641105+00	f	\N	saud.otaishan@north-riyadh-logistics.sa	Saud	Al-Otaishan	+966-12-237-3469	\N	member	active	550e8400-e29b-41d4-a716-44665544000e	st-bb165d360e884af0	Operations manager implementing smart warehousing and automated material handling systems.	Operations Manager	Operations	t	t	t	t	2025-03-29 08:56:02.641103+00
5509eed5-a121-4cd5-bfd5-201fb118c7fd	2025-03-24 08:56:02.648315+00	2025-08-08 08:56:02.648317+00	f	\N	reem.alharbi@advanced-electronics.sa	Reem	Al-Harbi	+966-11-945-6526	\N	member	active	550e8400-e29b-41d4-a716-446655440001	st-882710cab3874f82	Production Engineer leading manufacturing initiatives with expertise in automation and smart manufacturing technologies.	Production Engineer	Manufacturing	f	t	t	t	2024-11-26 08:56:02.648308+00
084c3380-c5f5-4bf1-a94a-6d412f56eb8f	2025-03-13 08:56:02.648455+00	2025-07-30 08:56:02.648456+00	f	\N	hassan.alshehri@gulf-plastics-ind.sa	Hassan	Al-Shehri	+966-17-355-8161	\N	member	active	550e8400-e29b-41d4-a716-446655440002	st-04b4457626ba4d45	Manufacturing Director with 13+ years of experience in operations. Passionate about driving innovation and operational excellence.	Manufacturing Director	Operations	f	t	f	t	2025-05-18 08:56:02.648452+00
f5e34b81-93af-494a-baba-eb1a733f9ded	2025-05-30 08:56:02.648516+00	2025-07-19 08:56:02.648517+00	f	\N	lina.alqasemi@saudi-steel-works.sa	Lina	Al-Qasemi	+966-11-563-9717	\N	member	active	550e8400-e29b-41d4-a716-446655440003	st-d7974ec1d7954483	Process Manager with 13+ years of experience in process engineering. Passionate about driving innovation and operational excellence.	Process Manager	Process Engineering	t	f	f	t	2025-07-07 08:56:02.648514+00
a4e01903-1e5e-4cde-bc9b-408f59ed1275	2025-05-07 08:56:02.648574+00	2025-07-31 08:56:02.648575+00	f	\N	faisal.alnajjar@arabian-food-proc.sa	Faisal	Al-Najjar	+966-13-714-5234	\N	member	pending	550e8400-e29b-41d4-a716-446655440004	st-8647a4efb8ba4130	Plant Engineer leading engineering initiatives with expertise in automation and smart manufacturing technologies.	Plant Engineer	Engineering	f	f	t	f	\N
482e85a8-8323-480a-bcd2-a6618cd2ffc5	2025-06-14 08:56:02.64863+00	2025-07-26 08:56:02.648631+00	f	\N	nadia.alfaraj@precision-mfg.sa	Nadia	Al-Faraj	+966-14-636-1079	\N	member	active	550e8400-e29b-41d4-a716-446655440005	st-631fd78068bb4297	Quality Specialist leading quality control initiatives with expertise in automation and smart manufacturing technologies.	Quality Specialist	Quality Control	t	f	t	t	2024-10-27 08:56:02.648628+00
74abc3b3-c18b-4928-b8de-60cee2cf36d9	2025-03-03 08:56:02.648684+00	2025-07-22 08:56:02.648684+00	f	\N	yousef.alhamad@e-green-ind.sa	Yousef	Al-Hamad	+966-14-853-4520	\N	member	active	550e8400-e29b-41d4-a716-446655440006	st-ecda0d05b8fc4eae	Automation Engineer with 8+ years of experience in engineering. Passionate about driving innovation and operational excellence.	Automation Engineer	Engineering	t	f	t	t	2025-05-12 08:56:02.648682+00
79d84be1-e420-4f4e-a7ab-dc057e0c5587	2025-02-28 08:56:02.648735+00	2025-08-08 08:56:02.648736+00	f	\N	layla.alkhalil@future-tech-mfg.sa	Layla	Al-Khalil	+966-14-295-6446	\N	member	active	550e8400-e29b-41d4-a716-446655440007	st-1fee091daed64861	Dedicated data analyst focused on implementing cutting-edge solutions in it & analytics operations.	Data Analyst	IT & Analytics	f	t	t	t	2025-03-16 08:56:02.648734+00
008db7dc-a4d9-48af-af49-dbf6f1d52c99	2025-02-25 08:56:02.648796+00	2025-07-23 08:56:02.648797+00	f	\N	tariq.alrashid@secure-supply.sa	Tariq	Al-Rashid	+966-13-882-2100	\N	member	pending	550e8400-e29b-41d4-a716-446655440008	st-48a331bedca54099	Dedicated maintenance manager focused on implementing cutting-edge solutions in maintenance operations.	Maintenance Manager	Maintenance	t	f	f	f	\N
3d9285b4-948e-4d2d-99a1-a1640545b4af	2025-03-11 08:56:02.648854+00	2025-07-10 08:56:02.648855+00	f	\N	hala.alsabah@pharma-excellence.sa	Hala	Al-Sabah	+966-11-865-8396	\N	member	active	550e8400-e29b-41d4-a716-446655440009	st-46f82adc973c480c	Dedicated supply chain manager focused on implementing cutting-edge solutions in logistics operations.	Supply Chain Manager	Logistics	f	t	t	t	2025-01-23 08:56:02.648852+00
7eb52d87-9016-4aae-99bd-9580862e9407	2025-02-14 08:56:02.648907+00	2025-07-12 08:56:02.648908+00	f	\N	majid.althani@safety-first-ind.sa	Majid	Al-Thani	+966-13-973-2812	\N	member	active	550e8400-e29b-41d4-a716-44665544000a	st-04489a0aed584106	Experienced safety engineer specializing in digital transformation and process optimization within safety & compliance.	Safety Engineer	Safety & Compliance	t	f	f	t	2024-12-26 08:56:02.648906+00
\.


--
-- Name: alembic_version alembic_version_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkey PRIMARY KEY (version_num);


--
-- Name: file_metadata_v2 file_metadata_v2_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_metadata_v2
    ADD CONSTRAINT file_metadata_v2_pkey PRIMARY KEY (id);


--
-- Name: forum_categories forum_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_categories
    ADD CONSTRAINT forum_categories_pkey PRIMARY KEY (id);


--
-- Name: forum_post_likes forum_post_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_post_likes
    ADD CONSTRAINT forum_post_likes_pkey PRIMARY KEY (id);


--
-- Name: forum_posts forum_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_pkey PRIMARY KEY (id);


--
-- Name: forum_topic_likes forum_topic_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_likes
    ADD CONSTRAINT forum_topic_likes_pkey PRIMARY KEY (id);


--
-- Name: forum_topic_views forum_topic_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_views
    ADD CONSTRAINT forum_topic_views_pkey PRIMARY KEY (id);


--
-- Name: forum_topics forum_topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: organizations uq_organizations_registration_number; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT uq_organizations_registration_number UNIQUE (registration_number);


--
-- Name: organizations uq_organizations_tax_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT uq_organizations_tax_id UNIQUE (tax_id);


--
-- Name: user_invitations user_invitations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_invitations
    ADD CONSTRAINT user_invitations_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_file_metadata_v2_file_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_file_metadata_v2_file_id ON public.file_metadata_v2 USING btree (file_id);


--
-- Name: ix_file_metadata_v2_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_file_metadata_v2_organization_id ON public.file_metadata_v2 USING btree (organization_id);


--
-- Name: ix_file_metadata_v2_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_file_metadata_v2_user_id ON public.file_metadata_v2 USING btree (user_id);


--
-- Name: ix_forum_categories_active_sort; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_categories_active_sort ON public.forum_categories USING btree (is_active, sort_order);


--
-- Name: ix_forum_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_categories_name ON public.forum_categories USING btree (name);


--
-- Name: ix_forum_post_likes_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_post_likes_organization_id ON public.forum_post_likes USING btree (organization_id);


--
-- Name: ix_forum_post_likes_post_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_post_likes_post_id ON public.forum_post_likes USING btree (post_id);


--
-- Name: ix_forum_post_likes_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_forum_post_likes_unique ON public.forum_post_likes USING btree (post_id, user_id);


--
-- Name: ix_forum_post_likes_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_post_likes_user ON public.forum_post_likes USING btree (user_id);


--
-- Name: ix_forum_post_likes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_post_likes_user_id ON public.forum_post_likes USING btree (user_id);


--
-- Name: ix_forum_posts_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_author_id ON public.forum_posts USING btree (author_id);


--
-- Name: ix_forum_posts_author_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_author_org ON public.forum_posts USING btree (author_id, organization_id);


--
-- Name: ix_forum_posts_best_answer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_best_answer ON public.forum_posts USING btree (topic_id, is_best_answer);


--
-- Name: ix_forum_posts_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_created ON public.forum_posts USING btree (created_at);


--
-- Name: ix_forum_posts_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_organization_id ON public.forum_posts USING btree (organization_id);


--
-- Name: ix_forum_posts_parent_post_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_parent_post_id ON public.forum_posts USING btree (parent_post_id);


--
-- Name: ix_forum_posts_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_topic_id ON public.forum_posts USING btree (topic_id);


--
-- Name: ix_forum_posts_topic_parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_posts_topic_parent ON public.forum_posts USING btree (topic_id, parent_post_id);


--
-- Name: ix_forum_topic_likes_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_likes_organization_id ON public.forum_topic_likes USING btree (organization_id);


--
-- Name: ix_forum_topic_likes_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_likes_topic_id ON public.forum_topic_likes USING btree (topic_id);


--
-- Name: ix_forum_topic_likes_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_forum_topic_likes_unique ON public.forum_topic_likes USING btree (topic_id, user_id);


--
-- Name: ix_forum_topic_likes_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_likes_user ON public.forum_topic_likes USING btree (user_id);


--
-- Name: ix_forum_topic_likes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_likes_user_id ON public.forum_topic_likes USING btree (user_id);


--
-- Name: ix_forum_topic_views_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_views_created ON public.forum_topic_views USING btree (created_at);


--
-- Name: ix_forum_topic_views_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_views_organization_id ON public.forum_topic_views USING btree (organization_id);


--
-- Name: ix_forum_topic_views_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_views_topic_id ON public.forum_topic_views USING btree (topic_id);


--
-- Name: ix_forum_topic_views_topic_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_views_topic_user ON public.forum_topic_views USING btree (topic_id, user_id);


--
-- Name: ix_forum_topic_views_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topic_views_user_id ON public.forum_topic_views USING btree (user_id);


--
-- Name: ix_forum_topics_activity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_activity ON public.forum_topics USING btree (last_activity_at);


--
-- Name: ix_forum_topics_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_author_id ON public.forum_topics USING btree (author_id);


--
-- Name: ix_forum_topics_author_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_author_org ON public.forum_topics USING btree (author_id, organization_id);


--
-- Name: ix_forum_topics_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_category_id ON public.forum_topics USING btree (category_id);


--
-- Name: ix_forum_topics_last_post_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_last_post_author_id ON public.forum_topics USING btree (last_post_author_id);


--
-- Name: ix_forum_topics_org_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_org_category ON public.forum_topics USING btree (organization_id, category_id);


--
-- Name: ix_forum_topics_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_organization_id ON public.forum_topics USING btree (organization_id);


--
-- Name: ix_forum_topics_pinned; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_pinned ON public.forum_topics USING btree (is_pinned, last_activity_at);


--
-- Name: ix_forum_topics_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_forum_topics_title ON public.forum_topics USING btree (title);


--
-- Name: ix_organizations_industry_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_industry_type ON public.organizations USING btree (industry_type);


--
-- Name: ix_organizations_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_organizations_name ON public.organizations USING btree (name);


--
-- Name: ix_organizations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_status ON public.organizations USING btree (status);


--
-- Name: ix_user_invitations_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_invitations_email ON public.user_invitations USING btree (email);


--
-- Name: ix_user_invitations_invited_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_invitations_invited_by ON public.user_invitations USING btree (invited_by);


--
-- Name: ix_user_invitations_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_invitations_organization_id ON public.user_invitations USING btree (organization_id);


--
-- Name: ix_user_invitations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_invitations_status ON public.user_invitations USING btree (status);


--
-- Name: ix_user_invitations_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_invitations_token ON public.user_invitations USING btree (token);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_organization_id ON public.users USING btree (organization_id);


--
-- Name: ix_users_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_status ON public.users USING btree (status);


--
-- Name: ix_users_supertokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_supertokens_user_id ON public.users USING btree (supertokens_user_id);


--
-- Name: file_metadata_v2 file_metadata_v2_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_metadata_v2
    ADD CONSTRAINT file_metadata_v2_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: file_metadata_v2 file_metadata_v2_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_metadata_v2
    ADD CONSTRAINT file_metadata_v2_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: forum_topics fk_forum_topics_best_answer_post; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT fk_forum_topics_best_answer_post FOREIGN KEY (best_answer_post_id) REFERENCES public.forum_posts(id);


--
-- Name: forum_topics fk_forum_topics_last_post; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT fk_forum_topics_last_post FOREIGN KEY (last_post_id) REFERENCES public.forum_posts(id);


--
-- Name: users fk_users_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: forum_post_likes forum_post_likes_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_post_likes
    ADD CONSTRAINT forum_post_likes_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: forum_post_likes forum_post_likes_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_post_likes
    ADD CONSTRAINT forum_post_likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.forum_posts(id);


--
-- Name: forum_post_likes forum_post_likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_post_likes
    ADD CONSTRAINT forum_post_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: forum_posts forum_posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: forum_posts forum_posts_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: forum_posts forum_posts_parent_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_parent_post_id_fkey FOREIGN KEY (parent_post_id) REFERENCES public.forum_posts(id);


--
-- Name: forum_posts forum_posts_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_posts
    ADD CONSTRAINT forum_posts_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.forum_topics(id);


--
-- Name: forum_topic_likes forum_topic_likes_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_likes
    ADD CONSTRAINT forum_topic_likes_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: forum_topic_likes forum_topic_likes_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_likes
    ADD CONSTRAINT forum_topic_likes_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.forum_topics(id);


--
-- Name: forum_topic_likes forum_topic_likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_likes
    ADD CONSTRAINT forum_topic_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: forum_topic_views forum_topic_views_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_views
    ADD CONSTRAINT forum_topic_views_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: forum_topic_views forum_topic_views_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_views
    ADD CONSTRAINT forum_topic_views_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.forum_topics(id);


--
-- Name: forum_topic_views forum_topic_views_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topic_views
    ADD CONSTRAINT forum_topic_views_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: forum_topics forum_topics_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: forum_topics forum_topics_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.forum_categories(id);


--
-- Name: forum_topics forum_topics_last_post_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_last_post_author_id_fkey FOREIGN KEY (last_post_author_id) REFERENCES public.users(id);


--
-- Name: forum_topics forum_topics_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- PostgreSQL database dump complete
--

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

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
-- PostgreSQL database dump complete
--

--
-- Database "supertokens" dump
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 15.13

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
-- Name: supertokens; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE supertokens WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE supertokens OWNER TO postgres;

\connect supertokens

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: all_auth_recipe_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.all_auth_recipe_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    primary_or_recipe_user_id character(36) NOT NULL,
    is_linked_or_is_a_primary_user boolean DEFAULT false NOT NULL,
    recipe_id character varying(128) NOT NULL,
    time_joined bigint NOT NULL,
    primary_or_recipe_user_time_joined bigint NOT NULL
);


ALTER TABLE public.all_auth_recipe_users OWNER TO postgres;

--
-- Name: app_id_to_user_id; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_id_to_user_id (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    recipe_id character varying(128) NOT NULL,
    primary_or_recipe_user_id character(36) NOT NULL,
    is_linked_or_is_a_primary_user boolean DEFAULT false NOT NULL
);


ALTER TABLE public.app_id_to_user_id OWNER TO postgres;

--
-- Name: apps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apps (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    created_at_time bigint
);


ALTER TABLE public.apps OWNER TO postgres;

--
-- Name: bulk_import_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bulk_import_users (
    id character(36) NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    primary_user_id character varying(36),
    raw_data text NOT NULL,
    status character varying(128) DEFAULT 'NEW'::character varying,
    error_msg text,
    created_at bigint NOT NULL,
    updated_at bigint NOT NULL
);


ALTER TABLE public.bulk_import_users OWNER TO postgres;

--
-- Name: dashboard_user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dashboard_user_sessions (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    session_id character(36) NOT NULL,
    user_id character(36) NOT NULL,
    time_created bigint NOT NULL,
    expiry bigint NOT NULL
);


ALTER TABLE public.dashboard_user_sessions OWNER TO postgres;

--
-- Name: dashboard_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dashboard_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL,
    password_hash character varying(256) NOT NULL,
    time_joined bigint NOT NULL
);


ALTER TABLE public.dashboard_users OWNER TO postgres;

--
-- Name: emailpassword_pswd_reset_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emailpassword_pswd_reset_tokens (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    token character varying(128) NOT NULL,
    email character varying(256),
    token_expiry bigint NOT NULL
);


ALTER TABLE public.emailpassword_pswd_reset_tokens OWNER TO postgres;

--
-- Name: emailpassword_user_to_tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emailpassword_user_to_tenant (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL
);


ALTER TABLE public.emailpassword_user_to_tenant OWNER TO postgres;

--
-- Name: emailpassword_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emailpassword_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL,
    password_hash character varying(256) NOT NULL,
    time_joined bigint NOT NULL
);


ALTER TABLE public.emailpassword_users OWNER TO postgres;

--
-- Name: emailverification_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emailverification_tokens (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    email character varying(256) NOT NULL,
    token character varying(128) NOT NULL,
    token_expiry bigint NOT NULL
);


ALTER TABLE public.emailverification_tokens OWNER TO postgres;

--
-- Name: emailverification_verified_emails; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emailverification_verified_emails (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    email character varying(256) NOT NULL
);


ALTER TABLE public.emailverification_verified_emails OWNER TO postgres;

--
-- Name: jwt_signing_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jwt_signing_keys (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    key_id character varying(255) NOT NULL,
    key_string text NOT NULL,
    algorithm character varying(10) NOT NULL,
    created_at bigint
);


ALTER TABLE public.jwt_signing_keys OWNER TO postgres;

--
-- Name: key_value; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.key_value (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    name character varying(128) NOT NULL,
    value text,
    created_at_time bigint
);


ALTER TABLE public.key_value OWNER TO postgres;

--
-- Name: oauth_clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_clients (
    app_id character varying(64) NOT NULL,
    client_id character varying(255) NOT NULL,
    client_secret text,
    enable_refresh_token_rotation boolean NOT NULL,
    is_client_credentials_only boolean NOT NULL
);


ALTER TABLE public.oauth_clients OWNER TO postgres;

--
-- Name: oauth_logout_challenges; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_logout_challenges (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    challenge character varying(128) NOT NULL,
    client_id character varying(255) NOT NULL,
    post_logout_redirect_uri character varying(1024),
    session_handle character varying(128),
    state character varying(128),
    time_created bigint NOT NULL
);


ALTER TABLE public.oauth_logout_challenges OWNER TO postgres;

--
-- Name: oauth_m2m_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_m2m_tokens (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    client_id character varying(255) NOT NULL,
    iat bigint NOT NULL,
    exp bigint NOT NULL
);


ALTER TABLE public.oauth_m2m_tokens OWNER TO postgres;

--
-- Name: oauth_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oauth_sessions (
    gid character varying(255) NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying,
    client_id character varying(255) NOT NULL,
    session_handle character varying(128),
    external_refresh_token character varying(255),
    internal_refresh_token character varying(255),
    jti text NOT NULL,
    exp bigint NOT NULL
);


ALTER TABLE public.oauth_sessions OWNER TO postgres;

--
-- Name: passwordless_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwordless_codes (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    code_id character(36) NOT NULL,
    device_id_hash character(44) NOT NULL,
    link_code_hash character(44) NOT NULL,
    created_at bigint NOT NULL
);


ALTER TABLE public.passwordless_codes OWNER TO postgres;

--
-- Name: passwordless_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwordless_devices (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    device_id_hash character(44) NOT NULL,
    email character varying(256),
    phone_number character varying(256),
    link_code_salt character(44) NOT NULL,
    failed_attempts integer NOT NULL
);


ALTER TABLE public.passwordless_devices OWNER TO postgres;

--
-- Name: passwordless_user_to_tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwordless_user_to_tenant (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256),
    phone_number character varying(256)
);


ALTER TABLE public.passwordless_user_to_tenant OWNER TO postgres;

--
-- Name: passwordless_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.passwordless_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256),
    phone_number character varying(256),
    time_joined bigint NOT NULL
);


ALTER TABLE public.passwordless_users OWNER TO postgres;

--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    role character varying(255) NOT NULL,
    permission character varying(255) NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    role character varying(255) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: session_access_token_signing_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.session_access_token_signing_keys (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    created_at_time bigint NOT NULL,
    value text
);


ALTER TABLE public.session_access_token_signing_keys OWNER TO postgres;

--
-- Name: session_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.session_info (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    session_handle character varying(255) NOT NULL,
    user_id character varying(128) NOT NULL,
    refresh_token_hash_2 character varying(128) NOT NULL,
    session_data text,
    expires_at bigint NOT NULL,
    created_at_time bigint NOT NULL,
    jwt_user_payload text,
    use_static_key boolean NOT NULL
);


ALTER TABLE public.session_info OWNER TO postgres;

--
-- Name: tenant_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_configs (
    connection_uri_domain character varying(256) DEFAULT ''::character varying NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    core_config text,
    email_password_enabled boolean,
    passwordless_enabled boolean,
    third_party_enabled boolean,
    is_first_factors_null boolean
);


ALTER TABLE public.tenant_configs OWNER TO postgres;

--
-- Name: tenant_first_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_first_factors (
    connection_uri_domain character varying(256) DEFAULT ''::character varying NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    factor_id character varying(128) NOT NULL
);


ALTER TABLE public.tenant_first_factors OWNER TO postgres;

--
-- Name: tenant_required_secondary_factors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_required_secondary_factors (
    connection_uri_domain character varying(256) DEFAULT ''::character varying NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    factor_id character varying(128) NOT NULL
);


ALTER TABLE public.tenant_required_secondary_factors OWNER TO postgres;

--
-- Name: tenant_thirdparty_provider_clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_thirdparty_provider_clients (
    connection_uri_domain character varying(256) DEFAULT ''::character varying NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    third_party_id character varying(28) NOT NULL,
    client_type character varying(64) DEFAULT ''::character varying NOT NULL,
    client_id character varying(256) NOT NULL,
    client_secret text,
    scope character varying(128)[],
    force_pkce boolean,
    additional_config text
);


ALTER TABLE public.tenant_thirdparty_provider_clients OWNER TO postgres;

--
-- Name: tenant_thirdparty_providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenant_thirdparty_providers (
    connection_uri_domain character varying(256) DEFAULT ''::character varying NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    third_party_id character varying(28) NOT NULL,
    name character varying(64),
    authorization_endpoint text,
    authorization_endpoint_query_params text,
    token_endpoint text,
    token_endpoint_body_params text,
    user_info_endpoint text,
    user_info_endpoint_query_params text,
    user_info_endpoint_headers text,
    jwks_uri text,
    oidc_discovery_endpoint text,
    require_email boolean,
    user_info_map_from_id_token_payload_user_id character varying(64),
    user_info_map_from_id_token_payload_email character varying(64),
    user_info_map_from_id_token_payload_email_verified character varying(64),
    user_info_map_from_user_info_endpoint_user_id character varying(64),
    user_info_map_from_user_info_endpoint_email character varying(64),
    user_info_map_from_user_info_endpoint_email_verified character varying(64)
);


ALTER TABLE public.tenant_thirdparty_providers OWNER TO postgres;

--
-- Name: tenants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenants (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    created_at_time bigint
);


ALTER TABLE public.tenants OWNER TO postgres;

--
-- Name: thirdparty_user_to_tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.thirdparty_user_to_tenant (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    third_party_id character varying(28) NOT NULL,
    third_party_user_id character varying(256) NOT NULL
);


ALTER TABLE public.thirdparty_user_to_tenant OWNER TO postgres;

--
-- Name: thirdparty_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.thirdparty_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    third_party_id character varying(28) NOT NULL,
    third_party_user_id character varying(256) NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL,
    time_joined bigint NOT NULL
);


ALTER TABLE public.thirdparty_users OWNER TO postgres;

--
-- Name: totp_used_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.totp_used_codes (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    code character varying(8) NOT NULL,
    is_valid boolean NOT NULL,
    expiry_time_ms bigint NOT NULL,
    created_time_ms bigint NOT NULL
);


ALTER TABLE public.totp_used_codes OWNER TO postgres;

--
-- Name: totp_user_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.totp_user_devices (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    device_name character varying(256) NOT NULL,
    secret_key character varying(256) NOT NULL,
    period integer NOT NULL,
    skew integer NOT NULL,
    verified boolean NOT NULL,
    created_at bigint
);


ALTER TABLE public.totp_user_devices OWNER TO postgres;

--
-- Name: totp_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.totp_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL
);


ALTER TABLE public.totp_users OWNER TO postgres;

--
-- Name: user_last_active; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_last_active (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    last_active_time bigint
);


ALTER TABLE public.user_last_active OWNER TO postgres;

--
-- Name: user_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_metadata (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    user_metadata text NOT NULL
);


ALTER TABLE public.user_metadata OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character varying(128) NOT NULL,
    role character varying(255) NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: userid_mapping; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userid_mapping (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    supertokens_user_id character(36) NOT NULL,
    external_user_id character varying(128) NOT NULL,
    external_user_id_info text
);


ALTER TABLE public.userid_mapping OWNER TO postgres;

--
-- Name: webauthn_account_recovery_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webauthn_account_recovery_tokens (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL,
    token character varying(256) NOT NULL,
    expires_at bigint NOT NULL
);


ALTER TABLE public.webauthn_account_recovery_tokens OWNER TO postgres;

--
-- Name: webauthn_credentials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webauthn_credentials (
    id character varying(256) NOT NULL,
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    rp_id character varying(256) NOT NULL,
    user_id character(36),
    counter bigint NOT NULL,
    public_key bytea NOT NULL,
    transports text NOT NULL,
    created_at bigint NOT NULL,
    updated_at bigint NOT NULL
);


ALTER TABLE public.webauthn_credentials OWNER TO postgres;

--
-- Name: webauthn_generated_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webauthn_generated_options (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    id character(36) NOT NULL,
    challenge character varying(256) NOT NULL,
    email character varying(256),
    rp_id character varying(256) NOT NULL,
    rp_name character varying(256) NOT NULL,
    origin character varying(256) NOT NULL,
    expires_at bigint NOT NULL,
    created_at bigint NOT NULL,
    user_presence_required boolean DEFAULT false NOT NULL,
    user_verification character varying(12) DEFAULT 'preferred'::character varying NOT NULL
);


ALTER TABLE public.webauthn_generated_options OWNER TO postgres;

--
-- Name: webauthn_user_to_tenant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webauthn_user_to_tenant (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    tenant_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL
);


ALTER TABLE public.webauthn_user_to_tenant OWNER TO postgres;

--
-- Name: webauthn_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webauthn_users (
    app_id character varying(64) DEFAULT 'public'::character varying NOT NULL,
    user_id character(36) NOT NULL,
    email character varying(256) NOT NULL,
    rp_id character varying(256) NOT NULL,
    time_joined bigint NOT NULL
);


ALTER TABLE public.webauthn_users OWNER TO postgres;

--
-- Data for Name: all_auth_recipe_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.all_auth_recipe_users (app_id, tenant_id, user_id, primary_or_recipe_user_id, is_linked_or_is_a_primary_user, recipe_id, time_joined, primary_or_recipe_user_time_joined) FROM stdin;
\.


--
-- Data for Name: app_id_to_user_id; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_id_to_user_id (app_id, user_id, recipe_id, primary_or_recipe_user_id, is_linked_or_is_a_primary_user) FROM stdin;
\.


--
-- Data for Name: apps; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.apps (app_id, created_at_time) FROM stdin;
public	1754728899111
\.


--
-- Data for Name: bulk_import_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bulk_import_users (id, app_id, primary_user_id, raw_data, status, error_msg, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dashboard_user_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboard_user_sessions (app_id, session_id, user_id, time_created, expiry) FROM stdin;
\.


--
-- Data for Name: dashboard_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboard_users (app_id, user_id, email, password_hash, time_joined) FROM stdin;
\.


--
-- Data for Name: emailpassword_pswd_reset_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emailpassword_pswd_reset_tokens (app_id, user_id, token, email, token_expiry) FROM stdin;
\.


--
-- Data for Name: emailpassword_user_to_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emailpassword_user_to_tenant (app_id, tenant_id, user_id, email) FROM stdin;
\.


--
-- Data for Name: emailpassword_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emailpassword_users (app_id, user_id, email, password_hash, time_joined) FROM stdin;
\.


--
-- Data for Name: emailverification_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emailverification_tokens (app_id, tenant_id, user_id, email, token, token_expiry) FROM stdin;
\.


--
-- Data for Name: emailverification_verified_emails; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emailverification_verified_emails (app_id, user_id, email) FROM stdin;
\.


--
-- Data for Name: jwt_signing_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jwt_signing_keys (app_id, key_id, key_string, algorithm, created_at) FROM stdin;
public	s-954ac47c-dc7a-4259-a985-b3c39f2db384	MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqWVzLTacR2a3uuOqB05cnf1VuDsNx+HvCn339nRggzz7O0LsN/7CSF8Ly8kg0qBUjKdJNnVFLfBvKwwOsTEyOVN646YMinfkjSsZAVzY7/mwr2teU8Vv1tw4sLkSwcb5H7E185MxKfdg0CWX3eFLLCe3Ex8QvboqMfL67tsoKJkGIoDjRl3t6cGU257ftX7tL8IXnBFL1/Z3uZpHD013thsmB1rnWCWhmFEBog786sZdLlD4BQP9Mdii4+M0GZ8eVCWKvc6Fo8mrAQHOxWsq83Ok6knE//BOAr0Vng48UuK8lA356wVqyplqnlkfXOKYfTZJkYZrw9BnEnumCgGJDQIDAQAB|MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCpZXMtNpxHZre646oHTlyd/VW4Ow3H4e8Kfff2dGCDPPs7Quw3/sJIXwvLySDSoFSMp0k2dUUt8G8rDA6xMTI5U3rjpgyKd+SNKxkBXNjv+bCva15TxW/W3DiwuRLBxvkfsTXzkzEp92DQJZfd4UssJ7cTHxC9uiox8vru2ygomQYigONGXe3pwZTbnt+1fu0vwhecEUvX9ne5mkcPTXe2GyYHWudYJaGYUQGiDvzqxl0uUPgFA/0x2KLj4zQZnx5UJYq9zoWjyasBAc7Fayrzc6TqScT/8E4CvRWeDjxS4ryUDfnrBWrKmWqeWR9c4ph9NkmRhmvD0GcSe6YKAYkNAgMBAAECggEAAid3iT6S9V0oSXtjL7rD9pYLPMTy0NT98/bJoYv10pLC3sxOp4tOalqxEktGvFRMdvRv+9NjyOja6mPPHQWTOK49LL9xaeJf7kP7H6y6rS888Ld6EzElJ14/Z09B3o56n7f3x8GaWV5bZWeQ+0HwnDQOFzNo2azQJA34ZHNg2vFKmfArmWByGslBZyHVO4ygsMCJKnIYLrBDskvKRbKlWkbR34qJqhUbmiLu8XVIpkSTw+kEdiO+y7U+91JjySd84jV/cSzd30nf14CcC413avUP937lKso58gnfRVwmvISY7RoJG4I5NXpOWY9Bk2XtoHyVOuIje4C6pqE81aXIuQKBgQDMIPGguzLg2bZAkJfe5d//MtCasFruxJO7LtRYhlTMrJ1vchiduF5YbSc/ibTNjPPibKgmUkmZcW4CiJvJZFxKpUfjUmH5OTotrwaxrgD96o/mP+StnVU/6hf5uuSww1B1P94m2L/+993OI4tRvWod/U6+HusJu1K+NOsZm7mTRQKBgQDUcRS9N7t6PcdV6iU5Xcfc85T6e1yul+uDamWCxgVSxnml/MbYRHCiC2/e5mSlnF0oAPo7mQQUNYmfY30jbmZr2cCbDdjp2bSkfx/HubLu1K1L+KMxIWqG3EPyyIoLIz4uvs/YvYtdBGmzgem9WMTuLM1Kv2n+2dAc6po1sNLXKQKBgEONQ2klihjO83k6YIfrGs2hS1dltTH+68SuIqeJDNcO6KrQ30SSluY8eRiVwbekRbFQs/S6lpCo8Pb1rlhfVgt91uRrhvCq943WtihmpP1iemyACHVL88JK/dQu/S9h82ZZ1HKWmDMQY96r9JcAT/XMthpEsRNvYlp/uK2o0yjhAoGAEsTCzkzENXKLz91V2JGefLjQaqjHcW1ek0etHDaedcevK6j/cE/rm4VjJtA4CCGeYVBkyysjnx1zwS8q+Rxh1Bly2MAKb+6Z9QZ+KkkPs+X6QYH/+PE41h1Tq3loKL++WKbm+gEU9OzU4dUSb3YOP/SZVoc+uBNKPaPEaAXtOrECgYAv445mhN/uzedHvX6kYts+JCLxjQ0hoSAo8SqKQCZAXkiKMRo5Kej8FilaiY+OilqNbtC4bFW2a8Ds5Kt9RzPTCUSu9uLzjuBIkMh9aeYGkWy79okp2pPLAmO9hN87+kgNQx0q89XpDEec/z+Gf96LAdbqQC6LMxdvViaIBb0GvA==	RS256	1754728899413
\.


--
-- Data for Name: key_value; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.key_value (app_id, tenant_id, name, value, created_at_time) FROM stdin;
public	public	FEATURE_FLAG	[]	1754728899125
public	public	refresh_token_key	1000:ca8074585eba06ccc3eaaab1d7289bc8765696a917d7808510519f3bd39b9fe912cf1b14f71a7fa6b6813efbe9bbac3a70d86de37f1a11b7aa76e267134f5b8c:85c71e85e718e4a9557e3c5a3731155d9145a07326fd7d2d55d4ec829ce69f62bdbd3cd2e4d56d7ec34d6ff797c4ce7beabe610b15c66e088a99ec2f1094a36c	1754728899406
public	public	TELEMETRY_ID	dfba5c54-3574-4c07-a601-3332a9210fdc	1754728899555
\.


--
-- Data for Name: oauth_clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_clients (app_id, client_id, client_secret, enable_refresh_token_rotation, is_client_credentials_only) FROM stdin;
\.


--
-- Data for Name: oauth_logout_challenges; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_logout_challenges (app_id, challenge, client_id, post_logout_redirect_uri, session_handle, state, time_created) FROM stdin;
\.


--
-- Data for Name: oauth_m2m_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_m2m_tokens (app_id, client_id, iat, exp) FROM stdin;
\.


--
-- Data for Name: oauth_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oauth_sessions (gid, app_id, client_id, session_handle, external_refresh_token, internal_refresh_token, jti, exp) FROM stdin;
\.


--
-- Data for Name: passwordless_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwordless_codes (app_id, tenant_id, code_id, device_id_hash, link_code_hash, created_at) FROM stdin;
\.


--
-- Data for Name: passwordless_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwordless_devices (app_id, tenant_id, device_id_hash, email, phone_number, link_code_salt, failed_attempts) FROM stdin;
\.


--
-- Data for Name: passwordless_user_to_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwordless_user_to_tenant (app_id, tenant_id, user_id, email, phone_number) FROM stdin;
\.


--
-- Data for Name: passwordless_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.passwordless_users (app_id, user_id, email, phone_number, time_joined) FROM stdin;
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (app_id, role, permission) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (app_id, role) FROM stdin;
\.


--
-- Data for Name: session_access_token_signing_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.session_access_token_signing_keys (app_id, created_at_time, value) FROM stdin;
public	1754728899361	MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAooeIcHY95NIqqtUig4gQseEvDN2BvHG3KvCnrKe66kjgJFeBgtmxfNODwSmZAvZlO8NpeO4OnzW1uJMkgu9sfRh2G/y828s7jhuIzEU4/u2bu+qHxBTaUoO/jb7mX5k7c66rIIC6oxoGllVJ9+hZCWcJ+QrejYxVonexkyMiy5ROZDhuOSv3NVVPxKNH9ZUEGHc02X4RksllAoijEZRV+TyN8cyd09SigCvIsqzl/BVmJud8KzvLmC/DBsdYuOh1W3ZlquTyj9uQBqNVwIRxAQfSjQyi48Hl3RLAaVR7MJAFPPS0di/gHmIdE7fOj5kJVru4u928NjomIca8zruJYQIDAQAB|MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCih4hwdj3k0iqq1SKDiBCx4S8M3YG8cbcq8Kesp7rqSOAkV4GC2bF804PBKZkC9mU7w2l47g6fNbW4kySC72x9GHYb/LzbyzuOG4jMRTj+7Zu76ofEFNpSg7+NvuZfmTtzrqsggLqjGgaWVUn36FkJZwn5Ct6NjFWid7GTIyLLlE5kOG45K/c1VU/Eo0f1lQQYdzTZfhGSyWUCiKMRlFX5PI3xzJ3T1KKAK8iyrOX8FWYm53wrO8uYL8MGx1i46HVbdmWq5PKP25AGo1XAhHEBB9KNDKLjweXdEsBpVHswkAU89LR2L+AeYh0Tt86PmQlWu7i73bw2OiYhxrzOu4lhAgMBAAECggEAShZzPSTBWRXuyjnnBkNXrOZj7r7ofXDu2L2kCYHaJCM9PYPAL1gx3p+Cj2J5dA7CnegZo70M4El5AV7dxWwDrdChQmfG5YBysPhfNxKVBSxmEda6tcj1rqiNAL3VQR3WKokkS+gya9gYyZ2uXrpFIBKeyq5IPgkLHkjmoxZgraC+f+fcLfjoK00936G8XxfH0pdcl1Ph0qhJD0+91DqYmrCmH18uuzD6hOjqgd249u0tVQYrT9P3Idk1gX2aAaFftbh2snD5QHdxbqyht45vlIp+0UUMMUP1FdqNmi0CltQDAB0+zYK33H9HiBUJATFsm29g6KEw4dEHtcLLHHn4cwKBgQDYmOqGode/75JQIfQe0xMKRTz3aWZE2m3f6HA6b4/yiEEs7eynxovAvU5bnfIgt+ZcMhoQdmxYzSwCrZZbqCoLK1FdCYHkzF1vVDuvNTcdXw54Twz5hOphNLEl+n57c6THE9mAuYobu2CBEdtdKmtn9Jsb0cJFHwdMEfjcIy+hswKBgQDAGKNZ/KIR6uursnjVAQkCf4soPqHDIGmB25A+RGDIZHS3RJ73oTQ/8RVYUdjn0f5w24gqf8cQVbDqEe3bi4lzNwLpdOCMOma4zIGNRaM5Fej9qarU0V0IFtQIPaKQgdEATG9Uq5yf+o4qRz2sI6itTvvlNVOi1hLYftBKeuPWmwKBgDeBwKBt+1dhstI8UU5Q81EvezdAWIgOnhfCfnhLPM1/o4w7EOnSFOB44wrRiEpgNnWsFUfgwVVkhwHMsHqett+T407/b71Nrigoov78mTo6sP+d6opLSLFOipNcBWvnr/Ogn53Abqc6trl89QWEKHBEnDdd4vZJxFn3RRpNHhjHAoGBAKPSn0T4CfPD6Ba2jwwA5QEnarL4rxXsx24CpQIlaHCeE1fUgsnmxdueK7j1nEkfsqHm5zpvXIIWwljsz3BDkQYcLTSSA4ozqDUD25xyfiAKCniCQPlcT729Ujhw7/nTbD2X8f5AmMNqd+Ggff0XMBwVVweDsf8WGF5f0B0krrfvAoGBAID8K78i9lpKmRj3K9wrXNDRU68IxSFQ7/9f7vls/SNy/HUC1XCxhQN5webdZSz3iH3IVvBOmvr/cf7NfaRodiVNgy2fuF7D2Cv2bFp0GfIP/3xT0ucTdbs08PcFECNAQSzaNtDUGkMwpkkgE2YtuXNcKS9QftND6GjUN+AqQNJe
\.


--
-- Data for Name: session_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.session_info (app_id, tenant_id, session_handle, user_id, refresh_token_hash_2, session_data, expires_at, created_at_time, jwt_user_payload, use_static_key) FROM stdin;
\.


--
-- Data for Name: tenant_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_configs (connection_uri_domain, app_id, tenant_id, core_config, email_password_enabled, passwordless_enabled, third_party_enabled, is_first_factors_null) FROM stdin;
	public	public	{}	t	t	t	t
\.


--
-- Data for Name: tenant_first_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_first_factors (connection_uri_domain, app_id, tenant_id, factor_id) FROM stdin;
\.


--
-- Data for Name: tenant_required_secondary_factors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_required_secondary_factors (connection_uri_domain, app_id, tenant_id, factor_id) FROM stdin;
\.


--
-- Data for Name: tenant_thirdparty_provider_clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_thirdparty_provider_clients (connection_uri_domain, app_id, tenant_id, third_party_id, client_type, client_id, client_secret, scope, force_pkce, additional_config) FROM stdin;
\.


--
-- Data for Name: tenant_thirdparty_providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenant_thirdparty_providers (connection_uri_domain, app_id, tenant_id, third_party_id, name, authorization_endpoint, authorization_endpoint_query_params, token_endpoint, token_endpoint_body_params, user_info_endpoint, user_info_endpoint_query_params, user_info_endpoint_headers, jwks_uri, oidc_discovery_endpoint, require_email, user_info_map_from_id_token_payload_user_id, user_info_map_from_id_token_payload_email, user_info_map_from_id_token_payload_email_verified, user_info_map_from_user_info_endpoint_user_id, user_info_map_from_user_info_endpoint_email, user_info_map_from_user_info_endpoint_email_verified) FROM stdin;
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tenants (app_id, tenant_id, created_at_time) FROM stdin;
public	public	1754728899111
\.


--
-- Data for Name: thirdparty_user_to_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.thirdparty_user_to_tenant (app_id, tenant_id, user_id, third_party_id, third_party_user_id) FROM stdin;
\.


--
-- Data for Name: thirdparty_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.thirdparty_users (app_id, third_party_id, third_party_user_id, user_id, email, time_joined) FROM stdin;
\.


--
-- Data for Name: totp_used_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.totp_used_codes (app_id, tenant_id, user_id, code, is_valid, expiry_time_ms, created_time_ms) FROM stdin;
\.


--
-- Data for Name: totp_user_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.totp_user_devices (app_id, user_id, device_name, secret_key, period, skew, verified, created_at) FROM stdin;
\.


--
-- Data for Name: totp_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.totp_users (app_id, user_id) FROM stdin;
\.


--
-- Data for Name: user_last_active; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_last_active (app_id, user_id, last_active_time) FROM stdin;
\.


--
-- Data for Name: user_metadata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_metadata (app_id, user_id, user_metadata) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (app_id, tenant_id, user_id, role) FROM stdin;
\.


--
-- Data for Name: userid_mapping; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.userid_mapping (app_id, supertokens_user_id, external_user_id, external_user_id_info) FROM stdin;
\.


--
-- Data for Name: webauthn_account_recovery_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webauthn_account_recovery_tokens (app_id, tenant_id, user_id, email, token, expires_at) FROM stdin;
\.


--
-- Data for Name: webauthn_credentials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webauthn_credentials (id, app_id, rp_id, user_id, counter, public_key, transports, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: webauthn_generated_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webauthn_generated_options (app_id, tenant_id, id, challenge, email, rp_id, rp_name, origin, expires_at, created_at, user_presence_required, user_verification) FROM stdin;
\.


--
-- Data for Name: webauthn_user_to_tenant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webauthn_user_to_tenant (app_id, tenant_id, user_id, email) FROM stdin;
\.


--
-- Data for Name: webauthn_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.webauthn_users (app_id, user_id, email, rp_id, time_joined) FROM stdin;
\.


--
-- Name: all_auth_recipe_users all_auth_recipe_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.all_auth_recipe_users
    ADD CONSTRAINT all_auth_recipe_users_pkey PRIMARY KEY (app_id, tenant_id, user_id);


--
-- Name: app_id_to_user_id app_id_to_user_id_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_id_to_user_id
    ADD CONSTRAINT app_id_to_user_id_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: apps apps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apps
    ADD CONSTRAINT apps_pkey PRIMARY KEY (app_id);


--
-- Name: bulk_import_users bulk_import_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bulk_import_users
    ADD CONSTRAINT bulk_import_users_pkey PRIMARY KEY (app_id, id);


--
-- Name: dashboard_user_sessions dashboard_user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_user_sessions
    ADD CONSTRAINT dashboard_user_sessions_pkey PRIMARY KEY (app_id, session_id);


--
-- Name: dashboard_users dashboard_users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_users
    ADD CONSTRAINT dashboard_users_email_key UNIQUE (app_id, email);


--
-- Name: dashboard_users dashboard_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_users
    ADD CONSTRAINT dashboard_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: emailpassword_pswd_reset_tokens emailpassword_pswd_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_pswd_reset_tokens
    ADD CONSTRAINT emailpassword_pswd_reset_tokens_pkey PRIMARY KEY (app_id, user_id, token);


--
-- Name: emailpassword_pswd_reset_tokens emailpassword_pswd_reset_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_pswd_reset_tokens
    ADD CONSTRAINT emailpassword_pswd_reset_tokens_token_key UNIQUE (token);


--
-- Name: emailpassword_user_to_tenant emailpassword_user_to_tenant_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_user_to_tenant
    ADD CONSTRAINT emailpassword_user_to_tenant_email_key UNIQUE (app_id, tenant_id, email);


--
-- Name: emailpassword_user_to_tenant emailpassword_user_to_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_user_to_tenant
    ADD CONSTRAINT emailpassword_user_to_tenant_pkey PRIMARY KEY (app_id, tenant_id, user_id);


--
-- Name: emailpassword_users emailpassword_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_users
    ADD CONSTRAINT emailpassword_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: emailverification_tokens emailverification_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailverification_tokens
    ADD CONSTRAINT emailverification_tokens_pkey PRIMARY KEY (app_id, tenant_id, user_id, email, token);


--
-- Name: emailverification_tokens emailverification_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailverification_tokens
    ADD CONSTRAINT emailverification_tokens_token_key UNIQUE (token);


--
-- Name: emailverification_verified_emails emailverification_verified_emails_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailverification_verified_emails
    ADD CONSTRAINT emailverification_verified_emails_pkey PRIMARY KEY (app_id, user_id, email);


--
-- Name: jwt_signing_keys jwt_signing_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jwt_signing_keys
    ADD CONSTRAINT jwt_signing_keys_pkey PRIMARY KEY (app_id, key_id);


--
-- Name: key_value key_value_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.key_value
    ADD CONSTRAINT key_value_pkey PRIMARY KEY (app_id, tenant_id, name);


--
-- Name: oauth_clients oauth_clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_clients
    ADD CONSTRAINT oauth_clients_pkey PRIMARY KEY (app_id, client_id);


--
-- Name: oauth_logout_challenges oauth_logout_challenges_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_logout_challenges
    ADD CONSTRAINT oauth_logout_challenges_pkey PRIMARY KEY (app_id, challenge);


--
-- Name: oauth_m2m_tokens oauth_m2m_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_m2m_tokens
    ADD CONSTRAINT oauth_m2m_tokens_pkey PRIMARY KEY (app_id, client_id, iat);


--
-- Name: oauth_sessions oauth_sessions_external_refresh_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_sessions
    ADD CONSTRAINT oauth_sessions_external_refresh_token_key UNIQUE (external_refresh_token);


--
-- Name: oauth_sessions oauth_sessions_internal_refresh_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_sessions
    ADD CONSTRAINT oauth_sessions_internal_refresh_token_key UNIQUE (internal_refresh_token);


--
-- Name: oauth_sessions oauth_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_sessions
    ADD CONSTRAINT oauth_sessions_pkey PRIMARY KEY (gid);


--
-- Name: passwordless_codes passwordless_codes_link_code_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_codes
    ADD CONSTRAINT passwordless_codes_link_code_hash_key UNIQUE (app_id, tenant_id, link_code_hash);


--
-- Name: passwordless_codes passwordless_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_codes
    ADD CONSTRAINT passwordless_codes_pkey PRIMARY KEY (app_id, tenant_id, code_id);


--
-- Name: passwordless_devices passwordless_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_devices
    ADD CONSTRAINT passwordless_devices_pkey PRIMARY KEY (app_id, tenant_id, device_id_hash);


--
-- Name: passwordless_user_to_tenant passwordless_user_to_tenant_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_user_to_tenant
    ADD CONSTRAINT passwordless_user_to_tenant_email_key UNIQUE (app_id, tenant_id, email);


--
-- Name: passwordless_user_to_tenant passwordless_user_to_tenant_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_user_to_tenant
    ADD CONSTRAINT passwordless_user_to_tenant_phone_number_key UNIQUE (app_id, tenant_id, phone_number);


--
-- Name: passwordless_user_to_tenant passwordless_user_to_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_user_to_tenant
    ADD CONSTRAINT passwordless_user_to_tenant_pkey PRIMARY KEY (app_id, tenant_id, user_id);


--
-- Name: passwordless_users passwordless_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_users
    ADD CONSTRAINT passwordless_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (app_id, role, permission);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (app_id, role);


--
-- Name: session_access_token_signing_keys session_access_token_signing_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_access_token_signing_keys
    ADD CONSTRAINT session_access_token_signing_keys_pkey PRIMARY KEY (app_id, created_at_time);


--
-- Name: session_info session_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_info
    ADD CONSTRAINT session_info_pkey PRIMARY KEY (app_id, tenant_id, session_handle);


--
-- Name: tenant_configs tenant_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_configs
    ADD CONSTRAINT tenant_configs_pkey PRIMARY KEY (connection_uri_domain, app_id, tenant_id);


--
-- Name: tenant_first_factors tenant_first_factors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_first_factors
    ADD CONSTRAINT tenant_first_factors_pkey PRIMARY KEY (connection_uri_domain, app_id, tenant_id, factor_id);


--
-- Name: tenant_required_secondary_factors tenant_required_secondary_factors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_required_secondary_factors
    ADD CONSTRAINT tenant_required_secondary_factors_pkey PRIMARY KEY (connection_uri_domain, app_id, tenant_id, factor_id);


--
-- Name: tenant_thirdparty_provider_clients tenant_thirdparty_provider_clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_thirdparty_provider_clients
    ADD CONSTRAINT tenant_thirdparty_provider_clients_pkey PRIMARY KEY (connection_uri_domain, app_id, tenant_id, third_party_id, client_type);


--
-- Name: tenant_thirdparty_providers tenant_thirdparty_providers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_thirdparty_providers
    ADD CONSTRAINT tenant_thirdparty_providers_pkey PRIMARY KEY (connection_uri_domain, app_id, tenant_id, third_party_id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (app_id, tenant_id);


--
-- Name: thirdparty_user_to_tenant thirdparty_user_to_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.thirdparty_user_to_tenant
    ADD CONSTRAINT thirdparty_user_to_tenant_pkey PRIMARY KEY (app_id, tenant_id, user_id);


--
-- Name: thirdparty_user_to_tenant thirdparty_user_to_tenant_third_party_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.thirdparty_user_to_tenant
    ADD CONSTRAINT thirdparty_user_to_tenant_third_party_user_id_key UNIQUE (app_id, tenant_id, third_party_id, third_party_user_id);


--
-- Name: thirdparty_users thirdparty_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.thirdparty_users
    ADD CONSTRAINT thirdparty_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: totp_used_codes totp_used_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_used_codes
    ADD CONSTRAINT totp_used_codes_pkey PRIMARY KEY (app_id, tenant_id, user_id, created_time_ms);


--
-- Name: totp_user_devices totp_user_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_user_devices
    ADD CONSTRAINT totp_user_devices_pkey PRIMARY KEY (app_id, user_id, device_name);


--
-- Name: totp_users totp_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_users
    ADD CONSTRAINT totp_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: user_last_active user_last_active_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_last_active
    ADD CONSTRAINT user_last_active_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: user_metadata user_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_metadata
    ADD CONSTRAINT user_metadata_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (app_id, tenant_id, user_id, role);


--
-- Name: userid_mapping userid_mapping_external_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userid_mapping
    ADD CONSTRAINT userid_mapping_external_user_id_key UNIQUE (app_id, external_user_id);


--
-- Name: userid_mapping userid_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userid_mapping
    ADD CONSTRAINT userid_mapping_pkey PRIMARY KEY (app_id, supertokens_user_id, external_user_id);


--
-- Name: userid_mapping userid_mapping_supertokens_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userid_mapping
    ADD CONSTRAINT userid_mapping_supertokens_user_id_key UNIQUE (app_id, supertokens_user_id);


--
-- Name: webauthn_account_recovery_tokens webauthn_account_recovery_token_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_account_recovery_tokens
    ADD CONSTRAINT webauthn_account_recovery_token_pkey PRIMARY KEY (app_id, tenant_id, user_id, token);


--
-- Name: webauthn_credentials webauthn_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_pkey PRIMARY KEY (app_id, rp_id, id);


--
-- Name: webauthn_generated_options webauthn_generated_options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_generated_options
    ADD CONSTRAINT webauthn_generated_options_pkey PRIMARY KEY (app_id, tenant_id, id);


--
-- Name: webauthn_user_to_tenant webauthn_user_to_tenant_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_user_to_tenant
    ADD CONSTRAINT webauthn_user_to_tenant_email_key UNIQUE (app_id, tenant_id, email);


--
-- Name: webauthn_user_to_tenant webauthn_user_to_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_user_to_tenant
    ADD CONSTRAINT webauthn_user_to_tenant_pkey PRIMARY KEY (app_id, tenant_id, user_id);


--
-- Name: webauthn_users webauthn_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_users
    ADD CONSTRAINT webauthn_users_pkey PRIMARY KEY (app_id, user_id);


--
-- Name: access_token_signing_keys_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX access_token_signing_keys_app_id_index ON public.session_access_token_signing_keys USING btree (app_id);


--
-- Name: all_auth_recipe_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_tenant_id_index ON public.all_auth_recipe_users USING btree (app_id, tenant_id);


--
-- Name: all_auth_recipe_user_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_user_app_id_index ON public.all_auth_recipe_users USING btree (app_id);


--
-- Name: all_auth_recipe_user_id_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_user_id_app_id_index ON public.all_auth_recipe_users USING btree (app_id, user_id);


--
-- Name: all_auth_recipe_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_user_id_index ON public.all_auth_recipe_users USING btree (user_id);


--
-- Name: all_auth_recipe_users_pagination_index1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_pagination_index1 ON public.all_auth_recipe_users USING btree (app_id, tenant_id, primary_or_recipe_user_time_joined DESC, primary_or_recipe_user_id DESC);


--
-- Name: all_auth_recipe_users_pagination_index2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_pagination_index2 ON public.all_auth_recipe_users USING btree (app_id, tenant_id, primary_or_recipe_user_time_joined, primary_or_recipe_user_id DESC);


--
-- Name: all_auth_recipe_users_pagination_index3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_pagination_index3 ON public.all_auth_recipe_users USING btree (recipe_id, app_id, tenant_id, primary_or_recipe_user_time_joined DESC, primary_or_recipe_user_id DESC);


--
-- Name: all_auth_recipe_users_pagination_index4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_pagination_index4 ON public.all_auth_recipe_users USING btree (recipe_id, app_id, tenant_id, primary_or_recipe_user_time_joined, primary_or_recipe_user_id DESC);


--
-- Name: all_auth_recipe_users_primary_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_primary_user_id_index ON public.all_auth_recipe_users USING btree (primary_or_recipe_user_id, app_id);


--
-- Name: all_auth_recipe_users_recipe_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX all_auth_recipe_users_recipe_id_index ON public.all_auth_recipe_users USING btree (app_id, recipe_id, tenant_id);


--
-- Name: app_id_to_user_id_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX app_id_to_user_id_app_id_index ON public.app_id_to_user_id USING btree (app_id);


--
-- Name: app_id_to_user_id_primary_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX app_id_to_user_id_primary_user_id_index ON public.app_id_to_user_id USING btree (primary_or_recipe_user_id, app_id);


--
-- Name: app_id_to_user_id_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX app_id_to_user_id_user_id_index ON public.app_id_to_user_id USING btree (user_id, app_id);


--
-- Name: bulk_import_users_pagination_index1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bulk_import_users_pagination_index1 ON public.bulk_import_users USING btree (app_id, status, created_at DESC, id DESC);


--
-- Name: bulk_import_users_pagination_index2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bulk_import_users_pagination_index2 ON public.bulk_import_users USING btree (app_id, created_at DESC, id DESC);


--
-- Name: bulk_import_users_status_updated_at_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX bulk_import_users_status_updated_at_index ON public.bulk_import_users USING btree (app_id, status, updated_at);


--
-- Name: dashboard_user_sessions_expiry_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dashboard_user_sessions_expiry_index ON public.dashboard_user_sessions USING btree (expiry);


--
-- Name: dashboard_user_sessions_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dashboard_user_sessions_user_id_index ON public.dashboard_user_sessions USING btree (app_id, user_id);


--
-- Name: dashboard_users_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dashboard_users_app_id_index ON public.dashboard_users USING btree (app_id);


--
-- Name: emailpassword_password_reset_token_expiry_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailpassword_password_reset_token_expiry_index ON public.emailpassword_pswd_reset_tokens USING btree (token_expiry);


--
-- Name: emailpassword_pswd_reset_tokens_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailpassword_pswd_reset_tokens_user_id_index ON public.emailpassword_pswd_reset_tokens USING btree (app_id, user_id);


--
-- Name: emailpassword_user_to_tenant_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailpassword_user_to_tenant_email_index ON public.emailpassword_user_to_tenant USING btree (app_id, tenant_id, email);


--
-- Name: emailpassword_users_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailpassword_users_email_index ON public.emailpassword_users USING btree (app_id, email);


--
-- Name: emailverification_tokens_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailverification_tokens_index ON public.emailverification_tokens USING btree (token_expiry);


--
-- Name: emailverification_tokens_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailverification_tokens_tenant_id_index ON public.emailverification_tokens USING btree (app_id, tenant_id);


--
-- Name: emailverification_verified_emails_app_id_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailverification_verified_emails_app_id_email_index ON public.emailverification_verified_emails USING btree (app_id, email);


--
-- Name: emailverification_verified_emails_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX emailverification_verified_emails_app_id_index ON public.emailverification_verified_emails USING btree (app_id);


--
-- Name: jwt_signing_keys_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX jwt_signing_keys_app_id_index ON public.jwt_signing_keys USING btree (app_id);


--
-- Name: key_value_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX key_value_tenant_id_index ON public.key_value USING btree (app_id, tenant_id);


--
-- Name: oauth_logout_challenges_time_created_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX oauth_logout_challenges_time_created_index ON public.oauth_logout_challenges USING btree (time_created DESC);


--
-- Name: oauth_m2m_token_exp_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX oauth_m2m_token_exp_index ON public.oauth_m2m_tokens USING btree (exp DESC);


--
-- Name: oauth_m2m_token_iat_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX oauth_m2m_token_iat_index ON public.oauth_m2m_tokens USING btree (iat DESC, app_id DESC);


--
-- Name: oauth_session_exp_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX oauth_session_exp_index ON public.oauth_sessions USING btree (exp DESC);


--
-- Name: oauth_session_external_refresh_token_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX oauth_session_external_refresh_token_index ON public.oauth_sessions USING btree (app_id, external_refresh_token DESC);


--
-- Name: passwordless_codes_created_at_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_codes_created_at_index ON public.passwordless_codes USING btree (app_id, tenant_id, created_at);


--
-- Name: passwordless_codes_device_id_hash_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_codes_device_id_hash_index ON public.passwordless_codes USING btree (app_id, tenant_id, device_id_hash);


--
-- Name: passwordless_devices_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_devices_email_index ON public.passwordless_devices USING btree (app_id, tenant_id, email);


--
-- Name: passwordless_devices_phone_number_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_devices_phone_number_index ON public.passwordless_devices USING btree (app_id, tenant_id, phone_number);


--
-- Name: passwordless_devices_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_devices_tenant_id_index ON public.passwordless_devices USING btree (app_id, tenant_id);


--
-- Name: passwordless_user_to_tenant_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_user_to_tenant_email_index ON public.passwordless_user_to_tenant USING btree (app_id, tenant_id, email);


--
-- Name: passwordless_user_to_tenant_phone_number_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_user_to_tenant_phone_number_index ON public.passwordless_user_to_tenant USING btree (app_id, tenant_id, phone_number);


--
-- Name: passwordless_users_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_users_email_index ON public.passwordless_users USING btree (app_id, email);


--
-- Name: passwordless_users_phone_number_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX passwordless_users_phone_number_index ON public.passwordless_users USING btree (app_id, phone_number);


--
-- Name: role_permissions_permission_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX role_permissions_permission_index ON public.role_permissions USING btree (app_id, permission);


--
-- Name: role_permissions_role_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX role_permissions_role_index ON public.role_permissions USING btree (app_id, role);


--
-- Name: roles_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX roles_app_id_index ON public.roles USING btree (app_id);


--
-- Name: session_expiry_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX session_expiry_index ON public.session_info USING btree (expires_at);


--
-- Name: session_info_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX session_info_tenant_id_index ON public.session_info USING btree (app_id, tenant_id);


--
-- Name: session_info_user_id_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX session_info_user_id_app_id_index ON public.session_info USING btree (user_id, app_id);


--
-- Name: tenant_default_required_factor_ids_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tenant_default_required_factor_ids_tenant_id_index ON public.tenant_required_secondary_factors USING btree (connection_uri_domain, app_id, tenant_id);


--
-- Name: tenant_first_factors_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tenant_first_factors_tenant_id_index ON public.tenant_first_factors USING btree (connection_uri_domain, app_id, tenant_id);


--
-- Name: tenant_thirdparty_provider_clients_third_party_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tenant_thirdparty_provider_clients_third_party_id_index ON public.tenant_thirdparty_provider_clients USING btree (connection_uri_domain, app_id, tenant_id, third_party_id);


--
-- Name: tenant_thirdparty_providers_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tenant_thirdparty_providers_tenant_id_index ON public.tenant_thirdparty_providers USING btree (connection_uri_domain, app_id, tenant_id);


--
-- Name: tenants_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tenants_app_id_index ON public.tenants USING btree (app_id);


--
-- Name: thirdparty_user_to_tenant_third_party_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX thirdparty_user_to_tenant_third_party_user_id_index ON public.thirdparty_user_to_tenant USING btree (app_id, tenant_id, third_party_id, third_party_user_id);


--
-- Name: thirdparty_users_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX thirdparty_users_email_index ON public.thirdparty_users USING btree (app_id, email);


--
-- Name: thirdparty_users_thirdparty_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX thirdparty_users_thirdparty_user_id_index ON public.thirdparty_users USING btree (app_id, third_party_id, third_party_user_id);


--
-- Name: totp_used_codes_expiry_time_ms_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX totp_used_codes_expiry_time_ms_index ON public.totp_used_codes USING btree (app_id, tenant_id, expiry_time_ms);


--
-- Name: totp_used_codes_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX totp_used_codes_tenant_id_index ON public.totp_used_codes USING btree (app_id, tenant_id);


--
-- Name: totp_used_codes_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX totp_used_codes_user_id_index ON public.totp_used_codes USING btree (app_id, user_id);


--
-- Name: totp_user_devices_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX totp_user_devices_user_id_index ON public.totp_user_devices USING btree (app_id, user_id);


--
-- Name: totp_users_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX totp_users_app_id_index ON public.totp_users USING btree (app_id);


--
-- Name: user_last_active_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_last_active_app_id_index ON public.user_last_active USING btree (app_id);


--
-- Name: user_last_active_last_active_time_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_last_active_last_active_time_index ON public.user_last_active USING btree (last_active_time DESC, app_id DESC);


--
-- Name: user_metadata_app_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_metadata_app_id_index ON public.user_metadata USING btree (app_id);


--
-- Name: user_roles_app_id_role_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_roles_app_id_role_index ON public.user_roles USING btree (app_id, role);


--
-- Name: user_roles_app_id_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_roles_app_id_user_id_index ON public.user_roles USING btree (app_id, user_id);


--
-- Name: user_roles_role_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_roles_role_index ON public.user_roles USING btree (app_id, tenant_id, role);


--
-- Name: user_roles_tenant_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_roles_tenant_id_index ON public.user_roles USING btree (app_id, tenant_id);


--
-- Name: userid_mapping_supertokens_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX userid_mapping_supertokens_user_id_index ON public.userid_mapping USING btree (app_id, supertokens_user_id);


--
-- Name: webauthn_account_recovery_token_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_account_recovery_token_email_index ON public.webauthn_account_recovery_tokens USING btree (app_id, tenant_id, email);


--
-- Name: webauthn_account_recovery_token_expires_at_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_account_recovery_token_expires_at_index ON public.webauthn_account_recovery_tokens USING btree (expires_at DESC);


--
-- Name: webauthn_account_recovery_token_token_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_account_recovery_token_token_index ON public.webauthn_account_recovery_tokens USING btree (app_id, tenant_id, token);


--
-- Name: webauthn_credentials_user_id_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_credentials_user_id_index ON public.webauthn_credentials USING btree (user_id);


--
-- Name: webauthn_user_challenges_expires_at_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_user_challenges_expires_at_index ON public.webauthn_generated_options USING btree (app_id, tenant_id, expires_at);


--
-- Name: webauthn_user_to_tenant_email_index; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX webauthn_user_to_tenant_email_index ON public.webauthn_user_to_tenant USING btree (app_id, email);


--
-- Name: all_auth_recipe_users all_auth_recipe_users_primary_or_recipe_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.all_auth_recipe_users
    ADD CONSTRAINT all_auth_recipe_users_primary_or_recipe_user_id_fkey FOREIGN KEY (app_id, primary_or_recipe_user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: all_auth_recipe_users all_auth_recipe_users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.all_auth_recipe_users
    ADD CONSTRAINT all_auth_recipe_users_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: all_auth_recipe_users all_auth_recipe_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.all_auth_recipe_users
    ADD CONSTRAINT all_auth_recipe_users_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: app_id_to_user_id app_id_to_user_id_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_id_to_user_id
    ADD CONSTRAINT app_id_to_user_id_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: app_id_to_user_id app_id_to_user_id_primary_or_recipe_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_id_to_user_id
    ADD CONSTRAINT app_id_to_user_id_primary_or_recipe_user_id_fkey FOREIGN KEY (app_id, primary_or_recipe_user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: bulk_import_users bulk_import_users_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bulk_import_users
    ADD CONSTRAINT bulk_import_users_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: dashboard_user_sessions dashboard_user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_user_sessions
    ADD CONSTRAINT dashboard_user_sessions_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.dashboard_users(app_id, user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: dashboard_users dashboard_users_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_users
    ADD CONSTRAINT dashboard_users_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: emailpassword_pswd_reset_tokens emailpassword_pswd_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_pswd_reset_tokens
    ADD CONSTRAINT emailpassword_pswd_reset_tokens_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: emailpassword_user_to_tenant emailpassword_user_to_tenant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_user_to_tenant
    ADD CONSTRAINT emailpassword_user_to_tenant_user_id_fkey FOREIGN KEY (app_id, tenant_id, user_id) REFERENCES public.all_auth_recipe_users(app_id, tenant_id, user_id) ON DELETE CASCADE;


--
-- Name: emailpassword_users emailpassword_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailpassword_users
    ADD CONSTRAINT emailpassword_users_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: emailverification_tokens emailverification_tokens_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailverification_tokens
    ADD CONSTRAINT emailverification_tokens_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: emailverification_verified_emails emailverification_verified_emails_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emailverification_verified_emails
    ADD CONSTRAINT emailverification_verified_emails_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: jwt_signing_keys jwt_signing_keys_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jwt_signing_keys
    ADD CONSTRAINT jwt_signing_keys_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: key_value key_value_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.key_value
    ADD CONSTRAINT key_value_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: oauth_clients oauth_clients_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_clients
    ADD CONSTRAINT oauth_clients_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: oauth_logout_challenges oauth_logout_challenges_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_logout_challenges
    ADD CONSTRAINT oauth_logout_challenges_client_id_fkey FOREIGN KEY (app_id, client_id) REFERENCES public.oauth_clients(app_id, client_id) ON DELETE CASCADE;


--
-- Name: oauth_m2m_tokens oauth_m2m_tokens_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_m2m_tokens
    ADD CONSTRAINT oauth_m2m_tokens_client_id_fkey FOREIGN KEY (app_id, client_id) REFERENCES public.oauth_clients(app_id, client_id) ON DELETE CASCADE;


--
-- Name: oauth_sessions oauth_sessions_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oauth_sessions
    ADD CONSTRAINT oauth_sessions_client_id_fkey FOREIGN KEY (app_id, client_id) REFERENCES public.oauth_clients(app_id, client_id) ON DELETE CASCADE;


--
-- Name: passwordless_codes passwordless_codes_device_id_hash_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_codes
    ADD CONSTRAINT passwordless_codes_device_id_hash_fkey FOREIGN KEY (app_id, tenant_id, device_id_hash) REFERENCES public.passwordless_devices(app_id, tenant_id, device_id_hash) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: passwordless_devices passwordless_devices_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_devices
    ADD CONSTRAINT passwordless_devices_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: passwordless_user_to_tenant passwordless_user_to_tenant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_user_to_tenant
    ADD CONSTRAINT passwordless_user_to_tenant_user_id_fkey FOREIGN KEY (app_id, tenant_id, user_id) REFERENCES public.all_auth_recipe_users(app_id, tenant_id, user_id) ON DELETE CASCADE;


--
-- Name: passwordless_users passwordless_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.passwordless_users
    ADD CONSTRAINT passwordless_users_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_fkey FOREIGN KEY (app_id, role) REFERENCES public.roles(app_id, role) ON DELETE CASCADE;


--
-- Name: roles roles_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: session_access_token_signing_keys session_access_token_signing_keys_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_access_token_signing_keys
    ADD CONSTRAINT session_access_token_signing_keys_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: session_info session_info_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.session_info
    ADD CONSTRAINT session_info_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: tenant_first_factors tenant_first_factors_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_first_factors
    ADD CONSTRAINT tenant_first_factors_tenant_id_fkey FOREIGN KEY (connection_uri_domain, app_id, tenant_id) REFERENCES public.tenant_configs(connection_uri_domain, app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: tenant_required_secondary_factors tenant_required_secondary_factors_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_required_secondary_factors
    ADD CONSTRAINT tenant_required_secondary_factors_tenant_id_fkey FOREIGN KEY (connection_uri_domain, app_id, tenant_id) REFERENCES public.tenant_configs(connection_uri_domain, app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: tenant_thirdparty_provider_clients tenant_thirdparty_provider_clients_third_party_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_thirdparty_provider_clients
    ADD CONSTRAINT tenant_thirdparty_provider_clients_third_party_id_fkey FOREIGN KEY (connection_uri_domain, app_id, tenant_id, third_party_id) REFERENCES public.tenant_thirdparty_providers(connection_uri_domain, app_id, tenant_id, third_party_id) ON DELETE CASCADE;


--
-- Name: tenant_thirdparty_providers tenant_thirdparty_providers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenant_thirdparty_providers
    ADD CONSTRAINT tenant_thirdparty_providers_tenant_id_fkey FOREIGN KEY (connection_uri_domain, app_id, tenant_id) REFERENCES public.tenant_configs(connection_uri_domain, app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: tenants tenants_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: thirdparty_user_to_tenant thirdparty_user_to_tenant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.thirdparty_user_to_tenant
    ADD CONSTRAINT thirdparty_user_to_tenant_user_id_fkey FOREIGN KEY (app_id, tenant_id, user_id) REFERENCES public.all_auth_recipe_users(app_id, tenant_id, user_id) ON DELETE CASCADE;


--
-- Name: thirdparty_users thirdparty_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.thirdparty_users
    ADD CONSTRAINT thirdparty_users_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: totp_used_codes totp_used_codes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_used_codes
    ADD CONSTRAINT totp_used_codes_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: totp_used_codes totp_used_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_used_codes
    ADD CONSTRAINT totp_used_codes_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.totp_users(app_id, user_id) ON DELETE CASCADE;


--
-- Name: totp_user_devices totp_user_devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_user_devices
    ADD CONSTRAINT totp_user_devices_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.totp_users(app_id, user_id) ON DELETE CASCADE;


--
-- Name: totp_users totp_users_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.totp_users
    ADD CONSTRAINT totp_users_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: user_last_active user_last_active_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_last_active
    ADD CONSTRAINT user_last_active_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: user_metadata user_metadata_app_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_metadata
    ADD CONSTRAINT user_metadata_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(app_id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: userid_mapping userid_mapping_supertokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userid_mapping
    ADD CONSTRAINT userid_mapping_supertokens_user_id_fkey FOREIGN KEY (app_id, supertokens_user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- Name: webauthn_account_recovery_tokens webauthn_account_recovery_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_account_recovery_tokens
    ADD CONSTRAINT webauthn_account_recovery_token_user_id_fkey FOREIGN KEY (app_id, tenant_id, user_id) REFERENCES public.all_auth_recipe_users(app_id, tenant_id, user_id) ON DELETE CASCADE;


--
-- Name: webauthn_credentials webauthn_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.webauthn_users(app_id, user_id) ON DELETE CASCADE;


--
-- Name: webauthn_generated_options webauthn_generated_options_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_generated_options
    ADD CONSTRAINT webauthn_generated_options_tenant_id_fkey FOREIGN KEY (app_id, tenant_id) REFERENCES public.tenants(app_id, tenant_id) ON DELETE CASCADE;


--
-- Name: webauthn_user_to_tenant webauthn_user_to_tenant_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_user_to_tenant
    ADD CONSTRAINT webauthn_user_to_tenant_user_id_fkey FOREIGN KEY (app_id, tenant_id, user_id) REFERENCES public.all_auth_recipe_users(app_id, tenant_id, user_id) ON DELETE CASCADE;


--
-- Name: webauthn_users webauthn_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webauthn_users
    ADD CONSTRAINT webauthn_users_user_id_fkey FOREIGN KEY (app_id, user_id) REFERENCES public.app_id_to_user_id(app_id, user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database cluster dump complete
--

