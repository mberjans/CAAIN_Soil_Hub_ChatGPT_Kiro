-- Agricultural Validation Database Schema
-- This migration creates tables for agricultural validation, expert review management, and metrics tracking

-- Validation Results Table
CREATE TABLE validation_results (
    id SERIAL PRIMARY KEY,
    validation_id UUID UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'expert_review_required')),
    overall_score DECIMAL(3,2) NOT NULL CHECK (overall_score >= 0.0 AND overall_score <= 1.0),
    issues JSONB NOT NULL DEFAULT '[]',
    expert_review_required BOOLEAN NOT NULL DEFAULT FALSE,
    validation_timestamp TIMESTAMP NOT NULL,
    validation_duration_ms DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    regional_context JSONB NOT NULL DEFAULT '{}',
    crop_context JSONB NOT NULL DEFAULT '{}',
    expert_review_status VARCHAR(20) CHECK (expert_review_status IN ('pending', 'approved', 'rejected', 'needs_revision', 'expert_consultation')),
    expert_feedback TEXT,
    expert_reviewer_id UUID,
    expert_review_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Expert Reviewers Table
CREATE TABLE expert_reviewers (
    id SERIAL PRIMARY KEY,
    reviewer_id UUID UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    credentials VARCHAR(500) NOT NULL,
    specialization JSONB NOT NULL DEFAULT '[]',
    region VARCHAR(100) NOT NULL,
    institution VARCHAR(200) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    review_count INTEGER NOT NULL DEFAULT 0,
    average_rating DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (average_rating >= 0.0 AND average_rating <= 1.0),
    created_at TIMESTAMP DEFAULT NOW(),
    last_review_at TIMESTAMP
);

-- Expert Reviews Table
CREATE TABLE expert_reviews (
    id SERIAL PRIMARY KEY,
    review_id UUID UNIQUE NOT NULL,
    validation_id UUID NOT NULL REFERENCES validation_results(validation_id),
    reviewer_id UUID NOT NULL REFERENCES expert_reviewers(reviewer_id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'approved', 'rejected', 'needs_revision', 'expert_consultation')),
    review_score DECIMAL(3,2) NOT NULL CHECK (review_score >= 0.0 AND review_score <= 1.0),
    agricultural_soundness DECIMAL(3,2) NOT NULL CHECK (agricultural_soundness >= 0.0 AND agricultural_soundness <= 1.0),
    regional_applicability DECIMAL(3,2) NOT NULL CHECK (regional_applicability >= 0.0 AND regional_applicability <= 1.0),
    economic_feasibility DECIMAL(3,2) NOT NULL CHECK (economic_feasibility >= 0.0 AND economic_feasibility <= 1.0),
    farmer_practicality DECIMAL(3,2) NOT NULL CHECK (farmer_practicality >= 0.0 AND farmer_practicality <= 1.0),
    comments TEXT NOT NULL,
    recommendations JSONB NOT NULL DEFAULT '[]',
    concerns JSONB NOT NULL DEFAULT '[]',
    approval_conditions JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Review Assignments Table
CREATE TABLE review_assignments (
    id SERIAL PRIMARY KEY,
    assignment_id UUID UNIQUE NOT NULL,
    validation_id UUID NOT NULL REFERENCES validation_results(validation_id),
    reviewer_id UUID NOT NULL REFERENCES expert_reviewers(reviewer_id),
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'overdue', 'cancelled')),
    assigned_at TIMESTAMP NOT NULL,
    due_date TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    review_notes TEXT,
    escalation_reason TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Expert Review Workflows Table
CREATE TABLE expert_review_workflows (
    id SERIAL PRIMARY KEY,
    workflow_id UUID UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    region VARCHAR(100) NOT NULL,
    crop_types JSONB NOT NULL DEFAULT '[]',
    required_specializations JSONB NOT NULL DEFAULT '[]',
    review_criteria JSONB NOT NULL DEFAULT '{}',
    auto_assignment_rules JSONB NOT NULL DEFAULT '{}',
    escalation_rules JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Farmer Feedback Table
CREATE TABLE farmer_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id UUID UNIQUE NOT NULL,
    recommendation_id UUID NOT NULL,
    farmer_id UUID NOT NULL,
    satisfaction_score DECIMAL(3,2) NOT NULL CHECK (satisfaction_score >= 0.0 AND satisfaction_score <= 1.0),
    feedback TEXT,
    recommendation_accuracy DECIMAL(3,2) CHECK (recommendation_accuracy >= 0.0 AND recommendation_accuracy <= 1.0),
    implementation_ease DECIMAL(3,2) CHECK (implementation_ease >= 0.0 AND implementation_ease <= 1.0),
    economic_outcome DECIMAL(3,2) CHECK (economic_outcome >= 0.0 AND economic_outcome <= 1.0),
    additional_comments TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Validation Metrics Reports Table
CREATE TABLE validation_metrics_reports (
    id SERIAL PRIMARY KEY,
    report_id UUID UNIQUE NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    
    -- Validation metrics
    total_validations INTEGER NOT NULL DEFAULT 0,
    successful_validations INTEGER NOT NULL DEFAULT 0,
    failed_validations INTEGER NOT NULL DEFAULT 0,
    validation_success_rate DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (validation_success_rate >= 0.0 AND validation_success_rate <= 1.0),
    average_validation_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (average_validation_score >= 0.0 AND average_validation_score <= 1.0),
    average_validation_duration_ms DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    
    -- Expert review metrics
    expert_reviews_required INTEGER NOT NULL DEFAULT 0,
    expert_reviews_completed INTEGER NOT NULL DEFAULT 0,
    expert_reviews_pending INTEGER NOT NULL DEFAULT 0,
    expert_reviews_overdue INTEGER NOT NULL DEFAULT 0,
    expert_review_completion_rate DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (expert_review_completion_rate >= 0.0 AND expert_review_completion_rate <= 1.0),
    average_expert_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (average_expert_score >= 0.0 AND average_expert_score <= 1.0),
    average_expert_review_duration_hours DECIMAL(8,2) NOT NULL DEFAULT 0.0,
    
    -- Quality metrics
    agricultural_soundness_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (agricultural_soundness_score >= 0.0 AND agricultural_soundness_score <= 1.0),
    regional_applicability_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (regional_applicability_score >= 0.0 AND regional_applicability_score <= 1.0),
    economic_feasibility_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (economic_feasibility_score >= 0.0 AND economic_feasibility_score <= 1.0),
    farmer_practicality_score DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (farmer_practicality_score >= 0.0 AND farmer_practicality_score <= 1.0),
    
    -- Coverage metrics
    regional_coverage JSONB NOT NULL DEFAULT '{}',
    crop_coverage JSONB NOT NULL DEFAULT '{}',
    
    -- Farmer satisfaction
    farmer_feedback_count INTEGER NOT NULL DEFAULT 0,
    average_farmer_satisfaction DECIMAL(3,2) NOT NULL DEFAULT 0.0 CHECK (average_farmer_satisfaction >= 0.0 AND average_farmer_satisfaction <= 1.0),
    farmer_satisfaction_distribution JSONB NOT NULL DEFAULT '{}',
    
    -- Performance trends
    validation_trend VARCHAR(20) NOT NULL DEFAULT 'stable' CHECK (validation_trend IN ('improving', 'stable', 'declining')),
    expert_review_trend VARCHAR(20) NOT NULL DEFAULT 'stable' CHECK (expert_review_trend IN ('improving', 'stable', 'declining')),
    farmer_satisfaction_trend VARCHAR(20) NOT NULL DEFAULT 'stable' CHECK (farmer_satisfaction_trend IN ('improving', 'stable', 'declining')),
    
    -- Issues and concerns
    common_validation_issues JSONB NOT NULL DEFAULT '[]',
    expert_concerns JSONB NOT NULL DEFAULT '[]',
    farmer_complaints JSONB NOT NULL DEFAULT '[]',
    
    -- Recommendations
    improvement_recommendations JSONB NOT NULL DEFAULT '[]',
    
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX idx_validation_results_validation_id ON validation_results(validation_id);
CREATE INDEX idx_validation_results_status ON validation_results(status);
CREATE INDEX idx_validation_results_timestamp ON validation_results(validation_timestamp);
CREATE INDEX idx_validation_results_expert_review_required ON validation_results(expert_review_required);

CREATE INDEX idx_expert_reviewers_reviewer_id ON expert_reviewers(reviewer_id);
CREATE INDEX idx_expert_reviewers_region ON expert_reviewers(region);
CREATE INDEX idx_expert_reviewers_active ON expert_reviewers(is_active);
CREATE INDEX idx_expert_reviewers_specialization ON expert_reviewers USING GIN(specialization);

CREATE INDEX idx_expert_reviews_review_id ON expert_reviews(review_id);
CREATE INDEX idx_expert_reviews_validation_id ON expert_reviews(validation_id);
CREATE INDEX idx_expert_reviews_reviewer_id ON expert_reviews(reviewer_id);
CREATE INDEX idx_expert_reviews_status ON expert_reviews(status);
CREATE INDEX idx_expert_reviews_created_at ON expert_reviews(created_at);

CREATE INDEX idx_review_assignments_assignment_id ON review_assignments(assignment_id);
CREATE INDEX idx_review_assignments_validation_id ON review_assignments(validation_id);
CREATE INDEX idx_review_assignments_reviewer_id ON review_assignments(reviewer_id);
CREATE INDEX idx_review_assignments_status ON review_assignments(status);
CREATE INDEX idx_review_assignments_due_date ON review_assignments(due_date);
CREATE INDEX idx_review_assignments_priority ON review_assignments(priority);

CREATE INDEX idx_expert_review_workflows_workflow_id ON expert_review_workflows(workflow_id);
CREATE INDEX idx_expert_review_workflows_region ON expert_review_workflows(region);
CREATE INDEX idx_expert_review_workflows_active ON expert_review_workflows(is_active);
CREATE INDEX idx_expert_review_workflows_crop_types ON expert_review_workflows USING GIN(crop_types);

CREATE INDEX idx_farmer_feedback_feedback_id ON farmer_feedback(feedback_id);
CREATE INDEX idx_farmer_feedback_recommendation_id ON farmer_feedback(recommendation_id);
CREATE INDEX idx_farmer_feedback_farmer_id ON farmer_feedback(farmer_id);
CREATE INDEX idx_farmer_feedback_created_at ON farmer_feedback(created_at);
CREATE INDEX idx_farmer_feedback_satisfaction_score ON farmer_feedback(satisfaction_score);

CREATE INDEX idx_validation_metrics_reports_report_id ON validation_metrics_reports(report_id);
CREATE INDEX idx_validation_metrics_reports_period ON validation_metrics_reports(period_start, period_end);
CREATE INDEX idx_validation_metrics_reports_period_type ON validation_metrics_reports(period_type);
CREATE INDEX idx_validation_metrics_reports_generated_at ON validation_metrics_reports(generated_at);

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_validation_results_updated_at BEFORE UPDATE ON validation_results FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expert_reviews_updated_at BEFORE UPDATE ON expert_reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_review_assignments_updated_at BEFORE UPDATE ON review_assignments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_expert_review_workflows_updated_at BEFORE UPDATE ON expert_review_workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW active_expert_reviewers AS
SELECT 
    reviewer_id,
    name,
    credentials,
    specialization,
    region,
    institution,
    contact_email,
    review_count,
    average_rating,
    last_review_at
FROM expert_reviewers
WHERE is_active = TRUE;

CREATE VIEW pending_expert_reviews AS
SELECT 
    ra.assignment_id,
    ra.validation_id,
    ra.reviewer_id,
    er.name as reviewer_name,
    er.region,
    ra.priority,
    ra.assigned_at,
    ra.due_date,
    EXTRACT(EPOCH FROM (ra.due_date - NOW())) / 3600 as hours_until_due
FROM review_assignments ra
JOIN expert_reviewers er ON ra.reviewer_id = er.reviewer_id
WHERE ra.status IN ('pending', 'assigned', 'in_progress')
ORDER BY ra.priority DESC, ra.due_date ASC;

CREATE VIEW validation_summary_stats AS
SELECT 
    COUNT(*) as total_validations,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_validations,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_validations,
    COUNT(CASE WHEN expert_review_required = TRUE THEN 1 END) as expert_reviews_required,
    AVG(overall_score) as average_validation_score,
    AVG(validation_duration_ms) as average_validation_duration_ms
FROM validation_results
WHERE validation_timestamp >= NOW() - INTERVAL '30 days';

-- Comments for documentation
COMMENT ON TABLE validation_results IS 'Stores results of agricultural validation processes';
COMMENT ON TABLE expert_reviewers IS 'Profiles of expert agricultural reviewers';
COMMENT ON TABLE expert_reviews IS 'Expert review assessments of agricultural recommendations';
COMMENT ON TABLE review_assignments IS 'Assignments of validation reviews to expert reviewers';
COMMENT ON TABLE expert_review_workflows IS 'Workflow configurations for expert review processes';
COMMENT ON TABLE farmer_feedback IS 'Farmer feedback on agricultural recommendations';
COMMENT ON TABLE validation_metrics_reports IS 'Comprehensive validation performance metrics reports';

COMMENT ON COLUMN validation_results.overall_score IS 'Overall validation score from 0.0 to 1.0';
COMMENT ON COLUMN validation_results.issues IS 'JSON array of validation issues found';
COMMENT ON COLUMN validation_results.regional_context IS 'JSON object containing regional context data';
COMMENT ON COLUMN validation_results.crop_context IS 'JSON object containing crop-specific context data';

COMMENT ON COLUMN expert_reviewers.specialization IS 'JSON array of expert specializations';
COMMENT ON COLUMN expert_reviewers.average_rating IS 'Average rating from farmers (0.0 to 1.0)';

COMMENT ON COLUMN expert_reviews.review_score IS 'Overall expert review score (0.0 to 1.0)';
COMMENT ON COLUMN expert_reviews.agricultural_soundness IS 'Agricultural soundness rating (0.0 to 1.0)';
COMMENT ON COLUMN expert_reviews.regional_applicability IS 'Regional applicability rating (0.0 to 1.0)';
COMMENT ON COLUMN expert_reviews.economic_feasibility IS 'Economic feasibility rating (0.0 to 1.0)';
COMMENT ON COLUMN expert_reviews.farmer_practicality IS 'Farmer practicality rating (0.0 to 1.0)';

COMMENT ON COLUMN review_assignments.priority IS 'Review priority: low, normal, high, urgent';
COMMENT ON COLUMN review_assignments.status IS 'Assignment status: pending, assigned, in_progress, completed, overdue, cancelled';

COMMENT ON COLUMN farmer_feedback.satisfaction_score IS 'Farmer satisfaction score (0.0 to 1.0)';
COMMENT ON COLUMN farmer_feedback.recommendation_accuracy IS 'Perceived recommendation accuracy (0.0 to 1.0)';
COMMENT ON COLUMN farmer_feedback.implementation_ease IS 'Implementation ease rating (0.0 to 1.0)';
COMMENT ON COLUMN farmer_feedback.economic_outcome IS 'Economic outcome rating (0.0 to 1.0)';