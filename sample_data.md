# TC01
## Input
```json
{
  "server_ip": "192.168.1.50",
  "port": 22,
  "username": "admin",
  "password": "secure_password"

```

## Output
```json
[
  {
    "severity": "Low",
    "issue": "Server Configuration Assessment Complete",
    "explanation": "No critical vulnerabilities were detected in the configuration checks.",
    "impact": "Minimal immediate security risk identified.",
    "fix_command": "# Continue monitoring and run periodic full security audits."
  }
]
```

---

# TC02
## Input
```json
{
  "server_ip": "192.168.1.51",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "Critical",
    "issue": "Root Login Enabled via SSH",
    "explanation": "PermitRootLogin is enabled (set to yes) in /etc/ssh/sshd_config, allowing direct root access over SSH.",
    "impact": "Attackers can brute-force the root password directly, bypassing intermediate account controls and obtaining complete administrative access.",
    "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  }
]
```

---

# TC03
## Input
```json
{
  "server_ip": "192.168.1.52",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "High",
    "issue": "Password Authentication Enabled over SSH",
    "explanation": "PasswordAuthentication is set to yes in sshd_config. Using passwords instead of SSH keys increases susceptibility to brute force attacks.",
    "impact": "Attackers could successfully brute force user accounts with weak credentials.",
    "fix_command": "sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  }
]
```

---

# TC04
## Input
```json
{
  "server_ip": "192.168.1.53",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "Medium",
    "issue": "Insecure Password Expiration Policy",
    "explanation": "PASS_MAX_DAYS is set to 99999 in /etc/login.defs. Passwords do not expire frequently enough.",
    "impact": "Compromised user credentials remain valid indefinitely, maximizing the attacker's window of opportunity.",
    "fix_command": "sudo sed -i 's/^PASS_MAX_DAYS.*/PASS_MAX_DAYS   90/' /etc/login.defs"
  }
]
```

---

# TC05
## Input
```json
{
  "server_ip": "192.168.1.54",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "High",
    "issue": "UFW Firewall is Inactive",
    "explanation": "Uncomplicated Firewall (UFW) is installed but currently disabled (inactive).",
    "impact": "All network ports are unprotected by a local firewall, increasing the system's attack surface.",
    "fix_command": "sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw allow ssh && sudo ufw --force enable"
  }
]
```

---

# TC06
## Input
```json
{
  "server_ip": "192.168.1.55",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "High",
    "issue": "SSH Service Inactive",
    "explanation": "The SSH daemon (sshd) is inactive or stopped on the server.",
    "impact": "Administrators will lose remote access, and automated deployment pipelines relying on SSH will fail.",
    "fix_command": "sudo systemctl enable --now ssh"
  }
]
```

---

# TC07
## Input
```json
{
  "server_ip": "192.168.1.56",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "Medium",
    "issue": "SSH MaxAuthTries Inadequately Configured",
    "explanation": "MaxAuthTries is set to 10, which is higher than the recommended limit of 3 or 4.",
    "impact": "Allows attackers more password guessing attempts per SSH connection, increasing brute-force efficiency.",
    "fix_command": "sudo sed -i 's/^MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  }
]
```

---

# TC08
## Input
```json
{
  "server_ip": "192.168.1.57",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "High",
    "issue": "Outdated Operating System",
    "explanation": "The server is running Ubuntu 16.04, which has reached End-of-Life (EOL) and no longer receives security updates.",
    "impact": "The system remains vulnerable to unpatched public CVEs, leading to high risk of server compromise.",
    "fix_command": "# Perform a full system backup and upgrade to a supported LTS release (e.g., Ubuntu 22.04 LTS or 24.04 LTS)."
  }
]
```

---

# TC09
## Input
```json
{
  "server_ip": "192.168.1.58",
  "port": 22,
  "username": "admin",
  "password": "password123"
}
```

## Output
```json
[
  {
    "severity": "Critical",
    "issue": "Root Login Enabled via SSH",
    "explanation": "PermitRootLogin is enabled (set to yes) in /etc/ssh/sshd_config, allowing direct root access over SSH.",
    "impact": "Attackers can brute-force the root password directly, bypassing intermediate account controls and obtaining complete administrative access.",
    "fix_command": "sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  },
  {
    "severity": "High",
    "issue": "Password Authentication Enabled over SSH",
    "explanation": "PasswordAuthentication is set to yes in sshd_config. Using passwords instead of SSH keys increases susceptibility to brute force attacks.",
    "impact": "Attackers could successfully brute force user accounts with weak credentials.",
    "fix_command": "sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart sshd"
  },
  {
    "severity": "High",
    "issue": "UFW Firewall is Inactive",
    "explanation": "Uncomplicated Firewall (UFW) is installed but currently disabled (inactive).",
    "impact": "All network ports are unprotected by a local firewall, increasing the system's attack surface.",
    "fix_command": "sudo ufw default deny incoming && sudo ufw default allow outgoing && sudo ufw allow ssh && sudo ufw --force enable"
  }
]
```

---

# TC10
## Input
```json
{
  "server_ip": "192.168.1.59",
  "port": 22,
  "username": "wrong_user",
  "password": "wrong_password"
}
```

## Output
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SSH_AUTHENTICATION_FAILED",
    "message": "Audit execution failed: Authentication failed for wrong_user@192.168.1.100:22",
    "details": "SSHConnectionError(\"Authentication failed for wrong_user@192.168.1.100:22\")"
  }
}
```
