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
    and accuracy improvement algorithms for agricultural field mapping.
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
        
        self.logger.info("GPS accuracy service initialized")
    
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