"""Browser guardrails for the real Raya dashboard DOM."""

from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import subprocess
from threading import Thread

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
RAYA = ROOT.parents[2] / "raya_lucaria" / ".worktrees" / "navigation-first-course-rail"
URL = "/arquitectura-de-computadoras/ai-escala-y-decision/index.html"


@contextmanager
def built_site():
    subprocess.run(
        ["uv", "run", "raya", "build", str(ROOT)], cwd=RAYA,
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

            images = page.locator(
                'img[src*="ai-training-"], img[src*="ai-inference-"], img[src*="ai-pareto-"]'
            )
            assert images.count() == 12
            boxes = [images.nth(index).bounding_box() for index in range(images.count())]
            assert all(box and box["width"] >= 320 and box["height"] < 600 for box in boxes)
            for index in range(images.count()):
                effective = images.nth(index).evaluate(
                    """image => {
                      const vb = image.naturalWidth;
                      return 27 * image.getBoundingClientRect().width / vb;
                    }"""
                )
                assert effective >= 16
        browser.close()
