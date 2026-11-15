# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

Qué librería usa este proyecto para cada cosa (forma de un dato, tablas,
archivos, pruebas, revisión), con su versión mayor, y qué no debe usar.

Python 3.x, Pydantic v2 (`BaseModel`, `field_validator`, `model_validate`,
`model_dump`) en la frontera, Polars para agregar, `pathlib` para rutas,
pytest para pruebas. Prohibido: `.apply`, `.dict()`, `@validator`, `os.path`.


## Definición de terminado

Qué comandos deben salir en verde, y sobre qué archivos, antes de dar un
cambio por terminado.
Corren sin errores, sobre `practica.py` y `test_practica.py`:
`ruff check practica.py test_practica.py`, `mypy practica.py` y `pytest`.



## Una regla mía

Una regla tuya, que salga de algo que viste en la clase o en la práctica, y
por qué.
Nunca usar pandas
Nunca cargar pickles ni archivos de origen
desconocido, validar toda entrada externa con un modelo de Pydantic