"""Security Agent — CWE Top 25 + OWASP audit engine."""

from __future__ import annotations

import logging
import random
import time

from core.models import (
    AgentType,
    SecurityFinding,
    SecurityReport,
    Severity,
)

logger = logging.getLogger("coderefactor.security_agent")


class SecurityAgent:
    """Audits codebase against CWE Top 25 and OWASP Top 10.

    Simulates static analysis for hard-coded credentials, injection risks,
    and other common vulnerability patterns.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.type = AgentType.SECURITY

    def audit(self, scan_data: dict) -> SecurityReport:
        """Run a full security audit on the scanned codebase."""
        total_files = scan_data.get("files", 0)
        logger.info("Security Agent: running CWE Top 25 + OWASP audit...")
        time.sleep(0.8)  # simulate deep analysis

        critical = self._find_critical(total_files)
        high = self._find_high(total_files)
        medium = self._find_medium(total_files)
        low = self._find_low(total_files)

        report = SecurityReport(
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
        )

        logger.info(
            "Security audit complete: %d critical, %d high, %d medium, %d low.",
            len(critical),
            len(high),
            len(medium),
            len(low),
        )
        logger.info("CRITICAL: %d hard-coded credentials, %d injection risks.",
                     report.hardcoded_credentials, report.injection_risks)
        return report

    def _find_critical(self, total_files: int) -> list[SecurityFinding]:
        count = max(1, int(total_files * 0.0003))
        findings: list[SecurityFinding] = []
        patterns = [
            ("CWE-798", "credential_hardcoded", "Hard-coded API key/secret in source code",
             Severity.CRITICAL),
            ("CWE-89", "sqli_reflected", "SQL injection via string concatenation",
             Severity.CRITICAL),
            ("CWE-78", "os_command_injection", "OS command injection risk",
             Severity.CRITICAL),
            ("CWE-798", "credential_password", "Hard-coded database password",
             Severity.CRITICAL),
            ("CWE-798", "credential_token", "Hard-coded authentication token",
             Severity.CRITICAL),
            ("CWE-89", "sqli_raw_execute", "Raw SQL execution with unescaped input",
             Severity.CRITICAL),
        ]
        for i in range(min(count, len(patterns))):
            cwe, vid, desc, sev = patterns[i]
            findings.append(SecurityFinding(
                vulnerability_id=vid,
                cwe_id=cwe,
                description=desc,
                severity=sev,
                file_path=f"src/services/auth/provider_{i}.py",
                line_number=random.randint(20, 500),
                remediation="Use environment variables and secret manager. "
                            "Replace string formatting with parameterized queries.",
            ))
        return findings

    def _find_high(self, total_files: int) -> list[SecurityFinding]:
        count = max(1, int(total_files * 0.0008))
        findings: list[SecurityFinding] = []
        patterns = [
            ("CWE-79", "xss_reflected", "Reflected XSS in template rendering",
             Severity.HIGH),
            ("CWE-22", "path_traversal", "Path traversal via user-supplied filename",
             Severity.HIGH),
            ("CWE-352", "csrf_missing", "Missing CSRF token on state-changing endpoint",
             Severity.HIGH),
            ("CWE-611", "xxe_injection", "XML External Entity (XXE) injection",
             Severity.HIGH),
            ("CWE-502", "unsafe_deserialize", "Unsafe deserialization of user input",
             Severity.HIGH),
            ("CWE-918", "ssrf", "Server-Side Request Forgery via user URL",
             Severity.HIGH),
            ("CWE-276", "permission_default", "Insecure default file permissions",
             Severity.HIGH),
        ]
        seen = set()
        for i in range(count):
            cwe, vid, desc, sev = patterns[i % len(patterns)]
            if vid not in seen or random.random() < 0.3:
                seen.add(vid)
                findings.append(SecurityFinding(
                    vulnerability_id=f"{vid}_{i}",
                    cwe_id=cwe,
                    description=desc,
                    severity=sev,
                    file_path=f"src/api/endpoints/v2/handler_{i % 10}.py",
                    line_number=random.randint(15, 600),
                    remediation="Sanitize user input, use parameterized queries, "
                                "implement proper access controls.",
                ))
        return findings

    def _find_medium(self, total_files: int) -> list[SecurityFinding]:
        count = max(1, int(total_files * 0.0015))
        return [
            SecurityFinding(
                vulnerability_id=f"misconfig_{i}",
                cwe_id="CWE-16",
                description="Insecure configuration: debug mode enabled in production",
                severity=Severity.MEDIUM,
                file_path=f"config/{'settings' if i % 2 == 0 else 'deploy'}.py",
                line_number=i * 12 + 5,
                remediation="Disable debug mode in production configuration.",
            )
            for i in range(count)
        ]

    def _find_low(self, total_files: int) -> list[SecurityFinding]:
        count = max(1, int(total_files * 0.002))
        return [
            SecurityFinding(
                vulnerability_id=f"info_leak_{i}",
                cwe_id="CWE-200",
                description="Potential information disclosure in error response",
                severity=Severity.LOW,
                file_path=f"src/middleware/error_handler.py",
                line_number=i * 20 + 10,
                remediation="Sanitise error messages before returning to client.",
            )
            for i in range(count)
        ]
