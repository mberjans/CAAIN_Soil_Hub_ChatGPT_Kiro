# Comparison API Reference

## Overview

The Comparison API provides comprehensive side-by-side comparison capabilities for crop varieties, enabling detailed analysis of traits, performance, and economic factors.

## Base URL

```
http://localhost:8001/api/v1/varieties/compare
```

## Authentication

All endpoints require authentication using API keys or JWT tokens.

### Headers

```http
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

## Core Endpoints

### 1. Compare Varieties

**Endpoint:** `POST /`

Compare multiple crop varieties side-by-side with detailed analysis.

#### Request Body

```json
{
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "comparison_criteria": [
    "yield_potential",
    "disease_resistance",
    "maturity_days",
    "drought_tolerance",
    "economic_value"
  ],
  "farm_context": {
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "climate_zone": "6a"
    },
    "soil_data": {
      "ph": 6.5,
      "organic_matter_percent": 3.2,
      "drainage": "well_drained",
      "soil_type": "clay_loam"
    },
    "field_size_acres": 100,
    "irrigation_available": true
  },
  "analysis_options": {
    "include_economic_analysis": true,
    "include_regional_performance": true,
    "include_risk_assessment": true,
    "include_recommendation": true
  }
}
```

#### Response

```json
{
  "comparison_id": "comp_12345",
  "varieties": [
    {
      "id": "pioneer-1197",
      "name": "Pioneer P1197AM",
      "company": "Pioneer",
      "scores": {
        "yield_potential": 9.2,
        "disease_resistance": 8.8,
        "maturity_days": 7.5,
        "drought_tolerance": 9.0,
        "economic_value": 8.5
      },
      "rank": 1,
      "detailed_analysis": {
        "yield_potential": {
          "score": 9.2,
          "value": "185 bu/acre",
          "advantage": "+12% vs average",
          "confidence": "high"
        },
        "disease_resistance": {
          "score": 8.8,
          "resistance_levels": {
            "northern_corn_leaf_blight": "R",
            "gray_leaf_spot": "MR",
            "common_rust": "R"
          },
          "advantage": "Excellent disease package"
        }
      },
      "economic_analysis": {
        "seed_cost_per_acre": 85,
        "expected_roi": 1.8,
        "break_even_yield": 150,
        "total_field_cost": 8500,
        "expected_revenue": 15300
      },
      "regional_performance": {
        "climate_zone_6a": {
          "yield_advantage": "+12%",
          "disease_rating": "Excellent",
          "stress_tolerance": "High"
        }
      },
      "risk_assessment": {
        "overall_risk": "Low",
        "risk_factors": [],
        "mitigation_strategies": []
      }
    }
  ],
  "comparison_summary": {
    "best_overall": "pioneer-1197",
    "best_yield": "syngenta-1234",
    "best_disease_resistance": "pioneer-1197",
    "best_economic_value": "dekalb-5678",
    "most_balanced": "pioneer-1197"
  },
  "detailed_comparison": {
    "yield_potential": {
      "winner": "syngenta-1234",
      "range": "180-190 bu/acre",
      "difference": "5 bu/acre between highest and lowest"
    },
    "disease_resistance": {
      "winner": "pioneer-1197",
      "summary": "All varieties have good resistance, Pioneer has best overall package"
    },
    "economic_value": {
      "winner": "dekalb-5678",
      "roi_range": "1.5-1.8",
      "cost_difference": "$15/acre between highest and lowest"
    }
  },
  "recommendation": {
    "primary_recommendation": "pioneer-1197",
    "reasoning": "Best overall balance of yield, disease resistance, and economic value",
    "alternative_options": [
      {
        "variety": "syngenta-1234",
        "reason": "If maximum yield is the priority"
      },
      {
        "variety": "dekalb-5678",
        "reason": "If cost optimization is the priority"
      }
    ],
    "considerations": [
      "All varieties are well-suited for your climate zone",
      "Consider disease pressure in your area when choosing",
      "Evaluate your risk tolerance for yield vs cost"
    ]
  }
}
```

### 2. Compare by Criteria

**Endpoint:** `POST /criteria`

Compare varieties based on specific criteria with weighted scoring.

#### Request Body

```json
{
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "criteria_weights": {
    "yield_potential": 0.4,
    "disease_resistance": 0.3,
    "economic_value": 0.2,
    "drought_tolerance": 0.1
  },
  "farm_context": {
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "soil_type": "clay_loam",
    "irrigation_available": true
  }
}
```

#### Response

```json
{
  "weighted_comparison": {
    "varieties": [
      {
        "id": "pioneer-1197",
        "name": "Pioneer P1197AM",
        "weighted_score": 8.7,
        "rank": 1,
        "criteria_scores": {
          "yield_potential": 9.2,
          "disease_resistance": 8.8,
          "economic_value": 8.5,
          "drought_tolerance": 9.0
        },
        "weighted_contributions": {
          "yield_potential": 3.68,
          "disease_resistance": 2.64,
          "economic_value": 1.70,
          "drought_tolerance": 0.90
        }
      }
    ],
    "criteria_analysis": {
      "yield_potential": {
        "weight": 0.4,
        "impact": "High - Primary driver of overall score",
        "variety_performance": {
          "pioneer-1197": 9.2,
          "dekalb-5678": 8.5,
          "syngenta-1234": 9.5
        }
      }
    }
  }
}
```

### 3. Matrix Comparison

**Endpoint:** `POST /matrix`

Generate a comparison matrix for multiple varieties and criteria.

#### Request Body

```json
{
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "criteria": [
    "yield_potential",
    "disease_resistance",
    "maturity_days",
    "drought_tolerance",
    "economic_value",
    "seed_cost"
  ],
  "format": "matrix"
}
```

#### Response

```json
{
  "comparison_matrix": {
    "varieties": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
    "criteria": [
      "yield_potential",
      "disease_resistance",
      "maturity_days",
      "drought_tolerance",
      "economic_value",
      "seed_cost"
    ],
    "matrix": [
      [9.2, 8.8, 7.5, 9.0, 8.5, 8.5],
      [8.5, 7.8, 8.0, 7.5, 9.0, 9.0],
      [9.5, 8.2, 6.5, 8.0, 7.8, 7.0]
    ],
    "best_performers": {
      "yield_potential": "syngenta-1234",
      "disease_resistance": "pioneer-1197",
      "maturity_days": "dekalb-5678",
      "drought_tolerance": "pioneer-1197",
      "economic_value": "dekalb-5678",
      "seed_cost": "dekalb-5678"
    },
    "performance_summary": {
      "pioneer-1197": {
        "wins": 2,
        "average_score": 8.58,
        "strengths": ["drought_tolerance", "disease_resistance"],
        "weaknesses": ["maturity_days"]
      }
    }
  }
}
```

### 4. Save Comparison

**Endpoint:** `POST /save`

Save a comparison for future reference or sharing.

#### Request Body

```json
{
  "comparison_id": "comp_12345",
  "name": "Corn Variety Comparison - Zone 6a",
  "description": "Comparison of top corn varieties for climate zone 6a",
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "is_public": false,
  "tags": ["corn", "zone-6a", "high-yield"]
}
```

#### Response

```json
{
  "saved_comparison_id": "saved_comp_67890",
  "comparison_id": "comp_12345",
  "name": "Corn Variety Comparison - Zone 6a",
  "created_at": "2024-01-15T10:30:00Z",
  "share_url": "https://api.example.com/varieties/compare/saved/saved_comp_67890",
  "access_level": "private"
}
```

### 5. Load Saved Comparison

**Endpoint:** `GET /saved/{saved_comparison_id}`

Load a previously saved comparison.

#### Response

```json
{
  "saved_comparison_id": "saved_comp_67890",
  "name": "Corn Variety Comparison - Zone 6a",
  "description": "Comparison of top corn varieties for climate zone 6a",
  "created_at": "2024-01-15T10:30:00Z",
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "comparison_data": {
    "varieties": [
      {
        "id": "pioneer-1197",
        "name": "Pioneer P1197AM",
        "scores": {
          "yield_potential": 9.2,
          "disease_resistance": 8.8,
          "maturity_days": 7.5,
          "drought_tolerance": 9.0,
          "economic_value": 8.5
        },
        "rank": 1
      }
    ],
    "comparison_summary": {
      "best_overall": "pioneer-1197",
      "best_yield": "syngenta-1234",
      "best_disease_resistance": "pioneer-1197"
    }
  },
  "tags": ["corn", "zone-6a", "high-yield"],
  "access_level": "private"
}
```

## Comparison Criteria

### Yield Potential

```json
{
  "yield_potential": {
    "score": 9.2,
    "value": "185 bu/acre",
    "advantage": "+12% vs average",
    "confidence": "high",
    "factors": [
      "genetic potential",
      "regional adaptation",
      "soil suitability"
    ]
  }
}
```

### Disease Resistance

```json
{
  "disease_resistance": {
    "score": 8.8,
    "resistance_levels": {
      "northern_corn_leaf_blight": "R",
      "gray_leaf_spot": "MR",
      "common_rust": "R",
      "anthracnose": "MR"
    },
    "advantage": "Excellent disease package",
    "risk_reduction": "High"
  }
}
```

### Economic Value

```json
{
  "economic_value": {
    "score": 8.5,
    "seed_cost_per_acre": 85,
    "expected_roi": 1.8,
    "break_even_yield": 150,
    "total_field_cost": 8500,
    "expected_revenue": 15300,
    "net_profit": 6800
  }
}
```

### Maturity Days

```json
{
  "maturity_days": {
    "score": 7.5,
    "value": 105,
    "advantage": "Early maturity for double cropping",
    "risk_factors": ["frost risk", "harvest timing"]
  }
}
```

### Drought Tolerance

```json
{
  "drought_tolerance": {
    "score": 9.0,
    "level": "High",
    "advantage": "Excellent drought tolerance",
    "benefits": [
      "Reduced irrigation needs",
      "Better performance in dry years",
      "Lower water stress risk"
    ]
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid comparison request",
  "error_code": "INVALID_COMPARISON",
  "field_errors": {
    "variety_ids": "At least 2 varieties required for comparison",
    "comparison_criteria": "At least 1 criterion required"
  }
}
```

### 404 Not Found

```json
{
  "detail": "Variety not found",
  "error_code": "VARIETY_NOT_FOUND",
  "variety_id": "invalid-variety-id"
}
```

### 422 Unprocessable Entity

```json
{
  "detail": "Cannot compare varieties from different crops",
  "error_code": "INCOMPATIBLE_VARIETIES",
  "crop_types": ["corn", "soybean"]
}
```

## Rate Limiting

- **Rate Limit:** 50 requests per minute per API key
- **Headers:** 
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## SDK Examples

### Python

```python
import requests

# Compare varieties
response = requests.post(
    "http://localhost:8001/api/v1/varieties/compare/",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
        "comparison_criteria": [
            "yield_potential",
            "disease_resistance",
            "economic_value"
        ],
        "farm_context": {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }
    }
)

comparison = response.json()
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8001/api/v1/varieties/compare/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    variety_ids: ['pioneer-1197', 'dekalb-5678', 'syngenta-1234'],
    comparison_criteria: [
      'yield_potential',
      'disease_resistance',
      'economic_value'
    ],
    farm_context: {
      location: {
        latitude: 40.7128,
        longitude: -74.0060
      }
    }
  })
});

const comparison = await response.json();
```

## Testing

### Test Environment

- **Base URL:** `http://localhost:8001/api/v1/varieties/compare`
- **Test API Key:** `test-api-key-12345`

### Sample Test Data

```json
{
  "test_variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "test_criteria": [
    "yield_potential",
    "disease_resistance",
    "economic_value"
  ]
}
```

## Changelog

### Version 1.2.0 (Current)
- Added matrix comparison format
- Enhanced economic analysis
- Improved risk assessment

### Version 1.1.0
- Added weighted comparison
- Enhanced saved comparisons
- Improved recommendation engine

### Version 1.0.0
- Initial release
- Basic variety comparison
- Core comparison criteria