#!/usr/bin/env python3
"""
Sample Data Insertion for Crop Taxonomy Service

Populates the PostgreSQL database with comprehensive sample crop data
including taxonomic hierarchy, agricultural classifications, and adaptations.
"""

import psycopg2
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://afas_user:secure_password@localhost:5432/afas_db')

# Sample crop data with complete taxonomic and agricultural information
SAMPLE_CROPS = [
    {
        'crop_name': 'Wheat',
        'scientific_name': 'Triticum aestivum',
        'taxonomic_hierarchy': {
            'kingdom': 'Plantae',
            'phylum': 'Tracheophyta',
            'class_name': 'Liliopsida',
            'order': 'Poales',
            'family': 'Poaceae',
            'genus': 'Triticum',
            'species': 'aestivum',
            'common_names': ['wheat', 'common wheat', 'bread wheat'],
            'botanical_authority': 'L.',
            'is_hybrid': False,
            'ploidy_level': 6,
            'chromosome_count': 42
        },
        'agricultural_classification': {
            'crop_category': 'grain',
            'primary_use': 'food_human',
            'plant_type': 'annual',
            'growth_habit': 'upright',
            'plant_height_range': [60, 120],
            'maturity_days_range': [90, 120],
            'harvest_index_range': [0.35, 0.55],
            'is_cover_crop': False,
            'is_cash_crop': True,
            'rotation_benefits': ['soil_structure_improvement'],
            'companion_plants': ['legumes'],
            'incompatible_plants': ['wild_oat']
        },
        'climate_adaptations': {
            'hardiness_zones': ['3', '4', '5', '6', '7'],
            'temperature_range': [-5, 35],
            'precipitation_range': [300, 800],
            'climate_zones': ['temperate', 'continental'],
            'drought_tolerance': 'moderate',
            'heat_tolerance': 'moderate',
            'cold_tolerance': 'high',
            'photoperiod_sensitivity': 'long_day',
            'seasonal_requirements': {'vernalization': True, 'cool_season': True},
            'elevation_range': [0, 3000]
        },
        'soil_requirements': {
            'ph_range': [6.0, 7.5],
            'preferred_textures': ['loam', 'clay_loam', 'silt_loam'],
            'drainage_requirement': 'well_drained',
            'organic_matter_range': [2.0, 4.0],
            'salinity_tolerance': 'low',
            'nutrient_requirements': {'nitrogen': 'high', 'phosphorus': 'moderate', 'potassium': 'moderate'},
            'soil_depth_requirements': [60, 150],
            'compaction_sensitivity': 'moderate'
        }
    },
    {
        'crop_name': 'Corn',
        'scientific_name': 'Zea mays',
        'taxonomic_hierarchy': {
            'kingdom': 'Plantae',
            'phylum': 'Tracheophyta',
            'class_name': 'Liliopsida',
            'order': 'Poales',
            'family': 'Poaceae',
            'genus': 'Zea',
            'species': 'mays',
            'common_names': ['corn', 'maize'],
            'botanical_authority': 'L.',
            'is_hybrid': False,
            'ploidy_level': 2,
            'chromosome_count': 20
        },
        'agricultural_classification': {
            'crop_category': 'grain',
            'primary_use': 'food_human',
            'plant_type': 'annual',
            'growth_habit': 'upright',
            'plant_height_range': [150, 300],
            'maturity_days_range': [60, 120],
            'harvest_index_range': [0.45, 0.65],
            'is_cover_crop': False,
            'is_cash_crop': True,
            'rotation_benefits': ['biomass_production'],
            'companion_plants': ['beans', 'squash'],
            'incompatible_plants': ['tomato']
        },
        'climate_adaptations': {
            'hardiness_zones': ['4', '5', '6', '7', '8', '9'],
            'temperature_range': [10, 40],
            'precipitation_range': [500, 1200],
            'climate_zones': ['temperate', 'subtropical'],
            'drought_tolerance': 'moderate',
            'heat_tolerance': 'high',
            'cold_tolerance': 'low',
            'photoperiod_sensitivity': 'short_day',
            'seasonal_requirements': {'warm_season': True},
            'elevation_range': [0, 2500]
        },
        'soil_requirements': {
            'ph_range': [6.0, 6.8],
            'preferred_textures': ['loam', 'silt_loam'],
            'drainage_requirement': 'well_drained',
            'organic_matter_range': [3.0, 6.0],
            'salinity_tolerance': 'moderate',
            'nutrient_requirements': {'nitrogen': 'high', 'phosphorus': 'high', 'potassium': 'high'},
            'soil_depth_requirements': [75, 200],
            'compaction_sensitivity': 'high'
        }
    },
    {
        'crop_name': 'Soybean',
        'scientific_name': 'Glycine max',
        'taxonomic_hierarchy': {
            'kingdom': 'Plantae',
            'phylum': 'Tracheophyta',
            'class_name': 'Magnoliopsida',
            'order': 'Fabales',
            'family': 'Fabaceae',
            'genus': 'Glycine',
            'species': 'max',
            'common_names': ['soybean', 'soya bean'],
            'botanical_authority': '(L.) Merr.',
            'is_hybrid': False,
            'ploidy_level': 2,
            'chromosome_count': 40
        },
        'agricultural_classification': {
            'crop_category': 'legume',
            'primary_use': 'food_human',
            'plant_type': 'annual',
            'growth_habit': 'upright',
            'plant_height_range': [30, 120],
            'maturity_days_range': [75, 140],
            'harvest_index_range': [0.40, 0.60],
            'is_cover_crop': False,
            'is_cash_crop': True,
            'rotation_benefits': ['nitrogen_fixation', 'soil_improvement'],
            'companion_plants': ['corn'],
            'incompatible_plants': ['sunflower']
        },
        'climate_adaptations': {
            'hardiness_zones': ['5', '6', '7', '8'],
            'temperature_range': [15, 35],
            'precipitation_range': [450, 700],
            'climate_zones': ['temperate', 'humid_continental'],
            'drought_tolerance': 'moderate',
            'heat_tolerance': 'moderate',
            'cold_tolerance': 'low',
            'photoperiod_sensitivity': 'short_day',
            'seasonal_requirements': {'warm_season': True},
            'elevation_range': [0, 1200]
        },
        'soil_requirements': {
            'ph_range': [6.0, 7.0],
            'preferred_textures': ['loam', 'silt_loam', 'clay_loam'],
            'drainage_requirement': 'well_drained',
            'organic_matter_range': [2.5, 4.0],
            'salinity_tolerance': 'low',
            'nutrient_requirements': {'nitrogen': 'low', 'phosphorus': 'moderate', 'potassium': 'moderate'},
            'soil_depth_requirements': [45, 120],
            'compaction_sensitivity': 'moderate'
        }
    },
    {
        'crop_name': 'Canola',
        'scientific_name': 'Brassica napus',
        'taxonomic_hierarchy': {
            'kingdom': 'Plantae',
            'phylum': 'Tracheophyta',
            'class_name': 'Magnoliopsida',
            'order': 'Brassicales',
            'family': 'Brassicaceae',
            'genus': 'Brassica',
            'species': 'napus',
            'common_names': ['canola', 'rapeseed', 'oilseed rape'],
            'botanical_authority': 'L.',
            'is_hybrid': False,
            'ploidy_level': 4,
            'chromosome_count': 38
        },
        'agricultural_classification': {
            'crop_category': 'oilseed',
            'primary_use': 'industrial',
            'plant_type': 'annual',
            'growth_habit': 'upright',
            'plant_height_range': [80, 160],
            'maturity_days_range': [90, 110],
            'harvest_index_range': [0.25, 0.45],
            'is_cover_crop': False,
            'is_cash_crop': True,
            'rotation_benefits': ['disease_break', 'soil_structure_improvement'],
            'companion_plants': ['cereals'],
            'incompatible_plants': ['other_brassicas']
        },
        'climate_adaptations': {
            'hardiness_zones': ['2', '3', '4', '5', '6'],
            'temperature_range': [-10, 25],
            'precipitation_range': [300, 600],
            'climate_zones': ['temperate', 'cool_temperate'],
            'drought_tolerance': 'moderate',
            'heat_tolerance': 'low',
            'cold_tolerance': 'high',
            'photoperiod_sensitivity': 'long_day',
            'seasonal_requirements': {'vernalization': True, 'cool_season': True},
            'elevation_range': [0, 2000]
        },
        'soil_requirements': {
            'ph_range': [6.0, 7.5],
            'preferred_textures': ['loam', 'clay_loam'],
            'drainage_requirement': 'well_drained',
            'organic_matter_range': [2.0, 4.0],
            'salinity_tolerance': 'low',
            'nutrient_requirements': {'nitrogen': 'high', 'phosphorus': 'moderate', 'potassium': 'moderate'},
            'soil_depth_requirements': [60, 120],
            'compaction_sensitivity': 'moderate'
        }
    },
    {
        'crop_name': 'Sunflower',
        'scientific_name': 'Helianthus annuus',
        'taxonomic_hierarchy': {
            'kingdom': 'Plantae',
            'phylum': 'Tracheophyta',
            'class_name': 'Magnoliopsida',
            'order': 'Asterales',
            'family': 'Asteraceae',
            'genus': 'Helianthus',
            'species': 'annuus',
            'common_names': ['sunflower', 'common sunflower'],
            'botanical_authority': 'L.',
            'is_hybrid': False,
            'ploidy_level': 2,
            'chromosome_count': 34
        },
        'agricultural_classification': {
            'crop_category': 'oilseed',
            'primary_use': 'industrial',
            'plant_type': 'annual',
            'growth_habit': 'upright',
            'plant_height_range': [150, 300],
            'maturity_days_range': [85, 120],
            'harvest_index_range': [0.20, 0.40],
            'is_cover_crop': False,
            'is_cash_crop': True,
            'rotation_benefits': ['deep_rooting', 'allelopathic_effects'],
            'companion_plants': ['corn'],
            'incompatible_plants': ['potato']
        },
        'climate_adaptations': {
            'hardiness_zones': ['4', '5', '6', '7', '8'],
            'temperature_range': [8, 35],
            'precipitation_range': [400, 700],
            'climate_zones': ['temperate', 'semiarid'],
            'drought_tolerance': 'high',
            'heat_tolerance': 'high',
            'cold_tolerance': 'low',
            'photoperiod_sensitivity': 'short_day',
            'seasonal_requirements': {'warm_season': True},
            'elevation_range': [0, 2000]
        },
        'soil_requirements': {
            'ph_range': [6.0, 7.5],
            'preferred_textures': ['loam', 'sandy_loam', 'clay_loam'],
            'drainage_requirement': 'well_drained',
            'organic_matter_range': [1.5, 3.0],
            'salinity_tolerance': 'moderate',
            'nutrient_requirements': {'nitrogen': 'moderate', 'phosphorus': 'moderate', 'potassium': 'high'},
            'soil_depth_requirements': [100, 200],
            'compaction_sensitivity': 'low'
        }
    }
]

def connect_to_database():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def insert_crop_data(conn, crop_data: Dict[str, Any]):
    """Insert comprehensive crop data into database tables."""
    cursor = conn.cursor()
    
    try:
        # Generate UUIDs for related records
        crop_id = str(uuid.uuid4())
        taxonomic_id = str(uuid.uuid4())
        agricultural_id = str(uuid.uuid4())
        climate_id = str(uuid.uuid4())
        soil_id = str(uuid.uuid4())
        
        # 1. Insert main crop record
        cursor.execute("""
            INSERT INTO crops (
                crop_id, crop_name, scientific_name, created_at, updated_at,
                taxonomic_hierarchy_id, agricultural_classification_id,
                climate_adaptations_id, soil_requirements_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            crop_id,
            crop_data['crop_name'],
            crop_data['scientific_name'],
            datetime.utcnow(),
            datetime.utcnow(),
            taxonomic_id,
            agricultural_id,
            climate_id,
            soil_id
        ))
        
        # 2. Insert taxonomic hierarchy
        tax = crop_data['taxonomic_hierarchy']
        cursor.execute("""
            INSERT INTO crop_taxonomic_hierarchy (
                id, kingdom, phylum, class_name, "order", family, genus, species,
                common_names, botanical_authority, is_hybrid, ploidy_level, chromosome_count,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            taxonomic_id,
            tax['kingdom'],
            tax['phylum'],
            tax['class_name'],
            tax['order'],
            tax['family'],
            tax['genus'],
            tax['species'],
            tax['common_names'],
            tax['botanical_authority'],
            tax['is_hybrid'],
            tax['ploidy_level'],
            tax['chromosome_count'],
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # 3. Insert agricultural classification
        ag = crop_data['agricultural_classification']
        cursor.execute("""
            INSERT INTO crop_agricultural_classification (
                id, crop_category, primary_use, plant_type, growth_habit,
                plant_height_range, maturity_days_range, harvest_index_range,
                is_cover_crop, is_cash_crop, rotation_benefits, companion_plants,
                incompatible_plants, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            agricultural_id,
            ag['crop_category'],
            ag['primary_use'],
            ag['plant_type'],
            ag['growth_habit'],
            ag['plant_height_range'],
            ag['maturity_days_range'],
            ag['harvest_index_range'],
            ag['is_cover_crop'],
            ag['is_cash_crop'],
            ag['rotation_benefits'],
            ag['companion_plants'],
            ag['incompatible_plants'],
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # 4. Insert climate adaptations
        climate = crop_data['climate_adaptations']
        cursor.execute("""
            INSERT INTO crop_climate_adaptations (
                id, hardiness_zones, temperature_range, precipitation_range,
                climate_zones, drought_tolerance, heat_tolerance, cold_tolerance,
                photoperiod_sensitivity, seasonal_requirements, elevation_range,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            climate_id,
            climate['hardiness_zones'],
            climate['temperature_range'],
            climate['precipitation_range'],
            climate['climate_zones'],
            climate['drought_tolerance'],
            climate['heat_tolerance'],
            climate['cold_tolerance'],
            climate['photoperiod_sensitivity'],
            climate.get('seasonal_requirements', {}),
            climate['elevation_range'],
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        # 5. Insert soil requirements
        soil = crop_data['soil_requirements']
        cursor.execute("""
            INSERT INTO crop_soil_requirements (
                id, ph_range, preferred_textures, drainage_requirement,
                organic_matter_range, salinity_tolerance, nutrient_requirements,
                soil_depth_requirements, compaction_sensitivity,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            soil_id,
            soil['ph_range'],
            soil['preferred_textures'],
            soil['drainage_requirement'],
            soil['organic_matter_range'],
            soil['salinity_tolerance'],
            soil.get('nutrient_requirements', {}),
            soil['soil_depth_requirements'],
            soil['compaction_sensitivity'],
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        print(f"✅ Successfully inserted {crop_data['crop_name']} ({crop_data['scientific_name']})")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting {crop_data['crop_name']}: {e}")
        cursor.execute("ROLLBACK")
        return False

def main():
    """Main function to populate database with sample crop data."""
    print("🌱 Starting crop taxonomy database population...")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    conn.autocommit = False  # Use transactions
    
    success_count = 0
    total_count = len(SAMPLE_CROPS)
    
    for crop_data in SAMPLE_CROPS:
        try:
            if insert_crop_data(conn, crop_data):
                conn.commit()
                success_count += 1
            else:
                conn.rollback()
        except Exception as e:
            print(f"❌ Transaction error for {crop_data['crop_name']}: {e}")
            conn.rollback()
    
    # Close connection
    conn.close()
    
    # Summary
    print(f"\n📊 Population Summary:")
    print(f"   Total crops processed: {total_count}")
    print(f"   Successfully inserted: {success_count}")
    print(f"   Failed insertions: {total_count - success_count}")
    
    if success_count == total_count:
        print("🎉 All sample crops successfully populated!")
    elif success_count > 0:
        print("⚠️  Partial success - some crops were inserted")
    else:
        print("❌ No crops were inserted successfully")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)