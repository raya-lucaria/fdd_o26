from decimal import Decimal
from pathlib import Path
import re
import importlib.util
import xml.etree.ElementTree as ET

import pytest
import yaml

import ai_hardware_costs as hardware_costs
from ai_hardware_costs import (
    accelerator_capex,
    accelerator_hours,
    aggregate_peaks,
    bits_to_bytes,
    gb_to_gib,
    gib_to_gb,
    installed_hbm_gb,
    installed_hbm_gib,
    kw_to_mw,
    peak_rate_tflops,
    system_capex,
    watts_to_kw,
    weight_floor_gb,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools" / "data" / "ai_hardware_costs.yaml"
PAGE = (
    ROOT
    / "course"
    / "3_arquitectura_de_computadoras"
    / "4_ai_escala_y_decision"
    / "0_index.md"
)
GENERATOR = ROOT / "tools" / "gen_ai_hardware_costs.py"
AI_SVG_NAMES = (
    "ai-aceleradores-entrenamiento.svg",
    "ai-hbm-entrenamiento.svg",
    "ai-potencia-hardware.svg",
    "ai-capex-hardware.svg",
    "ai-inferencia-capacidad.svg",
)
ALLOWED = {
    "FACT",
    "DERIVED",
    "ESTIMATE",
    "SCENARIO",
    "UNDISCLOSED_BY_CREATOR",
    "NOT_FOUND",
    "ESTIMATION_NOT_IDENTIFIABLE",
    "NOT_APPLICABLE",
}
POSITIVE = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}
NEGATIVE = {
    "UNDISCLOSED_BY_CREATOR",
    "NOT_FOUND",
    "ESTIMATION_NOT_IDENTIFIABLE",
    "NOT_APPLICABLE",
}
REQUIRED_CORPUS = {
    "announcement",
    "model_card",
    "system_card",
    "technical_paper",
    "repository_configuration",
}
REQUIRED_MODELS = {
    "GPT-3 175B",
    "BLOOM 176B",
    "PaLM 540B",
    "Llama 3.1 405B",
    "DeepSeek-V3",
    "GPT-5.6 Sol",
    "Claude Sonnet 5",
    "Gemini 3.1 Pro",
    "Kimi K3",
    "Qwen3.8-Max",
}
PRICE_BASIS_FIELDS = {
    "transaction_unit",
    "minimum_quantity",
    "price_date",
    "geography",
    "currency",
    "condition",
    "channel",
    "taxes",
    "support",
    "network",
    "storage",
    "included_components",
    "excluded_components",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_chart_generator():
    assert GENERATOR.is_file(), "falta el generador de las cinco visuales IA"
    spec = importlib.util.spec_from_file_location("gen_ai_hardware_costs", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def markdown_table_rows_after(markdown: str, heading: str) -> list[list[str]]:
    """Return data-cell rows from the first Markdown table after a heading."""
    section = markdown.split(heading, 1)[1]
    lines = section.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("|"))
    table_lines = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table_lines.append(line)
    assert len(table_lines) >= 3

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    header = cells(table_lines[0])
    rows = [cells(line) for line in table_lines[2:]]
    assert all(len(row) == len(header) for row in rows)
    return rows


def ledger_ids(cell: str) -> set[str]:
    return set(re.findall(r"`((?:H|I|M|S|T|V)_[A-Z0-9_]+)`", cell))


def immediate_table_after_image(markdown: str, filename: str) -> list[list[str]]:
    """Return only the first table before the next image or heading."""
    image_suffix = f"](../_assets/{filename})"
    assert image_suffix in markdown
    lines = markdown.split(image_suffix, 1)[1].splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("![") or line.startswith("#"):
            break
        if line.startswith("|"):
            start = index
            break
    assert start is not None, f"falta la tabla inmediata de {filename}"
    table_lines = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        table_lines.append(line)
    assert len(table_lines) >= 3, f"tabla incompleta para {filename}"

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip("|").split("|")]

    return [cells(line) for line in table_lines[2:]]


def fallback_tuples(chart_id: str, rows: list[list[str]]) -> list[tuple[str, str, str]]:
    """Normalize each chart's immediate table to label, value+unit, status."""
    columns = {
        "accelerators": (0, (1,), 2),
        "physical_hbm": (0, (1, 2), 3),
        "power": (1, (2,), 3),
        "capex": (0, (2,), 3),
        "inference_capacity": (0, (1,), 2),
    }
    label_column, value_columns, status_column = columns[chart_id]
    normalized = []
    for row in rows:
        state = row[status_column]
        match = re.match(r"\*\*([A-Z_]+)\*\*", state)
        assert match
        normalized.append(
            (
                row[label_column],
                " ".join(row[index] for index in value_columns),
                match.group(1),
            )
        )
    return normalized


EXPECTED_FALLBACK_ROWS = {
    "accelerators": [
        ("BLOOM 176B", "384", "FACT"),
        ("PaLM 540B", "6,144", "FACT"),
        ("Llama 3.1 405B", "16,384", "FACT"),
        ("DeepSeek-V3", "2,048", "FACT"),
    ],
    "physical_hbm": [
        ("BLOOM 176B", "30,720 GB", "DERIVED"),
        ("PaLM 540B", "196,608 GiB", "DERIVED"),
        ("Llama 3.1 405B", "1,310,720 GB", "DERIVED"),
        ("DeepSeek-V3", "163,840 GB", "DERIVED"),
    ],
    "power": [
        ("BLOOM 176B", "153,600 W", "DERIVED"),
        ("PaLM 540B", "1,179,648 W", "DERIVED"),
        ("Llama 3.1 405B", "11,468,800 W", "DERIVED"),
        ("DeepSeek-V3", "No identificable", "ESTIMATION_NOT_IDENTIFIABLE"),
    ],
    "capex": [
        ("accelerator-only · supuesto docente 2026", "USD 240,000", "DERIVED"),
        (
            "system-based · reposición 2026",
            "No identificable",
            "ESTIMATION_NOT_IDENTIFIABLE",
        ),
    ],
    "inference_capacity": [
        ("Pesos y metadata", "35.068693560 GB", "DERIVED"),
        ("Runtime", "4 GB", "SCENARIO"),
        ("Caché KV", "9.663676416 GB", "DERIVED"),
        ("Workspace", "4 GB", "SCENARIO"),
        ("Reserva 10 %", "5.27323699760 GB", "DERIVED"),
        ("Total presupuestado", "58.00560697360 GB", "DERIVED"),
        ("Capacidad física por shard", "80 GB", "SCENARIO"),
        ("Mínimo adquirible", "1 NVIDIA DGX H100", "SCENARIO"),
    ],
}


def test_ai_hardware_chart_metadata_conserva_orden_valores_y_estados_del_ledger():
    """Reordenar, redondear desde otra fuente o rellenar ausencias cambia evidencia."""
    generator = load_chart_generator()
    data = load_yaml(DATA)
    charts = {chart["id"]: chart for chart in generator.load_chart_metadata(DATA)}
    documented = [
        case for case in data["training_cases"]
        if case["include_in_documented_table"]
    ]
    model_names = {model["id"]: model["canonical_name"] for model in data["models"]}
    expected_names = [model_names[case["model_id"]] for case in documented]

    assert list(charts) == [
        "accelerators",
        "physical_hbm",
        "power",
        "capex",
        "inference_capacity",
    ]
    for chart_id, field in (
        ("accelerators", "accelerators_concurrent"),
        ("physical_hbm", "hbm_physical_installed"),
        ("power", "accelerator_power"),
    ):
        rows = charts[chart_id]["rows"]
        assert [row["label"] for row in rows] == expected_names
        assert [row["status"] for row in rows] == [
            case["metrics"][field]["status"] for case in documented
        ]
        assert [row["value"] for row in rows] == [
            case["metrics"][field]["value"] for case in documented
        ]
        assert [row["unit"] for row in rows] == [
            case["metrics"][field].get("unit") for case in documented
        ]

    valuation_rows = charts["capex"]["rows"]
    assert [row["id"] for row in valuation_rows] == [
        valuation["id"] for valuation in data["valuations"]
    ]
    assert [row["status"] for row in valuation_rows] == [
        data["didactic_scenarios"][0]["outputs"]["capex"]["status"],
        data["valuations"][1]["price"]["status"],
    ]


def test_ai_hardware_panels_preservan_fronteras_y_significado_fisico():
    """Mezclar parte+todo o piso+SLA produciría comparaciones falsas."""
    generator = load_chart_generator()
    data = load_yaml(DATA)
    charts = {chart["id"]: chart for chart in generator.load_chart_metadata(DATA)}

    assert charts["physical_hbm"]["panels"] == ["bytes; unidad nativa"]
    assert charts["power"]["panels"] == [row["panel"] for row in charts["power"]["rows"]]
    assert charts["capex"]["panels"] == [
        "accelerator-only · supuesto docente 2026",
        "system-based · reposición 2026",
    ]
    inference = charts["inference_capacity"]
    assert inference["scale"] == "linear"
    assert inference["claim"] == "piso de capacidad; cabe, sin SLA"
    assert inference["capacity_gb"] == 80
    assert inference["total_gb"] == "58.00560697360"
    assert inference["aggregate_system_hbm_used_as_fit_threshold"] is False
    capacity_case = data["inference_capacity_cases"][0]
    expected_capacity_keys = [
        "weights_and_metadata_gb",
        "runtime_gb",
        "kv_gb",
        "workspace_gb",
        "reserve_gb",
        "total_gb",
    ]
    assert [row["id"] for row in inference["rows"][:6]] == expected_capacity_keys
    assert [row["status"] for row in inference["rows"][:6]] == [
        capacity_case["capacity"][key]["status"] for key in expected_capacity_keys
    ]
    assert [row["value"] for row in inference["rows"][:6]] == [
        capacity_case["capacity"][key]["value"] for key in expected_capacity_keys
    ]


def test_ai_hardware_alt_desc_lectura_y_tabla_son_equivalentes():
    """La imagen debe comunicar lo mismo sin visión y sin depender del SVG."""
    generator = load_chart_generator()
    page = PAGE.read_text(encoding="utf-8")
    assets = ROOT / "course/3_arquitectura_de_computadoras/_assets"

    for chart in generator.load_chart_metadata(DATA):
        name = chart["filename"]
        assert name in AI_SVG_NAMES
        root = ET.parse(assets / name).getroot()
        desc = root.find("{http://www.w3.org/2000/svg}desc")
        assert desc is not None and desc.text == chart["alt"]
        assert f"![{chart['alt']}](../_assets/{name})" in page
        section = page.split(f"](../_assets/{name})", 1)[1]
        section = section.split("\n![", 1)[0].split("\n### ", 1)[0]
        assert "**Lectura visual:**" in section
        table = fallback_tuples(
            chart["id"], immediate_table_after_image(page, name)
        )
        expected = EXPECTED_FALLBACK_ROWS[chart["id"]]
        assert table == expected
        assert [
            (row["label"], row["fallback_value"], row["status"])
            for row in chart["rows"]
        ] == expected


def test_ai_hardware_eliminar_una_tabla_fallback_completa_falla():
    """Otra tabla posterior no debe suplir la tabla inmediata de una imagen."""
    page = PAGE.read_text(encoding="utf-8")
    name = "ai-aceleradores-entrenamiento.svg"
    suffix = f"](../_assets/{name})"
    before, after = page.split(suffix, 1)
    lines = after.splitlines()
    table_start = next(index for index, line in enumerate(lines) if line.startswith("|"))
    table_end = table_start
    while table_end < len(lines) and lines[table_end].startswith("|"):
        table_end += 1
    mutated = before + suffix + "\n".join(lines[:table_start] + lines[table_end:])

    with pytest.raises(AssertionError, match="falta la tabla inmediata"):
        immediate_table_after_image(mutated, name)


def test_ai_hardware_svg_real_conserva_orden_y_contenido_de_metadata():
    """Reagrupar unidades o cambiar un valor visible rompe el contrato del SVG."""
    generator = load_chart_generator()
    assets = ROOT / "course/3_arquitectura_de_computadoras/_assets"
    for chart in generator.load_chart_metadata(DATA):
        root = ET.parse(assets / chart["filename"]).getroot()
        actual = [
            (
                node.attrib["data-label"],
                node.attrib["data-value"],
                node.attrib["data-unit"],
                node.attrib["data-status"],
            )
            for node in root.iter()
            if node.attrib.get("data-row") == "true"
        ]
        expected = [
            (
                row["label"],
                "" if row.get("value") is None else str(row["value"]),
                str(row["unit"]),
                row["status"],
            )
            for row in chart["rows"]
            if row["status"] in POSITIVE
            and (row.get("value") is not None or "low" in row)
        ]
        assert actual == expected


def test_ai_hbm_svg_real_sigue_el_orden_del_ledger_sin_agrupar_unidades():
    """Filtrar GB y después GiB desplaza PaLM fuera del orden documental."""
    data = load_yaml(DATA)
    model_names = {model["id"]: model["canonical_name"] for model in data["models"]}
    expected = [
        model_names[case["model_id"]]
        for case in data["training_cases"]
        if case["include_in_documented_table"]
    ]
    root = ET.parse(
        ROOT
        / "course/3_arquitectura_de_computadoras/_assets"
        / "ai-hbm-entrenamiento.svg"
    ).getroot()
    actual = [
        node.attrib["data-label"]
        for node in root.iter()
        if node.attrib.get("data-status") and node.attrib.get("data-label")
    ]
    assert actual == expected


def test_training_tables_expose_ledger_ids_for_each_included_case():
    """A state/source in another row must not make a figure appear traceable."""
    data = load_yaml(DATA)
    page = PAGE.read_text(encoding="utf-8")

    documented = [
        case for case in data["training_cases"] if case["include_in_documented_table"]
    ]
    assert documented

    essential_rows = markdown_table_rows_after(
        page, "### Casos con hardware documentado"
    )
    scale_rows = markdown_table_rows_after(
        page, "#### Escala física y frontera económica"
    )
    detail_rows = markdown_table_rows_after(page, "#### Ledger visible")
    compute_rows = markdown_table_rows_after(
        page, "##### Trabajo publicado y utilización"
    )
    assert (
        len(essential_rows)
        == len(scale_rows)
        == len(detail_rows)
        == len(compute_rows)
        == len(documented)
    )

    essential_by_case = {
        case["id"]: next(
            row for row in essential_rows if case["id"] in ledger_ids(row[0])
        )
        for case in documented
    }
    scale_by_case = {
        case["id"]: next(
            row for row in scale_rows if case["id"] in ledger_ids(row[0])
        )
        for case in documented
    }
    detail_by_case = {
        case["id"]: next(
            row for row in detail_rows if case["id"] in ledger_ids(row[0])
        )
        for case in documented
    }
    compute_by_case = {
        case["id"]: next(
            row for row in compute_rows if case["id"] in ledger_ids(row[-1])
        )
        for case in documented
    }

    essential_columns = {
        "accelerators_concurrent": 1,
        "accelerator_hours": 2,
    }
    scale_columns = {
        "hbm_physical_installed": 1,
        "accelerator_power": 2,
        "attributed_training_capex": 3,
    }
    for case in documented:
        row = essential_by_case[case["id"]]
        assert ledger_ids(row[0]) == {case["id"], case["model_id"]}
        for field, column in essential_columns.items():
            cell = case["metrics"][field]
            expected_ids = set(cell.get("source_ids", [])) or {case["id"]}
            if field == "accelerators_concurrent":
                hardware = case["metrics"]["hardware_type"]
                assert f"**{hardware['status']}**" in row[column]
                expected_ids.update(hardware["source_ids"])
            assert f"**{cell['status']}**" in row[column]
            assert ledger_ids(row[column]) == expected_ids

        scale = scale_by_case[case["id"]]
        assert ledger_ids(scale[0]) == {case["id"], case["model_id"]}
        for field, column in scale_columns.items():
            cell = case["metrics"][field]
            expected_ids = set(cell.get("source_ids", [])) or {case["id"]}
            assert f"**{cell['status']}**" in scale[column]
            assert ledger_ids(scale[column]) == expected_ids

        detail = detail_by_case[case["id"]]
        assert ledger_ids(detail[0]) == {case["id"], case["model_id"]}
        parameter_sources = set(case["metrics"]["parameters_total"]["source_ids"])
        token_sources = set(case["metrics"]["training_tokens"]["source_ids"])
        active = case["metrics"]["parameters_active"]
        if active["status"] in POSITIVE:
            parameter_sources.update(active["source_ids"])
        assert ledger_ids(detail[1]) == parameter_sources | token_sources

        precision = case["metrics"]["training_precision"]
        assert f"**{precision['status']}**" in detail[2]
        assert ledger_ids(detail[2]) == set(precision["source_ids"])

        compute = compute_by_case[case["id"]]
        for field, column in {"training_compute_flop": 1, "mfu": 2}.items():
            cell = case["metrics"][field]
            expected_ids = set(cell.get("source_ids", [])) or {case["id"]}
            assert f"**{cell['status']}**" in compute[column]
            assert ledger_ids(compute[column]) == expected_ids
        assert ledger_ids(compute[-1]) == {case["id"]}


def test_training_scenario_is_unattributed_and_uses_the_ledger_valuation():
    """Attaching the didactic valuation to a model would turn a scenario into fact."""
    data = load_yaml(DATA)
    page = PAGE.read_text(encoding="utf-8")
    rows = markdown_table_rows_after(
        page, "### Escenarios equivalentes, no entrenamientos atribuidos"
    )
    valuation = next(
        item
        for item in data["valuations"]
        if item["id"] == "V_H100_30K_DIDACTIC_SCENARIO"
    )

    assert len(rows) == 1
    row = rows[0]
    assert "Sin modelo atribuido" in row[0]
    assert all("**SCENARIO**" in cell for cell in row)
    assert all(valuation["id"] in ledger_ids(cell) for cell in row)
    assert ledger_ids(row[1]) == {
        valuation["id"],
        valuation["hardware_id"],
    }
    model_names = {model["canonical_name"] for model in data["models"]}
    model_ids = {model["id"] for model in data["models"]}
    scenario_text = " ".join(row)
    assert not any(name in scenario_text for name in model_names)
    assert not ledger_ids(scenario_text) & model_ids
    assert "Thinkmate" not in scenario_text


def test_training_bibliography_links_every_primary_id_cited_in_review():
    """A visible source ID must lead students to its primary URL."""
    data = load_yaml(DATA)
    bibliography = PAGE.read_text(encoding="utf-8").split("## Fuentes", 1)[1]
    required_ids = {
        "S_BIGSCIENCE_BLOOM_CARD",
        "S_META_LLAMA31_CARD",
        "S_NVIDIA_H800_RELEASE_NOTES",
        "S_GOOGLE_GEMINI31_PAGE",
        "S_MOONSHOT_KIMI_K3_CARD",
    }

    for source_id in required_ids:
        assert data["sources"][source_id]["url"] in bibliography


def test_ledger_has_cutoff_and_cell_level_evidence():
    data = load_yaml(DATA)

    assert data["cutoff"] == "2026-08-18"
    assert {
        "sources",
        "hardware",
        "models",
        "training_cases",
        "inference_scenarios",
        "valuations",
    } <= data.keys()
    for case in data["training_cases"]:
        for field in case["metrics"].values():
            assert field["status"] in ALLOWED
            assert field.get("source_ids") or field["status"] in {
                "NOT_FOUND",
                "ESTIMATION_NOT_IDENTIFIABLE",
                "NOT_APPLICABLE",
            }


def evidence_cells(value):
    if isinstance(value, dict):
        if "status" in value:
            yield value
        for child in value.values():
            yield from evidence_cells(child)
    elif isinstance(value, list):
        for child in value:
            yield from evidence_cells(child)


def test_all_evidence_cells_resolve_sources_and_explain_absence():
    data = load_yaml(DATA)
    source_ids = set(data["sources"])

    for cell in evidence_cells(data):
        assert cell["status"] in ALLOWED
        assert set(cell.get("source_ids", [])) <= source_ids
        if cell["status"] in POSITIVE:
            assert cell.get("source_ids")
            assert cell.get("value") is not None
            assert cell.get("unit")
        elif cell["status"] == "UNDISCLOSED_BY_CREATOR":
            assert cell.get("source_ids")
            assert cell.get("value") is None
        elif cell["status"] == "NOT_FOUND":
            assert cell.get("searched_on") == data["cutoff"]
            assert cell.get("corpus_checked")
            assert all(
                reference in source_ids
                or (
                    isinstance(reference, str)
                    and reference.startswith(("https://", "http://"))
                )
                for reference in cell["corpus_checked"]
            )
            assert any(
                reference in source_ids for reference in cell["corpus_checked"]
            )
            assert cell.get("value") is None
        elif cell["status"] == "ESTIMATION_NOT_IDENTIFIABLE":
            assert cell.get("missing_observables")
            assert cell.get("value") is None
        elif cell["status"] == "NOT_APPLICABLE":
            assert cell.get("note")
            assert cell.get("value") is None


def test_minimum_corpus_and_current_model_audits_are_present():
    data = load_yaml(DATA)
    models = {model["canonical_name"]: model for model in data["models"]}

    assert REQUIRED_MODELS <= models.keys()
    for model in models.values():
        assert model["id"].startswith("M_")
        assert REQUIRED_CORPUS == model["corpus"].keys()
        assert {
            "canonical_name",
            "release_date",
            "availability",
            "region",
        } <= model["facts"].keys()


def test_documented_training_requires_same_scope_observables():
    data = load_yaml(DATA)

    for case in data["training_cases"]:
        metrics = case["metrics"]
        if not case["include_in_documented_table"]:
            continue
        assert metrics["hardware_type"]["status"] == "FACT"
        assert metrics["accelerators_concurrent"]["status"] == "FACT"
        assert metrics["accelerator_hours"]["status"] in {"FACT", "DERIVED"} or metrics[
            "duration_hours"
        ]["status"] in {"FACT", "DERIVED"}
        scope = case["scope"]
        for name in ("hardware_type", "accelerators_concurrent"):
            assert metrics[name]["scope"] == scope
        measured_time = [
            metrics[name]
            for name in ("accelerator_hours", "duration_hours")
            if metrics[name]["status"] in {"FACT", "DERIVED"}
        ]
        assert measured_time
        assert all(field["scope"] == scope for field in measured_time)


def test_closed_current_models_do_not_receive_attributed_estimates():
    data = load_yaml(DATA)
    current_closed = {
        case["model_id"]: case
        for case in data["training_cases"]
        if case["category"] == "current_closed"
    }

    assert current_closed
    for case in current_closed.values():
        assert not case["include_in_documented_table"]
        assert (
            case["metrics"]["attributed_training_capex"]["status"]
            == "ESTIMATION_NOT_IDENTIFIABLE"
        )
        assert all(
            field["status"] != "ESTIMATE" for field in case["metrics"].values()
        )


def test_valuations_declare_complete_price_basis_and_one_boundary():
    data = load_yaml(DATA)

    def basis_value(value):
        return value.get("value") if isinstance(value, dict) else value

    assert data["valuations"]
    for valuation in data["valuations"]:
        assert valuation["id"].startswith("V_")
        assert valuation["boundary"] in {"accelerator-only", "system-based"}
        assert PRICE_BASIS_FIELDS <= valuation["price_basis"].keys()
        assert valuation["price"]["unit"] == basis_value(
            valuation["price_basis"]["currency"]
        )
        assert basis_value(valuation["price_basis"]["channel"]) not in {
            "api",
            "cloud_rental",
            "accelerator_hour_rental",
        }
        if valuation["boundary"] == "accelerator-only":
            assert basis_value(valuation["price_basis"]["transaction_unit"]) in {
                "card",
                "module",
            }
        else:
            assert basis_value(valuation["price_basis"]["transaction_unit"]) in {
                "server",
                "rack",
            }
            excluded = basis_value(valuation["price_basis"]["excluded_components"])
            assert "accelerators_already_inside_system" in excluded


def test_primary_sources_are_owned_by_the_applicable_claimant():
    data = load_yaml(DATA)
    sources = data["sources"]

    def assert_support(cell, allowed_tags, allowed_owners, required_owners=()):
        referenced = [sources[source_id] for source_id in cell["source_ids"]]
        assert referenced
        assert all(source["source_class"] == "primary" for source in referenced)
        assert all(source["claim_owner"] in allowed_owners for source in referenced)
        assert all(set(source["primary_for"]) & allowed_tags for source in referenced)
        owners = {source["claim_owner"] for source in referenced}
        assert set(required_owners) <= owners

    model_claim_tags = {
        "canonical_name": {"canonical_name"},
        "release_date": {"release"},
        "availability": {"availability"},
        "service_availability": {"availability"},
        "region": {"region"},
        "parameters_total": {"parameters"},
        "parameters_active": {"parameters"},
        "open_weight_artifact": {"open_weight_artifact"},
        "artifact_release_date": {"artifact_release"},
        "artifact_identity": {"artifact_release", "repository_configuration"},
    }
    corpus_claim_tags = {
        "announcement": {"announcement_audit"},
        "model_card": {"model_card_audit"},
        "system_card": {"system_card_audit"},
        "technical_paper": {"technical_paper_audit"},
        "repository_configuration": {"repository_configuration"},
    }
    hardware_claim_tags = {
        "hbm_physical": {"hbm_physical"},
        "hbm_usable": {"hbm_usable"},
        "peak_theoretical_rate": {"peak_theoretical_rate"},
        "accelerator_power": {"accelerator_power"},
    }
    training_claim_tags = {
        "parameters_total": {"parameters"},
        "parameters_active": {"parameters"},
        "training_tokens": {"training_tokens"},
        "hardware_type": {"training_hardware"},
        "accelerators_concurrent": {"training_hardware"},
        "accelerator_hours": {"accelerator_hours", "training_duration"},
        "duration_hours": {"training_duration"},
        "reported_duration_bound": {"training_duration"},
        "training_precision": {"training_precision"},
        "training_compute_flop": {"training_compute"},
        "mfu": {"mfu"},
        "hbm_physical_installed": {"training_hardware", "hbm_physical"},
        "peak_theoretical_rate": {"training_hardware", "peak_theoretical_rate"},
        "accelerator_power": {"training_hardware", "accelerator_power"},
        "historical_acquisition_price": {"historical_acquisition_price"},
        "attributed_training_capex": {"attributed_training_capex"},
        "training_date_or_range": {"training_duration"},
    }

    for model in data["models"]:
        for name, cell in model["facts"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell, model_claim_tags[name], {"model_creator"}, {"model_creator"}
                )
        for name, cell in model["corpus"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell,
                    corpus_claim_tags[name],
                    {"model_creator"},
                    {"model_creator"},
                )

    for hardware in data["hardware"]:
        for name, cell in hardware["specs"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell,
                    hardware_claim_tags[name],
                    {"hardware_manufacturer"},
                    {"hardware_manufacturer"},
                )

    hardware_derived = {
        "hbm_physical_installed",
        "peak_theoretical_rate",
        "accelerator_power",
    }
    for case in data["training_cases"]:
        for name, cell in case["metrics"].items():
            if cell["status"] not in {"FACT", "DERIVED"}:
                continue
            if name == "historical_acquisition_price":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"seller", "purchase_record"},
                )
            elif name == "attributed_training_capex":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"seller", "purchase_record", "model_creator"},
                )
            elif name in hardware_derived and cell["status"] == "DERIVED":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"model_creator", "hardware_manufacturer"},
                    {"model_creator", "hardware_manufacturer"},
                )
            else:
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"model_creator"},
                    {"model_creator"},
                )

    for scenario in data["inference_scenarios"]:
        for cell in scenario["metrics"].values():
            if cell["status"] == "SCENARIO":
                referenced = [sources[source_id] for source_id in cell["source_ids"]]
                assert all(source["claim_owner"] == "course_design" for source in referenced)
                assert all(
                    source["source_class"] == "binding_specification"
                    for source in referenced
                )
                assert all("inference_target" in source["primary_for"] for source in referenced)

    for valuation in data["valuations"]:
        price = valuation["price"]
        if price["status"] == "FACT":
            assert_support(
                price, {"replacement_price"}, {"seller", "purchase_record"}
            )
        elif price["status"] == "SCENARIO":
            referenced = [sources[source_id] for source_id in price["source_ids"]]
            assert all(source["claim_owner"] == "course_design" for source in referenced)
            assert all("didactic_scenarios" in source["primary_for"] for source in referenced)
        basis_claim_tags = {
            "transaction_unit": {"transaction_unit"},
            "minimum_quantity": {"minimum_quantity"},
            "price_date": {"scope_rules"},
            "geography": {"geography"},
            "currency": {"currency"},
            "condition": {"condition"},
            "channel": {"channel"},
            "taxes": {"taxes"},
            "support": {"support"},
            "network": {"network"},
            "storage": {"storage"},
            "included_components": {"included_components"},
            "excluded_components": {"scope_rules"},
        }
        for name, cell in valuation["price_basis"].items():
            if not isinstance(cell, dict) or cell.get("status") not in POSITIVE:
                continue
            if cell["status"] == "FACT":
                assert_support(
                    cell,
                    basis_claim_tags[name],
                    {"seller", "purchase_record"},
                )
            elif cell["status"] == "SCENARIO":
                referenced = [sources[source_id] for source_id in cell["source_ids"]]
                assert all(
                    source["claim_owner"] == "course_design" for source in referenced
                )
                assert all(
                    source["source_class"] == "binding_specification"
                    for source in referenced
                )
                assert all(
                    set(source["primary_for"]) & basis_claim_tags[name]
                    for source in referenced
                )


def test_fact_prices_have_persistent_transaction_evidence():
    data = load_yaml(DATA)

    for valuation in data["valuations"]:
        if valuation["price"]["status"] != "FACT":
            continue
        price_sources = [
            data["sources"][source_id]
            for source_id in valuation["price"]["source_ids"]
        ]
        assert any(source.get("persistent_evidence") for source in price_sources)


def test_qwen_service_and_open_base_artifact_are_separate_models():
    data = load_yaml(DATA)
    models = {model["id"]: model for model in data["models"]}
    service = models["M_QWEN38_MAX_SERVICE"]
    artifact = models["M_QWEN38_2_4T_A95B"]
    cases = {case["model_id"]: case for case in data["training_cases"]}

    assert service["canonical_name"] == "Qwen3.8-Max"
    assert service["source_ids"] == ["S_QWEN38_ANNOUNCEMENT"]
    assert service["facts"]["availability"]["value"] == "hosted_on_QwenCloud"
    assert "open_weight_artifact" not in service["facts"]

    assert artifact["canonical_name"] == "Qwen3.8-2.4T-A95B"
    assert artifact["facts"]["availability"]["value"] == "open_weights"
    assert artifact["facts"]["release_date"]["value"] == "2026-08-12"
    assert artifact["corpus"]["model_card"]["source_ids"] == [
        "S_QWEN38_MODELSCOPE"
    ]
    assert artifact["corpus"]["repository_configuration"]["status"] == "FACT"
    assert artifact["corpus"]["repository_configuration"]["source_ids"] == [
        "S_QWEN38_MODELSCOPE"
    ]

    assert cases["M_QWEN38_MAX_SERVICE"]["category"] == "current_closed"
    assert cases["M_QWEN38_2_4T_A95B"]["category"] == "current_open"
    assert cases["M_QWEN38_2_4T_A95B"]["scope"] == (
        "Qwen3_8_2_4T_A95B_base_training"
    )


def test_unpersisted_thinkmate_configuration_has_no_unqualified_claims():
    data = load_yaml(DATA)
    valuation = next(
        item
        for item in data["valuations"]
        if item["id"] == "V_THINKMATE_QH14_H100_REPLACEMENT_20260818"
    )

    assert all(
        isinstance(cell, dict) and "status" in cell
        for cell in valuation["price_basis"].values()
    )

    for field in ("taxes", "support", "network", "storage", "included_components"):
        cell = valuation["price_basis"][field]
        assert cell["status"] == "ESTIMATION_NOT_IDENTIFIABLE"
        assert cell["value"] is None
        assert cell["missing_observables"]

    excluded = valuation["price_basis"]["excluded_components"]
    assert excluded["status"] == "SCENARIO"
    assert excluded["source_ids"] == ["S_COURSE_DESIGN"]
    assert "accelerators_already_inside_system" in excluded["value"]
    assert all("ConnectX" not in str(value) for value in valuation["price_basis"].values())

    supported = {
        "transaction_unit": "server",
        "geography": "United_States_online_storefront",
        "currency": "USD",
        "channel": "seller_online_configurator",
    }
    for field, expected in supported.items():
        cell = valuation["price_basis"][field]
        assert cell["status"] == "FACT"
        assert cell["value"] == expected
        assert cell["source_ids"] == ["S_THINKMATE_HGX_H100_CONFIGURATOR"]

    for field in ("minimum_quantity", "condition"):
        assert valuation["price_basis"][field]["status"] == (
            "ESTIMATION_NOT_IDENTIFIABLE"
        )

    assert valuation["price_basis"]["price_date"]["status"] == "SCENARIO"


def test_power_evidence_preserves_basis_and_boundary():
    data = load_yaml(DATA)
    allowed_hardware_bases = {
        "configurable_TDP",
        "maximum_power_consumption",
        "standard_TDP",
        "measured_max",
    }
    allowed_aggregate_bases = {
        "sum_of_configurable_TDP",
        "sum_of_maximum_power_consumption",
        "sum_of_standard_TDP",
        "sum_of_measured_max",
    }

    for hardware in data["hardware"]:
        assert "nominal_power" not in hardware["specs"]
        power = hardware["specs"]["accelerator_power"]
        if power["status"] in POSITIVE:
            assert power["power_basis"] in allowed_hardware_bases
            assert power["boundary"] in {"accelerator_chip", "accelerator_module"}

    for case in data["training_cases"]:
        assert "nominal_accelerator_power" not in case["metrics"]
        power = case["metrics"]["accelerator_power"]
        if power["status"] in POSITIVE:
            assert power["power_basis"] in allowed_aggregate_bases
            assert power["boundary"] == "accelerator-only"


def test_eight_accelerator_example_preserves_each_quantity_boundary():
    """A wrong multiplier would break the physical example students reconstruct."""
    assert installed_hbm_gb(8, 80) == Decimal("640")
    assert accelerator_hours(8, 24) == Decimal("192")
    assert accelerator_capex(8, 30_000) == Decimal("240000")


def test_system_capex_counts_each_component_once():
    """Adding each network component once prevents an accidental double count."""
    network = [(2, Decimal("12000")), (1, Decimal("8000"))]
    assert system_capex(
        4,
        Decimal("400000"),
        network,
        price_basis={
            "boundary": "system-based",
            "transaction_unit": "server",
            "network": "excluded",
        },
    ) == Decimal("1632000")


def test_mixed_peak_conventions_are_rejected_before_values_are_aggregated():
    """Changing precision must not produce a single comparable peak series."""
    with pytest.raises(ValueError, match="homogeneous peak convention"):
        aggregate_peaks([{"precision": "BF16"}, {"precision": "FP8"}])


def test_peak_rate_requires_complete_dense_precision_and_accumulation_convention():
    """Omitting sparsity could silently mix dense and sparse manufacturer peaks."""
    with pytest.raises(ValueError, match="sparsity"):
        peak_rate_tflops(
            8,
            Decimal("312"),
            {"precision": "BF16", "accumulation": "FP32"},
        )


def test_aggregate_peaks_rejects_different_hardware_even_when_precision_matches():
    """Per-chip peak values are only additive for homogeneous hardware."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "H100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("989.5"),
        },
    ]
    with pytest.raises(ValueError, match="homogeneous hardware"):
        aggregate_peaks(entries)


def test_aggregate_peaks_adds_only_one_homogeneous_peak_series():
    """Dropping an entry would understate a peak series with compatible conventions."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
    ]
    assert aggregate_peaks(entries) == Decimal("624")


def test_weight_floor_uses_decimal_gb_and_never_binary_gib_implicitly():
    """Treating GB as GiB changes the reported floor without a visible unit change."""
    assert weight_floor_gb(Decimal("35e9"), 8) == Decimal("35")
    assert installed_hbm_gib(8, 80) == Decimal("640")
    assert gb_to_gib(Decimal("14")) == Decimal("13.03851604461669921875")
    assert gib_to_gb(Decimal("13.03851604461669921875")) == Decimal("14")


def test_capacity_floor_keeps_components_visible():
    """Dropping quantization metadata would understate the capacity floor."""
    result = hardware_costs.inference_capacity_floor(
        parameters=Decimal("35e9"),
        bits=8,
        quant_overhead=Decimal("0.15"),
        runtime_gb=Decimal("4"),
        kv_gb=Decimal("8"),
        workspace_gb=Decimal("4"),
        reserve_fraction=Decimal("0.10"),
    )

    assert result["weights_gb"] == Decimal("35")
    assert result["quantized_weights_gb"] == Decimal("40.25")
    assert result["before_reserve_gb"] == Decimal("56.25")


def test_capacity_floor_reports_each_component_and_reserved_total():
    """Folding runtime, KV, workspace, or reserve together hides capacity drivers."""
    result = hardware_costs.inference_capacity_floor(
        parameters=Decimal("35e9"),
        bits=8,
        quant_overhead=Decimal("0.15"),
        runtime_gb=Decimal("4"),
        kv_gb=Decimal("8"),
        workspace_gb=Decimal("4"),
        reserve_fraction=Decimal("0.10"),
    )

    assert result == {
        "weights_gb": Decimal("35"),
        "quant_overhead_gb": Decimal("5.25"),
        "quantized_weights_gb": Decimal("40.25"),
        "runtime_gb": Decimal("4"),
        "kv_gb": Decimal("8"),
        "workspace_gb": Decimal("4"),
        "before_reserve_gb": Decimal("56.25"),
        "reserve_gb": Decimal("5.6250"),
        "total_gb": Decimal("61.8750"),
    }


def test_capacity_floor_rejects_a_reserve_that_is_not_a_fraction():
    """Treating 10 as 10% would inflate the physical requirement elevenfold."""
    with pytest.raises(ValueError, match="less than one"):
        hardware_costs.inference_capacity_floor(
            parameters=1,
            bits=8,
            quant_overhead=0,
            runtime_gb=0,
            kv_gb=0,
            workspace_gb=0,
            reserve_fraction=1,
        )


def test_versioned_inference_artifact_reconstructs_the_capacity_budget():
    """FP16 weights must not be mislabeled as GPTQ metadata above an 8-bit floor."""
    data = load_yaml(DATA)
    case = next(
        item
        for item in data["inference_capacity_cases"]
        if item["id"] == "I_QWEN25_32B_GPTQ_INT8_CAPACITY"
    )
    artifact = case["artifact"]
    capacity = case["capacity"]

    assert artifact["revision"]["value"] == (
        "eddc13f573fd3648cc8a4741fdf1b70e8d6fc5c1"
    )
    assert artifact["shard_count"]["value"] == 9
    assert artifact["shard_bytes"]["value"] == 35_068_693_560

    expected_components = {
        "weights_floor_gb": Decimal("32.763876352"),
        "weight_precision_differential_gb": Decimal("1.558254592"),
        "quantization_scales_gb": Decimal("0.487587840"),
        "quantization_qzeros_gb": Decimal("0.243793920"),
        "quantization_g_idx_gb": Decimal("0.014942208"),
        "safetensors_headers_gb": Decimal("0.000238648"),
    }
    for name, expected in expected_components.items():
        cell = capacity[name]
        assert Decimal(str(cell["value"])) == expected
        assert cell["source_ids"] == ["S_QWEN25_32B_GPTQ_INT8_ARTIFACT"]

    weights_gb = (
        expected_components["weights_floor_gb"]
        + expected_components["weight_precision_differential_gb"]
    )
    metadata_gb = sum(
        (
            expected_components[name]
            for name in (
                "quantization_scales_gb",
                "quantization_qzeros_gb",
                "quantization_g_idx_gb",
                "safetensors_headers_gb",
            )
        ),
        Decimal("0"),
    )
    assert weights_gb == Decimal("34.322130944")
    assert metadata_gb == Decimal("0.746562616")
    assert weights_gb + metadata_gb == Decimal("35.068693560")
    assert Decimal(str(capacity["weights_gb"]["value"])) == weights_gb
    assert Decimal(str(capacity["quantization_metadata_gb"]["value"])) == (
        metadata_gb
    )

    result = hardware_costs.inference_capacity_floor(
        parameters=Decimal(str(artifact["parameters"]["value"])),
        bits=Decimal(str(artifact["quantization_bits"]["value"])),
        quant_overhead=Decimal(str(capacity["artifact_overhead_fraction"]["value"])),
        runtime_gb=Decimal(str(capacity["runtime_gb"]["value"])),
        kv_gb=Decimal(str(capacity["kv_gb"]["value"])),
        workspace_gb=Decimal(str(capacity["workspace_gb"]["value"])),
        reserve_fraction=Decimal(str(capacity["reserve_fraction"]["value"])),
    )
    assert result["weights_gb"] == Decimal("32.763876352")
    assert result["quantized_weights_gb"] == Decimal("35.068693560")
    assert result["kv_gb"] == Decimal("9.663676416")
    assert result["total_gb"] == Decimal("58.00560697360")
    assert Decimal(str(capacity["total_gb"]["value"])) == result["total_gb"]


def test_kv_floor_is_recomputed_from_versioned_architecture_fields():
    """Changing a layer, KV head, head dimension, or dtype must change the KV floor."""
    data = load_yaml(DATA)
    case = data["inference_capacity_cases"][0]
    architecture = case["artifact"]["architecture"]
    capacity = case["capacity"]

    expected_artifact_fields = {
        "hidden_layers": 64,
        "kv_heads": 8,
        "head_dimension": 128,
    }
    for name, expected in expected_artifact_fields.items():
        cell = architecture[name]
        assert cell["value"] == expected
        assert cell["source_ids"] == ["S_QWEN25_32B_GPTQ_INT8_ARTIFACT"]

    dtype = architecture["kv_dtype"]
    assert dtype["status"] == "SCENARIO"
    assert dtype["value"] == "FP16"
    assert dtype["bytes_per_element"] == 2
    assert dtype["source_ids"] == [
        "S_COURSE_DESIGN",
        "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
    ]
    batch = capacity["kv_batch"]
    context = capacity["kv_context_tokens"]
    for cell, expected in ((batch, 16), (context, 2304)):
        assert cell["status"] == "SCENARIO"
        assert cell["value"] == expected
        assert cell["source_ids"] == ["S_COURSE_DESIGN"]

    per_layer_token_request = (
        2
        * architecture["kv_heads"]["value"]
        * architecture["head_dimension"]["value"]
        * dtype["bytes_per_element"]
    )
    kv_bytes = (
        per_layer_token_request
        * architecture["hidden_layers"]["value"]
        * context["value"]
        * batch["value"]
    )
    assert per_layer_token_request == 4096
    assert kv_bytes == 9_663_676_416
    assert capacity["kv_bytes_per_layer_token_request"]["value"] == (
        per_layer_token_request
    )
    assert Decimal(str(capacity["kv_gb"]["value"])) == (
        Decimal(kv_bytes) / Decimal("1e9")
    )
    assert capacity["kv_gb"]["source_ids"] == [
        "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
        "S_COURSE_DESIGN",
    ]


def test_inference_capacity_separates_physical_from_usable_memory():
    """A system HBM sum must not replace the per-replica/per-shard mapping."""
    data = load_yaml(DATA)
    case = data["inference_capacity_cases"][0]
    topology = case["topology"]
    mapping = topology["memory_mapping"]
    hardware = next(
        item
        for item in data["hardware"]
        if item["id"] == "H_NVIDIA_H100_SXM_80GB"
    )

    assert topology["transaction_unit"]["value"] == "system"
    assert topology["system"] == {
        "status": "FACT",
        "value": "NVIDIA_DGX_H100",
        "unit": "system_model",
        "source_ids": ["S_NVIDIA_DGX_H100_DATASHEET"],
    }
    assert topology["accelerator_hardware_id"] == {
        "status": "DERIVED",
        "value": "H_NVIDIA_H100_SXM_80GB",
        "unit": "hardware_ledger_id",
        "source_ids": [
            "S_NVIDIA_DGX_H100_DATASHEET",
            "S_NVIDIA_H100_PAGE",
        ],
    }
    assert topology["accelerators_per_system"]["value"] == 8
    assert topology["physical_hbm_per_accelerator_gb"] == {
        "status": "DERIVED",
        "value": 80,
        "unit": "GB_decimal_per_GPU",
        "source_ids": [
            "S_NVIDIA_DGX_H100_DATASHEET",
            "S_NVIDIA_H100_PAGE",
        ],
        "formula": "640 GB físicos ÷ 8 GPU; coincide con H_NVIDIA_H100_SXM_80GB",
    }
    assert hardware["specs"]["hbm_physical"]["value"] == 80
    assert hardware["specs"]["hbm_physical"]["source_ids"] == [
        "S_NVIDIA_H100_PAGE"
    ]
    assert topology["physical_hbm_gb"]["value"] == 640
    compatibility = topology["runtime_hardware_compatibility"]
    assert compatibility["status"] == "DERIVED"
    assert compatibility["value"] == (
        "Qwen_artifact_recommends_vLLM_vLLM_0_7_1_supports_GPTQ_on_Hopper_"
        "and_DGX_H100_contains_H100"
    )
    assert compatibility["source_ids"] == [
        "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
        "S_VLLM_071_QUANTIZATION_HARDWARE",
        "S_NVIDIA_DGX_H100_DATASHEET",
    ]

    assert case["capacity"]["weights_gb"]["status"] == "DERIVED"
    assert case["capacity"]["weights_gb"]["source_ids"] == [
        "S_QWEN25_32B_GPTQ_INT8_ARTIFACT"
    ]

    for field in (
        "tensor_parallel_size",
        "pipeline_parallel_size",
        "data_parallel_size",
        "replicas",
        "model_shards_per_replica",
        "active_accelerators_per_system",
    ):
        assert mapping[field]["status"] == "SCENARIO"
        assert mapping[field]["value"] == 1
        assert mapping[field]["source_ids"] == [
            "S_COURSE_DESIGN",
            "S_NVIDIA_DGX_H100_DATASHEET",
        ]
    assert mapping["physical_hbm_per_shard_gb"]["value"] == 80
    assert mapping["physical_hbm_per_replica_gb"]["value"] == 80
    assert mapping["kv_contexts_per_replica"]["value"] == 16
    assert mapping["kv_placement"]["value"] == (
        "all_16_contexts_on_the_single_H100_shard"
    )
    assert mapping["kv_placement"]["source_ids"] == [
        "S_COURSE_DESIGN",
        "S_NVIDIA_DGX_H100_DATASHEET",
    ]
    assert mapping["unused_accelerators_in_purchased_system"]["value"] == 7

    assert topology["hbm_usable_gb"]["status"] == "ESTIMATION_NOT_IDENTIFIABLE"
    assert {
        "runtime_allocator_peak",
        "driver_reserved_memory",
        "measured_shard_peak",
    } <= set(topology["hbm_usable_gb"]["missing_observables"])
    assert case["capacity_assessment"]["status"] == "SCENARIO"
    assert case["capacity_assessment"]["sla_claim"] is False
    assert case["capacity_assessment"]["budget_scope"] == (
        "one_replica_on_one_H100_shard"
    )
    assert case["capacity_assessment"]["comparison_physical_hbm_gb"] == 80
    assert case["capacity_assessment"]["aggregate_system_hbm_used_as_fit_threshold"] is (
        False
    )

    minimum = topology["minimum_purchasable_system"]
    assert minimum["value"] == "1 NVIDIA DGX H100"
    assert minimum["source_ids"] == [
        "S_COURSE_DESIGN",
        "S_NVIDIA_DGX_H100_DATASHEET",
        "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
        "S_VLLM_071_QUANTIZATION_HARDWARE",
    ]


def test_operational_capex_stays_unidentifiable_without_one_joint_measurement():
    """Separate throughput and latency runs cannot establish an SLA or CAPEX."""
    data = load_yaml(DATA)
    scenario = next(
        item
        for item in data["inference_scenarios"]
        if item["id"] == "I_PRODUCTION_DIDACTIC_TARGET"
    )
    metrics = scenario["metrics"]
    assert metrics["concurrent_requests"]["value"] == 16
    assert metrics["input_tokens_per_request"]["value"] == 2048
    assert metrics["max_output_tokens_per_request"]["value"] == 256
    assert metrics["target_output_throughput"]["value"] == 100
    assert metrics["ttft_p95_max"]["value"] == 2
    assert metrics["utilization_max"]["value"] == 70
    assert metrics["redundancy"]["value"] == "N active servers + 1 server"
    assert metrics["redundancy"]["failure_domain"] == "distinct"

    required = set(scenario["measurement_gate"]["same_configuration_fields"])
    assert required == {
        "artifact_revision",
        "runtime_version",
        "hardware_topology",
        "scheduler",
        "batch",
        "warmup",
        "input_length",
        "output_length",
        "context_length",
        "concurrency",
        "utilization",
    }
    assert scenario["measurement_gate"]["joint_output_throughput_and_ttft"] is True
    assert scenario["measurement_gate"]["allows_peak_flops_proxy"] is False
    assert metrics["joint_measurement"]["status"] == "NOT_FOUND"
    assert metrics["sla_compliance"]["status"] == "ESTIMATION_NOT_IDENTIFIABLE"
    assert metrics["active_server_count"]["status"] == (
        "ESTIMATION_NOT_IDENTIFIABLE"
    )
    assert metrics["operational_capex"]["status"] == (
        "ESTIMATION_NOT_IDENTIFIABLE"
    )


def test_inference_tables_expose_capacity_components_without_an_sla_claim():
    """Omitting a component or a gate would turn a floor into a service promise."""
    page = PAGE.read_text(encoding="utf-8")
    capacity_rows = markdown_table_rows_after(
        page, "### Inferencia de capacidad: cabe, sin SLA"
    )
    assert len(capacity_rows) == 13
    assert all(len(row) == 3 for row in capacity_rows)
    rows = {row[0]: row for row in capacity_rows}
    assert set(rows) == {
        "Artefacto y revisión",
        "Formato",
        "Pesos",
        "Escalas/metadata",
        "Runtime",
        "KV",
        "Workspace",
        "Reserva",
        "Total derivado",
        "Evaluación: cabe, sin SLA",
        "Sistema mínimo del corpus",
        "Compatibilidad",
        "HBM utilizable",
    }
    assert all(
        value in rows["Pesos"][1]
        for value in ("32.763876352 GB", "1.558254592 GB", "34.322130944 GB")
    )
    assert all(
        value in rows["Escalas/metadata"][1]
        for value in (
            "0.487587840 GB",
            "0.243793920 GB",
            "0.014942208 GB",
            "0.000238648 GB",
            "0.746562616 GB",
        )
    )
    assert "4 GB" in rows["Runtime"][1]
    assert "9.663676416 GB" in rows["KV"][1]
    assert "4 GB" in rows["Workspace"][1]
    assert "5.27323699760 GB" in rows["Reserva"][1]
    assert "58.00560697360 GB" in rows["Total derivado"][1]
    assert "54.022 GiB" in rows["Total derivado"][1]
    assert "sin SLA" in rows["Evaluación: cabe, sin SLA"][0]
    system = rows["Sistema mínimo del corpus"][1]
    assert "1 NVIDIA DGX H100" in system
    assert all(term in system for term in ("TP=1", "PP=1", "DP=1", "una réplica"))
    assert "80 GB físicos por réplica/shard" in system
    assert "16 contextos KV" in system
    assert "ESTIMATION_NOT_IDENTIFIABLE" in rows["HBM utilizable"][2]

    expected_evidence = {
        "Artefacto y revisión": {
            "I_QWEN25_32B_GPTQ_INT8_CAPACITY",
            "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
        },
        "Formato": {"S_QWEN25_32B_GPTQ_INT8_ARTIFACT"},
        "Pesos": {"S_QWEN25_32B_GPTQ_INT8_ARTIFACT"},
        "Escalas/metadata": {"S_QWEN25_32B_GPTQ_INT8_ARTIFACT"},
        "Runtime": {
            "S_COURSE_DESIGN",
            "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
            "S_VLLM_071_QUANTIZATION_HARDWARE",
        },
        "KV": {"S_COURSE_DESIGN", "S_QWEN25_32B_GPTQ_INT8_ARTIFACT"},
        "Workspace": {"S_COURSE_DESIGN"},
        "Reserva": {"S_COURSE_DESIGN", "S_QWEN25_32B_GPTQ_INT8_ARTIFACT"},
        "Total derivado": {
            "I_QWEN25_32B_GPTQ_INT8_CAPACITY",
            "S_COURSE_DESIGN",
            "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
        },
        "Evaluación: cabe, sin SLA": {
            "I_QWEN25_32B_GPTQ_INT8_CAPACITY",
            "S_COURSE_DESIGN",
        },
        "Sistema mínimo del corpus": {
            "S_COURSE_DESIGN",
            "S_NVIDIA_DGX_H100_DATASHEET",
        },
        "Compatibilidad": {
            "S_QWEN25_32B_GPTQ_INT8_ARTIFACT",
            "S_VLLM_071_QUANTIZATION_HARDWARE",
            "S_NVIDIA_DGX_H100_DATASHEET",
        },
        "HBM utilizable": {"I_QWEN25_32B_GPTQ_INT8_CAPACITY"},
    }
    assert {
        label: ledger_ids(row[2]) for label, row in rows.items()
    } == expected_evidence

    operational_rows = markdown_table_rows_after(
        page, "### Inferencia operacional: el SLA requiere una medición conjunta"
    )
    assert len(operational_rows) == 1
    operational = " ".join(operational_rows[0])
    operational_section = page.split(
        "### Inferencia operacional: el SLA requiere una medición conjunta", 1
    )[1].split("## Guía de decisión", 1)[0]
    assert "16" in operational_section
    assert "2,048" in operational_section
    assert "256" in operational_section
    assert "100 output tokens/s" in operational_section
    assert "TTFT p95 ≤ 2 s" in operational_section
    assert "≤ 70 %" in operational_section
    assert "N activos + 1" in operational
    assert operational.count("ESTIMATION_NOT_IDENTIFIABLE") >= 3


def test_unit_conversions_keep_power_energy_bits_and_accelerator_time_distinct():
    """Changing a divisor or labeling accelerator-hours as energy is a category error."""
    assert watts_to_kw(1000) == Decimal("1")
    assert kw_to_mw(1000) == Decimal("1")
    assert bits_to_bytes(32) == Decimal("4")
    with pytest.raises(ValueError, match="accelerator-hours are not kWh"):
        accelerator_hours(8, 24, unit="kWh")


def test_capex_boundaries_reject_a_system_price_as_an_accelerator_price():
    """Adding a server price under accelerator-only would double count its GPUs."""
    with pytest.raises(ValueError, match="accelerator-only"):
        accelerator_capex(
            8,
            Decimal("30000"),
            price_basis={"boundary": "system-based", "transaction_unit": "server"},
        )


def test_system_boundary_requires_network_outside_the_system_price():
    """A network item already included in a server price must not be added again."""
    with pytest.raises(ValueError, match="network_parts"):
        system_capex(
            1,
            Decimal("400000"),
            [(1, Decimal("12000"))],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network_included": True,
            },
        )


def test_negative_quantities_and_prices_are_rejected():
    """A negative accelerator, HBM, or price would make a physical total nonsensical."""
    with pytest.raises(ValueError, match="non-negative"):
        installed_hbm_gb(-1, 80)
    with pytest.raises(ValueError, match="non-negative"):
        accelerator_capex(1, Decimal("-1"))
    with pytest.raises(ValueError, match="non-negative"):
        weight_floor_gb(Decimal("1e9"), -8)


def test_system_capex_reads_canonical_network_basis_before_adding_parts():
    """Ignoring the ledger's network field would double count included network."""
    with pytest.raises(ValueError, match="network_parts"):
        system_capex(
            1,
            Decimal("400000"),
            [(1, Decimal("12000"))],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network": "included",
            },
        )


def test_system_capex_requires_a_network_basis_when_adding_network_parts():
    """Unknown network inclusion cannot establish the system CAPEX boundary."""
    with pytest.raises(ValueError, match="price_basis"):
        system_capex(1, Decimal("400000"), [(1, Decimal("12000"))])


def test_aggregate_peaks_normalizes_convention_strings_before_comparing():
    """Whitespace alone must not split an otherwise homogeneous peak series."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": " BF16 ",
            "sparsity": " dense ",
            "accumulation": " FP32 ",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
    ]
    assert aggregate_peaks(entries) == Decimal("624")


def test_aggregate_peaks_rejects_unhashable_convention_values_as_value_errors():
    """A malformed convention must not escape as a set/hash implementation error."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": ["BF16"],
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        }
    ]
    with pytest.raises(ValueError, match="peak convention requires precision"):
        aggregate_peaks(entries)


def test_peak_rate_calculates_one_complete_theoretical_rate_series():
    """Using a rate as if it were work would require a different, forbidden calculation."""
    assert peak_rate_tflops(
        8,
        Decimal("312"),
        {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
    ) == Decimal("2496")


@pytest.mark.parametrize(
    ("call", "invalid"),
    [
        (lambda value: installed_hbm_gb(1, value), 0.5),
        (
            lambda value: peak_rate_tflops(
                1,
                value,
                {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
            ),
            0.5,
        ),
        (
            lambda value: aggregate_peaks(
                [
                    {
                        "hardware_id": "A100-SXM-80GB",
                        "precision": "BF16",
                        "sparsity": "dense",
                        "accumulation": "FP32",
                        "tflops": value,
                    }
                ]
            ),
            0.5,
        ),
        (lambda value: accelerator_hours(1, value), 0.5),
        (lambda value: accelerator_capex(1, value), 0.5),
        (
            lambda value: system_capex(
                1,
                value,
                [],
                price_basis={
                    "boundary": "system-based",
                    "transaction_unit": "server",
                    "network": "excluded",
                },
            ),
            0.5,
        ),
        (lambda value: weight_floor_gb(value, 8), 0.5),
    ],
)
def test_calculation_interfaces_reject_binary_floats(call, invalid):
    """Accepting a float would silently inject binary rounding into a Decimal ledger."""
    with pytest.raises(TypeError, match="not float"):
        call(invalid)


@pytest.mark.parametrize("invalid", [Decimal("NaN"), Decimal("Infinity")])
@pytest.mark.parametrize(
    "call",
    [
        lambda value: installed_hbm_gb(1, value),
        lambda value: peak_rate_tflops(
            1,
            value,
            {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
        ),
        lambda value: aggregate_peaks(
            [
                {
                    "hardware_id": "A100-SXM-80GB",
                    "precision": "BF16",
                    "sparsity": "dense",
                    "accumulation": "FP32",
                    "tflops": value,
                }
            ]
        ),
        lambda value: accelerator_hours(1, value),
        lambda value: accelerator_capex(1, value),
        lambda value: system_capex(
            1,
            value,
            [],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network": "excluded",
            },
        ),
        lambda value: weight_floor_gb(value, 8),
        lambda value: bits_to_bytes(value),
    ],
)
def test_decimal_interfaces_reject_non_finite_values(call, invalid):
    """NaN and infinity cannot represent a physical quantity or price."""
    with pytest.raises(ValueError, match="finite"):
        call(invalid)
