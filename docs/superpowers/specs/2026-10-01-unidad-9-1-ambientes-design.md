# Unidad 9 · Python — sección 9.1 Ambientes (diseño)

Fecha: 2026-10-01 · Estado: **borrador para revisión del profesor**

## 1 · Qué es y para quién

Abre la unidad **9 · Python** (`course/9_python/`). Por ahora sólo existe la
sección **9.1 Ambientes**; las demás secciones se agregan cuando se escriban.

- Público: primera vez que ven ambientes, paquetes y gestores. Lectores con
  ADHD: párrafos de ≤ 3 líneas, **bold** sólo en lo que se rompe si no se lee,
  tabla antes que prosa, diagramas, y casi todo es comando + qué esperar.
- **Sin analogías.** Cada concepto: qué es (una línea) + el comando que lo
  demuestra + su salida. Las comparaciones son técnicas (qué aísla cada cosa),
  nunca metáforas.
- **El núcleo es uv y su `.venv`.** `venv` + `pip` se enseña corto, para
  reconocerlo en un README. conda, poetry, pdm, hatch, pixi, pyenv, pipx,
  pipenv, pip-tools se nombran, se comparan con pros y contras y no se
  practican.

## 2 · Decisiones tomadas

| Decisión | Valor |
|---|---|
| Sesión | **Hoy, jueves 2026-10-01, 19:00–20:00 (60 min)** |
| Herramienta núcleo | uv (`uv init/add/run/sync/lock`, `uv python`, `uvx`) |
| venv/pip | Una página corta + el experimento «pip con y sin ambiente activo» |
| Nombre del anexo de comandos | **Cheatsheet** (no «chuleta») |
| Tarea | Certificado DataCamp *Introduction to Python for Developers* + ejercicio uv dentro de Docker publicado en Docker Hub |
| Skill de la tarea | `crear_tarea` (seis piezas + revisión adversarial) |

### Supuestos por confirmar (el profesor no contestó; se usó lo recomendado)

| # | Supuesto | Alternativa |
|---|---|---|
| S1 | **Dos entregas**: `tarea-09-datacamp-python` → carpeta `python/`; `tarea-09-uv-docker` → carpeta `09_python/` | Una sola entrega en `09_python/` |
| S2 | Ambas vencen **2026-10-06** (martes, antes de clase); abren 2026-10-01 | 10-08, o escalonado |
| S3 | **10 puntos** cada una, penalización `"1/dia"` | `"a-decidir"` |
| S4 | IA **`permitida-revisada`** | `permitida` / `prohibida` |
| S5 | Esta sesión es **`session-13`** (asume que el martes 2026-09-29 no tuvo clase registrada) | `session-14` si el 29 hubo clase |

## 3 · El mapa mental (figura de portada y de cierre)

Diagrama técnico de qué produce qué. Se repite al final de la sección.

```
   lo que pides             lo que se resolvió          lo que está instalado
 pyproject.toml ──uv lock──▶ uv.lock ──uv sync──▶ .venv/ (python + site-packages)
      ▲                         ▲                         │
   uv add rich               PyPI                    uv run hola.py
                         uv python install ── el intérprete también lo pone uv
 git: ✅ pyproject.toml  ✅ uv.lock  ❌ .venv/  (se borra y se recrea con uv sync)
```

## 4 · Páginas

Ruta: `course/9_python/1_ambientes/`. 🎯 = se hace en clase (60 min);
📖 = lectura.

| # | Archivo | Contenido | |
|---|---|---|---|
| 0 | `0_index.md` | En corto, el mapa mental, tabla de páginas, qué está instalado antes de clase | 🎯 |
| 1 | `1_el_problema.md` | Dos proyectos con versiones incompatibles de un paquete y un solo Python. El error real `externally-managed-environment` (PEP 668) en Ubuntu y Homebrew | 🎯 |
| 2 | `2_las_piezas.md` | Glosario en tres columnas — término · qué es · lo ves con: intérprete, paquete, PyPI, pip, dependencia transitiva, ambiente, resolver, lockfile, TOML | 📖 |
| 3 | `3_un_ambiente_por_dentro.md` | Tres hechos con su comando: (1) es una carpeta — `ls .venv`, `cat .venv/pyvenv.cfg`; (2) trae su `python` y su `site-packages`; (3) activar = poner `.venv/bin` al frente del `PATH` — `which python` antes/después, `echo $PATH`. `quien_soy.py` corrido tres veces: sin activar, activado, con `uv run`. Remate: con uv no hace falta activar | 🎯 |
| 4 | `4_los_archivos.md` | Tabla `requirements.txt` / `pyproject.toml` (PEP 621) / `uv.lock`·`poetry.lock`·`pdm.lock` / `pylock.toml` (PEP 751) / `environment.yml`: qué es, quién lo escribe, ¿exacto?, ¿va a git? Un `pyproject.toml` de 8 líneas anotado; `[tool.X]` es lo propio de cada herramienta | 📖 |
| 5 | `5_las_herramientas.md` | Los 5 trabajos (instalar paquetes, aislar, proyecto + lock, versiones de Python, CLIs globales) × herramienta. Tabla grande con año, qué hace, pros, contras, dónde la verás: pip+venv, pip-tools, pipenv, poetry, pdm, hatch, conda/mamba, pixi, pyenv, pipx, uv. Árbol «¿cuál uso?». Rye se fundió en uv. Contras honestos de uv: empresa privada, adquirida por OpenAI (anuncio 2026-03-19); no maneja paquetes no-Python → pixi/conda | 📖 |
| 6 | `6_ambiente_conda_docker.md` | Tabla de qué aísla cada uno: paquetes / intérprete / librerías del SO / sistema de archivos / procesos / kernel (✅/❌), para venv-uv, conda/pixi y Docker. Cierra: en Docker también se usa uv (puente a la tarea) | 📖 |
| 7 | `7_lab_uv.md` | **El núcleo.** Diez pasos, cada uno comando + qué esperar + qué cambió en el mapa: `uv python list/install`, `uv init`, `uv add rich`, `uv run hola.py`, leer `uv.lock` (transitivas, `uv tree`), `rm -rf .venv` → `uv run` lo recrea, `uv remove` / `uv add --dev`, `uvx`, script con dependencias en línea (PEP 723), puente: `uv pip install`, `uv export` | 🎯 |
| 8 | `8_venv_y_pip.md` | Lab corto clásico: `python3 -m venv`, activar (Linux/macOS y Windows), `pip install`, `pip freeze > requirements.txt`, `deactivate`, borrar. Experimento predice-y-corre: `pip install` con y sin ambiente activo, con `quien_soy.py` | 📖 |
| 9 | `9_vs_code.md` | Ctrl+Shift+P → *Python: Select Interpreter* (el `.venv` de uv) y *Python: Create Environment*; dónde se ve en la barra inferior; la terminal integrada que se activa sola; el kernel de Jupyter | 🎯 |
| 10 | `10_las_trampas.md` | Síntoma → causa → dónde mirar: `ModuleNotFoundError` con el paquete instalado, pip instaló en otro Python, `.venv` en git, `python` vs `python3`, PEP 668, ExecutionPolicy de PowerShell, `.venv` copiado a una imagen Docker, `--locked` falla porque el lock no coincide | 📖 |
| A | `11_A_cheatsheet.md` | Una tabla: tarea · uv · venv+pip · poetry · conda. Sólo para traducir | 📖 |
| B | `12_B_entregas.md` | Tablero de las entregas de la unidad (modelo: `8_contenedores/7_D_entregas.md`) | 📖 |

Plan de la sesión de 60 min: 1 (5) → 3 (15) → 7 (30) → 9 (10).

IDs: unidad `python`, sección `ambientes-python`; páginas con id descriptivo
en inglés-o-español según el patrón del repo (`el-problema-de-los-ambientes`,
`ambiente-por-dentro`, `lab-uv`, …). Numbered objects con prefijo `py-`.

## 5 · Diagramas

Generador nuevo `tools/gen_python.py` con su catálogo `DIAGRAMAS` y su
`tools/test_gen_python.py`; paleta desde `tools/svg_base.py`. Cada SVG con
fila en `course/9_python/_assets/CREDITOS.md`.

| ID | Página | Muestra |
|---|---|---|
| `py-mapa` | 0, 7 | El mapa mental de § 3 |
| `py-choque` | 1 | Dos proyectos, un `site-packages` global, versión que pisa a la otra |
| `py-path` | 3 | La shell buscando `python` en el `PATH`, sin y con `.venv/bin` al frente |
| `py-venv-arbol` | 3 | El árbol de `.venv/` con lo que es cada cosa |
| `py-trabajos` | 5 | Matriz 5 trabajos × herramientas |
| `py-cual-uso` | 5 | Árbol de decisión |
| `py-aislamiento` | 6 | Capas: kernel / SO / intérprete / paquetes y qué cubre cada herramienta |
| `py-uv-docker` | B / tarea | Dockerfile: lock primero, `uv sync --locked`, código después |

Ilustración de portada (`gen_ilustraciones.py`): opcional, se decide al
implementar.

## 6 · Código del repo

`codigo/09_python/` (espejo; el alumno copia a `estudiantes/$GHUSER/09_python/`):

```
codigo/09_python/
├── README.md              # el ritual de copia, como codigo/08_contenedores/README.md
├── ambientes/             # labs de clase (no se entregan)
│   ├── quien_soy.py       # qué Python corre, sys.prefix, ¿estoy en un ambiente?
│   ├── hola.py            # hello world con rich
│   ├── script_autonomo.py # PEP 723: dependencias declaradas en el propio archivo
│   └── requirements.txt   # para el lab clásico
└── uv_docker/             # la tarea 2
    ├── reporte.py
    ├── pyproject.toml
    ├── Dockerfile         # con huecos marcados
    ├── .dockerignore      # con .venv
    └── bitacora.md
```

`codigo/python/certificaciones.md` (tarea 1, espejo en `estudiantes/$GHUSER/python/`).
Fila nueva en `codigo/README.md`.

Si `ambientes/` vive dentro de `09_python/`, el ritual `cp -r` lo copia y el
`git add` lo sube: la ficha lo pone en `prohibidos` **o** se mueve fuera de lo
que sube el ritual. Se decide en la revisión adversarial de `crear_tarea`.

## 7 · Las tareas

### T1 · `tarea-09-datacamp-python` → `python/`

- Curso: <https://app.datacamp.com/learn/courses/introduction-to-python-for-developers>
- Entrega: `certificaciones.md` (fecha `AAAA-MM-DD` + URL del Statement of
  Accomplishment) + captura `introduccion-python-developers.png` (nombre y
  100 % visibles, ≥ 5000 bytes).
- Ficha: secciones con `pide = ["fecha-iso", "url"]`.

### T2 · `tarea-09-uv-docker` → `09_python/`

Una app que reporta su propio ambiente, corrida en local con `uv run` y
dentro de un contenedor, publicada en Docker Hub.

- `reporte.py`: tabla `rich` con versión de Python, ruta del intérprete,
  `sys.prefix`, ¿ambiente?, paquetes y versiones. El alumno agrega **una fila
  propia**.
- `pyproject.toml` + `uv.lock` generados con uv, con `rich` y **un paquete que
  el alumno elige** y usa en su fila.
- `Dockerfile`: base `python:3.13-slim`, binario de uv, copia
  `pyproject.toml` y `uv.lock` antes del código, `uv sync --locked`,
  `CMD` con `uv run reporte.py`.
- `.dockerignore` con `.venv`.
- `bitacora.md`: salida local, salida en el contenedor, **qué cambió y qué no**
  (las versiones de paquetes coinciden por el lock; la ruta del intérprete y
  `sys.prefix` no), URL pública `hub.docker.com/r/...`, digest, y la prueba de
  pull (`docker rmi -f` → `docker run` con *Unable to find image locally*).
- No se entrega: `.venv/`, `__pycache__/` (ya son basura en
  `revisa_entrega.py`), tars de imagen, salida de `docker login`.
- `debe_explicar`: por qué `.venv` no se copia a la imagen; qué fija `uv.lock`
  y qué `pyproject.toml`; por qué el lock se copia antes que el código; qué hace
  `--locked` si el lock no coincide; por qué las versiones coinciden dentro y
  fuera pero la ruta del intérprete no.
- Apple Silicon: `--platform linux/amd64` (igual que la unidad 8).

Ambas siguen las seis piezas de `crear_tarea`: ficha, YAML oficial en
`course/9_python/_official/assignments/`, plantilla, `TAREAS`, tablero
(página B) y tests en `tools/test_revisa_ficha.py`, más la revisión
adversarial con tres agentes.

## 8 · Lo que cambia fuera de la unidad

- Calendario: `session-13` (S5) el 2026-10-01 19:00–20:00, `page: python` (o
  `ambientes-python`). Las fechas de entrega **no** se escriben: las deriva el
  YAML.
- Segunda excepción de 60 min: actualizar `course/0_index.md`, `README.md` y
  `CLAUDE.md` (que hoy dicen que `session-10` es la única excepción).
- `course/1_introduccion/1_el_curso/0_index.md`: la fila 13 «Gestión de
  dependencias» ya describe esto; revisar que la tabla siga siendo cierta.
- `CLAUDE.md`: agregar `python`/`ambientes-python` a la lista de `page`s del
  calendario y `gen_python.py` a la lista de generadores.

## 9 · Verificación

- `python3 -m pytest tools/ -q` (incluye `test_gen_python.py`,
  `test_creditos.py`, `test_revisa_ficha.py`).
- `raya validate` y `raya build` desde `~/itam/raya_lucaria`.
- Correr de verdad cada comando de los labs (uv, venv, Docker) y pegar salidas
  reales, no inventadas; versiones de uv/Python de la fecha.
- Construir la imagen de la plantilla resuelta en local para confirmar que el
  Dockerfile funciona antes de publicar los huecos.

## Fuentes (estado de las herramientas, 2026)

- <https://pydevtools.com/handbook/explanation/which-python-package-manager-should-i-use/>
- <https://cuttlesoft.com/blog/2026/01/27/python-dependency-management-in-2026/>
- <https://openai.com/index/openai-to-acquire-astral/>
- <https://docs.astral.sh/uv/concepts/projects/export/>
