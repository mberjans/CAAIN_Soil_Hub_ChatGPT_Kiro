from typing import List, Optional, Dict, Any
from uuid import UUID
from ..models.fertilizer_type_models import FertilizerType, FertilizerTypeEnum, FertilizerFormEnum, FertilizerReleaseTypeEnum, EnvironmentalImpactEnum, SuitabilityCriteria

class FertilizerTypeService:
    """Service for managing fertilizer types."""

    def __init__(self):
        # In-memory storage for demonstration purposes
        self._fertilizer_types: Dict[UUID, FertilizerType] = {}
        self._initialize_default_fertilizer_types()

    def _initialize_default_fertilizer_types(self):
        """Initialize with some default fertilizer types."""
        # Example: Urea (Synthetic, Granular, Quick Release)
        urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
        self._fertilizer_types[urea_id] = FertilizerType(
            id=urea_id,
            name="Urea",
            description="High nitrogen synthetic fertilizer, quick release.",
            npk_ratio="46-0-0",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC,
            form=FertilizerFormEnum.GRANULAR,
            release_type=FertilizerReleaseTypeEnum.QUICK,
            cost_per_unit=0.50,
            unit="USD/kg",
            environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
            suitability_criteria=SuitabilityCriteria(
                min_ph=6.0,
                max_ph=7.5,
                crop_types=["corn", "wheat", "rice"]
            )
        )

        # Example: Compost (Organic, Granular, Slow Release)
        compost_id = UUID("b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12")
        self._fertilizer_types[compost_id] = FertilizerType(
            id=compost_id,
            name="Compost",
            description="Organic soil amendment, slow release of nutrients.",
            npk_ratio="1-0.5-1",
            fertilizer_type=FertilizerTypeEnum.ORGANIC,
            form=FertilizerFormEnum.GRANULAR,
            release_type=FertilizerReleaseTypeEnum.SLOW,
            cost_per_unit=0.20,
            unit="USD/kg",
            environmental_impact_score=EnvironmentalImpactEnum.LOW,
            suitability_criteria=SuitabilityCriteria(
                min_ph=5.5,
                max_ph=8.0,
                soil_types=["loam", "clay", "sandy"]
            )
        )

        # Example: Liquid Fish Emulsion (Organic, Liquid, Quick Release)
        fish_emulsion_id = UUID("c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13")
        self._fertilizer_types[fish_emulsion_id] = FertilizerType(
            id=fish_emulsion_id,
            name="Liquid Fish Emulsion",
            description="Organic liquid fertilizer, quick nutrient availability.",
            npk_ratio="5-1-1",
            fertilizer_type=FertilizerTypeEnum.ORGANIC,
            form=FertilizerFormEnum.LIQUID,
            release_type=FertilizerReleaseTypeEnum.QUICK,
            cost_per_unit=1.50,
            unit="USD/L",
            environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
            suitability_criteria=SuitabilityCriteria(
                crop_types=["vegetables", "flowers"]
            )
        )

    def get_all_fertilizer_types(self) -> List[FertilizerType]:
        """Retrieve all available fertilizer types."""
        return list(self._fertilizer_types.values())

    def get_fertilizer_type_by_id(self, fertilizer_id: UUID) -> Optional[FertilizerType]:
        """Retrieve a specific fertilizer type by its ID."""
        return self._fertilizer_types.get(fertilizer_id)

    def create_fertilizer_type(self, fertilizer_data: FertilizerType) -> FertilizerType:
        """Add a new fertilizer type."""
        if fertilizer_data.id in self._fertilizer_types:
            raise ValueError(f"Fertilizer type with ID {fertilizer_data.id} already exists.")
        self._fertilizer_types[fertilizer_data.id] = fertilizer_data
        return fertilizer_data

    def update_fertilizer_type(self, fertilizer_id: UUID, fertilizer_data: FertilizerType) -> Optional[FertilizerType]:
        """Update an existing fertilizer type."""
        if fertilizer_id not in self._fertilizer_types:
            return None
        # Ensure the ID in the data matches the ID in the path
        if fertilizer_data.id != fertilizer_id:
            raise ValueError("Fertilizer ID in path and body do not match.")
        self._fertilizer_types[fertilizer_id] = fertilizer_data
        return fertilizer_data

    def delete_fertilizer_type(self, fertilizer_id: UUID) -> bool:
        """Delete a fertilizer type."""
        if fertilizer_id in self._fertilizer_types:
            del self._fertilizer_types[fertilizer_id]
            return True
        return False

    def filter_fertilizer_types(self, 
                                name: Optional[str] = None,
                                npk_ratio: Optional[str] = None,
                                fertilizer_type: Optional[FertilizerTypeEnum] = None,
                                form: Optional[FertilizerFormEnum] = None,
                                release_type: Optional[FertilizerReleaseTypeEnum] = None,
                                min_cost: Optional[float] = None,
                                max_cost: Optional[float] = None,
                                environmental_impact_score: Optional[EnvironmentalImpactEnum] = None,
                                min_ph: Optional[float] = None,
                                max_ph: Optional[float] = None,
                                soil_type: Optional[str] = None,
                                climate_zone: Optional[str] = None,
                                crop_type: Optional[str] = None,
                                application_method: Optional[str] = None
                                ) -> List[FertilizerType]:
        """Filter fertilizer types based on various criteria."""
        filtered_list = []
        for ft in self._fertilizer_types.values():
            match = True
            if name and name.lower() not in ft.name.lower():
                match = False
            if npk_ratio and npk_ratio != ft.npk_ratio:
                match = False
            if fertilizer_type and fertilizer_type != ft.fertilizer_type:
                match = False
            if form and form != ft.form:
                match = False
            if release_type and release_type != ft.release_type:
                match = False
            if min_cost is not None and ft.cost_per_unit < min_cost:
                match = False
            if max_cost is not None and ft.cost_per_unit > max_cost:
                match = False
            if environmental_impact_score and environmental_impact_score != ft.environmental_impact_score:
                match = False
            
            # Suitability criteria filtering
            if ft.suitability_criteria:
                if min_ph is not None and ft.suitability_criteria.min_ph is not None and min_ph < ft.suitability_criteria.min_ph:
                    match = False
                if max_ph is not None and ft.suitability_criteria.max_ph is not None and max_ph > ft.suitability_criteria.max_ph:
                    match = False
                if soil_type and ft.suitability_criteria.soil_types and soil_type not in ft.suitability_criteria.soil_types:
                    match = False
                if climate_zone and ft.suitability_criteria.climate_zones and climate_zone not in ft.suitability_criteria.climate_zones:
                    match = False
                if crop_type and ft.suitability_criteria.crop_types and crop_type not in ft.suitability_criteria.crop_types:
                    match = False
                if application_method and ft.suitability_criteria.application_methods and application_method not in ft.suitability_criteria.application_methods:
                    match = False

            if match:
                filtered_list.append(ft)
        return filtered_list
