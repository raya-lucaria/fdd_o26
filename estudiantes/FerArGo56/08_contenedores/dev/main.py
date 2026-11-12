"""
Lab 3: Dev Workflow con Volúmenes
Este proyecto usa 'requests' (instalado en la imagen).
Monta tu código con -v para iterar sin rebuild.
"""
import requests

resp = requests.get("https://httpbin.org/ip")
print(f"Tu IP pública: {resp.json()['origin']}")
print("Status code:", resp.status_code)
