# %% [markdown]
# ## 11.1 · D1: `async def` frente a `def` con 12 peticiones simultáneas
#
# **Qué se va a ver.** El servidor tiene dos endpoints que hacen lo mismo,
# dormir `s` segundos con `time.sleep` (una espera que **bloquea** el hilo que
# la ejecuta), y se diferencian sólo en cómo están declarados:
#
# - `/async-bloqueante` es `async def`: FastAPI lo ejecuta **en el hilo del
#   event loop**. Mientras duerme, el loop no atiende nada más.
# - `/def-bloqueante` es `def`: FastAPI lo **desplaza** a un pool de hilos (el
#   limitador de AnyIO admite 40 a la vez por defecto), y el loop queda libre.
#
# La celda manda **12 peticiones simultáneas** con `w = 0.5 s` a cada endpoint,
# una modalidad tras otra, contra un **solo worker**, y mide con
# `time.monotonic` el **total**: desde que salen las 12 hasta que todas
# contestan.
#
# **El latido.** Para ver si el loop estuvo bloqueado, el servidor corre una
# tarea de fondo que cada 10 ms se duerme con `asyncio.sleep(0.01)` y, al
# despertar, anota cuánto tardó realmente en volver a correr. Si el loop está
# libre, el hueco es de unos 10 ms; si una corrutina lo bloquea con
# `time.sleep`, la tarea no vuelve a correr hasta que el loop se libera, y el
# hueco crece. `GET /latido` devuelve el **hueco máximo** (`max_gap`) y el
# número de ticks; `POST /reinicia` los pone a cero. La celda reinicia antes de
# cada modalidad y lee `/latido` al terminar.
#
# Cuenta aproximada: con `async def` las esperas se ejecutan una tras otra,
# `T ≈ 12·w = 6 s`. Además el loop corre los 12 handlers **seguidos**, sin
# dejar correr a la tarea del latido entre uno y otro, así que el hueco máximo
# es de **≈ 12·w ≈ 6 s**, no de `w`; con `def` corren a la vez en hilos, `T ≈ w = 0.5 s` (más
# algo de costo fijo) y el hueco sigue siendo pequeño (< 0.1 s). Son
# aproximaciones; lo que se verifica son rangos. Antes de medir, la celda abre
# las 12 conexiones con una petición a `/quien` cada una (calentamiento), para
# que el tiempo de establecerlas no se mezcle con la espera. El servidor se
# lanza dentro de la celda y se cierra en un `finally`.

# %%
# celda 11.1
import asyncio
import httpx

W = 0.5          # segundos que duerme cada petición
N_PETICIONES = 12

LIMITES = httpx.Limits(max_connections=20, max_keepalive_connections=20)
PLAZOS = httpx.Timeout(30.0)       # lectura de 30 s: mayor que 2*12*w = 12 s


async def mide_modalidad(base, ruta):
    """12 peticiones simultáneas a `ruta`; devuelve (total, hueco máximo del latido)."""
    async with httpx.AsyncClient(limits=LIMITES, timeout=PLAZOS) as cliente:
        # calienta las 12 conexiones (keep-alive) antes de medir
        await asyncio.gather(*(cliente.get(base + "/quien") for _ in range(N_PETICIONES)))
        await cliente.post(base + "/reinicia")          # latido a cero

        t0 = time.monotonic()
        respuestas = await asyncio.gather(*(
            cliente.get(f"{base}{ruta}?s={W}") for _ in range(N_PETICIONES)))
        total = time.monotonic() - t0

        latido = (await cliente.get(base + "/latido")).json()
    assert all(r.status_code == 200 for r in respuestas)
    return total, latido["max_gap"], latido["ticks"]


proc = lanza_servidor()
try:
    print(f"servidor en {proc.url} (un worker)")
    resultados = {}
    async with asyncio.timeout(60):                      # plazo global
        for etiqueta, ruta in (("async def", "/async-bloqueante"),
                               ("def", "/def-bloqueante")):
            print(f"midiendo {etiqueta} ...")
            resultados[etiqueta] = await mide_modalidad(proc.url, ruta)
finally:
    detiene_servidor(proc)

print(f"\n{N_PETICIONES} peticiones simultáneas, w = {W} s")
print(f"{'modalidad':<10} {'total (s)':>10} {'hueco máx. del latido (s)':>26}")
for etiqueta, (total, hueco, ticks) in resultados.items():
    print(f"{etiqueta:<10} {total:>10.2f} {hueco:>26.3f}")
print(f"esperado: async def ~ {N_PETICIONES * W:.1f} s y hueco ~ {N_PETICIONES * W:.1f} s; "
      f"def ~ {W:.1f} s y hueco < 0.1 s")

t_async, h_async, _ = resultados["async def"]
t_def, h_def, _ = resultados["def"]
assert t_async >= 8 * W and t_def <= 3 * W, "los totales salen del rango esperado"
assert h_async >= 4 * W and h_def < 0.1, "el hueco del latido sale del rango esperado"

# %% [markdown]
# ### Salida esperada de la celda 11.1
#
# Una tabla con dos renglones y valores **en rangos**, no exactos:
#
# - `async def`: total **cercano a 6 s** (al menos 4 s; las 12 esperas se
#   sirvieron una tras otra) y hueco máximo del latido **también cercano a
#   6 s** (al menos 2 s): el loop ejecutó los 12 handlers seguidos y la tarea
#   del latido no pudo volver a correr en todo ese tiempo (no sólo durante una
#   espera de `w = 0.5 s`).
# - `def`: total **cercano a 0.5 s** (no más de 1.5 s) y hueco máximo
#   **menor que 0.1 s**: las esperas corrieron en hilos y el loop siguió
#   corriendo su latido cada ~10 ms.
#
# Si `async def` sale cerca de 0.5 s o `def` cerca de 6 s, revisa que el
# servidor tenga un solo worker y que no cambiaste `time.sleep` por
# `await asyncio.sleep` (esa versión **no** bloquea el loop). **Lectura.** No
# se bloqueó la CPU, se bloqueó el **loop**: mientras un `async def` llama a
# `time.sleep`, ninguna otra corrutina avanza, incluida la del latido. Un `def`
# llamado desde dentro de un `async def` no se desplaza: corre en el hilo del
# loop.

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
