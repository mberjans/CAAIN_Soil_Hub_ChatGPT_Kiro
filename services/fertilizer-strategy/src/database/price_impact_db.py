"""
Database operations for price impact analysis system.
"""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

from ..models.price_impact_models import (
    PriceImpactAnalysisRequest, PriceImpactAnalysisResult,
    PriceImpactAnalysisResponse, AnalysisType
)

logger = logging.getLogger(__name__)

Base = declarative_base()


class PriceImpactAnalysisRecord(Base):
    """Database model for price impact analysis records."""
    
    __tablename__ = "price_impact_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(String(255), unique=True, nullable=False, index=True)
    request_id = Column(String(255), nullable=False, index=True)
    
    # Analysis configuration
    analysis_type = Column(String(50), nullable=False)
    farm_id = Column(String(255), nullable=True)
    field_id = Column(String(255), nullable=True)
    field_size_acres = Column(Float, nullable=False)
    
    # Crop and yield data
    crop_type = Column(String(100), nullable=False)
    expected_yield_bu_per_acre = Column(Float, nullable=False)
    crop_price_per_bu = Column(Float, nullable=False)
    
    # Fertilizer requirements (stored as JSON)
    fertilizer_requirements = Column(JSON, nullable=False)
    
    # Analysis parameters
    analysis_horizon_days = Column(Integer, nullable=False, default=365)
    confidence_level = Column(Float, nullable=False, default=0.95)
    
    # Scenario parameters
    scenarios = Column(JSON, nullable=True)
    custom_scenarios = Column(JSON, nullable=True)
    
    # Sensitivity parameters
    price_change_percentages = Column(JSON, nullable=True)
    
    # Risk parameters
    volatility_threshold = Column(Float, nullable=True)
    
    # Results
    analysis_result = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    
    # Performance metrics
    processing_time_ms = Column(Float, nullable=False, default=0)
    confidence_score = Column(Float, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    
    # Data sources
    data_sources_used = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class PriceImpactMetricsRecord(Base):
    """Database model for price impact metrics."""
    
    __tablename__ = "price_impact_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(String(255), nullable=False, index=True)
    scenario_name = Column(String(100), nullable=False)
    
    # Financial metrics
    total_fertilizer_cost = Column(Float, nullable=False)
    total_crop_revenue = Column(Float, nullable=False)
    net_profit = Column(Float, nullable=False)
    profit_margin_percent = Column(Float, nullable=False)
    
    # Cost per unit metrics
    fertilizer_cost_per_acre = Column(Float, nullable=False)
    fertilizer_cost_per_bu = Column(Float, nullable=False)
    crop_revenue_per_acre = Column(Float, nullable=False)
    
    # Impact metrics
    price_impact_percent = Column(Float, nullable=False, default=0)
    profitability_change_percent = Column(Float, nullable=False, default=0)
    
    # Risk metrics
    value_at_risk = Column(Float, nullable=True)
    expected_shortfall = Column(Float, nullable=True)
    volatility_impact = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SensitivityAnalysisRecord(Base):
    """Database model for sensitivity analysis results."""
    
    __tablename__ = "sensitivity_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(String(255), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    
    # Parameter values and impacts
    parameter_values = Column(JSON, nullable=False)
    impact_values = Column(JSON, nullable=False)
    
    # Sensitivity metrics
    elasticity = Column(Float, nullable=False)
    sensitivity_score = Column(Float, nullable=False)
    critical_threshold = Column(Float, nullable=True)
    
    # Metadata
    analysis_date = Column(DateTime, nullable=False, default=datetime.utcnow)


class RiskAssessmentRecord(Base):
    """Database model for risk assessment results."""
    
    __tablename__ = "risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(String(255), nullable=False, index=True)
    
    # Overall risk
    overall_risk_level = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    
    # Risk factors
    price_volatility_risk = Column(Float, nullable=False)
    market_timing_risk = Column(Float, nullable=False)
    supply_chain_risk = Column(Float, nullable=False)
    weather_risk = Column(Float, nullable=False)
    
    # Risk mitigation
    recommended_actions = Column(JSON, nullable=False)
    hedging_recommendations = Column(JSON, nullable=True)
    
    # Metadata
    analysis_date = Column(DateTime, nullable=False, default=datetime.utcnow)


class PriceImpactAnalysisRepository:
    """Repository for price impact analysis database operations."""
    
    def __init__(self, database_url: str = "sqlite:///./price_impact.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionLocal = SessionLocal
    
    def get_db_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    async def save_analysis_request(
        self,
        request: PriceImpactAnalysisRequest,
        response: PriceImpactAnalysisResponse
    ) -> str:
        """Save analysis request and response to database."""
        db = self.get_db_session()
        try:
            # Create analysis record
            analysis_record = PriceImpactAnalysisRecord(
                analysis_id=request.analysis_id,
                request_id=response.request_id,
                analysis_type=request.analysis_type.value,
                farm_id=request.farm_id,
                field_id=request.field_id,
                field_size_acres=request.field_size_acres,
                crop_type=request.crop_type,
                expected_yield_bu_per_acre=request.expected_yield_bu_per_acre,
                crop_price_per_bu=request.crop_price_per_bu,
                fertilizer_requirements=request.fertilizer_requirements,
                analysis_horizon_days=request.analysis_horizon_days,
                confidence_level=request.confidence_level,
                scenarios=[s.value for s in request.scenarios] if request.scenarios else None,
                custom_scenarios=request.custom_scenarios,
                price_change_percentages=request.price_change_percentages,
                volatility_threshold=request.volatility_threshold,
                analysis_result=json.loads(json.dumps(response.analysis_result.model_dump(), cls=DateTimeEncoder)) if response.analysis_result else None,
                success=response.success,
                error_message=response.error_message,
                error_code=response.error_code,
                processing_time_ms=response.processing_time_ms,
                confidence_score=response.analysis_result.confidence_score if response.analysis_result else None,
                data_quality_score=response.analysis_result.data_quality_score if response.analysis_result else None,
                data_sources_used=response.data_sources_used,
                created_by=request.created_by
            )
            
            db.add(analysis_record)
            db.commit()
            db.refresh(analysis_record)
            
            # Save metrics if analysis was successful
            if response.success and response.analysis_result:
                await self._save_analysis_metrics(response.analysis_result, db)
                await self._save_sensitivity_results(response.analysis_result, db)
                await self._save_risk_assessment(response.analysis_result, db)
            
            return str(analysis_record.id)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving analysis request: {e}")
            raise
        finally:
            db.close()
    
    async def _save_analysis_metrics(
        self,
        analysis_result: PriceImpactAnalysisResult,
        db: Session
    ) -> None:
        """Save analysis metrics to database."""
        try:
            # Save baseline metrics
            baseline_record = PriceImpactMetricsRecord(
                analysis_id=analysis_result.analysis_id,
                scenario_name="baseline",
                total_fertilizer_cost=analysis_result.baseline_metrics.total_fertilizer_cost,
                total_crop_revenue=analysis_result.baseline_metrics.total_crop_revenue,
                net_profit=analysis_result.baseline_metrics.net_profit,
                profit_margin_percent=analysis_result.baseline_metrics.profit_margin_percent,
                fertilizer_cost_per_acre=analysis_result.baseline_metrics.fertilizer_cost_per_acre,
                fertilizer_cost_per_bu=analysis_result.baseline_metrics.fertilizer_cost_per_bu,
                crop_revenue_per_acre=analysis_result.baseline_metrics.crop_revenue_per_acre,
                price_impact_percent=analysis_result.baseline_metrics.price_impact_percent,
                profitability_change_percent=analysis_result.baseline_metrics.profitability_change_percent,
                value_at_risk=analysis_result.baseline_metrics.value_at_risk,
                expected_shortfall=analysis_result.baseline_metrics.expected_shortfall,
                volatility_impact=analysis_result.baseline_metrics.volatility_impact
            )
            db.add(baseline_record)
            
            # Save scenario metrics
            for scenario in analysis_result.scenarios:
                scenario_record = PriceImpactMetricsRecord(
                    analysis_id=analysis_result.analysis_id,
                    scenario_name=scenario.get('scenario_name', 'unknown'),
                    total_fertilizer_cost=scenario.get('total_fertilizer_cost', 0),
                    total_crop_revenue=scenario.get('total_crop_revenue', 0),
                    net_profit=scenario.get('net_profit', 0),
                    profit_margin_percent=scenario.get('profit_margin_percent', 0),
                    fertilizer_cost_per_acre=scenario.get('fertilizer_cost_per_acre', 0),
                    fertilizer_cost_per_bu=scenario.get('fertilizer_cost_per_bu', 0),
                    crop_revenue_per_acre=scenario.get('crop_revenue_per_acre', 0),
                    price_impact_percent=scenario.get('price_impact_percent', 0),
                    profitability_change_percent=scenario.get('profit_change_percent', 0)
                )
                db.add(scenario_record)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error saving analysis metrics: {e}")
            raise
    
    async def _save_sensitivity_results(
        self,
        analysis_result: PriceImpactAnalysisResult,
        db: Session
    ) -> None:
        """Save sensitivity analysis results to database."""
        try:
            if analysis_result.sensitivity_results:
                for sensitivity_result in analysis_result.sensitivity_results:
                    sensitivity_record = SensitivityAnalysisRecord(
                        analysis_id=analysis_result.analysis_id,
                        parameter_name=sensitivity_result.parameter_name,
                        parameter_values=sensitivity_result.parameter_values,
                        impact_values=sensitivity_result.impact_values,
                        elasticity=sensitivity_result.elasticity,
                        sensitivity_score=sensitivity_result.sensitivity_score,
                        critical_threshold=sensitivity_result.critical_threshold
                    )
                    db.add(sensitivity_record)
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving sensitivity results: {e}")
            raise
    
    async def _save_risk_assessment(
        self,
        analysis_result: PriceImpactAnalysisResult,
        db: Session
    ) -> None:
        """Save risk assessment results to database."""
        try:
            if analysis_result.risk_assessment:
                risk_record = RiskAssessmentRecord(
                    analysis_id=analysis_result.analysis_id,
                    overall_risk_level=analysis_result.risk_assessment.overall_risk_level.value,
                    risk_score=analysis_result.risk_assessment.risk_score,
                    price_volatility_risk=analysis_result.risk_assessment.price_volatility_risk,
                    market_timing_risk=analysis_result.risk_assessment.market_timing_risk,
                    supply_chain_risk=analysis_result.risk_assessment.supply_chain_risk,
                    weather_risk=analysis_result.risk_assessment.weather_risk,
                    recommended_actions=analysis_result.risk_assessment.recommended_actions,
                    hedging_recommendations=analysis_result.risk_assessment.hedging_recommendations
                )
                db.add(risk_record)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving risk assessment: {e}")
            raise
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[PriceImpactAnalysisRecord]:
        """Get analysis record by analysis ID."""
        db = self.get_db_session()
        try:
            return db.query(PriceImpactAnalysisRecord).filter(
                PriceImpactAnalysisRecord.analysis_id == analysis_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving analysis {analysis_id}: {e}")
            return None
        finally:
            db.close()
    
    async def get_analyses_by_farm(self, farm_id: str, limit: int = 10) -> List[PriceImpactAnalysisRecord]:
        """Get analyses for a specific farm."""
        db = self.get_db_session()
        try:
            return db.query(PriceImpactAnalysisRecord).filter(
                PriceImpactAnalysisRecord.farm_id == farm_id
            ).order_by(PriceImpactAnalysisRecord.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving analyses for farm {farm_id}: {e}")
            return []
        finally:
            db.close()
    
    async def get_analyses_by_field(self, field_id: str, limit: int = 10) -> List[PriceImpactAnalysisRecord]:
        """Get analyses for a specific field."""
        db = self.get_db_session()
        try:
            return db.query(PriceImpactAnalysisRecord).filter(
                PriceImpactAnalysisRecord.field_id == field_id
            ).order_by(PriceImpactAnalysisRecord.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving analyses for field {field_id}: {e}")
            return []
        finally:
            db.close()
    
    async def get_metrics_by_analysis(self, analysis_id: str) -> List[PriceImpactMetricsRecord]:
        """Get metrics for a specific analysis."""
        db = self.get_db_session()
        try:
            return db.query(PriceImpactMetricsRecord).filter(
                PriceImpactMetricsRecord.analysis_id == analysis_id
            ).all()
        except Exception as e:
            logger.error(f"Error retrieving metrics for analysis {analysis_id}: {e}")
            return []
        finally:
            db.close()
    
    async def get_sensitivity_results(self, analysis_id: str) -> List[SensitivityAnalysisRecord]:
        """Get sensitivity analysis results for a specific analysis."""
        db = self.get_db_session()
        try:
            return db.query(SensitivityAnalysisRecord).filter(
                SensitivityAnalysisRecord.analysis_id == analysis_id
            ).all()
        except Exception as e:
            logger.error(f"Error retrieving sensitivity results for analysis {analysis_id}: {e}")
            return []
        finally:
            db.close()
    
    async def get_risk_assessment(self, analysis_id: str) -> Optional[RiskAssessmentRecord]:
        """Get risk assessment for a specific analysis."""
        db = self.get_db_session()
        try:
            return db.query(RiskAssessmentRecord).filter(
                RiskAssessmentRecord.analysis_id == analysis_id
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving risk assessment for analysis {analysis_id}: {e}")
            return None
        finally:
            db.close()
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis and related records."""
        db = self.get_db_session()
        try:
            # Delete related records first
            db.query(PriceImpactMetricsRecord).filter(
                PriceImpactMetricsRecord.analysis_id == analysis_id
            ).delete()
            
            db.query(SensitivityAnalysisRecord).filter(
                SensitivityAnalysisRecord.analysis_id == analysis_id
            ).delete()
            
            db.query(RiskAssessmentRecord).filter(
                RiskAssessmentRecord.analysis_id == analysis_id
            ).delete()
            
            # Delete main analysis record
            result = db.query(PriceImpactAnalysisRecord).filter(
                PriceImpactAnalysisRecord.analysis_id == analysis_id
            ).delete()
            
            db.commit()
            return result > 0
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting analysis {analysis_id}: {e}")
            return False
        finally:
            db.close()
    
    async def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics."""
        db = self.get_db_session()
        try:
            total_analyses = db.query(PriceImpactAnalysisRecord).count()
            successful_analyses = db.query(PriceImpactAnalysisRecord).filter(
                PriceImpactAnalysisRecord.success == True
            ).count()
            
            # Get analysis types distribution
            analysis_types = db.query(
                PriceImpactAnalysisRecord.analysis_type,
                func.count(PriceImpactAnalysisRecord.id)
            ).group_by(PriceImpactAnalysisRecord.analysis_type).all()
            
            return {
                "total_analyses": total_analyses,
                "successful_analyses": successful_analyses,
                "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
                "analysis_types": {t[0]: t[1] for t in analysis_types}
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis statistics: {e}")
            return {}
        finally:
            db.close()


# Global repository instance
price_impact_repository = PriceImpactAnalysisRepository()