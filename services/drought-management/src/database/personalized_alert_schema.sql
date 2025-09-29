-- Personalized Alert and Response System Database Schema
-- This schema supports personalized drought alerts, automated responses, and emergency protocols

-- Personalized Alert Configuration Table
CREATE TABLE personalized_alert_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL,
    user_id UUID NOT NULL,
    crop_types TEXT[] NOT NULL,
    current_practices TEXT[] DEFAULT '{}',
    irrigation_system_type VARCHAR(100),
    water_source_types TEXT[] DEFAULT '{}',
    emergency_contacts JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Alert Thresholds Table
CREATE TABLE personalized_alert_thresholds (
    threshold_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES personalized_alert_configs(config_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    threshold_value DECIMAL(10,4) NOT NULL,
    comparison_operator VARCHAR(5) NOT NULL CHECK (comparison_operator IN ('>', '<', '>=', '<=', '==', '!=')),
    severity_level VARCHAR(20) NOT NULL CHECK (severity_level IN ('low', 'medium', 'high', 'critical', 'emergency')),
    enabled BOOLEAN DEFAULT TRUE,
    crop_specific VARCHAR(100),
    growth_stage_specific VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Preferences Table
CREATE TABLE notification_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id UUID REFERENCES personalized_alert_configs(config_id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'sms', 'push', 'webhook', 'dashboard')),
    enabled BOOLEAN DEFAULT TRUE,
    severity_levels TEXT[] NOT NULL,
    frequency_limit INTEGER,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    escalation_delay_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Emergency Protocols Table
CREATE TABLE emergency_protocols (
    protocol_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_type VARCHAR(50) NOT NULL CHECK (protocol_type IN ('water_restriction', 'crop_abandonment', 'emergency_irrigation', 'disaster_assistance', 'resource_sharing')),
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    trigger_conditions JSONB NOT NULL,
    activation_threshold VARCHAR(20) NOT NULL CHECK (activation_threshold IN ('low', 'medium', 'high', 'critical', 'emergency')),
    steps JSONB NOT NULL,
    required_authorizations TEXT[] DEFAULT '{}',
    estimated_duration_hours INTEGER NOT NULL CHECK (estimated_duration_hours >= 0),
    resource_requirements TEXT[] DEFAULT '{}',
    contact_information JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Personalized Alerts Table
CREATE TABLE personalized_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL,
    user_id UUID NOT NULL,
    config_id UUID REFERENCES personalized_alert_configs(config_id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical', 'emergency')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    triggered_threshold_id UUID REFERENCES personalized_alert_thresholds(threshold_id),
    current_metrics JSONB NOT NULL,
    historical_context JSONB DEFAULT '{}',
    crop_impact_assessment JSONB DEFAULT '{}',
    notification_channels TEXT[] NOT NULL,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Automated Response Recommendations Table
CREATE TABLE automated_response_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES personalized_alerts(alert_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('irrigation_adjustment', 'conservation_practice', 'crop_management', 'water_source_activation', 'emergency_protocol', 'resource_mobilization')),
    action_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL CHECK (priority >= 1 AND priority <= 5),
    estimated_cost DECIMAL(10,2),
    estimated_effectiveness DECIMAL(3,2) NOT NULL CHECK (estimated_effectiveness >= 0 AND estimated_effectiveness <= 1),
    implementation_time_hours INTEGER NOT NULL CHECK (implementation_time_hours >= 0),
    required_resources TEXT[] DEFAULT '{}',
    prerequisites TEXT[] DEFAULT '{}',
    expected_outcome TEXT NOT NULL,
    risk_assessment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Response Tracking Table
CREATE TABLE response_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES personalized_alerts(alert_id),
    recommendation_id UUID REFERENCES automated_response_recommendations(recommendation_id),
    action_taken TEXT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    implementation_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    start_time TIMESTAMP,
    completion_time TIMESTAMP,
    actual_cost DECIMAL(10,2),
    effectiveness_rating DECIMAL(3,2) CHECK (effectiveness_rating >= 0 AND effectiveness_rating <= 10),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Resource Mobilization Table
CREATE TABLE resource_mobilization (
    mobilization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES personalized_alerts(alert_id),
    resource_type VARCHAR(100) NOT NULL,
    resource_name VARCHAR(200) NOT NULL,
    quantity_needed DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    urgency_level VARCHAR(20) NOT NULL CHECK (urgency_level IN ('low', 'medium', 'high', 'critical', 'emergency')),
    source_location VARCHAR(200) NOT NULL,
    destination_location VARCHAR(200) NOT NULL,
    estimated_arrival_time TIMESTAMP,
    contact_information JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'requested' CHECK (status IN ('requested', 'confirmed', 'in_transit', 'delivered', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Alert History View (for reporting)
CREATE VIEW alert_history_view AS
SELECT 
    pa.alert_id,
    pa.farm_id,
    pa.user_id,
    pa.alert_type,
    pa.severity,
    pa.title,
    pa.message,
    pa.created_at,
    pa.acknowledged_at,
    pa.resolved_at,
    CASE 
        WHEN pa.resolved_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (pa.resolved_at - pa.created_at)) / 3600
        ELSE NULL 
    END AS resolution_time_hours,
    CASE 
        WHEN pa.acknowledged_at IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (pa.acknowledged_at - pa.created_at)) / 3600
        ELSE NULL 
    END AS acknowledgment_time_hours,
    COUNT(arr.recommendation_id) AS recommendations_count,
    COUNT(rt.tracking_id) AS responses_taken
FROM personalized_alerts pa
LEFT JOIN automated_response_recommendations arr ON pa.alert_id = arr.alert_id
LEFT JOIN response_tracking rt ON pa.alert_id = rt.alert_id
GROUP BY pa.alert_id, pa.farm_id, pa.user_id, pa.alert_type, pa.severity, 
         pa.title, pa.message, pa.created_at, pa.acknowledged_at, pa.resolved_at;

-- Response Effectiveness View
CREATE VIEW response_effectiveness_view AS
SELECT 
    rt.alert_id,
    rt.recommendation_id,
    rt.action_type,
    rt.implementation_status,
    rt.start_time,
    rt.completion_time,
    rt.actual_cost,
    rt.effectiveness_rating,
    CASE 
        WHEN rt.completion_time IS NOT NULL AND rt.start_time IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (rt.completion_time - rt.start_time)) / 3600
        ELSE NULL 
    END AS implementation_time_hours,
    arr.estimated_cost,
    arr.estimated_effectiveness,
    arr.priority
FROM response_tracking rt
LEFT JOIN automated_response_recommendations arr ON rt.recommendation_id = arr.recommendation_id;

-- Indexes for performance optimization
CREATE INDEX idx_personalized_alert_configs_farm_id ON personalized_alert_configs(farm_id);
CREATE INDEX idx_personalized_alert_configs_user_id ON personalized_alert_configs(user_id);
CREATE INDEX idx_personalized_alert_configs_active ON personalized_alert_configs(is_active);

CREATE INDEX idx_alert_thresholds_config_id ON personalized_alert_thresholds(config_id);
CREATE INDEX idx_alert_thresholds_alert_type ON personalized_alert_thresholds(alert_type);
CREATE INDEX idx_alert_thresholds_enabled ON personalized_alert_thresholds(enabled);

CREATE INDEX idx_notification_preferences_config_id ON notification_preferences(config_id);
CREATE INDEX idx_notification_preferences_channel ON notification_preferences(channel);

CREATE INDEX idx_personalized_alerts_farm_id ON personalized_alerts(farm_id);
CREATE INDEX idx_personalized_alerts_user_id ON personalized_alerts(user_id);
CREATE INDEX idx_personalized_alerts_alert_type ON personalized_alerts(alert_type);
CREATE INDEX idx_personalized_alerts_severity ON personalized_alerts(severity);
CREATE INDEX idx_personalized_alerts_created_at ON personalized_alerts(created_at);
CREATE INDEX idx_personalized_alerts_acknowledged ON personalized_alerts(acknowledged_at);
CREATE INDEX idx_personalized_alerts_resolved ON personalized_alerts(resolved_at);

CREATE INDEX idx_response_recommendations_alert_id ON automated_response_recommendations(alert_id);
CREATE INDEX idx_response_recommendations_action_type ON automated_response_recommendations(action_type);
CREATE INDEX idx_response_recommendations_priority ON automated_response_recommendations(priority);

CREATE INDEX idx_response_tracking_alert_id ON response_tracking(alert_id);
CREATE INDEX idx_response_tracking_recommendation_id ON response_tracking(recommendation_id);
CREATE INDEX idx_response_tracking_status ON response_tracking(implementation_status);
CREATE INDEX idx_response_tracking_start_time ON response_tracking(start_time);

CREATE INDEX idx_resource_mobilization_alert_id ON resource_mobilization(alert_id);
CREATE INDEX idx_resource_mobilization_status ON resource_mobilization(status);
CREATE INDEX idx_resource_mobilization_urgency ON resource_mobilization(urgency_level);

-- Triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_personalized_alert_configs_updated_at 
    BEFORE UPDATE ON personalized_alert_configs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_thresholds_updated_at 
    BEFORE UPDATE ON personalized_alert_thresholds 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_updated_at 
    BEFORE UPDATE ON notification_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emergency_protocols_updated_at 
    BEFORE UPDATE ON emergency_protocols 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_personalized_alerts_updated_at 
    BEFORE UPDATE ON personalized_alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_response_tracking_updated_at 
    BEFORE UPDATE ON response_tracking 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_resource_mobilization_updated_at 
    BEFORE UPDATE ON resource_mobilization 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();