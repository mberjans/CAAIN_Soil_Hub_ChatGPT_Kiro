# Cover Crop Selection Service

A comprehensive agricultural microservice for cover crop selection and recommendations, integrated with the CAAIN Soil Hub ecosystem.

## Overview

The Cover Crop Selection Service provides intelligent recommendations for cover crop species and mixtures based on:
- Soil conditions and health indicators
- Climate zone compatibility and weather patterns
- Farmer objectives and management goals
- Economic considerations and budget constraints
- Integration with existing crop rotation systems

## Features

### Core Functionality
- **Species Selection**: Intelligent matching of cover crop species to field conditions
- **Mixture Recommendations**: Custom cover crop mixtures for enhanced benefits
- **Climate Integration**: USDA Hardiness Zone and Köppen climate compatibility
- **Soil Analysis**: pH, drainage, texture, and fertility consideration
- **Seasonal Planning**: Season-specific planting and management recommendations

### Agricultural Focus Areas
- Nitrogen fixation and soil fertility improvement
- Erosion control and soil conservation
- Organic matter enhancement
- Soil compaction alleviation
- Weed suppression and pest management
- Nutrient scavenging and cycling

### API Endpoints

#### Main Selection Endpoint
- `POST /api/v1/cover-crops/select` - Comprehensive cover crop selection
- `POST /api/v1/cover-crops/seasonal` - Season-specific recommendations
- `POST /api/v1/cover-crops/soil-improvement` - Soil health focused selection
- `POST /api/v1/cover-crops/rotation` - Rotation integration optimization

#### Species Information
- `GET /api/v1/cover-crops/species` - Search and filter species database
- `GET /api/v1/cover-crops/species/{id}` - Detailed species information

#### Reference Data
- `GET /api/v1/cover-crops/types` - Available cover crop types
- `GET /api/v1/cover-crops/seasons` - Growing season options
- `GET /api/v1/cover-crops/benefits` - Soil benefit categories

## Installation

1. **Clone and navigate to service directory:**
   ```bash
   cd services/cover-crop-selection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the service:**
   ```bash
   python src/main.py
   ```

The service will start on port 8005 by default (configurable via `COVER_CROP_SERVICE_PORT`).

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COVER_CROP_SERVICE_PORT` | 8005 | Service port |
| `LOG_LEVEL` | INFO | Logging level |
| `DATA_INTEGRATION_URL` | http://localhost:8003 | Climate data service URL |
| `REDIS_URL` | redis://localhost:6379 | Redis cache URL (optional) |

### Service Dependencies

- **Data Integration Service**: For climate zone detection and weather data
- **Recommendation Engine**: For agricultural knowledge base integration
- **Redis**: For caching (optional)

## Usage Examples

### Basic Cover Crop Selection

```python
import httpx

request_data = {
    "request_id": "farm_123_field_5",
    "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    "soil_conditions": {
        "ph": 6.2,
        "organic_matter_percent": 2.8,
        "drainage_class": "moderately_well_drained",
        "test_date": "2024-03-15"
    },
    "objectives": {
        "primary_goals": ["nitrogen_fixation", "erosion_control"],
        "nitrogen_needs": True,
        "budget_per_acre": 75.0
    },
    "planting_window": {
        "start": "2024-09-15",
        "end": "2024-10-15"
    },
    "field_size_acres": 25.0
}

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8005/api/v1/cover-crops/select",
        json=request_data
    )
    recommendations = response.json()
```

### Species Lookup

```python
# Search for legume cover crops suitable for zone 7a
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8005/api/v1/cover-crops/species",
        params={
            "cover_crop_type": "legume",
            "hardiness_zone": "7a",
            "primary_benefit": "nitrogen_fixation"
        }
    )
    species_list = response.json()
```

### Seasonal Recommendations

```python
# Get winter cover crop recommendations for specific location
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8005/api/v1/cover-crops/seasonal",
        params={
            "latitude": 41.8781,
            "longitude": -87.6298,
            "target_season": "winter",
            "field_size_acres": 40.0
        }
    )
    seasonal_recs = response.json()
```

## Data Models

### Key Request/Response Models

- **CoverCropSelectionRequest**: Complete request with soil, climate, and objectives
- **CoverCropSelectionResponse**: Comprehensive recommendations with implementation guidance
- **CoverCropSpecies**: Detailed species information and requirements
- **SoilConditions**: Current field soil characteristics
- **CoverCropObjectives**: Farmer goals and priorities

### Cover Crop Types
- Legumes (nitrogen fixation)
- Grasses (biomass and erosion control)
- Brassicas (compaction relief and scavenging)
- Forbs (diversity and beneficial insects)
- Mixtures (combined benefits)

## Agricultural Knowledge Base

The service includes comprehensive agricultural data for:

### Species Database
- 50+ cover crop species with detailed characteristics
- Climate zone compatibility (USDA Hardiness Zones)
- Soil requirement specifications
- Agronomic management recommendations
- Economic cost estimates

### Soil Benefits
- Nitrogen fixation rates and potential
- Erosion control effectiveness
- Organic matter contribution
- Compaction alleviation capacity
- Nutrient scavenging capabilities

### Management Guidance
- Planting depth and seeding rates
- Establishment timelines and monitoring
- Termination method recommendations
- Integration with cash crop rotations

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/test_cover_crop_service.py

# Integration tests
pytest tests/test_api_endpoints.py

# All tests with coverage
pytest --cov=src tests/
```

## Integration with CAAIN Soil Hub

### Climate Zone Integration
- Automatic climate zone detection via coordinates
- Köppen climate classification compatibility
- Local weather pattern consideration

### Soil Data Integration
- pH and nutrient level analysis
- Drainage classification compatibility
- Soil texture and structure evaluation

### Recommendation Engine Integration
- Agricultural knowledge base access
- Expert-validated algorithms
- Economic analysis capabilities

## Agricultural Validation

All recommendations are based on:
- USDA NRCS Cover Crop Guidelines
- Regional Extension Service research
- SARE (Sustainable Agriculture Research and Education) findings
- Peer-reviewed agricultural publications
- Local farmer experience and feedback

## Monitoring and Health Checks

- Service health endpoint: `GET /health`
- Logging with structured output
- Integration monitoring with external services
- Agricultural validation checks

## Development

### Architecture
- FastAPI framework with async/await patterns
- Pydantic models for data validation
- Modular service design for extensibility
- Integration-ready for microservice ecosystem

### Contributing
1. Follow existing code patterns and style
2. Include comprehensive tests for new features
3. Update documentation for API changes
4. Validate agricultural accuracy with extension sources

## License

This service is part of the CAAIN Soil Hub project for agricultural technology advancement.

## Support

For technical support or agricultural questions:
- Review API documentation at `/docs`
- Check service health at `/health`
- Consult agricultural extension resources for local validation