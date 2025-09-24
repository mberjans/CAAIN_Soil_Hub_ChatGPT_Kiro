# Crop Variety Recommendations - Design Document

## Overview

This document outlines the technical design for implementing ranked crop variety recommendations with detailed explanations in the Autonomous Farm Advisory System (AFAS). The system will provide farmers with personalized, ranked lists of suitable crop varieties based on their specific conditions, complete with agricultural reasoning and supporting data.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Variety Selection │  Comparison    │  Filtering     │  Mobile   │
│  - Ranked Lists    │  - Side-by-Side│  - Preferences │  - Touch  │
│  - Explanations    │  - Trait Matrix│  - Constraints │  - Offline│
│  - Details         │  - Performance │  - Search      │  - GPS    │
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Variety API       │  Comparison API│  Filter API    │  Explain  │
│  - Recommendations │  - Multi-Select│  - Criteria    │  - Reasons│
│  - Rankings        │  - Analysis    │  - Search      │  - Sources│
│  - Details         │  - Trade-offs  │  - Categories  │  - Context│
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Variety           │  Ranking       │  Explanation   │  Economic │
│  Recommendation    │  Engine        │  Generator     │  Analysis │
│  Service           │  - Multi-      │  - AI Service  │  - ROI    │
│  - Suitability    │    Criteria    │  - Templates   │  - Costs  │
│  - Filtering       │  - Confidence  │  - Evidence    │  - Markets│
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                   │
├─────────────────────────────────────────────────────────────────┤
│  Variety Database  │  Performance   │  Suitability   │  Economic │
│  - Crops/Varieties │  Data          │  Rules         │  Data     │
│  - Traits          │  - Trials      │  - Soil Match  │  - Prices │
│  - Resistance      │  - Yields      │  - Climate Fit │  - Costs  │
│  - Companies       │  - Regional    │  - Constraints │  - Markets│
└─────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────┐
│                  External Data Sources                          │
├─────────────────────────────────────────────────────────────────┤
│  Seed Companies    │  University    │  Extension     │  Market   │
│  - Variety Catalogs│  - Trial Data  │  - Guidelines  │  - Prices │
│  - Trait Info      │  - Performance │  - Best        │  - Trends │
│  - Availability    │  - Statistics  │    Practices   │  - Futures│
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Variety Recommendation Service

The core service responsible for generating ranked crop variety recommendations.

```python
class VarietyRecommendationService:
    """Core service for crop variety recommendations."""
    
    async def get_variety_recommendations(
        self,
        location: Location,
        soil_data: SoilData,
        climate_zone: str,
        farm_constraints: FarmConstraints,
        preferences: Optional[FarmerPreferences] = None
    ) -> VarietyRecommendationResult:
        """Generate ranked variety recommendations."""
        
    async def compare_varieties(
        self,
        variety_ids: List[str],
        location: Location,
        soil_data: SoilData,
        climate_zone: str
    ) -> VarietyComparisonResult:
        """Compare multiple varieties side-by-side."""
        
    async def filter_varieties(
        self,
        filters: VarietyFilters,
        location: Location
    ) -> List[VarietyInfo]:
        """Filter varieties by specified criteria."""
        
    async def explain_recommendation(
        self,
        variety_id: str,
        location: Location,
        soil_data: SoilData,
        climate_zone: str
    ) -> RecommendationExplanation:
        """Generate detailed explanation for variety recommendation."""
```

### Data Models

#### VarietyRecommendationResult
```python
@dataclass
class VarietyRecommendationResult:
    """Result of variety recommendation request."""
    recommendations: List[VarietyRecommendation]
    total_varieties_considered: int
    filtering_applied: List[str]
    confidence_score: float
    data_sources: List[str]
    generated_at: datetime
    location_context: LocationContext
    
@dataclass
class VarietyRecommendation:
    """Individual variety recommendation."""
    variety: VarietyInfo
    suitability_score: float
    confidence_score: float
    rank: int
    
    # Performance predictions
    yield_potential: YieldPrediction
    economic_analysis: EconomicAnalysis
    
    # Suitability factors
    soil_compatibility: SuitabilityScore
    climate_suitability: SuitabilityScore
    disease_resistance_value: SuitabilityScore
    
    # Explanations
    primary_explanation: str
    detailed_reasoning: List[ReasoningPoint]
    supporting_evidence: List[EvidenceSource]
    
    # Timing and management
    planting_dates: PlantingDateRange
    management_requirements: ManagementRequirements
    
    # Warnings and considerations
    warnings: List[str]
    special_considerations: List[str]
```

#### VarietyInfo
```python
@dataclass
class VarietyInfo:
    """Comprehensive variety information."""
    variety_id: str
    variety_name: str
    crop_name: str
    company: str
    
    # Basic characteristics
    maturity_days: int
    maturity_group: Optional[str]
    yield_potential_range: Tuple[float, float]
    
    # Resistance profiles
    disease_resistance: Dict[str, ResistanceLevel]
    pest_resistance: Dict[str, ResistanceLevel]
    herbicide_tolerance: List[str]
    
    # Agronomic traits
    drought_tolerance: ToleranceLevel
    heat_tolerance: ToleranceLevel
    cold_tolerance: ToleranceLevel
    lodging_resistance: ResistanceLevel
    
    # Special traits
    special_traits: List[str]
    gmo_traits: List[str]
    organic_approved: bool
    
    # Adaptation and performance
    regional_adaptation: List[str]
    soil_type_preferences: List[str]
    ph_tolerance_range: Tuple[float, float]
    
    # Economic factors
    seed_cost_per_acre: Optional[float]
    premium_potential: Optional[float]
    
    # Metadata
    release_year: int
    is_active: bool
    data_quality_score: float
    last_updated: datetime
```

#### YieldPrediction
```python
@dataclass
class YieldPrediction:
    """Yield prediction for a variety in specific conditions."""
    expected_yield: float
    yield_range_low: float
    yield_range_high: float
    confidence_interval: float
    yield_units: str
    
    # Factors affecting yield
    soil_yield_factor: float
    climate_yield_factor: float
    management_yield_factor: float
    
    # Historical context
    regional_average_yield: Optional[float]
    variety_yield_advantage: Optional[float]
    
    # Risk assessment
    yield_stability_score: float
    weather_risk_factors: List[str]
    
    # Supporting data
    trial_data_points: int
    years_of_data: int
    geographic_relevance: float
```

### Ranking Algorithm

#### Multi-Criteria Scoring System
```python
class VarietyRankingEngine:
    """Engine for ranking crop varieties based on multiple criteria."""
    
    def __init__(self):
        self.scoring_weights = {
            'soil_compatibility': 0.25,
            'climate_suitability': 0.25,
            'yield_potential': 0.20,
            'disease_resistance': 0.15,
            'economic_viability': 0.10,
            'management_ease': 0.05
        }
    
    async def calculate_variety_score(
        self,
        variety: VarietyInfo,
        location: Location,
        soil_data: SoilData,
        climate_zone: str,
        farm_constraints: FarmConstraints
    ) -> ScoredVariety:
        """Calculate comprehensive suitability score for a variety."""
        
        # Soil compatibility scoring
        soil_score = await self._score_soil_compatibility(
            variety, soil_data
        )
        
        # Climate suitability scoring
        climate_score = await self._score_climate_suitability(
            variety, climate_zone, location
        )
        
        # Yield potential scoring
        yield_score = await self._score_yield_potential(
            variety, location, soil_data, climate_zone
        )
        
        # Disease resistance scoring
        disease_score = await self._score_disease_resistance(
            variety, location
        )
        
        # Economic viability scoring
        economic_score = await self._score_economic_viability(
            variety, farm_constraints
        )
        
        # Management ease scoring
        management_score = await self._score_management_ease(
            variety, farm_constraints
        )
        
        # Calculate weighted overall score
        overall_score = (
            soil_score * self.scoring_weights['soil_compatibility'] +
            climate_score * self.scoring_weights['climate_suitability'] +
            yield_score * self.scoring_weights['yield_potential'] +
            disease_score * self.scoring_weights['disease_resistance'] +
            economic_score * self.scoring_weights['economic_viability'] +
            management_score * self.scoring_weights['management_ease']
        )
        
        return ScoredVariety(
            variety=variety,
            overall_score=overall_score,
            component_scores={
                'soil_compatibility': soil_score,
                'climate_suitability': climate_score,
                'yield_potential': yield_score,
                'disease_resistance': disease_score,
                'economic_viability': economic_score,
                'management_ease': management_score
            },
            confidence_score=self._calculate_confidence(variety, location)
        )
    
    async def _score_soil_compatibility(
        self,
        variety: VarietyInfo,
        soil_data: SoilData
    ) -> float:
        """Score variety compatibility with soil conditions."""
        
        score = 1.0
        
        # pH compatibility
        if soil_data.ph:
            ph_min, ph_max = variety.ph_tolerance_range
            if ph_min <= soil_data.ph <= ph_max:
                # Within tolerance range
                optimal_ph = (ph_min + ph_max) / 2
                ph_deviation = abs(soil_data.ph - optimal_ph)
                ph_range = (ph_max - ph_min) / 2
                ph_score = max(0.7, 1.0 - (ph_deviation / ph_range) * 0.3)
            else:
                # Outside tolerance range
                if soil_data.ph < ph_min:
                    ph_score = max(0.3, 0.7 - (ph_min - soil_data.ph) * 0.2)
                else:
                    ph_score = max(0.3, 0.7 - (soil_data.ph - ph_max) * 0.2)
            
            score *= ph_score
        
        # Soil texture compatibility
        if soil_data.soil_texture and variety.soil_type_preferences:
            if soil_data.soil_texture in variety.soil_type_preferences:
                texture_score = 1.0
            else:
                # Partial compatibility based on texture similarity
                texture_score = self._calculate_texture_similarity(
                    soil_data.soil_texture, variety.soil_type_preferences
                )
            
            score *= texture_score
        
        # Drainage requirements
        if hasattr(variety, 'drainage_requirements') and soil_data.drainage_class:
            drainage_score = self._score_drainage_compatibility(
                variety.drainage_requirements, soil_data.drainage_class
            )
            score *= drainage_score
        
        return min(score, 1.0)
```

### Explanation Generation System

#### Agricultural Reasoning Engine
```python
class RecommendationExplainer:
    """Generates explanations for variety recommendations."""
    
    async def generate_explanation(
        self,
        variety: VarietyInfo,
        suitability_scores: Dict[str, float],
        location: Location,
        soil_data: SoilData,
        climate_zone: str
    ) -> RecommendationExplanation:
        """Generate comprehensive explanation for variety recommendation."""
        
        explanation_parts = []
        
        # Primary suitability explanation
        primary_reason = self._identify_primary_suitability_factor(
            suitability_scores
        )
        explanation_parts.append(
            await self._explain_primary_suitability(
                variety, primary_reason, location, soil_data, climate_zone
            )
        )
        
        # Soil compatibility explanation
        if suitability_scores['soil_compatibility'] > 0.8:
            explanation_parts.append(
                self._explain_soil_compatibility(variety, soil_data)
            )
        elif suitability_scores['soil_compatibility'] < 0.6:
            explanation_parts.append(
                self._explain_soil_challenges(variety, soil_data)
            )
        
        # Climate suitability explanation
        explanation_parts.append(
            self._explain_climate_suitability(variety, climate_zone, location)
        )
        
        # Yield potential explanation
        if suitability_scores['yield_potential'] > 0.8:
            explanation_parts.append(
                self._explain_yield_advantages(variety, location)
            )
        
        # Disease resistance explanation
        if suitability_scores['disease_resistance'] > 0.7:
            explanation_parts.append(
                self._explain_disease_resistance_benefits(variety, location)
            )
        
        # Economic considerations
        explanation_parts.append(
            self._explain_economic_factors(variety, location)
        )
        
        # Combine explanations
        primary_explanation = explanation_parts[0]
        detailed_reasoning = explanation_parts[1:]
        
        return RecommendationExplanation(
            primary_explanation=primary_explanation,
            detailed_reasoning=detailed_reasoning,
            supporting_evidence=await self._gather_supporting_evidence(
                variety, location
            ),
            confidence_factors=self._explain_confidence_factors(
                variety, suitability_scores
            ),
            agricultural_sources=self._get_agricultural_sources(variety)
        )
    
    def _explain_soil_compatibility(
        self,
        variety: VarietyInfo,
        soil_data: SoilData
    ) -> str:
        """Explain why variety is compatible with soil conditions."""
        
        explanations = []
        
        if soil_data.ph:
            ph_min, ph_max = variety.ph_tolerance_range
            if ph_min <= soil_data.ph <= ph_max:
                explanations.append(
                    f"Your soil pH of {soil_data.ph} is within the optimal range "
                    f"for {variety.variety_name} ({ph_min}-{ph_max})"
                )
        
        if soil_data.soil_texture and variety.soil_type_preferences:
            if soil_data.soil_texture in variety.soil_type_preferences:
                explanations.append(
                    f"Your {soil_data.soil_texture} soil is well-suited for "
                    f"{variety.variety_name}, which performs well in this soil type"
                )
        
        if soil_data.organic_matter_percent:
            if soil_data.organic_matter_percent >= 3.0:
                explanations.append(
                    f"Your soil's organic matter level of {soil_data.organic_matter_percent}% "
                    f"provides good nutrient availability for {variety.variety_name}"
                )
        
        return ". ".join(explanations) + "."
```

### Variety Comparison System

#### Side-by-Side Comparison
```python
class VarietyComparisonService:
    """Service for comparing multiple crop varieties."""
    
    async def compare_varieties(
        self,
        variety_ids: List[str],
        location: Location,
        soil_data: SoilData,
        climate_zone: str
    ) -> VarietyComparisonResult:
        """Generate detailed comparison of multiple varieties."""
        
        varieties = await self._get_varieties(variety_ids)
        
        # Calculate scores for each variety
        scored_varieties = []
        for variety in varieties:
            scored_variety = await self.ranking_engine.calculate_variety_score(
                variety, location, soil_data, climate_zone, FarmConstraints()
            )
            scored_varieties.append(scored_variety)
        
        # Generate comparison matrix
        comparison_matrix = self._build_comparison_matrix(scored_varieties)
        
        # Identify key differences
        key_differences = self._identify_key_differences(scored_varieties)
        
        # Generate trade-off analysis
        trade_offs = self._analyze_trade_offs(scored_varieties)
        
        return VarietyComparisonResult(
            varieties=scored_varieties,
            comparison_matrix=comparison_matrix,
            key_differences=key_differences,
            trade_off_analysis=trade_offs,
            recommendation_summary=self._generate_comparison_summary(
                scored_varieties
            )
        )
    
    def _build_comparison_matrix(
        self,
        scored_varieties: List[ScoredVariety]
    ) -> ComparisonMatrix:
        """Build matrix comparing variety characteristics."""
        
        characteristics = [
            'maturity_days',
            'yield_potential',
            'disease_resistance',
            'drought_tolerance',
            'soil_compatibility',
            'economic_viability'
        ]
        
        matrix = {}
        for char in characteristics:
            matrix[char] = {}
            for variety in scored_varieties:
                matrix[char][variety.variety.variety_id] = \
                    self._get_characteristic_value(variety, char)
        
        return ComparisonMatrix(
            characteristics=characteristics,
            variety_ids=[v.variety.variety_id for v in scored_varieties],
            values=matrix,
            highlights=self._identify_comparison_highlights(matrix)
        )
```

## Error Handling

### Recommendation Generation Errors
```python
class VarietyRecommendationError(Exception):
    """Base exception for variety recommendation operations."""
    pass

class InsufficientDataError(VarietyRecommendationError):
    """Error when insufficient data is available for recommendations."""
    pass

class NoSuitableVarietiesError(VarietyRecommendationError):
    """Error when no suitable varieties are found."""
    pass

# Error handling with graceful degradation
async def get_recommendations_with_fallback(
    location: Location,
    soil_data: SoilData,
    climate_zone: str
) -> VarietyRecommendationResult:
    """Get variety recommendations with fallback strategies."""
    
    try:
        # Primary recommendation generation
        return await variety_service.get_variety_recommendations(
            location, soil_data, climate_zone, FarmConstraints()
        )
    except InsufficientDataError:
        # Fallback 1: Use regional defaults
        try:
            return await variety_service.get_regional_default_recommendations(
                location, climate_zone
            )
        except Exception:
            # Fallback 2: Use crop-level recommendations
            return await variety_service.get_crop_level_recommendations(
                location, climate_zone
            )
    except NoSuitableVarietiesError:
        # Return best available with warnings
        return await variety_service.get_best_available_with_warnings(
            location, soil_data, climate_zone
        )
```

## Testing Strategy

### Unit Tests
- Variety ranking algorithm accuracy
- Explanation generation quality
- Comparison matrix calculations
- Data model validation

### Integration Tests
- End-to-end recommendation workflow
- API endpoint functionality
- Database query performance
- External data source integration

### Agricultural Validation Tests
- Recommendation accuracy against expert knowledge
- Yield prediction validation
- Disease resistance accuracy
- Regional adaptation correctness

### Performance Tests
- Recommendation generation response times
- Concurrent user handling
- Database query optimization
- Cache effectiveness

### User Experience Tests
- Explanation clarity and usefulness
- Mobile interface usability
- Comparison tool effectiveness
- Filter and search functionality

## Deployment Considerations

### Data Requirements
- Comprehensive variety database (~100MB)
- University trial data (~50MB)
- Disease resistance profiles (~20MB)
- Regional adaptation data (~30MB)

### Caching Strategy
- Variety recommendations cached for 1 hour
- Variety details cached for 24 hours
- Comparison results cached for 2 hours
- Explanation templates cached for 7 days

### Performance Optimization
- Database indexing for variety queries
- Pre-computed suitability matrices
- Efficient ranking algorithms
- Connection pooling for external APIs

### Monitoring and Alerting
- Recommendation generation success rates
- Explanation quality metrics
- User satisfaction scores
- Data source availability
- Cache hit rates

This design provides a comprehensive, scalable, and accurate crop variety recommendation system that delivers personalized, well-explained variety suggestions to help farmers make informed planting decisions.