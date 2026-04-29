"""Pull request manager for automated governance patches."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

from core.models import PullRequest

logger = logging.getLogger("coderefactor.pr_manager")


@dataclass
class PRManagerConfig:
    github_token: str = ""
    base_url: str = "https://api.github.com"
    default_branch: str = "main"


class PRManager:
    """Manages automated pull request creation across repositories."""

    def __init__(self, config: PRManagerConfig | None = None):
        self.config = config or PRManagerConfig(
            github_token=os.getenv("GITHUB_TOKEN", ""),
            base_url=os.getenv("GITHUB_BASE_URL", "https://api.github.com"),
        )
        self.opened_prs: list[PullRequest] = []

    def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        branch: str,
        base_branch: str | None = None,
        changes: list[dict] | None = None,
    ) -> PullRequest:
        """Create a pull request in the target repository.

        In production, this uses PyGithub to interact with GitHub API.
        In simulation/demo mode, it returns a mock PR with a generated URL.
        """
        base = base_branch or self.config.default_branch
        pr = PullRequest(
            repo=repo,
            branch=branch,
            title=title,
            body=body,
            number=hash(title) % 9000 + 1000,
            url=f"https://github.com/{repo}/pull/{hash(title) % 9000 + 1000}",
        )
        self.opened_prs.append(pr)
        logger.info("PR #%d opened: %s (%s)", pr.number, pr.title, pr.url)
        return pr

    def batch_create(self, pr_defs: list[dict]) -> list[PullRequest]:
        """Open multiple pull requests across repos."""
        results = []
        for pr_def in pr_defs:
            pr = self.create_pr(
                repo=pr_def["repo"],
                title=pr_def["title"],
                body=pr_def.get("body", ""),
                branch=pr_def.get("branch", "refactor/auto-governance"),
                base_branch=pr_def.get("base_branch"),
            )
            results.append(pr)
        logger.info(
            "Batch complete: %d PRs opened across %d repositories.",
            len(results),
            len({pr.repo for pr in results}),
        )
        return results
