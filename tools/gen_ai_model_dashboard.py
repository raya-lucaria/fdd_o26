#!/usr/bin/env python3
"""Render the nine AI dashboard figures from the shared view-model.

The ledger and ECI snapshot are combined before :func:`build_figure_specs` is
called. This module owns presentation and deterministic SVG output only; all
numerical derivations remain in :mod:`ai_model_dashboard`.
"""

from __future__ import annotations

import math
import locale
import os
from decimal import Decimal
from pathlib import Path
import sys
import textwrap
import xml.etree.ElementTree as ET

os.environ["TZ"] = "UTC"
os.environ["LC_ALL"] = "C.UTF-8"
locale.setlocale(locale.LC_ALL, "C.UTF-8")

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import pandas as pd
import seaborn as sns
import yaml


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from ai_model_dashboard import FigureRow, FigureSpec, build_figure_specs  # noqa: E402


ROOT = TOOLS.parent
DATA_PATH = TOOLS / "data/ai_hardware_costs.yaml"
ECI_PATH = TOOLS / "data/eci_snapshot_2026-08-18.yaml"
FONT_PATH = TOOLS / "fonts/DejaVuSans.ttf"
ASSETS_DIR = ROOT / "course/3_arquitectura_de_computadoras/_assets"
MAIN_PAGE = (
    ROOT
    / "course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md"
)
ANNEX_PAGE = (
    MAIN_PAGE.parent / "1_evidencia_dashboard/0_index.md"
)
SVG_FILENAMES = (
    "ai-dashboard-parameters.svg",
    "ai-dashboard-training-flop.svg",
    "ai-dashboard-inference-memory.svg",
    "ai-dashboard-inference-hardware.svg",
    "ai-dashboard-pareto-inference.svg",
    "ai-dashboard-training-accelerators.svg",
    "ai-dashboard-training-replacement.svg",
    "ai-dashboard-inference-power.svg",
    "ai-dashboard-inference-capex.svg",
)

TABLE_ANCHORS = {
    "parameters": "tabla-parametros",
    "training_flop": "tabla-flop-entrenamiento",
    "artifact_or_weight_floor": "tabla-memoria-inferencia",
    "h100_capacity_floor": "tabla-hardware-inferencia",
    "pareto_inference": "tabla-pareto-inferencia",
    "training_accelerators": "tabla-aceleradores-entrenamiento",
    "training_replacement_value": "tabla-reemplazo-entrenamiento",
    "inference_tdp_floor": "tabla-potencia-inferencia",
    "inference_capex_floor": "tabla-capex-inferencia",
}

TEACHING_COPY = {
    "parameters": {
        "conclusion": "El total fija almacenamiento; en MoE, el activo aproxima lo usado por token.",
        "say": "“Total” y “activo” difieren; en dense coinciden y no se duplica la marca.",
        "avoid": "Más parámetros no demuestran más calidad ni velocidad.",
        "limit": "La tabla completa enumera cada marca y fuente.",
    },
    "training_flop": {
        "conclusion": "El trabajo publicado cruza órdenes de magnitud; muchas cuentas no se divulgan.",
        "say": "FLOP mide trabajo; los ausentes no se dibujan como cero.",
        "avoid": "FLOP no es FLOP/s, duración, energía ni costo.",
        "limit": "Cada derivación exige parámetros, tokens y fórmula aplicables.",
    },
    "artifact_or_weight_floor": {
        "conclusion": "Artefacto y piso BF16 preguntan cuánto debe caber, no cómo corre.",
        "say": "El artefacto se observa; el piso es parámetros por bits entre ocho.",
        "avoid": "No incluye KV, activaciones, runtime, workspace ni reserva.",
        "limit": "Sin pesos o total aplicable, queda una ausencia.",
    },
    "h100_capacity_floor": {
        "conclusion": "Piso ÷ 80 GB, redondeado arriba, da H100-equivalentes de capacidad.",
        "say": "El mismo entero produce TDP y CAPEX accelerator-only comparables.",
        "avoid": "El resultado no es un servidor. TDP no es potencia de pared; CAPEX no es el costo real ni un SLA.",
        "limit": "Usa 700 W y USD 30,000 por H100-equivalente.",
    },
    "pareto_inference": {
        "conclusion": "Con costo y ECI declarados, hay opciones seguras, posibles o dominadas.",
        "say": "Dominar es costar no más y tener ECI no menor, con rangos incluidos.",
        "avoid": "ECI no es IQ ni selecciona el mejor modelo universal.",
        "limit": "Sólo vale para estas variantes, snapshot y frontera de costo.",
    },
    "training_accelerators": {
        "conclusion": (
            "Sólo unas cuantas publicaciones identifican una flota concurrente de "
            "entrenamiento comparable."
        ),
        "say": "El conteo concurrente es distinto de accelerator-hours.",
        "avoid": (
            "Más aceleradores no demuestra menor duración, mayor eficiencia ni una "
            "misma clase de chip."
        ),
        "limit": "Las ausencias documentadas no se reemplazan con rumores.",
    },
    "training_replacement_value": {
        "conclusion": (
            "Una banda común de USD 20,000–40,000 por plaza hace visible el orden de "
            "magnitud de cuatro flotas documentadas."
        ),
        "say": "Es un escenario de reemplazo accelerator-only al corte del curso.",
        "avoid": (
            "No reconstruye contratos históricos ni equipara el rendimiento de TPU, "
            "A100, H100 o H800."
        ),
        "limit": "Excluye servidores, red, almacenamiento, energía y personal.",
    },
    "inference_tdp_floor": {
        "conclusion": (
            "Multiplicar el piso H100-equivalente por 700 W muestra una envolvente "
            "térmica de aceleradores."
        ),
        "say": "La cifra es TDP accelerator-only derivado del mismo piso de capacidad.",
        "avoid": "TDP no es potencia de pared ni energía consumida durante una tarea.",
        "limit": "Faltan CPU, memoria, red, refrigeración, utilización y tiempo.",
    },
    "inference_capex_floor": {
        "conclusion": (
            "Multiplicar el mismo entero por USD 30,000 permite comparar CAPEX "
            "accelerator-only bajo una premisa común."
        ),
        "say": "La cuenta compara una frontera económica explícita y reproducible.",
        "avoid": "No es precio cotizado, costo del sistema ni costo total de propiedad.",
        "limit": "No incluye chasis, CPU, red, almacenamiento, soporte ni operación.",
    },
}

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
CC_NS = "http://creativecommons.org/ns#"
DC_NS = "http://purl.org/dc/elements/1.1/"
for prefix, namespace in (
    ("", SVG_NS),
    ("xlink", XLINK_NS),
    ("rdf", RDF_NS),
    ("cc", CC_NS),
    ("dc", DC_NS),
):
    ET.register_namespace(prefix, namespace)

STATUS_COLORS = {
    "FACT": "#0072B2",
    "DERIVED": "#009E73",
    "ESTIMATE": "#D55E00",
    "SCENARIO": "#CC79A7",
}
STATUS_STYLES = {
    "FACT": "solid-fill",
    "DERIVED": "light-fill",
    "ESTIMATE": "open-outline",
    "SCENARIO": "double-outline",
}
ROLE_MARKERS = ("o", "s", "D", "^", "v", "P", "X", "*")
FRONTIER_STYLES = {
    "safe": ("#0072B2", "solid"),
    "possible": ("#E69F00", "dashed"),
    "dominated": ("#6B7280", "dotted"),
}
ROLE_LEGENDS = {
    "parameters": {"total": "total", "active": "activo"},
    "artifact_or_weight_floor": {
        "documented artifact": "artefacto",
        "BF16 weight floor": "piso BF16",
    },
}
DISPLAY_LABELS = {
    "active": "activo",
    "documented artifact": "artefacto documentado",
    "BF16 weight floor": "piso de pesos BF16",
}
FRONTIER_LABELS = {
    "safe": "segura",
    "possible": "posible",
    "dominated": "dominada",
}
MODEL_SHORT_LABELS = {
    "DM_GEMMA2_27B": "Gemma 2 27B",
    "DM_GEMMA3_27B": "Gemma 3",
    "DM_GEMMA_7B": "Gemma 7B",
    "DM_LLAMA31_8B": "Llama 3.1 8B",
    "DM_LLAMA31_70B": "Llama 3.1 70B",
    "DM_QWEN2_72B": "Qwen2 72B",
    "DM_QWEN3_235B_A22B": "Qwen 3",
    "DM_DEEPSEEK_R1": "DeepSeek R1",
}
TEMPORAL_SHORT_LABELS = {
    "DM_BERT_LARGE": "BERT",
    "DM_T5_11B": "T5",
    "DM_GPT3_175B": "GPT-3",
    "DM_GOPHER_280B": "Gopher",
    "DM_BLOOM_176B": "BLOOM",
    "DM_OPT_175B": "OPT",
    "DM_PALM_540B": "PaLM",
    "DM_DEEPSEEK_V3": "DeepSeek",
    "DM_LLAMA31_405B": "Llama 3.1",
}
FIGURE_Y_LABELS = {
    "parameters": "mil millones de parámetros",
    "training_flop": "FLOP",
    "artifact_or_weight_floor": "GB decimales",
    "h100_capacity_floor": "H100-equivalentes",
    "pareto_inference": "Índice ECI",
    "training_accelerators": "Aceleradores concurrentes",
    "training_replacement_value": "USD accelerator-only",
    "inference_tdp_floor": "W accelerator-only",
    "inference_capex_floor": "USD accelerator-only",
}

if FONT_PATH.is_file():
    fontManager.addfont(FONT_PATH)

THEME_RC = {
    "font.family": "DejaVu Sans",
    "svg.fonttype": "none",
    "svg.hashsalt": "fdd-o26-ai-dashboard",
    "axes.titleweight": "bold",
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 16,
    "figure.dpi": 100,
    "savefig.dpi": 100,
}
mpl.rcParams.update(THEME_RC)


def _center(low: Decimal | float, high: Decimal | float, scale: str) -> float:
    """Return a display center without changing the declared interval."""
    low = float(low)
    high = float(high)
    if low == high:
        return low
    if scale == "log":
        return math.sqrt(low * high)
    return (low + high) / 2


def _role_markers(rows: tuple[FigureRow, ...]) -> dict[str, str]:
    roles = tuple(dict.fromkeys(row.label for row in rows))
    return {
        role: ROLE_MARKERS[index % len(ROLE_MARKERS)]
        for index, role in enumerate(roles)
    }


def _frame_for(spec: FigureSpec) -> pd.DataFrame:
    records = []
    for index, row in enumerate(spec.rows):
        records.append({
            "row_index": index,
            "model_id": row.model_id,
            "display_year": row.year + row.x_offset,
            "value": _center(row.low, row.high, spec.y_scale),
            "cost": (
                _center(row.cost_low, row.cost_high, "log")
                if row.cost_low is not None and row.cost_high is not None
                else None
            ),
            "status": row.status,
            "role": row.label,
        })
    return pd.DataFrame.from_records(records)


def _style_scatter(artist, status: str) -> None:
    color = STATUS_COLORS[status]
    artist.set_edgecolor(color)
    if status == "FACT":
        artist.set_facecolor(color)
        artist.set_linewidth(1.2)
        artist.set_alpha(1)
    elif status == "DERIVED":
        artist.set_facecolor(color)
        artist.set_linewidth(2)
        artist.set_alpha(0.48)
    elif status == "ESTIMATE":
        artist.set_facecolor("none")
        artist.set_linewidth(2.3)
        artist.set_alpha(1)
    else:
        artist.set_facecolor("white")
        artist.set_linewidth(1.8)
        artist.set_alpha(1)


def _scatter_artist(
    ax,
    spec: FigureSpec,
    frame: pd.DataFrame,
    index: int,
    role_markers: dict[str, str],
    *,
    size: float,
    zorder: int,
):
    x_column = "cost" if spec.x_scale == "log_cost" else "display_year"
    before = len(ax.collections)
    sns.scatterplot(
        data=frame.iloc[[index]],
        x=x_column,
        y="value",
        hue="status",
        style="role",
        palette=STATUS_COLORS,
        markers=role_markers,
        hue_order=tuple(STATUS_COLORS),
        style_order=tuple(role_markers),
        legend=False,
        s=size,
        zorder=zorder,
        ax=ax,
    )
    return ax.collections[before]


def _scatter_rows(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    role_markers = _role_markers(spec.rows)
    for index, row in enumerate(spec.rows):
        if row.status == "SCENARIO":
            outer = _scatter_artist(
                ax, spec, frame, index, role_markers, size=165, zorder=3
            )
            outer.set_gid(f"scenario-outline-{index:03d}")
            outer.set_facecolor("none")
            outer.set_edgecolor(STATUS_COLORS[row.status])
            outer.set_linewidth(1.8)
        artist = _scatter_artist(
            ax,
            spec,
            frame,
            index,
            role_markers,
            size=88 if row.status == "SCENARIO" else 105,
            zorder=4,
        )
        artist.set_gid(f"mark-{index:03d}")
        _style_scatter(artist, row.status)


def _draw_temporal_intervals(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    for index, row in enumerate(spec.rows):
        if row.low == row.high:
            continue
        center = float(frame.iloc[index]["value"])
        low = float(row.low)
        high = float(row.high)
        container = ax.errorbar(
            float(frame.iloc[index]["display_year"]),
            center,
            yerr=((center - low,), (high - center,)),
            fmt="none",
            ecolor=STATUS_COLORS[row.status],
            elinewidth=2,
            capsize=0,
            alpha=0.78,
            zorder=2,
        )
        for collection in container.lines[2]:
            collection.set_gid(f"interval-{index:03d}")


def _draw_pareto_intervals(ax, spec: FigureSpec) -> None:
    for index, row in enumerate(spec.rows):
        color, linestyle = FRONTIER_STYLES[row.frontier]
        cost_low = float(row.cost_low)
        cost_high = float(row.cost_high)
        width = cost_high - cost_low
        left = cost_low
        if width == 0:
            left = cost_low / 1.018
            width = cost_low * (1.018 - 1 / 1.018)
        high = float(row.high)
        low = float(row.low)
        height = high - low
        bottom = low
        if height == 0:
            height = max(low * 0.012, 0.5)
            bottom = low - height / 2
        rectangle = Rectangle(
            (left, bottom),
            width,
            height,
            facecolor=color,
            fill=True,
            alpha=0.14,
            edgecolor=color,
            linewidth=2.4,
            linestyle=linestyle,
            zorder=2,
        )
        rectangle.set_gid(f"interval-{index:03d}")
        ax.add_patch(rectangle)


def _format_si(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1e18:
        exponent = math.floor(math.log10(absolute))
        coefficient = value / 10 ** exponent
        rendered = f"{coefficient:.1f}".rstrip("0").rstrip(".")
        return f"{rendered}e{exponent}"
    for divisor, suffix in (
        (1e15, "P"),
        (1e12, "T"),
        (1e9, "mil M"),
        (1e6, "M"),
        (1e3, "mil"),
    ):
        if absolute >= divisor:
            scaled = value / divisor
            if abs(scaled) < 10:
                return f"{scaled:.1f} {suffix}"
            return f"{scaled:.0f} {suffix}"
    return f"{value:.1f}" if absolute < 10 else f"{value:.0f}"


def _format_decimal_scale(value: float, divisor: float) -> str:
    scaled = value / divisor
    if abs(scaled) >= 1:
        return f"{scaled:,.0f}".replace(",", " ")
    return f"{scaled:.2f}".rstrip("0").rstrip(".")


def _short_model_id(model_id: str) -> str:
    compact = model_id.removeprefix("DM_").replace("_", " ")
    return compact if len(compact) <= 14 else compact[:13] + "…"


def _add_direct_labels(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    if spec.x_scale == "log_cost":
        _add_pareto_labels(ax, spec, frame)
        return
    labelled = set()
    for index, row in enumerate(spec.rows):
        if row.model_id not in spec.direct_label_ids or row.model_id in labelled:
            continue
        labelled.add(row.model_id)
        annotation = ax.annotate(
            TEMPORAL_SHORT_LABELS.get(row.model_id, _short_model_id(row.model_id)),
            (
                float(frame.iloc[index]["display_year"]),
                float(frame.iloc[index]["value"]),
            ),
            xytext=(12, 12),
            textcoords="offset points",
            fontsize=16,
            fontweight="bold",
            color="#111827",
            ha="left",
            va="bottom",
            arrowprops={
                "arrowstyle": "-",
                "color": "#6B7280",
                "linewidth": 0.8,
                "shrinkA": 2,
                "shrinkB": 6,
            },
            zorder=5,
        )
        annotation.set_gid(f"direct-label-{index:03d}")


def _add_pareto_labels(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    for index, row in enumerate(spec.rows):
        key = ax.annotate(
            str(index + 1),
            (float(frame.iloc[index]["cost"]), float(frame.iloc[index]["value"])),
            xytext=(-12, 12),
            textcoords="offset points",
            fontsize=16,
            fontweight="bold",
            color="#111827",
            ha="right",
            va="bottom",
            zorder=6,
        )
        key.set_gid(f"pareto-key-{index:03d}")
    safe_rows = [
        (index, row)
        for index, row in enumerate(spec.rows)
        if row.frontier == "safe"
    ][:5]
    for index, row in safe_rows:
        label = ax.annotate(
            MODEL_SHORT_LABELS[row.model_id],
            (float(frame.iloc[index]["cost"]), float(frame.iloc[index]["value"])),
            xytext=(12, 12),
            textcoords="offset points",
            fontsize=16,
            fontweight="bold",
            color=FRONTIER_STYLES["safe"][0],
            ha="left",
            va="bottom",
            arrowprops={
                "arrowstyle": "-",
                "color": FRONTIER_STYLES["safe"][0],
                "linewidth": 0.8,
                "shrinkA": 2,
                "shrinkB": 6,
            },
            zorder=6,
        )
        label.set_gid(f"direct-label-{index:03d}")


def _add_legends(ax, spec: FigureSpec) -> None:
    present = tuple(status for status in STATUS_COLORS if any(
        row.status == status for row in spec.rows
    ))
    handles = []
    for status in present:
        filled = status in {"FACT", "DERIVED"}
        handles.append(Line2D(
            [], [],
            linestyle="none",
            marker="o",
            markersize=8,
            markerfacecolor=STATUS_COLORS[status] if filled else "none",
            markeredgecolor=STATUS_COLORS[status],
            markeredgewidth={"FACT": 1.2, "DERIVED": 2, "ESTIMATE": 2.3, "SCENARIO": 3}[status],
            alpha=0.5 if status == "DERIVED" else 1,
            label=status,
        ))
    if spec.figure_id in ROLE_LEGENDS:
        role_markers = _role_markers(spec.rows)
        handles.extend([
            Line2D(
                [], [], linestyle="none", marker=role_markers[role],
                markersize=8, markerfacecolor="white", markeredgecolor="#374151",
                label=label,
            )
            for role, label in ROLE_LEGENDS[spec.figure_id].items()
        ])

    if spec.x_scale == "log_cost":
        frontier_handles = [
            Patch(
                facecolor="white",
                edgecolor=color,
                linewidth=2,
                linestyle=linestyle,
                label={
                    "safe": "segura",
                    "possible": "posible",
                    "dominated": "dominada",
                }[frontier],
            )
            for frontier, (color, linestyle) in FRONTIER_STYLES.items()
        ]
        handles.extend(frontier_handles)

    if not handles:
        return
    legend = ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.04, 0.65, 0.92, 0),
        bbox_transform=ax.figure.transFigure,
        frameon=False,
        ncols=2,
        mode="expand",
        borderaxespad=0,
        handlelength=0.8,
        handletextpad=0.3,
        columnspacing=0.7,
    )
    status_labels = set(present)
    role_labels = set(ROLE_LEGENDS.get(spec.figure_id, {}).values())
    frontier_labels = {"segura", "posible", "dominada"}
    for index, text in enumerate(legend.get_texts()):
        label = text.get_text()
        if label in status_labels:
            text.set_gid(f"status-legend-{index:02d}")
        elif label in role_labels:
            text.set_gid(f"role-legend-{index:02d}")
        elif label in frontier_labels:
            text.set_gid(f"frontier-legend-{index:02d}")


def _boxes_intersect(first, second, pad: float = 8) -> bool:
    return not (
        first.x1 + pad <= second.x0
        or second.x1 + pad <= first.x0
        or first.y1 + pad <= second.y0
        or second.y1 + pad <= first.y0
    )


def _place_labels(fig, ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    """Choose deterministic callout positions clear of every plotted mark."""
    annotations = [
        text for text in ax.texts
        if (text.get_gid() or "").startswith(("direct-label-", "pareto-key-"))
    ]
    if not annotations:
        return
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes_box = ax.get_window_extent(renderer=renderer)
    x_column = "cost" if spec.x_scale == "log_cost" else "display_year"
    mark_boxes = []
    for _, record in frame.iterrows():
        x, y = ax.transData.transform((record[x_column], record["value"]))
        mark_boxes.append(
            mpl.transforms.Bbox.from_extents(x - 10, y - 10, x + 10, y + 10)
        )
    placed = []
    candidates = [
        (dx, dy)
        for distance in (
            (12, 30, 50, 70, 90, 110)
            if spec.x_scale == "log_cost"
            else (12, 30)
        )
        for dx, dy in (
            (12, distance), (-12, distance),
            (12, -distance), (-12, -distance),
            (distance, 12), (-distance, 12),
            (distance, -12), (-distance, -12),
            (distance, distance), (-distance, distance),
            (distance, -distance), (-distance, -distance),
        )
    ]
    for annotation in annotations:
        selected = None
        selected_offset = None
        for dx, dy in candidates:
            annotation.set_position((dx, dy))
            annotation.set_ha("left" if dx > 0 else "right")
            annotation.set_va("bottom" if dy > 0 else "top")
            bounds = mpl.text.Text.get_window_extent(annotation, renderer=renderer)
            inside = (
                bounds.x0 >= axes_box.x0 + 2
                and bounds.x1 <= axes_box.x1 - 2
                and bounds.y0 >= axes_box.y0 + 2
                and bounds.y1 <= axes_box.y1 - 2
            )
            if inside and not any(
                _boxes_intersect(bounds, other) for other in (*mark_boxes, *placed)
            ):
                selected = bounds
                selected_offset = (dx, dy)
                break
        if selected is None:
            if spec.x_scale != "log_cost":
                annotation.remove()
                continue
            selected = mpl.text.Text.get_window_extent(annotation, renderer=renderer)
            selected_offset = annotation.get_position()
        if annotation.arrow_patch is not None:
            annotation.arrow_patch.set_visible(
                max(map(abs, selected_offset)) > 15
            )
        placed.append(selected)


def _configure_axes(ax, spec: FigureSpec) -> None:
    title = "\n".join(textwrap.wrap(
        spec.question,
        width=16,
        break_long_words=False,
        break_on_hyphens=False,
    ))
    ax.set_title(title, pad=126)
    ax.grid(True, which="major", color="#D1D5DB", linewidth=0.8, alpha=0.8)
    ax.grid(False, which="minor")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel(FIGURE_Y_LABELS[spec.figure_id])
    if spec.x_scale == "log_cost":
        ax.set_xscale("log")
        ax.set_xlabel("CAPEX accelerator-only\n(USD, escala logarítmica)")
        ticks = sorted({
            _center(row.cost_low, row.cost_high, "log")
            for row in spec.rows
        })
        if len(ticks) > 4:
            picks = (
                0,
                round((len(ticks) - 1) / 3),
                round(2 * (len(ticks) - 1) / 3),
                len(ticks) - 1,
            )
            ticks = [ticks[index] for index in dict.fromkeys(picks)]
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelrotation=90)
        ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(
            lambda value, _position: _format_si(value)
        ))
        ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    else:
        ax.set_xlabel("Año de publicación")
        ax.set_xticks(range(2018, 2027))
        ax.set_xlim(2017.6, 2026.4)
        ax.tick_params(axis="x", labelrotation=90)
    if spec.y_scale == "log":
        ax.set_yscale("log")
    if spec.figure_id == "parameters":
        y_formatter = lambda value, _position: _format_decimal_scale(value, 1e9)
    elif spec.figure_id == "artifact_or_weight_floor":
        y_formatter = lambda value, _position: _format_decimal_scale(value, 1e9)
    else:
        y_formatter = lambda value, _position: _format_si(value)
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(y_formatter))


def _absence_text(spec: FigureSpec) -> str | None:
    if spec.absence is None:
        return None
    counts = ", ".join(
        f"{name}: {count}"
        for name, count in spec.absence.counts.items()
        if count
    )
    if not counts:
        return None
    return (
        f"Ausencias auditadas ({spec.absence.searched_on}): {counts}. "
        "No se grafican como cero."
    )


def render_figure(spec: FigureSpec, path: Path | None):
    """Render one spec with Seaborn and optionally write its canonical SVG."""
    sns.set_theme(
        style="whitegrid",
        context="notebook",
        font="DejaVu Sans",
        rc=THEME_RC,
    )
    fig, ax = plt.subplots(figsize=(334 / 72, 720 / 72), constrained_layout=False)
    frame = _frame_for(spec)
    if spec.x_scale == "log_cost":
        _draw_pareto_intervals(ax, spec)
    else:
        _draw_temporal_intervals(ax, spec, frame)
    _scatter_rows(ax, spec, frame)
    _add_direct_labels(ax, spec, frame)
    _configure_axes(ax, spec)
    _add_legends(ax, spec)
    fig.subplots_adjust(left=0.30, right=0.96, top=0.62, bottom=0.25)
    _place_labels(fig, ax, spec, frame)
    absence = _absence_text(spec)
    if absence:
        fig.text(
            0.05,
            0.035,
            "\n".join(textwrap.wrap(
                absence,
                width=30,
                break_long_words=False,
                break_on_hyphens=False,
            )),
            ha="left",
            va="bottom",
            fontsize=16,
            linespacing=1.3,
            color="#4B5563",
        )
    if spec.snapshot_date:
        snapshot = fig.text(
            0.97,
            0.035,
            f"Snapshot ECI: {spec.snapshot_date}",
            ha="right",
            va="bottom",
            fontsize=16,
            color="#4B5563",
        )
        snapshot.set_gid("snapshot-date")
    if path is not None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            path,
            format="svg",
            metadata={"Creator": "fdd-o26-ai-dashboard", "Date": None},
        )
        canonicalize_svg(path, spec)
    return fig


def _number(value: Decimal | float) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    return format(value, ".15g")


def _row_attributes(
    row: FigureRow, index: int, y_scale: str, role_marker: str
) -> dict[str, str]:
    value = _center(row.low, row.high, y_scale)
    attrs = {
        "data-quantitative": "true",
        "data-row-index": str(index),
        "data-model-id": row.model_id,
        "data-role": row.label,
        "data-status": row.status,
        "data-confidence": row.confidence,
        "data-low": _number(row.low),
        "data-high": _number(row.high),
        "data-value": _number(value),
        "data-unit": row.unit,
        "data-claim-scope": row.scope,
        "data-source-ids": " ".join(row.source_ids),
        "data-marker": role_marker,
        "data-status-style": STATUS_STYLES[row.status],
    }
    if row.cost_low is not None and row.cost_high is not None:
        attrs.update({
            "data-cost-low": _number(row.cost_low),
            "data-cost-high": _number(row.cost_high),
            "data-frontier": row.frontier,
        })
    return attrs


def _description(spec: FigureSpec) -> str:
    text = f"{spec.question} La figura contiene {len(spec.rows)} observaciones."
    if spec.x_scale == "log_cost":
        text += (
            " El costo usa escala logarítmica y ECI usa escala lineal; "
            "los rectángulos conservan los rangos declarados."
        )
        text += f" Snapshot ECI: {spec.snapshot_date}."
    elif spec.y_scale == "log":
        text += " El eje vertical usa escala logarítmica; no hay líneas que unan modelos."
    else:
        text += " No hay líneas que unan modelos."
    absence = _absence_text(spec)
    if absence:
        text += f" {absence}"
    return text


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def canonicalize_svg(path: Path, spec: FigureSpec) -> None:
    """Add stable accessibility/row metadata and serialize in a fixed order."""
    path = Path(path)
    root = ET.parse(path).getroot()
    for child in list(root):
        if _local_name(child.tag) in {"title", "desc"}:
            root.remove(child)

    title_id = f"{spec.figure_id}-title"
    desc_id = f"{spec.figure_id}-desc"
    title = ET.Element(f"{{{SVG_NS}}}title", {"id": title_id})
    title.text = spec.question
    desc = ET.Element(f"{{{SVG_NS}}}desc", {"id": desc_id})
    desc.text = _description(spec)
    root.insert(0, title)
    root.insert(1, desc)
    root.attrib.update({
        "role": "img",
        "aria-labelledby": f"{title_id} {desc_id}",
        "data-figure-id": spec.figure_id,
        "data-route": spec.route,
        "style": "max-width:100%;height:auto",
    })
    if spec.x_scale == "log_cost":
        root.attrib["data-pareto-table-map"] = ";".join(
            f"{index}={row.model_id}"
            for index, row in enumerate(spec.rows, 1)
        )

    by_id = {
        node.attrib["id"]: node
        for node in root.iter()
        if "id" in node.attrib
    }
    role_markers = _role_markers(spec.rows)
    for index, row in enumerate(spec.rows):
        mark = by_id.get(f"mark-{index:03d}")
        if mark is None:
            raise ValueError(f"SVG lost mark {index} for {spec.figure_id}")
        mark.attrib.update(_row_attributes(
            row, index, spec.y_scale, role_markers[row.label]
        ))
        outer = by_id.get(f"scenario-outline-{index:03d}")
        if outer is not None:
            outer.attrib.update({
                "data-scenario-outline": "true",
                "data-outline-for": str(index),
            })
        interval = by_id.get(f"interval-{index:03d}")
        if interval is not None:
            interval.attrib.update({
                "data-interval-geometry": "true",
                "data-row-index": str(index),
            })
        direct = by_id.get(f"direct-label-{index:03d}")
        if direct is not None:
            text_node = next(
                node for node in direct.iter()
                if _local_name(node.tag) == "text"
            )
            text_node.attrib["data-direct-label"] = "true"
        key = by_id.get(f"pareto-key-{index:03d}")
        if key is not None:
            text_node = next(
                node for node in key.iter()
                if _local_name(node.tag) == "text"
            )
            text_node.attrib["data-pareto-key"] = str(index + 1)

    for prefix, attribute in (
        ("role-legend-", "data-role-legend"),
        ("frontier-legend-", "data-frontier-legend"),
    ):
        for element_id, group in by_id.items():
            if not element_id.startswith(prefix):
                continue
            text_node = next(
                node for node in group.iter()
                if _local_name(node.tag) == "text"
            )
            text_node.attrib[attribute] = "true"

    for node in root.iter():
        dates = [key for key in node.attrib if _local_name(key).lower() == "date"]
        for key in dates:
            del node.attrib[key]
        if node.attrib:
            ordered = sorted(node.attrib.items())
            node.attrib.clear()
            node.attrib.update(ordered)

    ET.indent(root, space="  ")
    xml = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + xml + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_svg(spec: FigureSpec, path: Path) -> Path:
    """Write one figure and close its Matplotlib resources."""
    fig = render_figure(spec, path)
    plt.close(fig)
    return Path(path)


def _markdown_number(value: Decimal | int | float) -> str:
    """Render a stable, compact value without changing its declared precision."""
    number = value if isinstance(value, Decimal) else Decimal(str(value))
    if number == number.to_integral_value():
        return f"{number:,.0f}"
    return format(number, "f").rstrip("0").rstrip(".")


def _markdown_range(
    low: Decimal | int | float, high: Decimal | int | float
) -> str:
    if low == high:
        return _markdown_number(low)
    return f"{_markdown_number(low)}–{_markdown_number(high)}"


def _escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _model_names(ledger: dict) -> dict[str, str]:
    return {
        model["id"]: model["canonical_name"]
        for model in ledger["dashboard_models"]
    }


def _compact_reading(spec: FigureSpec, row: FigureRow) -> str:
    value = _markdown_range(row.low, row.high)
    if spec.figure_id == "parameters":
        value = _markdown_range(row.low / Decimal("1e9"), row.high / Decimal("1e9"))
        return (
            f"{value} mil millones; {DISPLAY_LABELS.get(row.label, row.label)}; "
            f"**{row.status}**"
        )
    if spec.figure_id == "training_flop":
        value = (
            format(row.low, ".3g")
            if row.low == row.high
            else f"{format(row.low, '.3g')}–{format(row.high, '.3g')}"
        )
        return f"{value} FLOP; **{row.status}**"
    if spec.figure_id == "artifact_or_weight_floor":
        value = _markdown_range(row.low / Decimal("1e9"), row.high / Decimal("1e9"))
        return f"{value} GB; {DISPLAY_LABELS.get(row.label, row.label)}; **{row.status}**"
    if spec.figure_id == "h100_capacity_floor":
        low_h100 = int(row.low)
        high_h100 = int(row.high)
        h100 = str(low_h100) if low_h100 == high_h100 else f"{low_h100}–{high_h100}"
        watts = _markdown_range(row.low * 700, row.high * 700)
        capex = _markdown_range(row.low * 30_000, row.high * 30_000)
        return (
            f"{h100} H100-equivalente(s); {watts} W TDP y USD {capex} CAPEX, "
            f"**{row.status}**"
        )
    if spec.figure_id == "pareto_inference":
        cost = _markdown_range(row.cost_low, row.cost_high)
        return (
            f"ECI {value}; USD {cost}; frontera {FRONTIER_LABELS[row.frontier]}, "
            f"**{row.status}**"
        )
    return (
        f"{value} {row.unit}; {DISPLAY_LABELS.get(row.label, row.label)}; "
        f"**{row.status}**"
    )


def _alt_text(spec: FigureSpec) -> str:
    copy = TEACHING_COPY[spec.figure_id]
    return f"{spec.question} {copy['conclusion']} Límite: {copy['limit']}"


def _sentinel(spec: FigureSpec, content: str) -> str:
    return (
        f"[AI_DASHBOARD:{spec.figure_id}:START]: "
        f"<#dashboard-{spec.figure_id}-start>\n\n"
        f"{content.rstrip()}\n\n"
        f"[AI_DASHBOARD:{spec.figure_id}:END]: "
        f"<#dashboard-{spec.figure_id}-end>"
    )


def _compact_table(spec: FigureSpec, names: dict[str, str]) -> str:
    lines = ["| Modelo | Lectura |", "|---|---|"]
    for row in spec.compact_rows:
        name = names[row.model_id]
        if spec.figure_id == "pareto_inference":
            name = f"{spec.rows.index(row) + 1} · {name}"
        cells = [
            f"**{_escape_cell(name)}**",
            _escape_cell(_compact_reading(spec, row)),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _pareto_key(spec: FigureSpec, names: dict[str, str]) -> str:
    if spec.figure_id != "pareto_inference":
        return ""
    mapping = "; ".join(
        f"{index} = {names[row.model_id]}"
        for index, row in enumerate(spec.rows, 1)
    )
    return f"**Clave de la gráfica:** {mapping}."


def _full_table(spec: FigureSpec, names: dict[str, str]) -> str:
    headers = [
        "Modelo e ID", "Año", "Valor o rango", "Unidad", "Estado",
        "Confianza", "Alcance", "Fuentes",
    ]
    aligns = ["---", "---:", "---:", "---", "---", "---", "---", "---"]
    if spec.figure_id == "pareto_inference":
        headers.insert(0, "Clave")
        aligns.insert(0, "---:")
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(aligns) + "|"]
    for index, row in enumerate(spec.rows, 1):
        value = _markdown_range(row.low, row.high)
        unit = row.unit
        if row.cost_low is not None and row.cost_high is not None:
            value = (
                f"ECI {value}; costo USD "
                f"{_markdown_range(row.cost_low, row.cost_high)}"
            )
            unit = "ECI y USD"
        frontier = (
            f"; frontera {FRONTIER_LABELS[row.frontier]}" if row.frontier else ""
        )
        cells = [
            _escape_cell(
                f"{names[row.model_id]} · `{row.model_id}` · "
                f"{DISPLAY_LABELS.get(row.label, row.label)}"
            ),
            str(row.year),
            _escape_cell(value),
            _escape_cell(unit),
            f"`{row.status}`{frontier}",
            f"`{row.confidence}`",
            _escape_cell(row.scope),
            _escape_cell(", ".join(f"`{source}`" for source in row.source_ids)),
        ]
        if spec.figure_id == "pareto_inference":
            cells.insert(0, str(index))
        lines.append(
            "| " + " | ".join(cells) + " |"
        )
    return "\n".join(lines)


def _essential_block(index: int, spec: FigureSpec, names: dict[str, str]) -> str:
    copy = TEACHING_COPY[spec.figure_id]
    anchor = TABLE_ANCHORS[spec.figure_id]
    content = f"""### {index}. {spec.question}

![{_alt_text(spec)}](../_assets/{spec.filename})

{_pareto_key(spec, names)}

**Conclusión:** {copy['conclusion']} **Di esto:** {copy['say']} **No concluyas esto:** {copy['avoid']}

{_compact_table(spec, names)}

**Límite:** {copy['limit']} Ve la [tabla completa](raya:evidencia-dashboard-ia#{anchor}) para año, rango, confianza y fuentes.
"""
    return _sentinel(spec, content)


def _full_table_block(
    spec: FigureSpec,
    names: dict[str, str],
    *,
    include_visual: bool,
) -> str:
    copy = TEACHING_COPY[spec.figure_id]
    parts = []
    if include_visual:
        parts.extend((
            f"### {spec.question}",
            f"![{_alt_text(spec)}](../../_assets/{spec.filename})",
            f"**Conclusión:** {copy['conclusion']}",
            f"**Di esto:** {copy['say']}",
            f"**No concluyas esto:** {copy['avoid']}",
            f"**Límite:** {copy['limit']}",
        ))
    parts.extend((
        f"### {TABLE_ANCHORS[spec.figure_id]}",
        (
            f"Tabla equivalente completa de `{spec.filename}`. Cada fila procede "
            "del mismo `FigureSpec` que dibuja la marca; el desplazamiento visual "
            "del año no cambia el año exacto mostrado aquí."
        ),
        _full_table(spec, names),
    ))
    return _sentinel(spec, "\n\n".join(parts))


def _master_cards(ledger: dict) -> str:
    groups = (
        ("Google", {"Google"}),
        ("OpenAI y Anthropic", {"OpenAI", "Anthropic"}),
        ("Meta y BigScience", {"Meta", "BigScience"}),
        ("Qwen", {"Qwen"}),
        ("DeepSeek y Mistral", {"DeepSeek", "Mistral AI"}),
        ("xAI y Moonshot", {"xAI", "Moonshot AI"}),
    )
    models = ledger["dashboard_models"]
    sections = []
    for heading, organizations in groups:
        lines = [f"##### {heading}", "", "| Modelo · año | Ficha física |", "|---|---|"]
        for model in models:
            if model["organization"] not in organizations:
                continue
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
            lines.append(
                f"| **{model['canonical_name']} · {model['year']['value']}** | "
                f"{openness} · {architecture} · E: {training} · I: {inference} |"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _main_dashboard(specs: tuple[FigureSpec, ...], ledger: dict) -> str:
    names = _model_names(ledger)
    essentials = [spec for spec in specs if spec.route == "essential"]
    blocks = [
        "### En 30 segundos\n\n"
        "Empieza por pregunta y unidad: cada figura tiene un eje Y. **FACT** se publica; "
        "**DERIVED** se calcula; **ESTIMATE** acota; **SCENARIO** supone. "
        "**no publicado** es ausencia, nunca cero.",
        "### Cómo leer el dashboard\n\n"
        "X muestra el año; el desplazamiento sólo separa marcas. En Y logarítmico, igual distancia significa multiplicar. **Confianza** califica evidencia, no calidad. **FLOP es trabajo**; **FLOP/s es una tasa**.\n\n"
        "La ruta pregunta por **parámetros totales** y **parámetros activos**, trabajo, memoria, hardware y costo–ECI. Lee visual, conclusión, frase defendible, inferencia prohibida, tabla y límite.\n\n"
        "Antes de comparar, identifica qué representa una marca: modelo y variante, año, unidad y estado de evidencia. Dos puntos próximos no describen la misma arquitectura ni el mismo experimento. Los intervalos conservan incertidumbre o escenarios explícitos; no autorizan escoger su centro como si fuera una medición. Si falta una cifra, la ausencia sigue visible en la auditoría, pero no entra al eje numérico.\n\n"
        "Después separa tres preguntas. **Escala** pregunta cuánto se almacena o calcula. **Capacidad** pregunta qué cabe bajo una precisión y una memoria declaradas. **Decisión** cruza una métrica de costo con ECI para descartar opciones dominadas. Ninguna responde por sí sola sobre latencia, throughput, energía de pared, calidad universal o costo total de propiedad; esas afirmaciones requieren variables y mediciones adicionales.\n\n"
        "Una comparación defendible nombra siempre su frontera: variante exacta, fecha del snapshot, precisión, alcance accelerator-only y fuente. Usa la tabla compacta para explicar la idea y la tabla completa para auditar el número. Si cambias una premisa, vuelve a calcular antes de trasladar la conclusión a otro modelo o sistema.",
    ]
    blocks.extend(
        _essential_block(index, spec, names)
        for index, spec in enumerate(essentials, start=1)
    )
    blocks.extend((
        "### Qué sí y qué no puedes concluir\n\n"
        "**Sí puedes decir:** “El estado y la unidad están declarados”, “el artefacto "
        "exige esta capacidad”, “no está dominado bajo estos ejes” y “la magnitud "
        "cambia por órdenes”. **No puedes decir:** “Un faltante vale cero”, “garantiza "
        "throughput o latencia”, “es mejor para cualquier tarea” ni “FLOP, watts o "
        "USD miden calidad”.",
        "**Fin de la ruta esencial. Continúa al anexo sólo si deseas profundizar.** "
        "[[evidencia-dashboard-ia]] conserva tabla maestra, cuatro vistas y nueve tablas. "
        "No hay Pareto de entrenamiento: las cuatro flotas no intersectan variantes ECI "
        "elegibles. **Recapitulación:** Total almacena y activo aproxima trabajo MoE. Trabajo, tasa, tiempo, flota y "
        "potencia difieren. Un piso responde “¿cabe?”, no “¿cumple SLA?”. TDP no es "
        "pared y CAPEX parcial no es costo real. ECI no es IQ: Pareto descarta, no decide.",
    ))
    return "\n\n".join(blocks)


def _annex_generated(specs: tuple[FigureSpec, ...], ledger: dict) -> str:
    names = _model_names(ledger)
    optional = [spec for spec in specs if spec.route == "annex"]
    essentials = [spec for spec in specs if spec.route == "essential"]
    parts = [(
        "Estas cuatro vistas no forman parte de la ruta oral esencial. Separan "
        "flota, valor de reemplazo, potencia y CAPEX para que una transformación "
        "no parezca un hallazgo independiente. El Pareto usa el Snapshot ECI "
        "fechado que se documenta en la metodología."
    )]
    parts.extend(_full_table_block(spec, names, include_visual=True) for spec in optional)
    parts.extend((
        "## Tablas completas equivalentes a las nueve visuales",
        (
            "Las cinco tablas restantes corresponden a la ruta esencial. Junto con "
            "las cuatro anteriores, contienen una fila por cada marca dibujada."
        ),
    ))
    parts.extend(_full_table_block(spec, names, include_visual=False) for spec in essentials)
    return "\n\n".join(parts)


def _replace_section(text: str, start: str, end: str, replacement: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"cannot find Markdown section boundaries: {start!r}, {end!r}")
    prefix, remainder = text.split(start, 1)
    _old, suffix = remainder.split(end, 1)
    return f"{prefix}{start}\n\n{replacement.rstrip()}\n\n{end}{suffix}"


def write_dashboard_markdown(
    specs: tuple[FigureSpec, ...],
    ledger: dict,
    main_path: Path = MAIN_PAGE,
    annex_path: Path = ANNEX_PAGE,
) -> tuple[Path, Path]:
    """Regenerate the main route, master ledger, optional views, and full tables."""
    main_path = Path(main_path)
    annex_path = Path(annex_path)
    main = main_path.read_text(encoding="utf-8")
    main = _replace_section(
        main,
        "## Dashboard: modelos, hardware y costo",
        "## Guía de decisión",
        _main_dashboard(specs, ledger),
    )
    main_path.write_text(main, encoding="utf-8", newline="\n")

    annex = annex_path.read_text(encoding="utf-8")
    intro = (
        "**Anexo opcional.** Conserva el detalle que haría ilegible la ruta oral, "
        "pero no forma parte del recorrido principal de la clase. El corte del ledger "
        "es **2026-08-18**. Regresa a [[ia-escala-decision]] para explicar las cinco "
        "gráficas esenciales; usa esta página para auditar una celda o profundizar.\n\n"
        "## Tabla maestra de 39 modelos\n\n"
        "Esta tabla vive fuera de la ruta esencial. Resume acceso, arquitectura y la "
        "frontera de evidencia de entrenamiento e inferencia; los registros verticales "
        "posteriores conservan las 546 celdas completas.\n\n"
        + _master_cards(ledger)
    )
    annex = _replace_section(
        annex,
        "# Evidencia del dashboard de modelos de IA",
        "## Estados y frontera de la afirmación",
        intro,
    )
    retired_heading = "## Tablas reconstruibles de las doce visuales"
    if retired_heading in annex:
        annex = annex.replace(retired_heading, "## Profundización opcional", 1)
    generated_start = "## Profundización opcional"
    annex = _replace_section(
        annex,
        generated_start,
        "## Fuentes",
        _annex_generated(specs, ledger),
    )
    annex_path.write_text(annex, encoding="utf-8", newline="\n")
    return main_path, annex_path


def render_dashboard(
    ledger_path: Path = DATA_PATH,
    eci_path: Path = ECI_PATH,
    assets_dir: Path = ASSETS_DIR,
) -> list[Path]:
    """Load ledger+ECI, build the shared specs, and write the exact manifest."""
    ledger = yaml.safe_load(Path(ledger_path).read_text(encoding="utf-8"))
    eci = yaml.safe_load(Path(eci_path).read_text(encoding="utf-8"))
    specs = build_figure_specs({"ledger": ledger, "eci": eci})
    filenames = tuple(spec.filename for spec in specs)
    if filenames != SVG_FILENAMES:
        raise ValueError(f"FigureSpec manifest differs from renderer: {filenames!r}")
    assets_dir = Path(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    return [write_svg(spec, assets_dir / spec.filename) for spec in specs]


def main() -> None:
    ledger = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))
    eci = yaml.safe_load(ECI_PATH.read_text(encoding="utf-8"))
    specs = build_figure_specs({"ledger": ledger, "eci": eci})
    for output in render_dashboard():
        print(output.relative_to(ROOT))
    for output in write_dashboard_markdown(specs, ledger):
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
