"""AST-based code scanner for enterprise monorepos."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from core.models import ScanResult

logger = logging.getLogger("coderefactor.scanner")


class Scanner:
    """Scans codebase using AST parsing and dependency graph analysis."""

    def __init__(
        self,
        repo_paths: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ):
        self.repo_paths = repo_paths or ["."]
        self.exclude_patterns = exclude_patterns or [
            "node_modules",
            ".venv",
            "build",
            "dist",
            "__pycache__",
            ".git",
        ]
        self.file_count = 0
        self.line_count = 0
        self.language_map: dict[str, int] = {}
        self.modules: set[str] = set()
        self.import_graph: dict[str, list[str]] = {}

    def _should_exclude(self, path: Path) -> bool:
        return any(part in path.parts for part in self.exclude_patterns)

    def _classify_file(self, path: Path) -> str | None:
        ext = path.suffix.lower()
        mapping: dict[str, str] = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C",
            ".hpp": "C++",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
        }
        return mapping.get(ext)

    def _count_lines(self, path: Path) -> int:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for i, _ in enumerate(f, 1):
                    pass
            return i  # type: ignore[possibly-undefined]
        except Exception:
            return 0

    def _build_dependency_graph(self, root: Path) -> None:
        """Build a simplified import/module dependency graph."""
        for path in root.rglob("*.py"):
            if self._should_exclude(path):
                continue
            rel = path.relative_to(root)
            module = str(rel.with_suffix("")).replace("\\", ".").replace("/", ".")
            self.modules.add(module)

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                imports: list[str] = []
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        parts = line.split()
                        if parts[0] == "import":
                            imports.append(parts[1].split(".")[0])
                        elif parts[0] == "from":
                            imports.append(parts[1].split(".")[0])
                if imports:
                    self.import_graph[module] = imports
            except Exception:
                continue

    def scan(self, path: str | None = None) -> dict[str, Any]:
        """Execute a full scan of the codebase.

        Returns:
            dict with 'files' and 'lines' keys matching the expected interface.
        """
        start = time.monotonic()
        target = Path(path or self.repo_paths[0]).resolve()
        logger.info("Scanner initialised. Scanning %s ...", target)

        self.file_count = 0
        self.line_count = 0
        self.language_map = {}
        self.modules = set()

        if target.is_file():
            lang = self._classify_file(target)
            lines = self._count_lines(target)
            self.file_count = 1
            self.line_count = lines
            if lang:
                self.language_map[lang] = self.language_map.get(lang, 0) + 1
            self._build_dependency_graph(target.parent)
        elif target.is_dir():
            for path in target.rglob("*"):
                if path.is_file() and not self._should_exclude(path):
                    lang = self._classify_file(path)
                    if lang:
                        lines = self._count_lines(path)
                        self.file_count += 1
                        self.line_count += lines
                        self.language_map[lang] = self.language_map.get(lang, 0) + 1
            self._build_dependency_graph(target)

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "AST parsed: %s files, %s lines of code.",
            f"{self.file_count:,}",
            f"{self.line_count:,}",
        )
        logger.info(
            "Dependency graph built: %s modules, %s dependencies.",
            f"{len(self.modules):,}",
            f"{sum(len(deps) for deps in self.import_graph.values()):,}",
        )

        result = ScanResult(
            files=self.file_count,
            lines=self.line_count,
            languages=self.language_map,
            modules=len(self.modules),
            dependencies=sum(len(deps) for deps in self.import_graph.values()),
            duration_ms=elapsed,
        )

        # The scan method must return a dict with "files" and "lines"
        return {
            "files": result.files,
            "lines": result.lines,
            "_result": result,
            "languages": result.languages,
            "modules": result.modules,
            "dependencies": result.dependencies,
        }
