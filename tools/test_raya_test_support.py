from importlib.util import find_spec
from pathlib import Path

import pytest

import tools.raya_test_support as raya_support
from tools.raya_test_support import resolve_raya_checkout


def test_shared_raya_checkout_discovery_is_available() -> None:
    assert find_spec("tools.raya_test_support") is not None


def _make_raya_checkout(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "pyproject.toml").write_text(
        '[project]\nname = "raya-lucaria"\n', encoding="utf-8"
    )
    return path


def test_override_selects_an_explicit_raya_checkout(tmp_path: Path) -> None:
    checkout = _make_raya_checkout(tmp_path / "custom-raya")

    assert resolve_raya_checkout(
        tmp_path / "course", {"RAYA_CHECKOUT": str(checkout)}
    ) == checkout.resolve()


@pytest.mark.parametrize(
    "repository_relative",
    ("fdd_o26", "fdd_o26/.worktrees/dashboard"),
)
def test_discovers_pinned_sibling_from_main_or_nested_worktree(
    tmp_path: Path, repository_relative: str
) -> None:
    repository = tmp_path / "itam" / repository_relative
    repository.mkdir(parents=True)
    checkout = _make_raya_checkout(
        tmp_path
        / "itam/raya_lucaria/.worktrees/navigation-first-course-rail"
    )

    assert resolve_raya_checkout(repository, {}) == checkout.resolve()


def test_missing_checkout_has_actionable_override_message(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="RAYA_CHECKOUT"):
        resolve_raya_checkout(tmp_path / "course", {})


def test_integration_resolver_is_available() -> None:
    assert getattr(raya_support, "resolve_raya_checkout_or_skip", None) is not None


def test_integration_resolver_keeps_available_checkout(tmp_path: Path) -> None:
    checkout = _make_raya_checkout(tmp_path / "custom-raya")

    assert raya_support.resolve_raya_checkout_or_skip(
        tmp_path / "course", {"RAYA_CHECKOUT": str(checkout)}
    ) == checkout.resolve()


def test_integration_resolver_skips_when_checkout_is_external(
    tmp_path: Path,
) -> None:
    with pytest.raises(pytest.skip.Exception, match="course-pages"):
        raya_support.resolve_raya_checkout_or_skip(tmp_path / "course", {})
