#!/usr/bin/env python3
"""Generate the twelve accessible SVG panels for the AI model dashboard.

The numerical series come exclusively from :mod:`ai_model_dashboard`.  This
module is deliberately limited to composition, scales, labels and SVG output.
"""

from __future__ import annotations

from decimal import Decimal
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import yaml

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from ai_model_dashboard import (  # noqa: E402
    CapacityScenario,
    ParetoPoint,
    PlotPoint,
    build_inference_series,
    build_training_series,
    pareto_frontier,
)


ROOT = TOOLS.parent
DATA_PATH = TOOLS / "data/ai_hardware_costs.yaml"
ECI_PATH = TOOLS / "data/eci_snapshot_2026-08-18.yaml"
ASSETS_DIR = ROOT / "course/3_arquitectura_de_computadoras/_assets"
SVG_FILENAMES = (
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
)

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
W, H = 600, 720
LEFT, RIGHT, TOP, BOTTOM = 100, 60, 190, 100
PLOT_W, PLOT_H = W - LEFT - RIGHT, H - TOP - BOTTOM
FONT = "system-ui, -apple-system, sans-serif"
COLORS = {
    "FACT": "#2dd4bf",
    "DERIVED": "#60a5fa",
    "ESTIMATE": "#fb923c",
    "SCENARIO": "#c084fc",
}
MARKERS = {
    "FACT": "circle",
    "DERIVED": "square",
    "ESTIMATE": "diamond",
    "SCENARIO": "triangle",
}

TEMPORAL = (
    ("ai-training-parameters.svg", "Parámetros: total y activo", "parameters_total_active", "Parámetros", "training"),
    ("ai-training-flop.svg", "Trabajo de entrenamiento", "training_flop", "FLOP", "training"),
    ("ai-training-accelerators.svg", "Aceleradores y horas", "accelerators_and_hours", "Conteos/horas · no se suman", "training"),
    ("ai-training-power.svg", "Envolvente de potencia", "power_or_energy_envelope", "W de aceleradores", "training"),
    ("ai-training-replacement-value.svg", "Valor de reemplazo", "replacement_value", "USD comparables", "training"),
    ("ai-inference-memory.svg", "Memoria mínima de pesos", "artifact_or_weight_floor", "Bytes", "inference"),
    ("ai-inference-accelerators.svg", "Piso de capacidad H100", "h100_capacity_equivalents", "Aceleradores", "inference"),
    ("ai-inference-power.svg", "TDP del piso de capacidad", "accelerator_tdp_scenario", "W de aceleradores", "inference"),
    ("ai-inference-capex.svg", "CAPEX del piso de capacidad", "accelerator_capex_scenario", "USD", "inference"),
    ("ai-inference-parameters.svg", "Parámetros: total y activo", "parameters_total_active", "Parámetros", "inference"),
)


def _svg(tag: str, attrs: dict[str, str] | None = None, text: str | None = None):
    node = ET.Element(f"{{{NS}}}{tag}", attrs or {})
    node.text = text
    return node


def _add(parent, tag, attrs=None, text=None):
    node = _svg(tag, attrs, text)
    parent.append(node)
    return node


def _root(title: str, desc: str):
    root = _svg("svg", {
        "viewBox": f"0 0 {W} {H}",
        "role": "img",
        "aria-labelledby": "title desc",
        "style": "max-width:100%;height:auto",
    })
    _add(root, "title", {"id": "title"}, f"{title} — dashboard de modelos de IA")
    _add(root, "desc", {"id": "desc"}, desc)
    _add(root, "rect", {"width": str(W), "height": str(H), "rx": "24", "fill": "#111827"})
    return root


def _text(parent, x, y, value, size=27, *, anchor="start", weight="400", fill="#f8fafc", **extra):
    size = max(27, size)
    attrs = {
        "x": str(x), "y": str(y), "font-size": str(size),
        "font-family": FONT, "fill": fill, "text-anchor": anchor,
        "font-weight": weight,
    }
    attrs.update({key.replace("_", "-"): str(val) for key, val in extra.items()})
    return _add(parent, "text", attrs, value)


def _format(value: Decimal) -> str:
    number = float(value)
    if abs(number) >= 1e18:
        exponent = int(math.floor(math.log10(abs(number))))
        coefficient = number / (10 ** exponent)
        return f"{coefficient:.0f}e{exponent}"
    for divisor, suffix in ((1e15, "P"), (1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k")):
        if abs(number) >= divisor:
            scaled = number / divisor
            return f"{scaled:.0f}{suffix}" if scaled >= 10 else f"{scaled:.1f}{suffix}"
    return f"{number:.0f}" if number >= 1 else f"{number:.2g}"


def _year_x(year: int, jitter: float = 0) -> float:
    return LEFT + (year - 2018) / 8 * PLOT_W + jitter


def _log_ticks(points: list[PlotPoint]) -> list[Decimal]:
    values = [bound for point in points for bound in (point.low or point.value, point.high or point.value)]
    lo = math.floor(math.log10(float(min(values))))
    hi = math.ceil(math.log10(float(max(values))))
    return [Decimal(10) ** exponent for exponent in range(lo, hi + 1)]


def _log_y(value: Decimal, ticks: list[Decimal]) -> float:
    lo, hi = math.log10(float(ticks[0])), math.log10(float(ticks[-1]))
    if hi == lo:
        return TOP + PLOT_H / 2
    ratio = (math.log10(float(value)) - lo) / (hi - lo)
    return TOP + PLOT_H * (1 - ratio)


def _marker(parent, point: PlotPoint, x: float, y: float, ticks: list[Decimal]):
    ring = point.label in {"active", "accelerator-hours"}
    attrs = {
        "data-quantitative": "true",
        "data-model-id": point.model_id,
        "data-status": point.status,
        "data-source-ids": " ".join(point.source_ids),
        "data-value": str(point.value),
        "data-unit": point.unit,
        "data-claim-scope": point.claim_scope,
        "data-marker": MARKERS[point.status],
        "data-series": point.label,
        "data-series-marker": "outer-ring" if ring else "single",
        "aria-label": f"{point.model_id}: {_format(point.value)} {point.unit}, {point.status}",
    }
    group = _add(parent, "g", attrs)
    color = COLORS[point.status]
    if point.low is not None and point.high is not None:
        low_y, high_y = _log_y(point.low, ticks), _log_y(point.high, ticks)
        _add(group, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": f"{low_y:.1f}", "y2": f"{high_y:.1f}", "stroke": color, "stroke-width": "7", "stroke-opacity": ".45"})
        _add(group, "line", {"x1": f"{x-8:.1f}", "x2": f"{x+8:.1f}", "y1": f"{low_y:.1f}", "y2": f"{low_y:.1f}", "stroke": color, "stroke-width": "3"})
        _add(group, "line", {"x1": f"{x-8:.1f}", "x2": f"{x+8:.1f}", "y1": f"{high_y:.1f}", "y2": f"{high_y:.1f}", "stroke": color, "stroke-width": "3"})
    common = {"fill": color, "stroke": "#f8fafc", "stroke-width": "2"}
    marker = MARKERS[point.status]
    if marker == "circle":
        _add(group, "circle", {**common, "cx": f"{x:.1f}", "cy": f"{y:.1f}", "r": "8"})
    elif marker == "square":
        _add(group, "rect", {**common, "x": f"{x-8:.1f}", "y": f"{y-8:.1f}", "width": "16", "height": "16"})
    elif marker == "diamond":
        _add(group, "path", {**common, "d": f"M{x:.1f},{y-10:.1f} L{x+10:.1f},{y:.1f} L{x:.1f},{y+10:.1f} L{x-10:.1f},{y:.1f} Z"})
    else:
        _add(group, "path", {**common, "d": f"M{x:.1f},{y-10:.1f} L{x+10:.1f},{y+9:.1f} L{x-10:.1f},{y+9:.1f} Z"})
    if ring:
        _add(group, "circle", {"cx": f"{x:.1f}", "cy": f"{y:.1f}", "r": "13", "fill": "none", "stroke": color, "stroke-width": "3"})


def _axes(root, points: list[PlotPoint], y_label: str):
    ticks = _log_ticks(points)
    for tick in ticks:
        y = _log_y(tick, ticks)
        _add(root, "line", {"x1": str(LEFT), "x2": str(W-RIGHT), "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": "#334155", "stroke-width": "2"})
        _text(root, LEFT-12, y+8, _format(tick), 25, anchor="end", fill="#cbd5e1")
    for year in (2018, 2020, 2022, 2024, 2026):
        x = _year_x(year)
        _add(root, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": str(TOP), "y2": str(TOP+PLOT_H), "stroke": "#1e293b", "stroke-width": "2"})
        _text(root, x, TOP+PLOT_H+35, str(year), 25, anchor="middle", fill="#cbd5e1")
    _text(root, W/2, H-22, "Año de publicación", 25, anchor="middle", weight="600")
    _text(root, 20, 124, y_label, 27, weight="600", fill="#cbd5e1")
    _text(root, 20, 162, "Y log · Igual distancia = multiplicar", 27, fill="#fbbf24")
    return ticks


def _selected(points: list[PlotPoint]) -> set[tuple[str, str]]:
    if not points:
        return set()
    ordered = sorted(points, key=lambda p: (p.value, p.year, p.model_id, p.label))
    picks = [ordered[0], ordered[-1]]
    chronological = sorted(points, key=lambda p: (p.year, p.model_id, p.label))
    picks.extend((chronological[0], chronological[-1]))
    return {(point.model_id, point.label) for point in picks}


def _render_temporal(title: str, y_label: str, points: list[PlotPoint], model_names: dict[str, str]):
    if points:
        desc = f"Serie temporal logarítmica de {y_label}. Cada punto conserva estado, fuente, unidad y alcance; n={len(points)}. Igual distancia vertical representa multiplicación."
    else:
        desc = "No existe una serie cuantitativa comparable con la evidencia disponible. Las ausencias no se convierten en cero ni reciben una posición inventada."
    root = _root(title, desc)
    _text(root, 24, 50, title, 32, weight="700")
    _text(root, 24, 88, f"n = {len(points)} · cada marca es un modelo", 25, fill="#cbd5e1")
    if not points:
        _text(root, W/2, 330, "No hay una serie comparable", 30, anchor="middle", weight="700")
        _text(root, W/2, 376, "La ausencia no equivale a cero", 25, anchor="middle", fill="#cbd5e1")
        _text(root, W/2, H-22, "Año de publicación", 25, anchor="middle", weight="600")
        return root

    ticks = _axes(root, points, y_label)
    chosen = _selected(points)
    seen = {}
    label_rows = []
    for index, point in enumerate(points):
        collision_key = (point.year, round(math.log10(float(point.value)), 1))
        offset = seen.get(collision_key, 0)
        seen[collision_key] = offset + 1
        x = _year_x(point.year, (offset % 5 - 2) * 7)
        y = _log_y(point.value, ticks)
        _marker(root, point, x, y, ticks)
        if (point.model_id, point.label) in chosen and len(label_rows) < 4:
            label_rows.append((point, x, y))
    # Direct labels in a dedicated strip stay readable; leader lines identify points.
    for row, (point, x, y) in enumerate(label_rows):
        label_y = 216 + row * 36
        label_x = W - 30
        _add(root, "line", {"x1": f"{x+8:.1f}", "y1": f"{y:.1f}", "x2": f"{label_x-205:.1f}", "y2": str(label_y-7), "stroke": COLORS[point.status], "stroke-width": "2", "stroke-dasharray": "5 5"})
        label = model_names.get(point.model_id, point.model_id).replace("Llama 3.1-", "Llama 3.1 ")
        if len(label) > 18:
            label = label[:17] + "…"
        _text(root, label_x, label_y, label, 27, anchor="end", weight="600", fill=COLORS[point.status], data_direct_label="true")
    return root


def _eci_points(eci: dict) -> dict[str, dict]:
    return {
        row["benchmark_model_id"]: row
        for row in eci.get("models", ())
        if row.get("pareto_eligible")
    }


def _pareto_inputs(cost_points: list[PlotPoint], eci: dict):
    scores = _eci_points(eci)
    by_model = {}
    for point in cost_points:
        if point.model_id in scores:
            by_model.setdefault(point.model_id, point)
    inputs = []
    for model_id, point in sorted(by_model.items()):
        score = scores[model_id]
        inputs.append(ParetoPoint(
            model_id,
            point.low or point.value,
            point.high or point.value,
            Decimal(str(score["score_low"])),
            Decimal(str(score["score_high"])),
        ))
    return inputs, by_model, scores


def _render_pareto(title: str, cost_points: list[PlotPoint], eci: dict, cost_label: str):
    inputs, costs, scores = _pareto_inputs(cost_points, eci)
    snapshot = eci["snapshot"]
    desc = (
        f"Frontera de Pareto entre {cost_label} y capacidad general según ECI, "
        f"snapshot {snapshot['as_of']}. Frontera segura sólida y posible punteada; n={len(inputs)}."
    )
    root = _root(title, desc)
    _text(root, 24, 50, title, 32, weight="700")
    _text(root, 24, 88, f"ECI snapshot {snapshot['as_of']} · n = {len(inputs)}", 25, fill="#cbd5e1")
    _add(root, "g", {"id": "frontera-segura", "stroke": "#2dd4bf", "stroke-width": "5", "fill": "none"})
    _add(root, "g", {"id": "frontera-posible", "stroke": "#fbbf24", "stroke-width": "5", "stroke-dasharray": "10 8", "fill": "none"})
    if not inputs:
        _text(root, W/2, 314, "Frontera no identificable", 30, anchor="middle", weight="700")
        _text(root, W/2, 360, "Falta un costo comparable", 25, anchor="middle", fill="#cbd5e1")
        _text(root, W/2, H-22, cost_label, 25, anchor="middle", weight="600")
        _text(root, 24, 126, "Capacidad general según ECI", 25, weight="600")
        return root

    result = pareto_frontier(inputs)
    cost_min = min(point.cost_low for point in inputs)
    cost_max = max(point.cost_high for point in inputs)
    score_min = min(point.score_low for point in inputs)
    score_max = max(point.score_high for point in inputs)
    cost_ticks = [Decimal(10) ** e for e in range(math.floor(math.log10(float(cost_min))), math.ceil(math.log10(float(cost_max))) + 1)]
    c_lo, c_hi = math.log10(float(cost_ticks[0])), math.log10(float(cost_ticks[-1]))
    s_pad = max(Decimal("2"), (score_max-score_min) * Decimal("0.1"))
    s_lo, s_hi = score_min-s_pad, score_max+s_pad
    def xy(model_id):
        cost = costs[model_id].value
        score = Decimal(str(scores[model_id]["score"]))
        x = LEFT + (math.log10(float(cost))-c_lo) / max(c_hi-c_lo, 1) * PLOT_W
        y = TOP + (1-float((score-s_lo)/(s_hi-s_lo))) * PLOT_H
        return x, y
    for tick in cost_ticks:
        x = LEFT + (math.log10(float(tick))-c_lo) / max(c_hi-c_lo, 1) * PLOT_W
        _add(root, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": str(TOP), "y2": str(TOP+PLOT_H), "stroke": "#334155", "stroke-width": "2"})
        _text(root, x, TOP+PLOT_H+35, _format(tick), 25, anchor="middle", fill="#cbd5e1")
    for value in (s_lo, (s_lo+s_hi)/2, s_hi):
        y = TOP + (1-float((value-s_lo)/(s_hi-s_lo))) * PLOT_H
        _add(root, "line", {"x1": str(LEFT), "x2": str(W-RIGHT), "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": "#334155", "stroke-width": "2"})
        _text(root, LEFT-12, y+8, f"{value:.0f}", 25, anchor="end", fill="#cbd5e1")
    _text(root, 20, 124, "Capacidad general según ECI", 25, weight="600")
    _text(root, W/2, H-22, cost_label, 25, anchor="middle", weight="600")
    _text(root, W-24, 124, "X log", 25, anchor="end", fill="#fbbf24")

    for frontier_id, ids in (("frontera-segura", result.safe_ids), ("frontera-posible", result.possible_ids)):
        group = next(node for node in root if node.attrib.get("id") == frontier_id)
        coords = [xy(model_id) for model_id in ids]
        if len(coords) >= 2:
            _add(group, "polyline", {"points": " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)})
    for index, item in enumerate(inputs):
        point = costs[item.model_id]
        score = scores[item.model_id]
        x, y = xy(item.model_id)
        attrs = {
            "data-quantitative": "true", "data-model-id": item.model_id,
            "data-status": point.status, "data-source-ids": " ".join((*point.source_ids, snapshot["scores_source_id"])),
            "data-value": str(point.value), "data-unit": point.unit,
            "data-claim-scope": f"{point.claim_scope};eci_exact_variant",
            "data-marker": MARKERS[point.status], "data-eci": str(score["score"]),
            "aria-label": f"{item.model_id}: {point.value} {point.unit}; ECI {score['score']}",
        }
        group = _add(root, "g", attrs)
        color = COLORS[point.status]
        _add(group, "path", {"d": f"M{x:.1f},{y-10:.1f} L{x+10:.1f},{y+9:.1f} L{x-10:.1f},{y+9:.1f} Z", "fill": color, "stroke": "#f8fafc", "stroke-width": "2"})
        # There are only eight eligible exact ECI matches: label every point.
        label = score["model_name"].replace("Llama 3.1-", "Llama 3.1 ")
        if len(label) > 18:
            label = label[:17] + "…"
        label_x = W - 24
        label_y = 216 + index * 39
        _add(root, "line", {"x1": f"{x+10:.1f}", "y1": f"{y:.1f}", "x2": str(label_x-235), "y2": str(label_y-7), "stroke": color, "stroke-width": "2", "stroke-dasharray": "5 5"})
        _text(root, label_x, label_y, label, 27, anchor="end", weight="600", fill=color, data_direct_label="true")
    return root


def _serialize(root) -> bytes:
    ET.indent(root, space="  ")
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + ET.tostring(root, encoding="unicode") + "\n").encode("utf-8")


def render_dashboard(ledger_path: Path, eci_path: Path, assets_dir: Path) -> list[Path]:
    ledger = yaml.safe_load(Path(ledger_path).read_text(encoding="utf-8"))
    eci = yaml.safe_load(Path(eci_path).read_text(encoding="utf-8"))
    training = build_training_series(ledger)
    inference = build_inference_series(ledger, CapacityScenario())
    names = {model["id"]: model["canonical_name"] for model in ledger["dashboard_models"]}
    roots = []
    for _, title, key, y_label, family in TEMPORAL:
        series = training[key] if family == "training" else inference[key]
        roots.append(_render_temporal(title, y_label, series, names))
    roots.extend((
        _render_pareto("Pareto · entrenamiento", training["replacement_value"], eci, "Valor de reemplazo (USD)"),
        _render_pareto("Pareto · inferencia local", inference["accelerator_capex_scenario"], eci, "CAPEX de capacidad (USD)"),
    ))
    assets_dir = Path(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, root in zip(SVG_FILENAMES, roots, strict=True):
        path = assets_dir / name
        path.write_bytes(_serialize(root))
        paths.append(path)
    return paths


if __name__ == "__main__":
    for output in render_dashboard(DATA_PATH, ECI_PATH, ASSETS_DIR):
        print(output.relative_to(ROOT))
