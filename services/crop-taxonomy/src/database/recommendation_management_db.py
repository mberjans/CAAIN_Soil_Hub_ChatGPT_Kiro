"""
Recommendation Management Database Access Layer

Database operations for recommendation management system including
saving, tracking, feedback collection, and updating variety recommendations.
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from sqlalchemy import create_engine, and_, or_, func, text, Column, String, Integer, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, joinedload, relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

# Create base for database models
Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class SavedVarietyRecommendationDB(Base):
    """Database model for saved variety recommendations."""
    
    __tablename__ = 'saved_variety_recommendations'
    
    recommendation_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    crop_id = Column(String, nullable=False, index=True)
    variety_ids = Column(JSON, nullable=False)  # List of variety IDs
    farm_context = Column(JSON, nullable=False)
    farmer_preferences = Column(JSON, nullable=False)
    recommendation_criteria = Column(JSON, nullable=False)
    recommendation_source = Column(String, nullable=False, default='system_generated')
    status = Column(String, nullable=False, default='active')
    saved_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True, default=list)
    recommendation_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history_records = relationship("RecommendationHistoryDB", back_populates="recommendation")
    feedback_records = relationship("RecommendationFeedbackDB", back_populates="recommendation")


class RecommendationHistoryDB(Base):
    """Database model for recommendation history tracking."""
    
    __tablename__ = 'recommendation_history'
    
    history_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    recommendation_id = Column(String, ForeignKey('saved_variety_recommendations.recommendation_id'), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False, index=True)
    action_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    action_data = Column(JSON, nullable=True, default=dict)
    session_context = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("SavedVarietyRecommendationDB", back_populates="history_records")


class RecommendationFeedbackDB(Base):
    """Database model for recommendation feedback."""
    
    __tablename__ = 'recommendation_feedback'
    
    feedback_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    recommendation_id = Column(String, ForeignKey('saved_variety_recommendations.recommendation_id'), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    feedback_type = Column(String, nullable=False, index=True)
    feedback_value = Column(JSON, nullable=False)  # Can store various types
    feedback_text = Column(Text, nullable=True)
    variety_performance = Column(JSON, nullable=True)
    implementation_notes = Column(Text, nullable=True)
    modification_details = Column(JSON, nullable=True)
    confidence_level = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    feedback_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("SavedVarietyRecommendationDB", back_populates="feedback_records")


# ============================================================================
# DATABASE ACCESS CLASS
# ============================================================================

class RecommendationManagementDatabase:
    """Database access layer for recommendation management."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database connection.
        
        Args:
            database_url: Optional database URL override
        """
        if database_url is None:
            # Default PostgreSQL connection for AFAS system
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://afas_user:afas_password@localhost:5432/afas_db'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Get a database session with proper exception handling."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # ============================================================================
    # SAVED RECOMMENDATIONS OPERATIONS
    # ============================================================================
    
    def save_recommendation(
        self,
        user_id: UUID,
        session_id: Optional[str],
        crop_id: str,
        variety_ids: List[str],
        farm_context: Dict[str, Any],
        farmer_preferences: Dict[str, Any],
        recommendation_criteria: Dict[str, Any],
        recommendation_source: str = "system_generated",
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save a variety recommendation."""
        try:
            with self.get_session() as session:
                recommendation = SavedVarietyRecommendationDB(
                    user_id=str(user_id),
                    session_id=session_id,
                    crop_id=crop_id,
                    variety_ids=variety_ids,
                    farm_context=farm_context,
                    farmer_preferences=farmer_preferences,
                    recommendation_criteria=recommendation_criteria,
                    recommendation_source=recommendation_source,
                    notes=notes,
                    tags=tags or [],
                    expires_at=expires_at,
                    metadata=metadata or {}
                )
                
                session.add(recommendation)
                session.flush()  # Get the ID
                
                # Log the save action
                self._log_history_action(
                    session=session,
                    recommendation_id=recommendation.recommendation_id,
                    user_id=str(user_id),
                    action_type="save",
                    action_data={"variety_count": len(variety_ids), "crop_id": crop_id}
                )
                
                return recommendation.recommendation_id
                
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            raise
    
    def get_recommendation(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Get a saved recommendation by ID."""
        try:
            with self.get_session() as session:
                recommendation = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.recommendation_id == recommendation_id
                ).first()
                
                if not recommendation:
                    return None
                
                return self._recommendation_to_dict(recommendation)
                
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            raise
    
    def get_user_recommendations(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        crop_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get saved recommendations for a user."""
        try:
            with self.get_session() as session:
                query = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.user_id == str(user_id)
                )
                
                if status:
                    query = query.filter(SavedVarietyRecommendationDB.status == status)
                
                if crop_id:
                    query = query.filter(SavedVarietyRecommendationDB.crop_id == crop_id)
                
                recommendations = query.order_by(
                    SavedVarietyRecommendationDB.saved_at.desc()
                ).offset(offset).limit(limit).all()
                
                return [self._recommendation_to_dict(rec) for rec in recommendations]
                
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            raise
    
    def update_recommendation(
        self,
        recommendation_id: str,
        user_id: UUID,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a saved recommendation."""
        try:
            with self.get_session() as session:
                recommendation = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.recommendation_id == recommendation_id,
                    SavedVarietyRecommendationDB.user_id == str(user_id)
                ).first()
                
                if not recommendation:
                    return False
                
                # Update fields
                updated_fields = []
                for field, value in updates.items():
                    if hasattr(recommendation, field) and value is not None:
                        setattr(recommendation, field, value)
                        updated_fields.append(field)
                
                recommendation.updated_at = datetime.utcnow()
                
                # Log the update action
                self._log_history_action(
                    session=session,
                    recommendation_id=recommendation_id,
                    user_id=str(user_id),
                    action_type="update",
                    action_data={"updated_fields": updated_fields}
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating recommendation: {e}")
            raise
    
    def delete_recommendation(self, recommendation_id: str, user_id: UUID) -> bool:
        """Delete a saved recommendation."""
        try:
            with self.get_session() as session:
                recommendation = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.recommendation_id == recommendation_id,
                    SavedVarietyRecommendationDB.user_id == str(user_id)
                ).first()
                
                if not recommendation:
                    return False
                
                # Log the delete action
                self._log_history_action(
                    session=session,
                    recommendation_id=recommendation_id,
                    user_id=str(user_id),
                    action_type="delete",
                    action_data={"crop_id": recommendation.crop_id}
                )
                
                session.delete(recommendation)
                return True
                
        except Exception as e:
            logger.error(f"Error deleting recommendation: {e}")
            raise
    
    # ============================================================================
    # HISTORY OPERATIONS
    # ============================================================================
    
    def get_recommendation_history(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        action_types: Optional[List[str]] = None,
        crop_ids: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get recommendation history for a user."""
        try:
            with self.get_session() as session:
                # Build query
                query = session.query(RecommendationHistoryDB).filter(
                    RecommendationHistoryDB.user_id == str(user_id)
                )
                
                if start_date:
                    query = query.filter(RecommendationHistoryDB.action_timestamp >= start_date)
                
                if end_date:
                    query = query.filter(RecommendationHistoryDB.action_timestamp <= end_date)
                
                if action_types:
                    query = query.filter(RecommendationHistoryDB.action_type.in_(action_types))
                
                if crop_ids:
                    # Join with recommendations to filter by crop
                    query = query.join(SavedVarietyRecommendationDB).filter(
                        SavedVarietyRecommendationDB.crop_id.in_(crop_ids)
                    )
                
                # Get total count
                total_count = query.count()
                
                # Get paginated results
                history_records = query.order_by(
                    RecommendationHistoryDB.action_timestamp.desc()
                ).offset(offset).limit(limit).all()
                
                return [self._history_to_dict(record) for record in history_records], total_count
                
        except Exception as e:
            logger.error(f"Error getting recommendation history: {e}")
            raise
    
    def _log_history_action(
        self,
        session: Session,
        recommendation_id: str,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> None:
        """Log a history action."""
        history_record = RecommendationHistoryDB(
            recommendation_id=recommendation_id,
            user_id=user_id,
            action_type=action_type,
            action_data=action_data
        )
        session.add(history_record)
    
    # ============================================================================
    # FEEDBACK OPERATIONS
    # ============================================================================
    
    def submit_feedback(
        self,
        recommendation_id: str,
        user_id: UUID,
        feedback_type: str,
        feedback_value: Any,
        feedback_text: Optional[str] = None,
        variety_performance: Optional[Dict[str, Any]] = None,
        implementation_notes: Optional[str] = None,
        modification_details: Optional[Dict[str, Any]] = None,
        confidence_level: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit feedback for a recommendation."""
        try:
            with self.get_session() as session:
                feedback = RecommendationFeedbackDB(
                    recommendation_id=recommendation_id,
                    user_id=str(user_id),
                    feedback_type=feedback_type,
                    feedback_value=feedback_value,
                    feedback_text=feedback_text,
                    variety_performance=variety_performance,
                    implementation_notes=implementation_notes,
                    modification_details=modification_details,
                    confidence_level=confidence_level,
                    metadata=metadata or {}
                )
                
                session.add(feedback)
                session.flush()  # Get the ID
                
                # Log the feedback action
                self._log_history_action(
                    session=session,
                    recommendation_id=recommendation_id,
                    user_id=str(user_id),
                    action_type="feedback",
                    action_data={"feedback_type": feedback_type, "feedback_id": feedback.feedback_id}
                )
                
                return feedback.feedback_id
                
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise
    
    def get_recommendation_feedback(
        self,
        recommendation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get feedback for a recommendation."""
        try:
            with self.get_session() as session:
                feedback_records = session.query(RecommendationFeedbackDB).filter(
                    RecommendationFeedbackDB.recommendation_id == recommendation_id
                ).order_by(
                    RecommendationFeedbackDB.submitted_at.desc()
                ).offset(offset).limit(limit).all()
                
                return [self._feedback_to_dict(feedback) for feedback in feedback_records]
                
        except Exception as e:
            logger.error(f"Error getting recommendation feedback: {e}")
            raise
    
    # ============================================================================
    # ANALYTICS OPERATIONS
    # ============================================================================
    
    def get_recommendation_analytics(self, user_id: UUID) -> Dict[str, Any]:
        """Get analytics for a user's recommendations."""
        try:
            with self.get_session() as session:
                # Get basic counts
                total_recommendations = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.user_id == str(user_id)
                ).count()
                
                active_recommendations = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.user_id == str(user_id),
                    SavedVarietyRecommendationDB.status == "active"
                ).count()
                
                implemented_recommendations = session.query(SavedVarietyRecommendationDB).filter(
                    SavedVarietyRecommendationDB.user_id == str(user_id),
                    SavedVarietyRecommendationDB.status == "implemented"
                ).count()
                
                # Get feedback count
                feedback_count = session.query(RecommendationFeedbackDB).filter(
                    RecommendationFeedbackDB.user_id == str(user_id)
                ).count()
                
                # Get average rating
                avg_rating_result = session.query(func.avg(RecommendationFeedbackDB.feedback_value)).filter(
                    RecommendationFeedbackDB.user_id == str(user_id),
                    RecommendationFeedbackDB.feedback_type == "rating"
                ).scalar()
                
                avg_rating = float(avg_rating_result) if avg_rating_result else None
                
                # Get most common crops
                crop_counts = session.query(
                    SavedVarietyRecommendationDB.crop_id,
                    func.count(SavedVarietyRecommendationDB.recommendation_id).label('count')
                ).filter(
                    SavedVarietyRecommendationDB.user_id == str(user_id)
                ).group_by(
                    SavedVarietyRecommendationDB.crop_id
                ).order_by(func.count(SavedVarietyRecommendationDB.recommendation_id).desc()).limit(5).all()
                
                most_common_crops = [{"crop_id": crop_id, "count": count} for crop_id, count in crop_counts]
                
                return {
                    "total_recommendations": total_recommendations,
                    "active_recommendations": active_recommendations,
                    "implemented_recommendations": implemented_recommendations,
                    "feedback_count": feedback_count,
                    "average_rating": avg_rating,
                    "most_common_crops": most_common_crops
                }
                
        except Exception as e:
            logger.error(f"Error getting recommendation analytics: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _recommendation_to_dict(self, recommendation: SavedVarietyRecommendationDB) -> Dict[str, Any]:
        """Convert recommendation database model to dictionary."""
        return {
            "recommendation_id": recommendation.recommendation_id,
            "user_id": recommendation.user_id,
            "session_id": recommendation.session_id,
            "crop_id": recommendation.crop_id,
            "variety_ids": recommendation.variety_ids,
            "farm_context": recommendation.farm_context,
            "farmer_preferences": recommendation.farmer_preferences,
            "recommendation_criteria": recommendation.recommendation_criteria,
            "recommendation_source": recommendation.recommendation_source,
            "status": recommendation.status,
            "saved_at": recommendation.saved_at,
            "expires_at": recommendation.expires_at,
            "notes": recommendation.notes,
            "tags": recommendation.tags,
            "metadata": recommendation.recommendation_metadata,
            "created_at": recommendation.created_at,
            "updated_at": recommendation.updated_at
        }
    
    def _history_to_dict(self, history: RecommendationHistoryDB) -> Dict[str, Any]:
        """Convert history database model to dictionary."""
        return {
            "history_id": history.history_id,
            "recommendation_id": history.recommendation_id,
            "user_id": history.user_id,
            "action_type": history.action_type,
            "action_timestamp": history.action_timestamp,
            "action_data": history.action_data,
            "session_context": history.session_context,
            "ip_address": history.ip_address,
            "user_agent": history.user_agent,
            "created_at": history.created_at
        }
    
    def _feedback_to_dict(self, feedback: RecommendationFeedbackDB) -> Dict[str, Any]:
        """Convert feedback database model to dictionary."""
        return {
            "feedback_id": feedback.feedback_id,
            "recommendation_id": feedback.recommendation_id,
            "user_id": feedback.user_id,
            "feedback_type": feedback.feedback_type,
            "feedback_value": feedback.feedback_value,
            "feedback_text": feedback.feedback_text,
            "variety_performance": feedback.variety_performance,
            "implementation_notes": feedback.implementation_notes,
            "modification_details": feedback.modification_details,
            "confidence_level": feedback.confidence_level,
            "submitted_at": feedback.submitted_at,
            "metadata": feedback.feedback_metadata,
            "created_at": feedback.created_at
        }


# Create a singleton instance for easy import
recommendation_management_db = RecommendationManagementDatabase()