"""
FastAPI router for auditing endpoints.
"""

from collections import Counter
from datetime import datetime, timezone
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ssh_service import SSHService
from app.services.audit_service import AuditService
from app.services.gemini_service import GeminiService, GeminiAnalysisError
from app.services.database_service import DatabaseService
from app.services.audit_orchestrator import AuditOrchestrator
from app.schemas.audit_schemas import (
    AuditRequest,
    StandardResponse,
    ErrorDetail,
    AuditDetailResponse,
    AuditSummaryResponse,
    SeverityBreakdown,
    FindingResponse,
    AuditComparisonResponse,
    ComparisonFinding,
)

router = APIRouter(prefix="/api", tags=["Audit"])


# ---------------------------------------------------------------------------
# Service Dependencies
# ---------------------------------------------------------------------------

def get_ssh_service() -> SSHService:
    """Return an SSHService instance."""
    return SSHService()


def get_audit_service() -> AuditService:
    """Return an AuditService instance."""
    return AuditService()


def get_gemini_service() -> GeminiService:
    """Return a GeminiService instance."""
    return GeminiService()


def get_database_service() -> DatabaseService:
    """Return a DatabaseService instance."""
    return DatabaseService()


def get_orchestrator(
    ssh: SSHService = Depends(get_ssh_service),
    audit: AuditService = Depends(get_audit_service),
    gemini: GeminiService = Depends(get_gemini_service),
    db_service: DatabaseService = Depends(get_database_service),
) -> AuditOrchestrator:
    """Return an AuditOrchestrator instance with injected service dependencies."""
    return AuditOrchestrator(
        ssh_service=ssh,
        audit_service=audit,
        gemini_service=gemini,
        db_service=db_service,
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_severity_breakdown(findings) -> SeverityBreakdown:
    """Count findings per severity level."""
    counts = Counter(f.severity for f in findings)
    return SeverityBreakdown(
        critical=counts.get("Critical", 0),
        high=counts.get("High", 0),
        medium=counts.get("Medium", 0),
        low=counts.get("Low", 0),
    )


# ---------------------------------------------------------------------------
# Router Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/audits",
    response_model=StandardResponse,
    summary="Run a full security audit on a remote server",
    status_code=status.HTTP_201_CREATED,
)
def create_audit(
    request: AuditRequest,
    db: Session = Depends(get_db),
    orchestrator: AuditOrchestrator = Depends(get_orchestrator),
):
    """
    Triggers the end-to-end audit process:
    1. Establishes SSH connection to the remote Linux host.
    2. Runs predefined security commands.
    3. Analyzes raw reports via Google Gemini AI.
    4. Persists the audit and findings.
    5. Returns audit details.
    """
    try:
        pipeline_result = orchestrator.run_pipeline(
            db=db,
            host=request.server_ip,
            port=request.port,
            username=request.username,
            password=request.password,
        )

        return StandardResponse(
            success=True,
            data=pipeline_result,
            error=None,
        )

    except Exception as exc:
        code = "AUDIT_PIPELINE_FAILED"
        if "Authentication failed" in str(exc):
            code = "SSH_AUTHENTICATION_FAILED"
        elif "Gemini API error" in str(exc) or isinstance(exc, GeminiAnalysisError):
            code = "GEMINI_ANALYSIS_FAILED"

        error_detail = ErrorDetail(
            code=code,
            message=f"Audit execution failed: {str(exc)}",
            details=repr(exc),
        )
        return StandardResponse(
            success=False,
            data=None,
            error=error_detail,
        )


@router.get(
    "/audits",
    response_model=StandardResponse,
    summary="Retrieve paginated audit run history",
)
def list_audits(
    limit: int = Query(default=50, ge=1, le=500, description="Max audits to fetch"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    server_ip: str = Query(default=None, description="Filter results by server IP"),
    db: Session = Depends(get_db),
    db_service: DatabaseService = Depends(get_database_service),
):
    """
    Returns a list of audit summaries with severity breakdowns.
    Supports pagination and filtering by IP.
    """
    try:
        if server_ip:
            audits = db_service.search_audits(db, server_ip=server_ip)
            # Basic client-side pagination on search results for simplicity
            audits = audits[offset : offset + limit]
        else:
            audits = db_service.get_audit_history(db, limit=limit, offset=offset)

        summaries: List[AuditSummaryResponse] = []
        for audit in audits:
            summaries.append(
                AuditSummaryResponse(
                    id=audit.id,
                    server_ip=audit.server_ip,
                    audit_date=audit.audit_date,
                    severity_breakdown=_build_severity_breakdown(audit.findings),
                )
            )

        return StandardResponse(
            success=True,
            data=[s.model_dump(mode="json") for s in summaries],
            error=None,
        )
    except Exception as exc:
        return StandardResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code="DATABASE_QUERY_ERROR",
                message=f"Failed to query audit history: {str(exc)}",
                details=repr(exc),
            ),
        )


@router.get(
    "/audits/{audit_id}",
    response_model=StandardResponse,
    summary="Get detailed audit records and findings",
)
def get_audit(
    audit_id: UUID,
    db: Session = Depends(get_db),
    db_service: DatabaseService = Depends(get_database_service),
):
    """
    Returns complete findings, raw configuration logs, and severity summaries
    for a specific audit ID.
    """
    try:
        audit = db_service.get_audit_details(db, audit_id)
        if not audit:
            return StandardResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code="AUDIT_NOT_FOUND",
                    message=f"Audit with ID {audit_id} was not found.",
                ),
            )

        detail = AuditDetailResponse(
            id=audit.id,
            server_ip=audit.server_ip,
            audit_date=audit.audit_date,
            raw_report=audit.raw_report,
            findings=[FindingResponse.model_validate(f) for f in audit.findings],
            severity_breakdown=_build_severity_breakdown(audit.findings),
        )

        return StandardResponse(
            success=True,
            data=detail.model_dump(mode="json"),
            error=None,
        )
    except Exception as exc:
        return StandardResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code="DATABASE_QUERY_ERROR",
                message=f"Failed to fetch audit details: {str(exc)}",
                details=repr(exc),
            ),
        )


@router.get(
    "/audits/{audit_id}/comparison",
    response_model=StandardResponse,
    summary="Compare an audit with the previous audit for the same server",
)
def compare_audit(
    audit_id: UUID,
    db: Session = Depends(get_db),
    db_service: DatabaseService = Depends(get_database_service),
):
    """
    Compares the current audit findings against the previous audit run for the same server IP.
    """
    try:
        current_audit = db_service.get_audit_details(db, audit_id)
        if not current_audit:
            return StandardResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code="AUDIT_NOT_FOUND",
                    message=f"Audit with ID {audit_id} was not found.",
                ),
            )

        previous_audit = db_service.get_previous_audit(
            db,
            server_ip=current_audit.server_ip,
            current_date=current_audit.audit_date,
        )

        if not previous_audit:
            # No previous audit, return successfully with data=None or empty comparison
            return StandardResponse(
                success=True,
                data=None,
                error=None,
            )

        # Normalize issue strings for reliable matching
        def normalize_issue(issue_name: str) -> str:
            return issue_name.strip().lower()

        prev_map = {normalize_issue(f.issue): f for f in previous_audit.findings}
        curr_map = {normalize_issue(f.issue): f for f in current_audit.findings}

        resolved_findings = []
        remaining_findings = []
        new_findings = []

        # Find resolved (in previous, not in current)
        for norm_issue, f in prev_map.items():
            if norm_issue not in curr_map:
                resolved_findings.append(
                    ComparisonFinding(
                        issue=f.issue,
                        severity=f.severity,
                        explanation=f.explanation,
                        fix_command=f.fix_command,
                    )
                )

        # Find remaining (in both) and new (in current, not in previous)
        for norm_issue, f in curr_map.items():
            if norm_issue in prev_map:
                remaining_findings.append(
                    ComparisonFinding(
                        issue=f.issue,
                        severity=f.severity,
                        explanation=f.explanation,
                        fix_command=f.fix_command,
                    )
                )
            else:
                new_findings.append(
                    ComparisonFinding(
                        issue=f.issue,
                        severity=f.severity,
                        explanation=f.explanation,
                        fix_command=f.fix_command,
                    )
                )

        comparison = AuditComparisonResponse(
            previous_audit_id=previous_audit.id,
            previous_audit_date=previous_audit.audit_date,
            resolved=resolved_findings,
            remaining=remaining_findings,
            new=new_findings,
        )

        return StandardResponse(
            success=True,
            data=comparison.model_dump(mode="json"),
            error=None,
        )

    except Exception as exc:
        return StandardResponse(
            success=False,
            data=None,
            error=ErrorDetail(
                code="DATABASE_QUERY_ERROR",
                message=f"Failed to generate audit comparison: {str(exc)}",
                details=repr(exc),
            ),
        )
