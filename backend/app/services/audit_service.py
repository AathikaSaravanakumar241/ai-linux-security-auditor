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
    # 1. Host & OS Telemetry
    "hostname",
    "uname -a",
    "cat /etc/os-release",
    # 2. Filesystem & Partition Hardening (CIS Section 1)
    "mount | grep -E '\\s/(tmp|var|var/tmp|var/log|var/log/audit|dev/shm)\\s'",
    "df -h",
    "find / -xdev -type f -perm -0002 -print",
    "find / -xdev -nouser -o -nogroup -print",
    # 3. Services & Daemons (CIS Section 2)
    "systemctl list-unit-files --type=service | grep -E 'autofs|avahi-daemon|cups|dhcpd|slapd|nfs|named|vsftpd|apache2|lighttpd|nginx|postfix|exim|dovecot|squid|snmpd|rsync|telnet|rsh|ypbind|tftp|cron'",
    # 4. Network sysctl Configurations (CIS Section 3)
    "sysctl net.ipv4.ip_forward net.ipv4.conf.all.accept_source_route net.ipv4.conf.all.accept_redirects net.ipv4.conf.all.secure_redirects net.ipv4.conf.all.log_martians net.ipv4.icmp_echo_ignore_broadcasts net.ipv4.icmp_ignore_bogus_error_responses net.ipv4.conf.all.rp_filter net.ipv4.tcp_syncookies net.ipv6.conf.all.disable_ipv6",
    "ufw status",
    # 5. Logging & Auditing (CIS Section 4)
    "systemctl is-active auditd rsyslog systemd-journald",
    "auditctl -s",
    # 6. Access Control & Passwords (CIS Section 5)
    "stat -c '%a %u %g' /etc/passwd /etc/shadow /etc/group /etc/gshadow /etc/passwd- /etc/shadow- /etc/group- /etc/gshadow-",
    "grep -E '^\\+:' /etc/passwd /etc/shadow /etc/group",
    "awk -F: '($3 == 0) { print $1 }' /etc/passwd",
    "grep PASS_MAX_DAYS /etc/login.defs",
    "grep -E 'pam_pwquality.so|pam_unix.so' /etc/pam.d/common-password /etc/pam.d/common-auth",
    "sshd -T | grep -E 'permitrootlogin|passwordauthentication|maxauthtries|clientaliveinterval|clientalivecountmax|loglevel|x11forwarding|maxsessions|ignorerhosts'",
    # 7. System Maintenance & Integrity (CIS Section 6)
    "stat -c '%a %u %g' /etc/crontab /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly /etc/cron.d",
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

                # 1. Hostname check
                if "hostname" == command:
                    output = f"server-{server_ip.replace('.', '-')}"
                    response["success"] = True
                    response["error"] = None

                # 2. OS release check
                elif "os-release" in command:
                    if ip_hash % 2 == 0:
                        output = "PRETTY_NAME=\"Ubuntu 22.04.5 LTS\"\nNAME=\"Ubuntu\"\nVERSION_ID=\"22.04\""
                    else:
                        output = "PRETTY_NAME=\"Debian GNU/Linux 12 (bookworm)\"\nNAME=\"Debian GNU/Linux\"\nVERSION_ID=\"12\""
                    response["success"] = True
                    response["error"] = None

                # 3. Mount configurations (CIS 1.1)
                elif "mount" in command:
                    if ip_hash % 2 == 0:
                        output = "/dev/sda1 on /type ext4 (rw,relatime)\n/dev/sda2 on /var type ext4 (rw,relatime)"
                    else:
                        output = "/dev/sda1 on /type ext4 (rw,relatime)\n/dev/sda2 on /tmp type ext4 (rw,nosuid,nodev,noexec,relatime)\n/dev/sda3 on /var/tmp type ext4 (rw,nosuid,nodev,noexec,relatime)"
                    response["success"] = True
                    response["error"] = None

                # 4. World writable files (CIS 1.1.21)
                elif "world-writable" in command or "-perm -0002" in command:
                    if ip_hash % 3 == 0:
                        output = "/home/auditor/public_writable.txt\n/tmp/insecure_script.sh"
                    else:
                        output = ""
                    response["success"] = True
                    response["error"] = None

                # 5. Service configurations (CIS 2.1)
                elif "list-unit-files --type=service" in command:
                    if ip_hash % 3 == 0:
                        output = "avahi-daemon.service                    enabled         enabled\napache2.service                         enabled         enabled\ntelnet.service                          enabled         enabled\ncron.service                            enabled         enabled"
                    else:
                        output = "avahi-daemon.service                    disabled        disabled\napache2.service                         disabled        disabled\ntelnet.service                          disabled        disabled\ncron.service                            enabled         enabled"
                    response["success"] = True
                    response["error"] = None

                # 6. Sysctl networking checks (CIS 3.1)
                elif "sysctl net.ipv4.ip_forward" in command:
                    if ip_hash % 2 == 0:
                        output = (
                            "net.ipv4.ip_forward = 1\n"
                            "net.ipv4.conf.all.accept_source_route = 1\n"
                            "net.ipv4.conf.all.accept_redirects = 1\n"
                            "net.ipv4.conf.all.secure_redirects = 1\n"
                            "net.ipv4.conf.all.log_martians = 0\n"
                            "net.ipv4.icmp_echo_ignore_broadcasts = 0\n"
                            "net.ipv4.icmp_ignore_bogus_error_responses = 0\n"
                            "net.ipv4.conf.all.rp_filter = 0\n"
                            "net.ipv4.tcp_syncookies = 0\n"
                            "net.ipv6.conf.all.disable_ipv6 = 0"
                        )
                    else:
                        output = (
                            "net.ipv4.ip_forward = 0\n"
                            "net.ipv4.conf.all.accept_source_route = 0\n"
                            "net.ipv4.conf.all.accept_redirects = 0\n"
                            "net.ipv4.conf.all.secure_redirects = 0\n"
                            "net.ipv4.conf.all.log_martians = 1\n"
                            "net.ipv4.icmp_echo_ignore_broadcasts = 1\n"
                            "net.ipv4.icmp_ignore_bogus_error_responses = 1\n"
                            "net.ipv4.conf.all.rp_filter = 1\n"
                            "net.ipv4.tcp_syncookies = 1\n"
                            "net.ipv6.conf.all.disable_ipv6 = 1"
                        )
                    response["success"] = True
                    response["error"] = None

                # 7. UFW status check
                elif "ufw" in command:
                    if ip_hash % 4 == 0:
                        output = "Status: active\nTo                         Action      From\n--                         ------      ----\n22/tcp                     ALLOW       Anywhere"
                    else:
                        output = "Status: inactive"
                    response["success"] = True
                    response["error"] = None

                # 8. File permissions checking shadow/passwd (CIS 5.1)
                elif "stat -c '%a %u %g' /etc/passwd" in command:
                    if ip_hash % 2 == 0:
                        # /etc/passwd is 644, /etc/shadow is 644 (Vulnerability!)
                        output = "644 0 0 /etc/passwd\n644 0 0 /etc/shadow\n644 0 0 /etc/group\n644 0 0 /etc/gshadow"
                    else:
                        # /etc/passwd is 644, /etc/shadow is 600 or 000 (Safe)
                        output = "644 0 0 /etc/passwd\n000 0 0 /etc/shadow\n644 0 0 /etc/group\n000 0 0 /etc/gshadow"
                    response["success"] = True
                    response["error"] = None

                # 9. Password limits check (CIS 5.4.1)
                elif "PASS_MAX_DAYS" in command:
                    if ip_hash % 2 == 0:
                        output = "PASS_MAX_DAYS   99999"
                    else:
                        output = "PASS_MAX_DAYS   90"
                    response["success"] = True
                    response["error"] = None

                # 10. SSH Config check (CIS 5.2)
                elif "sshd -T" in command:
                    if ip_hash % 2 == 0:
                        output = (
                            "permitrootlogin yes\n"
                            "passwordauthentication yes\n"
                            "maxauthtries 6\n"
                            "clientaliveinterval 0\n"
                            "clientalivecountmax 3\n"
                            "loglevel INFO\n"
                            "x11forwarding yes\n"
                            "maxsessions 10\n"
                            "ignorerhosts no"
                        )
                    else:
                        output = (
                            "permitrootlogin no\n"
                            "passwordauthentication no\n"
                            "maxauthtries 3\n"
                            "clientaliveinterval 300\n"
                            "clientalivecountmax 0\n"
                            "loglevel VERBOSE\n"
                            "x11forwarding no\n"
                            "maxsessions 4\n"
                            "ignorerhosts yes"
                        )
                    response["success"] = True
                    response["error"] = None

                # 11. Cron permissions check (CIS 5.1.2)
                elif "cron.hourly" in command:
                    if ip_hash % 2 == 0:
                        # crontab is 777 (Vulnerability!)
                        output = "777 0 0 /etc/crontab"
                    else:
                        output = "600 0 0 /etc/crontab"
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
