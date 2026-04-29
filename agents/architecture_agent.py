"""Architecture Agent — analyses layered boundaries and coupling."""

from __future__ import annotations

import logging
import random
import time

from core.models import (
    AgentType,
    ArchitectureReport,
    Severity,
    Violation,
)

logger = logging.getLogger("coderefactor.architecture_agent")


class ArchitectureAgent:
    """Analyses codebase architecture for layering violations and coupling issues.

    Simulates detection of boundary violations between architectural layers
    (e.g., presentation → business → data) in a large monorepo.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.type = AgentType.ARCHITECTURE

    def analyse(self, scan_data: dict) -> ArchitectureReport:
        """Analyse architectural boundaries and return violations."""
        start = time.monotonic()
        total_files = scan_data.get("files", 0)

        logger.info("Architecture Agent: analysing layered boundaries...")
        time.sleep(0.5)  # simulate processing

        # Simulate detection of boundary violations
        violations = self._detect_boundary_violations(total_files)
        coupling_scores = self._calculate_coupling(scan_data)

        elapsed = time.monotonic() - start
        logger.info(
            "Found %d boundary violations across %d files (%.1fs).",
            len(violations),
            total_files,
            elapsed,
        )

        return ArchitectureReport(
            boundary_violations=violations,
            total_violations=len(violations),
            layers_analyzed=[
                "presentation",
                "application",
                "domain",
                "infrastructure",
                "persistence",
            ],
            coupling_scores=coupling_scores,
        )

    def _detect_boundary_violations(self, total_files: int) -> list[Violation]:
        """Simulate detection of layer boundary violations."""
        violation_count = min(153, int(total_files * 0.008))
        violations: list[Violation] = []
        layers = [
            "presentation → domain",
            "infrastructure → presentation",
            "domain → infrastructure",
            "persistence → presentation",
            "application → persistence",
        ]
        files = [f"src/layer_{i}/module_{j}.py" for i in range(5) for j in range(20)]

        for i in range(violation_count):
            layer = layers[i % len(layers)]
            f = random.choice(files)
            violations.append(
                Violation(
                    rule_id=f"LAYER-{(i % 10) + 1:03d}",
                    description=f"Layer boundary violation: {layer}",
                    severity=Severity.HIGH if i < 30 else Severity.MEDIUM,
                    file_path=f,
                    line_number=random.randint(10, 800),
                    suggestion=(
                        "Extract interface to domain layer and invert dependency"
                        if "infrastructure" in layer
                        else "Move import to appropriate layer"
                    ),
                    category="architecture",
                )
            )

        violations.sort(key=lambda v: v.severity.value, reverse=True)
        return violations

    def _calculate_coupling(self, scan_data: dict) -> dict[str, float]:
        """Calculate coupling scores between layers."""
        modules = scan_data.get("modules", 1200)
        return {
            "presentation": round(random.uniform(0.1, 0.3), 3),
            "application": round(random.uniform(0.3, 0.5), 3),
            "domain": round(random.uniform(0.2, 0.4), 3),
            "infrastructure": round(random.uniform(0.4, 0.7), 3),
            "persistence": round(random.uniform(0.3, 0.6), 3),
            "avg_coupling": round(random.uniform(0.25, 0.45), 3),
            "total_dependencies": modules * 8 + random.randint(-100, 100),
        }
