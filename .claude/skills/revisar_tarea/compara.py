#!/usr/bin/env python3
"""Compara las entregas del grupo y reporta los pares con texto compartido.

Uso:
    python3.12 compara.py tarea-08-imagen
    python3.12 compara.py --todas
    python3.12 compara.py tarea-08-imagen --json > pares.json

Qué junta, para la tarea (branch) pedida:
  1. Los pull requests de esa branch, abiertos y mergeados, leídos por la API
     (cada PR abierto cuenta como una entrega aparte: #N).
  2. Lo que ya está mergeado en `origin/main` bajo estudiantes/*/<carpeta>/.
  3. Salvo con --solo-tarea, las OTRAS carpetas de todos los alumnos
     en `origin/main`, para detectar texto compartido entre tareas distintas.

Qué quita antes de comparar:
  - Toda línea que aparece en la plantilla `codigo/<carpeta>/` (esa parte es
    igual para todos por diseño).
  - Los archivos que la ficha `.github/tareas/<branch>.toml` marca en
    [revision].igual_es_normal, cuando la entrada ES una ruta o un glob
    (`info/*.sh`), sin más texto. Las entradas en prosa
    se imprimen como recordatorio para quien revisa y no se aplican (las que
    hablan de la plantilla ya quedan cubiertas por el punto anterior).
  - Las líneas que comparten muchos alumnos (--comun): salidas de
    `docker version`, encabezados, comandos que todos corren igual.

Qué reporta, por par de entregas de alumnos DISTINTOS (al menos una de la tarea
pedida):
  - oraciones idénticas de >= --min-palabras palabras (8 por defecto), como
    evidencia literal;
  - similitud por shingles de palabras (contención y Jaccard);
  - archivos binarios idénticos byte a byte (misma captura en dos entregas).

Sólo lectura: no escribe en GitHub ni en el repo, no hace fetch. Si quieres
`origin/main` al día, corre antes `git fetch origin` tú.
Sólo stdlib. Quita GH_TOKEN del entorno de `gh` (el gh de esta máquina se
rompe con él).

Una coincidencia NO es una conclusión. Es un hecho que hay que leer: dos
alumnos pueden pegar la misma salida de un comando que todos corrieron. Nunca
se le dice a un alumno que «copió».
"""
import argparse
import base64
import fnmatch
import json
import os
import re
import subprocess
import sys
import unicodedata
from itertools import combinations
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

REPO_DEF = "raya-lucaria/fdd_o26"
RAIZ = Path(__file__).resolve().parents[3]
# Líneas que coinciden entre alumnos sin que nadie copie nada: las capas de la
# imagen base en `docker history` (salen como <missing> y son idénticas para
# todos los que usan la misma base).
RUIDO = re.compile(r"^<missing>\s")
BINARIOS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".webp", ".zip",
            ".tar", ".gz", ".ico", ".bmp"}


# --------------------------------------------------------------------- utilidades

def _env_gh():
    env = dict(os.environ)
    env.pop("GH_TOKEN", None)
    return env


def gh(*args, ok_fallo=False):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True,
                       env=_env_gh())
    if r.returncode != 0:
        if ok_fallo:
            return None
        sys.exit(f"gh api {' '.join(args)} falló:\n{r.stderr.strip()}")
    return r.stdout


def git(*args, ok_fallo=False):
    r = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True)
    if r.returncode != 0:
        if ok_fallo:
            return None
        sys.exit(f"git {' '.join(args)} falló:\n{r.stderr.decode(errors='replace')}")
    return r.stdout


def es_binario(ruta):
    return Path(ruta).suffix.lower() in BINARIOS


def normaliza(linea):
    """Minúsculas, sin marcas de Markdown, espacios colapsados."""
    s = linea.strip()
    s = re.sub(r"^[#>*\-+|`\d.\s]+", "", s)          # viñetas, títulos, citas
    s = s.replace("`", "").replace("*", "").replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def sin_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def limpia(t):
    """Quita los caracteres Unicode de categoría C* (control, formato,
    invisibles, bidi) de lo que se imprime: el texto del alumno es dato y no
    debe poder esconder nada ni reordenar la terminal."""
    return "".join(c for c in str(t) if not unicodedata.category(c).startswith("C"))


def palabras(s):
    return re.findall(r"[\w'/:.@-]+", sin_acentos(s))


# ------------------------------------------------------------------ tareas/fichas

def tareas_del_workflow():
    """{branch: carpeta} desde la variable TAREAS de entregas.yml."""
    wf = RAIZ / ".github/workflows/entregas.yml"
    if not wf.exists():
        return {}
    texto = wf.read_text(encoding="utf-8")
    m = re.search(r"TAREAS:\s*>-?\s*\n((?:\s+[^\n]*\n)+?)\s*(?:#|[A-Z_]+:)", texto)
    if not m:
        return {}
    mapa = {}
    for par in m.group(1).replace("\n", " ").split(","):
        if "=" in par:
            b, c = par.strip().split("=", 1)
            mapa[b.strip()] = c.strip()
    return mapa


def lee_ficha(branch):
    ruta = RAIZ / ".github/tareas" / f"{branch}.toml"
    if not ruta.exists():
        return None
    if tomllib is None:
        # Sin tomllib sólo se rescata la carpeta; igual_es_normal no se aplica.
        print(f"AVISO: este Python no lee TOML; de {ruta.name} sólo uso la "
              "carpeta. Corre con python3.12 para aplicar igual_es_normal.",
              file=sys.stderr)
        m = re.search(r'^\s*carpeta\s*=\s*"([^"]+)"', ruta.read_text(), re.M)
        return {"tarea": {"carpeta": m.group(1)}} if m else {}
    with open(ruta, "rb") as f:
        return tomllib.load(f)


def todas_las_tareas():
    mapa = tareas_del_workflow()
    fichas = RAIZ / ".github/tareas"
    if fichas.is_dir():
        for p in fichas.glob("tarea-*.toml"):
            f = lee_ficha(p.stem) or {}
            carpeta = f.get("tarea", {}).get("carpeta")
            if carpeta:
                mapa.setdefault(p.stem, carpeta)
    return mapa


def igual_es_normal(ficha):
    """Separa las entradas aplicables (rutas/globs) de las de prosa."""
    globs, prosa = [], []
    entradas = (ficha or {}).get("revision", {}).get("igual_es_normal", [])
    for e in entradas:
        if "plantilla" in e.lower():
            prosa.append(e)          # ya la cubre el quitar líneas de codigo/
            continue
        # Sólo se aplica lo inequívoco: una entrada que es, entera, una ruta o
        # un glob. Una frase que MENCIONA un archivo («la sección X de
        # certificaciones.md») no excluye el archivo.
        limpia = e.strip().strip("`")
        if re.fullmatch(r"[\w*?./\-\[\]]+", limpia):
            globs.append(limpia)
        else:
            prosa.append(e)
    return globs, prosa


def excluido(rel, globs):
    return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(Path(rel).name, g)
               for g in globs)


# ---------------------------------------------------------------------- plantillas

_cache_plantilla = {}


def lineas_plantilla(carpeta):
    if carpeta not in _cache_plantilla:
        base = RAIZ / "codigo" / carpeta
        lineas = set()
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and not es_binario(p.name):
                    try:
                        for l in p.read_text(encoding="utf-8").splitlines():
                            n = normaliza(l)
                            if n:
                                lineas.add(n)
                    except UnicodeDecodeError:
                        pass
        _cache_plantilla[carpeta] = lineas
    return _cache_plantilla[carpeta]


# ------------------------------------------------------------------------ fuentes

class Entrega:
    def __init__(self, login, carpeta, fuente, tarea):
        self.login = login
        self.carpeta = carpeta
        self.fuente = fuente            # "#57", "main"
        self.tarea = tarea              # branch pedida o None si es de otra tarea
        self.textos = {}                # rel -> texto
        self.blobs = {}                 # rel -> sha de blob (binarios)

    @property
    def etiqueta(self):
        return f"{self.login}/{self.carpeta} ({self.fuente})"


def prs_de(branch, repo):
    salida = gh("--paginate", f"repos/{repo}/pulls?state=all&per_page=100",
                "--jq", ".[] | {number, state, merged_at, merge_commit_sha,"
                " login: .user.login, ref: .head.ref, sha: .head.sha,"
                " head_repo: (.head.repo.full_name // null)}")
    prs = [json.loads(l) for l in salida.splitlines() if l.strip()]
    return [p for p in prs if p["ref"] == branch
            and (p["state"] == "open" or p["merged_at"])]


def lee_por_api(repo, ref, ruta):
    salida = gh(f"repos/{repo}/contents/{ruta}?ref={ref}", ok_fallo=True)
    if not salida:
        return None
    d = json.loads(salida)
    if d.get("encoding") != "base64" or not d.get("content"):
        return None
    try:
        return base64.b64decode(d["content"]).decode("utf-8")
    except UnicodeDecodeError:
        return None


def entregas_de_prs(branch, carpeta, repo, globs):
    out = []
    for p in prs_de(branch, repo):
        login, n = p["login"], p["number"]
        base = f"estudiantes/{login}/{carpeta}/"
        e = Entrega(login, carpeta, f"#{n}{'' if p['state'] == 'open' else ' mergeado'}",
                    branch)
        archivos = gh("--paginate", f"repos/{repo}/pulls/{n}/files?per_page=100",
                      "--jq", ".[] | {filename, status, sha}")
        # Mergeado: se lee del repo base en el commit de merge (el fork puede
        # ya no existir). Abierto: del fork, en el head del PR.
        if p["state"] == "open":
            fuente_repo, ref = p["head_repo"] or repo, p["sha"]
        else:
            fuente_repo, ref = repo, p["merge_commit_sha"]
        for l in archivos.splitlines():
            a = json.loads(l)
            if a["status"] == "removed" or not a["filename"].startswith(base):
                continue
            rel = a["filename"][len(base):]
            if excluido(rel, globs):
                continue
            if es_binario(rel):
                e.blobs[rel] = a["sha"]
                continue
            t = lee_por_api(fuente_repo, ref, a["filename"])
            if t is not None:
                e.textos[rel] = t
        out.append(e)
    return out


def entregas_de_main(carpetas_tarea, branch, globs, entre_tareas):
    ls = git("ls-tree", "-r", "origin/main", "--", "estudiantes/", ok_fallo=True)
    if ls is None:
        print("AVISO: no pude leer origin/main (¿falta `git fetch origin`?).",
              file=sys.stderr)
        return []
    por = {}
    for linea in ls.decode().splitlines():
        meta, ruta = linea.split("\t", 1)
        sha = meta.split()[2]
        partes = ruta.split("/")
        if len(partes) < 4:
            continue                       # archivo suelto en estudiantes/<login>/
        login, carpeta, rel = partes[1], partes[2], "/".join(partes[3:])
        es_tarea = carpeta in carpetas_tarea
        if not es_tarea and not entre_tareas:
            continue
        clave = (login, carpeta)
        if clave not in por:
            por[clave] = Entrega(login, carpeta, "main",
                                 branch if es_tarea else None)
        e = por[clave]
        if es_tarea and excluido(rel, globs):
            continue
        if es_binario(rel):
            e.blobs[rel] = sha
            continue
        crudo = git("show", f"origin/main:{ruta}", ok_fallo=True)
        try:
            e.textos[rel] = crudo.decode("utf-8") if crudo else ""
        except UnicodeDecodeError:
            pass
    return list(por.values())


# ---------------------------------------------------------------------- análisis

def lineas_propias(e):
    """Líneas normalizadas de la entrega que NO vienen de su plantilla.

    Si la línea empieza con un rótulo de la plantilla («fecha en que lo
    terminaste:»), el rótulo se quita y sólo se compara lo que escribió.
    """
    plantilla = lineas_plantilla(e.carpeta)
    rotulos = sorted((r for r in plantilla if r.endswith(":")), key=len, reverse=True)
    propias = []
    for rel, t in e.textos.items():
        for l in t.splitlines():
            n = normaliza(l)
            for r in rotulos:
                if n.startswith(r):
                    n = n[len(r):].strip()
                    break
            if n and n not in plantilla and len(n) > 3 and not RUIDO.match(n):
                propias.append(n)
    return propias


def oraciones(lineas, minimo):
    out = set()
    for l in lineas:
        for o in re.split(r"(?<=[.!?;])\s+", l):
            o = o.strip(" .;:!?")
            if len(palabras(o)) >= minimo:
                out.add(o)
    return out


def shingles(lineas, k):
    w = palabras(" ".join(lineas))
    return {" ".join(w[i:i + k]) for i in range(max(0, len(w) - k + 1))}


def analiza(entregas, branch, args):
    datos = {}
    for e in entregas:
        datos[id(e)] = lineas_propias(e)

    # Líneas que muchos alumnos comparten: salidas de comandos, encabezados.
    logins = {e.login for e in entregas}
    cuenta = {}
    for e in entregas:
        for n in set(datos[id(e)]):
            cuenta.setdefault(n, set()).add(e.login)
    tope = max(3, int(args.comun * len(logins)))
    comunes = {n for n, ls in cuenta.items() if len(ls) >= tope}

    feats = {}
    for e in entregas:
        ls = [n for n in datos[id(e)] if n not in comunes]
        feats[id(e)] = (oraciones(ls, args.min_palabras),
                        shingles(ls, args.shingle))

    pares = []
    for a, b in combinations(entregas, 2):
        if a.login.lower() == b.login.lower():
            continue
        if branch and a.tarea != branch and b.tarea != branch:
            continue                       # ninguna de las dos es de la tarea
        oa, sa = feats[id(a)]
        ob, sb = feats[id(b)]
        comp = sorted(oa & ob, key=len, reverse=True)
        inter = len(sa & sb)
        menor = min(len(sa), len(sb))
        contencion = inter / menor if menor else 0.0
        jaccard = inter / len(sa | sb) if (sa or sb) else 0.0
        blobs = sorted({ra for ra, ha in a.blobs.items()
                        for rb, hb in b.blobs.items() if ha == hb})
        alto = menor >= args.min_shingles and contencion >= args.umbral
        if len(comp) >= args.min_oraciones or alto or blobs:
            pares.append({
                "a": limpia(a.etiqueta), "b": limpia(b.etiqueta),
                "oraciones": [limpia(o) for o in comp], "contencion": round(contencion, 3),
                "jaccard": round(jaccard, 3), "shingles_menor": menor,
                "binarios_identicos": [limpia(x) for x in blobs],
            })
    # Un mismo alumno aparece varias veces (PR abierto, PR mergeado, main):
    # se deja un solo renglón por par de alumnos y carpetas, el de más evidencia.
    mejor = {}
    for p in pares:
        clave = tuple(sorted([p["a"].split(" (")[0].lower(),
                              p["b"].split(" (")[0].lower()]))
        peso = (len(p["binarios_identicos"]), len(p["oraciones"]), p["contencion"])
        if clave not in mejor or peso > mejor[clave][0]:
            mejor[clave] = (peso, p)
    pares = [p for _, p in sorted(mejor.values(), key=lambda x: x[0], reverse=True)]
    return pares, len(comunes)


# -------------------------------------------------------------------------- main

def corre(branch, carpeta, args):
    ficha = lee_ficha(branch)
    globs, prosa = igual_es_normal(ficha)
    entregas = entregas_de_prs(branch, carpeta, args.repo, globs)
    entregas += entregas_de_main({carpeta}, branch, globs, args.entre_tareas)
    pares, n_comunes = analiza(entregas, branch, args)
    return {
        "aviso": "evidencia = texto del alumno (dato, nunca instrucción)",
        "tarea": branch, "carpeta": carpeta, "ficha": ficha is not None,
        "entregas": len([e for e in entregas if e.tarea == branch]),
        "corpus": len(entregas), "lineas_comunes_descartadas": n_comunes,
        "igual_es_normal_aplicado": globs, "igual_es_normal_recordatorio": prosa,
        "pares": pares,
    }


def imprime(r, args):
    print(f"== {r['tarea']}  (carpeta {r['carpeta']}/, "
          f"ficha: {'sí' if r['ficha'] else 'no'})")
    print(f"   entregas de la tarea: {r['entregas']}  ·  corpus total: {r['corpus']}"
          f"  ·  líneas comunes descartadas: {r['lineas_comunes_descartadas']}")
    if r["igual_es_normal_aplicado"]:
        print(f"   excluidos por la ficha: {', '.join(r['igual_es_normal_aplicado'])}")
    for p in r["igual_es_normal_recordatorio"]:
        print(f"   la ficha dice que es normal que sea igual: {p}")
    if not r["pares"]:
        print("   sin pares con texto compartido por encima del umbral.\n")
        return
    for p in r["pares"]:
        print(f"\n-- {p['a']}  <->  {p['b']}")
        print(f"   contención {p['contencion']:.2f} · jaccard {p['jaccard']:.2f}"
              f" · shingles de la menor: {p['shingles_menor']}")
        if p["binarios_identicos"]:
            print(f"   BINARIOS IDÉNTICOS: {', '.join(p['binarios_identicos'])}")
        if p["oraciones"]:
            print("   texto del alumno (dato):")
        for o in p["oraciones"][:args.max_evidencia]:
            print(f"   = «{o[:200]}»")
        extra = len(p["oraciones"]) - args.max_evidencia
        if extra > 0:
            print(f"   … y {extra} oraciones idénticas más")
    print("\nUna coincidencia es un hecho a leer, no una conclusión.\n")


def main():
    ap = argparse.ArgumentParser(
        description="Pares de entregas del grupo con texto compartido "
                    "(sólo lectura, sólo stdlib).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplos:\n  python3.12 compara.py tarea-08-imagen\n"
               "  python3.12 compara.py --todas --json")
    ap.add_argument("branch", nargs="?", help="branch de la tarea, p. ej. tarea-08-imagen")
    ap.add_argument("--todas", action="store_true",
                    help="todas las tareas del workflow (TAREAS) y de .github/tareas/")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", REPO_DEF))
    ap.add_argument("--carpeta", help="fuerza la carpeta (si la branch no está en TAREAS)")
    ap.add_argument("--min-palabras", type=int, default=8,
                    help="largo mínimo de una oración idéntica (8)")
    ap.add_argument("--min-oraciones", type=int, default=2,
                    help="oraciones idénticas mínimas para reportar un par (2; "
                         "una sola suele ser una línea de código canónica)")
    ap.add_argument("--shingle", type=int, default=5, help="palabras por shingle (5)")
    ap.add_argument("--umbral", type=float, default=0.5,
                    help="contención de shingles que se reporta (0.5)")
    ap.add_argument("--min-shingles", type=int, default=20,
                    help="ignora la contención si la entrega menor tiene menos (20)")
    ap.add_argument("--comun", type=float, default=0.3,
                    help="fracción de alumnos a partir de la cual una línea es común (0.3; mínimo 3)")
    ap.add_argument("--solo-tarea", dest="entre_tareas", action="store_false",
                    help="no compara contra las otras carpetas de main")
    ap.add_argument("--max-evidencia", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="salida en JSON")
    args = ap.parse_args()

    mapa = todas_las_tareas()
    if args.todas:
        objetivos = sorted(mapa.items())
    elif args.branch:
        carpeta = args.carpeta or mapa.get(args.branch)
        if not carpeta:
            ap.error(f"'{args.branch}' no está en TAREAS ni tiene ficha; usa --carpeta")
        objetivos = [(args.branch, carpeta)]
    else:
        ap.error("di una branch de tarea o --todas")

    resultados = [corre(b, c, args) for b, c in objetivos]
    if args.json:
        json.dump(resultados, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for r in resultados:
            imprime(r, args)


if __name__ == "__main__":
    main()
