"""
Comprehensive tests for Regulatory Compliance System.

This module tests the regulatory compliance service, API endpoints,
and database operations for fertilizer strategy optimization.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal

from ..services.environmental_service import RegulatoryComplianceService
from ..models.environmental_models import (
    ComplianceRequest, ComplianceResponse, ComplianceAssessment,
    EnvironmentalImpactAssessment, SustainabilityMetrics, ComplianceReport,
    RegulatoryRule, RegulationType, ComplianceStatus, EnvironmentalImpactLevel
)
from ..database.regulatory_compliance_db import RegulatoryComplianceDB


class TestRegulatoryComplianceService:
    """Test suite for RegulatoryComplianceService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return RegulatoryComplianceService(db_path=":memory:")
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_compliance_request(self, sample_field_id, sample_user_id):
        """Sample compliance request for testing."""
        return ComplianceRequest(
            field_id=sample_field_id,
            user_id=sample_user_id,
            regulation_types=[RegulationType.FEDERAL],
            jurisdiction="Federal",
            include_environmental_assessment=True,
            include_sustainability_metrics=True
        )
    
    @pytest.fixture
    def sample_regulatory_rule(self):
        """Sample regulatory rule for testing."""
        return RegulatoryRule(
            rule_id="TEST_RULE_001",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Federal",
            title="Test Federal Regulation",
            description="Test regulation for unit testing",
            max_application_rate=Decimal("150"),
            application_timing_restrictions=["winter_application_prohibited"],
            buffer_zone_requirements=Decimal("50"),
            water_body_protection=True,
            record_keeping_required=True,
            reporting_requirements=["annual_reporting"],
            effective_date=date(2020, 1, 1),
            source_url="https://test.gov/regulation"
        )
    
    @pytest.mark.asyncio
    async def test_assess_compliance_success(self, service, sample_compliance_request):
        """Test successful compliance assessment."""
        with patch.object(service.db, 'get_regulatory_rules') as mock_get_rules:
            mock_get_rules.return_value = []
            
            with patch.object(service.db, 'create_compliance_assessment') as mock_create_assessment:
                mock_create_assessment.return_value = True
                
                result = await service.assess_compliance(sample_compliance_request)
                
                assert isinstance(result, ComplianceResponse)
                assert result.field_id == sample_compliance_request.field_id
                assert result.compliance_assessment is not None
                assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_assess_compliance_with_violations(self, service, sample_compliance_request):
        """Test compliance assessment with violations."""
        # Create a rule that will cause violations
        rule = RegulatoryRule(
            rule_id="STRICT_RULE",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Federal",
            title="Strict Test Rule",
            description="Rule that will cause violations",
            max_application_rate=Decimal("100"),  # Lower than simulated planned rate
            buffer_zone_requirements=Decimal("100"),  # Higher than simulated buffer
            effective_date=date(2020, 1, 1)
        )
        
        with patch.object(service.db, 'get_regulatory_rules') as mock_get_rules:
            mock_get_rules.return_value = [rule]
            
            with patch.object(service.db, 'create_compliance_assessment') as mock_create_assessment:
                mock_create_assessment.return_value = True
                
                result = await service.assess_compliance(sample_compliance_request)
                
                assert isinstance(result, ComplianceResponse)
                assert len(result.compliance_assessment.violations) > 0
                assert result.compliance_assessment.compliance_score < 1.0
    
    @pytest.mark.asyncio
    async def test_get_compliance_history(self, service, sample_field_id):
        """Test getting compliance history."""
        with patch.object(service.db, 'get_compliance_assessments') as mock_get_assessments:
            mock_assessments = [
                ComplianceAssessment(
                    field_id=sample_field_id,
                    user_id=uuid4(),
                    regulation_type=RegulationType.FEDERAL,
                    jurisdiction="Federal",
                    overall_status=ComplianceStatus.COMPLIANT,
                    compliance_score=0.95,
                    applicable_rules=[],
                    violations=[],
                    recommendations=[],
                    risk_level=EnvironmentalImpactLevel.LOW,
                    risk_factors=[]
                )
            ]
            mock_get_assessments.return_value = mock_assessments
            
            result = await service.get_compliance_history(sample_field_id, limit=10)
            
            assert len(result) == 1
            assert result[0].field_id == sample_field_id
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, service):
        """Test compliance report generation."""
        farm_id = uuid4()
        
        with patch.object(service.db, 'get_compliance_assessments') as mock_get_assessments:
            mock_get_assessments.return_value = []
            
            with patch.object(service.db, 'create_compliance_report') as mock_create_report:
                mock_create_report.return_value = True
                
                result = await service.generate_compliance_report(
                    farm_id=farm_id,
                    report_period="2024-Q1",
                    generated_by="test"
                )
                
                assert isinstance(result, ComplianceReport)
                assert result.farm_id == farm_id
                assert result.report_period == "2024-Q1"
                assert result.generated_by == "test"
    
    @pytest.mark.asyncio
    async def test_get_compliance_statistics(self, service):
        """Test getting compliance statistics."""
        with patch.object(service.db, 'get_compliance_statistics') as mock_get_stats:
            mock_stats = {
                'compliance_counts': {'compliant': 5, 'non_compliant': 1},
                'environmental_counts': {'low': 4, 'moderate': 2},
                'total_assessments': 6,
                'generated_date': datetime.utcnow()
            }
            mock_get_stats.return_value = mock_stats
            
            result = await service.get_compliance_statistics()
            
            assert result['total_assessments'] == 6
            assert 'compliance_counts' in result
            assert 'environmental_counts' in result
    
    @pytest.mark.asyncio
    async def test_check_regulatory_updates(self, service):
        """Test checking for regulatory updates."""
        result = await service.check_regulatory_updates()
        
        assert isinstance(result, list)
        # Should return empty list for now (mock implementation)
        assert len(result) == 0


class TestRegulatoryComplianceDB:
    """Test suite for RegulatoryComplianceDB."""
    
    @pytest.fixture
    def db(self):
        """Create database instance for testing."""
        return RegulatoryComplianceDB(db_path=":memory:")
    
    @pytest.fixture
    def sample_rule(self):
        """Sample regulatory rule for testing."""
        return RegulatoryRule(
            rule_id="TEST_DB_RULE",
            regulation_type=RegulationType.STATE,
            jurisdiction="Test State",
            title="Test Database Rule",
            description="Rule for database testing",
            max_application_rate=Decimal("120"),
            effective_date=date(2021, 1, 1)
        )
    
    @pytest.mark.asyncio
    async def test_create_regulatory_rule(self, db, sample_rule):
        """Test creating a regulatory rule."""
        result = await db.create_regulatory_rule(sample_rule)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_regulatory_rules(self, db, sample_rule):
        """Test getting regulatory rules."""
        # First create a rule
        await db.create_regulatory_rule(sample_rule)
        
        # Then retrieve it
        rules = await db.get_regulatory_rules()
        
        assert len(rules) >= 1
        assert any(rule.rule_id == sample_rule.rule_id for rule in rules)
    
    @pytest.mark.asyncio
    async def test_get_regulatory_rules_filtered(self, db, sample_rule):
        """Test getting regulatory rules with filters."""
        # Create rule
        await db.create_regulatory_rule(sample_rule)
        
        # Test filtering by regulation type
        federal_rules = await db.get_regulatory_rules(regulation_type=RegulationType.FEDERAL)
        state_rules = await db.get_regulatory_rules(regulation_type=RegulationType.STATE)
        
        assert len(state_rules) >= 1
        assert any(rule.rule_id == sample_rule.rule_id for rule in state_rules)
    
    @pytest.mark.asyncio
    async def test_create_compliance_assessment(self, db):
        """Test creating a compliance assessment."""
        assessment = ComplianceAssessment(
            field_id=uuid4(),
            user_id=uuid4(),
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Federal",
            overall_status=ComplianceStatus.COMPLIANT,
            compliance_score=0.95,
            applicable_rules=[],
            violations=[],
            recommendations=["Test recommendation"],
            risk_level=EnvironmentalImpactLevel.LOW,
            risk_factors=[]
        )
        
        result = await db.create_compliance_assessment(assessment)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_compliance_assessments(self, db):
        """Test getting compliance assessments."""
        field_id = uuid4()
        user_id = uuid4()
        
        assessment = ComplianceAssessment(
            field_id=field_id,
            user_id=user_id,
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Federal",
            overall_status=ComplianceStatus.COMPLIANT,
            compliance_score=0.95,
            applicable_rules=[],
            violations=[],
            recommendations=[],
            risk_level=EnvironmentalImpactLevel.LOW,
            risk_factors=[]
        )
        
        # Create assessment
        await db.create_compliance_assessment(assessment)
        
        # Retrieve assessments
        assessments = await db.get_compliance_assessments(field_id=field_id)
        
        assert len(assessments) >= 1
        assert assessments[0].field_id == field_id
    
    @pytest.mark.asyncio
    async def test_create_environmental_assessment(self, db):
        """Test creating an environmental assessment."""
        assessment = EnvironmentalImpactAssessment(
            field_id=uuid4(),
            fertilizer_plan_id=uuid4(),
            nutrient_runoff_risk=EnvironmentalImpactLevel.MODERATE,
            groundwater_contamination_risk=EnvironmentalImpactLevel.LOW,
            air_quality_impact=EnvironmentalImpactLevel.LOW,
            soil_health_impact=EnvironmentalImpactLevel.MODERATE,
            estimated_nitrogen_loss=Decimal("25.5"),
            estimated_phosphorus_loss=Decimal("2.1"),
            carbon_footprint=Decimal("45.2"),
            recommended_mitigation=["Test mitigation"],
            buffer_zone_recommendations=Decimal("50"),
            assessment_method="Test Method",
            confidence_level=0.85
        )
        
        result = await db.create_environmental_assessment(assessment)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_create_sustainability_metrics(self, db):
        """Test creating sustainability metrics."""
        metrics = SustainabilityMetrics(
            field_id=uuid4(),
            assessment_period="2024",
            nitrogen_use_efficiency=0.75,
            phosphorus_use_efficiency=0.68,
            potassium_use_efficiency=0.82,
            soil_organic_matter_change=Decimal("0.2"),
            erosion_reduction=0.15,
            water_quality_score=0.78,
            cost_per_unit_yield=Decimal("2.45"),
            profitability_index=1.25,
            sustainability_score=0.76,
            data_sources=["Test data"]
        )
        
        result = await db.create_sustainability_metrics(metrics)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_create_compliance_report(self, db):
        """Test creating a compliance report."""
        report = ComplianceReport(
            farm_id=uuid4(),
            report_period="2024-Q1",
            total_fields_assessed=5,
            compliance_summary={"compliant": 4, "non_compliant": 1},
            environmental_summary={"low": 3, "moderate": 2},
            critical_violations=[],
            improvement_areas=["Test improvement"],
            best_practices=["Test best practice"],
            priority_actions=["Test action"],
            long_term_goals=["Test goal"],
            generated_by="test"
        )
        
        result = await db.create_compliance_report(report)
        
        assert result is True


class TestComplianceValidator:
    """Test suite for ComplianceValidator."""
    
    def test_validate_application_rate_compliant(self):
        """Test application rate validation when compliant."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            max_application_rate=Decimal("150"),
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        result = validator.validate_application_rate(Decimal("120"), rule)
        
        assert result is True
    
    def test_validate_application_rate_violation(self):
        """Test application rate validation when violating."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            max_application_rate=Decimal("100"),
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        result = validator.validate_application_rate(Decimal("150"), rule)
        
        assert result is False
    
    def test_validate_buffer_zone_compliant(self):
        """Test buffer zone validation when compliant."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            buffer_zone_requirements=Decimal("50"),
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        result = validator.validate_buffer_zone(Decimal("75"), rule)
        
        assert result is True
    
    def test_validate_buffer_zone_violation(self):
        """Test buffer zone validation when violating."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            buffer_zone_requirements=Decimal("100"),
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        result = validator.validate_buffer_zone(Decimal("50"), rule)
        
        assert result is False
    
    def test_validate_timing_restrictions_compliant(self):
        """Test timing restrictions validation when compliant."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            application_timing_restrictions=["winter_application_prohibited"],
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        # Test with summer date (should be compliant)
        result = validator.validate_timing_restrictions(date(2024, 6, 15), rule)
        
        assert result is True
    
    def test_validate_timing_restrictions_violation(self):
        """Test timing restrictions validation when violating."""
        from ..models.environmental_models import ComplianceValidator
        
        rule = RegulatoryRule(
            rule_id="TEST",
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Test",
            title="Test Rule",
            description="Test",
            application_timing_restrictions=["winter_application_prohibited"],
            effective_date=date.today()
        )
        
        validator = ComplianceValidator()
        # Test with winter date (should be violation)
        result = validator.validate_timing_restrictions(date(2024, 12, 15), rule)
        
        assert result is False


class TestEnvironmentalModels:
    """Test suite for environmental models."""
    
    def test_regulatory_rule_creation(self):
        """Test RegulatoryRule model creation."""
        rule = RegulatoryRule(
            rule_id="TEST_MODEL_RULE",
            regulation_type=RegulationType.LOCAL,
            jurisdiction="Test County",
            title="Test Model Rule",
            description="Rule for model testing",
            max_application_rate=Decimal("80"),
            application_timing_restrictions=["spring_application_preferred"],
            buffer_zone_requirements=Decimal("25"),
            water_body_protection=True,
            record_keeping_required=True,
            reporting_requirements=["monthly_reporting"],
            effective_date=date(2022, 1, 1),
            source_url="https://test.gov/model"
        )
        
        assert rule.rule_id == "TEST_MODEL_RULE"
        assert rule.regulation_type == RegulationType.LOCAL
        assert rule.max_application_rate == Decimal("80")
        assert rule.water_body_protection is True
    
    def test_compliance_assessment_creation(self):
        """Test ComplianceAssessment model creation."""
        assessment = ComplianceAssessment(
            field_id=uuid4(),
            user_id=uuid4(),
            regulation_type=RegulationType.STATE,
            jurisdiction="Test State",
            overall_status=ComplianceStatus.AT_RISK,
            compliance_score=0.75,
            applicable_rules=[],
            violations=[{"type": "test_violation", "severity": "medium"}],
            recommendations=["Test recommendation"],
            risk_level=EnvironmentalImpactLevel.MODERATE,
            risk_factors=["Test risk factor"]
        )
        
        assert assessment.overall_status == ComplianceStatus.AT_RISK
        assert assessment.compliance_score == 0.75
        assert len(assessment.violations) == 1
        assert assessment.risk_level == EnvironmentalImpactLevel.MODERATE
    
    def test_environmental_impact_assessment_creation(self):
        """Test EnvironmentalImpactAssessment model creation."""
        assessment = EnvironmentalImpactAssessment(
            field_id=uuid4(),
            fertilizer_plan_id=uuid4(),
            nutrient_runoff_risk=EnvironmentalImpactLevel.HIGH,
            groundwater_contamination_risk=EnvironmentalImpactLevel.MODERATE,
            air_quality_impact=EnvironmentalImpactLevel.LOW,
            soil_health_impact=EnvironmentalImpactLevel.MODERATE,
            estimated_nitrogen_loss=Decimal("35.0"),
            estimated_phosphorus_loss=Decimal("3.5"),
            carbon_footprint=Decimal("55.0"),
            recommended_mitigation=["Test mitigation 1", "Test mitigation 2"],
            buffer_zone_recommendations=Decimal("75"),
            assessment_method="Test Assessment Method",
            confidence_level=0.90
        )
        
        assert assessment.nutrient_runoff_risk == EnvironmentalImpactLevel.HIGH
        assert assessment.estimated_nitrogen_loss == Decimal("35.0")
        assert len(assessment.recommended_mitigation) == 2
        assert assessment.confidence_level == 0.90
    
    def test_sustainability_metrics_creation(self):
        """Test SustainabilityMetrics model creation."""
        metrics = SustainabilityMetrics(
            field_id=uuid4(),
            assessment_period="2024",
            nitrogen_use_efficiency=0.85,
            phosphorus_use_efficiency=0.78,
            potassium_use_efficiency=0.90,
            soil_organic_matter_change=Decimal("0.5"),
            erosion_reduction=0.25,
            water_quality_score=0.85,
            cost_per_unit_yield=Decimal("2.20"),
            profitability_index=1.35,
            sustainability_score=0.82,
            data_sources=["Soil tests", "Yield data", "Weather data"]
        )
        
        assert metrics.nitrogen_use_efficiency == 0.85
        assert metrics.soil_organic_matter_change == Decimal("0.5")
        assert metrics.sustainability_score == 0.82
        assert len(metrics.data_sources) == 3


# Integration tests
class TestRegulatoryComplianceIntegration:
    """Integration tests for regulatory compliance system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_compliance_assessment(self):
        """Test end-to-end compliance assessment workflow."""
        # Create service with in-memory database
        service = RegulatoryComplianceService(db_path=":memory:")
        
        # Create test request
        field_id = uuid4()
        user_id = uuid4()
        request = ComplianceRequest(
            field_id=field_id,
            user_id=user_id,
            regulation_types=[RegulationType.FEDERAL],
            include_environmental_assessment=True,
            include_sustainability_metrics=True
        )
        
        # Perform assessment
        result = await service.assess_compliance(request)
        
        # Verify results
        assert isinstance(result, ComplianceResponse)
        assert result.field_id == field_id
        assert result.compliance_assessment is not None
        assert result.environmental_assessment is not None
        assert result.sustainability_metrics is not None
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_compliance_report_generation_workflow(self):
        """Test complete compliance report generation workflow."""
        # Create service
        service = RegulatoryComplianceService(db_path=":memory:")
        
        # Create some test assessments
        field_id = uuid4()
        user_id = uuid4()
        
        assessment = ComplianceAssessment(
            field_id=field_id,
            user_id=user_id,
            regulation_type=RegulationType.FEDERAL,
            jurisdiction="Federal",
            overall_status=ComplianceStatus.COMPLIANT,
            compliance_score=0.95,
            applicable_rules=[],
            violations=[],
            recommendations=["Test recommendation"],
            risk_level=EnvironmentalImpactLevel.LOW,
            risk_factors=[]
        )
        
        await service.db.create_compliance_assessment(assessment)
        
        # Generate report
        farm_id = uuid4()
        report = await service.generate_compliance_report(
            farm_id=farm_id,
            report_period="2024-Q1",
            generated_by="integration_test"
        )
        
        # Verify report
        assert isinstance(report, ComplianceReport)
        assert report.farm_id == farm_id
        assert report.report_period == "2024-Q1"
        assert report.generated_by == "integration_test"
        assert report.total_fields_assessed >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
