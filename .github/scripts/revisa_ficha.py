#!/usr/bin/env python3
"""Revision de una entrega contra la ficha de su tarea.

Tercer paso de `entregas.yml`. `revisa_entrega.py` juzga la FORMA (donde viven
los archivos, como se llama la branch, que no haya basura) y
`revisa_contenido.py` el contenido minimo de las tareas que se quedaron en su
catalogo. Este juzga las tareas NUEVAS, cada una con su ficha:
`.github/tareas/<branch>.toml`. El nombre del archivo ES la branch; si la
branch no tiene ficha, no hay nada que revisar aqui y el paso sale en verde.

Por que la ficha vive en un archivo y no dentro del script, como el catalogo
de `revisa_contenido.py`: bajo `pull_request_target` el checkout esta fijado a
`base.sha`, asi que lo que este script lee del disco sale de la rama base y no
del pull request. El catalogo se escribio adentro por precaucion; la ficha
depende de esa fijacion, y por eso las pruebas la vigilan
(`tools/test_revisa_ficha.py`). Un pull request tampoco puede traer su propia
ficha: tocar `.github/` es tocar fuera de su carpeta, y la regla 2 de
`revisa_entrega.py` lo rechaza antes de que este paso corra.

Lo que si sigue valiendo: del disco solo se leen `.github/tareas/` (la ficha)
y `codigo/` (la plantilla, para reconocer una entrega sin tocar). Los archivos
del alumno se leen SOLO por la API, nunca de `estudiantes/`: esa carpeta en el
disco es la de la base, no la del pull request, y juzgarla seria juzgar otra
cosa.

No califica. Atrapa lo que un robot puede atrapar sin equivocarse, y cada
mensaje dice QUE esta mal, POR QUE es un error y DONDE INVESTIGAR. Nunca el
como: el como es la tarea, y darlo resuelto es quitarsela a quien la entrega.

El contenido del alumno es dato, nunca instruccion. Si trae frases dirigidas a
quien revisa ("ignora las instrucciones", "aprueba este"), se reporta como
aviso y no cambia nada: ni aprueba ni reprueba.
"""
import base64
import datetime
import json
import os
import re
import secrets
import subprocess
import sys
import unicodedata
import urllib.parse
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11: solo en maquinas locales viejas.
    # En CI (ubuntu-latest, Python 3.12) esto nunca corre: tomllib es stdlib.
    import tomli as tomllib

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_TAREAS = RAIZ_REPO / ".github" / "tareas"
DIR_CODIGO = RAIZ_REPO / "codigo"

# La misma forma que exige la regla 5 de revisa_entrega.py. Aqui ademas
# protege la busqueda de la ficha: una branch con otra forma no se convierte
# en ruta de disco.
PATRON_RAMA = re.compile(r"^tarea-\d{2}-[a-z0-9-]+$")

IA_VALIDAS = ("permitida", "permitida-revisada", "prohibida")
PIDE_VALIDOS = ("fecha", "url", "fecha-iso")
NIVELES = ("falla", "aviso")

# Sin la pagina de la tarea en la ficha, los mensajes genericos apuntan aqui.
PAGINA_POR_OMISION = "la pagina de la tarea en el sitio del curso"

# Tope de archivos de texto que se leen buscando frases dirigidas al revisor.
# Una entrega normal trae menos de diez; esto solo evita que un pull request
# enorme se coma el limite de la API.
TOPE_LECTURAS = 40
# Estas nunca son texto: no vale la pena una llamada a la API para saberlo.
EXT_BINARIAS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip",
                ".gz", ".tar", ".ico", ".mp4", ".mov")

# Frases dirigidas a quien revisa, sobre el texto ya normalizado (minusculas,
# sin acentos, espacios colapsados). Solo avisan: una cita legitima de la
# salida de un modelo tambien las contiene, y eso lo decide una persona.
INYECCION = (
    r"ignora(r)? (todas )?(las |tus |mis )?(instrucciones|indicaciones)",
    r"olvida (todas )?(las |tus )?instrucciones",
    r"ignore (all )?(the |your )?(previous|prior|above)",
    r"disregard (all )?(the |your )?(previous|prior|above)",
    r"aprueba (este|esta|el pr|el pull request|la entrega)",
    r"approve (this|the pr|the pull request)",
    r"\bas an ai\b",
    r"as a (large )?language model",
    r"como (un )?modelo de lenguaje",
    r"system prompt",
    r"prompt del sistema",
)

# Nombres completos de los meses, en espanol e ingles. Una palabra vale como
# mes si es un prefijo de al menos tres letras de alguno: "sep", "sept" y
# "septiembre" valen; "martes" no, aunque empiece como "marzo".
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}


def mes(palabra):
    """El numero del mes que nombra `palabra`, o None."""
    palabra = palabra.rstrip(".")
    if len(palabra) < 3:
        return None
    for nombre, n in MESES.items():
        if nombre.startswith(palabra):
            return n
    return None


# --------------------------------------------------------------------------
# Disco: solo la ficha y la plantilla
# --------------------------------------------------------------------------

def _leer_del_arbol(ruta):
    """Unica puerta al disco. Solo abre dentro de `.github/tareas/` y `codigo/`.

    Cualquier otra ruta —en particular `estudiantes/`— se rechaza con un
    error, no se ignora: un descuido futuro tiene que explotar en las pruebas,
    no pasar callado a produccion.
    """
    ruta = Path(ruta).resolve()
    if not any(ruta.is_relative_to(d.resolve()) for d in (DIR_TAREAS, DIR_CODIGO)):
        raise PermissionError(
            f"revisa_ficha.py solo lee .github/tareas/ y codigo/, no {ruta}"
        )
    return ruta.read_bytes() if ruta.is_file() else None


def cargar_ficha(rama):
    """La ficha de la branch, o None si no tiene.

    Una branch con otra forma no busca ficha: asi el nombre, que lo elige el
    alumno, nunca se convierte en una ruta arbitraria.
    """
    if not PATRON_RAMA.match(rama or ""):
        return None
    crudo = _leer_del_arbol(DIR_TAREAS / f"{rama}.toml")
    if crudo is None:
        return None
    return tomllib.loads(crudo.decode("utf-8"))


def plantilla(carpeta, ruta_rel):
    """El archivo original de `codigo/<carpeta>/`, en bytes, o None."""
    return _leer_del_arbol(DIR_CODIGO / carpeta / ruta_rel)


# --------------------------------------------------------------------------
# El esquema de la ficha
# --------------------------------------------------------------------------

_LLAVES = {
    "tarea": {"branch", "asignacion", "carpeta", "available", "due",
              "penalizacion_tarde", "ia", "debe_explicar", "pagina"},
    "entregables": {"requeridos", "prohibidos", "identica"},
    "capturas": {"nombre", "extensiones", "minimo_bytes"},
    "secciones": {"archivo", "aguja", "pide", "fecha_futura", "sin_tocar",
                  "falta"},
    "patrones": {"archivo", "debe", "no_debe", "que", "porque", "investiga",
                 "nivel", "seccion"},
    "revision": {"foco", "igual_es_normal", "debe_ser_propio", "senales",
                 "donde_investigar"},
}


def _fecha_str(valor):
    """TOML acepta la fecha con o sin comillas; aqui siempre es texto ISO."""
    if isinstance(valor, datetime.date):
        return valor.isoformat()
    return valor


def _lista_de_textos(valor):
    return isinstance(valor, list) and all(
        isinstance(v, str) and v.strip() for v in valor)


def validar_ficha(ficha, nombre_archivo):
    """Errores de esquema de una ficha. Lista vacia si esta sana.

    Una llave desconocida es un error y no un descuido tolerado: `requerido`
    en lugar de `requeridos` dejaria la tarea sin revisar sin que nadie lo
    notara.
    """
    err = []
    for seccion in ficha:
        if seccion not in _LLAVES:
            err.append(f"seccion desconocida [{seccion}]")

    tarea = ficha.get("tarea")
    if not isinstance(tarea, dict):
        return err + ["falta [tarea]"]
    for k in set(tarea) - _LLAVES["tarea"]:
        err.append(f"[tarea] llave desconocida '{k}'")
    for k in ("branch", "asignacion", "carpeta", "penalizacion_tarde", "ia"):
        if not isinstance(tarea.get(k), str) or not tarea[k].strip():
            err.append(f"[tarea] falta '{k}' o no es texto")
    rama = tarea.get("branch", "")
    esperado = nombre_archivo[:-5] if nombre_archivo.endswith(".toml") else None
    if rama != esperado:
        err.append(f"[tarea] branch '{rama}' no coincide con el archivo "
                   f"'{nombre_archivo}'")
    if isinstance(rama, str) and not PATRON_RAMA.match(rama):
        err.append(f"[tarea] branch '{rama}' no tiene la forma tarea-NN-nombre")
    carpeta = tarea.get("carpeta", "")
    if isinstance(carpeta, str) and (carpeta.startswith("/") or
                                     carpeta.endswith("/") or ".." in carpeta):
        err.append(f"[tarea] carpeta '{carpeta}' debe ser relativa y sin '/' "
                   "al inicio ni al final")
    for k in ("available", "due"):
        try:
            datetime.date.fromisoformat(_fecha_str(tarea.get(k)))
        except (TypeError, ValueError):
            err.append(f"[tarea] '{k}' no es una fecha AAAA-MM-DD")
    if tarea.get("ia") not in IA_VALIDAS:
        err.append(f"[tarea] ia debe ser una de {IA_VALIDAS}")
    if not _lista_de_textos(tarea.get("debe_explicar")) or not tarea["debe_explicar"]:
        err.append("[tarea] debe_explicar tiene que ser una lista no vacia de textos")
    if "pagina" in tarea and not isinstance(tarea["pagina"], str):
        err.append("[tarea] pagina tiene que ser texto")

    ent = ficha.get("entregables")
    if not isinstance(ent, dict):
        err.append("falta [entregables]")
        ent = {}
    for k in set(ent) - _LLAVES["entregables"]:
        err.append(f"[entregables] llave desconocida '{k}'")
    for k in ("requeridos", "prohibidos"):
        if not isinstance(ent.get(k), list) or not all(
                isinstance(v, str) and v.strip() for v in ent.get(k, [])):
            err.append(f"[entregables] '{k}' tiene que ser una lista de textos")
    if ent.get("identica", "falla") not in NIVELES:
        err.append(f"[entregables] identica debe ser uno de {NIVELES}")
    requeridos = set(ent.get("requeridos") or [])

    for i, cap in enumerate(ficha.get("capturas", [])):
        donde = f"[[capturas]] #{i + 1}"
        for k in set(cap) - _LLAVES["capturas"]:
            err.append(f"{donde} llave desconocida '{k}'")
        if not isinstance(cap.get("nombre"), str) or "." in cap.get("nombre", "."):
            err.append(f"{donde} nombre tiene que ser texto sin extension")
        exts = cap.get("extensiones")
        if not _lista_de_textos(exts) or not exts or not all(
                e.startswith(".") for e in exts):
            err.append(f"{donde} extensiones: lista de textos que empiezan con '.'")
        mb = cap.get("minimo_bytes")
        if not isinstance(mb, int) or isinstance(mb, bool) or mb < 0:
            err.append(f"{donde} minimo_bytes tiene que ser un entero >= 0")

    for i, sec in enumerate(ficha.get("secciones", [])):
        donde = f"[[secciones]] #{i + 1}"
        for k in set(sec) - _LLAVES["secciones"]:
            err.append(f"{donde} llave desconocida '{k}'")
        for k in ("archivo", "aguja"):
            if not isinstance(sec.get(k), str) or not sec[k].strip():
                err.append(f"{donde} falta '{k}'")
        if sec.get("archivo") not in requeridos:
            err.append(f"{donde} archivo '{sec.get('archivo')}' no esta en "
                       "[entregables] requeridos: si no se exige, no se revisa")
        pide = sec.get("pide", [])
        if not isinstance(pide, list) or not set(pide) <= set(PIDE_VALIDOS):
            err.append(f"{donde} pide solo admite {PIDE_VALIDOS}")
        for k in ("fecha_futura", "sin_tocar", "falta"):
            if sec.get(k, "falla") not in NIVELES:
                err.append(f"{donde} {k} debe ser uno de {NIVELES}")

    for i, pat in enumerate(ficha.get("patrones", [])):
        donde = f"[[patrones]] #{i + 1}"
        for k in set(pat) - _LLAVES["patrones"]:
            err.append(f"{donde} llave desconocida '{k}'")
        for k in ("archivo", "que", "porque", "investiga"):
            if not isinstance(pat.get(k), str) or not pat[k].strip():
                err.append(f"{donde} falta '{k}'")
        if ("debe" in pat) == ("no_debe" in pat):
            err.append(f"{donde} lleva exactamente uno de 'debe' o 'no_debe'")
        for k in ("debe", "no_debe"):
            if k in pat:
                try:
                    re.compile(pat[k], re.M | re.I)
                except (re.error, TypeError) as e:
                    err.append(f"{donde} '{k}' no es una regex valida: {e}")
        if pat.get("nivel") not in NIVELES:
            err.append(f"{donde} nivel debe ser uno de {NIVELES}")

    rev = ficha.get("revision")
    if not isinstance(rev, dict):
        err.append("falta [revision]")
    else:
        for k in set(rev) - _LLAVES["revision"]:
            err.append(f"[revision] llave desconocida '{k}'")
        for k in _LLAVES["revision"]:
            if not _lista_de_textos(rev.get(k)):
                err.append(f"[revision] '{k}' tiene que ser una lista de textos")
        for k in ("foco", "donde_investigar"):
            if not rev.get(k):
                err.append(f"[revision] '{k}' no puede ir vacio")
    return err


# --------------------------------------------------------------------------
# API: lo unico por donde entra el trabajo del alumno
# --------------------------------------------------------------------------

def _gh(*args):
    return subprocess.run(
        ["gh", "api", *args], capture_output=True, text=True, check=True
    ).stdout


def _pr_json(pr):
    repo = os.environ["GITHUB_REPOSITORY"]
    return json.loads(_gh(f"repos/{repo}/pulls/{pr}"))


def archivos_del_pr(pr):
    repo = os.environ["GITHUB_REPOSITORY"]
    salida = _gh(
        "--paginate", f"repos/{repo}/pulls/{pr}/files?per_page=100",
        "--jq", ".[] | {path: .filename, status: .status}",
    )
    return [json.loads(l) for l in salida.splitlines() if l.strip()]


def contenido(repo_head, sha, ruta):
    """(bytes_o_None, tamaño_o_None) de un archivo del pull request, por la API.

    Los bytes son None cuando la API no los manda (archivos de mas de 1 MB):
    una captura no se lee, solo se pesa. El tamaño es None cuando la API
    fallo: eso es un error de la revision, y no se puede confundir con un
    archivo vacio ni culpar por el al alumno.
    """
    ruta_url = urllib.parse.quote(ruta)
    try:
        d = json.loads(_gh(f"repos/{repo_head}/contents/{ruta_url}?ref={sha}"))
    except (subprocess.CalledProcessError, ValueError):
        return None, None
    if not isinstance(d, dict):
        return None, None  # una carpeta, no un archivo
    tam = d.get("size")
    if d.get("encoding") != "base64" or not d.get("content"):
        return None, tam
    return base64.b64decode(d["content"]), tam


def como_texto(crudo):
    if crudo is None:
        return None
    try:
        return crudo.decode("utf-8")
    except UnicodeDecodeError:
        return None


# --------------------------------------------------------------------------
# Secciones de un Markdown
# --------------------------------------------------------------------------

def cuerpo_de_seccion(texto, aguja):
    """El cuerpo de la seccion `##` cuyo titulo contiene `aguja`, o None.

    Por subcadena y no por titulo exacto, igual que `revisa_contenido.py`: la
    plantilla usa acentos y un separador facil de teclear distinto, y
    rechazar a alguien por un signo de puntuacion seria ridiculo.
    """
    bloques = re.split(r"^##\s+", texto, flags=re.M)[1:]
    for b in bloques:
        titulo = b.split("\n", 1)[0]
        if aguja.lower() in titulo.lower():
            return b.split("\n", 1)[1] if "\n" in b else ""
    return None


def _lineas_utiles(cuerpo):
    return [
        " ".join(l.split()) for l in cuerpo.splitlines()
        if l.strip() and not l.strip().startswith(("![", "<!--"))
    ]


def vacia(cuerpo):
    """La seccion no trae mas que rotulos: la regla del catalogo viejo.

    Solo lineas que terminan en dos puntos, que empiezan con "Se llena" o
    con "#", o nada. Esto siempre falla: ya fallaba antes de las fichas.
    """
    return all(l.endswith(":") or l.startswith(("Se llena", "#"))
               for l in _lineas_utiles(cuerpo))


def sin_tocar(cuerpo, cuerpo_plantilla=None):
    """La seccion no trae nada que no estuviera ya en la plantilla.

    Mas amplia que `vacia`: varias secciones de la plantilla traen
    instrucciones en prosa, y `vacia` sola las da por llenas. Por eso su
    nivel lo decide la ficha (`sin_tocar`): en las tareas migradas solo
    avisa, para no volverlas mas estrictas que el catalogo.
    """
    propias = set(_lineas_utiles(cuerpo_plantilla)) if cuerpo_plantilla else set()
    for l in _lineas_utiles(cuerpo):
        if l in propias or l.endswith(":") or l.startswith(("Se llena", "#")):
            continue
        return False
    return True


# Los formatos que se reconocen son una especificacion, no una pista: son los
# que el mensaje de "falta la fecha" enumera como validos.
#
#   2026-09-22  2026/09/22                     (anio primero)
#   22/09/2026  22-09-2026  22.09.2026  22/9/26 (dia primero, como en Mexico)
#   22 de septiembre de 2026  22 sep 2026  22-sep-2026  22 de sept. 2026
#   Sep 22, 2026  septiembre 22, 2026  September 22 2026
#
# Los de palabra exigen un mes de verdad. El `\d de \w+` del catalogo viejo
# casaba con el texto alternativo de la imagen de la plantilla («capitulos 1
# y 2 de Intermediate Docker») y daba por fechada una seccion sin fecha.
RE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
RE_AMD = re.compile(r"\b(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\b")
RE_DMA = re.compile(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](\d{4}|\d{2})\b")
RE_D_MES = re.compile(
    r"\b(\d{1,2})(?:\s+de\s+|\s+|-)([a-z]{3,}\.?)"
    r"(?:(?:\s+de\s+|\s+del\s+|\s+|-|,\s*)(\d{4})\b)?")
RE_MES_D = re.compile(r"\b([a-z]{3,}\.?)\s+(\d{1,2})\b(?:,?\s+(\d{4})\b)?")


def _sin_imagenes(cuerpo):
    """El cuerpo sin las lineas de imagen: su texto alternativo no es del alumno."""
    return "\n".join(l for l in cuerpo.splitlines()
                     if not l.strip().startswith("!["))


def _candidatas(cuerpo, anio_por_omision):
    """(anio, mes, dia) de cada cosa con forma de fecha, valida o no."""
    cuerpo = _sin_imagenes(cuerpo)
    plano = _normaliza(cuerpo)
    halladas = []
    for a, m, d in RE_AMD.findall(cuerpo):
        halladas.append((int(a), int(m), int(d)))
    # Sin las de anio primero: "2026-09-22" no debe leerse ademas como
    # "26-09-22" dia primero.
    resto = RE_AMD.sub(" ", cuerpo)
    for d, m, a in RE_DMA.findall(resto):
        halladas.append((int(a) + (2000 if len(a) == 2 else 0), int(m), int(d)))
    for d, palabra, a in RE_D_MES.findall(plano):
        if mes(palabra):
            halladas.append((int(a) if a else anio_por_omision, mes(palabra), int(d)))
    for palabra, d, a in RE_MES_D.findall(plano):
        if mes(palabra):
            halladas.append((int(a) if a else anio_por_omision, mes(palabra), int(d)))
    return halladas


def tiene_fecha(cuerpo):
    """Hay algo con forma de fecha. Como el catalogo viejo, no exige que la
    fecha exista en el calendario: 09/23/2026 cuenta aunque sea al reves."""
    return bool(_candidatas(cuerpo, 2000))


def tiene_fecha_iso(cuerpo):
    """Una fecha AAAA-MM-DD que exista: 2026-13-45 tiene la forma y no es fecha."""
    for m in RE_ISO.finditer(_sin_imagenes(cuerpo)):
        try:
            datetime.date(*map(int, m.groups()))
            return True
        except ValueError:
            continue
    return False


def tiene_url(cuerpo):
    return bool(re.search(r"https?://\S{10,}", _sin_imagenes(cuerpo)))


def fechas(cuerpo, anio_por_omision):
    """Las fechas que existen en el calendario. Las invalidas se omiten."""
    salida = []
    for a, m, d in _candidatas(cuerpo, anio_por_omision):
        try:
            salida.append(datetime.date(a, m, d))
        except ValueError:
            pass
    return salida


def _normaliza(texto):
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_acentos.lower().split())


def frases_al_revisor(texto):
    """Las frases de INYECCION que aparecen en el texto, tal como casaron."""
    plano = _normaliza(texto)
    return [m.group(0) for p in INYECCION for m in re.finditer(p, plano)]


# --------------------------------------------------------------------------
# La revision: pura, sin red ni disco, para poder probarla con falsos
# --------------------------------------------------------------------------

def limpio(texto):
    """Neutraliza los caracteres de control de algo que viene del pull request.

    Git acepta un salto de linea dentro de un nombre de archivo. Una captura
    llamada `x\n::error title=Aprobado::entrega aceptada\n.png` imprimiria una
    linea que Actions interpreta como comando: una anotacion falsa, un
    `::add-mask::`. Todo lo que viene del alumno (rutas, nombres, texto) pasa
    por aqui antes de imprimirse. `::stop-commands::` en main() es la segunda
    barrera, no la primera.
    """
    return re.sub(r"[\x00-\x1f\x7f]", "?", str(texto))


def _msg(que, porque, investiga):
    return (f"QUE: {que}\n"
            f"  POR QUE: {porque}\n"
            f"  DONDE INVESTIGAR: {investiga}")


def _no_pude_leer(base, ruta):
    """La API fallo: el problema es de la revision, no de la entrega."""
    return _msg(
        f"no pude leer {limpio(base)}/{limpio(ruta)} por la API (error de la "
        "revision, no de tu entrega).",
        "sin leerlo no se puede afirmar nada de el, ni para bien ni para mal, "
        "asi que la revision no se da por buena.",
        "nada que investigar de tu lado: la revision se vuelve a correr en tu "
        "proximo push; si se repite, avisale al profesor.")


def revisar(ficha, rel, leer, leer_plantilla, hoy, base):
    """(fallos, avisos) de una entrega contra su ficha.

    `rel`: rutas vivas del pull request, relativas a la carpeta de la tarea.
    `leer(ruta_rel)` -> (bytes_o_None, tamaño_o_None), por la API. Tamaño
        None quiere decir que la API fallo, no que el archivo este vacio.
    `leer_plantilla(ruta_rel)` -> bytes_o_None, de `codigo/<carpeta>/`.
    `hoy`: la fecha de la revision (UTC); contra ella se mide la fecha futura.
    """
    tarea = ficha["tarea"]
    pagina = tarea.get("pagina") or PAGINA_POR_OMISION
    carpeta = tarea["carpeta"]
    ent = ficha["entregables"]
    base = limpio(base)
    fallos, avisos = [], []

    def agrega(nivel, mensaje):
        (fallos if nivel == "falla" else avisos).append(mensaje)

    for req in ent["requeridos"]:
        if req not in rel:
            fallos.append(_msg(
                f"falta {base}/{req} en este pull request.",
                "es uno de los archivos que la tarea pide; sin el, esa parte "
                "de la entrega no existe.",
                f"{pagina}: ¿que archivos enumera la tarea, y en que carpeta "
                "viven?"))
            continue
        crudo = leer(req)[0]
        original = leer_plantilla(req)
        if crudo is not None and original is not None and crudo == original:
            agrega(ent.get("identica", "falla"), _msg(
                f"{base}/{req} es identico, byte a byte, a "
                f"codigo/{carpeta}/{req}.",
                "la plantilla sin tocar no contiene nada tuyo: entregarla asi "
                "es no entregar.",
                f"{pagina}: ¿que parte de ese archivo te toca llenar a ti?"))

    for prohibido in ent["prohibidos"]:
        if prohibido in rel:
            fallos.append(_msg(
                f"{base}/{prohibido} viene en el pull request y la tarea dice "
                "que no se sube.",
                "la tarea lo excluye de forma explicita: al repositorio viaja "
                "solo lo que la tarea enumera.",
                f"{pagina}: ¿que dice la tarea que NO se entrega, y por que?"))

    for cap in ficha.get("capturas", []):
        nombre, exts = cap["nombre"], tuple(cap["extensiones"])
        halladas = sorted(r for r in rel
                          if r.rsplit(".", 1)[0] == nombre
                          and r.lower().endswith(exts))
        if not halladas:
            parecidas = sorted(limpio(r) for r in rel if r.lower().endswith(exts))
            extra = (f" En su lugar encontre: {', '.join(parecidas)}."
                     if parecidas else "")
            fallos.append(_msg(
                f"no encuentro la captura {base}/{nombre} (con extension "
                f"{', '.join(exts)}).{extra}",
                "la captura es la evidencia de la tarea y se busca por su "
                "nombre exacto; con otro nombre, lo que la enlaza sale roto.",
                f"{pagina}: ¿con que nombre pide la tarea la captura?"))
            continue
        tam = leer(halladas[0])[1]
        if tam is None:
            fallos.append(_no_pude_leer(base, halladas[0]))
        elif tam < cap["minimo_bytes"]:
            # Cero tambien: el archivo esta en el pull request, asi que un
            # tamaño 0 es un archivo vacio, no uno que falta.
            fallos.append(_msg(
                f"{base}/{limpio(halladas[0])} pesa {tam} bytes.",
                "una captura de pantalla real pesa decenas de kilobytes; con "
                "tan poco no se ve nada, y la evidencia no existe.",
                "¿se ve tu captura cuando abres el archivo en GitHub?"))

    for sec in ficha.get("secciones", []):
        archivo, aguja = sec["archivo"], sec["aguja"]
        if archivo not in rel:
            continue  # ya lo reporto el requerido
        crudo, tam = leer(archivo)
        if tam is None:
            fallos.append(_no_pude_leer(base, archivo))
            continue
        texto = como_texto(crudo)
        if texto is None:
            fallos.append(_msg(
                f"{base}/{archivo} no es texto.",
                "la tarea lo pide como Markdown, y lo que se subio no lo es.",
                f"{pagina}: ¿que tipo de archivo pide la tarea?"))
            continue
        cuerpo = cuerpo_de_seccion(texto, aguja)
        if cuerpo is None:
            fallos.append(_msg(
                f"no encuentro en {base}/{archivo} la seccion cuyo titulo "
                f"menciona «{aguja}».",
                "la seccion se busca por su titulo; si el titulo cambio o se "
                "borro, no hay donde leer lo que la tarea pide.",
                f"codigo/{carpeta}/{archivo}: ¿que titulos tiene el original "
                "que el tuyo no?"))
            continue
        original = como_texto(leer_plantilla(archivo))
        cuerpo_original = (cuerpo_de_seccion(original, aguja)
                           if original else None)
        mensaje_vacia = _msg(
            f"la seccion «{aguja}» de {base}/{archivo} sigue como en la "
            "plantilla: no trae nada escrito por ti.",
            "esa seccion es la entrega; vacia, no hay nada que revisar.",
            f"{pagina}: ¿que pide la tarea que quede en esa seccion?")
        # Dos niveles de vacio. `vacia` (solo rotulos) ya fallaba con el
        # catalogo viejo y sigue fallando siempre. `sin_tocar` (solo lineas
        # de la plantilla, prosa incluida) es nuevo y su nivel lo pone la
        # ficha.
        if not cuerpo.strip() or vacia(cuerpo):
            fallos.append(mensaje_vacia)
            continue
        if sin_tocar(cuerpo, cuerpo_original):
            agrega(sec.get("sin_tocar", "falla"), mensaje_vacia)
            continue
        pide = sec.get("pide", [])
        nivel_falta = sec.get("falta", "falla")
        if "fecha" in pide and not tiene_fecha(cuerpo):
            agrega(nivel_falta, _msg(
                f"a la seccion «{aguja}» de {base}/{archivo} le falta la fecha "
                "de tu avance. Vale cualquier formato legible: 2026-09-22, "
                "22/09/2026, 22 de septiembre de 2026 o Sep 22, 2026.",
                "la fecha dice hasta donde llegaste y cuando; sin ella no se "
                "puede cotejar con lo que muestra tu evidencia. Si no "
                "terminaste, la fecha es la de hasta donde llegaste.",
                f"{pagina}: ¿que datos pide la tarea en esa seccion?"))
        if "fecha-iso" in pide and not tiene_fecha_iso(cuerpo):
            agrega(nivel_falta, _msg(
                f"a la seccion «{aguja}» de {base}/{archivo} le falta una "
                "fecha en formato AAAA-MM-DD.",
                "la tarea pide ese formato porque es el unico que no se lee "
                "distinto segun el pais.",
                f"{pagina}: ¿en que formato pide la tarea la fecha?"))
        if "url" in pide and not tiene_url(cuerpo):
            agrega(nivel_falta, _msg(
                f"a la seccion «{aguja}» de {base}/{archivo} le falta la URL.",
                "la URL es lo que permite verificar la evidencia en un clic; "
                "sin ella, lo que afirmas no se puede comprobar.",
                f"{pagina}: ¿que URL pide la tarea, y quien la emite?"))
        # Se mide contra el dia de la revision y no contra la apertura del
        # pull request: quien avanza despues de abrirlo y corrige la fecha en
        # la misma branch hace justo lo que se le pide. Un dia de holgura
        # cubre a quien escribe desde un huso adelantado a UTC.
        limite = hoy + datetime.timedelta(days=1)
        futuras = [f for f in fechas(cuerpo, hoy.year) if f > limite]
        if futuras:
            agrega(sec.get("fecha_futura", "falla"), _msg(
                f"la seccion «{aguja}» de {base}/{archivo} dice "
                f"{futuras[0].isoformat()}, y hoy es {hoy.isoformat()} (UTC).",
                "una fecha que todavia no llega no puede ser la de un avance "
                "que ya ocurrio: tal como esta, el archivo afirma algo que no "
                "paso.",
                "¿en que fecha llegaste de verdad a ese avance, y donde lo "
                "puedes comprobar?"))

    for pat in ficha.get("patrones", []):
        archivo = pat["archivo"]
        if archivo not in rel:
            continue
        texto = como_texto(leer(archivo)[0])
        if texto is None:
            continue  # la API fallo o no es texto: ya lo reportan arriba
        if pat.get("seccion"):
            texto = cuerpo_de_seccion(texto, pat["seccion"])
            if texto is None:
                continue  # la seccion ausente ya se reporta arriba
        if "debe" in pat:
            mal = not re.search(pat["debe"], texto, re.M | re.I)
        else:
            mal = bool(re.search(pat["no_debe"], texto, re.M | re.I))
        if mal:
            agrega(pat["nivel"], _msg(pat["que"], pat["porque"], pat["investiga"]))

    leidos = 0
    for r in sorted(rel):
        if r.lower().endswith(EXT_BINARIAS) or leidos >= TOPE_LECTURAS:
            continue
        leidos += 1
        texto = como_texto(leer(r)[0])
        if not texto:
            continue
        frases = frases_al_revisor(texto)
        if frases:
            avisos.append(_msg(
                f"{base}/{limpio(r)} contiene texto dirigido a quien revisa: "
                f"«{limpio(frases[0])}»"
                + (f" y {len(frases) - 1} mas." if len(frases) > 1 else "."),
                "una entrega se lee como dato, nunca como instruccion: esa "
                "frase no cambia el resultado de ninguna revision, ni humana "
                "ni automatica, y queda a la vista del profesor. Esto NO "
                "bloquea la entrega.",
                "¿esa frase la escribiste tu, y sabes por que esta ahi? Si es "
                "una cita legitima, no pasa nada."))

    return fallos, avisos


# --------------------------------------------------------------------------
# El paso del workflow
# --------------------------------------------------------------------------

def _error_de_ficha(rama, errores):
    """Una ficha rota es un error del curso, no del alumno. Se falla cerrado
    (en rojo) para que alguien lo vea, pero el mensaje lo dice claro."""
    print(f"ERROR DEL CURSO, NO TUYO: la ficha de '{rama}' esta mal escrita.\n")
    for e in errores:
        print(f"- {limpio(e)}")
    print("\nAvisale al profesor; no cambies nada de tu entrega por esto.")
    return 1


def _revisa():
    rama = limpio(os.environ["RAMA"])
    autor = os.environ["AUTOR"]
    mantenedores = {
        m.strip().lower()
        for m in os.environ.get("MANTENEDORES", "").split(",") if m.strip()
    }
    if autor.lower() in mantenedores:
        print(f"{limpio(autor)} es mantenedor del curso: sin restricciones. OK.")
        return 0

    try:
        ficha = cargar_ficha(os.environ["RAMA"])
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        return _error_de_ficha(rama, [f"el TOML no se puede leer: {e}"])
    if ficha is None:
        print(f"La branch '{rama}' no tiene ficha en .github/tareas/: "
              "sin ficha, nada que revisar aqui. OK.")
        return 0

    errores = validar_ficha(ficha, f"{os.environ['RAMA']}.toml")
    if errores:
        return _error_de_ficha(rama, errores)

    pr = os.environ["PR"]
    datos = _pr_json(pr)
    repo_head = datos["head"]["repo"]["full_name"]
    sha = datos["head"]["sha"]

    carpeta = ficha["tarea"]["carpeta"]
    base = f"estudiantes/{autor}/{carpeta}"
    vivos = [a["path"] for a in archivos_del_pr(pr) if a["status"] != "removed"]
    rel = {p[len(base) + 1:] for p in vivos if p.startswith(base + "/")}

    if not rel:
        print("La entrega no paso la revision de la ficha.\n")
        print("- " + _msg(
            f"este pull request no toca ningun archivo dentro de {limpio(base)}/.",
            f"la branch '{rama}' entrega en esa carpeta; lo que este en otra "
            "no es esta tarea.",
            f"{ficha['tarea'].get('pagina') or PAGINA_POR_OMISION}: ¿en que "
            "carpeta vive esta entrega?") + "\n")
        print("Sube los cambios a esta misma branch: el pull request se "
              "actualiza solo y la revision se vuelve a correr.")
        return 1

    cache = {}

    def leer(ruta_rel):
        if ruta_rel not in cache:
            cache[ruta_rel] = contenido(repo_head, sha, f"{base}/{ruta_rel}")
        return cache[ruta_rel]

    hoy = datetime.datetime.now(datetime.timezone.utc).date()
    fallos, avisos = revisar(ficha, rel, leer,
                             lambda r: plantilla(carpeta, r), hoy, base)

    for a in avisos:
        print(f"AVISO (no bloquea)\n- {a}\n")

    if fallos:
        print(f"La entrega no paso la revision de la ficha de '{rama}'.\n")
        for f in fallos:
            print(f"- {f}\n")
        print(
            "Esto NO es la calificacion: es lo que se puede revisar solo.\n"
            "Sube los cambios a esta misma branch: el pull request se\n"
            "actualiza solo y la revision se vuelve a correr. No abras otro."
        )
        return 1

    print(f"Ficha de '{rama}' en verde: {len(rel)} archivo(s) en {limpio(base)}/")
    return 0


def main():
    """Envuelve la revision entre `::stop-commands::` y su token de cierre.

    Mientras esta activo, Actions no interpreta ninguna linea `::comando::`
    del log: si algo del pull request se colara sin pasar por limpio(), no
    podria fingir una anotacion. El token es aleatorio para que el pull
    request no pueda adivinarlo y reactivar los comandos.
    """
    token = secrets.token_hex(16)
    print(f"::stop-commands::{token}")
    try:
        return _revisa()
    finally:
        print(f"::{token}::")


if __name__ == "__main__":
    sys.exit(main())
