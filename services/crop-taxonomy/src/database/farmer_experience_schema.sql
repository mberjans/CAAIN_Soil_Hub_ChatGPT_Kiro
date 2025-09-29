-- Farmer Experience Database Schema
-- Schema for storing farmer experience data, feedback, and validation results

-- Farmer profiles table
CREATE TABLE farmer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID UNIQUE NOT NULL,
    
    -- Basic information
    farm_size_acres DECIMAL(10,2),
    farming_experience_years INTEGER,
    primary_crops TEXT[],
    
    -- Location and climate
    region VARCHAR(100),
    climate_zone VARCHAR(50),
    
    -- Management style
    management_style VARCHAR(50),
    technology_adoption VARCHAR(50),
    risk_tolerance VARCHAR(50),
    
    -- Experience history
    total_varieties_tested INTEGER DEFAULT 0,
    average_rating_tendency DECIMAL(3,2),
    feedback_frequency VARCHAR(50),
    
    -- Bias indicators
    optimism_bias_score DECIMAL(3,2),
    experience_bias_score DECIMAL(3,2),
    
    -- Profile metadata
    profile_created TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    profile_completeness DECIMAL(3,2) DEFAULT 0.0,
    
    -- Constraints
    CONSTRAINT check_farm_size CHECK (farm_size_acres >= 0),
    CONSTRAINT check_experience_years CHECK (farming_experience_years >= 0),
    CONSTRAINT check_total_varieties CHECK (total_varieties_tested >= 0),
    CONSTRAINT check_rating_tendency CHECK (average_rating_tendency >= 1.0 AND average_rating_tendency <= 5.0),
    CONSTRAINT check_bias_scores CHECK (
        optimism_bias_score >= 0.0 AND optimism_bias_score <= 1.0 AND
        experience_bias_score >= 0.0 AND experience_bias_score <= 1.0
    ),
    CONSTRAINT check_profile_completeness CHECK (profile_completeness >= 0.0 AND profile_completeness <= 1.0)
);

-- Farmer experience entries table
CREATE TABLE farmer_experience_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id UUID NOT NULL REFERENCES farmer_profiles(farmer_id),
    variety_id UUID NOT NULL,
    
    -- Survey data (stored as JSONB for flexibility)
    survey_data JSONB NOT NULL,
    field_performance JSONB,
    
    -- Validation and quality
    collection_date TIMESTAMP DEFAULT NOW(),
    validation_status VARCHAR(20) DEFAULT 'pending',
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    data_quality_score DECIMAL(3,2) DEFAULT 0.0,
    
    -- Metadata
    collection_method VARCHAR(50),
    validation_notes TEXT,
    requires_review BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CONSTRAINT check_validation_status CHECK (validation_status IN ('pending', 'validated', 'invalid', 'requires_review')),
    CONSTRAINT check_confidence_score CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    CONSTRAINT check_data_quality_score CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
    CONSTRAINT check_survey_data_structure CHECK (
        survey_data ? 'yield_rating' AND
        survey_data ? 'disease_resistance_rating' AND
        survey_data ? 'overall_satisfaction'
    )
);

-- Performance validation results table
CREATE TABLE performance_validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL,
    
    -- Validation metrics
    total_entries INTEGER NOT NULL,
    validated_entries INTEGER NOT NULL,
    confidence_scores DECIMAL(3,2)[],
    validation_errors TEXT[],
    
    -- Statistical analysis (stored as JSONB)
    statistical_analysis JSONB,
    trial_data_comparison JSONB,
    
    -- Overall assessment
    overall_confidence DECIMAL(3,2),
    validation_timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_total_entries CHECK (total_entries >= 0),
    CONSTRAINT check_validated_entries CHECK (validated_entries >= 0 AND validated_entries <= total_entries),
    CONSTRAINT check_overall_confidence CHECK (overall_confidence >= 0.0 AND overall_confidence <= 1.0)
);

-- Bias correction results table
CREATE TABLE bias_correction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL,
    
    -- Correction details
    correction_applied BOOLEAN DEFAULT FALSE,
    biases_detected VARCHAR(50)[],
    correction_factors JSONB,
    correction_method VARCHAR(100),
    
    -- Quality assessment
    correction_confidence DECIMAL(3,2),
    impact_assessment JSONB,
    
    -- Metadata
    correction_timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_correction_confidence CHECK (correction_confidence >= 0.0 AND correction_confidence <= 1.0)
);

-- Experience aggregation results table
CREATE TABLE experience_aggregation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL,
    
    -- Aggregated data (stored as JSONB)
    aggregated_data JSONB NOT NULL,
    confidence_level VARCHAR(20) NOT NULL,
    
    -- Sample information
    sample_size INTEGER NOT NULL,
    bias_correction_applied BOOLEAN DEFAULT FALSE,
    bias_correction_details JSONB,
    
    -- Statistical significance
    statistical_significance JSONB,
    aggregation_errors TEXT[],
    
    -- Metadata
    aggregation_timestamp TIMESTAMP DEFAULT NOW(),
    aggregation_method VARCHAR(100) DEFAULT 'weighted_average',
    
    -- Constraints
    CONSTRAINT check_sample_size CHECK (sample_size >= 0),
    CONSTRAINT check_confidence_level CHECK (confidence_level IN ('low', 'medium', 'high'))
);

-- Farmer experience insights table
CREATE TABLE farmer_experience_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL,
    
    -- Key insights
    top_strengths TEXT[],
    top_weaknesses TEXT[],
    farmer_recommendations TEXT[],
    
    -- Performance insights
    yield_consistency VARCHAR(100),
    disease_performance VARCHAR(100),
    management_requirements VARCHAR(100),
    
    -- Market insights
    market_performance VARCHAR(100),
    profitability_assessment VARCHAR(100),
    
    -- Regional insights
    regional_performance JSONB,
    climate_adaptation VARCHAR(100),
    
    -- Confidence and quality
    insight_confidence DECIMAL(3,2),
    data_quality_score DECIMAL(3,2),
    
    -- Metadata
    insights_generated TIMESTAMP DEFAULT NOW(),
    sample_size INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT check_insight_confidence CHECK (insight_confidence >= 0.0 AND insight_confidence <= 1.0),
    CONSTRAINT check_insight_data_quality CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
    CONSTRAINT check_insight_sample_size CHECK (sample_size >= 0)
);

-- Indexes for performance optimization
CREATE INDEX idx_farmer_profiles_farmer_id ON farmer_profiles(farmer_id);
CREATE INDEX idx_farmer_profiles_region ON farmer_profiles(region);
CREATE INDEX idx_farmer_profiles_climate_zone ON farmer_profiles(climate_zone);

CREATE INDEX idx_experience_entries_farmer_id ON farmer_experience_entries(farmer_id);
CREATE INDEX idx_experience_entries_variety_id ON farmer_experience_entries(variety_id);
CREATE INDEX idx_experience_entries_validation_status ON farmer_experience_entries(validation_status);
CREATE INDEX idx_experience_entries_collection_date ON farmer_experience_entries(collection_date);
CREATE INDEX idx_experience_entries_confidence_score ON farmer_experience_entries(confidence_score);

CREATE INDEX idx_validation_results_variety_id ON performance_validation_results(variety_id);
CREATE INDEX idx_validation_results_timestamp ON performance_validation_results(validation_timestamp);

CREATE INDEX idx_bias_correction_variety_id ON bias_correction_results(variety_id);
CREATE INDEX idx_bias_correction_timestamp ON bias_correction_results(correction_timestamp);

CREATE INDEX idx_aggregation_results_variety_id ON experience_aggregation_results(variety_id);
CREATE INDEX idx_aggregation_results_timestamp ON experience_aggregation_results(aggregation_timestamp);
CREATE INDEX idx_aggregation_results_confidence_level ON experience_aggregation_results(confidence_level);

CREATE INDEX idx_insights_variety_id ON farmer_experience_insights(variety_id);
CREATE INDEX idx_insights_generated ON farmer_experience_insights(insights_generated);

-- GIN indexes for JSONB columns
CREATE INDEX idx_experience_entries_survey_data ON farmer_experience_entries USING GIN(survey_data);
CREATE INDEX idx_experience_entries_field_performance ON farmer_experience_entries USING GIN(field_performance);
CREATE INDEX idx_validation_statistical_analysis ON performance_validation_results USING GIN(statistical_analysis);
CREATE INDEX idx_validation_trial_comparison ON performance_validation_results USING GIN(trial_data_comparison);
CREATE INDEX idx_bias_correction_factors ON bias_correction_results USING GIN(correction_factors);
CREATE INDEX idx_aggregation_data ON experience_aggregation_results USING GIN(aggregated_data);
CREATE INDEX idx_insights_regional_performance ON farmer_experience_insights USING GIN(regional_performance);

-- Views for common queries
CREATE VIEW farmer_experience_summary AS
SELECT 
    fee.variety_id,
    COUNT(*) as total_entries,
    COUNT(CASE WHEN fee.validation_status = 'validated' THEN 1 END) as validated_entries,
    AVG(fee.confidence_score) as avg_confidence_score,
    AVG(fee.data_quality_score) as avg_data_quality_score,
    MAX(fee.collection_date) as last_collection_date
FROM farmer_experience_entries fee
GROUP BY fee.variety_id;

CREATE VIEW farmer_profile_summary AS
SELECT 
    fp.farmer_id,
    fp.farm_size_acres,
    fp.farming_experience_years,
    fp.region,
    fp.climate_zone,
    fp.total_varieties_tested,
    fp.average_rating_tendency,
    fp.optimism_bias_score,
    fp.experience_bias_score,
    fp.profile_completeness,
    COUNT(fee.id) as total_feedback_entries,
    AVG(fee.confidence_score) as avg_feedback_confidence
FROM farmer_profiles fp
LEFT JOIN farmer_experience_entries fee ON fp.farmer_id = fee.farmer_id
GROUP BY fp.farmer_id, fp.farm_size_acres, fp.farming_experience_years, 
         fp.region, fp.climate_zone, fp.total_varieties_tested, 
         fp.average_rating_tendency, fp.optimism_bias_score, 
         fp.experience_bias_score, fp.profile_completeness;

-- Functions for data validation and processing
CREATE OR REPLACE FUNCTION validate_survey_data(survey_json JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check required fields
    IF NOT (survey_json ? 'yield_rating' AND 
            survey_json ? 'disease_resistance_rating' AND 
            survey_json ? 'overall_satisfaction') THEN
        RETURN FALSE;
    END IF;
    
    -- Check rating ranges
    IF NOT (survey_json->>'yield_rating' ~ '^[1-5](\.\d+)?$' AND
            survey_json->>'disease_resistance_rating' ~ '^[1-5](\.\d+)?$' AND
            survey_json->>'overall_satisfaction' ~ '^[1-5](\.\d+)?$') THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_data_quality_score(survey_json JSONB, field_performance_json JSONB)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    quality_score DECIMAL(3,2) := 0.0;
    field_data_score DECIMAL(3,2) := 0.0;
BEGIN
    -- Base score for survey data completeness
    quality_score := 0.6;
    
    -- Bonus for additional survey fields
    IF survey_json ? 'management_ease_rating' THEN
        quality_score := quality_score + 0.1;
    END IF;
    
    IF survey_json ? 'market_performance_rating' THEN
        quality_score := quality_score + 0.1;
    END IF;
    
    IF survey_json ? 'comments' AND survey_json->>'comments' != '' THEN
        quality_score := quality_score + 0.1;
    END IF;
    
    -- Field performance data bonus
    IF field_performance_json IS NOT NULL THEN
        field_data_score := 0.1;
        
        IF field_performance_json ? 'actual_yield' THEN
            field_data_score := field_data_score + 0.1;
        END IF;
        
        IF field_performance_json ? 'field_size_acres' THEN
            field_data_score := field_data_score + 0.05;
        END IF;
        
        IF field_performance_json ? 'planting_date' THEN
            field_data_score := field_data_score + 0.05;
        END IF;
        
        IF field_performance_json ? 'harvest_date' THEN
            field_data_score := field_data_score + 0.05;
        END IF;
    END IF;
    
    RETURN LEAST(quality_score + field_data_score, 1.0);
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic data processing
CREATE OR REPLACE FUNCTION update_farmer_profile_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update farmer profile statistics when new experience entry is added
    UPDATE farmer_profiles 
    SET 
        total_varieties_tested = (
            SELECT COUNT(DISTINCT variety_id) 
            FROM farmer_experience_entries 
            WHERE farmer_id = NEW.farmer_id
        ),
        average_rating_tendency = (
            SELECT AVG((survey_data->>'overall_satisfaction')::DECIMAL)
            FROM farmer_experience_entries 
            WHERE farmer_id = NEW.farmer_id 
            AND validation_status = 'validated'
        ),
        last_updated = NOW()
    WHERE farmer_id = NEW.farmer_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_farmer_stats
    AFTER INSERT OR UPDATE ON farmer_experience_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_farmer_profile_stats();

-- Data retention policy (optional)
CREATE OR REPLACE FUNCTION cleanup_old_experience_data()
RETURNS VOID AS $$
BEGIN
    -- Delete experience entries older than 5 years
    DELETE FROM farmer_experience_entries 
    WHERE collection_date < NOW() - INTERVAL '5 years';
    
    -- Delete validation results older than 3 years
    DELETE FROM performance_validation_results 
    WHERE validation_timestamp < NOW() - INTERVAL '3 years';
    
    -- Delete aggregation results older than 2 years
    DELETE FROM experience_aggregation_results 
    WHERE aggregation_timestamp < NOW() - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your security model)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO farmer_experience_service;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO farmer_experience_service;