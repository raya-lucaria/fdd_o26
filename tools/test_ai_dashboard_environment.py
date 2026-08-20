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
