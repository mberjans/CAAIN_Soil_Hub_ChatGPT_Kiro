-- Migration: Create Image Analysis Schema
-- Version: 003
-- Date: December 2024
-- Description: Creates tables for image analysis and deficiency detection
-- Job: JOB3-003.4.impl

-- Enable UUID extension if not already enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        RAISE NOTICE 'Enabled uuid-ossp extension';
    END IF;
END
$$;

-- Check if image_analyses table needs to be created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'image_analyses'
    ) THEN
        -- Create image_analyses table
        CREATE TABLE image_analyses (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            image_path VARCHAR(512) NOT NULL,
            crop_type VARCHAR(100) NOT NULL,
            growth_stage VARCHAR(50),
            image_size_mb DECIMAL(10, 2),
            upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            processing_status VARCHAR(50) DEFAULT 'pending' NOT NULL,
            quality_score DECIMAL(3, 2),
            original_filename VARCHAR(255),
            image_format VARCHAR(10),
            image_width_pixels INTEGER,
            image_height_pixels INTEGER,
            model_version VARCHAR(20),
            image_quality_metrics JSONB,
            analysis_metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            -- Constraints
            CONSTRAINT check_processing_status CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
            CONSTRAINT check_quality_score_range CHECK (quality_score >= 0 AND quality_score <= 1),
            CONSTRAINT check_positive_image_size CHECK (image_size_mb > 0)
        );

        RAISE NOTICE 'Created image_analyses table';
    ELSE
        RAISE NOTICE 'image_analyses table already exists, skipping';
    END IF;
END
$$;

-- Check if deficiency_detections table needs to be created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'deficiency_detections'
    ) THEN
        -- Create deficiency_detections table
        CREATE TABLE deficiency_detections (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            image_analysis_id UUID NOT NULL REFERENCES image_analyses(id) ON DELETE CASCADE,
            nutrient VARCHAR(50) NOT NULL,
            confidence_score DECIMAL(3, 2) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            affected_area_percent DECIMAL(5, 2),
            symptoms_detected JSONB,
            symptom_indicators JSONB,
            affected_regions JSONB,
            color_analysis JSONB,
            pattern_analysis JSONB,
            deficiency_type VARCHAR(30),
            severity_score DECIMAL(3, 2),
            deficiency_probability DECIMAL(3, 2),
            model_version VARCHAR(20),
            model_confidence_metrics JSONB,
            expert_validated BOOLEAN DEFAULT FALSE,
            validation_notes TEXT,
            validation_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

            -- Constraints
            CONSTRAINT check_confidence_score_range CHECK (confidence_score >= 0 AND confidence_score <= 1),
            CONSTRAINT check_affected_area_range CHECK (affected_area_percent >= 0 AND affected_area_percent <= 100),
            CONSTRAINT check_severity_values CHECK (severity IN ('mild', 'moderate', 'severe')),
            CONSTRAINT check_severity_score_range CHECK (severity_score >= 0 AND severity_score <= 1),
            CONSTRAINT check_deficiency_probability_range CHECK (deficiency_probability >= 0 AND deficiency_probability <= 1)
        );

        RAISE NOTICE 'Created deficiency_detections table';
    ELSE
        RAISE NOTICE 'deficiency_detections table already exists, skipping';
    END IF;
END
$$;

-- Create indexes if they don't exist
DO $$
BEGIN
    -- Image Analyses indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_image_analyses_crop_type') THEN
        CREATE INDEX idx_image_analyses_crop_type ON image_analyses(crop_type);
        RAISE NOTICE 'Created index idx_image_analyses_crop_type';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_image_analyses_status') THEN
        CREATE INDEX idx_image_analyses_status ON image_analyses(processing_status);
        RAISE NOTICE 'Created index idx_image_analyses_status';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_image_analyses_upload_time') THEN
        CREATE INDEX idx_image_analyses_upload_time ON image_analyses(upload_timestamp);
        RAISE NOTICE 'Created index idx_image_analyses_upload_time';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_image_analyses_image_path') THEN
        CREATE INDEX idx_image_analyses_image_path ON image_analyses(image_path);
        RAISE NOTICE 'Created index idx_image_analyses_image_path';
    END IF;

    -- Deficiency Detections indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_deficiency_detections_analysis') THEN
        CREATE INDEX idx_deficiency_detections_analysis ON deficiency_detections(image_analysis_id);
        RAISE NOTICE 'Created index idx_deficiency_detections_analysis';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_deficiency_detections_nutrient') THEN
        CREATE INDEX idx_deficiency_detections_nutrient ON deficiency_detections(nutrient);
        RAISE NOTICE 'Created index idx_deficiency_detections_nutrient';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_deficiency_detections_severity') THEN
        CREATE INDEX idx_deficiency_detections_severity ON deficiency_detections(severity);
        RAISE NOTICE 'Created index idx_deficiency_detections_severity';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_deficiency_detections_confidence') THEN
        CREATE INDEX idx_deficiency_detections_confidence ON deficiency_detections(confidence_score);
        RAISE NOTICE 'Created index idx_deficiency_detections_confidence';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_deficiency_detections_expert_validated') THEN
        CREATE INDEX idx_deficiency_detections_expert_validated ON deficiency_detections(expert_validated);
        RAISE NOTICE 'Created index idx_deficiency_detections_expert_validated';
    END IF;
END
$$;

-- Create triggers for updated_at columns
DO $$
BEGIN
    -- Create trigger function if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $trigger$ language 'plpgsql';

        RAISE NOTICE 'Created update_updated_at_column function';
    END IF;

    -- Add triggers if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_image_analyses_updated_at') THEN
        CREATE TRIGGER update_image_analyses_updated_at
            BEFORE UPDATE ON image_analyses
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_image_analyses_updated_at';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_deficiency_detections_updated_at') THEN
        CREATE TRIGGER update_deficiency_detections_updated_at
            BEFORE UPDATE ON deficiency_detections
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_deficiency_detections_updated_at';
    END IF;
END
$$;

-- Add comments for documentation
COMMENT ON TABLE image_analyses IS 'Image analysis metadata and processing status for crop deficiency detection';
COMMENT ON COLUMN image_analyses.image_path IS 'Path to the stored image file';
COMMENT ON COLUMN image_analyses.crop_type IS 'Type of crop (corn, soybean, wheat, etc.)';
COMMENT ON COLUMN image_analyses.growth_stage IS 'Growth stage of the crop when image was taken';
COMMENT ON COLUMN image_analyses.processing_status IS 'Current processing status: pending, processing, completed, failed';
COMMENT ON COLUMN image_analyses.quality_score IS 'Overall image quality score (0-1)';
COMMENT ON COLUMN image_analyses.image_quality_metrics IS 'Detailed quality assessment metrics in JSON format';
COMMENT ON COLUMN image_analyses.analysis_metadata IS 'Additional analysis metadata in JSON format';

COMMENT ON TABLE deficiency_detections IS 'Detailed results of nutrient deficiency detection from image analysis';
COMMENT ON COLUMN deficiency_detections.image_analysis_id IS 'Foreign key to the associated image analysis';
COMMENT ON COLUMN deficiency_detections.nutrient IS 'Nutrient name (nitrogen, phosphorus, potassium, etc.)';
COMMENT ON COLUMN deficiency_detections.confidence_score IS 'Detection confidence score (0-1)';
COMMENT ON COLUMN deficiency_detections.severity IS 'Severity level: mild, moderate, severe';
COMMENT ON COLUMN deficiency_detections.affected_area_percent IS 'Estimated percentage of plant affected';
COMMENT ON COLUMN deficiency_detections.symptoms_detected IS 'List of detected symptoms in JSON format';
COMMENT ON COLUMN deficiency_detections.symptom_indicators IS 'Detailed symptom analysis indicators in JSON format';
COMMENT ON COLUMN deficiency_detections.affected_regions IS 'Regions of the image showing deficiency in JSON format';
COMMENT ON COLUMN deficiency_detections.color_analysis IS 'Color-based analysis results in JSON format';
COMMENT ON COLUMN deficiency_detections.pattern_analysis IS 'Pattern recognition results in JSON format';
COMMENT ON COLUMN deficiency_detections.deficiency_type IS 'Type of deficiency: primary, secondary, micronutrient';
COMMENT ON COLUMN deficiency_detections.severity_score IS 'Numerical severity score (0-1)';
COMMENT ON COLUMN deficiency_detections.deficiency_probability IS 'Overall probability of deficiency (0-1)';
COMMENT ON COLUMN deficiency_detections.expert_validated IS 'Whether this detection has been validated by an agricultural expert';
COMMENT ON COLUMN deficiency_detections.validation_notes IS 'Notes from expert validation';
COMMENT ON COLUMN deficiency_detections.validation_date IS 'Date when expert validation was performed';

-- Insert sample data for testing
DO $$
BEGIN
    -- Insert sample image analysis record if table is empty
    IF (SELECT COUNT(*) FROM image_analyses) = 0 THEN
        INSERT INTO image_analyses (
            id,
            image_path,
            crop_type,
            growth_stage,
            image_size_mb,
            processing_status,
            quality_score,
            original_filename,
            image_format,
            image_width_pixels,
            image_height_pixels,
            model_version
        ) VALUES (
            '550e8400-e29b-41d4-a716-446655440001',
            '/sample_images/corn_deficiency_test_1.jpg',
            'corn',
            'V6',
            2.4,
            'completed',
            0.85,
            'corn_deficiency_test_1.jpg',
            'jpg',
            1024,
            768,
            'v1.0'
        );

        RAISE NOTICE 'Inserted sample image analysis record';

        -- Insert sample deficiency detection record
        INSERT INTO deficiency_detections (
            id,
            image_analysis_id,
            nutrient,
            confidence_score,
            severity,
            affected_area_percent,
            symptoms_detected,
            deficiency_type,
            severity_score,
            deficiency_probability,
            model_version
        ) VALUES (
            '550e8400-e29b-41d4-a716-446655440002',
            '550e8400-e29b-41d4-a716-446655440001',
            'nitrogen',
            0.75,
            'moderate',
            35.5,
            '["Yellowing of older leaves", "Stunted growth", "Pale green color"]',
            'primary',
            0.65,
            0.75,
            'v1.0'
        );

        RAISE NOTICE 'Inserted sample deficiency detection record';
    ELSE
        RAISE NOTICE 'Sample data already exists, skipping inserts';
    END IF;
END
$$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 003_image_analysis_schema completed successfully';
    RAISE NOTICE 'JOB3-003.4.impl - Create migration SQL completed';
END
$$;