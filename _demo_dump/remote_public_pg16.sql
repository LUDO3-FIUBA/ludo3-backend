--
-- PostgreSQL database dump
--

\restrict YgIaQRpdUEhlUvuHxmppPIaOjJNtgt2gehvxlX5Dc1064AaGmBcDPVkeqs1huYW

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.10

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
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: backend_academiccalendarevent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_academiccalendarevent (
    id bigint NOT NULL,
    name character varying(200) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    category character varying(20) NOT NULL,
    year integer NOT NULL,
    is_deadline boolean NOT NULL
);


--
-- Name: backend_academiccalendarevent_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_academiccalendarevent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_academiccalendarevent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_academiccalendarevent_id_seq OWNED BY public.backend_academiccalendarevent.id;


--
-- Name: backend_attendance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_attendance (
    id bigint NOT NULL,
    submitted_at timestamp with time zone NOT NULL,
    qr_code_id bigint NOT NULL,
    semester_id bigint NOT NULL,
    student_id bigint NOT NULL,
    latitude double precision,
    location_valid boolean,
    longitude double precision
);


--
-- Name: backend_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_attendance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_attendance_id_seq OWNED BY public.backend_attendance.id;


--
-- Name: backend_attendanceqrcode; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_attendanceqrcode (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    qrid uuid NOT NULL,
    owner_teacher_id bigint NOT NULL,
    semester_id bigint NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    campus character varying(20),
    mode character varying(11) NOT NULL
);


--
-- Name: backend_attendanceqrcode_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_attendanceqrcode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_attendanceqrcode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_attendanceqrcode_id_seq OWNED BY public.backend_attendanceqrcode.id;


--
-- Name: backend_auditlog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_auditlog (
    id bigint NOT NULL,
    log text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    related_user_id bigint,
    user_id bigint NOT NULL
);


--
-- Name: backend_auditlog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_auditlog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_auditlog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_auditlog_id_seq OWNED BY public.backend_auditlog.id;


--
-- Name: backend_authidentity; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_authidentity (
    id bigint NOT NULL,
    provider character varying(32) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    email character varying(254) NOT NULL,
    added_at timestamp with time zone NOT NULL,
    last_used_at timestamp with time zone,
    user_id bigint NOT NULL
);


--
-- Name: backend_authidentity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_authidentity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_authidentity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_authidentity_id_seq OWNED BY public.backend_authidentity.id;


--
-- Name: backend_calendareventreminder; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_calendareventreminder (
    id bigint NOT NULL,
    days_before integer NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    event_id bigint NOT NULL,
    notification_id bigint NOT NULL
);


--
-- Name: backend_calendareventreminder_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_calendareventreminder_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_calendareventreminder_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_calendareventreminder_id_seq OWNED BY public.backend_calendareventreminder.id;


--
-- Name: backend_career; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_career (
    id bigint NOT NULL,
    siu_id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: backend_career_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_career_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_career_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_career_id_seq OWNED BY public.backend_career.id;


--
-- Name: backend_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_catalog (
    id bigint NOT NULL,
    catalog_key character varying(100) NOT NULL,
    catalog_name character varying(200) NOT NULL,
    catalog_description text
);


--
-- Name: backend_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_catalog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_catalog_id_seq OWNED BY public.backend_catalog.id;


--
-- Name: backend_catalogitem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_catalogitem (
    id bigint NOT NULL,
    catalog_item_value character varying(100) NOT NULL,
    catalog_item_label character varying(200) NOT NULL,
    catalog_item_order integer,
    catalog_item_active boolean NOT NULL,
    catalog_id bigint NOT NULL
);


--
-- Name: backend_catalogitem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_catalogitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_catalogitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_catalogitem_id_seq OWNED BY public.backend_catalogitem.id;


--
-- Name: backend_catedracalendarentry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_catedracalendarentry (
    id integer NOT NULL,
    date date NOT NULL,
    class_number integer,
    topic character varying(500) NOT NULL,
    entry_type character varying(20) NOT NULL,
    links jsonb NOT NULL,
    notes text NOT NULL,
    semester_id integer NOT NULL
);


--
-- Name: backend_catedracalendarentry_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_catedracalendarentry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_catedracalendarentry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_catedracalendarentry_id_seq OWNED BY public.backend_catedracalendarentry.id;


--
-- Name: backend_commission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_commission (
    id bigint NOT NULL,
    subject_siu_id integer NOT NULL,
    subject_name character varying(100) NOT NULL,
    siu_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    chief_teacher_id bigint NOT NULL,
    chief_teacher_grader_weight double precision NOT NULL,
    department_id bigint
);


--
-- Name: backend_commission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_commission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_commission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_commission_id_seq OWNED BY public.backend_commission.id;


--
-- Name: backend_commissioninscription; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_commissioninscription (
    id bigint NOT NULL,
    status character varying(1) NOT NULL,
    semester_id bigint NOT NULL,
    student_id bigint NOT NULL
);


--
-- Name: backend_commissioninscription_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_commissioninscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_commissioninscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_commissioninscription_id_seq OWNED BY public.backend_commissioninscription.id;


--
-- Name: backend_contact; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_contact (
    id bigint NOT NULL,
    status character varying(1) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    from_student_id bigint NOT NULL,
    to_student_id bigint NOT NULL
);


--
-- Name: backend_contact_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_contact ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_contact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_department; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_department (
    id bigint NOT NULL,
    name character varying(200) NOT NULL,
    location character varying(300) NOT NULL,
    schedule text NOT NULL,
    contact_info text NOT NULL,
    procedures text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: backend_department_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_department_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_department_id_seq OWNED BY public.backend_department.id;


--
-- Name: backend_evaluation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_evaluation (
    id bigint NOT NULL,
    evaluation_name character varying(100) NOT NULL,
    is_graded boolean NOT NULL,
    passing_grade integer,
    start_date timestamp with time zone,
    end_date timestamp with time zone NOT NULL,
    semester_id bigint NOT NULL,
    parent_evaluation_id bigint,
    requires_identity boolean NOT NULL,
    requires_qr boolean NOT NULL,
    is_gradeable boolean NOT NULL,
    description text
);


--
-- Name: backend_evaluation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_evaluation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_evaluation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_evaluation_id_seq OWNED BY public.backend_evaluation.id;


--
-- Name: backend_evaluationsubmission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_evaluationsubmission (
    id bigint NOT NULL,
    grade integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    evaluation_id bigint NOT NULL,
    student_id bigint NOT NULL,
    grader_id bigint,
    submission_text text,
    submission_status character varying(12),
    submission_file character varying(100),
    feedback_text text,
    original_filename character varying(255)
);


--
-- Name: backend_evaluationsubmission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_evaluationsubmission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_evaluationsubmission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_evaluationsubmission_id_seq OWNED BY public.backend_evaluationsubmission.id;


--
-- Name: backend_final; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_final (
    id bigint NOT NULL,
    date timestamp with time zone NOT NULL,
    qrid uuid NOT NULL,
    siu_id integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    teacher_id bigint NOT NULL,
    status character varying(2) NOT NULL,
    subject_siu_id integer NOT NULL,
    act character varying(10),
    subject_name character varying(100) NOT NULL
);


--
-- Name: backend_final_commissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_final_commissions (
    id integer NOT NULL,
    final_id bigint NOT NULL,
    commission_id bigint NOT NULL
);


--
-- Name: backend_final_commissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_final_commissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_final_commissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_final_commissions_id_seq OWNED BY public.backend_final_commissions.id;


--
-- Name: backend_final_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_final_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_final_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_final_id_seq OWNED BY public.backend_final.id;


--
-- Name: backend_finalexam; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_finalexam (
    id bigint NOT NULL,
    grade integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    final_id bigint NOT NULL,
    student_id bigint NOT NULL
);


--
-- Name: backend_finalexam_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_finalexam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_finalexam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_finalexam_id_seq OWNED BY public.backend_finalexam.id;


--
-- Name: backend_form; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_form (
    id bigint NOT NULL,
    form_name character varying(100) NOT NULL,
    form_description character varying(300) NOT NULL,
    form_information text,
    created_at timestamp with time zone NOT NULL,
    form_type_id bigint NOT NULL,
    requires_teacher_validation boolean NOT NULL,
    ownership_group_id integer NOT NULL
);


--
-- Name: backend_form_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_form_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_form_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_form_id_seq OWNED BY public.backend_form.id;


--
-- Name: backend_formanswer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formanswer (
    id bigint NOT NULL,
    answer_value text,
    field_id bigint NOT NULL,
    submission_id bigint NOT NULL
);


--
-- Name: backend_formanswer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formanswer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formanswer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formanswer_id_seq OWNED BY public.backend_formanswer.id;


--
-- Name: backend_formdocumentsource; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formdocumentsource (
    form_id bigint NOT NULL,
    form_document_source character varying(500) NOT NULL
);


--
-- Name: backend_formfield; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formfield (
    id bigint NOT NULL,
    form_field_label character varying(200) NOT NULL,
    form_field_require boolean NOT NULL,
    form_field_order integer NOT NULL,
    catalog_id bigint,
    form_id bigint NOT NULL,
    form_field_type_id bigint NOT NULL
);


--
-- Name: backend_formfield_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formfield_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formfield_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formfield_id_seq OWNED BY public.backend_formfield.id;


--
-- Name: backend_formfieldoption; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formfieldoption (
    id bigint NOT NULL,
    form_option_value character varying(100) NOT NULL,
    form_option_label character varying(200) NOT NULL,
    form_field_id bigint NOT NULL
);


--
-- Name: backend_formfieldoption_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formfieldoption_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formfieldoption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formfieldoption_id_seq OWNED BY public.backend_formfieldoption.id;


--
-- Name: backend_formfieldtype; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formfieldtype (
    id bigint NOT NULL,
    form_field_type_value character varying(100) NOT NULL
);


--
-- Name: backend_formfieldtype_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formfieldtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formfieldtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formfieldtype_id_seq OWNED BY public.backend_formfieldtype.id;


--
-- Name: backend_formownershipgroup; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formownershipgroup (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: backend_formownershipgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_formownershipgroup ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_formownershipgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_formownershipmember; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formownershipmember (
    id integer NOT NULL,
    entity_type character varying(20) NOT NULL,
    entity_id integer NOT NULL,
    is_editor boolean NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: backend_formownershipmember_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_formownershipmember ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_formownershipmember_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_formsubmission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formsubmission (
    id bigint NOT NULL,
    submitted_at timestamp with time zone NOT NULL,
    form_id bigint NOT NULL,
    user_id bigint NOT NULL,
    status_id bigint NOT NULL,
    teacher_id bigint,
    teacher_status character varying(20),
    teacher_comment text,
    recipient_entity_type character varying(20),
    recipient_entity_id integer
);


--
-- Name: backend_formsubmission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formsubmission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formsubmission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formsubmission_id_seq OWNED BY public.backend_formsubmission.id;


--
-- Name: backend_formsubmissionstatus; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formsubmissionstatus (
    id bigint NOT NULL,
    form_submission_status_value character varying(50) NOT NULL
);


--
-- Name: backend_formsubmissionstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formsubmissionstatus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formsubmissionstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formsubmissionstatus_id_seq OWNED BY public.backend_formsubmissionstatus.id;


--
-- Name: backend_formtype; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_formtype (
    id bigint NOT NULL,
    form_type_value character varying(100) NOT NULL
);


--
-- Name: backend_formtype_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_formtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_formtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_formtype_id_seq OWNED BY public.backend_formtype.id;


--
-- Name: backend_groupmembership; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_groupmembership (
    id bigint NOT NULL,
    status character varying(1) NOT NULL,
    joined_at timestamp with time zone NOT NULL,
    group_id bigint NOT NULL,
    student_id bigint NOT NULL
);


--
-- Name: backend_groupmembership_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_groupmembership ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_groupmembership_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_news; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_news (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    tag character varying(50) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    author_id bigint,
    image character varying(100),
    department_id bigint
);


--
-- Name: backend_news_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_news_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_news_id_seq OWNED BY public.backend_news.id;


--
-- Name: backend_notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_notification (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    sender_id bigint,
    is_urgent boolean DEFAULT false NOT NULL,
    send_push boolean DEFAULT false NOT NULL,
    send_email boolean DEFAULT false NOT NULL,
    image character varying(100),
    semester_id bigint,
    action_url character varying(200),
    department_id bigint
);


--
-- Name: backend_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_notification_id_seq OWNED BY public.backend_notification.id;


--
-- Name: backend_passwordresetotp; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_passwordresetotp (
    id bigint NOT NULL,
    code_hash character varying(64) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    attempts smallint NOT NULL,
    max_attempts smallint NOT NULL,
    is_used boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    user_id bigint NOT NULL,
    CONSTRAINT backend_passwordresetotp_attempts_check CHECK ((attempts >= 0)),
    CONSTRAINT backend_passwordresetotp_max_attempts_check CHECK ((max_attempts >= 0))
);


--
-- Name: backend_passwordresetotp_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_passwordresetotp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_passwordresetotp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_passwordresetotp_id_seq OWNED BY public.backend_passwordresetotp.id;


--
-- Name: backend_secretary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_secretary (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    location character varying(300) NOT NULL,
    schedule text NOT NULL,
    contact_info text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    parent_secretary_id integer
);


--
-- Name: backend_secretary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_secretary ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_secretary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_semester; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_semester (
    id bigint NOT NULL,
    year_moment character varying(2) NOT NULL,
    start_date timestamp with time zone NOT NULL,
    commission_id bigint NOT NULL,
    classes_amount integer,
    minimum_attendance double precision,
    calendar_source_url character varying(500)
);


--
-- Name: backend_semester_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_semester_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_semester_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_semester_id_seq OWNED BY public.backend_semester.id;


--
-- Name: backend_semesterschedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_semesterschedule (
    id bigint NOT NULL,
    day_of_week integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    semester_id bigint NOT NULL
);


--
-- Name: backend_semesterschedule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_semesterschedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_semesterschedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_semesterschedule_id_seq OWNED BY public.backend_semesterschedule.id;


--
-- Name: backend_staff; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_staff (
    user_id bigint NOT NULL,
    department_siu_id integer NOT NULL,
    department_id bigint,
    is_bedelia boolean NOT NULL,
    secretary_id integer,
    CONSTRAINT staff_department_or_secretary_not_both CHECK (((department_id IS NULL) OR (secretary_id IS NULL)))
);


--
-- Name: backend_student; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_student (
    user_id bigint NOT NULL,
    padron character varying(7) NOT NULL,
    inscripto boolean NOT NULL,
    face_encodings double precision[] NOT NULL,
    image character varying(120)
);


--
-- Name: backend_studentcareer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_studentcareer (
    id bigint NOT NULL,
    plan character varying(50) NOT NULL,
    enrollment_date date,
    graduation_date date,
    career_id bigint NOT NULL,
    student_id bigint NOT NULL
);


--
-- Name: backend_studentcareer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_studentcareer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_studentcareer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_studentcareer_id_seq OWNED BY public.backend_studentcareer.id;


--
-- Name: backend_studygroup; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_studygroup (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    creator_id bigint NOT NULL
);


--
-- Name: backend_studygroup_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.backend_studygroup ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.backend_studygroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: backend_teacher; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_teacher (
    user_id bigint NOT NULL,
    legajo character varying(8) NOT NULL,
    face_encodings double precision[] NOT NULL,
    siu_id integer NOT NULL
);


--
-- Name: backend_teacherrole; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_teacherrole (
    id bigint NOT NULL,
    role character varying(30) NOT NULL,
    commission_id bigint NOT NULL,
    teacher_id bigint NOT NULL,
    grader_weight double precision NOT NULL
);


--
-- Name: backend_teacherrole_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_teacherrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_teacherrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_teacherrole_id_seq OWNED BY public.backend_teacherrole.id;


--
-- Name: backend_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_user (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    is_student boolean NOT NULL,
    is_teacher boolean NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    username character varying(30) NOT NULL,
    dni character varying(9) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    github_url character varying(255) NOT NULL,
    linkedin_url character varying(255) NOT NULL,
    profile_photo character varying(500)
);


--
-- Name: backend_user_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_user_groups (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: backend_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_user_groups_id_seq OWNED BY public.backend_user_groups.id;


--
-- Name: backend_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_user_id_seq OWNED BY public.backend_user.id;


--
-- Name: backend_user_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_user_user_permissions (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: backend_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_user_user_permissions_id_seq OWNED BY public.backend_user_user_permissions.id;


--
-- Name: backend_usernotification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.backend_usernotification (
    id bigint NOT NULL,
    is_read boolean NOT NULL,
    notification_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: backend_usernotification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.backend_usernotification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: backend_usernotification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.backend_usernotification_id_seq OWNED BY public.backend_usernotification.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: push_notifications_apnsdevice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_notifications_apnsdevice (
    id integer NOT NULL,
    name character varying(255),
    active boolean NOT NULL,
    date_created timestamp with time zone,
    device_id uuid,
    registration_id character varying(200) NOT NULL,
    user_id bigint,
    application_id character varying(64)
);


--
-- Name: push_notifications_apnsdevice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.push_notifications_apnsdevice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: push_notifications_apnsdevice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.push_notifications_apnsdevice_id_seq OWNED BY public.push_notifications_apnsdevice.id;


--
-- Name: push_notifications_gcmdevice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_notifications_gcmdevice (
    id integer NOT NULL,
    name character varying(255),
    active boolean NOT NULL,
    date_created timestamp with time zone,
    device_id bigint,
    registration_id text NOT NULL,
    user_id bigint,
    cloud_message_type character varying(3) NOT NULL,
    application_id character varying(64)
);


--
-- Name: push_notifications_gcmdevice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.push_notifications_gcmdevice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: push_notifications_gcmdevice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.push_notifications_gcmdevice_id_seq OWNED BY public.push_notifications_gcmdevice.id;


--
-- Name: push_notifications_webpushdevice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_notifications_webpushdevice (
    id integer NOT NULL,
    name character varying(255),
    active boolean NOT NULL,
    date_created timestamp with time zone,
    application_id character varying(64),
    registration_id text NOT NULL,
    p256dh character varying(88) NOT NULL,
    auth character varying(24) NOT NULL,
    browser character varying(10) NOT NULL,
    user_id bigint
);


--
-- Name: push_notifications_webpushdevice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.push_notifications_webpushdevice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: push_notifications_webpushdevice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.push_notifications_webpushdevice_id_seq OWNED BY public.push_notifications_webpushdevice.id;


--
-- Name: push_notifications_wnsdevice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.push_notifications_wnsdevice (
    id integer NOT NULL,
    name character varying(255),
    active boolean NOT NULL,
    date_created timestamp with time zone,
    device_id uuid,
    registration_id text NOT NULL,
    user_id bigint,
    application_id character varying(64)
);


--
-- Name: push_notifications_wnsdevice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.push_notifications_wnsdevice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: push_notifications_wnsdevice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.push_notifications_wnsdevice_id_seq OWNED BY public.push_notifications_wnsdevice.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: backend_academiccalendarevent id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_academiccalendarevent ALTER COLUMN id SET DEFAULT nextval('public.backend_academiccalendarevent_id_seq'::regclass);


--
-- Name: backend_attendance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendance ALTER COLUMN id SET DEFAULT nextval('public.backend_attendance_id_seq'::regclass);


--
-- Name: backend_attendanceqrcode id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendanceqrcode ALTER COLUMN id SET DEFAULT nextval('public.backend_attendanceqrcode_id_seq'::regclass);


--
-- Name: backend_auditlog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_auditlog ALTER COLUMN id SET DEFAULT nextval('public.backend_auditlog_id_seq'::regclass);


--
-- Name: backend_authidentity id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity ALTER COLUMN id SET DEFAULT nextval('public.backend_authidentity_id_seq'::regclass);


--
-- Name: backend_calendareventreminder id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_calendareventreminder ALTER COLUMN id SET DEFAULT nextval('public.backend_calendareventreminder_id_seq'::regclass);


--
-- Name: backend_career id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_career ALTER COLUMN id SET DEFAULT nextval('public.backend_career_id_seq'::regclass);


--
-- Name: backend_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalog ALTER COLUMN id SET DEFAULT nextval('public.backend_catalog_id_seq'::regclass);


--
-- Name: backend_catalogitem id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalogitem ALTER COLUMN id SET DEFAULT nextval('public.backend_catalogitem_id_seq'::regclass);


--
-- Name: backend_catedracalendarentry id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catedracalendarentry ALTER COLUMN id SET DEFAULT nextval('public.backend_catedracalendarentry_id_seq'::regclass);


--
-- Name: backend_commission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commission ALTER COLUMN id SET DEFAULT nextval('public.backend_commission_id_seq'::regclass);


--
-- Name: backend_commissioninscription id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commissioninscription ALTER COLUMN id SET DEFAULT nextval('public.backend_commissioninscription_id_seq'::regclass);


--
-- Name: backend_department id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_department ALTER COLUMN id SET DEFAULT nextval('public.backend_department_id_seq'::regclass);


--
-- Name: backend_evaluation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluation ALTER COLUMN id SET DEFAULT nextval('public.backend_evaluation_id_seq'::regclass);


--
-- Name: backend_evaluationsubmission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission ALTER COLUMN id SET DEFAULT nextval('public.backend_evaluationsubmission_id_seq'::regclass);


--
-- Name: backend_final id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final ALTER COLUMN id SET DEFAULT nextval('public.backend_final_id_seq'::regclass);


--
-- Name: backend_final_commissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final_commissions ALTER COLUMN id SET DEFAULT nextval('public.backend_final_commissions_id_seq'::regclass);


--
-- Name: backend_finalexam id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_finalexam ALTER COLUMN id SET DEFAULT nextval('public.backend_finalexam_id_seq'::regclass);


--
-- Name: backend_form id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_form ALTER COLUMN id SET DEFAULT nextval('public.backend_form_id_seq'::regclass);


--
-- Name: backend_formanswer id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formanswer ALTER COLUMN id SET DEFAULT nextval('public.backend_formanswer_id_seq'::regclass);


--
-- Name: backend_formfield id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfield ALTER COLUMN id SET DEFAULT nextval('public.backend_formfield_id_seq'::regclass);


--
-- Name: backend_formfieldoption id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfieldoption ALTER COLUMN id SET DEFAULT nextval('public.backend_formfieldoption_id_seq'::regclass);


--
-- Name: backend_formfieldtype id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfieldtype ALTER COLUMN id SET DEFAULT nextval('public.backend_formfieldtype_id_seq'::regclass);


--
-- Name: backend_formsubmission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission ALTER COLUMN id SET DEFAULT nextval('public.backend_formsubmission_id_seq'::regclass);


--
-- Name: backend_formsubmissionstatus id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmissionstatus ALTER COLUMN id SET DEFAULT nextval('public.backend_formsubmissionstatus_id_seq'::regclass);


--
-- Name: backend_formtype id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formtype ALTER COLUMN id SET DEFAULT nextval('public.backend_formtype_id_seq'::regclass);


--
-- Name: backend_news id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_news ALTER COLUMN id SET DEFAULT nextval('public.backend_news_id_seq'::regclass);


--
-- Name: backend_notification id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_notification ALTER COLUMN id SET DEFAULT nextval('public.backend_notification_id_seq'::regclass);


--
-- Name: backend_passwordresetotp id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_passwordresetotp ALTER COLUMN id SET DEFAULT nextval('public.backend_passwordresetotp_id_seq'::regclass);


--
-- Name: backend_semester id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semester ALTER COLUMN id SET DEFAULT nextval('public.backend_semester_id_seq'::regclass);


--
-- Name: backend_semesterschedule id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semesterschedule ALTER COLUMN id SET DEFAULT nextval('public.backend_semesterschedule_id_seq'::regclass);


--
-- Name: backend_studentcareer id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studentcareer ALTER COLUMN id SET DEFAULT nextval('public.backend_studentcareer_id_seq'::regclass);


--
-- Name: backend_teacherrole id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacherrole ALTER COLUMN id SET DEFAULT nextval('public.backend_teacherrole_id_seq'::regclass);


--
-- Name: backend_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user ALTER COLUMN id SET DEFAULT nextval('public.backend_user_id_seq'::regclass);


--
-- Name: backend_user_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_groups ALTER COLUMN id SET DEFAULT nextval('public.backend_user_groups_id_seq'::regclass);


--
-- Name: backend_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.backend_user_user_permissions_id_seq'::regclass);


--
-- Name: backend_usernotification id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_usernotification ALTER COLUMN id SET DEFAULT nextval('public.backend_usernotification_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: push_notifications_apnsdevice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_apnsdevice ALTER COLUMN id SET DEFAULT nextval('public.push_notifications_apnsdevice_id_seq'::regclass);


--
-- Name: push_notifications_gcmdevice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_gcmdevice ALTER COLUMN id SET DEFAULT nextval('public.push_notifications_gcmdevice_id_seq'::regclass);


--
-- Name: push_notifications_webpushdevice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_webpushdevice ALTER COLUMN id SET DEFAULT nextval('public.push_notifications_webpushdevice_id_seq'::regclass);


--
-- Name: push_notifications_wnsdevice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_wnsdevice ALTER COLUMN id SET DEFAULT nextval('public.push_notifications_wnsdevice_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add user	1	add_user
2	Can change user	1	change_user
3	Can delete user	1	delete_user
4	Can view user	1	view_user
5	Can add Final	2	add_final
6	Can change Final	2	change_final
7	Can delete Final	2	delete_final
8	Can view Final	2	view_final
9	Can add Estudiante	3	add_student
10	Can change Estudiante	3	change_student
11	Can delete Estudiante	3	delete_student
12	Can view Estudiante	3	view_student
13	Can add Docentes	4	add_teacher
14	Can change Docentes	4	change_teacher
15	Can delete Docentes	4	delete_teacher
16	Can view Docentes	4	view_teacher
17	Can add Exámen final	5	add_finalexam
18	Can change Exámen final	5	change_finalexam
19	Can delete Exámen final	5	delete_finalexam
20	Can view Exámen final	5	view_finalexam
21	Can add Estudiante pre registrado	6	add_preregisteredstudent
22	Can change Estudiante pre registrado	6	change_preregisteredstudent
23	Can delete Estudiante pre registrado	6	delete_preregisteredstudent
24	Can view Estudiante pre registrado	6	view_preregisteredstudent
25	Can add Fecha para aprobar	7	add_finaltoapprove
26	Can change Fecha para aprobar	7	change_finaltoapprove
27	Can delete Fecha para aprobar	7	delete_finaltoapprove
28	Can view Fecha para aprobar	7	view_finaltoapprove
29	Can add Usuario Administrador	8	add_staffuser
30	Can change Usuario Administrador	8	change_staffuser
31	Can delete Usuario Administrador	8	delete_staffuser
32	Can view Usuario Administrador	8	view_staffuser
33	Can add Usuario Administrador	9	add_staff
34	Can change Usuario Administrador	9	change_staff
35	Can delete Usuario Administrador	9	delete_staff
36	Can view Usuario Administrador	9	view_staff
37	Can add Comisión	10	add_commission
38	Can change Comisión	10	change_commission
39	Can delete Comisión	10	delete_commission
40	Can view Comisión	10	view_commission
41	Can add Semestre	11	add_semester
42	Can change Semestre	11	change_semester
43	Can delete Semestre	11	delete_semester
44	Can view Semestre	11	view_semester
45	Can add Inscripcion a Cursada	12	add_commissioninscription
46	Can change Inscripcion a Cursada	12	change_commissioninscription
47	Can delete Inscripcion a Cursada	12	delete_commissioninscription
48	Can view Inscripcion a Cursada	12	view_commissioninscription
49	Can add Evaluation	13	add_evaluation
50	Can change Evaluation	13	change_evaluation
51	Can delete Evaluation	13	delete_evaluation
52	Can view Evaluation	13	view_evaluation
53	Can add Rol de Profesor	14	add_teacherrole
54	Can change Rol de Profesor	14	change_teacherrole
55	Can delete Rol de Profesor	14	delete_teacherrole
56	Can view Rol de Profesor	14	view_teacherrole
57	Can add Entrega de Evaluacion	15	add_evaluationsubmission
58	Can change Entrega de Evaluacion	15	change_evaluationsubmission
59	Can delete Entrega de Evaluacion	15	delete_evaluationsubmission
60	Can view Entrega de Evaluacion	15	view_evaluationsubmission
61	Can add QR de Asistencias	16	add_attendanceqrcode
62	Can change QR de Asistencias	16	change_attendanceqrcode
63	Can delete QR de Asistencias	16	delete_attendanceqrcode
64	Can view QR de Asistencias	16	view_attendanceqrcode
65	Can add Asistencia	17	add_attendance
66	Can change Asistencia	17	change_attendance
67	Can delete Asistencia	17	delete_attendance
68	Can view Asistencia	17	view_attendance
69	Can add Registro de Auditoria	18	add_auditlog
70	Can change Registro de Auditoria	18	change_auditlog
71	Can delete Registro de Auditoria	18	delete_auditlog
72	Can view Registro de Auditoria	18	view_auditlog
73	Can add auth identity	19	add_authidentity
74	Can change auth identity	19	change_authidentity
75	Can delete auth identity	19	delete_authidentity
76	Can view auth identity	19	view_authidentity
77	Can add Perfil Profesional Docente	20	add_teacherprofile
78	Can change Perfil Profesional Docente	20	change_teacherprofile
79	Can delete Perfil Profesional Docente	20	delete_teacherprofile
80	Can view Perfil Profesional Docente	20	view_teacherprofile
81	Can add work experience	21	add_workexperience
82	Can change work experience	21	change_workexperience
83	Can delete work experience	21	delete_workexperience
84	Can view work experience	21	view_workexperience
85	Can add Notificación	22	add_notification
86	Can change Notificación	22	change_notification
87	Can delete Notificación	22	delete_notification
88	Can view Notificación	22	view_notification
89	Can add Notificación de usuario	23	add_usernotification
90	Can change Notificación de usuario	23	change_usernotification
91	Can delete Notificación de usuario	23	delete_usernotification
92	Can view Notificación de usuario	23	view_usernotification
93	Can add Departamento	24	add_department
94	Can change Departamento	24	change_department
95	Can delete Departamento	24	delete_department
96	Can view Departamento	24	view_department
97	Can add log entry	25	add_logentry
98	Can change log entry	25	change_logentry
99	Can delete log entry	25	delete_logentry
100	Can view log entry	25	view_logentry
101	Can add permission	26	add_permission
102	Can change permission	26	change_permission
103	Can delete permission	26	delete_permission
104	Can view permission	26	view_permission
105	Can add group	27	add_group
106	Can change group	27	change_group
107	Can delete group	27	delete_group
108	Can view group	27	view_group
109	Can add content type	28	add_contenttype
110	Can change content type	28	change_contenttype
111	Can delete content type	28	delete_contenttype
112	Can view content type	28	view_contenttype
113	Can add Token	29	add_token
114	Can change Token	29	change_token
115	Can delete Token	29	delete_token
116	Can view Token	29	view_token
117	Can add token	30	add_tokenproxy
118	Can change token	30	change_tokenproxy
119	Can delete token	30	delete_tokenproxy
120	Can view token	30	view_tokenproxy
121	Can add session	31	add_session
122	Can change session	31	change_session
123	Can delete session	31	delete_session
124	Can view session	31	view_session
125	Can add APNS device	32	add_apnsdevice
126	Can change APNS device	32	change_apnsdevice
127	Can delete APNS device	32	delete_apnsdevice
128	Can view APNS device	32	view_apnsdevice
129	Can add FCM device	33	add_gcmdevice
130	Can change FCM device	33	change_gcmdevice
131	Can delete FCM device	33	delete_gcmdevice
132	Can view FCM device	33	view_gcmdevice
133	Can add WNS device	34	add_wnsdevice
134	Can change WNS device	34	change_wnsdevice
135	Can delete WNS device	34	delete_wnsdevice
136	Can view WNS device	34	view_wnsdevice
137	Can add WebPush device	35	add_webpushdevice
138	Can change WebPush device	35	change_webpushdevice
139	Can delete WebPush device	35	delete_webpushdevice
140	Can view WebPush device	35	view_webpushdevice
141	Can add Código recuperación de contraseña	36	add_passwordresetotp
142	Can change Código recuperación de contraseña	36	change_passwordresetotp
143	Can delete Código recuperación de contraseña	36	delete_passwordresetotp
144	Can view Código recuperación de contraseña	36	view_passwordresetotp
145	Can add Horario	37	add_semesterschedule
146	Can change Horario	37	change_semesterschedule
147	Can delete Horario	37	delete_semesterschedule
148	Can view Horario	37	view_semesterschedule
149	Can add Evento del Calendario Académico	38	add_academiccalendarevent
150	Can change Evento del Calendario Académico	38	change_academiccalendarevent
151	Can delete Evento del Calendario Académico	38	delete_academiccalendarevent
152	Can view Evento del Calendario Académico	38	view_academiccalendarevent
153	Can add Recordatorio de evento	39	add_calendareventreminder
154	Can change Recordatorio de evento	39	change_calendareventreminder
155	Can delete Recordatorio de evento	39	delete_calendareventreminder
156	Can view Recordatorio de evento	39	view_calendareventreminder
157	Can add Tipo de trámite	40	add_formproceduretype
158	Can change Tipo de trámite	40	change_formproceduretype
159	Can delete Tipo de trámite	40	delete_formproceduretype
160	Can view Tipo de trámite	40	view_formproceduretype
161	Can add Tipo de formulario	41	add_formtype
162	Can change Tipo de formulario	41	change_formtype
163	Can delete Tipo de formulario	41	delete_formtype
164	Can view Tipo de formulario	41	view_formtype
165	Can add Tipo de campo de formulario	42	add_formfieldtype
166	Can change Tipo de campo de formulario	42	change_formfieldtype
167	Can delete Tipo de campo de formulario	42	delete_formfieldtype
168	Can view Tipo de campo de formulario	42	view_formfieldtype
169	Can add Catálogo	43	add_catalog
170	Can change Catálogo	43	change_catalog
171	Can delete Catálogo	43	delete_catalog
172	Can view Catálogo	43	view_catalog
173	Can add Item de catálogo	44	add_catalogitem
174	Can change Item de catálogo	44	change_catalogitem
175	Can delete Item de catálogo	44	delete_catalogitem
176	Can view Item de catálogo	44	view_catalogitem
177	Can add Formulario	45	add_form
178	Can change Formulario	45	change_form
179	Can delete Formulario	45	delete_form
180	Can view Formulario	45	view_form
181	Can add Fuente de documento	46	add_formdocumentsource
182	Can change Fuente de documento	46	change_formdocumentsource
183	Can delete Fuente de documento	46	delete_formdocumentsource
184	Can view Fuente de documento	46	view_formdocumentsource
185	Can add Campo de formulario	47	add_formfield
186	Can change Campo de formulario	47	change_formfield
187	Can delete Campo de formulario	47	delete_formfield
188	Can view Campo de formulario	47	view_formfield
189	Can add Opción de campo	48	add_formfieldoption
190	Can change Opción de campo	48	change_formfieldoption
191	Can delete Opción de campo	48	delete_formfieldoption
192	Can view Opción de campo	48	view_formfieldoption
193	Can add Respuesta de formulario	49	add_formsubmission
194	Can change Respuesta de formulario	49	change_formsubmission
195	Can delete Respuesta de formulario	49	delete_formsubmission
196	Can view Respuesta de formulario	49	view_formsubmission
197	Can add Respuesta de campo	50	add_formanswer
198	Can change Respuesta de campo	50	change_formanswer
199	Can delete Respuesta de campo	50	delete_formanswer
200	Can view Respuesta de campo	50	view_formanswer
201	Can add Estado de respuesta	51	add_formsubmissionstatus
202	Can change Estado de respuesta	51	change_formsubmissionstatus
203	Can delete Estado de respuesta	51	delete_formsubmissionstatus
204	Can view Estado de respuesta	51	view_formsubmissionstatus
205	Can add Novedad	52	add_news
206	Can change Novedad	52	change_news
207	Can delete Novedad	52	delete_news
208	Can view Novedad	52	view_news
209	Can add Entrada del Calendario de Cátedra	53	add_catedracalendarentry
210	Can change Entrada del Calendario de Cátedra	53	change_catedracalendarentry
211	Can delete Entrada del Calendario de Cátedra	53	delete_catedracalendarentry
212	Can view Entrada del Calendario de Cátedra	53	view_catedracalendarentry
213	Can add Carrera de Alumno	54	add_studentcareer
214	Can change Carrera de Alumno	54	change_studentcareer
215	Can delete Carrera de Alumno	54	delete_studentcareer
216	Can view Carrera de Alumno	54	view_studentcareer
217	Can add Carrera	55	add_career
218	Can change Carrera	55	change_career
219	Can delete Carrera	55	delete_career
220	Can view Carrera	55	view_career
221	Can add Secretaría	56	add_secretary
222	Can change Secretaría	56	change_secretary
223	Can delete Secretaría	56	delete_secretary
224	Can view Secretaría	56	view_secretary
225	Can add Grupo de propiedad	57	add_formownershipgroup
226	Can change Grupo de propiedad	57	change_formownershipgroup
227	Can delete Grupo de propiedad	57	delete_formownershipgroup
228	Can view Grupo de propiedad	57	view_formownershipgroup
229	Can add Miembro del grupo	58	add_formownershipmember
230	Can change Miembro del grupo	58	change_formownershipmember
231	Can delete Miembro del grupo	58	delete_formownershipmember
232	Can view Miembro del grupo	58	view_formownershipmember
233	Can add Contacto	59	add_contact
234	Can change Contacto	59	change_contact
235	Can delete Contacto	59	delete_contact
236	Can view Contacto	59	view_contact
237	Can add Grupo de estudio	60	add_studygroup
238	Can change Grupo de estudio	60	change_studygroup
239	Can delete Grupo de estudio	60	delete_studygroup
240	Can view Grupo de estudio	60	view_studygroup
241	Can add Miembro de grupo	61	add_groupmembership
242	Can change Miembro de grupo	61	change_groupmembership
243	Can delete Miembro de grupo	61	delete_groupmembership
244	Can view Miembro de grupo	61	view_groupmembership
\.


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.authtoken_token (key, created, user_id) FROM stdin;
79a5bac4cbf937e61df4c1e8a7ccbff0a019c696	2026-05-27 19:51:11.33823+00	12
68670ec33a89795be3cbd7ec016799f8195ac196	2026-05-27 19:51:37.698902+00	15
a171b0fcd445dfb70c545ce4fd1f251c2ecf7b1e	2026-05-27 19:51:39.411424+00	101
e875f0c882b6822e7619a282c4ad10ce99d03da7	2026-05-27 20:06:47.054784+00	126
d8773ff374dcf9909f697810351bc54243c9e96a	2026-05-27 20:06:50.519838+00	127
\.


--
-- Data for Name: backend_academiccalendarevent; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_academiccalendarevent (id, name, start_date, end_date, category, year, is_deadline) FROM stdin;
1	Período de Clases - 1er Cuatrimestre	2026-03-16	2026-07-04	student	2026	f
2	Período de Clases - 2do Cuatrimestre	2026-08-03	2026-11-28	student	2026	f
3	Evaluaciones Parciales - 1er Cuatrimestre	2026-04-27	2026-06-13	student	2026	f
4	Evaluaciones Parciales - 1ra Recuperación (1C)	2026-06-15	2026-06-27	student	2026	f
5	Evaluaciones Parciales - 2da Recuperación (1C)	2026-06-29	2026-07-04	student	2026	f
6	Evaluaciones Parciales - 2do Cuatrimestre	2026-09-28	2026-11-07	student	2026	f
7	Evaluaciones Parciales - 1ra Recuperación (2C)	2026-11-09	2026-11-21	student	2026	f
8	Evaluaciones Parciales - 2da Recuperación (2C)	2026-11-23	2026-11-28	student	2026	f
10	Período para completar encuestas estudiantiles (2C)	2026-11-16	2026-11-28	student	2026	f
12	Evaluaciones Integradoras (1C)	2026-06-29	2026-07-04	student	2026	f
14	Evaluaciones Integradoras (2C)	2026-11-30	2026-12-05	student	2026	f
15	Presentación de Certificados de Trabajo / Discapacidad (1C)	2026-03-16	2026-04-04	student	2026	f
25	Admisión de estudiantes del CBC (1C)	2026-02-09	2026-03-07	student	2026	f
26	Admisión de estudiantes del CBC (2C)	2026-08-03	2026-08-22	student	2026	f
27	Período postulaciones movilidad académica saliente (2C)	2026-04-06	2026-04-25	student	2026	f
28	Período postulaciones movilidad académica saliente (1C 2027)	2026-09-28	2026-10-17	student	2026	f
29	Charla de Bienvenida a estudiantes de movilidad académica (1C)	2026-03-16	2026-03-21	student	2026	f
30	Charla de Bienvenida a estudiantes de movilidad académica (2C)	2026-08-03	2026-08-08	student	2026	f
31	Período de Solicitud de Prórrogas de Asignaturas Vencidas (1C→2C)	2026-07-06	2026-07-25	student	2026	f
32	Período de Solicitud de Prórrogas de Asignaturas Vencidas (2C→1C)	2026-12-07	2026-12-26	student	2026	f
35	Período para abonar trámite de convalidación (2C)	2026-03-16	2026-04-04	student	2026	f
36	Período para abonar trámite de convalidación (1C 2027)	2026-08-17	2026-09-05	student	2026	f
37	Período para mesas de examen especiales (verano)	2026-01-05	2026-02-28	student	2026	f
38	Período para mesas de examen especiales (receso invernal)	2026-07-13	2026-07-25	student	2026	f
39	Recepción de trámites de simultaneidad entre carreras de FIUBA (1C)	2026-02-09	2026-02-28	student	2026	f
41	Charla de Ingresantes	2026-02-23	2026-02-28	student	2026	f
42	Recepción de otros trámites para el cuatrimestre siguiente (1C→2C)	2026-05-04	2026-07-04	student	2026	f
43	Recepción de otros trámites para el cuatrimestre siguiente (2C→1C)	2026-10-05	2026-12-05	student	2026	f
44	Publicación oferta horaria de Cursos de Verano 2027	2026-10-05	2026-10-10	student	2026	f
45	Inscripción para Cursos de Verano 2027	2026-11-16	2026-11-21	student	2026	f
46	Desinscripción de Cursos de Verano 2027	2026-12-14	2026-12-19	student	2026	f
47	Inicio de los Cursos de Verano 2027	2027-01-25	2027-02-27	student	2026	f
48	Registro de notas de cursadas en Guaraní (1C)	2026-07-06	2026-07-25	teacher	2026	f
49	Registro de notas de evaluaciones integradoras en Guaraní (1C)	2026-07-06	2026-07-18	teacher	2026	f
50	Fecha límite presentación de planificaciones (1C)	2026-02-23	2026-02-28	teacher	2026	f
51	Registro de notas de cursadas en Guaraní (2C)	2026-12-07	2026-12-19	teacher	2026	f
52	Registro de notas de evaluaciones integradoras en Guaraní (2C)	2026-12-07	2026-12-14	teacher	2026	f
53	Fecha límite presentación de planificaciones (2C)	2026-07-27	2026-08-01	teacher	2026	f
54	Fecha límite presentación planificaciones de Cursos de Verano 2027	2026-10-26	2026-10-31	teacher	2026	f
55	Oferta horaria y vacantes (2C)	2026-05-04	2026-06-06	department	2026	f
56	Oferta horaria y vacantes (1C 2027)	2026-10-05	2026-11-07	department	2026	f
57	Cierre de Actas de cursadas en Guaraní (1C)	2026-07-20	2026-07-25	department	2026	f
58	Cierre de Actas de cursadas en Guaraní (2C)	2026-12-14	2026-12-19	department	2026	f
59	Cierre de Actas de Evaluaciones integradoras en Guaraní (1C)	2026-07-13	2026-07-18	department	2026	f
60	Cierre de Actas de Evaluaciones integradoras en Guaraní (2C)	2026-12-07	2026-12-12	department	2026	f
61	Creación de Mesas de Evaluaciones Integradoras (1C)	2026-05-25	2026-06-06	department	2026	f
62	Creación de Mesas de Evaluaciones Integradoras (2C)	2026-10-26	2026-11-07	department	2026	f
63	Período de entrega de dictámenes para Convalidaciones	2026-04-06	2026-06-27	career	2026	f
64	Revisión de Planificaciones (1C)	2026-03-02	2026-03-14	career	2026	f
65	Revisión de Planificaciones (2C)	2026-08-03	2026-08-15	career	2026	f
66	Control de Superposiciones Horarias (2C)	2026-06-08	2026-06-20	career	2026	f
67	Control de Superposiciones Horarias (1C 2027)	2026-11-09	2026-11-21	career	2026	f
68	Asignación de aulas (2C)	2026-06-22	2026-07-18	bedelia	2026	f
69	Asignación de aulas (1C 2027)	2026-11-23	2026-12-19	bedelia	2026	f
70	Verificación de regularidad de los estudiantes (1C)	2026-03-09	2026-03-14	systems	2026	f
71	Verificación de regularidad de los estudiantes (2C)	2026-08-03	2026-08-08	systems	2026	f
72	Procesamiento de matrices de equivalencias	2026-04-06	2026-04-25	systems	2026	f
73	Confirmación de inscripciones pendientes (2C)	2026-07-27	2026-08-08	systems	2026	f
74	Confirmación de inscripciones pendientes (1C 2027)	2027-01-18	2027-01-30	systems	2026	f
11	Inscripción para Evaluaciones Integradoras (1C)	2026-06-08	2026-06-13	student	2026	t
9	Período para completar encuestas estudiantiles (1C)	2026-06-15	2026-06-27	student	2026	t
17	Publicación oferta horaria para cursar (2C)	2026-06-22	2026-06-27	student	2026	t
18	Publicación de Prioridades para Inscripción (2C)	2026-06-29	2026-07-04	student	2026	t
33	Período de Solicitud de Excepciones de Correlatividades (1C→2C)	2026-07-06	2026-07-18	student	2026	t
19	Inscripción para Cursar Asignaturas (2C)	2026-07-06	2026-07-18	student	2026	t
40	Recepción de trámites de simultaneidad entre carreras de FIUBA (2C)	2026-08-03	2026-08-22	student	2026	t
20	Desinscripción de Asignaturas (2C)	2026-08-03	2026-08-15	student	2026	t
16	Presentación de Certificados de Trabajo / Discapacidad (2C)	2026-08-03	2026-08-22	student	2026	t
21	Publicación oferta horaria para cursar (1C 2027)	2026-11-02	2026-11-07	student	2026	t
13	Inscripción para Evaluaciones Integradoras (2C)	2026-11-02	2026-11-07	student	2026	t
22	Publicación de Prioridades para Inscripción (1C 2027)	2026-11-23	2026-11-28	student	2026	t
34	Período de Solicitud de Excepciones de Correlatividades (2C→1C)	2026-12-07	2026-12-19	student	2026	t
23	Inscripción para Cursar Asignaturas (1C 2027)	2026-12-07	2026-12-19	student	2026	t
24	Desinscripción de Asignaturas (1C 2027)	2027-01-11	2027-01-23	student	2026	t
75	Test event	2026-05-14	2026-05-31	student	2026	t
\.


--
-- Data for Name: backend_attendance; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_attendance (id, submitted_at, qr_code_id, semester_id, student_id, latitude, location_valid, longitude) FROM stdin;
21	2026-03-24 22:05:00+00	15	12	100	\N	\N	\N
22	2026-03-31 22:05:00+00	16	12	100	\N	\N	\N
23	2026-04-07 22:05:00+00	17	12	100	\N	\N	\N
24	2026-04-14 22:05:00+00	18	12	100	\N	\N	\N
25	2026-04-21 22:05:00+00	19	12	100	\N	\N	\N
1	2024-11-13 23:00:00+00	1	2	14	\N	\N	\N
2	2024-11-14 23:00:00+00	2	2	14	\N	\N	\N
3	2024-11-14 23:00:00+00	3	2	14	\N	\N	\N
4	2024-11-14 23:00:00+00	4	2	14	\N	\N	\N
5	2024-11-14 23:00:00+00	5	2	14	\N	\N	\N
6	2024-11-14 23:00:00+00	7	2	14	\N	\N	\N
7	2024-11-14 23:00:00+00	8	2	14	\N	\N	\N
8	2024-11-14 23:00:00+00	9	2	14	\N	\N	\N
10	2024-06-13 23:00:00+00	10	8	12	\N	\N	\N
11	2024-06-20 23:00:00+00	11	8	12	\N	\N	\N
12	2024-06-20 23:00:00+00	10	8	1	\N	\N	\N
13	2024-06-20 23:00:00+00	10	8	2	\N	\N	\N
14	2024-07-01 23:00:00+00	13	8	12	\N	\N	\N
15	2024-06-20 23:00:00+00	11	8	3	\N	\N	\N
16	2024-06-13 23:00:00+00	10	8	3	\N	\N	\N
17	2024-06-13 23:00:00+00	10	8	4	\N	\N	\N
18	2024-06-20 23:00:00+00	11	8	4	\N	\N	\N
19	2024-07-08 23:00:00+00	13	8	4	\N	\N	\N
20	2024-07-15 23:00:00+00	14	8	12	\N	\N	\N
\.


--
-- Data for Name: backend_attendanceqrcode; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_attendanceqrcode (id, created_at, qrid, owner_teacher_id, semester_id, expires_at, campus, mode) FROM stdin;
15	2026-03-24 22:00:00+00	c0db687c-1012-4f50-be8a-fd07a2c52220	8	12	2026-03-24 23:00:00+00	\N	qr
16	2026-03-31 22:00:00+00	4898acdf-8c93-488d-b063-6fe609f84f2e	8	12	2026-03-31 23:00:00+00	\N	qr
17	2026-04-07 22:00:00+00	9c11fb68-6fb3-4480-a923-a3a3a80bd6a1	8	12	2026-04-07 23:00:00+00	\N	qr
18	2026-04-14 22:00:00+00	77b427e2-b1e2-4f29-9615-3d414acb84d8	8	12	2026-04-14 23:00:00+00	\N	qr
19	2026-04-21 22:00:00+00	35d8e733-8792-45ba-b330-952eed9d9bd0	8	12	2026-04-21 23:00:00+00	\N	qr
1	2024-06-13 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-14 01:00:00+00	\N	qr
2	2024-06-14 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-15 01:00:00+00	\N	qr
3	2024-06-15 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-16 01:00:00+00	\N	qr
4	2024-06-16 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-17 01:00:00+00	\N	qr
5	2024-06-17 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-18 01:00:00+00	\N	qr
6	2024-06-18 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-19 01:00:00+00	\N	qr
7	2024-06-19 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-20 01:00:00+00	\N	qr
8	2024-06-20 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-21 01:00:00+00	\N	qr
9	2024-06-21 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-22 01:00:00+00	\N	qr
10	2024-06-13 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	12	8	2024-06-14 01:00:00+00	\N	qr
11	2024-06-20 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	12	8	2024-06-21 01:00:00+00	\N	qr
12	2024-06-22 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	5	2	2024-06-23 01:00:00+00	\N	qr
13	2024-07-08 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	12	8	2024-07-09 01:00:00+00	\N	qr
14	2024-07-15 22:00:00+00	f47ac10b-58cc-4372-a567-0e02b2c3d479	12	8	2024-07-16 01:00:00+00	\N	qr
\.


--
-- Data for Name: backend_auditlog; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_auditlog (id, log, "timestamp", related_user_id, user_id) FROM stdin;
1	Docente agrego una entrega manualmente para la evaluacion: 6 - Análisis Matemático II - Cátedra Cosso - Cosso, Pablo (12348) - 2026 FS - Parcial 1 - AM II	2026-04-25 17:48:35.24012+00	100	8
2	Docente envió aviso 'Bienvenidos a algo 1' a 2 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 03:34:27.333178+00	6	6
3	Docente envió aviso 'Cambio de Aula' a 2 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 19:54:06.878153+00	6	6
4	Docente añadió un estudiante al semestre: 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 19:57:32.759892+00	1	6
5	Docente envió aviso 'Otro cambio de aula' a 3 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 19:57:57.360596+00	6	6
6	Docente envió aviso 'Aviso general' a 3 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 19:58:19.124251+00	6	6
7	Docente envió aviso 'Se cancela parcial' a 3 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 20:12:39.025964+00	6	6
8	Docente envió aviso 'Paro docente del 12/5' a 3 alumnos del cuatrimestre 7 - Algoritmos y Programación I - Cátedra 1 - Essaya, Diego (12346) - 2026 FS	2026-04-29 20:57:52.03094+00	6	6
9	Docente creo un final para la materia: Física I - Catedra 1	2026-05-25 16:14:04.157693+00	\N	5
10	Admin aprobó fecha de final: 8 - Física I - Catedra 1 - Collinet, Jorge (12345) - 2026-05-26	2026-05-25 18:43:53.396422+00	\N	111
11	Usuario agregó un nuevo docente a la comisión 1 - Física I - Catedra 1 - Collinet, Jorge (12345)	2026-06-07 19:40:04.418934+00	128	5
\.


--
-- Data for Name: backend_authidentity; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_authidentity (id, provider, provider_user_id, email, added_at, last_used_at, user_id) FROM stdin;
2	local	38157957	danielap.riesgo@gmail.com	2026-04-11 16:41:48.631665+00	\N	2
3	local	40123123	juani.kristal@gmail.com	2026-04-11 16:41:49.090004+00	\N	3
4	local	36123123	alevinas@gmail.com	2026-04-11 16:41:49.549271+00	\N	4
5	local	35624188	jorge.collinet@gmail.com	2026-04-11 16:41:50.007316+00	\N	5
6	local	30123123	dessaya@gmail.com	2026-04-11 16:41:50.466248+00	\N	6
7	local	99999999	dato@dato.com	2026-04-11 16:41:50.92425+00	\N	7
8	local	13123123	pablo.cosso@gmail.com	2026-04-11 16:41:51.382322+00	\N	8
9	local	15151515	mariano.mendez@gmail.com	2026-04-11 16:41:51.841501+00	\N	9
10	local	17171717	alumno.fake@123.com	2026-04-11 16:41:52.299827+00	\N	10
11	local	18181818	alumna.fake@123.com	2026-04-11 16:41:52.759059+00	\N	11
12	local	41107811	fgiordano@fi.uba.ar	2026-04-11 16:41:53.216924+00	\N	12
13	local	41318038	airibarren@fi.uba.ar	2026-04-11 16:41:53.674242+00	\N	13
14	local	41099526	macohen@fi.uba.ar	2026-04-11 16:41:54.133409+00	\N	14
15	local	11111111	admin@ludo.com	2026-04-11 16:41:54.592816+00	\N	99
17	google	108904364424163819070	mmerlog@fi.uba.ar	2026-04-29 03:08:52.051498+00	\N	102
1	google	102175008748779643011	ggordyn@fi.uba.ar	2026-04-29 03:26:57.167329+00	\N	15
18	local	43459394	vlanzillotta@fi.uba.ar	2026-04-29 03:28:11.700833+00	\N	101
19	local	37247189	fede.est@gmail.com	2026-04-29 03:28:12.703822+00	\N	1
16	google	101394135503250076613	jandresen@fi.uba.ar	2026-04-11 16:45:14.236037+00	\N	100
\.


--
-- Data for Name: backend_calendareventreminder; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_calendareventreminder (id, days_before, sent_at, event_id, notification_id) FROM stdin;
1	6	2026-05-08 22:53:46.997324+00	75	8
\.


--
-- Data for Name: backend_career; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_career (id, siu_id, name) FROM stdin;
1	2	Ingeniería en Informática
2	15	Licenciatura en Análisis de Sistemas
\.


--
-- Data for Name: backend_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_catalog (id, catalog_key, catalog_name, catalog_description) FROM stdin;
1	rol_en_comunidad	Rol en la comunidad	\N
2	carreras	Carreras	\N
3	tipo_de_beca	Tipo de beca	\N
\.


--
-- Data for Name: backend_catalogitem; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_catalogitem (id, catalog_item_value, catalog_item_label, catalog_item_order, catalog_item_active, catalog_id) FROM stdin;
1	Alumno de Grado	Alumno de Grado	1	t	1
2	Alumno de Posgrado	Alumno de Posgrado	2	t	1
3	Alumno de Intercambio	Alumno de Intercambio	3	t	1
4	Graduado	Graduado	4	t	1
5	Docente	Docente	5	t	1
6	Docente de Posgrado	Docente de Posgrado	6	t	1
7	Investigador	Investigador	7	t	1
8	No Docente	No Docente	8	t	1
9	Contrato de Servicios	Contrato de Servicios	9	t	1
10	Autoridad	Autoridad	10	t	1
11	CBC	CBC	11	t	1
12	Alumno no regular/ ex alumno	Alumno no regular/ ex alumno	12	t	1
13	Ing. Civil	Ing. Civil	1	t	2
14	Ing. de Alimentos	Ing. de Alimentos	2	t	2
15	Ing. en Energía Eléctrica	Ing. en Energía Eléctrica	3	t	2
16	Ing. Electrónica	Ing. Electrónica	4	t	2
17	Ing. en Agrimensura	Ing. en Agrimensura	5	t	2
18	Ing. en Informática	Ing. en Informática	6	t	2
19	Ing. en Petróleo	Ing. en Petróleo	7	t	2
20	Ing. Industrial	Ing. Industrial	8	t	2
21	Ing. Mecánica	Ing. Mecánica	9	t	2
22	Ing. Naval y Mecánica	Ing. Naval y Mecánica	10	t	2
23	Ing. Química	Ing. Química	11	t	2
24	Lic. en Análisis de Sistemas	Lic. en Análisis de Sistemas	12	t	2
25	Bioingeniería	Bioingeniería	13	t	2
26	Doble Diploma	Doble Diploma	1	t	3
27	Programa UBAInt	Programa UBAInt	2	t	3
28	Programa AUGM	Programa AUGM	3	t	3
29	Programa "convocatoria unificada"	Programa "convocatoria unificada"	4	t	3
30	Beca Aelarg	Beca Aelarg	5	t	3
31	Programa sin beca	Programa sin beca	6	t	3
\.


--
-- Data for Name: backend_catedracalendarentry; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_catedracalendarentry (id, date, class_number, topic, entry_type, links, notes, semester_id) FROM stdin;
1	2026-05-01	1	Introducción y RPC	class	[{"url": "https://example.com/paper1", "label": "Saltzer y Kaashoek (2009)"}]	Lecturas: 2.1, 4.1 y 4.2	9
2	2026-05-08	2	MapReduce	class	[{"url": "https://example.com/paper2", "label": "MapReduce - Dean"}]		9
3	2026-05-15	3	TP1 MapReduce — enunciado	tp_delivery	[]	Entrega y presentación	9
4	2026-05-22	4	Replicación y Sharding	class	[{"url": "https://example.com/paper3", "label": "The Log - Kreps"}]	Capítulo 5, pp. 152–161	9
5	2026-05-01	1	Introducción y RPC	class	[{"url": "https://example.com/paper1", "label": "Saltzer y Kaashoek (2009)"}]	Lecturas: 2.1, 4.1 y 4.2	17
6	2026-05-08	2	MapReduce	class	[{"url": "https://example.com/paper2", "label": "MapReduce - Dean"}]		17
7	2026-05-15	3	TP1 MapReduce — enunciado	tp_delivery	[]	Entrega y presentación	17
8	2026-05-22	4	Replicación y Sharding	class	[{"url": "https://example.com/paper3", "label": "The Log - Kreps"}]	Capítulo 5, pp. 152–161	17
\.


--
-- Data for Name: backend_commission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_commission (id, subject_siu_id, subject_name, siu_id, created_at, updated_at, chief_teacher_id, chief_teacher_grader_weight, department_id) FROM stdin;
9	8	Introducción al Pensamiento Computacional - Cátedra 1	9	2024-02-01 12:00:00+00	2024-02-01 12:00:00+00	12	5	\N
1	1	Física I - Catedra 1	1	2026-04-29 03:27:23.140736+00	2026-04-29 03:27:23.140756+00	5	5	9
2	1	Física I - Catedra 2	2	2026-04-29 03:27:23.447592+00	2026-04-29 03:27:23.447609+00	6	5	9
3	1	Física I - Catedra 3	3	2026-04-29 03:27:23.679484+00	2026-04-29 03:27:23.679509+00	13	5	9
4	3	Análisis Matemático II - Catedra 1	4	2026-04-29 03:27:24.062065+00	2026-04-29 03:27:24.062083+00	13	5	16
5	3	Análisis Matemático II - Catedra 2	5	2026-04-29 03:27:24.296969+00	2026-04-29 03:27:24.296988+00	12	5	16
8	7	Álgebra II - Cátedra 1	8	2024-07-01 12:00:00+00	2024-07-01 12:00:00+00	13	5	16
6	5	Algoritmos y Programación I	6	2026-04-29 03:27:24.530349+00	2026-04-29 03:27:24.530366+00	15	5	4
7	5	Algoritmos y Programación I - Cátedra 1	7	2026-04-23 22:16:29.594893+00	2026-04-23 22:16:29.594893+00	6	5	4
11	9999	Tecnología de Base - TB025	9999	2026-05-27 20:06:51.478052+00	2026-05-27 20:06:51.478078+00	126	5	4
\.


--
-- Data for Name: backend_commissioninscription; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_commissioninscription (id, status, semester_id, student_id) FROM stdin;
21	A	12	100
22	A	13	100
23	A	14	100
24	A	15	100
25	A	16	100
26	A	12	101
27	A	13	101
28	A	14	101
1	A	1	14
2	A	2	14
5	A	1	13
6	A	2	13
7	R	3	14
9	A	8	12
10	A	3	14
11	A	6	12
14	A	10	1
15	A	10	2
16	A	8	1
17	A	8	2
18	A	8	3
19	A	8	4
20	A	11	14
29	A	14	1
30	A	17	1
31	P	18	127
\.


--
-- Data for Name: backend_contact; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_contact (id, status, created_at, from_student_id, to_student_id) FROM stdin;
1	A	2026-06-03 01:19:12.156574+00	100	15
\.


--
-- Data for Name: backend_department; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_department (id, name, location, schedule, contact_info, procedures, created_at, updated_at) FROM stdin;
3	Departamento de Agrimensura	Av. Las Heras 2214, 3er. piso - C1127AAR - Buenos Aires		Tel: (54-11) 528-50325 | Email: agrimen@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
4	Departamento de Computación	Av. Paseo Colón 850, 4to. piso - C1063ACV - Buenos Aires	Lunes a viernes de 10:00 a 21:00	Tel: (54-11) 528-50900 | Email: computacion@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
5	Departamento de Construcciones y Estructuras	Av. Las Heras 2214, PB - C1127AAR - Buenos Aires	Lunes a viernes de 9:00 a 21:00	Tel: (54-11) 528-50220 | Email: depto.cye@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
6	Departamento de Electrónica	Av. Paseo Colón 850, 1er. piso - C1063ACV - Buenos Aires	Lunes a viernes de 10:00 a 20:00	Tel: (54-11) 528-50704 / 50705 | Email: electron@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
7	Departamento de Energía	Av. Paseo Colón 850, Subsuelo - C1063ACV - Buenos Aires	Lunes a viernes de 9:00 a 13:00 y de 14:00 a 20:00	Tel: (54-11) 528-50410 / 50411 | Email: depto_energia@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
8	Departamento de Estabilidad	Av. Las Heras 2214, PB - C1127AAR - Buenos Aires	Lunes a viernes de 9:00 a 22:00	Tel: (54-11) 528-50222 / 50223 / 50224 / 50225 | Email: estabil@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
9	Departamento de Física	Av. Paseo Colón 850, 2do. piso - C1063ACV - Buenos Aires	Lunes a viernes de 8:00 a 14:00 y de 15:00 a 21:00	Tel: (54-11) 528-50811 / 50869 | Email: fisica@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
10	Departamento de Gestión	Av. Las Heras 2214, 1er. piso - C1127AAR - Buenos Aires		Tel: (54-11) 528-50265 / 50271 | Email: economia@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
11	Departamento de Hidráulica	Av. Las Heras 2214, 3er. piso - C1127AAR - Buenos Aires		Tel: (54-11) 528-50336 / 50337 | Email: hidrau@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
12	Departamento de Idiomas	Av. Paseo Colón 850, 5to. piso - C1063ACV - Buenos Aires	Consultar cartelera virtual en Campus Institucional	Email: idiomas@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
13	Departamento de Ingeniería Mecánica	Av. Paseo Colón 850, Subsuelo - C1063ACV - Buenos Aires	Lunes a viernes de 9:00 a 22:00	Tel: (54-11) 528-50472 / 50475 / 50476 | Email: mecanica@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
14	Departamento de Ingeniería Naval	Av. Paseo Colón 850, 4to. piso (ex-aula 410) - C1063ACV - Buenos Aires		Tel: (54-11) 528-50909 | Email: dindir@fi.uba.ar | Secretaría: dinsec@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
15	Departamento de Ingeniería Química	Int. Güiraldes 2160 - C1428EGA - Buenos Aires (Ciudad Universitaria)	Lunes a viernes de 9:30 a 12:30 y de 13:30 a 19:30	Tel: (54-11) 528-50352 | Email: deptoiq@di.fcen.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
16	Departamento de Matemática	Av. Paseo Colón 850, 1er. piso - C1063ACV - Buenos Aires	Lunes a viernes de 9:30 a 13:30 y de 14:45 a 18:45	Tel: (54-11) 528-50734 / 50735 | Email: matem@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
17	Departamento de Química	Av. Paseo Colón 850, 5to. piso - C1063ACV - Buenos Aires	Lunes a viernes de 8:00 a 13:00 y de 13:30 a 21:00	Tel: (54-11) 528-50963 | Email: dquimica@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
18	Departamento de Seguridad del Trabajo y Ambiente	Av. Paseo Colón 850, 4to. piso - C1063ACV - Buenos Aires	Lunes a viernes de 12:00 a 19:00	Tel: (54-11) 528-50910 / 50911 / 50912 | Email: diat@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
19	Departamento de Tecnología Industrial	Av. Las Heras 2214, 1er. piso - C1127AAR - Buenos Aires	Lunes a viernes de 15:00 a 22:00 | Ventanilla alumnos: 17:00 a 21:00	Tel: (54-11) 528-50277 / 50275 | Email: tecnologiaindustrial@fi.uba.ar | WhatsApp: +5491125718773	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
20	Departamento de Transporte	Av. Las Heras 2214, 2do. piso - C1127AAR - Buenos Aires		Tel: (54-11) 528-50302 | Email: transporte@fi.uba.ar	Equivalencias, posgrados, cambio de catedra y consultas generales	2026-04-11 18:01:52.278967+00	2026-04-11 18:01:52.278967+00
\.


--
-- Data for Name: backend_evaluation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_evaluation (id, evaluation_name, is_graded, passing_grade, start_date, end_date, semester_id, parent_evaluation_id, requires_identity, requires_qr, is_gradeable, description) FROM stdin;
15	Parcial 1 - AM II	t	4	2026-04-20 22:00:00+00	2026-04-30 01:00:00+00	12	\N	t	f	t	\N
16	Parcial 2 - AM II	t	4	2026-06-10 22:00:00+00	2026-06-13 01:00:00+00	12	\N	t	f	t	\N
17	Parcial 1 - Física I	t	4	2026-05-13 20:00:00+00	2026-05-15 23:00:00+00	13	\N	t	f	t	\N
18	Parcial 1 - Algoritmos I	t	4	2026-05-08 17:00:00+00	2026-05-08 21:00:00+00	14	\N	t	f	t	\N
19	TP1 - Integrales dobles	t	4	2026-03-24 22:00:00+00	2026-04-03 23:59:00+00	12	\N	f	f	t	\N
1	Parcial	t	4	2024-09-18 22:00:00+00	2024-09-19 01:00:00+00	2	\N	f	f	t	\N
2	Primer Parcial	t	4	2024-09-18 22:00:00+00	2024-09-19 01:00:00+00	8	\N	f	f	t	\N
3	Recuperatorio Parcial	t	4	2024-11-20 22:00:00+00	2024-11-21 01:00:00+00	2	1	f	f	t	\N
4	Segundo Recuperatorio Parcial	t	4	2024-11-20 22:00:00+00	2024-11-21 01:00:00+00	2	3	f	f	t	\N
5	Parcial	t	4	2024-11-13 22:00:00+00	2024-11-14 01:00:00+00	9	\N	f	f	t	\N
6	Parcial	t	4	2024-11-13 22:00:00+00	2024-11-14 01:00:00+00	10	\N	f	f	t	\N
7	Segundo Parcial	t	4	2024-10-21 22:00:00+00	2024-10-22 01:00:00+00	8	\N	f	f	t	\N
8	Parcial	t	4	2024-04-21 22:00:00+00	2024-04-22 01:00:00+00	11	\N	f	f	t	\N
9	Primer Parcial	t	4	2024-08-21 22:00:00+00	2024-08-22 01:00:00+00	6	\N	f	f	t	\N
13	Trabajo Práctico 1	f	7	2024-08-06 22:00:00+00	2024-09-07 02:59:00+00	6	\N	f	f	t	\N
10	Segundo Parcial	t	4	2024-10-17 22:00:00+00	2024-10-18 01:00:00+00	6	\N	f	f	t	\N
14	Trabajo Práctico 2	f	7	2024-09-06 22:00:00+00	2024-10-18 02:59:00+00	6	\N	f	f	t	\N
11	Primer Recuperatorio	t	4	2024-11-21 22:00:00+00	2024-11-22 01:00:00+00	6	9	f	f	t	\N
12	Segundo Recuperatorio	t	4	2024-12-12 22:00:00+00	2024-12-13 01:00:00+00	6	10	f	f	t	\N
\.


--
-- Data for Name: backend_evaluationsubmission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_evaluationsubmission (id, grade, created_at, updated_at, evaluation_id, student_id, grader_id, submission_text, submission_status, submission_file, feedback_text, original_filename) FROM stdin;
15	8	2026-04-02 19:30:00+00	2026-04-05 14:00:00+00	19	100	8	Resolución del TP de integrales dobles y cambio de variables.	GRADED	\N	\N	\N
16	\N	2026-04-25 17:48:33.622684+00	2026-04-25 17:48:33.622724+00	15	100	\N	\N	\N	\N	\N	\N
3	8	2026-04-29 03:27:38.603131+00	2026-04-29 03:27:38.603149+00	2	12	14	\N	\N	\N	\N	\N
4	5	2026-04-29 03:27:39.217801+00	2026-04-29 03:27:39.217818+00	1	14	5	\N	\N	\N	\N	\N
6	\N	2026-04-29 03:27:39.53506+00	2026-04-29 03:27:39.535077+00	2	1	\N	\N	\N	\N	\N	\N
7	\N	2026-04-29 03:27:40.037009+00	2026-04-29 03:27:40.037026+00	2	2	\N	\N	\N	\N	\N	\N
8	\N	2026-04-29 03:27:40.268725+00	2026-04-29 03:27:40.268744+00	2	3	\N	\N	\N	\N	\N	\N
9	\N	2026-04-29 03:27:40.651937+00	2026-04-29 03:27:40.651954+00	2	4	\N	\N	\N	\N	\N	\N
11	4	2026-04-29 03:27:41.265658+00	2026-04-29 03:27:41.265675+00	3	14	5	\N	\N	\N	\N	\N
13	7	2026-04-29 03:27:41.585282+00	2026-04-29 03:27:41.5853+00	5	12	14	\N	\N	\N	\N	\N
14	8	2026-04-29 03:27:41.982708+00	2026-04-29 03:27:41.982726+00	8	14	13	\N	\N	\N	\N	\N
\.


--
-- Data for Name: backend_final; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_final (id, date, qrid, siu_id, created_at, updated_at, teacher_id, status, subject_siu_id, act, subject_name) FROM stdin;
22	2026-05-08 22:00:00+00	3b41bd94-c329-4782-bb19-495cd3412c36	\N	2026-04-23 22:16:29.594893+00	2026-04-23 22:16:29.594893+00	8	OP	3	\N	Análisis Matemático II - Cátedra Cosso
23	2024-12-13 22:00:00+00	d354405e-5c40-48dc-b56c-4198c94a29df	\N	2024-11-20 12:00:00+00	2024-12-14 12:00:00+00	13	DF	7	\N	Álgebra II - Cátedra 1
24	2024-07-19 22:00:00+00	9be0b511-b786-46e8-a416-169e45f0aec1	\N	2024-06-30 12:00:00+00	2024-07-20 12:00:00+00	12	DF	8	\N	Introducción al Pensamiento Computacional - Cátedra 1
1	2023-07-15 22:00:00+00	ff7da029-a317-415f-be25-f36f007580c0	1	2026-04-29 03:27:05.830976+00	2026-04-29 03:27:05.830991+00	6	DF	1	\N	Física I
2	2023-07-22 22:00:00+00	c11003fd-b89b-40be-bc0a-4f3bc68df1d4	2	2026-04-29 03:27:06.152129+00	2026-04-29 03:27:06.152142+00	6	DF	1	\N	Física I
3	2023-07-15 22:00:00+00	97270deb-4223-436e-a4a5-2c303fcb9814	3	2026-04-29 03:27:06.551899+00	2026-04-29 03:27:06.551911+00	7	DF	4	\N	Álgebra II
4	2023-07-22 22:00:00+00	9c7a6bfa-9d4d-4c8a-bcf0-bd1543c92224	4	2026-04-29 03:27:06.787022+00	2026-04-29 03:27:06.787035+00	7	DF	4	\N	Álgebra II
5	2023-07-15 22:00:00+00	a8cc59f4-8dfd-4af7-bf5a-963638535ae8	5	2026-04-29 03:27:07.166655+00	2026-04-29 03:27:07.166667+00	8	DF	5	\N	Algoritmos y Programación I
6	2023-07-22 22:00:00+00	cf9783bb-0544-448c-998c-7ae1f2f0ccb5	6	2026-04-29 03:27:07.499477+00	2026-04-29 03:27:07.49949+00	8	DF	5	\N	Algoritmos y Programación I
7	2023-12-15 22:00:00+00	d02c9dc3-2bf7-4dcc-b8bb-510c2cd3adea	7	2026-04-29 03:27:07.985404+00	2026-04-29 03:27:07.985419+00	8	DF	3	\N	Análisis Matemático II
8	2024-10-03 22:00:00+00	4f0784c3-b939-4348-87a3-1b4a877d1ba5	8	2026-04-29 03:27:08.216992+00	2026-04-29 03:27:08.217005+00	13	DF	3	\N	Análisis Matemático II
9	2024-07-24 22:00:00+00	90cf6012-f0c8-41ee-9fd9-45b6f52e6e1d	9	2026-04-29 03:27:08.599633+00	2026-04-29 03:27:08.599645+00	13	OP	3	\N	Análisis Matemático II
10	2024-02-03 22:00:00+00	c6b74235-101a-4b0d-aed0-88085d7b29e6	10	2026-04-29 03:27:08.8354+00	2026-04-29 03:27:08.835413+00	8	DF	3	\N	Análisis Matemático II
11	2023-12-15 22:00:00+00	7c070313-b587-4b38-9920-715a44c739a9	11	2026-04-29 03:27:09.213918+00	2026-04-29 03:27:09.213931+00	9	DF	1	\N	Física I
12	2024-02-03 22:00:00+00	d1fd52f0-a181-46ae-8b64-30d603f5a6d5	12	2026-04-29 03:27:09.531892+00	2026-04-29 03:27:09.531905+00	9	DF	1	\N	Física I
13	2024-07-05 22:00:00+00	36b4ac7d-1aa9-442e-8b80-d2a7d3377fba	13	2026-04-29 03:27:10.032983+00	2026-04-29 03:27:10.032992+00	9	DF	1	\N	Física I
14	2024-07-12 22:00:00+00	00aa7c01-f46f-4342-970c-29e79e7ec354	14	2026-04-29 03:27:10.264075+00	2026-04-29 03:27:10.264088+00	9	DF	1	\N	Física I
15	2024-07-05 22:00:00+00	14ab460d-8dd2-424f-8256-17b8929b2318	15	2026-04-29 03:27:10.647899+00	2026-04-29 03:27:10.647912+00	5	DF	8	\N	Química I
16	2024-07-12 22:00:00+00	aa22ad90-6c36-4941-898a-5c6e829d5b53	16	2026-04-29 03:27:10.880237+00	2026-04-29 03:27:10.880249+00	5	DF	8	\N	Química I
17	2024-01-11 22:00:00+00	b9fa8fcd-91e3-4980-a246-6c02504ee80e	17	2026-04-29 03:27:11.261912+00	2026-04-29 03:27:11.261925+00	5	DF	8	\N	Química I
18	2024-07-11 22:00:00+00	da0d9615-da7d-4146-88d4-4b3ff2f966db	18	2026-04-29 03:27:11.582059+00	2026-04-29 03:27:11.582071+00	5	DF	9	\N	Matemática Discreta
19	2024-07-18 22:00:00+00	6de3ba17-d29e-46ce-b081-270c9cc81846	19	2026-04-29 03:27:11.979198+00	2026-04-29 03:27:11.979211+00	5	DF	9	\N	Matemática Discreta
20	2024-07-10 22:00:00+00	067363cf-34cd-4512-b8fb-ba132f20823b	20	2026-04-29 03:27:12.593325+00	2026-04-29 03:27:12.593338+00	13	PA	3	\N	Análisis Matemático II
21	2024-07-03 22:00:00+00	7270ae2a-84e0-4da8-a292-62bd3bb1eadc	21	2026-04-29 03:27:12.82469+00	2026-04-29 03:27:12.824702+00	13	AS	3	\N	Análisis Matemático II
25	2026-05-26 03:00:00+00	ec54f22d-0766-4115-badb-56e5c0ee0006	8	2026-05-25 16:14:02.948102+00	2026-05-25 16:14:02.948115+00	5	OP	1	\N	Física I - Catedra 1
\.


--
-- Data for Name: backend_final_commissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_final_commissions (id, final_id, commission_id) FROM stdin;
1	23	8
2	24	9
3	1	2
4	2	2
5	8	4
6	9	4
7	20	4
8	21	4
9	25	1
10	25	2
\.


--
-- Data for Name: backend_finalexam; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_finalexam (id, grade, created_at, updated_at, final_id, student_id) FROM stdin;
33	\N	2026-04-23 22:16:29.594893+00	2026-04-23 22:16:29.594893+00	22	100
34	7	2024-11-25 12:00:00+00	2024-12-14 14:00:00+00	23	100
35	9	2024-07-05 12:00:00+00	2024-07-20 14:00:00+00	24	100
36	\N	2026-04-28 23:01:47.671414+00	2026-04-28 23:01:47.671414+00	22	101
1	4	2026-04-29 03:27:13.208383+00	2026-04-29 03:27:13.208403+00	1	1
2	9	2026-04-29 03:27:13.507136+00	2026-04-29 03:27:13.507149+00	2	2
3	2	2026-04-29 03:27:13.740916+00	2026-04-29 03:27:13.740968+00	3	1
4	7	2026-04-29 03:27:14.129881+00	2026-04-29 03:27:14.129891+00	4	1
5	5	2026-04-29 03:27:14.360525+00	2026-04-29 03:27:14.360543+00	3	2
6	9	2026-04-29 03:27:14.757117+00	2026-04-29 03:27:14.757135+00	8	1
7	10	2026-04-29 03:27:15.063713+00	2026-04-29 03:27:15.06373+00	8	2
8	8	2026-04-29 03:27:15.33324+00	2026-04-29 03:27:15.33326+00	17	1
9	7	2026-04-29 03:27:15.576601+00	2026-04-29 03:27:15.57662+00	17	2
10	\N	2026-04-29 03:27:15.972257+00	2026-04-29 03:27:15.972276+00	18	1
11	2	2026-04-29 03:27:16.205612+00	2026-04-29 03:27:16.20563+00	18	2
12	\N	2026-04-29 03:27:16.587301+00	2026-04-29 03:27:16.58732+00	19	2
13	8	2026-04-29 03:27:16.819157+00	2026-04-29 03:27:16.819175+00	1	14
14	4	2026-04-29 03:27:17.201161+00	2026-04-29 03:27:17.20117+00	3	14
15	10	2026-04-29 03:27:17.626474+00	2026-04-29 03:27:17.626492+00	6	14
16	7	2026-04-29 03:27:18.020326+00	2026-04-29 03:27:18.020345+00	8	14
17	4	2026-04-29 03:27:18.251881+00	2026-04-29 03:27:18.251897+00	15	14
18	6	2026-04-29 03:27:18.635631+00	2026-04-29 03:27:18.63565+00	18	14
20	9	2026-04-29 03:27:19.248686+00	2026-04-29 03:27:19.248695+00	15	12
22	6	2026-04-29 03:27:19.529048+00	2026-04-29 03:27:19.529066+00	4	12
23	7	2026-04-29 03:27:19.966096+00	2026-04-29 03:27:19.966119+00	2	12
25	4	2026-04-29 03:27:20.286419+00	2026-04-29 03:27:20.28643+00	9	1
26	9	2026-04-29 03:27:20.682776+00	2026-04-29 03:27:20.682795+00	9	2
27	9	2026-04-29 03:27:20.920317+00	2026-04-29 03:27:20.920335+00	20	12
28	8	2026-04-29 03:27:21.284966+00	2026-04-29 03:27:21.284983+00	20	2
29	6	2026-04-29 03:27:21.519465+00	2026-04-29 03:27:21.519483+00	20	1
30	8	2026-04-29 03:27:21.912133+00	2026-04-29 03:27:21.912157+00	21	12
31	8	2026-04-29 03:27:22.526278+00	2026-04-29 03:27:22.526296+00	21	2
32	6	2026-04-29 03:27:22.757014+00	2026-04-29 03:27:22.757032+00	21	1
\.


--
-- Data for Name: backend_form; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_form (id, form_name, form_description, form_information, created_at, form_type_id, requires_teacher_validation, ownership_group_id) FROM stdin;
\.


--
-- Data for Name: backend_formanswer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formanswer (id, answer_value, field_id, submission_id) FROM stdin;
\.


--
-- Data for Name: backend_formdocumentsource; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formdocumentsource (form_id, form_document_source) FROM stdin;
\.


--
-- Data for Name: backend_formfield; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formfield (id, form_field_label, form_field_require, form_field_order, catalog_id, form_id, form_field_type_id) FROM stdin;
\.


--
-- Data for Name: backend_formfieldoption; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formfieldoption (id, form_option_value, form_option_label, form_field_id) FROM stdin;
\.


--
-- Data for Name: backend_formfieldtype; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formfieldtype (id, form_field_type_value) FROM stdin;
1	texto
2	numero
3	padron
4	mail
5	options
6	catalog
7	checkbox
8	adjunto
\.


--
-- Data for Name: backend_formownershipgroup; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formownershipgroup (id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: backend_formownershipmember; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formownershipmember (id, entity_type, entity_id, is_editor, group_id) FROM stdin;
\.


--
-- Data for Name: backend_formsubmission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formsubmission (id, submitted_at, form_id, user_id, status_id, teacher_id, teacher_status, teacher_comment, recipient_entity_type, recipient_entity_id) FROM stdin;
\.


--
-- Data for Name: backend_formsubmissionstatus; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formsubmissionstatus (id, form_submission_status_value) FROM stdin;
1	sent
2	pending_approval
3	approved
4	denied
\.


--
-- Data for Name: backend_formtype; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_formtype (id, form_type_value) FROM stdin;
1	Digital
2	Documento
\.


--
-- Data for Name: backend_groupmembership; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_groupmembership (id, status, joined_at, group_id, student_id) FROM stdin;
\.


--
-- Data for Name: backend_news; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_news (id, title, description, tag, created_at, updated_at, author_id, image, department_id) FROM stdin;
1	VOLEIBOL FEMENINO 2026 en FIUBA Comienzo de entrenamientos	Hola como están, desde el Departamento de Deportes de la Facultad de Ingeniería les informamos que el martes 10 de febrero comenzamos los entrenamientos de voleibol femenino en el gimnasio de la Facultad de Ingeniería.\n\nLos entrenamientos se realizarán a partir de marzo y durante todo el año\n\nDamas: Martes de 19:00 a 21:00 hs y los días sábados de 15:00 hs a 17:00 hs en la facultad\n\nEste martes 24 de febrero comenzamos los entrenamientos semanales\n\nNos acompañaron este Martes 7 de abril:\n\nÁlvarez, Nisha, Bernárdez, Delfina, Blanco, María Florencia, Casareto, Eliana, Celis, Ludmila Ayelen, Cuadros Pablo, Giannina, Cubecino, Cintia Belén, Foglia, María Fernanda, Jiménez Sánchez, Sofía, Osuma, Rusmar, Pérez Makishi, Daniela Hemilse, Ponce de León, Guadalupe, Rodríguez, Bettina, Simonazzi, Agustina, Soto, Marín, Suarez Hans, Carolina y Villamil Ciro, Ana Sofía\n\ny queremos agradecer la presencia de Juan Benigni, Nicolás Luppi y Santiago Cabrera que gracias a su colaboración desinteresada podemos entrenar en la semana ya que todavía no hemos podido contar con el Utilero en el gimnasio\n\nTe esperamos para entrenar, para probarte para los equipos representativos o si estas jugando en algún club sumarte para los equipos de la Facultad que participa del Torneo Interfacultades entre todas las facultades de la UBA y en el Torneo Externo\n\nSi estas interesada o tenes alguna duda nos escribís a depofiuba@yahoo.com o podes pasar por el Departamento de Deportes de la Facultad de Ingeniería, Paseo Colon 850 PB de lunes a viernes de 13 a 20 hs.	deportes	2026-05-09 18:39:56.134098+00	2026-05-09 18:56:02.480185+00	99	\N	\N
2	El pasto ahora puede ser azul	Esto es un test	institucional	2026-06-07 20:48:52.418494+00	2026-06-07 20:48:52.418515+00	105		3
\.


--
-- Data for Name: backend_notification; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_notification (id, title, message, created_at, sender_id, is_urgent, send_push, send_email, image, semester_id, action_url, department_id) FROM stdin;
1	Facultad cerrada por corte de luz	Por corte de luz, la facultad permanecera cerrada el dia de hoy	2026-04-25 17:45:26.270102+00	99	t	t	t		\N	\N	\N
2	Bienvenidos a algo 1	Bienvenidos a la materia	2026-04-29 03:34:25.934754+00	6	f	f	f		14	\N	\N
3	Cambio de Aula	Se cambia el aula a la 200	2026-04-29 19:54:05.3127+00	6	t	f	f		14	\N	\N
4	Otro cambio de aula	201	2026-04-29 19:57:55.662402+00	6	t	f	f		14	\N	\N
5	Aviso general	Material de la materia	2026-04-29 19:58:17.575081+00	6	f	f	f		14	\N	\N
6	Se cancela parcial	No se toma el martes	2026-04-29 20:12:37.894534+00	6	t	f	f		14	\N	\N
7	Paro docente del 12/5	No se dará clases el 12/5	2026-04-29 20:57:50.863886+00	6	f	f	f		14	\N	\N
8	Recordatorio: Test event	El evento 'Test event' vence en 6 días (2026-05-14).	2026-05-08 22:53:45.666483+00	\N	f	f	f		\N	\N	\N
9	Nueva solicitud de contacto	Joaquin Andresen te envió una solicitud de contacto.	2026-06-03 01:19:12.607107+00	100	f	f	f		\N	Contacts	\N
10	Esto es un test	Esto es un test	2026-06-07 20:37:39.676824+00	105	f	f	f		\N	\N	3
\.


--
-- Data for Name: backend_passwordresetotp; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_passwordresetotp (id, code_hash, expires_at, attempts, max_attempts, is_used, created_at, updated_at, user_id) FROM stdin;
1	337e54413a15bc26b89743ffd7df9d408408327bc2af76f0c3a9a4f3f882402d	2026-04-13 23:14:28.248931+00	0	5	t	2026-04-13 22:59:28.250391+00	2026-04-13 23:02:58.950042+00	100
2	c69660dc5986c5234cd0851e605a05b1fdf806176fcb44082ff8e64f649c07a9	2026-04-13 23:17:59.196828+00	1	5	t	2026-04-13 23:02:59.198415+00	2026-04-13 23:05:17.608677+00	100
3	7fe042f5e453dbf6815301ea167fd27796948793d06d444bb9fa37aa610b210b	2026-04-13 23:20:17.833344+00	0	5	t	2026-04-13 23:05:17.834573+00	2026-04-13 23:05:43.977619+00	100
4	ab03e0cdcf86f7ec7c0d6abd35d4d90ff0159cb5b86f533efd54ad7e8004a4be	2026-04-25 17:49:52.52243+00	0	5	t	2026-04-25 17:34:52.524085+00	2026-04-25 17:35:55.323246+00	100
\.


--
-- Data for Name: backend_secretary; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_secretary (id, name, location, schedule, contact_info, created_at, updated_at, parent_secretary_id) FROM stdin;
\.


--
-- Data for Name: backend_semester; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_semester (id, year_moment, start_date, commission_id, classes_amount, minimum_attendance, calendar_source_url) FROM stdin;
12	FS	2026-03-17 03:00:00+00	6	16	0.75	\N
13	FS	2026-03-17 03:00:00+00	1	16	0.75	\N
14	FS	2026-03-17 03:00:00+00	7	16	0.75	\N
15	SS	2024-08-05 03:00:00+00	8	16	0.75	\N
16	FS	2024-03-11 03:00:00+00	9	16	0.75	\N
1	FS	2024-03-10 22:00:00+00	1	10	0.8	\N
2	SS	2023-07-10 22:00:00+00	4	10	0.8	\N
4	SS	2024-07-10 22:00:00+00	2	18	0	\N
5	FS	2024-03-10 22:00:00+00	3	18	0	\N
6	SS	2024-07-10 22:00:00+00	3	18	0	\N
7	FS	2024-03-10 22:00:00+00	4	18	0	\N
8	SS	2024-07-10 22:00:00+00	4	18	0	\N
10	SS	2024-07-10 22:00:00+00	5	18	0	\N
11	FS	2024-04-10 22:00:00+00	4	18	0	\N
9	FS	2024-03-10 22:00:00+00	5	18	0	https://docs.google.com/spreadsheets/d/test123/edit
17	FS	2026-03-01 00:00:00+00	5	18	0.75	https://docs.google.com/spreadsheets/d/test123/edit
3	FS	2026-03-17 03:00:00+00	2	18	0.8	\N
18	FS	2026-03-01 00:00:00+00	11	18	0	\N
\.


--
-- Data for Name: backend_semesterschedule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_semesterschedule (id, day_of_week, start_time, end_time, semester_id) FROM stdin;
1	2	19:00:00	22:00:00	12
2	4	19:00:00	22:00:00	12
3	1	17:00:00	20:00:00	13
4	3	17:00:00	20:00:00	13
6	5	14:00:00	18:00:00	17
7	0	14:00:00	17:00:00	14
8	4	18:00:00	21:00:00	14
9	0	14:00:00	17:00:00	18
10	4	18:00:00	21:00:00	18
\.


--
-- Data for Name: backend_staff; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_staff (user_id, department_siu_id, department_id, is_bedelia, secretary_id) FROM stdin;
105	0	3	f	\N
106	0	4	f	\N
107	0	5	f	\N
108	0	6	f	\N
109	0	7	f	\N
110	0	8	f	\N
111	0	9	f	\N
112	0	10	f	\N
113	0	11	f	\N
114	0	12	f	\N
115	0	13	f	\N
116	0	14	f	\N
117	0	15	f	\N
118	0	16	f	\N
119	0	17	f	\N
120	0	18	f	\N
121	0	19	f	\N
122	0	20	f	\N
125	0	\N	t	\N
\.


--
-- Data for Name: backend_student; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_student (user_id, padron, inscripto, face_encodings, image) FROM stdin;
11		f	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
101	108257	t	{}	\N
102	104093	f	{}	\N
1	94557	t	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
100	102707	f	{-0.598310649394989,0.7096899747848511,-0.14428767561912537,0.4347063899040222,-0.34771454334259033,-0.33923742175102234,0.11654721945524216,-0.5873616337776184,-0.9335787296295166,0.6697256565093994,-0.10748742520809174,0.06923931837081909,0.13645629584789276,0.3326205611228943,-0.05847809091210365,-0.8883445858955383,-0.41127291321754456,0.12163423746824265,0.4581702649593353,0.3634148836135864,-0.11151743680238724,-0.7186563611030579,0.6960922479629517,0.01598253846168518,0.2612946033477783,0.8825334906578064,0.11820365488529205,0.18114769458770752,-0.4874694347381592,-0.04232155531644821,-0.43314114212989807,0.04237264767289162,-0.7718963623046875,-0.4531726837158203,-0.7586913704872131,-0.11757505685091019,-0.45450982451438904,0.060319751501083374,-0.5544279217720032,0.29890576004981995,0.07382002472877502,-0.30952179431915283,0.14575211703777313,0.4326142966747284,0.1937079280614853,-0.2841511368751526,0.208603173494339,-0.10819246619939804,-0.8717523813247681,-0.19469459354877472,-0.2508741319179535,0.8288562297821045,1.0892647504806519,0.3475768566131592,-0.8228286504745483,0.06454014033079147,0.648004412651062,-0.33135807514190674,-0.6135404109954834,0.07461371272802353,-0.6530121564865112,-0.10121186822652817,0.03670969977974892,-0.18555791676044464,0.22731900215148926,0.08662479370832443,-0.25681647658348083,0.3470146656036377,0.24092036485671997,0.7324722409248352,-0.8157190680503845,0.8180846571922302,-0.6913157105445862,-0.6339666843414307,-0.007441062014549971,0.18106412887573242,0.3011723458766937,0.36871767044067383,1.2062864303588867,-0.474132776260376,0.33982300758361816,0.03781815618276596,-0.09037654846906662,0.13737104833126068,0.053843408823013306,0.47658008337020874,0.094184011220932,0.348655104637146,0.4771036207675934,0.3998887836933136,0.31889986991882324,-0.27501168847084045,0.17608946561813354,-0.13702471554279327,-0.16577638685703278,0.18590302765369415,-0.3994646370410919,-0.18724358081817627,-0.3787221610546112,0.8073841333389282,-0.1678280532360077,-0.1587815135717392,-0.9160568118095398,-0.08238159120082855,-0.22749948501586914,0.8121770024299622,-0.2268417328596115,0.2175913155078888,0.24122384190559387,-0.03365484997630119,-0.5875319838523865,0.31341585516929626,0.10735509544610977,0.3729305863380432,-0.9059689044952393,0.2903265357017517,-0.15080668032169342,0.491399884223938,0.18678097426891327,1.1178960800170898,-0.8432510495185852,-0.377299964427948,0.36008667945861816,0.013560841791331768,-0.5517675280570984,-0.3423535227775574,0.7614191770553589,-0.6661955118179321}	https://ludo3-test.s3.amazonaws.com/3ce6dea7-edb1-490b-addf-fa3ed567b2bc.jpg
2	95557	t	{-0.083392322063446,0.0809348896145821,0.0733130425214767,-0.0540066361427307,-0.174843937158585,-0.00358903408050537,-0.0368717201054096,-0.100299723446369,0.119234308600426,-0.150944456458092,0.274468034505844,-0.04979457706213,-0.219506233930588,0.0931993946433067,0.00702124834060669,0.134448751807213,-0.180334195494652,-0.0947339236736298,-0.126001879572868,-0.143079906702042,0.0586014091968536,0.0765982791781425,0.0661674439907074,0.0862715393304825,-0.20697033405304,-0.316634684801102,-0.0539165139198303,-0.0904162973165512,0.0664069578051567,-0.0302533656358719,0.0158378854393959,0.0544502250850201,-0.11605241894722,0.0691349059343338,0.0934454724192619,0.0260029789060354,-0.0573304891586304,-0.135616987943649,0.229721382260323,-0.00412528589367867,-0.16940613090992,0.0415492504835129,0.117457590997219,0.14024256169796,0.133675053715706,-0.0160063505172729,0.119582295417786,-0.18397618830204,0.100715056061745,-0.265116959810257,0.0751597061753273,0.184965044260025,0.0381531417369843,0.116577640175819,0.11553929746151,-0.198301911354065,-0.00435981154441833,0.176023676991463,-0.175070196390152,0.0799106135964394,0.0574804730713367,0.063263900578022,-0.056468091905117,-0.10352811217308,0.175353273749352,0.171320796012878,-0.165873363614082,-0.160760104656219,0.144699051976204,-0.173176825046539,-0.100517690181732,0.167922675609589,-0.125599935650826,-0.238686203956604,-0.150348991155624,0.0258684754371643,0.439466744661331,0.188441887497902,-0.171247497200966,-0.026619590818882,-0.0542668923735619,-0.0767191126942635,0.00836376845836639,0.100862897932529,-0.0804525166749954,-0.0869344472885132,-0.0141675304621458,0.0729045867919922,0.217370554804802,0.00485210120677948,-0.00392106920480728,0.312765419483185,0.0977946147322655,-0.01722751557827,0.0218802131712437,0.110804937779903,-0.157148525118828,-0.0638326779007912,-0.0949655696749687,-0.058760866522789,-0.0520573034882545,-0.0655839741230011,-0.0502914637327194,0.0605535358190536,-0.235313981771469,0.232044845819473,-0.087082676589489,-0.104579024016857,-0.0518472343683243,0.0245128720998764,-0.0159405618906021,0.0340693891048431,0.13385871052742,-0.298567950725555,0.125581994652748,0.179684981703758,0.0917067676782608,0.200989812612534,0.0153898820281029,0.0784021764993668,0.0437071621417999,-0.0450139120221138,-0.136880353093147,-0.101415947079659,-0.0015685111284256,-0.0823299288749695,-0.0465857088565826,-0.00527937710285187}	\N
3	97123	t	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
4	95123	t	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
10		f	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
12	100608	f	{-0.08454550802707672,0.027362827211618423,0.03746267408132553,-0.04784805700182915,-0.037854649126529694,0.003210900817066431,-0.0533762127161026,-0.05898168683052063,0.22817188501358032,-0.13154156506061554,0.18738310039043427,0.08356784284114838,-0.18348738551139832,-0.11847204715013504,0.05626807361841202,0.12041094899177551,-0.10499847680330276,-0.17417950928211212,-0.01362577360123396,-0.14271220564842224,-0.02411406859755516,0.020366564393043518,0.051775164902210236,0.09282170236110687,-0.18826474249362946,-0.3499237298965454,-0.07844856381416321,-0.10160083323717117,-0.04125536233186722,-0.1549772471189499,0.0032408395782113075,0.053460653871297836,-0.15430966019630432,0.012357322499155998,-0.0003679729998111725,0.1209871917963028,0.009185802191495895,-0.0767359584569931,0.26236218214035034,0.03393035754561424,-0.16680286824703217,0.014552688226103783,0.0003561433404684067,0.2585192620754242,0.13065588474273682,-0.04336143285036087,0.07357817888259888,-0.06267054378986359,0.1973985731601715,-0.19217635691165924,0.1427125334739685,0.10856544226408005,0.018124282360076904,-0.0223429873585701,0.07701267302036285,-0.15181653201580048,-0.0809897780418396,0.1144961342215538,-0.18905745446681976,0.08938880264759064,0.025281062349677086,-0.04088897258043289,-0.11576084792613983,-0.06644343584775925,0.17143289744853973,0.20879796147346497,-0.11577669531106949,-0.20483404397964478,0.17747993767261505,-0.15447767078876495,-0.05035300925374031,0.10458440333604813,-0.11769215762615204,-0.17877542972564697,-0.25856339931488037,0.09714840352535248,0.3809138536453247,0.10006549954414368,-0.14190971851348877,0.04075497388839722,-0.03998376429080963,-0.03380875661969185,0.038024500012397766,0.10401611775159836,-0.0853421539068222,0.07207275927066803,-0.05436929687857628,0.11043791472911835,0.20690064132213593,0.13096526265144348,-0.12420376390218735,0.1887817531824112,-0.009740717709064484,0.09809563308954239,0.06741926074028015,0.08769679069519043,-0.07505600154399872,0.003221578896045685,-0.17075343430042267,0.006683525629341602,0.08330745995044708,-0.048684172332286835,0.024372808635234833,0.08807570487260818,-0.15069876611232758,0.17632591724395752,-0.017660461366176605,-0.016753090545535088,-0.01529616117477417,0.1183779165148735,-0.17212708294391632,-0.003024898236617446,0.13987450301647186,-0.2828315794467926,0.1814713329076767,0.09604962170124054,0.08405382186174393,0.16548503935337067,0.08059230446815491,0.06948584318161011,0.015779312700033188,-0.06419774144887924,-0.17899344861507416,-0.03447758033871651,0.024774283170700073,0.01543467864394188,0.13101191818714142,0.07711340487003326}	\N
13	101049	f	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
14	100812	f	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
15	104503	f	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	\N
127		f	{}	\N
\.


--
-- Data for Name: backend_studentcareer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_studentcareer (id, plan, enrollment_date, graduation_date, career_id, student_id) FROM stdin;
1	INF-2023	2018-03-01	\N	1	100
2	INF-2023	2019-02-28	\N	1	102
3	86V14	2021-09-06	\N	2	102
\.


--
-- Data for Name: backend_studygroup; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_studygroup (id, name, created_at, creator_id) FROM stdin;
\.


--
-- Data for Name: backend_teacher; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_teacher (user_id, legajo, face_encodings, siu_id) FROM stdin;
5	12345	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	1
6	12346	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	2
7	12347	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	3
8	12348	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	4
9	87654	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	5
14	100812	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	6
12	100608	{-0.08454550802707672,0.027362827211618423,0.03746267408132553,-0.04784805700182915,-0.037854649126529694,0.003210900817066431,-0.0533762127161026,-0.05898168683052063,0.22817188501358032,-0.13154156506061554,0.18738310039043427,0.08356784284114838,-0.18348738551139832,-0.11847204715013504,0.05626807361841202,0.12041094899177551,-0.10499847680330276,-0.17417950928211212,-0.01362577360123396,-0.14271220564842224,-0.02411406859755516,0.020366564393043518,0.051775164902210236,0.09282170236110687,-0.18826474249362946,-0.3499237298965454,-0.07844856381416321,-0.10160083323717117,-0.04125536233186722,-0.1549772471189499,0.0032408395782113075,0.053460653871297836,-0.15430966019630432,0.012357322499155998,-0.0003679729998111725,0.1209871917963028,0.009185802191495895,-0.0767359584569931,0.26236218214035034,0.03393035754561424,-0.16680286824703217,0.014552688226103783,0.0003561433404684067,0.2585192620754242,0.13065588474273682,-0.04336143285036087,0.07357817888259888,-0.06267054378986359,0.1973985731601715,-0.19217635691165924,0.1427125334739685,0.10856544226408005,0.018124282360076904,-0.0223429873585701,0.07701267302036285,-0.15181653201580048,-0.0809897780418396,0.1144961342215538,-0.18905745446681976,0.08938880264759064,0.025281062349677086,-0.04088897258043289,-0.11576084792613983,-0.06644343584775925,0.17143289744853973,0.20879796147346497,-0.11577669531106949,-0.20483404397964478,0.17747993767261505,-0.15447767078876495,-0.05035300925374031,0.10458440333604813,-0.11769215762615204,-0.17877542972564697,-0.25856339931488037,0.09714840352535248,0.3809138536453247,0.10006549954414368,-0.14190971851348877,0.04075497388839722,-0.03998376429080963,-0.03380875661969185,0.038024500012397766,0.10401611775159836,-0.0853421539068222,0.07207275927066803,-0.05436929687857628,0.11043791472911835,0.20690064132213593,0.13096526265144348,-0.12420376390218735,0.1887817531824112,-0.009740717709064484,0.09809563308954239,0.06741926074028015,0.08769679069519043,-0.07505600154399872,0.003221578896045685,-0.17075343430042267,0.006683525629341602,0.08330745995044708,-0.048684172332286835,0.024372808635234833,0.08807570487260818,-0.15069876611232758,0.17632591724395752,-0.017660461366176605,-0.016753090545535088,-0.01529616117477417,0.1183779165148735,-0.17212708294391632,-0.003024898236617446,0.13987450301647186,-0.2828315794467926,0.1814713329076767,0.09604962170124054,0.08405382186174393,0.16548503935337067,0.08059230446815491,0.06948584318161011,0.015779312700033188,-0.06419774144887924,-0.17899344861507416,-0.03447758033871651,0.024774283170700073,0.01543467864394188,0.13101191818714142,0.07711340487003326}	7
13	101049	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	8
15	104503	{-0.0718940645456314,0.158472895622253,0.129906058311462,-0.0620200484991074,-0.0562259405851364,-0.0182943046092987,-0.124562457203865,-0.11715641617775,0.12282095849514,-0.0747286081314087,0.205223634839058,0.0837890282273293,-0.202225238084793,0.0052119717001915,0.0129153057932854,0.091251365840435,-0.13077113032341,-0.100294426083565,-0.0693373382091522,-0.0663144141435623,0.0646603107452393,0.120691254734993,0.0327602624893188,0.0378443226218224,-0.0953375324606895,-0.404435753822327,-0.134638428688049,-0.0343223325908184,0.0510790348052979,-0.0333549976348877,0.0231383666396141,0.0124428793787956,-0.144889608025551,-0.00794278085231781,0.0571465194225311,0.0476001799106598,-0.0120797976851463,0.00288403779268265,0.163492813706398,0.0567040182650089,-0.121078208088875,0.132355138659477,0.0397978499531746,0.282226592302322,0.186612159013748,0.0570859722793102,0.110026188194752,-0.0754604637622833,0.0904536470770836,-0.226782888174057,0.167149156332016,0.140036821365356,0.134269043803215,0.0595759190618992,0.162044957280159,-0.149873271584511,-0.082541286945343,0.156666561961174,-0.16235014796257,0.196501970291138,0.101206034421921,-0.0161009896546602,-0.0156352296471596,-0.0834633111953735,0.176220640540123,0.133509784936905,-0.171006768941879,-0.115628361701965,0.130389183759689,-0.129572838544846,-0.0746951699256897,0.00165760517120361,-0.14546474814415,-0.1446772813797,-0.254748046398163,0.137416675686836,0.40243273973465,0.158332332968712,-0.257076740264893,-0.0350575596094131,-0.0156839564442635,0.00594057142734528,0.0493050366640091,0.0525273680686951,-0.0931551679968834,-0.0794475302100182,-0.0318538695573807,0.0529888868331909,0.195399969816208,0.0846337974071503,-0.0530000180006027,0.286837339401245,0.0123770795762539,0.0868316814303398,0.0272195339202881,0.0733735859394073,-0.113147214055061,-0.0799082517623901,-0.182952851057053,0.0191846191883087,-0.10839356482029,-0.0523698329925537,-0.0217332243919373,0.130411267280579,-0.111771732568741,0.192079693078995,-0.0256330668926239,-0.0165537409484386,-0.0343894511461258,0.165916308760643,-0.159314647316933,-0.0783812403678894,0.138054117560387,-0.206586733460426,0.220194667577744,0.175803557038307,0.0580093525350094,0.119370847940445,0.0532389022409916,0.0909135341644287,0.05124381929636,0.00429204106330872,-0.102031789720058,-0.100409373641014,0.0382491275668144,-0.054313525557518,0.00801995396614075,0.0457009077072144}	10
126		{}	0
128	102999	{}	0
\.


--
-- Data for Name: backend_teacherrole; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_teacherrole (id, role, commission_id, teacher_id, grader_weight) FROM stdin;
1	Profesor Adjunto	4	14	3
2	Profesor Adjunto	5	13	3
3	Profesor Adjunto	5	14	3
4	Profesor Adjunto	1	12	3
5	Profesor Adjunto	1	128	1
\.


--
-- Data for Name: backend_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_user (id, password, last_login, is_superuser, email, is_staff, is_active, date_joined, is_student, is_teacher, first_name, last_name, username, dni, created_at, updated_at, github_url, linkedin_url, profile_photo) FROM stdin;
7	pbkdf2_sha256$216000$YuTGjkcZZ9Gg$xb09Z9L39UMrlPclVDP5L5Z6xnKgC4EJyr8G3o3SoIU=	\N	f	dato@dato.com	f	t	2026-04-29 03:26:54.6985+00	f	t	Adeodato	Simó		99999999	2026-04-29 03:26:54.698529+00	2026-04-29 03:26:54.698536+00			\N
9	pbkdf2_sha256$216000$IxrUYoFTW9kT$72ci7XfWvF1IsyuPh+0m+wsrCOo7ZBBzTfS1UKBKp5M=	\N	f	mariano.mendez@gmail.com	f	t	2026-04-29 03:26:55.299717+00	f	t	Mariano	Mendez		15151515	2026-04-29 03:26:55.299753+00	2026-04-29 03:26:55.299762+00			\N
10	pbkdf2_sha256$216000$eeiDCg64oj72$a2vNOh+Qyn3Glx/O2ES7CWS+PUN8id2O9X4GynYqQpU=	\N	f	alumno.fake@123.com	f	t	2026-04-29 03:26:55.53235+00	t	f	Alumno	Fake		17171717	2026-04-29 03:26:55.532365+00	2026-04-29 03:26:55.532368+00			\N
11	pbkdf2_sha256$216000$hmxVq7PYJ6Cv$7dTA0DZS+IUzymVkyLl2ynOo4sI/fFOdyFLPsmVMl2g=	\N	f	alumna.fake@123.com	f	t	2026-04-29 03:26:55.765581+00	t	f	Alumna	Fake		18181818	2026-04-29 03:26:55.765609+00	2026-04-29 03:26:55.765616+00			\N
12	pbkdf2_sha256$216000$kBmSfk7HDVnh$RJ4mkjMVH3xK/Q+4dNirtwlTypfcdVCQfe6EY13nzJw=	\N	f	fgiordano@fi.uba.ar	f	t	2026-04-29 03:26:55.999505+00	t	t	Franco	Giordano		41107811	2026-04-29 03:26:55.999536+00	2026-04-29 03:26:55.999544+00			\N
8	pbkdf2_sha256$216000$dNCwh8U6Mjrx$8hDDcoFofkGFHiWGd/ZWKhdTo8/+NISANLC9LPbI+v4=	\N	f	pablo.cosso@gmail.com	f	t	2026-04-29 03:26:54.942072+00	f	t	Pablo	Cosso		13123123	2026-04-29 03:26:54.942124+00	2026-04-29 03:26:54.942141+00			\N
6	pbkdf2_sha256$216000$dNCwh8U6Mjrx$8hDDcoFofkGFHiWGd/ZWKhdTo8/+NISANLC9LPbI+v4=	\N	f	dessaya@gmail.com	f	t	2026-04-29 03:26:54.467668+00	f	t	Diego	Essaya		30123123	2026-04-29 03:26:54.467692+00	2026-04-29 03:26:54.467697+00			\N
13	pbkdf2_sha256$216000$DMbyFN1s1wHH$GJq6bazJNEB4ZjeRNokMqOueGgSPeCztMvTwZSYf39s=	\N	f	airibarren@fi.uba.ar	f	t	2026-04-29 03:26:56.233744+00	t	t	Alvaro Patricio	Iribarren		41318038	2026-04-29 03:26:56.233771+00	2026-04-29 03:26:56.233778+00			\N
14	pbkdf2_sha256$216000$iCf014e41Ivo$Ln0sQe+5DmV29ia8Bqd/+LEM5nDOLVSXYl6zlD2yh9c=	\N	f	macohen@fi.uba.ar	f	t	2026-04-29 03:26:56.465084+00	t	t	Martin	Cohen		41099526	2026-04-29 03:26:56.465141+00	2026-04-29 03:26:56.465148+00			\N
102	pbkdf2_sha256$216000$dNCwh8U6Mjrx$8hDDcoFofkGFHiWGd/ZWKhdTo8/+NISANLC9LPbI+v4=	\N	f	mmerlog@fi.uba.ar	f	t	2026-04-29 03:08:51.232097+00	t	f	Matías Sebastián	Merlo Gonzalez	mmerlog@fi.uba.ar	42150053	2026-04-29 03:08:51.232126+00	2026-04-29 03:08:51.232133+00			\N
101	pbkdf2_sha256$216000$aDrhrNZI0vLM$zY88CVA5g7ja1E9/hxXp3xwpH9fkjQlwONl2PDe+sok=	\N	f	vlanzillotta@fi.uba.ar	f	t	2026-04-26 21:05:16.74225+00	t	f	Valentina	Lanzillotta		43459394	2026-04-26 21:05:16.742269+00	2026-04-26 21:05:16.742271+00			\N
106	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept4@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Computación		00000002	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
107	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept5@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Construcciones y Estructuras		00000003	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
108	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept6@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Electrónica		00000004	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
109	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept7@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Energía		00000005	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
1	pbkdf2_sha256$216000$ElD2fYo2MjRF$eTQ5L67cLo2Dda/tZqBOZJcqwvBgxUO+hnXOzs5liHw=	\N	f	fede.est@gmail.com	f	t	2026-04-29 03:26:52.350735+00	t	f	Federico	Esteban		37247189	2026-04-29 03:26:52.350749+00	2026-04-29 03:26:52.350752+00			\N
2	pbkdf2_sha256$216000$v2IQlmMotHis$QZ+3LIT4Ta+CXCwJRTTwWD28DoYP9n12pJcjYKqdwW8=	\N	f	danielap.riesgo@gmail.com	f	t	2026-04-29 03:26:53.246477+00	t	f	Daniela	Riesgo		38157957	2026-04-29 03:26:53.246501+00	2026-04-29 03:26:53.246507+00			\N
3	pbkdf2_sha256$216000$IkPqPWgC2ekN$6f5dczFprzB4GTsMxNgT47uZTU3vmWLFU42gpsU+s9g=	\N	f	juani.kristal@gmail.com	f	t	2026-04-29 03:26:53.55947+00	t	f	Juan Ignacio	Kristal		40123123	2026-04-29 03:26:53.559513+00	2026-04-29 03:26:53.559524+00			\N
4	pbkdf2_sha256$216000$Gt2XtIo3zQzd$NqINE/NOtbCbW3nFztJI7LjKDA2BGgThNxARtmRuRj4=	\N	f	alevinas@gmail.com	f	t	2026-04-29 03:26:53.824589+00	t	f	Alejandro	Levinas		36123123	2026-04-29 03:26:53.824604+00	2026-04-29 03:26:53.824607+00			\N
110	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept8@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Estabilidad		00000006	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
111	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept9@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Física		00000007	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
112	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept10@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Gestión		00000008	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
113	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept11@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Hidráulica		00000009	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
114	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept12@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Idiomas		00000010	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
115	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept13@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Ingeniería Mecánica		00000011	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
116	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept14@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Ingeniería Naval		00000012	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
117	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept15@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Ingeniería Química		00000013	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
118	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept16@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Matemática		00000014	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
119	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept17@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Química		00000015	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
120	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept18@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Seguridad del Trabajo y Ambiente		00000016	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
121	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept19@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Tecnología Industrial		00000017	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
99	pbkdf2_sha256$1000000$xkhwxIbdvr4vGDRrSTff71$pHQCHgWXyvmdumS3Z/IgWLZB0s6gsMSzzJGc/Og4MLE=	2026-05-08 22:09:28.759724+00	t	admin@ludo.com	t	t	2026-04-29 03:26:57.554749+00	f	f	Super	Admin		11111111	2026-04-29 03:26:57.554786+00	2026-04-29 03:26:57.554793+00			\N
100	pbkdf2_sha256$216000$903L0NIPOL0X$6AO4Ul78uLVSiBestdo3m2M9Urf7yHDfOJfcSl1fAWA=	\N	f	jandresen@fi.uba.ar	f	t	2026-04-11 16:45:13.69772+00	t	f	Joaquin	Andresen	jandresen@fi.uba.ar	41835723	2026-04-11 16:45:13.69791+00	2026-04-11 16:45:13.697931+00	https://github.com/jandresen99	https://www.linkedin.com/in/joaquin-andresen-52378711a/	\N
5	pbkdf2_sha256$1000000$StBJwW0juTboJONdDwRGvK$jJKS3J9hafleszdh+Oj6dhH8x+K+2y+iXa/pde/bqio=	\N	f	jorge.collinet@gmail.com	f	t	2026-04-29 03:26:54.0711+00	f	t	Jorge	Collinet		35624188	2026-04-29 03:26:54.07112+00	2026-04-29 03:26:54.071124+00			\N
105	pbkdf2_sha256$1000000$qsqPc3ebmSTzcrkiQQfz59$exKG7FZkneHyk43dBXeBpgf1oFRSoxTzT1n1h1frnl8=	\N	f	admin.dept3@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Agrimensura		00000001	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
122	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	admin.dept20@dept.fi.uba.ar	t	t	2026-05-13 00:05:02.295828+00	f	f	Admin	Transporte		00000018	2026-05-13 00:05:02.295828+00	2026-05-13 00:05:02.295828+00			\N
125	pbkdf2_sha256$216000$oUpIgSbqO0Ht$rG5qd+B8TUcVywJA7PQ8scQ+UT154acNIAFoJFp8Lu4=	\N	f	bedelia@dept.fi.uba.ar	t	t	2026-05-17 21:22:24.693593+00	f	f	Bedelía	FIUBA		00000019	2026-05-17 21:22:24.693593+00	2026-05-17 21:22:24.693593+00			\N
126	pbkdf2_sha256$216000$7wvxf2eWxUjO$MqqnTHiWc/xVYGmkbhQT2Jv9+2autQZbVWuYNuR+47s=	\N	f	docente.test@fi.uba.ar	f	t	2026-05-27 20:06:44.40446+00	f	f	Docente	Test		12345678	2026-05-27 20:06:44.404507+00	2026-05-27 20:06:44.404515+00			\N
127	pbkdf2_sha256$216000$w1nwbFoQSfvo$UtePq8ku24XYkn+cZ14g4nijuiy/2qX/2cJKj7xfb+4=	\N	f	alumno.test@fi.uba.ar	f	t	2026-05-27 20:06:48.178669+00	f	f	Alumno	Test		87654321	2026-05-27 20:06:48.178721+00	2026-05-27 20:06:48.17873+00			\N
15	pbkdf2_sha256$1000000$ca8hsYKYhsssfZwSUJ2cH3$41uGHi5k1hjSsgUUOiz5FxC4j3OJHsRZ697GH0aJows=	\N	f	ggordyn@fi.uba.ar	f	t	2026-04-29 03:26:56.698388+00	t	t	Gonzalo	Gordyn Biello		41779246	2026-04-29 03:26:56.698403+00	2026-04-29 03:26:56.698406+00			\N
128	pbkdf2_sha256$1000000$vTl0RoIOa0WcsRfqOeEMAC$+bOOQ0dM22P+TABmZ0uHCSCiYitezjI0/17fycXowD0=	\N	f	joacoprofe@fi.uba.ar	f	t	2026-06-07 19:23:20.774948+00	f	t	Joaco	Profe		41835722	2026-06-07 19:23:20.774974+00	2026-06-07 19:23:20.774975+00			\N
\.


--
-- Data for Name: backend_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: backend_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: backend_usernotification; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.backend_usernotification (id, is_read, notification_id, user_id) FROM stdin;
2	f	1	3
3	f	1	99
4	f	1	2
5	f	1	14
6	f	1	9
8	f	1	5
9	f	1	4
10	f	1	10
11	f	1	11
12	f	1	13
13	f	1	100
14	f	1	7
15	f	1	12
16	f	1	8
17	f	2	100
19	f	3	100
21	f	4	100
24	f	5	100
26	t	5	1
23	t	4	1
7	t	1	6
27	f	6	100
30	f	7	100
29	t	6	1
32	t	7	1
33	f	8	10
34	f	8	11
35	f	8	12
36	f	8	13
37	f	8	14
38	f	8	15
39	f	8	100
41	f	8	102
42	f	8	1
43	f	8	2
44	f	8	3
45	f	8	4
40	t	8	101
46	t	9	15
47	f	10	9
48	f	10	14
49	f	10	5
50	f	10	100
51	f	10	113
52	f	10	119
53	f	10	11
54	f	10	117
55	f	10	111
56	f	10	108
57	f	10	109
58	f	10	10
59	f	10	118
60	f	10	4
61	f	10	112
62	f	10	127
63	f	10	110
64	f	10	126
65	f	10	114
66	f	10	2
67	f	10	8
68	f	10	1
69	f	10	128
70	f	10	116
71	f	10	99
72	f	10	101
73	f	10	122
74	f	10	13
75	f	10	12
76	f	10	6
77	f	10	106
78	f	10	115
79	f	10	7
80	f	10	105
81	f	10	125
82	f	10	3
83	f	10	102
84	f	10	107
85	f	10	121
86	f	10	120
87	f	10	15
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-05-08 22:13:40.655211+00	11	2026 · Inscripción para Evaluaciones Integradoras (1C) (2026-06-08 – 2026-06-13)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
2	2026-05-08 22:13:41.269618+00	9	2026 · Período para completar encuestas estudiantiles (1C) (2026-06-15 – 2026-06-27)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
3	2026-05-08 22:13:41.883905+00	17	2026 · Publicación oferta horaria para cursar (2C) (2026-06-22 – 2026-06-27)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
4	2026-05-08 22:13:42.498429+00	18	2026 · Publicación de Prioridades para Inscripción (2C) (2026-06-29 – 2026-07-04)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
5	2026-05-08 22:13:43.11301+00	33	2026 · Período de Solicitud de Excepciones de Correlatividades (1C→2C) (2026-07-06 – 2026-07-18)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
6	2026-05-08 22:13:43.726881+00	19	2026 · Inscripción para Cursar Asignaturas (2C) (2026-07-06 – 2026-07-18)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
7	2026-05-08 22:13:44.239372+00	40	2026 · Recepción de trámites de simultaneidad entre carreras de FIUBA (2C) (2026-08-03 – 2026-08-22)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
8	2026-05-08 22:13:44.854056+00	20	2026 · Desinscripción de Asignaturas (2C) (2026-08-03 – 2026-08-15)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
9	2026-05-08 22:13:45.469874+00	16	2026 · Presentación de Certificados de Trabajo / Discapacidad (2C) (2026-08-03 – 2026-08-22)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
10	2026-05-08 22:13:46.185359+00	21	2026 · Publicación oferta horaria para cursar (1C 2027) (2026-11-02 – 2026-11-07)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
11	2026-05-08 22:13:46.775139+00	13	2026 · Inscripción para Evaluaciones Integradoras (2C) (2026-11-02 – 2026-11-07)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
12	2026-05-08 22:13:47.311679+00	22	2026 · Publicación de Prioridades para Inscripción (1C 2027) (2026-11-23 – 2026-11-28)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
13	2026-05-08 22:13:47.925574+00	34	2026 · Período de Solicitud de Excepciones de Correlatividades (2C→1C) (2026-12-07 – 2026-12-19)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
14	2026-05-08 22:13:48.540129+00	23	2026 · Inscripción para Cursar Asignaturas (1C 2027) (2026-12-07 – 2026-12-19)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
15	2026-05-08 22:13:49.155822+00	24	2026 · Desinscripción de Asignaturas (1C 2027) (2027-01-11 – 2027-01-23)	2	[{"changed": {"fields": ["Es vencimiento"]}}]	38	99
16	2026-05-08 22:44:38.857284+00	75	2026 · Test event (2026-05-14 – 2026-05-31)	1	[{"added": {}}]	38	99
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	backend	user
2	backend	final
3	backend	student
4	backend	teacher
5	backend	finalexam
6	backend	preregisteredstudent
7	backend	finaltoapprove
8	backend	staffuser
9	backend	staff
10	backend	commission
11	backend	semester
12	backend	commissioninscription
13	backend	evaluation
14	backend	teacherrole
15	backend	evaluationsubmission
16	backend	attendanceqrcode
17	backend	attendance
18	backend	auditlog
19	backend	authidentity
20	backend	teacherprofile
21	backend	workexperience
22	backend	notification
23	backend	usernotification
24	backend	department
25	admin	logentry
26	auth	permission
27	auth	group
28	contenttypes	contenttype
29	authtoken	token
30	authtoken	tokenproxy
31	sessions	session
32	push_notifications	apnsdevice
33	push_notifications	gcmdevice
34	push_notifications	wnsdevice
35	push_notifications	webpushdevice
36	backend	passwordresetotp
37	backend	semesterschedule
38	backend	academiccalendarevent
39	backend	calendareventreminder
40	backend	formproceduretype
41	backend	formtype
42	backend	formfieldtype
43	backend	catalog
44	backend	catalogitem
45	backend	form
46	backend	formdocumentsource
47	backend	formfield
48	backend	formfieldoption
49	backend	formsubmission
50	backend	formanswer
51	backend	formsubmissionstatus
52	backend	news
53	backend	catedracalendarentry
54	backend	studentcareer
55	backend	career
56	backend	secretary
57	backend	formownershipgroup
58	backend	formownershipmember
59	backend	contact
60	backend	studygroup
61	backend	groupmembership
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-04-11 16:36:13.557522+00
2	contenttypes	0002_remove_content_type_name	2026-04-11 16:36:14.843946+00
3	auth	0001_initial	2026-04-11 16:36:16.355754+00
4	auth	0002_alter_permission_name_max_length	2026-04-11 16:36:19.331339+00
5	auth	0003_alter_user_email_max_length	2026-04-11 16:36:20.1961+00
6	auth	0004_alter_user_username_opts	2026-04-11 16:36:21.057007+00
7	auth	0005_alter_user_last_login_null	2026-04-11 16:36:21.916598+00
8	auth	0006_require_contenttypes_0002	2026-04-11 16:36:22.769245+00
9	auth	0007_alter_validators_add_error_messages	2026-04-11 16:36:23.627321+00
10	auth	0008_alter_user_username_max_length	2026-04-11 16:36:24.486826+00
11	auth	0009_alter_user_last_name_max_length	2026-04-11 16:36:25.34605+00
12	auth	0010_alter_group_name_max_length	2026-04-11 16:36:26.423288+00
13	auth	0011_update_proxy_permissions	2026-04-11 16:36:27.281484+00
14	auth	0012_alter_user_first_name_max_length	2026-04-11 16:36:28.139753+00
15	backend	0001_initial	2026-04-11 16:36:30.991843+00
16	admin	0001_initial	2026-04-11 16:36:36.993777+00
17	admin	0002_logentry_remove_auto_add	2026-04-11 16:36:38.703864+00
18	admin	0003_logentry_add_action_flag_choices	2026-04-11 16:36:39.56575+00
19	authtoken	0001_initial	2026-04-11 16:36:40.64563+00
20	authtoken	0002_auto_20160226_1747	2026-04-11 16:36:42.816027+00
21	authtoken	0003_tokenproxy	2026-04-11 16:36:43.670361+00
22	backend	0002_auto_20201026_1825	2026-04-11 16:36:45.814397+00
23	backend	0003_teacher_siu_id	2026-04-11 16:36:47.102533+00
24	backend	0004_auto_20201201_2331	2026-04-11 16:36:48.821306+00
25	backend	0005_auto_20210112_2001	2026-04-11 16:36:49.89485+00
26	backend	0006_auto_20210114_0246	2026-04-11 16:36:50.980637+00
27	backend	0007_auto_20210114_1514	2026-04-11 16:36:52.486915+00
28	backend	0008_staff	2026-04-11 16:36:53.559986+00
29	backend	0009_auto_20210122_2306	2026-04-11 16:36:54.843625+00
30	backend	0010_auto_20210201_2309	2026-04-11 16:36:56.6134+00
31	backend	0011_auto_20210201_2316	2026-04-11 16:36:59.312041+00
32	backend	0012_auto_20210210_2240	2026-04-11 16:37:00.388051+00
33	backend	0013_auto_20210317_2258	2026-04-11 16:37:01.25397+00
34	backend	0014_auto_20210421_2239	2026-04-11 16:37:02.558766+00
35	backend	0015_remove_user_image	2026-04-11 16:37:03.634272+00
36	backend	0016_student_image	2026-04-11 16:37:04.709161+00
37	backend	0017_auto_20210422_0045	2026-04-11 16:37:05.781808+00
38	backend	0018_final_subject_name	2026-04-11 16:37:07.066106+00
39	backend	0019_auto_20210805_0106	2026-04-11 16:37:09.032667+00
40	backend	0020_commission	2026-04-11 16:37:10.114834+00
41	backend	0021_semester	2026-04-11 16:37:12.475757+00
42	backend	0022_auto_20231021_1529	2026-04-11 16:37:14.206613+00
43	backend	0023_evaluation	2026-04-11 16:37:16.146154+00
44	backend	0024_teacherrole	2026-04-11 16:37:18.72532+00
45	backend	0025_auto_20231202_1840	2026-04-11 16:37:20.886043+00
46	backend	0026_auto_20231202_1931	2026-04-11 16:37:24.554357+00
47	backend	0027_evaluationsubmission_grader	2026-04-11 16:37:25.638794+00
48	backend	0028_attendance_attendanceqrcode	2026-04-11 16:37:27.17098+00
49	backend	0029_evaluation_parent_evaluation	2026-04-11 16:37:30.405862+00
50	backend	0029_auto_20240203_1926	2026-04-11 16:37:31.704457+00
51	backend	0030_merge_20240217_1901	2026-04-11 16:37:32.986052+00
52	backend	0031_attendanceqrcode_expires_at	2026-04-11 16:37:34.281092+00
53	backend	0032_auto_20240224_1824	2026-04-11 16:37:36.446179+00
54	backend	0033_auditlog	2026-04-11 16:37:37.523304+00
55	backend	0034_auto_20240324_0314	2026-04-11 16:37:40.310448+00
56	backend	0035_commission_chief_teacher_grader_weight	2026-04-11 16:37:41.60156+00
57	backend	0036_auto_20240420_2126	2026-04-11 16:37:42.740374+00
58	backend	0037_auto_20240420_2129	2026-04-11 16:37:43.823637+00
59	backend	0038_auth_identity	2026-04-11 16:37:45.139013+00
60	backend	0039_populate_auth_identity	2026-04-11 16:39:00.871273+00
61	backend	0040_auto_20260221_1845	2026-04-11 16:39:02.425908+00
62	backend	0041_teacherprofile_linkedin_url	2026-04-11 16:39:04.360279+00
63	backend	0042_notification_usernotification	2026-04-11 16:39:05.689451+00
64	backend	0043_department	2026-04-11 16:39:08.253407+00
65	push_notifications	0001_initial	2026-04-11 16:39:09.554072+00
66	push_notifications	0001_initial	2026-04-11 16:39:11.880067+00
67	push_notifications	0002_auto_20160106_0850	2026-04-11 16:39:12.124696+00
68	push_notifications	0002_auto_20160106_0850	2026-04-11 16:39:12.315105+00
69	push_notifications	0003_wnsdevice	2026-04-11 16:39:12.749684+00
70	push_notifications	0004_fcm	2026-04-11 16:39:13.1841+00
71	push_notifications	0003_wnsdevice	2026-04-11 16:39:13.21605+00
72	push_notifications	0005_applicationid	2026-04-11 16:39:13.618387+00
73	push_notifications	0006_webpushdevice	2026-04-11 16:39:14.052447+00
74	push_notifications	0007_uniquesetting	2026-04-11 16:39:14.486786+00
75	push_notifications	0008_webpush_add_edge	2026-04-11 16:39:14.922852+00
76	push_notifications	0004_fcm	2026-04-11 16:39:15.155996+00
77	push_notifications	0009_alter_apnsdevice_device_id	2026-04-11 16:39:15.357311+00
78	push_notifications	0010_alter_gcmdevice_options_and_more	2026-04-11 16:39:15.792187+00
79	push_notifications	0011_alter_apnsdevice_registration_id	2026-04-11 16:39:16.226077+00
80	push_notifications	0012_alter_webpushdevice_browser	2026-04-11 16:39:16.660436+00
81	push_notifications	0005_applicationid	2026-04-11 16:39:16.697085+00
82	sessions	0001_initial	2026-04-11 16:39:17.094351+00
83	push_notifications	0006_webpushdevice	2026-04-11 16:39:17.787717+00
84	push_notifications	0007_uniquesetting	2026-04-11 16:39:19.971313+00
85	push_notifications	0008_webpush_add_edge	2026-04-11 16:39:20.843983+00
86	push_notifications	0009_alter_apnsdevice_device_id	2026-04-11 16:39:21.712169+00
87	push_notifications	0010_alter_gcmdevice_options_and_more	2026-04-11 16:39:22.594283+00
88	push_notifications	0011_alter_apnsdevice_registration_id	2026-04-11 16:39:23.892712+00
89	push_notifications	0012_alter_webpushdevice_browser	2026-04-11 16:39:24.762027+00
90	sessions	0001_initial	2026-04-11 16:39:25.834246+00
91	backend	0042_evaluation_commission	2026-04-13 22:47:54.742056+00
92	backend	0043_auto_20260306_2045	2026-04-13 22:47:56.524754+00
93	backend	0044_evaluation_submission_grade_grader_blank	2026-04-13 22:47:58.288083+00
94	backend	0045_optional_qr_identity	2026-04-13 22:48:00.012602+00
95	backend	0046_remove_evaluationsubmission_submission_url	2026-04-13 22:48:01.084815+00
96	backend	0047_remove_evaluation_commission	2026-04-13 22:48:02.823286+00
97	backend	0048_add_evaluation_status_and_gradeable_option	2026-04-13 22:48:04.467218+00
98	backend	0049_auto_20260329_0127	2026-04-13 22:48:05.97811+00
99	backend	0050_remove_evaluationsubmission_file	2026-04-13 22:48:07.055908+00
100	backend	0051_merge_20260404_0440	2026-04-13 22:48:07.905953+00
101	backend	0052_auto_20260404_1724	2026-04-13 22:48:08.777331+00
102	backend	0043_auto_20260409_2207	2026-04-13 22:48:10.349613+00
103	backend	0053_merge_20260413_2247	2026-04-13 22:48:11.637463+00
104	backend	0054_semesterschedule	2026-04-18 13:15:08.400804+00
105	backend	0055_academiccalendarevent	2026-04-18 13:15:09.996904+00
106	backend	0043_notification_channels_and_urgency	2026-04-25 17:11:47.11554+00
107	backend	0044_notification_image	2026-04-25 17:11:47.11554+00
108	backend	0054_merge_20260416_1917	2026-04-25 17:11:47.11554+00
109	backend	0056_merge_20260420_0000	2026-04-25 18:09:34.521567+00
110	backend	0057_notification_semester	2026-04-29 02:45:40.34173+00
111	backend	0058_calendar_reminders	2026-05-08 22:03:56.782042+00
112	backend	0058_create_forms	2026-05-09 17:42:27.88465+00
113	backend	0059_form_submission_status	2026-05-09 17:42:42.933979+00
114	backend	0060_form_teacher_validation	2026-05-09 17:42:46.110083+00
115	backend	0061_seed_catalogs	2026-05-09 17:43:26.147488+00
116	backend	0062_seed_document_forms	2026-05-09 17:43:43.146694+00
117	backend	0063_seed_digital_forms	2026-05-09 17:44:02.807636+00
118	backend	0064_user_github_url	2026-05-09 17:44:04.651848+00
119	backend	0058_news	2026-05-09 18:33:19.605645+00
120	backend	0059_dept_admins	2026-05-09 21:21:24.06921+00
121	backend	0059_merge_20260509_2029	2026-05-10 23:08:37.405149+00
122	backend	0059_dept_admins	2026-05-13 00:05:02.295828+00
123	backend	0061_create_forms	2026-05-13 02:15:15.371475+00
124	backend	0062_form_submission_status	2026-05-13 02:15:15.846489+00
125	backend	0063_form_teacher_validation	2026-05-13 02:15:16.311809+00
126	backend	0064_seed_catalogs	2026-05-13 02:15:16.777729+00
127	backend	0065_seed_document_forms	2026-05-13 02:15:17.242023+00
128	backend	0066_seed_digital_forms	2026-05-13 02:15:17.707684+00
129	backend	0059_user_github_url	2026-05-13 02:15:18.173635+00
130	backend	0060_merge_20260509_2029	2026-05-13 02:15:18.639728+00
131	backend	0067_merge_20260510_2038	2026-05-13 02:15:19.106428+00
132	backend	0068_merge_20260513_0003	2026-05-13 02:15:45.378713+00
133	backend	0069_user_linkedin_url	2026-05-13 02:15:46.787136+00
134	backend	0070_remove_teacher_profile	2026-05-13 02:15:48.181843+00
135	backend	0068_evaluationsubmission_submission_file	2026-05-15 22:56:42.709074+00
136	backend	0069_evaluationsubmission_feedback_text	2026-05-15 22:56:43.887903+00
137	backend	0070_evaluation_description	2026-05-15 22:56:45.045569+00
138	backend	0071_evaluationsubmission_original_filename	2026-05-15 22:56:46.191596+00
139	backend	0058_auto_20260508_2255	2026-05-15 22:56:48.559361+00
140	backend	0059_attendance_qr_mode_qr_location	2026-05-15 22:56:49.984717+00
141	backend	0072_merge_20260515_2035	2026-05-15 22:56:50.884152+00
142	backend	0073_staff_is_bedelia	2026-05-17 21:14:26.648493+00
143	backend	0073_staff_is_bedelia	2026-05-17 21:22:24.693593+00
144	backend	0071_merge_20260513_2206	2026-05-21 19:59:53.319857+00
145	backend	0074_merge_20260518_0153	2026-05-21 19:59:54.550102+00
146	backend	0075_auto_20260520_0602	2026-05-21 19:59:56.393479+00
148	backend	0076_final_commissions	2026-05-25 14:57:45.511586+00
149	backend	0077_career_student_career	2026-06-01 22:18:43.985371+00
150	authtoken	0004_alter_tokenproxy_options	2026-06-03 01:02:04.528368+00
151	backend	0076_secretary_and_staff_link	2026-06-03 01:02:07.019637+00
152	backend	0077_form_ownership_group	2026-06-03 01:02:09.460745+00
153	backend	0078_migrate_procedure_types_to_groups	2026-06-03 01:02:18.215095+00
154	backend	0079_remove_form_procedure	2026-06-03 01:02:21.127271+00
155	backend	0080_delete_seeded_forms_and_legacy_groups	2026-06-03 01:02:24.437003+00
156	backend	0081_form_submission_recipient_fields	2026-06-03 01:02:25.57291+00
157	backend	0082_merge_20260527_0224	2026-06-03 01:02:26.00824+00
158	backend	0083_alter_formdocumentsource_form_document_source	2026-06-03 01:02:27.102274+00
159	backend	0077_contact	2026-06-03 01:02:29.331983+00
160	backend	0078_notification_action_url	2026-06-03 01:02:30.04838+00
161	backend	0079_study_group	2026-06-03 01:02:32.965328+00
162	backend	0076_auto_20260525_2310	2026-06-03 01:10:57.493876+00
163	backend	0077_merge_0076_auto_20260525_2310_0076_final_commissions	2026-06-03 01:10:57.957322+00
164	backend	0080_merge_20260529_2005	2026-06-03 01:10:58.603209+00
165	backend	0081_alter_contact_id_alter_groupmembership_id_and_more	2026-06-03 01:11:02.599672+00
166	backend	0078_merge_20260602_1454	2026-06-03 01:11:03.032233+00
167	backend	0079_alter_career_id_alter_studentcareer_id	2026-06-03 01:11:06.318042+00
168	backend	0077_user_profile_photo	2026-06-03 01:11:07.199908+00
169	backend	0078_merge_20260602_2105	2026-06-03 01:11:07.630175+00
147	backend	0077_catedra_calendar	2026-05-21 19:59:58.235089+00
170	backend	0084_merge_20260603_0101	2026-06-03 01:14:21.766994+00
171	backend	0085_notification_department	2026-06-07 20:35:54.881769+00
172	backend	0086_news_department	2026-06-07 20:47:33.113856+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
l1h9aibvs9i64c8glnwfdwaj8f85d6t1	.eJxVjMsOwiAQRf-FtSEOpTxcuvcbCDMDUjWQlHZl_HdD0oVu7znnvkWI-1bC3tMaFhYX4b04_Y4Y6ZnqIPyI9d4ktbqtC8qhyIN2eWucXtfD_TsosZdRk4KckHnyk-OkLSpSiATAPpuIGZ1yGdiits7MxPpsaNaQaIoeNIjPF0grOPs:1wBbj4:UDkFwtIspbaEyytxqlbJ-vLVaR2cZOhxB45fYmYSEtA	2026-04-25 17:02:30.84487+00
eo3rhlcxmy0ujiqd9onbfb16syt9ios2	.eJxVjEEOwiAQRe_C2hBaYCgu3XsGMsxMpWpoUtqV8e7apAvd_vfef6mE21rS1mRJE6uzilGdfseM9JC6E75jvc2a5rouU9a7og_a9HVmeV4O9--gYCvfmlh6HwwZAOp8NI4pYw7sO3CjHZB7S2RskEg5sidDADgwujHYACLq_QEhGzjP:1wLTNx:fav2fWxdgIdKSSwf7HIpS43AjHz2njE5tp6bCSCV-EQ	2026-05-22 22:09:29.065465+00
\.


--
-- Data for Name: push_notifications_apnsdevice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.push_notifications_apnsdevice (id, name, active, date_created, device_id, registration_id, user_id, application_id) FROM stdin;
\.


--
-- Data for Name: push_notifications_gcmdevice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.push_notifications_gcmdevice (id, name, active, date_created, device_id, registration_id, user_id, cloud_message_type, application_id) FROM stdin;
\.


--
-- Data for Name: push_notifications_webpushdevice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.push_notifications_webpushdevice (id, name, active, date_created, application_id, registration_id, p256dh, auth, browser, user_id) FROM stdin;
\.


--
-- Data for Name: push_notifications_wnsdevice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.push_notifications_wnsdevice (id, name, active, date_created, device_id, registration_id, user_id, application_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 244, true);


--
-- Name: backend_academiccalendarevent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_academiccalendarevent_id_seq', 75, true);


--
-- Name: backend_attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_attendance_id_seq', 25, true);


--
-- Name: backend_attendanceqrcode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_attendanceqrcode_id_seq', 19, true);


--
-- Name: backend_auditlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_auditlog_id_seq', 11, true);


--
-- Name: backend_authidentity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_authidentity_id_seq', 20, true);


--
-- Name: backend_calendareventreminder_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_calendareventreminder_id_seq', 1, true);


--
-- Name: backend_career_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_career_id_seq', 2, true);


--
-- Name: backend_catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_catalog_id_seq', 3, true);


--
-- Name: backend_catalogitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_catalogitem_id_seq', 31, true);


--
-- Name: backend_catedracalendarentry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_catedracalendarentry_id_seq', 8, true);


--
-- Name: backend_commission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_commission_id_seq', 11, true);


--
-- Name: backend_commissioninscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_commissioninscription_id_seq', 31, true);


--
-- Name: backend_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_contact_id_seq', 1, true);


--
-- Name: backend_department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_department_id_seq', 20, true);


--
-- Name: backend_evaluation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_evaluation_id_seq', 19, true);


--
-- Name: backend_evaluationsubmission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_evaluationsubmission_id_seq', 16, true);


--
-- Name: backend_final_commissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_final_commissions_id_seq', 10, true);


--
-- Name: backend_final_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_final_id_seq', 25, true);


--
-- Name: backend_finalexam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_finalexam_id_seq', 36, true);


--
-- Name: backend_form_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_form_id_seq', 15, true);


--
-- Name: backend_formanswer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formanswer_id_seq', 1, false);


--
-- Name: backend_formfield_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formfield_id_seq', 36, true);


--
-- Name: backend_formfieldoption_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formfieldoption_id_seq', 1, false);


--
-- Name: backend_formfieldtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formfieldtype_id_seq', 8, true);


--
-- Name: backend_formownershipgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formownershipgroup_id_seq', 4, true);


--
-- Name: backend_formownershipmember_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formownershipmember_id_seq', 1, false);


--
-- Name: backend_formsubmission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formsubmission_id_seq', 1, false);


--
-- Name: backend_formsubmissionstatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formsubmissionstatus_id_seq', 4, true);


--
-- Name: backend_formtype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_formtype_id_seq', 2, true);


--
-- Name: backend_groupmembership_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_groupmembership_id_seq', 1, false);


--
-- Name: backend_news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_news_id_seq', 2, true);


--
-- Name: backend_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_notification_id_seq', 10, true);


--
-- Name: backend_passwordresetotp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_passwordresetotp_id_seq', 4, true);


--
-- Name: backend_secretary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_secretary_id_seq', 1, false);


--
-- Name: backend_semester_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_semester_id_seq', 18, true);


--
-- Name: backend_semesterschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_semesterschedule_id_seq', 10, true);


--
-- Name: backend_studentcareer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_studentcareer_id_seq', 3, true);


--
-- Name: backend_studygroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_studygroup_id_seq', 1, false);


--
-- Name: backend_teacherrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_teacherrole_id_seq', 5, true);


--
-- Name: backend_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_user_groups_id_seq', 1, false);


--
-- Name: backend_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_user_id_seq', 128, true);


--
-- Name: backend_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_user_user_permissions_id_seq', 1, false);


--
-- Name: backend_usernotification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.backend_usernotification_id_seq', 87, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 16, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 61, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 172, true);


--
-- Name: push_notifications_apnsdevice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.push_notifications_apnsdevice_id_seq', 1, false);


--
-- Name: push_notifications_gcmdevice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.push_notifications_gcmdevice_id_seq', 1, false);


--
-- Name: push_notifications_webpushdevice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.push_notifications_webpushdevice_id_seq', 1, false);


--
-- Name: push_notifications_wnsdevice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.push_notifications_wnsdevice_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: authtoken_token authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: backend_academiccalendarevent backend_academiccalendarevent_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_academiccalendarevent
    ADD CONSTRAINT backend_academiccalendarevent_pkey PRIMARY KEY (id);


--
-- Name: backend_attendance backend_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendance
    ADD CONSTRAINT backend_attendance_pkey PRIMARY KEY (id);


--
-- Name: backend_attendanceqrcode backend_attendanceqrcode_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendanceqrcode
    ADD CONSTRAINT backend_attendanceqrcode_pkey PRIMARY KEY (id);


--
-- Name: backend_auditlog backend_auditlog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_auditlog
    ADD CONSTRAINT backend_auditlog_pkey PRIMARY KEY (id);


--
-- Name: backend_authidentity backend_authidentity_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity
    ADD CONSTRAINT backend_authidentity_email_key UNIQUE (email);


--
-- Name: backend_authidentity backend_authidentity_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity
    ADD CONSTRAINT backend_authidentity_pkey PRIMARY KEY (id);


--
-- Name: backend_authidentity backend_authidentity_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity
    ADD CONSTRAINT backend_authidentity_user_id_key UNIQUE (user_id);


--
-- Name: backend_calendareventreminder backend_calendareventrem_event_id_days_before_48ed667b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_calendareventreminder
    ADD CONSTRAINT backend_calendareventrem_event_id_days_before_48ed667b_uniq UNIQUE (event_id, days_before);


--
-- Name: backend_calendareventreminder backend_calendareventreminder_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_calendareventreminder
    ADD CONSTRAINT backend_calendareventreminder_pkey PRIMARY KEY (id);


--
-- Name: backend_career backend_career_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_career
    ADD CONSTRAINT backend_career_pkey PRIMARY KEY (id);


--
-- Name: backend_career backend_career_siu_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_career
    ADD CONSTRAINT backend_career_siu_id_key UNIQUE (siu_id);


--
-- Name: backend_catalog backend_catalog_catalog_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalog
    ADD CONSTRAINT backend_catalog_catalog_key_key UNIQUE (catalog_key);


--
-- Name: backend_catalog backend_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalog
    ADD CONSTRAINT backend_catalog_pkey PRIMARY KEY (id);


--
-- Name: backend_catalogitem backend_catalogitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalogitem
    ADD CONSTRAINT backend_catalogitem_pkey PRIMARY KEY (id);


--
-- Name: backend_catedracalendarentry backend_catedracalendarentry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catedracalendarentry
    ADD CONSTRAINT backend_catedracalendarentry_pkey PRIMARY KEY (id);


--
-- Name: backend_commission backend_commission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commission
    ADD CONSTRAINT backend_commission_pkey PRIMARY KEY (id);


--
-- Name: backend_commissioninscription backend_commissioninscription_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commissioninscription
    ADD CONSTRAINT backend_commissioninscription_pkey PRIMARY KEY (id);


--
-- Name: backend_contact backend_contact_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_contact
    ADD CONSTRAINT backend_contact_pkey PRIMARY KEY (id);


--
-- Name: backend_department backend_department_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_department
    ADD CONSTRAINT backend_department_pkey PRIMARY KEY (id);


--
-- Name: backend_evaluation backend_evaluation_parent_evaluation_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluation
    ADD CONSTRAINT backend_evaluation_parent_evaluation_id_key UNIQUE (parent_evaluation_id);


--
-- Name: backend_evaluation backend_evaluation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluation
    ADD CONSTRAINT backend_evaluation_pkey PRIMARY KEY (id);


--
-- Name: backend_evaluationsubmission backend_evaluationsubmission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission
    ADD CONSTRAINT backend_evaluationsubmission_pkey PRIMARY KEY (id);


--
-- Name: backend_final_commissions backend_final_commissions_final_id_commission_id_0561cdd2_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final_commissions
    ADD CONSTRAINT backend_final_commissions_final_id_commission_id_0561cdd2_uniq UNIQUE (final_id, commission_id);


--
-- Name: backend_final_commissions backend_final_commissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final_commissions
    ADD CONSTRAINT backend_final_commissions_pkey PRIMARY KEY (id);


--
-- Name: backend_final backend_final_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final
    ADD CONSTRAINT backend_final_pkey PRIMARY KEY (id);


--
-- Name: backend_finalexam backend_finalexam_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_finalexam
    ADD CONSTRAINT backend_finalexam_pkey PRIMARY KEY (id);


--
-- Name: backend_form backend_form_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_form
    ADD CONSTRAINT backend_form_pkey PRIMARY KEY (id);


--
-- Name: backend_formanswer backend_formanswer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formanswer
    ADD CONSTRAINT backend_formanswer_pkey PRIMARY KEY (id);


--
-- Name: backend_formdocumentsource backend_formdocumentsource_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formdocumentsource
    ADD CONSTRAINT backend_formdocumentsource_pkey PRIMARY KEY (form_id);


--
-- Name: backend_formfield backend_formfield_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfield
    ADD CONSTRAINT backend_formfield_pkey PRIMARY KEY (id);


--
-- Name: backend_formfieldoption backend_formfieldoption_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfieldoption
    ADD CONSTRAINT backend_formfieldoption_pkey PRIMARY KEY (id);


--
-- Name: backend_formfieldtype backend_formfieldtype_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfieldtype
    ADD CONSTRAINT backend_formfieldtype_pkey PRIMARY KEY (id);


--
-- Name: backend_formownershipgroup backend_formownershipgroup_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formownershipgroup
    ADD CONSTRAINT backend_formownershipgroup_name_key UNIQUE (name);


--
-- Name: backend_formownershipgroup backend_formownershipgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formownershipgroup
    ADD CONSTRAINT backend_formownershipgroup_pkey PRIMARY KEY (id);


--
-- Name: backend_formownershipmember backend_formownershipmember_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formownershipmember
    ADD CONSTRAINT backend_formownershipmember_pkey PRIMARY KEY (id);


--
-- Name: backend_formsubmission backend_formsubmission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission
    ADD CONSTRAINT backend_formsubmission_pkey PRIMARY KEY (id);


--
-- Name: backend_formsubmissionstatus backend_formsubmissionstatus_form_submission_status_value_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmissionstatus
    ADD CONSTRAINT backend_formsubmissionstatus_form_submission_status_value_key UNIQUE (form_submission_status_value);


--
-- Name: backend_formsubmissionstatus backend_formsubmissionstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmissionstatus
    ADD CONSTRAINT backend_formsubmissionstatus_pkey PRIMARY KEY (id);


--
-- Name: backend_formtype backend_formtype_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formtype
    ADD CONSTRAINT backend_formtype_pkey PRIMARY KEY (id);


--
-- Name: backend_groupmembership backend_groupmembership_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_groupmembership
    ADD CONSTRAINT backend_groupmembership_pkey PRIMARY KEY (id);


--
-- Name: backend_news backend_news_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_news
    ADD CONSTRAINT backend_news_pkey PRIMARY KEY (id);


--
-- Name: backend_notification backend_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_notification
    ADD CONSTRAINT backend_notification_pkey PRIMARY KEY (id);


--
-- Name: backend_passwordresetotp backend_passwordresetotp_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_passwordresetotp
    ADD CONSTRAINT backend_passwordresetotp_pkey PRIMARY KEY (id);


--
-- Name: backend_secretary backend_secretary_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_secretary
    ADD CONSTRAINT backend_secretary_pkey PRIMARY KEY (id);


--
-- Name: backend_semester backend_semester_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semester
    ADD CONSTRAINT backend_semester_pkey PRIMARY KEY (id);


--
-- Name: backend_semesterschedule backend_semesterschedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semesterschedule
    ADD CONSTRAINT backend_semesterschedule_pkey PRIMARY KEY (id);


--
-- Name: backend_staff backend_staff_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_staff
    ADD CONSTRAINT backend_staff_pkey PRIMARY KEY (user_id);


--
-- Name: backend_student backend_student_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_student
    ADD CONSTRAINT backend_student_pkey PRIMARY KEY (user_id);


--
-- Name: backend_studentcareer backend_studentcareer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studentcareer
    ADD CONSTRAINT backend_studentcareer_pkey PRIMARY KEY (id);


--
-- Name: backend_studentcareer backend_studentcareer_student_id_career_id_da730e56_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studentcareer
    ADD CONSTRAINT backend_studentcareer_student_id_career_id_da730e56_uniq UNIQUE (student_id, career_id);


--
-- Name: backend_studygroup backend_studygroup_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studygroup
    ADD CONSTRAINT backend_studygroup_pkey PRIMARY KEY (id);


--
-- Name: backend_teacher backend_teacher_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacher
    ADD CONSTRAINT backend_teacher_pkey PRIMARY KEY (user_id);


--
-- Name: backend_teacherrole backend_teacherrole_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacherrole
    ADD CONSTRAINT backend_teacherrole_pkey PRIMARY KEY (id);


--
-- Name: backend_user backend_user_dni_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user
    ADD CONSTRAINT backend_user_dni_key UNIQUE (dni);


--
-- Name: backend_user_groups backend_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_groups
    ADD CONSTRAINT backend_user_groups_pkey PRIMARY KEY (id);


--
-- Name: backend_user_groups backend_user_groups_user_id_group_id_decc787e_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_groups
    ADD CONSTRAINT backend_user_groups_user_id_group_id_decc787e_uniq UNIQUE (user_id, group_id);


--
-- Name: backend_user backend_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user
    ADD CONSTRAINT backend_user_pkey PRIMARY KEY (id);


--
-- Name: backend_user_user_permissions backend_user_user_permis_user_id_permission_id_d232313e_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_user_permissions
    ADD CONSTRAINT backend_user_user_permis_user_id_permission_id_d232313e_uniq UNIQUE (user_id, permission_id);


--
-- Name: backend_user_user_permissions backend_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_user_permissions
    ADD CONSTRAINT backend_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: backend_usernotification backend_usernotification_notification_id_user_id_e067d819_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_usernotification
    ADD CONSTRAINT backend_usernotification_notification_id_user_id_e067d819_uniq UNIQUE (notification_id, user_id);


--
-- Name: backend_usernotification backend_usernotification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_usernotification
    ADD CONSTRAINT backend_usernotification_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: backend_finalexam one_final_exam_per_student; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_finalexam
    ADD CONSTRAINT one_final_exam_per_student UNIQUE (final_id, student_id);


--
-- Name: backend_evaluationsubmission one_submission_per_student; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission
    ADD CONSTRAINT one_submission_per_student UNIQUE (evaluation_id, student_id);


--
-- Name: push_notifications_apnsdevice push_notifications_apnsdevice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_apnsdevice
    ADD CONSTRAINT push_notifications_apnsdevice_pkey PRIMARY KEY (id);


--
-- Name: push_notifications_gcmdevice push_notifications_gcmdevice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_gcmdevice
    ADD CONSTRAINT push_notifications_gcmdevice_pkey PRIMARY KEY (id);


--
-- Name: push_notifications_webpushdevice push_notifications_webpushdevice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_webpushdevice
    ADD CONSTRAINT push_notifications_webpushdevice_pkey PRIMARY KEY (id);


--
-- Name: push_notifications_wnsdevice push_notifications_wnsdevice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_wnsdevice
    ADD CONSTRAINT push_notifications_wnsdevice_pkey PRIMARY KEY (id);


--
-- Name: backend_contact unique_contact_pair; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_contact
    ADD CONSTRAINT unique_contact_pair UNIQUE (from_student_id, to_student_id);


--
-- Name: backend_formownershipmember unique_group_entity; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formownershipmember
    ADD CONSTRAINT unique_group_entity UNIQUE (group_id, entity_type, entity_id);


--
-- Name: backend_groupmembership unique_group_member; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_groupmembership
    ADD CONSTRAINT unique_group_member UNIQUE (group_id, student_id);


--
-- Name: backend_authidentity unique_identity_per_provider; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity
    ADD CONSTRAINT unique_identity_per_provider UNIQUE (provider, provider_user_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: authtoken_token_key_10f0b77e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX authtoken_token_key_10f0b77e_like ON public.authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: backend_attendance_qr_code_id_9a26eaf6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_attendance_qr_code_id_9a26eaf6 ON public.backend_attendance USING btree (qr_code_id);


--
-- Name: backend_attendance_semester_id_031b3295; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_attendance_semester_id_031b3295 ON public.backend_attendance USING btree (semester_id);


--
-- Name: backend_attendance_student_id_34eb9127; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_attendance_student_id_34eb9127 ON public.backend_attendance USING btree (student_id);


--
-- Name: backend_attendanceqrcode_owner_teacher_id_c3ebf874; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_attendanceqrcode_owner_teacher_id_c3ebf874 ON public.backend_attendanceqrcode USING btree (owner_teacher_id);


--
-- Name: backend_attendanceqrcode_semester_id_f6ac338d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_attendanceqrcode_semester_id_f6ac338d ON public.backend_attendanceqrcode USING btree (semester_id);


--
-- Name: backend_auditlog_related_user_id_dec5a622; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_auditlog_related_user_id_dec5a622 ON public.backend_auditlog USING btree (related_user_id);


--
-- Name: backend_auditlog_user_id_33ba79a9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_auditlog_user_id_33ba79a9 ON public.backend_auditlog USING btree (user_id);


--
-- Name: backend_authidentity_email_2e6b6f3a_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_authidentity_email_2e6b6f3a_like ON public.backend_authidentity USING btree (email varchar_pattern_ops);


--
-- Name: backend_calendareventreminder_event_id_cd50d87c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_calendareventreminder_event_id_cd50d87c ON public.backend_calendareventreminder USING btree (event_id);


--
-- Name: backend_calendareventreminder_notification_id_81c58c35; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_calendareventreminder_notification_id_81c58c35 ON public.backend_calendareventreminder USING btree (notification_id);


--
-- Name: backend_catalog_catalog_key_8d45ae8d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_catalog_catalog_key_8d45ae8d_like ON public.backend_catalog USING btree (catalog_key varchar_pattern_ops);


--
-- Name: backend_catalogitem_catalog_id_a56832b4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_catalogitem_catalog_id_a56832b4 ON public.backend_catalogitem USING btree (catalog_id);


--
-- Name: backend_catedracalendarentry_semester_id_866e884c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_catedracalendarentry_semester_id_866e884c ON public.backend_catedracalendarentry USING btree (semester_id);


--
-- Name: backend_commission_chief_teacher_id_378370af; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_chief_teacher_id_378370af ON public.backend_commission USING btree (chief_teacher_id);


--
-- Name: backend_commission_department_id_65809027; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_department_id_65809027 ON public.backend_commission USING btree (department_id);


--
-- Name: backend_commission_department_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_department_id_idx ON public.backend_commission USING btree (department_id);


--
-- Name: backend_commission_siu_id_9dc8232a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_siu_id_9dc8232a ON public.backend_commission USING btree (siu_id);


--
-- Name: backend_commission_subject_name_638c903c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_subject_name_638c903c ON public.backend_commission USING btree (subject_name);


--
-- Name: backend_commission_subject_name_638c903c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_subject_name_638c903c_like ON public.backend_commission USING btree (subject_name varchar_pattern_ops);


--
-- Name: backend_commission_subject_siu_id_dc6366ad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commission_subject_siu_id_dc6366ad ON public.backend_commission USING btree (subject_siu_id);


--
-- Name: backend_commissioninscription_semester_id_41961132; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commissioninscription_semester_id_41961132 ON public.backend_commissioninscription USING btree (semester_id);


--
-- Name: backend_commissioninscription_student_id_3d5072aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_commissioninscription_student_id_3d5072aa ON public.backend_commissioninscription USING btree (student_id);


--
-- Name: backend_contact_from_student_id_9e3f9640; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_contact_from_student_id_9e3f9640 ON public.backend_contact USING btree (from_student_id);


--
-- Name: backend_contact_to_student_id_a4127cff; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_contact_to_student_id_a4127cff ON public.backend_contact USING btree (to_student_id);


--
-- Name: backend_evaluation_end_date_97a5dd2a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_end_date_97a5dd2a ON public.backend_evaluation USING btree (end_date);


--
-- Name: backend_evaluation_evaluation_name_0262908f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_evaluation_name_0262908f ON public.backend_evaluation USING btree (evaluation_name);


--
-- Name: backend_evaluation_evaluation_name_0262908f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_evaluation_name_0262908f_like ON public.backend_evaluation USING btree (evaluation_name varchar_pattern_ops);


--
-- Name: backend_evaluation_passing_grade_6e8865c8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_passing_grade_6e8865c8 ON public.backend_evaluation USING btree (passing_grade);


--
-- Name: backend_evaluation_semester_id_11ee5907; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_semester_id_11ee5907 ON public.backend_evaluation USING btree (semester_id);


--
-- Name: backend_evaluation_start_date_ac6ea0e7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluation_start_date_ac6ea0e7 ON public.backend_evaluation USING btree (start_date);


--
-- Name: backend_evaluationsubmission_evaluation_id_168042de; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_evaluation_id_168042de ON public.backend_evaluationsubmission USING btree (evaluation_id);


--
-- Name: backend_evaluationsubmission_grade_27c0ae68; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_grade_27c0ae68 ON public.backend_evaluationsubmission USING btree (grade);


--
-- Name: backend_evaluationsubmission_grader_id_98422e73; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_grader_id_98422e73 ON public.backend_evaluationsubmission USING btree (grader_id);


--
-- Name: backend_evaluationsubmission_status_96860e3c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_status_96860e3c ON public.backend_evaluationsubmission USING btree (submission_status);


--
-- Name: backend_evaluationsubmission_status_96860e3c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_status_96860e3c_like ON public.backend_evaluationsubmission USING btree (submission_status varchar_pattern_ops);


--
-- Name: backend_evaluationsubmission_student_id_3739c43f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_evaluationsubmission_student_id_3739c43f ON public.backend_evaluationsubmission USING btree (student_id);


--
-- Name: backend_final_act_e9d9ff79; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_act_e9d9ff79 ON public.backend_final USING btree (act);


--
-- Name: backend_final_act_e9d9ff79_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_act_e9d9ff79_like ON public.backend_final USING btree (act varchar_pattern_ops);


--
-- Name: backend_final_commissions_commission_id_3b447ca3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_commissions_commission_id_3b447ca3 ON public.backend_final_commissions USING btree (commission_id);


--
-- Name: backend_final_commissions_final_id_03525291; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_commissions_final_id_03525291 ON public.backend_final_commissions USING btree (final_id);


--
-- Name: backend_final_date_50f66863; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_date_50f66863 ON public.backend_final USING btree (date);


--
-- Name: backend_final_siu_id_e5cede7a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_siu_id_e5cede7a ON public.backend_final USING btree (siu_id);


--
-- Name: backend_final_subject_name_2999abfc; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_subject_name_2999abfc ON public.backend_final USING btree (subject_name);


--
-- Name: backend_final_subject_name_2999abfc_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_subject_name_2999abfc_like ON public.backend_final USING btree (subject_name varchar_pattern_ops);


--
-- Name: backend_final_subject_siu_id_904246bd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_subject_siu_id_904246bd ON public.backend_final USING btree (subject_siu_id);


--
-- Name: backend_final_teacher_id_0c1dfc21; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_final_teacher_id_0c1dfc21 ON public.backend_final USING btree (teacher_id);


--
-- Name: backend_finalexam_final_id_471da19e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_finalexam_final_id_471da19e ON public.backend_finalexam USING btree (final_id);


--
-- Name: backend_finalexam_grade_53479cad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_finalexam_grade_53479cad ON public.backend_finalexam USING btree (grade);


--
-- Name: backend_finalexam_student_id_28f9e2fa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_finalexam_student_id_28f9e2fa ON public.backend_finalexam USING btree (student_id);


--
-- Name: backend_form_form_type_id_b9c1bc04; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_form_form_type_id_b9c1bc04 ON public.backend_form USING btree (form_type_id);


--
-- Name: backend_form_ownership_group_id_a1e9120d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_form_ownership_group_id_a1e9120d ON public.backend_form USING btree (ownership_group_id);


--
-- Name: backend_formanswer_field_id_e683e058; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formanswer_field_id_e683e058 ON public.backend_formanswer USING btree (field_id);


--
-- Name: backend_formanswer_submission_id_338e8a3f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formanswer_submission_id_338e8a3f ON public.backend_formanswer USING btree (submission_id);


--
-- Name: backend_formfield_catalog_id_e6d73868; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formfield_catalog_id_e6d73868 ON public.backend_formfield USING btree (catalog_id);


--
-- Name: backend_formfield_form_field_type_id_f3014536; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formfield_form_field_type_id_f3014536 ON public.backend_formfield USING btree (form_field_type_id);


--
-- Name: backend_formfield_form_id_0905f28c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formfield_form_id_0905f28c ON public.backend_formfield USING btree (form_id);


--
-- Name: backend_formfieldoption_form_field_id_ed0da86c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formfieldoption_form_field_id_ed0da86c ON public.backend_formfieldoption USING btree (form_field_id);


--
-- Name: backend_formownershipgroup_name_a5e3e3fa_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formownershipgroup_name_a5e3e3fa_like ON public.backend_formownershipgroup USING btree (name varchar_pattern_ops);


--
-- Name: backend_formownershipmember_group_id_10e46567; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formownershipmember_group_id_10e46567 ON public.backend_formownershipmember USING btree (group_id);


--
-- Name: backend_formsubmission_form_id_3a6ae321; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formsubmission_form_id_3a6ae321 ON public.backend_formsubmission USING btree (form_id);


--
-- Name: backend_formsubmission_status_id_d3289b17; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formsubmission_status_id_d3289b17 ON public.backend_formsubmission USING btree (status_id);


--
-- Name: backend_formsubmission_teacher_id_5ee8bc1a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formsubmission_teacher_id_5ee8bc1a ON public.backend_formsubmission USING btree (teacher_id);


--
-- Name: backend_formsubmission_user_id_82ddf966; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formsubmission_user_id_82ddf966 ON public.backend_formsubmission USING btree (user_id);


--
-- Name: backend_formsubmissionst_form_submission_status_v_743dd8d4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_formsubmissionst_form_submission_status_v_743dd8d4_like ON public.backend_formsubmissionstatus USING btree (form_submission_status_value varchar_pattern_ops);


--
-- Name: backend_groupmembership_group_id_06bf83b6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_groupmembership_group_id_06bf83b6 ON public.backend_groupmembership USING btree (group_id);


--
-- Name: backend_groupmembership_student_id_2965add9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_groupmembership_student_id_2965add9 ON public.backend_groupmembership USING btree (student_id);


--
-- Name: backend_news_author_id_9ec388f3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_news_author_id_9ec388f3 ON public.backend_news USING btree (author_id);


--
-- Name: backend_news_department_id_85481fe0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_news_department_id_85481fe0 ON public.backend_news USING btree (department_id);


--
-- Name: backend_notification_department_id_ab688b2d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_notification_department_id_ab688b2d ON public.backend_notification USING btree (department_id);


--
-- Name: backend_notification_semester_id_41a21a92; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_notification_semester_id_41a21a92 ON public.backend_notification USING btree (semester_id);


--
-- Name: backend_notification_sender_id_a0df67f9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_notification_sender_id_a0df67f9 ON public.backend_notification USING btree (sender_id);


--
-- Name: backend_pas_expires_796dde_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_pas_expires_796dde_idx ON public.backend_passwordresetotp USING btree (expires_at);


--
-- Name: backend_pas_user_id_bc2625_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_pas_user_id_bc2625_idx ON public.backend_passwordresetotp USING btree (user_id, created_at DESC);


--
-- Name: backend_passwordresetotp_user_id_22e93d12; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_passwordresetotp_user_id_22e93d12 ON public.backend_passwordresetotp USING btree (user_id);


--
-- Name: backend_secretary_parent_secretary_id_f92a644e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_secretary_parent_secretary_id_f92a644e ON public.backend_secretary USING btree (parent_secretary_id);


--
-- Name: backend_semester_classes_amount_453dbeae; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_semester_classes_amount_453dbeae ON public.backend_semester USING btree (classes_amount);


--
-- Name: backend_semester_commission_id_5a004687; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_semester_commission_id_5a004687 ON public.backend_semester USING btree (commission_id);


--
-- Name: backend_semester_minimum_attendance_797d2e22; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_semester_minimum_attendance_797d2e22 ON public.backend_semester USING btree (minimum_attendance);


--
-- Name: backend_semester_start_date_b639b231; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_semester_start_date_b639b231 ON public.backend_semester USING btree (start_date);


--
-- Name: backend_semesterschedule_semester_id_61b29be1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_semesterschedule_semester_id_61b29be1 ON public.backend_semesterschedule USING btree (semester_id);


--
-- Name: backend_staff_department_id_60ca9b21; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_staff_department_id_60ca9b21 ON public.backend_staff USING btree (department_id);


--
-- Name: backend_staff_department_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_staff_department_id_idx ON public.backend_staff USING btree (department_id);


--
-- Name: backend_staff_secretary_id_3f072af1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_staff_secretary_id_3f072af1 ON public.backend_staff USING btree (secretary_id);


--
-- Name: backend_staff_subject_siu_id_572cd909; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_staff_subject_siu_id_572cd909 ON public.backend_staff USING btree (department_siu_id);


--
-- Name: backend_studentcareer_career_id_c679668d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_studentcareer_career_id_c679668d ON public.backend_studentcareer USING btree (career_id);


--
-- Name: backend_studentcareer_student_id_f7a10696; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_studentcareer_student_id_f7a10696 ON public.backend_studentcareer USING btree (student_id);


--
-- Name: backend_studygroup_creator_id_3dc2f63b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_studygroup_creator_id_3dc2f63b ON public.backend_studygroup USING btree (creator_id);


--
-- Name: backend_teacher_siu_id_602bda4a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_teacher_siu_id_602bda4a ON public.backend_teacher USING btree (siu_id);


--
-- Name: backend_teacherrole_commission_id_0490481c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_teacherrole_commission_id_0490481c ON public.backend_teacherrole USING btree (commission_id);


--
-- Name: backend_teacherrole_teacher_id_294c6901; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_teacherrole_teacher_id_294c6901 ON public.backend_teacherrole USING btree (teacher_id);


--
-- Name: backend_user_dni_b0bf877f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_user_dni_b0bf877f_like ON public.backend_user USING btree (dni varchar_pattern_ops);


--
-- Name: backend_user_groups_group_id_df691386; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_user_groups_group_id_df691386 ON public.backend_user_groups USING btree (group_id);


--
-- Name: backend_user_groups_user_id_d2c44525; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_user_groups_user_id_d2c44525 ON public.backend_user_groups USING btree (user_id);


--
-- Name: backend_user_user_permissions_permission_id_634ab7e4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_user_user_permissions_permission_id_634ab7e4 ON public.backend_user_user_permissions USING btree (permission_id);


--
-- Name: backend_user_user_permissions_user_id_439140a5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_user_user_permissions_user_id_439140a5 ON public.backend_user_user_permissions USING btree (user_id);


--
-- Name: backend_usernotification_notification_id_094ec51f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_usernotification_notification_id_094ec51f ON public.backend_usernotification USING btree (notification_id);


--
-- Name: backend_usernotification_user_id_84ed3bd7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX backend_usernotification_user_id_84ed3bd7 ON public.backend_usernotification USING btree (user_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: push_notifications_apnsdevice_device_id_0ac3cde3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_apnsdevice_device_id_0ac3cde3 ON public.push_notifications_apnsdevice USING btree (device_id);


--
-- Name: push_notifications_apnsdevice_registration_id_5502bc8c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_apnsdevice_registration_id_5502bc8c ON public.push_notifications_apnsdevice USING btree (registration_id);


--
-- Name: push_notifications_apnsdevice_registration_id_5502bc8c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_apnsdevice_registration_id_5502bc8c_like ON public.push_notifications_apnsdevice USING btree (registration_id varchar_pattern_ops);


--
-- Name: push_notifications_apnsdevice_user_id_44cc44d2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_apnsdevice_user_id_44cc44d2 ON public.push_notifications_apnsdevice USING btree (user_id);


--
-- Name: push_notifications_gcmdevice_device_id_0b22a9c4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_gcmdevice_device_id_0b22a9c4 ON public.push_notifications_gcmdevice USING btree (device_id);


--
-- Name: push_notifications_gcmdevice_user_id_f3752f1b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_gcmdevice_user_id_f3752f1b ON public.push_notifications_gcmdevice USING btree (user_id);


--
-- Name: push_notifications_webpushdevice_user_id_e867e0a1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_webpushdevice_user_id_e867e0a1 ON public.push_notifications_webpushdevice USING btree (user_id);


--
-- Name: push_notifications_wnsdevice_device_id_7e1c24c4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_wnsdevice_device_id_7e1c24c4 ON public.push_notifications_wnsdevice USING btree (device_id);


--
-- Name: push_notifications_wnsdevice_user_id_670eff0d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX push_notifications_wnsdevice_user_id_670eff0d ON public.push_notifications_wnsdevice USING btree (user_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token authtoken_token_user_id_35299eff_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_attendance backend_attendance_qr_code_id_9a26eaf6_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendance
    ADD CONSTRAINT backend_attendance_qr_code_id_9a26eaf6_fk FOREIGN KEY (qr_code_id) REFERENCES public.backend_attendanceqrcode(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_attendance backend_attendance_semester_id_031b3295_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendance
    ADD CONSTRAINT backend_attendance_semester_id_031b3295_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_attendance backend_attendance_student_id_34eb9127_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendance
    ADD CONSTRAINT backend_attendance_student_id_34eb9127_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_attendanceqrcode backend_attendanceqrcode_owner_teacher_id_c3ebf874_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendanceqrcode
    ADD CONSTRAINT backend_attendanceqrcode_owner_teacher_id_c3ebf874_fk FOREIGN KEY (owner_teacher_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_attendanceqrcode backend_attendanceqrcode_semester_id_f6ac338d_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_attendanceqrcode
    ADD CONSTRAINT backend_attendanceqrcode_semester_id_f6ac338d_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_auditlog backend_auditlog_related_user_id_dec5a622_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_auditlog
    ADD CONSTRAINT backend_auditlog_related_user_id_dec5a622_fk FOREIGN KEY (related_user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_auditlog backend_auditlog_user_id_33ba79a9_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_auditlog
    ADD CONSTRAINT backend_auditlog_user_id_33ba79a9_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_authidentity backend_authidentity_user_id_13c74f15_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_authidentity
    ADD CONSTRAINT backend_authidentity_user_id_13c74f15_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_calendareventreminder backend_calendareventreminder_event_id_cd50d87c_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_calendareventreminder
    ADD CONSTRAINT backend_calendareventreminder_event_id_cd50d87c_fk FOREIGN KEY (event_id) REFERENCES public.backend_academiccalendarevent(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_calendareventreminder backend_calendareventreminder_notification_id_81c58c35_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_calendareventreminder
    ADD CONSTRAINT backend_calendareventreminder_notification_id_81c58c35_fk FOREIGN KEY (notification_id) REFERENCES public.backend_notification(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_catalogitem backend_catalogitem_catalog_id_a56832b4_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catalogitem
    ADD CONSTRAINT backend_catalogitem_catalog_id_a56832b4_fk FOREIGN KEY (catalog_id) REFERENCES public.backend_catalog(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_catedracalendarentry backend_catedracalen_semester_id_866e884c_fk_backend_s; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_catedracalendarentry
    ADD CONSTRAINT backend_catedracalen_semester_id_866e884c_fk_backend_s FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_commission backend_commission_chief_teacher_id_378370af_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commission
    ADD CONSTRAINT backend_commission_chief_teacher_id_378370af_fk FOREIGN KEY (chief_teacher_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_commission backend_commission_department_id_65809027_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commission
    ADD CONSTRAINT backend_commission_department_id_65809027_fk FOREIGN KEY (department_id) REFERENCES public.backend_department(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_commissioninscription backend_commissioninscription_semester_id_41961132_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commissioninscription
    ADD CONSTRAINT backend_commissioninscription_semester_id_41961132_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_commissioninscription backend_commissioninscription_student_id_3d5072aa_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_commissioninscription
    ADD CONSTRAINT backend_commissioninscription_student_id_3d5072aa_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_contact backend_contact_from_student_id_9e3f9640_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_contact
    ADD CONSTRAINT backend_contact_from_student_id_9e3f9640_fk FOREIGN KEY (from_student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_contact backend_contact_to_student_id_a4127cff_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_contact
    ADD CONSTRAINT backend_contact_to_student_id_a4127cff_fk FOREIGN KEY (to_student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_evaluation backend_evaluation_parent_evaluation_id_be564441_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluation
    ADD CONSTRAINT backend_evaluation_parent_evaluation_id_be564441_fk FOREIGN KEY (parent_evaluation_id) REFERENCES public.backend_evaluation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_evaluation backend_evaluation_semester_id_11ee5907_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluation
    ADD CONSTRAINT backend_evaluation_semester_id_11ee5907_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_evaluationsubmission backend_evaluationsubmission_evaluation_id_168042de_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission
    ADD CONSTRAINT backend_evaluationsubmission_evaluation_id_168042de_fk FOREIGN KEY (evaluation_id) REFERENCES public.backend_evaluation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_evaluationsubmission backend_evaluationsubmission_grader_id_98422e73_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission
    ADD CONSTRAINT backend_evaluationsubmission_grader_id_98422e73_fk FOREIGN KEY (grader_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_evaluationsubmission backend_evaluationsubmission_student_id_3739c43f_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_evaluationsubmission
    ADD CONSTRAINT backend_evaluationsubmission_student_id_3739c43f_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_final_commissions backend_final_commissions_commission_id_3b447ca3_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final_commissions
    ADD CONSTRAINT backend_final_commissions_commission_id_3b447ca3_fk FOREIGN KEY (commission_id) REFERENCES public.backend_commission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_final_commissions backend_final_commissions_final_id_03525291_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final_commissions
    ADD CONSTRAINT backend_final_commissions_final_id_03525291_fk FOREIGN KEY (final_id) REFERENCES public.backend_final(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_final backend_final_teacher_id_0c1dfc21_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_final
    ADD CONSTRAINT backend_final_teacher_id_0c1dfc21_fk FOREIGN KEY (teacher_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_finalexam backend_finalexam_final_id_471da19e_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_finalexam
    ADD CONSTRAINT backend_finalexam_final_id_471da19e_fk FOREIGN KEY (final_id) REFERENCES public.backend_final(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_finalexam backend_finalexam_student_id_28f9e2fa_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_finalexam
    ADD CONSTRAINT backend_finalexam_student_id_28f9e2fa_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_form backend_form_form_type_id_b9c1bc04_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_form
    ADD CONSTRAINT backend_form_form_type_id_b9c1bc04_fk FOREIGN KEY (form_type_id) REFERENCES public.backend_formtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_form backend_form_ownership_group_id_a1e9120d_fk_backend_f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_form
    ADD CONSTRAINT backend_form_ownership_group_id_a1e9120d_fk_backend_f FOREIGN KEY (ownership_group_id) REFERENCES public.backend_formownershipgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formanswer backend_formanswer_field_id_e683e058_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formanswer
    ADD CONSTRAINT backend_formanswer_field_id_e683e058_fk FOREIGN KEY (field_id) REFERENCES public.backend_formfield(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formanswer backend_formanswer_submission_id_338e8a3f_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formanswer
    ADD CONSTRAINT backend_formanswer_submission_id_338e8a3f_fk FOREIGN KEY (submission_id) REFERENCES public.backend_formsubmission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formdocumentsource backend_formdocumentsource_form_id_be1f9af4_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formdocumentsource
    ADD CONSTRAINT backend_formdocumentsource_form_id_be1f9af4_fk FOREIGN KEY (form_id) REFERENCES public.backend_form(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formfield backend_formfield_catalog_id_e6d73868_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfield
    ADD CONSTRAINT backend_formfield_catalog_id_e6d73868_fk FOREIGN KEY (catalog_id) REFERENCES public.backend_catalog(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formfield backend_formfield_form_field_type_id_f3014536_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfield
    ADD CONSTRAINT backend_formfield_form_field_type_id_f3014536_fk FOREIGN KEY (form_field_type_id) REFERENCES public.backend_formfieldtype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formfield backend_formfield_form_id_0905f28c_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfield
    ADD CONSTRAINT backend_formfield_form_id_0905f28c_fk FOREIGN KEY (form_id) REFERENCES public.backend_form(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formfieldoption backend_formfieldoption_form_field_id_ed0da86c_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formfieldoption
    ADD CONSTRAINT backend_formfieldoption_form_field_id_ed0da86c_fk FOREIGN KEY (form_field_id) REFERENCES public.backend_formfield(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formownershipmember backend_formownershi_group_id_10e46567_fk_backend_f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formownershipmember
    ADD CONSTRAINT backend_formownershi_group_id_10e46567_fk_backend_f FOREIGN KEY (group_id) REFERENCES public.backend_formownershipgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formsubmission backend_formsubmission_form_id_3a6ae321_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission
    ADD CONSTRAINT backend_formsubmission_form_id_3a6ae321_fk FOREIGN KEY (form_id) REFERENCES public.backend_form(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formsubmission backend_formsubmission_status_id_d3289b17_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission
    ADD CONSTRAINT backend_formsubmission_status_id_d3289b17_fk FOREIGN KEY (status_id) REFERENCES public.backend_formsubmissionstatus(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formsubmission backend_formsubmission_teacher_id_5ee8bc1a_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission
    ADD CONSTRAINT backend_formsubmission_teacher_id_5ee8bc1a_fk FOREIGN KEY (teacher_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_formsubmission backend_formsubmission_user_id_82ddf966_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_formsubmission
    ADD CONSTRAINT backend_formsubmission_user_id_82ddf966_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_groupmembership backend_groupmembership_group_id_06bf83b6_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_groupmembership
    ADD CONSTRAINT backend_groupmembership_group_id_06bf83b6_fk FOREIGN KEY (group_id) REFERENCES public.backend_studygroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_groupmembership backend_groupmembership_student_id_2965add9_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_groupmembership
    ADD CONSTRAINT backend_groupmembership_student_id_2965add9_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_news backend_news_author_id_9ec388f3_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_news
    ADD CONSTRAINT backend_news_author_id_9ec388f3_fk FOREIGN KEY (author_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_news backend_news_department_id_85481fe0_fk_backend_department_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_news
    ADD CONSTRAINT backend_news_department_id_85481fe0_fk_backend_department_id FOREIGN KEY (department_id) REFERENCES public.backend_department(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_notification backend_notification_department_id_ab688b2d_fk_backend_d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_notification
    ADD CONSTRAINT backend_notification_department_id_ab688b2d_fk_backend_d FOREIGN KEY (department_id) REFERENCES public.backend_department(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_notification backend_notification_semester_id_41a21a92_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_notification
    ADD CONSTRAINT backend_notification_semester_id_41a21a92_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_notification backend_notification_sender_id_a0df67f9_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_notification
    ADD CONSTRAINT backend_notification_sender_id_a0df67f9_fk FOREIGN KEY (sender_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_passwordresetotp backend_passwordresetotp_user_id_22e93d12_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_passwordresetotp
    ADD CONSTRAINT backend_passwordresetotp_user_id_22e93d12_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_secretary backend_secretary_parent_secretary_id_f92a644e_fk_backend_s; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_secretary
    ADD CONSTRAINT backend_secretary_parent_secretary_id_f92a644e_fk_backend_s FOREIGN KEY (parent_secretary_id) REFERENCES public.backend_secretary(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_semester backend_semester_commission_id_5a004687_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semester
    ADD CONSTRAINT backend_semester_commission_id_5a004687_fk FOREIGN KEY (commission_id) REFERENCES public.backend_commission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_semesterschedule backend_semesterschedule_semester_id_61b29be1_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_semesterschedule
    ADD CONSTRAINT backend_semesterschedule_semester_id_61b29be1_fk FOREIGN KEY (semester_id) REFERENCES public.backend_semester(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_staff backend_staff_department_id_60ca9b21_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_staff
    ADD CONSTRAINT backend_staff_department_id_60ca9b21_fk FOREIGN KEY (department_id) REFERENCES public.backend_department(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_staff backend_staff_secretary_id_3f072af1_fk_backend_secretary_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_staff
    ADD CONSTRAINT backend_staff_secretary_id_3f072af1_fk_backend_secretary_id FOREIGN KEY (secretary_id) REFERENCES public.backend_secretary(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_staff backend_staff_user_id_8cb9a3a0_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_staff
    ADD CONSTRAINT backend_staff_user_id_8cb9a3a0_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_student backend_student_user_id_ccb8ff7d_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_student
    ADD CONSTRAINT backend_student_user_id_ccb8ff7d_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_studentcareer backend_studentcareer_career_id_c679668d_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studentcareer
    ADD CONSTRAINT backend_studentcareer_career_id_c679668d_fk FOREIGN KEY (career_id) REFERENCES public.backend_career(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_studentcareer backend_studentcareer_student_id_f7a10696_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studentcareer
    ADD CONSTRAINT backend_studentcareer_student_id_f7a10696_fk FOREIGN KEY (student_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_studygroup backend_studygroup_creator_id_3dc2f63b_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_studygroup
    ADD CONSTRAINT backend_studygroup_creator_id_3dc2f63b_fk FOREIGN KEY (creator_id) REFERENCES public.backend_student(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_teacher backend_teacher_user_id_b6ab6fbb_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacher
    ADD CONSTRAINT backend_teacher_user_id_b6ab6fbb_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_teacherrole backend_teacherrole_commission_id_0490481c_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacherrole
    ADD CONSTRAINT backend_teacherrole_commission_id_0490481c_fk FOREIGN KEY (commission_id) REFERENCES public.backend_commission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_teacherrole backend_teacherrole_teacher_id_294c6901_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_teacherrole
    ADD CONSTRAINT backend_teacherrole_teacher_id_294c6901_fk FOREIGN KEY (teacher_id) REFERENCES public.backend_teacher(user_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_user_groups backend_user_groups_group_id_df691386_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_groups
    ADD CONSTRAINT backend_user_groups_group_id_df691386_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_user_groups backend_user_groups_user_id_d2c44525_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_groups
    ADD CONSTRAINT backend_user_groups_user_id_d2c44525_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_user_user_permissions backend_user_user_pe_permission_id_634ab7e4_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_user_permissions
    ADD CONSTRAINT backend_user_user_pe_permission_id_634ab7e4_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_user_user_permissions backend_user_user_permissions_user_id_439140a5_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_user_user_permissions
    ADD CONSTRAINT backend_user_user_permissions_user_id_439140a5_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_usernotification backend_usernotification_notification_id_094ec51f_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_usernotification
    ADD CONSTRAINT backend_usernotification_notification_id_094ec51f_fk FOREIGN KEY (notification_id) REFERENCES public.backend_notification(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: backend_usernotification backend_usernotification_user_id_84ed3bd7_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.backend_usernotification
    ADD CONSTRAINT backend_usernotification_user_id_84ed3bd7_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: push_notifications_apnsdevice push_notifications_apnsdevice_user_id_44cc44d2_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_apnsdevice
    ADD CONSTRAINT push_notifications_apnsdevice_user_id_44cc44d2_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: push_notifications_gcmdevice push_notifications_gcmdevice_user_id_f3752f1b_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_gcmdevice
    ADD CONSTRAINT push_notifications_gcmdevice_user_id_f3752f1b_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: push_notifications_webpushdevice push_notifications_webpushdevice_user_id_e867e0a1_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_webpushdevice
    ADD CONSTRAINT push_notifications_webpushdevice_user_id_e867e0a1_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: push_notifications_wnsdevice push_notifications_wnsdevice_user_id_670eff0d_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.push_notifications_wnsdevice
    ADD CONSTRAINT push_notifications_wnsdevice_user_id_670eff0d_fk FOREIGN KEY (user_id) REFERENCES public.backend_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict YgIaQRpdUEhlUvuHxmppPIaOjJNtgt2gehvxlX5Dc1064AaGmBcDPVkeqs1huYW

