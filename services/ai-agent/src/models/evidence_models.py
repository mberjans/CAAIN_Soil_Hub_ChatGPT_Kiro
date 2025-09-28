"""Evidence models for AI agent services.

Defines data structures for supporting evidence, source metadata,
credibility scoring, and aggregated summaries used by the
EvidenceManagementService.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class EvidenceSourceType(str, Enum):
    """Enumeration of supported evidence source types."""

    UNIVERSITY_RESEARCH = "university_research"
    EXTENSION_PUBLICATION = "extension_publication"
    GOVERNMENT_AGENCY = "government_agency"
    SEED_COMPANY_DATA = "seed_company_data"
    FARMER_TESTIMONIAL = "farmer_testimonial"
    PEER_REVIEWED_RESEARCH = "peer_reviewed_research"
    INTERNAL_ANALYSIS = "internal_analysis"
    UNKNOWN = "unknown"


class EvidenceStrengthLevel(str, Enum):
    """Strength level derived from evidence scoring."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    LIMITED = "limited"


class EvidenceRecord(BaseModel):
    """Detailed evidence record with scoring metadata."""

    id: str = Field(..., description="Unique evidence identifier")
    variety_name: Optional[str] = Field(None, description="Associated variety name")
    category: str = Field(..., description="Evidence category (yield, disease, etc.)")
    summary: str = Field(..., description="Concise evidence summary")
    source_name: str = Field(..., description="Source title or organization")
    source_type: EvidenceSourceType = Field(default=EvidenceSourceType.UNKNOWN)
    source_link: Optional[str] = Field(None, description="Reference URL or citation link")
    published_at: Optional[datetime] = Field(None, description="Publication or verification date")
    credibility_score: float = Field(..., ge=0.0, le=1.0, description="Credibility score between 0 and 1")
    strength_score: float = Field(..., ge=0.0, le=1.0, description="Strength score between 0 and 1")
    strength_level: EvidenceStrengthLevel = Field(default=EvidenceStrengthLevel.LIMITED)
    reliability_notes: Optional[str] = Field(None, description="Additional reliability notes")
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")

    @validator("summary")
    def validate_summary(cls, value: str) -> str:
        """Ensure summary content is not empty after stripping."""
        if value is None:
            raise ValueError("Summary content is required")
        normalized = value.strip()
        if len(normalized) == 0:
            raise ValueError("Summary content is required")
        return normalized


class EvidenceSummary(BaseModel):
    """Aggregated metrics for evidence collection."""

    total_records: int = Field(0, description="Number of evidence records")
    average_credibility: float = Field(0.0, ge=0.0, le=1.0, description="Average credibility across records")
    average_strength: float = Field(0.0, ge=0.0, le=1.0, description="Average strength across records")
    source_distribution: Dict[EvidenceSourceType, int] = Field(default_factory=dict, description="Distribution by source type")
    strength_distribution: Dict[EvidenceStrengthLevel, int] = Field(default_factory=dict, description="Distribution by strength level")
    latest_publication: Optional[datetime] = Field(None, description="Most recent publication date among evidence")
    high_credibility_records: int = Field(0, description="Count of records with high credibility scores")
    recent_evidence_ratio: float = Field(0.0, ge=0.0, le=1.0, description="Ratio of evidence within recency window")


class EvidenceCitation(BaseModel):
    """Structured citation entry for supporting evidence references."""

    citation_id: str = Field(..., description="Stable citation identifier")
    label: str = Field(..., description="Citation label for display (e.g., [1])")
    source_name: str = Field(..., description="Primary citation display name")
    source_type: EvidenceSourceType = Field(default=EvidenceSourceType.UNKNOWN, description="Evidence source classification")
    source_link: Optional[str] = Field(None, description="Link or reference for the citation")
    published_at: Optional[datetime] = Field(None, description="Publication date if available")
    strength_level: EvidenceStrengthLevel = Field(default=EvidenceStrengthLevel.LIMITED, description="Dominant strength level")
    categories: List[str] = Field(default_factory=list, description="Evidence categories supported by this citation")


class EvidencePackage(BaseModel):
    """Structured evidence payload returned by evidence management service."""

    variety_names: List[str] = Field(default_factory=list, description="Variety names covered by evidence")
    records: List[EvidenceRecord] = Field(default_factory=list, description="Evidence records")
    summary: EvidenceSummary = Field(default_factory=EvidenceSummary, description="Aggregated evidence summary")
    coverage_notes: List[str] = Field(default_factory=list, description="Coverage or follow-up notes")
    citations: List[EvidenceCitation] = Field(default_factory=list, description="Formatted citation references")
