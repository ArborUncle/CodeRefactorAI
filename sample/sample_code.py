"""Sample code with intentional issues for CodeRefactorAI to detect and fix."""

from __future__ import annotations

import hashlib
import os
import subprocess
from typing import Any

# === Architecture Violation: Domain importing infrastructure directly ===
from sample.infrastructure import DatabaseClient  # type: ignore[import]


# === Security Issue 1: Hard-coded credentials ===
DB_PASSWORD = "super_secret_password_123!"  # CWE-798
API_KEY = "sk-live-abc123def456ghi789jkl"  # CWE-798
SECRET_TOKEN = "3a1f2b8c9d0e4f5a6b7c8d9e0f1a2b3c"  # CWE-798


# === Architecture Issue: God class with high coupling ===
class UserService:  # LAYER-001: presentation mixing with domain
    """Handles everything — violates single responsibility principle."""

    def __init__(self):
        self.db = DatabaseClient()
        self.cache: dict[str, Any] = {}
        self._secret = "inline_secret_456"  # CWE-798

    def login(self, username: str, password: str) -> dict[str, Any]:
        # Security Issue 2: SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"  # CWE-89
        result = self.db.execute(query)
        if result:
            token = hashlib.md5(f"{username}:{password}".encode()).hexdigest()  # CWE-327: weak hash
            return {"token": token, "user": result}
        return {"error": "Invalid credentials"}

    def export_data(self, filepath: str) -> str:
        # Security Issue 3: Path Traversal
        with open(f"/data/exports/{filepath}", "r") as f:  # CWE-22
            return f.read()

    def ping_host(self, hostname: str) -> bool:
        # Security Issue 4: Command Injection
        result = subprocess.run(  # CWE-78
            f"ping -c 1 {hostname}",
            shell=True,
            capture_output=True,
        )
        return result.returncode == 0

    def process_user_input(self, user_input: str) -> str:
        # Security Issue 5: XSS via unsafe HTML rendering
        return f"<div>{user_input}</div>"  # CWE-79


# === Architecture Issue: Circular dependency pattern ===
class OrderProcessor:
    """Depends on UserService which depends on infrastructure — creates tight coupling."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def process(self, order_data: dict) -> dict:
        # Mixed concerns: data access + business logic + presentation
        user = self.user_service.login(
            order_data.get("user", ""),
            order_data.get("pass", ""),
        )
        return {"order_id": 1234, "user": user, "status": "created"}


# === Security Issue 6: Insecure deserialization ===
def load_config(serialised: str) -> Any:
    import pickle  # CWE-502: unsafe deserialization
    return pickle.loads(serialised.encode())  # type: ignore[arg-type]


# === Configuration issue: debug mode ===
DEBUG_MODE = True  # CWE-16: debug mode in production
