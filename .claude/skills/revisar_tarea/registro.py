#!/usr/bin/env python3
"""Lee y escribe el registro de entregas (branch `registro-entregas`, `registro.csv`).

El registro vive en una branch huérfana del repo del curso, nunca en `main`, y
se escribe SÓLO por la API de contenidos: no toca el árbol local ni hace
checkout. Una fila por (PR, tarea); un PR que cubre dos tareas lleva dos filas.
Se identifica sólo por login de GitHub, nunca por nombre real.

Subcomandos:
    leer        filtra y muestra filas              (sólo lectura)
    agregar     agrega la fila de un PR y una tarea (rellena lo que puede solo)
    actualizar  cambia campos de una fila existente

Ejemplos:
    python3 registro.py leer --tarea tarea-08-imagen
    python3 registro.py leer --login nat-aglo --formato json
    python3 registro.py leer --resumen
    python3 registro.py agregar --pr 91 --resultado mal \\
        --motivo "digest de otra longitud" --senales digest-recortado --dry-run
    python3 registro.py actualizar --pr 91 --resultado bien --motivo mergeado

Convenciones (las del README de la branch):
  abierto     timestamp UTC completo del PR (2026-09-22T03:14:15Z)
  due         AAAA-MM-DD; de la ficha, o del YAML oficial
  dias_tarde  días de calendario en hora de Ciudad de México después de due
              (0 a tiempo; vacío si no hay due)
  resultado   bien | mal | cerrada | pendiente
  senales     etiquetas separadas por «;»
  override    sólo por decisión del profesor
  revisado    fecha (Ciudad de México) de la revisión; hoy por defecto

Un motivo acusatorio («copió», «usó IA», «GPT», «trampa»…) es error; sólo
pasa con `--forzar`, por decisión del profesor. Las celdas que empiezan con
= + - @ se escriben con un apóstrofo delante (no son fórmulas).

`--dry-run` imprime lo que escribiría y no escribe nada. Sólo stdlib; quita
GH_TOKEN del entorno de `gh`.
"""
import argparse
import base64
import csv
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    import tomllib
except ImportError:  # Python < 3.11: basta una regex para `due`
    tomllib = None

REPO_DEF = "raya-lucaria/fdd_o26"
BRANCH = "registro-entregas"
ARCHIVO = "registro.csv"
COLUMNAS = ["login", "tarea", "pr", "intento", "abierto", "due", "dias_tarde",
            "resultado", "motivo", "senales", "override", "revisado"]
RESULTADOS = {"bien", "mal", "cerrada", "pendiente"}
CDMX = ZoneInfo("America/Mexico_City")
RAIZ = Path(__file__).resolve().parents[3]
# Señales ya usadas en el registro. Una nueva se acepta con aviso: que sea
# técnica, corta y en kebab-case, y que se agregue aquí y a la skill.
SENALES = {
    # forma de la entrega
    "archivo-fuera-de-tarea", "branch-de-otra-tarea", "carpeta-codigo-anidada",
    "carpeta-fuera-del-espejo", "dos-entregas-en-un-pr", "extension-no-coincide",
    "login-distinto",
    # plantilla
    "igual-al-original", "plantilla-sin-llenar", "seccion-vacia",
    "texto-de-plantilla-sin-borrar", "texto-mezclado-con-plantilla",
    # coherencia de la evidencia
    "bitacora-no-corresponde", "curso-no-terminado", "defecto-sin-corregir",
    "digest-recortado", "fecha-futura", "fecha-relativa", "salida-recortada",
    "salidas-incoherentes",
    # seguridad
    "inyeccion-de-prompt",
}
SENAL_CON_ARG = re.compile(r"^texto-igual-a:#\d+$")
# Un motivo guarda hechos. Estas palabras son conclusiones sobre el alumno:
# con ellas la fila no se escribe, salvo --forzar (decisión del profesor).
# Se comparan sin acentos y en minúsculas.
ACUSATORIAS = re.compile(
    r"\b(copio|copiado|plagio|plagiado|uso ia|usando ia|gpt|chatgpt|llm|"
    r"inteligencia artificial|trampa)\b")
# Una celda que empieza con estos caracteres la ejecuta como fórmula una hoja
# de cálculo. Se antepone un apóstrofo (idempotente: no se duplica).
FORMULA = ("=", "+", "-", "@")


def sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


def celda_segura(v):
    v = "" if v is None else str(v)
    return "'" + v if v.startswith(FORMULA) else v


# -------------------------------------------------------------------- GitHub API

def _env():
    env = dict(os.environ)
    env.pop("GH_TOKEN", None)
    return env


def gh(args, entrada=None):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True,
                       input=entrada, env=_env())
    return r.returncode, r.stdout, r.stderr


def lee_remoto(repo):
    """(filas, sha) del CSV en la branch del registro. Sale si no existe."""
    code, out, err = gh([f"repos/{repo}/contents/{ARCHIVO}?ref={BRANCH}"])
    if code != 0:
        sys.exit(f"No pude leer {ARCHIVO} en la branch {BRANCH} de {repo}.\n"
                 f"{err.strip()}\nEste script NO crea la branch ni el archivo.")
    d = json.loads(out)
    texto = base64.b64decode(d["content"]).decode("utf-8")
    lector = csv.DictReader(io.StringIO(texto))
    if lector.fieldnames != COLUMNAS:
        sys.exit(f"Las columnas de {ARCHIVO} no son las esperadas:\n"
                 f"  hay:    {lector.fieldnames}\n  espero: {COLUMNAS}\n"
                 "No escribo sobre un esquema que no conozco.")
    return list(lector), d["sha"]


def serializa(filas):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNAS, lineterminator="\n")
    w.writeheader()
    for f in filas:
        w.writerow({c: celda_segura(f.get(c, "")) for c in COLUMNAS})
    return buf.getvalue()


def escribe_remoto(repo, filas, sha, mensaje):
    cuerpo = json.dumps({
        "message": mensaje,
        "content": base64.b64encode(serializa(filas).encode()).decode(),
        "sha": sha,
        "branch": BRANCH,
    })
    code, out, err = gh(["-X", "PUT", f"repos/{repo}/contents/{ARCHIVO}",
                         "--input", "-"], entrada=cuerpo)
    if code != 0:
        return False, err
    return True, json.loads(out)["commit"]["sha"]


def pr_datos(repo, pr):
    code, out, err = gh([f"repos/{repo}/pulls/{pr}", "--jq",
                         "{login: .user.login, ref: .head.ref, created_at}"])
    if code != 0:
        sys.exit(f"No pude leer el PR #{pr}: {err.strip()}")
    return json.loads(out)


# ------------------------------------------------------------------- fechas y due

def hoy_cdmx():
    return dt.datetime.now(CDMX).date().isoformat()


def dias_tarde(abierto, due):
    if not due or not abierto:
        return ""
    t = dt.datetime.fromisoformat(abierto.replace("Z", "+00:00"))
    dia = t.astimezone(CDMX).date()
    return str(max(0, (dia - dt.date.fromisoformat(due)).days))


def due_de_ficha(tarea):
    ruta = RAIZ / ".github/tareas" / f"{tarea}.toml"
    if not ruta.exists():
        return None
    if tomllib:
        with open(ruta, "rb") as f:
            return (tomllib.load(f).get("tarea", {}) or {}).get("due")
    m = re.search(r'^\s*due\s*=\s*"(\d{4}-\d{2}-\d{2})"', ruta.read_text(), re.M)
    return m.group(1) if m else None


def due_de_yaml(tarea):
    """El due del YAML oficial cuyo id es `tarea`, o que nombra esa branch."""
    candidatos = []
    for p in (RAIZ / "course").rglob("_official/*/*.yaml"):
        t = p.read_text(encoding="utf-8")
        due = re.search(r'^\s*due:\s*"?(\d{4}-\d{2}-\d{2})', t, re.M)
        if not due:
            continue
        if re.search(rf"^id:\s*{re.escape(tarea)}\s*$", t, re.M):
            return due.group(1)
        if tarea.startswith("tarea-") and re.search(
                rf"branch\s+`?{re.escape(tarea)}\b", t):
            candidatos.append(due.group(1))
    return candidatos[0] if len(set(candidatos)) == 1 else None


def due_de(tarea):
    return due_de_ficha(tarea) or due_de_yaml(tarea)


# ----------------------------------------------------------------- validaciones

def valida(fila, forzar=False):
    errores, avisos = [], []
    if fila["resultado"] not in RESULTADOS:
        errores.append(f"resultado «{fila['resultado']}» no es uno de {sorted(RESULTADOS)}")
    for c in ("due",):
        if fila[c] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fila[c]):
            errores.append(f"{c} debe ser AAAA-MM-DD: «{fila[c]}»")
    if fila["revisado"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fila["revisado"]):
        errores.append(f"revisado debe ser AAAA-MM-DD: «{fila['revisado']}»")
    if fila["abierto"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                                            fila["abierto"]):
        errores.append(f"abierto debe ser timestamp UTC (…T…Z): «{fila['abierto']}»")
    for c in COLUMNAS:
        if "\n" in (fila.get(c) or ""):
            errores.append(f"{c} no puede llevar saltos de línea")
    for s in filter(None, (fila["senales"] or "").split(";")):
        if s not in SENALES and not SENAL_CON_ARG.match(s):
            avisos.append(f"señal nueva «{s}»: agrégala a SENALES y a la skill si se queda")
    m = ACUSATORIAS.search(sin_acentos(fila["motivo"] or "").lower())
    if m:
        texto = (f"el motivo dice «{m.group(0)}»: el registro guarda hechos, "
                 "no conclusiones sobre el alumno")
        if forzar:
            avisos.append(texto + " (escrito con --forzar)")
        else:
            errores.append(texto + ". Reescríbelo, o --forzar si lo decidió el profesor")
    return errores, avisos


# ------------------------------------------------------------------- subcomandos

def filtra(filas, a):
    out = filas
    if a.login:
        out = [f for f in out if f["login"].lower() == a.login.lower()]
    if a.tarea:
        out = [f for f in out if f["tarea"] == a.tarea]
    if a.pr:
        out = [f for f in out if f["pr"] == str(a.pr)]
    if getattr(a, "resultado", None):
        out = [f for f in out if f["resultado"] == a.resultado]
    return out


def cmd_leer(a):
    filas, _ = lee_remoto(a.repo)
    sel = filtra(filas, a)
    if a.resumen:
        tabla = {}
        for f in sel:
            tabla.setdefault(f["tarea"], {}).setdefault(f["resultado"], 0)
            tabla[f["tarea"]][f["resultado"]] += 1
        orden = ["bien", "mal", "pendiente", "cerrada"]
        print(f"{'tarea':32} " + " ".join(f"{r:>9}" for r in orden))
        for t in sorted(tabla):
            print(f"{t:32} " + " ".join(f"{tabla[t].get(r, 0):>9}" for r in orden))
        return 0
    if a.formato == "json":
        json.dump(sel, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif a.formato == "csv":
        sys.stdout.write(serializa(sel))
    else:
        cols = ["pr", "login", "tarea", "intento", "abierto", "due",
                "dias_tarde", "resultado", "senales", "override", "revisado", "motivo"]
        anchos = {c: max([len(c)] + [len(f[c]) for f in sel]) for c in cols[:-1]}
        print("  ".join(c.ljust(anchos.get(c, 0)) for c in cols))
        for f in sel:
            print("  ".join(f[c].ljust(anchos.get(c, 0)) for c in cols))
        print(f"\n{len(sel)} fila(s)")
    return 0


def _ordena(filas):
    return sorted(filas, key=lambda f: (int(f["pr"]) if f["pr"].isdigit() else 0,
                                        f["tarea"]))


def _guarda(a, filas, sha, mensaje, cambiadas):
    print("Fila(s) resultante(s):")
    sys.stdout.write(serializa(cambiadas))
    if a.dry_run:
        print(f"\n--dry-run: no se escribió nada en {BRANCH}.")
        return 0
    ok, info = escribe_remoto(a.repo, filas, sha, mensaje)
    if not ok and ("409" in info or "does not match" in info):
        return None                               # conflicto: reintentar
    if not ok:
        sys.exit(f"No pude escribir: {info.strip()}")
    print(f"\nEscrito en {BRANCH}: commit {info[:7]}")
    return 0


def cmd_agregar(a):
    datos = pr_datos(a.repo, a.pr) if not (a.login and a.tarea and a.abierto) else {}
    login = a.login or datos["login"]
    tarea = a.tarea or datos["ref"]
    abierto = a.abierto or datos["created_at"]
    for intento_escritura in range(2):
        filas, sha = lee_remoto(a.repo)
        if any(f["pr"] == str(a.pr) and f["tarea"] == tarea for f in filas):
            sys.exit(f"Ya hay fila para PR #{a.pr} y tarea {tarea}: usa `actualizar`.")
        due = a.due if a.due is not None else (due_de(tarea) or "")
        if not due and a.due is None:
            print(f"AVISO: no encontré el due de «{tarea}» (ni ficha ni YAML); "
                  "queda vacío. Pásalo con --due si lo sabes.", file=sys.stderr)
        previos = {f["pr"] for f in filas
                   if f["login"].lower() == login.lower() and f["tarea"] == tarea
                   and f["abierto"] < abierto}
        fila = {
            "login": login, "tarea": tarea, "pr": str(a.pr),
            "intento": str(a.intento or len(previos) + 1),
            "abierto": abierto, "due": due, "dias_tarde": dias_tarde(abierto, due),
            "resultado": a.resultado, "motivo": a.motivo or "",
            "senales": a.senales or "", "override": a.override or "",
            "revisado": a.revisado or ("" if a.resultado == "pendiente" else hoy_cdmx()),
        }
        errores, avisos = valida(fila, a.forzar)
        for av in avisos:
            print(f"AVISO: {av}", file=sys.stderr)
        if errores:
            sys.exit("No agrego la fila:\n  " + "\n  ".join(errores))
        nuevas = _ordena(filas + [fila])
        r = _guarda(a, nuevas, sha,
                    f"registro: {login} {tarea} #{a.pr} {a.resultado}", [fila])
        if r is not None:
            return r
        print("Conflicto: alguien escribió antes. Releo y reintento.", file=sys.stderr)
    sys.exit("Conflicto persistente al escribir; vuelve a correrlo.")


def cmd_actualizar(a):
    for intento_escritura in range(2):
        filas, sha = lee_remoto(a.repo)
        sel = [f for f in filas if f["pr"] == str(a.pr)
               and (not a.tarea or f["tarea"] == a.tarea)]
        if not sel:
            sys.exit(f"No hay fila para PR #{a.pr}"
                     f"{' y tarea ' + a.tarea if a.tarea else ''}: usa `agregar`.")
        if len(sel) > 1:
            sys.exit(f"PR #{a.pr} tiene {len(sel)} filas "
                     f"({', '.join(f['tarea'] for f in sel)}): di cuál con --tarea.")
        f = sel[0]
        antes = dict(f)
        for campo in ("resultado", "motivo", "override", "intento", "revisado", "due"):
            v = getattr(a, campo)
            if v is not None:
                f[campo] = v
        if a.senales is not None:
            f["senales"] = a.senales
        for s in a.agrega_senal or []:
            actuales = [x for x in f["senales"].split(";") if x]
            if s not in actuales:
                f["senales"] = ";".join(actuales + [s])
        if a.due is not None:
            f["dias_tarde"] = dias_tarde(f["abierto"], f["due"])
        if a.revisado is None and f["resultado"] != "pendiente" and f != antes:
            f["revisado"] = hoy_cdmx()
        if f == antes:
            print("Nada que cambiar.")
            return 0
        errores, avisos = valida(f, a.forzar)
        for av in avisos:
            print(f"AVISO: {av}", file=sys.stderr)
        if errores:
            sys.exit("No actualizo la fila:\n  " + "\n  ".join(errores))
        cambios = ", ".join(c for c in COLUMNAS if f[c] != antes[c])
        r = _guarda(a, filas, sha,
                    f"registro: {f['login']} {f['tarea']} #{a.pr} ({cambios})", [f])
        if r is not None:
            return r
        print("Conflicto: alguien escribió antes. Releo y reintento.", file=sys.stderr)
    sys.exit("Conflicto persistente al escribir; vuelve a correrlo.")


# -------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Registro de entregas en la branch registro-entregas "
                    "(sólo por la API de contenidos).",
        epilog=__doc__.split("Ejemplos:")[1].split("Convenciones")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", REPO_DEF))
    sub = ap.add_subparsers(dest="cmd", required=True)

    l = sub.add_parser("leer", help="muestra filas (sólo lectura)")
    l.add_argument("--login")
    l.add_argument("--tarea")
    l.add_argument("--pr", type=int)
    l.add_argument("--resultado", choices=sorted(RESULTADOS))
    l.add_argument("--formato", choices=["tabla", "csv", "json"], default="tabla")
    l.add_argument("--resumen", action="store_true",
                   help="conteo por tarea y resultado")
    l.set_defaults(func=cmd_leer)

    g = sub.add_parser("agregar", help="agrega la fila de (PR, tarea)")
    g.add_argument("--pr", type=int, required=True)
    g.add_argument("--resultado", required=True, choices=sorted(RESULTADOS))
    g.add_argument("--login", help="por defecto, el autor del PR")
    g.add_argument("--tarea", help="por defecto, la branch del PR; en la unidad 7, el id del YAML")
    g.add_argument("--abierto", help="timestamp UTC; por defecto, created_at del PR")
    g.add_argument("--due", help="AAAA-MM-DD; por defecto, de la ficha o del YAML")
    g.add_argument("--intento", help="por defecto, se cuenta en el registro")
    g.add_argument("--motivo", help="una frase corta y neutra")
    g.add_argument("--senales", help="etiquetas separadas por ;")
    g.add_argument("--override", help="SÓLO por decisión del profesor")
    g.add_argument("--revisado", help="AAAA-MM-DD; por defecto, hoy en CDMX")
    g.add_argument("--forzar", action="store_true",
                   help="acepta un motivo acusatorio: SÓLO por decisión del profesor")
    g.add_argument("--dry-run", action="store_true")
    g.set_defaults(func=cmd_agregar)

    u = sub.add_parser("actualizar", help="cambia campos de una fila")
    u.add_argument("--pr", type=int, required=True)
    u.add_argument("--tarea", help="obligatorio si el PR tiene dos filas")
    u.add_argument("--resultado", choices=sorted(RESULTADOS))
    u.add_argument("--motivo")
    u.add_argument("--senales", help="reemplaza todas las señales")
    u.add_argument("--agrega-senal", action="append", help="agrega una señal (repetible)")
    u.add_argument("--override", help="SÓLO por decisión del profesor")
    u.add_argument("--intento")
    u.add_argument("--due")
    u.add_argument("--revisado")
    u.add_argument("--forzar", action="store_true",
                   help="acepta un motivo acusatorio: SÓLO por decisión del profesor")
    u.add_argument("--dry-run", action="store_true")
    u.set_defaults(func=cmd_actualizar)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
