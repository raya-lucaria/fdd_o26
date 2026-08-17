"""Guardas editoriales para la unidad de arquitectura de computadoras."""

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
UNIT = ROOT / "course/3_arquitectura_de_computadoras"
PAGES = [
    UNIT / "0_index.md",
    UNIT / "1_compute_instrucciones_cpu/0_index.md",
    UNIT / "2_memoria_y_datos/0_index.md",
    UNIT / "3_paralelismo_performance_energia/0_index.md",
    UNIT / "4_ai_escala_y_decision/0_index.md",
]
ASSETS = UNIT / "_assets"
ASSIGNMENT = (
    ROOT
    / "course/3_arquitectura_de_computadoras/_official/assignments/1_videos_hardware.yaml"
)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return re.sub(r"\A---.*?^---\s*", "", text, flags=re.S | re.M)


def test_assignment_is_three_hardware_videos_due_august_18():
    assignment = load_yaml(ASSIGNMENT)
    assert assignment["id"] == "videos-hardware"
    assert assignment["content"]["due"] == "2026-08-18"
    instructions = assignment["content"]["instructions"]
    assert instructions.count("https://www.youtube.com/watch?v=") == 3
    assert "01_arquitectura.ipynb" not in instructions
    assert not (ASSIGNMENT.parent / "1_notebook_arquitectura.yaml").exists()


def test_unit_has_index_and_four_lessons_with_raya_frontmatter():
    assert all(path.is_file() for path in PAGES)
    ids = []
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        ids.append(metadata["id"])
        assert metadata["title"]
        assert metadata["summary"]
        assert metadata["status"] == "ready"
    assert len(ids) == len(set(ids)) == 5


def test_unit_keeps_scope_and_adhd_friendly_shape():
    prose = "\n".join(body(path) for path in PAGES)
    words = len(prose.split())
    assert 5700 <= words <= 6300
    assert "125 minutos" in prose
    assert prose.count("**FACT") >= 8
    assert prose.count("**DERIVED") >= 5
    assert prose.count("**ESTIMATE") >= 1
    assert "## Siete modelos mentales" in prose
    assert not re.search(r"<(?:img|div|figure|span|details)\b", prose)
    for paragraph in re.split(r"\n\s*\n", prose):
        if not paragraph.startswith(("|", "-", "1.", "2.", "3.", "4.", "5.")):
            assert len(paragraph.split()) <= 120


def test_practice_counts_are_exact_and_colocated_at_the_end():
    official = UNIT / "4_ai_escala_y_decision/_official"
    quizzes = list((official / "quizzes").glob("*.yaml"))
    scenarios = list((official / "examples").glob("*.yaml"))
    cards = list((official / "cards").glob("*.yaml"))
    assert len(quizzes) == 6
    assert len(scenarios) == 3
    assert len(cards) == 15
    assert not any("?" in body(path) for path in PAGES[:-1])


def test_assets_have_exact_credits_alt_and_text_fallbacks():
    expected = {
        "anatomia-computadora.svg",
        "cpu-vs-gpu.svg",
        "escala-decision.svg",
        "escala-energia.svg",
        "hero-arquitectura.webp",
        "isa-ciclos.svg",
        "jerarquia-memoria-datos.svg",
        "memoria-ai.svg",
        "real-macbook-m5.webp",
        "real-rtx-5090.webp",
        "real-tsubame4-node.webp",
        "roofline-lite.svg",
    }
    actual = {path.name for path in ASSETS.iterdir() if path.name != "CREDITOS.md"}
    assert actual == expected
    credits = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for name in expected:
        assert f"| {name} |" in credits
    prose = "\n".join(body(path) for path in PAGES)
    assert prose.count("![") == 12
    assert prose.count("**Lectura visual:**") == 9


def test_notebook_is_executed_and_practice_is_only_at_end():
    notebook = json.loads((UNIT / "code/01_arquitectura.ipynb").read_text())
    notebook_text = json.dumps(notebook, ensure_ascii=False)
    assert "Unidad 3" in notebook_text
    assert "Módulo 15" not in notebook_text
    practice_cells = [
        index
        for index, cell in enumerate(notebook["cells"])
        if "## Práctica FINAL — post-clase" in "".join(cell.get("source", []))
    ]
    assert practice_cells == [len(notebook["cells"]) - 4]
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert code
    assert code[-1]["id"] == "ejercicio"
    assert all("outputs" in cell for cell in code)
    assert not any(
        output.get("output_type") == "error"
        for cell in code
        for output in cell["outputs"]
    )
