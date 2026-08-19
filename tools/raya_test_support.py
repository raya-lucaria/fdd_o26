"""Shared Raya checkout discovery for integration tests."""

from collections.abc import Mapping
import os
from pathlib import Path

import pytest


PINNED_WORKTREE = Path(
    "raya_lucaria/.worktrees/navigation-first-course-rail"
)


def _is_raya_checkout(path: Path) -> bool:
    manifest = path / "pyproject.toml"
    return manifest.is_file() and 'name = "raya-lucaria"' in manifest.read_text(
        encoding="utf-8"
    )


def resolve_raya_checkout(
    repository_root: Path,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Find the pinned Raya worktree without assuming repository depth."""
    environment = os.environ if environ is None else environ
    override = environment.get("RAYA_CHECKOUT")
    if override:
        candidate = Path(override).expanduser().resolve()
        if _is_raya_checkout(candidate):
            return candidate
        raise FileNotFoundError(
            f"RAYA_CHECKOUT does not point to a Raya checkout: {candidate}"
        )

    root = Path(repository_root).resolve()
    for ancestor in (root, *root.parents):
        candidate = ancestor / PINNED_WORKTREE
        if _is_raya_checkout(candidate):
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not find Raya's navigation-first-course-rail worktree; "
        "set RAYA_CHECKOUT to its absolute path."
    )


def resolve_raya_checkout_or_skip(
    repository_root: Path,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Resolve Raya for integration guards, or skip in dependency-light CI."""
    try:
        return resolve_raya_checkout(repository_root, environ)
    except FileNotFoundError as error:
        pytest.skip(
            f"Raya integration checkout unavailable ({error}); the "
            "course-pages job independently validates and builds the course."
        )
