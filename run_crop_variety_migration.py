#!/usr/bin/env python3
"""
Crop Variety Database Migration Script
TICKET-005_crop-variety-recommendations-1.1

This script populates the enhanced_crop_varieties table with comprehensive variety data.
"""

import asyncio
import logging
import json
import uuid
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import database models and services
try:
    from databases.python.models import EnhancedCropVarieties, Crop
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, text
except ImportError as e:
    print(f"Error importing database modules: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CropVarietyMigration:
    """Crop variety database migration service."""
    
    def __init__(self, database_url: str = None):
        """Initialize the migration service."""
        self.database_url = database_url or os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/caain_soil_hub')
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def get_crop_id_by_name(self, crop_name: str) -> Optional[str]:
        """Get crop ID by crop name."""
        try:
            with self.Session() as session:
                crop = session.query(Crop).filter(Crop.crop_name.ilike(f"%{crop_name}%")).first()
                return str(crop.crop_id) if crop else None
        except Exception as e:
            logger.error(f"Error getting crop ID for {crop_name}: {e}")
            return None
    
    def load_variety_data_from_file(self, filename: str = "comprehensive_variety_data.json") -> List[Dict[str, Any]]:
        """Load variety data from JSON file."""
        try:
            with open(filename, 'r') as f:
                variety_data = json.load(f)
            logger.info(f"Loaded {len(variety_data)} variety records from {filename}")
            return variety_data
        except Exception as e:
            logger.error(f"Error loading variety data from file: {e}")
            return []
    
    def create_sample_variety_data(self) -> List[Dict[str, Any]]:
        """Create sample variety data for testing."""
        sample_data = [
            {
                "variety_name": "Pioneer P1197AMXT",
                "variety_code": "P1197AMXT",
                "breeder_company": "Pioneer",
                "relative_maturity": 119,
                "maturity_group": "119",
                "yield_potential_percentile": 95,
                "yield_stability_rating": 8.5,
                "market_acceptance_score": 4.2,
                "standability_rating": 8,
                "disease_resistances": {
                    "northern_corn_leaf_blight": "resistant",
                    "gray_leaf_spot": "moderately_resistant",
                    "rust": "resistant"
                },
                "herbicide_tolerances": ["glyphosate", "dicamba"],
                "stress_tolerances": ["drought", "heat"],
                "trait_stack": ["Roundup Ready 2", "XtendFlex"],
                "adapted_regions": ["Iowa", "Illinois", "Indiana"],
                "seed_availability": "widely_available",
                "seed_availability_status": "in_stock",
                "relative_seed_cost": "high",
                "release_year": 2020,
                "patent_status": "active",
                "crop_name": "corn"
            },
            {
                "variety_name": "Asgrow AG3431",
                "variety_code": "AG3431",
                "breeder_company": "Bayer/Asgrow",
                "relative_maturity": 33,
                "maturity_group": "3.3",
                "yield_potential_percentile": 92,
                "yield_stability_rating": 8.2,
                "market_acceptance_score": 4.0,
                "standability_rating": 8,
                "disease_resistances": {
                    "sudden_death_syndrome": "resistant",
                    "brown_stem_rot": "moderately_resistant"
                },
                "herbicide_tolerances": ["glyphosate"],
                "stress_tolerances": ["drought"],
                "trait_stack": ["Roundup Ready 2"],
                "adapted_regions": ["Illinois", "Indiana", "Ohio"],
                "seed_availability": "widely_available",
                "seed_availability_status": "in_stock",
                "relative_seed_cost": "moderate",
                "release_year": 2021,
                "patent_status": "active",
                "crop_name": "soybean"
            },
            {
                "variety_name": "USDA-ARS Wheat Variety 1",
                "variety_code": "USDA-W1",
                "breeder_company": "USDA-ARS",
                "relative_maturity": 95,
                "maturity_group": "95",
                "yield_potential_percentile": 85,
                "yield_stability_rating": 7.5,
                "market_acceptance_score": 3.8,
                "standability_rating": 8,
                "disease_resistances": {
                    "rust": "resistant",
                    "powdery_mildew": "moderately_resistant"
                },
                "herbicide_tolerances": ["glyphosate"],
                "stress_tolerances": ["drought", "cold"],
                "adapted_regions": ["Kansas", "Oklahoma", "Texas"],
                "seed_availability": "widely_available",
                "seed_availability_status": "in_stock",
                "relative_seed_cost": "low",
                "release_year": 2019,
                "patent_status": "none",
                "crop_name": "wheat"
            }
        ]
        
        # Add crop_id to all varieties
        for variety in sample_data:
            crop_id = self.get_crop_id_by_name(variety["crop_name"])
            variety["crop_id"] = crop_id
        
        return sample_data
    
    async def migrate_variety_data(self, variety_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Migrate variety data to the database."""
        saved_count = 0
        error_count = 0
        
        logger.info(f"Starting migration of {len(variety_data)} variety records")
        
        try:
            with self.Session() as session:
                for i, variety in enumerate(variety_data):
                    try:
                        # Skip if crop_id is None
                        if not variety.get("crop_id"):
                            logger.warning(f"Skipping variety {variety.get('variety_name', 'Unknown')} - no crop_id")
                            error_count += 1
                            continue
                        
                        # Check if variety already exists
                        existing = session.query(EnhancedCropVarieties).filter(
                            EnhancedCropVarieties.variety_name == variety["variety_name"],
                            EnhancedCropVarieties.crop_id == variety["crop_id"]
                        ).first()
                        
                        if existing:
                            logger.info(f"Variety {variety['variety_name']} already exists, skipping")
                            continue
                        
                        # Create enhanced variety record
                        enhanced_variety = EnhancedCropVarieties(
                            variety_id=uuid.uuid4(),
                            crop_id=variety["crop_id"],
                            variety_name=variety["variety_name"],
                            variety_code=variety.get("variety_code"),
                            breeder_company=variety.get("breeder_company"),
                            relative_maturity=variety.get("relative_maturity"),
                            maturity_group=variety.get("maturity_group"),
                            yield_potential_percentile=variety.get("yield_potential_percentile"),
                            yield_stability_rating=variety.get("yield_stability_rating"),
                            market_acceptance_score=variety.get("market_acceptance_score"),
                            standability_rating=variety.get("standability_rating"),
                            disease_resistances=variety.get("disease_resistances"),
                            pest_resistances=variety.get("pest_resistances"),
                            herbicide_tolerances=variety.get("herbicide_tolerances", []),
                            stress_tolerances=variety.get("stress_tolerances", []),
                            trait_stack=variety.get("trait_stack", []),
                            protein_content_range=variety.get("protein_content_range"),
                            oil_content_range=variety.get("oil_content_range"),
                            adapted_regions=variety.get("adapted_regions", []),
                            seed_availability=variety.get("seed_availability"),
                            seed_availability_status=variety.get("seed_availability_status"),
                            relative_seed_cost=variety.get("relative_seed_cost"),
                            release_year=variety.get("release_year"),
                            patent_status=variety.get("patent_status"),
                            regional_performance_data=variety.get("regional_performance_data", []),
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        session.add(enhanced_variety)
                        
                        # Commit in batches of 50
                        if (i + 1) % 50 == 0:
                            session.commit()
                            logger.info(f"Committed batch {i + 1}/{len(variety_data)}")
                        
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error saving variety {variety.get('variety_name', 'Unknown')}: {e}")
                        error_count += 1
                        session.rollback()
                
                # Commit remaining records
                session.commit()
                logger.info(f"Final commit completed")
                
        except Exception as e:
            logger.error(f"Error during batch migration: {e}")
            error_count += len(variety_data) - saved_count
        
        return {"saved": saved_count, "errors": error_count}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get current database statistics."""
        try:
            with self.Session() as session:
                stats = {
                    'total_crops': session.query(Crop).filter(Crop.crop_status == 'active').count(),
                    'total_varieties': session.query(EnhancedCropVarieties).filter(EnhancedCropVarieties.is_active == True).count(),
                    'varieties_by_crop': {}
                }
                
                # Get variety counts by crop
                for crop_name in ["corn", "soybean", "wheat", "cotton", "rice"]:
                    crop_id = self.get_crop_id_by_name(crop_name)
                    if crop_id:
                        count = session.query(EnhancedCropVarieties).filter(
                            EnhancedCropVarieties.crop_id == crop_id,
                            EnhancedCropVarieties.is_active == True
                        ).count()
                        stats['varieties_by_crop'][crop_name] = count
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_crops': 0, 'total_varieties': 0, 'varieties_by_crop': {}}
    
    async def run_migration(self, use_sample_data: bool = False) -> Dict[str, Any]:
        """Run the crop variety migration."""
        logger.info("Starting crop variety database migration")
        
        # Load variety data
        if use_sample_data:
            variety_data = self.create_sample_variety_data()
            logger.info("Using sample variety data")
        else:
            variety_data = self.load_variety_data_from_file()
            if not variety_data:
                logger.warning("No variety data loaded from file, using sample data")
                variety_data = self.create_sample_variety_data()
        
        # Get initial database stats
        initial_stats = self.get_database_stats()
        
        # Migrate data
        migration_results = await self.migrate_variety_data(variety_data)
        
        # Get final database stats
        final_stats = self.get_database_stats()
        
        results = {
            "varieties_processed": len(variety_data),
            "migration_results": migration_results,
            "initial_stats": initial_stats,
            "final_stats": final_stats,
            "varieties_added": final_stats['total_varieties'] - initial_stats['total_varieties'],
            "migration_status": "completed" if migration_results["errors"] == 0 else "completed_with_errors"
        }
        
        logger.info(f"Migration completed: {results}")
        return results

async def main():
    """Main function to run crop variety migration."""
    logger.info("Starting crop variety database migration")
    
    # Initialize migration service
    migration_service = CropVarietyMigration()
    
    # Run migration with sample data first
    logger.info("Running migration with sample data...")
    results = await migration_service.run_migration(use_sample_data=True)
    
    # Print results
    print("\n" + "="*60)
    print("CROP VARIETY DATABASE MIGRATION RESULTS")
    print("="*60)
    print(f"Varieties processed: {results['varieties_processed']}")
    print(f"Successfully saved: {results['migration_results']['saved']}")
    print(f"Errors: {results['migration_results']['errors']}")
    print(f"Varieties added: {results['varieties_added']}")
    print(f"Migration status: {results['migration_status']}")
    
    print(f"\nInitial database stats:")
    print(f"  Total crops: {results['initial_stats']['total_crops']}")
    print(f"  Total varieties: {results['initial_stats']['total_varieties']}")
    
    print(f"\nFinal database stats:")
    print(f"  Total crops: {results['final_stats']['total_crops']}")
    print(f"  Total varieties: {results['final_stats']['total_varieties']}")
    
    print(f"\nVarieties by crop:")
    for crop, count in results['final_stats']['varieties_by_crop'].items():
        print(f"  {crop}: {count}")
    
    print("="*60)
    
    if results['final_stats']['total_varieties'] >= 1000:
        print("\n✅ SUCCESS: Target of 1000+ varieties achieved!")
    else:
        print(f"\n⚠️  WARNING: Only {results['final_stats']['total_varieties']} varieties in database. Target is 1000+")

if __name__ == "__main__":
    asyncio.run(main())