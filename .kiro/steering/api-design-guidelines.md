# API Design Guidelines for AFAS

## Overview
This document establishes API design standards for the Autonomous Farm Advisory System (AFAS). All APIs must prioritize agricultural accuracy, farmer usability, and system reliability while following RESTful principles and agricultural domain best practices.

## Core API Principles

### Agricultural-First Design
- **Farmer-Centric**: APIs should reflect how farmers think about their operations
- **Agricultural Units**: Always use standard agricultural units (lbs/acre, bu/acre, ppm)
- **Seasonal Context**: Consider timing and seasonality in all agricultural endpoints
- **Regional Awareness**: Support location-specific recommendations and data
- **Conservative Responses**: When uncertain, provide conservative recommendations with clear confidence levels
- **FastAPI Consistency**: All services use FastAPI for automatic documentation and validation

### RESTful Standards with Agricultural Context
```
GET    /api/v1/farms/{farm_id}/fields                    # List farm fields
POST   /api/v1/farms/{farm_id}/fields                    # Create new field
GET    /api/v1/farms/{farm_id}/fields/{field_id}         # Get field details
PUT    /api/v1/farms/{farm_id}/fields/{field_id}         # Update field
DELETE /api/v1/farms/{farm_id}/fields/{field_id}         # Delete field

# Agricultural-specific nested resources
GET    /api/v1/farms/{farm_id}/soil-tests                # List soil tests
POST   /api/v1/farms/{farm_id}/soil-tests                # Submit soil test
GET    /api/v1/farms/{farm_id}/recommendations           # Get recommendations
POST   /api/v1/farms/{farm_id}/recommendations/generate  # Generate new recommendations
```

## Agricultural API Endpoints

### Question-Based Recommendation Endpoints
Each of the 20 key farmer questions has a dedicated endpoint following consistent patterns:

```python
# Question 1: Crop Selection
POST /api/v1/recommendations/crop-selection
{
    "farm_id": "uuid",
    "location": {
        "latitude": 42.0308,
        "longitude": -93.6319,
        "address": "Ames, Iowa, USA"  # Optional, for geocoding validation
    },
    "soil_data": {
        "ph": 6.2,
        "organic_matter_percent": 3.8,
        "phosphorus_ppm": 25,        # Mehlich-3 extraction
        "potassium_ppm": 180,        # Mehlich-3 extraction
        "soil_texture": "silt_loam",
        "drainage_class": "well_drained",
        "test_date": "2024-03-15"    # ISO 8601 format
    },
    "climate_preferences": {
        "drought_tolerance": "medium",
        "season_length_preference": "full_season",
        "frost_risk_tolerance": "low"
    },
    "farm_constraints": {
        "farm_size_acres": 320,
        "available_equipment": ["planter", "combine", "sprayer"],
        "irrigation_available": false,
        "organic_certification": false
    }
}

# Response
{
    "request_id": "uuid",
    "generated_at": "2024-12-09T10:30:00Z",
    "confidence_score": 0.87,
    "recommendations": [
        {
            "crop_name": "corn",
            "variety_suggestions": [
                {
                    "variety_name": "Pioneer P1197AM",
                    "maturity_days": 111,
                    "yield_potential_bu_per_acre": 185,
                    "drought_tolerance": "good",
                    "disease_resistance": ["gray_leaf_spot", "northern_corn_leaf_blight"],
                    "suitability_score": 0.92
                }
            ],
            "planting_recommendations": {
                "optimal_planting_window": {
                    "start_date": "2024-04-20",
                    "end_date": "2024-05-15"
                },
                "seeding_rate_seeds_per_acre": 32000,
                "planting_depth_inches": 2.0
            },
            "explanation": "Corn is highly suitable for your silt loam soil with pH 6.2. Your soil test shows adequate phosphorus and potassium levels. The 320-acre farm size makes corn economically viable, and your equipment is well-suited for corn production.",
            "confidence_factors": {
                "soil_suitability": 0.95,
                "climate_match": 0.88,
                "economic_viability": 0.85
            }
        }
    ],
    "agricultural_sources": [
        "Iowa State University Extension PM 1688",
        "USDA Plant Hardiness Zone Map",
        "Pioneer Seed Variety Guide 2024"
    ],
    "next_steps": [
        "Consider soil testing for micronutrients",
        "Review crop insurance options",
        "Plan nitrogen application strategy"
    ]
}
```

### Soil Management Endpoints
```python
# Question 2: Soil Fertility Improvement
POST /api/v1/recommendations/soil-fertility
{
    "farm_id": "uuid",
    "current_soil_status": {
        "soil_test_results": {
            "ph": 5.8,
            "organic_matter_percent": 2.1,
            "phosphorus_ppm": 12,
            "potassium_ppm": 95,
            "cec_meq_per_100g": 18.5,
            "test_date": "2024-03-15",
            "lab_name": "Iowa State Soil Testing Lab"
        },
        "field_observations": {
            "compaction_issues": true,
            "erosion_signs": "moderate",
            "drainage_problems": false
        }
    },
    "management_goals": {
        "primary_goal": "improve_organic_matter",
        "fertilizer_preference": "reduce_synthetic",
        "timeline": "3_years",
        "budget_per_acre": 150.00
    },
    "current_practices": {
        "tillage_system": "conventional",
        "cover_crops_used": false,
        "manure_available": {
            "type": "dairy_manure",
            "estimated_tons_available": 500,
            "nutrient_analysis": {
                "nitrogen_percent": 0.5,
                "phosphorus_percent": 0.2,
                "potassium_percent": 0.4
            }
        }
    }
}

# Response includes specific, actionable recommendations
{
    "request_id": "uuid",
    "soil_health_assessment": {
        "current_score": 6.2,  # Out of 10
        "limiting_factors": ["low_organic_matter", "acidic_ph", "low_phosphorus"],
        "improvement_potential": "high"
    },
    "recommendations": [
        {
            "practice": "lime_application",
            "priority": "high",
            "details": {
                "lime_type": "agricultural_limestone",
                "rate_tons_per_acre": 2.5,
                "application_timing": "fall_2024",
                "expected_ph_change": 6.5,
                "cost_estimate_per_acre": 45.00
            },
            "reasoning": "Soil pH of 5.8 is limiting phosphorus availability and reducing microbial activity. Lime application will improve nutrient availability and support beneficial soil organisms."
        },
        {
            "practice": "organic_matter_improvement",
            "priority": "high",
            "details": {
                "manure_application": {
                    "rate_tons_per_acre": 15,
                    "application_timing": "fall_after_harvest",
                    "nitrogen_credit_lbs_per_acre": 75,
                    "incorporation_required": true
                },
                "cover_crop_recommendation": {
                    "species": "crimson_clover_rye_mix",
                    "seeding_date": "september_15",
                    "termination_date": "april_15",
                    "nitrogen_fixation_potential_lbs": 60
                }
            },
            "reasoning": "Organic matter at 2.1% is below optimal range (3-4%). Manure and cover crops will improve soil structure, water retention, and nutrient cycling."
        }
    ],
    "implementation_timeline": {
        "year_1": ["lime_application", "manure_application", "cover_crop_seeding"],
        "year_2": ["soil_retest", "adjust_practices"],
        "year_3": ["evaluate_progress", "plan_maintenance"]
    },
    "expected_outcomes": {
        "soil_ph_target": 6.5,
        "organic_matter_target": 3.2,
        "estimated_yield_improvement": "8-12%",
        "fertilizer_reduction_potential": "20-30%"
    }
}
```

### Nutrient Management Endpoints
```python
# Question 16: Cost-Effective Fertilizer Strategy
POST /api/v1/recommendations/fertilizer-strategy
{
    "farm_id": "uuid",
    "crop_plan": {
        "primary_crop": "corn",
        "yield_goal_bu_per_acre": 180,
        "planted_acres": 250,
        "planting_date": "2024-05-01"
    },
    "soil_fertility": {
        "nitrogen_ppm": 8,           # Nitrate-N
        "phosphorus_ppm": 22,        # Mehlich-3
        "potassium_ppm": 140,        # Mehlich-3
        "organic_matter_percent": 3.2,
        "previous_crop": "soybean"
    },
    "economic_constraints": {
        "fertilizer_budget_total": 18000.00,
        "current_prices": {
            "urea_per_ton": 420.00,
            "dap_per_ton": 580.00,
            "potash_per_ton": 380.00,
            "anhydrous_ammonia_per_ton": 520.00
        },
        "application_costs": {
            "custom_application_per_acre": 12.00,
            "own_equipment_cost_per_acre": 8.50
        }
    },
    "market_conditions": {
        "corn_price_per_bushel": 4.25,
        "price_volatility": "moderate",
        "forward_contract_available": true
    }
}

# Response with economic optimization
{
    "request_id": "uuid",
    "economic_analysis": {
        "optimal_fertilizer_investment": 16250.00,
        "expected_roi_percent": 285,
        "payback_period_months": 8,
        "break_even_yield_bu_per_acre": 165
    },
    "fertilizer_strategy": {
        "nitrogen_program": {
            "total_n_rate_lbs_per_acre": 160,
            "legume_credit_lbs_per_acre": 40,  # From previous soybean
            "fertilizer_n_needed_lbs_per_acre": 120,
            "recommended_source": "anhydrous_ammonia",
            "application_timing": [
                {
                    "timing": "pre_plant",
                    "rate_lbs_n_per_acre": 80,
                    "application_date": "april_25"
                },
                {
                    "timing": "side_dress_v6",
                    "rate_lbs_n_per_acre": 40,
                    "application_date": "june_15"
                }
            ],
            "cost_per_acre": 52.80
        },
        "phosphorus_program": {
            "recommendation": "maintenance_only",
            "rate_lbs_p2o5_per_acre": 25,
            "source": "dap_at_planting",
            "reasoning": "Soil test P at 22 ppm is in adequate range. Maintenance application will replace crop removal.",
            "cost_per_acre": 18.50
        },
        "potassium_program": {
            "recommendation": "build_up",
            "rate_lbs_k2o_per_acre": 60,
            "source": "muriate_of_potash",
            "timing": "fall_application",
            "reasoning": "Soil test K at 140 ppm is below optimum for high-yield corn. Build-up application recommended.",
            "cost_per_acre": 22.40
        }
    },
    "cost_comparison": {
        "recommended_strategy": {
            "total_cost_per_acre": 93.70,
            "total_farm_cost": 23425.00,
            "expected_yield_bu_per_acre": 178,
            "gross_margin_per_acre": 663.10
        },
        "alternative_strategies": [
            {
                "strategy_name": "high_input",
                "total_cost_per_acre": 125.30,
                "expected_yield_bu_per_acre": 182,
                "gross_margin_per_acre": 648.20,
                "roi_comparison": "lower"
            },
            {
                "strategy_name": "low_input",
                "total_cost_per_acre": 68.40,
                "expected_yield_bu_per_acre": 168,
                "gross_margin_per_acre": 645.60,
                "roi_comparison": "lower"
            }
        ]
    },
    "risk_assessment": {
        "weather_risk": "moderate",
        "price_risk": "moderate",
        "yield_risk": "low",
        "mitigation_strategies": [
            "Consider crop insurance",
            "Monitor weather for application timing",
            "Use soil moisture sensors if available"
        ]
    }
}
```

## Data Validation Standards

### Agricultural Data Validation
```python
from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import date

class SoilTestData(BaseModel):
    """Soil test data with agricultural validation."""
    
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH (3.0-10.0)")
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter %")
    phosphorus_ppm: float = Field(..., ge=0.0, le=200.0, description="Phosphorus (Mehlich-3)")
    potassium_ppm: float = Field(..., ge=0.0, le=800.0, description="Potassium (Mehlich-3)")
    test_date: date = Field(..., description="Date of soil test")
    lab_name: Optional[str] = Field(None, description="Testing laboratory")
    
    @validator('test_date')
    def validate_test_date(cls, v):
        """Ensure soil test is not too old."""
        from datetime import date, timedelta
        
        max_age = date.today() - timedelta(days=3*365)  # 3 years
        if v < max_age:
            raise ValueError(f"Soil test date {v} is older than 3 years. Recent test recommended.")
        return v
    
    @validator('ph')
    def validate_ph_range(cls, v):
        """Provide warnings for extreme pH values."""
        if v < 4.5:
            # This will be logged as a warning
            import warnings
            warnings.warn(f"Extremely acidic soil (pH {v}). Lime application strongly recommended.")
        elif v > 8.5:
            warnings.warn(f"Very alkaline soil (pH {v}). May limit nutrient availability.")
        return v

class CropSelectionRequest(BaseModel):
    """Request for crop selection recommendations."""
    
    farm_id: str = Field(..., description="Unique farm identifier")
    location: LocationData
    soil_data: SoilTestData
    climate_preferences: ClimatePreferences
    farm_constraints: FarmConstraints
    
    class Config:
        schema_extra = {
            "example": {
                "farm_id": "farm_12345",
                "location": {
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "address": "Ames, Iowa, USA"
                },
                "soil_data": {
                    "ph": 6.2,
                    "organic_matter_percent": 3.8,
                    "phosphorus_ppm": 25,
                    "potassium_ppm": 180,
                    "test_date": "2024-03-15"
                }
            }
        }
```

### Response Validation
```python
class RecommendationResponse(BaseModel):
    """Standard response format for all recommendations."""
    
    request_id: str
    generated_at: datetime
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    recommendations: List[dict]
    agricultural_sources: List[str]
    next_steps: List[str]
    
    # Agricultural-specific metadata
    regional_applicability: str = Field(..., description="Geographic region for recommendations")
    seasonal_context: str = Field(..., description="Seasonal timing considerations")
    uncertainty_factors: List[str] = Field(default=[], description="Factors that may affect accuracy")
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        """Ensure confidence score meets minimum threshold."""
        if v < 0.7:
            import warnings
            warnings.warn(f"Low confidence score ({v}). Consider requesting more data.")
        return v
```

## Error Handling Standards

### Agricultural Error Responses
```python
class AgriculturalError(BaseModel):
    """Standard error response for agricultural issues."""
    
    error_code: str
    error_message: str
    agricultural_context: str
    suggested_actions: List[str]
    confidence_impact: Optional[str] = None

# Example error responses
{
    "error": {
        "error_code": "SOIL_DATA_INSUFFICIENT",
        "error_message": "Insufficient soil test data for accurate recommendations",
        "agricultural_context": "Phosphorus and potassium levels are required for fertilizer recommendations. Without this data, recommendations may be inaccurate and could lead to over or under-application.",
        "suggested_actions": [
            "Obtain recent soil test from certified laboratory",
            "Provide at minimum: pH, organic matter, P, and K levels",
            "Consider tissue testing during growing season for validation"
        ],
        "confidence_impact": "Recommendations without soil test data have <50% confidence"
    },
    "status_code": 422
}

{
    "error": {
        "error_code": "REGIONAL_DATA_UNAVAILABLE",
        "error_message": "Limited regional data for this location",
        "agricultural_context": "Crop recommendations are highly location-specific. Limited local data may result in recommendations that don't account for regional pest pressure, climate patterns, or soil characteristics.",
        "suggested_actions": [
            "Consult local extension service for region-specific guidance",
            "Consider recommendations as general guidance only",
            "Validate with local agricultural professionals"
        ],
        "confidence_impact": "Regional limitations reduce confidence by 20-30%"
    },
    "status_code": 200  # Partial success with warnings
}
```

## Rate Limiting and Quotas

### Agricultural-Aware Rate Limiting
```python
# Different rate limits based on agricultural seasonality
RATE_LIMITS = {
    "planting_season": {  # March-May
        "recommendations_per_hour": 100,
        "image_analysis_per_hour": 50,
        "soil_test_uploads_per_day": 20
    },
    "growing_season": {  # June-August
        "recommendations_per_hour": 150,  # Higher during critical growing period
        "image_analysis_per_hour": 100,   # More deficiency detection requests
        "soil_test_uploads_per_day": 10
    },
    "harvest_season": {  # September-November
        "recommendations_per_hour": 80,
        "image_analysis_per_hour": 30,
        "soil_test_uploads_per_day": 15
    },
    "off_season": {  # December-February
        "recommendations_per_hour": 50,
        "image_analysis_per_hour": 20,
        "soil_test_uploads_per_day": 5
    }
}
```

## API Versioning Strategy

### Agricultural Compatibility Versioning
```python
# Version headers that consider agricultural accuracy
@app.middleware("http")
async def add_agricultural_version_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add agricultural validation version
    response.headers["X-Agricultural-Logic-Version"] = "2024.1"
    response.headers["X-Expert-Validation-Date"] = "2024-01-15"
    response.headers["X-Regional-Data-Version"] = "2024.spring"
    
    return response

# Deprecation warnings for agricultural logic changes
@app.get("/api/v1/recommendations/fertilizer-rate")
async def get_fertilizer_rate_v1():
    """
    Deprecated: This endpoint uses 2023 fertilizer guidelines.
    Use /api/v2/recommendations/fertilizer-strategy for current recommendations.
    """
    warnings.warn(
        "v1 fertilizer recommendations use outdated guidelines. "
        "Migrate to v2 for current agricultural best practices.",
        DeprecationWarning
    )
```

## Testing API Endpoints

### Agricultural Validation Testing
```python
@pytest.mark.agricultural
async def test_crop_selection_iowa_conditions():
    """Test crop selection for typical Iowa farm conditions."""
    
    # Real-world Iowa farm data
    request_data = {
        "farm_id": "test_farm_iowa",
        "location": {"latitude": 42.0308, "longitude": -93.6319},
        "soil_data": {
            "ph": 6.4,
            "organic_matter_percent": 3.5,
            "phosphorus_ppm": 28,
            "potassium_ppm": 165,
            "test_date": "2024-03-01"
        },
        "farm_constraints": {
            "farm_size_acres": 160,
            "available_equipment": ["planter", "combine"],
            "irrigation_available": False
        }
    }
    
    response = await client.post("/api/v1/recommendations/crop-selection", 
                               json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Agricultural validation
    assert data["confidence_score"] >= 0.8
    recommendations = data["recommendations"]
    
    # Should recommend corn and soybean for Iowa
    crop_names = [rec["crop_name"] for rec in recommendations]
    assert "corn" in crop_names
    assert "soybean" in crop_names
    
    # Validate agricultural reasoning
    corn_rec = next(rec for rec in recommendations if rec["crop_name"] == "corn")
    assert "soil pH" in corn_rec["explanation"].lower()
    assert corn_rec["suitability_score"] > 0.8
    
    # Validate agricultural sources are cited
    assert len(data["agricultural_sources"]) > 0
    assert any("extension" in source.lower() for source in data["agricultural_sources"])

@pytest.mark.agricultural
async def test_fertilizer_rate_calculation_accuracy():
    """Test fertilizer rate calculations against extension guidelines."""
    
    # Test data matching Iowa State Extension recommendations
    request_data = {
        "crop_type": "corn",
        "yield_goal": 180,
        "soil_test": {
            "organic_matter_percent": 3.2,
            "nitrate_n_ppm": 10,
            "previous_crop": "soybean"
        }
    }
    
    response = await client.post("/api/v1/recommendations/nitrogen-rate", 
                               json=request_data)
    
    data = response.json()
    
    # Should match ISU guidelines within 10 lbs/acre
    expected_n_rate = 140  # From ISU Corn Nitrogen Rate Calculator
    actual_n_rate = data["nitrogen_rate_lbs_per_acre"]
    
    assert abs(actual_n_rate - expected_n_rate) <= 10
    assert "legume credit" in data["reasoning"].lower()
    assert data["confidence_score"] >= 0.85
```

## Documentation Standards

### Agricultural API Documentation
```yaml
# OpenAPI specification with agricultural context
openapi: 3.0.0
info:
  title: AFAS Agricultural Recommendations API
  version: 1.0.0
  description: |
    Autonomous Farm Advisory System API providing evidence-based agricultural recommendations.
    
    ## Agricultural Accuracy
    All recommendations are based on peer-reviewed research and validated by agricultural experts.
    Confidence scores indicate reliability of recommendations based on data quality and regional applicability.
    
    ## Regional Considerations
    Recommendations are calibrated for North American growing conditions. 
    International users should consult local agricultural experts for validation.
    
    ## Data Requirements
    - Soil test data should be <3 years old for accurate recommendations
    - Location data is required for climate-specific recommendations
    - All nutrient values should use standard agricultural units (ppm, %, lbs/acre)

paths:
  /api/v1/recommendations/crop-selection:
    post:
      summary: Get crop variety recommendations
      description: |
        Provides crop variety recommendations based on soil conditions, climate, and farm constraints.
        
        **Agricultural Basis:**
        - Matches crop requirements to soil pH, drainage, and fertility levels
        - Considers local climate zone, frost dates, and precipitation patterns
        - Evaluates economic viability based on farm size and equipment
        
        **Data Sources:**
        - USDA Plant Hardiness Zone data
        - State university extension variety trial results
        - FAO ECOCROP database for crop environmental requirements
        
        **Confidence Factors:**
        - Soil data completeness and recency
        - Regional data availability
        - Climate data quality
      parameters:
        - name: X-Region-Override
          in: header
          description: Override automatic region detection
          schema:
            type: string
            enum: [midwest, southeast, southwest, northwest, northeast]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CropSelectionRequest'
            examples:
              iowa_corn_farm:
                summary: Typical Iowa corn/soybean farm
                value:
                  farm_id: "farm_12345"
                  location:
                    latitude: 42.0308
                    longitude: -93.6319
                  soil_data:
                    ph: 6.2
                    organic_matter_percent: 3.8
                    phosphorus_ppm: 25
                    potassium_ppm: 180
                    test_date: "2024-03-15"
      responses:
        '200':
          description: Successful crop recommendations
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CropRecommendationResponse'
        '422':
          description: Invalid or insufficient agricultural data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgriculturalError'
```

This API design ensures that agricultural accuracy and farmer usability are prioritized while maintaining technical excellence and system reliability. All endpoints follow consistent patterns and provide comprehensive agricultural context for reliable decision-making.