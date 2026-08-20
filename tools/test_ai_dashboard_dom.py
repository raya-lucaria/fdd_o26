"""Mandatory Chromium guardrails for the dashboard built by Raya."""

import base64
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
import subprocess
from threading import Thread

from playwright.sync_api import sync_playwright
import pytest
import yaml

from ai_model_dashboard import build_figure_specs
from tools.raya_test_support import resolve_raya_checkout


ROOT = Path(__file__).resolve().parents[1]
MAIN_URL = "/arquitectura-de-computadoras/ai-escala-y-decision/index.html"
ANNEX_URL = MAIN_URL.replace("index.html", "evidencia-dashboard/index.html")
VIEWPORTS = (
    pytest.param({"width": 390, "height": 844}, id="mobile-390"),
    pytest.param({"width": 1440, "height": 900}, id="desktop-1440"),
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


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve the built artifact without flooding pytest output."""

    def log_message(self, _format, *_args):
        pass


@pytest.fixture(scope="module")
def specs():
    return build_figure_specs({
        "ledger": yaml.safe_load(
            (ROOT / "tools/data/ai_hardware_costs.yaml").read_text(
                encoding="utf-8"
            )
        ),
        "eci": yaml.safe_load(
            (ROOT / "tools/data/eci_snapshot_2026-08-18.yaml").read_text(
                encoding="utf-8"
            )
        ),
    })


@pytest.fixture(scope="module")
def model_names():
    ledger = yaml.safe_load(
        (ROOT / "tools/data/ai_hardware_costs.yaml").read_text(encoding="utf-8")
    )
    return {
        model["id"]: model["canonical_name"]
        for model in ledger["dashboard_models"]
    }


@contextmanager
def serve_built_site():
    raya = resolve_raya_checkout(ROOT)
    subprocess.run(
        ["uv", "run", "raya", "build", str(ROOT)],
        cwd=raya,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": ".venv-local"},
        check=True,
        stdout=subprocess.DEVNULL,
    )
    handler = partial(QuietHandler, directory=ROOT / "artifact/site")
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


@pytest.fixture(scope="module")
def built_site():
    with serve_built_site() as url:
        yield url


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        yield browser
        browser.close()


def table_after_heading(page, heading_id):
    return page.locator(f'[id="{heading_id}"]').locator(
        "xpath=following-sibling::table[1]"
    )


def compact_table_for(page, question):
    return page.locator("h3").filter(has_text=question).locator(
        "xpath=following-sibling::table[1]"
    )


def inspect_rendered_svg(image):
    """Measure external SVG text at the exact CSS width chosen by Raya."""
    return image.evaluate(
        """async image => {
          const response = await fetch(image.currentSrc || image.src);
          if (!response.ok) throw new Error(`SVG fetch failed: ${response.status}`);
          const source = await response.text();
          const documentNode = new DOMParser().parseFromString(
            source, 'image/svg+xml'
          );
          const parseError = documentNode.querySelector('parsererror');
          if (parseError) throw new Error(parseError.textContent);
          const svg = documentNode.documentElement;
          const imageBox = image.getBoundingClientRect();
          const host = document.createElement('div');
          Object.assign(host.style, {
            position: 'fixed', left: '0', top: '0', width: `${imageBox.width}px`,
            opacity: '0', pointerEvents: 'none', zIndex: '-1'
          });
          svg.style.width = `${imageBox.width}px`;
          svg.style.height = 'auto';
          svg.style.maxWidth = 'none';
          svg.style.display = 'block';
          host.appendChild(svg);
          document.body.appendChild(host);
          await document.fonts.ready;
          await new Promise(resolve => requestAnimationFrame(resolve));

          const root = svg.getBoundingClientRect();
          const scale = root.width / svg.viewBox.baseVal.width;
          const box = node => {
            const bounds = node.getBoundingClientRect();
            return {
              id: node.parentElement?.id || '',
              text: node.textContent.trim(),
              left: bounds.left, right: bounds.right,
              top: bounds.top, bottom: bounds.bottom
            };
          };
          const overlap = (first, second, tolerance = 0.5) =>
            Math.min(first.right, second.right) - Math.max(first.left, second.left)
              > tolerance &&
            Math.min(first.bottom, second.bottom) - Math.max(first.top, second.top)
              > tolerance;
          const textNodes = [...svg.querySelectorAll('text')].filter(
            node => node.textContent.trim() &&
              getComputedStyle(node).display !== 'none'
          );
          const texts = textNodes.map(box);
          const textCollisions = [];
          for (let first = 0; first < texts.length; first++) {
            for (let second = first + 1; second < texts.length; second++) {
              if (overlap(texts[first], texts[second])) {
                textCollisions.push([texts[first], texts[second]]);
              }
            }
          }
          const obstacleSelectors = {
            interval: '[data-interval-geometry="true"]',
            mark: '[data-quantitative="true"]',
            scenarioOutline: '[data-scenario-outline="true"]'
          };
          const obstacles = Object.entries(obstacleSelectors).flatMap(
            ([kind, selector]) => [...svg.querySelectorAll(selector)].map(
              node => ({...box(node), kind})
            )
          );
          const obstacleCounts = Object.fromEntries(
            Object.keys(obstacleSelectors).map(kind => [
              kind, obstacles.filter(obstacle => obstacle.kind === kind).length
            ])
          );
          const textObstacleCollisions = [];
          for (const text of texts) {
            for (const obstacle of obstacles) {
              if (overlap(text, obstacle)) {
                textObstacleCollisions.push({text, obstacle});
              }
            }
          }
          const outOfBounds = texts.filter(text =>
            text.left < root.left - 0.5 || text.right > root.right + 0.5 ||
            text.top < root.top - 0.5 || text.bottom > root.bottom + 0.5
          );
          const obstaclesOutOfBounds = obstacles.filter(obstacle =>
            obstacle.left < root.left - 0.5 ||
            obstacle.right > root.right + 0.5 ||
            obstacle.top < root.top - 0.5 ||
            obstacle.bottom > root.bottom + 0.5
          );
          const obstaclesWithoutGeometry = obstacles.filter(obstacle =>
            obstacle.right - obstacle.left <= 0.1 &&
            obstacle.bottom - obstacle.top <= 0.1
          );
          const fontSizes = textNodes.map(node =>
            parseFloat(getComputedStyle(node).fontSize) * scale
          );
          const legendCenters = [...svg.querySelectorAll(
            '[data-role-legend="true"], [data-frontier-legend="true"], '+
            '[id^="status-legend-"] text'
          )].map(node => {
            const bounds = node.getBoundingClientRect();
            return (bounds.top + bounds.bottom) / 2;
          }).sort((first, second) => first - second);
          const legendRows = [];
          for (const center of legendCenters) {
            if (!legendRows.length || center - legendRows.at(-1) > 2) {
              legendRows.push(center);
            }
          }
          const result = {
            minFontSize: Math.min(...fontSizes),
            obstacleCounts,
            obstaclesOutOfBounds,
            obstaclesWithoutGeometry,
            outOfBounds,
            textCollisions,
            textObstacleCollisions,
            legendRows: legendRows.length
          };
          host.remove();
          return result;
        }"""
    )


def inspect_table_container(table):
    """Report every vertical constraint between a full table and ``main``."""
    return table.evaluate(
        """table => {
          const rows = [...table.querySelectorAll('tbody tr')];
          const rowBoxes = rows.map(row => {
            const bounds = row.getBoundingClientRect();
            const style = getComputedStyle(row);
            return {
              top: bounds.top,
              bottom: bounds.bottom,
              width: bounds.width,
              height: bounds.height,
              visible: style.display !== 'none' &&
                !['collapse', 'hidden'].includes(style.visibility) &&
                parseFloat(style.opacity) > 0
            };
          });
          const tableBox = table.getBoundingClientRect();
          const containers = [];
          for (let node = table; node; node = node.parentElement) {
            const style = getComputedStyle(node);
            const bounds = node.getBoundingClientRect();
            const clientTop = bounds.top + node.clientTop;
            const clientBottom = clientTop + node.clientHeight;
            const clipsVertically = ['auto', 'clip', 'hidden', 'scroll']
              .includes(style.overflowY);
            const verticalOverflow = node.scrollHeight > node.clientHeight + 1;
            containers.push({
              tag: node.tagName.toLowerCase(),
              id: node.id,
              maxHeight: style.maxHeight,
              overflowY: style.overflowY,
              scrollHeight: node.scrollHeight,
              clientHeight: node.clientHeight,
              clipsRows: clipsVertically && verticalOverflow && rowBoxes.some(
                row => row.top < clientTop - 1 || row.bottom > clientBottom + 1
              )
            });
            if (node.tagName === 'MAIN') break;
          }
          const rowsRendered = rowBoxes.every(row =>
            row.width > 0 && row.height > 0 && row.visible
          );
          const rowsInsideTable = rowBoxes.every(row =>
            row.top >= tableBox.top - 1 && row.bottom <= tableBox.bottom + 1
          );
          const constrained = containers.some(container =>
            container.maxHeight !== 'none' || container.clipsRows
          );
          return {
            allRowsReachable: rowsRendered && rowsInsideTable && !constrained,
            containers,
            rowCount: rows.length,
            visibleRowCount: rowBoxes.filter(row =>
              row.width > 0 && row.height > 0 && row.visible
            ).length
          };
        }"""
    )


def test_svg_geometry_guard_rejects_mutated_quantitative_obstacles(browser):
    """Moving an interval outside the viewBox or under text must be detected."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
      <g id="fixture-label"><text x="10" y="20" font-size="16">label</text></g>
      <g data-quantitative="true"><circle cx="18" cy="15" r="5"/></g>
      <g data-interval-geometry="true"><rect x="8" y="8" width="40" height="18"/></g>
      <g data-scenario-outline="true"><circle cx="105" cy="95" r="10"/></g>
    </svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    page = browser.new_page(viewport={"width": 390, "height": 844})
    try:
        page.set_content(
            f'<img id="fixture" width="100" '
            f'src="data:image/svg+xml;base64,{encoded}">'
        )
        image = page.locator("#fixture")
        image.wait_for(state="visible")
        geometry = inspect_rendered_svg(image)

        assert geometry["obstacleCounts"] == {
            "interval": 1,
            "mark": 1,
            "scenarioOutline": 1,
        }
        assert {item["kind"] for item in geometry["obstaclesOutOfBounds"]} == {
            "scenarioOutline"
        }
        assert {
            collision["obstacle"]["kind"]
            for collision in geometry["textObstacleCollisions"]
        } == {"interval", "mark"}
    finally:
        page.close()


def test_table_guard_rejects_mutated_vertical_clipping(browser):
    """A max-height wrapper must not make complete audit rows unreachable."""
    page = browser.new_page(viewport={"width": 390, "height": 844})
    try:
        page.set_content(
            """<main><div id="clipped" style="max-height: 55px; overflow: hidden">
              <table><tbody>
                <tr><td>one</td></tr><tr><td>two</td></tr>
                <tr><td>three</td></tr><tr><td>four</td></tr>
              </tbody></table>
            </div></main>"""
        )
        layout = inspect_table_container(page.locator("table"))

        assert not layout["allRowsReachable"]
        assert any(
            container["maxHeight"] != "none"
            for container in layout["containers"]
        )
        assert any(
            container["overflowY"] in {"hidden", "clip"}
            and container["scrollHeight"] > container["clientHeight"]
            for container in layout["containers"]
        )
    finally:
        page.close()


@pytest.mark.parametrize(
    ("route", "url", "expected_count"),
    (("essential", MAIN_URL, 5), ("annex", ANNEX_URL, 4)),
)
@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_dashboard_pages_are_readable(
    browser, built_site, specs, route, url, expected_count, viewport
):
    """Both routes must remain readable in the real mobile and desktop shell."""
    page = browser.new_page(viewport=viewport)
    try:
        page.goto(built_site + url)
        page.wait_for_load_state("networkidle")

        assert (
            page.evaluate("document.documentElement.scrollWidth")
            == viewport["width"]
        )
        route_specs = [spec for spec in specs if spec.route == route]
        assert len(route_specs) == expected_count
        if route == "essential":
            dashboard = page.evaluate(
                """() => {
                  const headings = [...document.querySelectorAll('h2')];
                  const start = headings.find(node =>
                    node.textContent.includes('Dashboard:'));
                  const end = headings.find(node =>
                    node.textContent.includes('Guía de decisión'));
                  const range = document.createRange();
                  range.setStartAfter(start);
                  range.setEndBefore(end);
                  const fragment = range.cloneContents();
                  return {
                    height: end.getBoundingClientRect().top -
                      start.getBoundingClientRect().top,
                    text: fragment.textContent
                  };
                }"""
            )
            words = re.findall(
                r"[\wÁÉÍÓÚÜÑáéíóúüñ./+−-]+", dashboard["text"]
            )
            assert 8 <= dashboard["height"] / viewport["height"] <= 12
            assert 900 <= len(words) <= 1400
            assert "AI_DASHBOARD" not in dashboard["text"]
        images = page.locator('main img[src*="ai-dashboard-"]')
        assert images.count() == expected_count
        assert [Path(source).name for source in images.evaluate_all(
            "nodes => nodes.map(node => new URL(node.currentSrc || node.src).pathname)"
        )] == [spec.filename for spec in route_specs]

        boxes = []
        for index, spec in enumerate(route_specs):
            image = images.nth(index)
            alt = image.get_attribute("alt") or ""
            assert spec.question in alt
            assert "Límite:" in alt
            bounds = image.bounding_box()
            assert bounds is not None
            assert bounds["width"] >= 334
            assert bounds["x"] >= 0
            assert bounds["x"] + bounds["width"] <= viewport["width"]
            boxes.append(bounds)

            geometry = inspect_rendered_svg(image)
            expected_intervals = (
                len(spec.rows)
                if spec.x_scale == "log_cost"
                else sum(row.low != row.high for row in spec.rows)
            )
            assert geometry["obstacleCounts"] == {
                "interval": expected_intervals,
                "mark": len(spec.rows),
                "scenarioOutline": sum(
                    row.status == "SCENARIO" for row in spec.rows
                ),
            }, (spec.filename, geometry["obstacleCounts"])
            assert geometry["minFontSize"] >= 15.95, (
                spec.filename, geometry["minFontSize"]
            )
            assert not geometry["outOfBounds"], (
                spec.filename, "out of bounds", geometry["outOfBounds"]
            )
            assert not geometry["textCollisions"], (
                spec.filename, "text collisions", geometry["textCollisions"]
            )
            assert not geometry["obstaclesOutOfBounds"], (
                spec.filename,
                "quantitative geometry out of bounds",
                geometry["obstaclesOutOfBounds"],
            )
            assert not geometry["obstaclesWithoutGeometry"], (
                spec.filename,
                "empty quantitative geometry",
                geometry["obstaclesWithoutGeometry"],
            )
            assert not geometry["textObstacleCollisions"], (
                spec.filename,
                "text/quantitative geometry collisions",
                geometry["textObstacleCollisions"],
            )
            assert geometry["legendRows"] <= 2, (
                spec.filename, geometry["legendRows"]
            )

        assert all(
            following["y"] >= previous["y"] + previous["height"]
            for previous, following in zip(boxes, boxes[1:])
        )
    finally:
        page.close()


def test_main_compact_tables_link_to_matching_annex_tables(
    browser, built_site, specs, model_names
):
    """Every essential chart needs its two-column table and stable audit link."""
    page = browser.new_page(viewport={"width": 390, "height": 844})
    try:
        page.goto(built_site + MAIN_URL)
        page.wait_for_load_state("networkidle")
        essential = [spec for spec in specs if spec.route == "essential"]
        assert len(essential) == 5
        for spec in essential:
            table = compact_table_for(page, spec.question)
            assert table.count() == 1
            assert table.locator("th").all_inner_texts() == ["Modelo", "Lectura"]
            assert table.locator("tbody tr").count() == len(spec.compact_rows)
            assert 4 <= len(spec.compact_rows) <= 6

        links = page.locator('main a', has_text=re.compile(r"^tabla completa$"))
        assert links.count() == 5
        expected_hrefs = [
            built_site + ANNEX_URL + "#" + TABLE_ANCHORS[spec.figure_id]
            for spec in essential
        ]
        assert (
            links.evaluate_all("nodes => nodes.map(node => node.href)")
            == expected_hrefs
        )
        pareto_spec = next(
            spec for spec in essential if spec.figure_id == "pareto_inference"
        )
        key_text = page.locator("p", has_text="Clave de la gráfica:").inner_text()
        assert key_text == "Clave de la gráfica: " + "; ".join(
            f"{index} = {model_names[row.model_id]}"
            for index, row in enumerate(pareto_spec.rows, 1)
        ) + "."
    finally:
        page.close()


def test_annex_has_four_figures_and_nine_complete_equivalent_tables(
    browser, built_site, specs
):
    """The annex must expose one complete row per plotted mark and Pareto key."""
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(built_site + ANNEX_URL)
        page.wait_for_load_state("networkidle")
        assert page.locator('main img[src*="ai-dashboard-"]').count() == 4
        assert "AI_DASHBOARD" not in page.locator("body").inner_text()
        for spec in specs:
            table = table_after_heading(page, TABLE_ANCHORS[spec.figure_id])
            assert table.count() == 1
            assert table.locator("tbody tr").count() == len(spec.rows)

        pareto_spec = next(
            spec for spec in specs if spec.figure_id == "pareto_inference"
        )
        pareto = table_after_heading(page, TABLE_ANCHORS[pareto_spec.figure_id])
        assert pareto.locator("th").all_inner_texts()[0] == "Clave"
        assert pareto.locator("tbody tr td:first-child").all_inner_texts() == [
            str(index) for index in range(1, 9)
        ]
    finally:
        page.close()


@pytest.mark.parametrize("viewport", VIEWPORTS)
def test_annex_full_tables_have_no_vertical_clipping(
    browser, built_site, specs, viewport
):
    """Every full row must remain rendered without a capped scroll container."""
    page = browser.new_page(viewport=viewport)
    try:
        page.goto(built_site + ANNEX_URL)
        page.wait_for_load_state("networkidle")
        for spec in specs:
            table = table_after_heading(page, TABLE_ANCHORS[spec.figure_id])
            layout = inspect_table_container(table)
            assert layout["rowCount"] == len(spec.rows)
            assert layout["visibleRowCount"] == len(spec.rows)
            assert layout["allRowsReachable"], (spec.figure_id, layout)
            assert not [
                container
                for container in layout["containers"]
                if container["maxHeight"] != "none"
            ], (spec.figure_id, layout["containers"])
            assert not [
                container
                for container in layout["containers"]
                if container["overflowY"] in {"hidden", "clip"}
            ], (spec.figure_id, layout["containers"])
            assert all(
                container["scrollHeight"] <= container["clientHeight"] + 1
                for container in layout["containers"]
                if container["overflowY"] in {"auto", "scroll"}
            ), (spec.figure_id, layout["containers"])
    finally:
        page.close()


def test_optional_annex_rail_title_is_not_stacked_character_by_character(
    browser, built_site
):
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(built_site + MAIN_URL)
        page.wait_for_load_state("networkidle")
        title = page.locator(
            '[data-raya-map-node="evidencia-dashboard-ia"] '
            ".raya-course-map-node-title"
        )
        bounds = title.bounding_box()
        assert bounds is not None
        assert bounds["width"] >= 90
        assert bounds["height"] <= 100
        assert title.inner_text().startswith("Anexo opcional")
    finally:
        page.close()
