# Filtering API Reference

## Overview

The Filtering API provides advanced filtering capabilities for crop varieties based on multiple criteria including agronomic traits, economic factors, and regional performance.

## Base URL

```
http://localhost:8001/api/v1/varieties/filter
```

## Authentication

All endpoints require authentication using API keys or JWT tokens.

### Headers

```http
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

## Core Endpoints

### 1. Advanced Variety Filtering

**Endpoint:** `POST /advanced`

Advanced filtering with multiple criteria and intelligent matching.

#### Request Body

```json
{
  "crop_id": "corn",
  "filters": {
    "maturity_range": {
      "min": 100,
      "max": 115
    },
    "yield_potential": {
      "min": 180,
      "unit": "bu/acre"
    },
    "disease_resistance": {
      "levels": ["high", "medium"],
      "diseases": ["northern_corn_leaf_blight", "gray_leaf_spot"]
    },
    "traits": {
      "required": ["drought_tolerance"],
      "preferred": ["high_yield", "premium_quality"]
    },
    "economic_factors": {
      "seed_cost_range": {
        "min": 70,
        "max": 100,
        "unit": "dollars_per_acre"
      },
      "roi_threshold": 1.5
    },
    "regional_adaptation": {
      "climate_zones": ["6a", "6b", "7a"],
      "soil_types": ["clay_loam", "silt_loam"],
      "irrigation_required": false
    }
  },
  "sorting": {
    "primary": "yield_potential",
    "secondary": "disease_resistance",
    "order": "desc"
  },
  "pagination": {
    "page": 1,
    "limit": 20
  }
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
        "yield_potential": true,
        "disease_resistance": true,
        "traits": {
          "required": true,
          "preferred": 2
        },
        "economic_factors": true,
        "regional_adaptation": true
      },
      "scores": {
        "yield_potential": 9.2,
        "disease_resistance": 8.8,
        "economic_value": 8.5,
        "regional_fit": 9.0
      },
      "summary": "Excellent match for your criteria with high yield potential and strong disease resistance"
    }
  ],
  "filter_summary": {
    "total_varieties_searched": 150,
    "total_matches": 15,
    "applied_filters": {
      "maturity_range": "100-115 days",
      "yield_potential": "180+ bu/acre",
      "disease_resistance": "high, medium",
      "traits": "drought_tolerance (required), high_yield, premium_quality (preferred)",
      "economic_factors": "$70-$100/acre seed cost, 1.5+ ROI",
      "regional_adaptation": "Climate zones 6a-7a, clay/silt loam soils"
    },
    "filter_effectiveness": {
      "most_restrictive": "disease_resistance",
      "least_restrictive": "maturity_range",
      "recommendation": "Consider relaxing disease resistance requirements for more options"
    }
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 15,
    "items_per_page": 20
  }
}
```

### 2. Smart Filter Suggestions

**Endpoint:** `POST /suggestions`

Get intelligent filter suggestions based on farm context and user preferences.

#### Request Body

```json
{
  "crop_id": "corn",
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
    "irrigation_available": true,
    "previous_crop": "soybean"
  },
  "user_preferences": {
    "yield_priority": "high",
    "disease_concerns": ["northern_corn_leaf_blight", "gray_leaf_spot"],
    "budget_constraints": {
      "max_seed_cost_per_acre": 90
    },
    "management_preferences": {
      "prefers_early_maturity": true,
      "wants_drought_tolerance": true
    }
  }
}
```

#### Response

```json
{
  "suggested_filters": {
    "maturity_range": {
      "min": 100,
      "max": 110,
      "reason": "Early maturity preferred for your region and management style"
    },
    "yield_potential": {
      "min": 185,
      "reason": "High yield priority with good soil conditions"
    },
    "disease_resistance": {
      "levels": ["high"],
      "diseases": ["northern_corn_leaf_blight", "gray_leaf_spot"],
      "reason": "Based on your disease concerns and regional risk"
    },
    "traits": {
      "required": ["drought_tolerance"],
      "preferred": ["high_yield", "early_maturity"],
      "reason": "Matches your management preferences and regional conditions"
    },
    "economic_factors": {
      "seed_cost_range": {
        "max": 90,
        "reason": "Within your budget constraints"
      }
    }
  },
  "alternative_filters": [
    {
      "name": "Balanced Approach",
      "description": "Moderate yield with strong disease resistance",
      "filters": {
        "yield_potential": {"min": 175},
        "disease_resistance": {"levels": ["high", "medium"]}
      }
    },
    {
      "name": "Premium Performance",
      "description": "Maximum yield potential with premium traits",
      "filters": {
        "yield_potential": {"min": 190},
        "traits": {"required": ["high_yield", "premium_quality"]}
      }
    }
  ]
}
```

### 3. Filter Analytics

**Endpoint:** `GET /analytics`

Get analytics about filter usage and effectiveness.

#### Query Parameters

- `crop_id`: Crop type to analyze
- `time_range`: Time range for analytics (7d, 30d, 90d)
- `region`: Geographic region for analysis

#### Response

```json
{
  "filter_usage_stats": {
    "most_used_filters": [
      {
        "filter_name": "yield_potential",
        "usage_count": 1250,
        "usage_percentage": 85.2
      },
      {
        "filter_name": "disease_resistance",
        "usage_count": 980,
        "usage_percentage": 66.8
      }
    ],
    "filter_combinations": [
      {
        "combination": ["yield_potential", "disease_resistance", "maturity_range"],
        "usage_count": 450,
        "success_rate": 0.78
      }
    ]
  },
  "filter_effectiveness": {
    "high_success_filters": [
      {
        "filter_name": "regional_adaptation",
        "success_rate": 0.92,
        "user_satisfaction": 4.7
      }
    ],
    "low_success_filters": [
      {
        "filter_name": "price_range",
        "success_rate": 0.45,
        "user_satisfaction": 3.2,
        "recommendation": "Consider expanding price ranges or providing more flexible options"
      }
    ]
  },
  "regional_patterns": {
    "climate_zone_6a": {
      "preferred_maturity_range": "105-115 days",
      "common_disease_concerns": ["northern_corn_leaf_blight", "gray_leaf_spot"],
      "typical_yield_expectations": "180-200 bu/acre"
    }
  }
}
```

### 4. Save Filter Presets

**Endpoint:** `POST /presets`

Save commonly used filter combinations for quick access.

#### Request Body

```json
{
  "preset_name": "High Yield Corn - Zone 6a",
  "description": "Filters for high-yielding corn varieties in climate zone 6a",
  "crop_id": "corn",
  "filters": {
    "maturity_range": {"min": 105, "max": 115},
    "yield_potential": {"min": 185},
    "disease_resistance": {"levels": ["high"]},
    "regional_adaptation": {"climate_zones": ["6a"]}
  },
  "is_public": false
}
```

#### Response

```json
{
  "preset_id": "preset_12345",
  "preset_name": "High Yield Corn - Zone 6a",
  "created_at": "2024-01-15T10:30:00Z",
  "usage_count": 0,
  "share_url": "https://api.example.com/varieties/filter/presets/preset_12345"
}
```

### 5. Load Filter Presets

**Endpoint:** `GET /presets`

Get saved filter presets.

#### Query Parameters

- `user_id`: User ID (for private presets)
- `crop_id`: Filter by crop type
- `is_public`: Include public presets (true/false)

#### Response

```json
{
  "presets": [
    {
      "preset_id": "preset_12345",
      "preset_name": "High Yield Corn - Zone 6a",
      "description": "Filters for high-yielding corn varieties in climate zone 6a",
      "crop_id": "corn",
      "created_at": "2024-01-15T10:30:00Z",
      "usage_count": 15,
      "is_public": false,
      "created_by": "user_123"
    }
  ],
  "total_presets": 5
}
```

## Filter Types

### Maturity Range Filter

```json
{
  "maturity_range": {
    "min": 100,
    "max": 115,
    "unit": "days"
  }
}
```

### Yield Potential Filter

```json
{
  "yield_potential": {
    "min": 180,
    "max": 220,
    "unit": "bu/acre"
  }
}
```

### Disease Resistance Filter

```json
{
  "disease_resistance": {
    "levels": ["high", "medium"],
    "diseases": ["northern_corn_leaf_blight", "gray_leaf_spot", "common_rust"],
    "minimum_level": "medium"
  }
}
```

### Trait Filter

```json
{
  "traits": {
    "required": ["drought_tolerance"],
    "preferred": ["high_yield", "premium_quality"],
    "excluded": ["late_maturity"]
  }
}
```

### Economic Factors Filter

```json
{
  "economic_factors": {
    "seed_cost_range": {
      "min": 70,
      "max": 100,
      "unit": "dollars_per_acre"
    },
    "roi_threshold": 1.5,
    "break_even_yield": 150
  }
}
```

### Regional Adaptation Filter

```json
{
  "regional_adaptation": {
    "climate_zones": ["6a", "6b", "7a"],
    "soil_types": ["clay_loam", "silt_loam"],
    "irrigation_required": false,
    "drainage_preference": "well_drained"
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid filter parameters",
  "error_code": "INVALID_FILTERS",
  "field_errors": {
    "maturity_range.min": "Minimum maturity must be greater than 0",
    "yield_potential.min": "Minimum yield must be realistic for crop type"
  }
}
```

### 422 Unprocessable Entity

```json
{
  "detail": "Filter combination results in no matches",
  "error_code": "NO_MATCHES",
  "suggestions": [
    "Consider relaxing yield_potential minimum",
    "Expand maturity range by 5-10 days",
    "Include medium disease resistance levels"
  ]
}
```

## Rate Limiting

- **Rate Limit:** 200 requests per minute per API key
- **Headers:** 
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## SDK Examples

### Python

```python
import requests

# Advanced filtering
response = requests.post(
    "http://localhost:8001/api/v1/varieties/filter/advanced",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "crop_id": "corn",
        "filters": {
            "maturity_range": {"min": 100, "max": 115},
            "yield_potential": {"min": 180},
            "disease_resistance": {"levels": ["high", "medium"]}
        },
        "sorting": {"primary": "yield_potential", "order": "desc"}
    }
)

filtered_varieties = response.json()
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8001/api/v1/varieties/filter/advanced', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    crop_id: 'corn',
    filters: {
      maturity_range: { min: 100, max: 115 },
      yield_potential: { min: 180 },
      disease_resistance: { levels: ['high', 'medium'] }
    },
    sorting: { primary: 'yield_potential', order: 'desc' }
  })
});

const filteredVarieties = await response.json();
```

## Testing

### Test Environment

- **Base URL:** `http://localhost:8001/api/v1/varieties/filter`
- **Test API Key:** `test-api-key-12345`

### Sample Test Data

```json
{
  "test_filters": {
    "maturity_range": {"min": 100, "max": 115},
    "yield_potential": {"min": 180},
    "disease_resistance": {"levels": ["high"]},
    "traits": {"required": ["drought_tolerance"]}
  }
}
```

## Changelog

### Version 1.3.0 (Current)
- Added smart filter suggestions
- Enhanced filter analytics
- Improved preset management

### Version 1.2.0
- Added economic factors filtering
- Enhanced regional adaptation filters
- Improved filter effectiveness metrics

### Version 1.1.0
- Added filter presets
- Enhanced trait filtering
- Improved disease resistance filtering

### Version 1.0.0
- Initial release
- Basic filtering capabilities
- Core filter types