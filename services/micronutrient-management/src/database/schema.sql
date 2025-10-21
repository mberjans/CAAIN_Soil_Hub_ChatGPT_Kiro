CREATE TABLE IF NOT EXISTS micronutrients (
    name VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    role_in_plant TEXT NOT NULL,
    optimal_soil_range_ppm VARCHAR(50),
    toxicity_threshold_ppm VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS deficiency_symptoms (
    id SERIAL PRIMARY KEY,
    micronutrient_name VARCHAR(50) REFERENCES micronutrients(name),
    symptom_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    affected_plant_part VARCHAR(100) NOT NULL,
    severity_indicator VARCHAR(20) NOT NULL,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS crop_micronutrient_requirements (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    micronutrient_name VARCHAR(50) REFERENCES micronutrients(name),
    required_amount_per_ton_yield_g DECIMAL(10,4),
    critical_soil_level_ppm DECIMAL(10,4),
    sensitivity_to_deficiency VARCHAR(20) NOT NULL,
    sensitivity_to_toxicity VARCHAR(20) NOT NULL,
    UNIQUE (crop_name, micronutrient_name)
);
