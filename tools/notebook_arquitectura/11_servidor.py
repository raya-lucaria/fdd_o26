# %% [markdown]
# ## 11.1 · D1: la misma espera de 0.5 s, escrita de tres maneras
#
# **Qué se va a ver.** El servidor tiene tres endpoints que hacen lo mismo:
# esperar `s = 0.5` segundos y responder. Cambia sólo **cómo** esperan. Se
# mandan **12 peticiones simultáneas** a cada uno, contra **un solo worker**,
# y se mide con `time.monotonic` el **total**: desde que salen las 12 hasta que
# todas contestan. También se lee el **latido** del servidor:
#
# - el servidor anota un tic cada 10 ms;
# - si el loop está libre hay un tic cada 10 ms (hueco ≈ 0.01 s); si el loop
#   está bloqueado, los tics se detienen;
# - el hueco más largo entre tics es cuánto tiempo estuvo bloqueado el loop.
#
# La celda llama a `POST /reinicia` (pone el latido a cero) antes de cada
# versión y a `GET /latido` (devuelve `max_gap`, el hueco más largo) al
# terminar.
#
# 1. `/def-bloqueante` es una función `def` con `time.sleep(0.5)`. FastAPI
#    manda cada petición a **su propio hilo**; cada hilo se duerme por su
#    cuenta y las 12 esperas corren a la vez. Total esperado: **≈ 0.5 s**.
# 2. `/async-bloqueante` es una función `async def` con `time.sleep(0.5)`. Una
#    `async def` corre en el hilo del **event loop**, que es **un solo hilo**,
#    y `time.sleep` **bloquea** ese hilo: nada más avanza hasta que termina.
#    Las 12 esperas se hacen una tras otra: 12 × 0.5. Total esperado: **≈ 6 s**.
# 3. `/async-await` es una función `async def` con `await asyncio.sleep(0.5)`.
#    También corre en el hilo del loop, pero `await` **cede el turno**: el
#    loop deja esa petición esperando y atiende las otras 11. Las 12 esperas
#    se traslapan. Total esperado: **≈ 0.5 s**.
#
# Antes de medir, la celda abre las 12 conexiones con una petición a `/quien`
# cada una (calentamiento), para que el tiempo de establecerlas no se mezcle
# con la espera. El servidor se lanza dentro de la celda y se cierra en un
# `finally`; todo el bloque tiene un plazo de 60 s.

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
# **Qué se va a ver.** Una cuenta, sin servidor. Un despliegue con
# **R = 3** réplicas, cada una con **N = 4** workers, y cada worker con un
# pool local de hasta **k = 10** conexiones a la base de datos. Cada worker crea
# **su propio** pool (no se supone que un pool se comparta entre procesos), de
# modo que el máximo configurado contra la base es el producto
# `R × N × k = 3 × 4 × 10 = 120`.
#
# Esa cifra se compara con lo que admite una base PostgreSQL con el valor
# habitual `max_connections = 100`: con 3 plazas reservadas para superusuario
# quedan **97** para el resto (comprueba los tuyos con `SHOW max_connections;`
# y `SHOW superuser_reserved_connections;`). La cuenta supone que 10 es el
# máximo **total** por pool y que todas las conexiones van contra el mismo
# servidor.

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
