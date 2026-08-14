# Rediseño de la unidad Pipeline de Datos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Volver la unidad «Pipeline de datos» legible para alguien sin contexto previo — vocabulario definido antes de usarse, un solo caso que atraviesa las siete páginas, diagramas legibles en celular, e ilustraciones en un registro visual unificado — corrigiendo de paso cinco errores técnicos, uno de ellos calificado y en producción.

**Architecture:** El contenido es Markdown validado por el CLI `raya`, que vive en otro repositorio. El trabajo se reparte en tres capas: (1) dos arreglos en el framework, que deben desplegarse primero porque el sitio se construye con el SHA fijado en `pages.yml`; (2) una reestructuración de las siete páginas a directorios, para que cada una pueda llevar su propia evaluación; (3) las correcciones y reescrituras de contenido, todas sobre las rutas finales. Se añaden tres guardas nuevas en `tools/` para que las reglas del spec —vocabulario definido antes de usarse, presupuesto de palabras, texto corto dentro de los SVG— sean ejecutables y no intenciones.

**Tech Stack:** Python 3.12 (`pytest`, `Pillow`), `uv`, el CLI `raya` (paquetes `raya_schema` y `raya_static`), Markdown con directivas `:::`, YAML para objetos oficiales, SVG escrito a mano, API de imágenes de OpenAI (`gpt-image-2`), GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-08-13-pipeline-de-datos-rediseno-design.md`

## Global Constraints

- **Dos repositorios.** El contenido vive en `~/itam/fdd_o26`. El framework vive en `~/itam/raya_lucaria/.worktrees/native-course-calendar`, rama `feature/native-course-calendar`. Nunca mezclar cambios de los dos en un commit.
- **`raya` se invoca desde el repo del framework, con la ruta del curso como argumento:**
  `cd ~/itam/raya_lucaria/.worktrees/native-course-calendar && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26`
- **HTML crudo desactivado** (`MarkdownIt("commonmark", {"html": False})`, `rendering.py:105`). Nada de `<iframe>`, `<div>`, `<details>`, `<br>`.
- **`@nombre` es referencia a objeto numerado.** Un `@algo` suelto en prosa rompe el build. Los correos van en `` `code spans` ``.
- **Valores de frontmatter que contengan `:` van entre comillas.** Ya rompió el build una vez.
- **`.env` contiene `OPENAI_API_KEY` y está gitignorado. Nunca se commitea.** Verificar con `git check-ignore .env artifact/` antes de cada push.
- **El repositorio `raya-lucaria/fdd_o26` debe seguir siendo público**, o GitHub Pages falla en el plan de esta organización.
- **Los prompts de ilustración nunca piden personas reales ni personajes con derechos.**
- **Presupuesto de palabras de la unidad: ≤ 8 800**, contando prosa de página (no YAML).
- **Máximo 4 definiciones por página.**
- **Los ocho slugs de diagrama son fijos**: `d-dag`, `d-schema`, `d-etl-elt`, `d-tidy`, `d-calidad`, `d-idempotencia`, `d-tiempo`, `d-ciclo`. No se añade un noveno.
- **Idioma del curso: español.** Cualquier etiqueta visible al alumno va en español.

## File Structure

**Repo framework** (`~/itam/raya_lucaria/.worktrees/native-course-calendar`)

| Archivo | Responsabilidad |
|---|---|
| `packages/static/src/raya_static/rendering.py` | Etiqueta de callout localizada; CSS de blockquote en pantalla |
| `packages/static/src/raya_static/builder.py:973` | Pasa el idioma del curso al renderizador |
| `tests/contracts/test_static_builder.py` | Contrato: callout en español y regresión en inglés |

**Repo curso** (`~/itam/fdd_o26`)

| Archivo | Responsabilidad |
|---|---|
| `.github/workflows/pages.yml:34` | SHA del framework con el que se construye el sitio |
| `raya.yaml` | Declara la familia `definition` con etiqueta en español |
| `course/2_pipeline_de_datos/<n>_<slug>/0_index.md` | Las 7 páginas, ya como directorios |
| `course/2_pipeline_de_datos/<n>_<slug>/_official/` | Tarjetas y quiz de esa página |
| `course/2_pipeline_de_datos/7_glosario/0_index.md` | Glosario de la unidad (página nueva) |
| `course/2_pipeline_de_datos/_assets/` | Diagramas, ilustraciones, PDF y `CREDITOS.md` — no se mueve |
| `tools/gen_diagramas.py` | Única fuente de verdad de los 8 SVG |
| `tools/ilustraciones.json` | Única fuente de verdad de las 7 ilustraciones |
| `tools/test_vocabulario.py` | **Nuevo.** Guarda: cada término se define antes de usarse y está en el glosario |
| `tools/test_presupuesto.py` | **Nuevo.** Guarda: la unidad no pasa de 8 800 palabras |
| `tools/test_diagramas.py` | Guarda existente, más la regla de ≤4 palabras por `<text>` |
| `tools/test_ilustraciones.py` | Guarda existente, con el glob y las prohibiciones corregidos |

---

## Task 1: Framework — callouts en español y blockquotes con forma

Repo: `~/itam/raya_lucaria/.worktrees/native-course-calendar`.

Hoy `_callout_label` fija `Note`/`Tip`/`Warning`/`Caution` en inglés, y la unidad tiene 9 callouts en un curso que declara `language: "es"`. La función contenedora en `builder.py:903` ya recibe `language: str`, así que el cableado es de una línea.

**Files:**
- Modify: `packages/static/src/raya_static/rendering.py` (líneas 90-99, 313, 471-484, 8150-8156, y CSS antes de `.raya-callout {` en 6152)
- Modify: `packages/static/src/raya_static/builder.py:973`
- Test: `tests/contracts/test_static_builder.py`

**Interfaces:**
- Consumes: nada de tareas anteriores.
- Produces: un SHA de commit en `raya-lucaria/raya-lucaria.github.io` que la Task 2 fija en `pages.yml`.

- [ ] **Step 1: Escribir las dos pruebas que fallan**

Al final de `tests/contracts/test_static_builder.py`:

```python
def test_callout_label_uses_course_language(tmp_path: Path) -> None:
    course = _copy_minimal(tmp_path)
    config = course / "raya.yaml"
    config.write_text(
        config.read_text(encoding="utf-8").replace("language: en", "language: es"),
        encoding="utf-8",
    )
    index = course / "course" / "0_index.md"
    index.write_text(
        index.read_text(encoding="utf-8") + "\n\n> [!NOTE]\n> Cuerpo de la nota.\n",
        encoding="utf-8",
    )

    report = build_course(course)

    assert report.ok, [diagnostic.format() for diagnostic in report.diagnostics]
    html = (course / "artifact" / "site" / "index.html").read_text(encoding="utf-8")
    assert '<p class="raya-callout-title">Nota</p>' in html
    assert '<p class="raya-callout-title">Note</p>' not in html


def test_callout_label_defaults_to_english(tmp_path: Path) -> None:
    course = _copy_minimal(tmp_path)
    index = course / "course" / "0_index.md"
    index.write_text(
        index.read_text(encoding="utf-8") + "\n\n> [!WARNING]\n> Body of the warning.\n",
        encoding="utf-8",
    )

    report = build_course(course)

    assert report.ok, [diagnostic.format() for diagnostic in report.diagnostics]
    html = (course / "artifact" / "site" / "index.html").read_text(encoding="utf-8")
    assert '<p class="raya-callout-title">Warning</p>' in html
```

- [ ] **Step 2: Correr las pruebas y confirmar que la primera falla**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run pytest \
  tests/contracts/test_static_builder.py -k callout_label -q
```

Esperado: `test_callout_label_uses_course_language` FALLA (el HTML trae `Note`, no `Nota`). `test_callout_label_defaults_to_english` PASA — es la guarda de regresión.

- [ ] **Step 3: Localizar la etiqueta**

En `rendering.py`, sustituir la función de `:8150`:

```python
_CALLOUT_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "note": "Note",
        "tip": "Tip",
        "warning": "Warning",
        "caution": "Caution",
    },
    "es": {
        "note": "Nota",
        "tip": "Consejo",
        "warning": "Advertencia",
        "caution": "Precaución",
    },
}


def _callout_label(kind: str, language: str = "en") -> str:
    code = (language or "en").split("-")[0].lower()
    return _CALLOUT_LABELS.get(code, _CALLOUT_LABELS["en"])[kind]
```

- [ ] **Step 4: Cablear el idioma hasta el renderizador**

En `rendering.py`, añadir el parámetro a `RichMarkdownRenderer.__init__` (bloque de `:90-99`), como keyword con valor por omisión:

```python
        resolve_wikilink: Callable[[str], str | None] | None = None,
        language: str = "en",
    ) -> None:
        self._resolve_href = resolve_href
        self._language = language
```

En `_render_callout` (`:313`):

```python
        label = _callout_label(callout.kind, self._language)
```

En `render_markdown_body` (`:471-484`), añadir el parámetro y pasarlo:

```python
    resolve_wikilink: Callable[[str], str | None] | None = None,
    language: str = "en",
) -> str:
    return RichMarkdownRenderer(
        resolve_href,
        source_path=source_path,
        report=report,
        math_renderer=math_renderer,
        resolve_wikilink=resolve_wikilink,
        language=language,
    ).render(
```

En `builder.py`, dentro de la llamada que empieza en `:973`, añadir un argumento más (la función que la contiene ya declara `language: str` en `:903`):

```python
        resolve_wikilink=lambda target: _resolve_wikilink_page_id(
            target,
            wikilink_resolver,
        ),
        language=language,
    )
```

- [ ] **Step 5: Correr las pruebas y confirmar que pasan**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run pytest \
  tests/contracts/test_static_builder.py -k callout -q
```

Esperado: PASS en ambas.

- [ ] **Step 6: Añadir el CSS de blockquote en pantalla**

En `rendering.py`, justo **antes** de `.raya-callout {` (`:6152`), después del bloque de tabla que termina en `:6151`:

```css
.raya-main-article blockquote {
  border-left: 0.25rem solid var(--raya-color-accent);
  background: color-mix(in srgb, var(--raya-color-accent) 7%, var(--raya-color-surface));
  border-radius: 0 0.35rem 0.35rem 0;
  margin: 1.25rem 0;
  padding: 0.75rem 1rem;
}
.raya-main-article blockquote > :first-child {
  margin-top: 0;
}
.raya-main-article blockquote > :last-child {
  margin-bottom: 0;
}
```

Nota para quien implemente: ninguna página del curso usa hoy un blockquote suelto —los que hay son cuerpos de callout—, así que este cambio no tiene prueba de contenido. Viaja aquí porque es el mismo archivo, el mismo merge y el mismo SHA.

- [ ] **Step 7: Correr la suite completa del framework**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run pytest tests/contracts -q
```

Esperado: verde. Si algo falla en `test_static_skins.py` o `test_static_read_path.py`, es por el CSS nuevo: revisar que no se haya roto la llave de cierre del bloque anterior.

- [ ] **Step 8: Commit**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
git add packages/static/src/raya_static/rendering.py \
        packages/static/src/raya_static/builder.py \
        tests/contracts/test_static_builder.py
git commit -m "feat(static): etiqueta de callout segun el idioma del curso, y blockquote con forma en pantalla"
```

- [ ] **Step 9: Merge a main y push**

```bash
cd ~/itam/raya_lucaria
git -C .worktrees/native-course-calendar log --oneline -1   # anota el SHA
```

Hacer el merge del branch a `main` **desde el worktree donde `main` esté disponible** — `git checkout main` falla si `main` ya está tomado por otro worktree. Después:

```bash
git push origin main
git rev-parse origin/main    # este es el SHA que va en la Task 2
```

---

## Task 2: Reestructurar las 7 páginas a directorios

Todo el contenido posterior se edita sobre las rutas finales, así que este movimiento va antes que cualquier reescritura.

Un objeto oficial colocado **debe** apuntar a la página índice de su directorio (`packages/schema/src/raya_schema/official.py`, `_resolve_scope`). Hoy las tarjetas y el quiz cuelgan de la raíz de la unidad y solo aparecen en el índice y en `/_raya/practice/`.

**Las URLs no cambian:** `4_cuando_se_rompe.md` y `4_cuando_se_rompe/0_index.md` resuelven ambos a `/pipeline-de-datos/cuando-se-rompe/`. `_assets/` se queda en la raíz de la unidad, que es un ancestro, así que **ninguna ruta de imagen cambia**.

**Files:**
- Modify (git mv): las 7 `course/2_pipeline_de_datos/*.md` → `course/2_pipeline_de_datos/<mismo_nombre>/0_index.md`
- Modify (git mv): `course/2_pipeline_de_datos/_official/{cards,quizzes,prompts}/*` → el directorio de la página que enseña cada tema
- Modify: `tools/test_ilustraciones.py:97`
- Modify: `.github/workflows/pages.yml:34`

**Interfaces:**
- Consumes: el SHA de `origin/main` que produjo la Task 1.
- Produces: la estructura de directorios que consumen todas las tareas siguientes. A partir de aquí, «la página `4_cuando_se_rompe`» significa el archivo `course/2_pipeline_de_datos/4_cuando_se_rompe/0_index.md`.

- [ ] **Step 1: Escribir la prueba que falla**

`tools/test_ilustraciones.py:95-102` recorre las páginas con `PAGINAS.glob("*.md")`, que solo ve el nivel superior. En cuanto las páginas sean directorios, ese glob no encuentra nada y la prueba falla por la razón equivocada. Cambiar la línea 97:

```python
def test_cada_ilustracion_se_usa_en_una_pagina():
    texto = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(PAGINAS.rglob("*.md"))
    )
```

Y añadir al final del mismo archivo la prueba que fija la estructura nueva:

```python
def test_cada_pagina_es_un_directorio_con_indice():
    sueltas = sorted(p.name for p in PAGINAS.glob("*.md"))
    assert not sueltas, f"paginas sin promover a directorio: {sueltas}"
    directorios = sorted(
        d.name for d in PAGINAS.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )
    assert directorios, "la unidad no tiene ninguna pagina"
    for nombre in directorios:
        assert (PAGINAS / nombre / "0_index.md").is_file(), (
            f"{nombre}/ no tiene 0_index.md"
        )
```

- [ ] **Step 2: Correr la prueba y confirmar que falla**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_ilustraciones.py -k directorio -q
```

Esperado: FALLA con `paginas sin promover a directorio: ['0_index.md', '1_el_viaje.md', ...]`.

- [ ] **Step 3: Promover las 7 páginas, una por una**

`0_index.md` es el índice de la unidad y **se queda donde está** — ya es el `0_index.md` de `2_pipeline_de_datos/`. Se mueven las otras seis:

```bash
cd ~/itam/fdd_o26/course/2_pipeline_de_datos
for f in 1_el_viaje 2_etl_elt 3_eda 4_cuando_se_rompe 5_posiciones 6_presentacion; do
  mkdir -p "$f"
  git mv "$f.md" "$f/0_index.md"
done
```

Después de **cada** movimiento, validar:

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Si aparece «missing index page», es que faltó el `0_index.md` de ese directorio.

- [ ] **Step 4: Repartir tarjetas, quiz y prompts a la página que enseña cada tema**

```bash
cd ~/itam/fdd_o26/course/2_pipeline_de_datos
mkdir -p 1_el_viaje/_official/cards 2_etl_elt/_official/cards 4_cuando_se_rompe/_official/cards
git mv _official/cards/1_datalake_bd_warehouse.yaml          1_el_viaje/_official/cards/
git mv _official/cards/2_preprocesamiento_vs_procesamiento.yaml 1_el_viaje/_official/cards/
git mv _official/cards/3_algoritmo_vs_modelo.yaml            1_el_viaje/_official/cards/
git mv _official/cards/4_etl_vs_elt.yaml                     2_etl_elt/_official/cards/
git mv _official/cards/5_tidy_data.yaml                      2_etl_elt/_official/cards/
git mv _official/cards/6_idempotencia.yaml                   4_cuando_se_rompe/_official/cards/
```

Los dos prompts (`1_tiempo_de_limpieza`, `2_proceso_ciclico`) son de reflexión sobre la unidad entera: **se quedan en `_official/prompts/` de la raíz**.

El quiz de 6 preguntas se parte en la Task 10, cuando el contenido final ya existe. Por ahora **se queda en la raíz**.

- [ ] **Step 5: Correr las pruebas y validar**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
```

Esperado: pytest verde, build OK. Verificar que las URLs no cambiaron:

```bash
cd ~/itam/fdd_o26 && find artifact/site -name index.html | sort
```

Esperado: exactamente las mismas 16 rutas de antes.

- [ ] **Step 6: Subir el SHA del framework**

En `.github/workflows/pages.yml:34`, sustituir el SHA fijado por el que devolvió `git rev-parse origin/main` en la Task 1, Step 9.

- [ ] **Step 7: Commit**

```bash
cd ~/itam/fdd_o26
git add -A course/2_pipeline_de_datos tools/test_ilustraciones.py .github/workflows/pages.yml
git commit -m "refactor(unidad-2): cada pagina es un directorio con su propia evaluacion; sube SHA del framework"
```

---

## Task 3: Los cinco errores técnicos

Independiente del resto. Uno de los cinco está calificado y en producción, así que va temprano.

**Files:**
- Modify: `course/2_pipeline_de_datos/_official/quizzes/1_pipeline.yaml`
- Modify: `course/2_pipeline_de_datos/4_cuando_se_rompe/0_index.md`
- Modify: `course/2_pipeline_de_datos/2_etl_elt/0_index.md`
- Modify: `course/2_pipeline_de_datos/2_etl_elt/_official/cards/5_tidy_data.yaml`
- Modify: `course/2_pipeline_de_datos/0_index.md`

**Interfaces:**
- Consumes: la estructura de directorios de la Task 2.
- Produces: nada que otras tareas consuman.

- [ ] **Step 1: Corregir el distractor del quiz**

En `_official/quizzes/1_pipeline.yaml`, pregunta `dag-no-lineal`. La segunda opción dice hoy:

> Porque el término DAG es el nombre técnico correcto de cualquier secuencia de pasos, aunque sea estrictamente lineal

Eso es **verdadero** —una cadena lineal de pasos con dependencias dirigidas y sin ciclos es un DAG— y está marcado `correct: false`. Sustituir por un distractor que sí sea falso:

```yaml
        - label: >-
            Porque el nombre DAG exige que el pipeline tenga al menos dos ramas
            en paralelo: una sola cadena de pasos encadenados no calificaría
          correct: false
```

- [ ] **Step 2: Sacar CDC de la tabla de regímenes temporales**

En `4_cuando_se_rompe/0_index.md`, la tabla de `:88-93` lista CDC como cuarto régimen con latencia de milisegundos. CDC es una **técnica de captura**, no un régimen: se entrega por batch o por streaming. Dejar la tabla con tres filas:

```markdown
| Régimen | Latencia | Su mentira | Cuándo conviene |
|---|---|---|---|
| **Batch** | Horas o un día | Que el mundo se detiene a medianoche: hay devoluciones el día 5 que corrigen el 4 | Lo más simple y barato; basta casi siempre |
| **Micro-batch** | Minutos | La misma, más pequeña | Casi tiempo real con casi la simplicidad del batch |
| **Streaming** | Segundos | Que los eventos llegan en orden. No lo hacen | Cuando la decisión ocurre en el momento |
```

Y en la subsección «Streaming y CDC, con más detalle», reemplazar el párrafo de CDC (`:99`) por:

```markdown
**CDC no es un cuarto régimen: es una forma de *capturar* los cambios**, y lo
capturado se entrega por batch o por streaming, según convenga. En vez de
consultar la base origen, lee su registro de transacciones. Así detecta la fila
vieja que alguien editó ayer, que no tiene fecha de creación nueva pero sí
aparece en el log. A cambio, **acopla tu pipeline a los detalles internos del
origen**.
```

Actualizar también la fila correspondiente del «mapa de las seis fallas» (`:32`) para que no presente CDC como una opción de régimen:

```markdown
| «El dato de ahora» significa cosas distintas | Régimen temporal mal elegido | **Batch, micro-batch o streaming** según la decisión |
```

- [ ] **Step 3: Borrar la afirmación falsa sobre Parquet**

En `4_cuando_se_rompe/0_index.md:138`, la viñeta dice «en Parquet, tres columnas de cien es el 3 % de los bytes». En columnar los bytes dependen del ancho del tipo, de la codificación y de la compresión, no del conteo de columnas. Sustituir:

```markdown
- **Seleccionar columnas** en vez de `SELECT *`: un formato columnar solo lee
  las columnas que pediste, y las demás ni se tocan.
```

- [ ] **Step 4: Bajar la afirmación sobre tidy data**

En `2_etl_elt/0_index.md:24`, la viñeta de «En corto» dice «El objetivo de la transformación tiene nombre: **tidy data**». Sustituir:

```markdown
- Para análisis tabular, la forma que se busca tiene nombre: **tidy data**.
```

En `2_etl_elt/_official/cards/5_tidy_data.yaml`, la última frase del `back` dice «Es el objetivo de la T de ETL.» Sustituir por:

```yaml
    esperan las herramientas de análisis y graficado, así que ordenar una vez
    ahorra reacomodos en cada paso posterior. Es la forma que busca la T cuando
    el destino es análisis tabular; cuando el destino es un warehouse, la T
    suele apuntar a un modelo dimensional — hechos y dimensiones.
```

En `2_etl_elt/0_index.md`, al final de la sección «Tidy data», añadir la frase que nombra lo que `d-dag.svg` ya dibuja («Dimensión producto», «Tabla de hechos») sin abrir el tema:

```markdown
Tidy no es la única forma de destino. Cuando lo que se alimenta es un warehouse,
la transformación suele apuntar a un **modelo dimensional**: una tabla de hechos
con las métricas y varias tablas de dimensión con sus atributos. Es lo que dibuja
@dag a la derecha, y se ve a fondo más adelante en el curso.
```

- [ ] **Step 5: Corregir el tiempo estimado del índice**

En `course/2_pipeline_de_datos/0_index.md`, frontmatter: `estimated_time: 60m` → `estimated_time: 6m`. Hoy el índice declara el tiempo de la unidad entera y los hijos vuelven a contarse, así que el lector suma 127 minutos.

- [ ] **Step 6: Validar y construir**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Esperado: todo verde. Si `validate` se queja de `@dag`, es que la referencia al objeto numerado no resuelve desde `2_etl_elt` — en ese caso usar el wikilink `[[pipeline-de-datos]]` en vez de `@dag`.

- [ ] **Step 7: Commit**

```bash
cd ~/itam/fdd_o26
git add course/2_pipeline_de_datos
git commit -m "fix(unidad-2): distractor del quiz, CDC como tecnica de captura, Parquet, tidy data y tiempo estimado"
```

---

## Task 4: Declarar la familia `definition` en español

El framework ya trae `definition` como familia de objeto numerado (`packages/schema/src/raya_schema/numbered_objects.py:31`), con etiqueta `"Definition"` en inglés y secuencia compartida con `theorem`. Se le da secuencia propia y etiqueta en español desde el curso, sin tocar el framework.

**Files:**
- Modify: `raya.yaml`
- Test: verificación por build

**Interfaces:**
- Consumes: nada.
- Produces: la directiva `::: definition {#id title="Término"}`, que renderiza como «Definición N.M — Término» y es referenciable con `@id`. Las Tasks 5 y 10 la usan.

- [ ] **Step 1: Añadir secuencia y familia**

En `raya.yaml`, dentro de `render.numbered_objects`:

```yaml
render:
  skin: fdd-eva
  numbered_objects:
    numbering: page-hierarchy
    sequences:
      figure: { label: "Figura", style: caption }
      table: { label: "Tabla", style: caption }
      definicion: { label: "Definición", style: scannable }
    families:
      figure: { sequence: figure, label: "Figura" }
      table: { sequence: table, label: "Tabla" }
      definition: { sequence: definicion, label: "Definición" }
```

`scannable` es uno de los cinco estilos válidos (`numbered_objects.py:46`): `scannable`, `margin`, `banded`, `caption`, `equation`.

- [ ] **Step 2: Escribir una definición de prueba**

Al final de `course/2_pipeline_de_datos/0_index.md`, temporalmente:

```markdown
::: definition {#def-humo title="Prueba de humo"}
Esta definición existe solo para verificar que la familia quedó declarada.

Se borra en el paso 4.
:::
```

- [ ] **Step 3: Construir y verificar el render**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
grep -o 'raya-numbered-object--definition' \
  ~/itam/fdd_o26/artifact/site/pipeline-de-datos/index.html | head -1
grep -o 'Definición [0-9.]*' \
  ~/itam/fdd_o26/artifact/site/pipeline-de-datos/index.html | head -1
```

Esperado: la primera devuelve `raya-numbered-object--definition`; la segunda, algo como `Definición 2.1`. Si sale `Definition`, la familia no tomó la etiqueta: revisar la indentación del YAML.

- [ ] **Step 4: Borrar la definición de humo y commitear**

```bash
cd ~/itam/fdd_o26
# borrar a mano el bloque ::: definition {#def-humo ...} de 0_index.md
git add raya.yaml
git commit -m "feat(unidad-2): declara la familia definition con etiqueta en espanol"
```

---

## Task 5: Las 14 definiciones y el glosario

**Files:**
- Create: `tools/test_vocabulario.py`
- Create: `course/2_pipeline_de_datos/7_glosario/0_index.md`
- Modify: las 5 páginas que reciben definiciones

**Interfaces:**
- Consumes: la directiva `::: definition` de la Task 4; las rutas de directorio de la Task 2.
- Produces: 14 objetos numerados con `id` de la forma `def-<slug>`, referenciables con `@def-<slug>` desde cualquier página posterior. La Task 10 los usa en las tarjetas.

- [ ] **Step 1: Escribir la guarda que falla**

Crear `tools/test_vocabulario.py`:

```python
"""Guarda: cada termino del catalogo se define antes de usarse y esta en el glosario.

La regla del spec es que una definicion solo puede usar vocabulario ya definido,
y que ninguna pagina puede usar un termino que se define mas adelante. El orden
de las paginas lo da el prefijo numerico del directorio.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/2_pipeline_de_datos"
GLOSARIO = UNIDAD / "7_glosario/0_index.md"

# id de la definicion -> patron que delata su uso en prosa.
TERMINOS = {
    "def-tabla": r"\bfilas?\b|\bcolumnas?\b",
    "def-llave": r"\bllaves?\b",
    "def-join": r"`join`|\bjoin\b",
    "def-corrida": r"\bcorridas?\b",
    "def-esquema": r"\besquemas?\b",
    "def-formato-tabla": r"Iceberg|Delta Lake|Hudi",
    "def-particion": r"\bpartici[oó]n|\bparticionar\b",
    "def-parquet": r"\bParquet\b",
    "def-staging": r"\bstaging\b",
    "def-transaccion": r"\btransacci[oó]n|\bat[oó]mica?\b",
    "def-fuga": r"fuga de informaci[oó]n",
    "def-idempotencia": r"\bidempoten",
    "def-sistema-distribuido": r"sistema distribuido",
    "def-materializar": r"\bmaterializar\b|\bmaterializad",
}

APERTURA = re.compile(r"^::: +definition +\{#(?P<id>[A-Za-z][\w-]*)", re.M)


def paginas():
    """Las paginas de la unidad, en el orden en que las lee el alumno."""
    orden = [UNIDAD / "0_index.md"]
    orden += [
        d / "0_index.md"
        for d in sorted(UNIDAD.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    ]
    return [p for p in orden if p.is_file()]


def texto(pagina):
    return pagina.read_text(encoding="utf-8")


def test_cada_termino_tiene_exactamente_una_definicion():
    encontrados = []
    for pagina in paginas():
        encontrados += APERTURA.findall(texto(pagina))
    for termino in TERMINOS:
        assert encontrados.count(termino) == 1, (
            f"{termino} aparece {encontrados.count(termino)} veces; debe ser 1"
        )


def test_ninguna_pagina_pasa_de_cuatro_definiciones():
    for pagina in paginas():
        n = len(APERTURA.findall(texto(pagina)))
        assert n <= 4, f"{pagina.parent.name} tiene {n} definiciones; el tope es 4"


def test_ningun_termino_se_usa_antes_de_definirse():
    indice_definicion = {}
    for i, pagina in enumerate(paginas()):
        for encontrado in APERTURA.findall(texto(pagina)):
            indice_definicion[encontrado] = i

    for termino, patron in TERMINOS.items():
        assert termino in indice_definicion, f"{termino} no se define en ninguna pagina"
        for i, pagina in enumerate(paginas()):
            if pagina.name == "0_index.md" and pagina.parent.name == "7_glosario":
                continue  # el glosario recapitula todo
            if re.search(patron, texto(pagina)) and i < indice_definicion[termino]:
                raise AssertionError(
                    f"{pagina.parent.name} usa '{termino}', que se define despues"
                )


def test_el_glosario_lista_todos_los_terminos():
    assert GLOSARIO.is_file(), "falta 7_glosario/0_index.md"
    cuerpo = texto(GLOSARIO)
    for termino in TERMINOS:
        assert f"@{termino}" in cuerpo, f"el glosario no referencia @{termino}"
```

- [ ] **Step 2: Correr la guarda y confirmar que falla**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_vocabulario.py -q
```

Esperado: FALLA en las cuatro pruebas — no existe ninguna `::: definition` ni el glosario.

- [ ] **Step 3: Escribir las 14 definiciones, en orden de dependencia**

La forma es fija: **una frase de qué es, una frase de qué pasa sin eso**. Regla dura: una definición solo puede usar términos ya definidos.

> **Tres términos no van donde la intuición los pondría.** Se verificó con `grep`
> dónde aparece cada uno por primera vez, y el reparto de abajo ya lo respeta:
>
> - **`Parquet`** se menciona por primera vez en `1_el_viaje` (la lista de
>   formatos del data lake), no en `2_etl_elt`. Su definición va en `1_el_viaje`.
> - **`transacción` / `atómico`** aparecen por primera vez en `1_el_viaje` (las
>   garantías del lakehouse). Su definición va en `1_el_viaje`.
> - **`idempotencia`** aparece en `0_index` y en `2_etl_elt` **antes** de la
>   página que la enseña. Como `0_index` ya llega al tope de 4 definiciones, la
>   solución no es adelantar la definición sino **quitar el término de las dos
>   páginas tempranas** — que es exactamente el defecto que esta tarea corrige.
>   En el Step 3bis se reescriben esas dos menciones.
>
> Resultado: `0_index` 4, `1_el_viaje` 4, `2_etl_elt` 2, `3_eda` 1,
> `4_cuando_se_rompe` 3.

En `course/2_pipeline_de_datos/0_index.md`, sección nueva «Vocabulario mínimo» antes de «No es una flecha, es un grafo»:

```markdown
## Vocabulario mínimo

Cuatro palabras que el resto de la unidad da por sabidas.

::: definition {#def-tabla title="Tabla, fila, columna"}
Una tabla guarda datos en una rejilla: cada **fila** es una cosa registrada —una
venta, un cliente— y cada **columna** es un dato de esa cosa —la fecha, el monto—.

Si una columna guarda dos datos distintos, o una fila mezcla dos cosas, todo lo
que venga después tiene que adivinar.
:::

::: definition {#def-llave title="Llave"}
Una llave es la columna —o el conjunto de columnas— cuyo valor identifica sin
ambigüedad a una fila: el número de pedido, la matrícula.

Sin una llave de verdad única no se puede saber si dos filas son la misma cosa
registrada dos veces o dos cosas distintas.
:::

::: definition {#def-join title="Join"}
Un `join` pega dos tablas emparejando las filas que comparten el mismo valor de
llave: los pedidos con los datos del cliente que los hizo.

Cuando la llave no casa, el `join` no avisa: simplemente devuelve menos filas de
las que esperabas.
:::

::: definition {#def-corrida title="Corrida"}
Una corrida es una ejecución completa del proceso, de principio a fin, sobre un
período de datos: la corrida del martes.

Casi todo lo que falla en esta unidad falla entre una corrida y la siguiente.
:::
```

En `1_el_viaje/0_index.md`, antes de «La falla que abre el tema»:

```markdown
::: definition {#def-esquema title="Esquema"}
El esquema es la declaración de qué columnas tiene una tabla, cómo se llaman y
de qué tipo es cada una: `fecha` es una fecha, `monto` es un número.

Sin esquema declarado, cada quien interpreta los datos a su manera, y dos
personas obtienen dos números distintos de la misma tabla.
:::
```

Y en la subsección «Data lake», junto a la lista de formatos:

```markdown
::: definition {#def-parquet title="Parquet"}
Parquet es un formato de archivo que guarda los datos **por columna** en vez de
por fila, y comprimidos.

Guardar por columna permite leer solo las columnas que pediste; en un CSV, en
cambio, hay que recorrer todas las filas enteras para llegar a un solo dato.
:::
```

Y antes de la subsección «Lakehouse»:

```markdown
::: definition {#def-formato-tabla title="Formato de tabla abierto"}
Es una capa de metadatos que se pone encima de archivos sueltos y los hace
comportarse como una tabla: sabe qué archivos la componen, qué esquema tienen y
cómo cambió con el tiempo. Delta Lake, Iceberg y Hudi son los tres nombres.

Sin esa capa, un montón de archivos en un directorio es solo un montón de
archivos: nadie puede versionarlos ni consultarlos como una sola cosa.
:::

::: definition {#def-transaccion title="Transacción y escritura atómica"}
Una escritura es **atómica** cuando ocurre completa o no ocurre: no existe un
estado a medias que alguien pueda leer. Una transacción es el mecanismo que lo
garantiza.

Sin ella, quien consulte la tabla mientras se carga verá medio día de datos y
creerá que las ventas se desplomaron.
:::
```

Con esas cuatro, `1_el_viaje` queda **en el tope de 4**: no cabe ninguna más.

En `2_etl_elt/0_index.md`, antes de la sección «Load»:

```markdown
::: definition {#def-particion title="Partición"}
Una partición es un trozo de una tabla separado por el valor de una columna,
casi siempre la fecha: las filas del 5 de agosto viven aparte de las del 6.

Sin particiones, corregir un solo día obliga a reescribir la tabla entera.
:::
```

Y en la sección «Por qué ETL era lo único razonable», junto a la primera mención:

```markdown
::: definition {#def-staging title="Staging"}
El *staging* es el lugar de paso donde los datos se transforman antes de entrar
a su destino final: una máquina o un directorio intermedio.

Es la pieza que ELT elimina, y por eso su desaparición cambia toda la economía
del proceso.
:::
```

En `3_eda/0_index.md`, en la subsección «3. ¿Cómo se ven los datos?»:

```markdown
::: definition {#def-fuga title="Fuga de información"}
Hay fuga cuando una columna contiene, de forma disfrazada, la respuesta que se
quiere predecir: predecir si un cliente se dio de baja usando la columna «fecha
de baja».

El modelo sale con una exactitud excelente en la prueba y sirve para nada en
producción, donde esa columna todavía no existe.
:::
```

En `4_cuando_se_rompe/0_index.md`, en su sección 1, sustituyendo la definición inline de `:45`:

```markdown
::: definition {#def-idempotencia title="Idempotencia"}
Un paso es idempotente cuando correrlo una vez o cinco sobre la misma entrada
deja el sistema exactamente igual.

Sin idempotencia no puedes reintentar nada, y sin reintentos no hay orquestación
ni backfills que sirvan.
:::

::: definition {#def-sistema-distribuido title="Sistema distribuido"}
Es un sistema cuyas piezas corren en máquinas distintas y se hablan por la red:
tu proceso, la base origen, el almacenamiento y el orquestador.

La consecuencia práctica es que la red **se cae**, así que un error transitorio
no es un caso raro sino la operación normal.
:::
```

Y en la sección 6:

```markdown
::: definition {#def-materializar title="Materializar"}
Materializar es guardar el resultado de una consulta como una tabla, en vez de
recalcularlo cada vez que alguien pregunta.

Sin materializar, un tablero que se consulta cien veces al día recorre cien
veces el mismo histórico y lo cobra cien veces.
:::
```

Al escribir cada una: **borrar la definición en prosa que la duplicaba**. En `4_cuando_se_rompe`, la frase «Faltaba la **idempotencia**: correr el proceso una vez o cinco…» se reduce a «Faltaba la **idempotencia**.»

- [ ] **Step 3bis: Quitar «idempotencia» de las dos páginas que la usan antes de definirla**

`grep -l "idempoten"` la encuentra hoy en `0_index`, `2_etl_elt`, `4_cuando_se_rompe`, `5_posiciones` y `6_presentacion`. Las dos primeras van **antes** de la página que la enseña, y `0_index` ya está en el tope de 4 definiciones, así que se reescriben para decir lo mismo sin el término.

En `course/2_pipeline_de_datos/0_index.md`, la sección «Contrato, transformación, orquestación»:

```markdown
**`raya build` es la transformación, y es repetible.** Misma fuente, mismo
`artifact/`, hoy y en tres meses. Por eso `artifact/` no se versiona: es
regenerable.
```

Y la frase de cierre de esa sección, que hoy enumera «Fuente, contrato,
transformación, producto, orquestación, idempotencia»:

```markdown
Fuente, contrato, transformación, producto, orquestación: cuando alguno suene
abstracto, abre ese repositorio.
```

En `2_etl_elt/0_index.md`, la última fila de la tabla de estrategias de carga
(`Overwrite por partición`), cuya columna de riesgo dice «Base práctica de la
idempotencia»:

```markdown
| **Overwrite por partición** | Reescribe solo el período procesado | Es lo que hace segura una reejecución, y por eso reaparece en [[cuando-se-rompe]] |
```

Y la viñeta de «Qué te llevas» de esa misma página:

```markdown
- **La carga tiene estrategia.** Append duplica; sobrescribir por partición hace
  segura una reejecución.
```

`5_posiciones` y `6_presentacion` van **después** de `4_cuando_se_rompe`, así que sus menciones se quedan como están.

- [ ] **Step 4: Escribir el glosario**

Crear `course/2_pipeline_de_datos/7_glosario/0_index.md`:

```markdown
---
id: glosario
title: Glosario
nav_title: Glosario
summary: "Las catorce palabras que esta unidad define, en orden alfabético, cada una con el enlace a donde se explica."
status: ready
estimated_time: 4m
tags: [glosario, vocabulario]
prerequisites: [pipeline-de-datos]
---

# Glosario

## En corto

- Catorce términos, en orden alfabético, con una línea cada uno.
- La columna de la derecha lleva a la **definición completa**, donde se explica por qué importa.
- Es la página de repaso: si al leer una página posterior no reconoces una palabra, está aquí.

## Los términos

| Término | En una línea | Dónde se explica |
|---|---|---|
| Corrida | Una ejecución completa del proceso sobre un período de datos | @def-corrida |
| Esquema | Qué columnas tiene una tabla, cómo se llaman y de qué tipo son | @def-esquema |
| Formato de tabla abierto | Metadatos sobre archivos sueltos que los hacen actuar como tabla | @def-formato-tabla |
| Fuga de información | Una columna que contiene disfrazada la respuesta que se quiere predecir | @def-fuga |
| Idempotencia | Correr una vez o cinco deja el sistema igual | @def-idempotencia |
| Join | Pegar dos tablas emparejando filas por el valor de su llave | @def-join |
| Llave | La columna cuyo valor identifica sin ambigüedad a una fila | @def-llave |
| Materializar | Guardar el resultado de una consulta en vez de recalcularlo | @def-materializar |
| Parquet | Formato que guarda por columna y comprimido | @def-parquet |
| Partición | Un trozo de tabla separado por el valor de una columna, casi siempre la fecha | @def-particion |
| Sistema distribuido | Piezas que corren en máquinas distintas y se hablan por la red | @def-sistema-distribuido |
| Staging | El lugar de paso donde se transforma antes de cargar | @def-staging |
| Tabla, fila, columna | La rejilla: una fila por cosa registrada, una columna por dato | @def-tabla |
| Transacción y escritura atómica | La escritura ocurre completa o no ocurre | @def-transaccion |

## Qué te llevas

- Si una palabra de esta unidad no te suena, **está aquí y enlaza a donde se explica**.
- El glosario **recuerda**; la definición de cada página **enseña**. No son lo mismo y no se leen igual.
```

Añadir el renglón del glosario a la tabla «Recorrido» de `course/2_pipeline_de_datos/0_index.md`:

```markdown
| [[glosario]] | Las catorce palabras que la unidad define, en un solo lugar |
```

- [ ] **Step 5: Correr la guarda y validar**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_vocabulario.py -q
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
```

Esperado: PASS en las cuatro pruebas, `validate` y `build` OK.

Si `test_ningun_termino_se_usa_antes_de_definirse` falla, la corrección **no** es mover el patrón: es mover la definición a la página anterior, o reescribir la prosa que la adelanta.

- [ ] **Step 6: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/test_vocabulario.py course/2_pipeline_de_datos
git commit -m "feat(unidad-2): 14 definiciones antes de su primer uso, glosario y guarda de vocabulario"
```

---

## Task 6: El caso único — `ventas.csv`

Sustituye las seis anécdotas desconectadas por un solo conjunto ficticio al que cada página le suma una capa. **No se ejecuta nada y no se publica ningún archivo de datos**: el CSV se muestra como tabla Markdown.

**Files:**
- Modify: `course/2_pipeline_de_datos/0_index.md` y las 5 páginas de la tabla de abajo

**Interfaces:**
- Consumes: las definiciones de la Task 5 (`@def-llave`, `@def-particion`, `@def-idempotencia`).
- Produces: el conjunto `ventas.csv` con columnas `pedido`, `fecha`, `sucursal`, `producto`, `monto`. Las Tasks 7 y 10 lo dan por existente.

- [ ] **Step 1: Presentar el conjunto una sola vez**

En `course/2_pipeline_de_datos/0_index.md`, después de «Vocabulario mínimo»:

```markdown
## El caso de esta unidad

Toda la unidad usa el mismo ejemplo: **las ventas de una cafetería con tres
sucursales**, que llegan cada noche en un archivo llamado `ventas.csv`.

| pedido | fecha | sucursal | producto | monto |
|---|---|---|---|---|
| 1001 | 2026-08-04 | CDMX | Capuchino | 62 |
| 1002 | 04/08/2026 | D.F. | Latte | 68 |
| 1003 | 2026-08-04 | Santa Fe | Americano | 0 |
| 1004 | 2026-08-05 | CDMX | Capuchino | 62 |
| 1005 | 05/08/2026 | Polanco | Té | 45 |

Ya con verlo se ven tres problemas: **la fecha viene en dos formatos**,
**«CDMX» y «D.F.» son la misma sucursal escrita de dos maneras**, y **hay un
pedido de monto cero**. Cada página siguiente se hace cargo de uno.

La llave es `pedido` — ver @def-llave.
```

- [ ] **Step 2: Reemplazar la anécdota de cada página**

| Página | Anécdota que se va | Capa que entra |
|---|---|---|
| `1_el_viaje` | El archivo del proveedor con columna extra (`:28-34`) | `ventas.csv` llega crudo: ¿se rechaza el `04/08/2026` al escribir, o se acepta y explota al leer? |
| `2_etl_elt` | *(no tiene anécdota propia; se ancla en Load)* | Se normaliza `D.F.` → `CDMX` y las fechas a ISO; se carga con `append` y luego con `upsert`, y se cuentan las filas |
| `3_eda` | El modelo de abandono con once casos (`:26-32`) | El pedido 1003 con monto 0 → «¿el 12 % de los pedidos con monto cero son cortesías o errores de captura?» |
| `4_cuando_se_rompe` | Las ventas del martes duplicadas (`:43`) | La corrida del 4 de agosto falla a la mitad, se relanza, y el 4 aparece dos veces |
| `5_posiciones` | *(sin anécdota; la tabla es abstracta)* | Quién se hace cargo de cada uno de esos cuatro momentos |

En `2_etl_elt`, la tabla de estrategias de carga (`:87-92`) gana un ejemplo concreto justo debajo:

```markdown
Con `ventas.csv`, la diferencia se ve en un número. La corrida del 4 de agosto
trae 3 pedidos, y se relanza:

| Estrategia | Filas del 4 de agosto tras dos corridas |
|---|---|
| `append` | 6 — cada pedido aparece dos veces |
| `upsert` por `pedido` | 3 — la segunda escritura actualiza, no añade |
| Sobrescribir la partición del 4 | 3 — el día se reemplaza entero |
```

`6_presentacion` y `7_glosario` **no usan el caso**: no enseñan concepto nuevo.

- [ ] **Step 3: Verificar que no quedó ninguna anécdota vieja**

```bash
cd ~/itam/fdd_o26/course/2_pipeline_de_datos
grep -rn "notebook del viernes\|abandono de clientes\|region_code\|once" --include="0_index.md" . || echo "limpio"
```

Esperado: `limpio`. La única excepción legítima es «el notebook del viernes» en `0_index.md`, que es la apertura de la unidad y **se conserva**: es la falla que motiva todo, no una anécdota de página.

- [ ] **Step 4: Correr todo y commitear**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26

cd ~/itam/fdd_o26
git add course/2_pipeline_de_datos
git commit -m "feat(unidad-2): un solo caso, ventas.csv, atraviesa las cinco paginas de contenido"
```

---

## Task 7: Recortes hasta el presupuesto

Tras las Tasks 5 y 6 la unidad creció. El presupuesto es ≤ 8 800 palabras.

**Files:**
- Create: `tools/test_presupuesto.py`
- Modify: `course/2_pipeline_de_datos/0_index.md`, `5_posiciones/0_index.md`, `4_cuando_se_rompe/0_index.md`, `6_presentacion/0_index.md`

**Interfaces:**
- Consumes: el contenido final de las Tasks 3, 5 y 6.
- Produces: nada que otras tareas consuman.

- [ ] **Step 1: Escribir la guarda que falla**

Crear `tools/test_presupuesto.py`:

```python
"""Guarda: la unidad no pasa de 8 800 palabras de prosa.

Cuenta solo el cuerpo Markdown de cada pagina, sin frontmatter. Los objetos
oficiales son YAML y no cuentan.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/2_pipeline_de_datos"
TOPE = 8800

FRONTMATTER = re.compile(r"\A---.*?^---\s*", re.S | re.M)


def paginas():
    return sorted(UNIDAD.rglob("0_index.md"))


def palabras(pagina):
    cuerpo = FRONTMATTER.sub("", pagina.read_text(encoding="utf-8"))
    return len(cuerpo.split())


def test_la_unidad_no_pasa_del_presupuesto():
    detalle = {p.parent.name: palabras(p) for p in paginas()}
    total = sum(detalle.values())
    assert total <= TOPE, (
        f"la unidad tiene {total} palabras, {total - TOPE} por encima del tope.\n"
        + "\n".join(f"  {k}: {v}" for k, v in sorted(detalle.items()))
    )
```

- [ ] **Step 2: Correr la guarda y ver cuánto sobra**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_presupuesto.py -q
```

Esperado: FALLA, con el desglose por página. Anotar el excedente exacto.

- [ ] **Step 3: Recortar en los tres sitios identificados**

**a. `course/2_pipeline_de_datos/0_index.md:110-122`** — la tabla «Por qué esta unidad es el mapa del semestre» duplica la de `1_introduccion/1_el_curso/0_index.md:29-36`. Sustituir la sección entera por:

```markdown
## Por qué esta unidad es el mapa del semestre

Cada módulo del curso existe porque alguna parte del pipeline lo exige: la
terminal porque los datos llegan como archivos en máquinas ajenas, Git porque
las transformaciones son código que hay que auditar, Docker porque tiene que
correr igual aquí y allá. El reparto completo está en [[el-curso|El curso]].

Si te preguntas por qué estamos aprendiendo algo, la respuesta casi siempre
está en esta página.
```

**b. `5_posiciones/0_index.md:83-93`** — las tres fichas de papeles de la era de los modelos de lenguaje dicen lo mismo tres veces. Reducir a:

```markdown
## Los papeles de la era de los modelos de lenguaje

Desde 2023 hay títulos nuevos alrededor de los sistemas construidos sobre
modelos de lenguaje: **AI engineer**, que construye aplicaciones sobre modelos
que no entrenó; **ingeniere de plataforma de modelos**, que los despliega y
optimiza; y **evaluación de sistemas de IA**, que mide si funcionan. Trátalos
como responsabilidades emergentes, no como carreras consolidadas.

Ninguno reemplaza a los anteriores, y los tres son más parecidos a lo que ya
leíste de lo que su nombre sugiere: la recuperación aumentada, vista de cerca,
**es un pipeline de datos** —extraer documentos, fragmentarlos, cargarlos a un
índice, mantenerlos al día—. Quien la construye sigue necesitando que alguien
garantice que esos documentos llegan completos y actualizados.
```

**c. `4_cuando_se_rompe/0_index.md`** — es la página más larga y repite en prosa lo que ya dicen sus tres tablas. Recorrerla buscando el patrón «tabla, y debajo un párrafo que reexplica una fila». Borrar el párrafo, conservar la tabla.

**d. `6_presentacion/0_index.md`** — se va el changelog editorial. Borrar las secciones «Qué se reescribió, y por qué» (`:56-75`) y «Sobre las imágenes» (`:77-83`). Se conservan: el frontmatter, «En corto» reducido, «El archivo» con sus dos enlaces al PDF, el callout de advertencia, «Por qué se conserva» y «Qué se conservó». Deja la página en ~250 palabras.

- [ ] **Step 4: Correr la guarda hasta que pase**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_presupuesto.py -q
```

Esperado: PASS.

Regla del spec, y aplica aquí literalmente: **si un recorte quita una idea en vez de una repetición, se conserva la idea y se acepta pasar del presupuesto en esa página**, subiendo `TOPE` y dejando dicho en el mensaje de commit qué idea se salvó y cuánto costó.

- [ ] **Step 5: Validar y commitear**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q

git add tools/test_presupuesto.py course/2_pipeline_de_datos
git commit -m "refactor(unidad-2): recorta duplicacion y changelog editorial hasta el presupuesto"
```

---

## Task 8: Diagramas legibles en celular

Los ocho SVG están autorados a 880 px con texto de 11.5 px. Como `img { max-width: 100% }`, en un viewport de 390 px ese texto renderiza a unos 5 px. La causa concreta es `pie()` (`tools/gen_diagramas.py:183`), que pinta dentro del SVG una frase explicativa de hasta 20 palabras.

**Files:**
- Modify: `tools/gen_diagramas.py` (borrar `:183-184` y sus 8 llamadas)
- Modify: `tools/test_diagramas.py` (regla nueva)
- Modify: las 8 páginas con `::: figure`
- Regenerate: `course/2_pipeline_de_datos/_assets/d-*.svg`

**Interfaces:**
- Consumes: nada de tareas anteriores.
- Produces: los 8 SVG sin frase de pie; las 8 frases pasan a ser párrafo dentro del bloque `::: figure` correspondiente.

- [ ] **Step 1: Escribir la regla nueva en la guarda**

Al final de `tools/test_diagramas.py`:

```python
@pytest.mark.parametrize("slug", SLUGS)
def test_ningun_texto_del_svg_es_una_frase(slug):
    """El texto largo va al pie de figura en Markdown, no pintado dentro del SVG.

    Dentro del SVG solo caben etiquetas: a 880px reducidos a un movil, una frase
    de 11.5px queda en unos 5px y es ilegible. Se exceptuan el encabezado y su
    subtitulo, que van arriba y a mayor tamano.
    """
    import re

    texto = (GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8")
    nodos = re.findall(r"<text[^>]*>([^<]*)</text>", texto)
    cuerpo = nodos[2:]  # 0 = titulo del encabezado, 1 = subtitulo
    largos = [n for n in cuerpo if len(n.split()) > 4]
    assert not largos, (
        f"{slug}: hay texto de mas de 4 palabras dentro del SVG: {largos}"
    )


def test_el_generador_no_pinta_pies_de_figura():
    fuente = (RAIZ / "tools/gen_diagramas.py").read_text(encoding="utf-8")
    assert "def pie(" not in fuente, (
        "pie() volvio a gen_diagramas.py: el texto largo va al Markdown"
    )
```

- [ ] **Step 2: Correr la guarda y confirmar que falla**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_diagramas.py -k "frase or pies" -q
```

Esperado: FALLA en los 8 slugs y en `test_el_generador_no_pinta_pies_de_figura`.

- [ ] **Step 3: Anotar las 8 frases antes de borrarlas**

```bash
cd ~/itam/fdd_o26 && grep -n "pie(alto" -A 2 tools/gen_diagramas.py
```

Guardar la salida: esas frases son exactamente lo que hay que pegar en el Markdown en el Step 5. Corresponden en orden a `d-dag`, `d-schema`, `d-etl-elt`, `d-tidy`, `d-calidad`, `d-idempotencia`, `d-tiempo`, `d-ciclo`.

- [ ] **Step 4: Borrar `pie()` y sus llamadas, y regenerar**

Borrar de `tools/gen_diagramas.py`:

```python
def pie(alto, texto):
    return txt(30, alto - 18, texto, fill=SUAVE, size=11.5)
```

y las 8 líneas `p.append(pie(alto, "..."))` (en `:280`, `:352`, `:434`, `:510`, `:555`, `:622`, `:689`, `:774`, cada una con su continuación de cadena).

Después, revisar los `<text>` que sigan pasando de 4 palabras —los hay dentro de los diagramas, no solo en el pie— y acortarlos a etiqueta. Ejemplos reales: en `d-schema`, «Schema-on-write valida al escribir; schema-on-read acepta todo y valida al leer» (11 palabras) se parte en dos etiquetas de nodo; en `d-idempotencia`, «Cada reintento inventa datos que nadie produjo» (7) pasa al Markdown.

Regenerar:

```bash
cd ~/itam/fdd_o26 && python3 tools/gen_diagramas.py
```

- [ ] **Step 5: Mover las 8 frases al bloque `::: figure`**

En cada página, la frase anotada en el Step 3 va como párrafo **dentro** del bloque, después de la imagen. Así queda texto HTML real, seleccionable y escalable. Para `d-dag`, en `course/2_pipeline_de_datos/0_index.md`:

```markdown
::: figure {#dag title="El pipeline como grafo de dependencias"}
![Diagrama de un pipeline como DAG: nodos que se bifurcan y reconvergen](_assets/d-dag.svg)

Si una rama falla, solo se vuelve a correr esa rama: no hace falta rehacer el
pipeline entero.
:::
```

Repetir para los otros siete, cada uno en la página donde aparece.

- [ ] **Step 6: Darle eje Y a la curva de costo de `d-etl-elt`**

La curva de «Costo del almacenamiento por GB» (`gen_diagramas.py:408-425`) tiene tres defectos y hay que arreglar los tres juntos:

1. **No hay eje Y.** Se dibuja la línea vertical en `:409` y no lleva ni una etiqueta ni una unidad. Es una curva que baja sin decir desde dónde.
2. **Los valores son inventados.** `valores = [1.0, 0.42, 0.19, 0.09, 0.045, 0.022, 0.012]` son fracciones normalizadas sin fuente. La unidad critica en `3_eda` que el «60 % del tiempo» se cite sin fuente ni año; dibujar una curva cuantitativa sin ninguna de las dos es el mismo error.
3. **La escala lineal miente sobre la magnitud.** El costo por GB cayó unos cinco órdenes de magnitud desde 1990. La curva dibujada cae por un factor de 83, así que subrepresenta groseramente justo el fenómeno que la página usa como causa del cambio de ETL a ELT.

Sustituir el bloque por una escala logarítmica con décadas etiquetadas y valores anclados:

```python
    # Costo por GB de almacenamiento en disco, ordenes de magnitud aproximados
    # a partir de las series historicas de precio de HDD. Es una curva de
    # magnitud, no una serie exacta: por eso el eje va en potencias de diez y
    # el pie declara de donde sale.
    anios = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2026]
    usd_gb = [9000.0, 900.0, 16.0, 1.2, 0.09, 0.04, 0.023, 0.015]

    x0, x1, base, tope = 150, 830, 440, 336
    p.append(linea(x0, tope, x0, base, SUAVE, ancho=1))
    p.append(linea(x0, base, x1, base, SUAVE, ancho=1))

    # Eje logaritmico: de 10^-2 a 10^4 USD/GB, una marca por decada.
    lo, hi = -2, 4
    def _y(v):
        return base - (math.log10(v) - lo) / (hi - lo) * (base - tope)

    for exp in range(lo, hi + 1):
        y = _y(10.0 ** exp)
        p.append(linea(x0 - 4, y, x0, y, SUAVE, ancho=1))
        etiqueta = {
            -2: "$0.01", -1: "$0.10", 0: "$1", 1: "$10",
            2: "$100", 3: "$1k", 4: "$10k",
        }[exp]
        p.append(txt(x0 - 8, y + 4, etiqueta, fill=SUAVE, size=10, anchor="end"))
    p.append(txt(x0 - 8, tope - 12, "USD / GB", fill=SUAVE, size=10, anchor="end"))

    puntos = []
    for i, v in enumerate(usd_gb):
        px = x0 + i * ((x1 - x0 - 20) / (len(usd_gb) - 1))
        puntos.append((px, _y(v)))
```

El resto del bloque —el `<path>`, los círculos y la anotación— se conserva tal cual, sustituyendo `valores` por `usd_gb`. Las etiquetas del eje X pasan a derivarse de `anios`, no de coordenadas a mano:

```python
    for i in (0, 2, 4, 6, 7):
        px = x0 + i * ((x1 - x0 - 20) / (len(usd_gb) - 1))
        p.append(txt(px, 458, str(anios[i]), fill=SUAVE, size=11, anchor="middle"))
```

`math` ya está importado en `:18`.

La frase que sale al pie de figura en el Step 5 (Markdown, no SVG) declara la naturaleza del dato, en el mismo registro con que `3_eda` trata el 60 %:

```markdown
El eje va en potencias de diez: la caída es de unos **cinco órdenes de
magnitud**, no de un factor de dos. Son cifras de orden de magnitud tomadas de
las series históricas de precio de disco, no una serie exacta — lo que importa
aquí es la forma de la curva, y esa no está en duda.
```

- [ ] **Step 7: Correr las guardas y verificar el render**

```bash
cd ~/itam/fdd_o26 && python3 tools/gen_diagramas.py
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_diagramas.py -q
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
```

Las etiquetas del eje (`$0.01`, `$10k`, `USD / GB`, `1990`) son de una palabra, así que pasan la regla de ≤4 palabras del Step 1.

Esperado: PASS en todo. Verificar que la frase salió como HTML y no como imagen:

```bash
grep -c "no hace falta rehacer el pipeline entero" \
  ~/itam/fdd_o26/artifact/site/pipeline-de-datos/index.html
```

Esperado: `1`.

Y que el eje Y quedó etiquetado:

```bash
grep -o 'USD / GB\|\$10k\|\$0.01' \
  ~/itam/fdd_o26/course/2_pipeline_de_datos/_assets/d-etl-elt.svg | sort -u
```

Esperado: las tres cadenas.

- [ ] **Step 8: Revisar si algún otro diagrama afirma cantidades sin escala**

`d-etl-elt` es el único con una curva cuantitativa, pero `d-tiempo` compara latencias («horas», «minutos», «segundos») en un eje que puede sugerir proporción sin tenerla. Abrir el SVG y confirmar que las cuatro cajas están **igualmente espaciadas y sin eje**, de modo que se lean como categorías ordenadas y no como una escala. Si tienen eje, quitarlo: no hay dato detrás.

```bash
cd ~/itam/fdd_o26 && grep -c "<line" course/2_pipeline_de_datos/_assets/d-tiempo.svg
```

- [ ] **Step 9: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/gen_diagramas.py tools/test_diagramas.py \
        course/2_pipeline_de_datos
git commit -m "fix(unidad-2): frases fuera del SVG y eje logaritmico etiquetado en la curva de costo"
```

---

## Task 9: Ilustraciones en cel anime de los noventa

Registro unificado —Ghost in the Shell, Serial Experiments Lain, Akira— con **paleta distinta por página**, y cada escena representando el concepto de su página en vez de una tubería genérica. Hoy la portada de una página cuyo argumento es «no es una flecha, es un grafo» es un dibujo de tubos.

**Files:**
- Modify: `tools/test_ilustraciones.py` (líneas 20-24 y 76-81)
- Modify: `tools/ilustraciones.json`
- Modify: `course/2_pipeline_de_datos/_assets/CREDITOS.md`
- Regenerate: `course/2_pipeline_de_datos/_assets/ilus-*.jpg`

**Interfaces:**
- Consumes: el glob corregido de la Task 2.
- Produces: 7 JPG de 1024 px, menos de 400 KB cada uno, con los mismos nombres de archivo, así que ninguna página cambia su `![...](_assets/ilus-*.jpg)`.

- [ ] **Step 1: Corregir las dos guardas**

`test_ilustraciones.py:81` exige hoy que el estilo contenga `"sin figuras humanas"`, lo que prohíbe las siluetas que este registro necesita. Y `PROHIBIDOS` (`:20-24`) lista catorce nombres sin incluir **ninguno** de los personajes de estas obras, así que el hueco que la prueba dice cubrir está abierto.

```python
PROHIBIDOS = [
    "tukey", "wickham", "codd", "kimball", "inmon", "hadley",
    "musk", "bezos", "zuckerberg",
    "mickey", "pikachu", "mario", "batman", "sherlock",
    # Las obras de referencia estetica y sus personajes: se cita el registro
    # visual, nunca el personaje ni el titulo.
    "ghost in the shell", "kusanagi", "motoko", "batou",
    "serial experiments", "lain", "akira", "kaneda", "tetsuo",
    "frieren", "evangelion", "ayanami", "studio ghibli", "ghibli",
]
```

Y la prueba del estilo:

```python
def test_el_estilo_prohibe_texto_y_rostros_identificables():
    estilo = catalogo()["estilo"]
    assert estilo.rstrip().endswith(
        "Sin texto, sin letras, sin marcas de agua, sin firmas."
    ), "el estilo debe cerrar prohibiendo texto, marcas de agua y firmas"
    assert "sin rostros identificables" in estilo.lower()
```

Borrar la función vieja `test_el_estilo_prohibe_texto_y_figuras_humanas`.

- [ ] **Step 2: Correr las guardas y confirmar que fallan**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_ilustraciones.py -q
```

Esperado: FALLA `test_el_estilo_prohibe_texto_y_rostros_identificables` — el estilo actual dice «Sin figuras humanas».

- [ ] **Step 3: Reescribir el estilo y las siete escenas**

En `tools/ilustraciones.json`, el `estilo`:

```
Animacion cel de los anos noventa, ciencia ficcion urbana pintada a mano: sombreado cel de bordes duros sin degradados suaves, fondos pintados con pincel visible, grano de pelicula de 35 mm y aberracion cromatica leve en los bordes. Una sola fuente de luz dramatica por lamina —un monitor de tubo, un letrero de neon, una ventana— que recorta las formas a contraluz. Detalle denso de cables, racks, conductos y terminales. Todas las laminas comparten ese trazo y esa atmosfera; lo unico que cambia entre ellas es la paleta, que cada lamina declara por su cuenta y que domina la imagen entera. Las figuras aparecen siempre de espaldas, en silueta o recortadas por la luz, nunca de frente: sin rostros identificables, sin personajes reconocibles, sin mascotas, sin logotipos ni marcas comerciales. Sin texto, sin letras, sin marcas de agua, sin firmas.
```

Cada escena representa el concepto de su página. Reescribir las siete entradas de `ilustraciones`, conservando los nombres (`portada`, `viaje`, `etl-elt`, `eda`, `ruptura`, `oficios`, `archivo`) y la primera frase de cada una declarando la paleta:

| Nombre | Paleta | Qué representa ahora |
|---|---|---|
| `portada` | Verde terminal y ámbar sobre negro azulado | Un **grafo** de nodos luminosos que se bifurca y reconverge sobre una ciudad nocturna. No tubos |
| `viaje` | Azul medianoche y turquesa | Cuatro edificios-depósito de arquitectura distinta, el mismo caudal de luz entrando de forma diferente en cada uno |
| `etl-elt` | Magenta y violeta eléctrico | Un cruce de neón con dos rutas espejadas que recorren las mismas tres estaciones en orden invertido |
| `eda` | Cian frío y blanco azulado | Una figura de espaldas ante un muro de monitores CRT, midiendo antes de decidir |
| `ruptura` | Gris hierro con rojo de alarma | Un cable troncal reventado con la luz escapando, y la sala de control detrás en alerta |
| `oficios` | Latón, cobre y madera cálida | Siete estaciones de trabajo contiguas, cada una con su instrumental distinto, sin nadie en ellas |
| `archivo` | Sepia y ocre desaturado | Un archivo polvoriento de cintas y planos, luz de tarde atravesando el polvo |

Cada prompt sigue la misma estructura de tres partes que los actuales: **paleta primero, escena después, y una frase final que dice cuál es la estructura de la imagen.** Este es `portada` completo, como patrón de registro y de longitud para los otros seis:

```
Paleta: verde terminal fosforescente y ambar calido sobre negro azulado profundo; ningun otro color. Vista nocturna de una ciudad densa desde una azotea, y suspendido sobre ella un grafo de nodos luminosos conectados por haces de luz: un nodo de origen a la izquierda del que salen tres ramas que atraviesan nodos intermedios distintos y vuelven a converger en un solo nodo a la derecha, del que salen dos salidas finales. Los nodos son bloques de circuiteria con cables visibles; las ramas son haces de luz de grosor desigual. Una silueta de espaldas en primer plano, recortada a contraluz contra el grafo, ocupando el tercio inferior izquierdo. La estructura de la imagen es esa: division en ramas, reconvergencia en un punto, y salidas multiples — un grafo, no una tuberia.
```

Al escribir cada prompt, no usar ninguna palabra de `PROHIBIDOS` ni de `PROHIBIDOS_EN_PROMPT` —`rostro`, `retrato`, `cara humana`, `celebridad`, `famoso`, `fotografia de una persona`, `logotipo`, `marca comercial`—. Nótese que el ejemplo dice «silueta de espaldas» y nunca «rostro»: es la forma de pedir presencia humana sin disparar la guarda. La prueba del Step 5 lo verifica.

- [ ] **Step 4: Generar**

```bash
cd ~/itam/fdd_o26
set -a && . ./.env && set +a
python3 tools/gen_ilustraciones.py portada viaje etl-elt eda ruptura oficios archivo
```

Revisar cada JPG a ojo. **Máximo dos reintentos por escena** —volver a correr el generador con solo ese nombre— antes de aceptar la mejor. Si una escena no sale en dos intentos, restaurar la ilustración anterior de esa página con `git checkout` y dejarlo anotado en el commit.

- [ ] **Step 5: Correr las guardas**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_ilustraciones.py tools/test_creditos.py -q
```

Esperado: PASS. Si falla `test_dimensiones_y_peso`, el JPG pasa de 400 KB: bajar `CALIDAD_JPEG` en `tools/gen_ilustraciones.py:18` y regenerar.

- [ ] **Step 6: Actualizar CREDITOS.md**

El párrafo de `CREDITOS.md` que describe el estilo dice hoy «grabado técnico de línea fina sobre fondo oscuro» y enumera las paletas viejas. Reescribirlo con el registro y las paletas nuevas. `test_creditos.py` exige que cada archivo tenga su fila y que el encabezado siga diciendo que ninguna ilustración representa personas reales.

- [ ] **Step 7: Verificar que no se filtró la llave y commitear**

```bash
cd ~/itam/fdd_o26
git check-ignore .env artifact/    # ambas deben aparecer
git status --short | grep -i "\.env" && echo "PELIGRO: .env aparece en el status" || echo "ok"
git add tools/ilustraciones.json tools/test_ilustraciones.py \
        course/2_pipeline_de_datos/_assets
git commit -m "feat(unidad-2): ilustraciones en cel anime noventero, una por concepto, y cierra el hueco de PROHIBIDOS"
```

---

## Task 10: Dos tarjetas y dos preguntas por página

Hoy hay 6 tarjetas y un quiz de 6 preguntas para siete páginas. La meta son **2 tarjetas y 2 preguntas por página de contenido** —índice, viaje, ETL/ELT, EDA, cuando se rompe, posiciones—: 12 y 12. `6_presentacion` y `7_glosario` no llevan ninguna.

**Files:**
- Modify: las 6 tarjetas ya reubicadas en la Task 2
- Create: 6 tarjetas nuevas, en `<pagina>/_official/cards/`
- Create: 6 quizzes por página, en `<pagina>/_official/quizzes/`
- Delete: `course/2_pipeline_de_datos/_official/quizzes/1_pipeline.yaml`

**Interfaces:**
- Consumes: el contenido final de las Tasks 3, 5, 6 y 7; los `id` de definición de la Task 5.
- Produces: nada.

- [ ] **Step 1: Escribir la guarda que falla**

Al final de `tools/test_vocabulario.py`:

```python
CONTENIDO = [
    "0_index", "1_el_viaje", "2_etl_elt", "3_eda",
    "4_cuando_se_rompe", "5_posiciones",
]


def soporte(nombre):
    if nombre == "0_index":
        return UNIDAD / "_official"
    return UNIDAD / nombre / "_official"


def test_cada_pagina_de_contenido_tiene_dos_tarjetas_y_dos_preguntas():
    import yaml

    for nombre in CONTENIDO:
        base = soporte(nombre)
        tarjetas = sorted((base / "cards").glob("*.yaml")) if (base / "cards").is_dir() else []
        assert len(tarjetas) == 2, f"{nombre}: {len(tarjetas)} tarjetas, deben ser 2"

        quizzes = sorted((base / "quizzes").glob("*.yaml")) if (base / "quizzes").is_dir() else []
        assert len(quizzes) == 1, f"{nombre}: {len(quizzes)} quizzes, debe ser 1"
        preguntas = yaml.safe_load(quizzes[0].read_text(encoding="utf-8"))
        n = len(preguntas["content"]["questions"])
        assert n == 2, f"{nombre}: el quiz tiene {n} preguntas, deben ser 2"


def test_ninguna_pregunta_tiene_dos_opciones_correctas():
    import yaml

    for ruta in UNIDAD.rglob("_official/quizzes/*.yaml"):
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        for pregunta in datos["content"]["questions"]:
            correctas = [o for o in pregunta["options"] if o.get("correct")]
            assert len(correctas) == 1, (
                f"{ruta.name}/{pregunta['id']}: {len(correctas)} opciones correctas"
            )
```

- [ ] **Step 2: Correr la guarda y confirmar que falla**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_vocabulario.py -k "tarjetas or correctas" -q
```

Esperado: FALLA — hay páginas con 3 tarjetas, otras con 0, y un solo quiz de 6 preguntas en la raíz.

- [ ] **Step 3: Repartir el quiz existente**

Partir `_official/quizzes/1_pipeline.yaml` en seis archivos, uno por página, moviendo cada pregunta a la página que enseña su tema:

| Pregunta actual | Va a |
|---|---|
| `pipeline-vs-script` | `0_index` (raíz) |
| `dag-no-lineal` | `0_index` (raíz) |
| `schema-on-read-write` | `1_el_viaje` |
| `por-que-elt` | `2_etl_elt` |
| `preproceso-frontera` | `1_el_viaje` — la distinción pre/procesamiento se enseña ahí |
| `idempotencia-reintento` | `4_cuando_se_rompe` |

Cada archivo nuevo lleva `id` propio, por ejemplo:

```yaml
id: quiz-el-viaje
type: quiz
authority: official
content:
  questions:
    - id: schema-on-read-write
      prompt: >-
        ...
retrieval:
  kind: concept-check
```

Los `id` de curso son un espacio de nombres global: `quiz-pipeline`, `quiz-el-viaje`, `quiz-etl-elt`, `quiz-eda`, `quiz-cuando-se-rompe`, `quiz-posiciones`. Borrar `_official/quizzes/1_pipeline.yaml`.

- [ ] **Step 4: Escribir las preguntas faltantes**

Faltan preguntas en `3_eda` (2) y `5_posiciones` (2), y una en `2_etl_elt` y otra en `4_cuando_se_rompe`. Cada una con cuatro opciones y **exactamente una correcta**. La respuesta correcta se redacta completa, no como etiqueta suelta — es el patrón del quiz existente.

Ejemplo para `3_eda`:

```yaml
    - id: eda-viabilidad
      prompt: >-
        Un equipo va a construir un modelo que prediga qué clientes se dan de
        baja. ¿Cuál es la primera pregunta del EDA, y por qué esa y no otra?
      options:
        - label: >-
            Cuántos clientes se dieron de baja en el período disponible: si son
            once, no hay modelo posible, y saberlo el primer día cuesta una
            consulta en vez de seis semanas de trabajo
          correct: true
        - label: >-
            Qué algoritmo conviene usar, porque de esa elección dependen las
            transformaciones que habrá que aplicar después
          correct: false
        - label: >-
            Cómo se distribuyen las variables numéricas, porque sin conocer su
            forma no se pueden interpretar las gráficas posteriores
          correct: false
        - label: >-
            Qué proporción de valores faltantes hay, porque la completitud es la
            primera de las seis dimensiones de calidad
          correct: false
```

- [ ] **Step 5: Reescribir las 6 tarjetas y escribir las 6 nuevas**

Las tarjetas actuales parafrasean la prosa de su página; una tarjeta debe forzar recuperación. Regla: **el `front` plantea una situación, no pide una definición.** Comparar:

```yaml
# antes — pide un resumen
front: ¿Qué hace que una tabla sea tidy?

# después — obliga a aplicar
front: >-
  Una tabla tiene una columna por año: 2024, 2025, 2026. ¿Por qué no es tidy y
  qué forma debería tener?
```

Cada página de contenido queda con exactamente dos. Donde haya tres (`1_el_viaje`), fusionar las dos más cercanas o mover una a la página que ahora enseña ese tema.

- [ ] **Step 6: Correr todo**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
```

Esperado: verde. Verificar que cada página muestra su evaluación:

```bash
cd ~/itam/fdd_o26
grep -c "quiz-cuando-se-rompe" artifact/site/pipeline-de-datos/cuando-se-rompe/index.html
```

Esperado: al menos `1`. Si es `0`, el objeto no quedó bien colocado: revisar que su `_official/` cuelgue del directorio de la página y no de la raíz de la unidad.

- [ ] **Step 7: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/test_vocabulario.py course/2_pipeline_de_datos
git commit -m "feat(unidad-2): dos tarjetas y dos preguntas por pagina, junto a lo que evaluan"
```

---

## Task 11: Verificación final y despliegue

**Files:**
- Ninguno nuevo. Solo verificación y push.

**Interfaces:**
- Consumes: todas las tareas anteriores.
- Produces: el sitio publicado en https://rayalucaria.org/fdd_o26/.

- [ ] **Step 1: Correr la verificación completa**

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build    ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Esperado: los tres en verde.

- [ ] **Step 2: Recorrer los diez criterios de término del spec**

Uno por uno, contra el artifact recién construido:

```bash
cd ~/itam/fdd_o26

# 3 — las 14 definiciones existen
grep -rho '::: definition {#[a-z-]*' course/2_pipeline_de_datos | sort | wc -l   # 14

# 6 — pie() no volvió
grep -c "def pie" tools/gen_diagramas.py                                        # 0

# 8 — cada página es directorio con índice
find course/2_pipeline_de_datos -maxdepth 1 -name "*.md"                        # solo 0_index.md

# 9 — callouts en español
grep -o 'raya-callout-title">[^<]*' artifact/site/pipeline-de-datos/index.html | sort -u

# 10 — presupuesto
python3 -m pytest tools/test_presupuesto.py -q
```

El criterio 9 debe devolver `Nota`, `Consejo` o `Advertencia`, nunca `Note`.

- [ ] **Step 3: Confirmar que no se filtra nada**

```bash
cd ~/itam/fdd_o26
git check-ignore .env artifact/
git status --short
```

`.env` y `artifact/` deben estar ignorados, y `git status` no debe mencionar ninguno.

- [ ] **Step 4: Push y observar el despliegue**

```bash
cd ~/itam/fdd_o26
git push origin main
gh run watch
```

- [ ] **Step 5: Verificar el sitio publicado**

```bash
curl -sI https://rayalucaria.org/fdd_o26/pipeline-de-datos/glosario/ | head -1
gh api repos/raya-lucaria/fdd_o26/pages --jq '.https_enforced, .public'
```

Esperado: `HTTP/2 200`; `true` y `true`. Si el repositorio dejó de ser público, Pages falla en el plan de esta organización — hay que devolverlo a público antes de que el sitio vuelva a servir.

---

## Notas de ejecución

**Orden y paralelismo.** Las Tasks 1 y 2 son secuenciales y bloquean todo lo demás: la 1 produce el SHA que la 2 fija, y la 2 mueve las rutas sobre las que trabaja el resto. A partir de ahí, las Tasks 3, 8 y 9 son independientes entre sí y de la cadena 4→5→6→7→10, que sí es secuencial: la 5 necesita la familia declarada en la 4, la 6 usa las definiciones de la 5, la 7 mide después de que 5 y 6 añadieron, y la 10 evalúa el contenido final.

**Si el tiempo se acorta.** El corte con más valor por minuto es Task 3 sola: son cinco correcciones de texto, una de ellas un error calificado que hoy penaliza a quien responde bien. Se puede desplegar por su cuenta sin ninguna de las demás.

**Lo que este plan no toca.** El contenido conceptual completo (ELT y su historia económica, la L de Load, lakehouse, contratos, orquestación, linaje, costo, analytics engineer), la estructura «En corto» / «Qué te llevas», los `id` de página, las URLs, las rutas de `_assets/`, el PDF histórico y sus dos enlaces, el calendario, las tres tareas y la evaluación.
