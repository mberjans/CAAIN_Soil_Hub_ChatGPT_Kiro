--
-- PostgreSQL database dump
--

\restrict 7SqxOI6un1KJShkwtNuO4Y4azjpjndGysyB4Z1SknfWWnv2ycCm0D2v3Ddixedv

-- Dumped from database version 14.19 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

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
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: weather_observations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weather_observations (
    id integer NOT NULL,
    station_id character varying(50),
    observation_time timestamp without time zone NOT NULL,
    temperature_c numeric(5,2),
    temperature_min_c numeric(5,2),
    temperature_max_c numeric(5,2),
    precipitation_mm numeric(6,2),
    humidity_percent integer,
    wind_speed_kmh numeric(5,2),
    wind_direction_degrees integer,
    pressure_hpa numeric(6,2),
    conditions character varying(100),
    cloud_cover_percent integer,
    solar_radiation numeric(7,2),
    source character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.weather_observations OWNER TO postgres;

--
-- Name: _direct_view_6; Type: VIEW; Schema: _timescaledb_internal; Owner: postgres
--

CREATE VIEW _timescaledb_internal._direct_view_6 AS
 SELECT weather_observations.station_id,
    public.time_bucket('1 day'::interval, weather_observations.observation_time) AS day,
    avg(weather_observations.temperature_c) AS avg_temp,
    min(weather_observations.temperature_min_c) AS min_temp,
    max(weather_observations.temperature_max_c) AS max_temp,
    sum(weather_observations.precipitation_mm) AS total_precipitation,
    avg(weather_observations.humidity_percent) AS avg_humidity
   FROM public.weather_observations
  GROUP BY weather_observations.station_id, (public.time_bucket('1 day'::interval, weather_observations.observation_time));


ALTER TABLE _timescaledb_internal._direct_view_6 OWNER TO postgres;

--
-- Name: _materialized_hypertable_6; Type: TABLE; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TABLE _timescaledb_internal._materialized_hypertable_6 (
    station_id character varying(50),
    day timestamp without time zone NOT NULL,
    avg_temp numeric,
    min_temp numeric,
    max_temp numeric,
    total_precipitation numeric,
    avg_humidity numeric
);


ALTER TABLE _timescaledb_internal._materialized_hypertable_6 OWNER TO postgres;

--
-- Name: _partial_view_6; Type: VIEW; Schema: _timescaledb_internal; Owner: postgres
--

CREATE VIEW _timescaledb_internal._partial_view_6 AS
 SELECT weather_observations.station_id,
    public.time_bucket('1 day'::interval, weather_observations.observation_time) AS day,
    avg(weather_observations.temperature_c) AS avg_temp,
    min(weather_observations.temperature_min_c) AS min_temp,
    max(weather_observations.temperature_max_c) AS max_temp,
    sum(weather_observations.precipitation_mm) AS total_precipitation,
    avg(weather_observations.humidity_percent) AS avg_humidity
   FROM public.weather_observations
  GROUP BY weather_observations.station_id, (public.time_bucket('1 day'::interval, weather_observations.observation_time));


ALTER TABLE _timescaledb_internal._partial_view_6 OWNER TO postgres;

--
-- Name: crop_filtering_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_filtering_attributes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    variety_id uuid NOT NULL,
    pest_resistance_traits jsonb DEFAULT '{}'::jsonb,
    disease_resistance_traits jsonb DEFAULT '{}'::jsonb,
    market_class_filters jsonb DEFAULT '{}'::jsonb,
    certification_filters jsonb DEFAULT '{}'::jsonb,
    seed_availability_filters jsonb DEFAULT '{}'::jsonb,
    drought_tolerance character varying(20),
    heat_tolerance character varying(20),
    cold_tolerance character varying(20),
    management_complexity character varying(20),
    yield_stability_score integer,
    drought_tolerance_score integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.crop_filtering_attributes OWNER TO postgres;

--
-- Name: deficiency_detections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deficiency_detections (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    image_analysis_id uuid NOT NULL,
    nutrient character varying(50) NOT NULL,
    confidence_score numeric(3,2) NOT NULL,
    severity character varying(20) NOT NULL,
    affected_area_percent numeric(5,2),
    symptoms_detected jsonb,
    symptom_indicators jsonb,
    affected_regions jsonb,
    color_analysis jsonb,
    pattern_analysis jsonb,
    deficiency_type character varying(30),
    severity_score numeric(3,2),
    deficiency_probability numeric(3,2),
    model_version character varying(20),
    model_confidence_metrics jsonb,
    expert_validated boolean DEFAULT false,
    validation_notes text,
    validation_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_affected_area_range CHECK (((affected_area_percent >= (0)::numeric) AND (affected_area_percent <= (100)::numeric))),
    CONSTRAINT check_confidence_score_range CHECK (((confidence_score >= (0)::numeric) AND (confidence_score <= (1)::numeric))),
    CONSTRAINT check_deficiency_probability_range CHECK (((deficiency_probability >= (0)::numeric) AND (deficiency_probability <= (1)::numeric))),
    CONSTRAINT check_severity_score_range CHECK (((severity_score >= (0)::numeric) AND (severity_score <= (1)::numeric))),
    CONSTRAINT check_severity_values CHECK (((severity)::text = ANY ((ARRAY['mild'::character varying, 'moderate'::character varying, 'severe'::character varying])::text[])))
);


ALTER TABLE public.deficiency_detections OWNER TO postgres;

--
-- Name: TABLE deficiency_detections; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.deficiency_detections IS 'Detailed results of nutrient deficiency detection from image analysis';


--
-- Name: COLUMN deficiency_detections.image_analysis_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.image_analysis_id IS 'Foreign key to the associated image analysis';


--
-- Name: COLUMN deficiency_detections.nutrient; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.nutrient IS 'Nutrient name (nitrogen, phosphorus, potassium, etc.)';


--
-- Name: COLUMN deficiency_detections.confidence_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.confidence_score IS 'Detection confidence score (0-1)';


--
-- Name: COLUMN deficiency_detections.severity; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.severity IS 'Severity level: mild, moderate, severe';


--
-- Name: COLUMN deficiency_detections.affected_area_percent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.affected_area_percent IS 'Estimated percentage of plant affected';


--
-- Name: COLUMN deficiency_detections.symptoms_detected; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.symptoms_detected IS 'List of detected symptoms in JSON format';


--
-- Name: COLUMN deficiency_detections.symptom_indicators; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.symptom_indicators IS 'Detailed symptom analysis indicators in JSON format';


--
-- Name: COLUMN deficiency_detections.affected_regions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.affected_regions IS 'Regions of the image showing deficiency in JSON format';


--
-- Name: COLUMN deficiency_detections.color_analysis; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.color_analysis IS 'Color-based analysis results in JSON format';


--
-- Name: COLUMN deficiency_detections.pattern_analysis; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.pattern_analysis IS 'Pattern recognition results in JSON format';


--
-- Name: COLUMN deficiency_detections.deficiency_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.deficiency_type IS 'Type of deficiency: primary, secondary, micronutrient';


--
-- Name: COLUMN deficiency_detections.severity_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.severity_score IS 'Numerical severity score (0-1)';


--
-- Name: COLUMN deficiency_detections.deficiency_probability; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.deficiency_probability IS 'Overall probability of deficiency (0-1)';


--
-- Name: COLUMN deficiency_detections.expert_validated; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.expert_validated IS 'Whether this detection has been validated by an agricultural expert';


--
-- Name: COLUMN deficiency_detections.validation_notes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.validation_notes IS 'Notes from expert validation';


--
-- Name: COLUMN deficiency_detections.validation_date; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.deficiency_detections.validation_date IS 'Date when expert validation was performed';


--
-- Name: farmer_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farmer_preferences (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    preferred_filters jsonb DEFAULT '{}'::jsonb,
    filter_weights jsonb DEFAULT '{}'::jsonb,
    selected_varieties jsonb DEFAULT '[]'::jsonb,
    rejected_varieties jsonb DEFAULT '[]'::jsonb,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.farmer_preferences OWNER TO postgres;

--
-- Name: fertilizer_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fertilizer_prices (
    id integer NOT NULL,
    fertilizer_type_id integer NOT NULL,
    price numeric(10,2) NOT NULL,
    price_date date NOT NULL,
    region character varying(100) NOT NULL,
    source character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_fertilizer_prices_date_not_future CHECK ((price_date <= CURRENT_DATE)),
    CONSTRAINT chk_fertilizer_prices_price_positive CHECK ((price > (0)::numeric))
);


ALTER TABLE public.fertilizer_prices OWNER TO postgres;

--
-- Name: TABLE fertilizer_prices; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.fertilizer_prices IS 'Tracks historical fertilizer prices by region and date';


--
-- Name: COLUMN fertilizer_prices.price; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_prices.price IS 'Price per unit (typically per ton or per bag)';


--
-- Name: COLUMN fertilizer_prices.price_date; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_prices.price_date IS 'Date when the price was recorded';


--
-- Name: COLUMN fertilizer_prices.region; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_prices.region IS 'Geographic region for the price (e.g., state, province, market area)';


--
-- Name: COLUMN fertilizer_prices.source; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_prices.source IS 'Source of the price data (e.g., USDA, market report, supplier)';


--
-- Name: fertilizer_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fertilizer_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fertilizer_prices_id_seq OWNER TO postgres;

--
-- Name: fertilizer_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fertilizer_prices_id_seq OWNED BY public.fertilizer_prices.id;


--
-- Name: fertilizer_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fertilizer_types (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    category character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.fertilizer_types OWNER TO postgres;

--
-- Name: TABLE fertilizer_types; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.fertilizer_types IS 'Stores different types of fertilizers with their categories and descriptions';


--
-- Name: COLUMN fertilizer_types.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_types.name IS 'Unique name of the fertilizer type (e.g., Urea 46-0-0, Ammonium Nitrate)';


--
-- Name: COLUMN fertilizer_types.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.fertilizer_types.category IS 'Category of fertilizer (e.g., Nitrogen, Phosphorus, Potassium, Compound)';


--
-- Name: fertilizer_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fertilizer_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fertilizer_types_id_seq OWNER TO postgres;

--
-- Name: fertilizer_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fertilizer_types_id_seq OWNED BY public.fertilizer_types.id;


--
-- Name: filter_combinations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.filter_combinations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    combination_hash character varying(64) NOT NULL,
    filters jsonb NOT NULL,
    usage_count integer DEFAULT 1,
    avg_result_count integer,
    avg_response_time_ms integer,
    created_at timestamp without time zone DEFAULT now(),
    last_used_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.filter_combinations OWNER TO postgres;

--
-- Name: image_analyses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.image_analyses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    image_path character varying(512) NOT NULL,
    crop_type character varying(100) NOT NULL,
    growth_stage character varying(50),
    image_size_mb numeric(10,2),
    upload_timestamp timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    processing_status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    quality_score numeric(3,2),
    original_filename character varying(255),
    image_format character varying(10),
    image_width_pixels integer,
    image_height_pixels integer,
    model_version character varying(20),
    image_quality_metrics jsonb,
    analysis_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_positive_image_size CHECK ((image_size_mb > (0)::numeric)),
    CONSTRAINT check_processing_status CHECK (((processing_status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT check_quality_score_range CHECK (((quality_score >= (0)::numeric) AND (quality_score <= (1)::numeric)))
);


ALTER TABLE public.image_analyses OWNER TO postgres;

--
-- Name: TABLE image_analyses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.image_analyses IS 'Image analysis metadata and processing status for crop deficiency detection';


--
-- Name: COLUMN image_analyses.image_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.image_path IS 'Path to the stored image file';


--
-- Name: COLUMN image_analyses.crop_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.crop_type IS 'Type of crop (corn, soybean, wheat, etc.)';


--
-- Name: COLUMN image_analyses.growth_stage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.growth_stage IS 'Growth stage of the crop when image was taken';


--
-- Name: COLUMN image_analyses.processing_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.processing_status IS 'Current processing status: pending, processing, completed, failed';


--
-- Name: COLUMN image_analyses.quality_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.quality_score IS 'Overall image quality score (0-1)';


--
-- Name: COLUMN image_analyses.image_quality_metrics; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.image_quality_metrics IS 'Detailed quality assessment metrics in JSON format';


--
-- Name: COLUMN image_analyses.analysis_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.image_analyses.analysis_metadata IS 'Additional analysis metadata in JSON format';


--
-- Name: weather_daily_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.weather_daily_summary AS
 SELECT _materialized_hypertable_6.station_id,
    _materialized_hypertable_6.day,
    _materialized_hypertable_6.avg_temp,
    _materialized_hypertable_6.min_temp,
    _materialized_hypertable_6.max_temp,
    _materialized_hypertable_6.total_precipitation,
    _materialized_hypertable_6.avg_humidity
   FROM _timescaledb_internal._materialized_hypertable_6
  WHERE (_materialized_hypertable_6.day < COALESCE(_timescaledb_internal.to_timestamp_without_timezone(_timescaledb_internal.cagg_watermark(6)), '-infinity'::timestamp without time zone))
UNION ALL
 SELECT weather_observations.station_id,
    public.time_bucket('1 day'::interval, weather_observations.observation_time) AS day,
    avg(weather_observations.temperature_c) AS avg_temp,
    min(weather_observations.temperature_min_c) AS min_temp,
    max(weather_observations.temperature_max_c) AS max_temp,
    sum(weather_observations.precipitation_mm) AS total_precipitation,
    avg(weather_observations.humidity_percent) AS avg_humidity
   FROM public.weather_observations
  WHERE (weather_observations.observation_time >= COALESCE(_timescaledb_internal.to_timestamp_without_timezone(_timescaledb_internal.cagg_watermark(6)), '-infinity'::timestamp without time zone))
  GROUP BY weather_observations.station_id, (public.time_bucket('1 day'::interval, weather_observations.observation_time));


ALTER TABLE public.weather_daily_summary OWNER TO postgres;

--
-- Name: weather_forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weather_forecasts (
    id integer NOT NULL,
    station_id character varying(50),
    forecast_time timestamp without time zone NOT NULL,
    forecast_for timestamp without time zone NOT NULL,
    temperature_c numeric(5,2),
    precipitation_mm numeric(6,2),
    precipitation_probability integer,
    humidity_percent integer,
    wind_speed_kmh numeric(5,2),
    conditions character varying(100),
    source character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.weather_forecasts OWNER TO postgres;

--
-- Name: weather_forecasts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weather_forecasts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_forecasts_id_seq OWNER TO postgres;

--
-- Name: weather_forecasts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weather_forecasts_id_seq OWNED BY public.weather_forecasts.id;


--
-- Name: weather_observations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weather_observations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_observations_id_seq OWNER TO postgres;

--
-- Name: weather_observations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weather_observations_id_seq OWNED BY public.weather_observations.id;


--
-- Name: weather_stations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weather_stations (
    id integer NOT NULL,
    station_id character varying(50) NOT NULL,
    name character varying(200),
    latitude numeric(9,6) NOT NULL,
    longitude numeric(9,6) NOT NULL,
    elevation_meters integer,
    source character varying(50) NOT NULL,
    active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.weather_stations OWNER TO postgres;

--
-- Name: weather_stations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weather_stations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_stations_id_seq OWNER TO postgres;

--
-- Name: weather_stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weather_stations_id_seq OWNED BY public.weather_stations.id;


--
-- Name: fertilizer_prices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_prices ALTER COLUMN id SET DEFAULT nextval('public.fertilizer_prices_id_seq'::regclass);


--
-- Name: fertilizer_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_types ALTER COLUMN id SET DEFAULT nextval('public.fertilizer_types_id_seq'::regclass);


--
-- Name: weather_forecasts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_forecasts ALTER COLUMN id SET DEFAULT nextval('public.weather_forecasts_id_seq'::regclass);


--
-- Name: weather_observations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_observations ALTER COLUMN id SET DEFAULT nextval('public.weather_observations_id_seq'::regclass);


--
-- Name: weather_stations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_stations ALTER COLUMN id SET DEFAULT nextval('public.weather_stations_id_seq'::regclass);


--
-- Data for Name: cache_inval_bgw_job; Type: TABLE DATA; Schema: _timescaledb_cache; Owner: Mark
--

COPY _timescaledb_cache.cache_inval_bgw_job  FROM stdin;
\.


--
-- Data for Name: cache_inval_extension; Type: TABLE DATA; Schema: _timescaledb_cache; Owner: Mark
--

COPY _timescaledb_cache.cache_inval_extension  FROM stdin;
\.


--
-- Data for Name: cache_inval_hypertable; Type: TABLE DATA; Schema: _timescaledb_cache; Owner: Mark
--

COPY _timescaledb_cache.cache_inval_hypertable  FROM stdin;
\.


--
-- Data for Name: hypertable; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.hypertable (id, schema_name, table_name, associated_schema_name, associated_table_prefix, num_dimensions, chunk_sizing_func_schema, chunk_sizing_func_name, chunk_target_size, compression_state, compressed_hypertable_id, replication_factor) FROM stdin;
3	public	fertilizer_prices	_timescaledb_internal	_hyper_3	1	_timescaledb_internal	calculate_chunk_interval	0	0	\N	\N
4	public	weather_observations	_timescaledb_internal	_hyper_4	1	_timescaledb_internal	calculate_chunk_interval	0	0	\N	\N
5	public	weather_forecasts	_timescaledb_internal	_hyper_5	1	_timescaledb_internal	calculate_chunk_interval	0	0	\N	\N
6	_timescaledb_internal	_materialized_hypertable_6	_timescaledb_internal	_hyper_6	1	_timescaledb_internal	calculate_chunk_interval	0	0	\N	\N
\.


--
-- Data for Name: chunk; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.chunk (id, hypertable_id, schema_name, table_name, compressed_chunk_id, dropped, status, osm_chunk) FROM stdin;
\.


--
-- Data for Name: dimension; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.dimension (id, hypertable_id, column_name, column_type, aligned, num_slices, partitioning_func_schema, partitioning_func, interval_length, compress_interval_length, integer_now_func_schema, integer_now_func) FROM stdin;
3	3	price_date	date	t	\N	\N	\N	604800000000	\N	\N	\N
4	4	observation_time	timestamp without time zone	t	\N	\N	\N	604800000000	\N	\N	\N
5	5	forecast_for	timestamp without time zone	t	\N	\N	\N	604800000000	\N	\N	\N
6	6	day	timestamp without time zone	t	\N	\N	\N	6048000000000	\N	\N	\N
\.


--
-- Data for Name: dimension_slice; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.dimension_slice (id, dimension_id, range_start, range_end) FROM stdin;
\.


--
-- Data for Name: chunk_constraint; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.chunk_constraint (chunk_id, dimension_slice_id, constraint_name, hypertable_constraint_name) FROM stdin;
\.


--
-- Data for Name: chunk_data_node; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.chunk_data_node (chunk_id, node_chunk_id, node_name) FROM stdin;
\.


--
-- Data for Name: chunk_index; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.chunk_index (chunk_id, index_name, hypertable_id, hypertable_index_name) FROM stdin;
\.


--
-- Data for Name: compression_chunk_size; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.compression_chunk_size (chunk_id, compressed_chunk_id, uncompressed_heap_size, uncompressed_toast_size, uncompressed_index_size, compressed_heap_size, compressed_toast_size, compressed_index_size, numrows_pre_compression, numrows_post_compression) FROM stdin;
\.


--
-- Data for Name: continuous_agg; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_agg (mat_hypertable_id, raw_hypertable_id, parent_mat_hypertable_id, user_view_schema, user_view_name, partial_view_schema, partial_view_name, bucket_width, direct_view_schema, direct_view_name, materialized_only, finalized) FROM stdin;
6	4	\N	public	weather_daily_summary	_timescaledb_internal	_partial_view_6	86400000000	_timescaledb_internal	_direct_view_6	f	t
\.


--
-- Data for Name: continuous_agg_migrate_plan; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_agg_migrate_plan (mat_hypertable_id, start_ts, end_ts, user_view_definition) FROM stdin;
\.


--
-- Data for Name: continuous_agg_migrate_plan_step; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_agg_migrate_plan_step (mat_hypertable_id, step_id, status, start_ts, end_ts, type, config) FROM stdin;
\.


--
-- Data for Name: continuous_aggs_bucket_function; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_aggs_bucket_function (mat_hypertable_id, experimental, name, bucket_width, origin, timezone) FROM stdin;
\.


--
-- Data for Name: continuous_aggs_hypertable_invalidation_log; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_aggs_hypertable_invalidation_log (hypertable_id, lowest_modified_value, greatest_modified_value) FROM stdin;
\.


--
-- Data for Name: continuous_aggs_invalidation_threshold; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_aggs_invalidation_threshold (hypertable_id, watermark) FROM stdin;
4	-210866803200000000
\.


--
-- Data for Name: continuous_aggs_materialization_invalidation_log; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_aggs_materialization_invalidation_log (materialization_id, lowest_modified_value, greatest_modified_value) FROM stdin;
6	-9223372036854775808	9223372036854775807
\.


--
-- Data for Name: continuous_aggs_watermark; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.continuous_aggs_watermark (mat_hypertable_id, watermark) FROM stdin;
6	-210866803200000000
\.


--
-- Data for Name: dimension_partition; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.dimension_partition (dimension_id, range_start, data_nodes) FROM stdin;
\.


--
-- Data for Name: hypertable_compression; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.hypertable_compression (hypertable_id, attname, compression_algorithm_id, segmentby_column_index, orderby_column_index, orderby_asc, orderby_nullsfirst) FROM stdin;
\.


--
-- Data for Name: hypertable_data_node; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.hypertable_data_node (hypertable_id, node_hypertable_id, node_name, block_chunks) FROM stdin;
\.


--
-- Data for Name: metadata; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.metadata (key, value, include_in_telemetry) FROM stdin;
exported_uuid	20ae46ff-e73a-42e4-9cee-8f3d3a9cb7d6	t
\.


--
-- Data for Name: remote_txn; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.remote_txn (data_node_name, remote_transaction_id) FROM stdin;
\.


--
-- Data for Name: tablespace; Type: TABLE DATA; Schema: _timescaledb_catalog; Owner: Mark
--

COPY _timescaledb_catalog.tablespace (id, hypertable_id, tablespace_name) FROM stdin;
\.


--
-- Data for Name: bgw_job; Type: TABLE DATA; Schema: _timescaledb_config; Owner: Mark
--

COPY _timescaledb_config.bgw_job (id, application_name, schedule_interval, max_runtime, max_retries, retry_period, proc_schema, proc_name, owner, scheduled, fixed_schedule, initial_start, hypertable_id, config, check_schema, check_name, timezone) FROM stdin;
\.


--
-- Data for Name: _materialized_hypertable_6; Type: TABLE DATA; Schema: _timescaledb_internal; Owner: postgres
--

COPY _timescaledb_internal._materialized_hypertable_6 (station_id, day, avg_temp, min_temp, max_temp, total_precipitation, avg_humidity) FROM stdin;
\.


--
-- Data for Name: job_errors; Type: TABLE DATA; Schema: _timescaledb_internal; Owner: Mark
--

COPY _timescaledb_internal.job_errors (job_id, pid, start_time, finish_time, error_data) FROM stdin;
\.


--
-- Data for Name: crop_filtering_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_filtering_attributes (id, variety_id, pest_resistance_traits, disease_resistance_traits, market_class_filters, certification_filters, seed_availability_filters, drought_tolerance, heat_tolerance, cold_tolerance, management_complexity, yield_stability_score, drought_tolerance_score, created_at, updated_at) FROM stdin;
fbda1e02-518b-4c8e-aedd-f3dbcd972220	2ff31fd7-e292-4836-bfe4-d9b32060049f	{"rootworm": "moderate", "corn_borer": "resistant"}	{"gray_leaf_spot": "resistant", "northern_leaf_blight": "moderate"}	{"market_class": "yellow_dent", "organic_certified": true}	{"usda_organic": true, "non_gmo_project": false}	{"supplier": "Pioneer", "availability": "high", "lead_time_days": 14}	moderate	high	moderate	moderate	85	75	2025-10-21 11:44:24.948434	2025-10-21 11:44:24.948434
bd287d6f-59b0-416b-9cdd-90172403e4fb	acefcd6e-d787-40bf-bc76-c1c32d09d6a7	{"aphids": "resistant", "corn_earworm": "susceptible"}	{"rust": "resistant", "smut": "resistant"}	{"non_gmo": true, "market_class": "white_corn"}	{"usda_organic": false, "non_gmo_project": true}	{"supplier": "Monsanto", "availability": "medium", "lead_time_days": 21}	high	moderate	low	low	90	80	2025-10-21 11:44:24.948434	2025-10-21 11:44:24.948434
e76fe2c2-93db-4e06-8567-0fc797e0b7c6	14735c03-6ac3-4e9a-87ab-b08a669a7093	{"cutworm": "resistant", "wireworm": "moderate"}	{"blight": "resistant", "mildew": "moderate"}	{"market_class": "food_grade", "organic_certified": false}	{"traceable": true, "identity_preserved": true}	{"supplier": "Syngenta", "availability": "low", "lead_time_days": 30}	low	high	high	high	70	50	2025-10-21 11:44:24.948434	2025-10-21 11:44:24.948434
3a7cefaf-12a3-4795-8c89-645e93898f78	8e9c37fe-0752-4e52-bf09-c3d6b95c19ef	{"beetle": "moderate", "caterpillar": "susceptible"}	{"downy_mildew": "resistant", "powdery_mildew": "moderate"}	{"non_gmo": false, "market_class": "feed_grade"}	{"conventional": true}	{"supplier": "Local Coop", "availability": "very_high", "lead_time_days": 7}	moderate	moderate	moderate	low	75	65	2025-10-21 11:44:24.948434	2025-10-21 11:44:24.948434
f00c60f7-3ee9-4ce2-8cb9-4b8fdf781431	326a86e6-c91c-450e-8c1e-4311775231b5	{"thrips": "moderate", "spider_mites": "resistant"}	{"fusarium": "resistant", "anthracnose": "moderate"}	{"market_class": "specialty", "organic_certified": true}	{"non_gmo_project": true, "specialty_crop_certified": true}	{"supplier": "Specialty Seeds Inc", "availability": "limited", "lead_time_days": 25}	high	high	moderate	high	88	82	2025-10-21 11:44:24.948434	2025-10-21 11:44:24.948434
\.


--
-- Data for Name: deficiency_detections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deficiency_detections (id, image_analysis_id, nutrient, confidence_score, severity, affected_area_percent, symptoms_detected, symptom_indicators, affected_regions, color_analysis, pattern_analysis, deficiency_type, severity_score, deficiency_probability, model_version, model_confidence_metrics, expert_validated, validation_notes, validation_date, created_at, updated_at) FROM stdin;
550e8400-e29b-41d4-a716-446655440002	550e8400-e29b-41d4-a716-446655440001	nitrogen	0.75	moderate	35.50	["Yellowing of older leaves", "Stunted growth", "Pale green color"]	\N	\N	\N	\N	primary	0.65	0.75	v1.0	\N	f	\N	\N	2025-10-21 14:14:11.34274-06	2025-10-21 14:14:11.34274-06
\.


--
-- Data for Name: farmer_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farmer_preferences (id, user_id, preferred_filters, filter_weights, selected_varieties, rejected_varieties, created_at, updated_at) FROM stdin;
5c6f95ef-9356-4c81-9ce5-5697348c5086	0678f9d5-d167-4c38-b426-a3d362f40f31	{"market_class": "yellow_dent", "drought_tolerance": "high", "organic_certified": true}	{"market_class": 0.7, "drought_tolerance": 0.9, "organic_certified": 0.8}	["var_1", "var_2", "var_3"]	["var_4", "var_5"]	2025-10-21 11:44:24.954251	2025-10-21 11:44:24.954251
b570f617-31ea-4a56-9fdd-e8315329d98a	1a5b88cf-cfd9-499c-a56c-ec0aa246bc0e	{"pest_resistance": {"corn_borer": "resistant"}, "yield_stability": {"min": 80}}	{"pest_resistance": 0.95, "yield_stability": 0.85}	["var_6", "var_7"]	["var_8", "var_9", "var_10"]	2025-10-21 11:44:24.954251	2025-10-21 11:44:24.954251
98135608-b6c5-4910-9246-0b6289c3f50e	7621bb12-5f72-40d5-8502-20c769864652	{"availability": "high", "management_complexity": "low"}	{"availability": 0.7, "management_complexity": 0.9}	["var_11", "var_12", "var_13"]	[]	2025-10-21 11:44:24.954251	2025-10-21 11:44:24.954251
75edbd82-a434-4e08-b817-15c6ddeb322b	6fe483b2-097c-41ec-aed8-769dc4f6f929	{"certification": {"usda_organic": true}, "disease_resistance": {"rust": "resistant"}}	{"certification": 0.9, "disease_resistance": 0.8}	["var_14", "var_15"]	["var_16", "var_17"]	2025-10-21 11:44:24.954251	2025-10-21 11:44:24.954251
7c611efe-4375-4f98-9d0b-5557503bad9a	26cf7658-85ec-4572-9431-d03a4ea20997	{"cold_tolerance": "low", "heat_tolerance": "high", "drought_tolerance": "moderate"}	{"cold_tolerance": 0.6, "heat_tolerance": 0.8, "drought_tolerance": 0.7}	["var_18", "var_19", "var_20"]	["var_21"]	2025-10-21 11:44:24.954251	2025-10-21 11:44:24.954251
\.


--
-- Data for Name: fertilizer_prices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fertilizer_prices (id, fertilizer_type_id, price, price_date, region, source, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fertilizer_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fertilizer_types (id, name, description, category, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: filter_combinations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.filter_combinations (id, combination_hash, filters, usage_count, avg_result_count, avg_response_time_ms, created_at, last_used_at) FROM stdin;
f0ee0b9a-af0b-46ae-99b9-0f5b8065b1d6	hash1	{"crop_type": "corn", "drought_tolerance": "high"}	15	23	150	2025-10-21 11:44:24.955389	2025-10-21 11:44:24.955389
3523b0d0-2380-4d69-90f9-39e49ad70675	hash2	{"crop_type": "soybean", "pest_resistance": {"aphids": "resistant"}, "organic_certified": true}	8	12	95	2025-10-21 11:44:24.955389	2025-10-21 11:44:24.955389
6cd5c076-f9bf-4b6d-8a35-6ff47d5b32c2	hash3	{"crop_type": "corn", "market_class": "food_grade", "certification": {"usda_organic": true}}	22	8	180	2025-10-21 11:44:24.955389	2025-10-21 11:44:24.955389
f7a3c51e-6544-4c32-ac83-576c0975523d	hash4	{"crop_type": "wheat", "yield_stability_min": 80, "management_complexity": "low"}	5	31	125	2025-10-21 11:44:24.955389	2025-10-21 11:44:24.955389
805dbe89-550c-43c4-a48d-8c95920268cb	hash5	{"crop_type": "corn", "pest_resistance": {"rootworm": "moderate", "corn_borer": "resistant"}, "disease_resistance": {"rust": "resistant"}}	42	17	210	2025-10-21 11:44:24.955389	2025-10-21 11:44:24.955389
\.


--
-- Data for Name: image_analyses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.image_analyses (id, image_path, crop_type, growth_stage, image_size_mb, upload_timestamp, processing_status, quality_score, original_filename, image_format, image_width_pixels, image_height_pixels, model_version, image_quality_metrics, analysis_metadata, created_at, updated_at) FROM stdin;
550e8400-e29b-41d4-a716-446655440001	/sample_images/corn_deficiency_test_1.jpg	corn	V6	2.40	2025-10-21 14:14:11.34274-06	completed	0.85	corn_deficiency_test_1.jpg	jpg	1024	768	v1.0	\N	\N	2025-10-21 14:14:11.34274-06	2025-10-21 14:14:11.34274-06
\.


--
-- Data for Name: weather_forecasts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weather_forecasts (id, station_id, forecast_time, forecast_for, temperature_c, precipitation_mm, precipitation_probability, humidity_percent, wind_speed_kmh, conditions, source, created_at) FROM stdin;
\.


--
-- Data for Name: weather_observations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weather_observations (id, station_id, observation_time, temperature_c, temperature_min_c, temperature_max_c, precipitation_mm, humidity_percent, wind_speed_kmh, wind_direction_degrees, pressure_hpa, conditions, cloud_cover_percent, solar_radiation, source, created_at) FROM stdin;
\.


--
-- Data for Name: weather_stations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weather_stations (id, station_id, name, latitude, longitude, elevation_meters, source, active, created_at) FROM stdin;
\.


--
-- Name: chunk_constraint_name; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.chunk_constraint_name', 1, false);


--
-- Name: chunk_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.chunk_id_seq', 1, false);


--
-- Name: continuous_agg_migrate_plan_step_step_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.continuous_agg_migrate_plan_step_step_id_seq', 1, false);


--
-- Name: dimension_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.dimension_id_seq', 6, true);


--
-- Name: dimension_slice_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.dimension_slice_id_seq', 1, false);


--
-- Name: hypertable_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_catalog; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_catalog.hypertable_id_seq', 6, true);


--
-- Name: bgw_job_id_seq; Type: SEQUENCE SET; Schema: _timescaledb_config; Owner: Mark
--

SELECT pg_catalog.setval('_timescaledb_config.bgw_job_id_seq', 1000, false);


--
-- Name: fertilizer_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fertilizer_prices_id_seq', 1, false);


--
-- Name: fertilizer_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fertilizer_types_id_seq', 1, false);


--
-- Name: weather_forecasts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weather_forecasts_id_seq', 1, false);


--
-- Name: weather_observations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weather_observations_id_seq', 1, false);


--
-- Name: weather_stations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weather_stations_id_seq', 1, false);


--
-- Name: crop_filtering_attributes crop_filtering_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_filtering_attributes
    ADD CONSTRAINT crop_filtering_attributes_pkey PRIMARY KEY (id);


--
-- Name: crop_filtering_attributes crop_filtering_attributes_variety_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_filtering_attributes
    ADD CONSTRAINT crop_filtering_attributes_variety_id_key UNIQUE (variety_id);


--
-- Name: deficiency_detections deficiency_detections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deficiency_detections
    ADD CONSTRAINT deficiency_detections_pkey PRIMARY KEY (id);


--
-- Name: farmer_preferences farmer_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farmer_preferences
    ADD CONSTRAINT farmer_preferences_pkey PRIMARY KEY (id);


--
-- Name: fertilizer_prices fertilizer_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_prices
    ADD CONSTRAINT fertilizer_prices_pkey PRIMARY KEY (id, price_date);


--
-- Name: fertilizer_types fertilizer_types_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_types
    ADD CONSTRAINT fertilizer_types_name_key UNIQUE (name);


--
-- Name: fertilizer_types fertilizer_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_types
    ADD CONSTRAINT fertilizer_types_pkey PRIMARY KEY (id);


--
-- Name: filter_combinations filter_combinations_combination_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filter_combinations
    ADD CONSTRAINT filter_combinations_combination_hash_key UNIQUE (combination_hash);


--
-- Name: filter_combinations filter_combinations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.filter_combinations
    ADD CONSTRAINT filter_combinations_pkey PRIMARY KEY (id);


--
-- Name: image_analyses image_analyses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.image_analyses
    ADD CONSTRAINT image_analyses_pkey PRIMARY KEY (id);


--
-- Name: fertilizer_prices uk_fertilizer_prices_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_prices
    ADD CONSTRAINT uk_fertilizer_prices_unique UNIQUE (fertilizer_type_id, price_date, region, source);


--
-- Name: weather_stations weather_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_stations
    ADD CONSTRAINT weather_stations_pkey PRIMARY KEY (id);


--
-- Name: weather_stations weather_stations_station_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_stations
    ADD CONSTRAINT weather_stations_station_id_key UNIQUE (station_id);


--
-- Name: _materialized_hypertable_6_day_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _materialized_hypertable_6_day_idx ON _timescaledb_internal._materialized_hypertable_6 USING btree (day DESC);


--
-- Name: _materialized_hypertable_6_station_id_day_idx; Type: INDEX; Schema: _timescaledb_internal; Owner: postgres
--

CREATE INDEX _materialized_hypertable_6_station_id_day_idx ON _timescaledb_internal._materialized_hypertable_6 USING btree (station_id, day DESC);


--
-- Name: idx_certification_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_certification_gin ON public.crop_filtering_attributes USING gin (certification_filters);


--
-- Name: idx_deficiency_detections_analysis; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deficiency_detections_analysis ON public.deficiency_detections USING btree (image_analysis_id);


--
-- Name: idx_deficiency_detections_confidence; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deficiency_detections_confidence ON public.deficiency_detections USING btree (confidence_score);


--
-- Name: idx_deficiency_detections_expert_validated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deficiency_detections_expert_validated ON public.deficiency_detections USING btree (expert_validated);


--
-- Name: idx_deficiency_detections_nutrient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deficiency_detections_nutrient ON public.deficiency_detections USING btree (nutrient);


--
-- Name: idx_deficiency_detections_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deficiency_detections_severity ON public.deficiency_detections USING btree (severity);


--
-- Name: idx_disease_resistance_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_disease_resistance_gin ON public.crop_filtering_attributes USING gin (disease_resistance_traits);


--
-- Name: idx_farmer_pref_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farmer_pref_user ON public.farmer_preferences USING btree (user_id);


--
-- Name: idx_fertilizer_prices_composite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_prices_composite ON public.fertilizer_prices USING btree (fertilizer_type_id, price_date, region);


--
-- Name: idx_fertilizer_prices_fertilizer_type_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_prices_fertilizer_type_id ON public.fertilizer_prices USING btree (fertilizer_type_id);


--
-- Name: idx_fertilizer_prices_price_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_prices_price_date ON public.fertilizer_prices USING btree (price_date);


--
-- Name: idx_fertilizer_prices_region; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_prices_region ON public.fertilizer_prices USING btree (region);


--
-- Name: idx_fertilizer_prices_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_prices_source ON public.fertilizer_prices USING btree (source);


--
-- Name: idx_fertilizer_types_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_types_category ON public.fertilizer_types USING btree (category);


--
-- Name: idx_fertilizer_types_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fertilizer_types_name ON public.fertilizer_types USING btree (name);


--
-- Name: idx_filter_combo_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filter_combo_hash ON public.filter_combinations USING btree (combination_hash);


--
-- Name: idx_filter_combo_usage; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filter_combo_usage ON public.filter_combinations USING btree (usage_count);


--
-- Name: idx_filter_weights_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filter_weights_gin ON public.farmer_preferences USING gin (filter_weights);


--
-- Name: idx_filters_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_filters_gin ON public.filter_combinations USING gin (filters);


--
-- Name: idx_image_analyses_crop_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_image_analyses_crop_type ON public.image_analyses USING btree (crop_type);


--
-- Name: idx_image_analyses_image_path; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_image_analyses_image_path ON public.image_analyses USING btree (image_path);


--
-- Name: idx_image_analyses_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_image_analyses_status ON public.image_analyses USING btree (processing_status);


--
-- Name: idx_image_analyses_upload_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_image_analyses_upload_time ON public.image_analyses USING btree (upload_timestamp);


--
-- Name: idx_market_class_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_market_class_gin ON public.crop_filtering_attributes USING gin (market_class_filters);


--
-- Name: idx_pest_resistance_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_pest_resistance_gin ON public.crop_filtering_attributes USING gin (pest_resistance_traits);


--
-- Name: idx_preferred_filters_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_preferred_filters_gin ON public.farmer_preferences USING gin (preferred_filters);


--
-- Name: idx_rejected_varieties_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_rejected_varieties_gin ON public.farmer_preferences USING gin (rejected_varieties);


--
-- Name: idx_seed_availability_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_seed_availability_gin ON public.crop_filtering_attributes USING gin (seed_availability_filters);


--
-- Name: idx_selected_varieties_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_selected_varieties_gin ON public.farmer_preferences USING gin (selected_varieties);


--
-- Name: idx_weather_forecast_station_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_weather_forecast_station_time ON public.weather_forecasts USING btree (station_id, forecast_for DESC);


--
-- Name: idx_weather_obs_station_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_weather_obs_station_time ON public.weather_observations USING btree (station_id, observation_time DESC);


--
-- Name: idx_weather_obs_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_weather_obs_time ON public.weather_observations USING btree (observation_time DESC);


--
-- Name: weather_forecasts_forecast_for_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX weather_forecasts_forecast_for_idx ON public.weather_forecasts USING btree (forecast_for DESC);


--
-- Name: weather_observations_observation_time_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX weather_observations_observation_time_idx ON public.weather_observations USING btree (observation_time DESC);


--
-- Name: _materialized_hypertable_6 ts_insert_blocker; Type: TRIGGER; Schema: _timescaledb_internal; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON _timescaledb_internal._materialized_hypertable_6 FOR EACH ROW EXECUTE FUNCTION _timescaledb_internal.insert_blocker();


--
-- Name: weather_observations ts_cagg_invalidation_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_cagg_invalidation_trigger AFTER INSERT OR DELETE OR UPDATE ON public.weather_observations FOR EACH ROW EXECUTE FUNCTION _timescaledb_internal.continuous_agg_invalidation_trigger('4');


--
-- Name: fertilizer_prices ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.fertilizer_prices FOR EACH ROW EXECUTE FUNCTION _timescaledb_internal.insert_blocker();


--
-- Name: weather_forecasts ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.weather_forecasts FOR EACH ROW EXECUTE FUNCTION _timescaledb_internal.insert_blocker();


--
-- Name: weather_observations ts_insert_blocker; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER ts_insert_blocker BEFORE INSERT ON public.weather_observations FOR EACH ROW EXECUTE FUNCTION _timescaledb_internal.insert_blocker();


--
-- Name: deficiency_detections update_deficiency_detections_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_deficiency_detections_updated_at BEFORE UPDATE ON public.deficiency_detections FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: fertilizer_prices update_fertilizer_prices_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_fertilizer_prices_updated_at BEFORE UPDATE ON public.fertilizer_prices FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: fertilizer_types update_fertilizer_types_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_fertilizer_types_updated_at BEFORE UPDATE ON public.fertilizer_types FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: image_analyses update_image_analyses_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_image_analyses_updated_at BEFORE UPDATE ON public.image_analyses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: deficiency_detections deficiency_detections_image_analysis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deficiency_detections
    ADD CONSTRAINT deficiency_detections_image_analysis_id_fkey FOREIGN KEY (image_analysis_id) REFERENCES public.image_analyses(id) ON DELETE CASCADE;


--
-- Name: fertilizer_prices fertilizer_prices_fertilizer_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fertilizer_prices
    ADD CONSTRAINT fertilizer_prices_fertilizer_type_id_fkey FOREIGN KEY (fertilizer_type_id) REFERENCES public.fertilizer_types(id) ON DELETE CASCADE;


--
-- Name: weather_forecasts weather_forecasts_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_forecasts
    ADD CONSTRAINT weather_forecasts_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.weather_stations(station_id);


--
-- Name: weather_observations weather_observations_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weather_observations
    ADD CONSTRAINT weather_observations_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.weather_stations(station_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 7SqxOI6un1KJShkwtNuO4Y4azjpjndGysyB4Z1SknfWWnv2ycCm0D2v3Ddixedv

