-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create weather_stations table
CREATE TABLE IF NOT EXISTS weather_stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    elevation_meters INTEGER,
    source VARCHAR(50) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create weather_observations table
CREATE TABLE IF NOT EXISTS weather_observations (
    id SERIAL,
    station_id VARCHAR(50) REFERENCES weather_stations(station_id),
    observation_time TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5,2),
    temperature_min_c DECIMAL(5,2),
    temperature_max_c DECIMAL(5,2),
    precipitation_mm DECIMAL(6,2),
    humidity_percent INTEGER,
    wind_speed_kmh DECIMAL(5,2),
    wind_direction_degrees INTEGER,
    pressure_hpa DECIMAL(6,2),
    conditions VARCHAR(100),
    cloud_cover_percent INTEGER,
    solar_radiation DECIMAL(7,2),
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create weather_forecasts table
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id SERIAL,
    station_id VARCHAR(50) REFERENCES weather_stations(station_id),
    forecast_time TIMESTAMP NOT NULL,
    forecast_for TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5,2),
    precipitation_mm DECIMAL(6,2),
    precipitation_probability INTEGER,
    humidity_percent INTEGER,
    wind_speed_kmh DECIMAL(5,2),
    conditions VARCHAR(100),
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('weather_observations', 'observation_time', if_not_exists => TRUE);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('weather_forecasts', 'forecast_for', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_weather_obs_station_time ON weather_observations(station_id, observation_time DESC);
CREATE INDEX IF NOT EXISTS idx_weather_obs_time ON weather_observations(observation_time DESC);
CREATE INDEX IF NOT EXISTS idx_weather_forecast_station_time ON weather_forecasts(station_id, forecast_for DESC);

-- Create continuous aggregates for daily summaries
-- This continuous aggregate provides daily weather summaries for each station
CREATE MATERIALIZED VIEW IF NOT EXISTS weather_daily_summary
WITH (timescaledb.continuous) AS
SELECT
    station_id,
    time_bucket('1 day', observation_time) AS day,
    AVG(temperature_c) as avg_temp,
    MIN(temperature_min_c) as min_temp,
    MAX(temperature_max_c) as max_temp,
    SUM(precipitation_mm) as total_precipitation,
    AVG(humidity_percent) as avg_humidity
FROM weather_observations
GROUP BY station_id, day;

-- Add a continuous aggregate for forecast accuracy (comparing forecasts with actual observations)
-- This continuous aggregate tracks the accuracy of forecasts by comparing predicted values with actual observations
-- COMMENTED OUT DUE TO TIMESCALEDB LIMITATION: Cannot join multiple hypertables in continuous aggregates
-- CREATE MATERIALIZED VIEW IF NOT EXISTS forecast_accuracy_summary
-- WITH (timescaledb.continuous) AS
-- SELECT
--     f.station_id,
--     time_bucket('1 day', f.forecast_time) AS day,
--     AVG(ABS(f.temperature_c - o.temperature_c)) as avg_temp_error,
--     AVG(ABS(f.precipitation_mm - o.precipitation_mm)) as avg_precip_error
-- FROM weather_forecasts f
-- JOIN weather_observations o ON f.station_id = o.station_id 
--     AND f.forecast_for = o.observation_time
-- GROUP BY f.station_id, day;