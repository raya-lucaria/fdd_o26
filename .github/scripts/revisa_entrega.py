#!/usr/bin/env python3
"""Revision automatica de las entregas del curso.

Seis reglas, todas bloqueantes. El mensaje de cada fallo dice QUE esta mal,
POR QUE es un error y DONDE INVESTIGAR, nunca el como: el punto es que el
estudiante entienda el error y se corrija solo, no que copie un comando.

1. La branch: un pull request no puede salir de la rama default del fork.
2. Ubicacion: solo se puede escribir dentro de la carpeta propia.
3. Nombre de la carpeta: tiene que coincidir con el login exacto, mayusculas
   incluidas.
4. Basura: nada de archivos que nunca se suben (.env, __pycache__, llaves).
5. El nombre de la branch tiene que ser tarea-NN-nombre.
6. Una entrega, una carpeta: un pull request no puede tocar mas de una
   carpeta de entrega, ni una que no corresponda a su branch.

Las reglas 1 y 5 tienen cada una su propio periodo de gracia, con su propia
fecha de corte (BRANCH_ESTRICTA_DESDE y BRANCH_NOMBRE_ESTRICTO_DESDE): antes
de la fecha avisan, no rechazan. Las reglas 2, 3, 4 y 6 son estrictas desde
siempre.

Las cuentas listadas en MANTENEDORES quedan exentas: son quienes publican
material en la zona roja.

Corre bajo `pull_request_target`, asi que este script y su workflow salen
siempre de la rama base: un fork no puede reemplazarlos. A cambio, aqui NO se
lee ni se ejecuta nada del arbol de trabajo del pull request; todo lo que se
juzga viene de la API.
"""
import datetime
import json
import os
import re
import secrets
import subprocess
import sys

# Basura: si el nombre aparece como archivo o como carpeta de la ruta.
BASURA = (
    ".DS_Store", "Thumbs.db", "desktop.ini", "id_rsa",
    "__pycache__", "node_modules", ".ipynb_checkpoints", ".venv",
)
# Y todo lo que empieza con .env — .env.local con una llave dentro, en un
# repositorio publico, es mas probable que un .env a secas.
BASURA_PREFIJOS = (".env",)
BASURA_SUFIJOS = (".pyc", ".pyo", ".pem")

# Las branches de entrega tienen la forma tarea-NN-nombre: en minusculas y
# con guiones, nunca guiones bajos. Algunas tareas ya le asignaron un nombre
# exacto (el catalogo, abajo); las que todavia no existen no tienen uno, asi
# que aqui solo se comprueba la forma y, si el mapa esta disponible, que la
# carpeta corresponda.
PATRON_RAMA = re.compile(r"^tarea-\d{2}-[a-z0-9-]+$")


def _mapa_tareas():
    """branch -> subcarpeta esperada, tal como lo declara el workflow.

    El valor se normaliza a su primer segmento: subcarpeta() nunca devuelve
    mas de uno, asi que un valor como "09_sql/ejercicios" en el mapa haria
    que la comparacion no cerrara nunca y la tarea completa saliera
    rechazada.
    """
    mapa = {}
    for par in os.environ.get("TAREAS", "").split(","):
        par = par.strip()
        if "=" in par:
            rama, carpeta = par.split("=", 1)
            carpeta = carpeta.strip().strip("/")
            mapa[rama.strip()] = carpeta.split("/")[0]
    return mapa


RAIZ_ESTUDIANTES = "estudiantes/"

# A donde se manda a investigar. Los mensajes dicen QUE esta mal, POR QUE es
# un error y DONDE INVESTIGAR; nunca el como (ni comandos ni recetas): el
# como es parte de lo que el curso ensena, y darlo resuelto lo salta.
FLUJO = "https://rayalucaria.org/fdd_o26/git-y-github/github/el-flujo-del-curso/"
RITUAL = "https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/"
TOPE_LISTA = 20


def limpio(texto):
    """Neutraliza los caracteres de control de algo que viene del pull request.

    Git acepta un salto de linea dentro de un nombre de archivo, y una linea
    que empieza con `::` es un comando para Actions: un archivo llamado
    `x\n::error title=Aprobado::entrega aceptada` fingia una anotacion en el
    log. Toda ruta, nombre o branch que venga del alumno pasa por aqui antes
    de imprimirse; el `::stop-commands::` de main() es la segunda barrera.
    """
    return re.sub(r"[\x00-\x1f\x7f]", "?", str(texto))


def _gh(*args):
    return subprocess.run(
        ["gh", "api", *args], capture_output=True, text=True, check=True
    ).stdout


def archivos_del_pr(pr):
    """Ruta actual, ruta previa y estado de cada archivo del pull request.

    `previous_filename` es obligatorio: en un rename la API sólo pone la ruta
    destino en `filename`, asi que sin la previa un `git mv` saca archivos de la
    zona roja sin que nadie lo note.
    """
    repo = os.environ["GITHUB_REPOSITORY"]
    salida = _gh(
        "--paginate", f"repos/{repo}/pulls/{pr}/files?per_page=100",
        "--jq", ".[] | {path: .filename, previa: (.previous_filename // \"\"), "
                "status: .status}",
    )
    return [json.loads(l) for l in salida.splitlines() if l.strip()]


def total_declarado(pr):
    repo = os.environ["GITHUB_REPOSITORY"]
    return int(_gh(f"repos/{repo}/pulls/{pr}", "--jq", ".changed_files").strip())


def fecha_del_pr(pr):
    """El dia en que se abrio el pull request (UTC).

    Los periodos de gracia se miden contra esta fecha y no contra hoy: si no,
    un pull request abierto dentro de la gracia se vuelve rojo en cuanto el
    alumno corrige y hace push a la misma branch, que es justo lo que se le
    pide hacer.
    """
    repo = os.environ["GITHUB_REPOSITORY"]
    creado = _gh(f"repos/{repo}/pulls/{pr}", "--jq", ".created_at").strip()
    return datetime.date.fromisoformat(creado[:10])


def es_basura(ruta):
    partes = ruta.split("/")
    nombre = partes[-1]
    return (
        nombre.endswith(BASURA_SUFIJOS)
        or nombre.startswith(BASURA_PREFIJOS)
        or any(p in BASURA for p in partes)
    )


def subcarpeta(ruta, mio):
    """La carpeta de la entrega dentro de la del estudiante.

    `estudiantes/ana/docker/certificaciones.md` -> `docker`.
    Un archivo suelto en `estudiantes/ana/` devuelve "" y no cuenta: el
    .gitkeep de la primera entrega no puede invalidar la segunda.
    """
    resto = ruta[len(mio):]
    partes = resto.split("/")
    return partes[0] if len(partes) > 1 else ""


def _paso_la_fecha(variable_de_entorno, abierto):
    """True si el pull request se abrio en o despues de la fecha de corte.

    Sin la variable, estricto desde siempre: borrar la fecha endurece la
    regla, nunca la apaga. Las reglas 1 y 5 comparten este mecanismo pero
    cada una con su propia variable, para poder moverlas por separado.
    """
    desde = os.environ.get(variable_de_entorno, "").strip()
    if not desde:
        return True
    return abierto >= datetime.date.fromisoformat(desde)


def _estricto_en_branch(abierto):
    """La regla 1 (no entregar desde main) rechaza a partir de su fecha."""
    return _paso_la_fecha("BRANCH_ESTRICTA_DESDE", abierto)


def _estricto_en_nombre(abierto):
    """La regla 5 (nombre de la branch) rechaza a partir de su propia fecha.

    Es una variable distinta de BRANCH_ESTRICTA_DESDE a proposito: esa
    gobierna la regla 1, que ya estaba vigente y que nadie pidio relajar.
    """
    return _paso_la_fecha("BRANCH_NOMBRE_ESTRICTO_DESDE", abierto)


def _lista(rutas):
    filas = "".join(f"    - {limpio(r)}\n" for r in sorted(rutas)[:TOPE_LISTA])
    if len(rutas) > TOPE_LISTA:
        filas += f"    ... y {len(rutas) - TOPE_LISTA} mas.\n"
    return filas


def _revisa():
    autor = os.environ["AUTOR"]
    rama = os.environ["RAMA"]
    # `rama_` es la que se imprime: `rama` se usa tal cual para comparar.
    rama_ = limpio(rama)
    rama_default = os.environ.get("RAMA_DEFAULT") or "main"
    mantenedores = {
        m.strip().lower()
        for m in os.environ.get("MANTENEDORES", "").split(",")
        if m.strip()
    }

    if autor.lower() in mantenedores:
        print(f"{autor} es mantenedor del curso: sin restricciones. OK.")
        return 0

    pr = os.environ["PR"]
    archivos = archivos_del_pr(pr)
    mio = f"{RAIZ_ESTUDIANTES}{autor}/"
    mapa = _mapa_tareas()
    fallos, avisos = [], []
    abierto = fecha_del_pr(pr)
    branch_nueva = False

    # 0. Un pull request sin archivos no es una entrega.
    if not archivos:
        print(
            "Este pull request no cambia ningun archivo, asi que no hay nada\n"
            "que entregar.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿que tiene que traer un pull request para contar como entrega?"
        )
        return 1

    # La API corta en 3000 archivos. Si lo que bajamos no coincide con lo que
    # el pull request declara, no podemos afirmar que lo revisamos completo.
    declarado = total_declarado(pr)
    if declarado != len(archivos):
        print(
            f"No pude revisar la entrega completa: el pull request declara\n"
            f"{declarado} archivos y la API me devolvio {len(archivos)}.\n"
            "  Casi siempre significa que el pull request es enorme porque\n"
            "  arrastra cambios que no son tuyos.\n"
            f"  Donde investigar: {RITUAL}\n"
            "  ¿de que commit nace tu branch, y esta al dia con el curso?"
        )
        return 1

    # 1. La branch. Va primero porque invalida la entrega entera.
    #
    # Durante las primeras entregas esto solo avisa: el grupo ya tenia pull
    # requests abiertos desde main cuando la regla entro. A partir de la fecha
    # de corte rechaza. Para endurecerlo antes o despues, mueve
    # BRANCH_ESTRICTA_DESDE en entregas.yml; para hacerlo estricto ya, borra
    # esa variable.
    if rama == rama_default:
        texto = (
            f"BRANCH: este pull request sale de '{rama_}', la branch default de\n"
            "  tu fork. Cada tarea se entrega desde su propia branch, porque\n"
            "  desde main solo puedes tener un pull request abierto a la vez.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿desde que branch se entrega cada tarea, y de donde nace?"
        )
        if _estricto_en_branch(abierto):
            fallos.append(texto)
            branch_nueva = True
        else:
            avisos.append(
                texto + "\n"
                f"  POR AHORA ESTO SOLO ES UN AVISO. A partir del "
                f"{os.environ.get('BRANCH_ESTRICTA_DESDE')} rechaza la entrega."
            )

    # 5. El nombre de la branch. Se salta si el pull request sale de la rama
    # default, porque la regla 1 ya lo reporto y dos mensajes confunden.
    #
    # Igual que la regla 1, esto solo avisa antes de su fecha de corte: a las
    # tareas de la unidad 7 nunca se les pidio un nombre de branch, asi que
    # quien entrego con uno inventado no hizo nada mal. La fecha vive en
    # BRANCH_NOMBRE_ESTRICTO_DESDE, su propia variable, distinta de
    # BRANCH_ESTRICTA_DESDE: mover una no mueve la otra.
    if rama != rama_default and not PATRON_RAMA.match(rama):
        asignados = ", ".join(sorted(mapa)) or "tarea-NN-nombre"
        texto = (
            f"BRANCH: '{rama_}' no es el nombre de una entrega.\n"
            "  Una branch de entrega se llama tarea-NN-nombre, en minusculas y\n"
            "  con guiones, nunca guiones bajos.\n"
            "  Si tu tarea ya trae nombre asignado, usalo tal cual. Los\n"
            f"  asignados ahora mismo son: {asignados}.\n"
            "  Si la tuya no esta en esa lista, la forma es tarea-NN-<algo-corto>\n"
            "  con el numero de tu unidad.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿como se llama la branch de tu tarea, y que revisa ese nombre?"
        )
        if _estricto_en_nombre(abierto):
            fallos.append(texto)
            branch_nueva = True
        else:
            avisos.append(
                texto + "\n"
                f"  POR AHORA ESTO SOLO ES UN AVISO. A partir del "
                f"{os.environ.get('BRANCH_NOMBRE_ESTRICTO_DESDE')} rechaza la entrega."
            )

    fuera, mal_nombre, basura, mias = [], [], [], []
    for a in archivos:
        estado = a["status"]
        # En un rename hay que juzgar las DOS rutas: de donde salio y a donde
        # llego. Si sólo se mira el destino, un git mv de la zona roja a la
        # propia carpeta pasa en verde y el merge borra el archivo del curso.
        rutas = [a["path"]] + ([a["previa"]] if a.get("previa") else [])

        for ruta in rutas:
            # 2. Ubicacion y 3. nombre de la carpeta.
            if not ruta.startswith(RAIZ_ESTUDIANTES):
                fuera.append(ruta)
            elif not ruta.startswith(mio):
                partes = ruta.split("/")
                duenio = partes[1] if len(partes) > 2 else ""
                if duenio and duenio.lower() == autor.lower():
                    mal_nombre.append((ruta, duenio))
                else:
                    fuera.append(ruta)
            elif estado != "removed":
                # Un borrado puro no cuenta para la regla 6: borrar es lo
                # correcto, igual que en la regla de basura. La ruta previa de
                # un rename si cuenta, porque su estado es "renamed", no
                # "removed", asi que sigue entrando aqui sin excepcion.
                mias.append(ruta)

        # 4. Basura. Los borrados no cuentan: borrar un .DS_Store es lo correcto.
        if estado != "removed" and es_basura(a["path"]):
            basura.append(a["path"])

    if fuera:
        fallos.append(
            "UBICACION: tocaste archivos fuera de tu carpeta.\n"
            f"  Solo puedes escribir dentro de {mio}\n"
            + _lista(fuera)
            + "  Lo que esta fuera de tu carpeta es la zona roja: al mergear, tu\n"
            "  pull request cambiaria el material del curso para todo el grupo.\n"
            "  Mover un archivo del curso a tu carpeta tambien cuenta, porque lo\n"
            "  borra de donde estaba.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿que parte del repositorio es tuya y cual es la zona roja?"
        )

    if mal_nombre:
        malo = limpio(mal_nombre[0][1])
        fallos.append(
            "NOMBRE: tu carpeta no se llama exactamente como tu login.\n"
            f"  Esperaba: estudiantes/{autor}/\n"
            f"  Encontre: estudiantes/{malo}/\n"
            "  Las mayusculas cuentan: para git son dos carpetas distintas, y la\n"
            "  revision busca la tuya por tu login exacto. Ojo: macOS y Windows\n"
            "  no distinguen mayusculas en disco, asi que tu maquina puede\n"
            "  mostrarte bien un nombre que en git esta mal.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿como se llama exactamente tu carpeta, letra por letra?"
        )

    if basura:
        fallos.append(
            "BASURA: agregaste archivos que nunca se suben.\n"
            + _lista(basura)
            + "  Son archivos de tu maquina, no de tu trabajo. Si alguno es una\n"
            "  credencial, ya es publica: este repositorio es publico y lo que\n"
            "  entra queda en la historia aunque despues se borre.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿que archivos nunca viajan al repositorio, y por que?"
        )

    # 6. Una entrega, una carpeta. Cierra tres cosas de un golpe: dos entregas
    # metidas en el mismo pull request, el conflicto add/add cuando las dos
    # agregan el mismo archivo, y el alumno que llena el certificaciones.md de
    # la unidad pasada.
    carpetas = {subcarpeta(r, mio) for r in mias}
    carpetas.discard("")
    esperada = mapa.get(rama)
    if esperada and carpetas and carpetas != {esperada}:
        fallos.append(
            f"CARPETA: la branch '{rama_}' entrega en {mio}{esperada}/\n"
            f"  y este pull request toca: {', '.join(sorted(map(limpio, carpetas)))}\n"
            "  Cada entrega vive en una sola carpeta y en su propio pull request:\n"
            "  dos entregas juntas se pisan al mergear. Mover un archivo de una\n"
            "  carpeta a otra cuenta como tocar las dos.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿cuantas carpetas y cuantas tareas caben en un pull request?"
        )
    elif len(carpetas) > 1:
        fallos.append(
            "CARPETA: este pull request toca mas de una carpeta de entrega.\n"
            f"  Encontre: {', '.join(sorted(map(limpio, carpetas)))}\n"
            "  Cada entrega vive en una sola carpeta y en su propio pull request:\n"
            "  dos entregas juntas se pisan al mergear. Mover un archivo de una\n"
            "  carpeta a otra cuenta como tocar las dos.\n"
            f"  Donde investigar: {FLUJO}\n"
            "  ¿cuantas carpetas y cuantas tareas caben en un pull request?"
        )

    for a in avisos:
        print(f"AVISO\n- {a}\n")

    if fallos:
        print("La entrega no paso la revision.\n")
        for f in fallos:
            print(f"- {f}\n")
        if branch_nueva:
            # La unica correccion que no cabe en la misma branch: su nombre.
            print(
                "El problema es la branch misma, y la branch de un pull request\n"
                "no cambia con mas cambios: esta entrega necesita una branch nueva\n"
                "con su propio pull request, y este ya no se puede corregir.\n"
                f"  Donde investigar: {FLUJO}"
            )
        else:
            print(
                "Sube los cambios a ESTA MISMA branch: el pull request se actualiza\n"
                "solo y la revision se vuelve a correr. No abras otro."
            )
        return 1

    print(f"Entrega correcta: {len(archivos)} archivo(s), todos dentro de {mio}")
    return 0


def main():
    """La revision, entre `::stop-commands::` y su token de cierre.

    Mientras esta activo, Actions no interpreta ninguna linea `::comando::`:
    si algo del pull request se colara sin pasar por limpio(), no podria
    fingir una anotacion. El token es aleatorio para que el pull request no
    pueda adivinarlo y reactivar los comandos.
    """
    token = secrets.token_hex(16)
    print(f"::stop-commands::{token}")
    try:
        return _revisa()
    finally:
        print(f"::{token}::")


if __name__ == "__main__":
    sys.exit(main())
