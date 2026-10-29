# %% [markdown]
# ## 11.1 · D1: la misma espera de 0.5 s, escrita de tres maneras
#
# **Qué vamos a ver.** El servidor tiene tres endpoints que hacen lo mismo:
# esperar `w = 0.5` segundos y responder. Lo único que cambia es **cómo**
# esperan. Se mandan **n = 12 peticiones simultáneas** a cada uno, contra
# **un solo worker** (un solo proceso), y se mide con `time.monotonic` el
# **total**: desde que salen las 12 hasta que todas contestan.
#
# **Qué esperamos.** Tres tiempos totales muy distintos para la misma espera.
# Antes de correr la celda, estas son las tres cuentas; lo que cambia entre
# ellas es **quién ejecuta la espera y si la espera bloquea un hilo**.
#
# **Las variables (las mismas en las tres fórmulas).**
#
# - **n**: número de peticiones simultáneas (aquí 12).
# - **w**: segundos que espera cada petición (aquí 0.5).
# - **k_h**: cuántos hilos tiene el pool donde FastAPI ejecuta las funciones
#   `def` (el limitador de AnyIO; por omisión **40**).
# - **T**: el tiempo total que mide la celda, de la primera petición enviada a
#   la última respuesta recibida.
#
# **Las tres versiones.**
#
# 1. **`/def-bloqueante`: `def` con `time.sleep(w)`.**
#    - FastAPI manda cada petición a un **hilo del pool** (hasta k_h a la vez).
#    - Cada hilo se duerme por su cuenta; un hilo dormido no impide que otro
#      duerma.
#    - Si n ≤ k_h, las n esperas corren a la vez. Si n > k_h, las que sobran
#      esperan turno en tandas.
#    - **T_def ≈ ⌈n / k_h⌉ · w.** Aquí ⌈12 / 40⌉ = 1 tanda, así que
#      **T ≈ 0.5 s**.
# 2. **`/async-bloqueante`: `async def` con `time.sleep(w)`.**
#    - Una `async def` corre en el hilo del **event loop**, que es **un solo
#      hilo**.
#    - `time.sleep` **bloquea** ese hilo: mientras duerme no se atiende
#      ninguna otra petición ni se cuenta ningún tic.
#    - Las n esperas se hacen una tras otra.
#    - **T_async+sleep ≈ n · w.** Aquí 12 × 0.5 = **6 s**.
# 3. **`/async-await`: `async def` con `await asyncio.sleep(w)`.**
#    - También corre en el hilo del loop, pero `await` **cede el hilo**: el
#      loop deja esa petición esperando y atiende las otras 11.
#    - Las n esperas se traslapan en un solo hilo.
#    - **T_async+await ≈ w.** Aquí **T ≈ 0.5 s**.
#
# **El latido.** Para ver el bloqueo, el servidor anota un tic cada 10 ms.
#
# - Si el loop está libre hay un tic cada 10 ms (hueco ≈ 0.01 s).
# - Si el loop está bloqueado, los tics se detienen.
# - El **hueco máximo** entre tics es cuánto tiempo estuvo bloqueado el loop.
# - La celda llama a `POST /reinicia` (pone el latido a cero) antes de cada
#   versión y a `GET /latido` (devuelve `max_gap`) al terminar.
#
# **Cómo se mide.** Antes de medir, la celda abre las 12 conexiones con una
# petición a `/quien` cada una (calentamiento), para que el tiempo de
# establecerlas no se mezcle con la espera. El servidor se lanza dentro de la
# celda y se cierra en un `finally`; todo el bloque tiene un plazo de 60 s.

# %%
# celda 11.1
import asyncio
import httpx

W = 0.5          # segundos que espera cada petición
N_PETICIONES = 12

LIMITES = httpx.Limits(max_connections=20, max_keepalive_connections=20)
PLAZOS = httpx.Timeout(30.0)       # lectura de 30 s: mayor que 2*12*w = 12 s

VERSIONES = (
    ("def + time.sleep", "cada petición va a su hilo", "/def-bloqueante"),
    ("async def + time.sleep", "un hilo, el sleep lo bloquea", "/async-bloqueante"),
    ("async def + await asyncio.sleep", "await cede el hilo", "/async-await"),
)


async def mide_version(base, ruta):
    """12 peticiones simultáneas a `ruta`; devuelve (total, hueco máximo del latido)."""
    async with httpx.AsyncClient(limits=LIMITES, timeout=PLAZOS) as cliente:
        # calienta las 12 conexiones (keep-alive) antes de medir
        await asyncio.gather(*(cliente.get(base + "/quien") for _ in range(N_PETICIONES)))
        await cliente.post(base + "/reinicia")          # latido a cero

        t0 = time.monotonic()
        respuestas = await asyncio.gather(*(
            cliente.get(f"{base}{ruta}?s={W}") for _ in range(N_PETICIONES)))
        total = time.monotonic() - t0
        hueco = (await cliente.get(base + "/latido")).json()["max_gap"]
    assert all(r.status_code == 200 for r in respuestas)
    return total, hueco


proc = lanza_servidor()
try:
    print(f"servidor en {proc.url} (un worker)")
    totales = {}
    async with asyncio.timeout(60):                      # plazo global
        for nombre, _, ruta in VERSIONES:
            print(f"midiendo {nombre} ...")
            totales[nombre] = await mide_version(proc.url, ruta)
finally:
    detiene_servidor(proc)

print(f"\n{N_PETICIONES} peticiones simultáneas, cada una espera {W} s")
print(f"{'versión':<33} {'qué pasa':<30} {'total (s)':>9} {'hueco máx. latido (s)':>22}")
for nombre, que_pasa, _ in VERSIONES:
    total, hueco = totales[nombre]
    print(f"{nombre:<33} {que_pasa:<30} {total:>9.2f} {hueco:>22.3f}")
print(f"esperado: total ~{W} s, ~{N_PETICIONES * W:.1f} s y ~{W} s; "
      f"hueco < 0.1 s, ~{N_PETICIONES * W:.1f} s y < 0.1 s")
print("\nLo que importa no es la palabra async, sino si la espera BLOQUEA el hilo "
      "o lo CEDE.")

(t_def, h_def), (t_blq, h_blq), (t_aw, h_aw) = (totales[n] for n, _, _ in VERSIONES)
assert t_blq >= 4 and h_blq >= 2, "la espera bloqueante debía tardar y bloquear el loop"
assert t_def <= 1.5 and t_aw <= 1.5, "las esperas que no bloquean el loop debían traslaparse"
assert h_def < 0.1 and h_aw < 0.1, "el loop debía seguir libre"

# %% [markdown]
# ### Salida esperada de la celda 11.1
#
# Una tabla con tres renglones, total y hueco máximo del latido **en rangos**,
# no exactos:
#
# - `def + time.sleep`: total **cerca de 0.5 s** (no más de 1.5 s) y hueco
#   **menor que 0.1 s**. Las 12 esperas corrieron a la vez, cada una en su
#   hilo, y el loop siguió libre.
# - `async def + time.sleep`: total **cerca de 6 s** (al menos 4 s) y hueco
#   **también cerca de 6 s** (al menos 2 s). Las 12 esperas se hicieron una
#   tras otra porque `time.sleep` bloqueó el único hilo del loop, sin dejar
#   correr los tics.
# - `async def + await asyncio.sleep`: total **cerca de 0.5 s** (no más de
#   1.5 s) y hueco **menor que 0.1 s**. El `await` cedió el hilo y las 12
#   esperas se traslaparon.
#
# Al final, una línea con la conclusión. Si el segundo renglón sale cerca de
# 0.5 s, revisa que el servidor tenga un solo worker. **Lectura.** Las
# versiones 2 y 3 son las dos `async def`; la diferencia no está en esa palabra
# sino en la línea de espera: `time.sleep` **bloquea** el hilo del loop,
# `await asyncio.sleep` lo **cede**. Un `def` llamado desde dentro de un
# `async def` no se desplaza a otro hilo: corre en el hilo del loop.

# %% [markdown]
# ## 11.2 · Presupuesto de conexiones: R × N × k
#
# **Qué vamos a ver.** Una cuenta, sin servidor: cuántas conexiones a la base
# de datos puede llegar a abrir un despliegue, y si caben en lo que la base
# admite.
#
# **Las variables, una por una.**
#
# - **R = 3**: réplicas, es decir, copias del servicio corriendo (por
#   ejemplo, tres contenedores).
# - **N = 4**: workers por réplica; cada worker es un **proceso** distinto.
# - **k = 10**: conexiones **máximas** del pool de cada worker. Cada worker
#   crea **su propio** pool; un pool no se comparte entre procesos.
# - **max_connections = 100**: cuántas conexiones admite PostgreSQL en total
#   (valor habitual; compruébalo con `SHOW max_connections;`).
# - **plazas reservadas = 3**: conexiones que PostgreSQL guarda para
#   superusuarios (`SHOW superuser_reserved_connections;`); los demás no
#   pueden usarlas.
#
# **La cuenta, paso a paso.**
#
# 1. **Workers en total** = R × N = 3 × 4 = **12** procesos con pool propio.
# 2. **Capacidad potencial** = R × N × k = 12 × 10 = **120** conexiones: es el
#    máximo que los pools pueden llegar a abrir **a la vez**.
# 3. **Disponibles para la aplicación** = max_connections − plazas
#    reservadas = 100 − 3 = **97**.
# 4. **Diferencia** = 120 − 97 = **23** conexiones de más.
# 5. **¿Cabe?** Sí sólo si 120 ≤ 97. No cabe.
#
# **Supuestos.** 10 es el máximo **total** por pool y todas las conexiones van
# contra el mismo servidor PostgreSQL.
#
# **Qué esperamos.** La celda imprime esos mismos cinco números. Cambia R, N
# o k y repite para ver cuándo la cuenta cabe.

# %%
# celda 11.2
R, N, k = 3, 4, 10                    # réplicas, workers por réplica, conexiones por pool
max_connections = 100                 # valor habitual de PostgreSQL
reservadas = 3                        # plazas de superusuario

potencial = R * N * k
disponibles = max_connections - reservadas

print(f"capacidad potencial: R x N x k = {R} x {N} x {k} = {potencial} conexiones")
print(f"disponibles en la base: {max_connections} - {reservadas} = {disponibles}")
print(f"el máximo configurado excede lo disponible en {potencial - disponibles}")
print("¿cabe todo el máximo a la vez?", potencial <= disponibles)

# %% [markdown]
# ### Salida esperada de la celda 11.2
#
# Con los valores de partida (si los cambias, cambian las cifras):
#
# - `120` conexiones de capacidad potencial.
# - `97` disponibles.
# - El máximo configurado excede lo disponible en **23**, y la respuesta a
#   «¿cabe todo el máximo a la vez?» es `False`.
#
# **Lectura.** 120 es capacidad **potencial**, no uso: mientras los pools no
# se llenen, todo funciona. El problema aparece bajo carga, cuando varios
# pools piden su máximo a la vez, y escalar réplicas multiplica esa presión
# sobre la base. Cambia `R`, `N` o `k` y repite para ver cuándo la cuenta cabe
# en 97: la celda no tiene aserciones, así que cualquier valor se imprime.

# %% [markdown]
# ## 11.3 · Workers y cores: `uvicorn --workers 2` en vivo
#
# **Qué vamos a ver.** Hasta ahora el servidor tenía **un** proceso. Aquí se
# lanza con `--workers 2` y se miran cuatro cosas, en este orden:
#
# 1. **Procesos.** Cuántos procesos crea `uvicorn` y quién es hijo de quién
#    (se lee con `ps`).
# 2. **PIDs.** Se hacen 20 peticiones a `/contador` y se cuenta cuántos PIDs
#    distintos responden.
# 3. **Memoria.** `/contador` suma 1 a un contador que vive **en la memoria del
#    proceso** que responde. Si cada PID lleva su propia cuenta, el estado en
#    memoria **no se comparte** entre workers.
# 4. **Cálculo.** `/calcula?ms=300` es una función `def` que gasta 300 ms de
#    **CPU** (no duerme: calcula). Se mandan **4 peticiones simultáneas**, con
#    1 worker y luego con 2.
#
# **Qué esperamos del cálculo.**
#
# - **Variables.** **n = 4** peticiones, **c = 0.3 s** de CPU cada una,
#   **P** = número de workers (procesos).
# - **Con P = 1.** `def` manda cada petición a un hilo distinto, pero los
#   hilos de un mismo proceso comparten el **GIL**: sólo uno ejecuta Python a
#   la vez. Los cálculos se hacen uno tras otro: **T ≈ n · c = 1.2 s**.
# - **Con P = 2.** Cada proceso tiene su propio intérprete y su propio GIL,
#   así que dos cálculos corren a la vez en dos cores. Si las 4 peticiones se
#   reparten 2 y 2: **T ≈ (n / P) · c = 0.6 s**.
# - **Cuidado con el reparto.** Un worker se asigna a la **conexión**, no a
#   cada petición: el sistema operativo le entrega a un worker cada conexión
#   nueva y esa conexión se queda con él mientras siga abierta. Por eso la
#   celda abre varias conexiones, mira qué PID atiende cada una y se queda con
#   **dos por cada PID** antes de medir. Sin eso, 3 contra 1 es posible y el
#   tiempo no mejora.
#
# **Lanzamiento y limpieza.** La celda lanza su propio servidor (no usa
# `lanza_servidor`, que fuerza un worker), en un puerto libre, y lo cierra en
# un `finally`: manda `terminate` al proceso principal, espera, y si quedaron
# procesos descendientes los mata. Al final verifica con `ps` que no quedó
# ninguno.

# %%
# celda 11.3
import asyncio
import collections
import httpx

N_CALCULOS, C_MS = 4, 300


def arbol(raiz):
    """Descendientes de `raiz` según `ps`: lista de (pid, ppid, comando)."""
    filas = subprocess.run(["ps", "-eo", "pid=,ppid=,args="], capture_output=True,
                           text=True).stdout.splitlines()
    todos = {}
    for fila in filas:
        pid, ppid, cmd = fila.split(None, 2)
        todos[int(pid)] = (int(ppid), cmd)
    desc, cola = [], [raiz]
    while cola:
        padre = cola.pop()
        for pid, (pp, cmd) in todos.items():
            if pp == padre:
                desc.append((pid, pp, cmd))
                cola.append(pid)
    return desc


def rol(cmd):
    """Nombre legible del proceso según su línea de comando."""
    if "resource_tracker" in cmd:
        return "resource_tracker (vigila recursos de multiprocessing)"
    if "spawn_main" in cmd:
        return "worker (lanzado con multiprocessing, modo spawn)"
    return cmd[:60]


def lanza_con_workers(n_workers, puerto, plazo=25.0):
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app_arq:app", "--port", str(puerto),
         "--workers", str(n_workers), "--log-level", "warning"],
        cwd=CARPETA, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{puerto}"
    limite = time.monotonic() + plazo
    while time.monotonic() < limite:
        if proc.poll() is not None:
            raise RuntimeError(f"el servidor terminó (código {proc.returncode})")
        try:
            with urllib.request.urlopen(url + "/quien", timeout=1) as r:
                if r.status == 200:
                    return proc, url
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"sin respuesta de /quien en {plazo} s")


def cierra_con_workers(proc):
    """terminate al principal; mata lo que siga vivo de sus descendientes."""
    if proc is None:
        return
    restos = [pid for pid, _, _ in arbol(proc.pid)]
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    time.sleep(0.5)
    for pid in restos:
        try:
            os.kill(pid, 9)       # si el pid ya no existe, no hay nada que matar
        except ProcessLookupError:
            pass


async def conexiones_repartidas(url, por_pid, maximo=24):
    """Abre conexiones una a una y conserva `por_pid` por cada PID distinto."""
    elegidas, cerrar = collections.defaultdict(list), []
    for _ in range(maximo):
        c = httpx.AsyncClient(limits=httpx.Limits(max_connections=1), timeout=30)
        pid = (await c.get(url + "/quien")).json()["pid"]
        if len(elegidas[pid]) < por_pid:
            elegidas[pid].append(c)
        else:
            cerrar.append(c)
        if len(elegidas) >= 2 and all(len(v) >= por_pid for v in elegidas.values()):
            break
    for c in cerrar:
        await c.aclose()
    return [c for v in elegidas.values() for c in v]


async def mide_calculo(url, n_workers):
    if n_workers == 1:
        clientes = [httpx.AsyncClient(timeout=30) for _ in range(N_CALCULOS)]
        for c in clientes:
            await c.get(url + "/quien")                 # abre la conexión
    else:
        clientes = await conexiones_repartidas(url, N_CALCULOS // n_workers)
    try:
        t0 = time.monotonic()
        rs = await asyncio.gather(*(c.get(f"{url}/calcula?ms={C_MS}") for c in clientes))
        return time.monotonic() - t0, collections.Counter(r.json()["pid"] for r in rs)
    finally:
        for c in clientes:
            await c.aclose()


puerto = puerto_libre()
proc = None
try:
    # ---- 1) dos workers: procesos, PIDs, contadores ----
    proc, url = lanza_con_workers(2, puerto)
    print(f"proceso principal (supervisor): PID {proc.pid}")
    print("descendientes según ps:")
    for pid, ppid, cmd in arbol(proc.pid):
        print(f"  PID {pid}  padre {ppid}  {rol(cmd)}")

    ultimos, veces = {}, collections.Counter()
    async with httpx.AsyncClient(timeout=10) as c:       # una sola conexión
        for _ in range(20):
            r = (await c.get(url + "/contador")).json()
            ultimos[r["pid"]] = r["contador"]
            veces[r["pid"]] += 1
    print(f"\n20 peticiones a /contador con UNA conexión: {len(veces)} PID distinto(s)")
    for pid in veces:
        print(f"  PID {pid}: respondió {veces[pid]} veces, su contador va en {ultimos[pid]}")
    veces2, ultimos2 = collections.Counter(), {}
    for _ in range(20):                                   # una conexión nueva cada vez
        r = httpx.get(url + "/contador").json()
        ultimos2[r["pid"]] = r["contador"]
        veces2[r["pid"]] += 1
    print(f"20 peticiones más, cada una con conexión nueva: {len(veces2)} PID distinto(s)")
    for pid in veces2:
        print(f"  PID {pid}: respondió {veces2[pid]} veces, su contador va en {ultimos2[pid]}")

    # ---- 2) cálculo con 2 workers ----
    async with asyncio.timeout(60):
        t2, quienes2 = await mide_calculo(url, 2)
    cierra_con_workers(proc)
    proc = None

    # ---- 3) cálculo con 1 worker ----
    proc, url = lanza_con_workers(1, puerto_libre())
    async with asyncio.timeout(60):
        t1, quienes1 = await mide_calculo(url, 1)
finally:
    cierra_con_workers(proc)

print(f"\n{N_CALCULOS} cálculos simultáneos de {C_MS} ms de CPU cada uno")
print(f"{'workers':>8} {'PIDs que atendieron':>20} {'total (s)':>10} {'esperado':>12}")
print(f"{1:>8} {len(quienes1):>20} {t1:>10.2f} {'~' + str(N_CALCULOS * C_MS / 1000) + ' s':>12}")
print(f"{2:>8} {len(quienes2):>20} {t2:>10.2f} {'~' + str(N_CALCULOS * C_MS / 2000) + ' s':>12}")
print(f"\nprocesos que quedan del servidor: "
      f"{len([1 for _, _, cmd in arbol(os.getpid()) if 'app_arq' in cmd or 'multiprocessing' in cmd])}")

# %% [markdown]
# ### Salida esperada de la celda 11.3
#
# **Procesos (lo que se observó con uvicorn 0.54).** El proceso que lanzaste
# es el **supervisor**; `ps` lo muestra con la línea `python -m uvicorn
# app_arq:app ... --workers 2`. Sus hijos son **3**: los **2 workers**, que
# `ps` muestra como `python -c "from multiprocessing.spawn import spawn_main
# ..."` (no dicen `uvicorn` ni `app_arq`) y un `resource_tracker` de
# `multiprocessing`. Por eso `ps | grep uvicorn` ve **un** solo proceso aunque
# haya dos workers: para contarlos hay que mirar los **hijos** del supervisor.
# El supervisor no atiende peticiones: crea el socket de escucha, lanza los
# workers y los vigila.
#
# **PIDs y contadores.**
#
# - Con **una** conexión abierta, las 20 peticiones las atiende **el mismo
#   PID** y su contador llega a 20.
# - Con una conexión **nueva** por petición, responden **2 PIDs distintos**
#   (el reparto no es exactamente 10 y 10) y **cada PID lleva su propio
#   contador**: los contadores no suman 20 juntos, cada uno cuenta sólo lo
#   suyo. El estado en memoria **no se comparte** entre workers.
# - **Cómo se reparten.** El supervisor crea **un** socket de escucha y los
#   workers lo heredan y hacen `accept` sobre él (no usan `SO_REUSEPORT`); el
#   sistema operativo entrega cada conexión nueva a un worker que la espere.
#   El reparto depende del sistema operativo, no es un turno estricto.
#
# **Cálculo (rangos).**
#
# - **1 worker:** total **entre 1.0 y 1.8 s** (≈ 4 × 0.3): el GIL serializa
#   los cálculos aunque haya cuatro hilos.
# - **2 workers:** total **entre 0.5 y 1.2 s** (cerca de la mitad) y **2 PIDs**
#   distintos atendiendo.
# - Al final debe decir **0** procesos del servidor.
#
# **Lectura.** Más workers = más procesos = más GIL independientes = más
# cores trabajando a la vez en cálculo. A cambio, cada worker tiene **su**
# memoria (y su propio pool de conexiones, como en 11.2): lo que debe
# compartirse tiene que vivir fuera del proceso (base de datos, Redis).
