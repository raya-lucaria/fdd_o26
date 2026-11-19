# %% [markdown]
# # Tema 5 · Pools y recursos: quién corre, quién entra, qué conexión usas
#
# **Pregunta.** Un pool tiene 5 conexiones y las 5 están en vuelo, esperando respuesta. ¿Puede la sexta petición
# usar una de ellas? ¿Se reutiliza una conexión cuando su petición termina? ¿Qué libera `await`?
#
# Este tema es la versión verbosa de la página 5. En lugar de afirmar las respuestas, **las cuenta**: el servidor
# de la clase tiene un endpoint `GET /quien` que responde tres datos de **tu conexión**:
#
# | campo | qué es | para qué sirve aquí |
# |---|---|---|
# | `puerto` | el puerto del cliente de esa conexión TCP | un puerto distinto = una conexión distinta |
# | `hilo` | el hilo del servidor que la atiende | conexiones abiertas del cliente = hilos ocupados del servidor |
# | `peticion_en_conexion` | cuántas peticiones lleva esa conexión | si crece (1, 2, 3, …) la conexión se reutilizó |
#
# **Tres topes que se confunden** (y que este tema separa con mediciones):
#
# | tope | quién lo pone | qué cuenta | qué guarda |
# |---|---|---|---|
# | de tareas | nadie (`gather` sin límite) | corrutinas creadas | nada: son baratas |
# | de entrada | `Semaphore(k)` | permisos | sólo un número |
# | de recursos | el pool (`httpx.Limits`, una `Queue` de conexiones) | conexiones reales | **los objetos**: los presta, los recupera, los reutiliza |
#
# Todo el tema usa `await` de nivel superior. El servidor de la clase debe estar prendido
# (`FDD_SILENCIO=1 uv run python servidor.py`).

# %%
# Preparación del tema: imports y un diccionario donde se acumulan las cifras que el cierre comprueba.
import asyncio, logging, statistics, threading, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import httpx, requests
from requests.adapters import HTTPAdapter
from cable import URL
from gantt import registra, dibuja, reinicia

CIFRAS = {}          # nombre -> valor medido; el cierre del tema las comprueba y las imprime
print("listo · URL =", URL)

# %% [markdown]
# ## 5.1 · ¿Cuántas conexiones abre cada cliente?
#
# `requests.get(url)` crea una `Session`, la usa **una vez** y la tira: cada llamada es una conexión TCP nueva
# (un puerto nuevo, un hilo nuevo en el servidor). `requests.Session()` guarda la conexión abierta en su pool y
# la reutiliza: un solo puerto, y `peticion_en_conexion` sube 1, 2, 3, …
#
# **Qué esperar.** Suelto: 20 puertos, 20 hilos del servidor, 1 petición por conexión. `Session`: 1 puerto,
# 1 hilo, hasta 20 peticiones en esa conexión.

# %%
# celda 5.1
import requests
from cable import URL

def resume(nombre, vistos):                   # vistos: las respuestas de /quien
    puertos = {v["puerto"] for v in vistos}   # puerto del cliente: uno por conexión TCP
    hilos = {v["hilo"] for v in vistos}       # hilo del servidor que atendió esa conexión
    n_max = max(v["peticion_en_conexion"] for v in vistos)  # peticiones de la conexión más usada
    print(f"{nombre}: {len(puertos)} puertos · {len(hilos)} hilos del servidor"
          f" · hasta {n_max} peticiones por conexión")

resume("suelto ", [requests.get(f"{URL}/quien").json() for _ in range(20)])  # una conexión por llamada
with requests.Session() as s:                 # la Session guarda la conexión entre llamadas
    resume("Session", [s.get(f"{URL}/quien").json() for _ in range(20)])

# %% [markdown]
# ### 5.1 ampliada: los tres clientes lado a lado, y cuánto ahorra reutilizar
#
# Se agrega el tercer cliente, `httpx.AsyncClient(limits=httpx.Limits(max_connections=5))`, con 20 peticiones
# **simultáneas** de 0.2 s. Con `requests` las peticiones eran en serie, por eso una sola conexión bastaba; aquí
# hay 20 en vuelo y 5 conexiones, y la pregunta es cuántos puertos distintos ve el servidor.
#
# También se mide cuánto cuesta no reutilizar: 200 llamadas rápidas (`lento=0`) sin y con `Session`.
#
# **Qué esperar.** `httpx` con `Limits(5)`: **a lo más 5 puertos**. La diferencia por llamada entre suelto y
# `Session` es pequeña en localhost (décimas de milisegundo): el handshake TCP local casi no cuesta. El ahorro
# que se cita en la literatura (TCP + TLS + autenticación, uno a tres viajes de ida y vuelta por conexión) es de
# **red real**; en esta máquina no se ve, y por eso la cifra no se presenta como si lo fuera.

# %%
# Los tres clientes con el mismo resumen, y el costo de no reutilizar.
async def httpx_con_limite(k, n=20, lento=0.2):
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=k), timeout=30) as c:
        pedir = lambda: c.get(f"{URL}/quien?lento={lento}")             # NUEVO: peticiones simultáneas
        resp = await asyncio.gather(*(pedir() for _ in range(n)))
    return [r.json() for r in resp]

t0 = time.perf_counter()
vistos_httpx = await httpx_con_limite(5)                                # NUEVO: 20 en vuelo, pool de 5
T_httpx = time.perf_counter() - t0
resume("httpx  ", vistos_httpx)
print(f"       20 peticiones de 0.2 s con Limits(5): {T_httpx:.2f} s")

def mide_200(llamar):
    t0 = time.perf_counter()
    for _ in range(200):
        llamar(f"{URL}/quien?lento=0")                                  # 200 llamadas que responden de inmediato
    return time.perf_counter() - t0

suelto = mide_200(requests.get)
with requests.Session() as s:
    sesion = mide_200(s.get)
print(f"200 llamadas sin Session: {suelto:.2f} s  ({suelto / 200 * 1000:.2f} ms c/u)")
print(f"200 llamadas con Session: {sesion:.2f} s  ({sesion / 200 * 1000:.2f} ms c/u)")
print(f"diferencia por llamada:   {(suelto - sesion) / 200 * 1000:.2f} ms  (localhost: sin TLS ni viaje de red)")

puertos_suelto = len({requests.get(f"{URL}/quien").json()["puerto"] for _ in range(20)})
with requests.Session() as s:
    puertos_sesion = len({s.get(f"{URL}/quien").json()["puerto"] for _ in range(20)})
CIFRAS.update(puertos_suelto=puertos_suelto, puertos_sesion=puertos_sesion,
              puertos_httpx5=len({v["puerto"] for v in vistos_httpx}), t_httpx5=T_httpx)
assert puertos_suelto == 20 and puertos_sesion == 1
assert CIFRAS["puertos_httpx5"] <= 5

# %% [markdown]
# ## 5.2 · Un pool de 5 conexiones y 20 peticiones
#
# Las 20 tareas existen a la vez (tope de tareas: 20), pero sólo hay 5 conexiones (tope de recursos: 5). Las 15
# tareas restantes **esperan en la cola del pool** y entran en cuanto una conexión vuelve: salen en olas de 5.
# Cada ola dura 0.2 s, así que 4 olas ≈ 0.8 s.
#
# La sexta petición **no puede** usar ninguna de las cinco conexiones mientras sigan en vuelo: en HTTP/1.1 una
# conexión lleva una petición a la vez. Cuando la petición de una conexión termina, la conexión **sí se reutiliza**
# (`keep-alive`): la sexta la toma sin abrir otra.
#
# **Qué esperar.** 0.8 s, 5 puertos, 5 peticiones por ola, y 4 peticiones por cada conexión.

# %%
# celda 5.2
import asyncio, time
from collections import Counter
import httpx

limites = httpx.Limits(max_connections=5)     # el pool del cliente: a lo más 5 conexiones
async with httpx.AsyncClient(limits=limites, timeout=30) as cliente:
    async def una(i):
        d = (await cliente.get(f"{URL}/quien?lento=0.2")).json()   # 0.2 s en el servidor
        return i, round((time.perf_counter() - t0) / 0.2), d       # ola = fin / 0.2 s
    t0 = time.perf_counter()
    res = await asyncio.gather(*(una(i) for i in range(20)))      # 20 a la vez
print(f"20 peticiones, pool de 5: {time.perf_counter() - t0:.2f} s")
print("puertos distintos:", len({d["puerto"] for _, _, d in res}))
print("peticiones por ola:", dict(sorted(Counter(ola for _, ola, _ in res).items())))
print("peticiones por conexión:", sorted(Counter(d["puerto"] for _, _, d in res).values()))

# %% [markdown]
# ### 5.2 ampliada: el Gantt por petición
#
# Se repite el experimento anotando, para cada petición, **dos** intervalos:
#
# - `permiso` (ámbar): desde que se creó la tarea hasta que consiguió una conexión. Es la espera **en la cola del
#   pool**.
# - `espera` (contorno): la petición en vuelo, 0.2 s en el servidor.
#
# Un detalle de honestidad: `httpx` no avisa cuándo una petición obtiene la conexión. Aquí el inicio del vuelo se
# **estima** como `fin − 0.2 s` (el servidor duerme exactamente 0.2 s); el fin sí es medido. Con tareas cuyo
# tiempo en el servidor se conoce eso basta para que el dibujo muestre las olas.
#
# **Qué esperar.** Cinco filas sin barra ámbar (ola 1), cinco con 0.2 s de ámbar (ola 2), y así hasta 0.6 s.

# %%
# Gantt del pool de 5: una fila por petición, ámbar = esperó en la cola del pool.
async def una_g(cliente, i, creada):
    d = (await cliente.get(f"{URL}/quien?lento=0.2")).json()
    fin = time.perf_counter()
    ini = fin - 0.2                                            # NUEVO: inicio del vuelo estimado
    if ini - creada > 0.02:
        registra(f"petición {i:02d}", creada, ini, "permiso")  # NUEVO: esperó en la cola del pool
    registra(f"petición {i:02d}", max(ini, creada), fin, "espera")
    return d

reinicia()
async with httpx.AsyncClient(limits=httpx.Limits(max_connections=5), timeout=30) as cliente:
    creada = time.perf_counter()
    vistos = await asyncio.gather(*(una_g(cliente, i, creada) for i in range(20)))
T_pool5 = time.perf_counter() - creada
dibuja("Pool de 5 conexiones, 20 peticiones de 0.2 s · ámbar = espera en la cola del pool")
por_conexion = sorted(Counter(d["puerto"] for d in vistos).values())
print(f"{T_pool5:.2f} s · puertos {len(por_conexion)} · peticiones por conexión {por_conexion}")
CIFRAS.update(pool5_20_s=T_pool5, pool5_puertos=len(por_conexion))
assert 0.75 <= T_pool5 < 1.3 and len(por_conexion) <= 5
assert sum(por_conexion) == 20 and max(por_conexion) >= 4, "las conexiones se reutilizan"

# %% [markdown]
# ## 5.3 · Un pool es una cola de objetos
#
# Un pool de conexiones es, en esencia, una **cola de objetos reales** con dos operaciones: *prestar* (sacar uno;
# si no queda ninguno, esperar) y *devolver* (volver a meterlo). Un `Semaphore` sólo cuenta; no sabe qué objetos hay.
# La clase siguiente es el pool completo, sin abrir ni cerrar conexiones de verdad (son cadenas de texto que
# representan conexiones a una BD).
#
# Con ella se mide la regla de la página: **suelta el recurso antes de la espera larga**. Una tarea usa la
# conexión 0.2 s (consulta) y luego espera 0.5 s a *otra* API que no necesita la BD. Con $k=3$ conexiones y 12
# tareas:
#
# - *retener* hasta el final: cada tarea ocupa la conexión 0.7 s → $4\times0.7=2.8$ s;
# - *soltar* antes de la espera larga: cada tarea la ocupa 0.2 s → $4\times0.2+0.5=1.3$ s.
#
# **Qué esperar.** 2.8 s contra 1.3 s: la misma BD, la misma carga, más del doble de capacidad por haber soltado
# antes.

# %%
# La clase Pool: una cola de conexiones. prestar = get, devolver = put.
class Pool:
    def __init__(self, k):
        self.libres = asyncio.Queue()                  # la cola de objetos reales
        for i in range(k):
            self.libres.put_nowait(f"conexión-{i}")    # k conexiones (simuladas)
        self.k = k
    async def prestar(self):
        return await self.libres.get()                 # si no queda ninguna, la tarea se suspende aquí
    def devolver(self, conexion):
        self.libres.put_nowait(conexion)               # otra tarea suspendida la recibe
    def en_uso(self):
        return self.k - self.libres.qsize()

p = Pool(2)
a = await p.prestar(); b = await p.prestar()
print("prestadas:", a, b, "· en uso:", p.en_uso(), "· libres:", p.libres.qsize())
try:
    await asyncio.wait_for(p.prestar(), timeout=0.1)   # la tercera no puede: no hay conexión libre
except asyncio.TimeoutError:
    print("la tercera petición esperó 0.1 s y no consiguió conexión: el pool está lleno")
p.devolver(a)
print("devuelta", a, "· ahora la toma la siguiente:", await p.prestar())
assert p.en_uso() == 2

# %%
# celda 5.3
async def con_pool(retener, k=3, n=12):
    pool = asyncio.Queue()
    for i in range(k):
        pool.put_nowait(f"conexión-{i}")      # k conexiones (simuladas) a la BD
    async def tarea():
        c = await pool.get()                  # pedir prestada: espera si no queda ninguna
        await asyncio.sleep(0.2)              # la consulta usa la conexión
        if not retener: pool.put_nowait(c)    # soltar ANTES de la espera larga
        await asyncio.sleep(0.5)              # otra API: no necesita la BD
        if retener: pool.put_nowait(c)        # soltar DESPUÉS: la tuvo 0.7 s
    t0 = time.perf_counter()
    await asyncio.gather(*(tarea() for _ in range(n)))
    return time.perf_counter() - t0
for retener in (True, False):
    print(f"{'retiene' if retener else 'suelta '} la conexión: {await con_pool(retener):.2f} s")

# %% [markdown]
# ### 5.3 ampliada: lo mismo con la clase `Pool` y con Gantt
#
# Misma comparación, ahora con la clase `Pool` y con 6 tareas para que el dibujo quepa. En el Gantt, ámbar es
# la espera por una conexión; el contorno es "la tarea usa la conexión" (consulta) o "la tarea espera a la otra
# API". Observa **cuándo** reaparece el ámbar en el segundo dibujo: casi nunca, porque las conexiones vuelven al
# pool a los 0.2 s.

# %%
# Retener contra soltar, con la clase Pool y con Gantt (6 tareas, k=3).
async def tarea_pool(pool, i, retener):
    creada = time.perf_counter()
    c = await pool.prestar()                                   # NUEVO: el pool, no la cola suelta
    obtiene = time.perf_counter()
    await asyncio.sleep(0.2)                                   # consulta: la conexión está en uso
    if not retener: pool.devolver(c)                           # suelta ANTES de la espera larga
    consulta = time.perf_counter()
    await asyncio.sleep(0.5)                                   # otra API
    fin = time.perf_counter()
    if retener: pool.devolver(c)
    registra(f"tarea {i}", creada, obtiene, "permiso")         # NUEVO: espera por la conexión
    registra(f"tarea {i}", obtiene, consulta, "espera")        # consulta en la BD
    registra(f"tarea {i}", consulta, fin, "espera")            # otra API

tiempos = {}
for retener in (True, False):
    reinicia()
    pool = Pool(3)
    t0 = time.perf_counter()
    await asyncio.gather(*(tarea_pool(pool, i, retener) for i in range(6)))
    tiempos[retener] = time.perf_counter() - t0
    dibuja(f"{'RETIENE' if retener else 'SUELTA'} la conexión · 6 tareas, k=3 · {tiempos[retener]:.2f} s")
retiene_s, suelta_s = await con_pool(True), await con_pool(False)   # los números de las 12 tareas, como en 5.3
CIFRAS.update(retiene_s=retiene_s, suelta_s=suelta_s)
print(f"12 tareas, k=3: retiene {retiene_s:.2f} s · suelta {suelta_s:.2f} s · razón {retiene_s / suelta_s:.2f}")
assert 2.7 <= retiene_s < 3.2 and 1.25 <= suelta_s < 1.6
assert tiempos[True] > tiempos[False]

# %% [markdown]
# ## 5.4 · Semáforo y pool juntos: ¿quién limita?
#
# Cuando hay un `Semaphore(ks)` por encima de un pool de `kp` conexiones, lo que realmente está en vuelo es
# $\min(k_s,k_p)$. Tres combinaciones con 20 peticiones de 0.2 s:
#
# | `Semaphore` | pool | quien manda | olas $\lceil20/\min\rceil$ | tiempo esperado |
# |---:|---:|---|---:|---:|
# | 32 | 5 | pool | 4 | 0.8 s |
# | 5 | 5 | los dos | 4 | 0.8 s |
# | 3 | 5 | semáforo | 7 | 1.4 s |
#
# Con `Semaphore(3)` el pool **nunca abre más de 3 conexiones**: no hay petición que las pida. El puerto es la
# prueba: mide cuántas conexiones se abrieron de verdad.

# %%
# celda 5.4
async def lote(permisos, conexiones, n=20):
    sem = asyncio.Semaphore(permisos)                       # tope de entrada: cuenta permisos
    limites = httpx.Limits(max_connections=conexiones)      # tope de recursos: conexiones reales
    async with httpx.AsyncClient(limits=limites, timeout=30) as c:
        async def una():
            async with sem:                                 # el permiso se retiene durante el await
                return (await c.get(f"{URL}/quien?lento=0.2")).json()["puerto"]
        t0 = time.perf_counter()
        puertos = await asyncio.gather(*(una() for _ in range(n)))
    return time.perf_counter() - t0, len(set(puertos))

for permisos, conexiones in [(32, 5), (5, 5), (3, 5)]:
    t, p = await lote(permisos, conexiones)
    print(f"Semaphore({permisos:2d}) + pool de {conexiones}: {t:.2f} s · {p} puertos")

# %% [markdown]
# ### 5.4 ampliada: la tabla contra la predicción
#
# Se calcula la predicción $\lceil n/\min(k_s,k_p)\rceil\cdot0.2$ s y el número de puertos esperado
# ($\min(k_s,k_p)$) y se compara con cada medición. Dos combinaciones más: `Semaphore(2)` y `Semaphore(1)`.

# %%
# Tabla: predicción contra medición para más combinaciones.
import math
filas = []
for permisos, conexiones in [(32, 5), (5, 5), (3, 5), (2, 5), (1, 5)]:
    t, p = await lote(permisos, conexiones)
    esperado = math.ceil(20 / min(permisos, conexiones)) * 0.2
    filas.append((permisos, conexiones, t, esperado, p, min(permisos, conexiones)))
print(f"{'sem':>4}{'pool':>5}{'medido':>8}{'predicho':>9}{'puertos':>8}{'esperados':>10}")
for f in filas:
    print(f"{f[0]:>4}{f[1]:>5}{f[2]:>8.2f}{f[3]:>9.2f}{f[4]:>8}{f[5]:>10}")
CIFRAS["sem3_pool5_s"] = filas[2][2]
assert all(f[2] >= f[3] * 0.98 for f in filas), "ninguna medición puede estar bajo la predicción"
assert all(f[2] < f[3] * 1.5 for f in filas)
assert all(f[4] <= f[5] for f in filas), "nunca más conexiones que min(sem, pool)"

# %% [markdown]
# ## 5.5 (ejercicio) · 500 llamadas con un pool de 100: con y sin `Semaphore(32)`
#
# Con 500 llamadas de 0.2 s y 100 conexiones, lo ideal son 5 olas ≈ 1 s. Pero con **100 permisos** (o sin
# semáforo), la medición en esta máquina tarda **varios segundos** y abre más puertos que conexiones permitidas. La
# causa se midió en `.superpowers/medidas-10-2/hechos_pool.md`: con un pool de 100 y 500 peticiones, la cola
# vive **dentro** de `httpx` y su gestión recorre cola × conexiones en cada evento. Es **CPU del cliente**, no
# espera de red. Con un semáforo de 32 **por encima**, el pool sólo ve 32 peticiones a la vez y la cola queda en
# el semáforo, que es barata.
#
# La celda 5.5 de la página mide una vez cada combinación. Después, en la ampliación, el ejercicio es **repetirla
# 3 veces** y mirar la mediana y la CPU del cliente (`time.process_time()` mide el tiempo de CPU del proceso, no
# el reloj de pared).
#
# **Qué esperar.** Con 100 permisos: ≈ 8–10 s de pared, casi todos de CPU. Con 32: ≈ 3.4 s. Esta corrida tarda
# ≈ 45 s en total.

# %%
# celda 5.5
for permisos, conexiones in [(100, 100), (32, 100)]:
    t, p = await lote(permisos, conexiones, n=500)          # la función de la celda 5.4
    print(f"500 llamadas, Semaphore({permisos}) + pool de {conexiones}: {t:.2f} s · {p} puertos")

# %% [markdown]
# ### 5.5 ampliada: tres repeticiones, mediana y CPU del cliente
#
# Una sola medición engaña. Se repite tres veces cada combinación y se reporta la mediana. La columna *CPU* es
# `time.process_time()` antes y después: si la CPU del cliente es casi igual al tiempo de pared, el cliente
# estuvo ocupado calculando, no esperando.

# %%
# Ejercicio: 3 repeticiones por combinación, con mediana y CPU del cliente.
REPETICIONES = 3
tabla = {}
for permisos, conexiones in [(100, 100), (32, 100)]:
    corridas = []
    for _ in range(REPETICIONES):
        cpu0 = time.process_time()                          # NUEVO: tiempo de CPU del proceso
        t, p = await lote(permisos, conexiones, n=500)
        corridas.append((t, time.process_time() - cpu0, p))
    tabla[permisos] = corridas
print(f"{'semáforo':>9}{'pool':>6}{'mediana s':>10}{'CPU s':>7}{'puertos':>8}   todas")
for permisos, corridas in tabla.items():
    mediana = statistics.median(c[0] for c in corridas)
    cpu = statistics.median(c[1] for c in corridas)
    puertos = max(c[2] for c in corridas)
    todas = " ".join(f"{c[0]:.1f}" for c in corridas)
    print(f"{permisos:>9}{100:>6}{mediana:>10.2f}{cpu:>7.2f}{puertos:>8}   {todas}")
med100 = statistics.median(c[0] for c in tabla[100])
med32 = statistics.median(c[0] for c in tabla[32])
CIFRAS.update(pool100_500_s=med100, pool100_sem32_500_s=med32)
print(f"la cola dentro del pool cuesta ×{med100 / med32:.1f} el tiempo del semáforo de 32 por encima")
assert med32 < med100, "con el semáforo de 32 por encima, el lote debe ser más rápido"
assert med32 < 5.0

# %% [markdown]
# ## 5.6 · Un pool que no limita: `requests.Session` con 20 hilos
#
# `requests` también tiene un pool (el de `urllib3`, con `pool_maxsize=10` por omisión), y es la fuente de una
# confusión frecuente: **ese pool no hace esperar a nadie**. Es un *caché* de conexiones, no un tope. Con
# `pool_block=False` (el valor por omisión), si 20 hilos piden conexión a la vez, `urllib3` abre **20**; cuando
# vuelven, guarda 10 y **tira 10** con el aviso `Connection pool is full, discarding connection`.
#
# Para ver el aviso se engancha un *handler* al logger `urllib3.connectionpool`. Después se repite con
# `HTTPAdapter(pool_maxsize=5, pool_block=True)`: ahora el pool sí es un tope y hace esperar.
#
# **Qué esperar.** Primera parte: 20 puertos y ≈ 10 avisos, en ≈ 0.22 s. Segunda: ≤ 5 puertos y ≈ 0.8 s.

# %%
# Session compartida por 20 hilos: el pool NO limita (pool_block=False) y tira conexiones.
avisos = []
class Captura(logging.Handler):
    def emit(self, record):
        avisos.append(record.getMessage())                      # guarda el texto de cada aviso
logger = logging.getLogger("urllib3.connectionpool")
manejador = Captura(level=logging.WARNING)
logger.addHandler(manejador)

def pedir_quien(s, _):
    return s.get(f"{URL}/quien?lento=0.2").json()               # cada hilo hace una petición de 0.2 s

with requests.Session() as s, ThreadPoolExecutor(max_workers=20) as hilos:
    t0 = time.perf_counter()
    vistos = list(hilos.map(lambda i: pedir_quien(s, i), range(20)))   # 20 hilos, 20 peticiones a la vez
    T_sin_bloqueo = time.perf_counter() - t0
puertos_sin = len({v["puerto"] for v in vistos})
print(f"Session, 20 hilos, pool_maxsize=10 (por omisión): {T_sin_bloqueo:.2f} s · {puertos_sin} puertos · {len(avisos)} avisos")
print("ejemplo de aviso:", avisos[0] if avisos else "(ninguno)")
n_avisos = len(avisos)                                          # se guarda antes de limpiar la lista

# NUEVO: el mismo experimento con pool_block=True y pool_maxsize=5
avisos.clear()
with requests.Session() as s, ThreadPoolExecutor(max_workers=20) as hilos:
    s.mount("http://", HTTPAdapter(pool_connections=1, pool_maxsize=5, pool_block=True))   # NUEVO: el pool hace esperar
    t0 = time.perf_counter()
    vistos = list(hilos.map(lambda i: pedir_quien(s, i), range(20)))
    T_con_bloqueo = time.perf_counter() - t0
puertos_con = len({v["puerto"] for v in vistos})
print(f"Session, 20 hilos, pool_maxsize=5, pool_block=True: {T_con_bloqueo:.2f} s · {puertos_con} puertos · {len(avisos)} avisos")
logger.removeHandler(manejador)
CIFRAS.update(sesion20_puertos=puertos_sin, sesion20_avisos=n_avisos)
assert n_avisos >= 1, "debió salir al menos un aviso Connection pool is full"
assert puertos_sin > 10, "sin pool_block el pool de requests abre más conexiones que su maxsize"
assert puertos_con <= 5 and T_con_bloqueo >= 0.75
assert T_con_bloqueo > T_sin_bloqueo * 2

# %% [markdown]
# ## Cierre del tema: la tabla de lo medido
#
# Cada renglón responde una de las preguntas de la página y viene de una celda de arriba.
#
# | pregunta | respuesta medida |
# |---|---|
# | ¿`requests.get` suelto reutiliza la conexión? | no: un puerto por llamada |
# | ¿`Session` la reutiliza? | sí: 1 puerto, `peticion_en_conexion` crece |
# | ¿el pool de 5 deja que la 6.ª use una de las 5 en vuelo? | no: espera en la cola del pool |
# | ¿se reutiliza la conexión que terminó? | sí: 4 peticiones por conexión |
# | ¿retener o soltar? | soltar antes de la espera larga: la misma BD rinde más del doble |
# | ¿qué limita, el semáforo o el pool? | el menor de los dos |
# | ¿cuándo cuesta CPU la cola del pool? | con muchas peticiones en la cola de `httpx` |
# | ¿el pool de `requests` limita? | no, salvo `pool_block=True` |

# %%
print(f"{'cifra':<24}{'valor':>10}")
for nombre, valor in CIFRAS.items():
    print(f"{nombre:<24}{valor:>10.2f}" if isinstance(valor, float) else f"{nombre:<24}{valor:>10}")
assert CIFRAS["puertos_suelto"] == 20 and CIFRAS["puertos_sesion"] == 1
assert CIFRAS["pool5_puertos"] <= 5 and CIFRAS["retiene_s"] > 2 * CIFRAS["suelta_s"] * 0.95
assert CIFRAS["pool100_sem32_500_s"] < CIFRAS["pool100_500_s"]
print("tema 5: todas las comprobaciones pasan")
