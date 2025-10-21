import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from ..models.sqlalchemy_models import Base, NutrientDeficiencySymptomORM
from ..models.deficiency_models import Nutrient, Severity, PlantPart

# Database connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/afas_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

def populate_symptom_data():
    db = SessionLocal()
    try:
        symptoms_to_add = [
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.NITROGEN,
                crop_type="corn",
                symptom_name="general_chlorosis_older_leaves",
                description="General yellowing of older leaves, starting from the tip and moving along the midrib.",
                affected_parts=[PlantPart.OLDER_LEAVES],
                visual_characteristics=["yellowing", "stunted growth"],
                typical_severity=Severity.MODERATE,
                notes="Nitrogen is mobile in the plant, so symptoms appear on older leaves first."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.PHOSPHORUS,
                crop_type="corn",
                symptom_name="purpling_leaves",
                description="Leaves turn dark green or purplish, especially on the margins, often accompanied by stunted growth.",
                affected_parts=[PlantPart.WHOLE_PLANT, PlantPart.OLDER_LEAVES],
                visual_characteristics=["purpling", "dark green", "stunted growth"],
                typical_severity=Severity.MODERATE,
                notes="Phosphorus deficiency is common in cold, wet soils."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.POTASSIUM,
                crop_type="corn",
                symptom_name="leaf_margin_chlorosis_necrosis",
                description="Yellowing and necrosis (browning/death) of leaf margins, particularly on older leaves.",
                affected_parts=[PlantPart.OLDER_LEAVES, PlantPart.LEAF_MARGINS],
                visual_characteristics=["yellowing", "browning", "necrosis"],
                typical_severity=Severity.SEVERE,
                notes="Potassium is mobile, so symptoms appear on older leaves first. Often called 'firing'."
            ),
            NutricientDeficiencySymptomORM(
                nutrient=Nutrient.IRON,
                crop_type="soybean",
                symptom_name="interveinal_chlorosis_young_leaves",
                description="Yellowing between the veins of young leaves, while veins remain green.",
                affected_parts=[PlantPart.YOUNG_LEAVES, PlantPart.INTERVEINAL_AREAS],
                visual_characteristics=["interveinal yellowing", "green veins"],
                typical_severity=Severity.MILD,
                notes="Iron is immobile, so symptoms appear on new growth first. Common in high pH soils."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.CALCIUM,
                crop_type="tomato",
                symptom_name="blossom_end_rot",
                description="Dark, sunken lesions on the blossom end of fruits.",
                affected_parts=[PlantPart.FRUIT],
                visual_characteristics=["dark lesions", "sunken spots"],
                typical_severity=Severity.SEVERE,
                notes="Calcium deficiency is often related to inconsistent water supply rather than low soil calcium."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.SULFUR,
                crop_type="canola",
                symptom_name="general_chlorosis_young_leaves",
                description="General yellowing of young leaves, often accompanied by purpling of stems and petioles.",
                affected_parts=[PlantPart.YOUNG_LEAVES, PlantPart.STEM],
                visual_characteristics=["yellowing", "purpling"],
                typical_severity=Severity.MODERATE,
                notes="Sulfur is immobile, so symptoms appear on new growth first. Often confused with nitrogen deficiency."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.MAGNESIUM,
                crop_type="potato",
                symptom_name="interveinal_chlorosis_older_leaves",
                description="Yellowing between the veins of older leaves, with veins remaining green. Leaves may become brittle.",
                affected_parts=[PlantPart.OLDER_LEAVES, PlantPart.INTERVEINAL_AREAS],
                visual_characteristics=["interveinal yellowing", "green veins", "brittle leaves"],
                typical_severity=Severity.MODERATE,
                notes="Magnesium is mobile, so symptoms appear on older leaves first. Common in sandy, acidic soils."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.BORON,
                crop_type="sugar_beet",
                symptom_name="heart_rot",
                description="Death of the growing point, internal blackening, and cracking of roots.",
                affected_parts=[PlantPart.GROWING_POINTS, PlantPart.ROOTS],
                visual_characteristics=["growing point death", "blackening", "cracking"],
                typical_severity=Severity.SEVERE,
                notes="Boron is immobile. Deficiency can lead to hollow stems and poor pollination."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.ZINC,
                crop_type="corn",
                symptom_name="white_bands_midrib",
                description="White to yellow bands on either side of the midrib, especially on young leaves. Stunted growth and shortened internodes.",
                affected_parts=[PlantPart.YOUNG_LEAVES],
                visual_characteristics=["white bands", "yellow bands", "stunted growth"],
                typical_severity=Severity.MODERATE,
                notes="Zinc is immobile. Deficiency is common in high pH soils and soils with high phosphorus."
            ),
            NutrientDeficiencySymptomORM(
                nutrient=Nutrient.MANGANESE,
                crop_type="oats",
                symptom_name="gray_speck",
                description="Grayish-brown spots or streaks on the leaves, often leading to wilting and collapse.",
                affected_parts=[PlantPart.YOUNG_LEAVES],
                visual_characteristics=["gray spots", "brown streaks", "wilting"],
                typical_severity=Severity.SEVERE,
                notes="Manganese is immobile. Deficiency is common in organic soils and high pH soils."
            ),
        ]

        for symptom_data in symptoms_to_add:
            try:
                # Check if a similar symptom already exists to prevent duplicates
                existing_symptom = db.query(NutrientDeficiencySymptomORM).filter_by(
                    nutrient=symptom_data.nutrient,
                    crop_type=symptom_data.crop_type,
                    symptom_name=symptom_data.symptom_name
                ).first()
                if not existing_symptom:
                    db.add(symptom_data)
                    db.commit()
                    print(f"Added symptom: {symptom_data.symptom_name} for {symptom_data.crop_type} ({symptom_data.nutrient})")
                else:
                    print(f"Symptom already exists: {symptom_data.symptom_name} for {symptom_data.crop_type} ({symptom_data.nutrient})")
            except IntegrityError:
                db.rollback()
                print(f"Integrity error for symptom: {symptom_data.symptom_name} for {symptom_data.crop_type} ({symptom_data.nutrient})")
            except Exception as e:
                db.rollback()
                print(f"Error adding symptom {symptom_data.symptom_name}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # This part assumes a PostgreSQL database is running and accessible
    # You might need to set the DATABASE_URL environment variable
    # For example: export DATABASE_URL="postgresql://user:password@localhost:5432/afas_db"
    create_db_and_tables()
    populate_symptom_data()
