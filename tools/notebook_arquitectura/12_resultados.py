# %% [markdown]
# ## 12.1 · D2: cómo llegan los resultados (polling, long polling y SSE)
#
# **Qué se va a ver.** Un evento que ocurre en el servidor **10 s** después de
# `POST /inicia?t=10`. Tres maneras de enterarse, con **20 clientes** en cada
# una, cada modalidad **por separado** (reinicia el servidor y vuelve a
# iniciar el evento):
#
# - **polling**: cada cliente pregunta a `/listo` cada **Δ = 3 s**, con
#   reloj monotónico, y no hace consulta inicial: consulta en 3, 6, 9 y 12 s.
#   Cuenta esperada por cliente: 4 consultas (3 sin novedades) y una demora de
#   `Δ·⌈T/Δ⌉ − T = 2 s`; con 20 clientes, 80 consultas y 60 sin novedades;
# - **long polling**: una sola petición a `/espera` que el servidor mantiene
#   abierta hasta el evento; demora esperada: casi cero;
# - **SSE**: una respuesta HTTP continua en `/eventos` (streaming) que envía
#   latidos y el evento `listo`; demora esperada: casi cero.
#
# Se cuenta, por modalidad: las **consultas** que recibió el servidor, la
# **demora de detección** (desde el instante del evento hasta que el cliente se
# entera, promedio de los 20), los **long polls pendientes** (sólo cuenta las peticiones a `/espera`) y las
# **sesiones SSE abiertas** que reporta `/estado` a mitad de la espera, y los **sockets**
# que conserva el cliente (el polling con keep-alive también conserva
# conexiones, aunque no tenga peticiones pendientes). Son cosas distintas.
#
# Cada modalidad dura ~10-12 s, así que la celda tarda cerca de 35 s. Todo el
# bloque tiene un plazo global y el servidor se cierra en un `finally`.

# %%
# celda 12.1
import asyncio
import httpx

CLIENTES = 20
T_EVENTO = 10.0     # segundos hasta el evento
DELTA = 3.0         # periodo del polling
PLAZOS = httpx.Timeout(30.0)
LIMITES = httpx.Limits(max_connections=CLIENTES + 5,
                       max_keepalive_connections=CLIENTES + 5)


def sockets_de(cliente):
    """Conexiones que el cliente httpx tiene abiertas; None si no se puede inspeccionar."""
    try:
        return len(cliente._transport._pool.connections)
    except AttributeError:
        return None


async def polling(base, t_evento, cliente):
    inicio = t_evento - T_EVENTO
    consultas, k = 0, 1
    while True:
        await asyncio.sleep(max(0.0, inicio + k * DELTA - time.monotonic()))
        r = await cliente.get(base + "/listo")
        consultas += 1
        if r.json()["listo"]:
            return time.monotonic() - t_evento, consultas
        k += 1


async def long_polling(base, t_evento, cliente):
    r = await cliente.get(base + "/espera")
    assert r.json()["listo"]
    return time.monotonic() - t_evento, 1


async def sse(base, t_evento, cliente):
    async with cliente.stream("GET", base + "/eventos") as r:
        async for linea in r.aiter_lines():
            if linea.startswith("event: listo"):
                return time.monotonic() - t_evento, 1
    raise RuntimeError("el flujo SSE terminó sin el evento listo")


async def corre_modalidad(base, funcion):
    """Una modalidad completa: reinicia, inicia el evento, 20 clientes, estado."""
    async with httpx.AsyncClient(timeout=PLAZOS) as control:
        await control.post(base + "/reinicia")
        # /inicia devuelve el instante monotónico en que el SERVIDOR fijó el
        # evento; la demora se mide contra ese instante (mismo reloj: el
        # cliente y el servidor corren en esta máquina)
        t_evento = (await control.post(base + f"/inicia?t={T_EVENTO}")).json()["evento"]
        clientes = [httpx.AsyncClient(limits=LIMITES, timeout=PLAZOS)
                    for _ in range(CLIENTES)]
        try:
            tareas = [asyncio.create_task(funcion(base, t_evento, c)) for c in clientes]
            await asyncio.sleep(T_EVENTO / 2)            # a mitad de la espera
            medio = (await control.get(base + "/estado")).json()
            cuentas = [sockets_de(c) for c in clientes]
            sockets = None if None in cuentas else sum(cuentas)
            resultados = await asyncio.gather(*tareas)
            await asyncio.sleep(0.5)                     # deja cerrar los flujos
            final = (await control.get(base + "/estado")).json()
        finally:
            for t in locals().get("tareas", []):
                t.cancel()
            for c in clientes:
                await c.aclose()
    demoras = [d for d, _ in resultados]
    return {"consultas": final["consultas"] if funcion is polling
            else sum(n for _, n in resultados),
            "demora": sum(demoras) / len(demoras),
            "pendientes": medio["esperando"], "sesiones_sse": medio["sse"],
            "sockets": sockets, "sse_al_final": final["sse"]}


MODALIDADES = (("polling", polling), ("long polling", long_polling), ("SSE", sse))

proc = lanza_servidor()
try:
    print(f"servidor en {proc.url} (un worker)")
    medidas = {}
    async with asyncio.timeout(60):                      # plazo global
        for nombre, funcion in MODALIDADES:
            print(f"corriendo {nombre} con {CLIENTES} clientes (~{T_EVENTO:.0f} s) ...")
            medidas[nombre] = await corre_modalidad(proc.url, funcion)
finally:
    detiene_servidor(proc)

print(f"\nevento en T = {T_EVENTO:.0f} s, {CLIENTES} clientes por modalidad")
print(f"{'modalidad':<13} {'consultas':>9} {'demora (s)':>10} "
      f"{'long polls pendientes':>21} {'sesiones SSE':>12} {'sockets cliente':>15}")
for nombre, m in medidas.items():
    sockets_txt = "no disponible" if m["sockets"] is None else m["sockets"]
    print(f"{nombre:<13} {m['consultas']:>9} {m['demora']:>10.2f} {m['pendientes']:>21} "
          f"{m['sesiones_sse']:>12} {sockets_txt:>15}")

assert 1.5 <= medidas["polling"]["demora"] <= 3.0
assert medidas["long polling"]["demora"] < 0.5 and medidas["SSE"]["demora"] < 0.5
assert medidas["SSE"]["sse_al_final"] == 0, "quedaron sesiones SSE abiertas"

# %% [markdown]
# ### Salida esperada de la celda 12.1
#
# Una tabla con tres renglones. Los rangos son los que verifica la celda:
#
# - **polling:** `consultas` = **80** (20 clientes × 4; 60 sin novedades), demora
#   **entre 1.5 y 3.0 s** (esperado ~2 s), **0 long polls pendientes**, 0 sesiones SSE y
#   **~20 sockets** del cliente (conexiones keep-alive abiertas entre
#   consultas aunque no haya nada pendiente).
# - **long polling:** `consultas` = **20** (una petición por cliente), demora
#   **menos de 0.5 s**, **20 long polls pendientes** a mitad de la espera (el servidor
#   retiene esas peticiones abiertas), 0 sesiones SSE.
# - **SSE:** `consultas` = **20** (una apertura por cliente), demora **menos de
#   0.5 s**, 0 long polls pendientes, **20 sesiones SSE** abiertas a mitad de la espera y 20 sockets; al
#   final no queda ninguna sesión.
#
# Si el polling sale con 79 u 81 consultas, un cliente cayó justo en el borde
# del evento; repite la celda. Si `sockets cliente` dice «no disponible», tu
# versión de httpx guarda el pool en otro lugar: no afecta el resto de la
# medición. **Lectura.** Cambian tres cantidades distintas: cuántas peticiones
# hace el cliente, cuánto tarda en enterarse y qué retiene el servidor
# mientras espera. El mecanismo no decide por sí solo si se retiene un hilo o
# una tarea.
