import pytest
from app.routers.audit_router import get_ssh_service, get_gemini_service
from app.services.ssh_service import SSHConnectionError


# ---------------------------------------------------------------------------
# Mock Services
# ---------------------------------------------------------------------------

class MockSSHService:
    def __init__(self, should_fail_auth=False):
        self.should_fail_auth = should_fail_auth
        self.connected = False

    def connect(self, host, port, username, password):
        if self.should_fail_auth:
            raise SSHConnectionError(f"Authentication failed for {username}@{host}:{port}")
        self.connected = True
        return True

    def execute_command(self, command):
        return {
            "success": True,
            "output": f"Simulated command output for: {command}",
            "error": None
        }

    def disconnect(self):
        self.connected = False


class MockGeminiService:
    def __init__(self, findings=None):
        self.findings = findings or []

    def count_tokens(self, text):
        return len(text) // 4

    def analyze_report(self, raw_report):
        return {"findings": self.findings}


# ---------------------------------------------------------------------------
# Pytest Test Cases (TC01 to TC10)
# ---------------------------------------------------------------------------

def test_tc01_secure_server_audit(client):
    """
    TC01: Secure Server Audit
    Input: Valid IP, Username, Password
    Expected: Audit completed successfully with Low Risk findings
    """
    mock_findings = [
        {
            "severity": "Low",
            "issue": "Server Configuration Assessment Complete",
            "explanation": "No critical vulnerabilities were detected in the configuration checks.",
            "impact": "Minimal immediate security risk identified.",
            "fix_command": "# Continue monitoring and run periodic full security audits."
        }
    ]

    # Override dependencies
    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService(should_fail_auth=False)
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.50",
        "port": 22,
        "username": "admin",
        "password": "secure_password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["server_ip"] == "192.168.1.50"
    assert data["findings_count"] == 1
    assert data["low_count"] == 1
    assert data["critical_count"] == 0
    assert len(data["findings"]) == 1
    assert data["findings"][0]["severity"] == "Low"


def test_tc02_root_login_enabled(client):
    """
    TC02: Root Login Enabled
    Input: Server with PermitRootLogin yes
    Expected: Critical finding generated for Root Login
    """
    mock_findings = [
        {
            "severity": "Critical",
            "issue": "Root Login Enabled via SSH",
            "explanation": "PermitRootLogin is set to yes, allowing direct root access.",
            "impact": "Direct root login increases the risk of successful password brute force.",
            "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.51",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["critical_count"] == 1
    assert data["findings"][0]["severity"] == "Critical"
    assert "Root Login" in data["findings"][0]["issue"]


def test_tc03_password_authentication_enabled(client):
    """
    TC03: Password Authentication Enabled
    Input: Server with PasswordAuthentication yes
    Expected: High Risk finding generated
    """
    mock_findings = [
        {
            "severity": "High",
            "issue": "Password Authentication Enabled over SSH",
            "explanation": "PasswordAuthentication is set to yes in sshd_config.",
            "impact": "Enables attackers to perform online password guessing attacks.",
            "fix_command": "sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.52",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["high_count"] == 1
    assert data["findings"][0]["severity"] == "High"
    assert "Password Authentication" in data["findings"][0]["issue"]


def test_tc04_weak_password_policy(client):
    """
    TC04: Weak Password Policy
    Input: Server with PASS_MAX_DAYS 99999
    Expected: Medium Risk finding generated
    """
    mock_findings = [
        {
            "severity": "Medium",
            "issue": "Insecure Password Expiration Policy",
            "explanation": "PASS_MAX_DAYS is set to 99999 in /etc/login.defs.",
            "impact": "Compromised passwords remain active indefinitely.",
            "fix_command": "sudo sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.53",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["medium_count"] == 1
    assert data["findings"][0]["severity"] == "Medium"
    assert "Password Expiration" in data["findings"][0]["issue"]


def test_tc05_firewall_not_installed(client):
    """
    TC05: Firewall Not Installed
    Input: Server without UFW Firewall
    Expected: High Risk finding for missing firewall
    """
    mock_findings = [
        {
            "severity": "High",
            "issue": "UFW Firewall is Inactive",
            "explanation": "Firewall status is reported as inactive.",
            "impact": "Exposes the server ports to direct network traffic.",
            "fix_command": "sudo ufw enable"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.54",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["high_count"] == 1
    assert data["findings"][0]["severity"] == "High"
    assert "Firewall" in data["findings"][0]["issue"]


def test_tc06_ssh_service_inactive(client):
    """
    TC06: SSH Service Inactive
    Input: Server with SSH service stopped
    Expected: High Risk finding for SSH service issue
    """
    mock_findings = [
        {
            "severity": "High",
            "issue": "SSH Service Inactive",
            "explanation": "The SSH service configuration is reported inactive or stopped.",
            "impact": "Remote SSH administrative access will fail.",
            "fix_command": "sudo systemctl enable --now ssh"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.55",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["high_count"] == 1
    assert data["findings"][0]["severity"] == "High"
    assert "SSH Service Inactive" in data["findings"][0]["issue"]


def test_tc07_excessive_login_attempts(client):
    """
    TC07: Excessive Login Attempts
    Input: Server with MaxAuthTries 10
    Expected: Medium Risk finding generated
    """
    mock_findings = [
        {
            "severity": "Medium",
            "issue": "SSH MaxAuthTries Inadequately Configured",
            "explanation": "MaxAuthTries is set to 10 in sshd_config.",
            "impact": "Allows brute force tools to attempt more passwords per connection.",
            "fix_command": "sudo sed -i 's/^MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.56",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["medium_count"] == 1
    assert data["findings"][0]["severity"] == "Medium"
    assert "MaxAuthTries" in data["findings"][0]["issue"]


def test_tc08_outdated_operating_system(client):
    """
    TC08: Outdated Operating System
    Input: Ubuntu 16.04 Server
    Expected: High Risk finding for unsupported OS
    """
    mock_findings = [
        {
            "severity": "High",
            "issue": "Outdated Operating System",
            "explanation": "Server is running Ubuntu 16.04 which is EOL.",
            "impact": "Unpatched core OS vulnerabilities represent high exploitation risk.",
            "fix_command": "Upgrade OS to Ubuntu 22.04 LTS or 24.04 LTS"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.57",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["high_count"] == 1
    assert data["findings"][0]["severity"] == "High"
    assert "Outdated Operating System" in data["findings"][0]["issue"]


def test_tc09_multiple_vulnerabilities(client):
    """
    TC09: Multiple Vulnerabilities
    Input: Root Login + Password Auth + No Firewall
    Expected: Multiple findings categorized by severity
    """
    mock_findings = [
        {
            "severity": "Critical",
            "issue": "Root Login Enabled via SSH",
            "explanation": "PermitRootLogin set to yes.",
            "impact": "Direct root vulnerability.",
            "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config"
        },
        {
            "severity": "High",
            "issue": "Password Authentication Enabled over SSH",
            "explanation": "PasswordAuthentication set to yes.",
            "impact": "Brute force risk.",
            "fix_command": "sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config"
        },
        {
            "severity": "High",
            "issue": "UFW Firewall is Inactive",
            "explanation": "No active firewall rules.",
            "impact": "Direct port exposure.",
            "fix_command": "sudo ufw enable"
        }
    ]

    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService()
    client.app.dependency_overrides[get_gemini_service] = lambda: MockGeminiService(findings=mock_findings)

    payload = {
        "server_ip": "192.168.1.58",
        "port": 22,
        "username": "admin",
        "password": "password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["findings_count"] == 3
    assert data["critical_count"] == 1
    assert data["high_count"] == 2
    assert data["medium_count"] == 0
    assert data["low_count"] == 0


def test_tc10_invalid_credentials(client):
    """
    TC10: Invalid Credentials
    Input: Wrong Username/Password
    Expected: Authentication Failed message displayed
    """
    client.app.dependency_overrides[get_ssh_service] = lambda: MockSSHService(should_fail_auth=True)

    payload = {
        "server_ip": "192.168.1.59",
        "port": 22,
        "username": "wrong_user",
        "password": "wrong_password"
    }

    response = client.post("/api/audits", json=payload)
    assert response.status_code == 201  # API catches exceptions and returns success=False response object with 201 status code
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["error"]["code"] == "SSH_AUTHENTICATION_FAILED"
    assert "Authentication failed" in res_data["error"]["message"]
