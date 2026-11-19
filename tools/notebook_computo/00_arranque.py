# %% [markdown]
# # Cómputo y concurrencia · notebook de la unidad 11
#
# Este notebook es el lugar **verbose** de la unidad: aquí cada paso se explica,
# el código se repite entre versiones (cada versión trae completa la anterior)
# y lo que cambia se marca con `# NUEVO:`. Las páginas del curso traen sólo las
# celdas cortas `Haz (celda k.m)`; esas celdas aparecen aquí **literales**
# (su primer renglón es `# celda k.m`), rodeadas de versiones expandidas.
#
# Cada tema cierra con un `assert` (si falla, algo en tu ambiente o tu servidor
# no es lo que la página supone) y una tabla impresa de resultados.
#
# **Reglas de las celdas.** Usan `await` de nivel superior: el kernel de Jupyter
# ya tiene un event loop corriendo, así que `asyncio.run(...)` truena aquí y
# nunca aparece. Las cargas son pequeñas: a lo más 500 llamadas y a lo más
# 4 procesos de cálculo.

# %% [markdown]
# ## 0.1 · Arranque: ¿está vivo el servidor y ves tus módulos?
#
# La unidad mide contra el servidor de la clase (`servidor.py`, puerto 8026).
# Debe estar corriendo en **otra terminal**, desde esta misma carpeta:
#
# ```text
# FDD_SILENCIO=1 uv run python servidor.py
# ```
#
# `FDD_SILENCIO=1` apaga la radiografía por petición: imprimir 500 peticiones
# en una terminal es trabajo del servidor que estorbaría a la medición.
#
# La celda de abajo comprueba cuatro cosas: que `cable.py`, `gantt.py` y
# `trabajo_computo.py` se importan (viven junto a este notebook), que el
# servidor contesta `200`, cuántas CPU lógicas tiene tu máquina (el tope `P` de
# ejecución simultánea de la página 2) y las versiones de las bibliotecas.

# %%
# 0.1 arranque
import os, sys, platform
import requests, httpx, numpy, matplotlib
from cable import URL
import gantt                       # el Gantt medido de este notebook
import trabajo_computo             # el cálculo de los procesos

r = requests.get(f"{URL}/", timeout=5)
print("servidor:", URL, "->", r.status_code)
print("CPU lógicas (P):", os.cpu_count())
print("Python", platform.python_version(), "|", "requests", requests.__version__,
      "| httpx", httpx.__version__, "| numpy", numpy.__version__,
      "| matplotlib", matplotlib.__version__)
assert r.status_code == 200, "arranca servidor.py en otra terminal"
assert os.cpu_count() >= 2, "con 1 CPU lógica no hay paralelismo que medir"

# %% [markdown]
# **Qué esperar.** `servidor: http://127.0.0.1:8026 -> 200`, el número de CPU
# lógicas de tu máquina y las versiones. Si `requests.get` truena con
# `ConnectionError`, el servidor no está corriendo.
#
# ## 0.2 · El Gantt medido: cómo se lee
#
# `gantt.py` (junto a este notebook) guarda intervalos `[inicio, fin)` por
# tarea y los dibuja. Es la herramienta de todo el notebook, así que se prueba
# una vez con datos inventados a mano:
#
# | tipo | se dibuja | significa |
# |---|---|---|
# | `exec` | relleno | la tarea ejecuta instrucciones en una CPU |
# | `espera` | contorno | espera algo de fuera del programa (red, reloj) |
# | `lista` | rayado | puede ejecutar pero aún no tiene hilo o CPU |
# | `permiso` | ámbar | espera un permiso de otra tarea (semáforo, candado, pool) |
#
# Los intervalos son semiabiertos: la barra siguiente empieza donde acaba la
# anterior y no se solapan.

# %%
# 0.2 prueba del Gantt con tiempos inventados (no mide nada)
gantt.reinicia()
for i, (ini, lista, esp) in enumerate([(0.0, 0.0, 0.2), (0.0, 0.1, 0.2)]):
    gantt.registra(f"tarea {i}", ini, ini + lista, "lista")
    gantt.registra(f"tarea {i}", ini + lista, ini + lista + 0.02, "exec")
    gantt.registra(f"tarea {i}", ini + lista + 0.02, ini + lista + 0.02 + esp, "espera")
gantt.registra("tarea 1", 0.34, 0.40, "permiso")
gantt.dibuja("Prueba: las cuatro formas")
assert len(gantt.registros()) == 7

# %% [markdown]
# **Qué esperar.** Dos filas: la segunda empieza con una barra rayada (lista),
# luego un trazo relleno corto (exec), un contorno largo (espera) y al final un
# tramo ámbar. Si ves las cuatro formas, `gantt.py` y matplotlib funcionan.
# Cada tema empieza con `gantt.reinicia()` para no mezclar dibujos.
