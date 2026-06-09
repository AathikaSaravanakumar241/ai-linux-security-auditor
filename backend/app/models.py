"""
SQLAlchemy ORM models for the audit system.

Tables:
    audits   — One row per audit run against a server.
    findings — One row per security finding discovered in an audit.

Relationship:
    Audit (1) ←→ (N) Finding
    Cascade delete: removing an audit removes all its findings.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    UUID,
    Integer,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Audit(Base):
    """
    Represents a single security audit run against a Linux server.

    Attributes:
        id:          UUID primary key.
        server_ip:   IP address or hostname of the audited server.
        audit_date:  UTC timestamp of when the audit was executed.
        raw_report:  Combined text output of all audit commands.
        created_at:  UTC timestamp of when the record was created.
        updated_at:  UTC timestamp of when the record was last updated.
        findings:    List of Finding objects discovered in this audit.
    """

    __tablename__ = "audits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    server_ip = Column(String(255), nullable=False, index=True)
    audit_date = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )
    raw_report = Column(Text, nullable=True)
    executive_summary = Column(Text, nullable=True)
    security_score = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # One audit has many findings; delete findings when audit is deleted
    findings = relationship(
        "Finding",
        back_populates="audit",
        cascade="all, delete-orphan",
        lazy="selectin",  # Eager load findings by default
    )

    def __repr__(self) -> str:
        return f"<Audit(id={self.id}, server_ip='{self.server_ip}', date={self.audit_date})>"


class Finding(Base):
    """
    Represents a single security finding from a Gemini analysis.

    Attributes:
        id:          UUID primary key.
        audit_id:    Foreign key linking to the parent Audit (UUID).
        severity:    Classification: Critical, High, Medium, or Low.
        issue:       Short name of the security issue.
        explanation: Detailed description of the vulnerability.
        impact:      Business impact if the issue is not remediated.
        fix_command: Exact Linux command(s) to remediate the issue.
        created_at:  UTC timestamp of when the record was created.
    """

    __tablename__ = "findings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    audit_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    severity = Column(String(20), nullable=False, index=True)
    issue = Column(String(500), nullable=False)
    evidence = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    fix_command = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Back-reference to the parent audit
    audit = relationship("Audit", back_populates="findings")

    def __repr__(self) -> str:
        return f"<Finding(id={self.id}, severity='{self.severity}', issue='{self.issue}')>"
