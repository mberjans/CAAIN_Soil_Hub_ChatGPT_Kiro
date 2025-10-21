"""
SQLAlchemy models for fertilizer price tracking and optimization.

This module defines the database models for storing fertilizer types and their
associated price data, supporting the fertilizer optimization service.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

# Create declarative base for all models
Base = declarative_base()


class FertilizerType(Base):
    """
    Model representing different types of fertilizers.
    
    Stores basic information about fertilizer categories and types,
    serving as the reference for price data.
    """
    __tablename__ = "fertilizer_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to price records
    prices = relationship("FertilizerPrice", back_populates="fertilizer_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FertilizerType(id={self.id}, name='{self.name}', category='{self.category}')>"


class FertilizerPrice(Base):
    """
    Model representing price data for specific fertilizer types.
    
    Stores historical and current price information for fertilizers,
    including regional variations and data sources.
    """
    __tablename__ = "fertilizer_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fertilizer_type_id = Column(Integer, ForeignKey("fertilizer_types.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Price with 2 decimal places
    price_date = Column(Date, nullable=False)
    region = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to fertilizer type
    fertilizer_type = relationship("FertilizerType", back_populates="prices")

    def __repr__(self):
        return f"<FertilizerPrice(id={self.id}, fertilizer_type_id={self.fertilizer_type_id}, price={self.price}, region='{self.region}')>"