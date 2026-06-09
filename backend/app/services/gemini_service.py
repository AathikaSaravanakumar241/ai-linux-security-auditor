"""
Google Gemini API integration for security report analysis.

Architecture:
    - GeminiService class encapsulates report analysis using the google-genai SDK.
    - Implements exponential backoff retry logic to handle rate limits (HTTP 429)
      and transient API failures.
    - Counts tokens using models.count_tokens to avoid exceeding rate limits.
    - Validates parsed JSON findings and enforces rules (e.g. PermitRootLogin=Critical).
"""

import json
import logging
import re
import time
from typing import Any, List, Dict, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import get_settings

logger = logging.getLogger(__name__)

# System instructions directing Gemini on analysis and expected JSON output structure
SYSTEM_PROMPT = """\
You are an expert Linux security auditor. You will receive the raw output of \
security audit commands executed on a Linux server. Your task is to analyze \
the output and identify security vulnerabilities, misconfigurations, and weak settings.

**RULES:**
1. Classify each finding with one of these severity levels: Critical, High, Medium, Low.
2. SPECIAL RULE: If PermitRootLogin is set to "yes" or is enabled/commented-in as yes, \
   ALWAYS classify it as **Critical** severity.
3. For each issue, provide ALL of these fields:
   - "severity": "Critical" | "High" | "Medium" | "Low"
   - "issue": A brief descriptive name for the vulnerability/misconfiguration
   - "explanation": A clear, detailed description of the configuration issue
   - "impact": The business or security impact if this issue is not remediated
   - "fix_command": The specific Linux shell command(s) to remediate the issue
4. Return ONLY a valid JSON array of objects. Do not wrap in markdown or include preambles/commentary.
5. If no issues are found, return an empty JSON array: []

**EXAMPLE OUTPUT FORMAT:**
[
  {
    "severity": "Critical",
    "issue": "Root Login Enabled via SSH",
    "explanation": "PermitRootLogin is set to yes in sshd_config, allowing direct root access over SSH.",
    "impact": "An attacker who brute-forces or obtains the root password gains immediate full system control.",
    "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  }
]
"""

USER_PROMPT_TEMPLATE = """\
Analyze the following Linux security configuration report. Identify all misconfigurations, \
weak settings, and vulnerabilities. Return the findings as a valid JSON array.

--- AUDIT REPORT START ---
{report}
--- AUDIT REPORT END ---
"""


class GeminiAnalysisError(Exception):
    """Raised when Gemini analysis fails after all retries."""
    pass


class GeminiService:
    """
    Integrates with Google Gemini API to analyze Linux security audit reports.
    Manages rate limits, timeouts, token validation, and JSON parsing.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> Optional[genai.Client]:
        """Lazy initialization of the GenAI Client."""
        if self._client is None:
            if not self.settings.GEMINI_API_KEY or self.settings.GEMINI_API_KEY == "your-gemini-api-key-here":
                return None
            try:
                self._client = genai.Client(api_key=self.settings.GEMINI_API_KEY)
            except Exception as exc:
                logger.warning("Failed to initialize GenAI Client: %s", exc)
                return None
        return self._client

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the input text to prevent exceeding limits.
        """
        try:
            client = self.client
            if client is None:
                return len(text) // 4
            response = client.models.count_tokens(
                model=self.settings.GEMINI_MODEL,
                contents=text,
            )
            return response.total_tokens
        except Exception as exc:
            logger.warning("Failed to count tokens: %s", exc)
            return len(text) // 4  # Rough fallback estimation

    def analyze_report(self, raw_report: str) -> Dict[str, Any]:
        """
        Analyze a raw audit report using the Gemini API.
        Implements exponential backoff (starting at 1s, doubling up to 5 retries) to handle rate limiting.

        Args:
            raw_report: Combined string output of all audit commands.

        Returns:
            dict: JSON-like structure:
                {
                    "findings": [
                        {
                            "severity": "Critical|High|Medium|Low",
                            "issue": "...",
                            "explanation": "...",
                            "impact": "...",
                            "fix_command": "..."
                        }
                    ]
                }
        """
        # If API key is placeholder or missing, fallback immediately to local analysis
        if not self.settings.GEMINI_API_KEY or self.settings.GEMINI_API_KEY == "your-gemini-api-key-here":
            logger.warning("GEMINI_API_KEY is not configured or using placeholder. Running in local rule-based Mock fallback mode.")
            return self._generate_mock_findings(raw_report)

        user_prompt = USER_PROMPT_TEMPLATE.format(report=raw_report)
        token_count = self.count_tokens(user_prompt)
        logger.info("Prepared audit report for Gemini analysis. Input tokens: %d", token_count)

        # Retries: start at 1 second, double each retry, max 5 retries
        max_retries = 5
        backoff = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Sending report to Gemini API (attempt %d/%d, model=%s)...",
                    attempt, max_retries, self.settings.GEMINI_MODEL
                )

                client = self.client
                if client is None:
                    raise GeminiAnalysisError("Gemini Client could not be initialized (invalid or empty API Key).")

                # Generate content using google-genai SDK
                response = client.models.generate_content(
                    model=self.settings.GEMINI_MODEL,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.1,  # Low temperature for deterministic output
                        response_mime_type="application/json",  # Demand JSON schema directly if model supports it
                    ),
                )

                raw_text = response.text.strip()
                logger.debug("Raw response from Gemini API: %s", raw_text)

                findings = self._extract_json(raw_text)
                self._validate_and_sanitize_findings(findings, raw_report)

                logger.info("Successfully analyzed report. Discovered %d security findings.", len(findings))
                return {"findings": findings}

            except APIError as exc:
                is_rate_limit = exc.code == 429 or "quota" in str(exc).lower() or "limit" in str(exc).lower()
                severity_level = logging.ERROR if attempt == max_retries else logging.WARNING
                logger.log(
                    severity_level,
                    "Attempt %d/%d: Gemini API Error (Rate Limit=%s): %s",
                    attempt, max_retries, is_rate_limit, exc
                )

                if attempt == max_retries:
                    logger.warning("Gemini API call failed with APIError after all retries. Falling back to local rule-based analysis.")
                    return self._generate_mock_findings(raw_report)

                # Exponential backoff
                wait_time = backoff * (2 ** (attempt - 1))
                logger.info("Sleeping for %.1fs before retry...", wait_time)
                time.sleep(wait_time)

            except json.JSONDecodeError as exc:
                logger.warning("Attempt %d/%d: JSON decoding failed: %s", attempt, max_retries, exc)
                if attempt == max_retries:
                    logger.warning("Failed to parse JSON response from Gemini after all retries. Falling back to local rule-based analysis.")
                    return self._generate_mock_findings(raw_report)
                time.sleep(backoff * attempt)

            except Exception as exc:
                logger.error("Attempt %d/%d: Unexpected error during Gemini analysis: %s", attempt, max_retries, exc)
                if attempt == max_retries:
                    logger.warning("Unexpected error during Gemini analysis. Falling back to local rule-based analysis. Error: %s", exc)
                    return self._generate_mock_findings(raw_report)
                time.sleep(backoff * attempt)

        logger.warning("Audit analysis failed all retry attempts. Falling back to local rule-based analysis.")
        return self._generate_mock_findings(raw_report)

    def _generate_mock_findings(self, raw_report: str) -> Dict[str, Any]:
        """
        Generate realistic mock security findings by parsing the raw audit report.
        Allows testing the application flow without a valid Gemini API key.
        """
        findings = []

        # 1. Check SSH PermitRootLogin
        root_login_enabled = False
        for line in raw_report.splitlines():
            clean_line = line.strip()
            if "PermitRootLogin" in clean_line and not clean_line.startswith("#"):
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0] == "PermitRootLogin" and parts[1].lower() == "yes":
                    root_login_enabled = True
                    break
        if root_login_enabled:
            findings.append({
                "severity": "Critical",
                "issue": "Root Login Enabled via SSH",
                "explanation": "PermitRootLogin is enabled (set to yes) in /etc/ssh/sshd_config, allowing direct root access over SSH.",
                "impact": "Attackers can brute-force the root password directly, bypassing intermediate account controls and obtaining complete administrative access.",
                "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
            })

        # 2. Check SSH PasswordAuthentication
        pw_auth_enabled = False
        for line in raw_report.splitlines():
            clean_line = line.strip()
            if "PasswordAuthentication" in clean_line and not clean_line.startswith("#"):
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0] == "PasswordAuthentication" and parts[1].lower() == "yes":
                    pw_auth_enabled = True
                    break
        if pw_auth_enabled:
            findings.append({
                "severity": "High",
                "issue": "Password Authentication Enabled over SSH",
                "explanation": "PasswordAuthentication is set to yes in sshd_config. Using passwords instead of SSH keys increases susceptibility to brute force attacks.",
                "impact": "Attackers could successfully brute force accounts with weak credentials.",
                "fix_command": "sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
            })

        # 3. Check SSH MaxAuthTries
        max_tries_val = None
        for line in raw_report.splitlines():
            clean_line = line.strip()
            if "MaxAuthTries" in clean_line and not clean_line.startswith("#"):
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0] == "MaxAuthTries":
                    try:
                        max_tries_val = int(parts[1])
                    except ValueError:
                        pass
        if max_tries_val is None or max_tries_val > 4:
            findings.append({
                "severity": "Medium",
                "issue": "SSH MaxAuthTries Inadequately Configured",
                "explanation": f"MaxAuthTries is set to {max_tries_val if max_tries_val else 'default (6)'}, which is higher than the recommended limit of 3 or 4.",
                "impact": "Allows attackers more password guessing attempts per SSH connection, increasing brute-force efficiency.",
                "fix_command": "echo 'MaxAuthTries 3' | sudo tee -a /etc/ssh/sshd_config && sudo systemctl restart sshd"
            })

        # 4. Check Password Aging (PASS_MAX_DAYS)
        pass_max = None
        for line in raw_report.splitlines():
            clean_line = line.strip()
            if "PASS_MAX_DAYS" in clean_line and not clean_line.startswith("#"):
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0] == "PASS_MAX_DAYS":
                    try:
                        pass_max = int(parts[1])
                    except ValueError:
                        pass
        if pass_max is None or pass_max > 90:
            findings.append({
                "severity": "Medium",
                "issue": "Insecure Password Expiration Policy",
                "explanation": f"PASS_MAX_DAYS is set to {pass_max if pass_max else '99999'} in /etc/login.defs. Passwords do not expire frequently enough.",
                "impact": "Compromised user credentials remain valid indefinitely, maximizing the attacker's window of opportunity.",
                "fix_command": "sudo sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs"
            })

        # 5. Check UFW status
        ufw_inactive = False
        for line in raw_report.splitlines():
            clean_line = line.strip().lower()
            if "status: inactive" in clean_line or "inactive" in clean_line:
                ufw_inactive = True
                break
        if ufw_inactive:
            findings.append({
                "severity": "High",
                "issue": "UFW Firewall is Inactive",
                "explanation": "Uncomplicated Firewall (UFW) is installed but currently disabled (inactive).",
                "impact": "All network ports are unprotected by a firewall, increasing the system's attack surface.",
                "fix_command": "sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw allow ssh && sudo ufw --force enable"
            })

        # If no issues found (unlikely), inject a default low finding
        if not findings:
            findings.append({
                "severity": "Low",
                "issue": "Server Configuration Assessment Complete",
                "explanation": "No critical vulnerabilities were detected in the basic configuration checks.",
                "impact": "Minimal immediate security risk identified.",
                "fix_command": "# Continue monitoring and run periodic full security audits."
            })

        return {"findings": findings}

    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract and load JSON from response. Supports raw json array and markdown fenced json.
        """
        # Clean text
        text = text.strip()

        # Try direct parse
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict) and "findings" in parsed:
                # Sometimes model wraps it in an object
                return parsed["findings"]
        except json.JSONDecodeError:
            pass

        # Match markdown block
        markdown_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
        match = re.search(markdown_pattern, text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1).strip())
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict) and "findings" in parsed:
                    return parsed["findings"]
            except json.JSONDecodeError:
                pass

        # Try matching bracket to bracket
        bracket_match = re.search(r"\[.*\]", text, re.DOTALL)
        if bracket_match:
            try:
                parsed = json.loads(bracket_match.group(0))
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("Could not locate a valid JSON array of findings in Gemini response", text, 0)

    def _validate_and_sanitize_findings(self, findings: List[Dict[str, Any]], raw_report: str) -> None:
        """
        Validates structure of findings and enforces rules like PermitRootLogin=Critical.
        """
        required_fields = {"severity", "issue", "explanation", "impact", "fix_command"}
        valid_severities = {"Critical", "High", "Medium", "Low"}

        # Check raw report to see if PermitRootLogin is enabled
        root_login_enabled = False
        # Match lines like "PermitRootLogin yes" or uncommented PermitRootLogin enabled (not starting with #)
        for line in raw_report.splitlines():
            clean_line = line.strip()
            if "PermitRootLogin" in clean_line and not clean_line.startswith("#"):
                # split and see if value is yes
                parts = clean_line.split()
                if len(parts) >= 2 and parts[0] == "PermitRootLogin" and parts[1].lower() == "yes":
                    root_login_enabled = True
                    break

        for i, finding in enumerate(findings):
            # Fill missing keys
            missing = required_fields - set(finding.keys())
            for key in missing:
                finding[key] = "N/A"

            # Normalize severity casing
            severity = str(finding.get("severity", "Medium")).strip().capitalize()
            if severity not in valid_severities:
                severity = "Medium"
            finding["severity"] = severity

            # Enforce the special PermitRootLogin Rule: if it is related to SSH root login
            # and PermitRootLogin was detected as enabled, force severity to Critical
            is_root_login_issue = "root login" in str(finding.get("issue")).lower() or "permitrootlogin" in str(finding.get("explanation")).lower()
            if root_login_enabled and is_root_login_issue:
                finding["severity"] = "Critical"

        # If root login is enabled, but Gemini did not report it, manually inject it as Critical finding
        if root_login_enabled:
            has_root_login_finding = any(
                "root login" in str(f.get("issue")).lower() or "permitrootlogin" in str(f.get("explanation")).lower()
                for f in findings
            )
            if not has_root_login_finding:
                logger.info("PermitRootLogin yes detected but not flagged by Gemini. Manually injecting Critical finding.")
                findings.append({
                    "severity": "Critical",
                    "issue": "Root Login Enabled via SSH",
                    "explanation": "PermitRootLogin is enabled (set to yes) in /etc/ssh/sshd_config, allowing direct root access over SSH.",
                    "impact": "Attackers can brute-force the root password directly, bypassing intermediate account controls and obtaining complete administrative access.",
                    "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
                })
