"""
Farmer Preference Manager

Comprehensive farmer preference storage and management system for crop type filtering.
Implements hierarchical preferences, preference inheritance, and preference versioning.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from decimal import Decimal

try:
    from ..database.crop_taxonomy_db import get_db_connection
    from ..models.preference_models import PreferenceProfile, PreferenceType
except ImportError:
    from database.crop_taxonomy_db import get_db_connection
    from models.preference_models import PreferenceProfile, PreferenceType

logger = logging.getLogger(__name__)


class PreferenceCategory:
    """Enumeration of preference categories with validation rules"""
    CROP_TYPES = "crop_types"
    MANAGEMENT_STYLE = "management_style"
    RISK_TOLERANCE = "risk_tolerance"
    MARKET_FOCUS = "market_focus"
    SUSTAINABILITY = "sustainability"
    LABOR_REQUIREMENTS = "labor_requirements"
    EQUIPMENT_PREFERENCES = "equipment_preferences"
    CERTIFICATION_GOALS = "certification_goals"
    YIELD_PRIORITIES = "yield_priorities"
    ECONOMIC_FACTORS = "economic_factors"

    @classmethod
    def all_categories(cls) -> List[str]:
        return [
            cls.CROP_TYPES, cls.MANAGEMENT_STYLE, cls.RISK_TOLERANCE,
            cls.MARKET_FOCUS, cls.SUSTAINABILITY, cls.LABOR_REQUIREMENTS,
            cls.EQUIPMENT_PREFERENCES, cls.CERTIFICATION_GOALS,
            cls.YIELD_PRIORITIES, cls.ECONOMIC_FACTORS
        ]

    @classmethod
    def validate_category(cls, category: str) -> bool:
        return category in cls.all_categories()


class FarmerPreference:
    """Data model for individual farmer preference entries"""
    
    def __init__(
        self,
        id: Optional[UUID] = None,
        user_id: UUID = None,
        preference_category: str = None,
        preference_data: Dict[str, Any] = None,
        weight: float = 1.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        version: int = 1,
        active: bool = True
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.preference_category = preference_category
        self.preference_data = preference_data or {}
        self.weight = max(0.0, min(1.0, weight))  # Ensure weight is between 0 and 1
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.version = version
        self.active = active

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'preference_category': self.preference_category,
            'preference_data': self.preference_data,
            'weight': float(self.weight),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'active': self.active
        }


class FarmerPreferenceManager:
    """
    Comprehensive farmer preference management system.
    
    Features:
    - Hierarchical preferences with inheritance
    - Preference versioning for tracking changes
    - Category-based preference organization
    - Weight-based preference prioritization
    - CRUD operations with validation
    """

    def __init__(self):
        self.db_connection = None

    async def _get_connection(self):
        """Get database connection"""
        if not self.db_connection:
            self.db_connection = await get_db_connection()
        return self.db_connection

    def _validate_preference_data(self, category: str, data: Dict[str, Any]) -> bool:
        """Validate preference data structure based on category"""
        if not PreferenceCategory.validate_category(category):
            return False

        required_fields = {
            PreferenceCategory.CROP_TYPES: ['preferred_crops'],
            PreferenceCategory.MANAGEMENT_STYLE: [],
            PreferenceCategory.RISK_TOLERANCE: ['level'],
            PreferenceCategory.MARKET_FOCUS: [],
            PreferenceCategory.SUSTAINABILITY: [],
            PreferenceCategory.LABOR_REQUIREMENTS: [],
            PreferenceCategory.EQUIPMENT_PREFERENCES: [],
            PreferenceCategory.CERTIFICATION_GOALS: [],
            PreferenceCategory.YIELD_PRIORITIES: [],
            PreferenceCategory.ECONOMIC_FACTORS: []
        }

        category_required = required_fields.get(category, [])
        return all(field in data for field in category_required)

    async def create_preference(
        self,
        user_id: UUID,
        preference_category: str,
        preference_data: Dict[str, Any],
        weight: float = 1.0
    ) -> FarmerPreference:
        """Create a new farmer preference"""
        
        if not PreferenceCategory.validate_category(preference_category):
            raise ValueError(f"Invalid preference category: {preference_category}")

        if not self._validate_preference_data(preference_category, preference_data):
            raise ValueError(f"Invalid preference data for category: {preference_category}")

        conn = await self._get_connection()
        
        preference = FarmerPreference(
            user_id=user_id,
            preference_category=preference_category,
            preference_data=preference_data,
            weight=weight
        )

        query = """
        INSERT INTO farmer_preferences 
        (id, user_id, preference_category, preference_data, weight, created_at, updated_at, version, active)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """
        
        try:
            result = await conn.fetchrow(
                query,
                preference.id,
                preference.user_id,
                preference.preference_category,
                json.dumps(preference.preference_data),
                Decimal(str(preference.weight)),
                preference.created_at,
                preference.updated_at,
                preference.version,
                preference.active
            )
            
            if result:
                logger.info(f"Created preference {preference.id} for user {user_id}")
                return self._row_to_preference(result)
            else:
                raise Exception("Failed to create preference")
                
        except Exception as e:
            logger.error(f"Error creating preference: {e}")
            raise

    async def get_user_preferences(
        self,
        user_id: UUID,
        category: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[FarmerPreference]:
        """Get all preferences for a user, optionally filtered by category"""
        
        conn = await self._get_connection()
        
        base_query = "SELECT * FROM farmer_preferences WHERE user_id = $1"
        params = [user_id]
        
        if not include_inactive:
            base_query += " AND active = TRUE"
            
        if category:
            if not PreferenceCategory.validate_category(category):
                raise ValueError(f"Invalid preference category: {category}")
            base_query += f" AND preference_category = ${len(params) + 1}"
            params.append(category)
            
        base_query += " ORDER BY preference_category, weight DESC, created_at DESC"
        
        try:
            results = await conn.fetch(base_query, *params)
            preferences = [self._row_to_preference(row) for row in results]
            logger.info(f"Retrieved {len(preferences)} preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            raise

    async def update_preference(
        self,
        preference_id: UUID,
        preference_data: Optional[Dict[str, Any]] = None,
        weight: Optional[float] = None,
        active: Optional[bool] = None
    ) -> FarmerPreference:
        """Update an existing preference"""
        
        conn = await self._get_connection()
        
        # First get the current preference to validate updates
        current = await self.get_preference_by_id(preference_id)
        if not current:
            raise ValueError(f"Preference not found: {preference_id}")

        update_fields = []
        params = []
        param_index = 1

        if preference_data is not None:
            if not self._validate_preference_data(current.preference_category, preference_data):
                raise ValueError(f"Invalid preference data for category: {current.preference_category}")
            update_fields.append(f"preference_data = ${param_index}")
            params.append(json.dumps(preference_data))
            param_index += 1

        if weight is not None:
            weight = max(0.0, min(1.0, weight))
            update_fields.append(f"weight = ${param_index}")
            params.append(Decimal(str(weight)))
            param_index += 1

        if active is not None:
            update_fields.append(f"active = ${param_index}")
            params.append(active)
            param_index += 1

        if not update_fields:
            return current

        # Add the preference_id as the last parameter
        params.append(preference_id)
        
        query = f"""
        UPDATE farmer_preferences 
        SET {', '.join(update_fields)}
        WHERE id = ${param_index}
        RETURNING *
        """

        try:
            result = await conn.fetchrow(query, *params)
            if result:
                logger.info(f"Updated preference {preference_id}")
                return self._row_to_preference(result)
            else:
                raise Exception("Failed to update preference")
                
        except Exception as e:
            logger.error(f"Error updating preference {preference_id}: {e}")
            raise

    async def get_preference_by_id(self, preference_id: UUID) -> Optional[FarmerPreference]:
        """Get a specific preference by ID"""
        
        conn = await self._get_connection()
        
        query = "SELECT * FROM farmer_preferences WHERE id = $1"
        
        try:
            result = await conn.fetchrow(query, preference_id)
            return self._row_to_preference(result) if result else None
            
        except Exception as e:
            logger.error(f"Error retrieving preference {preference_id}: {e}")
            raise

    async def delete_preference(self, preference_id: UUID) -> bool:
        """Soft delete a preference by setting active = False"""
        
        updated_preference = await self.update_preference(
            preference_id=preference_id,
            active=False
        )
        return updated_preference is not None

    async def get_preference_hierarchy(
        self,
        user_id: UUID,
        category: str
    ) -> Dict[str, Any]:
        """
        Get preference hierarchy for a category with inheritance logic.
        Returns computed effective preferences considering weights and inheritance.
        """
        
        if not PreferenceCategory.validate_category(category):
            raise ValueError(f"Invalid preference category: {category}")
            
        preferences = await self.get_user_preferences(user_id, category)
        
        if not preferences:
            return self._get_default_preferences(category)
            
        # Compute effective preferences based on weights
        effective_prefs = {}
        total_weight = sum(pref.weight for pref in preferences)
        
        if total_weight == 0:
            return self._get_default_preferences(category)
            
        for pref in preferences:
            weight_ratio = pref.weight / total_weight
            for key, value in pref.preference_data.items():
                if key not in effective_prefs:
                    effective_prefs[key] = []
                effective_prefs[key].append({
                    'value': value,
                    'weight': weight_ratio,
                    'preference_id': str(pref.id)
                })
        
        # Resolve conflicts and compute final values
        resolved_prefs = {}
        for key, values in effective_prefs.items():
            resolved_prefs[key] = self._resolve_preference_conflict(key, values)
            
        return {
            'category': category,
            'user_id': str(user_id),
            'preferences': resolved_prefs,
            'total_weight': total_weight,
            'computed_at': datetime.now().isoformat()
        }

    async def get_preference_history(
        self,
        preference_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get version history for a preference"""
        
        conn = await self._get_connection()
        
        query = """
        SELECT * FROM farmer_preference_history 
        WHERE preference_id = $1 
        ORDER BY version DESC, archived_at DESC 
        LIMIT $2
        """
        
        try:
            results = await conn.fetch(query, preference_id, limit)
            history = []
            for row in results:
                history.append({
                    'id': str(row['id']),
                    'preference_id': str(row['preference_id']),
                    'user_id': str(row['user_id']),
                    'preference_category': row['preference_category'],
                    'preference_data': json.loads(row['preference_data']),
                    'weight': float(row['weight']),
                    'version': row['version'],
                    'created_at': row['created_at'].isoformat(),
                    'archived_at': row['archived_at'].isoformat()
                })
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving preference history for {preference_id}: {e}")
            raise

    def _row_to_preference(self, row) -> FarmerPreference:
        """Convert database row to FarmerPreference object"""
        return FarmerPreference(
            id=row['id'],
            user_id=row['user_id'],
            preference_category=row['preference_category'],
            preference_data=json.loads(row['preference_data']),
            weight=float(row['weight']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            version=row['version'],
            active=row['active']
        )

    def _get_default_preferences(self, category: str) -> Dict[str, Any]:
        """Get default preferences for a category"""
        defaults = {
            PreferenceCategory.CROP_TYPES: {
                'preferred_crops': [],
                'avoided_crops': [],
                'new_crop_interest': True
            },
            PreferenceCategory.MANAGEMENT_STYLE: {
                'organic': False,
                'conventional': True,
                'precision_ag': False,
                'no_till': False
            },
            PreferenceCategory.RISK_TOLERANCE: {
                'level': 'moderate',
                'diversification_preference': True,
                'experimental_willingness': 0.5
            },
            PreferenceCategory.MARKET_FOCUS: {
                'local_markets': True,
                'commodity_markets': True,
                'specialty_crops': False,
                'value_added': False
            },
            PreferenceCategory.SUSTAINABILITY: {
                'carbon_sequestration': True,
                'water_conservation': True,
                'biodiversity': True,
                'soil_health': True
            }
        }
        
        return {
            'category': category,
            'preferences': defaults.get(category, {}),
            'is_default': True
        }

    def _resolve_preference_conflict(self, key: str, values: List[Dict[str, Any]]) -> Any:
        """Resolve conflicts when multiple preferences exist for the same key"""
        if not values:
            return None
            
        if len(values) == 1:
            return values[0]['value']
            
        # For boolean values, use weighted average approach
        if all(isinstance(v['value'], bool) for v in values):
            weighted_sum = sum(v['value'] * v['weight'] for v in values)
            return weighted_sum > 0.5
            
        # For numeric values, use weighted average
        if all(isinstance(v['value'], (int, float)) for v in values):
            return sum(v['value'] * v['weight'] for v in values)
            
        # For lists, merge and deduplicate
        if all(isinstance(v['value'], list) for v in values):
            merged = []
            for v in values:
                merged.extend(v['value'])
            return list(set(merged))
            
        # For strings and other types, use highest weight
        highest_weight_value = max(values, key=lambda x: x['weight'])
        return highest_weight_value['value']


# Global instance for dependency injection
farmer_preference_manager = FarmerPreferenceManager()