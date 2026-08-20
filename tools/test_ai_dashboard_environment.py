from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_lock_and_font_are_pinned():
    lock = (ROOT / "tools/ai_dashboard_requirements.lock").read_text()
    assert "seaborn==" in lock and "--hash=sha256:" in lock
    assert (ROOT / "tools/fonts/DejaVuSans.ttf").stat().st_size > 100_000


def test_pages_requires_dashboard_and_course_jobs():
    workflow = yaml.safe_load((ROOT / ".github/workflows/pages.yml").read_text())
    assert {"checks", "dashboard-assets", "course-build"} <= workflow["jobs"].keys()


def test_dashboard_gate_locks_its_full_suite_and_rejects_skips():
    lock = (ROOT / "tools/ai_dashboard_requirements.lock").read_text()
    workflow = yaml.safe_load((ROOT / ".github/workflows/pages.yml").read_text())
    checks_steps = "\n".join(str(step) for step in workflow["jobs"]["checks"]["steps"])
    dashboard_steps = "\n".join(
        str(step) for step in workflow["jobs"]["dashboard-assets"]["steps"]
    )

    for package in ("pytest==8.4.2", "playwright==1.60.0"):
        package_block = lock.split(package, 1)[1].split("\n\n", 1)[0]
        assert "--hash=sha256:" in package_block
    assert "pytest tools/ -q" not in checks_steps
    assert "uv pip sync" in dashboard_steps and "--require-hashes" in dashboard_steps
    assert "pytest tools/ -q" in dashboard_steps
    assert "playwright install --with-deps chromium" in dashboard_steps
    assert "[0-9]+ skipped" in dashboard_steps
