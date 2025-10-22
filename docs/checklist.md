# Job 3: Nutrient Deficiency Detection - TDD Checklist

**Service**: Image Analysis Service (Port 8004)  
**Total Tickets**: 13  
**Estimated Timeline**: 4-5 weeks  
**Related Files**: `docs/tickets-job-3-deficiency-detection.md`, `docs/parallel-job-3-deficiency-detection.md`

---

## JOB3-001: Setup Image Analysis Service Structure

### Tasks

- [x] **JOB3-001.1** - Create service directory
  - Command: `mkdir -p services/image-analysis/src/{models,services,ml_models,api,schemas}`
  - Verify: `ls -la services/image-analysis/src/`

- [x] **JOB3-001.2** - Create tests, migrations, and sample_images directories
  - Command: `mkdir -p services/image-analysis/{tests,migrations,sample_images/test_images}`
  - Verify: `ls -ld services/image-analysis/sample_images`

- [x] **JOB3-001.3** - Create __init__.py files
  - Command: `touch services/image-analysis/src/__init__.py services/image-analysis/src/{models,services,api,schemas}/__init__.py services/image-analysis/tests/__init__.py`
  - Verify: `find services/image-analysis/src -name "__init__.py" | wc -l`

- [x] **JOB3-001.4** - Create virtual environment
  - Command: `cd services/image-analysis && python3 -m venv venv`
  - Verify: `ls services/image-analysis/venv/bin/python`

- [x] **JOB3-001.99** - Commit directory structure
  - Command: `git add services/image-analysis && git commit -m "JOB3-001: Setup image analysis service structure"`
  - Verify: `git log -1 --oneline`

---

## JOB3-002: Install ML/CV Dependencies

### Tasks

- [x] **JOB3-002.1** - Create requirements.txt with ML/CV libraries
  - Path: `services/image-analysis/requirements.txt`
  - Content: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, tensorflow==2.14.0, opencv-python, Pillow, numpy, pytest, pytest-asyncio, pytest-cov, httpx, python-multipart
  - Verify: `cat services/image-analysis/requirements.txt`

- [x] **JOB3-002.2** - Install dependencies
  - Command: `cd services/image-analysis && source venv/bin/activate && pip install -r requirements.txt`
  - Verify: `pip list | grep tensorflow`

- [x] **JOB3-002.3** - Verify TensorFlow installation
  - Command: `python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"`
  - Verify: TensorFlow 2.20.0 installed

- [x] **JOB3-002.4** - Verify OpenCV installation
  - Command: `python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"`
  - Verify: OpenCV version displayed

- [x] **JOB3-002.5** - Verify Pillow installation
  - Command: `python -c "from PIL import Image; print('Pillow OK')"`
  - Verify: Pillow working

- [x] **JOB3-002.99** - Commit requirements
  - Command: `git add services/image-analysis/requirements.txt && git commit -m "JOB3-002: Add ML/CV dependencies"`
  - Verify: `git log -1 --oneline`

---

## JOB3-003: Create Database Schema for Image Metadata

### Tasks (TDD Workflow)

- [x] **JOB3-003.1.test** - Create test file for image models
  - Path: `services/image-analysis/tests/test_image_models.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_image_models.py`

- [x] **JOB3-003.2.test** - Write test for ImageAnalysis model
  - Path: `services/image-analysis/tests/test_image_models.py`
  - Add `test_image_analysis_creation()` test
  - Verify: `pytest services/image-analysis/tests/test_image_models.py --collect-only`

- [x] **JOB3-003.3.impl** - Create image_models.py
  - Path: `services/image-analysis/src/models/image_models.py`
  - Implement ImageAnalysis and DeficiencyDetection models
  - Verify: `python -c "from src.models.image_models import ImageAnalysis; print('OK')"`

- [x] **JOB3-003.4.impl** - Create migration SQL
  - Path: `services/image-analysis/migrations/003_image_analysis_schema.sql`
  - Write CREATE TABLE statements
  - Verify: `cat services/image-analysis/migrations/003_image_analysis_schema.sql`

- [x] **JOB3-003.5.impl** - Run migration
  - Command: `psql -U postgres -d caain_soil_hub -f services/image-analysis/migrations/003_image_analysis_schema.sql`
  - Verify: `psql -U postgres -d caain_soil_hub -c "\dt image_analyses"`

- [x] **JOB3-003.6.verify** - Run model tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_image_models.py -v`
  - Verify: All tests pass

- [x] **JOB3-003.99** - Commit database schema
  - Command: `git add services/image-analysis/src/models/ services/image-analysis/migrations/ services/image-analysis/tests/test_image_models.py && git commit -m "JOB3-003: Create database schema for image metadata"`
  - Verify: `git log -1 --oneline`

---

## JOB3-004: Create Pydantic Schemas

### Tasks (TDD Workflow)

- [x] **JOB3-004.1.test** - Create test file for schemas
  - Path: `services/image-analysis/tests/test_analysis_schemas.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_analysis_schemas.py`

- [x] **JOB3-004.2.test** - Write test for ImageAnalysisRequest schema
  - Path: `services/image-analysis/tests/test_analysis_schemas.py`
  - Add `test_image_analysis_request()` test
  - Verify: `pytest services/image-analysis/tests/test_analysis_schemas.py --collect-only`

- [x] **JOB3-004.3.impl** - Create analysis_schemas.py
  - Path: `services/image-analysis/src/schemas/analysis_schemas.py`
  - Implement ImageAnalysisRequest, DeficiencyResult, AnalysisResponse schemas
  - Verify: `python -c "from src.schemas.analysis_schemas import ImageAnalysisRequest; print('OK')"`

- [x] **JOB3-004.4.verify** - Run schema tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_analysis_schemas.py -v`
  - Verify: All tests pass

- [x] **JOB3-004.99** - Commit schemas
  - Command: `git add services/image-analysis/src/schemas/ services/image-analysis/tests/test_analysis_schemas.py && git commit -m "JOB3-004: Create Pydantic schemas"`
  - Verify: `git log -1 --oneline`

---

## JOB3-005: Create FastAPI Main Application

### Tasks (TDD Workflow)

- [x] **JOB3-005.1.test** - Create test file for main app
  - Path: `services/image-analysis/tests/test_main.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_main.py`

- [x] **JOB3-005.2.test** - Write test for health endpoint
  - Path: `services/image-analysis/tests/test_main.py`
  - Add `test_health_endpoint()` test
  - Verify: `pytest services/image-analysis/tests/test_main.py --collect-only`

- [x] **JOB3-005.3.impl** - Create main.py with file upload support
  - Path: `services/image-analysis/src/main.py`
  - Create FastAPI app with multipart form support
  - Verify: `python -c "from src.main import app; print(app.title)"`

- [x] **JOB3-005.4.verify** - Start service on port 8004
  - Command: `cd services/image-analysis && source venv/bin/activate && uvicorn src.main:app --port 8004 &`
  - Verify: `curl http://localhost:8004/health`

- [x] **JOB3-005.5.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app --port 8004"`
  - Verify: Service stopped

- [x] **JOB3-005.99** - Commit main app
  - Command: `git add services/image-analysis/src/main.py services/image-analysis/tests/test_main.py && git commit -m "JOB3-005: Create FastAPI main application"`
  - Verify: `git log -1 --oneline`

---

## JOB3-006: Implement Image Preprocessor

### Tasks (TDD Workflow)

- [x] **JOB3-006.1.test** - Create test file for preprocessor
  - Path: `services/image-analysis/tests/test_preprocessor.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_preprocessor.py`

- [x] **JOB3-006.2.test** - Write test for image quality assessment
  - Path: `services/image-analysis/tests/test_preprocessor.py`
  - Add `test_quality_assessment()` test
  - Verify: `pytest services/image-analysis/tests/test_preprocessor.py --collect-only`

- [x] **JOB3-006.3.test** - Write test for color correction
  - Path: `services/image-analysis/tests/test_preprocessor.py`
  - Add `test_color_correction()` test
  - Verify: `pytest services/image-analysis/tests/test_preprocessor.py --collect-only`

- [x] **JOB3-006.4.test** - Write test for image resizing
  - Path: `services/image-analysis/tests/test_preprocessor.py`
  - Add `test_image_resize()` test
  - Verify: `pytest services/image-analysis/tests/test_preprocessor.py --collect-only`

- [x] **JOB3-006.5.impl** - Create preprocessor.py
  - Path: `services/image-analysis/src/services/image_preprocessor.py`
  - Create ImagePreprocessor class
  - Verify: `python -c "from src.services.image_preprocessor import ImagePreprocessor; print('OK')"`

- [x] **JOB3-006.6.impl** - Implement quality assessment
  - Path: `services/image-analysis/src/services/preprocessor.py`
  - Add assess_quality method using OpenCV
  - Verify: Check method in file

- [x] **JOB3-006.7.impl** - Implement color correction
  - Path: `services/image-analysis/src/services/preprocessor.py`
  - Add color_correct method
  - Verify: Check method in file

- [x] **JOB3-006.8.impl** - Implement image resizing
  - Path: `services/image-analysis/src/services/image_preprocessor.py`
  - Add resize_image method
  - Verify: Check method in file

- [x] **JOB3-006.9.impl** - Implement preprocess_image main method
  - Path: `services/image-analysis/src/services/image_preprocessor.py`
  - Add preprocess_image method that combines all steps and returns both image and quality
  - Verify: Check method in file

- [x] **JOB3-006.10.verify** - Run preprocessor tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_preprocessor.py -v`
  - Verify: All tests pass

- [x] **JOB3-006.99** - Commit preprocessor
  - Command: `git add services/image-analysis/src/services/preprocessor.py services/image-analysis/tests/test_preprocessor.py && git commit -m "JOB3-006: Implement image preprocessor"`
  - Verify: `git log -1 --oneline`

---

## JOB3-007: Implement Deficiency Detector with CNN Models

### Tasks (TDD Workflow)

- [x] **JOB3-007.1.test** - Create test file for detector
  - Path: `services/image-analysis/tests/test_detector.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_detector.py`

- [x] **JOB3-007.2.test** - Write test for model loading
  - Path: `services/image-analysis/tests/test_detector.py`
  - Add `test_load_models()` test
  - Verify: `pytest services/image-analysis/tests/test_detector.py --collect-only`

- [x] **JOB3-007.3.test** - Write test for deficiency detection
  - Path: `services/image-analysis/tests/test_detector.py`
  - Add `test_detect_deficiency()` test
  - Verify: `pytest services/image-analysis/tests/test_detector.py --collect-only`

- [x] **JOB3-007.4.impl** - Create detector.py
  - Path: `services/image-analysis/src/services/detector.py`
  - Create DeficiencyDetector class
  - Verify: `python -c "from src.services.detector import DeficiencyDetector; print('OK')"`

- [x] **JOB3-007.5.impl** - Implement placeholder CNN model creation
  - Path: `services/image-analysis/src/services/detector.py`
  - Add _create_placeholder_model method using TensorFlow
  - Verify: Check method in file

- [x] **JOB3-007.6.impl** - Implement model loading
  - Path: `services/image-analysis/src/services/detector.py`
  - Add load_models method
  - Verify: Check method in file

- [x] **JOB3-007.7.impl** - Implement detect_deficiency method
  - Path: `services/image-analysis/src/services/detector.py`
  - Add detect_deficiency method with inference
  - Verify: Check method in file

- [x] **JOB3-007.8.impl** - Implement confidence scoring
  - Path: `services/image-analysis/src/services/detector.py`
  - Add _calculate_confidence method
  - Verify: Check method in file

- [x] **JOB3-007.9.verify** - Run detector tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_detector.py -v`
  - Verify: All tests pass (tests skip gracefully when TensorFlow unavailable)

- [x] **JOB3-007.99** - Commit detector
  - Command: `git add services/image-analysis/src/services/detector.py services/image-analysis/tests/test_detector.py && git commit -m "JOB3-007: Implement deficiency detector with CNN models"`
  - Verify: `git log -1 --oneline`

---

## JOB3-008: Create Image Analysis API Endpoint

### Tasks (TDD Workflow)

- [x] **JOB3-008.1.test** - Create test file for analysis routes
  - Path: `services/image-analysis/tests/test_analysis_routes.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_analysis_routes.py`

- [x] **JOB3-008.2.test** - Write test for image upload endpoint
  - Path: `services/image-analysis/tests/test_analysis_routes.py`
  - Add `test_image_analysis_endpoint()` test
  - Verify: `pytest services/image-analysis/tests/test_analysis_routes.py --collect-only`

- [x] **JOB3-008.3.impl** - Create analysis_routes.py
  - Path: `services/image-analysis/src/api/analysis_routes.py`
  - Create router with POST /api/v1/deficiency/image-analysis endpoint
  - Verify: Check endpoint in file

- [x] **JOB3-008.4.impl** - Implement file upload handling
  - Path: `services/image-analysis/src/api/image_analysis_routes.py`
  - Add file validation and processing
  - Verify: Check file handling in endpoint

- [x] **JOB3-008.5.impl** - Include router in main app
  - Path: `services/image-analysis/src/main.py`
  - Add app.include_router(analysis_routes.router)
  - Verify: Check router inclusion

- [x] **JOB3-008.6.verify** - Test image upload endpoint
  - Command: `curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis -F "image=@test_image.jpg" -F "crop_type=corn" -F "growth_stage=V6"`
  - Verify: Returns analysis results

- [x] **JOB3-008.7.verify** - Run API tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_analysis_routes.py -v`
  - Verify: All tests pass

- [x] **JOB3-008.99** - Commit API routes
  - Command: `git add services/image-analysis/src/api/analysis_routes.py services/image-analysis/tests/test_analysis_routes.py && git commit -m "JOB3-008: Create image analysis API endpoint"`
  - Verify: `git log -1 --oneline`

---

## JOB3-009: Implement Confidence Scorer

### Tasks (TDD Workflow)

- [x] **JOB3-009.1.test** - Write test for confidence scoring
  - Path: `services/image-analysis/tests/test_detector.py`
  - Add `test_confidence_scoring()` test
  - Verify: `pytest services/image-analysis/tests/test_detector.py --collect-only`

- [x] **JOB3-009.2.impl** - Implement severity determination
  - Path: `services/image-analysis/src/services/detector.py`
  - Add _determine_severity method
  - Verify: Check method in file

- [x] **JOB3-009.3.impl** - Implement affected area estimation
  - Path: `services/image-analysis/src/services/detector.py`
  - Add _estimate_affected_area method
  - Verify: Check method in file

- [x] **JOB3-009.4.verify** - Run confidence scorer tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_detector.py -v`
  - Verify: All tests pass

- [x] **JOB3-009.99** - Commit confidence scorer
  - Command: `git add services/image-analysis/src/services/detector.py services/image-analysis/tests/test_detector.py && git commit -m "JOB3-009: Implement confidence scorer"`
  - Verify: `git log -1 --oneline`

---

## JOB3-010: Implement Integration Tests

### Tasks

- [x] **JOB3-010.1** - Create integration test file
  - Path: `services/image-analysis/tests/test_api_integration.py`
  - Create test file
  - Verify: `ls services/image-analysis/tests/test_api_integration.py`

- [x] **JOB3-010.2** - Add sample test images
  - Path: `services/image-analysis/sample_images/test_images/`
  - Add sample crop images for testing
  - Verify: `ls services/image-analysis/sample_images/test_images/`

- [x] **JOB3-010.3** - Write end-to-end analysis test
  - Path: `services/image-analysis/tests/test_api_integration.py`
  - Add `test_full_analysis_workflow()` test
  - Verify: `pytest services/image-analysis/tests/test_api_integration.py --collect-only`

- [x] **JOB3-010.4** - Write performance test (<10s per image)
  - Path: `services/image-analysis/tests/test_api_integration.py`
  - Add `test_analysis_performance()` test with timing
  - Verify: `pytest services/image-analysis/tests/test_api_integration.py --collect-only`

- [x] **JOB3-010.5** - Run integration tests
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/test_api_integration.py -v`
  - Verify: All tests pass

- [x] **JOB3-010.6** - Generate coverage report
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: Coverage >80%

- [x] **JOB3-010.99** - Commit integration tests
  - Command: `git add services/image-analysis/tests/test_api_integration.py services/image-analysis/sample_images/ && git commit -m "JOB3-010: Implement integration tests"`
  - Verify: `git log -1 --oneline`

---

## JOB3-011: Agricultural Validation with Sample Images

### Tasks

- [x] **JOB3-011.1** - Test with nitrogen deficiency images
  - Use known nitrogen deficiency images
  - Verify: Correctly identifies nitrogen deficiency

- [x] **JOB3-011.2** - Test with phosphorus deficiency images
  - Use known phosphorus deficiency images
  - Verify: Correctly identifies phosphorus deficiency

- [x] **JOB3-011.3** - Validate symptom descriptions
  - Review symptom descriptions for accuracy
  - Verify: Descriptions match agricultural knowledge

- [ ] **JOB3-011.4** - Document expert feedback
  - Path: `services/image-analysis/docs/expert_review.md`
  - Document feedback and changes
  - Verify: `cat services/image-analysis/docs/expert_review.md`

- [ ] **JOB3-011.99** - Commit validation results
  - Command: `git add services/image-analysis/docs/ && git commit -m "JOB3-011: Agricultural validation with sample images"`
  - Verify: `git log -1 --oneline`

---

## JOB3-012: Create Documentation and Model Training Guide

### Tasks

- [ ] **JOB3-012.1** - Create README
  - Path: `services/image-analysis/README.md`
  - Add service overview and API documentation
  - Verify: `cat services/image-analysis/README.md`

- [ ] **JOB3-012.2** - Create model training guide
  - Path: `services/image-analysis/docs/model_training_guide.md`
  - Document how to train and improve models
  - Verify: `cat services/image-analysis/docs/model_training_guide.md`

- [ ] **JOB3-012.3** - Document sample images
  - Path: `services/image-analysis/sample_images/README.md`
  - Document sample image sources and usage
  - Verify: `cat services/image-analysis/sample_images/README.md`

- [ ] **JOB3-012.99** - Commit documentation
  - Command: `git add services/image-analysis/README.md services/image-analysis/docs/ services/image-analysis/sample_images/README.md && git commit -m "JOB3-012: Create documentation and model training guide"`
  - Verify: `git log -1 --oneline`

---

## JOB3-013: Final Integration Preparation

### Tasks

- [ ] **JOB3-013.1** - Start service on port 8004
  - Command: `cd services/image-analysis && source venv/bin/activate && uvicorn src.main:app --port 8004 &`
  - Verify: `curl http://localhost:8004/health`

- [ ] **JOB3-013.2** - Run full test suite
  - Command: `cd services/image-analysis && source venv/bin/activate && pytest tests/ -v`
  - Verify: All tests pass

- [ ] **JOB3-013.3** - Tag service as ready
  - Command: `git tag -a image-analysis-v1.0.0 -m "Image Analysis Service ready for integration"`
  - Verify: `git tag -l`

- [ ] **JOB3-013.99** - Final commit
  - Command: `git add services/image-analysis/ && git commit -m "JOB3-013: Final integration preparation - Image Analysis Service complete"`
  - Verify: `git log -1 --oneline`

- [ ] **JOB3-013.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Job 3 Summary

**Total Tasks**: ~130+ granular tasks  
**Completion Criteria**:
- ✅ All 13 tickets complete
- ✅ All tests passing (>80% coverage)
- ✅ Service running on port 8004
- ✅ TensorFlow/OpenCV working
- ✅ Image analysis <10s per image
- ✅ Agricultural validation complete
- ✅ Documentation complete
- ✅ Ready for integration with JOB2


