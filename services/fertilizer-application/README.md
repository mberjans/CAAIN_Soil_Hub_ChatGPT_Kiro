# AFAS Fertilizer Application Service

A comprehensive microservice for fertilizer application method selection, equipment assessment, cost analysis, and application guidance.

## Overview

The Fertilizer Application Service provides intelligent recommendations for fertilizer application methods based on field conditions, crop requirements, available equipment, and economic considerations. It helps farmers optimize their fertilizer application practices for maximum efficiency and minimal environmental impact.

## Features

### Application Method Selection
- **Method Analysis**: Evaluates multiple application methods (broadcast, band, sidedress, foliar, injection, drip)
- **Equipment Compatibility**: Assesses equipment compatibility with different methods
- **Efficiency Scoring**: Provides efficiency ratings and optimization recommendations
- **Cost Analysis**: Comprehensive cost breakdown including fertilizer, equipment, labor, and fuel costs

### Equipment Assessment
- **Farm Equipment Evaluation**: Comprehensive assessment of current equipment inventory
- **Capacity Analysis**: Evaluates equipment capacity adequacy for farm operations
- **Upgrade Recommendations**: Identifies equipment upgrade opportunities and priorities
- **Maintenance Planning**: Provides maintenance requirements and scheduling recommendations

### Cost Analysis
- **Multi-factor Cost Analysis**: Analyzes fertilizer, equipment, labor, fuel, and maintenance costs
- **ROI Analysis**: Calculates return on investment and payback periods
- **Sensitivity Analysis**: Evaluates cost sensitivity to various factors
- **Optimization Recommendations**: Provides cost optimization strategies

### Application Guidance
- **Step-by-step Instructions**: Detailed application procedures for each method
- **Safety Guidelines**: Comprehensive safety precautions and PPE requirements
- **Calibration Procedures**: Equipment calibration instructions and verification steps
- **Weather Advisories**: Weather-based application recommendations
- **Troubleshooting**: Common issues and solutions for each application method

## API Endpoints

### Application Routes (`/api/v1/application`)
- `POST /select-methods` - Select optimal application methods
- `POST /analyze-costs` - Analyze costs for different methods
- `GET /methods` - Get available application methods
- `POST /validate-request` - Validate application request parameters

### Method Routes (`/api/v1/methods`)
- `GET /` - Get all application methods with filtering
- `GET /{method_id}` - Get specific method details
- `POST /compare` - Compare two application methods
- `POST /optimize` - Optimize method selection
- `POST /rank` - Rank methods by criteria
- `POST /validate/{method_id}` - Validate method for conditions

### Guidance Routes (`/api/v1/guidance`)
- `POST /application-guidance` - Get comprehensive application guidance
- `GET /best-practices/{method_type}` - Get method-specific best practices
- `GET /safety-guidelines/{method_type}` - Get safety guidelines
- `GET /calibration-guide/{method_type}` - Get calibration procedures
- `GET /weather-advisories` - Get weather-based advisories
- `GET /timing-recommendations/{method_type}` - Get timing recommendations

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd services/fertilizer-application
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the service**:
   ```bash
   python start_service.py
   ```

## Configuration

### Environment Variables

- `FERTILIZER_APPLICATION_PORT` - Service port (default: 8008)
- `FERTILIZER_APPLICATION_HOST` - Service host (default: 0.0.0.0)
- `DATABASE_URL` - PostgreSQL database URL
- `REDIS_URL` - Redis cache URL
- `LOG_LEVEL` - Logging level (default: INFO)

### Service Dependencies

- **Crop Taxonomy Service** - For crop-specific requirements
- **Soil Management Service** - For soil condition analysis
- **Economic Analysis Service** - For cost optimization
- **Weather Service** - For weather-based recommendations

## Usage Examples

### Select Application Methods

```python
import httpx

async def select_methods():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8008/api/v1/application/select-methods",
            json={
                "field_conditions": {
                    "field_size_acres": 100,
                    "soil_type": "loam",
                    "drainage_class": "well_drained",
                    "slope_percent": 2.5,
                    "irrigation_available": True
                },
                "crop_requirements": {
                    "crop_type": "corn",
                    "growth_stage": "vegetative",
                    "target_yield": 180,
                    "nutrient_requirements": {"nitrogen": 150, "phosphorus": 60, "potassium": 120}
                },
                "fertilizer_specification": {
                    "fertilizer_type": "liquid",
                    "npk_ratio": "28-0-0",
                    "form": "liquid",
                    "cost_per_unit": 0.85,
                    "unit": "lbs"
                },
                "available_equipment": [
                    {
                        "equipment_type": "sprayer",
                        "capacity": 500,
                        "capacity_unit": "gallons"
                    }
                ]
            }
        )
        return response.json()
```

### Get Application Guidance

```python
async def get_guidance():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8008/api/v1/guidance/application-guidance",
            json={
                "application_method": {
                    "method_id": "foliar_001",
                    "method_type": "foliar",
                    "recommended_equipment": {
                        "equipment_type": "sprayer",
                        "capacity": 500
                    },
                    "application_rate": 2.5,
                    "rate_unit": "gallons/acre",
                    "application_timing": "Early morning",
                    "efficiency_score": 0.9,
                    "cost_per_acre": 30.0,
                    "labor_requirements": "high",
                    "environmental_impact": "low",
                    "pros": ["High efficiency", "Quick response"],
                    "cons": ["Weather sensitive", "Higher cost"]
                },
                "field_conditions": {
                    "field_size_acres": 50,
                    "soil_type": "loam",
                    "irrigation_available": True
                },
                "weather_conditions": {
                    "temperature_celsius": 22,
                    "humidity_percent": 65,
                    "wind_speed_kmh": 8,
                    "precipitation_mm": 0
                },
                "application_date": "2024-05-15",
                "experience_level": "intermediate"
            }
        )
        return response.json()
```

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Development

### Code Style

The project uses Black for code formatting and Flake8 for linting:

```bash
black src/
flake8 src/
```

### Type Checking

Use MyPy for type checking:

```bash
mypy src/
```

## Architecture

### Service Structure

```
services/fertilizer-application/
├── src/
│   ├── api/                    # API route handlers
│   │   ├── application_routes.py
│   │   ├── method_routes.py
│   │   └── guidance_routes.py
│   ├── services/               # Business logic services
│   │   ├── application_method_service.py
│   │   ├── equipment_assessment_service.py
│   │   ├── cost_analysis_service.py
│   │   └── guidance_service.py
│   ├── models/                 # Pydantic data models
│   │   ├── application_models.py
│   │   ├── equipment_models.py
│   │   └── method_models.py
│   ├── database/               # Database models and connections
│   │   └── fertilizer_db.py
│   ├── utils/                  # Utility functions
│   ├── main.py                 # FastAPI application
│   └── config.py               # Configuration settings
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── start_service.py           # Service startup script
└── README.md                  # This file
```

### Data Flow

1. **Request Processing**: API routes receive and validate requests
2. **Service Layer**: Business logic services process requests
3. **Data Models**: Pydantic models ensure data validation
4. **Database Layer**: Database operations for persistence
5. **Response Generation**: Structured responses with metadata

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of the AFAS (Autonomous Farm Advisory System) and is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.