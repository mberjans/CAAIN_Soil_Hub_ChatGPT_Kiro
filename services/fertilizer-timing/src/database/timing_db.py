"""
Database utilities for the fertilizer timing optimization microservice.

Provides asynchronous database initialization, session management, and simple
SQLAlchemy models for persisting optimization runs and generated alerts.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, Optional
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class TimingOptimizationRecord(Base):
    """Database model for storing optimization requests and results."""

    __tablename__ = "timing_optimization_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    request_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    request_payload = Column(JSON, nullable=False)
    result_payload = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)


class TimingAlertRecord(Base):
    """Database model for storing generated alerts."""

    __tablename__ = "timing_alert_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    request_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    action = Column(Text, nullable=True)


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[sessionmaker] = None


def _database_url() -> str:
    """Resolve the database URL, falling back to a local SQLite database."""
    url = os.getenv("FERTILIZER_TIMING_DATABASE_URL")
    if url and url.strip():
        return url.strip()
    return "sqlite+aiosqlite:///./fertilizer_timing.db"


async def initialize_database() -> None:
    """Create the async engine, session factory, and database tables."""
    global _engine  # pylint: disable=global-statement
    global _session_factory  # pylint: disable=global-statement

    if _engine is not None and _session_factory is not None:
        return

    database_url = _database_url()
    logger.info("Initializing fertilizer timing database at %s", database_url)

    _engine = create_async_engine(database_url, echo=False, future=True)
    _session_factory = sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with _engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def shutdown_database() -> None:
    """Dispose the async engine and clear session factory references."""
    global _engine  # pylint: disable=global-statement
    global _session_factory  # pylint: disable=global-statement

    if _session_factory is not None:
        _session_factory = None

    if _engine is not None:
        await _engine.dispose()
        _engine = None


def get_session_factory() -> sessionmaker:
    """Return the session factory, ensuring the database is initialized."""
    if _session_factory is None:
        message = "Database not initialized. Call initialize_database() first."
        raise RuntimeError(message)
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide an async context manager that yields a database session."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


async def reset_database() -> None:
    """
    Drop and recreate all tables. Intended for testing environments only.
    """
    if _engine is None:
        await initialize_database()

    if _engine is None:
        raise RuntimeError("Engine still unavailable after initialization")

    async with _engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


__all__ = [
    "TimingAlertRecord",
    "TimingOptimizationRecord",
    "get_session",
    "get_session_factory",
    "initialize_database",
    "reset_database",
    "shutdown_database",
]
