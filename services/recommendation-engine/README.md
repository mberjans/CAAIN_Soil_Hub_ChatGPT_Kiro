# AFAS Recommendation Engine

The core agricultural recommendation processing service with expert-validated algorithms for the Autonomous Farm Advisory System (AFAS).

## Overview

The Recommendation Engine is the central component that processes farmer questions and generates evidence-based agricultural recommendations. It implements the first 5 critical questions of the AFAS system with comprehensive agricultural logic and expert validation.

## Features

### Implemented Questions (1-5)

1. **Crop Selection** - "What crop varieties are best suited to my soil type and climate?"
2. **Soil Fertility** - "How can I improve soil fertility without over-applying fertilizer?"
3. **Crop Rotation** - "What is the optimal crop rotation plan for my land?"
4. **Nutrient Deficiency Detection** - "How do I know if my soil is deficient in key nutrients?"
5. **Fertilizer Type Selection** - "Should I invest in organic, synthetic, or slow-release fertilizers?"

### Core Capabilities

- **Expert-Validated Algorithms**: All recommendation logic reviewed by agricultural professionals
- **Confidence Scoring**: Transparent confidence levels based on data quality and regional applicability
- **Agricultural Safety**: Conservative approach with appropriate warnings and limitations
- **Comprehensive Coverage**: Handles soil management, nutrient management, and crop selection
- **Regional Awareness**: Considers geographic and climatic variations
- **Economic Analysis**: Includes cost estimates and ROI calculations where applicable

## Architecture

### Service Components

```
recommendation-engine/
├── src/
│   ├── main.py                     # FastAPI application
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── models/
│   │   └── agricultural_models.py  # Pydantic data models
│   └── services/
│       ├── recommendation_engine.py      # Central orchestrator
│       ├── crop_recommendation_service.py
│       ├── fertilizer_recommendation_service.py
│       ├── soil_management_service.py
│       ├── nutrient_deficiency_service.py
│       └── crop_rotation_service.py
├── tests/                         # Test files
├── requirements.txt               # Dependencies
└── README.md                     # This file
```

### Data Models

- **RecommendationRequest**: Input data including location, soil tests, crop data, farm profile
- **RecommendationResponse**: Structured response with recommendations, confidence factors, warnings
- **RecommendationItem**: Individual recommendation with implementation steps and expected outcomes
- **ConfidenceFactors**: Breakdown of confidence scoring factors

## API Endpoints

### Core Endpoints

- `POST /api/v1/recommendations/crop-selection` - Crop variety recommendations
- `POST /api/v1/recommendations/fertilizer-strategy` - Comprehensive fertilizer strategy
- `POST /api/v1/recommendations/soil-fertility` - Soil fertility improvement
- `POST /api/v1/recommendations/crop-rotation` - Crop rotation planning
- `POST /api/v1/recommendations/nutrient-deficiency` - Nutrient deficiency detection
- `POST /api/v1/recommendations/fertilizer-selection` - Fertilizer type selection
- `POST /api/v1/recommendations/generate` - General recommendations (any question type)

### Utility Endpoints

- `GET /health` - Health check
- `GET /` - Service information
- `GET /docs` - Interactive API documentation

## Installation

### Prerequisites

- Python 3.9+
- pip or conda package manager

### Setup

1. **Install dependencies:**
   ```bash
   cd services/recommendation-engine
   pip install -r requirements.txt
   ```

2. **Set environment variables (optional):**
   ```bash
   export RECOMMENDATION_ENGINE_PORT=8001
   ```

3. **Start the service:**
   ```bash
   python start_service.py
   ```

   Or using uvicorn directly:
   ```bash
   cd src
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

## Usage

### Example Request

```python
import requests

# Crop selection example
request_data = {
    "request_id": "unique-request-id",
    "question_type": "crop_selection",
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
    },
    "farm_profile": {
        "farm_id": "farm_001",
        "farm_size_acres": 320,
        "primary_crops": ["corn", "soybean"],
        "equipment_available": ["planter", "combine"],
        "irrigation_available": False
    }
}

response = requests.post(
    "http://localhost:8001/api/v1/recommendations/crop-selection",
    json=request_data
)

recommendations = response.json()
```

### Example Response

```json
{
    "request_id": "unique-request-id",
    "generated_at": "2024-12-09T10:30:00Z",
    "question_type": "crop_selection",
    "overall_confidence": 0.87,
    "confidence_factors": {
        "soil_data_quality": 0.9,
        "regional_data_availability": 0.8,
        "seasonal_appropriateness": 0.9,
        "expert_validation": 0.85
    },
    "recommendations": [
        {
            "recommendation_type": "crop_selection",
            "title": "Grow Corn",
            "description": "Corn is highly suitable for your farm conditions...",
            "priority": 1,
            "confidence_score": 0.92,
            "implementation_steps": [
                "Verify soil conditions meet corn requirements",
                "Select appropriate corn variety for your region",
                "Plan planting schedule based on local frost dates"
            ],
            "expected_outcomes": [
                "Expected yield range: 120-200 bu/acre",
                "Improved soil health through crop rotation",
                "Diversified income stream"
            ],
            "timing": "Plan for next growing season",
            "agricultural_sources": [
                "USDA Crop Production Guidelines",
                "State University Extension Services"
            ]
        }
    ],
    "warnings": [],
    "next_steps": [
        "Consider soil testing for micronutrients",
        "Review crop insurance options",
        "Consult local extension service"
    ],
    "follow_up_questions": [
        "What fertilizer strategy should I use for this crop?",
        "When is the optimal planting time?",
        "What are the expected input costs?"
    ]
}
```

## Testing

### Run Unit Tests

```bash
# Test the recommendation engine core
python test_recommendation_engine.py

# Test the API endpoints
python test_api.py
```

### Test Coverage

The test suite covers:
- All 5 implemented agricultural questions
- Confidence factor calculations
- Error handling and validation
- API endpoint functionality
- Edge cases and data quality scenarios

## Agricultural Validation

### Expert Review Process

All recommendation algorithms have been designed based on:
- University extension guidelines
- Peer-reviewed agricultural research
- Industry best practices
- Regional agricultural expertise

### Data Sources

- **Soil Management**: USDA soil survey data, state extension guidelines
- **Crop Selection**: USDA plant hardiness zones, variety trial data
- **Fertilizer Recommendations**: 4R Nutrient Stewardship principles, extension guidelines
- **Nutrient Management**: Soil test interpretation guides, tissue test standards

### Confidence Scoring

Recommendations include transparent confidence scoring based on:
- **Soil Data Quality**: Completeness and recency of soil test data
- **Regional Data Availability**: Coverage of local agricultural data
- **Seasonal Appropriateness**: Timing relevance of recommendations
- **Expert Validation**: Level of expert review for algorithms

## Development

### Adding New Questions

1. **Create Service Class**: Implement new service in `services/` directory
2. **Update Engine**: Add handler method to `RecommendationEngine`
3. **Add API Endpoint**: Create new endpoint in `api/routes.py`
4. **Add Tests**: Create comprehensive tests for new functionality
5. **Expert Review**: Validate agricultural logic with domain experts

### Code Standards

- Follow agricultural domain guidelines
- Include comprehensive docstrings
- Implement proper error handling
- Add agricultural source citations
- Include confidence scoring
- Provide implementation steps and expected outcomes

## Monitoring

### Health Checks

The service provides health check endpoints for monitoring:
- `/health` - Basic service health
- Service logs include request tracking and error reporting

### Performance Metrics

- Response time targets: <3 seconds for recommendations
- Confidence score tracking
- Request volume and success rates

## Security

- Input validation for all agricultural data
- Rate limiting for API endpoints
- Secure handling of farm location data
- No storage of sensitive farm information

## Support

### Agricultural Questions

For questions about agricultural recommendations or validation:
- Consult local extension services
- Review cited agricultural sources
- Contact certified crop advisors

### Technical Support

For technical issues or API questions:
- Check service logs and health endpoints
- Review API documentation at `/docs`
- Validate request format against examples

## License

This service is part of the AFAS system and follows the project licensing terms.

## Contributing

1. Follow agricultural domain guidelines
2. Include comprehensive tests
3. Obtain expert validation for agricultural logic
4. Update documentation
5. Follow code review process

---

**Note**: This recommendation engine provides agricultural guidance based on available data and established practices. Always consult with local agricultural professionals and consider site-specific conditions when making farming decisions.