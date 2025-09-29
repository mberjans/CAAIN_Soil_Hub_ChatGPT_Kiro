"""
Rotation Plan Storage Service

Handles database operations for crop rotation plans with MongoDB and Redis caching.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

from ..models.rotation_models import CropRotationPlan, RotationPlanUpdateRequest

# Database imports
try:
    from databases.python.database_config import get_mongodb_collection, get_redis_client
except ImportError:
    # Fallback for testing/development
    def get_mongodb_collection(name): return None
    def get_redis_client(db=0): return None

logger = logging.getLogger(__name__)


class RotationStorageService:
    """Service for storing and retrieving rotation plans."""
    
    def __init__(self):
        """Initialize rotation storage service."""
        self.collection_name = "rotation_plans"
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.cache_db = 1  # Use Redis DB 1 for caching
        
    def _get_collection(self):
        """Get MongoDB collection for rotation plans."""
        try:
            return get_mongodb_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Failed to get MongoDB collection: {e}")
            return None
    
    def _get_cache_client(self):
        """Get Redis client for caching."""
        try:
            return get_redis_client(self.cache_db)
        except Exception as e:
            logger.error(f"Failed to get Redis client: {e}")
            return None
    
    def _cache_key(self, plan_id: str) -> str:
        """Generate cache key for rotation plan."""
        return f"rotation_plan:{plan_id}"
    
    def _plan_to_dict(self, plan: CropRotationPlan) -> Dict[str, Any]:
        """Convert CropRotationPlan to dictionary for storage."""
        plan_dict = asdict(plan)
        # Convert datetime objects to ISO strings
        if isinstance(plan_dict.get('created_date'), datetime):
            plan_dict['created_date'] = plan_dict['created_date'].isoformat()
        return plan_dict
    
    def _dict_to_plan(self, plan_dict: Dict[str, Any]) -> CropRotationPlan:
        """Convert dictionary to CropRotationPlan."""
        # Convert ISO strings back to datetime
        if isinstance(plan_dict.get('created_date'), str):
            plan_dict['created_date'] = datetime.fromisoformat(plan_dict['created_date'])
        
        # Handle missing fields with defaults
        defaults = {
            'goals': [],
            'constraints': [],
            'benefit_scores': {},
            'risk_scores': {},
            'implementation_status': {},
            'actual_vs_planned': {}
        }
        
        for key, default_value in defaults.items():
            if key not in plan_dict:
                plan_dict[key] = default_value
        
        return CropRotationPlan(**plan_dict)
    
    async def create_plan(self, plan: CropRotationPlan) -> bool:
        """Create a new rotation plan."""
        try:
            collection = self._get_collection()
            if not collection:
                logger.error("MongoDB collection not available")
                return False
            
            # Check if plan already exists
            existing = collection.find_one({"plan_id": plan.plan_id})
            if existing:
                raise ValueError(f"Rotation plan with ID {plan.plan_id} already exists")
            
            # Insert into MongoDB
            plan_dict = self._plan_to_dict(plan)
            result = collection.insert_one(plan_dict)
            
            if result.inserted_id:
                # Cache the plan
                await self._cache_plan(plan)
                logger.info(f"Created rotation plan: {plan.plan_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create rotation plan {plan.plan_id}: {e}")
            return False
    
    async def get_plan(self, plan_id: str) -> Optional[CropRotationPlan]:
        """Get rotation plan by ID, with caching."""
        try:
            # Try cache first
            cached_plan = await self._get_cached_plan(plan_id)
            if cached_plan:
                return cached_plan
            
            # Get from MongoDB
            collection = self._get_collection()
            if not collection:
                logger.error("MongoDB collection not available")
                return None
            
            plan_dict = collection.find_one({"plan_id": plan_id})
            if not plan_dict:
                return None
            
            # Remove MongoDB's _id field
            plan_dict.pop('_id', None)
            
            plan = self._dict_to_plan(plan_dict)
            
            # Cache for future requests
            await self._cache_plan(plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to get rotation plan {plan_id}: {e}")
            return None
    
    async def update_plan(self, plan_id: str, updates: RotationPlanUpdateRequest) -> Optional[CropRotationPlan]:
        """Update rotation plan with partial updates."""
        try:
            # Get existing plan
            existing_plan = await self.get_plan(plan_id)
            if not existing_plan:
                return None
            
            # Apply updates to existing plan
            updated_plan = await self._apply_updates(existing_plan, updates)
            
            # Update in MongoDB
            collection = self._get_collection()
            if not collection:
                logger.error("MongoDB collection not available")
                return None
            
            update_dict = self._plan_to_dict(updated_plan)
            update_dict.pop('_id', None)  # Remove if present
            
            result = collection.replace_one(
                {"plan_id": plan_id},
                update_dict
            )
            
            if result.modified_count > 0:
                # Update cache
                await self._cache_plan(updated_plan)
                logger.info(f"Updated rotation plan: {plan_id}")
                return updated_plan
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to update rotation plan {plan_id}: {e}")
            return None
    
    async def delete_plan(self, plan_id: str) -> bool:
        """Delete rotation plan."""
        try:
            collection = self._get_collection()
            if not collection:
                logger.error("MongoDB collection not available")
                return False
            
            result = collection.delete_one({"plan_id": plan_id})
            
            if result.deleted_count > 0:
                # Remove from cache
                await self._remove_cached_plan(plan_id)
                logger.info(f"Deleted rotation plan: {plan_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete rotation plan {plan_id}: {e}")
            return False
    
    async def list_plans(self, field_id: Optional[str] = None, farm_id: Optional[str] = None, 
                        is_active: Optional[bool] = None, limit: int = 100) -> List[CropRotationPlan]:
        """List rotation plans with optional filtering."""
        try:
            collection = self._get_collection()
            if not collection:
                logger.error("MongoDB collection not available")
                return []
            
            # Build query
            query = {}
            if field_id:
                query["field_id"] = field_id
            if farm_id:
                query["farm_id"] = farm_id
            if is_active is not None:
                query["is_active"] = is_active
            
            # Execute query
            cursor = collection.find(query).limit(limit).sort("created_date", -1)
            plans = []
            
            for plan_dict in cursor:
                plan_dict.pop('_id', None)
                try:
                    plan = self._dict_to_plan(plan_dict)
                    plans.append(plan)
                except Exception as e:
                    logger.warning(f"Failed to parse plan {plan_dict.get('plan_id', 'unknown')}: {e}")
                    continue
            
            return plans
            
        except Exception as e:
            logger.error(f"Failed to list rotation plans: {e}")
            return []
    
    async def _apply_updates(self, existing_plan: CropRotationPlan, 
                           updates: RotationPlanUpdateRequest) -> CropRotationPlan:
        """Apply partial updates to existing plan."""
        # Create updated plan by copying existing and applying changes
        updated_dict = asdict(existing_plan)
        
        # Apply non-None updates
        for field, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                if field in ['goals', 'constraints']:
                    # For complex fields, replace entirely
                    updated_dict[field] = [goal.dict() if hasattr(goal, 'dict') else goal for goal in value]
                else:
                    updated_dict[field] = value
        
        # Update version and timestamp
        updated_dict['version'] += 1
        updated_dict['created_date'] = datetime.utcnow()  # Update timestamp
        
        return self._dict_to_plan(updated_dict)
    
    async def _cache_plan(self, plan: CropRotationPlan):
        """Cache rotation plan in Redis."""
        try:
            redis_client = self._get_cache_client()
            if not redis_client:
                return
            
            cache_key = self._cache_key(plan.plan_id)
            plan_json = json.dumps(self._plan_to_dict(plan), default=str)
            redis_client.setex(cache_key, self.cache_ttl, plan_json)
            
        except Exception as e:
            logger.warning(f"Failed to cache rotation plan {plan.plan_id}: {e}")
    
    async def _get_cached_plan(self, plan_id: str) -> Optional[CropRotationPlan]:
        """Get cached rotation plan from Redis."""
        try:
            redis_client = self._get_cache_client()
            if not redis_client:
                return None
            
            cache_key = self._cache_key(plan_id)
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                plan_dict = json.loads(cached_data)
                return self._dict_to_plan(plan_dict)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get cached rotation plan {plan_id}: {e}")
            return None
    
    async def _remove_cached_plan(self, plan_id: str):
        """Remove cached rotation plan from Redis."""
        try:
            redis_client = self._get_cache_client()
            if not redis_client:
                return
                
            cache_key = self._cache_key(plan_id)
            redis_client.delete(cache_key)
            
        except Exception as e:
            logger.warning(f"Failed to remove cached rotation plan {plan_id}: {e}")


# Global service instance
rotation_storage_service = RotationStorageService()