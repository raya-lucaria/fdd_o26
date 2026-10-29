"""Guarda de codigo/11_computo/app_arq.py (demostraciones D1 y D2 de la 11.2)."""
import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("uvicorn")
httpx = pytest.importorskip("httpx")

CARPETA = Path(__file__).resolve().parent.parent / "codigo/11_computo"


@pytest.fixture(scope="module")
def base():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app_arq:app", "--port", str(puerto),
         "--log-level", "warning"],
        cwd=CARPETA, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{puerto}"
    try:
        fin = time.monotonic() + 15
        while True:
            assert p.poll() is None, "uvicorn salió antes de responder"
            try:
                httpx.get(url + "/quien", timeout=1)
                break
            except httpx.HTTPError:
                assert time.monotonic() < fin, "el servidor no respondió a tiempo"
                time.sleep(0.1)
        yield url
    finally:
        p.terminate()
        try:
            p.wait(5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()


def test_quien(base):
    r = httpx.get(base + "/quien").json()
    assert isinstance(r["pid"], int) and r["hilo"]


async def _doce(base, ruta, s):
    lim = httpx.Limits(max_connections=13, max_keepalive_connections=13)
    async with httpx.AsyncClient(base_url=base, limits=lim, timeout=20) as c:
        t0 = time.monotonic()
        rs = await asyncio.gather(*[c.get(ruta, params={"s": s}) for _ in range(12)])
        return time.monotonic() - t0, [r.json() for r in rs]


def test_def_vs_async_bloqueante(base):
    s = 0.2
    t_def, rd = asyncio.run(_doce(base, "/def-bloqueante", s))
    t_async, ra = asyncio.run(_doce(base, "/async-bloqueante", s))
    print(f"def={t_def:.2f}s async={t_async:.2f}s")
    assert t_def < 6 * s
    assert t_async > 10 * s
    assert all(r["hilo"] != "MainThread" for r in rd)  # pool de hilos
    assert len({r["hilo"] for r in ra}) == 1     # el loop
    assert len({r["pid"] for r in rd + ra}) == 1  # un solo proceso


def test_async_await_no_bloquea(base):
    t, rs = asyncio.run(_doce(base, "/async-await", 0.2))
    print(f"async-await={t:.2f}s")
    assert 0.2 <= t < 0.5
    assert all(r["s"] == 0.2 and r["hilo"] == "MainThread" for r in rs)


def test_latido_muestra_el_bloqueo_del_loop(base):
    s = 0.2
    huecos = {}
    for ruta in ("/async-bloqueante", "/def-bloqueante"):
        httpx.post(base + "/reinicia")
        asyncio.run(_doce(base, ruta, s))
        huecos[ruta] = httpx.get(base + "/latido").json()
    print(huecos)
    assert huecos["/async-bloqueante"]["max_gap"] >= 0.15
    assert huecos["/def-bloqueante"]["max_gap"] < 0.1
    assert huecos["/def-bloqueante"]["ticks"] > 0


def test_polling_long_polling_y_sse(base):
    with httpx.Client(base_url=base, timeout=10) as c:
        c.post("/reinicia")
        r = c.post("/inicia", params={"t": 2}).json()
        assert r["listo_en"] == 2 and isinstance(r["evento"], float)
        assert c.get("/listo").json() == {"listo": False}
        assert c.get("/estado").json()["consultas"] == 1
        t0 = time.monotonic()
        assert c.get("/espera").json() == {"listo": True}
        assert 1.5 < time.monotonic() - t0 < 4
        assert c.get("/listo").json() == {"listo": True}
        assert c.get("/estado").json()["esperando"] == 0
        # SSE después de reiniciar el reloj
        c.post("/inicia", params={"t": 2})
        lineas = []
        with c.stream("GET", "/eventos") as r:
            assert r.headers["content-type"].startswith("text/event-stream")
            assert c.get("/estado").json()["sse"] == 1
            for ln in r.iter_lines():
                lineas.append(ln)
        assert "event: listo" in lineas
        assert any(l.startswith("data:") for l in lineas)
        assert c.get("/estado").json()["sse"] == 0


def test_sse_se_limpia_al_desconectar(base):
    with httpx.Client(base_url=base, timeout=10) as c:
        c.post("/inicia", params={"t": 30})
        with c.stream("GET", "/eventos") as r:
            lineas = r.iter_lines()  # se conserva: soltarlo cierra el flujo
            next(lineas)
            assert c.get("/estado").json()["sse"] == 1
        time.sleep(1.5)
        assert c.get("/estado").json()["sse"] == 0
        c.post("/reinicia")
