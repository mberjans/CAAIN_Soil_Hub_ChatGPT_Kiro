"""
GPS Accuracy Assessment API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

API endpoints for GPS accuracy assessment and improvement services.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, validator

from ..services.gps_accuracy_service import (
    GPSAccuracyService, GPSReading, GPSAccuracyAssessment, 
    GPSImprovementResult, GPSAccuracyLevel, GPSImprovementMethod
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/gps-accuracy", tags=["gps-accuracy"])


# Pydantic models for API requests/responses
class GPSReadingRequest(BaseModel):
    """Request model for GPS reading."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    accuracy: float = Field(..., ge=0.0, description="GPS accuracy in meters")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    satellite_count: Optional[int] = Field(None, ge=0, description="Number of satellites")
    signal_strength: Optional[float] = Field(None, description="Signal strength in dBm")
    hdop: Optional[float] = Field(None, ge=0.0, description="Horizontal Dilution of Precision")
    vdop: Optional[float] = Field(None, ge=0.0, description="Vertical Dilution of Precision")
    timestamp: Optional[datetime] = Field(None, description="Reading timestamp")


class GPSAccuracyAssessmentResponse(BaseModel):
    """Response model for GPS accuracy assessment."""
    accuracy_level: GPSAccuracyLevel
    horizontal_accuracy: float
    vertical_accuracy: Optional[float]
    confidence_score: float
    satellite_count: Optional[int]
    signal_quality: str
    assessment_timestamp: datetime
    recommendations: List[str]
    improvement_methods: List[GPSImprovementMethod]


class GPSImprovementRequest(BaseModel):
    """Request model for GPS accuracy improvement."""
    readings: List[GPSReadingRequest] = Field(..., min_items=1, description="GPS readings to improve")
    method: Optional[GPSImprovementMethod] = Field(None, description="Improvement method to use")


class GPSImprovementResponse(BaseModel):
    """Response model for GPS accuracy improvement."""
    original_accuracy: float
    improved_accuracy: float
    improvement_percentage: float
    method_used: GPSImprovementMethod
    confidence_gain: float
    processing_time_ms: float
    improved_coordinates: Dict[str, float]


class GPSSignalQualityResponse(BaseModel):
    """Response model for GPS signal quality monitoring."""
    current_quality: str
    stability_score: float
    satellite_count: Optional[int]
    hdop: Optional[float]
    signal_strength: Optional[float]
    degradation_alerts: List[str]
    recommendations: List[str]
    timestamp: datetime


class GPSBatchAssessmentRequest(BaseModel):
    """Request model for batch GPS assessment."""
    readings: List[GPSReadingRequest] = Field(..., min_items=1, description="GPS readings to assess")
    include_improvement: bool = Field(False, description="Include accuracy improvement suggestions")


class GPSBatchAssessmentResponse(BaseModel):
    """Response model for batch GPS assessment."""
    assessments: List[GPSAccuracyAssessmentResponse]
    overall_quality: str
    average_accuracy: float
    improvement_suggestions: Optional[List[GPSImprovementMethod]] = None
    processing_time_ms: float


# Dependency injection
async def get_gps_accuracy_service() -> GPSAccuracyService:
    """Get GPS accuracy service instance."""
    return GPSAccuracyService()


@router.post("/assess", response_model=GPSAccuracyAssessmentResponse)
async def assess_gps_accuracy(
    reading: GPSReadingRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Assess GPS accuracy and signal quality for a single reading.
    
    This endpoint provides comprehensive GPS accuracy evaluation including:
    - Accuracy level classification (excellent, good, fair, poor, unacceptable)
    - Signal quality assessment based on satellite count, HDOP, and signal strength
    - Confidence scoring for the GPS reading
    - Recommendations for improving accuracy
    - Suggested improvement methods
    
    Agricultural Use Cases:
    - Field boundary mapping accuracy validation
    - Precision agriculture equipment positioning
    - Crop monitoring location verification
    - Soil sampling location accuracy
    """
    try:
        # Convert request to GPSReading object
        gps_reading = GPSReading(
            latitude=reading.latitude,
            longitude=reading.longitude,
            accuracy=reading.accuracy,
            altitude=reading.altitude,
            timestamp=reading.timestamp or datetime.utcnow(),
            satellite_count=reading.satellite_count,
            signal_strength=reading.signal_strength,
            hdop=reading.hdop,
            vdop=reading.vdop
        )
        
        # Assess GPS accuracy
        assessment = await service.assess_gps_accuracy(gps_reading)
        
        return GPSAccuracyAssessmentResponse(
            accuracy_level=assessment.accuracy_level,
            horizontal_accuracy=assessment.horizontal_accuracy,
            vertical_accuracy=assessment.vertical_accuracy,
            confidence_score=assessment.confidence_score,
            satellite_count=assessment.satellite_count,
            signal_quality=assessment.signal_quality,
            assessment_timestamp=assessment.assessment_timestamp,
            recommendations=assessment.recommendations,
            improvement_methods=assessment.improvement_methods
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error assessing GPS accuracy: {e}")
        raise HTTPException(status_code=500, detail="GPS accuracy assessment failed")


@router.post("/improve", response_model=GPSImprovementResponse)
async def improve_gps_accuracy(
    request: GPSImprovementRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Improve GPS accuracy using specified method.
    
    This endpoint applies various GPS accuracy improvement techniques:
    - Multi-reading averaging for noise reduction
    - Differential GPS correction simulation
    - RTK (Real-Time Kinematic) correction simulation
    - Signal filtering for outlier removal
    
    Agricultural Use Cases:
    - Improving field boundary mapping accuracy
    - Enhancing precision agriculture positioning
    - Reducing GPS noise in field data collection
    - Achieving centimeter-level accuracy for precision applications
    """
    try:
        # Convert requests to GPSReading objects
        gps_readings = []
        for reading_req in request.readings:
            gps_reading = GPSReading(
                latitude=reading_req.latitude,
                longitude=reading_req.longitude,
                accuracy=reading_req.accuracy,
                altitude=reading_req.altitude,
                timestamp=reading_req.timestamp or datetime.utcnow(),
                satellite_count=reading_req.satellite_count,
                signal_strength=reading_req.signal_strength,
                hdop=reading_req.hdop,
                vdop=reading_req.vdop
            )
            gps_readings.append(gps_reading)
        
        # Improve GPS accuracy
        improvement_result = await service.improve_gps_accuracy(gps_readings, request.method)
        
        return GPSImprovementResponse(
            original_accuracy=improvement_result.original_accuracy,
            improved_accuracy=improvement_result.improved_accuracy,
            improvement_percentage=improvement_result.improvement_percentage,
            method_used=improvement_result.method_used,
            confidence_gain=improvement_result.confidence_gain,
            processing_time_ms=improvement_result.processing_time_ms,
            improved_coordinates={
                "latitude": gps_readings[-1].latitude,  # Would be improved coordinates
                "longitude": gps_readings[-1].longitude
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error improving GPS accuracy: {e}")
        raise HTTPException(status_code=500, detail="GPS accuracy improvement failed")


@router.post("/monitor-signal", response_model=GPSSignalQualityResponse)
async def monitor_gps_signal_quality(
    reading: GPSReadingRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Monitor GPS signal quality in real-time.
    
    This endpoint provides real-time GPS signal quality monitoring including:
    - Current signal quality assessment
    - Signal stability over time
    - Satellite count and HDOP monitoring
    - Signal degradation alerts
    - Recommendations for signal improvement
    
    Agricultural Use Cases:
    - Real-time GPS quality monitoring during field mapping
    - Signal quality alerts for precision agriculture equipment
    - GPS signal troubleshooting in field conditions
    - Optimal timing recommendations for GPS-dependent tasks
    """
    try:
        # Convert request to GPSReading object
        gps_reading = GPSReading(
            latitude=reading.latitude,
            longitude=reading.longitude,
            accuracy=reading.accuracy,
            altitude=reading.altitude,
            timestamp=reading.timestamp or datetime.utcnow(),
            satellite_count=reading.satellite_count,
            signal_strength=reading.signal_strength,
            hdop=reading.hdop,
            vdop=reading.vdop
        )
        
        # Monitor signal quality
        quality_report = await service.monitor_gps_signal_quality(gps_reading)
        
        return GPSSignalQualityResponse(
            current_quality=quality_report['current_quality'],
            stability_score=quality_report['stability_score'],
            satellite_count=quality_report['satellite_count'],
            hdop=quality_report['hdop'],
            signal_strength=quality_report['signal_strength'],
            degradation_alerts=quality_report['degradation_alerts'],
            recommendations=quality_report['recommendations'],
            timestamp=quality_report['timestamp']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error monitoring GPS signal quality: {e}")
        raise HTTPException(status_code=500, detail="GPS signal quality monitoring failed")


@router.post("/batch-assess", response_model=GPSBatchAssessmentResponse)
async def batch_assess_gps_accuracy(
    request: GPSBatchAssessmentRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Assess GPS accuracy for multiple readings in batch.
    
    This endpoint provides batch processing of GPS accuracy assessments:
    - Individual assessment for each reading
    - Overall quality summary
    - Average accuracy calculation
    - Optional improvement suggestions
    
    Agricultural Use Cases:
    - Batch processing of field mapping GPS readings
    - Quality assessment of GPS data collected over time
    - Bulk validation of GPS coordinates for field boundaries
    - Performance analysis of GPS equipment over multiple readings
    """
    try:
        start_time = datetime.utcnow()
        
        # Convert requests to GPSReading objects
        gps_readings = []
        for reading_req in request.readings:
            gps_reading = GPSReading(
                latitude=reading_req.latitude,
                longitude=reading_req.longitude,
                accuracy=reading_req.accuracy,
                altitude=reading_req.altitude,
                timestamp=reading_req.timestamp or datetime.utcnow(),
                satellite_count=reading_req.satellite_count,
                signal_strength=reading_req.signal_strength,
                hdop=reading_req.hdop,
                vdop=reading_req.vdop
            )
            gps_readings.append(gps_reading)
        
        # Assess each reading
        assessments = []
        for reading in gps_readings:
            assessment = await service.assess_gps_accuracy(reading)
            assessments.append(GPSAccuracyAssessmentResponse(
                accuracy_level=assessment.accuracy_level,
                horizontal_accuracy=assessment.horizontal_accuracy,
                vertical_accuracy=assessment.vertical_accuracy,
                confidence_score=assessment.confidence_score,
                satellite_count=assessment.satellite_count,
                signal_quality=assessment.signal_quality,
                assessment_timestamp=assessment.assessment_timestamp,
                recommendations=assessment.recommendations,
                improvement_methods=assessment.improvement_methods
            ))
        
        # Calculate overall metrics
        accuracies = [a.horizontal_accuracy for a in assessments]
        average_accuracy = sum(accuracies) / len(accuracies)
        
        # Determine overall quality based on average accuracy
        if average_accuracy <= 3:
            overall_quality = "excellent"
        elif average_accuracy <= 10:
            overall_quality = "good"
        elif average_accuracy <= 30:
            overall_quality = "fair"
        elif average_accuracy <= 100:
            overall_quality = "poor"
        else:
            overall_quality = "unacceptable"
        
        # Generate improvement suggestions if requested
        improvement_suggestions = None
        if request.include_improvement:
            improvement_suggestions = []
            for assessment in assessments:
                improvement_suggestions.extend(assessment.improvement_methods)
            improvement_suggestions = list(set(improvement_suggestions))  # Remove duplicates
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return GPSBatchAssessmentResponse(
            assessments=assessments,
            overall_quality=overall_quality,
            average_accuracy=average_accuracy,
            improvement_suggestions=improvement_suggestions,
            processing_time_ms=processing_time
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in batch GPS assessment: {e}")
        raise HTTPException(status_code=500, detail="Batch GPS assessment failed")


@router.get("/accuracy-levels")
async def get_accuracy_levels():
    """
    Get GPS accuracy level definitions and thresholds.
    
    Returns the accuracy level classifications used by the service:
    - Excellent: < 3m accuracy
    - Good: 3-10m accuracy  
    - Fair: 10-30m accuracy
    - Poor: 30-100m accuracy
    - Unacceptable: > 100m accuracy
    """
    return {
        "accuracy_levels": {
            "excellent": {
                "threshold": 3.0,
                "description": "Suitable for precision agriculture and centimeter-level applications",
                "use_cases": ["RTK GPS", "Precision planting", "Variable rate application"]
            },
            "good": {
                "threshold": 10.0,
                "description": "Suitable for most agricultural field mapping applications",
                "use_cases": ["Field boundary mapping", "Yield monitoring", "Soil sampling"]
            },
            "fair": {
                "threshold": 30.0,
                "description": "Acceptable for general agricultural applications",
                "use_cases": ["General field mapping", "Equipment tracking", "Basic navigation"]
            },
            "poor": {
                "threshold": 100.0,
                "description": "Marginal accuracy, may require improvement",
                "use_cases": ["Rough field location", "General area identification"]
            },
            "unacceptable": {
                "threshold": float('inf'),
                "description": "Too inaccurate for reliable agricultural applications",
                "use_cases": ["Not recommended for agricultural use"]
            }
        },
        "improvement_methods": {
            "multi_reading_average": {
                "description": "Average multiple GPS readings to reduce noise",
                "expected_improvement": "30%",
                "requirements": "Multiple readings over time"
            },
            "differential_gps": {
                "description": "Use differential GPS correction signals",
                "expected_improvement": "70%",
                "requirements": "Differential GPS receiver and correction source"
            },
            "rtk_correction": {
                "description": "Real-Time Kinematic correction for centimeter accuracy",
                "expected_improvement": "90%",
                "requirements": "RTK-capable receiver and base station"
            },
            "signal_filtering": {
                "description": "Apply signal filtering to remove outliers",
                "expected_improvement": "20%",
                "requirements": "Multiple readings for filtering"
            }
        }
    }


@router.post("/verify-location", response_model=Dict[str, Any])
async def verify_location_accuracy(
    request: GPSBatchAssessmentRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Advanced location verification with agricultural area validation.
    
    This endpoint provides comprehensive location verification including:
    - Multi-reading consistency analysis
    - Agricultural area validation with confidence scoring
    - Location reasonableness checks
    - Duplicate location detection
    - Comprehensive recommendations and warnings
    
    Agricultural Use Cases:
    - Farm location validation for new field setup
    - GPS accuracy verification for precision agriculture equipment
    - Location validation for soil sampling and field mapping
    - Agricultural area suitability assessment
    """
    try:
        # Convert requests to GPSReading objects
        gps_readings = []
        for reading_req in request.readings:
            gps_reading = GPSReading(
                latitude=reading_req.latitude,
                longitude=reading_req.longitude,
                accuracy=reading_req.accuracy,
                altitude=reading_req.altitude,
                timestamp=reading_req.timestamp or datetime.utcnow(),
                satellite_count=reading_req.satellite_count,
                signal_strength=reading_req.signal_strength,
                hdop=reading_req.hdop,
                vdop=reading_req.vdop
            )
            gps_readings.append(gps_reading)
        
        # Perform location verification
        verification_result = await service.verify_location_accuracy(gps_readings)
        
        return verification_result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in location verification: {e}")
        raise HTTPException(status_code=500, detail="Location verification failed")


@router.post("/assess-agricultural-suitability", response_model=Dict[str, Any])
async def assess_agricultural_suitability(
    reading: GPSReadingRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Assess agricultural suitability of a location.
    
    This endpoint provides detailed agricultural suitability analysis including:
    - Agricultural area classification
    - Climate zone assessment
    - Growing season estimation
    - Precipitation analysis
    - Latitude/longitude suitability scoring
    
    Agricultural Use Cases:
    - New farm location evaluation
    - Crop suitability assessment for specific locations
    - Agricultural expansion planning
    - Location comparison for farming operations
    """
    try:
        # Convert request to GPSReading object
        gps_reading = GPSReading(
            latitude=reading.latitude,
            longitude=reading.longitude,
            accuracy=reading.accuracy,
            altitude=reading.altitude,
            timestamp=reading.timestamp or datetime.utcnow(),
            satellite_count=reading.satellite_count,
            signal_strength=reading.signal_strength,
            hdop=reading.hdop,
            vdop=reading.vdop
        )
        
        # Perform agricultural area validation
        agricultural_result = await service._validate_agricultural_area(gps_reading)
        
        # Get detailed agricultural factors analysis
        agricultural_factors = service._analyze_agricultural_factors(reading.latitude, reading.longitude)
        
        # Compile comprehensive assessment
        assessment = {
            'location': {
                'latitude': reading.latitude,
                'longitude': reading.longitude,
                'accuracy': reading.accuracy
            },
            'agricultural_validation': agricultural_result,
            'agricultural_factors': agricultural_factors,
            'overall_suitability': {
                'score': agricultural_result['agricultural_score'],
                'category': 'excellent' if agricultural_result['agricultural_score'] >= 0.8 else
                          'good' if agricultural_result['agricultural_score'] >= 0.6 else
                          'fair' if agricultural_result['agricultural_score'] >= 0.4 else
                          'poor',
                'recommendations': service._generate_agricultural_recommendations(agricultural_result, agricultural_factors)
            },
            'assessment_timestamp': datetime.utcnow()
        }
        
        return assessment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in agricultural suitability assessment: {e}")
        raise HTTPException(status_code=500, detail="Agricultural suitability assessment failed")


@router.post("/check-location-reasonableness", response_model=Dict[str, Any])
async def check_location_reasonableness(
    reading: GPSReadingRequest,
    service: GPSAccuracyService = Depends(get_gps_accuracy_service)
):
    """
    Check if location coordinates are reasonable for agricultural use.
    
    This endpoint validates coordinate reasonableness including:
    - Coordinate range validation
    - Ocean/water body detection
    - Extreme latitude/longitude checks
    - Agricultural latitude suitability
    - Geographic categorization
    
    Agricultural Use Cases:
    - GPS coordinate validation before field setup
    - Location data quality assurance
    - Coordinate system verification
    - Agricultural location screening
    """
    try:
        # Convert request to GPSReading object
        gps_reading = GPSReading(
            latitude=reading.latitude,
            longitude=reading.longitude,
            accuracy=reading.accuracy,
            altitude=reading.altitude,
            timestamp=reading.timestamp or datetime.utcnow(),
            satellite_count=reading.satellite_count,
            signal_strength=reading.signal_strength,
            hdop=reading.hdop,
            vdop=reading.vdop
        )
        
        # Perform reasonableness checks
        reasonableness_result = await service._check_location_reasonableness(gps_reading)
        
        return {
            'location': {
                'latitude': reading.latitude,
                'longitude': reading.longitude
            },
            'reasonableness_check': reasonableness_result,
            'check_timestamp': datetime.utcnow()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in location reasonableness check: {e}")
        raise HTTPException(status_code=500, detail="Location reasonableness check failed")


@router.get("/health")
async def health_check():
    """Health check endpoint for GPS accuracy service."""
    return {
        "status": "healthy",
        "service": "gps-accuracy-assessment",
        "timestamp": datetime.utcnow(),
        "features": [
            "accuracy_assessment",
            "signal_quality_monitoring", 
            "accuracy_improvement",
            "batch_processing",
            "location_verification",
            "agricultural_suitability_assessment",
            "location_reasonableness_checking"
        ]
    }