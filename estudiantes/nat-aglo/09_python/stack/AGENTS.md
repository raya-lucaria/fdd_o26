# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

Qué librería usa este proyecto para cada cosa (forma de un dato, tablas,
archivos, pruebas, revisión), con su versión mayor, y qué no debe usar.

Forma de un dato: Usa pydantic 2.14.0 (`BaseModel`, `model_validate`, `ConfigDict`). 
No usar metodos ni sintaxis de versiones anteriores (pydantic>=2.0) del tipo `parse_obj`, `.dict()` ni `class Config`.
Tablas: Usar polars>=2.0 (`pl.DataFrame`, expresiones nativas con `pl.col`). Prohibido usar Pandas (`pd.DataFrame`, `pd.Series`, `.apply()`).
Manejo de archivos: Usar pathlib.Path y polars>=2.0 (`pl.read_csv`).Prohibido usar `os.path` o `csv.DictReader`
sobre `open()`.
Pruebas: Usar pytest>=9.0 (`pytest.raises(ValidationError)`).
Revision: Usar Ruff para estilo (`ruff check`) y Mypy (mypy>=2.0) para tipado. 

## Definición de terminado

Qué comandos deben salir en verde, y sobre qué archivos, antes de dar un
cambio por terminado.
Un cambio se considera terminado unicamente cuando los siguientes comandos se ejecutan y reportan la salida en verde (codigo de salida 0):
1. `ruff check practica.py test_practica.py`
Sobre el codigo fuente y las pruebas, finalizando sin advertencias ni errores de formato o sintaxis.
2. `mypy practica.py`
Sobre el codigo fuente, finalizando con "Success: no issues found" que nos garantiza que no existan discrepancias en el tipado ni tipos 
ausentes.
3. `pytest`
Sobre codigo de las pruebas. Asegura que todos los test pasen (passed), lo cual incluye pruebas	de validacion positiva y capturas de lo errores
mediante pytest.raises(ValidationError).

## Una regla mía

Una regla tuya, que salga de algo que viste en la clase o en la práctica, y
por qué.

Regla: Manipular cualquier ruta de archivo o directorio exclusivamente a través de `pathlib.Path`.
Por qué: (antes)Tratar rutas como strings a veces causa errores en otros SO (como diagonales / de Linux vs \ de Windows) y no valida si existe
el archivo. Path encapsula el sistema de archivos: nos da la ruta exacta sin importar el SO (resuelve diferencias), nos da la opcion de 
composicion de rutas por medio de '/', nos da varias opciones de metodos (como .parent para acceder a la carpeta padre), etc. 
