import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RAYA = ROOT.parents[2] / "raya_lucaria/.worktrees/navigation-first-course-rail"
MAIN = (
    ROOT
    / "course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md"
)
ANNEX = MAIN.parent / "A_evidencia_dashboard/0_index.md"


def test_dashboard_evidence_is_a_linked_optional_appendix() -> None:
    """Keep evidence reachable without extending the numbered lesson sequence."""
    assert ANNEX.is_file()

    main = MAIN.read_text(encoding="utf-8")
    annex = ANNEX.read_text(encoding="utf-8")

    assert "[[evidencia-dashboard-ia]]" in main
    assert "id: evidencia-dashboard-ia" in annex
    assert "anexo opcional" in annex.lower()


def test_raya_build_marks_annex_and_makes_its_sequence_label_explicit() -> None:
    """Raya cannot omit appendices from sequence yet, so never imply required work."""
    subprocess.run(
        ["uv", "run", "raya", "build", str(ROOT)],
        cwd=RAYA,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": ".venv-local"},
        check=True,
        stdout=subprocess.DEVNULL,
    )

    artifact = ROOT / "artifact"
    navigation = json.loads(
        (artifact / "data/navigation.json").read_text(encoding="utf-8")
    )
    items = {item["id"]: item for item in navigation["items"]}
    main = items["ia-escala-decision"]
    annex = items["evidencia-dashboard-ia"]

    assert annex["hierarchy_key"] == "appendix"
    assert "Anexo opcional" in annex["nav_title"]
    assert main["next"] == annex["id"]

    main_html = (
        artifact / "site" / main["url"]
    ).read_text(encoding="utf-8")
    match = re.search(
        r'<a rel="next"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', main_html
    )
    assert match is not None
    assert "Next: Anexo opcional" in match.group(2)
    resolved = (artifact / "site" / main["url"]).parent / match.group(1)
    assert resolved.resolve().is_file()
