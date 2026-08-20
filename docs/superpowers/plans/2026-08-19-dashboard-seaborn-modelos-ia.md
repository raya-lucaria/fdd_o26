# Dashboard Seaborn de modelos de IA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el dashboard SVG ilegible por cinco gráficas Seaborn docentes y cuatro gráficas opcionales auditables, legibles a 390 px.

**Architecture:** `tools/ai_model_dashboard.py` conserva los cálculos y añade view-models puros. `tools/gen_ai_model_dashboard.py` se convierte en el único escritor de SVG y bloques Markdown; un `FigureSpec` alimenta simultáneamente marcas, tablas y accesibilidad. Los assets quedan versionados para que Raya no dependa del entorno de plotting.

**Tech Stack:** Python 3.12.11, pandas, Seaborn, Matplotlib/Agg, PyYAML, SVG/XML, pytest, Playwright/Chromium, Raya.

**Spec:** `docs/superpowers/specs/2026-08-19-dashboard-seaborn-modelos-ia-design.md`

## Global Constraints

- Cinco SVG esenciales en la página principal y cuatro opcionales sólo en el anexo.
- Una pregunta y un eje Y por figura; máximo 12–15 marcas y cinco etiquetas en la ruta esencial.
- SVG único, texto preservado, fuente DejaVu Sans vendida y salida determinista.
- Ningún dato ausente se representa como cero; ningún modelo distinto se une mediante línea.
- Principal: 900–1,400 palabras y 8–12 viewports a 390×844; tablas docentes de dos columnas y 4–6 filas.
- Anexo: corpus completo, confianza, fuentes y una fila equivalente por marca.
- No editar ni versionar `artifact/`.

---

### Task 1: Entorno reproducible y contrato CI

**Files:**
- Create: `tools/ai_dashboard_requirements.in`
- Create: `tools/ai_dashboard_requirements.lock`
- Create: `tools/fonts/DejaVuSans.ttf`
- Create: `tools/fonts/LICENSE-DejaVu.txt`
- Modify: `.github/workflows/pages.yml`
- Test: `tools/test_ai_dashboard_environment.py`

**Interfaces:**
- Produces: entorno Python 3.12.11 instalable con hashes; jobs requeridos `dashboard-assets` y `course-build`.

- [ ] **Step 1: Escribir pruebas RED del contrato**

```python
def test_dashboard_lock_and_font_are_pinned():
    lock = (ROOT / "tools/ai_dashboard_requirements.lock").read_text()
    assert "seaborn==" in lock and "--hash=sha256:" in lock
    assert (ROOT / "tools/fonts/DejaVuSans.ttf").stat().st_size > 100_000

def test_pages_requires_dashboard_and_course_jobs():
    workflow = yaml.safe_load((ROOT / ".github/workflows/pages.yml").read_text())
    assert {"checks", "dashboard-assets", "course-build"} <= workflow["jobs"].keys()
```

- [ ] **Step 2: Ejecutar RED**

Run: `python3 -m pytest tools/test_ai_dashboard_environment.py -q`
Expected: FAIL por archivos/jobs ausentes.

- [ ] **Step 3: Crear input, lock transitivo, fuente y jobs**

```text
numpy
pandas
seaborn
matplotlib
pyyaml
pillow
```

Run: `uv pip compile --python-version 3.12 --generate-hashes tools/ai_dashboard_requirements.in -o tools/ai_dashboard_requirements.lock`

Los jobs instalan el lock, Playwright/Chromium y Raya en `dd1fdba4e16cb79fa5515eb689fabbc74014f3b6`; ningún gate requerido acepta skip.

- [ ] **Step 4: Ejecutar GREEN y validar YAML**

Run: `python3 -m pytest tools/test_ai_dashboard_environment.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/pages.yml tools/ai_dashboard_requirements.* tools/fonts tools/test_ai_dashboard_environment.py
git commit -m "chore(unidad-3): fija entorno del dashboard Seaborn"
```

### Task 2: View-model único, ausencias y selecciones docentes

**Files:**
- Modify: `tools/ai_model_dashboard.py`
- Test: `tools/test_ai_model_dashboard.py`
- Test: `tools/test_ai_dashboard_views.py`

**Interfaces:**
- Produces: `FigureSpec`, `FigureRow`, `AbsenceSummary`, `build_figure_specs(corpus) -> tuple[FigureSpec, ...]`.
- `FigureSpec.rows` alimenta tanto plotting como tablas; `compact_rows` es un subconjunto de `rows`.

- [ ] **Step 1: Escribir pruebas RED de nueve specs**

```python
def test_figure_specs_define_five_essential_and_four_optional(corpus):
    specs = build_figure_specs(corpus)
    assert len(specs) == 9
    assert sum(s.route == "essential" for s in specs) == 5
    assert sum(s.route == "annex" for s in specs) == 4
    assert all(4 <= len(s.compact_rows) <= 6 for s in specs if s.route == "essential")

def test_missing_training_compute_is_not_a_zero_mark(corpus):
    spec = spec_by_id(build_figure_specs(corpus), "training_flop")
    assert all(row.low > 0 for row in spec.rows)
    assert spec.absence.counts["UNDISCLOSED"] > 0
```

- [ ] **Step 2: Ejecutar RED**

Run: `python3 -m pytest tools/test_ai_dashboard_views.py -q`
Expected: FAIL al importar tipos nuevos.

- [ ] **Step 3: Implementar dataclasses y selección determinista**

```python
@dataclass(frozen=True)
class FigureRow:
    model_id: str
    label: str
    year: int
    low: float
    high: float
    unit: str
    status: str
    confidence: str
    scope: str
    source_ids: tuple[str, ...]

@dataclass(frozen=True)
class FigureSpec:
    figure_id: str
    filename: str
    route: Literal["essential", "annex"]
    question: str
    rows: tuple[FigureRow, ...]
    compact_ids: tuple[str, ...]
    direct_label_ids: tuple[str, ...]
    x_scale: Literal["year", "log_cost"]
    y_scale: Literal["linear", "log"]
    absence: AbsenceSummary | None
```

La selección ordena por año/model ID, limita marcas esenciales a 15 y usa desplazamientos simétricos derivados del índice estable.

- [ ] **Step 4: Probar invariantes, Pareto y permutaciones**

Run: `python3 -m pytest tools/test_ai_model_dashboard.py tools/test_ai_dashboard_views.py -q`
Expected: PASS, incluidos safe/possible/dominated reconstruidos desde bounds.

- [ ] **Step 5: Commit**

```bash
git add tools/ai_model_dashboard.py tools/test_ai_model_dashboard.py tools/test_ai_dashboard_views.py
git commit -m "feat(unidad-3): define vistas docentes del dashboard IA"
```

### Task 3: Render Seaborn determinista y accesible

**Files:**
- Rewrite: `tools/gen_ai_model_dashboard.py`
- Delete: `tools/gen_ai_dashboard_confidence.py`
- Create: `tools/test_ai_dashboard_seaborn.py`
- Modify: `tools/test_diagramas.py`

**Interfaces:**
- Consumes: `build_figure_specs()`.
- Produces: `render_figure(spec, path)`, `canonicalize_svg(path, spec)`, nueve SVG del manifiesto.

- [ ] **Step 1: Escribir pruebas RED de artistas y SVG**

```python
def test_renderer_has_no_cross_model_lines(essential_specs):
    fig = render_figure(essential_specs[0], None)
    assert not [line for ax in fig.axes for line in ax.lines if line.get_linestyle() not in {"None", "none"}]

def test_svg_has_one_accessible_identity(tmp_path, essential_specs):
    path = tmp_path / "figure.svg"
    write_svg(essential_specs[0], path)
    root = ET.parse(path).getroot()
    assert root.attrib["role"] == "img"
    assert len(root.findall("{http://www.w3.org/2000/svg}title")) == 1
    assert len(root.findall("{http://www.w3.org/2000/svg}desc")) == 1
```

- [ ] **Step 2: Ejecutar RED**

Run: `python3 -m pytest tools/test_ai_dashboard_seaborn.py -q`
Expected: FAIL porque el generador aún construye SVG manual.

- [ ] **Step 3: Implementar tema, scatter, intervalos y Pareto**

```python
matplotlib.use("Agg")
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "none",
    "svg.hashsalt": "fdd-o26-ai-dashboard",
})
ax = sns.scatterplot(data=frame, x="display_year", y="value", hue="status", style="role", estimator=None)
```

Usar `errorbar` sólo para `low/high`; Pareto usa rectángulos/barras sin unir candidatos. Postprocesar título/desc/ARIA y metadatos con orden estable.

- [ ] **Step 4: Regenerar dos veces y comprobar bytes**

Run: `python3 tools/gen_ai_model_dashboard.py && sha256sum course/3_arquitectura_de_computadoras/_assets/ai-dashboard-*.svg > /tmp/a && python3 tools/gen_ai_model_dashboard.py && sha256sum course/3_arquitectura_de_computadoras/_assets/ai-dashboard-*.svg > /tmp/b && diff -u /tmp/a /tmp/b`
Expected: sin diff.

- [ ] **Step 5: Ejecutar pruebas del renderer**

Run: `python3 -m pytest tools/test_ai_dashboard_seaborn.py tools/test_diagramas.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/gen_ai_model_dashboard.py tools/test_ai_dashboard_seaborn.py tools/test_diagramas.py course/3_arquitectura_de_computadoras/_assets/ai-dashboard-*.svg
git rm tools/gen_ai_dashboard_confidence.py
git commit -m "feat(unidad-3): renderiza dashboard IA con Seaborn"
```

### Task 4: Ruta esencial, anexo y tablas generadas

**Files:**
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/1_evidencia_dashboard/0_index.md`
- Modify: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`
- Modify: `tools/gen_ai_model_dashboard.py`
- Modify: `tools/test_arquitectura.py`
- Modify: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- Consumes: nueve `FigureSpec` y SVG.
- Produces: bloques `AI_DASHBOARD:<id>:START/END` y navegación principal→anexo.

- [ ] **Step 1: Escribir pruebas RED de contenido y migración**

```python
def test_main_has_five_essential_figures_and_no_master_ledger():
    text = MAIN.read_text()
    assert text.count("ai-dashboard-") == 5
    assert "Fin de la ruta esencial" in text
    assert "39 modelos" not in dashboard_main_section(text)

def test_retired_assets_have_no_active_consumers():
    for basename in RETIRED:
        assert not active_consumer_hits(basename)
        assert not (ASSETS / basename).exists()
```

- [ ] **Step 2: Ejecutar RED**

Run: `python3 -m pytest tools/test_arquitectura.py -q`
Expected: FAIL por 12 embeds y ledger principal.

- [ ] **Step 3: Generar narrativa y tablas desde sentinelas**

Cada bloque escribe pregunta, SVG, conclusión, `Di esto`, `No concluyas esto`, tabla de 4–6 filas y enlace a ancla. El anexo recibe cuatro visuales opcionales, tabla maestra y filas completas de nueve specs.

- [ ] **Step 4: Actualizar créditos y retirar exactamente 12 assets**

Run: `git rm course/3_arquitectura_de_computadoras/_assets/{ai-training-parameters,ai-training-flop,ai-training-accelerators,ai-training-power,ai-training-replacement-value,ai-inference-parameters,ai-inference-memory,ai-inference-accelerators,ai-inference-power,ai-inference-capex,ai-pareto-training,ai-pareto-inference}.svg`

- [ ] **Step 5: Regenerar y probar equivalencia**

Run: `python3 tools/gen_ai_model_dashboard.py && python3 -m pytest tools/test_arquitectura.py tools/test_ai_hardware_costs.py -q && git diff --exit-code`
Expected: PASS y regeneración limpia.

- [ ] **Step 6: Commit**

```bash
git add course/3_arquitectura_de_computadoras tools/gen_ai_model_dashboard.py tools/test_arquitectura.py tools/test_ai_hardware_costs.py
git commit -m "docs(unidad-3): ordena dashboard IA para lectura docente"
```

### Task 5: DOM móvil, geometría y accesibilidad real

**Files:**
- Rewrite: `tools/test_ai_dashboard_dom.py`
- Modify: `tools/test_ai_dashboard_seaborn.py`

**Interfaces:**
- Consumes: artifact Raya construido y nueve SVG.
- Produces: gate Chromium no opcional para 390×844 y 1440×900.

- [ ] **Step 1: Escribir pruebas RED contra el DOM construido**

```python
@pytest.mark.parametrize("viewport", [{"width": 390, "height": 844}, {"width": 1440, "height": 900}])
def test_dashboard_is_readable(page, built_site, viewport):
    page.set_viewport_size(viewport)
    page.goto(built_site)
    assert page.evaluate("document.documentElement.scrollWidth") == viewport["width"]
    assert page.locator("main img[src*='ai-dashboard-']").count() == 5
    assert min(rendered_svg_font_sizes(page)) >= 16
    assert not intersecting_text_boxes(page)
```

- [ ] **Step 2: Ejecutar RED contra el sitio actual**

Run: `python3 -m pytest tools/test_ai_dashboard_dom.py -q`
Expected: FAIL si persiste cualquier miniatura, colisión o conteo viejo.

- [ ] **Step 3: Ajustar dimensiones, labels y tablas sin ocultar datos**

Modificar `FigureSpec`/renderer, no el SVG generado. Mantener una figura por fila móvil y claves Pareto vinculadas a tabla.

- [ ] **Step 4: Ejecutar GREEN en ambas páginas**

Run: `python3 -m pytest tools/test_ai_dashboard_dom.py tools/test_ai_dashboard_seaborn.py -q`
Expected: PASS sin skips.

- [ ] **Step 5: Commit**

```bash
git add tools/test_ai_dashboard_dom.py tools/test_ai_dashboard_seaborn.py tools/ai_model_dashboard.py tools/gen_ai_model_dashboard.py course/3_arquitectura_de_computadoras
git commit -m "fix(unidad-3): asegura legibilidad móvil del dashboard IA"
```

### Task 6: Auditoría adversarial y release

**Files:**
- No source changes planned; any verified finding reopens the owning task and its listed files.

**Interfaces:**
- Produces: migración aprobada, publicada y comprobada en producción.

- [ ] **Step 1: Ejecutar todos los gates frescos**

Run: `python3 -m pytest tools/ -q`
Expected: PASS sin skips de gates requeridos.

Run: `UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ../fdd_o26 && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ../fdd_o26 && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect ../fdd_o26/artifact`
Expected: exit 0.

- [ ] **Step 2: Solicitar revisiones adversariales independientes**

Revisores: matemáticas/evidencia, visual/ADHD, accesibilidad/DOM e ingeniería/release. Cada uno devuelve `APPROVE` o hallazgos con archivo/línea; corregir por TDD y repetir hasta aprobación.

- [ ] **Step 3: Verificar migración y registrar SHA previo**

```bash
git fetch origin
git status --short
git rev-parse origin/main
git diff --check
```

Expected: worktree limpio y `origin/main` ancestro del HEAD.

- [ ] **Step 4: Publicar main y monitorear**

```bash
git push origin main
gh run watch --exit-status
```

Expected: `checks`, `dashboard-assets`, `course-build` y Pages exitosos para el HEAD exacto.

- [ ] **Step 5: Verificar producción**

Comprobar HTTP 200 y contenido para página principal, anexo y nueve assets; medir nuevamente 390/1440 contra producción.

- [ ] **Step 6: Revertir si falla el release**

```bash
MIGRATION_SHA=$(git rev-parse HEAD)
git revert "$MIGRATION_SHA"
git push origin main
gh run watch --exit-status
```

Expected: Pages vuelve al dashboard anterior sin editar `artifact/` ni force-push.
