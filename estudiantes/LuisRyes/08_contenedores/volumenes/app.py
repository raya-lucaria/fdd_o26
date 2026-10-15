"""
Lab 1: Bind Mounts — archivo de ejemplo
Este archivo vive en tu HOST. El contenedor lo ve vía volumen.
"""
import sys
import os
from datetime import datetime

print("=" * 40)
print("  Lab 1: Bind Mounts")
print("=" * 40)
print(f"Python version: {sys.version}")
print(f"Working dir:    {os.getcwd()}")
print(f"Timestamp:      {datetime.now().isoformat()}")
print()

# Listar archivos visibles en /app (el punto de montaje)
print("Archivos en /app:")
for f in sorted(os.listdir("/app")):
    size = os.path.getsize(f"/app/{f}")
    print(f"  {f:30s} {size:>6d} bytes")

print()

# Escribir un archivo de salida — aparecerá en tu host
output_path = "/app/output.txt"
with open(output_path, "w") as f:
    f.write(f"Generado por Python {sys.version}\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write(f"PID: {os.getpid()}\n")
    f.write(f"User: {os.getenv('USER', 'unknown')} (uid={os.getuid()})\n")

print(f"Archivo creado: {output_path}")
print("Revisa tu host — el archivo debería estar ahí.")
