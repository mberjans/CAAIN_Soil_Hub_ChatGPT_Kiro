"""
Seed Data for Fertilizer Type Selection Database

Initial data for fertilizer products and equipment compatibility.
"""

from sqlalchemy.orm import Session
from .fertilizer_schema import FertilizerProduct, EquipmentCompatibility
import logging

logger = logging.getLogger(__name__)


def seed_fertilizer_products(session: Session):
    """Seed database with initial fertilizer products."""
    
    fertilizer_products = [
        # Synthetic Fertilizers
        {
            "product_id": "urea_46_0_0",
            "name": "Urea (46-0-0)",
            "manufacturer": "Generic",
            "fertilizer_type": "synthetic",
            "release_pattern": "immediate",
            "nutrient_content": {
                "nitrogen_percent": 46.0,
                "phosphorus_p2o5_percent": 0.0,
                "potassium_k2o_percent": 0.0
            },
            "cost_per_unit": 420.0,
            "unit_size": 2000.0,
            "unit_type": "ton",
            "application_methods": ["broadcast", "banded"],
            "equipment_requirements": ["spreader", "drill"],
            "application_rate_range": {"min": 100.0, "max": 200.0},
            "organic_certified": False,
            "environmental_impact_score": 0.6,
            "soil_health_score": 0.3,
            "pros": ["High nitrogen content", "Cost effective", "Quick results", "Easy to handle"],
            "cons": ["Volatilization risk", "No soil health benefits", "Potential burn risk"],
            "application_notes": ["Incorporate within 24 hours", "Avoid hot, windy conditions"],
            "safety_considerations": ["Wear protective equipment", "Store in dry location"]
        },
        {
            "product_id": "dap_18_46_0",
            "name": "Diammonium Phosphate (18-46-0)",
            "manufacturer": "Generic",
            "fertilizer_type": "synthetic",
            "release_pattern": "immediate",
            "nutrient_content": {
                "nitrogen_percent": 18.0,
                "phosphorus_p2o5_percent": 46.0,
                "potassium_k2o_percent": 0.0,
                "sulfur_percent": 1.5
            },
            "cost_per_unit": 580.0,
            "unit_size": 2000.0,
            "unit_type": "ton",
            "application_methods": ["broadcast", "banded"],
            "equipment_requirements": ["spreader", "drill"],
            "application_rate_range": {"min": 80.0, "max": 150.0},
            "organic_certified": False,
            "environmental_impact_score": 0.65,
            "soil_health_score": 0.3,
            "pros": ["High phosphorus content", "Good starter fertilizer", "Reliable results"],
            "cons": ["Can tie up micronutrients", "No organic matter", "Acidifying effect"],
            "application_notes": ["Good for planting time application", "Band away from seed"],
            "safety_considerations": ["Avoid contact with skin", "Store in cool, dry place"]
        },
        
        # Organic Fertilizers
        {
            "product_id": "compost_2_1_1",
            "name": "Premium Compost (2-1-1)",
            "manufacturer": "Local Compost Co.",
            "fertilizer_type": "organic",
            "release_pattern": "organic_breakdown",
            "nutrient_content": {
                "nitrogen_percent": 2.0,
                "phosphorus_p2o5_percent": 1.0,
                "potassium_k2o_percent": 1.0,
                "calcium_percent": 1.5,
                "magnesium_percent": 0.5,
                "sulfur_percent": 0.3
            },
            "micronutrients": {
                "iron_percent": 0.1,
                "manganese_percent": 0.05,
                "zinc_percent": 0.02
            },
            "cost_per_unit": 45.0,
            "unit_size": 2000.0,
            "unit_type": "ton",
            "application_methods": ["broadcast", "incorporation"],
            "equipment_requirements": ["spreader", "tillage_equipment"],
            "application_rate_range": {"min": 2000.0, "max": 8000.0},
            "organic_certified": True,
            "environmental_impact_score": 0.9,
            "soil_health_score": 0.95,
            "soil_health_benefits": ["Improves soil structure", "Increases organic matter", 
                                   "Enhances microbial activity", "Improves water retention"],
            "pros": ["Builds soil health", "Slow nutrient release", "Improves soil structure", 
                    "Environmentally friendly"],
            "cons": ["Low nutrient content", "Bulky to handle", "Slow initial response", 
                    "Higher cost per nutrient unit"],
            "application_notes": ["Apply 1-4 tons per acre", "Incorporate for best results"],
            "storage_requirements": "Store in covered area to prevent nutrient loss",
            "shelf_life_months": 24,
            "safety_considerations": ["Wear dust mask when handling", "Avoid inhaling dust"]
        },
        {
            "product_id": "bone_meal_4_12_0",
            "name": "Bone Meal (4-12-0)",
            "manufacturer": "Organic Nutrients Inc.",
            "fertilizer_type": "organic",
            "release_pattern": "organic_breakdown",
            "nutrient_content": {
                "nitrogen_percent": 4.0,
                "phosphorus_p2o5_percent": 12.0,
                "potassium_k2o_percent": 0.0,
                "calcium_percent": 24.0
            },
            "cost_per_unit": 850.0,
            "unit_size": 50.0,
            "unit_type": "bag",
            "application_methods": ["broadcast", "banded"],
            "equipment_requirements": ["spreader"],
            "application_rate_range": {"min": 50.0, "max": 150.0},
            "organic_certified": True,
            "environmental_impact_score": 0.85,
            "soil_health_score": 0.8,
            "soil_health_benefits": ["Slow phosphorus release", "Adds calcium"],
            "pros": ["Organic phosphorus source", "Long-lasting", "Adds calcium"],
            "cons": ["Expensive", "Slow release", "Limited availability"],
            "application_notes": ["Apply in fall for spring benefit", "Work into soil"],
            "storage_requirements": "Store in dry location away from moisture",
            "shelf_life_months": 36,
            "safety_considerations": ["Wear gloves when handling", "Avoid inhaling dust"]
        },
        
        # Slow-Release Fertilizers
        {
            "product_id": "pcr_19_5_8",
            "name": "Polymer Coated Release (19-5-8)",
            "manufacturer": "Advanced Nutrients Corp.",
            "fertilizer_type": "slow_release",
            "release_pattern": "controlled",
            "nutrient_content": {
                "nitrogen_percent": 19.0,
                "phosphorus_p2o5_percent": 5.0,
                "potassium_k2o_percent": 8.0,
                "magnesium_percent": 1.0,
                "sulfur_percent": 3.0
            },
            "micronutrients": {
                "iron_percent": 0.5,
                "manganese_percent": 0.1
            },
            "cost_per_unit": 1200.0,
            "unit_size": 50.0,
            "unit_type": "bag",
            "application_methods": ["broadcast", "banded"],
            "equipment_requirements": ["spreader"],
            "application_rate_range": {"min": 200.0, "max": 400.0},
            "organic_certified": False,
            "slow_release": True,
            "environmental_impact_score": 0.75,
            "soil_health_score": 0.6,
            "soil_health_benefits": ["Reduces leaching", "Consistent feeding"],
            "pros": ["Controlled release", "Reduced applications", "Less leaching", "Consistent feeding"],
            "cons": ["High cost", "Temperature dependent", "Limited organic benefits"],
            "application_notes": ["Single season application", "Temperature affects release rate"],
            "storage_requirements": "Store in cool, dry place away from direct sunlight",
            "shelf_life_months": 24,
            "safety_considerations": ["Handle with care to avoid coating damage", "Wear protective equipment"]
        },
        
        # Liquid Fertilizers
        {
            "product_id": "uan_28_0_0",
            "name": "UAN Solution (28-0-0)",
            "manufacturer": "Liquid Fertilizer Solutions",
            "fertilizer_type": "liquid",
            "release_pattern": "immediate",
            "nutrient_content": {
                "nitrogen_percent": 28.0,
                "phosphorus_p2o5_percent": 0.0,
                "potassium_k2o_percent": 0.0
            },
            "cost_per_unit": 280.0,
            "unit_size": 2000.0,
            "unit_type": "ton",
            "application_methods": ["foliar_spray", "fertigation", "injection"],
            "equipment_requirements": ["sprayer", "injection_equipment", "fertigation_system"],
            "application_rate_range": {"min": 60.0, "max": 120.0},
            "organic_certified": False,
            "water_soluble": True,
            "environmental_impact_score": 0.65,
            "soil_health_score": 0.4,
            "pros": ["Uniform application", "Can mix with other inputs", "Flexible timing", 
                    "Good for side-dress"],
            "cons": ["Requires special equipment", "Corrosive", "Volatilization risk"],
            "application_notes": ["Avoid hot weather application", "Use proper safety equipment"],
            "storage_requirements": "Store in corrosion-resistant tanks, protect from freezing",
            "shelf_life_months": 12,
            "safety_considerations": ["Highly corrosive", "Wear full protective equipment", "Ensure proper ventilation"]
        }
    ]
    
    for product_data in fertilizer_products:
        # Check if product already exists
        existing_product = session.query(FertilizerProduct).filter_by(
            product_id=product_data["product_id"]
        ).first()
        
        if not existing_product:
            product = FertilizerProduct(**product_data)
            session.add(product)
            logger.info(f"Added fertilizer product: {product_data['name']}")
    
    session.commit()
    logger.info(f"Seeded {len(fertilizer_products)} fertilizer products")


def seed_equipment_compatibility(session: Session):
    """Seed database with equipment compatibility data."""
    
    equipment_data = [
        {
            "equipment_type": "spreader",
            "compatible_fertilizer_types": ["granular", "synthetic"],
            "compatible_application_methods": ["broadcast"],
            "limitations": ["Particle size matters", "Calibration required"],
            "recommendations": ["Regular calibration", "Check particle size compatibility"],
            "cost_range_min": 15000.0,
            "cost_range_max": 45000.0
        },
        {
            "equipment_type": "sprayer",
            "compatible_fertilizer_types": ["liquid", "foliar"],
            "compatible_application_methods": ["foliar_spray"],
            "limitations": ["Tank compatibility", "Nozzle selection"],
            "recommendations": ["Use compatible tank materials", "Select appropriate nozzles"],
            "cost_range_min": 25000.0,
            "cost_range_max": 85000.0
        },
        {
            "equipment_type": "drill",
            "compatible_fertilizer_types": ["granular", "synthetic"],
            "compatible_application_methods": ["banded"],
            "limitations": ["Seed placement", "Fertilizer separation"],
            "recommendations": ["Maintain proper seed-fertilizer separation", "Regular maintenance"],
            "cost_range_min": 35000.0,
            "cost_range_max": 120000.0
        },
        {
            "equipment_type": "fertigation_system",
            "compatible_fertilizer_types": ["liquid"],
            "compatible_application_methods": ["fertigation"],
            "limitations": ["Water quality", "System compatibility"],
            "recommendations": ["Monitor water quality", "Regular system maintenance"],
            "cost_range_min": 5000.0,
            "cost_range_max": 25000.0
        },
        {
            "equipment_type": "injection_equipment",
            "compatible_fertilizer_types": ["liquid"],
            "compatible_application_methods": ["injection"],
            "limitations": ["Soil conditions", "Timing critical"],
            "recommendations": ["Consider soil moisture", "Time applications properly"],
            "cost_range_min": 8000.0,
            "cost_range_max": 35000.0
        },
        {
            "equipment_type": "tillage_equipment",
            "compatible_fertilizer_types": ["organic"],
            "compatible_application_methods": ["incorporation"],
            "limitations": ["Soil conditions", "Timing requirements"],
            "recommendations": ["Proper soil moisture", "Timely incorporation"],
            "cost_range_min": 20000.0,
            "cost_range_max": 75000.0
        }
    ]
    
    for equipment in equipment_data:
        # Check if equipment already exists
        existing_equipment = session.query(EquipmentCompatibility).filter_by(
            equipment_type=equipment["equipment_type"]
        ).first()
        
        if not existing_equipment:
            equipment_obj = EquipmentCompatibility(**equipment)
            session.add(equipment_obj)
            logger.info(f"Added equipment compatibility: {equipment['equipment_type']}")
    
    session.commit()
    logger.info(f"Seeded {len(equipment_data)} equipment compatibility records")