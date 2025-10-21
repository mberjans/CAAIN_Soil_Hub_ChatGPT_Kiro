CREATE TYPE nutrient_enum AS ENUM (
    'nitrogen', 'phosphorus', 'potassium', 'calcium', 'magnesium', 'sulfur',
    'iron', 'manganese', 'zinc', 'copper', 'boron', 'molybdenum', 'chlorine', 'nickel'
);

CREATE TYPE growth_stage_enum AS ENUM (
    'seedling', 'vegetative', 'flowering', 'fruiting', 'maturity'
);

CREATE TYPE symptom_severity_enum AS ENUM (
    'mild', 'moderate', 'severe'
);

CREATE TYPE visual_characteristic_enum AS ENUM (
    'yellowing_leaves', 'purple_tints', 'stunted_growth', 'necrosis', 'chlorosis',
    'interveinal_chlorosis', 'spotting', 'wilting', 'deformed_fruit', 'thin_stems', 'dark_green_leaves'
);

CREATE TABLE nutrient_deficiency_symptoms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nutrient nutrient_enum NOT NULL,
    crop_type VARCHAR(255) NOT NULL,
    growth_stages growth_stage_enum[] NOT NULL,
    symptom_description TEXT NOT NULL,
    visual_characteristics visual_characteristic_enum[] NOT NULL,
    severity symptom_severity_enum NOT NULL,
    confidence_score FLOAT NOT NULL,
    management_recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nutrient_deficiency_symptoms_nutrient ON nutrient_deficiency_symptoms (nutrient);
CREATE INDEX idx_nutrient_deficiency_symptoms_crop_type ON nutrient_deficiency_symptoms (crop_type);
CREATE INDEX idx_nutrient_deficiency_symptoms_growth_stages ON nutrient_deficiency_symptoms USING GIN (growth_stages);
CREATE INDEX idx_nutrient_deficiency_symptoms_visual_characteristics ON nutrient_deficiency_symptoms USING GIN (visual_characteristics);
