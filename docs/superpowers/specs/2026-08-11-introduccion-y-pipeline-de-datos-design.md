---
id: fdd-o26-introduccion-pipeline-design
title: FDD O26 — Introducción y Pipeline de Datos
status: aprobado
workflow: superpowers
created: 2026-08-11
---
# FDD O26 — Introducción y Pipeline de Datos

## Problema

`fdd_o26` existe como repositorio vacío (`git@github.com:raya-lucaria/fdd_o26.git`,
un README y un `.gitignore`). El curso arranca el **martes 11 de agosto de 2026** y
necesita, antes de esa fecha, un sitio desplegado con las dos primeras unidades y el
calendario del semestre.

El material de origen es `~/itam/fdd_p26`, construido sobre `uu_framework` (Eleventy +
preprocesamiento en Python). El destino es **Raya Lucaria**, que tiene otro contrato de
fuente. No es una copia: es una adaptación, y las dos unidades se mejoran en el camino.

`~/itam/ia_o26` es el curso de referencia — misma estructura, mismo despliegue, mismo
pipeline de imágenes.

## Alcance

**Dentro:**

- Andamiaje completo del repositorio de curso (`raya.yaml`, `skins/`, `tools/`, CI).
- Unidad 1: **Introducción** — de qué va el curso, temario, evaluación, link al repo.
- Unidad 2: **Pipeline de Datos** — adaptada y mejorada desde el deck de 33 slides de p26.
- Calendario nativo del semestre Otoño 2026 (33 fechas, martes y jueves 19:00–20:30).
- Dos tareas reales con entrega para la segunda clase.
- Despliegue verificado en GitHub Pages.

**Fuera:** terminal, bash, regex, git, y el resto del temario. Migración de
`estudiantes/`, `exams/`, `codigo/`. Adopción del calendario nuevo en `ia_o26`
(el merge la habilita, pero es trabajo aparte).

## Prerrequisito de framework

El calendario nativo está implementado en `~/itam/raya_lucaria` en la rama
`feature/native-course-calendar` (18 commits, `b0ec778`, worktree
`.worktrees/native-course-calendar`). **No está mergeado a `main` ni pusheado a
`origin`.**

Esto bloquea todo lo demás porque el reusable workflow hace:

```yaml
- uses: actions/checkout@…
  with:
    repository: ${{ job.workflow_repository }}
    ref: ${{ job.workflow_sha }}
    path: .raya-framework
- run: uv sync --directory .raya-framework --locked …
```

El SHA que se fija en `pages.yml` **es** la versión del framework que construye el
sitio. Con el `6b8b29b` actual (main de hoy), `course/_official/calendar/` no existe
como familia válida y `raya validate` falla.

Orden obligatorio:

1. Mergear `feature/native-course-calendar` → `main` en `raya_lucaria`.
2. `git push origin main` a `raya-lucaria/raya-lucaria.github.io`.
3. Anotar el SHA nuevo de `main` y fijarlo en `pages.yml` de `fdd_o26`.

## Estructura del repositorio

```
fdd_o26/
├── raya.yaml
├── .env                                    OPENAI_API_KEY (gitignored)
├── .gitignore                              se le añaden artifact/ y .env
├── CLAUDE.md
├── calesc2026.pdf                          calendario escolar ITAM 2026
├── skins/
│   └── fdd-eva.yaml
├── tools/
│   ├── ilustraciones.json                  catálogo de prompts de imagen
│   ├── gen_ilustraciones.py                gpt-image-2
│   ├── gen_diagramas.py                    SVG deterministas
│   ├── test_creditos.py                    guarda: toda imagen tiene fila en CREDITOS.md
│   └── test_diagramas.py                   guarda: cada SVG == lo que su generador produce hoy
├── docs/superpowers/specs/                 este documento
├── .github/workflows/pages.yml
└── course/
    ├── 0_index.md                          id: course-root
    ├── _official/
    │   └── calendar/
    │       └── 1_2026-o26.yaml
    ├── 1_introduccion/
    │   ├── 0_index.md
    │   └── 1_el_curso/
    │       ├── 0_index.md
    │       └── _official/
    │           └── assignments/
    │               ├── 1_cuentas.yaml
    │               └── 2_ai_assisted_coding.yaml
    └── 2_pipeline_de_datos/
        ├── 0_index.md
        ├── 1_conceptos.md
        ├── 2_etl.md
        ├── 3_eda.md
        ├── 4_posiciones.md
        ├── 5_presentacion.md
        ├── _assets/
        │   ├── CREDITOS.md
        │   ├── 01_pipeline_de_datos.pdf
        │   ├── ilus-*.jpg
        │   └── d-*.svg
        └── _official/
            ├── cards/
            ├── quizzes/
            └── prompts/
```

`artifact/` es salida generada y va gitignorado. Nunca se edita a mano.

### `raya.yaml`

```yaml
course_id: fdd_o26
title: "Fuentes de Datos — Otoño 2026 (ITAM)"
description: "Curso de Fuentes de Datos del ITAM, Otoño 2026."
language: "es"
source: course
artifact: artifact
calendar:
  timezone: America/Mexico_City
render:
  skin: fdd-eva
  numbered_objects:
    numbering: page-hierarchy
    sequences:
      figure: { label: "Figura", style: caption }
      table: { label: "Tabla", style: caption }
    families:
      figure: { sequence: figure, label: "Figura" }
      table: { sequence: table, label: "Tabla" }
```

### Skin

`skins/fdd-eva.yaml`, derivada del tema `eva01` oscuro que usaba fdd_p26 — misma
familia visual que ia_o26 pero paleta distinta, para que las dos materias se
distingan de un vistazo. `raya validate` comprueba contraste automáticamente; el
diseño no se da por bueno hasta que esa validación pasa.

## Contrato de autoría (lo que muerde)

Reglas de Raya que difieren de uu_framework y que rigen toda la conversión:

- **Prefijos numéricos = orden de autoría solamente.** Se eliminan de URLs,
  etiquetas e IDs estables. Renumerar no puede romper nada.
- **Identidad durable = `id` de frontmatter**, no el nombre de archivo.
- **Todo directorio renderizado necesita `0_index.md`.**
- **Frontmatter compacto:** `id`, `title`, `nav_title`, `summary`, `status`, y
  opcionalmente `estimated_time`, `tags`, `prerequisites`, `aliases`.
- **Enlaces internos** con wikilinks `[[id]]` / `[[id|etiqueta]]` o `raya:<id>`.
  Un wikilink ambiguo o roto falla la validación.
- **`_assets/` sustituye a `images/`.** Una página solo puede enlazar a su propio
  `_assets/` o al de un ancestro.
- **Figuras numeradas** van en directiva: `::: figure {#id title="…"}` … `:::`.
  Un `![]()` pelón se renderiza sin pie "Figura N".
- **HTML crudo está desactivado** (`MarkdownIt("commonmark", {"html": False})`).
  No hay `<iframe>`, `<div>` ni `<details>`.
- **Objetos oficiales** son YAML bajo `_official/<familia>/`. Familias válidas:
  `assignments`, `cards`, `exams`, `examples`, `projects`, `prompts`, `quizzes`,
  `tasks`. Un objeto colocado junto a su quantum puede omitir `scope.quantum`
  (se infiere); uno bajo `course/_official/` **debe** declararlo.

## Calendario

Fuente: `calesc2026.pdf` (calendario escolar de licenciaturas del ITAM 2026, ya
presente en `~/itam/ia_o26`). Se copia a la raíz de `fdd_o26` como respaldo de las
fechas.

Semestre Otoño 2026: **inicio de cursos lun 10 ago**, **fin de cursos mié 2 dic**,
exámenes finales del 7 al 19 de diciembre.

Clase: **martes y jueves, 19:00–20:30**. Eso da **33 slots**, de los cuales uno cae
en día no hábil:

- **Jue 17 sep** — descanso obligatorio del ITAM → `kind: cancellation`.
- Mié 16 sep (asueto), lun 2 nov (asueto) y lun 16 nov (descanso obligatorio) caen
  en días sin clase de esta materia; no generan evento.

Total: **32 sesiones**, del mar 11 ago al mar 1 dic.

### `course/_official/calendar/1_2026-o26.yaml`

Documento de familia calendario — se descubre aparte de los objetos oficiales
y no aparece en `data/official.json`.

```yaml
id: fdd-o26-calendar
type: calendar
authority: official
scope:
  quantum: course-root
events:
  - id: session-01
    kind: session
    date: "2026-08-11"
    start_time: "19:00"
    end_time: "20:30"
    title: Introducción
    page: el-curso
  - id: session-02
    kind: session
    date: "2026-08-13"
    start_time: "19:00"
    end_time: "20:30"
    title: Pipeline de Datos
    page: pipeline-de-datos
  # … sesiones 03–32
  - id: descanso-obligatorio-septiembre
    kind: cancellation
    date: "2026-09-17"
    title: Descanso obligatorio — no hay clase
    summary: El jueves 17 de septiembre no hay sesión de Fuentes de Datos.
  - id: inicio-de-cursos
    kind: milestone
    date: "2026-08-10"
    title: Inicio de cursos
  - id: fin-de-cursos
    kind: milestone
    date: "2026-12-02"
    title: Fin de cursos
  - id: examenes-finales
    kind: milestone
    date: "2026-12-07"
    title: Período de exámenes finales
    summary: Del 7 al 19 de diciembre.
```

### Sesiones y temas provisionales

Los temas vienen del temario de p26 (33 clases → 32 sesiones; se recorta uno de los
cuatro slots "por determinar"). Son provisionales por decisión explícita: el temario
se va a ajustar, pero el calendario debe estar completo desde el día uno.

| # | Fecha | Tema |
|--:|---|---|
| 1 | mar 11 ago | Introducción |
| 2 | jue 13 ago | Pipeline de Datos |
| 3 | mar 18 ago | Sistemas Operativos |
| 4 | jue 20 ago | Terminal |
| 5 | mar 25 ago | Bash & Shell |
| 6 | jue 27 ago | Regex |
| 7 | mar 1 sep | Git |
| 8 | jue 3 sep | GitHub |
| 9 | mar 8 sep | Docker I |
| 10 | jue 10 sep | Docker II |
| 11 | mar 15 sep | Python Basics |
| — | **jue 17 sep** | **Sin clase — descanso obligatorio** |
| 12 | mar 22 sep | IDEs |
| 13 | jue 24 sep | Gestión de dependencias (uv) |
| 14 | mar 29 sep | Memoria y referencias |
| 15 | jue 1 oct | Pydantic |
| 16 | mar 6 oct | Patrones funcionales |
| 17 | jue 8 oct | Metaprogramación |
| 18 | mar 13 oct | Logging |
| 19 | jue 15 oct | Configuración |
| 20 | mar 20 oct | Arquitectura de software |
| 21 | jue 22 oct | Testing |
| 22 | mar 27 oct | Despliegue |
| 23 | jue 29 oct | Arquitectura de computadoras |
| 24 | mar 3 nov | Concurrencia I |
| 25 | jue 5 nov | Concurrencia II |
| 26 | mar 10 nov | Concurrencia III |
| 27 | jue 12 nov | Arquitectura de sistemas I |
| 28 | mar 17 nov | Arquitectura de sistemas II |
| 29 | jue 19 nov | Arquitectura de sistemas III |
| 30 | mar 24 nov | Por determinar |
| 31 | jue 26 nov | Por determinar |
| 32 | mar 1 dic | Cierre y proyecto final |

### Derivación automática

Todo objeto oficial validado con `content.due` o `content.available` produce su
propia entrada de calendario. **Las tareas se escriben una sola vez**, como
`assignment`; no se duplican como eventos.

## Contenido

### `course/0_index.md` — raíz

`id: course-root`. Portada con:

- Horario: martes y jueves, 19:00–20:30.
- **Link al repositorio del curso**: `https://github.com/raya-lucaria/fdd_o26`.
- Fechas académicas que afectan al curso (inicio, el jueves cancelado, fin de
  cursos, finales).
- Contacto.

### `1_introduccion/1_el_curso/0_index.md`

`id: el-curso`. Sigue el patrón de `ia_o26/course/1_introduccion/1_el_curso/`:

- **De qué va el curso** — prosa breve.
- **Temario** — las cinco fases del temario de p26 en tabla, marcadas como
  provisionales.
- **Evaluación** — la tabla acordada, más la explicación del componente del 20 %:

  | Peso | Componente |
  |---:|---|
  | 30 % | Proyecto final |
  | 20 % | **El mínimo** entre el promedio de tareas y el promedio de controles |
  | 10 % | Examen parcial 1 |
  | 10 % | Examen parcial 2 |
  | 10 % | Proyecto 1 |
  | 10 % | Proyecto 2 |
  | 10 % | Participación |

  Ese 20 % **no es el promedio de las dos cosas: es la menor de las dos.** Con 9 en
  tareas y 6 en controles, el componente se calcula sobre 6. Las tareas se hacen con
  tiempo y con ayuda; los controles se responden solo y en el momento. Cuando una
  nota es muy superior a la otra, casi siempre significa que el trabajo se entregó
  pero no se entendió, o que se entendió pero no se practicó.

- **Dónde vive todo** — el repositorio, el sitio, cómo se entregan las tareas.

### `2_pipeline_de_datos/` — cinco páginas

Adaptada del deck `clase/02_pipeline_de_datos/01_pipeline_de_datos.pdf` (33 slides).
El contenido conceptual se conserva; la organización, los diagramas y la prosa se
rehacen.

| Página | `id` | Contenido | Origen en el deck |
|---|---|---|---|
| `0_index.md` | `pipeline-de-datos` | Qué es un pipeline. El flujo de 9 pasos, de la generación al consumo. Las cuatro etapas (ETL, EDA, entrenamiento, producción). Advertencia: son abstracciones, y el proceso no es lineal. | slides 2, 4, 5 |
| `1_conceptos.md` | `conceptos-de-datos` | Datalake, base de datos, data warehouse. Pre-procesamiento vs procesamiento (la distinción es si afecta supuestos estadísticos). Algoritmo vs modelo. | slide 3 |
| `2_etl.md` | `etl` | Extract (fuentes, conectividad, validación, metadatos), Transform (estandarización, nulos, duplicados, atípicos), Load. Datos tabulares y tidy data. | slides 11–16 |
| `3_eda.md` | `eda` | Qué es el EDA y qué se busca. Calidad de datos en seis dimensiones. Viabilidad, conocimiento del negocio, visualización, herramientas. El dato del 60 % del tiempo en limpieza. | slides 6, 17–22 |
| `4_posiciones.md` | `posiciones` | Los roles alrededor de un pipeline: ingeniere de datos, científique de datos, ML engineer, analista, MLOps, DevOps, developer (backend/frontend), PM, product owner. | slides 23–31 |
| `5_presentacion.md` | `presentacion-pipeline` | El deck original, **abrir y descargar**. | — |

Mejoras respecto a p26, explícitas:

- El deck nunca explica la **L de ETL** (pasa de Transform a tidy data). Se escribe.
- Las capturas en inglés y de terceros ("Caricatura Empresarial", StreamSets, la
  gráfica de calidad de datos) se sustituyen por diagramas propios en español.
- El dato de CrowdFlower (60 % del tiempo limpiando) se presenta con su fuente
  citada, no como captura de pantalla de un blog.

## Imágenes

Dos pipelines, según el tipo de imagen. Ninguna imagen del deck original se reusa
tal cual: son arte de plantilla y capturas de terceros sin licencia clara.

### Diagramas — `tools/gen_diagramas.py`

SVG propios y deterministas, en español, con los colores de la skin. El generador es
la fuente de verdad; editar un SVG a mano es un error que la prueba detecta.

1. El flujo de datos de nueve pasos.
2. Las cuatro etapas: ETL → EDA → entrenamiento → producción, con el ciclo de vuelta.
3. Ciclo de vida de un proyecto de datos (siete fases).
4. Tidy data: variables, observaciones, valores.
5. Calidad de datos: seis dimensiones.
6. Distribución del tiempo del científico de datos (60/19/9/3/4/5), como gráfica real.
7. Arquitectura moderna de integración de datos.

### Ilustraciones — `tools/gen_ilustraciones.py`

Adaptado de `ia_o26/tools/gen_ilustraciones.py`: modelo `gpt-image-2`, 1024 px,
JPEG calidad 85, prompts en `tools/ilustraciones.json` con un `estilo` común. Usa
`OPENAI_API_KEY` desde `.env` (`set -a && . ./.env && set +a`), copiado del `.env`
de `ia_o26`.

Cuatro o cinco ilustraciones, una por página, en un estilo propio de FDD —
distinto del violeta/magenta de ia_o26. **Nunca personas reales ni personajes
protegidos**, misma regla que ia_o26.

### Créditos

`_assets/CREDITOS.md` con una fila por archivo: nombre, descripción, autor/origen,
licencia. `tools/test_creditos.py` falla si una imagen del directorio no tiene fila,
y `tools/test_diagramas.py` falla si un SVG dejó de coincidir con lo que su generador
produce hoy. Son las dos únicas guardas que se copian de ia_o26; el resto de su suite
(fuentes verificadas, inventario de Commons, prompts sin personas reales) no aplica
a estas unidades.

## El PDF

`_assets/01_pipeline_de_datos.pdf` (4.2 MB, 33 slides). `5_presentacion.md` lo
ofrece de las dos formas pedidas:

- **Abrir** — link normal al asset, que el navegador muestra en su visor de PDF.
- **Descargar** — el mismo asset, con el peso indicado en el texto para que se sepa
  qué se está bajando.

**No hay iframe.** El renderer corre `MarkdownIt("commonmark", {"html": False})` y no
existe directiva de PDF embebido, así que cualquier `<iframe>` se descarta en el
build. Embeberlo de verdad requeriría una propuesta en el framework, fuera de este
alcance.

## Objetos de aprendizaje

Deliberadamente mínimos: la clase es pronto y esto se amplía después sin tocar nada
más.

### Tareas — reales, tomadas de `fdd_p26/clase/a_stack/`

Ambas se entregan **para la siguiente clase**, igual que en p26, donde las dos
vencían el día de la clase 2. Clase 1 = mar 11 ago, clase 2 = jue 13 ago, así que
ambas vencen el **jueves 13 de agosto de 2026**.

`_official/assignments/1_cuentas.yaml` — de `a_stack/01_introduction/01_cuentas.md`
(era `A.1.1`):

```yaml
id: cuentas-llms-datacamp
type: assignment
authority: official
content:
  title: "Crear cuentas: LLMs y DataCamp"
  instructions: >-
    Crea cuentas en las plataformas de LLM y únete al grupo de DataCamp con tu
    correo @itam.mx. Verifica que puedas abrir un curso.
  due: "2026-08-13"
  points: 0
  status: published
  tags: [cuentas, setup]
```

La página de la unidad conserva el detalle real de p26: los links a Gemini (con el
plan gratuito de estudiantes), ChatGPT, Claude, Mistral, Perplexity y DeepSeek; la
verificación de Google Colab; y el **link de invitación al grupo de DataCamp del
ITAM**, con la advertencia de cerrar cualquier otra sesión antes de unirse.

`_official/assignments/2_ai_assisted_coding.yaml` — de
`a_stack/02_llms/01_conceptos_llm.md` (era `A.2.1`):

```yaml
id: ai-assisted-coding
type: assignment
authority: official
content:
  title: "Curso: AI Assisted Coding for Developers"
  instructions: >-
    Completa las dos primeras unidades del curso de DataCamp — "Unlocking the
    Power of AI in Code" y "Prompt Engineering for Real-World Coding Tasks". La
    evidencia se sube más adelante, al cerrar el módulo de Git; el curso hay que
    hacerlo ahora porque se usa en las tareas siguientes.
  due: "2026-08-13"
  points: 20
  status: published
  tags: [datacamp, llms]
```

Las dos aparecen en el calendario **por derivación**, no como eventos escritos a mano.

### Repaso

- **~6 cards** (`_official/cards/`): datalake vs base de datos vs data warehouse;
  pre-procesamiento vs procesamiento; algoritmo vs modelo; ETL vs EDA; qué hace
  tidy a una tabla; ingeniere de datos vs científique de datos.
- **1 quiz** (`_official/quizzes/`) de la unidad de pipeline.
- **2 prompts** de discusión (`_official/prompts/`): por qué el 60 % del tiempo se
  va en limpiar, y qué se pierde al tratar un proceso cíclico como si fuera lineal.

## CI y despliegue

`.github/workflows/pages.yml`, siguiendo a ia_o26. El job `checks` corre las dos
guardas de `tools/`, mucho más ligeras que las 56 pruebas de ia_o26:

```yaml
name: Verify and publish course
on: [push, pull_request]
permissions: { contents: read, pages: write, id-token: write }
concurrency: { group: pages, cancel-in-progress: true }
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with: { python-version: "3.12" }
      - run: pip install pytest pillow pyyaml
      - run: python -m pytest tools/ -q
  course-pages:
    needs: checks
    uses: raya-lucaria/raya-lucaria.github.io/.github/workflows/reusable-course-pages.yml@<SHA-NUEVO>
    with: { course_path: . }
    permissions: { contents: read, pages: write, id-token: write }
```

`needs: checks` es lo que convierte la prueba en compuerta real; sin esa línea los
dos jobs corren en paralelo y el sitio se publica aunque la suite falle.

URL resultante: `https://raya-lucaria.github.io/fdd_o26/`.

## Verificación

Local, desde `~/itam/raya_lucaria` (o su worktree del calendario hasta que el merge
aterrice):

```bash
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate /home/uumami/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build    /home/uumami/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya preview  /home/uumami/itam/fdd_o26
```

Desde `~/itam/fdd_o26`:

```bash
python3 -m pytest tools/ -q
```

El trabajo está hecho cuando:

1. `raya validate` pasa sin errores, incluida la validación de contraste de la skin.
2. `raya build` genera `artifact/data/calendar.json` con 32 sesiones, 1 cancelación,
   3 milestones y las 2 tareas derivadas.
3. `raya preview` muestra el Calendar con el jueves 17 de septiembre marcado como
   sin clase, y las dos tareas el 13 de agosto.
4. `python3 -m pytest tools/ -q` pasa: toda imagen tiene fila de créditos y todo SVG
   coincide con lo que su generador produce hoy.
5. El sitio carga en `https://raya-lucaria.github.io/fdd_o26/`, con el link al
   repositorio visible en la portada y el PDF descargable desde la unidad de pipeline.

## Riesgos

- **El merge del calendario puede traer regresiones.** Son 18 commits sobre `main`.
  Antes de pushear hay que correr `./scripts/check.sh` en `raya_lucaria`. Si el merge
  se complica, el contenido de las dos unidades se puede escribir igual — lo único
  que se pospone es el calendario.
- **El deck es de enero de 2026 y cita datos sin fecha de corte** (la encuesta de
  CrowdFlower no lleva año en el slide). Al reescribir se cita la fuente con su
  fecha, o se marca como ilustrativo.
- **`gpt-image-2` es no determinista.** Las ilustraciones se generan una vez, se
  revisan a ojo y se commitean; no se regeneran en CI.
