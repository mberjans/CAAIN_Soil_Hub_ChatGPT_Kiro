-- Preference Learning and Adaptation System Database Schema
-- Tables for tracking user interactions and feedback for preference learning

-- User interactions tracking table
CREATE TABLE IF NOT EXISTS user_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN (
        'view', 'select', 'reject', 'save', 'share', 'skip', 'search', 'filter', 'compare'
    )),
    crop_id VARCHAR(50), -- References crops table
    recommendation_id UUID, -- References recommendations table if applicable
    interaction_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(100),
    
    -- Additional context
    page_context VARCHAR(100), -- Where the interaction happened
    search_query TEXT, -- If interaction was from search
    filter_criteria JSONB, -- If interaction involved filtering
    
    -- Performance tracking
    response_time_ms INTEGER,
    
    CONSTRAINT fk_user_interactions_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- User feedback tracking table
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    recommendation_id UUID, -- References recommendations table
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN (
        'rating', 'implemented', 'rejected', 'modified', 'helpful', 'not_helpful'
    )),
    feedback_value JSONB NOT NULL, -- Rating number, boolean, or structured data
    feedback_text TEXT,
    crop_ids TEXT[], -- Array of crop IDs related to feedback
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional context
    implementation_notes TEXT,
    modification_details JSONB,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 5),
    
    CONSTRAINT fk_user_feedback_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Preference learning sessions table
CREATE TABLE IF NOT EXISTS preference_learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_type VARCHAR(50) NOT NULL CHECK (session_type IN (
        'interaction_analysis', 'feedback_learning', 'collaborative_filtering', 'pattern_detection'
    )),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- Learning parameters
    learning_algorithm VARCHAR(50),
    data_points_processed INTEGER DEFAULT 0,
    preferences_updated INTEGER DEFAULT 0,
    
    -- Results
    learning_results JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    
    -- Status
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    
    CONSTRAINT fk_learning_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Preference adaptation history table
CREATE TABLE IF NOT EXISTS preference_adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preference_id UUID NOT NULL, -- References farmer_preferences table
    adaptation_type VARCHAR(50) NOT NULL CHECK (adaptation_type IN (
        'weight_adjustment', 'data_update', 'new_preference', 'preference_merge'
    )),
    
    -- Before and after states
    old_weight DECIMAL(3,2),
    new_weight DECIMAL(3,2),
    old_preference_data JSONB,
    new_preference_data JSONB,
    
    -- Learning context
    trigger_event VARCHAR(50), -- What caused this adaptation
    learning_session_id UUID REFERENCES preference_learning_sessions(id),
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    
    -- Metadata
    adaptation_algorithm VARCHAR(50),
    data_sources TEXT[], -- What data was used for this adaptation
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_adaptations_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_adaptations_preference_id FOREIGN KEY (preference_id) REFERENCES farmer_preferences(id) ON DELETE CASCADE
);

-- User behavior patterns table
CREATE TABLE IF NOT EXISTS user_behavior_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    pattern_type VARCHAR(50) NOT NULL CHECK (pattern_type IN (
        'crop_affinity', 'interaction_timing', 'search_behavior', 'decision_speed', 'risk_pattern'
    )),
    pattern_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    
    -- Pattern validity
    first_detected TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_confirmed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    detection_count INTEGER DEFAULT 1,
    
    -- Pattern strength
    strength_score DECIMAL(3,2) CHECK (strength_score BETWEEN 0 AND 1),
    stability_score DECIMAL(3,2) CHECK (stability_score BETWEEN 0 AND 1),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT fk_behavior_patterns_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_crop_id ON user_interactions(crop_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_session ON user_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_time ON user_interactions(user_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_timestamp ON user_feedback(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_recommendation ON user_feedback(recommendation_id);

CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON preference_learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_status ON preference_learning_sessions(status);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_type ON preference_learning_sessions(session_type);

CREATE INDEX IF NOT EXISTS idx_adaptations_user_id ON preference_adaptations(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_preference_id ON preference_adaptations(preference_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_timestamp ON preference_adaptations(timestamp);
CREATE INDEX IF NOT EXISTS idx_adaptations_session ON preference_adaptations(learning_session_id);

CREATE INDEX IF NOT EXISTS idx_behavior_patterns_user_id ON user_behavior_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_behavior_patterns_type ON user_behavior_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_behavior_patterns_active ON user_behavior_patterns(is_active);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_user_interactions_data_gin ON user_interactions USING GIN(interaction_data);
CREATE INDEX IF NOT EXISTS idx_user_feedback_value_gin ON user_feedback USING GIN(feedback_value);
CREATE INDEX IF NOT EXISTS idx_learning_results_gin ON preference_learning_sessions USING GIN(learning_results);
CREATE INDEX IF NOT EXISTS idx_behavior_patterns_data_gin ON user_behavior_patterns USING GIN(pattern_data);

-- Create functions for automatic learning triggers

-- Function to automatically trigger learning after feedback
CREATE OR REPLACE FUNCTION trigger_learning_on_feedback()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a learning session for immediate feedback processing
    INSERT INTO preference_learning_sessions (
        user_id, 
        session_type, 
        learning_algorithm,
        status
    ) VALUES (
        NEW.user_id, 
        'feedback_learning', 
        'immediate_feedback_processor',
        'running'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic learning on feedback
CREATE TRIGGER auto_learning_on_feedback
    AFTER INSERT ON user_feedback
    FOR EACH ROW
    EXECUTE FUNCTION trigger_learning_on_feedback();

-- Function to trigger periodic learning analysis
CREATE OR REPLACE FUNCTION trigger_periodic_learning()
RETURNS TRIGGER AS $$
DECLARE
    interaction_count INTEGER;
    last_learning TIMESTAMP;
BEGIN
    -- Check if user has enough interactions for learning
    SELECT COUNT(*) INTO interaction_count
    FROM user_interactions
    WHERE user_id = NEW.user_id 
    AND timestamp >= NOW() - INTERVAL '7 days';
    
    -- Check when last learning session occurred
    SELECT MAX(start_time) INTO last_learning
    FROM preference_learning_sessions
    WHERE user_id = NEW.user_id
    AND session_type = 'interaction_analysis';
    
    -- Trigger learning if enough interactions and time since last learning
    IF interaction_count >= 10 AND (last_learning IS NULL OR last_learning < NOW() - INTERVAL '3 days') THEN
        INSERT INTO preference_learning_sessions (
            user_id, 
            session_type, 
            learning_algorithm,
            status
        ) VALUES (
            NEW.user_id, 
            'interaction_analysis', 
            'pattern_detection_algorithm',
            'running'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for periodic learning
CREATE TRIGGER auto_periodic_learning
    AFTER INSERT ON user_interactions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_periodic_learning();

-- Create view for learning analytics
CREATE OR REPLACE VIEW user_learning_analytics AS
SELECT 
    u.user_id,
    u.email,
    
    -- Interaction statistics
    COALESCE(ui_stats.total_interactions, 0) as total_interactions,
    COALESCE(ui_stats.interaction_types, 0) as unique_interaction_types,
    ui_stats.last_interaction,
    
    -- Feedback statistics
    COALESCE(fb_stats.total_feedback, 0) as total_feedback,
    fb_stats.avg_rating,
    fb_stats.last_feedback,
    
    -- Learning statistics
    COALESCE(ls_stats.learning_sessions, 0) as learning_sessions,
    ls_stats.last_learning,
    COALESCE(ls_stats.preferences_learned, 0) as preferences_learned,
    
    -- Behavior patterns
    COALESCE(bp_stats.active_patterns, 0) as active_behavior_patterns,
    
    -- Preference statistics
    COALESCE(pref_stats.total_preferences, 0) as total_preferences,
    COALESCE(pref_stats.learned_preferences, 0) as learned_preferences
    
FROM users u

-- Interaction statistics
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_interactions,
        COUNT(DISTINCT interaction_type) as interaction_types,
        MAX(timestamp) as last_interaction
    FROM user_interactions
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
) ui_stats ON u.user_id = ui_stats.user_id

-- Feedback statistics
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_feedback,
        AVG(CASE 
            WHEN feedback_type = 'rating' AND feedback_value::text ~ '^\d+(\.\d+)?$'
            THEN CAST(feedback_value::text AS DECIMAL)
            ELSE NULL 
        END) as avg_rating,
        MAX(timestamp) as last_feedback
    FROM user_feedback
    WHERE timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
) fb_stats ON u.user_id = fb_stats.user_id

-- Learning session statistics
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as learning_sessions,
        MAX(start_time) as last_learning,
        SUM(preferences_updated) as preferences_learned
    FROM preference_learning_sessions
    WHERE start_time >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
) ls_stats ON u.user_id = ls_stats.user_id

-- Behavior pattern statistics
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as active_patterns
    FROM user_behavior_patterns
    WHERE is_active = TRUE
    GROUP BY user_id
) bp_stats ON u.user_id = bp_stats.user_id

-- Preference statistics
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_preferences,
        COUNT(CASE WHEN preference_data->>'learned_from_interactions' = 'true' THEN 1 END) as learned_preferences
    FROM farmer_preferences
    WHERE active = TRUE
    GROUP BY user_id
) pref_stats ON u.user_id = pref_stats.user_id;

-- Comment on tables
COMMENT ON TABLE user_interactions IS 'Tracks all user interactions with the system for learning user preferences';
COMMENT ON TABLE user_feedback IS 'Stores explicit user feedback on recommendations for preference learning';
COMMENT ON TABLE preference_learning_sessions IS 'Tracks preference learning algorithm execution sessions';
COMMENT ON TABLE preference_adaptations IS 'Records all changes made to user preferences by learning algorithms';
COMMENT ON TABLE user_behavior_patterns IS 'Stores detected behavioral patterns for each user';

-- Sample data types for documentation
COMMENT ON COLUMN user_interactions.interaction_data IS 'JSONB structure varies by interaction_type:
view: {"duration_seconds": 30, "scroll_depth": 0.8, "elements_viewed": ["description", "images"]}
select: {"selected_items": ["crop_id_1"], "selection_time_ms": 1500, "alternatives_considered": 3}
search: {"query": "organic corn varieties", "filters_applied": {"region": "midwest"}, "results_count": 15}
filter: {"filters_applied": {"crop_type": "grain", "maturity": "early"}, "results_before": 100, "results_after": 25}';

COMMENT ON COLUMN user_feedback.feedback_value IS 'JSONB structure varies by feedback_type:
rating: 4 (integer 1-5)
implemented: true (boolean)
helpful: {"helpful": true, "reason": "detailed information"}
modified: {"original_recommendation": "variety_a", "user_choice": "variety_b", "reason": "better local availability"}';

COMMENT ON COLUMN user_behavior_patterns.pattern_data IS 'JSONB structure varies by pattern_type:
crop_affinity: {"preferred_categories": ["grains", "legumes"], "affinity_scores": {"corn": 0.9, "soybeans": 0.8}}
interaction_timing: {"peak_hours": [9, 14, 19], "session_duration_avg": 1200, "frequency_pattern": "weekday_morning"}
search_behavior: {"query_complexity": "medium", "filter_usage": "heavy", "refinement_rate": 0.3}
decision_speed: {"avg_time_to_decision_ms": 45000, "comparison_behavior": "thorough", "confidence_level": "high"}';