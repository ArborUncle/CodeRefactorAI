"""Test Agent — sandboxed test execution and repair loop."""

from __future__ import annotations

import logging
import random
import time

from core.models import (
    AgentType,
    RefactoringPlan,
    TestResult,
)

logger = logging.getLogger("coderefactor.test_agent")


class TestAgent:
    """Executes tests in a sandboxed environment and drives the repair loop.

    Runs the full test suite against refactored code, identifies failures,
    and triggers the Writer Agent for targeted repairs in a maximum of
    5 self-healing cycles.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.type = AgentType.TEST
        self.max_repair_loops = config.get("max_repair_loops", 5) if config else 5

    def execute(self, plan: RefactoringPlan) -> list[TestResult]:
        """Run the full test suite and return results across cycles."""
        logger.info("Test Agent: launching sandbox...")
        time.sleep(0.5)

        results: list[TestResult] = []

        # First run — initial test suite after refactoring
        first_run = self._run_test_suite(phase="initial")
        results.append(first_run)
        logger.info(
            "Collected %d tests. Passed: %d  Failed: %d",
            first_run.total,
            first_run.passed,
            first_run.failed,
        )

        # Repair loop — up to 5 rounds of fix → retest
        repair_round = 1
        while (
            first_run.failed > 0
            and repair_round <= self.max_repair_loops
            and first_run.pass_rate < 0.98
        ):
            logger.info("Repair loop %d/%d initiated...", repair_round, self.max_repair_loops)
            time.sleep(0.3)

            # Simulate writer regenerating patches
            patch_count = min(len(first_run.failures), 7)
            logger.info("Writer Agent regenerating %d patches...", patch_count)

            # Re-run tests after simulated repair
            rerun = self._run_test_suite(phase=f"repair_{repair_round}", repair=True)
            results.append(rerun)

            if rerun.failed == 0:
                logger.info("All %d tests passed! Repair successful.", rerun.total)
                break
            elif rerun.failed < first_run.failed:
                logger.info(
                    "Improvement: %d failures remaining (was %d).",
                    rerun.failed,
                    first_run.failed,
                )
                first_run = rerun
            else:
                logger.info("No improvement this round. Continuing...")

            repair_round += 1

        if repair_round > self.max_repair_loops and results[-1].failed > 0:
            logger.warning(
                "Max repair loops reached. %d tests still failing.",
                results[-1].failed,
            )

        return results

    def _run_test_suite(
        self,
        phase: str = "initial",
        repair: bool = False,
    ) -> TestResult:
        """Simulate running the test suite."""
        total = 11430
        if repair:
            passed = total
            failed = 0
            failures: list[str] = []
        else:
            passed = 11412
            failed = 18
            failures = [
                f"tests/{['api','core','services','integration'][i % 4]}/"
                f"test_{['auth','db','cache','validation','serializer'][i % 5]}_"
                f"{i:03d}.py::{['test_login','test_query','test_put','test_post','test_marshal'][i % 5]}"
                for i in range(failed)
            ]

        return TestResult(
            total=total,
            passed=passed,
            failed=failed,
            coverage=round(random.uniform(82.0, 94.0), 1),
            duration_ms=round(random.uniform(8000, 15000), 0),
            failures=failures,
        )
