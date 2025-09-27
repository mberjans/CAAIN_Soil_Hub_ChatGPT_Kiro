"""
Crop Taxonomy Database Access Layer
TICKET-005: Comprehensive Crop Type Filtering System

This module provides database access operations for the crop taxonomy system,
integrating with the PostgreSQL database schema defined in 003_create_crop_taxonomy_system.sql.

Version: 1.0
Author: Agricultural AI Systems
Date: 2024
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy import create_engine, and_, or_, func, text
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from contextlib import contextmanager
import os
import sys

# Add the databases directory to the Python path for imports
sys.path.append('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/databases/python')

from models import (
    Base, Crop, CropTaxonomicHierarchy, CropAgriculturalClassification,
    CropClimateAdaptations, CropSoilRequirements, CropNutritionalProfiles,
    CropFilteringAttributes, EnhancedCropVarieties, CropRegionalAdaptations
)

# Import Pydantic models from our service
from ..models.crop_taxonomy_models import (
    CropTaxonomyResponse, CropSearchFilters, CropCompatibilityFilters
)
from ..models.crop_variety_models import (
    VarietyRecommendationResponse, VarietyComparisonResponse
)
from ..models.service_models import (
    CropSearchResponse, RegionalAdaptationResponse
)

logger = logging.getLogger(__name__)


class CropTaxonomyDatabase:
    """Database access layer for crop taxonomy operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database connection.
        
        Args:
            database_url: Optional database URL override
        """
        if database_url is None:
            # Default PostgreSQL connection for AFAS system
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://afas_user:afas_password@localhost:5432/afas_db'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    @contextmanager
    def get_session(self) -> Session:
        """Get a database session with proper exception handling."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # ============================================================================
    # CROP SEARCH AND FILTERING OPERATIONS
    # ============================================================================
    
    def search_crops(
        self,
        search_text: Optional[str] = None,
        filters: Optional[CropSearchFilters] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search crops with advanced filtering capabilities.
        
        Args:
            search_text: Text to search in crop names, scientific names, keywords
            filters: CropSearchFilters object with filtering criteria
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            
        Returns:
            List of crop dictionaries with comprehensive information
        """
        try:
            with self.get_session() as session:
                # Build base query with all related data
                query = session.query(Crop).options(
                    joinedload(Crop.taxonomic_hierarchy),
                    joinedload(Crop.agricultural_classification),
                    joinedload(Crop.climate_adaptations),
                    joinedload(Crop.soil_requirements),
                    joinedload(Crop.nutritional_profile),
                    joinedload(Crop.filtering_attributes)
                ).filter(Crop.crop_status == 'active')
                
                # Apply text search
                if search_text:
                    search_pattern = f"%{search_text}%"
                    query = query.filter(or_(
                        Crop.crop_name.ilike(search_pattern),
                        Crop.scientific_name.ilike(search_pattern),
                        func.array_to_string(Crop.search_keywords, ' ').ilike(search_pattern),
                        func.array_to_string(Crop.tags, ' ').ilike(search_pattern)
                    ))
                
                # Apply filters if provided
                if filters:
                    query = self._apply_crop_filters(query, filters)
                
                # Execute query with pagination
                crops = query.offset(offset).limit(limit).all()
                
                # Convert to response format
                result = []
                for crop in crops:
                    crop_data = self._crop_to_dict(crop)
                    result.append(crop_data)
                
                return result
                
        except Exception as e:
            logger.error(f"Error searching crops: {e}")
            raise
    
    def _apply_crop_filters(self, query, filters: CropSearchFilters):
        """Apply filtering criteria to crop query."""
        
        # Geographic filters
        if filters.geographic_filters:
            geo = filters.geographic_filters
            if geo.hardiness_zones:
                query = query.join(CropClimateAdaptations).filter(
                    CropClimateAdaptations.hardiness_zones.op('&&')(geo.hardiness_zones)
                )
            if geo.latitude_range:
                query = query.join(CropClimateAdaptations).filter(
                    and_(
                        CropClimateAdaptations.latitude_range_min <= geo.latitude_range.max_value,
                        CropClimateAdaptations.latitude_range_max >= geo.latitude_range.min_value
                    )
                )
        
        # Climate filters
        if filters.climate_filters:
            climate = filters.climate_filters
            if climate.drought_tolerance:
                query = query.join(CropClimateAdaptations).filter(
                    CropClimateAdaptations.drought_tolerance.in_(climate.drought_tolerance)
                )
            if climate.heat_tolerance:
                query = query.join(CropClimateAdaptations).filter(
                    CropClimateAdaptations.heat_tolerance.in_(climate.heat_tolerance)
                )
            if climate.temperature_range:
                query = query.join(CropClimateAdaptations).filter(
                    and_(
                        CropClimateAdaptations.optimal_temp_min_f <= climate.temperature_range.max_temp,
                        CropClimateAdaptations.optimal_temp_max_f >= climate.temperature_range.min_temp
                    )
                )
        
        # Soil filters
        if filters.soil_filters:
            soil = filters.soil_filters
            if soil.ph_range:
                query = query.join(CropSoilRequirements).filter(
                    and_(
                        CropSoilRequirements.optimal_ph_min <= soil.ph_range.max_ph,
                        CropSoilRequirements.optimal_ph_max >= soil.ph_range.min_ph
                    )
                )
            if soil.preferred_textures:
                query = query.join(CropSoilRequirements).filter(
                    CropSoilRequirements.preferred_textures.op('&&')(soil.preferred_textures)
                )
            if soil.drainage_requirements:
                query = query.join(CropSoilRequirements).filter(
                    CropSoilRequirements.drainage_requirement.in_(soil.drainage_requirements)
                )
        
        # Agricultural filters
        if filters.agricultural_filters:
            ag = filters.agricultural_filters
            if ag.crop_categories:
                query = query.join(CropAgriculturalClassification).filter(
                    CropAgriculturalClassification.crop_category.in_(ag.crop_categories)
                )
            if ag.growth_habits:
                query = query.join(CropAgriculturalClassification).filter(
                    CropAgriculturalClassification.growth_habit.in_(ag.growth_habits)
                )
            if ag.plant_types:
                query = query.join(CropAgriculturalClassification).filter(
                    CropAgriculturalClassification.plant_type.in_(ag.plant_types)
                )
            if ag.primary_uses:
                query = query.join(CropAgriculturalClassification).filter(
                    CropAgriculturalClassification.primary_use.in_(ag.primary_uses)
                )
        
        # Seasonal filters
        if filters.seasonal_filters:
            seasonal = filters.seasonal_filters
            if seasonal.planting_seasons:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.planting_season.op('&&')(seasonal.planting_seasons)
                )
            if seasonal.growing_seasons:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.growing_season.op('&&')(seasonal.growing_seasons)
                )
            if seasonal.harvest_seasons:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.harvest_season.op('&&')(seasonal.harvest_seasons)
                )
        
        # Management filters
        if filters.management_filters:
            mgmt = filters.management_filters
            if mgmt.complexity_levels:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.management_complexity.in_(mgmt.complexity_levels)
                )
            if mgmt.input_requirements:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.input_requirements.in_(mgmt.input_requirements)
                )
            if mgmt.labor_requirements:
                query = query.join(CropFilteringAttributes).filter(
                    CropFilteringAttributes.labor_requirements.in_(mgmt.labor_requirements)
                )
        
        return query
    
    def get_crop_by_id(self, crop_id: UUID) -> Optional[Dict[str, Any]]:
        """Get comprehensive crop information by ID."""
        try:
            with self.get_session() as session:
                crop = session.query(Crop).options(
                    joinedload(Crop.taxonomic_hierarchy),
                    joinedload(Crop.agricultural_classification),
                    joinedload(Crop.climate_adaptations),
                    joinedload(Crop.soil_requirements),
                    joinedload(Crop.nutritional_profile),
                    joinedload(Crop.filtering_attributes)
                ).filter(Crop.crop_id == crop_id).first()
                
                if crop:
                    return self._crop_to_dict(crop)
                return None
                
        except Exception as e:
            logger.error(f"Error getting crop by ID {crop_id}: {e}")
            raise
    
    def get_crops_by_family(self, family: str) -> List[Dict[str, Any]]:
        """Get all crops in a botanical family."""
        try:
            with self.get_session() as session:
                crops = session.query(Crop).join(CropTaxonomicHierarchy).filter(
                    CropTaxonomicHierarchy.family.ilike(f"%{family}%"),
                    Crop.crop_status == 'active'
                ).options(
                    joinedload(Crop.taxonomic_hierarchy),
                    joinedload(Crop.agricultural_classification)
                ).all()
                
                return [self._crop_to_dict(crop) for crop in crops]
                
        except Exception as e:
            logger.error(f"Error getting crops by family {family}: {e}")
            raise
    
    # ============================================================================
    # CROP VARIETY OPERATIONS
    # ============================================================================
    
    def get_varieties_for_crop(
        self,
        crop_id: UUID,
        region: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get varieties for a specific crop, optionally filtered by region."""
        try:
            with self.get_session() as session:
                query = session.query(EnhancedCropVarieties).filter(
                    EnhancedCropVarieties.crop_id == crop_id,
                    EnhancedCropVarieties.is_active == True
                )
                
                if region:
                    query = query.filter(
                        EnhancedCropVarieties.adapted_regions.any(region)
                    )
                
                varieties = query.limit(limit).all()
                return [self._variety_to_dict(variety) for variety in varieties]
                
        except Exception as e:
            logger.error(f"Error getting varieties for crop {crop_id}: {e}")
            raise
    
    def search_varieties(
        self,
        search_text: Optional[str] = None,
        crop_id: Optional[UUID] = None,
        traits: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search varieties with advanced filtering."""
        try:
            with self.get_session() as session:
                query = session.query(EnhancedCropVarieties).filter(
                    EnhancedCropVarieties.is_active == True
                )
                
                if search_text:
                    search_pattern = f"%{search_text}%"
                    query = query.filter(or_(
                        EnhancedCropVarieties.variety_name.ilike(search_pattern),
                        EnhancedCropVarieties.breeder_company.ilike(search_pattern)
                    ))
                
                if crop_id:
                    query = query.filter(EnhancedCropVarieties.crop_id == crop_id)
                
                if traits:
                    # Search in herbicide tolerances and stress tolerances
                    for trait in traits:
                        query = query.filter(or_(
                            EnhancedCropVarieties.herbicide_tolerances.any(trait),
                            EnhancedCropVarieties.stress_tolerances.any(trait)
                        ))
                
                varieties = query.limit(limit).all()
                return [self._variety_to_dict(variety) for variety in varieties]
                
        except Exception as e:
            logger.error(f"Error searching varieties: {e}")
            raise
    
    # ============================================================================
    # REGIONAL ADAPTATION OPERATIONS
    # ============================================================================
    
    def get_regional_adaptations(
        self,
        crop_id: Optional[UUID] = None,
        region_name: Optional[str] = None,
        min_adaptation_score: int = 5
    ) -> List[Dict[str, Any]]:
        """Get regional adaptation data for crops."""
        try:
            with self.get_session() as session:
                query = session.query(CropRegionalAdaptations).filter(
                    CropRegionalAdaptations.adaptation_score >= min_adaptation_score
                )
                
                if crop_id:
                    query = query.filter(CropRegionalAdaptations.crop_id == crop_id)
                
                if region_name:
                    query = query.filter(
                        CropRegionalAdaptations.region_name.ilike(f"%{region_name}%")
                    )
                
                adaptations = query.all()
                return [self._adaptation_to_dict(adaptation) for adaptation in adaptations]
                
        except Exception as e:
            logger.error(f"Error getting regional adaptations: {e}")
            raise
    
    def get_crops_for_region(
        self,
        region_name: str,
        production_potential: Optional[str] = None,
        min_adaptation_score: int = 6
    ) -> List[Dict[str, Any]]:
        """Get crops suitable for a specific region."""
        try:
            with self.get_session() as session:
                query = session.query(Crop).join(CropRegionalAdaptations).filter(
                    CropRegionalAdaptations.region_name.ilike(f"%{region_name}%"),
                    CropRegionalAdaptations.adaptation_score >= min_adaptation_score,
                    Crop.crop_status == 'active'
                )
                
                if production_potential:
                    query = query.filter(
                        CropRegionalAdaptations.production_potential == production_potential
                    )
                
                crops = query.options(
                    joinedload(Crop.taxonomic_hierarchy),
                    joinedload(Crop.agricultural_classification)
                ).all()
                
                return [self._crop_to_dict(crop) for crop in crops]
                
        except Exception as e:
            logger.error(f"Error getting crops for region {region_name}: {e}")
            raise
    
    # ============================================================================
    # COMPATIBILITY AND ROTATION OPERATIONS
    # ============================================================================
    
    def get_rotation_compatible_crops(
        self,
        primary_crop_id: UUID,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get crops compatible for rotation with the primary crop."""
        try:
            with self.get_session() as session:
                # Use the database function for rotation compatibility
                sql = text("""
                    SELECT * FROM get_crop_rotation_compatibility(
                        :primary_crop_id,
                        :region_name_filter
                    )
                """)
                
                result = session.execute(sql, {
                    'primary_crop_id': primary_crop_id,
                    'region_name_filter': region
                }).fetchall()
                
                # Convert result to list of dictionaries
                compatible_crops = []
                for row in result:
                    compatible_crops.append({
                        'crop_id': row.compatible_crop_id,
                        'crop_name': row.compatible_crop_name,
                        'compatibility_type': row.compatibility_type,
                        'benefits': row.benefits,
                        'considerations': row.considerations
                    })
                
                return compatible_crops
                
        except Exception as e:
            logger.error(f"Error getting rotation compatible crops: {e}")
            raise
    
    # ============================================================================
    # DATA CONVERSION HELPER METHODS
    # ============================================================================
    
    def _crop_to_dict(self, crop: Crop) -> Dict[str, Any]:
        """Convert SQLAlchemy Crop model to dictionary."""
        crop_dict = {
            'crop_id': str(crop.crop_id),
            'crop_name': crop.crop_name,
            'scientific_name': crop.scientific_name,
            'crop_category': crop.crop_category,
            'crop_family': crop.crop_family,
            'crop_code': crop.crop_code,
            'crop_status': crop.crop_status,
            'is_cover_crop': crop.is_cover_crop,
            'is_companion_crop': crop.is_companion_crop,
            'search_keywords': crop.search_keywords or [],
            'tags': crop.tags or [],
            
            # Legacy fields
            'nitrogen_fixing': crop.nitrogen_fixing,
            'typical_yield_range': {
                'min': crop.typical_yield_range_min,
                'max': crop.typical_yield_range_max,
                'units': crop.yield_units
            } if crop.typical_yield_range_min else None,
            'maturity_days_range': {
                'min': crop.maturity_days_min,
                'max': crop.maturity_days_max
            } if crop.maturity_days_min else None,
            'growing_degree_days': crop.growing_degree_days,
        }
        
        # Add taxonomic hierarchy if available
        if crop.taxonomic_hierarchy:
            th = crop.taxonomic_hierarchy
            crop_dict['taxonomic_hierarchy'] = {
                'kingdom': th.kingdom,
                'phylum': th.phylum,
                'class': th.class_,
                'order': th.order_name,
                'family': th.family,
                'genus': th.genus,
                'species': th.species,
                'subspecies': th.subspecies,
                'variety': th.variety,
                'cultivar': th.cultivar,
                'common_synonyms': th.common_synonyms or []
            }
        
        # Add agricultural classification if available
        if crop.agricultural_classification:
            ac = crop.agricultural_classification
            crop_dict['agricultural_classification'] = {
                'crop_category': ac.crop_category,
                'crop_subcategory': ac.crop_subcategory,
                'primary_use': ac.primary_use,
                'secondary_uses': ac.secondary_uses or [],
                'growth_habit': ac.growth_habit,
                'plant_type': ac.plant_type,
                'growth_form': ac.growth_form,
                'photosynthesis_type': ac.photosynthesis_type,
                'nitrogen_fixing': ac.nitrogen_fixing,
                'mature_size': {
                    'height_inches': {
                        'min': ac.mature_height_min_inches,
                        'max': ac.mature_height_max_inches
                    } if ac.mature_height_min_inches else None,
                    'width_inches': {
                        'min': ac.mature_width_min_inches,
                        'max': ac.mature_width_max_inches
                    } if ac.mature_width_min_inches else None
                },
                'root_system_type': ac.root_system_type
            }
        
        # Add climate adaptations if available
        if crop.climate_adaptations:
            ca = crop.climate_adaptations
            crop_dict['climate_adaptations'] = {
                'temperature_range_f': {
                    'optimal_min': ca.optimal_temp_min_f,
                    'optimal_max': ca.optimal_temp_max_f,
                    'absolute_min': ca.absolute_temp_min_f,
                    'absolute_max': ca.absolute_temp_max_f
                },
                'hardiness_zones': ca.hardiness_zones or [],
                'precipitation_requirements': {
                    'annual_min_inches': ca.annual_precipitation_min_inches,
                    'annual_max_inches': ca.annual_precipitation_max_inches,
                    'water_requirement': ca.water_requirement
                },
                'tolerance': {
                    'drought': ca.drought_tolerance,
                    'heat': ca.heat_tolerance,
                    'frost': ca.frost_tolerance,
                    'flooding': ca.flooding_tolerance
                },
                'photoperiod_sensitivity': ca.photoperiod_sensitivity,
                'vernalization_requirement': ca.vernalization_requirement,
                'elevation_range_feet': {
                    'min': ca.elevation_min_feet,
                    'max': ca.elevation_max_feet
                } if ca.elevation_min_feet else None
            }
        
        # Add soil requirements if available
        if crop.soil_requirements:
            sr = crop.soil_requirements
            crop_dict['soil_requirements'] = {
                'ph_range': {
                    'optimal_min': sr.optimal_ph_min,
                    'optimal_max': sr.optimal_ph_max,
                    'tolerable_min': sr.tolerable_ph_min,
                    'tolerable_max': sr.tolerable_ph_max
                },
                'texture_preferences': {
                    'preferred': sr.preferred_textures or [],
                    'tolerable': sr.tolerable_textures or []
                },
                'drainage_requirement': sr.drainage_requirement,
                'tolerance': {
                    'salinity': sr.salinity_tolerance,
                    'alkalinity': sr.alkalinity_tolerance,
                    'acidity': sr.acidity_tolerance,
                    'compaction': sr.compaction_tolerance
                },
                'nutrient_requirements': {
                    'nitrogen': sr.nitrogen_requirement,
                    'phosphorus': sr.phosphorus_requirement,
                    'potassium': sr.potassium_requirement
                },
                'organic_matter_preference': sr.organic_matter_preference
            }
        
        # Add filtering attributes if available
        if crop.filtering_attributes:
            fa = crop.filtering_attributes
            crop_dict['filtering_attributes'] = {
                'filter_id': str(fa.filter_id) if fa.filter_id else None,
                'crop_id': str(fa.crop_id) if fa.crop_id else None,
                'seasonality': {
                    'planting_season': fa.planting_season or [],
                    'growing_season': fa.growing_season or [],
                    'harvest_season': fa.harvest_season or []
                },
                'agricultural_systems': {
                    'farming_systems': fa.farming_systems or [],
                    'rotation_compatibility': fa.rotation_compatibility or [],
                    'intercropping_compatible': fa.intercropping_compatible,
                    'cover_crop_compatible': fa.cover_crop_compatible
                },
                'management': {
                    'complexity': fa.management_complexity,
                    'input_requirements': fa.input_requirements,
                    'labor_requirements': fa.labor_requirements
                },
                'technology': {
                    'precision_ag_compatible': fa.precision_ag_compatible,
                    'gps_guidance_recommended': fa.gps_guidance_recommended,
                    'sensor_monitoring_beneficial': fa.sensor_monitoring_beneficial
                },
                'sustainability': {
                    'carbon_sequestration_potential': fa.carbon_sequestration_potential,
                    'biodiversity_support': fa.biodiversity_support,
                    'pollinator_value': fa.pollinator_value,
                    'water_use_efficiency': fa.water_use_efficiency
                },
                'market': {
                    'market_stability': fa.market_stability,
                    'price_premium_potential': fa.price_premium_potential,
                    'value_added_opportunities': fa.value_added_opportunities or []
                },
                'advanced_filters': {
                    'pest_resistance_traits': fa.pest_resistance_traits or {},
                    'market_class_filters': fa.market_class_filters or {},
                    'certification_filters': fa.certification_filters or {},
                    'seed_availability_filters': fa.seed_availability_filters or {}
                }
            }

        return crop_dict
    
    def _variety_to_dict(self, variety: EnhancedCropVarieties) -> Dict[str, Any]:
        """Convert SQLAlchemy EnhancedCropVarieties model to dictionary."""
        return {
            'variety_id': str(variety.variety_id),
            'crop_id': str(variety.crop_id),
            'variety_name': variety.variety_name,
            'variety_code': variety.variety_code,
            'breeder_company': variety.breeder_company,
            'parent_varieties': variety.parent_varieties or [],
            'maturity': {
                'relative_maturity': variety.relative_maturity,
                'maturity_group': variety.maturity_group,
                'days_to_emergence': variety.days_to_emergence,
                'days_to_flowering': variety.days_to_flowering,
                'days_to_physiological_maturity': variety.days_to_physiological_maturity
            },
            'performance': {
                'yield_potential_percentile': variety.yield_potential_percentile,
                'yield_stability_rating': variety.yield_stability_rating,
                'standability_rating': variety.standability_rating
            },
            'traits': {
                'disease_resistances': variety.disease_resistances or {},
                'pest_resistances': variety.pest_resistances or {},
                'herbicide_tolerances': variety.herbicide_tolerances or [],
                'stress_tolerances': variety.stress_tolerances or []
            },
            'quality': {
                'quality_characteristics': variety.quality_characteristics or {},
                'protein_content_range': variety.protein_content_range,
                'oil_content_range': variety.oil_content_range
            },
            'adaptation': {
                'adapted_regions': variety.adapted_regions or [],
                'recommended_planting_populations': variety.recommended_planting_populations or {},
                'special_management_notes': variety.special_management_notes
            },
            'commercial': {
                'seed_availability': variety.seed_availability,
                'relative_seed_cost': variety.relative_seed_cost,
                'technology_package': variety.technology_package,
                'organic_approved': variety.organic_approved,
                'non_gmo_certified': variety.non_gmo_certified,
                'registration_year': variety.registration_year,
                'patent_protected': variety.patent_protected
            },
            'is_active': variety.is_active
        }
    
    def _adaptation_to_dict(self, adaptation: CropRegionalAdaptations) -> Dict[str, Any]:
        """Convert SQLAlchemy CropRegionalAdaptations model to dictionary."""
        return {
            'adaptation_id': str(adaptation.adaptation_id),
            'crop_id': str(adaptation.crop_id),
            'region': {
                'region_name': adaptation.region_name,
                'region_type': adaptation.region_type,
                'country_code': adaptation.country_code
            },
            'adaptation_metrics': {
                'adaptation_score': adaptation.adaptation_score,
                'production_potential': adaptation.production_potential,
                'risk_level': adaptation.risk_level
            },
            'regional_characteristics': {
                'typical_planting_dates': adaptation.typical_planting_dates or {},
                'typical_harvest_dates': adaptation.typical_harvest_dates or {},
                'common_varieties': adaptation.common_varieties or [],
                'regional_challenges': adaptation.regional_challenges or [],
                'management_considerations': adaptation.management_considerations or []
            },
            'economic_factors': {
                'market_demand': adaptation.market_demand,
                'infrastructure_support': adaptation.infrastructure_support
            }
        }

    # ============================================================================
    # DATABASE MANAGEMENT OPERATIONS
    # ============================================================================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for the taxonomy system."""
        try:
            with self.get_session() as session:
                stats = {
                    'total_crops': session.query(Crop).filter(Crop.crop_status == 'active').count(),
                    'total_varieties': session.query(EnhancedCropVarieties).filter(EnhancedCropVarieties.is_active == True).count(),
                    'crops_by_category': {},
                    'varieties_by_availability': {},
                    'regional_adaptations_count': session.query(CropRegionalAdaptations).count()
                }
                
                # Get crop counts by category
                category_counts = session.query(
                    CropAgriculturalClassification.crop_category,
                    func.count(Crop.crop_id).label('count')
                ).join(Crop).filter(Crop.crop_status == 'active').group_by(
                    CropAgriculturalClassification.crop_category
                ).all()
                
                stats['crops_by_category'] = {cat: count for cat, count in category_counts}
                
                # Get variety counts by availability
                availability_counts = session.query(
                    EnhancedCropVarieties.seed_availability,
                    func.count(EnhancedCropVarieties.variety_id).label('count')
                ).filter(EnhancedCropVarieties.is_active == True).group_by(
                    EnhancedCropVarieties.seed_availability
                ).all()
                
                stats['varieties_by_availability'] = {avail: count for avail, count in availability_counts if avail}
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            raise


# Create a singleton instance for easy import
crop_taxonomy_db = CropTaxonomyDatabase()
