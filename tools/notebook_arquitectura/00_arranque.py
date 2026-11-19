# %% [markdown]
# # Arquitectura y concurrencia · notebook de las clases 11.2 y 11.3
#
# Este notebook acompaña las páginas 9 a 12 de la unidad 11. Es el lugar
# **verboso**: cada tema se explica antes de la celda, la celda imprime
# mensajes claros y, después, una celda «Salida esperada» dice qué debe
# aparecer. Las páginas traen sólo las celdas cortas; aquí se repite el
# contexto para que puedas ejecutar cada tema sin volver a leer la página.
#
# **Reglas de las celdas.**
#
# - Se ejecutan **en orden**, de arriba abajo. Cada celda de código empieza con
#   un rótulo `# celda N.M`; ese rótulo es el que citan las páginas.
# - Usan `await` de nivel superior: el kernel de Jupyter ya tiene un event loop
#   corriendo, así que `asyncio.run(...)` truena aquí y nunca aparece.
# - Los valores de «Salida esperada» son **cualitativos o rangos**. Los PID, los
#   nombres de hilo y los milisegundos exactos cambian en cada máquina y en
#   cada corrida; lo que debe repetirse es la **forma** del resultado.
# - Las celdas 11.1 y 12.1 lanzan su propio servidor (`app_arq.py`, un solo
#   worker) en un subproceso y lo cierran en un `finally`. No necesitas abrir
#   otra terminal.

# %% [markdown]
# ## 0.1 · Arranque: un lanzador reutilizable para el servidor de la clase
#
# El servidor de las demostraciones D1 y D2 es `app_arq.py`, una aplicación
# FastAPI que vive junto a este notebook. Guarda su estado **en la memoria del
# proceso** (el evento de D2, los contadores), por eso se lanza con **un solo
# worker** y sin `--reload`: con dos workers cada uno tendría su propia
# memoria y las mediciones no significarían lo que dicen.
#
# La celda de abajo sólo **define** dos funciones; no lanza nada todavía:
#
# - `lanza_servidor(puerto=None, plazo=20.0)` ejecuta
#   `sys.executable -m uvicorn app_arq:app --port PUERTO --workers 1` en un
#   subproceso (el `--workers 1` explícito evita que una variable de entorno
#   como `WEB_CONCURRENCY` active varios y parta el estado en memoria),
#   con la carpeta de este notebook como directorio de trabajo. Si no das
#   puerto, pide uno libre al sistema operativo. Espera, con un plazo, a que
#   `/quien` responda. Falla con un mensaje claro si el puerto ya está ocupado
#   o si el proceso termina antes de responder (y muestra el final de su log).
#   Devuelve el proceso, con la dirección en `proc.url`.
# - `detiene_servidor(proc)` pide el cierre con `terminate`, espera hasta 5 s y,
#   sólo si no cerró, lo mata con `kill`. Es seguro llamarla dos veces.
#
# El patrón de uso, en todas las celdas que miden, es siempre el mismo:
#
# ```text
# proc = lanza_servidor()
# try:
#     ...   # la medición
# finally:
#     detiene_servidor(proc)
# ```
#
# Así el servidor se cierra aunque la medición falle o interrumpas el kernel.

# %%
# celda 0.1
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

CARPETA = Path.cwd()   # Jupyter arranca el kernel en la carpeta del notebook


def puerto_libre():
    """Un puerto TCP que el sistema operativo declara libre ahora mismo."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ocupado(puerto):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def _final_del_log(proc, lineas=15):
    try:
        proc.log.flush()
        texto = Path(proc.log.name).read_text(errors="replace")
    except Exception:
        return "(sin log)"
    return "\n".join(texto.splitlines()[-lineas:]) or "(log vacío)"


def lanza_servidor(puerto=None, plazo=20.0):
    """Arranca app_arq con UN worker y espera a que /quien responda."""
    if not (CARPETA / "app_arq.py").is_file():
        raise FileNotFoundError(f"no encuentro app_arq.py en {CARPETA}")
    puerto = puerto or puerto_libre()
    if _ocupado(puerto):
        raise RuntimeError(f"el puerto {puerto} ya está ocupado: elige otro")
    log = tempfile.NamedTemporaryFile("w+", prefix="app_arq_", suffix=".log",
                                      delete=False)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app_arq:app",
         "--port", str(puerto), "--workers", "1",
         "--log-level", "warning"],
        cwd=CARPETA, stdout=log, stderr=subprocess.STDOUT)
    proc.log = log
    proc.url = f"http://127.0.0.1:{puerto}"
    try:
        limite = time.monotonic() + plazo
        while time.monotonic() < limite:
            if proc.poll() is not None:
                raise RuntimeError(f"el servidor terminó antes de responder "
                                   f"(código {proc.returncode}). Final de su "
                                   f"log:\n{_final_del_log(proc)}")
            try:
                with urllib.request.urlopen(proc.url + "/quien", timeout=1) as r:
                    if r.status == 200:
                        return proc
            except OSError:
                time.sleep(0.1)
        raise TimeoutError(f"el servidor no respondió /quien en {plazo} s")
    except BaseException:       # también Ctrl-C / interrupción del kernel
        detiene_servidor(proc)  # cierra el hijo y borra el log
        raise


def detiene_servidor(proc):
    """terminate, espera acotada y, si hace falta, kill. Idempotente."""
    if proc is None:
        return
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    log = getattr(proc, "log", None)
    if log is not None and not log.closed:
        log.close()
        try:
            os.unlink(log.name)
        except OSError:
            pass


print("lanza_servidor y detiene_servidor definidas")
print("carpeta de trabajo:", CARPETA)
print("python del kernel :", sys.executable)

# %% [markdown]
# ### Salida esperada de la celda 0.1
#
# Tres renglones: el aviso de que las dos funciones quedaron definidas, la
# carpeta donde está este notebook (debe contener `app_arq.py`) y la ruta del
# Python del kernel (debe ser el de tu ambiente `uv`, no el del sistema). Si
# la carpeta no es la del notebook, abre el notebook desde su carpeta o cambia
# el directorio del kernel antes de seguir.
