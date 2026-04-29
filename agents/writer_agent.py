"""Code Writer Agent — generates refactoring patches."""

from __future__ import annotations

import logging
import random
import time
import uuid

from core.models import (
    AgentType,
    ArchitectureReport,
    Patch,
    RefactoringPlan,
    SecurityReport,
)

logger = logging.getLogger("coderefactor.writer_agent")


class WriterAgent:
    """Generates automated refactoring patches based on architecture and security reports.

    Creates targeted code changes to fix violations found by analysis agents.
    Supports multi-round repair cycles with progressive improvement.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.type = AgentType.WRITER

    def plan_refactoring(
        self,
        arch_report: ArchitectureReport,
        sec_report: SecurityReport,
    ) -> RefactoringPlan:
        """Create a refactoring plan addressing all found violations."""
        logger.info("Code Writer Agent: planning refactoring patches...")
        time.sleep(0.6)

        patches: list[Patch] = []
        patch_id_counter = 0

        # Generate patches for boundary violations
        for v in arch_report.boundary_violations[:50]:
            patch_id_counter += 1
            patches.append(
                Patch(
                    patch_id=f"ARC-{patch_id_counter:04d}",
                    file_path=v.file_path,
                    description=f"Fix: {v.description[:80]}",
                    diff=self._generate_diff(v.file_path, v.suggestion or ""),
                )
            )

        # Generate patches for critical security findings
        for f in sec_report.critical_findings:
            patch_id_counter += 1
            patches.append(
                Patch(
                    patch_id=f"SEC-{patch_id_counter:04d}",
                    file_path=f.file_path,
                    description=f"Security fix: {f.description[:80]}",
                    diff=self._generate_security_diff(f),
                )
            )

        # Generate patches for high severity findings
        for f in sec_report.high_findings[:10]:
            patch_id_counter += 1
            patches.append(
                Patch(
                    patch_id=f"SEC-{patch_id_counter:04d}",
                    file_path=f.file_path,
                    description=f"Security fix: {f.description[:80]}",
                    diff=self._generate_security_diff(f),
                )
            )

        logger.info("Generated %d refactoring patches.", len(patches))
        return RefactoringPlan(
            patches=patches,
            total_files_changed=len({p.file_path for p in patches}),
            estimated_token_cost=len(patches) * 45000,
        )

    def regenerate_patches(
        self,
        plan: RefactoringPlan,
        failed_tests: list[str],
        repair_round: int,
    ) -> RefactoringPlan:
        """Regenerate patches for components that failed tests."""
        logger.info(
            "Writer Agent regenerating %d patches (round %d)...",
            len(failed_tests),
            repair_round,
        )
        time.sleep(0.4)

        new_patches: list[Patch] = []
        for test_name in failed_tests:
            # Simulate finding the relevant patch and improving it
            related_patches = [
                p for p in plan.patches if test_name.split(".")[0] in p.file_path
            ]
            for p in related_patches[:3]:
                new_patches.append(
                    Patch(
                        patch_id=f"{p.patch_id}-R{repair_round}",
                        file_path=p.file_path,
                        description=f"[Repair {repair_round}] {p.description}",
                        diff=p.diff.replace("TODO", "FIXED"),
                    )
                )

        plan.patches.extend(new_patches)
        plan.total_files_changed = len({p.file_path for p in plan.patches})
        logger.info("Regenerated %d additional patches.", len(new_patches))
        return plan

    def _generate_diff(self, file_path: str, suggestion: str) -> str:
        return (
            f"--- a/{file_path}\n"
            f"+++ b/{file_path}\n"
            f"@@ -1,5 +1,7 @@\n"
            f" # Auto-generated fix by CodeRefactorAI\n"
            f"-    # {suggestion}\n"
            f"+    # Applied: {suggestion}\n"
            f"+    # Review required before merge\n"
        )

    def _generate_security_diff(self, finding) -> str:
        return (
            f"--- a/{finding.file_path}\n"
            f"+++ b/{finding.file_path}\n"
            f"@@ -10,6 +10,8 @@\n"
            f" # Security fix for {finding.vulnerability_id}\n"
            f"-    # {finding.description}\n"
            f"+    # TODO: {finding.remediation or 'Apply fix'}\n"
            f"+    # Severity: {finding.severity.value}\n"
        )
