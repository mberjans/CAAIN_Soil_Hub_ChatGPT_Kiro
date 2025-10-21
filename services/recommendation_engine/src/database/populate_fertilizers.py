"""
Populate Fertilizers

Script to populate the fertilizer database with sample data.
"""

from sqlalchemy.orm import sessionmaker
from services.recommendation_engine.src.database.fertilizer_schema import (
    engine,
    FertilizerProduct,
)

Session = sessionmaker(bind=engine)

def populate_fertilizers():
    """Populate the fertilizer database with sample data."""
    session = Session()

    fertilizers = [
        {
            "product_id": "urea_46_0_0",
            "name": "Urea (46-0-0)",
            "manufacturer": "Generic",
            "fertilizer_type": "synthetic",
            "cost_per_unit": 450,
            "environmental_impact_score": 0.4,
            "soil_health_score": 0.3,
            "equipment_requirements": ["broadcast_spreader"],
            "application_methods": ["broadcast"],
            "organic_certified": False,
            "pros": ["High nitrogen content", "Low cost per unit N"],
            "cons": ["Volatilization risk", "No secondary nutrients"],
        },
        {
            "product_id": "ammonium_sulfate_21_0_0",
            "name": "Ammonium Sulfate (21-0-0-24S)",
            "manufacturer": "Generic",
            "fertilizer_type": "synthetic",
            "cost_per_unit": 380,
            "environmental_impact_score": 0.5,
            "soil_health_score": 0.4,
            "equipment_requirements": ["broadcast_spreader"],
            "application_methods": ["broadcast"],
            "organic_certified": False,
            "pros": ["Adds sulfur", "Acidifying effect"],
            "cons": ["Lower N content", "Can lower pH"],
        },
        {
            "product_id": "composted_manure_organic",
            "name": "Composted Manure",
            "manufacturer": "Various",
            "fertilizer_type": "organic",
            "cost_per_unit": 50,
            "environmental_impact_score": 0.9,
            "soil_health_score": 0.95,
            "equipment_requirements": ["manure_spreader"],
            "application_methods": ["broadcast", "incorporation"],
            "organic_certified": True,
            "pros": ["Improves soil structure", "Slow release", "Organic matter"],
            "cons": ["Low nutrient content", "Variable analysis", "High volume needed"],
        },
    ]

    for fert_data in fertilizers:
        fertilizer = FertilizerProduct(**fert_data)
        session.add(fertilizer)

    session.commit()
    session.close()

if __name__ == "__main__":
    populate_fertilizers()