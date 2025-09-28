"""
Seed Company Integration Service

Service for automated integration with major seed company databases and APIs,
providing real-time variety data synchronization, availability tracking, and
comprehensive seed company information management.
"""

import asyncio
import logging
import aiohttp
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from uuid import UUID
import json
import hashlib
from dataclasses import dataclass
from enum import Enum

try:
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        SeedCompanyOffering,
        SeedAvailabilityStatus,
        VarietyDataRecord,
        DataSource,
        VarietyDataQuality
    )
    from ..models.service_models import (
        ValidationResult,
        DataQualityScore
    )
    from ..database.crop_taxonomy_db import CropTaxonomyDatabase
except ImportError:
    from models.crop_variety_models import (
        EnhancedCropVariety,
        SeedCompanyOffering,
        SeedAvailabilityStatus,
        VarietyDataRecord,
        DataSource,
        VarietyDataQuality
    )
    from models.service_models import (
        ValidationResult,
        DataQualityScore
    )

logger = logging.getLogger(__name__)


class SeedCompanyType(str, Enum):
    """Types of seed companies."""
    MAJOR_CORPORATE = "major_corporate"
    REGIONAL = "regional"
    SPECIALTY = "specialty"
    RESEARCH = "research"


class SyncStatus(str, Enum):
    """Data synchronization status."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class SeedCompanyConfig:
    """Configuration for a seed company integration."""
    company_name: str
    company_type: SeedCompanyType
    api_endpoint: Optional[str]
    api_key: Optional[str]
    rate_limit_per_minute: int
    data_fields: List[str]
    update_frequency_hours: int
    last_sync: Optional[datetime]
    sync_status: SyncStatus
    error_count: int
    max_retries: int


@dataclass
class VarietyUpdateRecord:
    """Record of variety data updates from seed companies."""
    variety_id: UUID
    company_name: str
    update_type: str  # 'new', 'updated', 'discontinued'
    changes: Dict[str, Any]
    timestamp: datetime
    data_hash: str


class SeedCompanyProvider:
    """Base class for seed company data providers."""
    
    def __init__(self, config: SeedCompanyConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_variety_data(self) -> List[Dict[str, Any]]:
        """Fetch variety data from the seed company."""
        raise NotImplementedError("Subclasses must implement fetch_variety_data")
    
    def normalize_variety_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize variety data to standard format."""
        raise NotImplementedError("Subclasses must implement normalize_variety_data")


class PioneerProvider(SeedCompanyProvider):
    """Pioneer/Corteva seed company data provider."""
    
    async def fetch_variety_data(self) -> List[Dict[str, Any]]:
        """Fetch variety data from Pioneer/Corteva."""
        try:
            session = await self.get_session()
            
            # Mock API call - in production, this would be real Pioneer API
            # Pioneer typically provides variety data through their dealer portal
            mock_data = [
                {
                    "variety_name": "Pioneer P1234",
                    "variety_code": "P1234",
                    "breeder_company": "Pioneer/Corteva",
                    "relative_maturity": 105,
                    "yield_potential_percentile": 92,
                    "disease_resistances": {
                        "corn_rootworm": "resistant",
                        "corn_borer": "moderate_resistance"
                    },
                    "herbicide_tolerances": ["glyphosate", "glufosinate"],
                    "seed_availability": "widely_available",
                    "seed_availability_status": "in_stock",
                    "relative_seed_cost": "high",
                    "release_year": 2021,
                    "technology_package": "Roundup Ready 2 Xtend"
                },
                {
                    "variety_name": "Pioneer P5678",
                    "variety_code": "P5678", 
                    "breeder_company": "Pioneer/Corteva",
                    "relative_maturity": 110,
                    "yield_potential_percentile": 88,
                    "disease_resistances": {
                        "corn_rootworm": "resistant",
                        "corn_borer": "resistant"
                    },
                    "herbicide_tolerances": ["glyphosate"],
                    "seed_availability": "limited",
                    "seed_availability_status": "preorder",
                    "relative_seed_cost": "moderate",
                    "release_year": 2022,
                    "technology_package": "Roundup Ready 2"
                }
            ]
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error fetching Pioneer data: {e}")
            return []
    
    def normalize_variety_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Pioneer variety data to standard format."""
        return {
            "variety_name": raw_data.get("variety_name"),
            "variety_code": raw_data.get("variety_code"),
            "breeder_company": raw_data.get("breeder_company", "Pioneer/Corteva"),
            "relative_maturity": raw_data.get("relative_maturity"),
            "yield_potential_percentile": raw_data.get("yield_potential_percentile"),
            "disease_resistances": raw_data.get("disease_resistances", {}),
            "herbicide_tolerances": raw_data.get("herbicide_tolerances", []),
            "seed_availability": raw_data.get("seed_availability"),
            "seed_availability_status": raw_data.get("seed_availability_status"),
            "relative_seed_cost": raw_data.get("relative_seed_cost"),
            "release_year": raw_data.get("release_year"),
            "technology_package": raw_data.get("technology_package"),
            "data_source": DataSource.SEED_COMPANY,
            "data_quality": VarietyDataQuality.HIGH,
            "last_updated": datetime.now()
        }


class BayerProvider(SeedCompanyProvider):
    """Bayer/Dekalb seed company data provider."""
    
    async def fetch_variety_data(self) -> List[Dict[str, Any]]:
        """Fetch variety data from Bayer/Dekalb."""
        try:
            # Mock API call - in production, this would be real Bayer API
            mock_data = [
                {
                    "variety_name": "Dekalb DKC1234",
                    "variety_code": "DKC1234",
                    "breeder_company": "Bayer/Dekalb",
                    "relative_maturity": 108,
                    "yield_potential_percentile": 90,
                    "disease_resistances": {
                        "corn_rootworm": "resistant",
                        "corn_borer": "resistant",
                        "gray_leaf_spot": "moderate_resistance"
                    },
                    "herbicide_tolerances": ["glyphosate", "dicamba"],
                    "seed_availability": "widely_available",
                    "seed_availability_status": "in_stock",
                    "relative_seed_cost": "high",
                    "release_year": 2020,
                    "technology_package": "Roundup Ready 2 Xtend"
                }
            ]
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error fetching Bayer data: {e}")
            return []
    
    def normalize_variety_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Bayer variety data to standard format."""
        return {
            "variety_name": raw_data.get("variety_name"),
            "variety_code": raw_data.get("variety_code"),
            "breeder_company": raw_data.get("breeder_company", "Bayer/Dekalb"),
            "relative_maturity": raw_data.get("relative_maturity"),
            "yield_potential_percentile": raw_data.get("yield_potential_percentile"),
            "disease_resistances": raw_data.get("disease_resistances", {}),
            "herbicide_tolerances": raw_data.get("herbicide_tolerances", []),
            "seed_availability": raw_data.get("seed_availability"),
            "seed_availability_status": raw_data.get("seed_availability_status"),
            "relative_seed_cost": raw_data.get("relative_seed_cost"),
            "release_year": raw_data.get("release_year"),
            "technology_package": raw_data.get("technology_package"),
            "data_source": DataSource.SEED_COMPANY,
            "data_quality": VarietyDataQuality.HIGH,
            "last_updated": datetime.now()
        }


class SyngentaProvider(SeedCompanyProvider):
    """Syngenta seed company data provider."""
    
    async def fetch_variety_data(self) -> List[Dict[str, Any]]:
        """Fetch variety data from Syngenta."""
        try:
            # Mock API call - in production, this would be real Syngenta API
            mock_data = [
                {
                    "variety_name": "Syngenta NK603",
                    "variety_code": "NK603",
                    "breeder_company": "Syngenta",
                    "relative_maturity": 105,
                    "yield_potential_percentile": 85,
                    "disease_resistances": {
                        "corn_rootworm": "moderate_resistance",
                        "corn_borer": "resistant"
                    },
                    "herbicide_tolerances": ["glyphosate"],
                    "seed_availability": "widely_available",
                    "seed_availability_status": "in_stock",
                    "relative_seed_cost": "moderate",
                    "release_year": 2019,
                    "technology_package": "Roundup Ready"
                }
            ]
            
            return mock_data
            
        except Exception as e:
            logger.error(f"Error fetching Syngenta data: {e}")
            return []
    
    def normalize_variety_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Syngenta variety data to standard format."""
        return {
            "variety_name": raw_data.get("variety_name"),
            "variety_code": raw_data.get("variety_code"),
            "breeder_company": raw_data.get("breeder_company", "Syngenta"),
            "relative_maturity": raw_data.get("relative_maturity"),
            "yield_potential_percentile": raw_data.get("yield_potential_percentile"),
            "disease_resistances": raw_data.get("disease_resistances", {}),
            "herbicide_tolerances": raw_data.get("herbicide_tolerances", []),
            "seed_availability": raw_data.get("seed_availability"),
            "seed_availability_status": raw_data.get("seed_availability_status"),
            "relative_seed_cost": raw_data.get("relative_seed_cost"),
            "release_year": raw_data.get("release_year"),
            "technology_package": raw_data.get("technology_package"),
            "data_source": DataSource.SEED_COMPANY,
            "data_quality": VarietyDataQuality.HIGH,
            "last_updated": datetime.now()
        }


class SeedCompanyIntegrationService:
    """
    Service for automated integration with seed company databases and APIs.
    
    Features:
    - Real-time variety data synchronization
    - Automated data updates and change detection
    - Data normalization and validation
    - Conflict resolution and data provenance tracking
    - Rate limiting and API compliance
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the seed company integration service."""
        try:
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Seed company service database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available for seed company service")
            self.db = None
            self.database_available = False
        
        # Initialize seed company configurations
        self.company_configs = self._initialize_company_configs()
        self.providers = self._initialize_providers()
        self.sync_history = []
        
    def _initialize_company_configs(self) -> Dict[str, SeedCompanyConfig]:
        """Initialize configurations for major seed companies."""
        return {
            "pioneer": SeedCompanyConfig(
                company_name="Pioneer/Corteva",
                company_type=SeedCompanyType.MAJOR_CORPORATE,
                api_endpoint="https://api.pioneer.com/varieties",  # Mock endpoint
                api_key=None,  # Would be provided via environment variables
                rate_limit_per_minute=60,
                data_fields=["variety_name", "maturity", "yield", "traits", "availability"],
                update_frequency_hours=24,
                last_sync=None,
                sync_status=SyncStatus.PENDING,
                error_count=0,
                max_retries=3
            ),
            "bayer": SeedCompanyConfig(
                company_name="Bayer/Dekalb",
                company_type=SeedCompanyType.MAJOR_CORPORATE,
                api_endpoint="https://api.bayer.com/dekalb/varieties",  # Mock endpoint
                api_key=None,
                rate_limit_per_minute=60,
                data_fields=["variety_name", "maturity", "yield", "traits", "availability"],
                update_frequency_hours=24,
                last_sync=None,
                sync_status=SyncStatus.PENDING,
                error_count=0,
                max_retries=3
            ),
            "syngenta": SeedCompanyConfig(
                company_name="Syngenta",
                company_type=SeedCompanyType.MAJOR_CORPORATE,
                api_endpoint="https://api.syngenta.com/varieties",  # Mock endpoint
                api_key=None,
                rate_limit_per_minute=60,
                data_fields=["variety_name", "maturity", "yield", "traits", "availability"],
                update_frequency_hours=24,
                last_sync=None,
                sync_status=SyncStatus.PENDING,
                error_count=0,
                max_retries=3
            )
        }
    
    def _initialize_providers(self) -> Dict[str, SeedCompanyProvider]:
        """Initialize seed company data providers."""
        return {
            "pioneer": PioneerProvider(self.company_configs["pioneer"]),
            "bayer": BayerProvider(self.company_configs["bayer"]),
            "syngenta": SyngentaProvider(self.company_configs["syngenta"])
        }
    
    async def sync_all_companies(self) -> Dict[str, SyncStatus]:
        """
        Synchronize data from all configured seed companies.
        
        Returns:
            Dictionary mapping company names to sync status
        """
        sync_results = {}
        
        for company_name, provider in self.providers.items():
            try:
                logger.info(f"Starting sync for {company_name}")
                status = await self._sync_company_data(company_name, provider)
                sync_results[company_name] = status
                
                # Update configuration
                self.company_configs[company_name].last_sync = datetime.now()
                self.company_configs[company_name].sync_status = status
                
            except Exception as e:
                logger.error(f"Error syncing {company_name}: {e}")
                sync_results[company_name] = SyncStatus.FAILED
                self.company_configs[company_name].error_count += 1
        
        return sync_results
    
    async def _sync_company_data(self, company_name: str, provider: SeedCompanyProvider) -> SyncStatus:
        """
        Synchronize data from a specific seed company.
        
        Args:
            company_name: Name of the seed company
            provider: Provider instance for the company
            
        Returns:
            Sync status for the operation
        """
        try:
            # Fetch variety data from the company
            raw_varieties = await provider.fetch_variety_data()
            
            if not raw_varieties:
                logger.warning(f"No variety data received from {company_name}")
                return SyncStatus.FAILED
            
            # Process and normalize the data
            processed_varieties = []
            for raw_variety in raw_varieties:
                try:
                    normalized_data = provider.normalize_variety_data(raw_variety)
                    processed_varieties.append(normalized_data)
                except Exception as e:
                    logger.error(f"Error normalizing variety data from {company_name}: {e}")
                    continue
            
            # Update database with new data
            if self.database_available:
                update_result = await self._update_database_varieties(
                    company_name, processed_varieties
                )
                
                if update_result["success"]:
                    logger.info(f"Successfully synced {len(processed_varieties)} varieties from {company_name}")
                    return SyncStatus.SUCCESS
                else:
                    logger.error(f"Database update failed for {company_name}: {update_result['error']}")
                    return SyncStatus.FAILED
            else:
                logger.warning(f"Database not available, skipping update for {company_name}")
                return SyncStatus.PARTIAL
                
        except Exception as e:
            logger.error(f"Error in sync for {company_name}: {e}")
            return SyncStatus.FAILED
        finally:
            await provider.close()
    
    async def _update_database_varieties(
        self, 
        company_name: str, 
        varieties: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update database with variety data from a seed company.
        
        Args:
            company_name: Name of the seed company
            varieties: List of normalized variety data
            
        Returns:
            Dictionary with success status and details
        """
        try:
            if not self.db:
                return {"success": False, "error": "Database not available"}
            
            # For now, we'll simulate database updates
            # In production, this would use the actual database operations
            logger.info(f"Updating database with {len(varieties)} varieties from {company_name}")
            
            # Track changes for provenance
            for variety in varieties:
                change_record = VarietyUpdateRecord(
                    variety_id=UUID(),  # Would be actual variety ID
                    company_name=company_name,
                    update_type="updated",
                    changes=variety,
                    timestamp=datetime.now(),
                    data_hash=self._calculate_data_hash(variety)
                )
                self.sync_history.append(change_record)
            
            return {"success": True, "varieties_updated": len(varieties)}
            
        except Exception as e:
            logger.error(f"Database update error: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data change tracking."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def get_company_sync_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get synchronization status for all companies.
        
        Returns:
            Dictionary with company sync status information
        """
        status_info = {}
        
        for company_name, config in self.company_configs.items():
            status_info[company_name] = {
                "company_name": config.company_name,
                "last_sync": config.last_sync,
                "sync_status": config.sync_status,
                "error_count": config.error_count,
                "update_frequency_hours": config.update_frequency_hours,
                "next_sync_due": self._calculate_next_sync_time(config)
            }
        
        return status_info
    
    def _calculate_next_sync_time(self, config: SeedCompanyConfig) -> Optional[datetime]:
        """Calculate when the next sync should occur."""
        if not config.last_sync:
            return datetime.now()
        
        return config.last_sync + timedelta(hours=config.update_frequency_hours)
    
    async def validate_variety_data(self, variety_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate variety data from seed companies.
        
        Args:
            variety_data: Variety data to validate
            
        Returns:
            Validation result with quality score and issues
        """
        issues = []
        quality_score = 1.0
        
        # Required fields validation
        required_fields = ["variety_name", "breeder_company"]
        for field in required_fields:
            if not variety_data.get(field):
                issues.append(f"Missing required field: {field}")
                quality_score -= 0.3
        
        # Data type validation
        if variety_data.get("relative_maturity") and not isinstance(variety_data["relative_maturity"], int):
            issues.append("relative_maturity must be an integer")
            quality_score -= 0.1
        
        if variety_data.get("yield_potential_percentile"):
            percentile = variety_data["yield_potential_percentile"]
            if not isinstance(percentile, int) or not (0 <= percentile <= 100):
                issues.append("yield_potential_percentile must be integer between 0-100")
                quality_score -= 0.2
        
        # Availability status validation
        valid_availability = ["widely_available", "limited", "specialty", "research_only"]
        if variety_data.get("seed_availability") not in valid_availability:
            issues.append(f"Invalid seed_availability: {variety_data.get('seed_availability')}")
            quality_score -= 0.1
        
        # Determine data quality level
        if quality_score >= 0.9:
            data_quality = VarietyDataQuality.HIGH
        elif quality_score >= 0.7:
            data_quality = VarietyDataQuality.MEDIUM
        else:
            data_quality = VarietyDataQuality.LOW
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            quality_score=max(0.0, quality_score),
            issues=issues,
            data_quality=data_quality
        )
    
    async def get_variety_availability(
        self, 
        variety_name: str, 
        company_name: Optional[str] = None
    ) -> List[SeedCompanyOffering]:
        """
        Get availability information for a specific variety.
        
        Args:
            variety_name: Name of the variety
            company_name: Optional specific company to check
            
        Returns:
            List of seed company offerings for the variety
        """
        # This would query the database for variety availability
        # For now, return mock data
        mock_offerings = [
            SeedCompanyOffering(
                company_name="Pioneer/Corteva",
                product_code="P1234",
                availability_status=SeedAvailabilityStatus.IN_STOCK,
                distribution_regions=["Midwest", "Great Plains"],
                price_per_unit=350.0,
                price_unit="bag",
                last_updated=datetime.now(),
                notes="Widely available in major corn growing regions"
            )
        ]
        
        return mock_offerings
    
    async def schedule_automatic_sync(self, interval_hours: int = 24):
        """
        Schedule automatic synchronization with seed companies.
        
        Args:
            interval_hours: Hours between sync operations
        """
        while True:
            try:
                logger.info("Starting scheduled seed company sync")
                sync_results = await self.sync_all_companies()
                
                # Log results
                for company, status in sync_results.items():
                    logger.info(f"Sync result for {company}: {status}")
                
                # Wait for next sync
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled sync: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    def get_sync_history(self, company_name: Optional[str] = None) -> List[VarietyUpdateRecord]:
        """
        Get synchronization history for tracking changes.
        
        Args:
            company_name: Optional filter by company name
            
        Returns:
            List of variety update records
        """
        if company_name:
            return [record for record in self.sync_history if record.company_name == company_name]
        return self.sync_history.copy()
    
    async def close(self):
        """Close all provider sessions."""
        for provider in self.providers.values():
            await provider.close()


# Example usage and testing
async def main():
    """Example usage of the SeedCompanyIntegrationService."""
    service = SeedCompanyIntegrationService()
    
    try:
        # Sync all companies
        print("Syncing all seed companies...")
        sync_results = await service.sync_all_companies()
        print(f"Sync results: {sync_results}")
        
        # Get sync status
        print("\nSync status:")
        status_info = await service.get_company_sync_status()
        for company, info in status_info.items():
            print(f"{company}: {info}")
        
        # Get variety availability
        print("\nVariety availability:")
        availability = await service.get_variety_availability("Pioneer P1234")
        for offering in availability:
            print(f"{offering.company_name}: {offering.availability_status}")
        
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())