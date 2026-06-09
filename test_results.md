# AI Linux Security Auditor - Test Results Report

This document contains the formal test execution results conducted on the system.

---

## 1. Test Run Metadata

| Parameter | Value |
|---|---|
| **Test Run ID** | TR-20260609-001 |
| **Execution Date & Time** | 2026-06-09T20:53:13+05:30 (Local Time) |
| **Lead Tester** | Antigravity QA Automation Agent |
| **System Under Test** | AI Linux Security Auditor Backend (FastAPI + SQL Alchemy) |
| **Testing Framework** | Pytest v9.0.3 |
| **Environment** | Python 3.11.9, Windows (Local Development venv), Isolated File SQLite |
| **Overall Status** | **PASSED (100% Success Rate)** |

---

## 2. Execution Summary

| Total Executed | Passed | Failed | Blocked | Success Rate |
|---|---|---|---|---|
| **10** | **10** | **0** | **0** | **100.0%** |

---

## 3. Test Cases Execution Details

| Test Case ID | Scenario Name | Test Type | Input Condition | Expected Output | Status |
|---|---|---|---|---|---|
| **TC01** | Secure Server Audit | Happy Path | Valid IP, Username, Password | Audit completed successfully with Low Risk findings | **PASS** |
| **TC02** | Root Login Enabled | Happy Path | Server with `PermitRootLogin yes` | Critical finding generated for Root Login | **PASS** |
| **TC03** | Password Authentication Enabled | Happy Path | Server with `PasswordAuthentication yes` | High Risk finding generated | **PASS** |
| **TC04** | Weak Password Policy | Happy Path | Server with `PASS_MAX_DAYS 99999` | Medium Risk finding generated | **PASS** |
| **TC05** | Firewall Not Installed | Happy Path | Server without UFW Firewall | High Risk finding for missing firewall | **PASS** |
| **TC06** | SSH Service Inactive | Happy Path | Server with SSH service stopped | High Risk finding for SSH service issue | **PASS** |
| **TC07** | Excessive Login Attempts | Happy Path | Server with `MaxAuthTries 10` | Medium Risk finding generated | **PASS** |
| **TC08** | Outdated Operating System | Happy Path | Ubuntu 16.04 Server | High Risk finding for unsupported OS | **PASS** |
| **TC09** | Multiple Vulnerabilities | Happy Path | Root Login + Password Auth + No Firewall | Multiple findings categorized by severity | **PASS** |
| **TC10** | Invalid Credentials | Failure Path | Wrong Username/Password | Authentication Failed message displayed | **PASS** |

---

## 4. Raw Pytest Console Output

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\admin\Desktop\ai-linux-security-auditor\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\admin\Desktop\ai-linux-security-auditor\backend
plugins: anyio-4.13.0, mock-3.15.1
collecting ... collected 10 items

tests/test_audit.py::test_tc01_secure_server_audit PASSED                [ 10%]
tests/test_audit.py::test_tc02_root_login_enabled PASSED                 [ 20%]
tests/test_audit.py::test_tc03_password_authentication_enabled PASSED    [ 30%]
tests/test_audit.py::test_tc04_weak_password_policy PASSED               [ 40%]
tests/test_audit.py::test_tc05_firewall_not_installed PASSED             [ 50%]
tests/test_audit.py::test_tc06_ssh_service_inactive PASSED               [ 60%]
tests/test_audit.py::test_tc07_excessive_login_attempts PASSED           [ 70%]
tests/test_audit.py::test_tc08_outdated_operating_system PASSED          [ 80%]
tests/test_audit.py::test_tc09_multiple_vulnerabilities PASSED           [ 90%]
tests/test_audit.py::test_tc10_invalid_credentials PASSED                [100%]

======================== 10 passed, 1 warning in 1.62s ========================
```
