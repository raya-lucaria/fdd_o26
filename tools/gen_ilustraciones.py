"""Genera ilustraciones con gpt-image-2. Nunca personas reales ni personajes protegidos."""
import base64
import io
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "tools/ilustraciones.json"
# La unidad de cada ilustracion vive en el catalogo: agregar una unidad con
# portada propia es agregar una linea ahi, no editar este archivo.
UNIDAD_POR_OMISION = "2_pipeline_de_datos"
URL = "https://api.openai.com/v1/images/generations"
MODELO = os.environ.get("MODELO_IMAGEN", "gpt-image-2")
CALIDAD_JPEG = 85


def clave():
    valor = os.environ.get("OPENAI_API_KEY")
    if not valor:
        raise SystemExit("falta OPENAI_API_KEY: correr 'set -a && . ./.env && set +a'")
    return valor


def assets_de(datos, nombre):
    unidad = datos.get("unidades", {}).get(nombre, UNIDAD_POR_OMISION)
    return RAIZ / "course" / unidad / "_assets"


def generar(nombre):
    datos = json.loads(CATALOGO.read_text(encoding="utf-8"))
    assets = assets_de(datos, nombre)
    assets.mkdir(parents=True, exist_ok=True)
    # Casi todas comparten el estilo del curso; una lamina puede declarar el
    # suyo en "estilos" cuando su registro visual no es el urbano.
    estilo = datos.get("estilos", {}).get(nombre, datos["estilo"])
    prompt = f'{datos["ilustraciones"][nombre]} {estilo}'
    cuerpo = json.dumps({
        "model": MODELO,
        "prompt": prompt,
        "size": datos["tamano"],
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        URL, data=cuerpo,
        headers={"Authorization": f"Bearer {clave()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        salida = json.load(r)
    item = salida["data"][0]
    if item.get("b64_json"):
        crudo = base64.b64decode(item["b64_json"])
    else:
        with urllib.request.urlopen(item["url"], timeout=300) as r:
            crudo = r.read()
    destino = assets / f"ilus-{nombre}.jpg"
    with Image.open(io.BytesIO(crudo)) as im:
        im = im.convert("RGB")
        if im.width != 1024:
            im = im.resize((1024, round(im.height * 1024 / im.width)), Image.LANCZOS)
        im.save(destino, "JPEG", quality=CALIDAD_JPEG, optimize=True)
    print(f"{destino.name}  ({destino.stat().st_size/1000:.0f} KB)")
    return destino


if __name__ == "__main__":
    nombres = sys.argv[1:]
    if not nombres:
        raise SystemExit("uso: gen_ilustraciones.py <nombre> [nombre ...]")
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(generar, nombres))
