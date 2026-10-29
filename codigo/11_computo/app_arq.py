"""Servidor experimental de la clase 11.2 (demostraciones D1 y D2).

Un solo worker: el estado vive en la memoria del proceso.
Lanzar desde esta carpeta:  python -m uvicorn app_arq:app --port 8765
"""
import asyncio
import contextlib
import json
import os
import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse



@contextlib.asynccontextmanager
async def vida(_app):
    tarea = asyncio.create_task(_latido())
    yield
    tarea.cancel()


app = FastAPI(title="app_arq", lifespan=vida)

# Estado en memoria del proceso (por eso un solo worker).
E = {"evento": None, "consultas": 0, "esperando": 0, "sse": 0,
     "max_gap": 0.0, "ticks": 0}


async def _latido():
    """Tarea de fondo: cada 0.01 s mide el hueco entre ticks del loop."""
    previo = time.monotonic()
    while True:
        await asyncio.sleep(0.01)
        ahora = time.monotonic()
        E["max_gap"] = max(E["max_gap"], ahora - previo)
        E["ticks"] += 1
        previo = ahora


def _quien(**extra):
    return {"pid": os.getpid(), "hilo": threading.current_thread().name, **extra}


def _listo() -> bool:
    return E["evento"] is not None and time.monotonic() >= E["evento"]


@app.get("/quien")
async def quien():
    """Proceso e hilo que atienden la petición."""
    return _quien()


@app.get("/def-bloqueante")
def def_bloqueante(s: float = 0.5):
    """`def` síncrono: corre en el pool de hilos; duerme s segundos."""
    time.sleep(s)
    return _quien(s=s)


@app.get("/async-bloqueante")
async def async_bloqueante(s: float = 0.5):
    """`async def` que bloquea el loop a propósito con time.sleep."""
    time.sleep(s)
    return _quien(s=s)


@app.post("/inicia")
async def inicia(t: float = 10):
    """Fija el evento para dentro de t segundos y reinicia contadores."""
    E.update(evento=time.monotonic() + t, consultas=0)
    return {"listo_en": t, "evento": E["evento"]}


@app.get("/listo")
async def listo():
    """Polling: responde de inmediato; cuenta cada consulta."""
    E["consultas"] += 1
    return {"listo": _listo()}


@app.get("/espera")
async def espera():
    """Long polling: espera (asyncio) hasta el evento o 30 s."""
    E["esperando"] += 1
    try:
        limite = time.monotonic() + 30
        while not _listo() and time.monotonic() < limite:
            await asyncio.sleep(0.05)
        return {"listo": _listo()}
    finally:
        E["esperando"] -= 1


@app.get("/eventos")
async def eventos(request: Request):
    """SSE: heartbeat cada ~1 s y `event: listo` al ocurrir el evento."""
    async def flujo():
        E["sse"] += 1
        try:
            ultimo = 0.0
            while True:
                if _listo():
                    datos = json.dumps({"listo": True})
                    yield f"event: listo\ndata: {datos}\n\n"
                    return
                if await request.is_disconnected():
                    return
                if time.monotonic() - ultimo >= 1:
                    yield ": latido\n\n"
                    ultimo = time.monotonic()
                await asyncio.sleep(0.05)
        finally:
            E["sse"] -= 1

    return StreamingResponse(flujo(), media_type="text/event-stream")


@app.get("/latido")
async def latido():
    """Hueco máximo entre ticks del loop y número de ticks desde el reinicio."""
    return {"max_gap": E["max_gap"], "ticks": E["ticks"]}


@app.get("/estado")
async def estado():
    """Consultas de polling, long polling y SSE abiertos ahora."""
    return {"consultas": E["consultas"], "esperando": E["esperando"],
            "sse": E["sse"], "pid": os.getpid()}


@app.post("/reinicia")
async def reinicia():
    """Pone todo a cero (el contador de abiertos lo llevan las conexiones)."""
    E.update(evento=None, consultas=0, max_gap=0.0, ticks=0)
    return {"ok": True}
