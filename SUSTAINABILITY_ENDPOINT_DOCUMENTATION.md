# Sustainability Score Endpoint Implementation

## Overview

The `POST /api/v1/rotations/sustainability-score` endpoint has been successfully implemented to provide comprehensive sustainability metrics for crop rotation sequences. This endpoint analyzes environmental impact, soil health, carbon sequestration, water efficiency, biodiversity, and long-term viability of rotation plans.

## Endpoint Details

**URL:** `POST /api/v1/rotations/sustainability-score`

**Parameters:**
- `field_id` (string, required): Unique identifier for the field
- `rotation_sequence` (List[str], required): Array of crop names in rotation order

**Response Format:**
```json
{
  "field_id": "string",
  "rotation_sequence": ["crop1", "crop2", "crop3"],
  "sustainability_scores": {
    "environmental_impact": 0-100,
    "soil_health": 0-100,
    "carbon_sequestration": 0-100,
    "water_efficiency": 0-100,
    "biodiversity": 0-100,
    "long_term_viability": 0-100
  },
  "overall_sustainability_score": 0-100,
  "sustainability_grade": "A-F",
  "recommendations": ["improvement suggestions"],
  "analysis_details": {
    "crop_diversity_index": 0-100,
    "nitrogen_fixation_lbs_per_acre": 0-200,
    "carbon_sequestration_tons": 0-10,
    "erosion_reduction_percent": 0-100,
    "water_use_efficiency_score": 0-100,
    "soil_health_trajectory": [50, 55, 60, 65],
    "unique_crops_count": 2-6,
    "rotation_length_years": 2-10,
    "has_nitrogen_fixing_crops": true/false
  },
  "sustainability_insights": [
    "Key insights about rotation sustainability"
  ]
}
```

## Implementation Features

### 1. Comprehensive Sustainability Analysis
- **Environmental Impact**: Evaluates nitrogen leaching and soil erosion risks
- **Soil Health**: Assesses organic matter improvement and nutrient cycling
- **Carbon Sequestration**: Calculates CO2 capture potential
- **Water Efficiency**: Measures water use optimization
- **Biodiversity**: Evaluates crop diversity and habitat support
- **Long-term Viability**: Assesses economic and environmental sustainability

### 2. Intelligent Scoring System
- All scores normalized to 0-100 scale for consistency
- Weighted calculations based on agricultural research
- Grade assignment (A-F) based on overall performance
- Comparative analysis across multiple metrics

### 3. Smart Recommendations Engine
- Context-aware suggestions based on score weaknesses
- Crop-specific recommendations for improvement
- Diversity and balance optimization advice
- Nitrogen fixation and soil health enhancement tips

### 4. Agricultural Science Integration
- Based on established crop compatibility matrices
- Incorporates nitrogen fixation rates for legumes
- Uses water use efficiency data by crop type
- Applies carbon sequestration research findings

## Sustainability Metrics Details

### Environmental Impact (0-100)
Calculated from:
- Soil erosion factors by crop
- Nitrogen leaching risk assessment
- Input intensity requirements
- Environmental protection potential

### Soil Health (0-100)
Based on:
- Organic matter contribution
- Nitrogen fixation from legumes
- Soil structure improvement
- Long-term fertility enhancement

### Carbon Sequestration (0-100)
Derived from:
- Crop-specific carbon capture rates
- Root biomass contribution
- Soil organic carbon increase
- Long-term carbon storage potential

### Water Efficiency (0-100)
Measured by:
- Crop water use efficiency ratings
- Drought tolerance factors
- Irrigation requirements
- Water conservation potential

### Biodiversity (0-100)
Evaluated through:
- Shannon diversity index calculation
- Crop family diversification
- Habitat support for beneficial insects
- Pollinator-friendly crop inclusion

### Long-term Viability (0-100)
Assessed via:
- Economic sustainability balance
- Soil health trajectory analysis
- Risk diversification benefits
- Climate resilience factors

## Usage Examples

### Basic API Call
```bash
curl -X POST "http://localhost:8000/api/v1/rotations/sustainability-score" \
     -G -d "field_id=field_001" \
     -d "rotation_sequence=corn" \
     -d "rotation_sequence=soybean" \
     -d "rotation_sequence=wheat"
```

### Python Request Example
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/rotations/sustainability-score",
    params={
        "field_id": "field_001",
        "rotation_sequence": ["corn", "soybean", "wheat", "oats"]
    }
)

data = response.json()
print(f"Overall Score: {data['overall_sustainability_score']}")
print(f"Grade: {data['sustainability_grade']}")
```

### JavaScript/TypeScript Example
```typescript
const response = await fetch('/api/v1/rotations/sustainability-score?' + 
  new URLSearchParams({
    field_id: 'field_001',
    rotation_sequence: ['corn', 'soybean', 'wheat']
  }), {
  method: 'POST'
});

const data = await response.json();
console.log('Sustainability Analysis:', data);
```

## Error Handling

The endpoint includes comprehensive error handling:

- **400 Bad Request**: Invalid or empty rotation sequence
- **404 Not Found**: Field ID not found in system
- **500 Internal Server Error**: Analysis calculation failures

## Recommendations Logic

The system generates targeted recommendations based on:

1. **Score Thresholds**: Suggestions triggered when specific scores fall below 70
2. **Crop Diversity**: Recommendations for rotations with <3 unique crops
3. **Nitrogen Fixation**: Suggestions when no legumes are present
4. **Balance Optimization**: Advice for improving weak sustainability areas

## Integration with Existing Services

The endpoint integrates with:
- **RotationAnalysisService**: Core sustainability calculations
- **FieldHistoryService**: Field profile and characteristics
- **RotationOptimizationEngine**: Yield estimation and crop compatibility

## Testing

Run the test suite:
```bash
# Unit tests
python test_sustainability_endpoint.py

# API integration tests  
python test_sustainability_api.py
```

## Performance Considerations

- Response time: Typically <2 seconds for standard rotations
- Caching: Field profile data cached for session duration
- Scalability: Designed for concurrent requests
- Memory usage: Minimal footprint with efficient calculations

## Future Enhancements

Planned improvements:
1. Real-time weather data integration
2. Regional sustainability factor adjustments
3. Climate change impact projections
4. Economic sustainability weighting options
5. Custom sustainability goal targeting

## Code Location

- **Main Implementation**: `services/recommendation-engine/src/api/rotation_routes.py`
- **Analysis Service**: `services/recommendation-engine/src/services/rotation_analysis_service.py`
- **Models**: `services/recommendation-engine/src/models/rotation_models.py`

## Maintenance Notes

- Update sustainability factors annually based on research
- Review recommendation thresholds based on user feedback
- Monitor API performance and optimize calculations as needed
- Keep crop compatibility matrices current with agricultural best practices