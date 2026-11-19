# %% [markdown]
# # Tema 4 · El cliente de 500 llamadas, en cinco versiones
#
# **Pregunta.** Tienes que hacer 500 llamadas de 0.2 s a la misma dependencia. ¿Cuánto tardan, y qué cambia de
# una versión del cliente a la siguiente?
#
# Este tema es el lugar verboso de la página 4 (página 4, concurrencia acotada): aquí el mismo cliente aparece **cinco
# veces**, cada vez con el código completo de la versión anterior y la línea nueva marcada con `# NUEVO:`.
#
# | versión | idea | qué agrega |
# |---|---|---|
# | v1 | `for` + `requests` | nada: línea base secuencial |
# | v2 | hilos (`ThreadPoolExecutor`, 32) | concurrencia con un recurso (hilo) por llamada en vuelo |
# | v3 | `gather` **sin tope** | concurrencia con corrutinas; se prueba sólo con 20 |
# | v4 | `gather` + `Semaphore(32)` + `Limits(32)` | tope de entrada y tope de recursos |
# | v5 | v4 + reintento + `asyncio.Queue` productor-consumidor | fallos transitorios y cola acotada |
#
# **La cota.** Con $k$ llamadas en vuelo a la vez y $W=0.2$ s por llamada, $n$ llamadas no pueden tardar menos
# que $\lceil n/k\rceil\cdot W$. Esa cota es la regla con la que se juzga cada versión.
#
# Cargas de este tema: **a lo más 500 llamadas**. Antes de correr, el servidor de la clase debe estar prendido
# (`FDD_SILENCIO=1 uv run python servidor.py`). Todo usa `await` de nivel superior: el kernel del notebook ya
# tiene un event loop corriendo, y `asyncio.run` truena aquí.

# %%
# Preparación del tema: imports, constantes y la tabla donde se acumulan las mediciones de las cinco versiones.
import asyncio, math, random, time
import httpx, requests
import matplotlib.pyplot as plt
from cable import URL
from gantt import registra, dibuja, reinicia

W = 0.2                                   # segundos que tarda cada llamada en el servidor (?lento=0.2)
LLAMADA = f"{URL}/ventas?lento=0.2"       # la llamada de todo el tema
RESULTADOS = {}                           # versión -> (n, k, segundos, nota)

def cota(n, k):
    """Lo mínimo que puede tardar n llamadas de W segundos con k en vuelo."""
    return math.ceil(n / k) * W

print("W =", W, "s · cota(500, 32) =", cota(500, 32), "s · cota(20, 1) =", cota(20, 1), "s")

# %% [markdown]
# ## v1 · `for` + `requests`: la línea base
#
# **Qué hace.** Una llamada, espera la respuesta, la siguiente. Un solo hilo, una sola llamada en vuelo
# ($k=1$). Es la versión que escribe cualquiera la primera vez.
#
# **Por qué se mide con 20 y no con 500.** La cota es $\lceil n/1\rceil\cdot0.2$: 500 llamadas tardarían
# **100 s**. Con 20 son 4 s, suficiente para ver la forma; el valor de 500 se calcula, y la tabla final lo
# rotula como *estimado* para que nadie lo confunda con una medición.
#
# **Qué esperar.** Un poco más de 4 s: 20 × 0.2 s más lo que cada llamada gasta en el cliente. El Gantt
# muestra 20 barras de `espera` una detrás de otra, sin solaparse.

# %%
# v1 · for + requests (secuencial). Repite 20 llamadas, una tras otra.
def lote_v1(n):
    marcas_t = []                                     # (inicio, fin) de cada llamada
    for i in range(n):
        ini = time.perf_counter()
        r = requests.get(LLAMADA, timeout=30)       # el hilo se bloquea aquí hasta la respuesta
        r.raise_for_status()
        marcas_t.append((ini, time.perf_counter()))
    return marcas_t

reinicia()
t0 = time.perf_counter()
marcas = lote_v1(20)
T = time.perf_counter() - t0
for i, (a, b) in enumerate(marcas):
    registra(f"llamada {i:02d}", a, b, "espera")   # una barra de espera por llamada
dibuja("v1 · for + requests · 20 llamadas")
RESULTADOS["v1"] = (20, 1, T, "medido con n=20; n=500 sería ≈ %.0f s (estimado)" % cota(500, 1))
print(f"v1: 20 llamadas en {T:.2f} s · cota {cota(20, 1):.2f} s · 500 llamadas (estimado): {cota(500, 1):.0f} s")
assert cota(20, 1) <= T < cota(20, 1) * 1.3, "v1 debería rondar la cota secuencial"

# %% [markdown]
# ## v2 · hilos: `ThreadPoolExecutor(32)`
#
# **Qué cambia.** La función de la llamada es **la misma** (`requests.get`). Lo nuevo es quién la ejecuta: un
# pool de 32 hilos. Cada hilo se bloquea esperando su respuesta, pero hay 32 hilos esperando a la vez.
#
# **Por qué 32.** Es el tope $k$ que se usa en toda la unidad. Con $k=32$ y $n=500$ la cota es
# $\lceil500/32\rceil\cdot0.2=16\cdot0.2=3.2$ s.
#
# **Qué esperar.** 20 llamadas ≈ 0.23 s (caben en una sola tanda), 100 ≈ 0.8 s y 500 ≈ 3.3 s: la forma de
# escalera de la cota. Cada hilo cuesta memoria y cada llamada suelta de `requests.get` abre su propia
# conexión; es la versión que "funciona" y la que más recursos del sistema gasta por llamada en vuelo.

# %%
# v2 · hilos. Mismo código de v1 + el pool de hilos.
from concurrent.futures import ThreadPoolExecutor          # NUEVO: el pool de hilos

def una_llamada_v2(_):                                      # igual que en v1: bloquea al hilo que la corre
    r = requests.get(LLAMADA, timeout=30)
    r.raise_for_status()
    return r.status_code

def lote_v2(n, k=32):
    with ThreadPoolExecutor(max_workers=k) as pool:         # NUEVO: k hilos, cada uno hace llamadas
        return list(pool.map(una_llamada_v2, range(n)))     # NUEVO: map reparte las n entre los k hilos

for n in (20, 100, 500):
    ini = time.perf_counter()
    codigos = lote_v2(n)
    T = time.perf_counter() - ini
    RESULTADOS["v2" if n == 500 else f"v2 (n={n})"] = (n, 32, T, "hilos")
    print(f"v2: {n:>3} llamadas con 32 hilos: {T:5.2f} s · cota {cota(n, 32):.2f} s · {set(codigos)}")
assert RESULTADOS["v2"][2] < cota(500, 32) * 1.5

# %% [markdown]
# ## v3 · `gather` **sin tope**, sólo con 20
#
# **Qué cambia.** Se deja `requests` (bloqueante) por `httpx.AsyncClient`, cuyo `get` es una corrutina, y se
# lanzan todas las tareas a la vez con `asyncio.gather`. No hay hilos: un solo hilo (el del loop) atiende
# a todas, porque cada `await` le devuelve el hilo mientras la respuesta no llega.
#
# **Por qué `return_exceptions=True`.** Sin esa opción, la primera excepción sale por el `await` de `gather`
# y las demás tareas siguen corriendo sin que nadie recoja su resultado. Con la opción, cada excepción ocupa su
# lugar en la lista de resultados y la versión puede contar fallos en lugar de abortar.
#
# **Por qué sólo 20.** "Sin tope" aquí quiere decir *sin semáforo propio*: lo único que limita es el pool
# por omisión de `httpx` (`max_connections=100`). Con 20 no se nota. Con 500, las 400 que no caben esperan
# **dentro del pool**, y esa espera tiene dos costos medidos en esta máquina (`hechos_pool`, experimento h):
# CPU del cliente (11.6 s de pared para 500 llamadas con 100 conexiones, contra 3.4 s con un semáforo de 32
# por encima) y el `timeout` de 5 s por omisión, que **incluye** la espera por una conexión del pool. Por eso
# la tarea de 500 se hace en v4, no aquí.
#
# **Qué esperar.** 20 llamadas ≈ 0.23 s: la cota con $k=20$ es una sola tanda de 0.2 s.

# %%
# v3 · gather sin tope. Mismo lote que v2, pero con corrutinas en lugar de hilos.
async def una_llamada_v3(cliente):                          # NUEVO: corrutina; el await cede el hilo
    r = await cliente.get(LLAMADA)                          # NUEVO: httpx asíncrono en lugar de requests
    r.raise_for_status()
    return r.status_code

async def lote_v3(n):
    async with httpx.AsyncClient(timeout=30) as cliente:   # NUEVO: un cliente (y un pool) para todas
        tareas = (una_llamada_v3(cliente) for _ in range(n))
        return await asyncio.gather(*tareas, return_exceptions=True)  # NUEVO: gather lanza las n a la vez

ini = time.perf_counter()
res = await lote_v3(20)
T = time.perf_counter() - ini
fallos = [r for r in res if isinstance(r, Exception)]       # las excepciones llegan como valores
RESULTADOS["v3"] = (20, 20, T, "gather sin tope, sólo n=20")
print(f"v3: 20 llamadas con gather sin tope: {T:.2f} s · cota {cota(20, 20):.2f} s · fallos: {len(fallos)}")
assert not fallos and T < 0.6

# %% [markdown]
# ## v4 · `gather` + `Semaphore(32)` + `Limits(32)`
#
# La página 4 corre esta versión en la celda 4.1. Aquí aparece **literal** (primer bloque) y después
# ampliada en el bloque siguiente.
#
# **Qué agrega.** Dos topes del mismo valor:
#
# - `Semaphore(32)` es el tope de **entrada**: a lo más 32 tareas dentro del bloque `async with sem`. Las demás
#   quedan bloqueadas en la cola del semáforo, que cuesta casi nada (una corrutina suspendida).
# - `httpx.Limits(max_connections=32)` es el tope de **recursos**: a lo más 32 conexiones abiertas. Con el mismo
#   valor, el pool nunca tiene cola propia.
#
# **Qué esperar.** 20 → 0.23 s, 100 → 0.8 s, 500 → 3.4 s: cada tiempo se acerca a su cota por arriba.

# %%
# celda 4.1
import asyncio, time, httpx
from cable import URL
async def pide(cliente, sem):
    async with sem:  # toma un permiso; si no hay, la tarea queda bloqueada en la cola
        return (await cliente.get(f"{URL}/ventas?lento=0.2")).status_code  # cede el hilo durante la espera

async def lote(n):
    sem = asyncio.Semaphore(32)  # 32 permisos: a lo más 32 dentro del bloque
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=32), timeout=30) as cliente:  # pool con el mismo tope
        return await asyncio.gather(*(pide(cliente, sem) for _ in range(n)))  # n tareas; resultados en orden

for n in (20, 100, 500):
    inicio = time.perf_counter()
    codigos = await lote(n)  # await de nivel superior: el notebook ya tiene un loop corriendo
    print(f"{n:>3} llamadas, asyncio con 32: {time.perf_counter() - inicio:5.2f} s  ({set(codigos)})")

# %% [markdown]
# ### v4 ampliada: la misma celda, con medición de la espera por permiso y la curva $T$ contra $n$
#
# **Qué se agrega a la celda 4.1.**
#
# 1. `return_exceptions=True`, como en v3.
# 2. Cada tarea anota **tres instantes**: cuando se creó, cuando obtuvo el permiso y cuando terminó. La
#    diferencia entre el primero y el segundo es la espera por el permiso (`permiso` en el Gantt); la que hay entre
#    el segundo y el tercero es la espera de la red (`espera`).
# 3. Un Gantt pequeño ($n=12$, $k=4$) para que se vean las tandas, y una curva con seis valores de $n$ contra
#    la cota $\lceil n/k\rceil\cdot W$.
#
# **Qué esperar en el Gantt.** Cuatro barras de `espera` por columna de tiempo; las demás tareas con una barra
# ámbar (`permiso`) que termina justo cuando alguna otra libera su permiso.

# %%
# v4 ampliada · semáforo + pool, medición de la espera por permiso y Gantt de una versión chica.
async def pide_v4(cliente, sem, i, t0, anota):
    creada = time.perf_counter()                             # la tarea existe pero no tiene permiso
    async with sem:                                          # entra: a lo más k dentro del bloque
        con_permiso = time.perf_counter()                    # NUEVO: el instante en que obtuvo el permiso
        r = await cliente.get(LLAMADA)                       # cede el hilo; el permiso sigue tomado
        r.raise_for_status()
        fin = time.perf_counter()
    if anota:                                                # NUEVO: anotar para el Gantt (sólo en lotes chicos)
        registra(f"tarea {i:02d}", creada, con_permiso, "permiso")
        registra(f"tarea {i:02d}", con_permiso, fin, "espera")
    return r.status_code

async def lote_v4(n, k=32, anota=False):
    sem = asyncio.Semaphore(k)                               # tope de entrada
    limites = httpx.Limits(max_connections=k)                # tope de recursos, el mismo valor
    t0 = time.perf_counter()
    async with httpx.AsyncClient(limits=limites, timeout=30) as cliente:
        res = await asyncio.gather(*(pide_v4(cliente, sem, i, t0, anota) for i in range(n)),
                                   return_exceptions=True)   # NUEVO: los fallos llegan como valores
    return res, time.perf_counter() - t0

reinicia()
res, T = await lote_v4(12, k=4, anota=True)                  # 12 tareas, 4 permisos: 3 tandas
dibuja("v4 · 12 llamadas con Semaphore(4) · la franja ámbar es la espera por el permiso")
print(f"12 llamadas con k=4: {T:.2f} s · cota {cota(12, 4):.2f} s")

puntos = []
for n in (20, 50, 100, 200, 350, 500):                       # NUEVO: la curva T contra n con k=32
    res, T = await lote_v4(n)
    fallos = sum(isinstance(r, Exception) for r in res)
    puntos.append((n, T, cota(n, 32), fallos))
    print(f"n={n:>3}  T={T:5.2f} s  cota={cota(n, 32):4.2f} s  T/cota={T / cota(n, 32):4.2f}  fallos={fallos}")
RESULTADOS["v4"] = (500, 32, puntos[-1][1], "Semaphore(32) + Limits(32)")

ns = list(range(1, 501))
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.step(ns, [cota(n, 32) for n in ns], where="post", color="#555555", label="cota ⌈n/32⌉·0.2 s")
ax.plot([p[0] for p in puntos], [p[1] for p in puntos], "o", color="#1f4e8c", label="medido (v4)")
ax.set_xlabel("llamadas n"); ax.set_ylabel("segundos"); ax.set_title("v4: el tiempo sigue la escalera de la cota")
ax.legend(); fig.tight_layout(); plt.show()
assert all(p[1] >= p[2] * 0.98 for p in puntos), "ninguna medición puede estar bajo la cota"
assert all(p[1] < p[2] * 1.6 for p in puntos), "v4 debería quedar cerca de la cota"
assert all(p[3] == 0 for p in puntos), "ninguna llamada debería fallar"

# %% [markdown]
# ### La celda 4.2 (opcional): el orden y los fallos de `gather`
#
# Dos reglas que sostienen a v3, v4 y v5:
#
# 1. `gather` devuelve los resultados **en el orden en que se pasaron las corrutinas**, no en el orden en que
#    terminaron.
# 2. Con `return_exceptions=True`, una llamada que falla ocupa **su lugar** en la lista como una excepción. Esa
#    segunda línea de la salida es la que imprime `HTTPStatusError`. Sin la opción, el `await` de `gather` relanzaría
#    la primera excepción y el resto de la lista se perdería.
#
# En la celda 4.2 la segunda ruta (`/ventas/99999`) no existe: el servidor responde 404.

# %%
# celda 4.2
import asyncio, httpx
from cable import URL

async def pide(cliente, ruta):
    r = await cliente.get(f"{URL}{ruta}")
    r.raise_for_status()  # un 404 se vuelve excepción (httpx no lo hace solo)
    return r.status_code

rutas = ["/ventas?lento=0.3", "/ventas/99999?lento=0.1", "/ventas?lento=0.2"]
async with httpx.AsyncClient(timeout=30) as cliente:
    res = await asyncio.gather(*(pide(cliente, r) for r in rutas), return_exceptions=True)  # la excepción ocupa su lugar
for ruta, x in zip(rutas, res):
    print(f"{ruta:<24} {x if isinstance(x, int) else type(x).__name__}")

# %%
# Comprobación de 4.2: el orden es el de las rutas aunque la segunda terminó primero (0.1 s) y la primera al final (0.3 s).
assert res[0] == 200 and isinstance(res[1], httpx.HTTPStatusError) and res[2] == 200

# %% [markdown]
# ## v5 · v4 + reintento + `asyncio.Queue` productor-consumidor
#
# Dos problemas que v4 no resuelve:
#
# 1. **Una falla transitoria arruina la llamada.** Si 1 de cada 25 llamadas falla una vez (red, reinicio de un
#    proxy), v4 devuelve una excepción en esa posición y el trabajo pierde esa venta. v5 **reintenta** ante error
#    hasta 3 veces, con espera creciente (*backoff*) y un poco de azar (*jitter*) para que los reintentos no
#    lleguen todos juntos.
# 2. **`gather` crea las $n$ tareas de golpe.** Con 500 es barato; con 10 millones, no. v5 reparte el trabajo con
#    una `asyncio.Queue(maxsize=…)`: **un productor** mete los ids en la cola (se suspende si está llena:
#    contrapresión) y **$k$ consumidores** los sacan y llaman. Los consumidores son los $k$ recursos; ya no hace
#    falta el `Semaphore`, porque sólo hay $k$ tareas que llaman.
#
# **Cómo se prueba el reintento.** El servidor no falla solo. Se simula en el cliente y se rotula como tal:
# toda llamada con `i % 25 == 0` lanza `httpx.ConnectError` en su **primer** intento. Son 20 de las 500; con el
# reintento no debe quedar ningún fallo. Un reintento es seguro aquí porque un `GET` es idempotente; con un `POST`
# que crea una venta, reintentar duplicaría el recurso.

# %%
# v5 · v4 + reintento + cola productor-consumidor. Todo lo de v4 sigue aquí.
async def llama_v5(cliente, i, reintentos, intentos=3):
    for intento in range(1, intentos + 1):                   # NUEVO: hasta 3 intentos
        try:
            if i % 25 == 0 and intento == 1:                 # NUEVO: falla transitoria SIMULADA, sólo el 1.er intento
                raise httpx.ConnectError("falla simulada")
            r = await cliente.get(LLAMADA)                   # la llamada de v3 y v4
            r.raise_for_status()
            return r.status_code
        except httpx.HTTPError:
            if intento == intentos:
                raise                                        # NUEVO: se agotaron los intentos: la falla es real
            reintentos.append(i)                             # NUEVO: contar cuántos reintentos hubo
            await asyncio.sleep(0.05 * 2 ** intento + random.uniform(0, 0.05))  # NUEVO: backoff + jitter

async def lote_v5(n, k=32, tam_cola=64):
    cola = asyncio.Queue(maxsize=tam_cola)                   # NUEVO: cola acotada: el productor espera si se llena
    resultados, reintentos = {}, []

    async def productor():
        for i in range(n):
            await cola.put(i)                                # NUEVO: se suspende si la cola está llena
    async def consumidor(cliente):
        while True:                                          # NUEVO: cada consumidor es uno de los k recursos
            i = await cola.get()
            try:
                resultados[i] = await llama_v5(cliente, i, reintentos)
            except httpx.HTTPError as e:
                resultados[i] = e                            # se guarda el fallo, no se pierde el consumidor
            finally:
                cola.task_done()

    limites = httpx.Limits(max_connections=k)
    async with httpx.AsyncClient(limits=limites, timeout=30) as cliente:
        consumidores = [asyncio.create_task(consumidor(cliente)) for _ in range(k)]   # NUEVO: k consumidores
        await productor()
        await cola.join()                                    # NUEVO: espera a que se procese todo lo encolado
        for c in consumidores:
            c.cancel()                                       # NUEVO: ya no hay más trabajo
        await asyncio.gather(*consumidores, return_exceptions=True)
    return resultados, reintentos

t0 = time.perf_counter()
resultados, reintentos = await lote_v5(500)
T = time.perf_counter() - t0
fallos = [i for i, r in resultados.items() if isinstance(r, Exception)]
RESULTADOS["v5"] = (500, 32, T, f"{len(reintentos)} reintentos, {len(fallos)} fallos")
print(f"v5: 500 llamadas con 32 consumidores: {T:.2f} s · cota {cota(500, 32):.2f} s")
print(f"reintentos: {len(reintentos)} (esperados 20) · fallos finales: {len(fallos)} · resultados: {len(resultados)}")
assert len(resultados) == 500 and not fallos
assert len(reintentos) == 20, "20 llamadas (i múltiplo de 25) fallan una vez y se reintentan"
assert cota(500, 32) * 0.98 <= T < cota(500, 32) * 1.6

# %% [markdown]
# ## La tabla final: v1 … v5
#
# Todas las cifras salen de las celdas de arriba, en **esta** máquina y en **esta** corrida. La columna
# *cota* es $\lceil n/k\rceil\cdot W$ con el $k$ de la versión. v1 se midió con $n=20$; el valor para $n=500$ es
# la cota, no una medición.
#
# **Cómo leerla.**
#
# - v1 → v2 cambia **quién espera** (un hilo por llamada en vuelo) y gana ×30 en tiempo.
# - v2 → v3 cambia **el costo de esperar** (una corrutina en lugar de un hilo) pero no el tiempo: la cota es la
#   misma. Lo que se gana es poder subir $n$ sin crear hilos.
# - v3 → v4 agrega **el tope**: sin él, 500 llamadas pelean por el pool de `httpx`.
# - v4 → v5 agrega **tolerancia a fallos** y una cola acotada. El tiempo no mejora; la corrección sí.

# %%
print(f"{'versión':<11}{'n':>5}{'k':>5}{'segundos':>10}{'cota':>8}  nota")
for nombre in ("v1", "v2", "v3", "v4", "v5"):
    n, k, T, nota = RESULTADOS[nombre]
    print(f"{nombre:<11}{n:>5}{k:>5}{T:>10.2f}{cota(n, k):>8.2f}  {nota}")
assert set(RESULTADOS) >= {"v1", "v2", "v3", "v4", "v5"}
# v1 con 500 llamadas (estimado) contra v4: cuántas veces más rápida es la versión acotada
print(f"v4 contra v1 (v1 con n=500 estimado): ×{cota(500, 1) / RESULTADOS['v4'][2]:.0f}")
assert RESULTADOS["v4"][2] < cota(500, 1) / 20
