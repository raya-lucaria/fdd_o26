# %% [markdown]
# ## 11.4 · El pool de Postgres visto desde el servidor
#
# **Qué se va a ver.** En la celda 11.2 se hizo una cuenta, `R × N × k`, de
# cuántas conexiones **podrían** llegar a la base. Aquí se mira una base
# PostgreSQL real, por dentro, para ver qué es exactamente cada conexión y qué
# hace un pool. La celda arranca un contenedor **temporal** de Docker con
# PostgreSQL, lo usa y lo borra.
#
# **Variables (definiciones, una por una).**
#
# - **Conexión**: un canal abierto entre tu programa y la base, por el que
#   viajan las consultas. En el programa es un objeto `psycopg.Connection`.
# - **Backend**: el **proceso del sistema operativo**, del lado de PostgreSQL,
#   que atiende una conexión. PostgreSQL crea **un backend por cada conexión**
#   que se abre, y ese proceso vive en la máquina de la **base**, no en la de
#   tu servidor web.
# - **PID**: el número con que el sistema operativo identifica un proceso. Si
#   dos conexiones tienen PID distinto, son dos procesos distintos.
# - **Consulta activa**: una consulta que **se está ejecutando ahora**. En
#   `pg_stat_activity` aparece como `state = 'active'`.
# - **Conexión ociosa**: una conexión abierta que **no está ejecutando nada**
#   (`state = 'idle'`). Sigue ocupando su backend y una plaza de la base.
# - **Pool**: un conjunto de conexiones ya abiertas que el programa **presta**
#   y devuelve, en vez de abrir y cerrar una por cada consulta.
# - **Tamaño del pool**: cuántas conexiones puede tener. En `psycopg_pool` son
#   dos números: `min_size` (las que abre al inicio y mantiene) y `max_size`
#   (el tope; el pool crece hasta ahí sólo si hay quien espere).
#
# **Qué esperamos (cuatro observaciones, A a D).**
#
# 1. **A.** Un pool de 10 conexiones abiertas son **10 backends** con **PID
#    distinto**, y esos PID son procesos del contenedor (de la base), no del
#    notebook.
# 2. **B.** Una conexión abierta no es una consulta activa: con 3 consultas de
#    `pg_sleep(2)` corriendo a la vez, 3 conexiones están `active` y las otras
#    7 siguen `idle`.
# 3. **C.** El pool es un **tope**. Con un pool de **2** conexiones y **6**
#    tareas de 0.5 s, sólo 2 corren a la vez; las demás **esperan** una
#    conexión (igual que en la página 5 esperaba el hilo). Cuenta:
#    1. tareas por tanda = tamaño del pool = 2;
#    2. tandas = ⌈6 / 2⌉ = 3;
#    3. tiempo ≈ 3 × 0.5 s = **1.5 s**.
# 4. **D.** La base tiene su propio tope, `max_connections`, y reserva unas
#    plazas (`superuser_reserved_connections`) para administradores. Se leen
#    con `SHOW` y se comparan con la cuenta de la celda 11.2.
#
# **Cómo funciona la celda.** Requiere Docker en marcha.
#
# 1. Lanza `postgres:17-alpine` con nombre único `fdd-pg-<aleatorio>`,
#    contraseña de prueba y un puerto libre del equipo (sólo `127.0.0.1`).
# 2. Espera, con plazo de 60 s, a que la base acepte conexiones.
# 3. Hace las observaciones A a D.
# 4. En el `finally` borra el contenedor con `docker rm -f`. No toca ningún
#    otro contenedor.
#
# Si Docker no está disponible o el arranque falla, la celda lo dice y
# muestra una **captura de salida previa** (rotulada «no es una ejecución»).

# %%
# celda 11.4
import concurrent.futures as cf
import secrets
import socket
import subprocess
import time

CAPTURA_PREVIA = """\
contenedor fdd-pg-9fa5fd75 (postgres:17-alpine), servidor PostgreSQL 17.11, puerto 57203

== A. Un pool de 10 conexiones = 10 backends ==
conexiones del pool vistas en pg_stat_activity: 10
PID distintos: 10  ->  [61, 62, 63, 64, 65, 66, 67, 68, 69, 70]
de esos PID, procesos que existen DENTRO del contenedor: 10 de 10
tres procesos backend según `ps` dentro del contenedor (el primero puede ser la conexión de monitoreo):
    60 postgres: postgres postgres 172.17.0.1(49098) idle
    61 postgres: postgres postgres 172.17.0.1(49104) idle
    62 postgres: postgres postgres 172.17.0.1(49108) idle

== B. Conexión ociosa (idle) vs consulta activa (active) ==
con 3 `SELECT pg_sleep(2)` en curso: 10 conexiones abiertas, 3 active, 7 idle
2 s después, sin consultas: 10 conexiones abiertas, 0 active
tras cerrar el pool: 0 conexiones del pool en la base

== C. El pool es un tope: pool de 2, 6 tareas de 0.5 s ==
tamaño del pool = 2, tareas = 6, cada una pg_sleep(0.5)
tiempo total: 1.51 s   (cuenta: ceil(6/2) x 0.5 = 1.50 s)
duración de cada tarea (incluye esperar conexión): 0.50, 0.50, 1.01, 1.01, 1.51, 1.51
backends del pool2 en la base: 2 (nunca más de 2)

== D. Los topes de la base ==
max_connections = 100
superuser_reserved_connections = 3
plazas para clientes normales = 100 - 3 = 97
cuenta de la celda 11.2: R x N x k = 3 x 4 x 10 = 120  ->  NO cabe

contenedor fdd-pg-9fa5fd75 borrado"""


def docker(*args, plazo=60):
    return subprocess.run(["docker", *args], capture_output=True, text=True,
                          timeout=plazo, stdin=subprocess.DEVNULL)


def puerto_libre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def espera_postgres(dsn, plazo=60.0):
    """Reintenta conectar hasta `plazo` s; devuelve la versión del servidor."""
    import psycopg
    fin = time.monotonic() + plazo
    ultimo = None
    while time.monotonic() < fin:
        try:
            with psycopg.connect(dsn, connect_timeout=2) as c:
                return c.execute("SHOW server_version").fetchone()[0]
        except psycopg.OperationalError as e:
            ultimo = e
            time.sleep(0.5)
    raise TimeoutError(f"Postgres no aceptó conexiones en {plazo:.0f} s: {ultimo}")


def estados(monitor, app):
    """[(pid, state)] de las conexiones cuyo application_name es `app`."""
    return monitor.execute(
        "SELECT pid, state FROM pg_stat_activity "
        "WHERE backend_type = 'client backend' AND application_name = %s ORDER BY pid",
        (app,)).fetchall()


def corre_pg():
    import psycopg
    from psycopg_pool import ConnectionPool

    nombre = f"fdd-pg-{secrets.token_hex(4)}"
    puerto = puerto_libre()
    dsn = f"host=127.0.0.1 port={puerto} user=postgres password=prueba dbname=postgres"
    creado = False
    try:
        r = docker("run", "-d", "--name", nombre, "-e", "POSTGRES_PASSWORD=prueba",
                   "-p", f"127.0.0.1:{puerto}:5432", "postgres:17-alpine", plazo=120)
        if r.returncode != 0:
            raise RuntimeError(f"docker run falló: {r.stderr.strip()[:300]}")
        creado = True
        version = espera_postgres(dsn)
        print(f"contenedor {nombre} (postgres:17-alpine), servidor PostgreSQL {version}, "
              f"puerto {puerto}\n")

        with psycopg.connect(dsn, autocommit=True,
                             application_name="fdd-monitor") as monitor:
            # ---------- A ----------
            print("== A. Un pool de 10 conexiones = 10 backends ==")
            with ConnectionPool(dsn, min_size=10, max_size=10, open=True,
                                kwargs={"application_name": "fdd-pool",
                                        "autocommit": True}) as pool:
                pool.wait(timeout=30)                  # espera a que abra las 10
                filas = estados(monitor, "fdd-pool")
                pids = {p for p, _ in filas}
                print(f"conexiones del pool vistas en pg_stat_activity: {len(filas)}")
                print(f"PID distintos: {len(pids)}  ->  {sorted(pids)}")
                ps = docker("exec", nombre, "ps", "-o", "pid,args").stdout
                en_contenedor = {int(l.split()[0]) for l in ps.splitlines()[1:]
                                 if l.split() and l.split()[0].isdigit()}
                print(f"de esos PID, procesos que existen DENTRO del contenedor: "
                      f"{len(pids & en_contenedor)} de {len(pids)}")
                muestra = [l.strip() for l in ps.splitlines() if "postgres: postgres" in l][:3]
                print("tres procesos backend según `ps` dentro del contenedor (el primero puede ser la conexión de monitoreo):")
                for l in muestra:
                    print("   ", l[:90])

                # ---------- B ----------
                print("\n== B. Conexión ociosa (idle) vs consulta activa (active) ==")

                def duerme2(_):
                    with pool.connection() as c:
                        c.execute("SELECT pg_sleep(2)")

                with cf.ThreadPoolExecutor(3) as ex:
                    futuros = [ex.submit(duerme2, i) for i in range(3)]
                    time.sleep(0.7)                    # a mitad de las consultas
                    en_vuelo = estados(monitor, "fdd-pool")
                    for f in futuros:
                        f.result()
                activas = sum(1 for _, s in en_vuelo if s == "active")
                ociosas = sum(1 for _, s in en_vuelo if s == "idle")
                print(f"con 3 `SELECT pg_sleep(2)` en curso: {len(en_vuelo)} conexiones "
                      f"abiertas, {activas} active, {ociosas} idle")
                despues = estados(monitor, "fdd-pool")
                print(f"2 s después, sin consultas: {len(despues)} conexiones abiertas, "
                      f"{sum(1 for _, s in despues if s == 'active')} active")

            # el pool se cerró: sus backends desaparecen
            time.sleep(0.5)
            print(f"tras cerrar el pool: {len(estados(monitor, 'fdd-pool'))} conexiones "
                  f"del pool en la base")

            # ---------- C ----------
            print("\n== C. El pool es un tope: pool de 2, 6 tareas de 0.5 s ==")
            with ConnectionPool(dsn, min_size=2, max_size=2, open=True,
                                kwargs={"application_name": "fdd-pool2",
                                        "autocommit": True}) as pool2:
                pool2.wait(timeout=30)

                def tarea(_):
                    t = time.monotonic()
                    with pool2.connection() as c:
                        c.execute("SELECT pg_sleep(0.5)")
                    return time.monotonic() - t

                t0 = time.monotonic()
                with cf.ThreadPoolExecutor(6) as ex:
                    espera = sorted(ex.map(tarea, range(6)))
                total = time.monotonic() - t0
                print(f"tamaño del pool = 2, tareas = 6, cada una pg_sleep(0.5)")
                print(f"tiempo total: {total:.2f} s   (cuenta: ceil(6/2) x 0.5 = 1.50 s)")
                print("duración de cada tarea (incluye esperar conexión): "
                      + ", ".join(f"{t:.2f}" for t in espera))
                print(f"backends del pool2 en la base: {len(estados(monitor, 'fdd-pool2'))} "
                      "(nunca más de 2)")

            # ---------- D ----------
            print("\n== D. Los topes de la base ==")
            maxc = int(monitor.execute("SHOW max_connections").fetchone()[0])
            res = int(monitor.execute(
                "SHOW superuser_reserved_connections").fetchone()[0])
            print(f"max_connections = {maxc}")
            print(f"superuser_reserved_connections = {res}")
            print(f"plazas para clientes normales = {maxc} - {res} = {maxc - res}")
            potencial = 3 * 4 * 10
            print(f"cuenta de la celda 11.2: R x N x k = 3 x 4 x 10 = {potencial}"
                  f"  ->  {'cabe' if potencial <= maxc - res else 'NO cabe'}")
    finally:
        if creado:
            docker("rm", "-f", nombre, plazo=60)
            print(f"\ncontenedor {nombre} borrado")


try:
    ok = docker("info", "--format", "{{.ServerVersion}}", plazo=15)
    if ok.returncode != 0:
        raise RuntimeError(ok.stderr.strip()[:200] or "docker info falló")
    corre_pg()
except Exception as e:                  # Docker ausente, caído o arranque fallido
    print(f"No se pudo correr la celda con Docker real: {type(e).__name__}: {e}")
    print("\n--- captura de salida previa (no es una ejecución) ---")
    print(CAPTURA_PREVIA)

# %% [markdown]
# ### Salida esperada de la celda 11.4
#
# Los PID, el nombre del contenedor y los tiempos cambian en cada corrida; lo
# que debe repetirse es la **forma**:
#
# - **Encabezado**: nombre `fdd-pg-…` y la versión de PostgreSQL (17.x).
# - **A.** `10` conexiones, `10` PID distintos, y «10 de 10» PID que existen
#   dentro del contenedor. Cada conexión del pool es un proceso `postgres:`
#   aparte, en la base.
# - **B.** Con las 3 consultas en curso: `10` conexiones abiertas, **3
#   `active` y 7 `idle`**. Sin consultas, 0 activas. Tras cerrar el pool, 0
#   conexiones: cerrar el pool cierra los backends.
# - **C.** Total **cerca de 1.5 s** (entre 1.4 y 2 s); las duraciones
#   individuales salen en tres grupos (≈0.5, ≈1.0, ≈1.5 s): las que tuvieron
#   que esperar una conexión. Nunca más de 2 backends.
# - **D.** `max_connections = 100`, `superuser_reserved_connections = 3`,
#   97 plazas; la cuenta `3 × 4 × 10 = 120` **no cabe**.
# - Última línea: «contenedor … borrado». Comprueba en una terminal que no
#   quedó nada: `docker ps -a | grep fdd-pg` no debe imprimir nada.
#
# **Lectura.** Una conexión **no** es gratis: es un proceso en la base, aunque
# esté ociosa. Un pool reparte pocas conexiones entre muchas tareas, y por eso
# sirve de tope (las tareas esperan), pero cada **worker** de cada **réplica**
# tiene el suyo, y la base sólo tiene `max_connections` plazas.
