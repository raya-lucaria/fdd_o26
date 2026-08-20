#!/usr/bin/env python3
"""Render the nine AI dashboard figures from the shared view-model.

The ledger and ECI snapshot are combined before :func:`build_figure_specs` is
called. This module owns presentation and deterministic SVG output only; all
numerical derivations remain in :mod:`ai_model_dashboard`.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
import sys
import textwrap
import xml.etree.ElementTree as ET

os.environ.setdefault("TZ", "UTC")

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
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
FIGURE_Y_LABELS = {
    "parameters": "Parámetros",
    "training_flop": "FLOP",
    "artifact_or_weight_floor": "Bytes",
    "h100_capacity_floor": "H100-equivalentes",
    "pareto_inference": "Índice ECI",
    "training_accelerators": "Aceleradores / horas",
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
    "axes.titlesize": 19,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 11,
    "figure.dpi": 100,
    "savefig.dpi": 100,
}
mpl.rcParams.update(THEME_RC)


def _center(low: float, high: float, scale: str) -> float:
    """Return a display center without changing the declared interval."""
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
        artist.set_facecolor("none")
        artist.set_linewidth(4)
        artist.set_alpha(1)


def _scatter_rows(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    role_markers = _role_markers(spec.rows)
    x_column = "cost" if spec.x_scale == "log_cost" else "display_year"
    for index, row in enumerate(spec.rows):
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
            s=105,
            zorder=4,
            ax=ax,
        )
        artist = ax.collections[before]
        artist.set_gid(f"mark-{index:03d}")
        _style_scatter(artist, row.status)


def _draw_temporal_intervals(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    for index, row in enumerate(spec.rows):
        if row.low == row.high:
            continue
        center = float(frame.iloc[index]["value"])
        container = ax.errorbar(
            float(frame.iloc[index]["display_year"]),
            center,
            yerr=((center - row.low,), (row.high - center,)),
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
        cost_low = row.cost_low
        cost_high = row.cost_high
        width = cost_high - cost_low
        left = cost_low
        if width == 0:
            left = cost_low / 1.018
            width = cost_low * (1.018 - 1 / 1.018)
        height = row.high - row.low
        bottom = row.low
        if height == 0:
            height = max(row.low * 0.012, 0.5)
            bottom = row.low - height / 2
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


def _short_model_id(model_id: str) -> str:
    compact = model_id.removeprefix("DM_").replace("_", " ")
    return compact if len(compact) <= 14 else compact[:13] + "…"


def _add_direct_labels(ax, spec: FigureSpec, frame: pd.DataFrame) -> None:
    labelled = set()
    x_column = "cost" if spec.x_scale == "log_cost" else "display_year"
    latest_year = max((row.year for row in spec.rows), default=0)
    for index, row in enumerate(spec.rows):
        if row.model_id not in spec.direct_label_ids or row.model_id in labelled:
            continue
        labelled.add(row.model_id)
        label = (
            str(index + 1)
            if spec.x_scale == "log_cost"
            else _short_model_id(row.model_id)
        )
        align_right = spec.x_scale == "year" and row.year >= latest_year - 1
        ax.annotate(
            label,
            (float(frame.iloc[index][x_column]), float(frame.iloc[index]["value"])),
            xytext=((-6 if align_right else 6), 7),
            textcoords="offset points",
            fontsize=13,
            fontweight="bold",
            color="#111827",
            ha="right" if align_right else "left",
            zorder=5,
        )


def _status_legend(ax, spec: FigureSpec) -> None:
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
    if handles:
        ax.legend(
            handles=handles,
            loc="upper left",
            bbox_to_anchor=(0, 1.01),
            frameon=False,
            ncols=min(4, len(handles)),
            borderaxespad=0,
            handletextpad=0.35,
            columnspacing=0.85,
        )


def _configure_axes(ax, spec: FigureSpec) -> None:
    title = "\n".join(textwrap.wrap(
        spec.question,
        width=34,
        break_long_words=False,
        break_on_hyphens=False,
    ))
    ax.set_title(title, pad=34)
    ax.grid(True, which="major", color="#D1D5DB", linewidth=0.8, alpha=0.8)
    ax.grid(False, which="minor")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel(FIGURE_Y_LABELS[spec.figure_id])
    if spec.x_scale == "log_cost":
        ax.set_xscale("log")
        ax.set_xlabel("CAPEX accelerator-only (USD, escala logarítmica)")
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
        ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(
            lambda value, _position: _format_si(value)
        ))
        ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())
    else:
        ax.set_xlabel("Año de publicación")
        years = [row.year for row in spec.rows]
        if years:
            first, last = min(years), max(years)
            ticks = list(range(first, last + 1, 2))
            if last not in ticks:
                ticks.append(last)
            ax.set_xticks(ticks)
            ax.set_xlim(first - 0.6, last + 0.6)
    if spec.y_scale == "log":
        ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
        lambda value, _position: _format_si(value)
    ))


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
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=False)
    frame = _frame_for(spec)
    if spec.x_scale == "log_cost":
        _draw_pareto_intervals(ax, spec)
    else:
        _draw_temporal_intervals(ax, spec, frame)
    _scatter_rows(ax, spec, frame)
    _add_direct_labels(ax, spec, frame)
    _configure_axes(ax, spec)
    _status_legend(ax, spec)
    fig.subplots_adjust(left=0.19, right=0.97, top=0.77, bottom=0.20)
    absence = _absence_text(spec)
    if absence:
        fig.text(
            0.14,
            0.035,
            absence,
            ha="left",
            va="bottom",
            fontsize=9.5,
            color="#4B5563",
        )
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


def _number(value: float) -> str:
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
        interval = by_id.get(f"interval-{index:03d}")
        if interval is not None:
            interval.attrib.update({
                "data-interval-geometry": "true",
                "data-row-index": str(index),
            })

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
    for output in render_dashboard():
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
