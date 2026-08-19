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
W, H = 600, 300
# Four non-overlapping bands: heading 0–80, key 86–120, plot 132–232,
# and the temporal X axis 250–294.  Labels live in the right gutter.
LEFT, RIGHT, TOP, BOTTOM = 100, 220, 145, 68
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
    size = max(29, size)
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


def _marker(parent, point: PlotPoint, x: float, y: float, ticks: list[Decimal], y_func=None):
    ring = point.label == "active"
    hour_mark = point.label == "accelerator-hours"
    y_func = y_func or (lambda value: _log_y(value, ticks))
    range_text = ""
    if point.low is not None and point.high is not None:
        range_text = f"; rango {point.low}–{point.high} {point.unit}"
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
        "data-series-marker": "outer-ring" if ring else "underline" if hour_mark else "single",
        "aria-label": f"{point.model_id}: {point.value} {point.unit}{range_text}, {point.status}",
    }
    if point.low is not None and point.high is not None:
        attrs.update({"data-low": str(point.low), "data-high": str(point.high)})
    group = _add(parent, "g", attrs)
    _add(group, "title", text=attrs["aria-label"])
    color = COLORS[point.status]
    if point.low is not None and point.high is not None:
        low_y, high_y = y_func(point.low), y_func(point.high)
        _add(group, "line", {"data-interval-geometry": "true", "x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": f"{low_y:.1f}", "y2": f"{high_y:.1f}", "stroke": color, "stroke-width": "7", "stroke-opacity": ".45"})
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
        _add(group, "circle", {"data-series-ring": "true", "cx": f"{x:.1f}", "cy": f"{y:.1f}", "r": "13", "fill": "none", "stroke": "#cbd5e1", "stroke-width": "3"})
    if hour_mark:
        _add(group, "line", {"data-series-hour-mark": "true", "x1": f"{x-13:.1f}", "x2": f"{x+13:.1f}", "y1": f"{y+15:.1f}", "y2": f"{y+15:.1f}", "stroke": "#cbd5e1", "stroke-width": "3"})


def _axes(root, points: list[PlotPoint], y_label: str):
    ticks = _log_ticks(points)
    if len(ticks) > 2:
        ticks = [ticks[0], ticks[-1]]
    for tick in ticks:
        y = _log_y(tick, ticks)
        _add(root, "line", {"x1": str(LEFT), "x2": str(W-RIGHT), "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": "#334155", "stroke-width": "2"})
        _text(root, LEFT-12, y+8, _format(tick), 27, anchor="end", fill="#cbd5e1", data_axis_label="true")
    for year in (2018, 2022, 2026):
        x = _year_x(year)
        _add(root, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": str(TOP), "y2": str(TOP+PLOT_H), "stroke": "#1e293b", "stroke-width": "2"})
        anchor = "end" if year == 2018 else "start" if year == 2026 else "middle"
        _text(root, x, 278, str(year), 27, anchor=anchor, fill="#cbd5e1", data_axis_label="true")
    _text(root, 20, 108, y_label, 27, weight="600", fill="#cbd5e1", data_axis_label="true", data_layout_role="axis-unit")
    _text(root, 580, 282, "Y log · ×", 29, anchor="end", fill="#fbbf24", data_axis_label="true", data_layout_role="axis-scale")
    return ticks


def _selected(points: list[PlotPoint]) -> set[tuple[str, str]]:
    if not points:
        return set()
    ordered = sorted(points, key=lambda p: (p.value, p.year, p.model_id, p.label))
    picks = [ordered[0], ordered[-1]]
    chronological = sorted(points, key=lambda p: (p.year, p.model_id, p.label))
    picks.extend((chronological[0], chronological[-1]))
    return {(point.model_id, point.label) for point in picks}


def _short_label(label: str) -> str:
    replacements = {
        "BERT-Large": "BERT 336M",
        "BLOOM 176B": "BLOOM176",
        "Kimi K3": "Kimi K3",
        "T5-11B": "T5 11B",
        "DeepSeek-R1": "DeepSeek R1",
        "Llama 3.1-405B": "L3 405B",
        "Llama 3.1-70B": "Llama3 70B",
        "Llama 3.1-8B": "Llama3 8B",
        "Qwen3-30B-A3B": "Q3 30B",
        "Qwen3-235B-A22B": "Q3 235B",
        "Qwen3.8-2.4T-A95B": "Q3.8 2.4T",
        "Qwen3.8-Max": "Q3.8 Max",
    }
    short = replacements.get(label, label)
    return short if len(short) <= 11 else short[:10] + "…"


def _add_model_key(root, rows, model_names, *, x=410, ys=(155, 195, 235)):
    """Place selected model identities in the reserved band right of the plot."""
    used = set()
    selected = []
    for point, px, py in rows:
        if point.model_id not in used:
            selected.append((point, px, py))
            used.add(point.model_id)
        if len(selected) == len(ys):
            break
    for (point, px, py), y in zip(selected, ys, strict=False):
        _add(root, "path", {
            "d": f"M{px+10:.1f},{py:.1f} L395,{y-8} L{x-10},{y-8}",
            "fill": "none", "stroke": COLORS[point.status], "stroke-width": "2",
            "data-leader": "true", "data-model-id": point.model_id,
        })
        _text(root, x, y, _short_label(model_names[point.model_id]), 29,
              weight="600", data_direct_label="true", data_model_id=point.model_id,
              data_layout_role="direct-label")


def _render_temporal(title: str, y_label: str, points: list[PlotPoint], model_names: dict[str, str]):
    if points:
        desc = f"Serie por Año de publicación, logarítmica, de {y_label}. Cada punto conserva estado, fuente, unidad y alcance; n={len(points)}. Igual distancia = multiplicar."
    else:
        desc = "No existe una serie cuantitativa comparable por Año de publicación. Las ausencias no se convierten en cero ni reciben una posición inventada."
    root = _root(title, desc)
    _text(root, 24, 38, title, 31, weight="700")
    model_count = len({point.model_id for point in points})
    _text(root, 24, 72, f"{model_count} modelos · {len(points)} observaciones", 27, fill="#cbd5e1")
    if not points:
        _text(root, W/2, 175, "No hay una serie comparable", 30, anchor="middle", weight="700")
        _text(root, W/2, 215, "La ausencia no equivale a cero", 27, anchor="middle", fill="#cbd5e1")
        return root

    labels = {point.label for point in points}
    if {"total", "active"} <= labels:
        _text(root, 250, 108, "● total", 29, fill="#cbd5e1", data_legend="true", data_series="total", data_series_marker="single", data_layout_role="legend")
        _text(root, 400, 108, "◎ activo", 29, fill="#cbd5e1", data_legend="true", data_series="active", data_series_marker="outer-ring", data_layout_role="legend")

    ticks = _axes(root, points, y_label)
    chosen = _selected(points)
    seen = {}
    label_rows = []
    for index, point in enumerate(points):
        collision_key = (point.year, round(math.log10(float(point.value)), 1))
        offset = seen.get(collision_key, 0)
        seen[collision_key] = offset + 1
        x = _year_x(point.year, (offset % 5 - 2) * 7)
        x = max(LEFT + 18, min(W - RIGHT - 18, x))
        y = _log_y(point.value, ticks)
        _marker(root, point, x, y, ticks)
        if (point.model_id, point.label) in chosen and len(label_rows) < 4:
            label_rows.append((point, x, y))
    _add_model_key(root, label_rows, model_names)
    return root


def _render_accelerators(points: list[PlotPoint], model_names: dict[str, str]):
    """Render counts and accelerator-hours as separate log small multiples."""
    root = _root(
        "Aceleradores y horas",
        "Dos paneles por Año de publicación con escalas logarítmicas independientes. Igual distancia = multiplicar. El panel superior muestra aceleradores concurrentes y el inferior accelerator-hours; las unidades no se suman.",
    )
    _text(root, 24, 38, "Aceleradores y horas", 31, weight="700")
    model_count = len({point.model_id for point in points})
    _text(root, 24, 72, f"{model_count} modelos · {len(points)} observaciones", 27, fill="#cbd5e1")
    _text(root, 580, 108, "Y log · ×", 27, anchor="end", fill="#fbbf24",
          data_axis_label="true", data_layout_role="axis-scale")
    specs = (
        ("concurrent accelerators", "● chips", 140, 35),
        ("accelerator-hours", "↔ chip-hours", 218, 35),
    )
    all_positions = []
    for series_label, visible_label, panel_top, panel_height in specs:
        panel = _add(root, "g", {"data-series-panel": series_label})
        subset = [point for point in points if point.label == series_label]
        ticks = _log_ticks(subset)
        if len(ticks) > 2:
            ticks = [ticks[0], ticks[-1]]
        y_func = lambda value, ticks=ticks, top=panel_top, height=panel_height: (
            top + height * (1 - (
                math.log10(float(value)) - math.log10(float(ticks[0]))
            ) / max(math.log10(float(ticks[-1])) - math.log10(float(ticks[0])), 1))
        )
        # Both series names live in the header band.  Keeping the lower-panel
        # legend out of the plot prevents it from covering quantitative marks.
        legend_y = 108
        legend_x = 20 if series_label == "concurrent accelerators" else 145
        _text(root, legend_x, legend_y, visible_label, 27, weight="600", fill="#cbd5e1",
              data_legend="true", data_series=series_label, data_layout_role="legend")
        for tick in ticks:
            y = y_func(tick)
            _add(panel, "line", {"x1": str(LEFT), "x2": str(W-RIGHT), "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": "#334155", "stroke-width": "2"})
            _text(root, LEFT-12, y+8, _format(tick), 27, anchor="end", fill="#cbd5e1", data_axis_label="true")
        for year in (2018, 2022, 2026):
            x = _year_x(year)
            _add(panel, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": str(panel_top), "y2": str(panel_top+panel_height), "stroke": "#1e293b", "stroke-width": "2"})
            if series_label == "accelerator-hours":
                anchor = "start" if year == 2018 else "end" if year == 2026 else "middle"
                _text(root, x, 286, str(year), 27, anchor=anchor, fill="#cbd5e1", data_axis_label="true")
        seen = {}
        positions = []
        for point in subset:
            offset = seen.get(point.year, 0)
            seen[point.year] = offset + 1
            x = _year_x(point.year, (offset % 3 - 1) * 7)
            x = max(LEFT + 18, min(W - RIGHT - 18, x))
            y = y_func(point.value)
            _marker(panel, point, x, y, ticks, y_func=y_func)
            positions.append((point, x, y))
            all_positions.append((point, x, y))
    chosen = _selected(points)
    selected_positions = [row for row in all_positions
                          if (row[0].model_id, row[0].label) in chosen]
    _add_model_key(root, selected_positions, model_names)
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


def segments_cross(a, b) -> bool:
    """Return whether two closed line segments cross away from shared ends."""
    def orientation(p, q, r):
        value = (q[1]-p[1])*(r[0]-q[0]) - (q[0]-p[0])*(r[1]-q[1])
        if abs(value) < 1e-9:
            return 0
        return 1 if value > 0 else 2

    p1, q1 = (a[0], a[1]), (a[2], a[3])
    p2, q2 = (b[0], b[1]), (b[2], b[3])
    if {p1, q1} & {p2, q2}:
        return False
    return (
        orientation(p1, q1, p2) != orientation(p1, q1, q2)
        and orientation(p2, q2, p1) != orientation(p2, q2, q1)
    )


def _leader_path_with_bridges(
    routes: dict[str, list[tuple[float, float]]], model_id: str
) -> str:
    """Serialize an orthogonal route, opening small gaps at foreign crossings."""
    route = routes[model_id]
    foreign_verticals = []
    for other_id, points in routes.items():
        if other_id == model_id:
            continue
        for start, end in zip(points, points[1:]):
            if abs(start[0] - end[0]) < 0.01:
                foreign_verticals.append((start[0], min(start[1], end[1]), max(start[1], end[1])))
    commands = []
    gap = 2.5
    for start, end in zip(route, route[1:]):
        if abs(start[1] - end[1]) >= 0.01:
            commands.append(f"M{start[0]:.1f},{start[1]:.1f} L{end[0]:.1f},{end[1]:.1f}")
            continue
        low, high = sorted((start[0], end[0]))
        cuts = sorted(
            x for x, y_low, y_high in foreign_verticals
            if low + gap < x < high - gap and y_low + 0.1 < start[1] < y_high - 0.1
        )
        cursor = low
        for x in cuts:
            commands.append(f"M{cursor:.1f},{start[1]:.1f} L{x-gap:.1f},{start[1]:.1f}")
            cursor = x + gap
        commands.append(f"M{cursor:.1f},{start[1]:.1f} L{high:.1f},{start[1]:.1f}")
    return " ".join(commands)


def _render_pareto(title: str, cost_points: list[PlotPoint], eci: dict, cost_label: str):
    inputs, costs, scores = _pareto_inputs(cost_points, eci)
    snapshot = eci["snapshot"]
    desc = (
        f"Frontera de Pareto entre {cost_label} y capacidad general según ECI, "
        f"snapshot {snapshot['as_of']}. Un borde sólido marca una frontera segura en todo el rango; "
        f"un borde punteado marca una frontera posible en algún valor del rango; n={len(inputs)}. "
        "Capacidad general según ECI es el eje vertical."
    )
    root = _root(title, desc)
    _text(root, 24, 38, title, 31, weight="700")
    _text(root, 580, 38, f"n={len(inputs)}", 27, anchor="end", fill="#cbd5e1",
          data_layout_role="count")
    safe_group = _add(root, "g", {"id": "frontera-segura"})
    possible_group = _add(root, "g", {"id": "frontera-posible"})
    dominated_group = _add(root, "g", {"id": "fuera-de-frontera"})
    _text(root, 20, 76, "━ segura", 27, fill="#2dd4bf", data_legend="true",
          data_series="safe", data_layout_role="legend")
    _text(root, 175, 76, "┅ posible", 27, fill="#fbbf24", data_legend="true",
          data_series="possible", data_layout_role="legend")
    if not inputs:
        _text(root, W/2, 184, "Frontera no identificable", 30, anchor="middle", weight="700")
        _text(root, W/2, 226, "Falta un costo comparable", 27, anchor="middle", fill="#cbd5e1")
        _text(root, 320, 76, "ECI", 27, weight="600", data_axis_label="true", data_layout_role="axis-y")
        _text(root, 380, 76, "CAPEX", 29, weight="600", data_axis_label="true", data_axis_role="x-title")
        _text(root, 580, 76, "X log", 29, anchor="end", fill="#fbbf24", data_axis_label="true", data_axis_role="x-log-note")
        return root

    result = pareto_frontier(inputs)
    cost_min = min(point.cost_low for point in inputs)
    cost_max = max(point.cost_high for point in inputs)
    score_min = min(point.score_low for point in inputs)
    score_max = max(point.score_high for point in inputs)
    cost_ticks = [Decimal(10) ** e for e in range(math.floor(math.log10(float(cost_min))), math.ceil(math.log10(float(cost_max))) + 1)]
    if len(cost_ticks) > 2:
        cost_ticks = [cost_ticks[0], cost_ticks[-1]]
    c_lo, c_hi = math.log10(float(cost_ticks[0])), math.log10(float(cost_ticks[-1]))
    s_pad = max(Decimal("2"), (score_max-score_min) * Decimal("0.1"))
    s_lo, s_hi = score_min-s_pad, score_max+s_pad
    pareto_left, pareto_width = 75, 190
    def cost_x(value):
        return pareto_left + (math.log10(float(value))-c_lo) / max(c_hi-c_lo, 1) * pareto_width
    def score_y(value):
        return TOP + (1-float((value-s_lo)/(s_hi-s_lo))) * PLOT_H
    for tick in cost_ticks:
        x = pareto_left + (math.log10(float(tick))-c_lo) / max(c_hi-c_lo, 1) * pareto_width
        _add(root, "line", {"x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": str(TOP), "y2": str(TOP+PLOT_H), "stroke": "#334155", "stroke-width": "2"})
        anchor = "end" if tick in {cost_ticks[0], cost_ticks[-1]} else "middle"
        _text(root, x, TOP+PLOT_H+45, _format(tick), 27, anchor=anchor, fill="#cbd5e1", data_axis_label="true")
    for value in (s_lo, (s_lo+s_hi)/2, s_hi):
        y = TOP + (1-float((value-s_lo)/(s_hi-s_lo))) * PLOT_H
        _add(root, "line", {"x1": str(pareto_left), "x2": str(pareto_left+pareto_width), "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": "#334155", "stroke-width": "2"})
        _text(root, pareto_left-10, y+8, f"{value:.0f}", 27, anchor="end", fill="#cbd5e1", data_axis_label="true")
    _text(root, 20, 116, "ECI", 27, weight="600", data_axis_label="true", data_layout_role="axis-y")
    _text(root, 105, 116, "CAPEX", 29, weight="600", data_axis_label="true", data_axis_role="x-title")
    _text(root, 300, 116, "X log", 29, anchor="end", fill="#fbbf24", data_axis_label="true", data_axis_role="x-log-note")

    compact_names = {
        "DM_DEEPSEEK_R1": "DS R1", "DM_GEMMA2_27B": "G2 27B",
        "DM_GEMMA3_27B": "G3 27B", "DM_GEMMA_7B": "G1 7B",
        "DM_LLAMA31_70B": "L3 70B", "DM_LLAMA31_8B": "L3 8B",
        "DM_QWEN2_72B": "Q2 72B", "DM_QWEN3_235B_A22B": "Q3 235B",
    }

    # Labels use two external gutters.  The second column is right-aligned so
    # even the widest compact name keeps a deliberate viewBox margin.
    ordered_inputs = sorted(
        inputs,
        key=lambda item: (-(item.score_low + item.score_high), item.model_id),
    )
    key_positions = {}
    for row in range(0, len(ordered_inputs), 2):
        pair = sorted(
            ordered_inputs[row:row + 2],
            key=lambda item: cost_x(item.cost_high),
        )
        for column, paired_item in enumerate(pair):
            key_positions[paired_item.model_id] = (
                325 if column == 0 else 570,
                150 + (row // 2) * 35,
                column,
            )
    pending_leaders = []
    routes = {}
    for index, item in enumerate(ordered_inputs):
        point = costs[item.model_id]
        score = scores[item.model_id]
        x = cost_x(point.value)
        y = score_y(Decimal(str(score["score"])))
        x_low, x_high = cost_x(item.cost_low), cost_x(item.cost_high)
        y_low, y_high = score_y(item.score_low), score_y(item.score_high)
        frontier = (
            "safe" if item.model_id in result.safe_ids
            else "possible" if item.model_id in result.possible_ids
            else "dominated"
        )
        parent = {"safe": safe_group, "possible": possible_group, "dominated": dominated_group}[frontier]
        fallback = (
            f"{item.model_id}: costo {item.cost_low}–{item.cost_high} {point.unit}; "
            f"ECI {item.score_low}–{item.score_high}; frontera {frontier}"
        )
        attrs = {
            "data-quantitative": "true", "data-model-id": item.model_id,
            "data-status": point.status, "data-source-ids": " ".join((*point.source_ids, snapshot["scores_source_id"])),
            "data-value": str(point.value), "data-unit": point.unit,
            "data-claim-scope": f"{point.claim_scope};eci_exact_variant",
            "data-marker": MARKERS[point.status], "data-eci": str(score["score"]),
            "data-low": str(item.cost_low), "data-high": str(item.cost_high),
            "data-pareto-interval": "true", "data-cost-low": str(item.cost_low),
            "data-cost-high": str(item.cost_high), "data-score-low": str(item.score_low),
            "data-score-high": str(item.score_high), "data-frontier": frontier,
            "aria-label": fallback,
        }
        group = _add(parent, "g", attrs)
        _add(group, "title", text=fallback)
        color = COLORS[point.status]
        frontier_color = {"safe": "#2dd4bf", "possible": "#fbbf24", "dominated": "#64748b"}[frontier]
        dash = {"safe": "", "possible": "10 8", "dominated": "3 7"}[frontier]
        rect_x = min(x_low, x_high) - (4 if abs(x_high-x_low) < 8 else 0)
        rect_y = min(y_low, y_high)
        rect_w = max(8, abs(x_high-x_low))
        rect_h = max(8, abs(y_high-y_low))
        rect_attrs = {"data-interval-geometry": "true", "x": f"{rect_x:.1f}", "y": f"{rect_y:.1f}", "width": f"{rect_w:.1f}", "height": f"{rect_h:.1f}", "fill": frontier_color, "fill-opacity": ".10", "stroke": frontier_color, "stroke-width": "4"}
        if dash:
            rect_attrs["stroke-dasharray"] = dash
        _add(group, "rect", rect_attrs)
        _add(group, "line", {"data-interval-geometry": "true", "x1": f"{x_low:.1f}", "x2": f"{x_high:.1f}", "y1": f"{y:.1f}", "y2": f"{y:.1f}", "stroke": frontier_color, "stroke-width": "4"})
        _add(group, "line", {"data-interval-geometry": "true", "x1": f"{x:.1f}", "x2": f"{x:.1f}", "y1": f"{y_low:.1f}", "y2": f"{y_high:.1f}", "stroke": frontier_color, "stroke-width": "4"})
        _add(group, "path", {"d": f"M{x:.1f},{y-10:.1f} L{x+10:.1f},{y+9:.1f} L{x-10:.1f},{y+9:.1f} Z", "fill": color, "stroke": "#f8fafc", "stroke-width": "2"})
        key_x, key_y, key_column = key_positions[item.model_id]
        leader_y = key_y - 10
        _text(root, key_x, key_y, compact_names[item.model_id], 29,
              anchor="start" if key_column == 0 else "end",
              fill=color, weight="600", data_direct_label="true",
              data_model_id=item.model_id, data_layout_role="direct-label")
        start_x = max(x_high, x) + 12
        # Top-to-bottom channels run right-to-left.  Together with increasing
        # lower passages this nesting prevents any two orthogonal guides from
        # crossing.
        channel_x = 309 - index * 5
        if key_column == 0:
            route = [
                (start_x, y), (channel_x, y),
                (channel_x, leader_y), (313.0, leader_y),
            ]
        else:
            right_index = sum(
                1 for prior in ordered_inputs[:index]
                if key_positions[prior.model_id][2] == 1
            )
            passage_y = 282 + right_index * 4
            right_channel = 584 + right_index * 4
            route = [
                (start_x, y), (channel_x, y),
                (channel_x, passage_y), (right_channel, passage_y),
                (right_channel, leader_y), (578.0, leader_y),
            ]
        routes[item.model_id] = route
        pending_leaders.append((item.model_id, frontier_color))
    for model_id, frontier_color in pending_leaders:
        _add(root, "path", {
            "d": _leader_path_with_bridges(routes, model_id), "fill": "none",
            "stroke": frontier_color, "stroke-width": "2",
            "data-leader": "true", "data-pareto-leader": "true",
            "data-model-id": model_id,
        })
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
        if key == "accelerators_and_hours":
            roots.append(_render_accelerators(series, names))
        else:
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
