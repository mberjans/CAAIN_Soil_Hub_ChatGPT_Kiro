-- Farmer Preferences Schema
-- Comprehensive farmer preference storage for crop type filtering

-- Create farmer_preferences table
CREATE TABLE IF NOT EXISTS farmer_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preference_category VARCHAR(50) NOT NULL CHECK (preference_category IN (
        'crop_types', 'management_style', 'risk_tolerance', 'market_focus',
        'sustainability', 'labor_requirements', 'equipment_preferences', 
        'certification_goals', 'yield_priorities', 'economic_factors'
    )),
    preference_data JSONB NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 1.0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_farmer_preferences_user_id ON farmer_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_farmer_preferences_category ON farmer_preferences(preference_category);
CREATE INDEX IF NOT EXISTS idx_farmer_preferences_user_category ON farmer_preferences(user_id, preference_category);
CREATE INDEX IF NOT EXISTS idx_farmer_preferences_active ON farmer_preferences(active) WHERE active = TRUE;
CREATE INDEX IF NOT EXISTS idx_farmer_preferences_data ON farmer_preferences USING GIN(preference_data);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_farmer_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER farmer_preferences_updated_at
    BEFORE UPDATE ON farmer_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_farmer_preferences_updated_at();

-- Create preference history table for versioning
CREATE TABLE IF NOT EXISTS farmer_preference_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preference_id UUID NOT NULL REFERENCES farmer_preferences(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    preference_category VARCHAR(50) NOT NULL,
    preference_data JSONB NOT NULL,
    weight DECIMAL(3,2) NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    archived_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_farmer_preference_history_preference_id ON farmer_preference_history(preference_id);
CREATE INDEX IF NOT EXISTS idx_farmer_preference_history_user_id ON farmer_preference_history(user_id);

-- Function to archive preference changes
CREATE OR REPLACE FUNCTION archive_preference_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO farmer_preference_history (
        preference_id, user_id, preference_category, 
        preference_data, weight, version, created_at
    ) VALUES (
        OLD.id, OLD.user_id, OLD.preference_category,
        OLD.preference_data, OLD.weight, OLD.version, OLD.created_at
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_farmer_preference_changes
    BEFORE UPDATE ON farmer_preferences
    FOR EACH ROW
    EXECUTE FUNCTION archive_preference_change();

-- Create view for active preferences with inheritance
CREATE OR REPLACE VIEW active_farmer_preferences AS
SELECT 
    fp.*,
    CASE 
        WHEN fp.preference_category = 'crop_types' THEN fp.weight * 1.2
        WHEN fp.preference_category = 'management_style' THEN fp.weight * 1.1
        ELSE fp.weight
    END as effective_weight
FROM farmer_preferences fp
WHERE fp.active = TRUE;

-- Sample preference data structures (for documentation)
COMMENT ON TABLE farmer_preferences IS 'Stores comprehensive farmer preferences for crop filtering and recommendations';
COMMENT ON COLUMN farmer_preferences.preference_data IS 'JSONB structure varies by category:
crop_types: {"preferred_crops": ["corn", "soybeans"], "avoided_crops": ["wheat"], "new_crop_interest": true}
management_style: {"organic": true, "conventional": false, "precision_ag": true, "no_till": true}
risk_tolerance: {"level": "moderate", "diversification_preference": true, "experimental_willingness": 0.3}
market_focus: {"local_markets": true, "commodity_markets": true, "specialty_crops": false, "value_added": true}
sustainability: {"carbon_sequestration": true, "water_conservation": true, "biodiversity": true, "soil_health": true}
labor_requirements: {"max_labor_hours_per_acre": 8, "seasonal_labor_availability": true, "automation_preference": true}
equipment_preferences: {"existing_equipment": ["planter", "harvester"], "planned_purchases": ["drone"], "equipment_sharing": true}
certification_goals: {"organic_certification": false, "gmo_free": true, "sustainable_certification": true}
yield_priorities: {"maximum_yield": false, "consistent_yield": true, "quality_over_quantity": true}
economic_factors: {"input_cost_sensitivity": "high", "price_volatility_tolerance": "low", "roi_timeframe": "short_term"}';