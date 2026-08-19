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
AI_PAGE = UNIT / "4_ai_escala_y_decision/0_index.md"
DASHBOARD_ANNEX = (
    UNIT
    / "4_ai_escala_y_decision/1_evidencia_dashboard/0_index.md"
)
AI_LEDGER = ROOT / "tools/data/ai_hardware_costs.yaml"
DASHBOARD_ASSETS = {
    "ai-training-parameters.svg",
    "ai-training-flop.svg",
    "ai-training-accelerators.svg",
    "ai-training-power.svg",
    "ai-training-replacement-value.svg",
    "ai-inference-memory.svg",
    "ai-inference-accelerators.svg",
    "ai-inference-power.svg",
    "ai-inference-capex.svg",
    "ai-inference-parameters.svg",
    "ai-pareto-training.svg",
    "ai-pareto-inference.svg",
}
RETIRED_DASHBOARD_ASSETS = {
    "ai-aceleradores-entrenamiento.svg",
    "ai-hbm-entrenamiento.svg",
    "ai-potencia-hardware.svg",
    "ai-capex-hardware.svg",
    "ai-inferencia-capacidad.svg",
}
ASSIGNMENT = (
    ROOT
    / "course/3_arquitectura_de_computadoras/_official/assignments/1_videos_hardware.yaml"
)
TERMINAL_ASSIGNMENT = (
    ROOT
    / "course/3_arquitectura_de_computadoras/_official/assignments/2_videos_terminal.yaml"
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


def test_terminal_videos_are_structured_and_due_august_20():
    """Catches an incomplete, reordered, or unstructured August 20 assignment."""
    assignment = load_yaml(TERMINAL_ASSIGNMENT)
    content = assignment["content"]
    resources = content["resources"]
    expected_resources = [
        {
            "title": "Registers and RAM: Crash Course Computer Science #6",
            "url": "https://www.youtube.com/watch?v=fpnE6UAfbtU",
            "note": "Distingue los registros de la RAM y su papel durante la ejecución.",
        },
        {
            "title": "The Central Processing Unit (CPU): Crash Course Computer Science #7",
            "url": "https://www.youtube.com/watch?v=FZGugFqdr60",
            "note": "Explica cómo la CPU ejecuta instrucciones y coordina sus componentes.",
        },
        {
            "title": "Operating Systems: Crash Course Computer Science #18",
            "url": "https://www.youtube.com/watch?v=26QPDBe-NB8",
            "note": "Presenta al sistema operativo como intermediario entre programas y hardware.",
        },
        {
            "title": "Memory & Storage: Crash Course Computer Science #19",
            "url": "https://www.youtube.com/watch?v=TQCr9RV7twk",
            "note": "Relaciona memoria temporal, almacenamiento persistente y sus diferencias.",
        },
        {
            "title": "Files & File Systems: Crash Course Computer Science #20",
            "url": "https://www.youtube.com/watch?v=KN8YgJnShPM",
            "note": "Muestra cómo el sistema de archivos organiza y localiza los datos guardados.",
        },
    ]

    assert assignment["id"] == "videos-terminal"
    assert content["due"] == "2026-08-20"
    assert isinstance(resources, list)
    assert resources == expected_resources
    expected_urls = [resource["url"] for resource in expected_resources]
    assert len(resources) == len(set(resource["url"] for resource in resources)) == 5
    assert not any(url in content["instructions"] for url in expected_urls)


def test_august_18_hardware_assignment_is_preserved():
    """Catches replacing the existing August 18 preparation task."""
    assignment = load_yaml(ASSIGNMENT)
    expected_assignment = {
        "id": "videos-hardware",
        "type": "assignment",
        "authority": "official",
        "content": {
            "title": "Ver tres videos: cómo funciona una computadora",
            "instructions": (
                "Ve estos tres videos antes de la clase del 18 de agosto. Juntos explican "
                "qué hay dentro de una computadora y por qué la memoria se organiza en capas."
            ),
            "resources": [
                {
                    "title": "¿Cómo funciona un PC y qué hace cada pieza?",
                    "url": "https://www.youtube.com/watch?v=0zkX6nlpiSk",
                    "note": "Panorama de los componentes principales.",
                },
                {
                    "title": "Introduction to the Memory Hierarchy",
                    "url": "https://www.youtube.com/watch?v=JogSnkvENr0",
                    "note": "Este video está en inglés.",
                },
                {
                    "title": "¿Por qué tantas memorias?",
                    "url": "https://www.youtube.com/watch?v=IwUq0RiUank",
                    "note": "Jerarquía, capacidad y velocidad.",
                },
            ],
            "due": "2026-08-18",
            "points": 0,
            "status": "published",
            "tags": ["hardware", "memoria", "arquitectura", "preparacion"],
        },
    }
    assert assignment == expected_assignment


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
    # La lección de costos declara ahora una ruta principal de 50–55 minutos;
    # el techo conserva una unidad escaneable sin fingir que cabe en 25 minutos.
    assert 7500 <= words <= 13500
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
        "ai-aceleradores-entrenamiento.svg",
        "ai-hbm-entrenamiento.svg",
        "ai-potencia-hardware.svg",
        "ai-capex-hardware.svg",
        "ai-inferencia-capacidad.svg",
        "ai-training-parameters.svg",
        "ai-training-flop.svg",
        "ai-training-accelerators.svg",
        "ai-training-power.svg",
        "ai-training-replacement-value.svg",
        "ai-inference-memory.svg",
        "ai-inference-accelerators.svg",
        "ai-inference-power.svg",
        "ai-inference-capex.svg",
        "ai-inference-parameters.svg",
        "ai-pareto-training.svg",
        "ai-pareto-inference.svg",
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
    assert all(
        term in ai
        for term in (
            "GPT-5.6 Sol",
            "Claude Sonnet 5",
            "Gemini 3.1 Pro",
            "Kimi K3",
            "Qwen3.8-Max",
            "Qwen3.8-2.4T-A95B",
        )
    )
    assert "Confianza" in ai
    assert "no divulgado" in ai.lower()


def dashboard_section() -> str:
    ai = body(AI_PAGE)
    return ai.split("## Dashboard: modelos, hardware y costo", 1)[1].split(
        "## Guía de decisión", 1
    )[0]


def visible_words(markdown: str) -> list[str]:
    without_images = re.sub(r"\[?!\[[^]]*]\([^)]+\)\]?\([^)]+\)?", "", markdown)
    without_markup = re.sub(r"[`*_#>|]", " ", without_images)
    return re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ./+−-]+\b", without_markup)


def test_dashboard_main_route_is_short_visual_and_model_rich():
    section = dashboard_section()
    assert 900 <= len(visible_words(section)) <= 1400
    assert {name for name in DASHBOARD_ASSETS if name in section} == DASHBOARD_ASSETS
    assert "[[evidencia-dashboard-ia]]" in section
    assert "data-source-ids" not in section
    assert not re.search(r"\b(?:S|DM|T|V)_[A-Z0-9_]{4,}\b", section)
    assert all(name not in section for name in RETIRED_DASHBOARD_ASSETS)


def test_dashboard_model_cards_expose_each_model_boundary_without_ids():
    section = dashboard_section()
    models = load_yaml(AI_LEDGER)["dashboard_models"]
    cards = section.split("#### Los 39 modelos, por ficha", 1)[1].split(
        "### Entrenamiento a través del tiempo", 1
    )[0]
    assert cards.count("\n| **") == 39
    for model in models:
        openness = "abierto" if model["availability"] == "open_weights" else "cerrado"
        architecture = model["architecture"].get("value") or "no publicado"
        training = (
            "cifra"
            if any(
                model["metrics"][key]["status"] in {"FACT", "DERIVED", "ESTIMATE"}
                for key in ("training_flop", "accelerators_concurrent", "accelerator_hours")
            )
            else "no publicado"
        )
        inference = (
            "artefacto"
            if model["metrics"]["artifact_bytes"]["status"] == "FACT"
            else "piso BF16"
            if model["metrics"]["weight_floor_bf16"]["status"] in {"FACT", "DERIVED", "ESTIMATE"}
            else "no identificable"
        )
        expected = (
            f"| **{model['canonical_name']} · {model['year']['value']}** | "
            f"{openness} · {architecture} · E: {training} · I: {inference} |"
        )
        assert expected in cards
    for heading in ("Google", "OpenAI y Anthropic", "Meta y BigScience", "Qwen", "DeepSeek y Mistral", "xAI y Moonshot"):
        assert f"##### {heading}" in cards


def test_dashboard_inference_cards_distinguish_artifact_floor_and_absence():
    section = dashboard_section()
    models = load_yaml(AI_LEDGER)["dashboard_models"]
    for model in models:
        artifact = model["metrics"]["artifact_bytes"]["status"] == "FACT"
        floor = model["metrics"]["weight_floor_bf16"]["status"] in {"FACT", "DERIVED", "ESTIMATE"}
        expected = "artefacto" if artifact else "piso BF16" if floor else "no identificable"
        row = next(line for line in section.splitlines() if f"**{model['canonical_name']} ·" in line)
        assert f"I: {expected}" in row


def test_dashboard_main_route_has_teaching_order_and_plain_language_boundaries():
    section = dashboard_section()
    headings = (
        "### En 30 segundos",
        "### Cómo leer el dashboard",
        "### Entrenamiento a través del tiempo",
        "### Inferencia local a través del tiempo",
        "### Pareto: mejorar una cosa sin empeorar la otra",
        "### Qué sí y qué no puedes concluir",
        "### Recapitulación del dashboard",
    )
    positions = [section.index(heading) for heading in headings]
    assert positions == sorted(positions)
    required = (
        "FLOP es trabajo",
        "FLOP/s es una tasa",
        "parámetros totales",
        "parámetros activos",
        "piso",
        "no es un servidor",
        "TDP no es potencia de pared",
        "no es el costo real",
        "ECI no es IQ",
        "no publicado",
    )
    assert all(term in section for term in required)


def test_dashboard_main_route_is_mobile_scannable():
    section = dashboard_section()
    lines = section.splitlines()
    wide_headers = []
    for index, line in enumerate(lines[:-1]):
        if not line.startswith("|") or not lines[index + 1].startswith("|---"):
            continue
        columns = len(line.strip().strip("|").split("|"))
        if columns > 2:
            wide_headers.append((line, columns))
    assert not wide_headers, wide_headers
    for paragraph in re.split(r"\n\s*\n", section):
        if not paragraph.startswith(("|", "-", "1.", "2.", "3.", "4.", "5.", "![", ">")):
            assert len(paragraph.split()) <= 75


def test_dashboard_visuals_render_inline_instead_of_thumbnail_inspector():
    section = dashboard_section()
    for name in DASHBOARD_ASSETS:
        pattern = rf"\[!\[[^]]+]\(\.\./_assets/{re.escape(name)}\)\]\(\.\./_assets/{re.escape(name)}\)"
        assert re.search(pattern, section), name


def test_dashboard_annex_preserves_complete_evidence():
    assert DASHBOARD_ANNEX.is_file()
    annex = body(DASHBOARD_ANNEX)
    ledger = load_yaml(AI_LEDGER)
    models = ledger["dashboard_models"]
    assert len(models) == 39
    for model in models:
        assert model["id"] in annex
        assert model["canonical_name"] in annex
    required = (
        "Metodología de las series",
        "Pisos de precisión",
        "Metodología de frontera de Pareto",
        "Frontera segura",
        "Frontera posible",
        "Corpus negativo",
        "Snapshot ECI",
        "UNDISCLOSED_BY_CREATOR",
        "ESTIMATION_NOT_IDENTIFIABLE",
        "Fórmula",
        "Fuentes",
    )
    assert all(term in annex for term in required)
    assert "id: evidencia-dashboard-ia" in DASHBOARD_ANNEX.read_text(encoding="utf-8")
    assert "\n+##" not in annex
    assert "## Tablas reconstruibles de las doce visuales" in annex


def test_dashboard_annex_reproduces_all_546_metric_cells_exactly():
    annex = body(DASHBOARD_ANNEX)
    models = load_yaml(AI_LEDGER)["dashboard_models"]
    metric_names = (
        "year", "architecture", "parameters_total", "parameters_active",
        "training_tokens", "training_flop", "accelerators_concurrent",
        "accelerator_hours", "accelerator_power_basis", "training_date",
        "artifact_revision", "artifact_bytes", "weight_floor_bf16",
        "weight_floor_fp8", "weight_floor_int8", "weight_floor_int4",
    )
    # Architecture and year are identity cells; the remaining 14 are metrics.
    assert sum(len(model["metrics"]) for model in models) == 546
    for model in models:
        section = annex.split(f"### {model['canonical_name']} — `{model['id']}`", 1)[1]
        section = section.split("\n### ", 1)[0]
        cells = {"year": model["year"], "architecture": model["architecture"], **model["metrics"]}
        for name in metric_names:
            cell = cells[name]
            value = "—" if cell.get("value") is None else str(cell["value"])
            unit = f" {cell['unit']}" if cell.get("unit") else ""
            assert f"- **{name}:** `{cell['status']}` · {value}{unit}" in section
            assert f"**source_ids:** {', '.join(cell['source_ids'])}" in section
            if cell.get("formula"):
                assert f"**formula:** {cell['formula']}" in section
            for key, value in cell.items():
                if key in {"status", "value", "unit", "source_ids"}:
                    continue
                rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value).lower() if isinstance(value, bool) else str(value)
                assert f"**{key}:** {rendered}" in section, (model["id"], name, key)


def test_dashboard_annex_uses_vertical_records_not_a_wide_ledger():
    annex = body(DASHBOARD_ANNEX)
    assert "<br>" not in annex
    records = annex.split("## Registros verticales por modelo", 1)[1].split(
        "## Corpus negativo", 1
    )[0]
    assert "| Métrica |" not in records
    assert "- **parameters_total:**" in records
    for index, line in enumerate(annex.splitlines()[:-1]):
        if line.startswith("|") and annex.splitlines()[index + 1].startswith("|---"):
            assert len(line.strip().strip("|").split("|")) <= 3


def test_dashboard_source_catalog_lives_only_in_annex():
    main = body(AI_PAGE)
    annex = body(DASHBOARD_ANNEX)
    dashboard_only_sources = (
        "openai.com/index/previewing-gpt-5-6-sol",
        "anthropic.com/news/claude-sonnet-5",
        "qwen.ai/blog?id=qwen3.8",
        "epoch.ai/data/eci_scores.csv",
    )
    assert all(source not in main for source in dashboard_only_sources)
    assert all(source in annex for source in dashboard_only_sources)


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
