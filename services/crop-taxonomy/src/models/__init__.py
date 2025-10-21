"""
Crop Taxonomy Models

Pydantic models for comprehensive crop classification, filtering, and taxonomic data.
This module provides the data models for the crop taxonomy system that extends
the CAAIN Soil Hub with advanced crop categorization capabilities.
"""

import sys
from types import ModuleType

from .crop_taxonomy_models import *
from .crop_filtering_models import *
from .crop_variety_models import *
from .service_models import *
from .preference_models import *
from .recommendation_management_models import *
from .growing_season_models import *
from .pest_resistance_models import *
from .resistance_explanation_models import *
from .trial_data_models import *
from .filtering_models import *

__all__ = [
    # Core taxonomy models
    'CropTaxonomicHierarchy',
    'CropAgriculturalClassification', 
    'CropClimateAdaptations',
    'CropSoilRequirements',
    'CropNutritionalProfile',
    
    # Filtering and search models
    'CropFilteringAttributes',
    'CropSearchRequest',
    'CropSearchResponse',
    'TaxonomyFilterCriteria',
    'FilterDirective',
    'FilterCombinationRequest',
    'FilterCombinationResponse',
    'FilterPresetSummary',
    'FilterPreset',
    'FilterSuggestionRequest',
    'FilterSuggestionResponse',
    'FilterSuggestion',

    # Variety and regional models
    'EnhancedCropVariety',
    'CropRegionalAdaptation',
    'VarietyRecommendation',
    'VarietyComparisonMatrix',
    'VarietyComparisonDetail',
    'VarietyTradeOff',
    'VarietyComparisonSummary',
    'VarietyComparisonRequest',
    'VarietyComparisonResponse',

    # Service request/response models
    'CropTaxonomyRequest',
    'CropTaxonomyResponse',
    'CropClassificationRequest',
    'CropClassificationResponse',
    'AutoTagGenerationRequest',
    'AutoTagGenerationResponse',
    'TagManagementRequest',
    'TagManagementResponse',
    'CropAttributeTagPayload',
    'TagManagementInstruction',
    
    # Enumerations
    'CropCategory',
    'PrimaryUse',
    'GrowthHabit',
    'PlantType',
    'PhotosynthesisType',
    'FrostTolerance',
    'DroughtTolerance',
    'WaterRequirement',
    'ToleranceLevel',
    'ManagementComplexity',
    'InputRequirements',
    'LaborRequirements',
    'CarbonSequestrationPotential',
    'BiodiversitySupport',
    'PollinatorValue',
    'WaterUseEfficiency',
    'MarketStability',
    'SearchOperator',
    'SortOrder',
    'SortField',
    'TagCategory',
    'TagType',
    'TagValidationStatus',
    'TagManagementAction',
    'SeedAvailabilityStatus',
    'PatentStatus',
    'SeedCompanyOffering',
    'TraitStackEntry',
    'RegionalPerformanceEntry',

    # Growing season models
    'GrowthStage',
    'TemperatureSensitivity',
    'PhotoperiodResponse',
    'SeasonRiskLevel',
    'PhenologyModelType',
    'GrowingDegreeDayParameters',
    'PhenologyStage',
    'VarietyPhenologyProfile',
    'SeasonLengthAnalysis',
    'TemperatureSensitivityAnalysis',
    'PhotoperiodAnalysis',
    'CriticalDatePrediction',
    'GrowingSeasonCalendar',
    'SeasonRiskAssessment',
    'GrowingSeasonAnalysis',
    'GrowingSeasonAnalysisRequest',
    'GrowingSeasonAnalysisResponse',
    'PhenologyPredictionRequest',
    'PhenologyPredictionResponse',
    'GrowingSeasonModelsValidator',

    # Preference models
    'PreferenceType',
    'PreferenceDimension',
    'ConstraintType',
    'RiskTolerance',
    'ManagementStyle',
    
    # Recommendation management models
    'SavedVarietyRecommendation',
    'RecommendationHistory',
    'RecommendationFeedback',
    'SaveRecommendationRequest',
    'RecommendationHistoryRequest',
    'RecommendationFeedbackRequest',
    'UpdateRecommendationRequest',
    'SaveRecommendationResponse',
    'RecommendationHistoryResponse',
    'RecommendationFeedbackResponse',
    'UpdateRecommendationResponse',
    'RecommendationAnalytics',
    'RecommendationStatus',
    'FeedbackType',
    'RecommendationSource',
    'RecommendationManagementValidator',
    'PreferenceWeight',
    'PreferenceConstraint',
    'PreferenceConfidence',
    'PreferenceSignal',
    'PreferenceLearningRequest',
    'PreferenceProfile',
    'PreferenceProfileResponse',
    'PreferenceUpdateRequest',

    # Pest resistance models
    'PestType',
    'PestSeverity',
    'PestRiskLevel',
    'ResistanceMechanism',
    'ResistanceDurability',
    'IPMStrategy',
    'PestData',
    'RegionalPestPressure',
    'PestPressureEntry',
    'VarietyPestResistance',
    'PestResistanceEntry',
    'PestResistanceRequest',
    'PestResistanceResponse',
    'VarietyPestAnalysis',
    'VarietyRecommendation',
    'PestManagementRecommendations',
    'ChemicalControlRecommendation',
    'PestTimingGuidance',
    'CriticalTimingPeriod',
    'MonitoringPeriod',
    'ActionThreshold',
    'SeasonalActivity',
    'ResistanceAnalysis',
    'ResistanceStack',
    'RefugeRequirements',
    'PestForecast',
    'PestForecastEntry',
    'PestTrends',
    'PestTrendEntry',

    # Resistance explanation models
    'ResistanceType',
    'ResistanceMechanism',
    'StewardshipLevel',
    'EducationLevel',
    'ComplianceLevel',
    'ResistanceTrait',
    'MechanismExplanation',
    'PestPressureAnalysis',
    'ResistanceEffectiveness',
    'RiskAssessment',
    'EducationalContent',
    'TraitSpecificEducation',
    'RefugeRequirements',
    'StewardshipGuidelines',
    'ManagementRecommendations',
    'DurabilityAssessment',
    'ComplianceRequirements',
    'ExplanationSections',
    'ResistanceExplanationRequest',
    'ResistanceExplanationResponse',
    'EducationalContentRequest',
    'EducationalContentResponse',
    'StewardshipGuidelinesRequest',
    'StewardshipGuidelinesResponse',
    'MechanismExplanationRequest',
    'MechanismExplanationResponse',
    'ComplianceRequirementsRequest',
    'ComplianceRequirementsResponse',
    'DurabilityAssessmentRequest',
    'DurabilityAssessmentResponse',
    'ResistanceExplanationValidator',

    # Trial data models
    'TrialDataQuality',
    'StatisticalSignificance',
    'TrialDataRequest',
    'VarietyPerformanceRequest',
    'RegionalTrialRequest',
    'TrialIngestionRequest',
    'TrialLocationInfo',
    'TrialDesignInfo',
    'TrialStatistics',
    'TrialQualityInfo',
    'TrialMetadata',
    'TrialSummaryInfo',
    'TrialDataResponse',
    'VarietyPerformanceMetrics',
    'VarietyPerformanceResponse',
    'RegionalTrialInfo',
    'RegionalTrialResponse',
    'TrialIngestionResult',
    'TrialIngestionResponse',
    'TrialDataValidation',
    'TrialDataValidationResult',
    'TrialDataFilter',
    'TrialDataSort',
    'TrialDataAggregation'
]


def _ensure_src_module_aliases():
    """Expose models through the `src` namespace for legacy imports."""
    if 'src' in sys.modules:
        src_module = sys.modules['src']
    else:
        src_module = ModuleType('src')
        sys.modules['src'] = src_module

    if hasattr(src_module, 'models') and isinstance(getattr(src_module, 'models'), ModuleType):
        models_module = getattr(src_module, 'models')
    else:
        models_module = ModuleType('src.models')
        setattr(src_module, 'models', models_module)
        sys.modules['src.models'] = models_module

    from . import service_models as _service_models  # Local import to avoid circulars
    setattr(models_module, 'service_models', _service_models)
    sys.modules['src.models.service_models'] = _service_models


_ensure_src_module_aliases()
