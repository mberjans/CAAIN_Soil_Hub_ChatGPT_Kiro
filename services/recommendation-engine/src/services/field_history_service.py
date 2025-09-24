"""
Field History Management Service
Handles field history input, validation, and management for crop rotation planning.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date
import logging
import asyncio
import json
from dataclasses import asdict

from ..models.rotation_models import (
    FieldHistoryRecord, FieldProfile, FieldHistoryRequest
)

logger = logging.getLogger(__name__)


class FieldHistoryService:
    """Service for managing field history data."""
    
    def __init__(self):
        self.field_profiles = {}  # In production, this would be a database
        self.validation_rules = self._initialize_validation_rules()
        self.data_quality_thresholds = {
            'minimum_years': 3,
            'required_fields': ['crop_name', 'year'],
            'recommended_fields': ['yield_amount', 'planting_date', 'harvest_date']
        }
    
    async def create_field_profile(
        self,
        field_id: str,
        field_name: str,
        farm_id: str,
        field_characteristics: Dict
    ) -> FieldProfile:
        """Create a new field profile."""
        
        try:
            field_profile = FieldProfile(
                field_id=field_id,
                field_name=field_name,
                farm_id=farm_id,
                size_acres=field_characteristics.get('size_acres', 0),
                soil_type=field_characteristics.get('soil_type'),
                drainage_class=field_characteristics.get('drainage_class'),
                slope_percent=field_characteristics.get('slope_percent'),
                irrigation_available=field_characteristics.get('irrigation_available', False),
                coordinates=field_characteristics.get('coordinates'),
                climate_zone=field_characteristics.get('climate_zone'),
                elevation_ft=field_characteristics.get('elevation_ft')
            )
            
            self.field_profiles[field_id] = field_profile
            
            logger.info(f"Created field profile for {field_name} ({field_id})")
            return field_profile
            
        except Exception as e:
            logger.error(f"Error creating field profile: {str(e)}")
            raise
    
    async def add_field_history_record(
        self,
        field_id: str,
        history_data: FieldHistoryRequest
    ) -> FieldHistoryRecord:
        """Add a field history record."""
        
        try:
            # Get field profile
            field_profile = self.field_profiles.get(field_id)
            if not field_profile:
                raise ValueError(f"Field {field_id} not found")
            
            # Validate history data
            validation_result = await self._validate_history_record(history_data, field_profile)
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid history data: {validation_result['errors']}")
            
            # Create history record
            history_record = FieldHistoryRecord(
                year=history_data.year,
                crop_name=history_data.crop_name,
                variety=history_data.variety,
                planting_date=history_data.planting_date,
                harvest_date=history_data.harvest_date,
                yield_amount=history_data.yield_amount,
                yield_units=history_data.yield_units,
                tillage_type=history_data.tillage_type,
                fertilizer_applications=history_data.fertilizer_applications,
                pesticide_applications=history_data.pesticide_applications,
                irrigation_used=history_data.irrigation_used,
                cover_crop=history_data.cover_crop,
                gross_revenue=history_data.gross_revenue,
                total_costs=history_data.total_costs,
                net_profit=history_data.net_profit,
                soil_test_results=history_data.soil_test_results,
                notes=history_data.notes
            )
            
            # Remove existing record for same year if it exists
            field_profile.history = [
                h for h in field_profile.history if h.year != history_data.year
            ]
            
            # Add new record
            field_profile.history.append(history_record)
            field_profile.last_updated = datetime.utcnow()
            
            logger.info(f"Added history record for field {field_id}, year {history_data.year}")
            return history_record
            
        except Exception as e:
            logger.error(f"Error adding field history record: {str(e)}")
            raise
    
    async def bulk_import_history(
        self,
        field_id: str,
        history_records: List[Dict]
    ) -> Dict[str, Any]:
        """Bulk import field history records."""
        
        try:
            results = {
                'successful': [],
                'failed': [],
                'warnings': [],
                'summary': {}
            }
            
            for record_data in history_records:
                try:
                    # Convert dict to FieldHistoryRequest
                    history_request = FieldHistoryRequest(**record_data)
                    
                    # Add record
                    record = await self.add_field_history_record(field_id, history_request)
                    results['successful'].append({
                        'year': record.year,
                        'crop': record.crop_name
                    })
                    
                except Exception as e:
                    results['failed'].append({
                        'data': record_data,
                        'error': str(e)
                    })
            
            # Generate summary
            results['summary'] = {
                'total_records': len(history_records),
                'successful_imports': len(results['successful']),
                'failed_imports': len(results['failed']),
                'success_rate': len(results['successful']) / len(history_records) if history_records else 0
            }
            
            # Add data quality assessment
            if results['successful']:
                quality_assessment = await self.assess_data_quality(field_id)
                results['data_quality'] = quality_assessment
            
            logger.info(f"Bulk import completed for field {field_id}: {results['summary']}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk import: {str(e)}")
            raise
    
    async def get_field_history(
        self,
        field_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[FieldHistoryRecord]:
        """Get field history records."""
        
        try:
            field_profile = self.field_profiles.get(field_id)
            if not field_profile:
                raise ValueError(f"Field {field_id} not found")
            
            history = field_profile.history
            
            # Filter by year range if specified
            if start_year or end_year:
                history = [
                    record for record in history
                    if (not start_year or record.year >= start_year) and
                       (not end_year or record.year <= end_year)
                ]
            
            # Sort by year
            history.sort(key=lambda x: x.year)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting field history: {str(e)}")
            raise
    
    async def update_field_history_record(
        self,
        field_id: str,
        year: int,
        updates: Dict
    ) -> FieldHistoryRecord:
        """Update an existing field history record."""
        
        try:
            field_profile = self.field_profiles.get(field_id)
            if not field_profile:
                raise ValueError(f"Field {field_id} not found")
            
            # Find existing record
            record_index = None
            for i, record in enumerate(field_profile.history):
                if record.year == year:
                    record_index = i
                    break
            
            if record_index is None:
                raise ValueError(f"No history record found for year {year}")
            
            # Update record
            existing_record = field_profile.history[record_index]
            
            # Update fields
            for field_name, value in updates.items():
                if hasattr(existing_record, field_name):
                    setattr(existing_record, field_name, value)
            
            field_profile.last_updated = datetime.utcnow()
            
            logger.info(f"Updated history record for field {field_id}, year {year}")
            return existing_record
            
        except Exception as e:
            logger.error(f"Error updating field history record: {str(e)}")
            raise
    
    async def delete_field_history_record(
        self,
        field_id: str,
        year: int
    ) -> bool:
        """Delete a field history record."""
        
        try:
            field_profile = self.field_profiles.get(field_id)
            if not field_profile:
                raise ValueError(f"Field {field_id} not found")
            
            # Remove record
            original_count = len(field_profile.history)
            field_profile.history = [
                record for record in field_profile.history if record.year != year
            ]
            
            if len(field_profile.history) == original_count:
                raise ValueError(f"No history record found for year {year}")
            
            field_profile.last_updated = datetime.utcnow()
            
            logger.info(f"Deleted history record for field {field_id}, year {year}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting field history record: {str(e)}")
            raise
    
    async def assess_data_quality(self, field_id: str) -> Dict[str, Any]:
        """Assess the quality of field history data."""
        
        try:
            field_profile = self.field_profiles.get(field_id)
            if not field_profile:
                raise ValueError(f"Field {field_id} not found")
            
            history = field_profile.history
            
            if not history:
                return {
                    'overall_score': 0.0,
                    'completeness': 0.0,
                    'consistency': 0.0,
                    'recency': 0.0,
                    'issues': ['No history data available'],
                    'recommendations': ['Add field history data to enable rotation planning']
                }
            
            # Assess completeness
            completeness_score = self._assess_completeness(history)
            
            # Assess consistency
            consistency_score = self._assess_consistency(history)
            
            # Assess recency
            recency_score = self._assess_recency(history)
            
            # Calculate overall score
            overall_score = (completeness_score + consistency_score + recency_score) / 3
            
            # Identify issues and recommendations
            issues = []
            recommendations = []
            
            if len(history) < self.data_quality_thresholds['minimum_years']:
                issues.append(f"Insufficient history data ({len(history)} years, need {self.data_quality_thresholds['minimum_years']})")
                recommendations.append("Add more years of field history data")
            
            if completeness_score < 0.7:
                issues.append("Missing key data fields in history records")
                recommendations.append("Complete missing yield, planting, and harvest date information")
            
            if consistency_score < 0.7:
                issues.append("Inconsistent data patterns detected")
                recommendations.append("Review and verify data for accuracy and consistency")
            
            current_year = datetime.now().year
            most_recent_year = max(record.year for record in history)
            if current_year - most_recent_year > 2:
                issues.append("History data is not current")
                recommendations.append("Add recent field history data")
            
            return {
                'overall_score': overall_score,
                'completeness': completeness_score,
                'consistency': consistency_score,
                'recency': recency_score,
                'years_of_data': len(history),
                'most_recent_year': most_recent_year,
                'issues': issues,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {str(e)}")
            raise
    
    async def get_crop_sequence_analysis(
        self,
        field_id: str,
        years: int = 10
    ) -> Dict[str, Any]:
        """Analyze crop sequence patterns in field history."""
        
        try:
            history = await self.get_field_history(field_id)
            
            if not history:
                return {'error': 'No history data available'}
            
            # Get recent crop sequence
            recent_history = [
                record for record in history 
                if record.year >= (datetime.now().year - years)
            ]
            recent_history.sort(key=lambda x: x.year)
            
            crop_sequence = [record.crop_name for record in recent_history]
            
            # Analyze patterns
            analysis = {
                'crop_sequence': crop_sequence,
                'years_analyzed': len(crop_sequence),
                'unique_crops': len(set(crop_sequence)),
                'crop_frequency': {},
                'rotation_patterns': [],
                'potential_issues': [],
                'recommendations': []
            }
            
            # Calculate crop frequency
            for crop in crop_sequence:
                analysis['crop_frequency'][crop] = analysis['crop_frequency'].get(crop, 0) + 1
            
            # Detect rotation patterns
            if len(crop_sequence) >= 4:
                patterns = self._detect_rotation_patterns(crop_sequence)
                analysis['rotation_patterns'] = patterns
            
            # Identify potential issues
            issues = self._identify_sequence_issues(crop_sequence)
            analysis['potential_issues'] = issues
            
            # Generate recommendations
            recommendations = self._generate_sequence_recommendations(crop_sequence, analysis)
            analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing crop sequence: {str(e)}")
            raise
    
    def _initialize_validation_rules(self) -> Dict:
        """Initialize field history validation rules."""
        
        return {
            'year_range': (1900, 2100),
            'yield_range': (0, 1000),  # bu/acre or equivalent
            'valid_tillage_types': [
                'conventional', 'no_till', 'minimum_till', 'strip_till', 'ridge_till'
            ],
            'valid_yield_units': [
                'bu/acre', 'tons/acre', 'cwt/acre', 'lbs/acre', 'kg/ha', 'tons/ha'
            ]
        }
    
    async def _validate_history_record(
        self,
        history_data: FieldHistoryRequest,
        field_profile: FieldProfile
    ) -> Dict[str, Any]:
        """Validate field history record data."""
        
        errors = []
        warnings = []
        
        # Year validation
        current_year = datetime.now().year
        if not (1900 <= history_data.year <= current_year + 1):
            errors.append(f"Invalid year: {history_data.year}")
        
        # Crop name validation
        if not history_data.crop_name or len(history_data.crop_name.strip()) == 0:
            errors.append("Crop name is required")
        
        # Date validation
        if history_data.planting_date and history_data.harvest_date:
            if history_data.harvest_date <= history_data.planting_date:
                errors.append("Harvest date must be after planting date")
        
        # Yield validation
        if history_data.yield_amount is not None:
            if history_data.yield_amount < 0:
                errors.append("Yield amount cannot be negative")
            elif history_data.yield_amount > 1000:
                warnings.append("Unusually high yield amount")
        
        # Economic validation
        if history_data.gross_revenue is not None and history_data.gross_revenue < 0:
            errors.append("Gross revenue cannot be negative")
        
        if history_data.total_costs is not None and history_data.total_costs < 0:
            errors.append("Total costs cannot be negative")
        
        # Check for duplicate year
        existing_years = [record.year for record in field_profile.history]
        if history_data.year in existing_years:
            warnings.append(f"Record for year {history_data.year} already exists and will be replaced")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _assess_completeness(self, history: List[FieldHistoryRecord]) -> float:
        """Assess completeness of field history data."""
        
        if not history:
            return 0.0
        
        required_fields = self.data_quality_thresholds['required_fields']
        recommended_fields = self.data_quality_thresholds['recommended_fields']
        
        total_score = 0.0
        
        for record in history:
            record_score = 0.0
            
            # Check required fields (weight: 0.6)
            required_complete = 0
            for field in required_fields:
                if hasattr(record, field) and getattr(record, field) is not None:
                    required_complete += 1
            record_score += (required_complete / len(required_fields)) * 0.6
            
            # Check recommended fields (weight: 0.4)
            recommended_complete = 0
            for field in recommended_fields:
                if hasattr(record, field) and getattr(record, field) is not None:
                    recommended_complete += 1
            record_score += (recommended_complete / len(recommended_fields)) * 0.4
            
            total_score += record_score
        
        return total_score / len(history)
    
    def _assess_consistency(self, history: List[FieldHistoryRecord]) -> float:
        """Assess consistency of field history data."""
        
        if len(history) < 2:
            return 1.0  # Can't assess consistency with less than 2 records
        
        consistency_score = 1.0
        
        # Check for reasonable yield variations
        yields = [record.yield_amount for record in history if record.yield_amount is not None]
        if len(yields) >= 2:
            yield_cv = self._calculate_coefficient_of_variation(yields)
            if yield_cv > 0.5:  # High variation
                consistency_score -= 0.2
        
        # Check for logical date sequences
        date_issues = 0
        for record in history:
            if record.planting_date and record.harvest_date:
                days_diff = (record.harvest_date - record.planting_date).days
                if days_diff < 30 or days_diff > 365:  # Unreasonable growing season
                    date_issues += 1
        
        if date_issues > 0:
            consistency_score -= (date_issues / len(history)) * 0.3
        
        return max(0.0, consistency_score)
    
    def _assess_recency(self, history: List[FieldHistoryRecord]) -> float:
        """Assess recency of field history data."""
        
        if not history:
            return 0.0
        
        current_year = datetime.now().year
        most_recent_year = max(record.year for record in history)
        years_since_last = current_year - most_recent_year
        
        if years_since_last <= 1:
            return 1.0
        elif years_since_last <= 3:
            return 0.8
        elif years_since_last <= 5:
            return 0.6
        else:
            return 0.3
    
    def _calculate_coefficient_of_variation(self, values: List[float]) -> float:
        """Calculate coefficient of variation for a list of values."""
        
        if not values or len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return 0.0
        
        variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
        std_dev = variance ** 0.5
        
        return std_dev / mean_val
    
    def _detect_rotation_patterns(self, crop_sequence: List[str]) -> List[Dict]:
        """Detect rotation patterns in crop sequence."""
        
        patterns = []
        
        # Look for repeating patterns of length 2-4
        for pattern_length in range(2, min(5, len(crop_sequence) // 2 + 1)):
            for start_idx in range(len(crop_sequence) - pattern_length * 2 + 1):
                pattern = crop_sequence[start_idx:start_idx + pattern_length]
                next_pattern = crop_sequence[start_idx + pattern_length:start_idx + pattern_length * 2]
                
                if pattern == next_pattern:
                    patterns.append({
                        'pattern': pattern,
                        'length': pattern_length,
                        'start_year': start_idx,
                        'confidence': 'high' if pattern_length >= 3 else 'medium'
                    })
        
        return patterns
    
    def _identify_sequence_issues(self, crop_sequence: List[str]) -> List[str]:
        """Identify potential issues in crop sequence."""
        
        issues = []
        
        # Check for monoculture (same crop multiple years)
        for i in range(len(crop_sequence) - 2):
            if crop_sequence[i] == crop_sequence[i + 1] == crop_sequence[i + 2]:
                issues.append(f"Continuous {crop_sequence[i]} for 3+ years may increase pest/disease pressure")
        
        # Check for lack of diversity
        unique_crops = set(crop_sequence)
        if len(unique_crops) < 2 and len(crop_sequence) >= 3:
            issues.append("Low crop diversity may limit rotation benefits")
        
        # Check for missing nitrogen-fixing crops
        legumes = ['soybean', 'alfalfa', 'clover', 'peas', 'beans']
        has_legumes = any(crop.lower() in [leg.lower() for leg in legumes] for crop in crop_sequence)
        if not has_legumes and len(crop_sequence) >= 3:
            issues.append("No nitrogen-fixing crops detected in rotation")
        
        return issues
    
    def _generate_sequence_recommendations(
        self,
        crop_sequence: List[str],
        analysis: Dict
    ) -> List[str]:
        """Generate recommendations based on crop sequence analysis."""
        
        recommendations = []
        
        # Diversity recommendations
        if analysis['unique_crops'] < 3 and len(crop_sequence) >= 4:
            recommendations.append("Consider adding more crop diversity to improve soil health and reduce pest pressure")
        
        # Nitrogen fixation recommendations
        legumes = ['soybean', 'alfalfa', 'clover', 'peas', 'beans']
        has_legumes = any(crop.lower() in [leg.lower() for leg in legumes] for crop in crop_sequence)
        if not has_legumes:
            recommendations.append("Include nitrogen-fixing crops (legumes) to reduce fertilizer needs")
        
        # Break crop recommendations
        if len(set(crop_sequence)) == 1:
            recommendations.append("Introduce break crops to interrupt pest and disease cycles")
        
        # Cover crop recommendations
        recommendations.append("Consider cover crops between cash crops to improve soil health")
        
        return recommendations


# Global service instance
field_history_service = FieldHistoryService()