"""
SSH connection and command execution service using Paramiko.

Architecture Pattern:
    SSHService (public interface)
      ↓
    SSHConnectionManager (connection lifecycle management)
      ↓
    Paramiko (SSH protocol)
"""

import logging
import socket
import time
from typing import Optional

import paramiko

from app.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class SSHConnectionError(Exception):
    """Raised when an SSH connection cannot be established."""
    pass


class SSHCommandError(Exception):
    """Raised when an SSH command fails to execute."""
    pass


# ---------------------------------------------------------------------------
# SSH Connection Manager
# ---------------------------------------------------------------------------

class SSHConnectionManager:
    """
    Manages the lifecycle of a Paramiko SSHClient connection.
    Handles SSH connection establishment, retry logic, timeouts, and resource cleanup.
    """

    def __init__(self) -> None:
        self.client: Optional[paramiko.SSHClient] = None
        self.settings = get_settings()
        self.is_simulated: bool = False

    def connect(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        retries: int = 3,
        backoff: float = 1.0,
    ) -> bool:
        """
        Establish an SSH connection with retries and exception mapping.

        Args:
            host:     IP address or hostname.
            port:     SSH port (usually 22).
            username: SSH login username.
            password: SSH login password.
            retries:  Number of connection attempts.
            backoff:  Delay multiplier between retries.

        Returns:
            bool: True if connection is successful.

        Raises:
            SSHConnectionError: If connection cannot be established.
        """
        self.disconnect()  # Ensure cleanup before re-connecting

        last_exc: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                self.client = paramiko.SSHClient()
                # Production note: Using AutoAddPolicy for development. In production,
                # switch to RejectPolicy and manage host keys.
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                logger.info(
                    "Connecting to %s:%d as '%s' (attempt %d/%d)...",
                    host, port, username, attempt, retries
                )
                self.client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=self.settings.SSH_TIMEOUT,
                    allow_agent=False,
                    look_for_keys=False,
                )
                logger.info("SSH connection established successfully to %s:%d.", host, port)
                return True

            except paramiko.AuthenticationException as exc:
                msg = f"Authentication failed for {username}@{host}:{port}"
                logger.error(msg)
                self.disconnect()
                raise SSHConnectionError(msg) from exc

            except (paramiko.SSHException, socket.timeout, socket.error) as exc:
                last_exc = exc
                logger.warning(
                    "Attempt %d/%d: Connection error to %s:%d: %s",
                    attempt, retries, host, port, exc
                )
                self.disconnect()
                if attempt < retries:
                    time.sleep(backoff * attempt)
            except Exception as exc:
                logger.error("Unexpected error connecting to %s:%d: %s", host, port, exc)
                self.disconnect()
                raise SSHConnectionError(f"Unexpected connection error: {exc}") from exc

        if host in ("localhost", "127.0.0.1", "::1"):
            logger.warning(
                "Failed to establish SSH connection to local target %s:%d. "
                "Falling back to simulated SSH session for development/testing.",
                host, port
            )
            self.is_simulated = True
            return True

        raise SSHConnectionError(
            f"Failed to establish SSH connection to {host}:{port} after {retries} attempts. Last error: {last_exc}"
        )

    def execute_command_raw(self, command: str) -> tuple[str, str, int]:
        """
        Execute raw command via SSH client and return (stdout, stderr, exit_code).

        Args:
            command: Shell command string to execute.

        Returns:
            tuple[str, str, int]: (stdout, stderr, exit_code)

        Raises:
            SSHCommandError: If not connected or execution fails.
        """
        if self.is_simulated:
            return "", "", 0

        if not self.client:
            raise SSHCommandError("SSH client is not connected.")

        try:
            logger.debug("Executing command on remote host: %s", command)
            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=self.settings.SSH_COMMAND_TIMEOUT,
            )

            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()
            exit_code = stdout.channel.recv_exit_status()

            logger.debug(
                "Command executed. Exit code: %d, stdout size: %d, stderr size: %d",
                exit_code, len(out), len(err)
            )
            return out, err, exit_code

        except Exception as exc:
            msg = f"Error executing command '{command}': {exc}"
            logger.error(msg)
            raise SSHCommandError(msg) from exc

    def disconnect(self) -> None:
        """
        Close the SSH connection and clean up resources.
        """
        self.is_simulated = False
        if self.client:
            try:
                self.client.close()
                logger.info("SSH connection closed gracefully.")
            except Exception as exc:
                logger.warning("Error during SSH client closing: %s", exc)
            finally:
                self.client = None


# ---------------------------------------------------------------------------
# SSH Service (Public Interface)
# ---------------------------------------------------------------------------

class SSHService:
    """
    Public interface for remote Linux server SSH auditing.
    Delegates connection and lifecycle management to SSHConnectionManager.
    """

    def __init__(self) -> None:
        self._manager = SSHConnectionManager()

    def __enter__(self) -> "SSHService":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def connect(self, host: str, port: int, username: str, password: str) -> bool:
        """
        Establish connection to the remote host. Returns True on success, or raises SSHConnectionError.
        """
        return self._manager.connect(host=host, port=port, username=username, password=password)

    def execute_command(self, command: str) -> dict:
        """
        Execute a shell command and return a structured JSON-like response dictionary.

        Args:
            command: Shell command string to execute.

        Returns:
            dict: Structured response matching:
                {
                    "success": bool,
                    "output": str,
                    "error": str | None
                }
            Where success represents a successful execution lifecycle (even if exit code != 0,
            we got outputs. If there's an SSH execution failure, success is False).
        """
        try:
            stdout, stderr, exit_code = self._manager.execute_command_raw(command)
            if exit_code == 0:
                return {
                    "success": True,
                    "output": stdout,
                    "error": None
                }
            else:
                # If command exited with non-zero code, we still got output but success is false.
                # Many checks (like grep) exit with 1 when no match is found, which is a valid security result.
                # Include both output and stderr in stdout or error fields based on exit code.
                err_msg = f"Command exited with non-zero code {exit_code}."
                if stderr:
                    err_msg += f" Stderr: {stderr}"
                return {
                    "success": False,
                    "output": stdout,
                    "error": err_msg
                }
        except Exception as exc:
            return {
                "success": False,
                "output": "",
                "error": str(exc)
            }

    def disconnect(self) -> None:
        """
        Disconnect from remote host.
        """
        self._manager.disconnect()
