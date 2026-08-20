import os
from pathlib import Path
import subprocess
import sys
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


def test_repositioned_direct_labels_keep_leader_lines(figure_specs):
    """Collision-free callouts must still identify their source marks."""
    for spec in figure_specs:
        fig = render_figure(spec, None)
        try:
            direct = [
                text for text in fig.axes[0].texts
                if (text.get_gid() or "").startswith("direct-label-")
            ]
            assert all(
                text.arrow_patch is not None and text.arrow_patch.get_visible()
                for text in direct
                if max(map(abs, text.get_position())) > 15
            )
        finally:
            plt.close(fig)


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


def test_training_accelerator_view_excludes_accelerator_hours(figure_specs):
    """Mixing accelerator-hours into a fleet-count chart compares unlike units."""
    spec = next(
        spec for spec in figure_specs if spec.figure_id == "training_accelerators"
    )

    assert {row.label for row in spec.rows} == {"concurrent accelerators"}
    assert all("hour" not in row.unit.lower() for row in spec.rows)


def test_pareto_svg_maps_all_keys_and_explains_frontier(tmp_path, figure_specs):
    """Every Pareto candidate needs a visible key and the safe set needs names."""
    spec = next(spec for spec in figure_specs if spec.figure_id == "pareto_inference")
    path = tmp_path / spec.filename
    write_svg(spec, path)
    root = ET.parse(path).getroot()
    keyed = [node for node in root.iter() if node.attrib.get("data-pareto-key")]
    direct = [
        node for node in root.iter()
        if node.attrib.get("data-direct-label") == "true"
    ]
    text = " ".join(root.itertext())

    assert spec.snapshot_date == "2026-08-18"
    assert [node.attrib["data-pareto-key"] for node in keyed] == [
        str(index) for index in range(1, 9)
    ]
    assert root.attrib["data-pareto-table-map"] == ";".join(
        f"{index}={row.model_id}" for index, row in enumerate(spec.rows, 1)
    )
    assert {"segura", "posible", "dominada"} <= {
        node.text for node in root.iter() if node.attrib.get("data-frontier-legend")
    }
    assert "Snapshot ECI: 2026-08-18" in text
    assert len(direct) <= 5
    assert {"Gemma 3", "Qwen 3"} <= {node.text for node in direct}


def test_role_legends_are_orthogonal_to_status(tmp_path, figure_specs):
    """Total/active and artifact/floor cannot rely on status color for meaning."""
    expected = {
        "parameters": {"total", "activo"},
        "artifact_or_weight_floor": {"artefacto", "piso BF16"},
    }
    for figure_id, labels in expected.items():
        spec = next(spec for spec in figure_specs if spec.figure_id == figure_id)
        path = tmp_path / spec.filename
        write_svg(spec, path)
        root = ET.parse(path).getroot()
        legends = {
            node.text for node in root.iter()
            if node.attrib.get("data-role-legend") == "true"
        }
        assert legends == labels


def test_scenario_marks_have_two_real_outline_artists(tmp_path, figure_specs):
    """A thick single stroke is not the documented SCENARIO double outline."""
    spec = next(spec for spec in figure_specs if spec.figure_id == "h100_capacity_floor")
    path = tmp_path / spec.filename
    write_svg(spec, path)
    root = ET.parse(path).getroot()
    scenarios = [
        node for node in root.iter()
        if node.attrib.get("data-status") == "SCENARIO"
    ]
    outlines = [
        node for node in root.iter()
        if node.attrib.get("data-scenario-outline") == "true"
    ]

    assert scenarios
    assert len(outlines) == len(scenarios)
    assert {node.attrib["data-outline-for"] for node in outlines} == {
        node.attrib["data-row-index"] for node in scenarios
    }


def test_axes_use_pedagogical_units_and_complete_year_ticks(figure_specs):
    """Bytes/B abbreviations and sparse years obscure the stated comparison."""
    for spec in figure_specs:
        fig = render_figure(spec, None)
        try:
            fig.canvas.draw()
            ax = fig.axes[0]
            if spec.x_scale == "year":
                assert list(ax.get_xticks()) == list(range(2018, 2027))
            if spec.figure_id == "parameters":
                assert ax.get_ylabel() == "mil millones de parámetros"
                assert "1" in {label.get_text() for label in ax.get_yticklabels()}
            if spec.figure_id == "artifact_or_weight_floor":
                assert ax.get_ylabel() == "GB decimales"
                assert all("e" not in label.get_text().lower()
                           for label in ax.get_yticklabels())
        finally:
            plt.close(fig)


def test_generator_forces_reproducible_locale_and_timezone():
    """Inherited TZ/locale settings must not change labels or SVG bytes."""
    env = {**os.environ, "TZ": "Pacific/Honolulu", "LC_ALL": "C"}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os; import tools.gen_ai_model_dashboard; "
            "print(os.environ['TZ'], os.environ['LC_ALL'])",
        ],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "UTC C.UTF-8"


@pytest.mark.parametrize("width", [334, 600])
def test_all_svg_text_is_readable_and_non_overlapping(tmp_path, width):
    """Responsive scaling must preserve 16 px text and separate visual labels."""
    from playwright.sync_api import sync_playwright

    paths = render_dashboard(DATA_PATH, ECI_PATH, tmp_path / "assets")
    failures = []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": 900})
        for path in paths:
            page.set_content(
                "<style>html,body,main{margin:0;width:100%}"
                "svg{display:block;width:100%;height:auto}</style>"
                f"<main>{path.read_text(encoding='utf-8')}</main>"
            )
            layout = page.locator("svg").evaluate(
                """svg => {
                  const root = svg.getBoundingClientRect();
                  const scale = root.width / svg.viewBox.baseVal.width;
                  const box = node => {
                    const b = node.getBoundingClientRect();
                    return {x:b.x,y:b.y,r:b.right,b:b.bottom,
                            text:node.textContent.trim()};
                  };
                  const hit = (a,b,pad=1) =>
                    Math.min(a.r,b.r)-Math.max(a.x,b.x)>pad &&
                    Math.min(a.b,b.b)-Math.max(a.y,b.y)>pad;
                  const nodes = [...svg.querySelectorAll('text')]
                    .filter(node => getComputedStyle(node).display !== 'none');
                  const texts = nodes.map(box);
                  const outOfBounds=texts.filter(text =>
                    text.x < root.x-1 || text.r > root.right+1 ||
                    text.y < root.y-1 || text.b > root.bottom+1);
                  const textHits=[];
                  for(let i=0;i<texts.length;i++) for(let j=i+1;j<texts.length;j++)
                    if(hit(texts[i],texts[j])) textHits.push([texts[i],texts[j]]);
                  const labels = [...svg.querySelectorAll(
                    '[data-direct-label="true"],[data-pareto-key]')].map(box);
                  const marks = [...svg.querySelectorAll(
                    '[data-quantitative="true"]')].map(box);
                  const labelMarkHits=[];
                  for(const label of labels) for(const mark of marks)
                    if(hit(label,mark)) labelMarkHits.push([label,mark]);
                  const sizes = nodes.map(node =>
                    parseFloat(getComputedStyle(node).fontSize) * scale);
                  return {minSize:Math.min(...sizes),outOfBounds,
                          textHits,labelMarkHits};
                }"""
            )
            if layout["minSize"] < 15.95:
                failures.append((path.name, "font", layout["minSize"]))
            if layout["outOfBounds"]:
                failures.append((path.name, "bounds", [
                    (text, text) for text in layout["outOfBounds"]
                ]))
            if layout["textHits"]:
                failures.append((path.name, "text", layout["textHits"]))
            if layout["labelMarkHits"]:
                failures.append((path.name, "mark", layout["labelMarkHits"]))
        browser.close()

    assert not failures, "\n".join(
        f"{name} {kind}: "
        + (
            f"{value:.2f}px"
            if kind == "font"
            else "; ".join(
                f"{left['text']!r}@({left['x']:.0f},{left['y']:.0f}) / "
                f"{right['text']!r}@({right['x']:.0f},{right['y']:.0f})"
                for left, right in value
            )
        )
        for name, kind, value in failures
    )


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
