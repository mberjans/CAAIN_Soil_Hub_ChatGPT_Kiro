"""
AFAS Knowledge Base Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This module implements the knowledge base structure that combines PostgreSQL
for structured agricultural data and MongoDB for flexible document storage.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING, TEXT

# Import database managers and models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from database_config import get_postgres_session, get_mongodb_collection
from models import (
    Crop, CropVariety, SoilTest, FertilizerProduct, 
    QuestionType, Recommendation, WeatherData
)

logger = logging.getLogger(__name__)

class KnowledgeCategory(Enum):
    """Categories for agricultural knowledge."""
    CROP_MANAGEMENT = "crop_management"
    SOIL_HEALTH = "soil_health"
    NUTRIENT_MANAGEMENT = "nutrient_management"
    PEST_MANAGEMENT = "pest_management"
    EQUIPMENT_OPERATION = "equipment_operation"
    ECONOMIC_ANALYSIS = "economic_analysis"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    BEST_PRACTICES = "best_practices"

class SourceType(Enum):
    """Types of knowledge sources."""
    EXTENSION_SERVICE = "extension_service"
    RESEARCH_PAPER = "research_paper"
    EXPERT_KNOWLEDGE = "expert_knowledge"
    GOVERNMENT_GUIDELINE = "government_guideline"
    INDUSTRY_STANDARD = "industry_standard"

@dataclass
class KnowledgeSource:
    """Represents a source of agricultural knowledge."""
    type: SourceType
    name: str
    url: Optional[str] = None
    publication_date: Optional[date] = None
    credibility_score: float = 0.8

@dataclass
class KnowledgeItem:
    """Represents an item of agricultural knowledge."""
    knowledge_id: str
    category: KnowledgeCategory
    subcategory: str
    title: str
    description: str
    guidelines: List[str]
    calculations: Optional[Dict[str, Any]] = None
    regional_variations: Optional[List[Dict[str, str]]] = None
    source: Optional[KnowledgeSource] = None
    applicability: Optional[Dict[str, Any]] = None
    tags: List[str] = None
    expert_validated: bool = False
    validation_date: Optional[date] = None

class KnowledgeBase:
    """
    Main knowledge base class that manages agricultural knowledge
    across PostgreSQL and MongoDB databases.
    """
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.postgres_session = None
        self.mongodb_collections = {}
        self._initialize_connections()
        self._setup_collections()
    
    def _initialize_connections(self):
        """Initialize database connections."""
        try:
            self.postgres_session = get_postgres_session()
            
            # Initialize MongoDB collections
            self.mongodb_collections = {
                'agricultural_knowledge': get_mongodb_collection('agricultural_knowledge'),
                'question_responses': get_mongodb_collection('question_responses'),
                'external_data_cache': get_mongodb_collection('external_data_cache'),
                'image_analysis': get_mongodb_collection('image_analysis'),
                'conversation_history': get_mongodb_collection('conversation_history')
            }
            
            logger.info("Knowledge base database connections initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base connections: {e}")
            raise
    
    def _setup_collections(self):
        """Setup MongoDB collections with proper indexes."""
        try:
            # Agricultural knowledge indexes
            knowledge_collection = self.mongodb_collections['agricultural_knowledge']
            
            # Create indexes if they don't exist
            existing_indexes = knowledge_collection.list_indexes()
            index_names = [idx['name'] for idx in existing_indexes]
            
            if 'knowledge_id_1' not in index_names:
                knowledge_collection.create_index([("knowledge_id", ASCENDING)], unique=True)
            
            if 'category_subcategory_1' not in index_names:
                knowledge_collection.create_index([("category", ASCENDING), ("subcategory", ASCENDING)])
            
            if 'tags_1' not in index_names:
                knowledge_collection.create_index([("tags", ASCENDING)])
            
            if 'text_search' not in index_names:
                knowledge_collection.create_index([
                    ("content.title", TEXT),
                    ("content.description", TEXT),
                    ("tags", TEXT)
                ], name="text_search")
            
            logger.info("MongoDB collections and indexes setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup MongoDB collections: {e}")
            raise
    
    # ========================================================================
    # AGRICULTURAL KNOWLEDGE MANAGEMENT
    # ========================================================================
    
    def add_knowledge_item(self, knowledge_item: KnowledgeItem) -> bool:
        """
        Add a new knowledge item to the knowledge base.
        
        Args:
            knowledge_item: The knowledge item to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            knowledge_collection = self.mongodb_collections['agricultural_knowledge']
            
            # Convert knowledge item to MongoDB document
            document = {
                "knowledge_id": knowledge_item.knowledge_id,
                "category": knowledge_item.category.value,
                "subcategory": knowledge_item.subcategory,
                "content": {
                    "title": knowledge_item.title,
                    "description": knowledge_item.description,
                    "guidelines": knowledge_item.guidelines,
                    "calculations": knowledge_item.calculations,
                    "regional_variations": knowledge_item.regional_variations
                },
                "source": {
                    "type": knowledge_item.source.type.value if knowledge_item.source else None,
                    "name": knowledge_item.source.name if knowledge_item.source else None,
                    "url": knowledge_item.source.url if knowledge_item.source else None,
                    "publication_date": knowledge_item.source.publication_date if knowledge_item.source else None,
                    "credibility_score": knowledge_item.source.credibility_score if knowledge_item.source else 0.8
                },
                "applicability": knowledge_item.applicability,
                "tags": knowledge_item.tags or [],
                "expert_validated": knowledge_item.expert_validated,
                "validation_date": knowledge_item.validation_date,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert the document
            result = knowledge_collection.insert_one(document)
            
            if result.inserted_id:
                logger.info(f"Knowledge item added: {knowledge_item.knowledge_id}")
                return True
            else:
                logger.error(f"Failed to add knowledge item: {knowledge_item.knowledge_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding knowledge item: {e}")
            return False
    
    def get_knowledge_by_category(self, category: KnowledgeCategory, 
                                 subcategory: Optional[str] = None,
                                 expert_validated_only: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge items by category.
        
        Args:
            category: The knowledge category
            subcategory: Optional subcategory filter
            expert_validated_only: Only return expert-validated items
            
        Returns:
            List of knowledge items
        """
        try:
            knowledge_collection = self.mongodb_collections['agricultural_knowledge']
            
            # Build query
            query = {"category": category.value}
            
            if subcategory:
                query["subcategory"] = subcategory
            
            if expert_validated_only:
                query["expert_validated"] = True
            
            # Execute query
            cursor = knowledge_collection.find(query).sort("updated_at", DESCENDING)
            results = list(cursor)
            
            logger.info(f"Retrieved {len(results)} knowledge items for category: {category.value}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge by category: {e}")
            return []
    
    def search_knowledge(self, search_text: str, 
                        categories: Optional[List[KnowledgeCategory]] = None,
                        tags: Optional[List[str]] = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search knowledge items using text search.
        
        Args:
            search_text: Text to search for
            categories: Optional list of categories to filter by
            tags: Optional list of tags to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge items
        """
        try:
            knowledge_collection = self.mongodb_collections['agricultural_knowledge']
            
            # Build query
            query = {"$text": {"$search": search_text}}
            
            # Add category filter
            if categories:
                category_values = [cat.value for cat in categories]
                query["category"] = {"$in": category_values}
            
            # Add tag filter
            if tags:
                query["tags"] = {"$in": tags}
            
            # Execute search with text score sorting
            cursor = knowledge_collection.find(
                query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            
            results = list(cursor)
            
            logger.info(f"Found {len(results)} knowledge items for search: '{search_text}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []
    
    def get_knowledge_for_crop(self, crop_name: str, 
                              categories: Optional[List[KnowledgeCategory]] = None) -> List[Dict[str, Any]]:
        """
        Get knowledge items applicable to a specific crop.
        
        Args:
            crop_name: Name of the crop
            categories: Optional categories to filter by
            
        Returns:
            List of applicable knowledge items
        """
        try:
            knowledge_collection = self.mongodb_collections['agricultural_knowledge']
            
            # Build query
            query = {
                "$or": [
                    {"applicability.crops": crop_name},
                    {"applicability.crops": {"$exists": False}},  # General knowledge
                    {"tags": crop_name}
                ]
            }
            
            if categories:
                category_values = [cat.value for cat in categories]
                query["category"] = {"$in": category_values}
            
            cursor = knowledge_collection.find(query).sort("expert_validated", DESCENDING)
            results = list(cursor)
            
            logger.info(f"Retrieved {len(results)} knowledge items for crop: {crop_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving crop knowledge: {e}")
            return []
    
    # ========================================================================
    # STRUCTURED DATA QUERIES (PostgreSQL)
    # ========================================================================
    
    def get_crop_information(self, crop_name: str) -> Optional[Dict[str, Any]]:
        """
        Get structured crop information from PostgreSQL.
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Crop information dictionary or None
        """
        try:
            crop = self.postgres_session.query(Crop).filter(
                Crop.crop_name.ilike(f"%{crop_name}%")
            ).first()
            
            if crop:
                return {
                    "crop_id": str(crop.crop_id),
                    "crop_name": crop.crop_name,
                    "scientific_name": crop.scientific_name,
                    "category": crop.crop_category,
                    "family": crop.crop_family,
                    "nitrogen_fixing": crop.nitrogen_fixing,
                    "yield_range": {
                        "min": crop.typical_yield_range_min,
                        "max": crop.typical_yield_range_max,
                        "units": crop.yield_units
                    },
                    "growing_requirements": {
                        "growing_degree_days": crop.growing_degree_days,
                        "maturity_days_min": crop.maturity_days_min,
                        "maturity_days_max": crop.maturity_days_max,
                        "optimal_ph_min": crop.optimal_ph_min,
                        "optimal_ph_max": crop.optimal_ph_max
                    },
                    "tolerance": {
                        "drought": crop.drought_tolerance,
                        "cold": crop.cold_tolerance
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving crop information: {e}")
            return None
    
    def get_crop_varieties(self, crop_name: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get crop varieties for a specific crop.
        
        Args:
            crop_name: Name of the crop
            region: Optional region filter
            
        Returns:
            List of crop varieties
        """
        try:
            query = self.postgres_session.query(CropVariety).join(Crop).filter(
                Crop.crop_name.ilike(f"%{crop_name}%"),
                CropVariety.is_active == True
            )
            
            varieties = query.all()
            
            result = []
            for variety in varieties:
                # Filter by region if specified
                if region and variety.regional_adaptation:
                    if region.lower() not in [r.lower() for r in variety.regional_adaptation]:
                        continue
                
                result.append({
                    "variety_id": str(variety.variety_id),
                    "variety_name": variety.variety_name,
                    "company": variety.company,
                    "maturity_days": variety.maturity_days,
                    "yield_potential": variety.yield_potential,
                    "disease_resistance": variety.disease_resistance,
                    "herbicide_tolerance": variety.herbicide_tolerance,
                    "special_traits": variety.special_traits,
                    "regional_adaptation": variety.regional_adaptation,
                    "release_year": variety.release_year
                })
            
            logger.info(f"Retrieved {len(result)} varieties for crop: {crop_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving crop varieties: {e}")
            return []
    
    def get_fertilizer_products(self, product_type: Optional[str] = None,
                               nutrient_focus: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get fertilizer products from the database.
        
        Args:
            product_type: Optional product type filter
            nutrient_focus: Optional nutrient focus (N, P, K)
            
        Returns:
            List of fertilizer products
        """
        try:
            query = self.postgres_session.query(FertilizerProduct).filter(
                FertilizerProduct.is_active == True
            )
            
            if product_type:
                query = query.filter(FertilizerProduct.product_type == product_type)
            
            products = query.all()
            
            result = []
            for product in products:
                # Filter by nutrient focus if specified
                if nutrient_focus:
                    if nutrient_focus.upper() == 'N' and product.nitrogen_percent < 5:
                        continue
                    elif nutrient_focus.upper() == 'P' and product.phosphorus_percent < 5:
                        continue
                    elif nutrient_focus.upper() == 'K' and product.potassium_percent < 5:
                        continue
                
                result.append({
                    "product_id": str(product.product_id),
                    "product_name": product.product_name,
                    "manufacturer": product.manufacturer,
                    "product_type": product.product_type,
                    "nutrient_analysis": {
                        "nitrogen_percent": product.nitrogen_percent,
                        "phosphorus_percent": product.phosphorus_percent,
                        "potassium_percent": product.potassium_percent,
                        "sulfur_percent": product.sulfur_percent,
                        "calcium_percent": product.calcium_percent,
                        "magnesium_percent": product.magnesium_percent
                    },
                    "micronutrients": {
                        "iron_percent": product.iron_percent,
                        "manganese_percent": product.manganese_percent,
                        "zinc_percent": product.zinc_percent,
                        "copper_percent": product.copper_percent,
                        "boron_percent": product.boron_percent
                    },
                    "physical_properties": {
                        "bulk_density": product.bulk_density,
                        "particle_size": product.particle_size,
                        "application_method": product.application_method
                    },
                    "economic_data": {
                        "typical_price_per_ton": product.typical_price_per_ton,
                        "price_currency": product.price_currency,
                        "price_date": product.price_date
                    }
                })
            
            logger.info(f"Retrieved {len(result)} fertilizer products")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving fertilizer products: {e}")
            return []
    
    def get_soil_test_interpretation(self, ph: float, organic_matter: float,
                                   phosphorus: float, potassium: float,
                                   crop_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get soil test interpretation based on values.
        
        Args:
            ph: Soil pH value
            organic_matter: Organic matter percentage
            phosphorus: Phosphorus level (ppm)
            potassium: Potassium level (ppm)
            crop_type: Optional crop type for specific recommendations
            
        Returns:
            Soil test interpretation
        """
        try:
            interpretation = {
                "ph_interpretation": self._interpret_ph(ph, crop_type),
                "organic_matter_interpretation": self._interpret_organic_matter(organic_matter),
                "phosphorus_interpretation": self._interpret_phosphorus(phosphorus),
                "potassium_interpretation": self._interpret_potassium(potassium),
                "overall_assessment": "",
                "recommendations": []
            }
            
            # Generate overall assessment
            issues = []
            if interpretation["ph_interpretation"]["status"] != "optimal":
                issues.append("pH management needed")
            if interpretation["organic_matter_interpretation"]["status"] == "low":
                issues.append("organic matter improvement needed")
            if interpretation["phosphorus_interpretation"]["status"] == "low":
                issues.append("phosphorus supplementation needed")
            if interpretation["potassium_interpretation"]["status"] == "low":
                issues.append("potassium supplementation needed")
            
            if not issues:
                interpretation["overall_assessment"] = "Soil fertility levels are generally good"
            else:
                interpretation["overall_assessment"] = f"Priority areas: {', '.join(issues)}"
            
            # Compile recommendations
            for category in ["ph_interpretation", "organic_matter_interpretation", 
                           "phosphorus_interpretation", "potassium_interpretation"]:
                if interpretation[category].get("recommendations"):
                    interpretation["recommendations"].extend(interpretation[category]["recommendations"])
            
            return interpretation
            
        except Exception as e:
            logger.error(f"Error interpreting soil test: {e}")
            return {}
    
    def _interpret_ph(self, ph: float, crop_type: Optional[str] = None) -> Dict[str, Any]:
        """Interpret soil pH value."""
        if ph < 5.5:
            status = "very_acidic"
            description = "Very acidic soil may limit nutrient availability"
            recommendations = ["Apply lime to raise pH", "Consider sulfur-tolerant crops"]
        elif ph < 6.0:
            status = "acidic"
            description = "Acidic soil may reduce phosphorus availability"
            recommendations = ["Consider lime application", "Monitor micronutrient levels"]
        elif ph <= 7.0:
            status = "optimal"
            description = "pH is in the optimal range for most crops"
            recommendations = []
        elif ph <= 8.0:
            status = "alkaline"
            description = "Alkaline soil may reduce micronutrient availability"
            recommendations = ["Monitor iron and zinc levels", "Consider acidifying amendments"]
        else:
            status = "very_alkaline"
            description = "Very alkaline soil may cause nutrient deficiencies"
            recommendations = ["Apply sulfur to lower pH", "Use acidifying fertilizers"]
        
        return {
            "value": ph,
            "status": status,
            "description": description,
            "recommendations": recommendations
        }
    
    def _interpret_organic_matter(self, om: float) -> Dict[str, Any]:
        """Interpret organic matter percentage."""
        if om < 2.0:
            status = "low"
            description = "Low organic matter reduces soil health and nutrient retention"
            recommendations = ["Add compost or manure", "Use cover crops", "Reduce tillage"]
        elif om < 3.0:
            status = "moderate"
            description = "Moderate organic matter levels"
            recommendations = ["Continue organic matter building practices"]
        elif om <= 5.0:
            status = "good"
            description = "Good organic matter levels support soil health"
            recommendations = ["Maintain current practices"]
        else:
            status = "high"
            description = "High organic matter levels"
            recommendations = ["Monitor nitrogen mineralization"]
        
        return {
            "value": om,
            "status": status,
            "description": description,
            "recommendations": recommendations
        }
    
    def _interpret_phosphorus(self, p: float) -> Dict[str, Any]:
        """Interpret phosphorus level."""
        if p < 15:
            status = "low"
            description = "Low phosphorus may limit root development and yield"
            recommendations = ["Apply phosphorus fertilizer", "Consider starter fertilizer"]
        elif p < 25:
            status = "moderate"
            description = "Moderate phosphorus levels"
            recommendations = ["Maintenance phosphorus application recommended"]
        elif p <= 40:
            status = "adequate"
            description = "Adequate phosphorus for most crops"
            recommendations = ["Maintenance rates sufficient"]
        else:
            status = "high"
            description = "High phosphorus levels"
            recommendations = ["Reduce or eliminate phosphorus applications"]
        
        return {
            "value": p,
            "status": status,
            "description": description,
            "recommendations": recommendations
        }
    
    def _interpret_potassium(self, k: float) -> Dict[str, Any]:
        """Interpret potassium level."""
        if k < 120:
            status = "low"
            description = "Low potassium may reduce stress tolerance and yield"
            recommendations = ["Apply potassium fertilizer", "Consider fall application"]
        elif k < 160:
            status = "moderate"
            description = "Moderate potassium levels"
            recommendations = ["Maintenance potassium application recommended"]
        elif k <= 200:
            status = "adequate"
            description = "Adequate potassium for most crops"
            recommendations = ["Maintenance rates sufficient"]
        else:
            status = "high"
            description = "High potassium levels"
            recommendations = ["Reduce potassium applications"]
        
        return {
            "value": k,
            "status": status,
            "description": description,
            "recommendations": recommendations
        }
    
    # ========================================================================
    # RECOMMENDATION HISTORY AND CACHING
    # ========================================================================
    
    def store_recommendation(self, user_id: str, question_type: str,
                           request_data: Dict[str, Any], 
                           response_data: Dict[str, Any],
                           ai_explanation: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a recommendation in MongoDB for future reference.
        
        Args:
            user_id: User identifier
            question_type: Type of question asked
            request_data: Original request parameters
            response_data: Generated response
            ai_explanation: Optional AI explanation metadata
            
        Returns:
            Recommendation ID
        """
        try:
            responses_collection = self.mongodb_collections['question_responses']
            
            recommendation_id = str(uuid.uuid4())
            
            document = {
                "recommendation_id": recommendation_id,
                "user_id": user_id,
                "question_type": question_type,
                "request_data": request_data,
                "response_data": response_data,
                "ai_explanation": ai_explanation,
                "timestamp": datetime.utcnow(),
                "session_id": request_data.get("session_id")
            }
            
            result = responses_collection.insert_one(document)
            
            if result.inserted_id:
                logger.info(f"Recommendation stored: {recommendation_id}")
                return recommendation_id
            else:
                logger.error("Failed to store recommendation")
                return ""
                
        except Exception as e:
            logger.error(f"Error storing recommendation: {e}")
            return ""
    
    def get_user_recommendations(self, user_id: str, 
                               question_type: Optional[str] = None,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recommendation history for a user.
        
        Args:
            user_id: User identifier
            question_type: Optional question type filter
            limit: Maximum number of results
            
        Returns:
            List of user recommendations
        """
        try:
            responses_collection = self.mongodb_collections['question_responses']
            
            query = {"user_id": user_id}
            if question_type:
                query["question_type"] = question_type
            
            cursor = responses_collection.find(query).sort("timestamp", DESCENDING).limit(limit)
            results = list(cursor)
            
            logger.info(f"Retrieved {len(results)} recommendations for user: {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving user recommendations: {e}")
            return []
    
    def cache_external_data(self, cache_key: str, data_source: str,
                          data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """
        Cache external API data in MongoDB.
        
        Args:
            cache_key: Unique cache key
            data_source: Source of the data
            data: Data to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_collection = self.mongodb_collections['external_data_cache']
            
            expires_at = datetime.utcnow().timestamp() + ttl_seconds
            
            document = {
                "cache_key": cache_key,
                "data_source": data_source,
                "data": data,
                "cached_at": datetime.utcnow(),
                "expires_at": datetime.fromtimestamp(expires_at)
            }
            
            # Use upsert to replace existing cache entries
            result = cache_collection.replace_one(
                {"cache_key": cache_key},
                document,
                upsert=True
            )
            
            logger.info(f"Data cached: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data from MongoDB.
        
        Args:
            cache_key: Cache key to retrieve
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            cache_collection = self.mongodb_collections['external_data_cache']
            
            document = cache_collection.find_one({
                "cache_key": cache_key,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if document:
                logger.info(f"Cache hit: {cache_key}")
                return document["data"]
            else:
                logger.info(f"Cache miss: {cache_key}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving cached data: {e}")
            return None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def close(self):
        """Close database connections."""
        if self.postgres_session:
            self.postgres_session.close()
        logger.info("Knowledge base connections closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ========================================================================
# KNOWLEDGE BASE INITIALIZATION AND SEEDING
# ========================================================================

def initialize_knowledge_base() -> KnowledgeBase:
    """Initialize and return a knowledge base instance."""
    return KnowledgeBase()

def seed_initial_knowledge(kb: KnowledgeBase):
    """Seed the knowledge base with initial agricultural knowledge."""
    
    # Corn nitrogen management knowledge
    corn_nitrogen = KnowledgeItem(
        knowledge_id="corn_nitrogen_management_001",
        category=KnowledgeCategory.NUTRIENT_MANAGEMENT,
        subcategory="nitrogen",
        title="Corn Nitrogen Rate Calculation",
        description="Standard method for calculating nitrogen fertilizer rates for corn production based on yield goals, soil conditions, and previous crops.",
        guidelines=[
            "Base nitrogen rate on realistic yield goal (1.2 lbs N per bushel expected yield)",
            "Credit nitrogen from previous legume crops (40 lbs/acre for soybean, 100 lbs/acre for alfalfa)",
            "Account for soil organic matter mineralization (20 lbs N per 1% OM)",
            "Consider soil test nitrate levels (2 lbs N credit per ppm nitrate-N)",
            "Split applications for rates >150 lbs/acre to improve efficiency"
        ],
        calculations={
            "formula": "N_rate = (Yield_goal * 1.2) - Legume_credit - Soil_N_credit - OM_credit",
            "parameters": {
                "yield_goal_multiplier": 1.2,
                "soybean_credit": 40,
                "alfalfa_credit": 100,
                "om_mineralization_rate": 20,
                "soil_n_credit_multiplier": 2
            },
            "example": {
                "yield_goal": 180,
                "base_n_need": 216,
                "soybean_credit": 40,
                "soil_n_credit": 24,
                "final_n_rate": 152
            }
        },
        source=KnowledgeSource(
            type=SourceType.EXTENSION_SERVICE,
            name="Iowa State University Extension PM 1688",
            url="https://extension.iastate.edu/corn/nitrogen",
            publication_date=date(2024, 1, 1),
            credibility_score=0.95
        ),
        applicability={
            "regions": ["midwest", "corn_belt"],
            "crops": ["corn"],
            "soil_types": ["silt_loam", "clay_loam", "sandy_loam"],
            "farm_sizes": {"min_acres": 10, "max_acres": 10000}
        },
        tags=["nitrogen", "corn", "fertilizer", "calculation", "yield", "iowa"],
        expert_validated=True,
        validation_date=date(2024, 1, 15)
    )
    
    # Soil pH management knowledge
    soil_ph = KnowledgeItem(
        knowledge_id="soil_ph_management_001",
        category=KnowledgeCategory.SOIL_HEALTH,
        subcategory="ph_management",
        title="Soil pH Management for Optimal Nutrient Availability",
        description="Guidelines for managing soil pH to optimize nutrient availability and crop performance.",
        guidelines=[
            "Maintain pH between 6.0-7.0 for most crops",
            "Apply lime 6-12 months before planting for best results",
            "Use buffer pH for lime rate calculations on high organic matter soils",
            "Monitor pH changes over time with regular soil testing",
            "Consider crop-specific pH requirements (blueberries prefer 4.5-5.5)"
        ],
        calculations={
            "lime_rate_formula": "Lime_rate = (Target_pH - Current_pH) * Buffer_pH_factor * Soil_depth",
            "parameters": {
                "buffer_ph_factors": {
                    "sandy_soil": 1000,
                    "loam_soil": 1500,
                    "clay_soil": 2000
                },
                "standard_depth": 6.67  # 8 inches converted to tons/acre factor
            }
        },
        source=KnowledgeSource(
            type=SourceType.EXTENSION_SERVICE,
            name="University of Wisconsin Extension A2809",
            credibility_score=0.92
        ),
        applicability={
            "regions": ["midwest", "northeast", "southeast"],
            "crops": ["corn", "soybean", "wheat", "alfalfa"],
            "soil_types": ["all"]
        },
        tags=["pH", "lime", "soil_health", "nutrient_availability"],
        expert_validated=True,
        validation_date=date(2024, 1, 10)
    )
    
    # Crop rotation benefits knowledge
    crop_rotation = KnowledgeItem(
        knowledge_id="crop_rotation_benefits_001",
        category=KnowledgeCategory.CROP_MANAGEMENT,
        subcategory="rotation",
        title="Benefits of Crop Rotation Systems",
        description="Comprehensive overview of crop rotation benefits for soil health, pest management, and economic returns.",
        guidelines=[
            "Include legumes to fix nitrogen and reduce fertilizer needs",
            "Rotate crop families to break pest and disease cycles",
            "Use deep-rooted crops to improve soil structure",
            "Consider market factors and equipment compatibility",
            "Plan 3-4 year rotations for maximum benefits"
        ],
        regional_variations=[
            {
                "region": "midwest",
                "modifications": "Corn-soybean rotation is most common, consider adding wheat or cover crops"
            },
            {
                "region": "southeast",
                "modifications": "Include cotton, peanuts, or winter cover crops in rotation"
            }
        ],
        source=KnowledgeSource(
            type=SourceType.RESEARCH_PAPER,
            name="Crop Rotation Effects on Soil Health and Productivity",
            credibility_score=0.88
        ),
        applicability={
            "regions": ["all"],
            "crops": ["corn", "soybean", "wheat", "cotton"],
            "farm_sizes": {"min_acres": 20, "max_acres": 5000}
        },
        tags=["rotation", "soil_health", "pest_management", "nitrogen_fixation"],
        expert_validated=True,
        validation_date=date(2024, 1, 20)
    )
    
    # Add knowledge items to the knowledge base
    try:
        kb.add_knowledge_item(corn_nitrogen)
        kb.add_knowledge_item(soil_ph)
        kb.add_knowledge_item(crop_rotation)
        
        logger.info("Initial knowledge base seeding completed successfully")
        
    except Exception as e:
        logger.error(f"Error seeding knowledge base: {e}")
        raise


if __name__ == "__main__":
    # Test the knowledge base
    try:
        print("Testing AFAS Knowledge Base...")
        
        with initialize_knowledge_base() as kb:
            # Seed initial knowledge
            seed_initial_knowledge(kb)
            
            # Test knowledge retrieval
            print("\n1. Testing knowledge retrieval by category:")
            nutrient_knowledge = kb.get_knowledge_by_category(
                KnowledgeCategory.NUTRIENT_MANAGEMENT,
                expert_validated_only=True
            )
            print(f"   Found {len(nutrient_knowledge)} nutrient management items")
            
            print("\n2. Testing knowledge search:")
            search_results = kb.search_knowledge("nitrogen corn fertilizer")
            print(f"   Found {len(search_results)} items for 'nitrogen corn fertilizer'")
            
            print("\n3. Testing crop information retrieval:")
            corn_info = kb.get_crop_information("corn")
            if corn_info:
                print(f"   Corn info: {corn_info['crop_name']} - {corn_info['category']}")
            
            print("\n4. Testing soil test interpretation:")
            interpretation = kb.get_soil_test_interpretation(
                ph=5.8, organic_matter=2.1, phosphorus=12, potassium=95
            )
            print(f"   Soil assessment: {interpretation.get('overall_assessment', 'N/A')}")
            
            print("\n✅ Knowledge base test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Knowledge base test failed: {e}")