#!/usr/bin/env bash
# Unidad 07 — un script mínimo para tener algo que versionar.
# Cópialo a tu carpeta y modifícalo ahí; nunca aquí.
set -euo pipefail

nombre="${1:-mundo}"
echo "hola, ${nombre}"
echo "hoy es $(date +%Y-%m-%d)"
