-- TimescaleDB setup for fertilizer price tracking
-- This migration sets up TimescaleDB extension and creates hypertables for time-series data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertable for fertilizer price history
-- This will automatically partition the data by time for better performance
SELECT create_hypertable('fertilizer_price_history', 'price_date', if_not_exists => TRUE);

-- Create hypertable for price trend cache
SELECT create_hypertable('price_trend_cache', 'analysis_date', if_not_exists => TRUE);

-- Create hypertable for market intelligence cache
SELECT create_hypertable('market_intelligence_cache', 'report_date', if_not_exists => TRUE);

-- Add compression policy for older data (compress data older than 30 days)
SELECT add_compression_policy('fertilizer_price_history', INTERVAL '30 days', if_not_exists => TRUE);

-- Add retention policy (keep data for 2 years)
SELECT add_retention_policy('fertilizer_price_history', INTERVAL '2 years', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_fertilizer_price_history_product_region_date 
ON fertilizer_price_history (product_id, region, price_date DESC);

CREATE INDEX IF NOT EXISTS idx_fertilizer_price_history_source_date 
ON fertilizer_price_history (source, price_date DESC);

CREATE INDEX IF NOT EXISTS idx_fertilizer_price_history_fertilizer_type_date 
ON fertilizer_price_history (fertilizer_type, price_date DESC);

-- Create continuous aggregates for common queries
-- Daily price averages
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_price_averages
WITH (timescaledb.continuous) AS
SELECT 
    product_id,
    region,
    fertilizer_type,
    time_bucket('1 day', price_date) AS day,
    AVG(price_per_unit) AS avg_price,
    MIN(price_per_unit) AS min_price,
    MAX(price_per_unit) AS max_price,
    COUNT(*) AS price_points
FROM fertilizer_price_history
GROUP BY product_id, region, fertilizer_type, day;

-- Weekly price averages
CREATE MATERIALIZED VIEW IF NOT EXISTS weekly_price_averages
WITH (timescaledb.continuous) AS
SELECT 
    product_id,
    region,
    fertilizer_type,
    time_bucket('1 week', price_date) AS week,
    AVG(price_per_unit) AS avg_price,
    MIN(price_per_unit) AS min_price,
    MAX(price_per_unit) AS max_price,
    COUNT(*) AS price_points
FROM fertilizer_price_history
GROUP BY product_id, region, fertilizer_type, week;

-- Monthly price averages
CREATE MATERIALIZED VIEW IF NOT EXISTS monthly_price_averages
WITH (timescaledb.continuous) AS
SELECT 
    product_id,
    region,
    fertilizer_type,
    time_bucket('1 month', price_date) AS month,
    AVG(price_per_unit) AS avg_price,
    MIN(price_per_unit) AS min_price,
    MAX(price_per_unit) AS max_price,
    COUNT(*) AS price_points
FROM fertilizer_price_history
GROUP BY product_id, region, fertilizer_type, month;

-- Refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('daily_price_averages',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

SELECT add_continuous_aggregate_policy('weekly_price_averages',
    start_offset => INTERVAL '1 week',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

SELECT add_continuous_aggregate_policy('monthly_price_averages',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 week',
    schedule_interval => INTERVAL '1 week',
    if_not_exists => TRUE);

-- Create a function to get price trends efficiently
CREATE OR REPLACE FUNCTION get_price_trend(
    p_product_id UUID,
    p_region VARCHAR(50),
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    price_date DATE,
    price_per_unit FLOAT,
    price_change FLOAT,
    price_change_percent FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH price_data AS (
        SELECT 
            price_date,
            price_per_unit,
            LAG(price_per_unit) OVER (ORDER BY price_date) AS prev_price
        FROM fertilizer_price_history
        WHERE product_id = p_product_id 
        AND region = p_region
        AND price_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
        ORDER BY price_date
    )
    SELECT 
        pd.price_date,
        pd.price_per_unit,
        pd.price_per_unit - pd.prev_price AS price_change,
        CASE 
            WHEN pd.prev_price > 0 THEN 
                ((pd.price_per_unit - pd.prev_price) / pd.prev_price) * 100
            ELSE NULL
        END AS price_change_percent
    FROM price_data pd
    ORDER BY pd.price_date;
END;
$$ LANGUAGE plpgsql;

-- Create a function to calculate price volatility
CREATE OR REPLACE FUNCTION calculate_price_volatility(
    p_product_id UUID,
    p_region VARCHAR(50),
    p_days INTEGER DEFAULT 30
)
RETURNS FLOAT AS $$
DECLARE
    volatility FLOAT;
BEGIN
    WITH price_returns AS (
        SELECT 
            (price_per_unit - LAG(price_per_unit) OVER (ORDER BY price_date)) / 
            LAG(price_per_unit) OVER (ORDER BY price_date) AS daily_return
        FROM fertilizer_price_history
        WHERE product_id = p_product_id 
        AND region = p_region
        AND price_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
        ORDER BY price_date
    )
    SELECT STDDEV(daily_return) * SQRT(252) INTO volatility
    FROM price_returns
    WHERE daily_return IS NOT NULL;
    
    RETURN COALESCE(volatility, 0.0);
END;
$$ LANGUAGE plpgsql;

-- Create a function to get market summary
CREATE OR REPLACE FUNCTION get_market_summary(
    p_region VARCHAR(50) DEFAULT 'US',
    p_days INTEGER DEFAULT 7
)
RETURNS TABLE (
    fertilizer_type VARCHAR(50),
    avg_price FLOAT,
    price_change_7d FLOAT,
    price_change_7d_percent FLOAT,
    volatility FLOAT,
    price_points INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH current_prices AS (
        SELECT 
            fertilizer_type,
            AVG(price_per_unit) AS avg_price,
            COUNT(*) AS price_points
        FROM fertilizer_price_history
        WHERE region = p_region
        AND price_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
        GROUP BY fertilizer_type
    ),
    historical_prices AS (
        SELECT 
            fertilizer_type,
            AVG(price_per_unit) AS avg_price_7d_ago
        FROM fertilizer_price_history
        WHERE region = p_region
        AND price_date >= CURRENT_DATE - INTERVAL '1 day' * (p_days + 7)
        AND price_date < CURRENT_DATE - INTERVAL '1 day' * p_days
        GROUP BY fertilizer_type
    ),
    volatility_data AS (
        SELECT 
            fertilizer_type,
            calculate_price_volatility(product_id, p_region, p_days) AS volatility
        FROM fertilizer_price_history
        WHERE region = p_region
        AND price_date >= CURRENT_DATE - INTERVAL '1 day' * p_days
        GROUP BY fertilizer_type, product_id
    )
    SELECT 
        cp.fertilizer_type,
        cp.avg_price,
        cp.avg_price - hp.avg_price_7d_ago AS price_change_7d,
        CASE 
            WHEN hp.avg_price_7d_ago > 0 THEN 
                ((cp.avg_price - hp.avg_price_7d_ago) / hp.avg_price_7d_ago) * 100
            ELSE NULL
        END AS price_change_7d_percent,
        AVG(vd.volatility) AS volatility,
        cp.price_points
    FROM current_prices cp
    LEFT JOIN historical_prices hp ON cp.fertilizer_type = hp.fertilizer_type
    LEFT JOIN volatility_data vd ON cp.fertilizer_type = vd.fertilizer_type
    GROUP BY cp.fertilizer_type, cp.avg_price, hp.avg_price_7d_ago, cp.price_points
    ORDER BY cp.fertilizer_type;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fertilizer_strategy_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO fertilizer_strategy_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO fertilizer_strategy_user;

-- Create a view for easy access to current prices
CREATE OR REPLACE VIEW current_fertilizer_prices AS
SELECT DISTINCT ON (product_id, region)
    product_id,
    product_name,
    fertilizer_type,
    specific_product,
    price_per_unit,
    unit,
    currency,
    region,
    state,
    source,
    price_date,
    is_spot_price,
    is_contract_price,
    market_conditions,
    seasonal_factors,
    confidence,
    volatility,
    created_at
FROM fertilizer_price_history
ORDER BY product_id, region, price_date DESC;

-- Create a view for price trends
CREATE OR REPLACE VIEW fertilizer_price_trends AS
SELECT 
    product_id,
    product_name,
    fertilizer_type,
    specific_product,
    region,
    price_date,
    price_per_unit,
    LAG(price_per_unit) OVER (PARTITION BY product_id, region ORDER BY price_date) AS prev_price,
    price_per_unit - LAG(price_per_unit) OVER (PARTITION BY product_id, region ORDER BY price_date) AS price_change,
    CASE 
        WHEN LAG(price_per_unit) OVER (PARTITION BY product_id, region ORDER BY price_date) > 0 THEN 
            ((price_per_unit - LAG(price_per_unit) OVER (PARTITION BY product_id, region ORDER BY price_date)) / 
             LAG(price_per_unit) OVER (PARTITION BY product_id, region ORDER BY price_date)) * 100
        ELSE NULL
    END AS price_change_percent
FROM fertilizer_price_history
ORDER BY product_id, region, price_date DESC;

-- Add comments for documentation
COMMENT ON TABLE fertilizer_price_history IS 'Time-series table for fertilizer price data with TimescaleDB optimization';
COMMENT ON FUNCTION get_price_trend IS 'Get price trend data for a specific product and region';
COMMENT ON FUNCTION calculate_price_volatility IS 'Calculate price volatility for a specific product and region';
COMMENT ON FUNCTION get_market_summary IS 'Get market summary statistics for a region';
COMMENT ON VIEW current_fertilizer_prices IS 'View showing the most recent price for each product and region';
COMMENT ON VIEW fertilizer_price_trends IS 'View showing price trends with change calculations';
