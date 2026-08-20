import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
import pytest
import yaml

from ai_model_dashboard import build_figure_specs
from gen_ai_model_dashboard import (
    ECI_PATH,
    DATA_PATH,
    SVG_FILENAMES,
    render_dashboard,
    render_figure,
    write_svg,
)


SVG_NS = "{http://www.w3.org/2000/svg}"
EXPECTED_FILENAMES = (
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


@pytest.fixture(scope="module")
def figure_specs():
    corpus = {
        "ledger": yaml.safe_load(DATA_PATH.read_text(encoding="utf-8")),
        "eci": yaml.safe_load(ECI_PATH.read_text(encoding="utf-8")),
    }
    return build_figure_specs(corpus)


@pytest.fixture(scope="module")
def essential_specs(figure_specs):
    return tuple(spec for spec in figure_specs if spec.route == "essential")


def test_renderer_has_no_cross_model_lines(essential_specs):
    """A temporal comparison must never imply a trajectory between models."""
    fig = render_figure(essential_specs[0], None)
    try:
        assert not [
            line
            for ax in fig.axes
            for line in ax.lines
            if line.get_linestyle() not in {"None", "none", ""}
        ]
    finally:
        plt.close(fig)


def test_renderer_preserves_accessible_theme_sizes(essential_specs):
    """Resetting the theme inside render must not shrink text to Seaborn defaults."""
    fig = render_figure(essential_specs[0], None)
    try:
        ax = fig.axes[0]
        assert ax.title.get_fontsize() >= 19
        assert ax.xaxis.label.get_fontsize() >= 16
        assert ax.yaxis.label.get_fontsize() >= 16
    finally:
        plt.close(fig)


def test_renderer_wraps_long_titles_and_limits_pareto_ticks(essential_specs):
    """Long questions and automatic log ticks must not leave the viewBox."""
    temporal = render_figure(essential_specs[0], None)
    pareto = render_figure(
        next(spec for spec in essential_specs if spec.figure_id == "pareto_inference"),
        None,
    )
    try:
        assert "\n" in temporal.axes[0].get_title()
        assert "\n" in pareto.axes[0].get_title()
        assert len(pareto.axes[0].get_xticks()) <= 4
    finally:
        plt.close(temporal)
        plt.close(pareto)


def test_large_axis_values_use_compact_scientific_labels(essential_specs):
    """FLOP ticks above the SI prefix range must not become billion-digit labels."""
    spec = next(spec for spec in essential_specs if spec.figure_id == "training_flop")
    fig = render_figure(spec, None)
    try:
        fig.canvas.draw()
        labels = [label.get_text() for label in fig.axes[0].get_yticklabels()]
        assert any("e" in label for label in labels)
        assert max(map(len, labels)) <= 9
    finally:
        plt.close(fig)


def test_renderer_keeps_primary_text_inside_canvas(figure_specs):
    """Titles, axis labels and direct labels must not be clipped by the SVG canvas."""
    failures = []
    for spec in figure_specs:
        fig = render_figure(spec, None)
        try:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            canvas = fig.bbox
            ax = fig.axes[0]
            artists = [ax.title, ax.xaxis.label, ax.yaxis.label, *ax.texts]
            for artist in artists:
                bounds = artist.get_window_extent(renderer=renderer)
                if (
                    bounds.x0 < canvas.x0 - 1
                    or bounds.y0 < canvas.y0 - 1
                    or bounds.x1 > canvas.x1 + 1
                    or bounds.y1 > canvas.y1 + 1
                ):
                    failures.append((spec.figure_id, artist.get_text(), bounds.bounds))
        finally:
            plt.close(fig)

    assert not failures


def test_renderer_draws_declared_intervals_without_seaborn_estimation(figure_specs):
    """Dropping low/high would turn bounded evidence into an exact point."""
    spec = next(spec for spec in figure_specs if spec.figure_id == "training_flop")
    expected_intervals = sum(row.low != row.high for row in spec.rows)

    fig = render_figure(spec, None)
    try:
        intervals = [
            artist
            for ax in fig.axes
            for artist in ax.collections
            if isinstance(artist, LineCollection)
            and (artist.get_gid() or "").startswith("interval-")
        ]
        assert len(intervals) == expected_intervals
    finally:
        plt.close(fig)


def test_pareto_uses_one_uncertainty_rectangle_per_candidate(figure_specs):
    """A Pareto center point alone cannot reconstruct interval dominance."""
    spec = next(spec for spec in figure_specs if spec.figure_id == "pareto_inference")

    fig = render_figure(spec, None)
    try:
        rectangles = [
            artist
            for ax in fig.axes
            for artist in ax.patches
            if isinstance(artist, Rectangle)
            and (artist.get_gid() or "").startswith("interval-")
        ]
        assert len(rectangles) == len(spec.rows)
        assert not [line for ax in fig.axes for line in ax.lines]
    finally:
        plt.close(fig)


def test_svg_has_one_accessible_identity(tmp_path, essential_specs):
    """Regeneration must not duplicate or omit the SVG accessible name."""
    path = tmp_path / "figure.svg"
    write_svg(essential_specs[0], path)
    root = ET.parse(path).getroot()
    titles = root.findall(f"{SVG_NS}title")
    descriptions = root.findall(f"{SVG_NS}desc")

    assert root.attrib["role"] == "img"
    assert len(titles) == 1 and titles[0].attrib["id"].endswith("-title")
    assert len(descriptions) == 1 and descriptions[0].attrib["id"].endswith("-desc")
    assert root.attrib["aria-labelledby"] == (
        f"{titles[0].attrib['id']} {descriptions[0].attrib['id']}"
    )
    assert essential_specs[0].question in descriptions[0].text


def test_svg_preserves_one_metadata_group_per_figure_row(tmp_path, figure_specs):
    """A rendered mark without its source row breaks visual/table equivalence."""
    spec = next(spec for spec in figure_specs if spec.figure_id == "training_flop")
    path = tmp_path / spec.filename
    write_svg(spec, path)
    root = ET.parse(path).getroot()
    marks = [
        node for node in root.iter()
        if node.attrib.get("data-quantitative") == "true"
    ]

    assert len(marks) == len(spec.rows)
    assert [node.attrib["data-model-id"] for node in marks] == [
        row.model_id for row in spec.rows
    ]
    assert all(node.attrib["data-source-ids"] for node in marks)
    assert all(float(node.attrib["data-low"]) > 0 for node in marks)
    assert all(float(node.attrib["data-high"]) >= float(node.attrib["data-low"])
               for node in marks)


def test_generator_loads_combined_corpus_and_writes_exact_manifest(tmp_path):
    """Calling build_figure_specs with only the ledger would lose ECI Pareto rows."""
    paths = render_dashboard(DATA_PATH, ECI_PATH, tmp_path)

    assert SVG_FILENAMES == EXPECTED_FILENAMES
    assert tuple(path.name for path in paths) == EXPECTED_FILENAMES
    assert {path.name for path in tmp_path.glob("*.svg")} == set(EXPECTED_FILENAMES)
    pareto = ET.parse(tmp_path / "ai-dashboard-pareto-inference.svg").getroot()
    assert sum(
        node.attrib.get("data-frontier") in {"safe", "possible", "dominated"}
        for node in pareto.iter()
    ) == 8


def test_svg_generation_is_byte_deterministic(tmp_path):
    """A timestamp, random jitter or unstable SVG ID must change no checked-in byte."""
    first = render_dashboard(DATA_PATH, ECI_PATH, tmp_path / "first")
    second = render_dashboard(DATA_PATH, ECI_PATH, tmp_path / "second")

    assert [path.read_bytes() for path in first] == [path.read_bytes() for path in second]
    forbidden = (b"<dc:date", b"timestamp", b"generated-at")
    assert all(
        not any(token in path.read_bytes().lower() for token in forbidden)
        for path in first
    )
