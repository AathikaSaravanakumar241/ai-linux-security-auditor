"""
Database persistence service implementing the Repository Pattern.

Architecture:
    - DatabaseService class wraps database access operations.
    - Uses selectin loading to eagerly load findings for audits in queries, preventing N+1 problems.
    - Exposes pagination, bulk findings insertions, and filtered queries.
    - Provides backward-compatible module-level functions mapping to the service instance.
"""

import logging
from datetime import datetime, timezone
from typing import Any, List, Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Audit, Finding

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Repository class handling all CRUD and search queries for Audits and Findings.
    """

    def save_audit(
        self,
        db: Session,
        server_ip: str,
        audit_date: datetime,
        raw_report: str,
        executive_summary: Optional[str] = None,
        security_score: Optional[int] = None,
    ) -> Audit:
        """
        Persist a new Audit record.
        """
        audit = Audit(
            server_ip=server_ip,
            audit_date=audit_date,
            raw_report=raw_report,
            executive_summary=executive_summary,
            security_score=security_score,
        )
        db.add(audit)
        db.flush()  # Generates the UUID immediately
        logger.info("Saved audit record for %s with ID %s.", server_ip, audit.id)
        return audit

    def save_findings(
        self,
        db: Session,
        audit_id: UUID,
        findings: List[Dict[str, Any]],
    ) -> List[Finding]:
        """
        Bulk insert findings for a specific audit.
        """
        finding_objs: List[Finding] = []
        for item in findings:
            finding = Finding(
                audit_id=audit_id,
                severity=item.get("severity", "Medium"),
                issue=item.get("issue", "Unknown Issue"),
                evidence=item.get("evidence"),
                explanation=item.get("explanation"),
                impact=item.get("impact"),
                fix_command=item.get("fix_command"),
            )
            finding_objs.append(finding)

        # Bulk save
        db.add_all(finding_objs)
        db.flush()
        logger.info("Bulk-saved %d findings for audit %s.", len(finding_objs), audit_id)
        return finding_objs

    def get_audit_history(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Audit]:
        """
        Retrieve paginated audit history sorted by date descending.
        """
        stmt = (
            select(Audit)
            .options(selectinload(Audit.findings))
            .order_by(Audit.audit_date.desc())
            .offset(offset)
            .limit(limit)
        )
        results = db.scalars(stmt).all()
        logger.debug("Fetched %d audits for history.", len(results))
        return list(results)

    def get_audit_details(
        self,
        db: Session,
        audit_id: UUID,
    ) -> Optional[Audit]:
        """
        Retrieve full details for a single audit by its UUID.
        """
        stmt = (
            select(Audit)
            .options(selectinload(Audit.findings))
            .where(Audit.id == audit_id)
        )
        result = db.scalars(stmt).first()
        if not result:
            logger.warning("Audit with ID %s not found in database.", audit_id)
        return result

    def search_audits(
        self,
        db: Session,
        server_ip: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Audit]:
        """
        Search and filter audits by server IP and findings severity.
        """
        query = select(Audit).options(selectinload(Audit.findings))
        if server_ip:
            query = query.where(Audit.server_ip.ilike(f"%{server_ip}%"))
        if severity:
            query = query.join(Audit.findings).where(Finding.severity == severity.capitalize())

        query = query.order_by(Audit.audit_date.desc())
        results = db.scalars(query).all()
        return list(results)


# ---------------------------------------------------------------------------
# Backwards Compatibility Module Helpers
# ---------------------------------------------------------------------------

_service_instance = DatabaseService()


def create_audit(db: Session, server_ip: str, raw_report: str) -> Audit:
    """Legacy helper function to create audit."""
    return _service_instance.save_audit(db, server_ip, datetime.now(timezone.utc), raw_report)


def create_findings(db: Session, audit_id: Any, findings_data: List[dict]) -> List[Finding]:
    """Legacy helper function to save findings."""
    # Convert ID to UUID if it's passed as string or keep as is
    uuid_id = UUID(audit_id) if isinstance(audit_id, str) else audit_id
    return _service_instance.save_findings(db, uuid_id, findings_data)


def create_audit_with_findings(
    db: Session,
    server_ip: str,
    raw_report: str,
    findings_data: List[dict],
) -> Audit:
    """Legacy helper function to perform transactional audit and findings creation."""
    audit = _service_instance.save_audit(db, server_ip, datetime.now(timezone.utc), raw_report)
    _service_instance.save_findings(db, audit.id, findings_data)
    db.refresh(audit)
    return audit


def get_audit_by_id(db: Session, audit_id: Any) -> Optional[Audit]:
    """Legacy helper function to retrieve audit details."""
    try:
        uuid_id = UUID(audit_id) if isinstance(audit_id, str) else audit_id
    except ValueError:
        # Fallback in case old int format is somehow supplied
        return None
    return _service_instance.get_audit_details(db, uuid_id)


def get_all_audits(db: Session, skip: int = 0, limit: int = 100) -> List[Audit]:
    """Legacy helper function to retrieve all audits."""
    return _service_instance.get_audit_history(db, limit=limit, offset=skip)
