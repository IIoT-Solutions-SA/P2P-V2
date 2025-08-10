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
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:IEX/UyFLnebWjCZ2aRGZnA==$E3xduAt2XWMSI5nr9/BDghMjrVdI+0Lk3IHiFbFFELI=:9LYTS1sr5VqQvnoiyaMtiTi7+jr1j8egBqreTx+llhU=';

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
    is_deleted boolean NOT NULL,
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
    expires_at timestamp with time zone NOT NULL,
    accepted_at timestamp with time zone,
    personal_message character varying(1000)
);


ALTER TABLE public.user_invitations OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_deleted boolean NOT NULL,
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
    email_verified boolean NOT NULL,
    email_verified_at timestamp with time zone,
    bio character varying(1000),
    job_title character varying(100),
    department character varying(100),
    email_notifications_enabled boolean NOT NULL,
    forum_notifications_enabled boolean NOT NULL,
    message_notifications_enabled boolean NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
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
cf48c547-c210-4db1-bce5-d261d6bf0d30	2025-05-12 11:10:12.069316	2025-08-09 11:10:12.069321	Automation	Discussion about automation in manufacturing	AUTOMATION	bg-blue-100	t	0	42	126
76dc1a7c-b5fd-4023-abdf-6642070173aa	2025-05-12 11:10:12.069455	2025-08-09 11:10:12.069456	Quality Management	Discussion about quality management in manufacturing	QUALITY_MANAGEMENT	bg-green-100	t	1	38	114
28c60647-47ad-49e5-91b4-39daad007a4f	2025-05-12 11:10:12.069489	2025-08-09 11:10:12.069489	Maintenance	Discussion about maintenance in manufacturing	MAINTENANCE	bg-yellow-100	t	2	29	87
0442e133-c716-44db-840c-bb6b03591c6a	2025-05-12 11:10:12.069537	2025-08-09 11:10:12.069539	Artificial Intelligence	Discussion about artificial intelligence in manufacturing	ARTIFICIAL_INTELLIGENCE	bg-purple-100	t	3	25	75
a4896433-e69d-4e07-a521-1979f0d17953	2025-05-12 11:10:12.069569	2025-08-09 11:10:12.069569	Internet of Things	Discussion about internet of things in manufacturing	IOT	bg-orange-100	t	4	22	66
299f0a21-b117-4b9d-a8f7-ca797f96c85b	2025-05-12 11:10:12.069598	2025-08-09 11:10:12.069599	General Discussion	Discussion about general discussion in manufacturing	GENERAL	bg-gray-100	t	5	10	30
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
550e8400-e29b-41d4-a716-446655440001	2024-08-10 11:10:11.981068+00	2025-07-11 11:10:11.981073+00	f	\N	Advanced Electronics Co.	شركة الإلكترونيات المتقدمة	Leading electronics manufacturing company specializing in AI-powered quality inspection systems and smart manufacturing solutions.	info@advanced-electronics.sa	+966-11-456-7890	https://advanced-electronics.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	51-200	CR-1010123456	300123456700003	\N	\N	active	\N	standard	10	50	10	t	f
550e8400-e29b-41d4-a716-446655440002	2024-08-10 11:10:11.996752+00	2025-07-11 11:10:11.996759+00	f	\N	Gulf Plastics Industries	صناعات البلاستيك الخليجية	Major plastics manufacturer implementing predictive maintenance and IoT solutions for enhanced operational efficiency.	contact@gulf-plastics.com	+966-13-234-5678	https://gulf-plastics.com	Industrial Area, Dammam	\N	Dammam	Eastern Province	31421	SA	manufacturing	201-500	CR-1013234567	300234567800003	\N	\N	active	\N	professional	100	1000	200	t	f
550e8400-e29b-41d4-a716-446655440003	2024-08-10 11:10:11.996845+00	2025-07-11 11:10:11.996846+00	f	\N	Saudi Steel Works	أعمال الصلب السعودية	Integrated steel manufacturing facility utilizing advanced automation and robotic systems for increased productivity.	admin@saudi-steel.sa	+966-14-345-6789	https://saudi-steel.sa	Industrial Area, Yanbu	\N	Yanbu	Al Madinah Region	46455	SA	manufacturing	501-1000	CR-1014345678	300345678900003	\N	\N	active	\N	professional	200	2000	500	t	f
550e8400-e29b-41d4-a716-446655440004	2024-08-10 11:10:11.996905+00	2025-07-11 11:10:11.996906+00	f	\N	Arabian Food Processing	معالجة الأغذية العربية	Food processing company implementing smart inventory management and quality control systems for enhanced food safety.	info@arabian-food.sa	+966-12-456-7890	https://arabian-food.sa	Industrial Area, Jeddah	\N	Jeddah	Makkah Region	21442	SA	manufacturing	101-200	CR-1012456789	300456789000003	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-446655440005	2024-08-10 11:10:11.99696+00	2025-07-11 11:10:11.996961+00	f	\N	Precision Manufacturing Ltd	شركة التصنيع الدقيق المحدودة	Precision engineering company specializing in high-tech manufacturing solutions and advanced automation systems.	contact@precision-mfg.sa	+966-11-567-8901	https://precision-mfg.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11623	SA	manufacturing	51-100	CR-1011567890	300567890100003	\N	\N	active	\N	standard	25	200	50	t	f
550e8400-e29b-41d4-a716-446655440006	2024-08-10 11:10:11.997013+00	2025-07-11 11:10:11.997014+00	f	\N	Eco-Green Industries	الصناعات الإيكولوجية الخضراء	Sustainable manufacturing company focusing on green technologies and energy-efficient production processes.	info@eco-green.sa	+966-11-678-9012	https://eco-green.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	energy	11-50	CR-1011678901	300678901200003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-446655440007	2024-08-10 11:10:11.997085+00	2025-07-11 11:10:11.997087+00	f	\N	Future Tech Manufacturing	تصنيع التقنيات المستقبلية	Technology-driven manufacturing company implementing AI, IoT, and blockchain solutions for Industry 4.0 transformation.	hello@future-tech.sa	+966-11-789-0123	https://future-tech.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	technology	51-200	CR-1011789012	300789012300003	\N	\N	active	\N	standard	10	50	10	t	f
550e8400-e29b-41d4-a716-446655440008	2024-08-10 11:10:11.997146+00	2025-07-11 11:10:11.997147+00	f	\N	Secure Supply Co.	شركة التوريد الآمن	Supply chain and logistics company utilizing advanced tracking systems and smart inventory management solutions.	info@secure-supply.sa	+966-11-890-1234	https://secure-supply.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	logistics	11-50	CR-1011890123	300890123400003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-446655440009	2024-08-10 11:10:11.997272+00	2025-07-11 11:10:11.997274+00	f	\N	Pharma Excellence Ltd	شركة التميز الدوائي المحدودة	Pharmaceutical manufacturing company implementing AI-powered quality inspection and automated production systems.	contact@pharma-excellence.sa	+966-12-901-2345	https://pharma-excellence.sa	Industrial Area, Mecca	\N	Mecca	Makkah Region	21955	SA	healthcare	101-200	CR-1012901234	300901234500003	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-44665544000a	2024-08-10 11:10:11.997332+00	2025-07-11 11:10:11.997333+00	f	\N	Safety First Industries	صناعات السلامة أولاً	Industrial safety equipment manufacturer focusing on smart monitoring systems and predictive safety analytics.	safety@safety-first.sa	+966-11-012-3456	https://safety-first.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	11-50	CR-1011012345	300012345600003	\N	\N	active	\N	standard	15	100	25	t	f
550e8400-e29b-41d4-a716-44665544000b	2024-08-10 11:10:11.997389+00	2025-07-11 11:10:11.997389+00	f	\N	Eastern Industries	الصناعات الشرقية	Diversified industrial conglomerate implementing digital transformation across multiple manufacturing sectors.	info@eastern-industries.sa	+966-13-123-4567	https://eastern-industries.sa	Industrial Area, Dammam	\N	Dammam	Eastern Province	31421	SA	manufacturing	1000+	CR-1013123456	300123456700004	\N	\N	active	\N	professional	500	5000	1000	t	f
550e8400-e29b-41d4-a716-44665544000c	2024-08-10 11:10:11.997437+00	2025-07-11 11:10:11.997438+00	f	\N	Red Sea Food Processing	معالجة أغذية البحر الأحمر	Seafood processing company utilizing advanced cold chain management and AI-powered quality control systems.	info@redsea-food.sa	+966-12-234-5678	https://redsea-food.sa	Industrial Area, Jeddah	\N	Jeddah	Makkah Region	21442	SA	manufacturing	51-100	CR-1012234567	300234567800004	\N	\N	active	\N	standard	25	200	50	t	f
550e8400-e29b-41d4-a716-44665544000d	2024-08-10 11:10:11.997572+00	2025-07-11 11:10:11.997573+00	f	\N	Capital Manufacturing Hub	مركز التصنيع الرأسمالي	Manufacturing hub providing shared smart manufacturing facilities and Industry 4.0 technologies to SMEs.	hub@capital-mfg.sa	+966-11-345-6789	https://capital-mfg.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	manufacturing	201-500	CR-1011345678	300345678900004	\N	\N	active	\N	professional	100	1000	200	t	f
550e8400-e29b-41d4-a716-44665544000e	2024-08-10 11:10:11.997625+00	2025-07-11 11:10:11.997626+00	f	\N	North Riyadh Logistics	لوجستيات شمال الرياض	Logistics and warehousing company implementing smart inventory management and automated material handling systems.	ops@north-riyadh-logistics.sa	+966-11-456-7890	https://north-riyadh-logistics.sa	Industrial Area, Riyadh	\N	Riyadh	Riyadh Region	13241	SA	logistics	101-200	CR-1011456789	300456789000004	\N	\N	active	\N	standard	50	500	100	t	f
550e8400-e29b-41d4-a716-44665544000f	2024-08-10 11:10:11.997687+00	2025-07-11 11:10:11.997688+00	f	\N	South Valley Industries	صناعات الوادي الجنوبي	Multi-sector manufacturing company specializing in process optimization and energy-efficient production technologies.	contact@south-valley.sa	+966-17-567-8901	https://south-valley.sa	Industrial Area, Abha	\N	Abha	Aseer Region	62521	SA	manufacturing	51-200	CR-1017567890	300567890100004	\N	\N	active	\N	standard	10	50	10	t	f
38c843b6-fdf6-4d6d-acce-294a373c3c80	2025-07-26 11:10:11.997757+00	2025-08-09 11:10:11.997757+00	f	\N	Innovation Startup Ltd	شركة الابتكار الناشئة المحدودة	Emerging technology startup exploring AI and IoT solutions for manufacturing.	hello@innovation-startup.sa	+966-11-000-0000	\N	Business District, Riyadh	\N	Riyadh	Riyadh Region	11564	SA	technology	1-10	\N	\N	\N	\N	trial	2025-09-09 11:10:11.997755+00	basic	5	25	5	t	f
5074b47f-2e05-48a3-91e3-d2f9e69a4339	2025-07-26 11:10:11.997814+00	2025-08-09 11:10:11.997815+00	f	\N	Green Manufacturing Co	شركة التصنيع الأخضر	Sustainable manufacturing company testing eco-friendly production methods.	info@green-mfg.sa	+966-11-000-0000	\N	Business District, Jeddah	\N	Jeddah	Makkah Region	11564	SA	energy	11-50	\N	\N	\N	\N	trial	2025-09-09 11:10:11.997813+00	standard	15	100	25	t	f
\.


--
-- Data for Name: user_invitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_invitations (id, created_at, updated_at, email, token, organization_id, invited_role, invited_by, status, first_name, last_name, job_title, department, expires_at, accepted_at, personal_message) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, created_at, updated_at, is_deleted, deleted_at, email, first_name, last_name, phone_number, profile_picture_url, role, status, organization_id, supertokens_user_id, email_verified, email_verified_at, bio, job_title, department, email_notifications_enabled, forum_notifications_enabled, message_notifications_enabled) FROM stdin;
450e8400-e29b-41d4-a716-446655440001	2024-10-14 11:10:12.028444+00	2025-08-06 11:10:12.028445+00	f	\N	sarah.ahmed@advanced-electronics.sa	Sarah	Ahmed	+966-14-769-8985	\N	member	active	550e8400-e29b-41d4-a716-446655440001	st-fcfbd78f64df4c68	t	2024-08-29 11:10:12.028439+00	Experienced production engineer specializing in smart manufacturing and IoT sensor integration.	Production Engineer	Manufacturing Operations	t	t	t
450e8400-e29b-41d4-a716-446655440002	2024-11-16 11:10:12.028656+00	2025-08-07 11:10:12.028657+00	f	\N	mohammed.rashid@precision-mfg.sa	Mohammed	Al-Rashid	+966-13-381-4676	\N	member	active	550e8400-e29b-41d4-a716-446655440005	st-675f20058db443de	t	2025-01-01 11:10:12.028653+00	IoT and automation specialist with 8+ years experience implementing industrial sensor networks.	IoT Specialist	Technology Solutions	t	t	t
450e8400-e29b-41d4-a716-446655440003	2025-02-26 11:10:12.028726+00	2025-07-16 11:10:12.028727+00	f	\N	fatima.hassan@arabian-food.sa	Fatima	Hassan	+966-11-468-7517	\N	member	active	550e8400-e29b-41d4-a716-446655440004	st-a81559aed69d4c3d	t	2025-01-28 11:10:12.028724+00	Quality control expert specializing in AI-powered inspection systems for food processing.	Quality Manager	Quality Assurance	t	t	t
450e8400-e29b-41d4-a716-446655440004	2025-01-29 11:10:12.028788+00	2025-08-09 11:10:12.028789+00	f	\N	ahmed.alzahrani@south-valley.sa	Ahmed	Al-Zahrani	+966-13-779-1054	\N	admin	active	550e8400-e29b-41d4-a716-44665544000f	st-825d11efaaba41f4	t	2025-04-27 11:10:12.028787+00	Factory owner and entrepreneur focused on digital transformation and team development.	Factory Owner	Executive Management	t	t	t
450e8400-e29b-41d4-a716-446655440005	2024-10-21 11:10:12.028843+00	2025-08-05 11:10:12.028844+00	f	\N	mohammed.shahri@gulf-plastics.com	Mohammed	Al-Shahri	+966-13-445-6740	\N	member	active	550e8400-e29b-41d4-a716-446655440002	st-c3e56914c56247a3	t	2024-08-23 11:10:12.028842+00	Operations manager with proven track record in predictive maintenance and cost reduction.	Operations Manager	Operations	t	t	t
450e8400-e29b-41d4-a716-446655440006	2025-01-07 11:10:12.028898+00	2025-08-04 11:10:12.028899+00	f	\N	fatima.otaibi@eastern-industries.sa	Fatima	Al-Otaibi	+966-11-227-5622	\N	admin	active	550e8400-e29b-41d4-a716-44665544000b	st-e951df482ab548a0	t	2024-08-22 11:10:12.028897+00	Factory owner specializing in electrical equipment manufacturing and smart inventory systems.	Factory Owner	Executive Management	t	t	t
450e8400-e29b-41d4-a716-446655440007	2025-01-21 11:10:12.02895+00	2025-08-09 11:10:12.028951+00	f	\N	khalid.ghamdi@pharma-excellence.sa	Khalid	Al-Ghamdi	+966-14-213-5543	\N	member	active	550e8400-e29b-41d4-a716-446655440009	st-61639f25613d4f99	t	2025-02-14 11:10:12.028949+00	Quality engineer with expertise in AI-powered quality inspection for pharmaceutical packaging.	Quality Engineer	Quality Control	t	t	t
450e8400-e29b-41d4-a716-446655440008	2025-05-08 11:10:12.029008+00	2025-07-22 11:10:12.029009+00	f	\N	ahmed.rasheed@saudi-steel.sa	Ahmed	Al-Rasheed	+966-17-205-3843	\N	member	active	550e8400-e29b-41d4-a716-446655440003	st-2978e2d529b64838	t	2024-08-31 11:10:12.029007+00	Plant manager overseeing steel production operations with focus on automation and robotics.	Plant Manager	Manufacturing Operations	t	t	t
450e8400-e29b-41d4-a716-446655440009	2025-05-03 11:10:12.029064+00	2025-08-05 11:10:12.029065+00	f	\N	sarah.mansouri@eco-green.sa	Sarah	Al-Mansouri	+966-14-314-2570	\N	member	active	550e8400-e29b-41d4-a716-446655440006	st-4083dde7258b4016	t	2025-01-17 11:10:12.029062+00	Sustainability-focused quality engineer implementing green manufacturing practices.	Quality Engineer	Quality Assurance	t	t	t
450e8400-e29b-41d4-a716-44665544000a	2024-12-20 11:10:12.029113+00	2025-08-06 11:10:12.029114+00	f	\N	mohammed.zahrani@future-tech.sa	Mohammed	Al-Zahrani	+966-12-213-6274	\N	member	active	550e8400-e29b-41d4-a716-446655440007	st-88c3021b4fe54a89	t	2024-11-04 11:10:12.029112+00	Operations director leading Industry 4.0 transformation initiatives and digital innovation.	Operations Director	Operations	t	t	t
450e8400-e29b-41d4-a716-44665544000b	2024-12-31 11:10:12.029175+00	2025-07-12 11:10:12.029176+00	f	\N	noura.alsaud@secure-supply.sa	Noura	Al-Saud	+966-17-418-8677	\N	member	active	550e8400-e29b-41d4-a716-446655440008	st-cc695df0a9a14342	t	2025-02-11 11:10:12.029174+00	Innovation leader driving smart logistics and supply chain technology adoption.	Innovation Lead	Research & Development	t	t	t
450e8400-e29b-41d4-a716-44665544000c	2025-05-21 11:10:12.029233+00	2025-08-02 11:10:12.029234+00	f	\N	omar.harthi@safety-first.sa	Omar	Al-Harthi	+966-13-726-2662	\N	member	active	550e8400-e29b-41d4-a716-44665544000a	st-1d61c6ee103d44ba	t	2024-08-21 11:10:12.029232+00	Technical director specializing in industrial safety systems and predictive analytics.	Technical Director	Engineering	t	t	t
450e8400-e29b-41d4-a716-44665544000d	2025-01-08 11:10:12.029282+00	2025-07-23 11:10:12.029282+00	f	\N	maryam.dosari@redsea-food.sa	Maryam	Al-Dosari	+966-13-505-9509	\N	member	active	550e8400-e29b-41d4-a716-44665544000c	st-66674b80d1d640c4	t	2025-03-02 11:10:12.029281+00	Sustainability manager focusing on eco-friendly food processing and cold chain optimization.	Sustainability Manager	Sustainability	t	t	t
450e8400-e29b-41d4-a716-44665544000e	2025-05-10 11:10:12.029333+00	2025-07-17 11:10:12.029334+00	f	\N	aisha.mutairi@capital-mfg.sa	Aisha	Al-Mutairi	+966-13-554-6475	\N	member	active	550e8400-e29b-41d4-a716-44665544000d	st-f7d44566028242f1	t	2025-06-05 11:10:12.029332+00	Quality manager promoting shared manufacturing excellence across SME community.	Quality Manager	Quality Assurance	t	t	t
450e8400-e29b-41d4-a716-44665544000f	2024-08-24 11:10:12.029383+00	2025-07-20 11:10:12.029385+00	f	\N	saud.otaishan@north-riyadh-logistics.sa	Saud	Al-Otaishan	+966-11-597-1195	\N	member	active	550e8400-e29b-41d4-a716-44665544000e	st-afc8635363e34c4e	t	2025-04-18 11:10:12.029382+00	Operations manager implementing smart warehousing and automated material handling systems.	Operations Manager	Operations	t	t	t
ae4b0d2a-0805-456b-9d73-64fb6449a7f1	2025-03-06 11:10:12.035023+00	2025-08-01 11:10:12.035026+00	f	\N	reem.alharbi@advanced-electronics.sa	Reem	Al-Harbi	+966-12-225-2285	\N	member	pending	550e8400-e29b-41d4-a716-446655440001	st-6200831553df480c	f	\N	Dedicated production engineer focused on implementing cutting-edge solutions in manufacturing operations.	Production Engineer	Manufacturing	f	t	t
03c413a1-9389-4cc1-9d45-73748108c60e	2025-02-10 11:10:12.035129+00	2025-08-05 11:10:12.03513+00	f	\N	hassan.alshehri@gulf-plastics-ind.sa	Hassan	Al-Shehri	+966-13-434-7959	\N	member	active	550e8400-e29b-41d4-a716-446655440002	st-6b881efa17784f23	t	2025-07-11 11:10:12.035126+00	Manufacturing Director with 10+ years of experience in operations. Passionate about driving innovation and operational excellence.	Manufacturing Director	Operations	t	f	t
7c8c8da0-89dc-4fcd-beb8-f84a88c33dc9	2025-01-31 11:10:12.035201+00	2025-08-09 11:10:12.035203+00	f	\N	lina.alqasemi@saudi-steel-works.sa	Lina	Al-Qasemi	+966-17-519-8789	\N	member	pending	550e8400-e29b-41d4-a716-446655440003	st-ff88e4681d8a4faa	f	\N	Process Manager leading process engineering initiatives with expertise in automation and smart manufacturing technologies.	Process Manager	Process Engineering	f	t	t
94f65c91-8fdf-433a-8509-dd8440410492	2025-05-03 11:10:12.035263+00	2025-08-09 11:10:12.035264+00	f	\N	faisal.alnajjar@arabian-food-proc.sa	Faisal	Al-Najjar	+966-12-619-9774	\N	member	active	550e8400-e29b-41d4-a716-446655440004	st-a5f8df6fcbc04ca6	t	2025-03-21 11:10:12.035261+00	Plant Engineer with 14+ years of experience in engineering. Passionate about driving innovation and operational excellence.	Plant Engineer	Engineering	f	t	t
c0a8176a-6a4e-4249-ac7a-8db4e8ff18dd	2025-06-19 11:10:12.035317+00	2025-07-29 11:10:12.035317+00	f	\N	nadia.alfaraj@precision-mfg.sa	Nadia	Al-Faraj	+966-12-360-1005	\N	member	active	550e8400-e29b-41d4-a716-446655440005	st-795d1df85a954bf5	t	2024-11-03 11:10:12.035315+00	Experienced quality specialist specializing in digital transformation and process optimization within quality control.	Quality Specialist	Quality Control	t	t	t
977cd72f-4e9a-4b35-95eb-99131683bdbb	2025-05-25 11:10:12.035366+00	2025-07-17 11:10:12.035367+00	f	\N	yousef.alhamad@e-green-ind.sa	Yousef	Al-Hamad	+966-12-327-9997	\N	member	active	550e8400-e29b-41d4-a716-446655440006	st-d507f8ba387b479b	t	2025-06-04 11:10:12.035364+00	Experienced automation engineer specializing in digital transformation and process optimization within engineering.	Automation Engineer	Engineering	t	t	t
1f21a75e-774d-4fd1-aa93-9ae6a625002b	2025-01-30 11:10:12.035415+00	2025-07-12 11:10:12.035415+00	f	\N	layla.alkhalil@future-tech-mfg.sa	Layla	Al-Khalil	+966-11-477-6076	\N	member	active	550e8400-e29b-41d4-a716-446655440007	st-6e92fc5e7c8d4c93	t	2024-11-01 11:10:12.035413+00	Data Analyst with 9+ years of experience in it & analytics. Passionate about driving innovation and operational excellence.	Data Analyst	IT & Analytics	f	f	t
9691f13b-ea45-434e-8fc9-06c80c6bfe0b	2025-06-20 11:10:12.03547+00	2025-07-27 11:10:12.035471+00	f	\N	tariq.alrashid@secure-supply.sa	Tariq	Al-Rashid	+966-13-393-5873	\N	member	active	550e8400-e29b-41d4-a716-446655440008	st-e7c59be431964833	t	2025-02-14 11:10:12.035468+00	Maintenance Manager leading maintenance initiatives with expertise in automation and smart manufacturing technologies.	Maintenance Manager	Maintenance	f	f	t
ec3c266b-95bd-401c-a1ac-c7a8b4b4148f	2025-04-29 11:10:12.035523+00	2025-08-06 11:10:12.035524+00	f	\N	hala.alsabah@pharma-excellence.sa	Hala	Al-Sabah	+966-17-638-5379	\N	member	active	550e8400-e29b-41d4-a716-446655440009	st-6e287223ba83478f	t	2025-04-01 11:10:12.035521+00	Experienced supply chain manager specializing in digital transformation and process optimization within logistics.	Supply Chain Manager	Logistics	f	f	f
4025ef63-2145-4a94-a017-d8c63fc206a6	2025-05-06 11:10:12.035574+00	2025-07-26 11:10:12.035575+00	f	\N	majid.althani@safety-first-ind.sa	Majid	Al-Thani	+966-12-426-1265	\N	member	active	550e8400-e29b-41d4-a716-44665544000a	st-84c742ce4b8f47bd	t	2025-04-29 11:10:12.035572+00	Safety Engineer with 14+ years of experience in safety & compliance. Passionate about driving innovation and operational excellence.	Safety Engineer	Safety & Compliance	f	t	t
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


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
-- Name: organizations organizations_registration_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_registration_number_key UNIQUE (registration_number);


--
-- Name: organizations organizations_tax_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_tax_id_key UNIQUE (tax_id);


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
-- Name: forum_topics forum_topics_best_answer_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_best_answer_post_id_fkey FOREIGN KEY (best_answer_post_id) REFERENCES public.forum_posts(id);


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
-- Name: forum_topics forum_topics_last_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_last_post_id_fkey FOREIGN KEY (last_post_id) REFERENCES public.forum_posts(id);


--
-- Name: forum_topics forum_topics_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.forum_topics
    ADD CONSTRAINT forum_topics_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: users users_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


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
public	1754823376962
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
public	s-3cf94759-2e9d-4f35-9a6d-ad78e74a06fd	MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoGNlpYCxZ8ZjV9HfvM10K02OWuMSSHnZUaAVj7GjYzpPQWKmI7uDH8OAkTWcnesyMcFMCxslCFY6wq035LlPmdMtYuh/jZnZHhMFW2lM6QKp0MOXuhMrNhNuab4VoYp0Z0ahw9MbUKJrbcHS/anDU5LnXZscQdg8+OvpxxVkOeSAYhBMHi6la5spNJgzc90AJSJK6FEMQfma7R08AnKs5TwiUZ2E2RS4Lz6pZr4RGvmg23AKOwWxuja2Lc0Zm1dqQxjM8bxpv1W4ymCubqEuqiCDf2Ajj3AzddIFw8ND4cSg6dshUyEVOr4PkHElbdQe9Q+/OQihBsNx7oWQetzOCQIDAQAB|MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCgY2WlgLFnxmNX0d+8zXQrTY5a4xJIedlRoBWPsaNjOk9BYqYju4Mfw4CRNZyd6zIxwUwLGyUIVjrCrTfkuU+Z0y1i6H+NmdkeEwVbaUzpAqnQw5e6Eys2E25pvhWhinRnRqHD0xtQomttwdL9qcNTkuddmxxB2Dz46+nHFWQ55IBiEEweLqVrmyk0mDNz3QAlIkroUQxB+ZrtHTwCcqzlPCJRnYTZFLgvPqlmvhEa+aDbcAo7BbG6NrYtzRmbV2pDGMzxvGm/VbjKYK5uoS6qIIN/YCOPcDN10gXDw0PhxKDp2yFTIRU6vg+QcSVt1B71D785CKEGw3HuhZB63M4JAgMBAAECggEAAbD2DzgSZtVhpKbtHdagf3ivGvXQu5x8v4WHIBr9gAC4517RbqzicSfyYzEImtMgA9/et1ZoS+tHtuo+QkiuP48SumAz944R+NLbPNG9y85bmQ8IFg4CHrY3B1hHt2YBbl44FpucfQ3TruQbH2Raz7beEP1D8fGESoGsDg2Vw8LJAr+J65872B0MHLjaM67KtqDp4IOkWHnMtSjn2v5RDo9PIZIcW7EpYXN9+zWjvCUU/aS7wp0u7w/TD+j3GsuLjtcqFZXJNbHxP3tYd4Gh/89YZa5sCpNVMVPBXmpuno+oJLxoCuvWr/Bk+ULTLvYktYoGaJTGYeNI4AwjvBZaYwKBgQC+QIQ4JzgoidDENRIg0zoli62N9zcnVPsLP8QxsZo89KHtezKr+UbA9EQ6uTNuE+oD+WJSdND3kh9saoAuFL4PFAgeDjD0FMri/dM0mRPOK1WxKi+NMDv2h+eX8OG7rbyvs6hijOEDGI9jGJtWBMJqFS+EM7oYbW/SBk2w7/T5BwKBgQDX0No7K/U68o2w8bmKAHMvYVBagtXkJCmYtwsH3a5SI4jUsz3rBPkzaVSNsZJUrh4WzmqniAvGol9fParmezf8LpzDdi5RNh14h4KsPgg6d5LINxeotaR2DNBR3yBVvyJupSca/423kGkhLaMATuKSMoDBh71Bag9rVyjK2KOMbwKBgBRktAeU5Kcrxq4RhkTwf24g39S06DuWF2boSe6NvBvGmUjsiMz4ZoYuaNXmnkWxasdMRybRkMjI6AdmDyFhZdIV8pzOJp8zT2AvlyEvO3lBGelovTokLnlJriCSWJAWmoA3ANi3gzMiwdP8gkIhNnnKlZJVPSB7Mp5PwKozvo2nAoGAL8gv6RXsb6awNFLwj1tWJVFYZxG8pYxUIVm1eYJdTBZN/znIJbauLfHOJKkCCvmZ89azym/Wm53rm7ydj/YMCSuQzb3mt1hR4hOunNAHJlq/BtEbzeCZjwF7RgUutY1h5DlwlQurps60WAIwqqrMgy3nT/HrtwXycAOWJoMcgsUCgYB/Sot6cbYU2g4zLFoyue+HUo4I+3bS19LtfomHrQO1QJi0ZDI19/1W2q1xRMw6DYU4aeRu8AC/AY64U5GI8ntmX2AzZPcVtKDcnZFrV/SGqeUWgBme6TIb/Glpf/z56ArlO8X3qX8KIU27ed4dLdwtWN/pM4w2pEBv7Po+/gL8eA==	RS256	1754823377223
\.


--
-- Data for Name: key_value; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.key_value (app_id, tenant_id, name, value, created_at_time) FROM stdin;
public	public	refresh_token_key	1000:a2b6b915a197eb6c79b6220bbe183b7a7c4995c76affdaab1ae0dfb38915d18b8643d7d9a74390c008e40f4d5374809b507d2432cc2b04ce9f7ab60700470fe5:62af9e93d5df6e018a699c822278cd6266d47dc7ec47c8de9bae6fddd09ec719e1128f783f4be1918c3457384183fde423062dfa2675435f72c3307933126327	1754823377216
public	public	TELEMETRY_ID	3a20ad5b-f70b-4fd4-b3a3-20a1355cb843	1754823377352
public	public	websiteDomain	http://localhost:5173	1754823430822
public	public	apiDomain	http://localhost:8000	1754823430825
public	public	FEATURE_FLAG	[]	1754824035129
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
public	1754823377182	MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0liyDlbv6k6OpUSTiEi97Mt/WjMQ9ctN67hj5f/fGj27zeNjDud1YkmIzuvrntQe0fZdTC9cvIIJ2S6Y4gJ0qTY0p5lINF+3Ipx6K+p90V7CXattL0J4W7P8qS2Y49Kj/U+2TOGbYdNNSnV5jqw/O3O9cV/e56OCgCF9SRZJ8MgFLAuGPmgYVRUqzEKb0R2c2Ref781vazc5rUhZWM5Qy6vaOLSwycmQp9XttvlRvXhMr//ULJd23krpf2he5g6rqW+pYLPuug9IcKAY04uPnrk/OM3z8siePauHHdQ8RrUemHuV//FrI3gmFdKlf5kvgfhURHSYGnCwfV+uBsbo7wIDAQAB|MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDSWLIOVu/qTo6lRJOISL3sy39aMxD1y03ruGPl/98aPbvN42MO53ViSYjO6+ue1B7R9l1ML1y8ggnZLpjiAnSpNjSnmUg0X7cinHor6n3RXsJdq20vQnhbs/ypLZjj0qP9T7ZM4Zth001KdXmOrD87c71xX97no4KAIX1JFknwyAUsC4Y+aBhVFSrMQpvRHZzZF5/vzW9rNzmtSFlYzlDLq9o4tLDJyZCn1e22+VG9eEyv/9Qsl3beSul/aF7mDqupb6lgs+66D0hwoBjTi4+euT84zfPyyJ49q4cd1DxGtR6Ye5X/8WsjeCYV0qV/mS+B+FREdJgacLB9X64GxujvAgMBAAECggEALhnRYHIuX9h6y/71JLPoqErLbR3vFCfMOqLthh2nrI0mKZAyCDSzVejO6qbrO6K65IKN3SIuPYR0mxxq1nH6VpGyRZ9DI3Ns5FGONyzMCYSura/iHK8BSPvwHrYHIbtrRJvhVQVHNFAGyxBnJV1b+HA772q3JGaCNgng9xFDAFm4gPMoatDZpmB+tyqog5H1w022DgMr/TuWRIiFKvVClNTpWv/CoeKaqhrjmuZEmtTdnitPNSxMBQELPZ6fVtN6Pez0JbmeVR+cyaGmwkDqLvIwt/iW1BJV8FqijMkjcbeyViM1msmvpAk874v87grWi0BQcr5R48LOJMRS5+MUAQKBgQDvHapi9QjwtqAcsCwm3ACC8onZdmcEGB+3WUdcQj10IeP3y+Ui/eC1iBDSLOCRdBN9F6oQwOB2p/y0aOr8XXXyOUfLcw2wKpb5OHGYvh6Vh6/n+9cWshbRx1mCH2bCOK3cAor6RelYJ9i+i2452C/dc1jZGy8zJiY82l76zZDUAQKBgQDhMvwjNPWrk3nJFBr0NZRrf5B4FbrmZxZ7+NxuHyhmo1HyV7BBIyzrwhLf0YiJX1WZlPxP6RcgIK9kPpW/5mk1CHnjCApa2Z1LLZ9kk15WI5zimhMpao7GwWX0yQke23iWHa29velpOWYxen7cfZN/PJmNKU+T6pLnWdlYC+D87wKBgQCpql0KFmAfnRYDBSZu9FAQmlQhz5fNGej3SgwOdJnyW1HMtAqER6w4YrG80EcQLlLdwfrUJGehChWPVZrXMuHL28ULoTmnNLEnaVuBS/WbmEnCy7mUywzSESd74xgg2+LRZ6SBbTXjbXKn0XuG49UixwPWGSnmmz0qlLAsOcx4AQKBgHDcyYqnhxwnPBjvb5bGp4y8kN3uHg5MyfL1xRuXl/rgjThEhDwQ8flx+V2cuK4ITnE7PryZ2BIs71nxF8HmKwH+Ln/+zpm7iF5eDg0s4lGPZZgXmdTe55Fq6bslaeHCIowxcZqvbCRlNPdFKgE9GkfhSh95/bznChrSZ9/9jBOXAoGANpqmtfoMBShd1WCcdvpUNgVkNBKjFm9on17lDKwlOZdCnsOf1YqoMhQfNYtWyikSAvflhAA9+ePU4obcpCCSvrnvh+3b/XuFhA2hew/71h/0PY4YLBeet2t3ct3oU4pQjuKwsD8R1TSCSFtHwDmx8t6LJMbwdCmxuRoU4n4HWgs=
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
public	public	1754823376962
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

