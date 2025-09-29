"""
Comprehensive tests for Soil Management Assessment Service

Tests cover all aspects of soil management practice assessment,
scoring, and improvement recommendations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from uuid import uuid4
from decimal import Decimal

from src.services.soil_assessment_service import SoilManagementAssessmentService
from src.models.soil_assessment_models import (
    SoilAssessmentRequest,
    SoilAssessmentResponse,
    TillagePracticeAssessment,
    CoverCropAssessment,
    OrganicMatterAssessment,
    SoilCompactionAssessment,
    DrainageAssessment,
    SoilHealthScore,
    ImprovementOpportunity,
    AssessmentReport,
    TillageType,
    CompactionLevel,
    DrainageClass,
    PriorityLevel,
    SoilHealthGrade
)


class TestSoilManagementAssessmentService:
    """Test suite for Soil Management Assessment Service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilManagementAssessmentService()
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_farm_id(self):
        """Sample farm ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_assessment_request(self, sample_field_id, sample_farm_id):
        """Sample assessment request for testing."""
        return SoilAssessmentRequest(
            field_id=sample_field_id,
            farm_location_id=sample_farm_id,
            tillage_practices={
                'tillage_type': 'conventional',
                'frequency_per_year': 3,
                'average_depth_inches': 6,
                'equipment_type': 'moldboard_plow'
            },
            cover_crop_practices={
                'cover_crops_used': False,
                'species': [],
                'planting_timing': 'fall',
                'termination_timing': 'spring',
                'biomass_production_lbs_per_acre': 0
            },
            organic_matter_data={
                'current_om_percent': 2.5,
                'target_om_percent': 4.0,
                'management_practices': ['crop_rotation'],
                'manure_applications_per_year': 0,
                'compost_applications_per_year': 0
            },
            compaction_data={
                'compaction_level': 'moderate',
                'bulk_density_g_cm3': 1.4,
                'penetration_resistance_psi': 250,
                'management_practices': []
            },
            drainage_data={
                'drainage_class': 'moderately_well_drained',
                'surface_drainage': 'adequate',
                'subsurface_drainage': 'none',
                'management_practices': []
            },
            include_recommendations=True,
            assessment_depth_months=12
        )
    
    @pytest.fixture
    def sample_field_data(self):
        """Sample field characteristics data."""
        return {
            'field_id': uuid4(),
            'soil_type': 'clay_loam',
            'slope_percent': 2.0,
            'field_size_acres': 40.0,
            'climate_zone': '6a'
        }
    
    @pytest.fixture
    def sample_soil_data(self):
        """Sample soil data."""
        return {
            'field_id': uuid4(),
            'soil_series': 'Marshall',
            'drainage_class': 'moderately_well_drained',
            'water_holding_capacity': 0.18,
            'organic_matter': 2.5
        }
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.soil_ph_service is not None
        assert service.usda_soil_service is not None
        assert service.weather_service is not None
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_assess_current_practices_comprehensive(self, service, sample_assessment_request):
        """Test comprehensive soil management practice assessment."""
        await service.initialize()
        
        with patch.object(service, '_get_field_characteristics') as mock_field, \
             patch.object(service, '_get_soil_data') as mock_soil:
            
            mock_field.return_value = {
                'field_id': sample_assessment_request.field_id,
                'soil_type': 'clay_loam',
                'slope_percent': 2.0,
                'field_size_acres': 40.0,
                'climate_zone': '6a'
            }
            
            mock_soil.return_value = {
                'field_id': sample_assessment_request.field_id,
                'soil_series': 'Marshall',
                'drainage_class': 'moderately_well_drained',
                'water_holding_capacity': 0.18,
                'organic_matter': 2.5
            }
            
            response = await service.assess_current_practices(sample_assessment_request)
            
            # Verify response structure
            assert isinstance(response, SoilAssessmentResponse)
            assert response.field_id == sample_assessment_request.field_id
            assert response.assessment_date is not None
            
            # Verify individual assessments
            assert isinstance(response.tillage_assessment, TillagePracticeAssessment)
            assert isinstance(response.cover_crop_assessment, CoverCropAssessment)
            assert isinstance(response.organic_matter_assessment, OrganicMatterAssessment)
            assert isinstance(response.compaction_assessment, SoilCompactionAssessment)
            assert isinstance(response.drainage_assessment, DrainageAssessment)
            
            # Verify soil health score
            assert isinstance(response.soil_health_score, SoilHealthScore)
            assert 0 <= response.soil_health_score.overall_score <= 100
            
            # Verify improvement opportunities
            assert isinstance(response.improvement_opportunities, list)
            for opportunity in response.improvement_opportunities:
                assert isinstance(opportunity, ImprovementOpportunity)
                assert opportunity.priority in ['high', 'medium', 'low']
                assert opportunity.potential_impact >= 0
            
            # Verify assessment report
            assert isinstance(response.assessment_report, AssessmentReport)
            assert response.assessment_report.field_id == sample_assessment_request.field_id
    
    @pytest.mark.asyncio
    async def test_tillage_practice_assessment(self, service, sample_field_data, sample_soil_data):
        """Test tillage practice assessment logic."""
        await service.initialize()
        
        tillage_data = {
            'tillage_type': 'conventional',
            'frequency_per_year': 3,
            'average_depth_inches': 6,
            'equipment_type': 'moldboard_plow'
        }
        
        assessment = await service._assess_tillage_practices(tillage_data, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment, TillagePracticeAssessment)
        assert assessment.tillage_type == TillageType.CONVENTIONAL
        assert assessment.tillage_frequency == 3
        assert assessment.tillage_depth == 6.0
        assert assessment.equipment_type == 'moldboard_plow'
        
        # Verify scores
        assert 0 <= assessment.intensity_score <= 100
        assert 0 <= assessment.disturbance_score <= 100
        assert 0 <= assessment.moisture_retention_score <= 100
        assert 0 <= assessment.overall_score <= 100
        
        # Verify recommendations
        assert isinstance(assessment.improvement_recommendations, list)
        assert len(assessment.improvement_recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_cover_crop_assessment(self, service, sample_field_data, sample_soil_data):
        """Test cover crop assessment logic."""
        await service.initialize()
        
        # Test with no cover crops
        cover_crop_data_no = {
            'cover_crops_used': False,
            'species': [],
            'planting_timing': 'fall',
            'termination_timing': 'spring',
            'biomass_production_lbs_per_acre': 0
        }
        
        assessment_no = await service._assess_cover_crop_usage(cover_crop_data_no, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment_no, CoverCropAssessment)
        assert assessment_no.cover_crops_used is False
        assert assessment_no.overall_score == 0
        assert len(assessment_no.improvement_recommendations) > 0
        
        # Test with cover crops
        cover_crop_data_yes = {
            'cover_crops_used': True,
            'species': ['cereal_rye', 'crimson_clover'],
            'planting_timing': 'fall',
            'termination_timing': 'spring',
            'biomass_production_lbs_per_acre': 2500
        }
        
        assessment_yes = await service._assess_cover_crop_usage(cover_crop_data_yes, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment_yes, CoverCropAssessment)
        assert assessment_yes.cover_crops_used is True
        assert len(assessment_yes.species) == 2
        assert assessment_yes.biomass_production == 2500
        assert assessment_yes.overall_score > 0
    
    @pytest.mark.asyncio
    async def test_organic_matter_assessment(self, service, sample_field_data, sample_soil_data):
        """Test organic matter assessment logic."""
        await service.initialize()
        
        om_data = {
            'current_om_percent': 2.5,
            'target_om_percent': 4.0,
            'management_practices': ['crop_rotation', 'cover_crops'],
            'manure_applications_per_year': 1,
            'compost_applications_per_year': 0
        }
        
        assessment = await service._assess_organic_matter(om_data, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment, OrganicMatterAssessment)
        assert assessment.current_om_percent == 2.5
        assert assessment.target_om_percent == 4.0
        assert len(assessment.management_practices) == 2
        assert assessment.manure_applications == 1
        assert assessment.compost_applications == 0
        
        # Verify scores
        assert 0 <= assessment.om_level_score <= 100
        assert 0 <= assessment.management_score <= 100
        assert 0 <= assessment.improvement_score <= 100
        assert 0 <= assessment.overall_score <= 100
    
    @pytest.mark.asyncio
    async def test_compaction_assessment(self, service, sample_field_data, sample_soil_data):
        """Test soil compaction assessment logic."""
        await service.initialize()
        
        compaction_data = {
            'compaction_level': 'moderate',
            'bulk_density_g_cm3': 1.4,
            'penetration_resistance_psi': 250,
            'management_practices': ['cover_crops']
        }
        
        assessment = await service._assess_soil_compaction(compaction_data, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment, SoilCompactionAssessment)
        assert assessment.compaction_level == CompactionLevel.MODERATE
        assert assessment.bulk_density == 1.4
        assert assessment.penetration_resistance == 250
        assert len(assessment.management_practices) == 1
        
        # Verify scores
        assert 0 <= assessment.severity_score <= 100
        assert 0 <= assessment.management_score <= 100
        assert 0 <= assessment.improvement_score <= 100
        assert 0 <= assessment.overall_score <= 100
    
    @pytest.mark.asyncio
    async def test_drainage_assessment(self, service, sample_field_data, sample_soil_data):
        """Test drainage assessment logic."""
        await service.initialize()
        
        drainage_data = {
            'drainage_class': 'moderately_well_drained',
            'surface_drainage': 'adequate',
            'subsurface_drainage': 'none',
            'management_practices': []
        }
        
        assessment = await service._assess_drainage(drainage_data, sample_field_data, sample_soil_data)
        
        assert isinstance(assessment, DrainageAssessment)
        assert assessment.drainage_class == DrainageClass.MODERATELY_WELL_DRAINED
        assert assessment.surface_drainage == 'adequate'
        assert assessment.subsurface_drainage == 'none'
        
        # Verify scores
        assert 0 <= assessment.drainage_class_score <= 100
        assert 0 <= assessment.surface_drainage_score <= 100
        assert 0 <= assessment.subsurface_drainage_score <= 100
        assert 0 <= assessment.management_score <= 100
        assert 0 <= assessment.overall_score <= 100
    
    @pytest.mark.asyncio
    async def test_soil_health_score_calculation(self, service):
        """Test overall soil health score calculation."""
        await service.initialize()
        
        # Create mock assessments
        tillage_assessment = TillagePracticeAssessment(
            tillage_type=TillageType.CONVENTIONAL,
            tillage_frequency=3,
            tillage_depth=6.0,
            equipment_type='moldboard_plow',
            intensity_score=40.0,
            disturbance_score=30.0,
            moisture_retention_score=40.0,
            overall_score=40.0,
            improvement_recommendations=[]
        )
        
        cover_crop_assessment = CoverCropAssessment(
            cover_crops_used=False,
            species=[],
            planting_timing='fall',
            termination_timing='spring',
            biomass_production=0,
            implementation_score=0,
            biomass_score=0,
            soil_health_score=0,
            overall_score=0,
            improvement_recommendations=[]
        )
        
        organic_matter_assessment = OrganicMatterAssessment(
            current_om_percent=2.5,
            target_om_percent=4.0,
            management_practices=[],
            manure_applications=0,
            compost_applications=0,
            om_level_score=60.0,
            management_score=20.0,
            improvement_score=60.0,
            overall_score=60.0,
            improvement_recommendations=[]
        )
        
        compaction_assessment = SoilCompactionAssessment(
            compaction_level=CompactionLevel.MODERATE,
            bulk_density=1.4,
            penetration_resistance=250,
            management_practices=[],
            severity_score=60.0,
            management_score=20.0,
            improvement_score=40.0,
            overall_score=60.0,
            improvement_recommendations=[]
        )
        
        drainage_assessment = DrainageAssessment(
            drainage_class=DrainageClass.MODERATELY_WELL_DRAINED,
            surface_drainage='adequate',
            subsurface_drainage='none',
            management_practices=[],
            drainage_class_score=80.0,
            surface_drainage_score=60.0,
            subsurface_drainage_score=20.0,
            management_score=0.0,
            overall_score=80.0,
            improvement_recommendations=[]
        )
        
        soil_health_score = await service._calculate_soil_health_score(
            tillage_assessment,
            cover_crop_assessment,
            organic_matter_assessment,
            compaction_assessment,
            drainage_assessment
        )
        
        assert isinstance(soil_health_score, SoilHealthScore)
        assert 0 <= soil_health_score.overall_score <= 100
        assert soil_health_score.tillage_score == 40.0
        assert soil_health_score.cover_crop_score == 0.0
        assert soil_health_score.organic_matter_score == 60.0
        assert soil_health_score.compaction_score == 60.0
        assert soil_health_score.drainage_score == 80.0
        assert 0 <= soil_health_score.moisture_retention_score <= 100
        assert isinstance(soil_health_score.limiting_factors, list)
        assert isinstance(soil_health_score.strengths, list)
        assert 0 <= soil_health_score.improvement_potential <= 100
    
    @pytest.mark.asyncio
    async def test_improvement_opportunities_identification(self, service):
        """Test improvement opportunities identification."""
        await service.initialize()
        
        # Create mock soil health score with low scores
        soil_health_score = SoilHealthScore(
            overall_score=45.0,
            tillage_score=30.0,
            cover_crop_score=20.0,
            organic_matter_score=50.0,
            compaction_score=60.0,
            drainage_score=70.0,
            moisture_retention_score=40.0,
            limiting_factors=['Tillage practices', 'Cover crop usage'],
            strengths=['Drainage conditions'],
            improvement_potential=55.0
        )
        
        # Create mock assessments
        tillage_assessment = TillagePracticeAssessment(
            tillage_type=TillageType.CONVENTIONAL,
            tillage_frequency=3,
            tillage_depth=6.0,
            equipment_type='moldboard_plow',
            intensity_score=30.0,
            disturbance_score=30.0,
            moisture_retention_score=30.0,
            overall_score=30.0,
            improvement_recommendations=[]
        )
        
        cover_crop_assessment = CoverCropAssessment(
            cover_crops_used=False,
            species=[],
            planting_timing='fall',
            termination_timing='spring',
            biomass_production=0,
            implementation_score=0,
            biomass_score=0,
            soil_health_score=0,
            overall_score=20.0,
            improvement_recommendations=[]
        )
        
        organic_matter_assessment = OrganicMatterAssessment(
            current_om_percent=2.5,
            target_om_percent=4.0,
            management_practices=[],
            manure_applications=0,
            compost_applications=0,
            om_level_score=50.0,
            management_score=20.0,
            improvement_score=50.0,
            overall_score=50.0,
            improvement_recommendations=[]
        )
        
        compaction_assessment = SoilCompactionAssessment(
            compaction_level=CompactionLevel.MODERATE,
            bulk_density=1.4,
            penetration_resistance=250,
            management_practices=[],
            severity_score=60.0,
            management_score=20.0,
            improvement_score=40.0,
            overall_score=60.0,
            improvement_recommendations=[]
        )
        
        drainage_assessment = DrainageAssessment(
            drainage_class=DrainageClass.MODERATELY_WELL_DRAINED,
            surface_drainage='adequate',
            subsurface_drainage='none',
            management_practices=[],
            drainage_class_score=80.0,
            surface_drainage_score=60.0,
            subsurface_drainage_score=20.0,
            management_score=0.0,
            overall_score=70.0,
            improvement_recommendations=[]
        )
        
        opportunities = await service._identify_improvement_opportunities(
            soil_health_score,
            tillage_assessment,
            cover_crop_assessment,
            organic_matter_assessment,
            compaction_assessment,
            drainage_assessment
        )
        
        assert isinstance(opportunities, list)
        assert len(opportunities) > 0
        
        # Verify high priority opportunities are identified
        high_priority_opportunities = [opp for opp in opportunities if opp.priority == PriorityLevel.HIGH]
        assert len(high_priority_opportunities) > 0
        
        # Verify opportunity structure
        for opportunity in opportunities:
            assert isinstance(opportunity, ImprovementOpportunity)
            assert opportunity.category in ['Tillage Practices', 'Cover Crops', 'Organic Matter', 'Soil Compaction', 'Drainage']
            assert opportunity.priority in [PriorityLevel.HIGH, PriorityLevel.MEDIUM, PriorityLevel.LOW]
            assert opportunity.potential_impact >= 0
            assert opportunity.implementation_cost >= 0
            assert opportunity.water_savings_potential >= 0
    
    def test_tillage_intensity_scoring(self, service):
        """Test tillage intensity scoring logic."""
        # Test no-till (should get highest score)
        score_no_till = service._calculate_tillage_intensity_score('no_till', 1, 2, 'no_till_drill')
        assert score_no_till == 100
        
        # Test conventional tillage (should get lower score)
        score_conventional = service._calculate_tillage_intensity_score('conventional', 3, 6, 'moldboard_plow')
        assert score_conventional < score_no_till
        assert score_conventional >= 0
        
        # Test reduced tillage
        score_reduced = service._calculate_tillage_intensity_score('reduced_till', 2, 4, 'chisel_plow')
        assert score_reduced > score_conventional
        assert score_reduced < score_no_till
    
    def test_cover_crop_implementation_scoring(self, service):
        """Test cover crop implementation scoring logic."""
        # Test no cover crops
        score_no_cover = service._calculate_cover_crop_implementation_score(False, [], 'fall', 'spring')
        assert score_no_cover == 0
        
        # Test with cover crops
        score_with_cover = service._calculate_cover_crop_implementation_score(True, ['cereal_rye'], 'fall', 'spring')
        assert score_with_cover > 0
        
        # Test with multiple species
        score_multiple = service._calculate_cover_crop_implementation_score(True, ['cereal_rye', 'clover'], 'fall', 'spring')
        assert score_multiple > score_with_cover
    
    def test_organic_matter_level_scoring(self, service):
        """Test organic matter level scoring logic."""
        soil_data = {'soil_type': 'clay_loam'}
        
        # Test low organic matter
        score_low = service._calculate_om_level_score(1.5, soil_data)
        assert score_low < 50
        
        # Test moderate organic matter
        score_moderate = service._calculate_om_level_score(3.0, soil_data)
        assert score_moderate > score_low
        
        # Test high organic matter
        score_high = service._calculate_om_level_score(5.0, soil_data)
        assert score_high > score_moderate
        assert score_high == 100
    
    def test_compaction_severity_scoring(self, service):
        """Test compaction severity scoring logic."""
        soil_data = {'soil_type': 'clay_loam'}
        
        # Test no compaction
        score_none = service._calculate_compaction_severity_score('none', 1.2, 150, soil_data)
        assert score_none == 100
        
        # Test moderate compaction
        score_moderate = service._calculate_compaction_severity_score('moderate', 1.4, 250, soil_data)
        assert score_moderate < score_none
        
        # Test severe compaction
        score_severe = service._calculate_compaction_severity_score('severe', 1.6, 400, soil_data)
        assert score_severe < score_moderate
        assert score_severe >= 0
    
    def test_drainage_class_scoring(self, service):
        """Test drainage class scoring logic."""
        # Test well drained (should get highest score)
        score_well = service._calculate_drainage_class_score('well_drained')
        assert score_well == 100
        
        # Test moderately well drained
        score_moderate = service._calculate_drainage_class_score('moderately_well_drained')
        assert score_moderate == 80
        
        # Test poorly drained
        score_poor = service._calculate_drainage_class_score('poorly_drained')
        assert score_poor == 40
        
        # Test very poorly drained
        score_very_poor = service._calculate_drainage_class_score('very_poorly_drained')
        assert score_very_poor == 20
    
    def test_soil_health_grade_calculation(self, service):
        """Test soil health grade calculation."""
        # Test A+ grade
        grade_a_plus = service._calculate_soil_health_grade(95.0)
        assert grade_a_plus == SoilHealthGrade.A_PLUS
        
        # Test A grade
        grade_a = service._calculate_soil_health_grade(85.0)
        assert grade_a == SoilHealthGrade.A
        
        # Test B grade
        grade_b = service._calculate_soil_health_grade(75.0)
        assert grade_b == SoilHealthGrade.B
        
        # Test C grade
        grade_c = service._calculate_soil_health_grade(65.0)
        assert grade_c == SoilHealthGrade.C
        
        # Test D grade
        grade_d = service._calculate_soil_health_grade(55.0)
        assert grade_d == SoilHealthGrade.D
        
        # Test F grade
        grade_f = service._calculate_soil_health_grade(35.0)
        assert grade_f == SoilHealthGrade.F
    
    def test_water_savings_estimation(self, service):
        """Test water savings estimation logic."""
        # Test tillage water savings
        tillage_savings = service._estimate_water_savings('tillage', 40.0)
        assert tillage_savings > 0
        assert tillage_savings <= 15.0  # Max tillage savings
        
        # Test cover crop water savings
        cover_crop_savings = service._estimate_water_savings('cover_crops', 20.0)
        assert cover_crop_savings > 0
        assert cover_crop_savings <= 20.0  # Max cover crop savings
        
        # Test organic matter water savings
        om_savings = service._estimate_water_savings('organic_matter', 50.0)
        assert om_savings > 0
        assert om_savings <= 25.0  # Max organic matter savings
    
    def test_implementation_timeline_calculation(self, service):
        """Test implementation timeline calculation."""
        opportunities = [
            ImprovementOpportunity(
                category="Tillage Practices",
                priority=PriorityLevel.HIGH,
                description="Reduce tillage intensity",
                potential_impact=50.0,
                implementation_cost=Decimal('50.00'),
                water_savings_potential=15.0,
                timeline="immediate",
                resources_required=[]
            ),
            ImprovementOpportunity(
                category="Cover Crops",
                priority=PriorityLevel.HIGH,
                description="Implement cover crops",
                potential_impact=60.0,
                implementation_cost=Decimal('30.00'),
                water_savings_potential=20.0,
                timeline="immediate",
                resources_required=[]
            ),
            ImprovementOpportunity(
                category="Organic Matter",
                priority=PriorityLevel.MEDIUM,
                description="Increase organic matter",
                potential_impact=40.0,
                implementation_cost=Decimal('100.00'),
                water_savings_potential=25.0,
                timeline="short_term",
                resources_required=[]
            )
        ]
        
        timeline = service._calculate_implementation_timeline(opportunities)
        
        assert 'immediate' in timeline
        assert 'short_term' in timeline
        assert 'long_term' in timeline
        
        assert 'Tillage Practices' in timeline['immediate']
        assert 'Cover Crops' in timeline['immediate']
        assert 'Organic Matter' in timeline['short_term']
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service, sample_assessment_request):
        """Test error handling in assessment process."""
        await service.initialize()
        
        # Test with invalid field data
        with patch.object(service, '_get_field_characteristics', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                await service.assess_current_practices(sample_assessment_request)
        
        # Test with invalid soil data
        with patch.object(service, '_get_field_characteristics', return_value={}):
            with patch.object(service, '_get_soil_data', side_effect=Exception("Soil service error")):
                with pytest.raises(Exception):
                    await service.assess_current_practices(sample_assessment_request)
    
    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, service, sample_assessment_request):
        """Test confidence score calculation."""
        await service.initialize()
        
        field_data = {
            'field_id': sample_assessment_request.field_id,
            'soil_type': 'clay_loam',
            'slope_percent': 2.0,
            'field_size_acres': 40.0,
            'climate_zone': '6a'
        }
        
        confidence = service._calculate_confidence_score(sample_assessment_request, field_data)
        
        assert 0 <= confidence <= 1
        assert confidence >= 0.7  # Should have good confidence with complete data
    
    def test_best_practices_initialization(self, service):
        """Test best practices initialization."""
        best_practices = service._initialize_best_practices()
        
        assert 'tillage' in best_practices
        assert 'cover_crops' in best_practices
        assert 'organic_matter' in best_practices
        
        # Verify tillage practices
        tillage_practices = best_practices['tillage']
        assert 'no_till' in tillage_practices
        assert 'conventional' in tillage_practices
        assert tillage_practices['no_till']['score'] == 100
        assert tillage_practices['conventional']['score'] == 40
        
        # Verify cover crop practices
        cover_crop_practices = best_practices['cover_crops']
        assert cover_crop_practices['biomass_target'] == 2500
        assert cover_crop_practices['species_diversity'] == 3
        
        # Verify organic matter practices
        om_practices = best_practices['organic_matter']
        assert om_practices['target_percent'] == 4.0
        assert om_practices['minimum_percent'] == 3.0


class TestSoilAssessmentModels:
    """Test suite for soil assessment data models."""
    
    def test_tillage_practice_assessment_model(self):
        """Test TillagePracticeAssessment model validation."""
        assessment = TillagePracticeAssessment(
            tillage_type=TillageType.CONVENTIONAL,
            tillage_frequency=3,
            tillage_depth=6.0,
            equipment_type='moldboard_plow',
            intensity_score=40.0,
            disturbance_score=30.0,
            moisture_retention_score=40.0,
            overall_score=40.0,
            improvement_recommendations=['Reduce tillage frequency']
        )
        
        assert assessment.tillage_type == TillageType.CONVENTIONAL
        assert assessment.tillage_frequency == 3
        assert assessment.tillage_depth == 6.0
        assert assessment.equipment_type == 'moldboard_plow'
        assert assessment.intensity_score == 40.0
        assert assessment.disturbance_score == 30.0
        assert assessment.moisture_retention_score == 40.0
        assert assessment.overall_score == 40.0
        assert len(assessment.improvement_recommendations) == 1
    
    def test_cover_crop_assessment_model(self):
        """Test CoverCropAssessment model validation."""
        assessment = CoverCropAssessment(
            cover_crops_used=True,
            species=['cereal_rye', 'crimson_clover'],
            planting_timing='fall',
            termination_timing='spring',
            biomass_production=2500.0,
            implementation_score=80.0,
            biomass_score=80.0,
            soil_health_score=75.0,
            overall_score=78.0,
            improvement_recommendations=['Increase biomass production']
        )
        
        assert assessment.cover_crops_used is True
        assert len(assessment.species) == 2
        assert assessment.planting_timing == 'fall'
        assert assessment.termination_timing == 'spring'
        assert assessment.biomass_production == 2500.0
        assert assessment.implementation_score == 80.0
        assert assessment.biomass_score == 80.0
        assert assessment.soil_health_score == 75.0
        assert assessment.overall_score == 78.0
    
    def test_organic_matter_assessment_model(self):
        """Test OrganicMatterAssessment model validation."""
        assessment = OrganicMatterAssessment(
            current_om_percent=2.5,
            target_om_percent=4.0,
            management_practices=['crop_rotation', 'cover_crops'],
            manure_applications=1,
            compost_applications=0,
            om_level_score=60.0,
            management_score=50.0,
            improvement_score=60.0,
            overall_score=57.0,
            improvement_recommendations=['Increase organic matter inputs']
        )
        
        assert assessment.current_om_percent == 2.5
        assert assessment.target_om_percent == 4.0
        assert len(assessment.management_practices) == 2
        assert assessment.manure_applications == 1
        assert assessment.compost_applications == 0
        assert assessment.om_level_score == 60.0
        assert assessment.management_score == 50.0
        assert assessment.improvement_score == 60.0
        assert assessment.overall_score == 57.0
    
    def test_soil_health_score_model(self):
        """Test SoilHealthScore model validation."""
        score = SoilHealthScore(
            overall_score=65.0,
            tillage_score=40.0,
            cover_crop_score=20.0,
            organic_matter_score=60.0,
            compaction_score=70.0,
            drainage_score=80.0,
            moisture_retention_score=50.0,
            limiting_factors=['Tillage practices', 'Cover crop usage'],
            strengths=['Drainage conditions'],
            improvement_potential=35.0
        )
        
        assert score.overall_score == 65.0
        assert score.tillage_score == 40.0
        assert score.cover_crop_score == 20.0
        assert score.organic_matter_score == 60.0
        assert score.compaction_score == 70.0
        assert score.drainage_score == 80.0
        assert score.moisture_retention_score == 50.0
        assert len(score.limiting_factors) == 2
        assert len(score.strengths) == 1
        assert score.improvement_potential == 35.0
    
    def test_improvement_opportunity_model(self):
        """Test ImprovementOpportunity model validation."""
        opportunity = ImprovementOpportunity(
            category="Tillage Practices",
            priority=PriorityLevel.HIGH,
            description="Reduce tillage intensity",
            potential_impact=50.0,
            implementation_cost=Decimal('50.00'),
            water_savings_potential=15.0,
            timeline="immediate",
            resources_required=['no_till_drill', 'cover_crop_seeder']
        )
        
        assert opportunity.category == "Tillage Practices"
        assert opportunity.priority == PriorityLevel.HIGH
        assert opportunity.description == "Reduce tillage intensity"
        assert opportunity.potential_impact == 50.0
        assert opportunity.implementation_cost == Decimal('50.00')
        assert opportunity.water_savings_potential == 15.0
        assert opportunity.timeline == "immediate"
        assert len(opportunity.resources_required) == 2
    
    def test_assessment_report_model(self):
        """Test AssessmentReport model validation."""
        report = AssessmentReport(
            field_id=uuid4(),
            assessment_date=datetime.utcnow(),
            overall_soil_health_score=65.0,
            soil_health_grade=SoilHealthGrade.C,
            improvement_opportunities_count=3,
            total_water_savings_potential=45.0,
            recommendations_summary="Focus on high-priority improvements",
            implementation_timeline={
                'immediate': ['Tillage Practices'],
                'short_term': ['Cover Crops'],
                'long_term': ['Drainage']
            },
            next_assessment_date=datetime.utcnow(),
            confidence_level=0.85
        )
        
        assert report.field_id is not None
        assert report.assessment_date is not None
        assert report.overall_soil_health_score == 65.0
        assert report.soil_health_grade == SoilHealthGrade.C
        assert report.improvement_opportunities_count == 3
        assert report.total_water_savings_potential == 45.0
        assert report.recommendations_summary == "Focus on high-priority improvements"
        assert 'immediate' in report.implementation_timeline
        assert report.next_assessment_date is not None
        assert report.confidence_level == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])