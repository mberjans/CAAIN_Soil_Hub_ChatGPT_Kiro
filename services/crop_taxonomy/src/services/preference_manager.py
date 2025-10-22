from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from ..models.filtering_models import FarmerPreference, CropFilteringAttributes
from ..models.crop_models import CropVariety
from ..schemas.preference_schemas import PreferenceCreate, PreferenceUpdate, PreferenceResponse, PreferenceLearningRequest, PreferenceLearningResponse

class FarmerPreferenceManager:
    """Comprehensive farmer preference storage (TICKET-005_crop-type-filtering-3.1)"""

    def __init__(self, db: Session):
        self.db = db

    async def create_preference(self, preference: PreferenceCreate) -> PreferenceResponse:
        """Create new farmer preference"""
        db_preference = FarmerPreference(
            user_id=preference.user_id,
            preference_category=preference.preference_category,
            preferred_filters=preference.preference_data,
            weight=preference.weight
        )
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def get_user_preferences(self, user_id: UUID) -> List[PreferenceResponse]:
        """Get all preferences for a user"""
        preferences = self.db.query(FarmerPreference).filter(
            FarmerPreference.user_id == user_id
        ).all()
        return [PreferenceResponse.from_orm(p) for p in preferences]

    async def update_preference(self, preference_id: UUID, update: PreferenceUpdate) -> PreferenceResponse:
        """Update existing preference"""
        db_preference = self.db.query(FarmerPreference).filter(
            FarmerPreference.id == preference_id
        ).first()

        if not db_preference:
            raise ValueError(f"Preference {preference_id} not found")

        if update.preference_data is not None:
            db_preference.preferred_filters = update.preference_data
        if update.weight is not None:
            db_preference.weight = update.weight

        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def delete_preference(self, preference_id: UUID) -> bool:
        """Delete preference"""
        result = self.db.query(FarmerPreference).filter(
            FarmerPreference.id == preference_id
        ).delete()
        self.db.commit()
        return result > 0

    async def save_preferences(
        self,
        user_id: UUID,
        preference_category: str,
        preference_data: Dict[str, Any],
        weight: float = 1.0
    ) -> PreferenceResponse:
        """
        Save farmer preferences. Creates a new preference or updates an existing one
        for a given user_id and preference_category.
        """
        existing_preference = self.db.query(FarmerPreference).filter(
            FarmerPreference.user_id == user_id,
            FarmerPreference.preference_category == preference_category
        ).first()

        if existing_preference:
            # Update existing preference
            existing_preference.preference_data = preference_data
            existing_preference.weight = weight
            self.db.commit()
            self.db.refresh(existing_preference)
            return PreferenceResponse.from_orm(existing_preference)
        else:
            # Create new preference
            new_preference = PreferenceCreate(
                user_id=user_id,
                preference_category=preference_category,
                preference_data=preference_data,
                weight=weight
            )
            return await self.create_preference(new_preference)

    async def load_preferences(self, user_id: UUID) -> List[PreferenceResponse]:
        """Load all preferences for a user"""
        return await self.get_user_preferences(user_id)

    async def learn_from_selection(self, request: PreferenceLearningRequest) -> PreferenceLearningResponse:
        """
        Learns from user's selected and rejected varieties to adapt preferences.
        """
        user_id = request.user_id
        selected_varieties_ids = request.selected_varieties
        rejected_varieties_ids = request.rejected_varieties or []

        # 1. Retrieve existing preferences or create a default one
        user_preference = self.db.query(FarmerPreference).filter(
            FarmerPreference.user_id == user_id,
            FarmerPreference.preference_category == "crop_filters"
        ).first()

        if not user_preference:
        user_preference = FarmerPreference(
            user_id=learning_request.user_id,
            preference_category="crop_filters", # Default category for learned preferences
            preferred_filters=preference_data,
            filter_weights=filter_weights
        )
            self.db.add(user_preference)
            new_preferences_created = 1
        else:
            new_preferences_created = 0

        # Initialize preference data and weights if empty
        if not user_preference.preference_data:
            user_preference.preference_data = {}
        if not user_preference.filter_weights:
            user_preference.filter_weights = {
                "climate_zones": 0.5,
                "soil_ph_range": 0.5,
                "soil_types": 0.5,
                "maturity_days_range": 0.5,
                "drought_tolerance": 0.5,
                "heat_tolerance": 0.5,
                "cold_tolerance": 0.5,
                "pest_resistance": 0.5,
                "disease_resistance": 0.5,
                "market_class": 0.5,
                "certifications": 0.5,
                "management_complexity": 0.5
            }

        # Store original preference data for comparison
        original_preference_data = user_preference.preference_data.copy()
        original_filter_weights = user_preference.filter_weights.copy()

        # 2. Process selected varieties
        selected_attributes = self._get_aggregated_attributes(selected_varieties_ids)
        rejected_attributes = self._get_aggregated_attributes(rejected_varieties_ids)

        # 3. Update preferred_filters and filter_weights
        preferences_updated_count = 0
        learned_patterns = []

        # Example: Learning from drought tolerance
        if "drought_tolerance" in selected_attributes:
            for tolerance_level, count in selected_attributes["drought_tolerance"].items():
                if tolerance_level not in rejected_attributes.get("drought_tolerance", {}):
                    # Increase preference for this tolerance level
                    current_value = user_preference.preference_data.get("drought_tolerance", {})
                    current_value[tolerance_level] = current_value.get(tolerance_level, 0) + count
                    user_preference.preference_data["drought_tolerance"] = current_value
                    user_preference.filter_weights["drought_tolerance"] = min(1.0, user_preference.filter_weights["drought_tolerance"] + 0.1)
                    preferences_updated_count += 1
                    learned_patterns.append(f"Increased preference for drought tolerance: {tolerance_level}")

        # Example: Learning from pest resistance
        if "pest_resistance_traits" in selected_attributes:
            for pest, resistance_level_counts in selected_attributes["pest_resistance_traits"].items():
                for level, count in resistance_level_counts.items():
                    if level not in rejected_attributes.get("pest_resistance_traits", {}).get(pest, {}):
                        current_value = user_preference.preference_data.get("pest_resistance", {})
                        if pest not in current_value:
                            current_value[pest] = {}
                        current_value[pest][level] = current_value[pest].get(level, 0) + count
                        user_preference.preference_data["pest_resistance"] = current_value
                        user_preference.filter_weights["pest_resistance"] = min(1.0, user_preference.filter_weights["pest_resistance"] + 0.05)
                        preferences_updated_count += 1
                        learned_patterns.append(f"Increased preference for {pest} resistance: {level}")

        # Example: Decreasing preference for attributes in rejected varieties
        if "drought_tolerance" in rejected_attributes:
            for tolerance_level, count in rejected_attributes["drought_tolerance"].items():
                if tolerance_level not in selected_attributes.get("drought_tolerance", {}):
                    current_value = user_preference.preference_data.get("drought_tolerance", {})
                    if tolerance_level in current_value:
                        current_value[tolerance_level] = max(0, current_value.get(tolerance_level, 0) - count)
                        if current_value[tolerance_level] == 0:
                            del current_value[tolerance_level]
                        user_preference.preference_data["drought_tolerance"] = current_value
                        user_preference.filter_weights["drought_tolerance"] = max(0.0, user_preference.filter_weights["drought_tolerance"] - 0.05)
                        preferences_updated_count += 1
                        learned_patterns.append(f"Decreased preference for drought tolerance: {tolerance_level}")

        # 4. Save updated preferences
        self.db.commit()
        self.db.refresh(user_preference)

        # 5. Calculate confidence improvements (simple heuristic for now)
        confidence_improvements = {}
        if preferences_updated_count > 0:
            confidence_improvements["overall"] = 0.1 * preferences_updated_count # Simple heuristic

        return PreferenceLearningResponse(
            preferences_updated=preferences_updated_count,
            new_preferences_created=new_preferences_created,
            confidence_improvements=confidence_improvements,
            learned_patterns=learned_patterns
        )

    def _get_aggregated_attributes(self, variety_ids: List[UUID]) -> Dict[str, Any]:
        """
        Aggregates attributes from a list of variety IDs.
        Returns a dictionary where keys are attribute names and values are counts or aggregated data.
        """
        aggregated_attrs = {}

        if not variety_ids:
            return aggregated_attrs

        # Fetch CropVariety and CropFilteringAttributes for the given IDs
        results = self.db.query(CropVariety, CropFilteringAttributes).join(
            CropFilteringAttributes, CropVariety.id == CropFilteringAttributes.variety_id
        ).filter(
            CropVariety.id.in_(variety_ids)
        ).all()

        for variety, filtering_attrs in results:
            # Aggregate drought tolerance
            if filtering_attrs.drought_tolerance:
                aggregated_attrs.setdefault("drought_tolerance", {}).setdefault(filtering_attrs.drought_tolerance, 0)
                aggregated_attrs["drought_tolerance"][filtering_attrs.drought_tolerance] += 1

            # Aggregate pest resistance traits
            if filtering_attrs.pest_resistance_traits:
                for pest, level in filtering_attrs.pest_resistance_traits.items():
                    aggregated_attrs.setdefault("pest_resistance_traits", {}).setdefault(pest, {}).setdefault(level, 0)
                    aggregated_attrs["pest_resistance_traits"][pest][level] += 1

            # TODO: Add aggregation for other attributes like soil_ph_range, climate_zones, etc.

        return aggregated_attrs