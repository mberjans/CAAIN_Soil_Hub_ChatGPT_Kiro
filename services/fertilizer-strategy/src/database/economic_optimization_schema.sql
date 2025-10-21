"""
Database Schema for Economic Optimization Service.

This SQL script creates the necessary database tables and indexes for storing
economic optimization results, scenario modeling data, and related analytics.
"""

-- Create economic optimization results table for performance
CREATE TABLE economic_optimization_results (
    id SERIAL PRIMARY KEY,
    analysis_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    farm_id UUID,
    field_id UUID,
    scenarios JSONB NOT NULL,
    optimization_results JSONB NOT NULL,
    risk_assessments JSONB NOT NULL,
    sensitivity_analysis JSONB NOT NULL,
    monte_carlo_simulation JSONB NOT NULL,
    budget_allocations JSONB NOT NULL,
    investment_priorities JSONB NOT NULL,
    recommendations JSONB NOT NULL,
    processing_time_ms DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_economic_optimization_analysis_id ON economic_optimization_results(analysis_id);
CREATE INDEX idx_economic_optimization_user_id ON economic_optimization_results(user_id);
CREATE INDEX idx_economic_optimization_farm_id ON economic_optimization_results(farm_id);
CREATE INDEX idx_economic_optimization_field_id ON economic_optimization_results(field_id);
CREATE INDEX idx_economic_optimization_created_at ON economic_optimization_results(created_at);

-- Create hypertable for time series optimization (if using TimescaleDB)
-- SELECT create_hypertable('economic_optimization_results', 'created_at');

-- Create economic scenario modeling table
CREATE TABLE economic_scenarios (
    id SERIAL PRIMARY KEY,
    scenario_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    scenario_name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(50) NOT NULL,
    market_condition VARCHAR(50) NOT NULL,
    fertilizer_prices JSONB NOT NULL,
    crop_prices JSONB NOT NULL,
    scenario_metrics JSONB NOT NULL,
    probability_distribution JSONB NOT NULL,
    risk_assessment JSONB NOT NULL,
    description TEXT,
    assumptions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic scenarios
CREATE INDEX idx_economic_scenarios_scenario_id ON economic_scenarios(scenario_id);
CREATE INDEX idx_economic_scenarios_analysis_id ON economic_scenarios(analysis_id);
CREATE INDEX idx_economic_scenarios_scenario_type ON economic_scenarios(scenario_type);
CREATE INDEX idx_economic_scenarios_market_condition ON economic_scenarios(market_condition);
CREATE INDEX idx_economic_scenarios_created_at ON economic_scenarios(created_at);

-- Create multi-objective optimization results table
CREATE TABLE multi_objective_optimization_results (
    id SERIAL PRIMARY KEY,
    optimization_id UUID UNIQUE NOT NULL,
    scenario_id UUID NOT NULL REFERENCES economic_scenarios(scenario_id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    base_optimization JSONB NOT NULL,
    weighted_optimization JSONB,
    constraint_optimization JSONB,
    risk_adjusted_optimization JSONB,
    objectives JSONB NOT NULL,
    constraints JSONB NOT NULL,
    optimization_methods JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for multi-objective optimization
CREATE INDEX idx_multi_objective_optimization_id ON multi_objective_optimization_results(optimization_id);
CREATE INDEX idx_multi_objective_scenario_id ON multi_objective_optimization_results(scenario_id);
CREATE INDEX idx_multi_objective_analysis_id ON multi_objective_optimization_results(analysis_id);
CREATE INDEX idx_multi_objective_created_at ON multi_objective_optimization_results(created_at);

-- Create risk assessment results table
CREATE TABLE risk_assessment_results (
    id SERIAL PRIMARY KEY,
    assessment_id UUID UNIQUE NOT NULL,
    scenario_id UUID NOT NULL REFERENCES economic_scenarios(scenario_id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    overall_risk_score DECIMAL(3,2) NOT NULL CHECK (overall_risk_score >= 0 AND overall_risk_score <= 1),
    risk_level VARCHAR(20) NOT NULL,
    individual_risks JSONB NOT NULL,
    mitigation_strategies JSONB NOT NULL,
    confidence_intervals JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for risk assessment
CREATE INDEX idx_risk_assessment_id ON risk_assessment_results(assessment_id);
CREATE INDEX idx_risk_assessment_scenario_id ON risk_assessment_results(scenario_id);
CREATE INDEX idx_risk_assessment_analysis_id ON risk_assessment_results(analysis_id);
CREATE INDEX idx_risk_assessment_risk_level ON risk_assessment_results(risk_level);
CREATE INDEX idx_risk_assessment_created_at ON risk_assessment_results(created_at);

-- Create sensitivity analysis results table
CREATE TABLE sensitivity_analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_id UUID UNIQUE NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    parameter_variations JSONB NOT NULL,
    sensitivity_results JSONB NOT NULL,
    critical_parameters JSONB NOT NULL,
    recommendations JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for sensitivity analysis
CREATE INDEX idx_sensitivity_analysis_id ON sensitivity_analysis_results(analysis_id);
CREATE INDEX idx_sensitivity_analysis_created_at ON sensitivity_analysis_results(created_at);

-- Create Monte Carlo simulation results table
CREATE TABLE monte_carlo_simulation_results (
    id SERIAL PRIMARY KEY,
    simulation_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    iterations INTEGER NOT NULL,
    confidence_levels JSONB NOT NULL,
    scenario_results JSONB NOT NULL,
    overall_statistics JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for Monte Carlo simulation
CREATE INDEX idx_monte_carlo_simulation_id ON monte_carlo_simulation_results(simulation_id);
CREATE INDEX idx_monte_carlo_analysis_id ON monte_carlo_simulation_results(analysis_id);
CREATE INDEX idx_monte_carlo_created_at ON monte_carlo_simulation_results(created_at);

-- Create budget allocation results table
CREATE TABLE budget_allocation_results (
    id SERIAL PRIMARY KEY,
    allocation_id UUID UNIQUE NOT NULL,
    optimization_id UUID NOT NULL REFERENCES multi_objective_optimization_results(optimization_id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    total_budget DECIMAL(12,2) NOT NULL,
    field_size_acres DECIMAL(10,2) NOT NULL,
    allocation_breakdown JSONB NOT NULL,
    per_acre_allocation DECIMAL(10,2) NOT NULL,
    budget_utilization DECIMAL(5,4) NOT NULL CHECK (budget_utilization >= 0 AND budget_utilization <= 1),
    remaining_budget DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for budget allocation
CREATE INDEX idx_budget_allocation_id ON budget_allocation_results(allocation_id);
CREATE INDEX idx_budget_optimization_id ON budget_allocation_results(optimization_id);
CREATE INDEX idx_budget_analysis_id ON budget_allocation_results(analysis_id);
CREATE INDEX idx_budget_created_at ON budget_allocation_results(created_at);

-- Create investment prioritization results table
CREATE TABLE investment_prioritization_results (
    id SERIAL PRIMARY KEY,
    priority_id UUID UNIQUE NOT NULL,
    optimization_id UUID NOT NULL REFERENCES multi_objective_optimization_results(optimization_id) ON DELETE CASCADE,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    priority_score DECIMAL(5,4) NOT NULL CHECK (priority_score >= 0 AND priority_score <= 1),
    priority_level VARCHAR(20) NOT NULL,
    investment_recommendations JSONB NOT NULL,
    risk_adjusted_return DECIMAL(12,2) NOT NULL,
    payback_period JSONB NOT NULL,
    opportunity_cost JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for investment prioritization
CREATE INDEX idx_investment_priority_id ON investment_prioritization_results(priority_id);
CREATE INDEX idx_investment_optimization_id ON investment_prioritization_results(optimization_id);
CREATE INDEX idx_investment_analysis_id ON investment_prioritization_results(analysis_id);
CREATE INDEX idx_investment_priority_level ON investment_prioritization_results(priority_level);
CREATE INDEX idx_investment_created_at ON investment_prioritization_results(created_at);

-- Create economic validation dataset table
CREATE TABLE economic_validation_datasets (
    id SERIAL PRIMARY KEY,
    dataset_id UUID UNIQUE NOT NULL,
    dataset_name VARCHAR(200) NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    validation_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic validation datasets
CREATE INDEX idx_economic_validation_dataset_id ON economic_validation_datasets(dataset_id);
CREATE INDEX idx_economic_validation_dataset_type ON economic_validation_datasets(dataset_type);
CREATE INDEX idx_economic_validation_created_at ON economic_validation_datasets(created_at);

-- Create economic optimization configuration table
CREATE TABLE economic_optimization_configurations (
    id SERIAL PRIMARY KEY,
    config_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    optimization_preferences JSONB NOT NULL,
    risk_tolerance VARCHAR(20) NOT NULL,
    budget_constraints JSONB,
    environmental_constraints JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization configurations
CREATE INDEX idx_economic_config_id ON economic_optimization_configurations(config_id);
CREATE INDEX idx_economic_config_user_id ON economic_optimization_configurations(user_id);
CREATE INDEX idx_economic_config_risk_tolerance ON economic_optimization_configurations(risk_tolerance);
CREATE INDEX idx_economic_config_created_at ON economic_optimization_configurations(created_at);

-- Create economic optimization history table
CREATE TABLE economic_optimization_history (
    id SERIAL PRIMARY KEY,
    history_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    optimization_type VARCHAR(100) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization history
CREATE INDEX idx_economic_history_id ON economic_optimization_history(history_id);
CREATE INDEX idx_economic_history_analysis_id ON economic_optimization_history(analysis_id);
CREATE INDEX idx_economic_history_user_id ON economic_optimization_history(user_id);
CREATE INDEX idx_economic_history_optimization_type ON economic_optimization_history(optimization_type);
CREATE INDEX idx_economic_history_created_at ON economic_optimization_history(created_at);

-- Create economic optimization feedback table
CREATE TABLE economic_optimization_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    feedback_value DECIMAL(5,2),
    feedback_text TEXT,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization feedback
CREATE INDEX idx_economic_feedback_id ON economic_optimization_feedback(feedback_id);
CREATE INDEX idx_economic_feedback_analysis_id ON economic_optimization_feedback(analysis_id);
CREATE INDEX idx_economic_feedback_user_id ON economic_optimization_feedback(user_id);
CREATE INDEX idx_economic_feedback_type ON economic_optimization_feedback(feedback_type);
CREATE INDEX idx_economic_feedback_created_at ON economic_optimization_feedback(created_at);

-- Create economic optimization analytics table
CREATE TABLE economic_optimization_analytics (
    id SERIAL PRIMARY KEY,
    analytics_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    processing_time_ms DECIMAL(10,2) NOT NULL,
    accuracy_score DECIMAL(5,2),
    user_satisfaction_score DECIMAL(5,2),
    implementation_success_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization analytics
CREATE INDEX idx_economic_analytics_id ON economic_optimization_analytics(analytics_id);
CREATE INDEX idx_economic_analytics_analysis_id ON economic_optimization_analytics(analysis_id);
CREATE INDEX idx_economic_analytics_user_id ON economic_optimization_analytics(user_id);
CREATE INDEX idx_economic_analytics_created_at ON economic_optimization_analytics(created_at);

-- Create economic optimization recommendations table
CREATE TABLE economic_optimization_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    recommendation_type VARCHAR(100) NOT NULL,
    recommendation_text TEXT NOT NULL,
    priority_level VARCHAR(20) NOT NULL,
    implementation_timeline_days INTEGER,
    estimated_cost DECIMAL(12,2),
    expected_benefit DECIMAL(12,2),
    roi_percent DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization recommendations
CREATE INDEX idx_economic_recommendations_id ON economic_optimization_recommendations(recommendation_id);
CREATE INDEX idx_economic_recommendations_analysis_id ON economic_optimization_recommendations(analysis_id);
CREATE INDEX idx_economic_recommendations_user_id ON economic_optimization_recommendations(user_id);
CREATE INDEX idx_economic_recommendations_type ON economic_optimization_recommendations(recommendation_type);
CREATE INDEX idx_economic_recommendations_priority ON economic_optimization_recommendations(priority_level);
CREATE INDEX idx_economic_recommendations_created_at ON economic_optimization_recommendations(created_at);

-- Create economic optimization scenario comparisons table
CREATE TABLE economic_scenario_comparisons (
    id SERIAL PRIMARY KEY,
    comparison_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    scenario_ids JSONB NOT NULL,
    comparison_metrics JSONB NOT NULL,
    best_scenario UUID,
    worst_scenario UUID,
    recommendations JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic scenario comparisons
CREATE INDEX idx_economic_comparison_id ON economic_scenario_comparisons(comparison_id);
CREATE INDEX idx_economic_comparison_analysis_id ON economic_scenario_comparisons(analysis_id);
CREATE INDEX idx_economic_comparison_created_at ON economic_scenario_comparisons(created_at);

-- Create economic optimization trend analysis table
CREATE TABLE economic_trend_analysis (
    id SERIAL PRIMARY KEY,
    trend_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    trend_type VARCHAR(50) NOT NULL,
    trend_data JSONB NOT NULL,
    trend_direction VARCHAR(20),
    confidence_level DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic trend analysis
CREATE INDEX idx_economic_trend_id ON economic_trend_analysis(trend_id);
CREATE INDEX idx_economic_trend_analysis_id ON economic_trend_analysis(analysis_id);
CREATE INDEX idx_economic_trend_user_id ON economic_trend_analysis(user_id);
CREATE INDEX idx_economic_trend_type ON economic_trend_analysis(trend_type);
CREATE INDEX idx_economic_trend_created_at ON economic_trend_analysis(created_at);

-- Create economic optimization user preferences table
CREATE TABLE economic_user_preferences (
    id SERIAL PRIMARY KEY,
    preference_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    preference_type VARCHAR(50) NOT NULL,
    preference_data JSONB NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic user preferences
CREATE INDEX idx_economic_preferences_id ON economic_user_preferences(preference_id);
CREATE INDEX idx_economic_preferences_user_id ON economic_user_preferences(user_id);
CREATE INDEX idx_economic_preferences_type ON economic_user_preferences(preference_type);
CREATE INDEX idx_economic_preferences_created_at ON economic_user_preferences(created_at);

-- Create economic optimization model parameters table
CREATE TABLE economic_model_parameters (
    id SERIAL PRIMARY KEY,
    parameter_id UUID UNIQUE NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    parameter_name VARCHAR(100) NOT NULL,
    parameter_value JSONB NOT NULL,
    parameter_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic model parameters
CREATE INDEX idx_economic_parameters_id ON economic_model_parameters(parameter_id);
CREATE INDEX idx_economic_parameters_model_type ON economic_model_parameters(model_type);
CREATE INDEX idx_economic_parameters_name ON economic_model_parameters(parameter_name);
CREATE INDEX idx_economic_parameters_created_at ON economic_model_parameters(created_at);

-- Create economic optimization performance metrics table
CREATE TABLE economic_performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_unit VARCHAR(20),
    metric_description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic performance metrics
CREATE INDEX idx_economic_metrics_id ON economic_performance_metrics(metric_id);
CREATE INDEX idx_economic_metrics_analysis_id ON economic_performance_metrics(analysis_id);
CREATE INDEX idx_economic_metrics_type ON economic_performance_metrics(metric_type);
CREATE INDEX idx_economic_metrics_created_at ON economic_performance_metrics(created_at);

-- Create economic optimization alert subscriptions table
CREATE TABLE economic_alert_subscriptions (
    id SERIAL PRIMARY KEY,
    subscription_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_criteria JSONB NOT NULL,
    notification_channels JSONB NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic alert subscriptions
CREATE INDEX idx_economic_alerts_subscription_id ON economic_alert_subscriptions(subscription_id);
CREATE INDEX idx_economic_alerts_user_id ON economic_alert_subscriptions(user_id);
CREATE INDEX idx_economic_alerts_type ON economic_alert_subscriptions(alert_type);
CREATE INDEX idx_economic_alerts_active ON economic_alert_subscriptions(active);
CREATE INDEX idx_economic_alerts_created_at ON economic_alert_subscriptions(created_at);

-- Create economic optimization alerts table
CREATE TABLE economic_alerts (
    id SERIAL PRIMARY KEY,
    alert_id UUID UNIQUE NOT NULL,
    subscription_id UUID NOT NULL REFERENCES economic_alert_subscriptions(subscription_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_message TEXT NOT NULL,
    alert_severity VARCHAR(20) NOT NULL,
    triggered_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Create indexes for economic alerts
CREATE INDEX idx_economic_alerts_alert_id ON economic_alerts(alert_id);
CREATE INDEX idx_economic_alerts_subscription_id ON economic_alerts(subscription_id);
CREATE INDEX idx_economic_alerts_user_id ON economic_alerts(user_id);
CREATE INDEX idx_economic_alerts_type ON economic_alerts(alert_type);
CREATE INDEX idx_economic_alerts_severity ON economic_alerts(alert_severity);
CREATE INDEX idx_economic_alerts_triggered_at ON economic_alerts(triggered_at);
CREATE INDEX idx_economic_alerts_resolved_at ON economic_alerts(resolved_at);

-- Create economic optimization notification logs table
CREATE TABLE economic_notification_logs (
    id SERIAL PRIMARY KEY,
    notification_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    notification_content JSONB NOT NULL,
    delivery_status VARCHAR(20) NOT NULL,
    delivery_timestamp TIMESTAMP DEFAULT NOW(),
    read_timestamp TIMESTAMP
);

-- Create indexes for economic notification logs
CREATE INDEX idx_economic_notifications_id ON economic_notification_logs(notification_id);
CREATE INDEX idx_economic_notifications_user_id ON economic_notification_logs(user_id);
CREATE INDEX idx_economic_notifications_type ON economic_notification_logs(notification_type);
CREATE INDEX idx_economic_notifications_status ON economic_notification_logs(delivery_status);
CREATE INDEX idx_economic_notifications_delivered_at ON economic_notification_logs(delivery_timestamp);
CREATE INDEX idx_economic_notifications_read_at ON economic_notification_logs(read_timestamp);

-- Create economic optimization report templates table
CREATE TABLE economic_report_templates (
    id SERIAL PRIMARY KEY,
    template_id UUID UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    template_content JSONB NOT NULL,
    template_description TEXT,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic report templates
CREATE INDEX idx_economic_templates_id ON economic_report_templates(template_id);
CREATE INDEX idx_economic_templates_name ON economic_report_templates(template_name);
CREATE INDEX idx_economic_templates_type ON economic_report_templates(template_type);
CREATE INDEX idx_economic_templates_created_by ON economic_report_templates(created_by);
CREATE INDEX idx_economic_templates_created_at ON economic_report_templates(created_at);

-- Create economic optimization reports table
CREATE TABLE economic_reports (
    id SERIAL PRIMARY KEY,
    report_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    template_id UUID NOT NULL REFERENCES economic_report_templates(template_id) ON DELETE CASCADE,
    report_content JSONB NOT NULL,
    report_format VARCHAR(20) NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic reports
CREATE INDEX idx_economic_reports_id ON economic_reports(report_id);
CREATE INDEX idx_economic_reports_analysis_id ON economic_reports(analysis_id);
CREATE INDEX idx_economic_reports_user_id ON economic_reports(user_id);
CREATE INDEX idx_economic_reports_template_id ON economic_reports(template_id);
CREATE INDEX idx_economic_reports_generated_at ON economic_reports(generated_at);

-- Create economic optimization tracking table
CREATE TABLE economic_optimization_tracking (
    id SERIAL PRIMARY KEY,
    tracking_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    tracking_type VARCHAR(50) NOT NULL,
    tracking_data JSONB NOT NULL,
    tracking_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization tracking
CREATE INDEX idx_economic_tracking_id ON economic_optimization_tracking(tracking_id);
CREATE INDEX idx_economic_tracking_analysis_id ON economic_optimization_tracking(analysis_id);
CREATE INDEX idx_economic_tracking_user_id ON economic_optimization_tracking(user_id);
CREATE INDEX idx_economic_tracking_type ON economic_optimization_tracking(tracking_type);
CREATE INDEX idx_economic_tracking_status ON economic_optimization_tracking(tracking_status);
CREATE INDEX idx_economic_tracking_created_at ON economic_optimization_tracking(created_at);

-- Create economic optimization audit logs table
CREATE TABLE economic_audit_logs (
    id SERIAL PRIMARY KEY,
    log_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic audit logs
CREATE INDEX idx_economic_audit_logs_id ON economic_audit_logs(log_id);
CREATE INDEX idx_economic_audit_logs_user_id ON economic_audit_logs(user_id);
CREATE INDEX idx_economic_audit_logs_action_type ON economic_audit_logs(action_type);
CREATE INDEX idx_economic_audit_logs_created_at ON economic_audit_logs(created_at);

-- Create economic optimization cache table for performance
CREATE TABLE economic_optimization_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization cache
CREATE INDEX idx_economic_cache_key ON economic_optimization_cache(cache_key);
CREATE INDEX idx_economic_cache_expires ON economic_optimization_cache(expires_at);
CREATE INDEX idx_economic_cache_created_at ON economic_optimization_cache(created_at);

-- Create economic optimization settings table
CREATE TABLE economic_optimization_settings (
    id SERIAL PRIMARY KEY,
    setting_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    setting_type VARCHAR(50) NOT NULL,
    setting_value JSONB NOT NULL,
    setting_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization settings
CREATE INDEX idx_economic_settings_id ON economic_optimization_settings(setting_id);
CREATE INDEX idx_economic_settings_user_id ON economic_optimization_settings(user_id);
CREATE INDEX idx_economic_settings_type ON economic_optimization_settings(setting_type);
CREATE INDEX idx_economic_settings_created_at ON economic_optimization_settings(created_at);

-- Create economic optimization metadata table
CREATE TABLE economic_optimization_metadata (
    id SERIAL PRIMARY KEY,
    metadata_id UUID UNIQUE NOT NULL,
    analysis_id UUID NOT NULL REFERENCES economic_optimization_results(analysis_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    metadata_type VARCHAR(50) NOT NULL,
    metadata_content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic optimization metadata
CREATE INDEX idx_economic_metadata_id ON economic_optimization_metadata(metadata_id);
CREATE INDEX idx_economic_metadata_analysis_id ON economic_optimization_metadata(analysis_id);
CREATE INDEX idx_economic_metadata_user_id ON economic_optimization_metadata(user_id);
CREATE INDEX idx_economic_metadata_type ON economic_optimization_metadata(metadata_type);
CREATE INDEX idx_economic_metadata_created_at ON economic_optimization_metadata(created_at);

-- Create economic optimization error logs table
CREATE TABLE economic_error_logs (
    id SERIAL PRIMARY KEY,
    error_id UUID UNIQUE NOT NULL,
    analysis_id UUID REFERENCES economic_optimization_results(analysis_id) ON DELETE SET NULL,
    user_id UUID,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_details JSONB,
    stack_trace TEXT,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for economic error logs
CREATE INDEX idx_economic_errors_id ON economic_error_logs(error_id);
CREATE INDEX idx_economic_errors_analysis_id ON economic_error_logs(analysis_id);
CREATE INDEX idx_economic_errors_user_id ON economic_error_logs(user_id);
CREATE INDEX idx_economic_errors_type ON economic_error_logs(error_type);
CREATE INDEX idx_economic_errors_occurred_at ON economic_error_logs(occurred_at);