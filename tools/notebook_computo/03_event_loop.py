# %% [markdown]
# # Tema 3 · Asíncrono y el event loop
#
# **Pregunta.** Los hilos solapan esperas, pero cada hilo cuesta memoria y el
# sistema los reparte. ¿Se pueden solapar esperas en **un** solo hilo?
# **Meta.** Entender el mecanismo (corrutina, `Task`, event loop tick a tick)
# y medir con Gantt reales qué pasa cuando se usa bien (`gather`), cuando se
# usa mal (`await` en serie) y cuando se rompe (`time.sleep` dentro de una
# corrutina).
#
# **Asíncrono** (definición de la página 3) es un mecanismo: la llamada
# **regresa antes de tener el resultado** y quien espera **cede el hilo**. No es
# una celda del Gantt: es la manera en que una tarea deja de ocupar el hilo
# mientras espera.

# %% [markdown]
# ## Paso 1 · Corrutina y `Task`
#
# - Una función `async def` no corre al llamarla: devuelve un objeto
#   **corrutina** (una receta pausable).
# - `asyncio.create_task(c)` agenda esa corrutina en el event loop y regresa de
#   inmediato un `Task`; la corrutina empieza a correr la próxima vez que el
#   loop recupere el control.
# - `await t` suspende a quien lo escribe hasta que `t` termina y **cede el
#   hilo** al loop mientras tanto.
#
# **Qué esperar.** Primero `coroutine` (nada corrió); luego `terminó: False`
# justo después de `create_task`; y al final `terminó: True y devolvió 42`.

# %%
# celda 3.1
import asyncio

async def cuenta():                        # corrutina: puede suspenderse en un await
    await asyncio.sleep(0.2)               # espera 0.2 s cediendo el hilo al loop
    return 42

c = cuenta()                               # sólo crea el objeto: no corre nada
print("llamarla devuelve:", type(c).__name__)
c.close()                                  # se descarta sin correrla (evita el aviso)
tarea = asyncio.create_task(cuenta())      # la agenda en la cola de listas y regresa
print("justo después de crearla, terminó:", tarea.done())
resultado = await tarea                    # main cede el hilo hasta que la tarea termina
print("después de await, terminó:", tarea.done(), "y devolvió", resultado)

# %% [markdown]
# Aviso para el notebook: el kernel ya tiene un event loop; por eso la celda usa
# `await` directo y nunca `asyncio.run`.

# %%
assert tarea.done() and resultado == 42

# %% [markdown]
# ## Paso 2 · El event loop tick a tick (simulación determinista)
#
# Un **tick** del loop hace tres cosas, en este orden:
#
# 1. Corre, una tras otra, todas las tareas de la **cola de listas**, cada una
#    hasta su siguiente `await` (o hasta que termina).
# 2. Pregunta al sistema qué esperas ya se cumplieron (`select`), con un
#    plazo máximo igual al temporizador más próximo.
# 3. Pasa a la cola de listas las tareas cuya espera se cumplió.
#
# La celda siguiente es un loop de juguete en Python puro (reloj **virtual**,
# no mide nada real) con `gather(A, B, C)`: cada tarea ejecuta 10 ms, duerme
# `d` y ejecuta 10 ms más, con `d_A = 0.3`, `d_B = 0.1`, `d_C = 0.2` s.
# Imprime una fila por tick con las tres colas.

# %%
import heapq
from collections import deque

def tarea_juguete(nombre, d):                  # cada yield es un await: cede el hilo al loop
    yield ("duerme", d)                        # entre el arranque y el yield, 10 ms de exec
    return nombre                              # después del yield, otros 10 ms de exec

def loop_juguete(spec, ms_exec=10):
    listas = deque((n, tarea_juguete(n, d)) for n, d in spec)    # la cola de listas
    durmiendo = []                                               # montículo: (vence_ms, nombre, tarea)
    reloj, tick, orden = 0, 0, []
    print("tick  reloj ms  cola de listas -> ejecutó  | esperando (vence en ms)")
    while listas or durmiendo:
        en_cola = ", ".join(n for n, _ in listas)                 # la cola de listas al empezar el tick
        corridas = []
        while listas:                                            # 1) corre toda la cola de listas
            nombre, g = listas.popleft()
            reloj += ms_exec                                     # su tramo de exec: el hilo ocupado
            try:
                _, d = next(g)                                   # corre hasta su await
                heapq.heappush(durmiendo, (reloj + round(d * 1000), nombre, g))
                corridas.append(nombre + " (hasta await)")
            except StopIteration:
                orden.append(nombre); corridas.append(nombre + " (termina)")
        esperando = ", ".join(f"{n}({v})" for v, n, _ in sorted(durmiendo))
        print(f"{tick:4d} {reloj:8d}  {en_cola:12} -> {', '.join(corridas)}  | esperando: {esperando}")
        if durmiendo:                                            # 2) select: salta al temporizador más próximo
            reloj = max(reloj, durmiendo[0][0])
            while durmiendo and durmiendo[0][0] <= reloj:        # 3) las vencidas pasan a listas
                _, nombre, g = heapq.heappop(durmiendo)
                listas.append((nombre, g))
        tick += 1
    return reloj, orden

fin_virtual, orden_fin = loop_juguete([("A", 0.3), ("B", 0.1), ("C", 0.2)])
print("terminaron en orden:", orden_fin, "| reloj virtual al final:", fin_virtual, "ms")
assert orden_fin == ["B", "C", "A"] and fin_virtual == 320

# %% [markdown]
# **Qué pasó.** El tick 0 corre A, B y C seguidas (cada una 10 ms, el hilo
# ocupado: 30 ms) y las tres quedan esperando con su temporizador (A vence en
# 310, B en 120, C en 230). Entonces el loop no tiene nada que correr: pregunta
# al sistema y **duerme hasta 120 ms**, el temporizador más próximo. Despierta B,
# la corre y así sucesivamente. El tiempo total (320 ms) es el de la tarea más
# larga (310) más lo que tarda en ejecutar el último tramo, no la suma de las tres.
#
# Esa cola de listas y esa espera con plazo son todo el mecanismo. Lo que sigue
# es el loop **real** de `asyncio`, instrumentado para que imprima su propio
# número de tick.

# %% [markdown]
# ## Paso 3 · La traza real de `gather(A, B, C)`
#
# Dos celdas de la página. La primera define `marca`, que imprime cada evento
# con el número de tick (un tick nuevo empieza cuando se agenda con
# `call_soon`, que entra a la cola del tick siguiente) y los milisegundos desde
# `t0`. La segunda corre `gather` con las tres tareas de la simulación, esta vez
# con `asyncio.sleep` de verdad y `time.sleep(0.01)` como 10 ms de CPU ocupada.

# %%
# celda 3.2
import asyncio, time
loop = asyncio.get_running_loop()          # el loop que corre las celdas

def abre_tick():                           # corre al principio del tick siguiente
    global en_tick
    en_tick = False

def marca(texto):                          # imprime: tick, ms desde t0, texto
    global tick, en_tick
    if not en_tick:                        # primera línea de este tick: le toca número nuevo
        tick, en_tick = tick + 1, True
        loop.call_soon(abre_tick)          # call_soon: entra a la cola del tick siguiente
    print(f"tick {tick}  {(loop.time() - t0) * 1000:4.0f} ms  {texto}")

# %%
# celda 3.3
async def tarea(nombre, d):
    marca(f"{nombre} ejecuta 10 ms y hace await sleep({d})")
    time.sleep(0.01)                       # 10 ms con el hilo ocupado, sin ceder
    await asyncio.sleep(d)                 # cede el hilo; su temporizador vence en d s
    marca(f"{nombre} se reanuda, ejecuta 10 ms y termina")
    time.sleep(0.01)
    return nombre

t0, tick, en_tick = loop.time(), -1, False # reinicia el reloj y el contador
marca("main: gather crea A, B y C y hace await")
resultado = await asyncio.gather(tarea("A", 0.3), tarea("B", 0.1), tarea("C", 0.2))
marca(f"main recibe {resultado}")

# %% [markdown]
# **Qué esperar.** Los eventos de arranque de A, B y C salen en el mismo tick y
# separados ~10 ms en el reloj (el hilo está ocupado con cada uno); luego B, C y
# A se reanudan en ticks distintos, hacia los 120, 230 y 310 ms, y
# `main recibe ['A', 'B', 'C']`: `gather` devuelve los resultados en el orden en
# que se pasaron las corrutinas, no en el orden en que terminaron.

# %%
assert resultado == ["A", "B", "C"]

# %% [markdown]
# ## Paso 4 · `await` bien y `await` en serie, con Gantt medido
#
# Misma tarea (llamadas de 0.2 s al servidor) con dos formas de escribirla:
#
# - **`await` en serie:** `for ...: await cliente.get(...)`. Cada `await` cede el
#   hilo, pero el `for` no lanza la siguiente llamada hasta tenerla resuelta. Es
#   asíncrono (cede el hilo al esperar) y **secuencial** (nada se solapa).
# - **`gather`:** crea todas las tareas primero y las espera juntas. Eso solapa.
#
# Primero la celda de la página (serie), luego la versión **v3** del cliente.

# %%
# celda 3.4
import time, httpx
from cable import URL

inicio = time.perf_counter()
async with httpx.AsyncClient(timeout=30) as cliente:    # cliente HTTP que cede el hilo al esperar
    for _ in range(20):
        r = await cliente.get(f"{URL}/ventas?lento=0.2")  # espera ésta antes de lanzar la siguiente
print(f"20 llamadas con await en serie: {time.perf_counter() - inicio:.2f} s")

# %% [markdown]
# **Qué esperar.** ≈ 4 s: igual que la v1 con `for` + `requests`. Que sea
# `async` y use `await` no lo hizo concurrente.

# %%
t_serie = time.perf_counter() - inicio
assert t_serie >= 20 * 0.2

# %% [markdown]
# ### v3: corrutinas con `gather`, medida
#
# Mismo cliente que antes, ahora como corrutina. Lo nuevo es `gather`, que
# agenda las 20 llamadas como `Task` antes de esperar a ninguna, y el registro
# del Gantt con `loop.time()`.

# %%
# v3: el cliente v1/v2, con corrutinas y gather
import asyncio, time, httpx
from cable import URL
import gantt

async def pide_v3(cliente, i, lento=0.2):               # NUEVO: async def
    a = loop.time()
    r = await cliente.get(f"{URL}/ventas?lento={lento}")      # NUEVO: await cede el hilo
    gantt.registra(f"llamada {i:02d}", a, loop.time(), "espera")
    return r.status_code

async def cliente_v3(n, en_serie=False):
    gantt.reinicia()
    inicio = loop.time()
    async with httpx.AsyncClient(timeout=30) as cliente:      # NUEVO: cliente que cede el hilo
        if en_serie:                                          # el error: await dentro del for
            codigos = [await pide_v3(cliente, i) for i in range(n)]
        else:                                                 # NUEVO: gather agenda todas y espera juntas
            codigos = await asyncio.gather(*(pide_v3(cliente, i) for i in range(n)))
    return list(codigos), loop.time() - inicio

loop = asyncio.get_running_loop()
codigos_s, t_s = await cliente_v3(20, en_serie=True)
gantt.dibuja("v3 · 20 llamadas con await en serie")
codigos_g, t_g = await cliente_v3(20)
gantt.dibuja("v3 · 20 llamadas con gather")

# %% [markdown]
# **Qué esperar.** El primer dibujo es la escalera de la v1 (ninguna barra
# empieza antes de que acabe la anterior). El segundo son 20 barras alineadas,
# todas abiertas al mismo tiempo: concurrente, en **un** solo hilo. Esa es la
# diferencia que hace `gather` y que no hace el `for` con `await`.

# %%
assert set(codigos_s) == set(codigos_g) == {200}
assert t_s >= 20 * 0.2 and t_g < 1.0
print(f"{'versión':32} {'llamadas':>8} {'tiempo (s)':>11} {'vs v1':>7}")
print(f"{'v1 for + requests':32} {20:8d} {t_v1:11.2f} {'1.0x':>7}")
print(f"{'v2 hilos (k=32)':32} {20:8d} {t_h32:11.2f} {t_v1 / t_h32:6.1f}x")
print(f"{'v3 await en serie':32} {20:8d} {t_s:11.2f} {t_v1 / t_s:6.1f}x")
print(f"{'v3 gather':32} {20:8d} {t_g:11.2f} {t_v1 / t_g:6.1f}x")

# %% [markdown]
# ## Paso 5 · `time.sleep` dentro de una corrutina rompe el loop
#
# El loop solapa esperas **sólo si quien espera cede el hilo**. `await
# asyncio.sleep(d)` lo cede; `time.sleep(d)` no: duerme el hilo entero y el loop,
# que corre en ese hilo, no puede avanzar a ninguna otra tarea. La celda de la
# página repite la traza de `gather(A, B, C)` pero con `time.sleep`.
#
# **Qué esperar.** Las tareas corren **una tras otra** y el tiempo total es la
# suma de las tres esperas más sus tramos: ≈ 0.3 + 0.1 + 0.2 + 0.06 = 0.66 s,
# en lugar de ≈ 0.32 s. Ninguna se reanuda en otro tick: la `Task` B no puede
# empezar hasta que A suelta el hilo al terminar.

# %%
# celda 3.5
async def tarea_bloqueante(nombre, d):
    marca(f"{nombre} ocupa el hilo 10 ms + time.sleep({d}) + 10 ms")
    time.sleep(d + 0.02)                   # duerme SIN soltar el hilo: el loop no recupera el turno
    marca(f"{nombre} termina")
    return nombre

t0, tick, en_tick = loop.time(), -1, False
marca("main: gather crea A, B y C y hace await")
tareas = [("A", 0.3), ("B", 0.1), ("C", 0.2)]
resultado = await asyncio.gather(*(tarea_bloqueante(n, d) for n, d in tareas))
marca(f"main recibe {resultado}")

# %% [markdown]
# ### La misma comparación, medida con Gantt
#
# Las tres tareas de la traza con `await asyncio.sleep` y con `time.sleep`, cada
# una con sus tres tramos: `exec` 10 ms, `espera` (o la espera que bloquea el
# hilo), `exec` 10 ms. Lo nuevo: las tareas que todavía no pueden correr porque
# otra tiene el hilo se registran como `lista` (rayado) desde que `gather` las
# creó hasta que arrancan.

# %%
async def tarea_g(nombre, d, bloqueante):
    inicio = loop.time()
    gantt.registra(nombre, T0, inicio, "lista")           # NUEVO: lista hasta que el hilo es suyo
    time.sleep(0.01)                                      # 10 ms de exec (hilo ocupado)
    a = loop.time(); gantt.registra(nombre, inicio, a, "exec")
    if bloqueante:
        time.sleep(d)                                     # NUEVO: duerme el hilo del loop
    else:
        await asyncio.sleep(d)                            # cede el hilo
    b = loop.time(); gantt.registra(nombre, a, b, "espera")
    time.sleep(0.01)                                      # 10 ms de exec
    gantt.registra(nombre, b, loop.time(), "exec")

async def corre_tres(bloqueante):
    global T0
    gantt.reinicia()
    T0 = loop.time()
    await asyncio.gather(*(tarea_g(n, d, bloqueante) for n, d in (("A", 0.3), ("B", 0.1), ("C", 0.2))))
    return loop.time() - T0

t_async = await corre_tres(False); gantt.dibuja("tres tareas con await asyncio.sleep")
t_bloq = await corre_tres(True);   gantt.dibuja("tres tareas con time.sleep (bloquea el loop)")

# %% [markdown]
# **Qué esperar.** Primer dibujo: las tres filas comparten el intervalo de espera
# (contornos alineados), total ≈ 0.32 s. Segundo: las tres tareas ejecutan una
# tras otra, y las que esperan turno aparecen como `lista` (rayadas) mientras
# la otra duerme el hilo; el total es la suma, ≈ 0.66 s. El mismo código con
# **una** palabra distinta (`time.sleep` por `await asyncio.sleep`) pasa de
# concurrente a secuencial.

# %%
assert t_async < 0.45 and t_bloq > 0.6
assert t_bloq > 1.5 * t_async
print(f"{'tres tareas A=0.3 B=0.1 C=0.2':32} {'tiempo (s)':>11} {'predicción (s)':>15}")
print(f"{'await asyncio.sleep':32} {t_async:11.2f} {0.3 + 0.02:15.2f}")
print(f"{'time.sleep (bloquea el loop)':32} {t_bloq:11.2f} {0.3 + 0.1 + 0.2 + 0.06:15.2f}")
