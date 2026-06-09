"""
Orchestrates the entire audit workflow pipeline:
SSH connection -> Audit collection -> Gemini analysis -> DB persistence.
Uses Dependency Injection for all service layers to allow mocking and unit testing.
"""

import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.services.ssh_service import SSHService
from app.services.audit_service import AuditService
from app.services.gemini_service import GeminiService
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class AuditOrchestrator:
    """
    Coordinates SSH collection, Gemini analysis, and database persistence.
    """

    def __init__(
        self,
        ssh_service: SSHService,
        audit_service: AuditService,
        gemini_service: GeminiService,
        db_service: DatabaseService,
    ) -> None:
        self.ssh_service = ssh_service
        self.audit_service = audit_service
        self.gemini_service = gemini_service
        self.db_service = db_service

    def run_pipeline(
        self,
        db: Session,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Execute the complete end-to-end security audit pipeline.

        1. SSH: Connect to target server.
        2. Audit: Collect configuration parameters.
        3. Gemini: Analyze the raw configuration output.
        4. DB: Save Audit and Findings records (transaction safe).
        5. Clean up: Disconnect SSH session even on failures.

        Args:
            db:       Active SQLAlchemy Session.
            host:     Host IP/name.
            port:     Host port.
            username: SSH login username.
            password: SSH login password.

        Returns:
            dict: Structured response matching the response DTO structure:
                {
                    "audit_id": str(UUID),
                    "server_ip": str,
                    "audit_date": datetime,
                    "findings_count": int,
                    "critical_count": int,
                    "high_count": int,
                    "medium_count": int,
                    "low_count": int,
                    "findings": list[dict]
                }
        """
        logger.info("Starting audit pipeline execution for server: %s:%d", host, port)

        raw_report = ""
        findings_list = []

        try:
            # Step 1: Establish SSH connection
            logger.info("Pipeline step 1: Connecting to host...")
            self.ssh_service.connect(host=host, port=port, username=username, password=password)

            # Step 2: Execute security commands
            logger.info("Pipeline step 2: Running audit commands...")
            audit_result = self.audit_service.run_audit(self.ssh_service)
            raw_report = audit_result["raw_report"]

        finally:
            # Step 5 (part 1): Clean up resources immediately after SSH/audit work is done
            logger.info("Pipeline SSH clean up: Disconnecting SSH connection...")
            self.ssh_service.disconnect()

        # Step 3: Send report to Gemini for analysis
        logger.info("Pipeline step 3: Sending report for AI analysis...")
        analysis_result = self.gemini_service.analyze_report(raw_report)
        findings_data = analysis_result.get("findings", [])

        # Count severities
        severity_counts = Counter(f.get("severity", "Medium") for f in findings_data)
        critical_count = severity_counts.get("Critical", 0)
        high_count = severity_counts.get("High", 0)
        medium_count = severity_counts.get("Medium", 0)
        low_count = severity_counts.get("Low", 0)

        # Calculate a security score (starts at 100)
        # Deduct: Critical (25), High (15), Medium (5), Low (1)
        security_score = max(
            0,
            100 - (critical_count * 25 + high_count * 15 + medium_count * 5 + low_count * 1)
        )

        # Generate a brief executive summary
        if not findings_data:
            executive_summary = "The security audit completed successfully. No critical vulnerabilities or misconfigurations were identified."
        else:
            total_findings = len(findings_data)
            executive_summary = (
                f"Security audit completed. Found {total_findings} vulnerability vector(s) "
                f"({critical_count} Critical, {high_count} High, {medium_count} Medium, {low_count} Low). "
                f"Overall security rating is {security_score}/100."
            )

        # Step 4: Persist the audit and findings
        logger.info("Pipeline step 4: Saving audit and findings to database...")
        # Make sure the date is UTC
        audit_date = datetime.now(timezone.utc)
        
        # Save audit record
        audit = self.db_service.save_audit(
            db=db,
            server_ip=host,
            audit_date=audit_date,
            raw_report=raw_report,
            executive_summary=executive_summary,
            security_score=security_score,
        )
        
        # Save findings linked to the audit
        self.db_service.save_findings(db=db, audit_id=audit.id, findings=findings_data)

        logger.info("Audit pipeline completed successfully. Audit ID: %s", audit.id)

        # Build response DTO dict
        return {
            "audit_id": str(audit.id),
            "server_ip": audit.server_ip,
            "audit_date": audit.audit_date,
            "findings_count": len(findings_data),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "findings": findings_data,
        }

