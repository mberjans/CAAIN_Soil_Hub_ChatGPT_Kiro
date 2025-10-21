
CREATE TABLE tissue_test_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    field_id UUID NOT NULL,
    crop_type VARCHAR(100) NOT NULL,
    growth_stage VARCHAR(100) NOT NULL,
    test_date DATE NOT NULL,
    lab_id VARCHAR(100),
    nutrient_levels JSONB NOT NULL, -- e.g., {"N": 3.5, "P": 0.3, "K": 2.1, "Zn": 50}
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tissue_test_data_field_id ON tissue_test_data(field_id);
CREATE INDEX idx_tissue_test_data_crop_type ON tissue_test_data(crop_type);
