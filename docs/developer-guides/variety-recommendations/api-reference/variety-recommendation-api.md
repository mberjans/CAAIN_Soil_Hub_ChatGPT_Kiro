# Variety Recommendation API Reference

## Overview

The Variety Recommendation API provides intelligent crop variety selection with regional adaptation analysis, performance prediction, and comparative evaluation. This API is part of the CAAIN Soil Hub's crop variety recommendations system.

## Base URL

```
http://localhost:8001/api/v1/varieties
```

## Authentication

All API endpoints require authentication using API keys or JWT tokens.

### Headers

```http
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

## Core Endpoints

### 1. Get Variety Recommendations

**Endpoint:** `POST /recommend`

Get advanced variety recommendations for a specific crop and regional context.

#### Request Body

```json
{
  "crop_id": "corn",
  "farm_data": {
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
  "user_preferences": {
    "yield_priority": "high",
    "disease_resistance_priority": "medium",
    "maturity_preference": "early",
    "seed_budget": 50000
  },
  "max_recommendations": 20
}
```

#### Response

```json
[
  {
    "id": "pioneer-1197",
    "name": "Pioneer P1197AM",
    "company": "Pioneer",
    "description": "High-yielding corn hybrid with excellent disease resistance and drought tolerance.",
    "yield_potential": "185 bu/acre",
    "maturity_days": 105,
    "confidence": 0.92,
    "suitability": "Excellent",
    "disease_resistance": "high",
    "traits": [
      {
        "name": "Drought Tolerance",
        "category": "resistance"
      },
      {
        "name": "High Yield",
        "category": "yield"
      },
      {
        "name": "Premium Quality",
        "category": "quality"
      }
    ],
    "regional_performance": {
      "yield_advantage": "+12%",
      "disease_rating": "Excellent",
      "stress_tolerance": "High"
    },
    "economic_analysis": {
      "seed_cost_per_acre": 85,
      "expected_roi": 1.8,
      "break_even_yield": 150
    }
  }
]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `crop_id` | string | Yes | Crop type (corn, soybean, wheat, etc.) |
| `farm_data` | object | Yes | Farm and field characteristics |
| `user_preferences` | object | No | User preferences and priorities |
| `max_recommendations` | integer | No | Maximum number of recommendations (default: 20) |

### 2. Compare Varieties

**Endpoint:** `POST /compare`

Compare multiple crop varieties side-by-side.

#### Request Body

```json
{
  "variety_ids": ["pioneer-1197", "dekalb-5678", "syngenta-1234"],
  "comparison_criteria": [
    "yield_potential",
    "disease_resistance",
    "maturity_days",
    "drought_tolerance"
  ],
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
  "comparison_id": "comp_12345",
  "varieties": [
    {
      "id": "pioneer-1197",
      "name": "Pioneer P1197AM",
      "scores": {
        "yield_potential": 9.2,
        "disease_resistance": 8.8,
        "maturity_days": 7.5,
        "drought_tolerance": 9.0
      },
      "rank": 1
    }
  ],
  "summary": {
    "best_overall": "pioneer-1197",
    "best_yield": "syngenta-1234",
    "best_disease_resistance": "pioneer-1197"
  }
}
```

### 3. Get Variety Details

**Endpoint:** `GET /{variety_id}/details`

Get detailed information about a specific variety.

#### Response

```json
{
  "id": "pioneer-1197",
  "name": "Pioneer P1197AM",
  "company": "Pioneer",
  "description": "High-yielding corn hybrid with excellent disease resistance and drought tolerance.",
  "characteristics": {
    "maturity_days": 105,
    "yield_potential": "185 bu/acre",
    "plant_height": "8.5 ft",
    "ear_height": "3.2 ft"
  },
  "disease_resistance": {
    "northern_corn_leaf_blight": "R",
    "gray_leaf_spot": "MR",
    "common_rust": "R",
    "anthracnose": "MR"
  },
  "traits": [
    {
      "name": "Drought Tolerance",
      "category": "resistance",
      "description": "Excellent drought tolerance with deep root system"
    }
  ],
  "regional_performance": {
    "corn_belt": {
      "yield_advantage": "+12%",
      "disease_rating": "Excellent",
      "stress_tolerance": "High"
    }
  },
  "economic_data": {
    "seed_cost_per_acre": 85,
    "expected_roi": 1.8,
    "break_even_yield": 150,
    "market_premium": 0.05
  }
}
```

### 4. Filter Varieties

**Endpoint:** `POST /filter`

Filter varieties based on specific criteria.

#### Request Body

```json
{
  "crop_id": "corn",
  "filters": {
    "maturity_range": {
      "min": 100,
      "max": 115
    },
    "yield_potential_min": 180,
    "disease_resistance": ["high", "medium"],
    "traits": ["drought_tolerance", "high_yield"],
    "price_range": {
      "min": 70,
      "max": 100
    }
  },
  "sort_by": "yield_potential",
  "sort_order": "desc"
}
```

#### Response

```json
{
  "filtered_varieties": [
    {
      "id": "pioneer-1197",
      "name": "Pioneer P1197AM",
      "match_score": 0.95,
      "filter_matches": {
        "maturity_range": true,
        "yield_potential_min": true,
        "disease_resistance": true,
        "traits": true,
        "price_range": true
      }
    }
  ],
  "total_matches": 15,
  "applied_filters": {
    "maturity_range": "100-115 days",
    "yield_potential_min": "180+ bu/acre",
    "disease_resistance": "high, medium",
    "traits": "drought_tolerance, high_yield",
    "price_range": "$70-$100/acre"
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters",
  "error_code": "INVALID_PARAMETERS",
  "field_errors": {
    "crop_id": "Invalid crop type",
    "farm_data.location": "Location data is required"
  }
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required",
  "error_code": "UNAUTHORIZED"
}
```

### 404 Not Found

```json
{
  "detail": "Variety not found",
  "error_code": "VARIETY_NOT_FOUND"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

## Rate Limiting

- **Rate Limit:** 100 requests per minute per API key
- **Headers:** 
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Pagination

For endpoints that return lists, pagination is supported:

### Request Parameters

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

### Response Headers

- `X-Total-Count`: Total number of items
- `X-Page-Count`: Total number of pages
- `X-Current-Page`: Current page number

## Data Models

### VarietyRecommendation

```typescript
interface VarietyRecommendation {
  id: string;
  name: string;
  company: string;
  description: string;
  yield_potential: string;
  maturity_days: number;
  confidence: number;
  suitability: string;
  disease_resistance: string;
  traits: Trait[];
  regional_performance: RegionalPerformance;
  economic_analysis: EconomicAnalysis;
}
```

### Trait

```typescript
interface Trait {
  name: string;
  category: string;
  description?: string;
}
```

### RegionalPerformance

```typescript
interface RegionalPerformance {
  yield_advantage: string;
  disease_rating: string;
  stress_tolerance: string;
}
```

### EconomicAnalysis

```typescript
interface EconomicAnalysis {
  seed_cost_per_acre: number;
  expected_roi: number;
  break_even_yield: number;
  market_premium?: number;
}
```

## SDK Examples

### Python

```python
import requests

# Get variety recommendations
response = requests.post(
    "http://localhost:8001/api/v1/varieties/recommend",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "crop_id": "corn",
        "farm_data": {
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "soil_data": {
                "ph": 6.5,
                "organic_matter_percent": 3.2
            }
        },
        "max_recommendations": 10
    }
)

recommendations = response.json()
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8001/api/v1/varieties/recommend', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    crop_id: 'corn',
    farm_data: {
      location: {
        latitude: 40.7128,
        longitude: -74.0060
      },
      soil_data: {
        ph: 6.5,
        organic_matter_percent: 3.2
      }
    },
    max_recommendations: 10
  })
});

const recommendations = await response.json();
```

## Testing

### Test Environment

- **Base URL:** `http://localhost:8001/api/v1/varieties`
- **Test API Key:** `test-api-key-12345`

### Sample Test Data

```json
{
  "test_farm_data": {
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
  }
}
```

## Changelog

### Version 1.2.0 (Current)
- Added economic analysis to recommendations
- Enhanced regional performance data
- Improved filtering capabilities

### Version 1.1.0
- Added variety comparison endpoint
- Enhanced trait information
- Improved disease resistance data

### Version 1.0.0
- Initial release
- Basic variety recommendations
- Core filtering functionality