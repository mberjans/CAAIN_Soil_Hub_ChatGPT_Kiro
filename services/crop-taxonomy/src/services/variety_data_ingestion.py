"""
Crop Variety Data Ingestion Service
TICKET-005_crop-variety-recommendations-1.1

This service handles ingestion of crop variety data from multiple sources:
- University variety trial data
- Seed company catalogs
- USDA variety databases
- Regional extension services
"""

import logging
import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class DataSource(str, Enum):
    """Enumeration of data sources for variety information."""
    UNIVERSITY_TRIAL = "university_trial"
    SEED_COMPANY = "seed_company"
    USDA_DATABASE = "usda_database"
    EXTENSION_SERVICE = "extension_service"
    RESEARCH_STATION = "research_station"
    FARMER_FEEDBACK = "farmer_feedback"

class VarietyDataQuality(str, Enum):
    """Data quality assessment levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNVERIFIED = "unverified"

@dataclass
class VarietyDataRecord:
    """Structure for variety data records from external sources."""
    
    # Core identification
    variety_name: str
    crop_name: str
    breeder_company: Optional[str] = None
    variety_code: Optional[str] = None
    
    # Performance data
    yield_potential_percentile: Optional[int] = None
    yield_stability_rating: Optional[float] = None
    market_acceptance_score: Optional[float] = None
    
    # Maturity and timing
    relative_maturity: Optional[int] = None
    maturity_group: Optional[str] = None
    days_to_emergence: Optional[int] = None
    days_to_flowering: Optional[int] = None
    days_to_physiological_maturity: Optional[int] = None
    
    # Resistance traits
    disease_resistances: Optional[Dict[str, Any]] = None
    pest_resistances: Optional[Dict[str, Any]] = None
    herbicide_tolerances: Optional[List[str]] = None
    stress_tolerances: Optional[List[str]] = None
    
    # Quality traits
    protein_content_range: Optional[str] = None
    oil_content_range: Optional[str] = None
    quality_characteristics: Optional[Dict[str, Any]] = None
    
    # Commercial information
    seed_availability: Optional[str] = None
    seed_availability_status: Optional[str] = None
    relative_seed_cost: Optional[str] = None
    release_year: Optional[int] = None
    
    # Regional data
    adapted_regions: Optional[List[str]] = None
    regional_performance_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    data_source: DataSource = DataSource.UNIVERSITY_TRIAL
    data_quality: VarietyDataQuality = VarietyDataQuality.UNVERIFIED
    source_url: Optional[str] = None
    last_updated: Optional[datetime] = None
    validation_notes: Optional[str] = None

class VarietyDataIngestionService:
    """Service for ingesting crop variety data from multiple sources."""
    
    def __init__(self, database_manager=None):
        """Initialize the ingestion service."""
        self.database_manager = database_manager
        self.session = None
        self.data_sources = {
            DataSource.UNIVERSITY_TRIAL: self._ingest_university_data,
            DataSource.SEED_COMPANY: self._ingest_seed_company_data,
            DataSource.USDA_DATABASE: self._ingest_usda_data,
            DataSource.EXTENSION_SERVICE: self._ingest_extension_data,
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def ingest_from_source(self, source: DataSource, source_config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """
        Ingest variety data from a specific source.
        
        Args:
            source: The data source type
            source_config: Configuration for the data source
            
        Returns:
            List of variety data records
        """
        logger.info(f"Starting data ingestion from {source.value}")
        
        try:
            if source in self.data_sources:
                records = await self.data_sources[source](source_config)
                logger.info(f"Successfully ingested {len(records)} records from {source.value}")
                return records
            else:
                logger.error(f"Unknown data source: {source}")
                return []
                
        except Exception as e:
            logger.error(f"Error ingesting data from {source.value}: {e}")
            return []
    
    async def _ingest_university_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Ingest variety trial data from university sources."""
        records = []
        
        # Example: Iowa State University Corn Variety Trials
        if config.get("source") == "iowa_state_corn":
            records.extend(await self._parse_iowa_state_corn_data(config))
        
        # Example: University of Illinois Soybean Trials
        elif config.get("source") == "illinois_soybean":
            records.extend(await self._parse_illinois_soybean_data(config))
            
        return records
    
    async def _parse_iowa_state_corn_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Parse Iowa State University corn variety trial data."""
        records = []
        
        # This would typically fetch from ISU's API or parse CSV files
        # For now, we'll create sample data structure
        
        sample_data = [
            {
                "variety_name": "Pioneer P1197AMXT",
                "breeder_company": "Pioneer",
                "relative_maturity": 119,
                "yield_potential_percentile": 95,
                "yield_stability_rating": 8.5,
                "disease_resistances": {
                    "northern_corn_leaf_blight": "resistant",
                    "gray_leaf_spot": "moderately_resistant",
                    "rust": "resistant"
                },
                "herbicide_tolerances": ["glyphosate", "dicamba"],
                "adapted_regions": ["Iowa", "Illinois", "Indiana"],
                "release_year": 2020
            },
            {
                "variety_name": "Dekalb DKC62-08",
                "breeder_company": "Bayer/Dekalb",
                "relative_maturity": 108,
                "yield_potential_percentile": 88,
                "yield_stability_rating": 7.8,
                "disease_resistances": {
                    "northern_corn_leaf_blight": "moderately_resistant",
                    "gray_leaf_spot": "resistant"
                },
                "herbicide_tolerances": ["glyphosate"],
                "adapted_regions": ["Iowa", "Nebraska"],
                "release_year": 2019
            }
        ]
        
        for data in sample_data:
            record = VarietyDataRecord(
                variety_name=data["variety_name"],
                crop_name="corn",
                breeder_company=data["breeder_company"],
                relative_maturity=data["relative_maturity"],
                yield_potential_percentile=data["yield_potential_percentile"],
                yield_stability_rating=data["yield_stability_rating"],
                disease_resistances=data["disease_resistances"],
                herbicide_tolerances=data["herbicide_tolerances"],
                adapted_regions=data["adapted_regions"],
                release_year=data["release_year"],
                data_source=DataSource.UNIVERSITY_TRIAL,
                data_quality=VarietyDataQuality.HIGH,
                source_url="https://www.extension.iastate.edu/corn/",
                last_updated=datetime.now()
            )
            records.append(record)
        
        return records
    
    async def _parse_illinois_soybean_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Parse University of Illinois soybean variety trial data."""
        records = []
        
        sample_data = [
            {
                "variety_name": "Asgrow AG3431",
                "breeder_company": "Bayer/Asgrow",
                "relative_maturity": 3.3,
                "yield_potential_percentile": 92,
                "yield_stability_rating": 8.2,
                "disease_resistances": {
                    "sudden_death_syndrome": "resistant",
                    "brown_stem_rot": "moderately_resistant"
                },
                "herbicide_tolerances": ["glyphosate"],
                "adapted_regions": ["Illinois", "Indiana", "Ohio"],
                "release_year": 2021
            }
        ]
        
        for data in sample_data:
            record = VarietyDataRecord(
                variety_name=data["variety_name"],
                crop_name="soybean",
                breeder_company=data["breeder_company"],
                relative_maturity=int(data["relative_maturity"] * 10),  # Convert to integer
                yield_potential_percentile=data["yield_potential_percentile"],
                yield_stability_rating=data["yield_stability_rating"],
                disease_resistances=data["disease_resistances"],
                herbicide_tolerances=data["herbicide_tolerances"],
                adapted_regions=data["adapted_regions"],
                release_year=data["release_year"],
                data_source=DataSource.UNIVERSITY_TRIAL,
                data_quality=VarietyDataQuality.HIGH,
                source_url="https://extension.illinois.edu/soybean/",
                last_updated=datetime.now()
            )
            records.append(record)
        
        return records
    
    async def _ingest_seed_company_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Ingest variety data from seed company sources."""
        records = []
        
        # This would typically integrate with seed company APIs
        # For now, we'll create sample data
        
        sample_data = [
            {
                "variety_name": "Syngenta NK603",
                "breeder_company": "Syngenta",
                "relative_maturity": 105,
                "yield_potential_percentile": 90,
                "disease_resistances": {
                    "corn_rootworm": "resistant"
                },
                "herbicide_tolerances": ["glyphosate"],
                "seed_availability": "widely_available",
                "seed_availability_status": "in_stock",
                "relative_seed_cost": "moderate",
                "release_year": 2020
            }
        ]
        
        for data in sample_data:
            record = VarietyDataRecord(
                variety_name=data["variety_name"],
                crop_name="corn",
                breeder_company=data["breeder_company"],
                relative_maturity=data["relative_maturity"],
                yield_potential_percentile=data["yield_potential_percentile"],
                disease_resistances=data["disease_resistances"],
                herbicide_tolerances=data["herbicide_tolerances"],
                seed_availability=data["seed_availability"],
                seed_availability_status=data["seed_availability_status"],
                relative_seed_cost=data["relative_seed_cost"],
                release_year=data["release_year"],
                data_source=DataSource.SEED_COMPANY,
                data_quality=VarietyDataQuality.MEDIUM,
                last_updated=datetime.now()
            )
            records.append(record)
        
        return records
    
    async def _ingest_usda_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Ingest variety data from USDA databases."""
        records = []
        
        # This would integrate with USDA variety databases
        # For now, we'll create sample data
        
        sample_data = [
            {
                "variety_name": "USDA-ARS Wheat Variety 1",
                "breeder_company": "USDA-ARS",
                "relative_maturity": 95,
                "yield_potential_percentile": 85,
                "disease_resistances": {
                    "rust": "resistant",
                    "powdery_mildew": "moderately_resistant"
                },
                "adapted_regions": ["Kansas", "Oklahoma", "Texas"],
                "release_year": 2019
            }
        ]
        
        for data in sample_data:
            record = VarietyDataRecord(
                variety_name=data["variety_name"],
                crop_name="wheat",
                breeder_company=data["breeder_company"],
                relative_maturity=data["relative_maturity"],
                yield_potential_percentile=data["yield_potential_percentile"],
                disease_resistances=data["disease_resistances"],
                adapted_regions=data["adapted_regions"],
                release_year=data["release_year"],
                data_source=DataSource.USDA_DATABASE,
                data_quality=VarietyDataQuality.HIGH,
                last_updated=datetime.now()
            )
            records.append(record)
        
        return records
    
    async def _ingest_extension_data(self, config: Dict[str, Any]) -> List[VarietyDataRecord]:
        """Ingest variety data from extension services."""
        records = []
        
        # This would integrate with extension service databases
        # For now, we'll create sample data
        
        sample_data = [
            {
                "variety_name": "Extension Recommended Cotton 1",
                "breeder_company": "Various",
                "relative_maturity": 120,
                "yield_potential_percentile": 88,
                "disease_resistances": {
                    "bacterial_blight": "resistant"
                },
                "adapted_regions": ["Georgia", "Alabama", "Mississippi"],
                "release_year": 2020
            }
        ]
        
        for data in sample_data:
            record = VarietyDataRecord(
                variety_name=data["variety_name"],
                crop_name="cotton",
                breeder_company=data["breeder_company"],
                relative_maturity=data["relative_maturity"],
                yield_potential_percentile=data["yield_potential_percentile"],
                disease_resistances=data["disease_resistances"],
                adapted_regions=data["adapted_regions"],
                release_year=data["release_year"],
                data_source=DataSource.EXTENSION_SERVICE,
                data_quality=VarietyDataQuality.MEDIUM,
                last_updated=datetime.now()
            )
            records.append(record)
        
        return records
    
    def validate_variety_data(self, record: VarietyDataRecord) -> bool:
        """
        Validate variety data record for completeness and accuracy.
        
        Args:
            record: Variety data record to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not record.variety_name or not record.crop_name:
            logger.warning(f"Missing required fields for variety: {record.variety_name}")
            return False
        
        # Validate numeric ranges
        if record.yield_potential_percentile and not (0 <= record.yield_potential_percentile <= 100):
            logger.warning(f"Invalid yield percentile for variety: {record.variety_name}")
            return False
        
        if record.yield_stability_rating and not (0 <= record.yield_stability_rating <= 10):
            logger.warning(f"Invalid yield stability rating for variety: {record.variety_name}")
            return False
        
        if record.market_acceptance_score and not (0 <= record.market_acceptance_score <= 5):
            logger.warning(f"Invalid market acceptance score for variety: {record.variety_name}")
            return False
        
        return True
    
    async def save_variety_records(self, records: List[VarietyDataRecord]) -> Dict[str, int]:
        """
        Save variety records to the database.
        
        Args:
            records: List of variety data records to save
            
        Returns:
            Dictionary with save statistics
        """
        if not self.database_manager:
            logger.error("Database manager not available")
            return {"saved": 0, "errors": len(records)}
        
        saved_count = 0
        error_count = 0
        
        for record in records:
            try:
                if self.validate_variety_data(record):
                    # Convert to database format and save
                    await self._save_single_record(record)
                    saved_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Error saving variety {record.variety_name}: {e}")
                error_count += 1
        
        return {"saved": saved_count, "errors": error_count}
    
    async def _save_single_record(self, record: VarietyDataRecord):
        """Save a single variety record to the database."""
        # This would use the database manager to save the record
        # For now, we'll just log the action
        logger.info(f"Saving variety record: {record.variety_name} from {record.data_source.value}")
        
        # In a real implementation, this would:
        # 1. Find or create the crop record
        # 2. Create the enhanced variety record
        # 3. Handle conflicts and updates
        # 4. Update data quality metrics

class VarietyDataIngestionPipeline:
    """Pipeline for orchestrating variety data ingestion from multiple sources."""
    
    def __init__(self, database_manager=None):
        """Initialize the ingestion pipeline."""
        self.database_manager = database_manager
        self.ingestion_service = VarietyDataIngestionService(database_manager)
        
    async def run_full_ingestion(self, sources_config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run full variety data ingestion from all configured sources.
        
        Args:
            sources_config: Configuration for each data source
            
        Returns:
            Summary of ingestion results
        """
        logger.info("Starting full variety data ingestion pipeline")
        
        all_records = []
        source_results = {}
        
        async with self.ingestion_service as service:
            for source_name, config in sources_config.items():
                try:
                    source = DataSource(source_name)
                    records = await service.ingest_from_source(source, config)
                    all_records.extend(records)
                    source_results[source_name] = {
                        "records_ingested": len(records),
                        "status": "success"
                    }
                except Exception as e:
                    logger.error(f"Error ingesting from {source_name}: {e}")
                    source_results[source_name] = {
                        "records_ingested": 0,
                        "status": "error",
                        "error": str(e)
                    }
        
        # Save all records
        save_results = await self.ingestion_service.save_variety_records(all_records)
        
        return {
            "total_records": len(all_records),
            "source_results": source_results,
            "save_results": save_results,
            "pipeline_status": "completed" if save_results["errors"] == 0 else "completed_with_errors"
        }

# Example usage and configuration
async def main():
    """Example usage of the variety data ingestion pipeline."""
    
    # Configuration for different data sources
    sources_config = {
        "university_trial": {
            "source": "iowa_state_corn",
            "api_url": "https://api.iastate.edu/corn-trials",
            "api_key": "your_api_key_here"
        },
        "seed_company": {
            "companies": ["pioneer", "bayer", "syngenta"],
            "api_endpoints": {
                "pioneer": "https://api.pioneer.com/varieties",
                "bayer": "https://api.bayer.com/varieties"
            }
        },
        "usda_database": {
            "database_url": "https://data.usda.gov/api/varieties",
            "crop_types": ["corn", "soybean", "wheat", "cotton"]
        }
    }
    
    # Initialize pipeline
    pipeline = VarietyDataIngestionPipeline()
    
    # Run ingestion
    results = await pipeline.run_full_ingestion(sources_config)
    
    print(f"Ingestion completed:")
    print(f"Total records: {results['total_records']}")
    print(f"Saved: {results['save_results']['saved']}")
    print(f"Errors: {results['save_results']['errors']}")

if __name__ == "__main__":
    asyncio.run(main())