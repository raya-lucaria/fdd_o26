#!/bin/bash
echo "=== Información del sistema ==="
echo "Hostname: $(hostname)"
echo "Usuario: $(whoami)"
echo "Directorio: $(pwd)"
echo "Fecha: $(date)"
echo "Kernel: $(uname -r)"
echo "GitHub: DabtcAvila"
echo "Imagen construida: 2026-09-24"
echo "Arquitectura: $(uname -m)"
echo "=== Procesos ==="
ps aux
echo "=== Memoria ==="
free -h 2>/dev/null || echo "(free no disponible)"
echo "=== Disco ==="
df -h /
