"""Data models for CodeRefactorAI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AgentType(str, Enum):
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    WRITER = "writer"
    TEST = "test"
    ORCHESTRATOR = "orchestrator"


@dataclass
class ScanResult:
    files: int
    lines: int
    languages: dict[str, int] = field(default_factory=dict)
    modules: int = 0
    dependencies: int = 0
    duration_ms: float = 0.0


@dataclass
class Violation:
    rule_id: str
    description: str
    severity: Severity
    file_path: str
    line_number: int
    suggestion: str | None = None
    category: str = "general"


@dataclass
class ArchitectureReport:
    boundary_violations: list[Violation]
    total_violations: int
    layers_analyzed: list[str] = field(default_factory=list)
    coupling_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class SecurityFinding:
    vulnerability_id: str
    cwe_id: str
    description: str
    severity: Severity
    file_path: str
    line_number: int
    remediation: str | None = None


@dataclass
class SecurityReport:
    critical_findings: list[SecurityFinding]
    high_findings: list[SecurityFinding]
    medium_findings: list[SecurityFinding]
    low_findings: list[SecurityFinding]

    @property
    def total(self) -> int:
        return (
            len(self.critical_findings)
            + len(self.high_findings)
            + len(self.medium_findings)
            + len(self.low_findings)
        )

    @property
    def critical_count(self) -> int:
        return len(self.critical_findings)

    @property
    def injection_risks(self) -> int:
        return sum(
            1
            for f in [
                *self.critical_findings,
                *self.high_findings,
                *self.medium_findings,
            ]
            if "injection" in f.vulnerability_id.lower()
        )

    @property
    def hardcoded_credentials(self) -> int:
        return sum(
            1
            for f in [*self.critical_findings, *self.high_findings]
            if "credential" in f.vulnerability_id.lower()
        )


@dataclass
class Patch:
    file_path: str
    diff: str
    description: str
    patch_id: str = ""


@dataclass
class RefactoringPlan:
    patches: list[Patch]
    total_files_changed: int
    estimated_token_cost: int = 0


@dataclass
class TestResult:
    total: int
    passed: int
    failed: int
    coverage: float = 0.0
    duration_ms: float = 0.0
    failures: list[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


@dataclass
class PullRequest:
    repo: str
    branch: str
    title: str
    body: str
    url: str = ""
    number: int = 0


@dataclass
class GovernanceReport:
    scan_result: ScanResult
    architecture_report: ArchitectureReport | None = None
    security_report: SecurityReport | None = None
    refactoring_plan: RefactoringPlan | None = None
    test_results: list[TestResult] = field(default_factory=list)
    pull_requests: list[PullRequest] = field(default_factory=list)
    total_tokens: int = 0
    total_elapsed_seconds: float = 0.0
    repair_loops: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
