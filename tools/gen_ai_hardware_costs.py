"""Genera cinco SVG accesibles desde el ledger de hardware de IA.

El YAML conserva evidencia y orden; ``ai_hardware_costs`` valida la cuenta de
capacidad. Este archivo decide únicamente la presentación. Los SVG generados
no se editan a mano.
"""

from decimal import Decimal
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

try:
    from ai_hardware_costs import inference_capacity_floor
except ModuleNotFoundError:  # Importado como ``tools.gen_ai_hardware_costs``.
    from tools.ai_hardware_costs import inference_capacity_floor


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "tools/data/ai_hardware_costs.yaml"
ASSETS_DIR = ROOT / "course/3_arquitectura_de_computadoras/_assets"
SVG_FILENAMES = (
    "ai-aceleradores-entrenamiento.svg",
    "ai-hbm-entrenamiento.svg",
    "ai-potencia-hardware.svg",
    "ai-capex-hardware.svg",
    "ai-inferencia-capacidad.svg",
)

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

WIDTH = 360
FONT = "system-ui, -apple-system, Segoe UI, sans-serif"
BG = "#0b0f12"
PANEL = "#141b20"
TEXT = "#f3f7f3"
MUTED = "#b7c5bb"
GRID = "#52645a"
FACT = "#6fd8e8"
DERIVED = "#7ef29d"
ESTIMATE = "#ffc857"
SCENARIO = "#c9a7ff"
ACCENT = "#ff9f6b"
POSITIVE = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}
SCALE_NOTE = "Igual distancia representa multiplicación."


def _tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def _decimal(value) -> Decimal:
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(value)


def log_position(value, minimum, maximum, start, end) -> float:
    """Map a positive value to a logarithmic horizontal coordinate."""
    values = tuple(float(item) for item in (value, minimum, maximum))
    if any(item <= 0 for item in values):
        raise ValueError("logarithmic values must be positive")
    value_f, minimum_f, maximum_f = values
    if maximum_f <= minimum_f or not minimum_f <= value_f <= maximum_f:
        raise ValueError("value must lie inside a positive increasing domain")
    fraction = math.log10(value_f / minimum_f) / math.log10(
        maximum_f / minimum_f
    )
    return float(start) + fraction * (float(end) - float(start))


def _trim_decimal(value: Decimal, places: int = 2) -> str:
    quant = Decimal(1).scaleb(-places)
    text = f"{value.quantize(quant):f}".rstrip("0").rstrip(".")
    return text or "0"


def format_si(value, unit: str) -> str:
    """Format ledger magnitudes without changing their numeric value."""
    number = _decimal(value)
    if unit == "USD":
        return f"USD {number:,.0f}"
    if unit == "W":
        if number >= Decimal("1000000"):
            return f"{_trim_decimal(number / Decimal('1000000'))} MW"
        if number >= Decimal("1000"):
            return f"{_trim_decimal(number / Decimal('1000'))} kW"
        return f"{_trim_decimal(number)} W"
    return f"{number:,.0f} {unit}"


def marker_for_status(status: str) -> str:
    """Return a shape name so status never depends on color alone."""
    markers = {
        "FACT": "circle",
        "DERIVED": "square",
        "ESTIMATE": "triangle",
        "SCENARIO": "diamond",
    }
    if status not in markers:
        raise ValueError(f"status {status!r} is not plottable")
    return markers[status]


def svg_header(width: int, height: int, title: str, desc: str) -> ET.Element:
    """Create an accessible, responsive SVG root with explicit title and desc."""
    root = ET.Element(
        _tag("svg"),
        {
            "width": str(width),
            "height": str(height),
            "viewBox": f"0 0 {width} {height}",
            "role": "img",
            "aria-labelledby": "title desc",
            "style": "max-width:100%;height:auto",
        },
    )
    ET.SubElement(root, _tag("title"), {"id": "title"}).text = title
    ET.SubElement(root, _tag("desc"), {"id": "desc"}).text = desc
    ET.SubElement(
        root,
        _tag("rect"),
        {
            "x": "0",
            "y": "0",
            "width": str(width),
            "height": str(height),
            "rx": "18",
            "fill": BG,
        },
    )
    return root


def _text(
    root: ET.Element,
    x: float,
    y: float,
    content: str,
    *,
    size: int = 18,
    fill: str = TEXT,
    weight: str = "400",
    anchor: str = "start",
) -> ET.Element:
    node = ET.SubElement(
        root,
        _tag("text"),
        {
            "x": f"{x:g}",
            "y": f"{y:g}",
            "fill": fill,
            "font-family": FONT,
            "font-size": str(size),
            "font-weight": weight,
            "text-anchor": anchor,
        },
    )
    node.text = content
    return node


def _line(
    root: ET.Element,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    color: str = GRID,
    width: float = 1.5,
    dash: str | None = None,
) -> None:
    attrs = {
        "x1": f"{x1:g}",
        "y1": f"{y1:g}",
        "x2": f"{x2:g}",
        "y2": f"{y2:g}",
        "stroke": color,
        "stroke-width": f"{width:g}",
    }
    if dash:
        attrs["stroke-dasharray"] = dash
    ET.SubElement(root, _tag("line"), attrs)


def _panel(
    root: ET.Element,
    y: float,
    height: float,
    label: str | tuple[str, ...],
) -> None:
    ET.SubElement(
        root,
        _tag("rect"),
        {
            "x": "12",
            "y": f"{y:g}",
            "width": "336",
            "height": f"{height:g}",
            "rx": "13",
            "fill": PANEL,
            "stroke": GRID,
            "stroke-width": "1",
        },
    )
    lines = (label,) if isinstance(label, str) else label
    for index, line in enumerate(lines):
        _text(
            root,
            24,
            y + 25 + index * 24,
            line,
            size=18,
            fill=MUTED,
            weight="700",
        )


def _status_color(status: str) -> str:
    return {
        "FACT": FACT,
        "DERIVED": DERIVED,
        "ESTIMATE": ESTIMATE,
        "SCENARIO": SCENARIO,
    }[status]


def _marker(
    root: ET.Element,
    x: float,
    y: float,
    status: str,
    label: str,
    *,
    size: float = 8,
) -> None:
    marker = marker_for_status(status)
    common = {
        "fill": _status_color(status),
        "stroke": BG,
        "stroke-width": "2",
        "data-status": status,
        "data-marker": marker,
        "data-label": label,
    }
    if marker == "circle":
        ET.SubElement(
            root, _tag("circle"), {**common, "cx": f"{x:g}", "cy": f"{y:g}", "r": f"{size:g}"}
        )
    elif marker == "square":
        ET.SubElement(
            root,
            _tag("rect"),
            {
                **common,
                "x": f"{x - size:g}",
                "y": f"{y - size:g}",
                "width": f"{size * 2:g}",
                "height": f"{size * 2:g}",
                "rx": "1",
            },
        )
    elif marker == "diamond":
        ET.SubElement(
            root,
            _tag("polygon"),
            {
                **common,
                "points": (
                    f"{x:g},{y - size:g} {x + size:g},{y:g} "
                    f"{x:g},{y + size:g} {x - size:g},{y:g}"
                ),
            },
        )
    else:
        ET.SubElement(
            root,
            _tag("polygon"),
            {
                **common,
                "points": (
                    f"{x:g},{y - size:g} {x + size:g},{y + size:g} "
                    f"{x - size:g},{y + size:g}"
                ),
            },
        )


def _heading(root: ET.Element, title: str, subtitle: str) -> None:
    _text(root, 18, 31, title, size=21, weight="750")
    _text(root, 18, 57, subtitle, size=18, fill=MUTED)


def _tick_label(value: int) -> str:
    superscripts = str(int(round(math.log10(value)))).translate(
        str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
    )
    return f"10{superscripts}"


def _log_axis(
    root: ET.Element,
    ticks: list[int],
    top: float,
    bottom: float,
    axis_y: float,
) -> None:
    start, end = 36, 324
    for tick in ticks:
        x = log_position(tick, ticks[0], ticks[-1], start, end)
        _line(root, x, top, x, bottom, color=GRID, width=1, dash="3 5")
        _line(root, x, axis_y - 4, x, axis_y + 4, color=MUTED)
        _text(root, x, axis_y + 24, _tick_label(tick), fill=MUTED, anchor="middle")
    _line(root, start, axis_y, end, axis_y, color=MUTED)


def _plot_log_row(
    root: ET.Element,
    row: dict,
    y: float,
    ticks: list[int],
) -> None:
    _text(root, 24, y, row["label"], weight="650")
    x = log_position(row["value"], ticks[0], ticks[-1], 36, 324)
    _text(
        root,
        24,
        y + 23,
        f"{row['display']} [{row['status']}]",
        fill=_status_color(row["status"]),
        weight="650",
    )
    marker_y = y + 48
    _marker(root, x, marker_y, row["status"], row["label"])


def _scale_note(root: ET.Element, y: float) -> None:
    group = ET.SubElement(root, _tag("g"), {"aria-label": SCALE_NOTE})
    _text(group, 18, y, "Igual distancia representa", fill=MUTED)
    _text(group, 18, y + 22, "multiplicación.", fill=MUTED)


def _missing_status(root: ET.Element, x: float, y: float, status: str) -> None:
    """Render the long absence state on two lines, retaining its full label."""
    if status != "ESTIMATION_NOT_IDENTIFIABLE":
        raise ValueError("only the long non-identifiable state uses this helper")
    group = ET.SubElement(root, _tag("g"), {"aria-label": f"[{status}]"})
    _text(group, x, y, "[ESTIMATION_NOT_", fill=MUTED)
    _text(group, x, y + 24, "IDENTIFIABLE]", fill=MUTED)


def _load_data(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _training_rows(data: dict, field: str) -> list[dict]:
    model_names = {model["id"]: model["canonical_name"] for model in data["models"]}
    rows = []
    for case in data["training_cases"]:
        if not case["include_in_documented_table"]:
            continue
        cell = case["metrics"][field]
        row = {
            "id": case["id"],
            "label": model_names[case["model_id"]],
            "status": cell["status"],
            "value": cell.get("value"),
            "unit": cell.get("unit"),
            "source_ids": list(cell.get("source_ids", [])),
        }
        rows.append(row)
    return rows


def _plotted(rows: list[dict]) -> list[dict]:
    return [
        row for row in rows
        if row["status"] in POSITIVE and row["value"] is not None
    ]


def _status_sequence(points: list[dict]) -> list[str]:
    return list(dict.fromkeys(point["status"] for point in points))


def _inference_rows(case: dict) -> list[dict]:
    labels = {
        "weights_and_metadata_gb": "Pesos y metadata",
        "runtime_gb": "Runtime",
        "kv_gb": "Caché KV",
        "workspace_gb": "Workspace",
        "reserve_gb": "Reserva 10 %",
        "total_gb": "Total presupuestado",
    }
    rows = []
    for key in labels:
        cell = case["capacity"][key]
        rows.append(
            {
                "id": key,
                "label": labels[key],
                "status": cell["status"],
                "value": cell["value"],
                "unit": cell["unit"],
                "source_ids": list(cell["source_ids"]),
                "display": f"{_trim_decimal(_decimal(cell['value']), 3)} GB",
            }
        )
    shard = case["topology"]["memory_mapping"]["physical_hbm_per_shard_gb"]
    rows.append(
        {
            "id": "physical_hbm_per_shard_gb",
            "label": "Capacidad física por shard",
            "status": shard["status"],
            "value": shard["value"],
            "unit": shard["unit"],
            "source_ids": list(shard["source_ids"]),
            "display": f"{shard['value']} GB físicos",
        }
    )
    minimum = case["topology"]["minimum_purchasable_system"]
    rows.append(
        {
            "id": "minimum_purchasable_system",
            "label": "Mínimo adquirible",
            "status": minimum["status"],
            "value": minimum["value"],
            "unit": minimum["unit"],
            "source_ids": list(minimum["source_ids"]),
            "display": minimum["value"],
        }
    )
    return rows


def _validate_inference_with_motor(case: dict) -> None:
    artifact = case["artifact"]
    capacity = case["capacity"]
    result = inference_capacity_floor(
        artifact["parameters"]["value"],
        artifact["quantization_bits"]["value"],
        capacity["artifact_overhead_fraction"]["value"],
        capacity["runtime_gb"]["value"],
        capacity["kv_gb"]["value"],
        capacity["workspace_gb"]["value"],
        capacity["reserve_fraction"]["value"],
    )
    expected = {
        "quantized_weights_gb": capacity["weights_and_metadata_gb"]["value"],
        "before_reserve_gb": capacity["before_reserve_gb"]["value"],
        "reserve_gb": capacity["reserve_gb"]["value"],
        "total_gb": capacity["total_gb"]["value"],
    }
    for key, ledger_value in expected.items():
        if result[key] != _decimal(ledger_value):
            raise ValueError(f"inference motor disagrees with ledger for {key}")


def load_chart_metadata(data_path: Path = DATA_PATH) -> list[dict]:
    """Return presentation metadata derived only from the ordered ledger."""
    data = _load_data(data_path)

    accelerator_rows = _training_rows(data, "accelerators_concurrent")
    for row in accelerator_rows:
        row["display"] = f"{int(row['value']):,} aceleradores"
    accelerator_points = _plotted(accelerator_rows)

    hbm_rows = _training_rows(data, "hbm_physical_installed")
    for row in hbm_rows:
        unit = "GiB" if str(row["unit"]).startswith("GiB") else "GB"
        row["panel"] = f"{unit} físicos"
        row["display"] = format_si(row["value"], unit)
    hbm_points = _plotted(hbm_rows)

    power_rows = _training_rows(data, "accelerator_power")
    for row in power_rows:
        row["panel"] = "GPU/chip-only"
        row["display"] = (
            format_si(row["value"], "W") if row["value"] is not None
            else "sin valor identificable"
        )
    power_points = _plotted(power_rows)

    capex_rows = []
    panel_by_boundary = {
        "accelerator-only": "accelerator-only · supuesto docente 2026",
        "system-based": "system-based · reposición 2026",
    }
    for valuation in data["valuations"]:
        price = valuation["price"]
        capex_rows.append(
            {
                "id": valuation["id"],
                "label": panel_by_boundary[valuation["boundary"]],
                "panel": panel_by_boundary[valuation["boundary"]],
                "boundary": valuation["boundary"],
                "status": price["status"],
                "value": price.get("value"),
                "unit": price["unit"],
                "source_ids": list(price.get("source_ids", [])),
                "display": (
                    format_si(price["value"], "USD")
                    if price.get("value") is not None
                    else "sin precio identificable"
                ),
            }
        )
    capex_points = _plotted(capex_rows)

    inference_case = data["inference_capacity_cases"][0]
    _validate_inference_with_motor(inference_case)
    inference_rows = _inference_rows(inference_case)
    inference_points = [
        row for row in inference_rows
        if row["id"] != "minimum_purchasable_system"
    ]
    assessment = inference_case["capacity_assessment"]
    capacity_gb = inference_case["topology"]["memory_mapping"][
        "physical_hbm_per_shard_gb"
    ]["value"]

    accelerators_alt = (
        "Escala logarítmica de aceleradores concurrentes: "
        + "; ".join(
            f"{row['label']}, {row['display']} [{row['status']}]"
            for row in accelerator_rows
        )
        + "."
    )
    hbm_alt = (
        "HBM física instalada en paneles separados para GB y GiB: "
        + "; ".join(
            f"{row['label']}, {row['display']} [{row['status']}]"
            for row in hbm_rows
        )
        + ". HBM utilizable no es identificable y no se grafica."
    )
    power_alt = (
        "Potencia nominal de aceleradores, separada de servidor e IT: "
        + "; ".join(
            f"{row['label']}, {row['display']} [{row['status']}]"
            for row in power_rows
        )
        + ". El ledger no aporta potencia de servidor o IT y no se suma parte más todo."
    )
    capex_alt = (
        "CAPEX en fronteras y bases separadas: "
        + "; ".join(
            f"{row['label']}, {row['display']} [{row['status']}]"
            for row in capex_rows
        )
        + "."
    )
    inference_alt = (
        "Piso de capacidad de inferencia para Qwen2.5-32B GPTQ Int8: "
        + "; ".join(
            f"{row['label']}, {row['display']} [{row['status']}]"
            for row in inference_rows
        )
        + ". Cabe en capacidad física, sin afirmar SLA ni HBM utilizable."
    )

    return [
        {
            "id": "accelerators",
            "filename": SVG_FILENAMES[0],
            "title": "Aceleradores concurrentes de entrenamiento",
            "alt": accelerators_alt,
            "scale": "log",
            "ticks": [100, 1000, 10000, 100000],
            "scale_note": SCALE_NOTE,
            "panels": ["Aceleradores concurrentes"],
            "rows": accelerator_rows,
            "points": accelerator_points,
            "plotted_statuses": _status_sequence(accelerator_points),
        },
        {
            "id": "physical_hbm",
            "filename": SVG_FILENAMES[1],
            "title": "HBM física instalada en el pico",
            "alt": hbm_alt,
            "scale": "log",
            "ticks": [10000, 100000, 1000000, 10000000],
            "scale_note": SCALE_NOTE,
            "panels": ["GB físicos", "GiB físicos"],
            "rows": hbm_rows,
            "points": hbm_points,
            "plotted_statuses": _status_sequence(hbm_points),
        },
        {
            "id": "power",
            "filename": SVG_FILENAMES[2],
            "title": "Potencia: parte y todo no se suman",
            "alt": power_alt,
            "scale": "log",
            "ticks": [100000, 1000000, 10000000, 100000000],
            "scale_note": SCALE_NOTE,
            "panels": ["GPU/chip-only", "Servidor/IT"],
            "rows": power_rows,
            "points": power_points,
            "plotted_statuses": _status_sequence(power_points),
        },
        {
            "id": "capex",
            "filename": SVG_FILENAMES[3],
            "title": "CAPEX por frontera y base de valoración",
            "alt": capex_alt,
            "scale": "log",
            "ticks": [10000, 100000, 1000000],
            "scale_note": SCALE_NOTE,
            "panels": list(panel_by_boundary.values()),
            "rows": capex_rows,
            "points": capex_points,
            "plotted_statuses": _status_sequence(capex_points),
        },
        {
            "id": "inference_capacity",
            "filename": SVG_FILENAMES[4],
            "title": "Inferencia: piso de memoria y capacidad",
            "alt": inference_alt,
            "scale": "linear",
            "ticks": [0, 20, 40, 60, 80],
            "scale_note": "GB decimales por réplica y shard; no es HBM utilizable.",
            "panels": ["Piso presupuestado", "Capacidad física por shard"],
            "rows": inference_rows,
            "points": inference_points,
            "plotted_statuses": _status_sequence(inference_points),
            "claim": "piso de capacidad; cabe, sin SLA",
            "capacity_gb": capacity_gb,
            "total_gb": inference_case["capacity"]["total_gb"]["value"],
            "aggregate_system_hbm_used_as_fit_threshold": assessment[
                "aggregate_system_hbm_used_as_fit_threshold"
            ],
        },
    ]


def _render_accelerators(chart: dict) -> ET.Element:
    root = svg_header(WIDTH, 570, chart["title"], chart["alt"])
    _heading(root, "Aceleradores concurrentes", "Casos documentados · log₁₀")
    _panel(root, 78, 392, "Cantidad en el pico publicado")
    _log_axis(root, chart["ticks"], 112, 430, 446)
    for row, y in zip(chart["points"], (130, 208, 286, 364), strict=True):
        _plot_log_row(root, row, y, chart["ticks"])
    _scale_note(root, 496)
    _text(root, 18, 552, "Modelos no forman serie.", fill=MUTED)
    return root


def _render_hbm(chart: dict) -> ET.Element:
    root = svg_header(WIDTH, 680, chart["title"], chart["alt"])
    _heading(root, "HBM física instalada", "Pico concurrente · ejes log₁₀")
    _panel(root, 78, 316, "GB físicos")
    _panel(root, 404, 112, "GiB físicos · unidad separada")
    _log_axis(root, chart["ticks"], 112, 516, 548)
    gb_rows = [row for row in chart["points"] if row["panel"] == "GB físicos"]
    gib_rows = [row for row in chart["points"] if row["panel"] == "GiB físicos"]
    for row, y in zip(gb_rows, (130, 215, 300), strict=True):
        _plot_log_row(root, row, y, chart["ticks"])
    for row, y in zip(gib_rows, (456,), strict=True):
        _plot_log_row(root, row, y, chart["ticks"])
    _scale_note(root, 594)
    _text(root, 18, 646, "Física ≠ utilizable;", fill=MUTED)
    _text(root, 18, 668, "no se infiere la reserva.", fill=MUTED)
    return root


def _render_power(chart: dict) -> ET.Element:
    root = svg_header(WIDTH, 800, chart["title"], chart["alt"])
    _heading(root, "Potencia nominal", "Parte y todo, separados")
    _panel(root, 78, 390, ("GPU/chip-only", "no es consumo medido"))
    _log_axis(root, chart["ticks"], 150, 450, 486)
    for row, y in zip(chart["points"], (150, 238, 326), strict=True):
        _plot_log_row(root, row, y, chart["ticks"])
    missing = next(row for row in chart["rows"] if row["value"] is None)
    _text(root, 24, 414, missing["label"], weight="650")
    _missing_status(root, 24, 438, missing["status"])
    _scale_note(root, 540)
    _panel(root, 594, 176, ("Servidor/IT", "ya incluiría aceleradores"))
    _text(root, 24, 676, "Sin valor identificable", fill=MUTED)
    _text(root, 24, 700, "en el ledger.", fill=MUTED)
    _text(root, 24, 731, "Nunca sumar GPU/chip-only", fill=ACCENT)
    _text(root, 24, 755, "+ servidor/IT.", fill=ACCENT)
    return root


def _render_capex(chart: dict) -> ET.Element:
    root = svg_header(WIDTH, 600, chart["title"], chart["alt"])
    _heading(root, "CAPEX de hardware", "Fronteras y bases separadas")
    _panel(root, 78, 168, ("accelerator-only · supuesto", "docente 2026"))
    row = chart["points"][0]
    plotted = {**row, "label": "Precio por módulo H100 SXM"}
    _plot_log_row(root, plotted, 150, chart["ticks"])
    _log_axis(root, chart["ticks"], 142, 228, 268)
    _scale_note(root, 316)
    _panel(root, 362, 204, ("system-based · reposición", "2026"))
    missing = chart["rows"][1]
    _text(root, 24, 434, "Servidor completo", weight="650")
    _missing_status(root, 24, 458, missing["status"])
    _text(root, 24, 522, "Sin precio persistente;", fill=MUTED)
    _text(root, 24, 546, "no se grafica.", fill=MUTED)
    return root


def _render_inference(chart: dict) -> ET.Element:
    root = svg_header(WIDTH, 810, chart["title"], chart["alt"])
    _heading(root, "Piso y capacidad", "1 réplica · 1 shard · sin SLA")
    _panel(root, 78, 356, ("Componentes del piso", "GB decimales"))
    component_rows = chart["rows"][:5]
    for row, y in zip(component_rows, (150, 208, 266, 324, 382), strict=True):
        _marker(root, 31, y - 5, row["status"], row["label"], size=7)
        _text(root, 49, y, row["label"], weight="650")
        _text(
            root,
            49,
            y + 23,
            f"{row['display']} [{row['status']}]",
            fill=_status_color(row["status"]),
            weight="650",
        )

    total = chart["rows"][5]
    capacity = chart["rows"][6]
    _panel(root, 448, 188, ("Piso presupuestado", "frente a capacidad física"))
    bar_start, bar_end = 28, 332
    total_end = bar_start + (bar_end - bar_start) * (
        float(total["value"]) / float(capacity["value"])
    )
    ET.SubElement(
        root,
        _tag("rect"),
        {"x": str(bar_start), "y": "514", "width": str(bar_end - bar_start),
         "height": "24", "rx": "8", "fill": "none", "stroke": SCENARIO,
         "stroke-width": "3"},
    )
    ET.SubElement(
        root,
        _tag("rect"),
        {"x": str(bar_start), "y": "514", "width": f"{total_end - bar_start:g}",
         "height": "24", "rx": "8", "fill": DERIVED},
    )
    _marker(root, total_end, 526, total["status"], total["label"], size=7)
    _text(root, 24, 574, f"Piso: {total['display']} [{total['status']}]", fill=DERIVED,
          weight="650")
    _marker(root, 31, 602, capacity["status"], capacity["label"], size=7)
    _text(root, 49, 607, f"Capacidad: {capacity['display']}", fill=SCENARIO, weight="650")
    _text(root, 49, 629, f"[{capacity['status']}]", fill=SCENARIO, weight="650")
    minimum = chart["rows"][7]
    _marker(root, 31, 676, minimum["status"], minimum["label"], size=7)
    _text(root, 49, 681, "Mínimo adquirible", weight="650")
    _text(root, 49, 704, minimum["display"], weight="650")
    _text(root, 49, 728, f"[{minimum['status']}]", fill=SCENARIO, weight="650")
    _text(root, 18, 762, "Capacidad física ≠", fill=ACCENT)
    _text(root, 18, 786, "HBM utilizable ≠ SLA.", fill=ACCENT)
    return root


RENDERERS = {
    "accelerators": _render_accelerators,
    "physical_hbm": _render_hbm,
    "power": _render_power,
    "capex": _render_capex,
    "inference_capacity": _render_inference,
}


def _serialize(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def render_all(data_path: Path, assets_dir: Path) -> list[Path]:
    """Render the five declared SVGs in stable order and return their paths."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    charts = load_chart_metadata(data_path)
    if tuple(chart["filename"] for chart in charts) != SVG_FILENAMES:
        raise ValueError("chart metadata and SVG manifest disagree")
    rendered = []
    for chart in charts:
        destination = assets_dir / chart["filename"]
        destination.write_bytes(_serialize(RENDERERS[chart["id"]](chart)))
        rendered.append(destination)
    return rendered


def main() -> None:
    for path in render_all(DATA_PATH, ASSETS_DIR):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
