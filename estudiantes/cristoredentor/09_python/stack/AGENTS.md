# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

Es la práctica de la 9.3: sacar el total vendido por tienda de `ventas.csv`.
Las versiones exactas están en `uv.lock`.

- Presupón que se está usando python 3.14, con uv para el ambiente y las dependencias (nada de
  `pip install`).
- Usar Pydantic 2 parara validar cada fila del CSV. La
  sintaxis de la v1 (`.dict()`, `@validator`, `class Config`) ya está
  obsoleta, así que se usa la de la v2: `model_validate`, `model_dump`,
  `field_validator`.
- Usa Polars para las tablas. Es mucho más rápido que pandas porque trabaja por columnas y no fila por fila, así que todo el cálculo va con expresiones (pl.col, group_by). Nada de .apply, map_elements ni for sobre las filas. pandas sólo aparece en
ventas_ia.py, que es el código que se reescribió.
Usa pathlib para las rutas, no os.path.
Usa pytest para las pruebas, ruff y mypy para revisar el código.

Si vas a meter una librería que no está aquí, pregúntame primero.

**Cómo se corre** (el ambiente `.venv-stack` vive en la raíz del fork):

```bash
source .venv-stack/bin/activate        # desde la raíz del fork
cd estudiantes/cristoredentor/09_python/stack
uv sync --active
python practica.py
```

## Definición de terminado

Un cambio está listo cuando esto pasa, corrido dentro de `stack/`:

```bash
ruff check practica.py test_practica.py   # All checks passed!
mypy practica.py                          # Success: no issues found
pytest -v test_practica.py                # todo passed, nada skipped
```

Sólo sobre esos archivos: modelos.py tiene errores a propósito. Además,
python practica.py tiene que dar los mismos totales que ventas_ia.py.
No se modifican ventas_ia.py, modelos.py, datos.py, mide.py ni
ventas.csv.

## Una regla mía

Se valida una sola vez, al leer el CSV, y nunca otra vez.

valida() pasa cada fila por el modelo Venta y tira las que vienen mal
(un precio "abc", una fecha que no es fecha). Lo que sale de ahí ya es
confiable, así que total_por_tienda() lo trabaja directo en Polars sin
volver a revisarlo. Validar tiene un costo, y pagarlo dos veces por el mismo
dato no gana nada.
