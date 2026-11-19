"""Servidor de ventas de la clase de APIs (10.1) y de la unidad 11.

Sólo usa la librería estándar. Córrelo en una terminal aparte y déjalo
abierto: cada petición que llega se imprime completa, tal como viajó
(la «radiografía»), y debajo lo que el servidor respondió.

    uv run python servidor.py

Para medir (unidad 11) la radiografía estorba: con FDD_SILENCIO=1 no
imprime nada por petición.

    FDD_SILENCIO=1 uv run python servidor.py

Lo que expone (el contrato) está en GET /, en JSON.
"""
import csv
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.parse import parse_qs, urlsplit

PUERTO = 8026
TOKEN = "fdd-2026"          # el token que escribe (POST, PUT, DELETE)
TOKEN_LECTOR = "lector"     # un token válido, pero sin permiso de escribir
SILENCIO = os.environ.get("FDD_SILENCIO") == "1"   # sin radiografía, para medir

INICIALES = [
    {"id": 1, "tienda": "Centro", "producto": "café", "cantidad": 3, "precio": 45.0},
    {"id": 2, "tienda": "Norte", "producto": "pan dulce", "cantidad": 6, "precio": 18.5},
    {"id": 3, "tienda": "Sur", "producto": "té", "cantidad": 2, "precio": 30.0},
    {"id": 4, "tienda": "Polanco", "producto": "café", "cantidad": 1, "precio": 52.0},
]
CAMPOS = ["id", "tienda", "producto", "cantidad", "precio"]

CONTRATO = {
    "api": "ventas de la clase",
    "endpoints": {
        "GET /ventas": "lista las ventas (filtra con ?tienda=Norte)",
        "GET /ventas/{id}": "una venta",
        "POST /ventas": "crea una venta (pide token)",
        "PUT /ventas/{id}": "reemplaza una venta completa (pide token)",
        "DELETE /ventas/{id}": "borra una venta (pide token)",
        "GET /exportar": "las ventas en CSV, desde un endpoint viejo",
        "GET /panel": "una página HTML con enlaces",
        "GET /borrar?id={id}": "borra con GET (mal diseño, a propósito)",
        "POST /reiniciar": "regresa los datos al inicio",
        "GET /quien": "tu puerto, el hilo que te atiende y cuántas peticiones lleva tu conexión",
    },
    "autenticacion": "header Authorization: Bearer <token>",
    "formatos": ["application/json", "text/csv"],
}

ventas = {}
siguiente_id = 1
respuestas_guardadas = {}   # Idempotency-Key -> (status, cuerpo)
peticiones = 0
candado = Lock()          # un cambio a la vez: los hilos del servidor atienden peticiones concurrentes


def reiniciar():
    global siguiente_id
    ventas.clear()
    ventas.update({v["id"]: dict(v) for v in INICIALES})
    siguiente_id = len(INICIALES) + 1
    respuestas_guardadas.clear()


def en_csv(filas):
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=CAMPOS, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return salida.getvalue()


def etag_de(cuerpo):
    """Huella de los bytes exactos de una representación."""
    return f'"{hashlib.sha256(cuerpo).hexdigest()[:12]}"'


def imprime(texto=""):
    if SILENCIO:
        return
    print(texto, file=sys.stderr, flush=True)


class Ventas(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"   # sin esto, http.server responde HTTP/1.0
    disable_nagle_algorithm = True  # sin esto, cada respuesta tarda ~40 ms de más
    def version_string(self):        # el header Server de cada respuesta
        return "VentasFDD/1.0"

    def log_message(self, *args):   # el log de siempre, lo reemplaza la radiografía
        pass

    def setup(self):
        super().setup()
        self.n_en_conexion = 0   # un handler por conexión: con keep-alive cuenta sus peticiones

    # ── entrada ───────────────────────────────────────────────────────────
    def leer(self):
        global peticiones
        with candado:   # `+= 1` lee, suma y escribe: sin candado dos hilos pueden perder una cuenta
            peticiones += 1
            numero = peticiones
        self.n_en_conexion += 1
        largo = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(largo) if largo else b""
        imprime(f"\n━━ petición #{numero} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        imprime(f"  {self.requestline}")
        for nombre, valor in self.headers.items():
            imprime(f"  {nombre}: {valor}")
        if cuerpo:
            imprime("")
            imprime(f"  {cuerpo.decode(errors='replace')}")
        partes = urlsplit(self.path)
        self.ruta = partes.path.rstrip("/") or "/"
        self.query = {k: v[0] for k, v in parse_qs(partes.query).items()}
        if "lento" in self.query:
            time.sleep(float(self.query["lento"]))
        return cuerpo

    # ── salida ────────────────────────────────────────────────────────────
    def responder(self, status, datos=None, headers=None, tipo=None):
        headers = dict(headers or {})
        cuerpo = b""
        if datos is not None:
            tipo, cuerpo = self.serializa(datos, tipo)
            headers["Content-Type"] = tipo
        self.send_response(status)
        for nombre, valor in headers.items():
            self.send_header(nombre, valor)
        if status not in (204, 304):   # esas dos respuestas nunca llevan body
            self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(cuerpo)
        imprime(f"  ⇢ respondí {status} {self.responses[status][0]}"
                f"   · ventas guardadas: {len(ventas)}")

    def serializa(self, datos, tipo=None):
        """Convierte datos de Python en (Content-Type, bytes), según Accept."""
        if tipo is None:
            quiere_csv = "text/csv" in self.headers.get("Accept", "")
            tipo = "text/csv; charset=utf-8" if quiere_csv else "application/json"
        if tipo.startswith("text/csv"):
            filas = datos if isinstance(datos, list) else [datos]
            return tipo, en_csv(filas).encode()
        if tipo.startswith("text/html"):
            return tipo, datos.encode()
        return tipo, json.dumps(datos, ensure_ascii=False).encode()

    def error(self, status, mensaje, headers=None):
        self.responder(status, {"error": mensaje}, headers, tipo="application/json")

    def id_de_la_ruta(self):
        m = re.fullmatch(r"/ventas/(\d+)", self.ruta)
        return int(m.group(1)) if m else None

    def autorizado(self):
        """Regresa True si puede escribir; si no, ya respondió 401 o 403."""
        valor = self.headers.get("Authorization", "")
        if valor == f"Bearer {TOKEN}":
            return True
        if valor == f"Bearer {TOKEN_LECTOR}":
            self.error(403, "tu token es válido, pero sólo puede leer")
            return False
        self.error(401, "falta el token o no es válido",
                   {"WWW-Authenticate": 'Bearer realm="ventas"'})
        return False

    # ── métodos ───────────────────────────────────────────────────────────
    def do_GET(self):
        self.leer()
        if self.ruta == "/":
            return self.responder(200, CONTRATO, tipo="application/json")
        if self.ruta == "/ventas":
            with candado:   # otro hilo puede cambiar el dict mientras se recorre
                filas = [v for v in ventas.values()
                         if self.query.get("tienda") in (None, v.get("tienda"))]
            return self.con_etag(filas)
        if self.id_de_la_ruta() is not None:
            with candado:
                venta = ventas.get(self.id_de_la_ruta())
            if venta is None:
                return self.error(404, f"no hay venta {self.id_de_la_ruta()}")
            return self.con_etag(venta)
        if self.ruta == "/exportar":
            # Endpoint viejo: dice que es CSV pero no dice en qué codificación.
            with candado:
                filas = list(ventas.values())
            return self.responder(200, filas, tipo="text/csv")
        if self.ruta == "/panel":
            with candado:
                ids = list(ventas)
            enlaces = "\n".join(f'<a href="/borrar?id={i}">borrar venta {i}</a><br>'
                                for i in ids)
            return self.responder(200, f"<h1>Panel de ventas</h1>\n{enlaces}\n",
                                  tipo="text/html; charset=utf-8")
        if self.ruta == "/quien":
            return self.responder(200, {"puerto": self.client_address[1],
                                        "hilo": threading.current_thread().name,
                                        "peticion_en_conexion": self.n_en_conexion})
        if self.ruta == "/borrar":
            with candado:
                ventas.pop(int(self.query.get("id", 0)), None)
            return self.responder(200, {"ok": True})
        self.error(404, f"no existe {self.ruta}")

    def con_etag(self, datos):
        tipo, cuerpo = self.serializa(datos)
        # Cada representación (JSON o CSV) tiene su propia huella, y Vary avisa
        # a las cachés que la respuesta depende del header Accept.
        headers = {"ETag": etag_de(cuerpo), "Vary": "Accept"}
        if self.headers.get("If-None-Match") == headers["ETag"]:
            return self.responder(304, headers=headers)
        self.responder(200, datos, headers, tipo=tipo)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        cuerpo = self.leer()
        if self.ruta == "/reiniciar":
            with candado:
                reiniciar()
                n = len(ventas)
            return self.responder(200, {"ok": True, "ventas": n})
        if self.ruta != "/ventas":
            return self.error(405, "aquí no se crea nada", {"Allow": "GET, HEAD"})
        if not self.autorizado():
            return
        with candado:   # revisar la llave, dar el id y guardar sin que otro hilo se cuele
            status, datos, headers, tipo = self.crear(cuerpo)
        self.responder(status, datos, headers, tipo)   # escribir a la red, fuera del candado

    def crear(self, cuerpo):
        """Sólo toca los datos y regresa la respuesta; no escribe al socket."""
        global siguiente_id
        llave = self.headers.get("Idempotency-Key")
        if llave in respuestas_guardadas:
            status, guardada = respuestas_guardadas[llave]
            return status, guardada, {"Idempotent-Replayed": "true"}, None
        try:
            nueva = json.loads(cuerpo)
        except json.JSONDecodeError:
            return 400, {"error": "el body no es JSON válido"}, None, "application/json"
        if not isinstance(nueva, dict):
            return 400, {"error": "el body debe ser un objeto JSON"}, None, "application/json"
        while siguiente_id in ventas:  # un PUT pudo haber ocupado este id
            siguiente_id += 1
        nueva["id"] = siguiente_id
        ventas[siguiente_id] = nueva
        siguiente_id += 1
        if llave:
            respuestas_guardadas[llave] = (201, nueva)
        return 201, nueva, {"Location": f"/ventas/{nueva['id']}"}, None

    def do_PUT(self):
        cuerpo = self.leer()
        i = self.id_de_la_ruta()
        if i is None:
            return self.error(405, "PUT va a una venta: /ventas/{id}", {"Allow": "GET, HEAD, POST"})
        if not self.autorizado():
            return
        try:
            nueva = json.loads(cuerpo)
        except json.JSONDecodeError:
            return self.error(400, "el body no es JSON válido")
        if not isinstance(nueva, dict):
            return self.error(400, "el body debe ser un objeto JSON")
        with candado:   # comprobar, escribir y copiar la respuesta sin que otro hilo se cuele
            existia = i in ventas
            ventas[i] = {**nueva, "id": i}
            guardada = dict(ventas[i])
        self.responder(200 if existia else 201, guardada)

    def do_DELETE(self):
        self.leer()
        i = self.id_de_la_ruta()
        if i is None:
            return self.error(405, "DELETE va a una venta: /ventas/{id}", {"Allow": "GET, HEAD, POST"})
        if not self.autorizado():
            return
        with candado:
            borrada = ventas.pop(i, None)
        if borrada is None:
            return self.error(404, f"no hay venta {i}")
        self.responder(204)

    def do_PATCH(self):
        self.leer()
        self.error(405, "este servidor no implementa PATCH",
                   {"Allow": "GET, HEAD, PUT, DELETE"})


class Servidor(ThreadingHTTPServer):
    request_queue_size = 1024   # por omisión son 5: con 500 clientes a la vez, el resto se rechaza


if __name__ == "__main__":
    reiniciar()
    imprime(f"Servidor de ventas en http://127.0.0.1:{PUERTO}  (Ctrl+C para apagarlo)")
    Servidor(("127.0.0.1", PUERTO), Ventas).serve_forever()
