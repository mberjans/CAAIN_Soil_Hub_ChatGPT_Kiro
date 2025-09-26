-- Cover Crop Benefit Tracking Database Schema
-- PostgreSQL schema for comprehensive benefit quantification and tracking

-- Create schema for benefit tracking
CREATE SCHEMA IF NOT EXISTS benefit_tracking;
SET search_path TO benefit_tracking, public;

-- ======================================================================
-- BENEFIT QUANTIFICATION TABLES
-- ======================================================================

-- Main benefit quantification entries table
CREATE TABLE benefit_quantification_entries (
    entry_id VARCHAR(255) PRIMARY KEY,
    farm_id VARCHAR(255) NOT NULL,
    field_id VARCHAR(255) NOT NULL,
    cover_crop_implementation_id VARCHAR(255) NOT NULL,
    
    -- Benefit identification
    benefit_type VARCHAR(50) NOT NULL, -- SoilBenefit enum values
    benefit_category VARCHAR(50) NOT NULL,
    
    -- Timing and status
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'predicted', -- BenefitQuantificationStatus enum
    
    -- Predicted values
    predicted_value DECIMAL(12,4) NOT NULL,
    predicted_unit VARCHAR(50) NOT NULL,
    predicted_confidence DECIMAL(3,2) CHECK (predicted_confidence >= 0.0 AND predicted_confidence <= 1.0),
    
    -- Actual measurements
    validated_value DECIMAL(12,4),
    measurement_variance DECIMAL(12,4),
    
    -- Economic quantification
    economic_value_predicted DECIMAL(12,2),
    economic_value_actual DECIMAL(12,2),
    cost_savings DECIMAL(12,2),
    
    -- Temporal tracking
    measurement_start_date TIMESTAMP WITH TIME ZONE,
    measurement_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Accuracy and validation
    prediction_accuracy DECIMAL(3,2) CHECK (prediction_accuracy >= 0.0 AND prediction_accuracy <= 1.0),
    validation_status VARCHAR(20) DEFAULT 'pending',
    expert_validation_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_farm_field (farm_id, field_id),
    INDEX idx_benefit_type (benefit_type),
    INDEX idx_prediction_date (prediction_date),
    INDEX idx_status (status)
);

-- Measurement records table
CREATE TABLE benefit_measurement_records (
    record_id VARCHAR(255) PRIMARY KEY,
    entry_id VARCHAR(255) NOT NULL,
    
    -- Measurement details
    measurement_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    measurement_method VARCHAR(50) NOT NULL, -- BenefitMeasurementMethod enum
    measured_value DECIMAL(12,4) NOT NULL,
    measurement_unit VARCHAR(50) NOT NULL,
    measurement_accuracy DECIMAL(3,2) CHECK (measurement_accuracy >= 0.0 AND measurement_accuracy <= 1.0),
    
    -- Context and conditions
    measurement_conditions JSONB,
    sample_size INTEGER,
    location_details JSONB,
    
    -- Quality control
    validated BOOLEAN DEFAULT FALSE,
    validator_id VARCHAR(255),
    validation_notes TEXT,
    
    -- Metadata
    measurement_protocol VARCHAR(255),
    equipment_used TEXT[],
    technician_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key
    FOREIGN KEY (entry_id) REFERENCES benefit_quantification_entries(entry_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_entry_id (entry_id),
    INDEX idx_measurement_date (measurement_date),
    INDEX idx_measurement_method (measurement_method),
    INDEX idx_validated (validated)
);

-- ======================================================================
-- FIELD-LEVEL TRACKING TABLES
-- ======================================================================

-- Field-level benefit tracking aggregation
CREATE TABLE benefit_tracking_fields (
    tracking_id VARCHAR(255) PRIMARY KEY,
    farm_id VARCHAR(255) NOT NULL,
    field_id VARCHAR(255) NOT NULL,
    field_size_acres DECIMAL(8,2) NOT NULL CHECK (field_size_acres > 0),
    
    -- Implementation details
    cover_crop_species TEXT[] NOT NULL,
    implementation_year INTEGER NOT NULL CHECK (implementation_year >= 2020),
    implementation_season VARCHAR(20) NOT NULL,
    
    -- Aggregated benefits
    total_predicted_value DECIMAL(12,2) DEFAULT 0.0,
    total_realized_value DECIMAL(12,2),
    
    -- Performance metrics
    overall_prediction_accuracy DECIMAL(3,2) CHECK (overall_prediction_accuracy >= 0.0 AND overall_prediction_accuracy <= 1.0),
    roi_predicted DECIMAL(6,2),
    roi_actual DECIMAL(6,2),
    
    -- Historical comparison
    baseline_measurements JSONB,
    improvement_metrics JSONB,
    
    -- Tracking metadata
    tracking_started TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tracking_duration_months INTEGER,
    
    -- Indexes
    INDEX idx_farm_field_tracking (farm_id, field_id),
    INDEX idx_implementation_year (implementation_year),
    INDEX idx_tracking_started (tracking_started),
    
    -- Unique constraint
    UNIQUE (farm_id, field_id, implementation_year, implementation_season)
);

-- Link table between field tracking and benefit entries
CREATE TABLE field_tracking_benefits (
    tracking_id VARCHAR(255) NOT NULL,
    entry_id VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (tracking_id, entry_id),
    FOREIGN KEY (tracking_id) REFERENCES benefit_tracking_fields(tracking_id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id) REFERENCES benefit_quantification_entries(entry_id) ON DELETE CASCADE
);

-- ======================================================================
-- VALIDATION AND PROTOCOL TABLES
-- ======================================================================

-- Benefit validation protocols
CREATE TABLE benefit_validation_protocols (
    protocol_id VARCHAR(255) PRIMARY KEY,
    protocol_name VARCHAR(255) NOT NULL,
    benefit_type VARCHAR(50) NOT NULL,
    
    -- Validation requirements
    minimum_measurements INTEGER DEFAULT 3 CHECK (minimum_measurements >= 1),
    measurement_frequency VARCHAR(50) NOT NULL,
    measurement_duration_months INTEGER DEFAULT 12 CHECK (measurement_duration_months >= 1),
    
    -- Quality standards
    required_accuracy DECIMAL(3,2) DEFAULT 0.90 CHECK (required_accuracy >= 0.0 AND required_accuracy <= 1.0),
    acceptable_variance DECIMAL(3,2) DEFAULT 0.15 CHECK (acceptable_variance >= 0.0),
    expert_validation_required BOOLEAN DEFAULT TRUE,
    
    -- Measurement specifications
    preferred_methods TEXT[], -- BenefitMeasurementMethod enum values
    required_equipment TEXT[],
    sampling_requirements JSONB,
    
    -- Environmental considerations
    measurement_season_constraints TEXT[],
    weather_constraints JSONB,
    
    -- Documentation requirements
    required_documentation TEXT[],
    photo_documentation_required BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_benefit_type_protocol (benefit_type),
    INDEX idx_protocol_name (protocol_name)
);

-- ======================================================================
-- ANALYTICS AND REPORTING TABLES
-- ======================================================================

-- Benefit tracking analytics snapshots
CREATE TABLE benefit_tracking_analytics (
    analytics_id VARCHAR(255) PRIMARY KEY,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    analysis_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Scope
    farm_ids TEXT[] NOT NULL,
    field_count INTEGER NOT NULL CHECK (field_count >= 0),
    total_acres_analyzed DECIMAL(10,2) NOT NULL CHECK (total_acres_analyzed >= 0),
    
    -- Benefit performance summary
    benefit_accuracy_by_type JSONB,
    top_performing_benefits JSONB,
    underperforming_benefits JSONB,
    
    -- Economic insights
    total_predicted_value DECIMAL(15,2) DEFAULT 0.0,
    total_realized_value DECIMAL(15,2) DEFAULT 0.0,
    average_roi DECIMAL(6,2) DEFAULT 0.0,
    cost_benefit_distribution JSONB,
    
    -- Species performance
    species_performance_ranking JSONB,
    species_benefit_specialization JSONB,
    
    -- Timing and seasonal insights
    seasonal_benefit_patterns JSONB,
    optimal_measurement_timing JSONB,
    
    -- Recommendations
    measurement_protocol_improvements TEXT[],
    prediction_model_refinements TEXT[],
    farmer_recommendations TEXT[],
    
    -- Quality metrics
    overall_data_quality_score DECIMAL(3,2) CHECK (overall_data_quality_score >= 0.0 AND overall_data_quality_score <= 1.0),
    measurement_completion_rate DECIMAL(3,2) CHECK (measurement_completion_rate >= 0.0 AND measurement_completion_rate <= 1.0),
    validation_completion_rate DECIMAL(3,2) CHECK (validation_completion_rate >= 0.0 AND validation_completion_rate <= 1.0),
    
    -- Indexes
    INDEX idx_analysis_period (analysis_period_start, analysis_period_end),
    INDEX idx_generated_at (generated_at)
);

-- ======================================================================
-- BENEFIT REALIZATION TIMELINE TABLE
-- ======================================================================

-- Track benefit realization over time
CREATE TABLE benefit_realization_timeline (
    timeline_id VARCHAR(255) PRIMARY KEY,
    entry_id VARCHAR(255) NOT NULL,
    
    -- Timeline data
    timeline_date TIMESTAMP WITH TIME ZONE NOT NULL,
    realization_stage VARCHAR(50) NOT NULL, -- establishment, development, maturity, termination
    benefit_realization_percent DECIMAL(5,2) CHECK (benefit_realization_percent >= 0.0 AND benefit_realization_percent <= 100.0),
    
    -- Measurement details
    measured_indicator VARCHAR(100),
    measured_value DECIMAL(12,4),
    measurement_unit VARCHAR(50),
    
    -- Context
    growth_stage VARCHAR(50),
    environmental_conditions JSONB,
    management_actions TEXT[],
    
    -- Notes
    observations TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (entry_id) REFERENCES benefit_quantification_entries(entry_id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_timeline_entry (entry_id),
    INDEX idx_timeline_date (timeline_date),
    INDEX idx_realization_stage (realization_stage)
);

-- ======================================================================
-- VIEWS FOR COMMON QUERIES
-- ======================================================================

-- Complete benefit tracking view with measurements
CREATE VIEW benefit_tracking_complete AS
SELECT 
    bqe.entry_id,
    bqe.farm_id,
    bqe.field_id,
    bqe.cover_crop_implementation_id,
    bqe.benefit_type,
    bqe.benefit_category,
    bqe.predicted_value,
    bqe.predicted_unit,
    bqe.predicted_confidence,
    bqe.validated_value,
    bqe.economic_value_predicted,
    bqe.economic_value_actual,
    bqe.prediction_accuracy,
    bqe.status,
    COUNT(bmr.record_id) as measurement_count,
    AVG(bmr.measured_value) as avg_measured_value,
    MAX(bmr.measurement_date) as last_measurement_date
FROM benefit_quantification_entries bqe
LEFT JOIN benefit_measurement_records bmr ON bqe.entry_id = bmr.entry_id
GROUP BY bqe.entry_id, bqe.farm_id, bqe.field_id, bqe.cover_crop_implementation_id,
         bqe.benefit_type, bqe.benefit_category, bqe.predicted_value, bqe.predicted_unit,
         bqe.predicted_confidence, bqe.validated_value, bqe.economic_value_predicted,
         bqe.economic_value_actual, bqe.prediction_accuracy, bqe.status;

-- Field performance summary view
CREATE VIEW field_performance_summary AS
SELECT 
    btf.tracking_id,
    btf.farm_id,
    btf.field_id,
    btf.field_size_acres,
    btf.implementation_year,
    btf.implementation_season,
    btf.total_predicted_value,
    btf.total_realized_value,
    btf.roi_predicted,
    btf.roi_actual,
    btf.overall_prediction_accuracy,
    COUNT(ftb.entry_id) as tracked_benefit_count,
    COUNT(CASE WHEN bqe.status = 'validated' THEN 1 END) as validated_benefit_count,
    AVG(bqe.prediction_accuracy) as avg_prediction_accuracy
FROM benefit_tracking_fields btf
LEFT JOIN field_tracking_benefits ftb ON btf.tracking_id = ftb.tracking_id
LEFT JOIN benefit_quantification_entries bqe ON ftb.entry_id = bqe.entry_id
GROUP BY btf.tracking_id, btf.farm_id, btf.field_id, btf.field_size_acres,
         btf.implementation_year, btf.implementation_season, btf.total_predicted_value,
         btf.total_realized_value, btf.roi_predicted, btf.roi_actual, btf.overall_prediction_accuracy;

-- ======================================================================
-- FUNCTIONS AND TRIGGERS
-- ======================================================================

-- Function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_benefit_quantification_entries_updated_at
    BEFORE UPDATE ON benefit_quantification_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_benefit_tracking_fields_updated_at
    BEFORE UPDATE ON benefit_tracking_fields
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_benefit_validation_protocols_updated_at
    BEFORE UPDATE ON benefit_validation_protocols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate field-level aggregations
CREATE OR REPLACE FUNCTION update_field_tracking_aggregations()
RETURNS TRIGGER AS $$
BEGIN
    -- Update total predicted value
    UPDATE benefit_tracking_fields 
    SET total_predicted_value = (
        SELECT COALESCE(SUM(bqe.economic_value_predicted), 0)
        FROM field_tracking_benefits ftb
        JOIN benefit_quantification_entries bqe ON ftb.entry_id = bqe.entry_id
        WHERE ftb.tracking_id = NEW.tracking_id
    ),
    total_realized_value = (
        SELECT COALESCE(SUM(bqe.economic_value_actual), 0)
        FROM field_tracking_benefits ftb
        JOIN benefit_quantification_entries bqe ON ftb.entry_id = bqe.entry_id
        WHERE ftb.tracking_id = NEW.tracking_id
        AND bqe.economic_value_actual IS NOT NULL
    ),
    overall_prediction_accuracy = (
        SELECT AVG(bqe.prediction_accuracy)
        FROM field_tracking_benefits ftb
        JOIN benefit_quantification_entries bqe ON ftb.entry_id = bqe.entry_id
        WHERE ftb.tracking_id = NEW.tracking_id
        AND bqe.prediction_accuracy IS NOT NULL
    )
    WHERE tracking_id = NEW.tracking_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update field aggregations when benefits are added
CREATE TRIGGER update_field_aggregations_on_benefit_link
    AFTER INSERT ON field_tracking_benefits
    FOR EACH ROW EXECUTE FUNCTION update_field_tracking_aggregations();

-- ======================================================================
-- INDEXES FOR PERFORMANCE
-- ======================================================================

-- Composite indexes for common query patterns
CREATE INDEX idx_benefit_farm_field_type ON benefit_quantification_entries (farm_id, field_id, benefit_type);
CREATE INDEX idx_benefit_status_date ON benefit_quantification_entries (status, prediction_date);
CREATE INDEX idx_measurement_entry_date ON benefit_measurement_records (entry_id, measurement_date);
CREATE INDEX idx_field_tracking_year_season ON benefit_tracking_fields (implementation_year, implementation_season);

-- Partial indexes for validated records
CREATE INDEX idx_validated_benefits ON benefit_quantification_entries (entry_id) WHERE status = 'validated';
CREATE INDEX idx_validated_measurements ON benefit_measurement_records (entry_id) WHERE validated = TRUE;

-- ======================================================================
-- SAMPLE DATA INSERTION (FOR TESTING)
-- ======================================================================

-- Insert sample validation protocols
INSERT INTO benefit_validation_protocols (
    protocol_id, protocol_name, benefit_type, minimum_measurements, measurement_frequency,
    preferred_methods, expert_validation_required
) VALUES 
('nfix_protocol_v1', 'Nitrogen Fixation Validation Protocol', 'nitrogen_fixation', 3, 'monthly',
 ARRAY['soil_sampling', 'laboratory_analysis', 'biomass_measurement'], TRUE),
('erosion_protocol_v1', 'Erosion Control Validation Protocol', 'erosion_control', 2, 'quarterly',
 ARRAY['erosion_monitoring', 'field_observation'], TRUE),
('weed_protocol_v1', 'Weed Suppression Validation Protocol', 'weed_suppression', 4, 'monthly',
 ARRAY['weed_density_count', 'field_observation'], FALSE);

-- Create initial database user and permissions
-- CREATE USER benefit_tracking_user WITH PASSWORD 'secure_password_here';
-- GRANT USAGE ON SCHEMA benefit_tracking TO benefit_tracking_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA benefit_tracking TO benefit_tracking_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA benefit_tracking TO benefit_tracking_user;