"""Dos ayudas para ver lo que viaja por el cable en la clase de APIs.

- a_mano(host, puerto, texto): manda una petición HTTP escrita a mano por un
  socket y regresa la respuesta tal como llegó, en texto.
- ver(r): imprime una petición y su respuesta de `requests` en el formato en
  que HTTP las escribe: línea inicial, headers, línea en blanco y body.
- total(): cuántas ventas tiene guardadas el servidor ahora mismo.
"""
import socket

import requests

URL = "http://127.0.0.1:8026"
TOKEN = {"Authorization": "Bearer fdd-2026"}


def total():
    """Cuántas ventas guarda el servidor (con un GET, que no cambia nada)."""
    return len(requests.get(f"{URL}/ventas", timeout=5).json())


def a_mano(host, puerto, texto):
    """Abre una conexión TCP, manda `texto` y lee hasta que el servidor cierra."""
    with socket.create_connection((host, puerto), timeout=10) as s:
        s.sendall(texto.encode())
        recibido = b""
        while trozo := s.recv(4096):
            recibido += trozo
    return recibido.decode(errors="replace")


def _corta(texto, limite):
    return texto if len(texto) <= limite else texto[:limite] + f" …(+{len(texto) - limite} caracteres)"


def ver(r, limite=300):
    """Imprime la petición (>>) y la respuesta (<<) de un `requests.Response`."""
    p = r.request
    ruta = p.path_url
    print(f">> {p.method} {ruta} HTTP/1.1")
    for nombre, valor in p.headers.items():
        print(f">> {nombre}: {valor}")
    print(">>")
    if p.body:
        cuerpo = p.body.decode() if isinstance(p.body, bytes) else p.body
        print(f">> {_corta(cuerpo, limite)}")
    print()
    version = {10: "1.0", 11: "1.1"}.get(r.raw.version, "?")
    print(f"<< HTTP/{version} {r.status_code} {r.reason}")
    for nombre, valor in r.headers.items():
        print(f"<< {nombre}: {valor}")
    print("<<")
    if r.content:
        print(f"<< {_corta(r.text, limite)}")
