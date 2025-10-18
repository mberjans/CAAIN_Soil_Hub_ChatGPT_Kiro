"""
Database persistence for fertilizer strategy management.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..models.strategy_management_models import (
    FieldStrategyData,
    PerformanceMetric,
    SaveStrategyRequest,
)
from ..models.mobile_strategy_tracking_models import MobileStrategyProgressEntry

logger = logging.getLogger(__name__)

Base = declarative_base()


class StrategyRecord(Base):
    """Top-level strategy metadata record."""

    __tablename__ = "strategy_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    strategy_id = Column(String(36), unique=True, nullable=False, index=True)
    strategy_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(36), nullable=False, index=True)
    farm_id = Column(String(36), nullable=True, index=True)
    is_template = Column(Boolean, nullable=False, default=False)
    tags = Column(JSON, nullable=False, default=list)
    sharing_settings = Column(JSON, nullable=False, default=dict)
    metadata_payload = Column(JSON, nullable=False, default=dict)
    latest_version = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyVersionRecord(Base):
    """Versioned snapshot of strategy configuration."""

    __tablename__ = "strategy_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    version_id = Column(String(36), unique=True, nullable=False, index=True)
    strategy_id = Column(String(36), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    version_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(36), nullable=False)
    field_strategies = Column(JSON, nullable=False, default=list)
    economic_summary = Column(JSON, nullable=False, default=dict)
    environmental_metrics = Column(JSON, nullable=False, default=dict)
    roi_estimate = Column(Float, nullable=True)
    metadata_snapshot = Column(JSON, nullable=False, default=dict)


class StrategyPerformanceRecord(Base):
    """Performance tracking data for strategies."""

    __tablename__ = "strategy_performance"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    strategy_id = Column(String(36), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    reporting_period_start = Column(DateTime, nullable=False)
    reporting_period_end = Column(DateTime, nullable=False)
    realized_yield = Column(Float, nullable=True)
    realized_cost = Column(Float, nullable=True)
    realized_revenue = Column(Float, nullable=True)
    performance_metrics = Column(JSON, nullable=False, default=list)
    observations = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class MobileStrategyActivityRecord(Base):
    """Mobile activity tracking data recorded from the field."""

    __tablename__ = "mobile_strategy_activity"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    activity_id = Column(String(36), unique=True, nullable=False, index=True)
    strategy_id = Column(String(36), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    user_id = Column(String(64), nullable=False, index=True)
    field_id = Column(String(64), nullable=True, index=True)
    activity_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="recorded")
    activity_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    device_identifier = Column(String(128), nullable=True)
    captured_offline = Column(Boolean, nullable=False, default=False)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    gps_accuracy = Column(Float, nullable=True)
    application_detail = Column(JSON, nullable=False, default=dict)
    cost_summary = Column(JSON, nullable=False, default=dict)
    yield_summary = Column(JSON, nullable=False, default=dict)
    photo_metadata = Column(JSON, nullable=False, default=list)
    attachments = Column(JSON, nullable=False, default=dict)
    client_event_id = Column(String(128), nullable=False, unique=True, index=True)
    conflict_resolved = Column(Boolean, nullable=False, default=False)
    sync_status = Column(String(32), nullable=False, default="pending")
    synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class StrategyRepository:
    """Repository encapsulating database interactions."""

    def __init__(
        self,
        database_url: str = "sqlite:///./strategy_management.db",
        engine_options: Optional[Dict[str, Any]] = None,
    ):
        options: Dict[str, Any] = {}

        if database_url == "sqlite:///:memory:":
            options["connect_args"] = {"check_same_thread": False}
            options["poolclass"] = StaticPool
        else:
            options["connect_args"] = {"check_same_thread": False}

        if engine_options:
            for key in engine_options:
                options[key] = engine_options[key]

        self.engine = create_engine(database_url, **options)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        """Return a new database session."""
        return self.SessionLocal()

    def save_strategy(
        self,
        request: SaveStrategyRequest,
        strategy_id: str,
    ) -> Tuple[bool, StrategyRecord, StrategyVersionRecord]:
        """Persist strategy data and return created state with records."""
        session = self.get_session()
        created = False

        try:
            strategy_record = session.query(StrategyRecord).filter(StrategyRecord.strategy_id == strategy_id).first()

            if strategy_record is None:
                created = True
                strategy_record = StrategyRecord(
                    strategy_id=strategy_id,
                    strategy_name=request.strategy_name,
                    description=request.description,
                    user_id=request.user_id,
                    farm_id=request.farm_id,
                    is_template=request.is_template,
                    tags=self._serialize_tags(request.tags),
                    sharing_settings=request.sharing.model_dump(),
                    metadata_payload=self._serialize_metadata(request.metadata),
                    latest_version=0,
                )
                session.add(strategy_record)
            else:
                strategy_record.strategy_name = request.strategy_name
                strategy_record.description = request.description
                strategy_record.is_template = request.is_template
                strategy_record.tags = self._serialize_tags(request.tags)
                strategy_record.farm_id = request.farm_id
                strategy_record.sharing_settings = request.sharing.model_dump()
                strategy_record.metadata_payload = self._serialize_metadata(request.metadata)
                strategy_record.updated_at = datetime.utcnow()

            next_version = strategy_record.latest_version + 1
            field_strategies_payload = self._serialize_field_strategies(request.field_strategies)

            version_record = StrategyVersionRecord(
                version_id=str(uuid4()),
                strategy_id=strategy_id,
                version_number=next_version,
                version_notes=request.version_notes,
                created_by=request.user_id,
                field_strategies=field_strategies_payload,
                economic_summary=self._safe_json(request.economic_summary),
                environmental_metrics=self._safe_json(request.environmental_metrics),
                roi_estimate=request.roi_estimate,
                metadata_snapshot=self._serialize_metadata(request.metadata),
            )

            session.add(version_record)

            strategy_record.latest_version = next_version
            session.commit()

            session.refresh(strategy_record)
            session.refresh(version_record)

            return created, strategy_record, version_record

        except Exception as error:
            session.rollback()
            logger.error("Failed to save strategy: %s", error)
            raise
        finally:
            session.close()

    def _serialize_tags(self, tags: List[str]) -> List[str]:
        """Normalize tag collection."""
        normalized: List[str] = []
        for tag in tags:
            if tag is None:
                continue
            text = str(tag).strip()
            if text:
                normalized.append(text)
        return normalized

    def _serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata payload is JSON serializable."""
        try:
            json.dumps(metadata)
            return metadata
        except TypeError:
            fallback: Dict[str, Any] = {}
            for key in metadata:
                try:
                    json.dumps({key: metadata[key]})
                    fallback[key] = metadata[key]
                except TypeError:
                    fallback[key] = str(metadata[key])
            return fallback

    def _serialize_field_strategies(self, field_strategies: List[FieldStrategyData]) -> List[Dict[str, Any]]:
        """Serialize field strategy data."""
        serialized: List[Dict[str, Any]] = []
        for field_strategy in field_strategies:
            payload = field_strategy.model_dump()
            serialized.append(payload)
        return serialized

    def _safe_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure payload can be stored as JSON."""
        try:
            json.dumps(payload)
            return payload
        except TypeError:
            sanitized: Dict[str, Any] = {}
            for key in payload:
                value = payload[key]
                try:
                    json.dumps({key: value})
                    sanitized[key] = value
                except TypeError:
                    sanitized[key] = str(value)
            return sanitized

    def fetch_strategy(self, strategy_id: str) -> Optional[StrategyRecord]:
        """Fetch strategy metadata."""
        session = self.get_session()
        try:
            return session.query(StrategyRecord).filter(StrategyRecord.strategy_id == strategy_id).first()
        finally:
            session.close()

    def fetch_versions(self, strategy_id: str) -> List[StrategyVersionRecord]:
        """Fetch all versions for a strategy."""
        session = self.get_session()
        try:
            query = session.query(StrategyVersionRecord).filter(StrategyVersionRecord.strategy_id == strategy_id).order_by(
                StrategyVersionRecord.version_number
            )
            versions: List[StrategyVersionRecord] = []
            for record in query:
                versions.append(record)
            return versions
        finally:
            session.close()

    def fetch_latest_version(self, strategy_id: str) -> Optional[StrategyVersionRecord]:
        """Fetch the most recent version record for a strategy."""
        session = self.get_session()
        try:
            query = (
                session.query(StrategyVersionRecord)
                .filter(StrategyVersionRecord.strategy_id == strategy_id)
                .order_by(StrategyVersionRecord.version_number.desc())
            )
            record = query.first()
            return record
        finally:
            session.close()

    def fetch_version(self, strategy_id: str, version_number: int) -> Optional[StrategyVersionRecord]:
        """Fetch a specific version record."""
        session = self.get_session()
        try:
            record = (
                session.query(StrategyVersionRecord)
                .filter(StrategyVersionRecord.strategy_id == strategy_id)
                .filter(StrategyVersionRecord.version_number == version_number)
                .first()
            )
            return record
        finally:
            session.close()

    def log_performance(
        self,
        strategy_id: str,
        version_number: int,
        reporting_period_start: datetime,
        reporting_period_end: datetime,
        realized_yield: Optional[float],
        realized_cost: Optional[float],
        realized_revenue: Optional[float],
        performance_metrics: List[PerformanceMetric],
        observations: Optional[str],
    ) -> StrategyPerformanceRecord:
        """Persist performance tracking information."""
        session = self.get_session()
        try:
            metrics_payload: List[Dict[str, Any]] = []
            for metric in performance_metrics:
                metrics_payload.append(
                    {
                        "metric_name": metric.metric_name,
                        "metric_value": metric.metric_value,
                    }
                )

            record = StrategyPerformanceRecord(
                strategy_id=strategy_id,
                version_number=version_number,
                reporting_period_start=reporting_period_start,
                reporting_period_end=reporting_period_end,
                realized_yield=realized_yield,
                realized_cost=realized_cost,
                realized_revenue=realized_revenue,
                performance_metrics=metrics_payload,
                observations=observations,
            )

            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except Exception as error:
            session.rollback()
            logger.error("Failed to log strategy performance: %s", error)
            raise
        finally:
            session.close()

    def fetch_mobile_activity_by_client_event(
        self,
        client_event_id: str,
    ) -> Optional[MobileStrategyActivityRecord]:
        """Fetch stored mobile activity by client event identifier."""
        session = self.get_session()
        try:
            record = (
                session.query(MobileStrategyActivityRecord)
                .filter(MobileStrategyActivityRecord.client_event_id == client_event_id)
                .first()
            )
            return record
        finally:
            session.close()

    def log_mobile_activity(
        self,
        entry: MobileStrategyProgressEntry,
    ) -> Dict[str, Any]:
        """Persist mobile strategy activity with conflict resolution."""
        session = self.get_session()
        created = False
        conflict_resolved = False

        try:
            existing = (
                session.query(MobileStrategyActivityRecord)
                .filter(MobileStrategyActivityRecord.client_event_id == entry.client_event_id)
                .first()
            )

            photos_payload: List[Dict[str, Any]] = []
            if entry.photos:
                index = 0
                while index < len(entry.photos):
                    photo = entry.photos[index]
                    if photo is not None:
                        photo_dict = photo.model_dump()
                        if "captured_at" in photo_dict:
                            captured_value = photo_dict.get("captured_at")
                            if isinstance(captured_value, datetime):
                                photo_dict["captured_at"] = captured_value.isoformat()
                        photos_payload.append(photo_dict)
                    index += 1

            application_payload: Dict[str, Any] = {}
            if entry.application is not None:
                application_payload = entry.application.model_dump()

            cost_payload: Dict[str, Any] = {}
            if entry.cost_summary is not None:
                cost_payload = entry.cost_summary.model_dump()

            yield_payload: Dict[str, Any] = {}
            if entry.yield_summary is not None:
                yield_payload = entry.yield_summary.model_dump()

            attachments_payload: Dict[str, Any] = {}
            if entry.attachments:
                for key in entry.attachments:
                    value = entry.attachments[key]
                    if isinstance(value, datetime):
                        attachments_payload[key] = value.isoformat()
                    else:
                        attachments_payload[key] = value

            if entry.notes:
                attachments_payload["notes"] = entry.notes

            if existing:
                conflict_resolved = True
                existing.status = entry.status
                existing.activity_timestamp = entry.activity_timestamp
                existing.user_id = entry.user_id
                existing.field_id = entry.field_id
                existing.activity_type = entry.activity_type
                existing.device_identifier = entry.device_identifier
                existing.captured_offline = entry.captured_offline
                existing.application_detail = application_payload
                existing.cost_summary = cost_payload
                existing.yield_summary = yield_payload
                existing.photo_metadata = photos_payload
                existing.attachments = attachments_payload
                existing.conflict_resolved = True
                if entry.gps:
                    existing.gps_latitude = entry.gps.latitude
                    existing.gps_longitude = entry.gps.longitude
                    existing.gps_accuracy = entry.gps.accuracy
                session.commit()
                session.refresh(existing)
                return {
                    "created": created,
                    "conflict_resolved": conflict_resolved,
                    "record": existing,
                }

            activity_id = str(uuid4())
            gps_latitude = None
            gps_longitude = None
            gps_accuracy = None
            if entry.gps:
                gps_latitude = entry.gps.latitude
                gps_longitude = entry.gps.longitude
                gps_accuracy = entry.gps.accuracy

            record = MobileStrategyActivityRecord(
                activity_id=activity_id,
                strategy_id=entry.strategy_id,
                version_number=entry.version_number,
                user_id=entry.user_id,
                field_id=entry.field_id,
                activity_type=entry.activity_type,
                status=entry.status,
                activity_timestamp=entry.activity_timestamp,
                device_identifier=entry.device_identifier,
                captured_offline=entry.captured_offline,
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude,
                gps_accuracy=gps_accuracy,
                application_detail=application_payload,
                cost_summary=cost_payload,
                yield_summary=yield_payload,
                photo_metadata=photos_payload,
                attachments=attachments_payload,
                client_event_id=entry.client_event_id,
                conflict_resolved=False,
                sync_status="pending",
            )

            session.add(record)
            session.commit()
            session.refresh(record)
            created = True

            return {
                "created": created,
                "conflict_resolved": conflict_resolved,
                "record": record,
            }

        except Exception as error:
            session.rollback()
            logger.error("Failed to log mobile activity: %s", error)
            raise
        finally:
            session.close()

    def fetch_recent_mobile_activities(
        self,
        strategy_id: str,
        limit: int = 10,
    ) -> List[MobileStrategyActivityRecord]:
        """Fetch recent mobile activities for a strategy."""
        session = self.get_session()
        try:
            query = (
                session.query(MobileStrategyActivityRecord)
                .filter(MobileStrategyActivityRecord.strategy_id == strategy_id)
                .order_by(MobileStrategyActivityRecord.activity_timestamp.desc())
            )
            if limit and limit > 0:
                query = query.limit(limit)
            records = query.all()
            return records
        finally:
            session.close()

    def calculate_mobile_progress(
        self,
        strategy_id: str,
        version_number: int,
    ) -> Dict[str, Any]:
        """Calculate progress metrics based on mobile activities."""
        session = self.get_session()
        try:
            records = (
                session.query(MobileStrategyActivityRecord)
                .filter(MobileStrategyActivityRecord.strategy_id == strategy_id)
                .filter(MobileStrategyActivityRecord.version_number == version_number)
                .all()
            )

            total_events = 0
            completed_events = 0
            pending_actions = 0
            last_synced_at: Optional[datetime] = None

            index = 0
            while index < len(records):
                record = records[index]
                total_events += 1
                status_value = record.status or ""
                normalized_status = status_value.lower()

                if normalized_status in ("completed", "complete", "done"):
                    completed_events += 1
                elif normalized_status in ("pending", "scheduled", "in_progress"):
                    pending_actions += 1

                if record.synced_at:
                    if last_synced_at is None or record.synced_at > last_synced_at:
                        last_synced_at = record.synced_at

                index += 1

            progress_percent = 0.0
            if total_events > 0:
                progress_percent = (completed_events / total_events) * 100.0

            return {
                "progress_percent": progress_percent,
                "pending_actions": pending_actions,
                "total_events": total_events,
                "last_synced_at": last_synced_at,
            }
        finally:
            session.close()

    def mark_activity_synced(
        self,
        activity_id: str,
        sync_status: str = "synced",
    ) -> Optional[MobileStrategyActivityRecord]:
        """Update activity sync status."""
        session = self.get_session()
        try:
            record = (
                session.query(MobileStrategyActivityRecord)
                .filter(MobileStrategyActivityRecord.activity_id == activity_id)
                .first()
            )
            if record is None:
                return None

            record.sync_status = sync_status
            record.synced_at = datetime.utcnow()
            session.commit()
            session.refresh(record)
            return record
        except Exception as error:
            session.rollback()
            logger.error("Failed to update activity sync status: %s", error)
            raise
        finally:
            session.close()

    def fetch_latest_performance(
        self,
        strategy_id: str,
    ) -> Optional[StrategyPerformanceRecord]:
        """Fetch the latest performance record for a strategy."""
        session = self.get_session()
        try:
            record = (
                session.query(StrategyPerformanceRecord)
                .filter(StrategyPerformanceRecord.strategy_id == strategy_id)
                .order_by(StrategyPerformanceRecord.recorded_at.desc())
                .first()
            )
            return record
        finally:
            session.close()
