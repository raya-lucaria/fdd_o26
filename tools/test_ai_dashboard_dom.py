"""Browser guardrails for the real Raya dashboard DOM."""

from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import pytest
import re
import subprocess
from threading import Thread

import yaml

from ai_model_dashboard import build_figure_specs

from tools.raya_test_support import resolve_raya_checkout_or_skip


playwright_sync_api = pytest.importorskip(
    "playwright.sync_api",
    reason=(
        "Playwright is optional in dependency-light checks; the course-pages "
        "job independently validates and builds the course."
    ),
)
sync_playwright = playwright_sync_api.sync_playwright


ROOT = Path(__file__).resolve().parents[1]
URL = "/arquitectura-de-computadoras/ai-escala-y-decision/index.html"


def dashboard_specs():
    return build_figure_specs({
        "ledger": yaml.safe_load(
            (ROOT / "tools/data/ai_hardware_costs.yaml").read_text(encoding="utf-8")
        ),
        "eci": yaml.safe_load(
            (ROOT / "tools/data/eci_snapshot_2026-08-18.yaml").read_text(
                encoding="utf-8"
            )
        ),
    })


def table_after_heading(page, heading_id):
    return page.locator(f'[id="{heading_id}"]').locator(
        "xpath=following-sibling::table[1]"
    )


@contextmanager
def built_site():
    raya = resolve_raya_checkout_or_skip(ROOT)
    subprocess.run(
        ["uv", "run", "raya", "build", str(ROOT)], cwd=raya,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": ".venv-local"}, check=True,
        stdout=subprocess.DEVNULL,
    )
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(
        *args, directory=ROOT / "artifact/site", **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}{URL}"
    finally:
        server.shutdown()
        thread.join()


def test_real_raya_dashboard_has_bounded_height_and_svg_geometry():
    specs = dashboard_specs()
    essential = [spec for spec in specs if spec.route == "essential"]
    with built_site() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for width, height in ((390, 844), (1440, 900)):
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(url)
            page.wait_for_load_state("networkidle")
            headings = page.locator("h2")
            labels = headings.all_text_contents()
            start = headings.nth(next(i for i, text in enumerate(labels) if "Dashboard:" in text)).bounding_box()
            end = headings.nth(next(i for i, text in enumerate(labels) if "Guía de decisión" in text)).bounding_box()
            dashboard_height = end["y"] - start["y"]
            assert 8 <= dashboard_height / height <= 12
            assert page.evaluate("document.documentElement.scrollWidth") == width

            dashboard = page.evaluate(
                """() => {
                  const headings = [...document.querySelectorAll('h2')];
                  const start = headings.find(node => node.textContent.includes('Dashboard:'));
                  const end = headings.find(node => node.textContent.includes('Guía de decisión'));
                  const range = document.createRange();
                  range.setStartAfter(start);
                  range.setEndBefore(end);
                  const fragment = range.cloneContents();
                  return {
                    text: fragment.textContent,
                    rows: [...fragment.querySelectorAll('table')].map(
                      table => table.querySelectorAll('tbody tr').length
                    ),
                  };
                }"""
            )
            words = re.findall(
                r"[\wÁÉÍÓÚÜÑáéíóúüñ./+−-]+", dashboard["text"]
            )
            assert 900 <= len(words) <= 1400
            assert "AI_DASHBOARD" not in dashboard["text"]
            assert dashboard["rows"] == [
                len(spec.compact_rows) for spec in essential
            ]

            images = page.locator(
                'img[src*="ai-dashboard-"]'
            )
            assert images.count() == 5
            boxes = [images.nth(index).bounding_box() for index in range(images.count())]
            assert all(
                box
                and box["width"] >= 320
                and 2.14 <= box["height"] / box["width"] <= 2.16
                for box in boxes
            )
            for index in range(images.count()):
                effective = images.nth(index).evaluate(
                    """async image => {
                      const xml = await (await fetch(image.src)).text();
                      const svg = new DOMParser().parseFromString(xml, 'image/svg+xml').documentElement;
                      const vb = svg.viewBox.baseVal.width;
                      const minFont = Math.min(...[...svg.querySelectorAll('text')]
                        .map(node => parseFloat(
                          node.getAttribute('font-size') || node.style.fontSize
                        )));
                      return minFont * image.getBoundingClientRect().width / vb;
                    }"""
                )
                assert effective >= 16

            pareto = table_after_heading(
                page, "5-qu-opciones-quedan-en-la-frontera-costoeci"
            )
            assert pareto.locator("th").all_inner_texts() == [
                "Clave", "Modelo", "Lectura"
            ]
            pareto_spec = next(
                spec for spec in essential if spec.figure_id == "pareto_inference"
            )
            assert pareto.locator("tbody tr td:first-child").all_inner_texts() == [
                str(pareto_spec.rows.index(row) + 1)
                for row in pareto_spec.compact_rows
            ]
            key_text = page.locator(
                "p", has_text="Clave de la gráfica:"
            ).inner_text()
            names = {
                model["id"]: model["canonical_name"]
                for model in yaml.safe_load(
                    (ROOT / "tools/data/ai_hardware_costs.yaml").read_text(
                        encoding="utf-8"
                    )
                )["dashboard_models"]
            }
            assert key_text == "Clave de la gráfica: " + "; ".join(
                f"{index} = {names[row.model_id]}"
                for index, row in enumerate(pareto_spec.rows, 1)
            ) + "."
        browser.close()


def test_real_raya_annex_tables_have_exact_rows_and_pareto_keys():
    specs = dashboard_specs()
    with built_site() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url.replace("/index.html", "/evidencia-dashboard/index.html"))
        page.wait_for_load_state("networkidle")

        assert "AI_DASHBOARD" not in page.locator("body").inner_text()
        anchors = {
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
        for spec in specs:
            table = table_after_heading(page, anchors[spec.figure_id])
            assert table.locator("tbody tr").count() == len(spec.rows)

        pareto_spec = next(
            spec for spec in specs if spec.figure_id == "pareto_inference"
        )
        pareto = table_after_heading(page, anchors[pareto_spec.figure_id])
        assert pareto.locator("th").all_inner_texts()[0] == "Clave"
        assert pareto.locator("tbody tr td:first-child").all_inner_texts() == [
            str(index) for index in range(1, 9)
        ]
        browser.close()


def test_optional_annex_rail_title_is_not_stacked_character_by_character():
    with built_site() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url)
        page.wait_for_load_state("networkidle")
        title = page.locator(
            '[data-raya-map-node="evidencia-dashboard-ia"] '
            '.raya-course-map-node-title'
        )
        box = title.bounding_box()
        assert box is not None
        # A character-stacked label collapses near one glyph (~10–20 px) and
        # grows hundreds of pixels tall. Four ordinary wrapped lines are fine.
        assert box["width"] >= 90
        assert box["height"] <= 100
        assert title.inner_text().startswith("Anexo opcional")
        browser.close()
