"""
GPS Accuracy Assessment and Improvement Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive GPS accuracy assessment, signal quality monitoring,
and accuracy improvement system for agricultural field mapping.
"""

import logging
import asyncio
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics
import json

logger = logging.getLogger(__name__)


class GPSAccuracyLevel(str, Enum):
    """GPS accuracy quality levels."""
    EXCELLENT = "excellent"      # < 3m accuracy
    GOOD = "good"               # 3-10m accuracy
    FAIR = "fair"               # 10-30m accuracy
    POOR = "poor"               # 30-100m accuracy
    UNACCEPTABLE = "unacceptable"  # > 100m accuracy


class GPSImprovementMethod(str, Enum):
    """GPS accuracy improvement methods."""
    MULTI_READING_AVERAGE = "multi_reading_average"
    DIFFERENTIAL_GPS = "differential_gps"
    RTK_CORRECTION = "rtk_correction"
    POST_PROCESSING = "post_processing"
    SIGNAL_FILTERING = "signal_filtering"


@dataclass
class GPSReading:
    """Individual GPS reading with metadata."""
    latitude: float
    longitude: float
    accuracy: float
    altitude: Optional[float] = None
    timestamp: datetime = None
    satellite_count: Optional[int] = None
    signal_strength: Optional[float] = None
    hdop: Optional[float] = None  # Horizontal Dilution of Precision
    vdop: Optional[float] = None  # Vertical Dilution of Precision
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class GPSAccuracyAssessment:
    """GPS accuracy assessment result."""
    accuracy_level: GPSAccuracyLevel
    horizontal_accuracy: float
    vertical_accuracy: Optional[float]
    confidence_score: float
    satellite_count: Optional[int]
    signal_quality: str
    assessment_timestamp: datetime
    recommendations: List[str]
    improvement_methods: List[GPSImprovementMethod]


@dataclass
class GPSImprovementResult:
    """Result of GPS accuracy improvement."""
    original_accuracy: float
    improved_accuracy: float
    improvement_percentage: float
    method_used: GPSImprovementMethod
    confidence_gain: float
    processing_time_ms: float


class GPSAccuracyService:
    """
    GPS accuracy assessment and improvement service.
    
    Provides comprehensive GPS accuracy evaluation, signal quality monitoring,
    accuracy improvement algorithms, and advanced location verification for agricultural field mapping.
    """
    
    def __init__(self):
        """Initialize the GPS accuracy service."""
        self.logger = logging.getLogger(__name__)
        
        # Accuracy thresholds for different quality levels
        self.accuracy_thresholds = {
            GPSAccuracyLevel.EXCELLENT: 3.0,
            GPSAccuracyLevel.GOOD: 10.0,
            GPSAccuracyLevel.FAIR: 30.0,
            GPSAccuracyLevel.POOR: 100.0,
            GPSAccuracyLevel.UNACCEPTABLE: float('inf')
        }
        
        # Signal quality thresholds
        self.signal_thresholds = {
            'excellent': {'min_satellites': 8, 'max_hdop': 1.5, 'min_signal': -80},
            'good': {'min_satellites': 6, 'max_hdop': 2.5, 'min_signal': -90},
            'fair': {'min_satellites': 4, 'max_hdop': 4.0, 'min_signal': -100},
            'poor': {'min_satellites': 3, 'max_hdop': 6.0, 'min_signal': -110}
        }
        
        # Improvement method configurations
        self.improvement_config = {
            GPSImprovementMethod.MULTI_READING_AVERAGE: {
                'min_readings': 5,
                'max_time_window': 60,  # seconds
                'expected_improvement': 0.3  # 30% improvement
            },
            GPSImprovementMethod.DIFFERENTIAL_GPS: {
                'correction_source': 'satellite',
                'expected_improvement': 0.7  # 70% improvement
            },
            GPSImprovementMethod.RTK_CORRECTION: {
                'correction_source': 'ground_station',
                'expected_improvement': 0.9  # 90% improvement
            }
        }
        
        # Reading history for averaging
        self.reading_history: List[GPSReading] = []
        self.max_history_size = 50
        
        # Location verification settings
        self.verification_config = {
            'max_distance_variation': 1000,  # meters
            'min_confidence_threshold': 0.7,
            'agricultural_area_confidence_threshold': 0.8,
            'duplicate_detection_threshold': 10,  # meters
            'reasonableness_check_enabled': True
        }
        
        # Agricultural area validation data
        self.agricultural_regions = self._load_agricultural_regions()
        
        self.logger.info("GPS accuracy service initialized with enhanced location verification")
    
    async def assess_gps_accuracy(self, reading: GPSReading) -> GPSAccuracyAssessment:
        """
        Assess GPS accuracy and signal quality.
        
        Args:
            reading: GPS reading to assess
            
        Returns:
            GPSAccuracyAssessment with detailed analysis
        """
        try:
            start_time = datetime.utcnow()
            
            # Determine accuracy level
            accuracy_level = self._determine_accuracy_level(reading.accuracy)
            
            # Assess signal quality
            signal_quality = self._assess_signal_quality(reading)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(reading, signal_quality)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(reading, accuracy_level, signal_quality)
            
            # Suggest improvement methods
            improvement_methods = self._suggest_improvement_methods(reading, accuracy_level)
            
            assessment = GPSAccuracyAssessment(
                accuracy_level=accuracy_level,
                horizontal_accuracy=reading.accuracy,
                vertical_accuracy=reading.altitude,
                confidence_score=confidence_score,
                satellite_count=reading.satellite_count,
                signal_quality=signal_quality,
                assessment_timestamp=start_time,
                recommendations=recommendations,
                improvement_methods=improvement_methods
            )
            
            # Store reading in history
            self._store_reading(reading)
            
            self.logger.info(f"GPS accuracy assessed: {accuracy_level.value} ({reading.accuracy}m)")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing GPS accuracy: {e}")
            raise
    
    async def improve_gps_accuracy(
        self, 
        readings: List[GPSReading], 
        method: Optional[GPSImprovementMethod] = None
    ) -> GPSImprovementResult:
        """
        Improve GPS accuracy using specified method.
        
        Args:
            readings: List of GPS readings to process
            method: Improvement method to use (auto-select if None)
            
        Returns:
            GPSImprovementResult with improvement details
        """
        try:
            start_time = datetime.utcnow()
            
            if not readings:
                raise ValueError("No GPS readings provided")
            
            # Auto-select method if not specified
            if method is None:
                method = self._select_improvement_method(readings)
            
            # Calculate original accuracy (average of readings)
            original_accuracy = statistics.mean([r.accuracy for r in readings])
            
            # Apply improvement method
            improved_reading = await self._apply_improvement_method(readings, method)
            
            # Calculate improvement metrics
            improvement_percentage = ((original_accuracy - improved_reading.accuracy) / original_accuracy) * 100
            confidence_gain = self._calculate_confidence_gain(readings, improved_reading)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            result = GPSImprovementResult(
                original_accuracy=original_accuracy,
                improved_accuracy=improved_reading.accuracy,
                improvement_percentage=improvement_percentage,
                method_used=method,
                confidence_gain=confidence_gain,
                processing_time_ms=processing_time
            )
            
            self.logger.info(f"GPS accuracy improved by {improvement_percentage:.1f}% using {method.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error improving GPS accuracy: {e}")
            raise
    
    async def monitor_gps_signal_quality(self, reading: GPSReading) -> Dict[str, Any]:
        """
        Monitor GPS signal quality in real-time.
        
        Args:
            reading: Current GPS reading
            
        Returns:
            Signal quality monitoring data
        """
        try:
            # Assess current signal quality
            signal_quality = self._assess_signal_quality(reading)
            
            # Calculate signal stability over time
            stability_score = self._calculate_signal_stability()
            
            # Detect signal degradation
            degradation_alerts = self._detect_signal_degradation(reading)
            
            # Generate signal quality report
            quality_report = {
                'current_quality': signal_quality,
                'stability_score': stability_score,
                'satellite_count': reading.satellite_count,
                'hdop': reading.hdop,
                'signal_strength': reading.signal_strength,
                'degradation_alerts': degradation_alerts,
                'recommendations': self._generate_signal_recommendations(reading, signal_quality),
                'timestamp': datetime.utcnow()
            }
            
            return quality_report
            
        except Exception as e:
            self.logger.error(f"Error monitoring GPS signal quality: {e}")
            raise
    
    def _determine_accuracy_level(self, accuracy: float) -> GPSAccuracyLevel:
        """Determine GPS accuracy level based on accuracy value."""
        for level, threshold in self.accuracy_thresholds.items():
            if accuracy <= threshold:
                return level
        return GPSAccuracyLevel.UNACCEPTABLE
    
    def _assess_signal_quality(self, reading: GPSReading) -> str:
        """Assess GPS signal quality based on multiple factors."""
        quality_score = 0
        factors = []
        
        # Satellite count factor
        if reading.satellite_count:
            if reading.satellite_count >= 8:
                quality_score += 3
                factors.append("excellent_satellites")
            elif reading.satellite_count >= 6:
                quality_score += 2
                factors.append("good_satellites")
            elif reading.satellite_count >= 4:
                quality_score += 1
                factors.append("fair_satellites")
            else:
                factors.append("poor_satellites")
        
        # HDOP factor
        if reading.hdop:
            if reading.hdop <= 1.5:
                quality_score += 3
                factors.append("excellent_hdop")
            elif reading.hdop <= 2.5:
                quality_score += 2
                factors.append("good_hdop")
            elif reading.hdop <= 4.0:
                quality_score += 1
                factors.append("fair_hdop")
            else:
                factors.append("poor_hdop")
        
        # Signal strength factor
        if reading.signal_strength:
            if reading.signal_strength >= -80:
                quality_score += 2
                factors.append("strong_signal")
            elif reading.signal_strength >= -90:
                quality_score += 1
                factors.append("moderate_signal")
            else:
                factors.append("weak_signal")
        
        # Determine overall quality
        if quality_score >= 7:
            return "excellent"
        elif quality_score >= 5:
            return "good"
        elif quality_score >= 3:
            return "fair"
        else:
            return "poor"
    
    def _calculate_confidence_score(self, reading: GPSReading, signal_quality: str) -> float:
        """Calculate confidence score for GPS reading."""
        base_confidence = 0.5
        
        # Accuracy factor
        accuracy_factor = max(0, 1 - (reading.accuracy / 100))
        
        # Signal quality factor
        quality_factors = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        quality_factor = quality_factors.get(signal_quality, 0.3)
        
        # Satellite count factor
        satellite_factor = 0.5
        if reading.satellite_count:
            satellite_factor = min(1.0, reading.satellite_count / 8)
        
        # HDOP factor
        hdop_factor = 0.5
        if reading.hdop:
            hdop_factor = max(0.1, 1 - (reading.hdop / 10))
        
        confidence = (base_confidence + accuracy_factor + quality_factor + satellite_factor + hdop_factor) / 5
        return min(1.0, max(0.0, confidence))
    
    def _generate_recommendations(self, reading: GPSReading, accuracy_level: GPSAccuracyLevel, signal_quality: str) -> List[str]:
        """Generate recommendations based on GPS assessment."""
        recommendations = []
        
        if accuracy_level == GPSAccuracyLevel.UNACCEPTABLE:
            recommendations.extend([
                "GPS accuracy is too poor for reliable field mapping",
                "Move to an area with better satellite visibility",
                "Wait for better weather conditions",
                "Consider using differential GPS or RTK correction"
            ])
        elif accuracy_level == GPSAccuracyLevel.POOR:
            recommendations.extend([
                "GPS accuracy is marginal for field mapping",
                "Take multiple readings and average them",
                "Avoid mapping during poor weather conditions",
                "Consider using a GPS receiver with better accuracy"
            ])
        elif accuracy_level == GPSAccuracyLevel.FAIR:
            recommendations.extend([
                "GPS accuracy is acceptable for general field mapping",
                "Consider taking multiple readings for better accuracy",
                "Monitor signal quality during mapping"
            ])
        elif accuracy_level == GPSAccuracyLevel.GOOD:
            recommendations.extend([
                "GPS accuracy is good for field mapping",
                "Current readings are suitable for most agricultural applications"
            ])
        else:  # EXCELLENT
            recommendations.append("GPS accuracy is excellent for precision field mapping")
        
        # Signal quality specific recommendations
        if signal_quality == "poor":
            recommendations.extend([
                "Signal quality is poor - wait for better satellite coverage",
                "Check for obstructions blocking satellite signals",
                "Consider using external GPS antenna"
            ])
        
        return recommendations
    
    def _suggest_improvement_methods(self, reading: GPSReading, accuracy_level: GPSAccuracyLevel) -> List[GPSImprovementMethod]:
        """Suggest GPS accuracy improvement methods."""
        methods = []
        
        if accuracy_level in [GPSAccuracyLevel.POOR, GPSAccuracyLevel.UNACCEPTABLE]:
            methods.extend([
                GPSImprovementMethod.MULTI_READING_AVERAGE,
                GPSImprovementMethod.DIFFERENTIAL_GPS,
                GPSImprovementMethod.RTK_CORRECTION
            ])
        elif accuracy_level == GPSAccuracyLevel.FAIR:
            methods.extend([
                GPSImprovementMethod.MULTI_READING_AVERAGE,
                GPSImprovementMethod.SIGNAL_FILTERING
            ])
        elif accuracy_level == GPSAccuracyLevel.GOOD:
            methods.append(GPSImprovementMethod.MULTI_READING_AVERAGE)
        
        return methods
    
    def _select_improvement_method(self, readings: List[GPSReading]) -> GPSImprovementMethod:
        """Auto-select the best improvement method based on readings."""
        if len(readings) >= 5:
            return GPSImprovementMethod.MULTI_READING_AVERAGE
        elif any(r.satellite_count and r.satellite_count >= 6 for r in readings):
            return GPSImprovementMethod.DIFFERENTIAL_GPS
        else:
            return GPSImprovementMethod.SIGNAL_FILTERING
    
    async def _apply_improvement_method(self, readings: List[GPSReading], method: GPSImprovementMethod) -> GPSReading:
        """Apply the specified improvement method to readings."""
        if method == GPSImprovementMethod.MULTI_READING_AVERAGE:
            return self._apply_multi_reading_average(readings)
        elif method == GPSImprovementMethod.DIFFERENTIAL_GPS:
            return self._apply_differential_gps(readings)
        elif method == GPSImprovementMethod.RTK_CORRECTION:
            return self._apply_rtk_correction(readings)
        elif method == GPSImprovementMethod.SIGNAL_FILTERING:
            return self._apply_signal_filtering(readings)
        else:
            raise ValueError(f"Unknown improvement method: {method}")
    
    def _apply_multi_reading_average(self, readings: List[GPSReading]) -> GPSReading:
        """Apply multi-reading averaging to improve accuracy."""
        if len(readings) < 2:
            return readings[0]
        
        # Calculate weighted average based on accuracy
        weights = [1 / r.accuracy for r in readings]
        total_weight = sum(weights)
        
        avg_lat = sum(r.latitude * w for r, w in zip(readings, weights)) / total_weight
        avg_lng = sum(r.longitude * w for r, w in zip(readings, weights)) / total_weight
        
        # Calculate improved accuracy (typically 1/sqrt(n) improvement)
        original_accuracies = [r.accuracy for r in readings]
        improved_accuracy = statistics.mean(original_accuracies) / math.sqrt(len(readings))
        
        # Use metadata from most recent reading
        latest_reading = max(readings, key=lambda r: r.timestamp)
        
        return GPSReading(
            latitude=avg_lat,
            longitude=avg_lng,
            accuracy=improved_accuracy,
            altitude=latest_reading.altitude,
            timestamp=datetime.utcnow(),
            satellite_count=latest_reading.satellite_count,
            signal_strength=latest_reading.signal_strength,
            hdop=latest_reading.hdop,
            vdop=latest_reading.vdop
        )
    
    def _apply_differential_gps(self, readings: List[GPSReading]) -> GPSReading:
        """Apply differential GPS correction (simulated)."""
        # In a real implementation, this would connect to differential GPS services
        # For now, we simulate improvement based on satellite count
        base_reading = readings[-1]  # Use most recent reading
        
        # Simulate differential GPS improvement
        improvement_factor = 0.7  # 70% improvement
        if base_reading.satellite_count and base_reading.satellite_count >= 6:
            improvement_factor = 0.8  # Better improvement with more satellites
        
        improved_accuracy = base_reading.accuracy * (1 - improvement_factor)
        
        return GPSReading(
            latitude=base_reading.latitude,
            longitude=base_reading.longitude,
            accuracy=improved_accuracy,
            altitude=base_reading.altitude,
            timestamp=datetime.utcnow(),
            satellite_count=base_reading.satellite_count,
            signal_strength=base_reading.signal_strength,
            hdop=base_reading.hdop,
            vdop=base_reading.vdop
        )
    
    def _apply_rtk_correction(self, readings: List[GPSReading]) -> GPSReading:
        """Apply RTK (Real-Time Kinematic) correction (simulated)."""
        # RTK provides centimeter-level accuracy
        base_reading = readings[-1]
        
        # Simulate RTK correction to centimeter accuracy
        improved_accuracy = 0.02  # 2cm accuracy
        
        return GPSReading(
            latitude=base_reading.latitude,
            longitude=base_reading.longitude,
            accuracy=improved_accuracy,
            altitude=base_reading.altitude,
            timestamp=datetime.utcnow(),
            satellite_count=base_reading.satellite_count,
            signal_strength=base_reading.signal_strength,
            hdop=base_reading.hdop,
            vdop=base_reading.vdop
        )
    
    def _apply_signal_filtering(self, readings: List[GPSReading]) -> GPSReading:
        """Apply signal filtering to reduce noise."""
        if len(readings) < 3:
            return readings[-1]
        
        # Apply median filter to reduce outliers
        latitudes = [r.latitude for r in readings]
        longitudes = [r.longitude for r in readings]
        accuracies = [r.accuracy for r in readings]
        
        filtered_lat = statistics.median(latitudes)
        filtered_lng = statistics.median(longitudes)
        filtered_accuracy = statistics.median(accuracies)
        
        # Use metadata from most recent reading
        latest_reading = readings[-1]
        
        return GPSReading(
            latitude=filtered_lat,
            longitude=filtered_lng,
            accuracy=filtered_accuracy,
            altitude=latest_reading.altitude,
            timestamp=datetime.utcnow(),
            satellite_count=latest_reading.satellite_count,
            signal_strength=latest_reading.signal_strength,
            hdop=latest_reading.hdop,
            vdop=latest_reading.vdop
        )
    
    def _calculate_confidence_gain(self, original_readings: List[GPSReading], improved_reading: GPSReading) -> float:
        """Calculate confidence gain from improvement."""
        original_confidence = statistics.mean([self._calculate_confidence_score(r, self._assess_signal_quality(r)) for r in original_readings])
        improved_confidence = self._calculate_confidence_score(improved_reading, self._assess_signal_quality(improved_reading))
        
        return improved_confidence - original_confidence
    
    def _store_reading(self, reading: GPSReading):
        """Store reading in history for analysis."""
        self.reading_history.append(reading)
        
        # Keep only recent readings
        if len(self.reading_history) > self.max_history_size:
            self.reading_history = self.reading_history[-self.max_history_size:]
    
    def _calculate_signal_stability(self) -> float:
        """Calculate signal stability over recent readings."""
        if len(self.reading_history) < 3:
            return 0.5
        
        recent_readings = self.reading_history[-10:]  # Last 10 readings
        
        # Calculate variance in accuracy
        accuracies = [r.accuracy for r in recent_readings]
        if len(accuracies) < 2:
            return 0.5
        
        variance = statistics.variance(accuracies)
        mean_accuracy = statistics.mean(accuracies)
        
        # Stability score (lower variance = higher stability)
        stability_score = max(0, 1 - (variance / (mean_accuracy ** 2)))
        return min(1.0, stability_score)
    
    def _detect_signal_degradation(self, reading: GPSReading) -> List[str]:
        """Detect GPS signal degradation patterns."""
        alerts = []
        
        if len(self.reading_history) < 3:
            return alerts
        
        recent_readings = self.reading_history[-5:]
        
        # Check for decreasing accuracy trend
        accuracies = [r.accuracy for r in recent_readings]
        if len(accuracies) >= 3:
            # Simple trend detection
            if accuracies[-1] > accuracies[-2] > accuracies[-3]:
                alerts.append("GPS accuracy is degrading")
        
        # Check for satellite count decrease
        satellite_counts = [r.satellite_count for r in recent_readings if r.satellite_count]
        if len(satellite_counts) >= 2:
            if satellite_counts[-1] < satellite_counts[-2]:
                alerts.append("Satellite count is decreasing")
        
        # Check for HDOP increase
        hdops = [r.hdop for r in recent_readings if r.hdop]
        if len(hdops) >= 2:
            if hdops[-1] > hdops[-2]:
                alerts.append("HDOP is increasing (signal quality degrading)")
        
        return alerts
    
    def _generate_signal_recommendations(self, reading: GPSReading, signal_quality: str) -> List[str]:
        """Generate signal-specific recommendations."""
        recommendations = []
        
        if signal_quality == "poor":
            recommendations.extend([
                "Move to an open area with clear sky view",
                "Check for obstructions (buildings, trees, hills)",
                "Wait for better satellite constellation",
                "Consider using external GPS antenna"
            ])
        elif signal_quality == "fair":
            recommendations.extend([
                "Monitor signal quality during mapping",
                "Take multiple readings for better accuracy",
                "Avoid mapping during poor weather"
            ])
        
        return recommendations
    
    async def verify_location_accuracy(self, readings: List[GPSReading]) -> Dict[str, Any]:
        """
        Advanced location verification with agricultural area validation.
        
        Args:
            readings: List of GPS readings to verify
            
        Returns:
            Verification result with confidence scoring and agricultural validation
        """
        try:
            if not readings:
                raise ValueError("No GPS readings provided for verification")
            
            # Basic verification checks
            verification_result = {
                'verified': False,
                'confidence_score': 0.0,
                'verification_methods': [],
                'agricultural_validation': {},
                'reasonableness_checks': {},
                'duplicate_detection': {},
                'recommendations': [],
                'warnings': []
            }
            
            # 1. Multi-reading consistency check
            consistency_result = await self._check_reading_consistency(readings)
            verification_result['verification_methods'].append('consistency_check')
            verification_result['confidence_score'] += consistency_result['confidence_contribution']
            
            # 2. Agricultural area validation
            agricultural_result = await self._validate_agricultural_area(readings[0])
            verification_result['agricultural_validation'] = agricultural_result
            verification_result['verification_methods'].append('agricultural_validation')
            verification_result['confidence_score'] += agricultural_result['confidence_contribution']
            
            # 3. Reasonableness checks
            reasonableness_result = await self._check_location_reasonableness(readings[0])
            verification_result['reasonableness_checks'] = reasonableness_result
            verification_result['verification_methods'].append('reasonableness_check')
            verification_result['confidence_score'] += reasonableness_result['confidence_contribution']
            
            # 4. Duplicate detection
            duplicate_result = await self._detect_duplicate_locations(readings[0])
            verification_result['duplicate_detection'] = duplicate_result
            verification_result['verification_methods'].append('duplicate_detection')
            
            # 5. Overall verification decision
            verification_result['verified'] = verification_result['confidence_score'] >= self.verification_config['min_confidence_threshold']
            
            # 6. Generate recommendations and warnings
            verification_result['recommendations'] = self._generate_verification_recommendations(verification_result)
            verification_result['warnings'] = self._generate_verification_warnings(verification_result)
            
            self.logger.info(f"Location verification completed: {verification_result['verified']} "
                           f"(confidence: {verification_result['confidence_score']:.2f})")
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Error in location verification: {e}")
            raise
    
    async def _check_reading_consistency(self, readings: List[GPSReading]) -> Dict[str, Any]:
        """Check consistency across multiple GPS readings."""
        if len(readings) < 2:
            return {
                'consistent': True,
                'confidence_contribution': 0.3,
                'max_distance_variation': 0,
                'average_accuracy': readings[0].accuracy if readings else 0
            }
        
        # Calculate distances between readings
        distances = []
        for i in range(len(readings) - 1):
            dist = self._calculate_distance(
                readings[i].latitude, readings[i].longitude,
                readings[i+1].latitude, readings[i+1].longitude
            )
            distances.append(dist)
        
        max_distance = max(distances) if distances else 0
        avg_distance = statistics.mean(distances) if distances else 0
        
        # Determine consistency
        consistent = max_distance <= self.verification_config['max_distance_variation']
        
        # Calculate confidence contribution
        if consistent:
            confidence_contribution = 0.4
        elif max_distance <= self.verification_config['max_distance_variation'] * 2:
            confidence_contribution = 0.2
        else:
            confidence_contribution = 0.0
        
        return {
            'consistent': consistent,
            'confidence_contribution': confidence_contribution,
            'max_distance_variation': max_distance,
            'average_distance': avg_distance,
            'readings_count': len(readings)
        }
    
    async def _validate_agricultural_area(self, reading: GPSReading) -> Dict[str, Any]:
        """Validate that location is in an agricultural area."""
        lat, lng = reading.latitude, reading.longitude
        
        # Check against agricultural regions
        agricultural_score = 0.0
        region_match = None
        
        for region_name, region_data in self.agricultural_regions.items():
            if self._point_in_region(lat, lng, region_data['bounds']):
                agricultural_score = region_data['confidence']
                region_match = region_name
                break
        
        # Fallback to coordinate-based agricultural area detection
        if agricultural_score == 0.0:
            agricultural_score = self._estimate_agricultural_suitability(lat, lng)
        
        # Determine confidence contribution
        if agricultural_score >= self.verification_config['agricultural_area_confidence_threshold']:
            confidence_contribution = 0.3
        elif agricultural_score >= 0.5:
            confidence_contribution = 0.15
        else:
            confidence_contribution = 0.0
        
        return {
            'is_agricultural': agricultural_score >= 0.5,
            'agricultural_score': agricultural_score,
            'confidence_contribution': confidence_contribution,
            'region_match': region_match,
            'suitability_factors': self._analyze_agricultural_factors(lat, lng)
        }
    
    async def _check_location_reasonableness(self, reading: GPSReading) -> Dict[str, Any]:
        """Check if location coordinates are reasonable for agricultural use."""
        lat, lng = reading.latitude, reading.longitude
        issues = []
        confidence_contribution = 0.2
        
        # Check for obviously invalid coordinates
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            issues.append("Invalid coordinate ranges")
            confidence_contribution = 0.0
        
        # Check for ocean coordinates (simplified)
        if self._is_likely_ocean(lat, lng):
            issues.append("Location appears to be in ocean")
            confidence_contribution = 0.0
        
        # Check for extreme latitudes
        if abs(lat) > 70:
            issues.append("Extreme latitude - limited agricultural potential")
            confidence_contribution *= 0.5
        
        # Check for polar regions
        if abs(lat) > 66.5:
            issues.append("Polar region - very limited agricultural potential")
            confidence_contribution *= 0.3
        
        # Check for reasonable agricultural latitudes
        if 25 <= abs(lat) <= 60:
            confidence_contribution *= 1.2  # Bonus for good agricultural latitudes
        
        return {
            'reasonable': len(issues) == 0,
            'confidence_contribution': min(confidence_contribution, 0.2),
            'issues': issues,
            'latitude_category': self._categorize_latitude(lat),
            'longitude_category': self._categorize_longitude(lng)
        }
    
    async def _detect_duplicate_locations(self, reading: GPSReading) -> Dict[str, Any]:
        """Detect if location is duplicate of existing locations."""
        lat, lng = reading.latitude, reading.longitude
        duplicates = []
        
        # Check against reading history
        for historical_reading in self.reading_history:
            distance = self._calculate_distance(
                lat, lng,
                historical_reading.latitude, historical_reading.longitude
            )
            
            if distance <= self.verification_config['duplicate_detection_threshold']:
                duplicates.append({
                    'distance': distance,
                    'timestamp': historical_reading.timestamp,
                    'accuracy': historical_reading.accuracy
                })
        
        return {
            'is_duplicate': len(duplicates) > 0,
            'duplicate_count': len(duplicates),
            'duplicates': duplicates,
            'threshold_used': self.verification_config['duplicate_detection_threshold']
        }
    
    def _generate_verification_recommendations(self, verification_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on verification results."""
        recommendations = []
        
        # Agricultural validation recommendations
        agricultural = verification_result['agricultural_validation']
        if not agricultural['is_agricultural']:
            recommendations.append("Location may not be suitable for agricultural operations")
            recommendations.append("Verify coordinates are correct for your farming operation")
        
        # Consistency recommendations
        if 'consistency_check' in verification_result['verification_methods']:
            recommendations.append("Take multiple GPS readings for better accuracy verification")
        
        # Reasonableness recommendations
        reasonableness = verification_result['reasonableness_checks']
        if not reasonableness['reasonable']:
            recommendations.extend([
                "Check coordinate format and coordinate system",
                "Verify location using map interface",
                "Ensure GPS device is properly calibrated"
            ])
        
        # Duplicate detection recommendations
        duplicate = verification_result['duplicate_detection']
        if duplicate['is_duplicate']:
            recommendations.append("Location appears to be duplicate of previous reading")
            recommendations.append("Consider if this is intentional or requires verification")
        
        return recommendations
    
    def _generate_verification_warnings(self, verification_result: Dict[str, Any]) -> List[str]:
        """Generate warnings based on verification results."""
        warnings = []
        
        # Low confidence warnings
        if verification_result['confidence_score'] < 0.5:
            warnings.append("Low confidence in location verification")
        
        # Agricultural area warnings
        agricultural = verification_result['agricultural_validation']
        if agricultural['agricultural_score'] < 0.3:
            warnings.append("Location has very low agricultural suitability score")
        
        # Reasonableness warnings
        reasonableness = verification_result['reasonableness_checks']
        if reasonableness['issues']:
            warnings.extend([f"Location issue: {issue}" for issue in reasonableness['issues']])
        
        return warnings
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in meters using Haversine formula."""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _point_in_region(self, lat: float, lng: float, bounds: Dict[str, float]) -> bool:
        """Check if point is within region bounds."""
        return (bounds['min_lat'] <= lat <= bounds['max_lat'] and
                bounds['min_lng'] <= lng <= bounds['max_lng'])
    
    def _estimate_agricultural_suitability(self, lat: float, lng: float) -> float:
        """Estimate agricultural suitability based on coordinates."""
        # Simplified agricultural suitability estimation
        suitability = 0.5  # Base suitability
        
        # Continental US agricultural regions
        if 25 <= lat <= 49 and -125 <= lng <= -66:
            suitability = 0.8
            
            # Corn Belt bonus
            corn_belt_regions = [
                (40.375, 43.501, -96.639, -90.140),  # Iowa
                (36.970, 42.508, -91.513, -87.494),  # Illinois
                (37.913, 41.761, -95.774, -89.098),  # Missouri
            ]
            
            for min_lat, max_lat, min_lng, max_lng in corn_belt_regions:
                if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                    suitability = 0.95
                    break
        
        # Adjust for extreme latitudes
        if abs(lat) > 60:
            suitability *= 0.3
        elif abs(lat) > 50:
            suitability *= 0.7
        
        return suitability
    
    def _analyze_agricultural_factors(self, lat: float, lng: float) -> Dict[str, Any]:
        """Analyze agricultural factors for location."""
        return {
            'latitude_suitability': self._assess_latitude_suitability(lat),
            'climate_zone_estimate': self._estimate_climate_zone(lat),
            'growing_season_estimate': self._estimate_growing_season(lat),
            'precipitation_estimate': self._estimate_precipitation(lat, lng)
        }
    
    def _assess_latitude_suitability(self, lat: float) -> str:
        """Assess latitude suitability for agriculture."""
        abs_lat = abs(lat)
        if 25 <= abs_lat <= 45:
            return "excellent"
        elif 20 <= abs_lat <= 50:
            return "good"
        elif 15 <= abs_lat <= 55:
            return "fair"
        else:
            return "poor"
    
    def _estimate_climate_zone(self, lat: float) -> str:
        """Estimate climate zone based on latitude."""
        if lat >= 48:
            return "3a-4b"
        elif lat >= 45:
            return "4a-5b"
        elif lat >= 42:
            return "5a-6a"
        elif lat >= 39:
            return "6a-7a"
        elif lat >= 36:
            return "7a-8a"
        elif lat >= 33:
            return "8a-9a"
        elif lat >= 30:
            return "9a-10a"
        else:
            return "10a+"
    
    def _estimate_growing_season(self, lat: float) -> int:
        """Estimate growing season length in days."""
        abs_lat = abs(lat)
        if abs_lat <= 30:
            return 365  # Year-round
        elif abs_lat <= 35:
            return 300
        elif abs_lat <= 40:
            return 250
        elif abs_lat <= 45:
            return 200
        elif abs_lat <= 50:
            return 150
        elif abs_lat <= 55:
            return 120
        else:
            return 90
    
    def _estimate_precipitation(self, lat: float, lng: float) -> str:
        """Estimate precipitation category."""
        # Simplified precipitation estimation
        if 25 <= lat <= 49 and -125 <= lng <= -66:  # Continental US
            if lng < -100:  # Western US
                return "low"
            elif lng < -80:  # Central US
                return "moderate"
            else:  # Eastern US
                return "high"
        else:
            return "unknown"
    
    def _is_likely_ocean(self, lat: float, lng: float) -> bool:
        """Check if coordinates are likely in ocean."""
        # Simplified ocean detection - exclude continental US
        if 25 <= lat <= 49 and -125 <= lng <= -66:  # Continental US
            return False
        
        # Simplified ocean detection
        ocean_regions = [
            {'lat_range': (-60, 70), 'lon_range': (-80, 20)},  # Atlantic
            {'lat_range': (-60, 70), 'lon_range': (-180, -80)},  # Pacific West
            {'lat_range': (-60, 70), 'lon_range': (120, 180)},  # Pacific East
        ]
        
        for region in ocean_regions:
            if (region['lat_range'][0] <= lat <= region['lat_range'][1] and
                region['lon_range'][0] <= lng <= region['lon_range'][1]):
                return True
        return False
    
    def _categorize_latitude(self, lat: float) -> str:
        """Categorize latitude for agricultural purposes."""
        abs_lat = abs(lat)
        if abs_lat <= 25:
            return "tropical"
        elif abs_lat <= 35:
            return "subtropical"
        elif abs_lat <= 50:
            return "temperate"
        elif abs_lat <= 60:
            return "cool_temperate"
        else:
            return "polar"
    
    def _categorize_longitude(self, lng: float) -> str:
        """Categorize longitude for agricultural purposes."""
        if -125 <= lng <= -66:  # Continental US
            return "continental_us"
        elif -141 <= lng <= -52:  # Canada
            return "canada"
        elif -10 <= lng <= 40:  # Europe
            return "europe"
        else:
            return "other"
    
    def _load_agricultural_regions(self) -> Dict[str, Dict]:
        """Load agricultural region data."""
        # Simplified agricultural regions data
        # In production, this would load from USDA/NASS data
        return {
            'corn_belt': {
                'bounds': {'min_lat': 36.0, 'max_lat': 44.0, 'min_lng': -97.0, 'max_lng': -87.0},
                'confidence': 0.95,
                'description': 'Primary corn and soybean production region'
            },
            'wheat_belt': {
                'bounds': {'min_lat': 35.0, 'max_lat': 49.0, 'min_lng': -110.0, 'max_lng': -95.0},
                'confidence': 0.9,
                'description': 'Major wheat production region'
            },
            'cotton_belt': {
                'bounds': {'min_lat': 30.0, 'max_lat': 37.0, 'min_lng': -100.0, 'max_lng': -75.0},
                'confidence': 0.85,
                'description': 'Cotton production region'
            }
        }
    
    def _generate_agricultural_recommendations(self, agricultural_result: Dict[str, Any], agricultural_factors: Dict[str, Any]) -> List[str]:
        """Generate agricultural recommendations based on validation results."""
        recommendations = []
        
        # Agricultural area recommendations
        if agricultural_result['is_agricultural']:
            if agricultural_result['agricultural_score'] >= 0.8:
                recommendations.append("Excellent agricultural location with high suitability")
                recommendations.append("Suitable for most major crops and agricultural operations")
            elif agricultural_result['agricultural_score'] >= 0.6:
                recommendations.append("Good agricultural location with moderate suitability")
                recommendations.append("Consider soil testing and local climate conditions")
            else:
                recommendations.append("Fair agricultural location - verify local conditions")
                recommendations.append("Consult local agricultural extension services")
        else:
            recommendations.append("Location may not be suitable for traditional agriculture")
            recommendations.append("Consider specialized agricultural practices or alternative uses")
        
        # Climate zone recommendations
        climate_zone = agricultural_factors.get('climate_zone_estimate', 'unknown')
        if climate_zone.startswith('3') or climate_zone.startswith('4'):
            recommendations.append("Cold climate zone - select cold-hardy crop varieties")
            recommendations.append("Plan for shorter growing seasons")
        elif climate_zone.startswith('9') or climate_zone.startswith('10'):
            recommendations.append("Warm climate zone - consider heat-tolerant varieties")
            recommendations.append("May support year-round growing in some areas")
        
        # Growing season recommendations
        growing_season = agricultural_factors.get('growing_season_estimate', 0)
        if growing_season < 120:
            recommendations.append("Short growing season - select early-maturing varieties")
            recommendations.append("Consider season extension techniques")
        elif growing_season > 300:
            recommendations.append("Long growing season - multiple crop cycles possible")
            recommendations.append("Consider succession planting strategies")
        
        # Precipitation recommendations
        precipitation = agricultural_factors.get('precipitation_estimate', 'unknown')
        if precipitation == 'low':
            recommendations.append("Low precipitation area - irrigation planning essential")
            recommendations.append("Consider drought-tolerant crop varieties")
        elif precipitation == 'high':
            recommendations.append("High precipitation area - ensure good drainage")
            recommendations.append("Consider disease-resistant varieties")
        
        return recommendations