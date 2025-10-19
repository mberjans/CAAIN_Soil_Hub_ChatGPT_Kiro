"""
Crop and planting date integration service.

Provides comprehensive integration between crop taxonomy knowledge and the
planting date optimization engine so fertilizer timing workflows can align
with crop-specific development and regional recommendations.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from utils.module_loader import ensure_service_packages, get_services_root

logger = logging.getLogger(__name__)

_SERVICES_ROOT = get_services_root()
_RECOMMENDATION_ENGINE_SRC = _SERVICES_ROOT / "recommendation_engine" / "src"
_CROP_TAXONOMY_SRC = _SERVICES_ROOT / "crop-taxonomy" / "src"

ensure_service_packages(
    "recommendation_engine",
    {
        "services": _RECOMMENDATION_ENGINE_SRC / "services",
        "models": _RECOMMENDATION_ENGINE_SRC / "models",
    },
)

ensure_service_packages(
    "crop_taxonomy",
    {
        "services": _CROP_TAXONOMY_SRC / "services",
        "models": _CROP_TAXONOMY_SRC / "models",
        "data": _CROP_TAXONOMY_SRC / "data",
    },
    filesystem_name="crop-taxonomy",
)

from services.recommendation_engine.src.services.planting_date_service import (  # pylint: disable=wrong-import-position,import-error
    PlantingDateCalculatorService,
    PlantingWindow,
)
from services.recommendation_engine.src.models.agricultural_models import (  # pylint: disable=wrong-import-position,import-error
    LocationData,
)
from services.crop_taxonomy.src.services.crop_taxonomy_service import (  # pylint: disable=wrong-import-position,import-error
    CropTaxonomyService,
)


@dataclass
class CropIntegrationResult:
    """Structured integration result for crop timing alignment."""

    crop_name: str
    planting_window: PlantingWindow
    crop_metadata: Dict[str, Any] = field(default_factory=dict)
    growth_stage_timeline: Dict[str, str] = field(default_factory=dict)
    nutrient_focus: Dict[str, str] = field(default_factory=dict)
    extension_recommendations: List[str] = field(default_factory=list)
    planting_risk_notes: List[str] = field(default_factory=list)
    summary: str = ""


class CropPlantingIntegrationService:
    """
    Bridge between crop taxonomy data and planting date optimization.
    """

    def __init__(self) -> None:
        self._planting_service = PlantingDateCalculatorService()
        self._taxonomy_service = CropTaxonomyService()
        self._stage_templates = self._build_stage_templates()
        self._nutrient_focus = self._build_stage_nutrient_focus()
        self._extension_guidelines = self._build_extension_guidelines()
        self._region_states = self._build_region_state_map()
        logger.info("CropPlantingIntegrationService initialized")

    async def fetch_crop_metadata(self, crop_name: str) -> Dict[str, Any]:
        """
        Retrieve core taxonomy metadata for a crop by combining taxonomy,
        climate adaptation, and soil requirement information.

        Args:
            crop_name: Common crop name.

        Returns:
            Dictionary containing available metadata fields.
        """
        if not crop_name or len(crop_name.strip()) == 0:
            message = "Crop name required for metadata lookup"
            raise ValueError(message)

        crop_key = crop_name.strip().lower()
        metadata: Dict[str, Any] = {}

        reference_crop = None
        if hasattr(self._taxonomy_service, "reference_crop_index"):
            reference_crop = self._taxonomy_service.reference_crop_index.get(crop_key)

        if reference_crop is None:
            try:
                reference_list = await self._taxonomy_service.list_reference_crops(limit=200)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("Unable to list reference crops: %s", exc)
                reference_list = []

            for item in reference_list:
                name_value = item.crop_name or ""
                if name_value.lower() == crop_key:
                    reference_crop = item
                    break

        if reference_crop is None:
            metadata["display_name"] = crop_name
            metadata["data_quality"] = "unknown"
            return metadata

        metadata["display_name"] = reference_crop.crop_name
        metadata["data_quality"] = "reference_dataset"

        if reference_crop.taxonomic_hierarchy is not None:
            taxonomy_dict = reference_crop.taxonomic_hierarchy.model_dump(exclude_none=True)
            metadata["taxonomic_hierarchy"] = taxonomy_dict

        if reference_crop.agricultural_classification is not None:
            ag_dict = reference_crop.agricultural_classification.model_dump(exclude_none=True)
            metadata["agricultural_classification"] = ag_dict

        if reference_crop.climate_adaptations is not None:
            climate_dict = reference_crop.climate_adaptations.model_dump(exclude_none=True)
            metadata["climate_adaptations"] = climate_dict

        if reference_crop.soil_requirements is not None:
            soil_dict = reference_crop.soil_requirements.model_dump(exclude_none=True)
            metadata["soil_requirements"] = soil_dict

        if reference_crop.nutritional_profile is not None:
            nutrition_dict = reference_crop.nutritional_profile.model_dump(exclude_none=True)
            metadata["nutritional_profile"] = nutrition_dict

        if reference_crop.tags:
            tags_copy: List[str] = []
            for tag in reference_crop.tags:
                tags_copy.append(tag)
            metadata["tags"] = tags_copy

        if reference_crop.search_keywords:
            keywords_copy: List[str] = []
            for keyword in reference_crop.search_keywords:
                keywords_copy.append(keyword)
            metadata["search_keywords"] = keywords_copy

        return metadata

    async def optimize_planting_date(
        self,
        crop_name: str,
        location: Dict[str, Any],
        planting_season: str = "spring",
    ) -> PlantingWindow:
        """
        Optimize planting window for a crop at a specific location using the
        planting date calculator service.

        Args:
            crop_name: Crop name.
            location: Mapping with latitude and longitude fields.
            planting_season: Target planting season label.
        """
        location_data = self._build_location_data(location)
        try:
            planting_window = await self._planting_service.calculate_planting_dates(
                crop_name=crop_name,
                location=location_data,
                planting_season=planting_season,
            )
            return planting_window
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to calculate planting dates for %s: %s", crop_name, exc)
            raise

    async def build_integration_profile(
        self,
        crop_name: str,
        location: Dict[str, Any],
        planting_season: str = "spring",
    ) -> CropIntegrationResult:
        """
        Construct a combined profile of crop metadata and planting guidance.

        Args:
            crop_name: Target crop.
            location: Mapping containing location context.
            planting_season: Desired planting season.

        Returns:
            CropIntegrationResult with metadata and planting recommendations.
        """
        crop_key = crop_name.strip().lower()
        metadata = await self.fetch_crop_metadata(crop_key)
        planting_window = await self.optimize_planting_date(crop_key, location, planting_season)
        location_data = self._build_location_data(location)

        growth_timeline = self._build_growth_stage_timeline(
            crop_key,
            planting_window.optimal_date,
        )

        if planting_window.expected_harvest_date is None and "harvest" in growth_timeline:
            try:
                harvest_date = date.fromisoformat(growth_timeline["harvest"])
                planting_window.expected_harvest_date = harvest_date
            except ValueError:
                logger.debug("Unable to parse harvest date for %s", crop_key)

        nutrient_focus = self._derive_nutrient_focus_map(crop_key)
        extension_recommendations = self._collect_extension_guidelines(crop_key, location_data)
        planting_risk = self._assess_planting_risk(planting_window)

        summary_lines: List[str] = []
        summary_lines.append(
            f"{crop_name.title()} optimal planting date: {planting_window.optimal_date.isoformat()}"
        )
        if planting_window.earliest_safe_date and planting_window.latest_safe_date:
            window_range = (
                f"{planting_window.earliest_safe_date.isoformat()} – "
                f"{planting_window.latest_safe_date.isoformat()}"
            )
            summary_lines.append(f"Safe planting window: {window_range}")

        if planting_window.expected_harvest_date:
            summary_lines.append(
                f"Projected harvest: {planting_window.expected_harvest_date.isoformat()}"
            )

        if len(extension_recommendations) > 0:
            summary_lines.append("Extension guidance integrated for regional alignment.")

        summary_text = "\n".join(summary_lines)

        return CropIntegrationResult(
            crop_name=crop_name,
            planting_window=planting_window,
            crop_metadata=metadata,
            growth_stage_timeline=growth_timeline,
            nutrient_focus=nutrient_focus,
            extension_recommendations=extension_recommendations,
            planting_risk_notes=planting_risk,
            summary=summary_text,
        )

    def _build_location_data(self, location: Dict[str, Any]) -> LocationData:
        """Convert location dictionary into validated LocationData."""
        if location is None:
            raise ValueError("Location information is required")

        data_payload: Dict[str, Any] = {}

        if "latitude" not in location or "longitude" not in location:
            raise ValueError("Latitude and longitude are required for location context")

        data_payload["latitude"] = float(location["latitude"])
        data_payload["longitude"] = float(location["longitude"])

        optional_fields = ["elevation_ft", "address", "state", "county", "climate_zone"]
        for field_name in optional_fields:
            if field_name in location and location[field_name] is not None:
                data_payload[field_name] = location[field_name]

        climate_zone_name = "climate_zone_name"
        if climate_zone_name in location and location[climate_zone_name] is not None:
            data_payload[climate_zone_name] = location[climate_zone_name]

        return LocationData(**data_payload)

    def _build_stage_templates(self) -> Dict[str, List[Tuple[str, int]]]:
        """Create crop growth stage timelines (days after planting)."""
        templates: Dict[str, List[Tuple[str, int]]] = {}

        corn_template: List[Tuple[str, int]] = [
            ("planting", 0),
            ("emergence", 7),
            ("v2", 14),
            ("v4", 21),
            ("v6", 28),
            ("v10", 42),
            ("vt", 56),
            ("r1", 63),
            ("r3", 77),
            ("r5", 91),
            ("harvest", 120),
        ]
        templates["corn"] = corn_template

        soybean_template: List[Tuple[str, int]] = [
            ("planting", 0),
            ("emergence", 6),
            ("v2", 12),
            ("v4", 20),
            ("r1", 35),
            ("r3", 50),
            ("r5", 70),
            ("harvest", 110),
        ]
        templates["soybean"] = soybean_template

        wheat_template: List[Tuple[str, int]] = [
            ("planting", 0),
            ("emergence", 10),
            ("tillering", 25),
            ("jointing", 45),
            ("boot", 70),
            ("heading", 85),
            ("flowering", 95),
            ("grain_fill", 110),
            ("harvest", 135),
        ]
        templates["wheat"] = wheat_template

        canola_template: List[Tuple[str, int]] = [
            ("planting", 0),
            ("emergence", 6),
            ("rosette", 18),
            ("bolting", 30),
            ("flowering", 45),
            ("pod_fill", 70),
            ("harvest", 105),
        ]
        templates["canola"] = canola_template

        return templates

    def _build_stage_nutrient_focus(self) -> Dict[str, Dict[str, str]]:
        """Define nutrient focus recommendations by crop stage."""
        focus: Dict[str, Dict[str, str]] = {}

        corn_focus: Dict[str, str] = {}
        corn_focus["planting"] = "Starter nitrogen and phosphorus to drive early vigor."
        corn_focus["v4"] = "Side-dress nitrogen to support rapid vegetative growth."
        corn_focus["v6"] = "Ensure nitrogen availability; consider sulfur if soils are deficient."
        corn_focus["vt"] = "Foliar micronutrients if tissue tests indicate deficiencies."
        corn_focus["r1"] = "Monitor soil moisture to aid nutrient uptake; avoid late heavy N."
        corn_focus["r5"] = "Focus on potassium for grain fill; minimize stress."
        focus["corn"] = corn_focus

        soybean_focus: Dict[str, str] = {}
        soybean_focus["planting"] = "Inoculate seed with Rhizobium; balanced starter if soils are cool."
        soybean_focus["v2"] = "Phosphorus and potassium to support branching and nodulation."
        soybean_focus["r1"] = "Foliar feed micronutrients if tissue tests show shortages."
        soybean_focus["r3"] = "Maintain potassium availability for pod development."
        soybean_focus["r5"] = "Protect leaves and maintain nutrient flow until pod fill completes."
        focus["soybean"] = soybean_focus

        wheat_focus: Dict[str, str] = {}
        wheat_focus["planting"] = "Phosphorus and potassium banded with seed; moderate nitrogen."
        wheat_focus["tillering"] = "Topdress nitrogen to encourage strong tiller development."
        wheat_focus["jointing"] = "Nitrogen and sulfur mix; monitor for micronutrient deficiencies."
        wheat_focus["heading"] = "Zinc and manganese foliar sprays where deficiencies occur."
        wheat_focus["grain_fill"] = "Maintain potassium and manage irrigation to protect grain quality."
        focus["wheat"] = wheat_focus

        canola_focus: Dict[str, str] = {}
        canola_focus["planting"] = "Adequate phosphorus and sulfur at seeding for root development."
        canola_focus["rosette"] = "Nitrogen split application to sustain canopy growth."
        canola_focus["flowering"] = "Boron supplementation to prevent flower abortion."
        canola_focus["pod_fill"] = "Monitor sulfur and potassium; avoid late nitrogen that delays maturity."
        focus["canola"] = canola_focus

        return focus

    def _build_extension_guidelines(self) -> Dict[str, Dict[str, List[str]]]:
        """Load extension guideline text by crop and region."""
        guidelines: Dict[str, Dict[str, List[str]]] = {}

        corn_guidelines: Dict[str, List[str]] = {}
        corn_general: List[str] = [
            "Split nitrogen applications between planting and V6 stage to reduce leaching risk.",
            "Avoid field operations when soils are wetter than field capacity to prevent compaction.",
            "Track growing degree days to fine-tune sidedress and post-emergence window.",
        ]
        corn_midwest: List[str] = [
            "University of Illinois recommends sidedress nitrogen between V4 and V6 for heavy soils.",
            "Iowa State research shows improved yield when late-season nitrogen is spoon-fed before tassel.",
        ]
        corn_great_plains: List[str] = [
            "Kansas State suggests monitoring soil moisture deficits before V10 to plan fertigation.",
            "Nebraska extension highlights sulfur supplementation on irrigated sandy soils.",
        ]
        corn_southern: List[str] = [
            "Split applications reduce losses from heavy rainfall common in humid regions.",
            "Coordinate fertilizer with irrigation sets to maximize uptake efficiency.",
        ]
        corn_guidelines["general"] = corn_general
        corn_guidelines["midwest"] = corn_midwest
        corn_guidelines["great_plains"] = corn_great_plains
        corn_guidelines["southern"] = corn_southern
        guidelines["corn"] = corn_guidelines

        soybean_guidelines: Dict[str, List[str]] = {}
        soybean_general: List[str] = [
            "Use inoculated seed when fields have not grown soybeans in the last four years.",
            "Delay in-season nitrogen applications unless nodulation is clearly failing.",
            "Tissue test around R1 to verify micronutrient sufficiency before pod set.",
        ]
        soybean_midwest: List[str] = [
            "Michigan State recommends foliar manganese on high organic matter soils showing deficiency.",
            "University of Minnesota advises potassium top-ups on coarse soils prior to R3.",
        ]
        soybean_southern: List[str] = [
            "Extension programs stress irrigation timing at R1 and R5 to reduce heat stress.",
            "Scout for foliage diseases before R3 to coordinate fungicide and nutrient passes.",
        ]
        soybean_guidelines["general"] = soybean_general
        soybean_guidelines["midwest"] = soybean_midwest
        soybean_guidelines["southern"] = soybean_southern
        guidelines["soybean"] = soybean_guidelines

        wheat_guidelines: Dict[str, List[str]] = {}
        wheat_general: List[str] = [
            "Split nitrogen between green-up and jointing for improved protein response.",
            "Maintain sulfur availability on coarse soils to support tiller retention.",
            "Flag-leaf protection is critical; align foliar nutrition with fungicide timing.",
        ]
        wheat_northern: List[str] = [
            "North Dakota State recommends delaying spring nitrogen until soils reach 40°F.",
            "Monitor for snow mold in northern zones; adjust spring fertility accordingly.",
        ]
        wheat_southern: List[str] = [
            "Oklahoma State indicates nitrogen plus chloride improves test weight in sandy soils.",
            "Avoid late nitrogen after boot to prevent lodging in high rainfall years.",
        ]
        wheat_guidelines["general"] = wheat_general
        wheat_guidelines["northern"] = wheat_northern
        wheat_guidelines["southern"] = wheat_southern
        guidelines["wheat"] = wheat_guidelines

        return guidelines

    def _build_region_state_map(self) -> Dict[str, List[str]]:
        """Define state groupings for regional guidance selection."""
        state_map: Dict[str, List[str]] = {}

        midwest_states: List[str] = [
            "IA",
            "IL",
            "IN",
            "OH",
            "MN",
            "WI",
            "MI",
            "MO",
        ]
        great_plains_states: List[str] = [
            "KS",
            "NE",
            "SD",
            "ND",
            "CO",
        ]
        southern_states: List[str] = [
            "TX",
            "LA",
            "MS",
            "AL",
            "GA",
            "FL",
            "SC",
            "NC",
            "TN",
            "AR",
        ]

        state_map["midwest"] = midwest_states
        state_map["great_plains"] = great_plains_states
        state_map["southern"] = southern_states
        return state_map

    def _build_growth_stage_timeline(
        self,
        crop_key: str,
        planting_date: date,
    ) -> Dict[str, str]:
        """Construct growth stage timeline keyed by stage name."""
        timeline: Dict[str, str] = {}
        template = self._stage_templates.get(crop_key)

        if template is None:
            timeline["planting"] = planting_date.isoformat()
            harvest_date = planting_date + timedelta(days=110)
            timeline["harvest"] = harvest_date.isoformat()
            return timeline

        index = 0
        while index < len(template):
            stage_name, offset_days = template[index]
            stage_date = planting_date + timedelta(days=offset_days)
            timeline[stage_name] = stage_date.isoformat()
            index += 1

        return timeline

    def _derive_nutrient_focus_map(self, crop_key: str) -> Dict[str, str]:
        """Retrieve nutrient focus notes for the crop."""
        focus_map = self._nutrient_focus.get(crop_key)
        if focus_map is None:
            return {}

        focus_copy: Dict[str, str] = {}
        for stage_name, description in focus_map.items():
            focus_copy[stage_name] = description

        return focus_copy

    def _collect_extension_guidelines(
        self,
        crop_key: str,
        location: LocationData,
    ) -> List[str]:
        """Gather extension guidelines relevant to the crop and region."""
        collected: List[str] = []
        crop_guidelines = self._extension_guidelines.get(crop_key)
        if crop_guidelines is None:
            return collected

        general_guidelines = crop_guidelines.get("general")
        if general_guidelines is not None:
            for guideline in general_guidelines:
                collected.append(guideline)

        region_key = self._determine_region_key(location)
        if region_key is not None:
            region_guidelines = crop_guidelines.get(region_key)
            if region_guidelines is not None:
                for item in region_guidelines:
                    collected.append(item)

        return collected

    def _determine_region_key(self, location: LocationData) -> Optional[str]:
        """Infer region key based on state or climate zone."""
        state_value = None
        if location.state:
            state_value = location.state.strip().upper()

        selected_region = None
        for region_name, state_list in self._region_states.items():
            if state_value is None:
                break
            for item in state_list:
                if item == state_value:
                    selected_region = region_name
                    break
            if selected_region is not None:
                break

        if selected_region is None and location.climate_zone:
            zone_value = location.climate_zone.strip()
            if len(zone_value) > 0:
                first_char = zone_value[0]
                if first_char in ("3", "4"):
                    selected_region = "northern"
                elif first_char in ("8", "9"):
                    selected_region = "southern"

        return selected_region

    def _assess_planting_risk(self, planting_window: PlantingWindow) -> List[str]:
        """Assess planting risk notes based on window characteristics."""
        risk_notes: List[str] = []

        if planting_window.safety_margin_days < 0:
            risk_notes.append(
                "Optimal date precedes recommended frost-free window; monitor soil temperature closely."
            )

        if planting_window.confidence_score < 0.75:
            risk_notes.append(
                "Confidence score is moderate; validate against local frost data and field history."
            )

        if planting_window.earliest_safe_date and planting_window.latest_safe_date:
            window_length = (
                planting_window.latest_safe_date - planting_window.earliest_safe_date
            ).days
            if window_length < 10:
                risk_notes.append(
                    "Safe planting window is narrow (<10 days); prepare equipment and labor resources in advance."
                )
            if window_length > 25:
                risk_notes.append(
                    "Wide planting window detected; adjust scheduling to balance labor and fertilizer utilization."
                )

        if planting_window.climate_warnings:
            for warning in planting_window.climate_warnings:
                risk_notes.append(warning)

        return risk_notes
