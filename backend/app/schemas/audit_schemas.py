"""
Pydantic schemas for API request/response validation and serialization.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class AuditRequest(BaseModel):
    """Payload for POST /api/audits — server credentials to audit."""

    server_ip: str = Field(..., description="IP address or hostname of the target server")
    port: int = Field(default=22, ge=1, le=65535, description="SSH port")
    username: str = Field(..., description="SSH username")
    password: str = Field(..., description="SSH password")


# ---------------------------------------------------------------------------
# DTO / Sub-models
# ---------------------------------------------------------------------------

class FindingResponse(BaseModel):
    """Representing a single security finding in details response."""

    id: UUID
    severity: str
    issue: str
    evidence: Optional[str] = None
    explanation: Optional[str] = None
    impact: Optional[str] = None
    fix_command: Optional[str] = None

    model_config = {"from_attributes": True}


class SeverityBreakdown(BaseModel):
    """Count of findings per severity level."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class AuditSummaryResponse(BaseModel):
    """Summarized audit details for historical lists."""

    id: UUID
    server_ip: str
    audit_date: datetime
    security_score: Optional[int] = None
    severity_breakdown: SeverityBreakdown

    model_config = {"from_attributes": True}

    @field_validator("audit_date", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class AuditDetailResponse(BaseModel):
    """Detailed audit information including findings and report logs."""

    id: UUID
    server_ip: str
    audit_date: datetime
    raw_report: Optional[str] = None
    executive_summary: Optional[str] = None
    security_score: Optional[int] = None
    findings: List[FindingResponse] = []
    severity_breakdown: SeverityBreakdown

    model_config = {"from_attributes": True}

    @field_validator("audit_date", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


# ---------------------------------------------------------------------------
# Standard Response Wrapper
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    """Technical and human-readable details about an API failure."""

    code: str
    message: str
    details: Optional[str] = None


class StandardResponse(BaseModel):
    """Unified response structure for all endpoints."""

    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
