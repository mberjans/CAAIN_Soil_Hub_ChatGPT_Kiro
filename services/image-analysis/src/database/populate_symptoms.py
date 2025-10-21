import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.symptom_models import Base, NutrientDeficiencySymptom

# Database URL from environment variable or default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/image_analysis_db")

def populate_initial_symptoms():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine) # Ensure table is created
    Session = sessionmaker(bind=engine)
    session = Session()

    symptoms_data = [
        {
            "nutrient": "Nitrogen",
            "crop_type": "Corn",
            "symptom_name": "Nitrogen Deficiency in Corn (General Yellowing)",
            "description": "General yellowing of older leaves, starting at the tip and moving down the midrib in a V-shape.",
            "affected_parts": ["Older leaves", "Lower leaves"],
            "visual_characteristics": ["Pale green to yellow discoloration", "V-shaped yellowing from leaf tip", "Stunted growth"],
            "severity_levels": {
                "mild": "Slight pale green color on older leaves.",
                "moderate": "Distinct yellowing of older leaves, especially along the midrib.",
                "severe": "Pronounced yellowing, browning, and necrosis of older leaves; severe stunting."
            },
            "growth_stages": ["Vegetative stages", "Early reproductive stages"],
            "confidence_score_threshold": 0.75
        },
        {
            "nutrient": "Potassium",
            "crop_type": "Corn",
            "symptom_name": "Potassium Deficiency in Corn (Leaf Margin Yellowing)",
            "description": "Yellowing and necrosis along the margins of older leaves, often starting at the tip.",
            "affected_parts": ["Older leaves", "Leaf margins"],
            "visual_characteristics": ["Yellow or orange discoloration on leaf edges", "Scorching or browning of leaf margins", "Weak stalks"],
            "severity_levels": {
                "mild": "Slight yellowing on the edges of older leaves.",
                "moderate": "Pronounced yellowing and some scorching along leaf margins.",
                "severe": "Severe scorching and necrosis of leaf margins, leaves may appear ragged."
            },
            "growth_stages": ["Vegetative stages", "Reproductive stages"],
            "confidence_score_threshold": 0.70
        },
        {
            "nutrient": "Phosphorus",
            "crop_type": "Corn",
            "symptom_name": "Phosphorus Deficiency in Corn (Purple Discoloration)",
            "description": "Purplish discoloration of leaves, especially on younger plants, due to accumulation of sugars.",
            "affected_parts": ["Lower leaves", "Stems"],
            "visual_characteristics": ["Dark green to purplish coloration", "Stunted growth", "Delayed maturity"],
            "severity_levels": {
                "mild": "Slight purplish tint on lower leaves.",
                "moderate": "Distinct purple coloration, especially on leaf undersides and stems.",
                "severe": "Intense purple, almost black, discoloration; severe stunting and poor root development."
            },
            "growth_stages": ["Early vegetative stages"],
            "confidence_score_threshold": 0.80
        },
        {
            "nutrient": "Iron",
            "crop_type": "Soybean",
            "symptom_name": "Iron Deficiency in Soybean (Interveinal Chlorosis)",
            "description": "Yellowing between the veins of young leaves, while veins remain green.",
            "affected_parts": ["Younger leaves"],
            "visual_characteristics": ["Interveinal chlorosis (yellowing between green veins)", "Stunted growth", "White or bleached leaves in severe cases"],
            "severity_levels": {
                "mild": "Slight yellowing between veins of youngest leaves.",
                "moderate": "Pronounced interveinal chlorosis on young leaves.",
                "severe": "Leaves become almost white or bleached, with necrosis on leaf margins."
            },
            "growth_stages": ["Vegetative stages"],
            "confidence_score_threshold": 0.75
        }
    ]

    for symptom_data in symptoms_data:
        # Check if symptom already exists to prevent duplicates
        existing_symptom = session.query(NutrientDeficiencySymptom).filter_by(symptom_name=symptom_data["symptom_name"]).first()
        if not existing_symptom:
            symptom = NutrientDeficiencySymptom(**symptom_data)
            session.add(symptom)
            print(f"Added: {symptom_data['symptom_name']}")
        else:
            print(f"Skipped (already exists): {symptom_data['symptom_name']}")

    session.commit()
    session.close()
    print("Initial symptom data population complete.")

if __name__ == "__main__":
    populate_initial_symptoms()
