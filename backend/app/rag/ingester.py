"""PDF parser and Git crawler modules.

Purpose:
    Extract text contents from resume files and crawl cloned code repo directories.
"""

import os
from pathlib import Path
from urllib.parse import urlparse


class PDFExtractor:
    """Utility to extract plain text from PDF document files."""

    @staticmethod
    def extract(path: Path) -> str:
        """Extract text from the pages of a PDF file using pypdf."""
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Dependency 'pypdf' is missing.") from exc

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at {path}")

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(page.strip() for page in pages if page.strip())
        if not text:
            raise ValueError("No text could be extracted from the resume PDF.")
        return text


class GitHubCrawler:
    """Clones public repositories and yields paths to code source files."""

    ignored_dirs = {
        ".git",
        "node_modules",
        ".next",
        "dist",
        "build",
        "__pycache__",
        ".venv",
        "venv",
        "venv_py",
    }
    ignored_suffixes = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".lock",
        ".exe",
        ".dll",
    }

    # Only ingest these documentation files - they describe what a project does
    # in human-readable language without code noise
    readme_whitelist = {
        "readme.md",
        "readme.rst",
        "readme.txt",
        "readme",
    }

    @staticmethod
    def clone_repository(repo_url: str, branch: str, target_dir: Path) -> None:
        """Clone a git repository to a local folder using shallow depth."""
        try:
            from git import Repo
        except ImportError as exc:
            raise RuntimeError("Dependency 'GitPython' is missing.") from exc

        try:
            Repo.clone_from(repo_url, target_dir, branch=branch, depth=1)
        except Exception as exc:
            raise RuntimeError(f"Git clone failed: {exc}") from exc

    @classmethod
    def get_code_files(cls, repo_dir: Path):
        """Iterate ONLY README files in the cloned directory.
        
        We only ingest README files because they describe what a project does
        in human-readable language. Code files, configs, prompt templates, and
        JSON files create noise that confuses the RAG retrieval — e.g., the
        system returns 'lms_agent.py' prompt text as if it were the user's
        own self-description.
        """
        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            if any(part in cls.ignored_dirs for part in path.parts):
                continue
            # Only yield README files
            if path.name.lower() in cls.readme_whitelist:
                yield path

    @staticmethod
    def repo_name(repo_url: str) -> str:
        """Infer repository project directory name from URL."""
        parsed = urlparse(repo_url)
        name = Path(parsed.path.rstrip("/")).name
        return name.removesuffix(".git") or "repository"
