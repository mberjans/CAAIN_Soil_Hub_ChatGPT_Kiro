# Image Analysis Service

## Overview

The Image Analysis Service is a computer vision and machine learning service that analyzes crop photos to detect nutrient deficiencies. This service is part of the CAAIN Soil Hub project and operates on port 8004.

## Features

- **Image Preprocessing**: Quality assessment, color correction, and feature enhancement
- **Deficiency Detection**: CNN-based detection for nitrogen, phosphorus, potassium, and other nutrient deficiencies
- **Multi-Crop Support**: Supports corn, soybean, and wheat analysis
- **Confidence Scoring**: Provides confidence scores and severity assessments
- **RESTful API**: FastAPI-based service with file upload support
- **Performance Optimized**: <10 second analysis time per image

## Supported Crops

- **Corn**: Detects nitrogen, phosphorus, potassium, sulfur, iron, and zinc deficiencies
- **Soybean**: Detects nitrogen, phosphorus, potassium, iron, and manganese deficiencies
- **Wheat**: Detects nitrogen, phosphorus, potassium, and sulfur deficiencies

## Service Architecture

```
services/image-analysis/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # Database models
│   │   ├── image_analysis_models.py
│   │   └── symptom_models.py
│   ├── services/               # Business logic
│   │   ├── crop_photo_analyzer.py
│   │   ├── symptom_matching_service.py
│   │   └── image_preprocessor.py
│   ├── api/                    # API routes
│   │   ├── image_analysis_routes.py
│   │   └── analysis_routes.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── image_schemas.py
│   │   └── symptom_schemas.py
│   ├── database/               # Database utilities
│   │   ├── image_db.py
│   │   └── populate_symptoms.py
│   ├── ml_models/              # ML model definitions
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
├── sample_images/              # Sample crop images
├── requirements.txt            # Python dependencies
├── venv/                      # Virtual environment
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- 8GB+ RAM (for TensorFlow models)

### Installation

1. **Create and activate virtual environment**:
```bash
cd services/image-analysis
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installations**:
```bash
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "from PIL import Image; print('Pillow OK')"
```

### Database Setup

Ensure the PostgreSQL database is running and migrations have been applied:
```bash
psql -U postgres -d caain_soil_hub -f migrations/003_image_analysis_schema.sql
```

## Running the Service

### Development Mode
```bash
cd services/image-analysis
source venv/bin/activate
uvicorn src.main:app --reload --port 8004
```

### Production Mode
```bash
cd services/image-analysis
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8004 --workers 4
```

### Health Check
```bash
curl http://localhost:8004/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "image-analysis"
}
```

## API Documentation

### Main Endpoint

#### `POST /api/v1/deficiency/image-analysis`

Analyzes a crop image for nutrient deficiencies.

**Request Parameters:**
- `image` (file, required): Crop image file (JPEG/PNG)
- `crop_type` (string, required): Type of crop (`corn`, `soybean`, `wheat`)
- `growth_stage` (string, optional): Growth stage (e.g., `V6`, `R2`)

**Example Request:**
```bash
curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis \
  -F "image=@crop_photo.jpg" \
  -F "crop_type=corn" \
  -F "growth_stage=V6"
```

**Response Format:**
```json
{
  "success": true,
  "analysis_id": "generated_uuid_here",
  "image_quality": {
    "score": 0.85,
    "resolution_ok": true,
    "brightness_ok": true,
    "blur_ok": true,
    "issues": []
  },
  "analysis": {
    "crop_type": "corn",
    "growth_stage": "V6",
    "deficiencies": [
      {
        "nutrient": "nitrogen",
        "confidence": 0.75,
        "severity": "moderate",
        "affected_area_percent": 75.0,
        "symptoms_detected": [
          "Yellowing of older leaves",
          "Stunted growth",
          "Pale green color"
        ]
      }
    ],
    "healthy_probability": 0.25,
    "model_version": "v1.0"
  },
  "recommendations": [
    {
      "action": "Apply nitrogen fertilizer",
      "priority": "medium",
      "timing": "within 1 week",
      "details": "Address nitrogen deficiency detected with 75% confidence"
    }
  ]
}
```

### Image Quality Requirements

For best results, images should meet these criteria:

- **Format**: JPEG or PNG
- **Resolution**: Minimum 224x224 pixels
- **Quality**: Clear, non-blurry images
- **Lighting**: Good, even lighting conditions
- **Content**: Clear view of plant leaves/stems

### Error Responses

**Low Quality Image (400)**:
```json
{
  "success": false,
  "message": "Image quality too low for analysis",
  "image_quality": {
    "score": 0.3,
    "issues": ["Low resolution", "Image is blurry"]
  },
  "suggestions": [
    "Ensure good lighting",
    "Hold camera steady to avoid blur",
    "Get closer to the plant"
  ]
}
```

**Unsupported Crop Type (400)**:
```json
{
  "detail": "Unsupported crop type: rice"
}
```

## Testing

### Run Unit Tests
```bash
cd services/image-analysis
source venv/bin/activate
pytest tests/ -v
```

### Run Integration Tests
```bash
cd services/image-analysis
source venv/bin/activate
pytest tests/test_api_integration.py -v
```

### Generate Coverage Report
```bash
cd services/image-analysis
source venv/bin/activate
pytest tests/ --cov=src --cov-report=html
```

Target test coverage: >80%

## Performance

- **Analysis Time**: <10 seconds per image
- **Memory Usage**: ~2GB (TensorFlow models)
- **Concurrent Requests**: Up to 4 with production workers

## Model Training Guide

For training custom models, see: [docs/model_training_guide.md](docs/model_training_guide.md)

### Current Models

The service uses placeholder CNN models for development. Production models should be trained using:

- **Framework**: TensorFlow 2.14+
- **Architecture**: Convolutional Neural Networks
- **Input Size**: 224x224 RGB images
- **Output**: Multi-class classification for nutrient deficiencies

## Integration with Other Services

This service integrates with:

- **Recommendation Engine** (Port 8002): For fertilizer recommendations
- **User Management**: For image storage and analysis history
- **Mobile App**: For camera integration and image upload

## Troubleshooting

### Common Issues

1. **TensorFlow Import Error**:
   - Ensure TensorFlow 2.20+ is installed
   - Check Python version compatibility

2. **Out of Memory Errors**:
   - Reduce worker count in production
   - Ensure sufficient system RAM

3. **Poor Analysis Results**:
   - Check image quality and lighting
   - Verify correct crop type is specified
   - Ensure images show clear leaf symptoms

### Logs

Monitor logs for debugging:
```bash
# Development
uvicorn src.main:app --reload --port 8004 --log-level debug

# Production
journalctl -u image-analysis-service -f
```

## Contributing

1. Follow the existing code style
2. Add unit tests for new features
3. Update API documentation
4. Test with sample images

## Version History

- **v1.0.0**: Initial release with basic deficiency detection
- Support for corn, soybean, and wheat
- Image preprocessing and quality assessment
- REST API with file upload support

## Support

For technical support or questions:
- Create an issue in the project repository
- Check the [docs/](docs/) directory for additional guides
- Review test cases for usage examples

## License

This service is part of the CAAIN Soil Hub project. See the main project license for details.