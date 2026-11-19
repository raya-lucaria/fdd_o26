"""Guarda de la seccion 10.1 APIs y HTTP (unidad 10).

Lo que protege: el notebook es el que producen las paginas, las celdas citadas
existen, las paginas siguen el contrato de la clase (sin analogias, trio
Haz / Que hace / Deberias ver, cierre «Si sólo recuerdas»), y el servidor de
la plantilla cumple lo que las paginas muestran.
"""
import importlib.util
import json
import re
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SECCION = RAIZ / "course/10_apis/1_apis_y_http"
PLANTILLA = RAIZ / "codigo/10_apis"
NOTEBOOK = PLANTILLA / "apis.ipynb"

ORDEN = [
    ("1_que_es_una_api.md", "que-es-una-api"),
    ("2_el_mensaje_http.md", "el-mensaje-http"),
    ("3_metodos_y_status.md", "metodos-y-status"),
    ("4_http_rest_y_crud.md", "http-rest-y-crud"),
]
ANALOGIAS = ("imagina", "es como", "como si", "analogía", "piensa en", "receta",
             "cocina", "mesero", "restaurante")


def _modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _cuerpo(nombre):
    return (SECCION / nombre).read_text(encoding="utf-8").split("---", 2)[2]


def test_el_notebook_es_el_que_produce_su_generador():
    gen = _modulo("gen_notebook_apis", RAIZ / "tools/gen_notebook_apis.py")
    assert NOTEBOOK.read_text(encoding="utf-8") == gen.notebook(), (
        "apis.ipynb no coincide con tools/gen_notebook_apis.py: no lo edites a "
        "mano, cambia la pagina o CELDAS y vuelve a correr el generador")


def test_el_notebook_no_trae_salidas():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            assert c["outputs"] == [] and c["execution_count"] is None


def test_cada_celda_de_las_paginas_esta_en_CELDAS_y_en_orden():
    gen = _modulo("gen_notebook_apis", RAIZ / "tools/gen_notebook_apis.py")
    vistas = []
    for nombre in ["0_index.md"] + [n for n, _ in ORDEN]:
        vistas += re.findall(r"^\*\*Haz \(celda (\d+\.\d+)\):\*\*", _cuerpo(nombre), re.M)
    assert vistas == [c for c, _ in gen.CELDAS]


@pytest.mark.parametrize("nombre,ident", ORDEN)
def test_cada_pagina_tiene_su_id_y_su_numero(nombre, ident):
    texto = (SECCION / nombre).read_text(encoding="utf-8")
    assert f"\nid: {ident}\n" in texto
    n = nombre[0]
    assert f"**Página {n} de 4 · APIs y HTTP**" in texto


@pytest.mark.parametrize("nombre,_", ORDEN)
def test_sin_analogias(nombre, _):
    texto = _cuerpo(nombre).lower()
    for a in ANALOGIAS:
        assert a not in texto, f"{nombre}: «{a}»"


@pytest.mark.parametrize("nombre,_", ORDEN)
def test_cada_haz_trae_que_hace_y_deberias_ver(nombre, _):
    bloques = re.split(r"^\*\*Haz \(celda", _cuerpo(nombre), flags=re.M)[1:]
    assert bloques, f"{nombre} no tiene celdas"
    for b in bloques:
        assert "**Qué hace cada línea:**" in b and "**Deberías ver" in b


@pytest.mark.parametrize("nombre,_", ORDEN)
def test_cierra_con_si_solo_recuerdas(nombre, _):
    assert "> [!NOTE]\n> **Si sólo recuerdas una cosa:**" in _cuerpo(nombre)


def test_el_proyecto_pide_requests_y_ipykernel():
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    p = tomllib.loads((PLANTILLA / "pyproject.toml").read_text(encoding="utf-8"))
    assert any(d.startswith("requests") for d in p["project"]["dependencies"])
    assert any(d.startswith("ipykernel") for d in p["dependency-groups"]["dev"])
    assert (PLANTILLA / "uv.lock").is_file()


# ── el servidor hace lo que las paginas muestran ──────────────────────────

@pytest.fixture
def servidor():
    mod = _modulo("servidor_apis", PLANTILLA / "servidor.py")
    mod.imprime = lambda *a, **k: None
    mod.reiniciar()
    srv = mod.Servidor(("127.0.0.1", 0), mod.Ventas)   # la misma clase que __main__
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _pide(url, metodo="GET", datos=None, headers=None):
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(url, data=cuerpo, method=metodo, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


TOKEN = {"Authorization": "Bearer fdd-2026", "Content-Type": "application/json"}


def test_post_crea_con_201_y_location(servidor):
    status, headers, _ = _pide(f"{servidor}/ventas", "POST", {"producto": "té"}, TOKEN)
    assert status == 201 and headers["Location"] == "/ventas/5"


def test_401_403_405_como_en_la_galeria(servidor):
    assert _pide(f"{servidor}/ventas", "POST", {})[0] == 401
    lector = {"Authorization": "Bearer lector"}
    assert _pide(f"{servidor}/ventas", "POST", {}, lector)[0] == 403
    status, headers, _ = _pide(f"{servidor}/ventas/1", "PATCH", {})
    assert status == 405 and headers["Allow"] == "GET, HEAD, PUT, DELETE"


def test_delete_dos_veces_204_y_404(servidor):
    assert _pide(f"{servidor}/ventas/2", "DELETE", headers=TOKEN)[0] == 204
    assert _pide(f"{servidor}/ventas/2", "DELETE", headers=TOKEN)[0] == 404


def test_idempotency_key_repite_sin_crear(servidor):
    llave = {**TOKEN, "Idempotency-Key": "k1"}
    a = _pide(f"{servidor}/ventas", "POST", {"producto": "té"}, llave)
    b = _pide(f"{servidor}/ventas", "POST", {"producto": "té"}, llave)
    assert json.loads(a[2])["id"] == json.loads(b[2])["id"]
    assert b[1].get("Idempotent-Replayed") == "true"
    assert len(json.loads(_pide(f"{servidor}/ventas")[2])) == 5


def test_etag_da_304_sin_body(servidor):
    _, headers, _ = _pide(f"{servidor}/ventas/1")
    status, _, cuerpo = _pide(f"{servidor}/ventas/1", headers={"If-None-Match": headers["ETag"]})
    assert status == 304 and cuerpo == b""


def test_exportar_omite_el_charset_a_proposito(servidor):
    _, headers, _ = _pide(f"{servidor}/exportar")
    assert headers["Content-Type"] == "text/csv"
    _, headers, _ = _pide(f"{servidor}/ventas", headers={"Accept": "text/csv"})
    assert headers["Content-Type"] == "text/csv; charset=utf-8"


def test_post_no_pisa_un_id_que_ocupo_un_put(servidor):
    assert _pide(f"{servidor}/ventas/5", "PUT", {"producto": "pan"}, TOKEN)[0] == 201
    status, headers, _ = _pide(f"{servidor}/ventas", "POST", {"producto": "té"}, TOKEN)
    assert status == 201 and headers["Location"] == "/ventas/6"


def test_json_y_csv_tienen_etag_distinto_y_vary(servidor):
    _, h_json, _ = _pide(f"{servidor}/ventas/1")
    _, h_csv, _ = _pide(f"{servidor}/ventas/1", headers={"Accept": "text/csv"})
    assert h_json["ETag"] != h_csv["ETag"] and h_json["Vary"] == "Accept"
    status, _, _ = _pide(f"{servidor}/ventas/1", headers={"Accept": "text/csv",
                                                         "If-None-Match": h_json["ETag"]})
    assert status == 200


def test_put_con_body_invalido_responde_400(servidor):
    req = urllib.request.Request(f"{servidor}/ventas/1", data=b"hola", method="PUT", headers=TOKEN)
    try:
        urllib.request.urlopen(req, timeout=5)
        status = 200
    except urllib.error.HTTPError as e:
        status = e.code
    assert status == 400
