#!/bin/bash

GHUSER=cristoredendor

echo " === Usuario de github === "


echo "GitHub login: $GHUSER"

echo ""

echo " === Fecha de construcción  === "

echo "Build date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"

echo "" 

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
