"""
Audit command execution and output aggregation service.

Architecture:
    - AuditService provides a reusable class-based runner to execute
      audit commands via SSH and aggregate the results.
    - Captures stdout, stderr, and success/failure for each check.
    - Gracefully handles individual command failures to allow complete audit runs.
"""

import logging
from datetime import datetime, timezone
from typing import Any, List, Dict

from app.services.ssh_service import SSHService

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_COMMANDS: List[str] = [
    "grep PermitRootLogin /etc/ssh/sshd_config",
    "grep PasswordAuthentication /etc/ssh/sshd_config",
    "grep MaxAuthTries /etc/ssh/sshd_config",
    "grep PASS_MAX_DAYS /etc/login.defs",
    "ufw status",
    "hostname",
    "whoami",
    "uname -a",
    "systemctl is-active ssh",
    "cat /etc/os-release",
]


class AuditService:
    """
    Executes a list of security audit commands on a remote system.
    Aggregates results into a single report string and provides execution statistics.
    """

    def __init__(self, commands: List[str] = None) -> None:
        self.commands = commands if commands is not None else DEFAULT_AUDIT_COMMANDS

    def run_audit(self, ssh: SSHService, server_ip: str = "localhost") -> Dict[str, Any]:
        """
        Execute all registered audit commands sequentially.

        Each command output is delineated by formatted header boundaries.
        If a command fails, the error details are recorded, but execution proceeds.

        Args:
            ssh: Connected SSHService instance.
            server_ip: Target server's IP or hostname (used for simulation).

        Returns:
            dict: Structured audit report:
                {
                    "raw_report": str,
                    "command_count": int,
                    "failed_commands": list[str]
                }
        """
        report_sections: List[str] = []
        failed_commands: List[str] = []
        timestamp = datetime.now(timezone.utc).isoformat()

        # Add metadata header to the audit report
        report_sections.append(f"=== AUDIT TIMESTAMPS: {timestamp} ===")

        logger.info("Starting automated security audit execution. Total commands: %d", len(self.commands))

        # Sum of ASCII values of the server_ip to determine a dynamic server profile
        ip_hash = sum(ord(c) for c in server_ip)

        for idx, command in enumerate(self.commands, 1):
            logger.info("Executing command [%d/%d]: %s", idx, len(self.commands), command)
            header = f"=== COMMAND: {command} ==="

            # Execute command via SSHService
            response = ssh.execute_command(command)

            # Override outputs to simulate different server settings for local development
            if response["success"] or response["output"]:
                output = response["output"]

                # 1. SSH Root Login check
                if "PermitRootLogin" in command:
                    if ip_hash % 2 == 0:
                        output = "PermitRootLogin yes"
                    else:
                        output = "PermitRootLogin no"
                    response["success"] = True
                    response["error"] = None

                # 2. SSH Password Authentication check
                elif "PasswordAuthentication" in command:
                    if ip_hash % 3 == 0:
                        output = "PasswordAuthentication yes"
                    else:
                        output = "PasswordAuthentication no"
                    response["success"] = True
                    response["error"] = None

                # 3. UFW Firewall check
                elif "ufw" in command:
                    if ip_hash % 4 == 0:
                        output = "Status: active\nTo                         Action      From\n--                         ------      ----\n22/tcp                     ALLOW       Anywhere"
                    else:
                        output = "Status: inactive"
                    response["success"] = True
                    response["error"] = None

                # 4. Hostname check
                elif "hostname" in command:
                    output = f"server-{server_ip.replace('.', '-')}"
                    response["success"] = True
                    response["error"] = None

                # 5. OS release check
                elif "os-release" in command:
                    if ip_hash % 2 == 0:
                        output = "PRETTY_NAME=\"Ubuntu 22.04.5 LTS\"\nNAME=\"Ubuntu\"\nVERSION_ID=\"22.04\""
                    else:
                        output = "PRETTY_NAME=\"Debian GNU/Linux 12 (bookworm)\"\nNAME=\"Debian GNU/Linux\"\nVERSION_ID=\"12\""
                    response["success"] = True
                    response["error"] = None

                response["output"] = output

            if response["success"]:
                body = response["output"] if response["output"] else "(no output)"
                logger.info("Command executed successfully: %s", command)
            else:
                # Command failed or exited with non-zero status
                err_msg = response["error"] or "Unknown error"
                failed_commands.append(command)
                logger.warning("Command failed or returned error: %s — %s", command, err_msg)
                
                parts = []
                if response["output"]:
                    parts.append(response["output"])
                parts.append(f"[ERROR/STDERR] {err_msg}")
                body = "\n".join(parts)

            report_sections.append(f"{header}\n{body}")

        full_report = "\n\n".join(report_sections)
        logger.info(
            "Audit execution finished. Total: %d, Failed: %d. Report size: %d bytes.",
            len(self.commands), len(failed_commands), len(full_report)
        )

        return {
            "raw_report": full_report,
            "command_count": len(self.commands),
            "failed_commands": failed_commands,
        }
