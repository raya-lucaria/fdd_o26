# %% [markdown]
# ## 12.1 · D2: cómo llegan los resultados (polling, long polling y SSE)
#
# **Qué vamos a ver.** Un evento que ocurre en el servidor **10 s** después de
# `POST /inicia?t=10`. Hay tres maneras de que los clientes se enteren; se
# prueba cada una **por separado**, con **20 clientes**, reiniciando el
# servidor y volviendo a iniciar el evento.
#
# **Las tres modalidades.**
#
# - **Polling:** cada cliente pregunta a `/listo` cada Δ segundos.
# - **Long polling:** cada cliente hace **una** petición a `/espera` y el
#   servidor la mantiene abierta hasta que ocurre el evento.
# - **SSE:** cada cliente abre **una** respuesta HTTP continua en `/eventos`
#   (streaming); el servidor envía latidos y, al final, el evento `listo`.
#
# **Las variables del polling.**
#
# - **T = 10 s:** cuándo ocurre el evento.
# - **Δ = 3 s:** cada cuánto pregunta un cliente. Mide con reloj monotónico y
#   no hace consulta inicial: pregunta en los segundos 3, 6, 9 y 12.
# - **Clientes = 20.**
#
# **La cuenta esperada del polling, paso a paso.**
#
# 1. **Consultas por cliente.** Las que hace hasta enterarse:
#    ⌈T/Δ⌉ = ⌈10/3⌉ = 4 (en los segundos 3, 6, 9 y 12).
# 2. **Consultas sin novedades por cliente.** Las que llegan antes del
#    evento: 4 − 1 = **3** (las de los segundos 3, 6 y 9).
# 3. **Demora por cliente.** Desde el evento hasta la consulta que lo
#    descubre: Δ·⌈T/Δ⌉ − T = 3·4 − 10 = **2 s**.
# 4. **Con 20 clientes.** Consultas: 20 × 4 = **80**. Sin novedades:
#    20 × 3 = **60**.
#
# **Qué esperamos de las otras dos.** Long polling y SSE no preguntan una y
# otra vez: **20 peticiones** en total (una por cliente) y una demora **casi
# cero**, porque el servidor avisa en cuanto ocurre el evento.
#
# **Qué se mide, por modalidad.** Son cosas distintas, no las confundas:
#
# - **consultas:** las peticiones que recibió el servidor.
# - **demora de detección:** desde el instante del evento hasta que el
#   cliente se entera (promedio de los 20).
# - **long polls pendientes:** peticiones a `/espera` que el servidor retiene
#   abiertas a mitad de la espera (sólo cuenta esas).
# - **sesiones SSE abiertas:** las que reporta `/estado` a mitad de la espera.
# - **sockets del cliente:** conexiones que conserva el cliente (el polling
#   con keep-alive también las conserva entre consultas, aunque no tenga
#   peticiones pendientes).
#
# **Duración.** Cada modalidad dura ~10-12 s, así que la celda tarda cerca de
# 35 s. Todo el bloque tiene un plazo global y el servidor se cierra en un
# `finally`.

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
