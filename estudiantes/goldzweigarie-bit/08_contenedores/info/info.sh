#!/bin/bash
echo "=== Información del sistema ==="
echo "Hostname: $(hostname)"
echo "Usuario: $(whoami)"
echo "Directorio: $(pwd)"
echo "Fecha: $(date)"
echo "Kernel: $(uname -r)"
echo ""
echo "=== Procesos ==="
ps aux
echo ""
echo "=== Memoria ==="
free -h 2>/dev/null || echo "(free no disponible)"
echo ""
echo "=== Disco ==="

df -h /
echo "GitHub: goldzweigarie-bit"
echo "Fecha de build: $(cat /app/fecha_build)"
echo "Dato extra: arquitectura $(uname -m), $(nproc) CPUs"
