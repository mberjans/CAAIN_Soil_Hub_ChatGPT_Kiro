"""
Regulatory Compliance Database Service.

This module provides database operations for regulatory compliance tracking,
environmental impact assessment, and sustainability metrics.
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import sqlite3
import json
from contextlib import asynccontextmanager

from ..models.environmental_models import (
    RegulatoryRule, ComplianceAssessment, EnvironmentalImpactAssessment,
    SustainabilityMetrics, ComplianceReport, RegulatoryUpdate,
    RegulationType, ComplianceStatus, EnvironmentalImpactLevel
)

logger = logging.getLogger(__name__)


class RegulatoryComplianceDB:
    """Database service for regulatory compliance operations."""
    
    def __init__(self, db_path: str = "regulatory_compliance.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create regulatory rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulatory_rules (
                    rule_id TEXT PRIMARY KEY,
                    regulation_type TEXT NOT NULL,
                    jurisdiction TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    max_application_rate DECIMAL(10,2),
                    application_timing_restrictions TEXT,
                    buffer_zone_requirements DECIMAL(10,2),
                    soil_conditions TEXT,
                    weather_restrictions TEXT,
                    water_body_protection BOOLEAN,
                    record_keeping_required BOOLEAN DEFAULT FALSE,
                    reporting_requirements TEXT,
                    effective_date DATE NOT NULL,
                    expiration_date DATE,
                    source_url TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create compliance assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    field_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    regulation_type TEXT NOT NULL,
                    jurisdiction TEXT NOT NULL,
                    overall_status TEXT NOT NULL,
                    compliance_score REAL NOT NULL,
                    applicable_rules TEXT NOT NULL,
                    violations TEXT,
                    recommendations TEXT,
                    risk_level TEXT NOT NULL,
                    risk_factors TEXT,
                    supporting_documents TEXT,
                    notes TEXT
                )
            """)
            
            # Create environmental impact assessments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS environmental_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    field_id TEXT NOT NULL,
                    fertilizer_plan_id TEXT NOT NULL,
                    nutrient_runoff_risk TEXT NOT NULL,
                    groundwater_contamination_risk TEXT NOT NULL,
                    air_quality_impact TEXT NOT NULL,
                    soil_health_impact TEXT NOT NULL,
                    estimated_nitrogen_loss DECIMAL(10,2),
                    estimated_phosphorus_loss DECIMAL(10,2),
                    carbon_footprint DECIMAL(10,2),
                    recommended_mitigation TEXT,
                    buffer_zone_recommendations DECIMAL(10,2),
                    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assessment_method TEXT NOT NULL,
                    confidence_level REAL NOT NULL
                )
            """)
            
            # Create sustainability metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sustainability_metrics (
                    field_id TEXT NOT NULL,
                    assessment_period TEXT NOT NULL,
                    nitrogen_use_efficiency REAL,
                    phosphorus_use_efficiency REAL,
                    potassium_use_efficiency REAL,
                    soil_organic_matter_change DECIMAL(5,2),
                    erosion_reduction REAL,
                    water_quality_score REAL,
                    cost_per_unit_yield DECIMAL(10,2),
                    profitability_index REAL,
                    sustainability_score REAL NOT NULL,
                    calculated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_sources TEXT,
                    PRIMARY KEY (field_id, assessment_period)
                )
            """)
            
            # Create compliance reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_reports (
                    report_id TEXT PRIMARY KEY,
                    farm_id TEXT NOT NULL,
                    report_period TEXT NOT NULL,
                    total_fields_assessed INTEGER NOT NULL,
                    compliance_summary TEXT NOT NULL,
                    environmental_summary TEXT NOT NULL,
                    critical_violations TEXT,
                    improvement_areas TEXT,
                    best_practices TEXT,
                    priority_actions TEXT,
                    long_term_goals TEXT,
                    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    generated_by TEXT NOT NULL,
                    report_format TEXT DEFAULT 'pdf'
                )
            """)
            
            # Create regulatory updates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulatory_updates (
                    update_id TEXT PRIMARY KEY,
                    regulation_id TEXT NOT NULL,
                    update_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    effective_date DATE NOT NULL,
                    affected_fields TEXT,
                    compliance_impact TEXT NOT NULL,
                    notification_sent BOOLEAN DEFAULT FALSE,
                    notification_date TIMESTAMP,
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_type_jurisdiction ON regulatory_rules(regulation_type, jurisdiction)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rules_effective_date ON regulatory_rules(effective_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_field_date ON compliance_assessments(field_id, assessment_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_status ON compliance_assessments(overall_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_env_assessments_field ON environmental_assessments(field_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sustainability_field_period ON sustainability_metrics(field_id, assessment_period)")
            
            conn.commit()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    # Regulatory Rules Operations
    async def create_regulatory_rule(self, rule: RegulatoryRule) -> bool:
        """Create a new regulatory rule."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO regulatory_rules (
                        rule_id, regulation_type, jurisdiction, title, description,
                        max_application_rate, application_timing_restrictions,
                        buffer_zone_requirements, soil_conditions, weather_restrictions,
                        water_body_protection, record_keeping_required, reporting_requirements,
                        effective_date, expiration_date, source_url, last_updated, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule.rule_id, rule.regulation_type.value, rule.jurisdiction,
                    rule.title, rule.description, rule.max_application_rate,
                    json.dumps(rule.application_timing_restrictions) if rule.application_timing_restrictions else None,
                    rule.buffer_zone_requirements,
                    json.dumps(rule.soil_conditions) if rule.soil_conditions else None,
                    json.dumps(rule.weather_restrictions) if rule.weather_restrictions else None,
                    rule.water_body_protection, rule.record_keeping_required,
                    json.dumps(rule.reporting_requirements) if rule.reporting_requirements else None,
                    rule.effective_date, rule.expiration_date, rule.source_url,
                    rule.last_updated, rule.created_at
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating regulatory rule: {e}")
            return False
    
    async def get_regulatory_rules(
        self,
        regulation_type: Optional[RegulationType] = None,
        jurisdiction: Optional[str] = None,
        active_only: bool = True
    ) -> List[RegulatoryRule]:
        """Get regulatory rules with optional filtering."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM regulatory_rules WHERE 1=1"
                params = []
                
                if regulation_type:
                    query += " AND regulation_type = ?"
                    params.append(regulation_type.value)
                
                if jurisdiction:
                    query += " AND jurisdiction = ?"
                    params.append(jurisdiction)
                
                if active_only:
                    query += " AND (expiration_date IS NULL OR expiration_date > ?)"
                    params.append(date.today())
                
                query += " ORDER BY effective_date DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                rules = []
                for row in rows:
                    rule_data = dict(row)
                    rule_data['application_timing_restrictions'] = (
                        json.loads(rule_data['application_timing_restrictions'])
                        if rule_data['application_timing_restrictions'] else None
                    )
                    rule_data['soil_conditions'] = (
                        json.loads(rule_data['soil_conditions'])
                        if rule_data['soil_conditions'] else None
                    )
                    rule_data['weather_restrictions'] = (
                        json.loads(rule_data['weather_restrictions'])
                        if rule_data['weather_restrictions'] else None
                    )
                    rule_data['reporting_requirements'] = (
                        json.loads(rule_data['reporting_requirements'])
                        if rule_data['reporting_requirements'] else None
                    )
                    
                    rules.append(RegulatoryRule(**rule_data))
                
                return rules
        except Exception as e:
            logger.error(f"Error getting regulatory rules: {e}")
            return []
    
    # Compliance Assessment Operations
    async def create_compliance_assessment(self, assessment: ComplianceAssessment) -> bool:
        """Create a new compliance assessment."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO compliance_assessments (
                        assessment_id, field_id, user_id, assessment_date,
                        regulation_type, jurisdiction, overall_status, compliance_score,
                        applicable_rules, violations, recommendations, risk_level,
                        risk_factors, supporting_documents, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(assessment.assessment_id), str(assessment.field_id),
                    str(assessment.user_id), assessment.assessment_date,
                    assessment.regulation_type.value, assessment.jurisdiction,
                    assessment.overall_status.value, assessment.compliance_score,
                    json.dumps([rule.dict() for rule in assessment.applicable_rules]),
                    json.dumps(assessment.violations),
                    json.dumps(assessment.recommendations),
                    assessment.risk_level.value,
                    json.dumps(assessment.risk_factors),
                    json.dumps(assessment.supporting_documents) if assessment.supporting_documents else None,
                    assessment.notes
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating compliance assessment: {e}")
            return False
    
    async def get_compliance_assessments(
        self,
        field_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        regulation_type: Optional[RegulationType] = None,
        limit: int = 100
    ) -> List[ComplianceAssessment]:
        """Get compliance assessments with optional filtering."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM compliance_assessments WHERE 1=1"
                params = []
                
                if field_id:
                    query += " AND field_id = ?"
                    params.append(str(field_id))
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(str(user_id))
                
                if regulation_type:
                    query += " AND regulation_type = ?"
                    params.append(regulation_type.value)
                
                query += " ORDER BY assessment_date DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                assessments = []
                for row in rows:
                    assessment_data = dict(row)
                    assessment_data['assessment_id'] = UUID(assessment_data['assessment_id'])
                    assessment_data['field_id'] = UUID(assessment_data['field_id'])
                    assessment_data['user_id'] = UUID(assessment_data['user_id'])
                    assessment_data['regulation_type'] = RegulationType(assessment_data['regulation_type'])
                    assessment_data['overall_status'] = ComplianceStatus(assessment_data['overall_status'])
                    assessment_data['risk_level'] = EnvironmentalImpactLevel(assessment_data['risk_level'])
                    
                    # Parse JSON fields
                    assessment_data['applicable_rules'] = [
                        RegulatoryRule(**rule_data)
                        for rule_data in json.loads(assessment_data['applicable_rules'])
                    ]
                    assessment_data['violations'] = json.loads(assessment_data['violations'] or '[]')
                    assessment_data['recommendations'] = json.loads(assessment_data['recommendations'] or '[]')
                    assessment_data['risk_factors'] = json.loads(assessment_data['risk_factors'] or '[]')
                    assessment_data['supporting_documents'] = (
                        json.loads(assessment_data['supporting_documents'])
                        if assessment_data['supporting_documents'] else None
                    )
                    
                    assessments.append(ComplianceAssessment(**assessment_data))
                
                return assessments
        except Exception as e:
            logger.error(f"Error getting compliance assessments: {e}")
            return []
    
    # Environmental Impact Assessment Operations
    async def create_environmental_assessment(self, assessment: EnvironmentalImpactAssessment) -> bool:
        """Create a new environmental impact assessment."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO environmental_assessments (
                        assessment_id, field_id, fertilizer_plan_id,
                        nutrient_runoff_risk, groundwater_contamination_risk,
                        air_quality_impact, soil_health_impact,
                        estimated_nitrogen_loss, estimated_phosphorus_loss,
                        carbon_footprint, recommended_mitigation,
                        buffer_zone_recommendations, assessment_date,
                        assessment_method, confidence_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(assessment.assessment_id), str(assessment.field_id),
                    str(assessment.fertilizer_plan_id),
                    assessment.nutrient_runoff_risk.value,
                    assessment.groundwater_contamination_risk.value,
                    assessment.air_quality_impact.value,
                    assessment.soil_health_impact.value,
                    assessment.estimated_nitrogen_loss,
                    assessment.estimated_phosphorus_loss,
                    assessment.carbon_footprint,
                    json.dumps(assessment.recommended_mitigation),
                    assessment.buffer_zone_recommendations,
                    assessment.assessment_date,
                    assessment.assessment_method,
                    assessment.confidence_level
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating environmental assessment: {e}")
            return False
    
    # Sustainability Metrics Operations
    async def create_sustainability_metrics(self, metrics: SustainabilityMetrics) -> bool:
        """Create new sustainability metrics."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sustainability_metrics (
                        field_id, assessment_period, nitrogen_use_efficiency,
                        phosphorus_use_efficiency, potassium_use_efficiency,
                        soil_organic_matter_change, erosion_reduction,
                        water_quality_score, cost_per_unit_yield,
                        profitability_index, sustainability_score,
                        calculated_date, data_sources
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(metrics.field_id), metrics.assessment_period,
                    metrics.nitrogen_use_efficiency, metrics.phosphorus_use_efficiency,
                    metrics.potassium_use_efficiency, metrics.soil_organic_matter_change,
                    metrics.erosion_reduction, metrics.water_quality_score,
                    metrics.cost_per_unit_yield, metrics.profitability_index,
                    metrics.sustainability_score, metrics.calculated_date,
                    json.dumps(metrics.data_sources)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating sustainability metrics: {e}")
            return False
    
    async def get_sustainability_metrics(
        self,
        field_id: UUID,
        assessment_period: Optional[str] = None
    ) -> List[SustainabilityMetrics]:
        """Get sustainability metrics for a field."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM sustainability_metrics WHERE field_id = ?"
                params = [str(field_id)]
                
                if assessment_period:
                    query += " AND assessment_period = ?"
                    params.append(assessment_period)
                
                query += " ORDER BY calculated_date DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metric_data = dict(row)
                    metric_data['field_id'] = UUID(metric_data['field_id'])
                    metric_data['data_sources'] = json.loads(metric_data['data_sources'] or '[]')
                    metrics.append(SustainabilityMetrics(**metric_data))
                
                return metrics
        except Exception as e:
            logger.error(f"Error getting sustainability metrics: {e}")
            return []
    
    # Compliance Report Operations
    async def create_compliance_report(self, report: ComplianceReport) -> bool:
        """Create a new compliance report."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO compliance_reports (
                        report_id, farm_id, report_period, total_fields_assessed,
                        compliance_summary, environmental_summary,
                        critical_violations, improvement_areas, best_practices,
                        priority_actions, long_term_goals, generated_date,
                        generated_by, report_format
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(report.report_id), str(report.farm_id), report.report_period,
                    report.total_fields_assessed,
                    json.dumps(report.compliance_summary),
                    json.dumps(report.environmental_summary),
                    json.dumps(report.critical_violations),
                    json.dumps(report.improvement_areas),
                    json.dumps(report.best_practices),
                    json.dumps(report.priority_actions),
                    json.dumps(report.long_term_goals),
                    report.generated_date, report.generated_by, report.report_format
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating compliance report: {e}")
            return False
    
    # Utility Methods
    async def get_compliance_statistics(
        self,
        farm_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get compliance statistics for reporting."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get compliance status counts
                query = """
                    SELECT overall_status, COUNT(*) as count
                    FROM compliance_assessments
                    WHERE 1=1
                """
                params = []
                
                if date_from:
                    query += " AND assessment_date >= ?"
                    params.append(datetime.combine(date_from, datetime.min.time()))
                
                if date_to:
                    query += " AND assessment_date <= ?"
                    params.append(datetime.combine(date_to, datetime.max.time()))
                
                query += " GROUP BY overall_status"
                
                cursor.execute(query, params)
                compliance_counts = {row['overall_status']: row['count'] for row in cursor.fetchall()}
                
                # Get environmental impact level counts
                query = """
                    SELECT risk_level, COUNT(*) as count
                    FROM environmental_assessments
                    WHERE 1=1
                """
                params = []
                
                if date_from:
                    query += " AND assessment_date >= ?"
                    params.append(datetime.combine(date_from, datetime.min.time()))
                
                if date_to:
                    query += " AND assessment_date <= ?"
                    params.append(datetime.combine(date_to, datetime.max.time()))
                
                query += " GROUP BY risk_level"
                
                cursor.execute(query, params)
                environmental_counts = {row['risk_level']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'compliance_counts': compliance_counts,
                    'environmental_counts': environmental_counts,
                    'total_assessments': sum(compliance_counts.values()),
                    'generated_date': datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Error getting compliance statistics: {e}")
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """Clean up old data beyond retention period."""
        try:
            async with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
                
                # Clean up old assessments
                cursor.execute("""
                    DELETE FROM compliance_assessments
                    WHERE assessment_date < ?
                """, (cutoff_date,))
                
                deleted_assessments = cursor.rowcount
                
                # Clean up old environmental assessments
                cursor.execute("""
                    DELETE FROM environmental_assessments
                    WHERE assessment_date < ?
                """, (cutoff_date,))
                
                deleted_env_assessments = cursor.rowcount
                
                conn.commit()
                
                return deleted_assessments + deleted_env_assessments
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0