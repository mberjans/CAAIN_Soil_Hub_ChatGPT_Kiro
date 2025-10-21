# Job 3: Nutrient Deficiency Detection - Development Tickets

**Total Tickets**: 13  
**Estimated Timeline**: 4-5 weeks  
**Service**: Image Analysis Service (Port 8004)  
**Related Plan**: `docs/parallel-job-3-deficiency-detection.md`

---

## JOB3-001: Setup Image Analysis Service Structure

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: None (Can start immediately)  
**Blocks**: JOB3-002, JOB3-003, JOB3-004  
**Parallel Execution**: No

**Description**:
Create directory structure for image analysis service with ML model directories.

**Acceptance Criteria**:
- [ ] Directory structure created
- [ ] ml_models directory created
- [ ] sample_images directory created
- [ ] Virtual environment created

**Validation Commands**:
```bash
mkdir -p services/image-analysis/src/{models,services,ml_models,api,schemas}
mkdir -p services/image-analysis/tests
mkdir -p services/image-analysis/sample_images/test_images
cd services/image-analysis
python3 -m venv venv
source venv/bin/activate
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.1

---

## JOB3-002: Install ML/CV Dependencies

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB3-001  
**Blocks**: JOB3-003, JOB3-004, JOB3-005  
**Parallel Execution**: No

**Description**:
Install TensorFlow, OpenCV, and other ML/CV dependencies.

**Acceptance Criteria**:
- [ ] TensorFlow 2.14+ installed
- [ ] OpenCV installed
- [ ] Pillow installed
- [ ] All imports working

**Validation Commands**:
```bash
pip install -r requirements.txt
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "from PIL import Image; print('Pillow OK')"
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.1

---

## JOB3-003: Create Database Schema for Image Metadata

**Priority**: High  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB3-002  
**Blocks**: JOB3-008  
**Parallel Execution**: Can run parallel with JOB3-004, JOB3-005

**Description**:
Create database schema for storing image analysis results and metadata.

**Acceptance Criteria**:
- [ ] image_analyses table created
- [ ] deficiency_detections table created
- [ ] Indexes created
- [ ] Sample data inserted

**Validation Commands**:
```bash
psql -U postgres -d caain_soil_hub -f migrations/003_image_analysis_schema.sql
psql -U postgres -d caain_soil_hub -c "SELECT * FROM image_analyses LIMIT 5;"
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.2

---

## JOB3-004: Create Pydantic Schemas

**Priority**: High  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB3-002  
**Blocks**: JOB3-008, JOB3-009  
**Parallel Execution**: Can run parallel with JOB3-003, JOB3-005

**Description**:
Create schemas for image upload, analysis requests, and responses.

**Acceptance Criteria**:
- [ ] ImageAnalysisRequest schema created
- [ ] DeficiencyResult schema created
- [ ] AnalysisResponse schema created
- [ ] File upload validation working

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.3

---

## JOB3-005: Create FastAPI Main Application

**Priority**: High  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB3-002  
**Blocks**: JOB3-008, JOB3-009  
**Parallel Execution**: Can run parallel with JOB3-003, JOB3-004

**Description**:
Create main FastAPI app with file upload support on port 8004.

**Acceptance Criteria**:
- [ ] FastAPI app created
- [ ] File upload middleware configured
- [ ] Health endpoint working
- [ ] App starts on port 8004

**Validation Commands**:
```bash
uvicorn src.main:app --port 8004 &
curl http://localhost:8004/health
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.1

---

## JOB3-006: Implement Image Preprocessor

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: JOB3-002, JOB3-004  
**Blocks**: JOB3-007, JOB3-008  
**Parallel Execution**: Can run parallel with JOB3-003

**Description**:
Implement ImagePreprocessor with quality assessment, color correction, and feature enhancement.

**Acceptance Criteria**:
- [ ] ImagePreprocessor class implemented
- [ ] Quality assessment working
- [ ] Color correction implemented
- [ ] Image resizing working
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-3-deficiency-detection.md` for complete implementation.

**Validation Commands**:
```bash
pytest tests/test_preprocessor.py -v
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.2

---

## JOB3-007: Implement Deficiency Detector with CNN Models

**Priority**: Critical  
**Estimated Effort**: 2 days  
**Dependencies**: JOB3-006  
**Blocks**: JOB3-008  
**Parallel Execution**: No

**Description**:
Implement DeficiencyDetector with CNN models for corn, soybean, and wheat. Use placeholder models for development.

**Acceptance Criteria**:
- [ ] DeficiencyDetector class implemented
- [ ] Placeholder CNN models created
- [ ] Model loading working
- [ ] Inference working
- [ ] Confidence scoring implemented
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-3-deficiency-detection.md` for complete implementation.

**Validation Commands**:
```bash
pytest tests/test_detector.py -v
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-2.3, TICKET-007_nutrient-deficiency-detection-3.1

---

## JOB3-008: Create Image Analysis API Endpoint

**Priority**: Critical  
**Estimated Effort**: 6 hours  
**Dependencies**: JOB3-004, JOB3-005, JOB3-006, JOB3-007  
**Blocks**: JOB3-010  
**Parallel Execution**: Can run parallel with JOB3-009

**Description**:
Create POST /api/v1/deficiency/image-analysis endpoint with file upload.

**Acceptance Criteria**:
- [ ] POST /api/v1/deficiency/image-analysis endpoint working
- [ ] File upload working
- [ ] Image validation working
- [ ] Analysis results returned
- [ ] API tests passing

**Validation Commands**:
```bash
curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis \
  -F "image=@test_image.jpg" \
  -F "crop_type=corn" \
  -F "growth_stage=V6"
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-3.2

---

## JOB3-009: Implement Confidence Scorer

**Priority**: High  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB3-007  
**Blocks**: JOB3-010  
**Parallel Execution**: Can run parallel with JOB3-008

**Description**:
Implement confidence scoring system for deficiency predictions.

**Acceptance Criteria**:
- [ ] ConfidenceScorer class implemented
- [ ] Severity determination working
- [ ] Affected area estimation working
- [ ] Unit tests passing

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-3.1

---

## JOB3-010: Implement Integration Tests

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: JOB3-008, JOB3-009  
**Blocks**: JOB3-011  
**Parallel Execution**: No

**Description**:
Create integration tests with sample crop images.

**Acceptance Criteria**:
- [ ] Integration tests created
- [ ] Sample images added to test suite
- [ ] End-to-end analysis tested
- [ ] Performance <10s per image
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/ -v --cov=src
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-4.1

---

## JOB3-011: Agricultural Validation with Sample Images

**Priority**: High  
**Estimated Effort**: 1 day  
**Dependencies**: JOB3-010  
**Blocks**: JOB3-012  
**Parallel Execution**: No

**Description**:
Validate deficiency detection with known deficiency images and expert review.

**Acceptance Criteria**:
- [ ] Test with known nitrogen deficiency images
- [ ] Test with known phosphorus deficiency images
- [ ] Symptom descriptions validated
- [ ] Expert feedback incorporated

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-4.2

---

## JOB3-012: Create Documentation and Model Training Guide

**Priority**: Medium  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB3-011  
**Blocks**: JOB3-013  
**Parallel Execution**: No

**Description**:
Create documentation including model training guide for future improvements.

**Acceptance Criteria**:
- [ ] README created
- [ ] API documentation complete
- [ ] Model training guide created
- [ ] Sample images documented

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-5.1

---

## JOB3-013: Final Integration Preparation

**Priority**: Critical  
**Estimated Effort**: 3 hours  
**Dependencies**: JOB3-012  
**Blocks**: None (Ready for integration)  
**Parallel Execution**: No

**Description**:
Final checks and preparation for integration with fertilizer optimization service.

**Acceptance Criteria**:
- [ ] Service runs on port 8004
- [ ] All tests passing
- [ ] Mock endpoints for dependencies
- [ ] Ready for integration with JOB2

**Validation Commands**:
```bash
uvicorn src.main:app --port 8004 &
pytest tests/ -v
curl http://localhost:8004/health
```

**Related Tickets**: TICKET-007_nutrient-deficiency-detection-6.1

---

## Summary

**Total Tickets**: 13  
**Critical Path**: JOB3-001 → JOB3-002 → JOB3-006 → JOB3-007 → JOB3-008 → JOB3-010 → JOB3-011 → JOB3-012 → JOB3-013  
**Estimated Total Time**: 4-5 weeks  
**Parallel Opportunities**: JOB3-003/004/005, JOB3-008/009


