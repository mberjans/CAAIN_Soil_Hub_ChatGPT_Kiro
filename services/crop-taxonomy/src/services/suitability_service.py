"""Crop Suitability Matrix Service.

Implements multi-dimensional crop suitability matrices and scoring across
environmental, management, and economic dimensions with risk assessment.
"""

import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

_SRC_ROOT = Path(__file__).resolve().parents[1]
_SRC_STR = str(_SRC_ROOT)
if _SRC_STR not in sys.path:
    sys.path.insert(0, _SRC_STR)

try:
    from src.models.suitability_models import (
        SuitabilityMatrixRequest,
        SuitabilityMatrixResponse,
        SuitabilityScore,
        EnvironmentalSuitabilityMatrix,
        ManagementSuitabilityMatrix,
        EconomicSuitabilityMatrix,
        ComprehensiveSuitabilityMatrix,
        SuitabilityLevel,
        RiskLevel,
        EnvironmentalFactor,
        ManagementFactor,
        EconomicFactor
    )
    from src.models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropClimateAdaptations,
        CropSoilRequirements,
        CropAgriculturalClassification
    )
    from src.models.crop_variety_models import EnhancedCropVariety
    from src.models.service_models import ConfidenceLevel
except ImportError:
    try:
        from ..models.suitability_models import (  # type: ignore
            SuitabilityMatrixRequest,
            SuitabilityMatrixResponse,
            SuitabilityScore,
            EnvironmentalSuitabilityMatrix,
            ManagementSuitabilityMatrix,
            EconomicSuitabilityMatrix,
            ComprehensiveSuitabilityMatrix,
            SuitabilityLevel,
            RiskLevel,
            EnvironmentalFactor,
            ManagementFactor,
            EconomicFactor
        )
        from ..models.crop_taxonomy_models import (  # type: ignore
            ComprehensiveCropData,
            CropClimateAdaptations,
            CropSoilRequirements,
            CropAgriculturalClassification
        )
        from ..models.crop_variety_models import EnhancedCropVariety  # type: ignore
        from ..models.service_models import ConfidenceLevel  # type: ignore
    except ImportError:  # pragma: no cover - fallback for standalone execution
        from models.suitability_models import (  # type: ignore
            SuitabilityMatrixRequest,
            SuitabilityMatrixResponse,
            SuitabilityScore,
            EnvironmentalSuitabilityMatrix,
            ManagementSuitabilityMatrix,
            EconomicSuitabilityMatrix,
            ComprehensiveSuitabilityMatrix,
            SuitabilityLevel,
            RiskLevel,
            EnvironmentalFactor,
            ManagementFactor,
            EconomicFactor
        )
        from models.crop_taxonomy_models import (  # type: ignore
            ComprehensiveCropData,
            CropClimateAdaptations,
            CropSoilRequirements,
            CropAgriculturalClassification
        )
        from models.crop_variety_models import EnhancedCropVariety  # type: ignore
        from models.service_models import ConfidenceLevel  # type: ignore

try:
    from src.data.reference_crops import build_reference_crops_dataset
except ImportError:
    try:
        from ..data.reference_crops import build_reference_crops_dataset  # type: ignore
    except ImportError:  # pragma: no cover
        from data.reference_crops import build_reference_crops_dataset  # type: ignore

try:
    from src.services.variety_recommendation_service import VarietyRecommendationService
except ImportError:
    try:
        from .variety_recommendation_service import VarietyRecommendationService  # type: ignore
    except ImportError:  # pragma: no cover
        VarietyRecommendationService = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentalContext:
    """Normalized environmental context for scoring."""

    climate_zone: Optional[str]
    average_temperature_f: Optional[float]
    precipitation_inches: Optional[float]
    humidity_percent: Optional[float]
    wind_risk: Optional[str]
    soil_ph: Optional[float]
    soil_texture: Optional[str]
    soil_drainage: Optional[str]
    soil_fertility: Optional[str]
    soil_salinity: Optional[str]
    pest_pressure: Optional[str]
    disease_pressure: Optional[str]
    weed_pressure: Optional[str]


@dataclass
class ManagementContext:
    """Normalized management context for scoring."""

    irrigation: Optional[str]
    fertilizer_program: Optional[str]
    equipment: Optional[str]
    labor: Optional[str]
    market_access: Optional[str]
    transportation: Optional[str]
    storage: Optional[str]
    processing: Optional[str]


@dataclass
class EconomicContext:
    """Normalized economic context for scoring."""

    seed_cost_index: Optional[float]
    input_cost_index: Optional[float]
    labor_cost_index: Optional[float]
    market_price_index: Optional[float]
    transportation_cost_index: Optional[float]
    storage_cost_index: Optional[float]
    processing_cost_index: Optional[float]
    profit_margin_index: Optional[float]


class CropSuitabilityMatrixService:
    """Service that generates comprehensive crop suitability matrices."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url
        self.precomputed_matrices: Dict[str, ComprehensiveSuitabilityMatrix] = {}
        self.precomputed_metadata: Dict[str, Dict[str, Any]] = {}
        self.reference_crops: List[ComprehensiveCropData] = []
        self.variety_service: Optional[VarietyRecommendationService] = None
        self.database_available = False
        self.environmental_weights = {
            EnvironmentalFactor.CLIMATE_TEMPERATURE: 0.18,
            EnvironmentalFactor.CLIMATE_PRECIPITATION: 0.14,
            EnvironmentalFactor.CLIMATE_HUMIDITY: 0.08,
            EnvironmentalFactor.CLIMATE_WIND: 0.05,
            EnvironmentalFactor.SOIL_PH: 0.18,
            EnvironmentalFactor.SOIL_TEXTURE: 0.12,
            EnvironmentalFactor.SOIL_DRAINAGE: 0.09,
            EnvironmentalFactor.SOIL_FERTILITY: 0.08,
            EnvironmentalFactor.SOIL_SALINITY: 0.04,
            EnvironmentalFactor.PEST_PRESSURE: 0.02,
            EnvironmentalFactor.DISEASE_PRESSURE: 0.01,
            EnvironmentalFactor.WEED_PRESSURE: 0.01
        }
        self.management_weights = {
            ManagementFactor.IRRIGATION_AVAILABILITY: 0.2,
            ManagementFactor.FERTILIZER_ACCESS: 0.15,
            ManagementFactor.EQUIPMENT_AVAILABILITY: 0.15,
            ManagementFactor.LABOR_AVAILABILITY: 0.1,
            ManagementFactor.MARKET_ACCESS: 0.15,
            ManagementFactor.TRANSPORTATION: 0.1,
            ManagementFactor.STORAGE_FACILITIES: 0.075,
            ManagementFactor.PROCESSING_FACILITIES: 0.075
        }
        self.economic_weights = {
            EconomicFactor.SEED_COST: 0.12,
            EconomicFactor.INPUT_COSTS: 0.12,
            EconomicFactor.LABOR_COSTS: 0.12,
            EconomicFactor.MARKET_PRICE: 0.18,
            EconomicFactor.TRANSPORTATION_COSTS: 0.08,
            EconomicFactor.STORAGE_COSTS: 0.08,
            EconomicFactor.PROCESSING_COSTS: 0.1,
            EconomicFactor.PROFIT_MARGIN: 0.2
        }

        self._initialize_database()
        self._initialize_reference_data()
        self._initialize_variety_service()
        self._precompute_reference_matrices()

    def _initialize_database(self) -> None:
        """Initialize database connection if available."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(self.database_url)
            self.database_available = self.db.test_connection()
            if self.database_available:
                logger.info("CropSuitabilityMatrixService connected to database")
            else:
                logger.warning("CropSuitabilityMatrixService database unavailable; using reference data")
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("Database integration unavailable for suitability service: %s", exc)
            self.db = None
            self.database_available = False

    def _initialize_reference_data(self) -> None:
        """Load reference crop dataset for fallback computations."""
        try:
            dataset = build_reference_crops_dataset()
            index = 0
            for crop in dataset:
                if index >= 25:
                    break
                self.reference_crops.append(crop)
                index += 1
        except Exception as exc:  # pragma: no cover - dataset should exist
            logger.error("Unable to load reference crop dataset: %s", exc)
            self.reference_crops = []

    def _initialize_variety_service(self) -> None:
        """Instantiate variety recommendation service for variety lookups."""
        if 'VarietyRecommendationService' not in globals() or VarietyRecommendationService is None:  # type: ignore[name-defined]
            self.variety_service = None
            return
        try:
            self.variety_service = VarietyRecommendationService(self.database_url)  # type: ignore[call-arg]
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("Variety recommendation service unavailable: %s", exc)
            self.variety_service = None

    def _precompute_reference_matrices(self) -> None:
        """Pre-compute suitability matrices for common reference scenarios."""
        if not self.reference_crops:
            return

        count = 0
        for crop in self.reference_crops:
            if count >= 10:
                break
            default_request = self._build_default_request_for_crop(crop)
            if default_request is None:
                continue
            matrix = self._build_comprehensive_matrix(
                crop,
                None,
                default_request,
                ConfidenceLevel.HIGH
            )
            cache_key = self._build_cache_key(crop.crop_id, default_request)
            self.precomputed_matrices[cache_key] = matrix
            meta: Dict[str, Any] = {}
            meta['source'] = 'precomputed_reference'
            meta['generated_at'] = datetime.utcnow()
            meta['confidence'] = matrix.confidence_score
            self.precomputed_metadata[cache_key] = meta
            count += 1

    async def generate_suitability_matrices(
        self,
        request: SuitabilityMatrixRequest
    ) -> SuitabilityMatrixResponse:
        """Generate suitability matrices for the provided request."""

        start_time = time.perf_counter()
        matrices: List[ComprehensiveSuitabilityMatrix] = []
        data_sources: List[str] = []
        confidence_summary: Dict[str, float] = {}
        evaluated_crops = 0

        crop_data = self._resolve_crop_data(request)
        if crop_data is None:
            message = "Requested crop not found for suitability analysis"
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return SuitabilityMatrixResponse(
                request_id=self._resolve_request_id(request),
                matrices=[],
                total_crops_evaluated=0,
                top_suitable_crops=[],
                processing_time_ms=elapsed,
                data_sources_used=["reference_dataset"],
                confidence_summary={},
                overall_recommendations=[message],
                risk_warnings=[message]
            )

        variety_data = self._resolve_variety_data(request, crop_data)

        cache_key = self._lookup_cache_key(crop_data, request)
        if cache_key in self.precomputed_matrices:
            matrix = self.precomputed_matrices[cache_key]
            matrices.append(matrix)
            evaluated_crops = 1
            data_sources.append("precomputed_reference")
            confidence_summary['environmental'] = matrix.environmental_matrix.overall_environmental_score
            confidence_summary['management'] = matrix.management_matrix.overall_management_score
            confidence_summary['economic'] = matrix.economic_matrix.overall_economic_score
        else:
            matrix = self._build_comprehensive_matrix(
                crop_data,
                variety_data,
                request,
                ConfidenceLevel.MEDIUM
            )
            matrices.append(matrix)
            evaluated_crops = 1
            data_sources.append("real_time_context")
            self.precomputed_matrices[cache_key] = matrix
            metadata: Dict[str, Any] = {}
            metadata['source'] = 'dynamic'
            metadata['generated_at'] = datetime.utcnow()
            metadata['confidence'] = matrix.confidence_score
            self.precomputed_metadata[cache_key] = metadata
            confidence_summary['environmental'] = matrix.environmental_matrix.overall_environmental_score
            confidence_summary['management'] = matrix.management_matrix.overall_management_score
            confidence_summary['economic'] = matrix.economic_matrix.overall_economic_score

        top_suitable_crops: List[Dict[str, Any]] = []
        index = 0
        for matrix_entry in matrices:
            crop_summary: Dict[str, Any] = {}
            crop_summary['crop_id'] = str(matrix_entry.crop_id)
            crop_summary['crop_name'] = matrix_entry.crop_name
            crop_summary['overall_score'] = matrix_entry.overall_suitability_score
            crop_summary['suitability_level'] = matrix_entry.overall_suitability_level.value
            crop_summary['risk_level'] = matrix_entry.risk_level.value
            top_suitable_crops.append(crop_summary)
            index += 1

        elapsed = (time.perf_counter() - start_time) * 1000.0

        recommendations = self._summarize_recommendations(matrices[0])
        warnings = self._summarize_warnings(matrices[0])

        return SuitabilityMatrixResponse(
            request_id=self._resolve_request_id(request),
            matrices=matrices,
            total_crops_evaluated=evaluated_crops,
            top_suitable_crops=top_suitable_crops,
            processing_time_ms=elapsed,
            data_sources_used=data_sources,
            confidence_summary=confidence_summary,
            overall_recommendations=recommendations,
            risk_warnings=warnings
        )

    def _resolve_request_id(self, request: SuitabilityMatrixRequest) -> str:
        if request.crop_id is not None:
            return f"suitability-{str(request.crop_id)}"
        if request.crop_name:
            return f"suitability-{request.crop_name.lower()}"
        return "suitability-default"

    def _lookup_cache_key(
        self,
        crop_data: ComprehensiveCropData,
        request: SuitabilityMatrixRequest
    ) -> str:
        return self._build_cache_key(crop_data.crop_id, request)

    def _build_cache_key(
        self,
        crop_id: Optional[UUID],
        request: SuitabilityMatrixRequest
    ) -> str:
        parts: List[str] = []
        if crop_id is not None:
            parts.append(str(crop_id))
        elif request.crop_name:
            parts.append(request.crop_name.lower())
        else:
            parts.append("unknown_crop")
        zone = request.climate_zone or "unknown"
        parts.append(zone)
        soil = "unknown_soil"
        if request.soil_conditions and 'texture' in request.soil_conditions:
            soil = str(request.soil_conditions['texture']).lower()
        parts.append(soil)
        management = "management_default"
        if request.management_capabilities and 'management_profile' in request.management_capabilities:
            management = str(request.management_capabilities['management_profile']).lower()
        parts.append(management)
        return "::".join(parts)

    def _resolve_crop_data(self, request: SuitabilityMatrixRequest) -> Optional[ComprehensiveCropData]:
        if request.crop_id and self.database_available:
            try:
                crop_record = self.db.get_crop_by_id(request.crop_id)
                if crop_record:
                    return self._convert_db_record(crop_record)
            except Exception as exc:
                logger.error("Database crop lookup failed: %s", exc)

        if request.crop_name:
            target_name = request.crop_name.lower()
            for crop in self.reference_crops:
                if crop.crop_name.lower() == target_name:
                    return crop
                if crop.search_keywords:
                    for keyword in crop.search_keywords:
                        if keyword.lower() == target_name:
                            return crop

        if self.reference_crops:
            return self.reference_crops[0]
        return None

    def _resolve_variety_data(
        self,
        request: SuitabilityMatrixRequest,
        crop_data: ComprehensiveCropData
    ) -> Optional[EnhancedCropVariety]:
        _ = request
        _ = crop_data
        return None

    def _build_comprehensive_matrix(
        self,
        crop_data: ComprehensiveCropData,
        variety_data: Optional[EnhancedCropVariety],
        request: SuitabilityMatrixRequest,
        confidence_level: ConfidenceLevel
    ) -> ComprehensiveSuitabilityMatrix:
        environmental_context = self._build_environmental_context(crop_data, request)
        management_context = self._build_management_context(request)
        economic_context = self._build_economic_context(request)

        resolved_crop_id = crop_data.crop_id if crop_data.crop_id is not None else uuid4()

        environmental_matrix = self._build_environmental_matrix(crop_data, environmental_context, resolved_crop_id)
        management_matrix = self._build_management_matrix(crop_data, management_context, resolved_crop_id)
        economic_matrix = self._build_economic_matrix(crop_data, economic_context, resolved_crop_id)

        overall_score = self._combine_overall_score(
            environmental_matrix.overall_environmental_score,
            management_matrix.overall_management_score,
            economic_matrix.overall_economic_score,
            request
        )

        suitability_level = self._score_to_level(overall_score)
        risk_level, risk_factors = self._derive_risk_level(environmental_matrix, management_matrix, economic_matrix)
        mitigation_strategies = self._derive_mitigation_strategies(risk_factors)

        confidence_score = self._map_confidence_level(confidence_level)
        data_completeness = self._estimate_data_completeness(environmental_context, management_context, economic_context)
        recommendations = self._build_recommendations(suitability_level, risk_level, crop_data, environmental_context)

        matrix = ComprehensiveSuitabilityMatrix(
            crop_id=resolved_crop_id,
            crop_name=crop_data.crop_name,
            variety_id=variety_data.variety_id if variety_data else None,
            variety_name=variety_data.variety_name if variety_data else None,
            environmental_matrix=environmental_matrix,
            management_matrix=management_matrix,
            economic_matrix=economic_matrix,
            overall_suitability_score=overall_score,
            overall_suitability_level=suitability_level,
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            confidence_score=confidence_score,
            data_completeness=data_completeness,
            last_updated=datetime.utcnow(),
            recommendations=recommendations,
            adaptation_strategies=mitigation_strategies
        )
        return matrix

    def _build_environmental_context(
        self,
        crop_data: ComprehensiveCropData,
        request: SuitabilityMatrixRequest
    ) -> EnvironmentalContext:
        climate_zone = request.climate_zone
        average_temp = None
        precipitation = None
        humidity = None
        wind_risk = None
        ph_value = None
        texture = None
        drainage = None
        fertility = None
        salinity = None
        pest = None
        disease = None
        weed = None

        if request.weather_patterns:
            if 'average_temp_f' in request.weather_patterns:
                average_temp = float(request.weather_patterns['average_temp_f'])
            if 'annual_precip_inches' in request.weather_patterns:
                precipitation = float(request.weather_patterns['annual_precip_inches'])
            if 'average_humidity_percent' in request.weather_patterns:
                humidity = float(request.weather_patterns['average_humidity_percent'])
            if 'wind_risk' in request.weather_patterns:
                wind_risk = str(request.weather_patterns['wind_risk']).lower()

        if request.soil_conditions:
            if 'ph' in request.soil_conditions:
                ph_value = float(request.soil_conditions['ph'])
            if 'texture' in request.soil_conditions:
                texture = str(request.soil_conditions['texture']).lower()
            if 'drainage_class' in request.soil_conditions:
                drainage = str(request.soil_conditions['drainage_class']).lower()
            if 'fertility' in request.soil_conditions:
                fertility = str(request.soil_conditions['fertility']).lower()
            if 'salinity' in request.soil_conditions:
                salinity = str(request.soil_conditions['salinity']).lower()

        if request.pest_pressure:
            if 'pest' in request.pest_pressure:
                pest = str(request.pest_pressure['pest']).lower()
            if 'disease' in request.pest_pressure:
                disease = str(request.pest_pressure['disease']).lower()
            if 'weed' in request.pest_pressure:
                weed = str(request.pest_pressure['weed']).lower()

        if climate_zone is None and crop_data.climate_adaptations:
            zones = crop_data.climate_adaptations.hardiness_zones
            if zones:
                climate_zone = zones[0]
        if average_temp is None and crop_data.climate_adaptations:
            climate: CropClimateAdaptations = crop_data.climate_adaptations
            min_temp = climate.optimal_temp_min_f
            max_temp = climate.optimal_temp_max_f
            average_temp = (min_temp + max_temp) / 2.0
        if precipitation is None:
            precipitation = 30.0
        if humidity is None:
            humidity = 65.0
        if wind_risk is None:
            wind_risk = "moderate"

        soil_requirements: Optional[CropSoilRequirements] = crop_data.soil_requirements
        if soil_requirements is not None:
            if ph_value is None and soil_requirements.optimal_ph_min is not None and soil_requirements.optimal_ph_max is not None:
                ph_value = (soil_requirements.optimal_ph_min + soil_requirements.optimal_ph_max) / 2.0
            if texture is None and soil_requirements.preferred_textures:
                texture = str(soil_requirements.preferred_textures[0]).lower()
            if drainage is None and soil_requirements.drainage_requirement is not None:
                drainage_value = soil_requirements.drainage_requirement
                drainage = str(drainage_value.value).lower() if hasattr(drainage_value, 'value') else str(drainage_value).lower()
            if fertility is None:
                fertility = "moderate"
            if salinity is None and soil_requirements.salinity_tolerance:
                salinity = str(soil_requirements.salinity_tolerance.value).lower() if hasattr(soil_requirements.salinity_tolerance, 'value') else str(soil_requirements.salinity_tolerance).lower()

        context = EnvironmentalContext(
            climate_zone=climate_zone,
            average_temperature_f=average_temp,
            precipitation_inches=precipitation,
            humidity_percent=humidity,
            wind_risk=wind_risk,
            soil_ph=ph_value,
            soil_texture=texture,
            soil_drainage=drainage,
            soil_fertility=fertility,
            soil_salinity=salinity,
            pest_pressure=pest,
            disease_pressure=disease,
            weed_pressure=weed
        )
        return context

    def _build_management_context(self, request: SuitabilityMatrixRequest) -> ManagementContext:
        irrigation = None
        fertilizer = None
        equipment = None
        labor = None
        market = None
        transport = None
        storage = None
        processing = None

        if request.management_capabilities:
            if 'irrigation' in request.management_capabilities:
                irrigation = str(request.management_capabilities['irrigation']).lower()
            if 'fertility_program' in request.management_capabilities:
                fertilizer = str(request.management_capabilities['fertility_program']).lower()
            if 'equipment' in request.management_capabilities:
                equipment = str(request.management_capabilities['equipment']).lower()
            if 'labor' in request.management_capabilities:
                labor = str(request.management_capabilities['labor']).lower()
            if 'market_access' in request.management_capabilities:
                market = str(request.management_capabilities['market_access']).lower()
            if 'transportation' in request.management_capabilities:
                transport = str(request.management_capabilities['transportation']).lower()
            if 'storage' in request.management_capabilities:
                storage = str(request.management_capabilities['storage']).lower()
            if 'processing' in request.management_capabilities:
                processing = str(request.management_capabilities['processing']).lower()

        if irrigation is None:
            irrigation = "available"
        if fertilizer is None:
            fertilizer = "standard"
        if equipment is None:
            equipment = "moderate"
        if labor is None:
            labor = "sufficient"
        if market is None:
            market = "regional"
        if transport is None:
            transport = "average"
        if storage is None:
            storage = "basic"
        if processing is None:
            processing = "limited"

        context = ManagementContext(
            irrigation=irrigation,
            fertilizer_program=fertilizer,
            equipment=equipment,
            labor=labor,
            market_access=market,
            transportation=transport,
            storage=storage,
            processing=processing
        )
        return context

    def _build_economic_context(self, request: SuitabilityMatrixRequest) -> EconomicContext:
        seed_cost = None
        input_cost = None
        labor_cost = None
        market_price = None
        transport_cost = None
        storage_cost = None
        processing_cost = None
        profit_margin = None

        if request.cost_structure:
            if 'seed_cost_index' in request.cost_structure:
                seed_cost = float(request.cost_structure['seed_cost_index'])
            if 'input_cost_index' in request.cost_structure:
                input_cost = float(request.cost_structure['input_cost_index'])
            if 'labor_cost_index' in request.cost_structure:
                labor_cost = float(request.cost_structure['labor_cost_index'])
            if 'transport_cost_index' in request.cost_structure:
                transport_cost = float(request.cost_structure['transport_cost_index'])
            if 'storage_cost_index' in request.cost_structure:
                storage_cost = float(request.cost_structure['storage_cost_index'])
            if 'processing_cost_index' in request.cost_structure:
                processing_cost = float(request.cost_structure['processing_cost_index'])

        if request.market_conditions:
            if 'market_price_index' in request.market_conditions:
                market_price = float(request.market_conditions['market_price_index'])
            if 'profit_margin_index' in request.market_conditions:
                profit_margin = float(request.market_conditions['profit_margin_index'])

        if seed_cost is None:
            seed_cost = 1.0
        if input_cost is None:
            input_cost = 1.0
        if labor_cost is None:
            labor_cost = 1.0
        if market_price is None:
            market_price = 1.0
        if transport_cost is None:
            transport_cost = 1.0
        if storage_cost is None:
            storage_cost = 1.0
        if processing_cost is None:
            processing_cost = 1.0
        if profit_margin is None:
            profit_margin = 1.0

        context = EconomicContext(
            seed_cost_index=seed_cost,
            input_cost_index=input_cost,
            labor_cost_index=labor_cost,
            market_price_index=market_price,
            transportation_cost_index=transport_cost,
            storage_cost_index=storage_cost,
            processing_cost_index=processing_cost,
            profit_margin_index=profit_margin
        )
        return context

    def _build_environmental_matrix(
        self,
        crop_data: ComprehensiveCropData,
        context: EnvironmentalContext,
        resolved_crop_id: UUID
    ) -> EnvironmentalSuitabilityMatrix:
        scores: Dict[EnvironmentalFactor, SuitabilityScore] = {}
        scores[EnvironmentalFactor.CLIMATE_TEMPERATURE] = self._score_temperature(crop_data, context)
        scores[EnvironmentalFactor.CLIMATE_PRECIPITATION] = self._score_precipitation(crop_data, context)
        scores[EnvironmentalFactor.CLIMATE_HUMIDITY] = self._score_humidity(context)
        scores[EnvironmentalFactor.CLIMATE_WIND] = self._score_wind(context)
        scores[EnvironmentalFactor.SOIL_PH] = self._score_soil_ph(crop_data, context)
        scores[EnvironmentalFactor.SOIL_TEXTURE] = self._score_soil_texture(crop_data, context)
        scores[EnvironmentalFactor.SOIL_DRAINAGE] = self._score_soil_drainage(crop_data, context)
        scores[EnvironmentalFactor.SOIL_FERTILITY] = self._score_soil_fertility(context)
        scores[EnvironmentalFactor.SOIL_SALINITY] = self._score_soil_salinity(crop_data, context)
        scores[EnvironmentalFactor.PEST_PRESSURE] = self._score_pest_pressure(context)
        scores[EnvironmentalFactor.DISEASE_PRESSURE] = self._score_disease_pressure(context)
        scores[EnvironmentalFactor.WEED_PRESSURE] = self._score_weed_pressure(context)

        total_weight = 0.0
        weighted_sum = 0.0
        for factor, score in scores.items():
            weight = self.environmental_weights.get(factor, 0.0)
            total_weight += weight
            weighted_sum += score.score * weight

        overall = 0.0
        if total_weight > 0.0:
            overall = weighted_sum / total_weight
        level = self._score_to_level(overall)

        matrix = EnvironmentalSuitabilityMatrix(
            crop_id=resolved_crop_id,
            crop_name=crop_data.crop_name,
            temperature_suitability=scores[EnvironmentalFactor.CLIMATE_TEMPERATURE],
            precipitation_suitability=scores[EnvironmentalFactor.CLIMATE_PRECIPITATION],
            humidity_suitability=scores[EnvironmentalFactor.CLIMATE_HUMIDITY],
            wind_suitability=scores[EnvironmentalFactor.CLIMATE_WIND],
            ph_suitability=scores[EnvironmentalFactor.SOIL_PH],
            texture_suitability=scores[EnvironmentalFactor.SOIL_TEXTURE],
            drainage_suitability=scores[EnvironmentalFactor.SOIL_DRAINAGE],
            fertility_suitability=scores[EnvironmentalFactor.SOIL_FERTILITY],
            salinity_suitability=scores[EnvironmentalFactor.SOIL_SALINITY],
            pest_pressure_suitability=scores[EnvironmentalFactor.PEST_PRESSURE],
            disease_pressure_suitability=scores[EnvironmentalFactor.DISEASE_PRESSURE],
            weed_pressure_suitability=scores[EnvironmentalFactor.WEED_PRESSURE],
            overall_environmental_score=overall,
            environmental_level=level
        )
        return matrix

    def _build_management_matrix(
        self,
        crop_data: ComprehensiveCropData,
        context: ManagementContext,
        resolved_crop_id: UUID
    ) -> ManagementSuitabilityMatrix:
        scores: Dict[ManagementFactor, SuitabilityScore] = {}
        scores[ManagementFactor.IRRIGATION_AVAILABILITY] = self._score_irrigation(context)
        scores[ManagementFactor.FERTILIZER_ACCESS] = self._score_fertilizer_access(context)
        scores[ManagementFactor.EQUIPMENT_AVAILABILITY] = self._score_equipment(context)
        scores[ManagementFactor.LABOR_AVAILABILITY] = self._score_labor(context)
        scores[ManagementFactor.MARKET_ACCESS] = self._score_market_access(context)
        scores[ManagementFactor.TRANSPORTATION] = self._score_transportation(context)
        scores[ManagementFactor.STORAGE_FACILITIES] = self._score_storage(context)
        scores[ManagementFactor.PROCESSING_FACILITIES] = self._score_processing(context)

        total_weight = 0.0
        weighted_sum = 0.0
        for factor, score in scores.items():
            weight = self.management_weights.get(factor, 0.0)
            total_weight += weight
            weighted_sum += score.score * weight

        overall = 0.0
        if total_weight > 0.0:
            overall = weighted_sum / total_weight
        level = self._score_to_level(overall)

        matrix = ManagementSuitabilityMatrix(
            crop_id=resolved_crop_id,
            crop_name=crop_data.crop_name,
            irrigation_suitability=scores[ManagementFactor.IRRIGATION_AVAILABILITY],
            fertilizer_suitability=scores[ManagementFactor.FERTILIZER_ACCESS],
            equipment_suitability=scores[ManagementFactor.EQUIPMENT_AVAILABILITY],
            labor_suitability=scores[ManagementFactor.LABOR_AVAILABILITY],
            market_access_suitability=scores[ManagementFactor.MARKET_ACCESS],
            transportation_suitability=scores[ManagementFactor.TRANSPORTATION],
            storage_suitability=scores[ManagementFactor.STORAGE_FACILITIES],
            processing_suitability=scores[ManagementFactor.PROCESSING_FACILITIES],
            overall_management_score=overall,
            management_level=level
        )
        return matrix

    def _build_economic_matrix(
        self,
        crop_data: ComprehensiveCropData,
        context: EconomicContext,
        resolved_crop_id: UUID
    ) -> EconomicSuitabilityMatrix:
        scores: Dict[EconomicFactor, SuitabilityScore] = {}
        scores[EconomicFactor.SEED_COST] = self._score_seed_cost(context)
        scores[EconomicFactor.INPUT_COSTS] = self._score_input_cost(context)
        scores[EconomicFactor.LABOR_COSTS] = self._score_labor_cost(context)
        scores[EconomicFactor.MARKET_PRICE] = self._score_market_price(context)
        scores[EconomicFactor.TRANSPORTATION_COSTS] = self._score_transport_cost(context)
        scores[EconomicFactor.STORAGE_COSTS] = self._score_storage_cost(context)
        scores[EconomicFactor.PROCESSING_COSTS] = self._score_processing_cost(context)
        scores[EconomicFactor.PROFIT_MARGIN] = self._score_profit_margin(context)

        total_weight = 0.0
        weighted_sum = 0.0
        for factor, score in scores.items():
            weight = self.economic_weights.get(factor, 0.0)
            total_weight += weight
            weighted_sum += score.score * weight

        overall = 0.0
        if total_weight > 0.0:
            overall = weighted_sum / total_weight
        level = self._score_to_level(overall)

        matrix = EconomicSuitabilityMatrix(
            crop_id=resolved_crop_id,
            crop_name=crop_data.crop_name,
            seed_cost_suitability=scores[EconomicFactor.SEED_COST],
            input_cost_suitability=scores[EconomicFactor.INPUT_COSTS],
            labor_cost_suitability=scores[EconomicFactor.LABOR_COSTS],
            transportation_cost_suitability=scores[EconomicFactor.TRANSPORTATION_COSTS],
            storage_cost_suitability=scores[EconomicFactor.STORAGE_COSTS],
            processing_cost_suitability=scores[EconomicFactor.PROCESSING_COSTS],
            market_price_suitability=scores[EconomicFactor.MARKET_PRICE],
            profit_margin_suitability=scores[EconomicFactor.PROFIT_MARGIN],
            overall_economic_score=overall,
            economic_level=level
        )
        return matrix

    def _combine_overall_score(
        self,
        environmental_score: float,
        management_score: float,
        economic_score: float,
        request: SuitabilityMatrixRequest
    ) -> float:
        env_weight = request.environmental_weight if request.include_environmental else 0.0
        man_weight = request.management_weight if request.include_management else 0.0
        eco_weight = request.economic_weight if request.include_economic else 0.0
        total_weight = env_weight + man_weight + eco_weight
        if total_weight == 0.0:
            env_weight = 0.34
            man_weight = 0.33
            eco_weight = 0.33
            total_weight = env_weight + man_weight + eco_weight
        weighted_sum = (environmental_score * env_weight) + (management_score * man_weight) + (economic_score * eco_weight)
        return weighted_sum / total_weight

    def _derive_risk_level(
        self,
        environmental_matrix: EnvironmentalSuitabilityMatrix,
        management_matrix: ManagementSuitabilityMatrix,
        economic_matrix: EconomicSuitabilityMatrix
    ) -> Tuple[RiskLevel, List[str]]:
        limiting_factors: List[str] = []
        lowest_score = 1.0
        lowest_component = "environmental"

        if environmental_matrix.overall_environmental_score < lowest_score:
            lowest_score = environmental_matrix.overall_environmental_score
            lowest_component = "environmental"
        if management_matrix.overall_management_score < lowest_score:
            lowest_score = management_matrix.overall_management_score
            lowest_component = "management"
        if economic_matrix.overall_economic_score < lowest_score:
            lowest_score = economic_matrix.overall_economic_score
            lowest_component = "economic"

        matrix_map = {
            "environmental": environmental_matrix,
            "management": management_matrix,
            "economic": economic_matrix
        }
        limiting_matrix = matrix_map[lowest_component]

        for attr_name in limiting_matrix.__fields__.keys():
            if attr_name.endswith("suitability"):
                score_obj = getattr(limiting_matrix, attr_name)
                if isinstance(score_obj, SuitabilityScore):
                    if score_obj.score <= 0.55:
                        factor_name = score_obj.factor.value.replace("_", " ")
                        limiting_factors.append(factor_name)

        risk_level = RiskLevel.VERY_LOW
        if lowest_score <= 0.4:
            risk_level = RiskLevel.VERY_HIGH
        elif lowest_score <= 0.55:
            risk_level = RiskLevel.HIGH
        elif lowest_score <= 0.7:
            risk_level = RiskLevel.MODERATE
        elif lowest_score <= 0.85:
            risk_level = RiskLevel.LOW

        return risk_level, limiting_factors

    def _derive_mitigation_strategies(self, limiting_factors: List[str]) -> List[str]:
        strategies: List[str] = []
        for factor in limiting_factors:
            text = f"Develop mitigation plan for {factor}"
            strategies.append(text)
        if not strategies:
            strategies.append("Maintain current best management practices")
        return strategies

    def _map_confidence_level(self, confidence_level: ConfidenceLevel) -> float:
        mapping = {
            ConfidenceLevel.VERY_HIGH: 0.95,
            ConfidenceLevel.HIGH: 0.85,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.5
        }
        return mapping.get(confidence_level, 0.6)

    def _estimate_data_completeness(
        self,
        environmental_context: EnvironmentalContext,
        management_context: ManagementContext,
        economic_context: EconomicContext
    ) -> float:
        filled_fields = 0
        total_fields = 0

        for value in environmental_context.__dict__.values():
            total_fields += 1
            if value is not None:
                filled_fields += 1
        for value in management_context.__dict__.values():
            total_fields += 1
            if value is not None:
                filled_fields += 1
        for value in economic_context.__dict__.values():
            total_fields += 1
            if value is not None:
                filled_fields += 1

        if total_fields == 0:
            return 0.0
        return filled_fields / float(total_fields)

    def _build_recommendations(
        self,
        suitability_level: SuitabilityLevel,
        risk_level: RiskLevel,
        crop_data: ComprehensiveCropData,
        context: EnvironmentalContext
    ) -> List[str]:
        recommendations: List[str] = []
        if suitability_level in (SuitabilityLevel.EXCELLENT, SuitabilityLevel.GOOD):
            recommendations.append(f"{crop_data.crop_name} is suitable for the provided conditions")
        elif suitability_level == SuitabilityLevel.MODERATE:
            recommendations.append(f"{crop_data.crop_name} can be grown with targeted risk mitigation")
        else:
            recommendations.append(f"Consider alternative crops or aggressive mitigation before planting {crop_data.crop_name}")

        if context.soil_ph is not None:
            if context.soil_ph < 5.8:
                recommendations.append("Adjust soil pH with lime applications")
            elif context.soil_ph > 7.2:
                recommendations.append("Consider sulfur amendments to reduce soil pH")

        if risk_level in (RiskLevel.HIGH, RiskLevel.VERY_HIGH):
            recommendations.append("Implement intensive scouting and adaptive management plans")
        elif risk_level == RiskLevel.MODERATE:
            recommendations.append("Monitor limiting factors and adjust inputs accordingly")

        return recommendations

    def _summarize_recommendations(self, matrix: ComprehensiveSuitabilityMatrix) -> List[str]:
        recommendations: List[str] = []
        for item in matrix.recommendations:
            recommendations.append(item)
        return recommendations

    def _summarize_warnings(self, matrix: ComprehensiveSuitabilityMatrix) -> List[str]:
        warnings: List[str] = []
        for factor in matrix.risk_factors:
            warning = f"Elevated risk: {factor}"
            warnings.append(warning)
        if not warnings:
            warnings.append("No significant suitability risks detected")
        return warnings

    def _build_default_request_for_crop(self, crop: ComprehensiveCropData) -> Optional[SuitabilityMatrixRequest]:
        if crop.climate_adaptations is None:
            return None

        soil_ph = 6.5
        texture = "loam"
        drainage = "well_drained"
        if crop.soil_requirements:
            soil = crop.soil_requirements
            if soil.optimal_ph_min is not None and soil.optimal_ph_max is not None:
                soil_ph = (soil.optimal_ph_min + soil.optimal_ph_max) / 2.0
            if soil.preferred_textures:
                texture = str(soil.preferred_textures[0]).lower()
            if soil.drainage_requirement is not None:
                drainage_value = soil.drainage_requirement
                drainage = str(drainage_value.value).lower() if hasattr(drainage_value, 'value') else str(drainage_value).lower()

        climate_zone = None
        if crop.climate_adaptations.hardiness_zones:
            climate_zone = crop.climate_adaptations.hardiness_zones[0]

        soil_conditions = {
            'ph': soil_ph,
            'texture': texture,
            'drainage_class': drainage,
            'fertility': 'moderate'
        }
        weather_patterns = {
            'average_temp_f': (crop.climate_adaptations.optimal_temp_min_f + crop.climate_adaptations.optimal_temp_max_f) / 2.0,
            'annual_precip_inches': 32.0,
            'average_humidity_percent': 65.0,
            'wind_risk': 'moderate'
        }
        management_capabilities = {
            'irrigation': 'available',
            'fertility_program': 'standard',
            'equipment': 'modern',
            'labor': 'sufficient',
            'market_access': 'regional'
        }
        market_conditions = {
            'market_price_index': 1.0,
            'profit_margin_index': 1.0
        }
        cost_structure = {
            'seed_cost_index': 1.0,
            'input_cost_index': 1.0,
            'labor_cost_index': 1.0
        }

        request = SuitabilityMatrixRequest(
            crop_id=crop.crop_id,
            climate_zone=climate_zone,
            soil_conditions=soil_conditions,
            weather_patterns=weather_patterns,
            management_capabilities=management_capabilities,
            market_conditions=market_conditions,
            cost_structure=cost_structure
        )
        return request

    def _convert_db_record(self, record: Dict[str, Any]) -> ComprehensiveCropData:
        service = None
        try:
            from .crop_taxonomy_service import CropTaxonomyService
            service = CropTaxonomyService(self.database_url)
        except Exception as exc:
            logger.error("Failed to initialize taxonomy service for conversion: %s", exc)
        if service and hasattr(service, '_convert_db_to_comprehensive_crop_data'):
            return service._convert_db_to_comprehensive_crop_data(record)  # type: ignore
        raise ValueError("Database record conversion unavailable without taxonomy service")

    # ---------------------------------------------------------------------
    # Scoring helpers
    # ---------------------------------------------------------------------

    def _score_temperature(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.5
        explanation = "Temperature data partially available"
        weight = self.environmental_weights.get(EnvironmentalFactor.CLIMATE_TEMPERATURE, 0.1)
        confidence = 0.6
        if crop_data.climate_adaptations and context.average_temperature_f is not None:
            climate = crop_data.climate_adaptations
            optimal_min = climate.optimal_temp_min_f
            optimal_max = climate.optimal_temp_max_f
            temp = context.average_temperature_f
            if optimal_min <= temp <= optimal_max:
                score = 0.95
                explanation = "Temperature within optimal range"
            else:
                distance = 0.0
                if temp < optimal_min:
                    distance = optimal_min - temp
                else:
                    distance = temp - optimal_max
                penalty = min(distance / 30.0, 1.0)
                score = max(0.2, 1.0 - penalty)
                explanation = "Temperature slightly outside optimal range"
            confidence = 0.85
        return SuitabilityScore(
            factor=EnvironmentalFactor.CLIMATE_TEMPERATURE,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=weight,
            explanation=explanation,
            data_sources=["crop_climate_reference"]
        )

    def _score_precipitation(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.6
        explanation = "Precipitation data limited"
        weight = self.environmental_weights.get(EnvironmentalFactor.CLIMATE_PRECIPITATION, 0.1)
        confidence = 0.55
        if context.precipitation_inches is not None:
            precip = context.precipitation_inches
            optimal_range = self._derive_optimal_precipitation_range(crop_data)
            min_val, max_val = optimal_range
            if min_val <= precip <= max_val:
                score = 0.9
                explanation = "Precipitation within optimal range"
            else:
                distance = 0.0
                if precip < min_val:
                    distance = min_val - precip
                else:
                    distance = precip - max_val
                penalty = min(distance / 20.0, 1.0)
                score = max(0.2, 1.0 - penalty)
                explanation = "Precipitation outside optimal range"
            confidence = 0.75
        return SuitabilityScore(
            factor=EnvironmentalFactor.CLIMATE_PRECIPITATION,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=weight,
            explanation=explanation,
            data_sources=["regional_weather_profiles"]
        )

    def _score_humidity(self, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.7
        explanation = "Typical humidity assumptions applied"
        weight = self.environmental_weights.get(EnvironmentalFactor.CLIMATE_HUMIDITY, 0.05)
        confidence = 0.5
        if context.humidity_percent is not None:
            humidity = context.humidity_percent
            if 55.0 <= humidity <= 75.0:
                score = 0.9
                explanation = "Humidity in ideal range for most crops"
            elif 45.0 <= humidity <= 85.0:
                score = 0.75
                explanation = "Humidity acceptable with management"
            else:
                score = 0.45
                explanation = "Humidity outside typical range"
            confidence = 0.7
        return SuitabilityScore(
            factor=EnvironmentalFactor.CLIMATE_HUMIDITY,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=weight,
            explanation=explanation,
            data_sources=["regional_weather_profiles"]
        )

    def _score_wind(self, context: EnvironmentalContext) -> SuitabilityScore:
        score_map = {
            "low": (0.95, "Limited wind risk"),
            "moderate": (0.8, "Moderate wind exposure manageable"),
            "high": (0.55, "High wind risk requires mitigation"),
            "extreme": (0.35, "Extreme wind risk threatens crop stability")
        }
        risk_key = context.wind_risk or "moderate"
        if risk_key not in score_map:
            risk_key = "moderate"
        score_value, explanation = score_map[risk_key]
        return SuitabilityScore(
            factor=EnvironmentalFactor.CLIMATE_WIND,
            score=score_value,
            level=self._score_to_level(score_value),
            confidence=0.65,
            weight=self.environmental_weights.get(EnvironmentalFactor.CLIMATE_WIND, 0.05),
            explanation=explanation,
            data_sources=["regional_weather_profiles"]
        )

    def _score_soil_ph(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.6
        explanation = "Soil pH assumptions applied"
        confidence = 0.55
        ph = context.soil_ph
        if crop_data.soil_requirements and ph is not None:
            soil = crop_data.soil_requirements
            optimal_min = soil.optimal_ph_min
            optimal_max = soil.optimal_ph_max
            if optimal_min <= ph <= optimal_max:
                score = 0.95
                explanation = "Soil pH within optimal range"
            else:
                acceptable = (soil.tolerable_ph_min, soil.tolerable_ph_max)
                if acceptable[0] <= ph <= acceptable[1]:
                    score = 0.75
                    explanation = "Soil pH within tolerable range"
                else:
                    distance = 0.0
                    if ph < acceptable[0]:
                        distance = acceptable[0] - ph
                    else:
                        distance = ph - acceptable[1]
                    penalty = min(distance / 2.0, 1.0)
                    score = max(0.1, 0.6 - penalty * 0.4)
                    explanation = "Soil pH outside tolerable range"
            confidence = 0.85
        return SuitabilityScore(
            factor=EnvironmentalFactor.SOIL_PH,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=self.environmental_weights.get(EnvironmentalFactor.SOIL_PH, 0.1),
            explanation=explanation,
            data_sources=["soil_profile"]
        )

    def _score_soil_texture(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.6
        explanation = "Soil texture assumed moderate"
        confidence = 0.5
        texture = context.soil_texture
        if crop_data.soil_requirements and texture is not None:
            soil = crop_data.soil_requirements
            preferred = []
            for item in soil.preferred_textures:
                preferred.append(str(item).lower())
            tolerable = []
            for item in soil.tolerable_textures:
                tolerable.append(str(item).lower())
            if texture in preferred:
                score = 0.9
                explanation = "Preferred soil texture"
            elif texture in tolerable:
                score = 0.7
                explanation = "Tolerable soil texture with management"
            else:
                score = 0.4
                explanation = "Soil texture outside recommended range"
            confidence = 0.75
        return SuitabilityScore(
            factor=EnvironmentalFactor.SOIL_TEXTURE,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=self.environmental_weights.get(EnvironmentalFactor.SOIL_TEXTURE, 0.1),
            explanation=explanation,
            data_sources=["soil_profile"]
        )

    def _score_soil_drainage(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        score = 0.65
        explanation = "Drainage set to default"
        confidence = 0.5
        drainage = context.soil_drainage
        if crop_data.soil_requirements and drainage is not None:
            required = crop_data.soil_requirements.drainage_requirement
            preferred_value = None
            if required is not None:
                preferred_value = str(required.value).lower() if hasattr(required, 'value') else str(required).lower()
            if preferred_value is not None and drainage == preferred_value:
                score = 0.9
                explanation = "Drainage matches crop requirements"
            else:
                score = 0.55
                explanation = "Drainage differs from optimal requirement"
            confidence = 0.7
        return SuitabilityScore(
            factor=EnvironmentalFactor.SOIL_DRAINAGE,
            score=score,
            level=self._score_to_level(score),
            confidence=confidence,
            weight=self.environmental_weights.get(EnvironmentalFactor.SOIL_DRAINAGE, 0.1),
            explanation=explanation,
            data_sources=["soil_profile"]
        )

    def _score_soil_fertility(self, context: EnvironmentalContext) -> SuitabilityScore:
        fertility = context.soil_fertility or "moderate"
        score_map = {
            "high": (0.92, "High fertility supports yield potential"),
            "moderate": (0.78, "Moderate fertility manageable"),
            "low": (0.52, "Low fertility requires amendments"),
            "very_low": (0.35, "Severe fertility limitations")
        }
        if fertility not in score_map:
            fertility = "moderate"
        score_value, explanation = score_map[fertility]
        return SuitabilityScore(
            factor=EnvironmentalFactor.SOIL_FERTILITY,
            score=score_value,
            level=self._score_to_level(score_value),
            confidence=0.6,
            weight=self.environmental_weights.get(EnvironmentalFactor.SOIL_FERTILITY, 0.08),
            explanation=explanation,
            data_sources=["soil_profile"]
        )

    def _score_soil_salinity(self, crop_data: ComprehensiveCropData, context: EnvironmentalContext) -> SuitabilityScore:
        salinity = context.soil_salinity or "low"
        tolerance = "low"
        if crop_data.soil_requirements and crop_data.soil_requirements.salinity_tolerance:
            tolerance_value = crop_data.soil_requirements.salinity_tolerance
            tolerance = str(tolerance_value.value).lower() if hasattr(tolerance_value, 'value') else str(tolerance_value).lower()

        score = 0.85
        explanation = "Salinity within tolerance"
        if salinity == "moderate" and tolerance in ("low", "very_low"):
            score = 0.55
            explanation = "Moderate salinity challenges crop"
        if salinity == "high" and tolerance not in ("high", "very_high"):
            score = 0.35
            explanation = "High salinity requires mitigation"

        return SuitabilityScore(
            factor=EnvironmentalFactor.SOIL_SALINITY,
            score=score,
            level=self._score_to_level(score),
            confidence=0.6,
            weight=self.environmental_weights.get(EnvironmentalFactor.SOIL_SALINITY, 0.04),
            explanation=explanation,
            data_sources=["soil_profile"]
        )

    def _score_pest_pressure(self, context: EnvironmentalContext) -> SuitabilityScore:
        pressure = context.pest_pressure or "moderate"
        return self._score_pressure_level(pressure, EnvironmentalFactor.PEST_PRESSURE, "pest pressure")

    def _score_disease_pressure(self, context: EnvironmentalContext) -> SuitabilityScore:
        pressure = context.disease_pressure or "moderate"
        return self._score_pressure_level(pressure, EnvironmentalFactor.DISEASE_PRESSURE, "disease pressure")

    def _score_weed_pressure(self, context: EnvironmentalContext) -> SuitabilityScore:
        pressure = context.weed_pressure or "moderate"
        return self._score_pressure_level(pressure, EnvironmentalFactor.WEED_PRESSURE, "weed pressure")

    def _score_pressure_level(
        self,
        pressure: str,
        factor: EnvironmentalFactor,
        label: str
    ) -> SuitabilityScore:
        score_map = {
            "low": (0.9, f"Low {label}"),
            "moderate": (0.7, f"Moderate {label} manageable"),
            "high": (0.45, f"High {label} requires mitigation"),
            "severe": (0.25, f"Severe {label} limits suitability")
        }
        key = pressure
        if key not in score_map:
            key = "moderate"
        score_value, explanation = score_map[key]
        return SuitabilityScore(
            factor=factor,
            score=score_value,
            level=self._score_to_level(score_value),
            confidence=0.55,
            weight=self.environmental_weights.get(factor, 0.02),
            explanation=explanation,
            data_sources=["regional_pest_pressure"]
        )

    def _score_irrigation(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "available": (0.92, "Irrigation available when needed"),
            "limited": (0.65, "Limited irrigation access"),
            "rainfed": (0.55, "Rainfed reliance increases risk"),
            "none": (0.35, "No irrigation available")
        }
        key = context.irrigation if context.irrigation else "limited"
        if key not in mapping:
            key = "limited"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.IRRIGATION_AVAILABILITY,
            score=value,
            level=self._score_to_level(value),
            confidence=0.7,
            weight=self.management_weights.get(ManagementFactor.IRRIGATION_AVAILABILITY, 0.15),
            explanation=explanation,
            data_sources=["farm_management_profile"]
        )

    def _score_fertilizer_access(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "advanced": (0.92, "Advanced fertility program"),
            "standard": (0.82, "Standard fertility inputs available"),
            "limited": (0.58, "Limited fertilizer availability"),
            "minimal": (0.4, "Minimal fertility inputs")
        }
        key = context.fertilizer_program if context.fertilizer_program else "standard"
        if key not in mapping:
            key = "standard"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.FERTILIZER_ACCESS,
            score=value,
            level=self._score_to_level(value),
            confidence=0.68,
            weight=self.management_weights.get(ManagementFactor.FERTILIZER_ACCESS, 0.12),
            explanation=explanation,
            data_sources=["farm_management_profile"]
        )

    def _score_equipment(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "modern": (0.88, "Modern equipment available"),
            "moderate": (0.76, "Adequate equipment"),
            "basic": (0.6, "Basic equipment support"),
            "limited": (0.45, "Limited equipment availability")
        }
        key = context.equipment if context.equipment else "moderate"
        if key not in mapping:
            key = "moderate"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.EQUIPMENT_AVAILABILITY,
            score=value,
            level=self._score_to_level(value),
            confidence=0.65,
            weight=self.management_weights.get(ManagementFactor.EQUIPMENT_AVAILABILITY, 0.12),
            explanation=explanation,
            data_sources=["farm_management_profile"]
        )

    def _score_labor(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "abundant": (0.9, "Strong labor availability"),
            "sufficient": (0.8, "Labor generally sufficient"),
            "limited": (0.55, "Labor constraints expected"),
            "scarce": (0.35, "Labor shortage severe")
        }
        key = context.labor if context.labor else "sufficient"
        if key not in mapping:
            key = "sufficient"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.LABOR_AVAILABILITY,
            score=value,
            level=self._score_to_level(value),
            confidence=0.62,
            weight=self.management_weights.get(ManagementFactor.LABOR_AVAILABILITY, 0.1),
            explanation=explanation,
            data_sources=["labor_market_profile"]
        )

    def _score_market_access(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "international": (0.92, "Strong market access"),
            "national": (0.85, "Reliable market access"),
            "regional": (0.73, "Regional market access"),
            "local": (0.55, "Limited market reach")
        }
        key = context.market_access if context.market_access else "regional"
        if key not in mapping:
            key = "regional"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.MARKET_ACCESS,
            score=value,
            level=self._score_to_level(value),
            confidence=0.64,
            weight=self.management_weights.get(ManagementFactor.MARKET_ACCESS, 0.12),
            explanation=explanation,
            data_sources=["market_access_profile"]
        )

    def _score_transportation(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "excellent": (0.9, "Excellent transportation infrastructure"),
            "average": (0.75, "Average transportation support"),
            "limited": (0.55, "Limited transportation access"),
            "poor": (0.35, "Transportation severely constrained")
        }
        key = context.transportation if context.transportation else "average"
        if key not in mapping:
            key = "average"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.TRANSPORTATION,
            score=value,
            level=self._score_to_level(value),
            confidence=0.63,
            weight=self.management_weights.get(ManagementFactor.TRANSPORTATION, 0.1),
            explanation=explanation,
            data_sources=["infrastructure_profile"]
        )

    def _score_storage(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "advanced": (0.9, "Advanced storage systems"),
            "enhanced": (0.82, "Enhanced storage options"),
            "basic": (0.65, "Basic storage options"),
            "limited": (0.45, "Storage constraints present")
        }
        key = context.storage if context.storage else "basic"
        if key not in mapping:
            key = "basic"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.STORAGE_FACILITIES,
            score=value,
            level=self._score_to_level(value),
            confidence=0.6,
            weight=self.management_weights.get(ManagementFactor.STORAGE_FACILITIES, 0.075),
            explanation=explanation,
            data_sources=["infrastructure_profile"]
        )

    def _score_processing(self, context: ManagementContext) -> SuitabilityScore:
        mapping = {
            "extensive": (0.88, "Extensive processing infrastructure"),
            "moderate": (0.75, "Moderate processing infrastructure"),
            "limited": (0.55, "Limited processing capacity"),
            "none": (0.35, "Processing infrastructure absent")
        }
        key = context.processing if context.processing else "moderate"
        if key not in mapping:
            key = "moderate"
        value, explanation = mapping[key]
        return SuitabilityScore(
            factor=ManagementFactor.PROCESSING_FACILITIES,
            score=value,
            level=self._score_to_level(value),
            confidence=0.58,
            weight=self.management_weights.get(ManagementFactor.PROCESSING_FACILITIES, 0.075),
            explanation=explanation,
            data_sources=["infrastructure_profile"]
        )

    def _score_seed_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.seed_cost_index, EconomicFactor.SEED_COST, "Seed cost index")

    def _score_input_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.input_cost_index, EconomicFactor.INPUT_COSTS, "Input cost index")

    def _score_labor_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.labor_cost_index, EconomicFactor.LABOR_COSTS, "Labor cost index")

    def _score_transport_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.transportation_cost_index, EconomicFactor.TRANSPORTATION_COSTS, "Transportation cost index")

    def _score_storage_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.storage_cost_index, EconomicFactor.STORAGE_COSTS, "Storage cost index")

    def _score_processing_cost(self, context: EconomicContext) -> SuitabilityScore:
        return self._score_cost_index(context.processing_cost_index, EconomicFactor.PROCESSING_COSTS, "Processing cost index")

    def _score_market_price(self, context: EconomicContext) -> SuitabilityScore:
        price = context.market_price_index if context.market_price_index is not None else 1.0
        score = 0.75
        explanation = "Average market price"
        if price >= 1.2:
            score = 0.92
            explanation = "Premium market price"
        elif price >= 1.0:
            score = 0.83
            explanation = "Above average market price"
        elif price <= 0.8:
            score = 0.55
            explanation = "Below average market price"
        return SuitabilityScore(
            factor=EconomicFactor.MARKET_PRICE,
            score=score,
            level=self._score_to_level(score),
            confidence=0.68,
            weight=self.economic_weights.get(EconomicFactor.MARKET_PRICE, 0.14),
            explanation=explanation,
            data_sources=["market_price_index"]
        )

    def _score_profit_margin(self, context: EconomicContext) -> SuitabilityScore:
        margin = context.profit_margin_index if context.profit_margin_index is not None else 1.0
        score = 0.75
        explanation = "Typical profit margin"
        if margin >= 1.2:
            score = 0.93
            explanation = "High profit margin expectations"
        elif margin <= 0.8:
            score = 0.55
            explanation = "Slim profit margins"
        return SuitabilityScore(
            factor=EconomicFactor.PROFIT_MARGIN,
            score=score,
            level=self._score_to_level(score),
            confidence=0.68,
            weight=self.economic_weights.get(EconomicFactor.PROFIT_MARGIN, 0.16),
            explanation=explanation,
            data_sources=["market_profit_index"]
        )

    def _score_cost_index(
        self,
        index_value: Optional[float],
        factor: EconomicFactor,
        label: str
    ) -> SuitabilityScore:
        value = index_value if index_value is not None else 1.0
        score = 0.75
        explanation = f"{label} balanced"
        if value <= 0.8:
            score = 0.9
            explanation = f"{label} favorable"
        elif value <= 1.1:
            score = 0.78
            explanation = f"{label} manageable"
        elif value <= 1.3:
            score = 0.6
            explanation = f"{label} elevated"
        else:
            score = 0.4
            explanation = f"{label} highly unfavorable"
        return SuitabilityScore(
            factor=factor,
            score=score,
            level=self._score_to_level(score),
            confidence=0.66,
            weight=self.economic_weights.get(factor, 0.1),
            explanation=explanation,
            data_sources=["regional_cost_indices"]
        )

    def _score_to_level(self, score: float) -> SuitabilityLevel:
        if score >= 0.9:
            return SuitabilityLevel.EXCELLENT
        if score >= 0.7:
            return SuitabilityLevel.GOOD
        if score >= 0.5:
            return SuitabilityLevel.MODERATE
        if score >= 0.3:
            return SuitabilityLevel.POOR
        return SuitabilityLevel.UNSUITABLE

    def _derive_optimal_precipitation_range(self, crop_data: ComprehensiveCropData) -> Tuple[float, float]:
        if crop_data.climate_adaptations is None:
            return (20.0, 40.0)
        category: Optional[CropAgriculturalClassification] = crop_data.agricultural_classification
        primary_value = None
        if category is not None:
            primary_field = getattr(category, 'crop_category', None)
            if primary_field is not None:
                primary_value = primary_field.value if hasattr(primary_field, 'value') else str(primary_field)
        if primary_value == 'grain':
            return (25.0, 40.0)
        if primary_value == 'legume':
            return (22.0, 36.0)
        return (18.0, 45.0)
