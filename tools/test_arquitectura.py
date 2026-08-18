"""Guardas editoriales para la unidad de arquitectura de computadoras."""

import json
import re
import xml.etree.ElementTree as ET
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
    resources = assignment["content"]["resources"]
    assert len(resources) == 3
    assert all(item["url"].startswith("https://www.youtube.com/watch?v=") for item in resources)
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
    assert 7500 <= words <= 13000
    assert "90 minutos" in prose
    assert prose.count("**FACT") >= 15
    assert prose.count("**DERIVED") >= 10
    assert prose.count("**ESTIMATE") >= 5
    assert "## Siete modelos mentales" in prose
    assert prose.count("## Qué debes recordar") == 5
    assert prose.count("|---") >= 12
    assert "Ejemplo de juguete" in prose
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
        "threads-cores-simd.svg",
        "latencia-throughput.svg",
        "rutas-cpu-gpu.svg",
        "precision-parametros.svg",
        "dense-moe.svg",
        "prefill-decode.svg",
    }
    actual = {path.name for path in ASSETS.iterdir() if path.name != "CREDITOS.md"}
    assert actual == expected
    credits = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for name in expected:
        assert f"| {name} |" in credits
    prose = "\n".join(body(path) for path in PAGES)
    assert prose.count("![") >= 18
    assert prose.count("**Lectura visual:**") >= 15


def test_required_beginner_visual_topics_and_current_models_are_present():
    compute = body(PAGES[1])
    memory = body(PAGES[2])
    performance = body(PAGES[3])
    ai = body(PAGES[4])
    assert all(term in compute for term in ("threads-cores-simd.svg", "latencia-throughput.svg"))
    assert "rutas-cpu-gpu.svg" in memory
    assert all(term in memory for term in ("L1", "L2", "L3", "escala logarítmica"))
    assert all(term in performance for term in ("FLOP/byte", "foco LED", "microondas", "aire acondicionado"))
    assert all(term in ai for term in ("precision-parametros.svg", "dense-moe.svg", "prefill-decode.svg"))
    assert all(term in ai for term in ("GPT-5.6", "Claude Fable 5", "Gemini 3.6 Flash", "Kimi K3", "Qwen3.7"))
    assert "Confianza" in ai
    assert "no divulgado" in ai


def test_weight_memory_formula_defines_symbols_and_converts_bits_before_formula():
    ai = body(PAGES[4])
    section = ai.split("## La cuenta mínima de los pesos", 1)[1]
    section = section.split("## Cuantizar cambia más que capacidad", 1)[0]
    required = (
        "$N_p$",
        "número de parámetros",
        "$b$",
        "bits usados por cada parámetro",
        "$M_{pesos}$",
        "memoria total",
        "8 bits = 1 byte",
        "32 ÷ 8 = 4 bytes",
        "10 parámetros × 4 bytes = 40 bytes",
        "FP32",
        "BF16",
        "INT8",
        "INT4",
        "contenido numérico",
        "no el tamaño total",
        "objeto `float` de Python",
        "NumPy `float32`",
        "metadatos",
        "alineación",
        "buffers",
        "`sys.getsizeof`",
    )
    assert all(term in section for term in required)
    formula = section.index("$$M_{pesos}")
    assert section.index("8 bits = 1 byte") < formula
    assert section.index("10 parámetros × 4 bytes = 40 bytes") < formula


def test_latency_throughput_uses_a_traceable_numeric_task_example():
    compute = body(PAGES[1])
    section = compute.split("## Latencia y throughput no son sinónimos", 1)[1]
    section = section.split("## Puente a memoria", 1)[0]
    required = (
        "1 tarea tarda 4 segundos",
        "12 ÷ 4 = 3 tareas",
        "3 ÷ 12 = 0.25 tareas/s",
        "6 ÷ 12 = 0.5 tareas/s",
        "La latencia sigue siendo 4 segundos",
    )
    assert all(term in section for term in required)
    assert "cocina" not in section.lower()
    assert "plato" not in section.lower()

    svg = (ASSETS / "latencia-throughput.svg").read_text(encoding="utf-8")
    assert all(term in svg for term in ("4 s por tarea", "3 tareas / 12 s", "6 tareas / 12 s"))
    root = ET.parse(ASSETS / "latencia-throughput.svg").getroot()
    assert root.attrib["width"] == "720"
    assert root.attrib["height"] == "600"
    assert root.attrib["viewBox"] == "0 0 360 300"
    assert "cocina" not in svg.lower()
    assert "plato" not in svg.lower()


def test_roofline_uses_a_traceable_numeric_example_without_kitchen_analogy():
    performance = body(PAGES[3])
    roofline = performance.split("## Roofline conecta cómputo y memoria", 1)[1]
    roofline = roofline.split("## Pico, benchmark y aplicación", 1)[0]
    assert all(
        term in roofline
        for term in (
            "C[0] = A[0] + B[0]",
            "primera posición",
            "4 + 4 + 4 = **12 bytes**",
            "1,000 elementos",
            "12,000 bytes",
            "1,000 FLOP",
            "0.083 FLOP/byte",
            "100 GB/s",
            "2 TFLOPS",
            "8.3 GFLOPS",
            "elige el menor",
        )
    )
    assert all(label in roofline for label in ("Memoria", "Cómputo del chip", "Limita memoria"))
    assert "cocina" not in roofline.lower()
    assert "ejemplo de juguete" not in roofline.lower()
    assert "write-allocate" not in roofline.lower()
    assert "writeback" not in roofline.lower()
    assert "prefetch" not in roofline.lower()
    assert "multiplicación matricial" not in roofline.lower()
    assert all(
        term in roofline
        for term in (
            "1 FLOP/byte",
            "10 FLOP/byte",
            "20 FLOP/byte",
            "30 FLOP/byte",
            "meseta",
            "no significa por sí sola",
            "porcentaje del techo",
            "mismo trabajo",
        )
    )


def test_roofline_svg_is_compact_and_summarizes_without_repeating_the_arithmetic():
    performance = body(PAGES[3])
    alt = re.search(r"!\[([^]]+)]\(\.\./_assets/roofline-lite\.svg\)", performance)
    assert alt
    root = ET.parse(ASSETS / "roofline-lite.svg").getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    assert root.attrib["width"] == "640"
    assert root.attrib["height"] == "720"
    assert root.attrib["viewBox"] == "0 0 320 360"
    title = root.findtext("svg:title", namespaces=namespace)
    desc = root.findtext("svg:desc", namespaces=namespace)
    svg_text = " ".join(root.itertext())
    required = (
        "100 GB/s",
        "2 TFLOPS FP32",
        "2,000 GFLOPS",
        "0.083 FLOP/byte",
        "8.3 GFLOPS",
        "20 FLOP/byte",
    )
    assert all(term in alt.group(1) for term in required)
    assert all(term in title for term in required)
    assert all(term in desc for term in required)
    assert "12,000 bytes" not in svg_text
    assert "1,000 sumas" not in svg_text
    assert "multiplicación matricial" not in svg_text
    assert "limita memoria" in svg_text.lower()


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
