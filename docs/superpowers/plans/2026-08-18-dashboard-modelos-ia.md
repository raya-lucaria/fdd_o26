# Dashboard comparativo de modelos de IA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el expediente técnico actual por un dashboard docente con 30–35 modelos, diez gráficas temporales, dos fronteras de Pareto y un anexo técnico completo.

**Architecture:** El ledger YAML seguirá siendo la fuente de verdad. Un módulo puro validará y derivará series y fronteras; un generador determinista producirá doce SVG y tablas equivalentes. La página principal presentará sólo conclusiones y comparaciones, mientras un subdirectorio renderizado conservará metodología, fuentes, IDs y cuentas exactas.

**Tech Stack:** Markdown/Raya, YAML, Python 3, `Decimal`, pytest, SVG accesible, Epoch ECI, Chromium/Playwright y Raya CLI.

**Spec:** `docs/superpowers/specs/2026-08-18-dashboard-modelos-ia-design.md`

## Global Constraints

- La tabla maestra contendrá al menos 30 modelos y cubrirá OpenAI, Anthropic, Google/DeepMind, Meta, DeepSeek, Qwen, Kimi, Mistral y xAI.
- Cada gráfica temporal usa año en X; las magnitudes de varios órdenes usan Y logarítmica.
- Cada celda es `FACT`, `DERIVED`, `ESTIMATE`, `SCENARIO`, `UNDISCLOSED_BY_CREATOR`, `NOT_FOUND`, `ESTIMATION_NOT_IDENTIFIABLE` o `NOT_APPLICABLE`.
- Los modelos cerrados permanecen visibles, pero no reciben parámetros, hardware o costos inventados.
- Entrenamiento, capacidad de inferencia, operación medida, API y CAPEX no se mezclan.
- ECI se rotula “capacidad general según ECI”, nunca inteligencia o IQ; LiveBench sólo sirve como sensibilidad separada.
- La ruta principal tiene 900–1,400 palabras y 8–12 pantallas móviles; IDs, fórmulas y evidencia completa viven en el anexo.
- En móvil, la ruta principal usa una o dos columnas; no usa `overflow-wrap:anywhere` para comprimir contenido.
- Los SVG tienen texto efectivo ≥16 px a 390 px, codificación redundante, `title`, `desc`, alt, fallback y `data-source-ids`.
- Los doce SVG son deterministas y se generan desde el ledger; nunca se editan manualmente.

---

### Task 1: Corpus amplio y snapshots verificables

**Files:**
- Modify: `tools/data/ai_hardware_costs.yaml`
- Modify: `tools/test_ai_hardware_costs.py`
- Create: `tools/data/eci_snapshot_2026-08-18.yaml`

**Interfaces:**
- Produces: `dashboard_models`, `dashboard_training_series`, `dashboard_inference_series`, `benchmark_snapshots`.
- Produces: IDs estables `DM_*`, revisiones de artefacto y métricas con evidencia por celda.

- [ ] **Step 1: Escribir la prueba roja de cobertura**

```python
REQUIRED_ORGS = {
    "OpenAI", "Anthropic", "Google", "Meta", "DeepSeek",
    "Qwen", "Moonshot AI", "Mistral AI", "xAI",
}

def test_dashboard_corpus_is_broad_and_cell_evidenced():
    data = load_yaml(DATA)
    models = data["dashboard_models"]
    assert 30 <= len(models) <= 40
    assert REQUIRED_ORGS <= {model["organization"] for model in models}
    assert len({model["id"] for model in models}) == len(models)
    for model in models:
        assert model["year"]["value"] in range(2018, 2027)
        for metric in model["metrics"].values():
            assert metric["status"] in ALLOWED
            assert metric.get("source_ids") or metric["status"] in NEGATIVE_STATES
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_ai_hardware_costs.py -q -k dashboard_corpus`

Expected: FAIL porque `dashboard_models` y el snapshot ECI aún no existen.

- [ ] **Step 3: Registrar identidades y métricas de entrenamiento**

Añadir 30–35 filas del corpus de la especificación. Cada fila incluye organización, nombre canónico, año, variante, open/closed, dense/MoE, parámetros totales/activos, tokens, FLOP de entrenamiento, chips, accelerator-hours, base de potencia y fecha de entrenamiento. Reutilizar IDs de fuentes existentes y añadir fuentes primarias nuevas.

Para densos con `N` y `T` publicados:

```yaml
training_flop:
  value: "7.78e24"
  unit: FLOP
  status: DERIVED
  formula: "6 * total_parameters * training_tokens"
  input_metric_ids: [parameters_total, training_tokens]
  source_ids: [S_QWEN25_REPORT]
```

Para MoE, `6NT_activo` será `ESTIMATE` con `low`, `high` y supuestos; nunca `DERIVED` exacto.

- [ ] **Step 4: Registrar capacidad de inferencia**

Para artefactos abiertos, registrar revisión/commit, bytes cuando existan, piso BF16/FP8/INT8/INT4 y parámetros totales. Para modelos cerrados:

```yaml
artifact_bytes:
  value: null
  unit: byte
  status: UNDISCLOSED_BY_CREATOR
  corpus_checked: [S_CREATOR_MODEL_CARD]
```

No poblar GPU, watts o CAPEX desde precio API o hardware de entrenamiento.

- [ ] **Step 5: Fijar el snapshot ECI**

Guardar modelo/variante exacta, score, intervalo, fecha del snapshot, URL y revisión/dataset de Epoch. La prueba exige correspondencia exacta entre `benchmark_model_id` y `DM_*`; variantes sin match quedan fuera de Pareto.

- [ ] **Step 6: Añadir resultados negativos verificables**

Cada `NOT_FOUND`/`UNDISCLOSED` cita documentos exactos revisados por modelo. Prohibir aliases de corpus compartidos entre organizaciones.

- [ ] **Step 7: Verificar y commit**

```bash
python3 -m pytest tools/test_ai_hardware_costs.py -q
git add tools/data/ai_hardware_costs.yaml tools/data/eci_snapshot_2026-08-18.yaml tools/test_ai_hardware_costs.py
git commit -m "data(unidad-3): amplía corpus comparativo de IA"
```

---

### Task 2: Series derivadas y fronteras de Pareto

**Files:**
- Create: `tools/ai_model_dashboard.py`
- Create: `tools/test_ai_model_dashboard.py`

**Interfaces:**
- `build_training_series(ledger: dict) -> dict[str, list[PlotPoint]]`
- `build_inference_series(ledger: dict, scenario: CapacityScenario) -> dict[str, list[PlotPoint]]`
- `pareto_frontier(points: list[ParetoPoint]) -> ParetoResult`
- `CapacityScenario(hbm_gb=Decimal("80"), tdp_w=Decimal("700"), unit_price_usd=Decimal("30000"), precision="BF16")`.
- `PlotPoint(model_id: str, year: int, value: Decimal, unit: str, status: str, low: Decimal | None, high: Decimal | None, source_ids: tuple[str, ...], label: str, claim_scope: str)`.
- `ParetoPoint(model_id: str, cost_low: Decimal, cost_high: Decimal, score_low: Decimal, score_high: Decimal)`.
- `ParetoResult(safe_ids: tuple[str, ...], possible_ids: tuple[str, ...])`.

- [ ] **Step 1: Escribir pruebas rojas de series**

```python
def test_training_series_keep_missing_models_out_of_log_axes():
    series = build_training_series(sample_ledger())
    assert [p.model_id for p in series["parameters_total"]] == ["DM_A", "DM_B"]
    assert [p.model_id for p in series["training_flop"]] == ["DM_A"]
    assert all(p.value > 0 for points in series.values() for p in points)

def test_inference_scenario_is_capacity_not_sla():
    point = build_inference_series(sample_ledger(), CapacityScenario())["capex_equivalent"][0]
    assert point.value == Decimal("60000")
    assert point.status == "SCENARIO"
    assert point.claim_scope == "capacity_floor_not_sla"
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_ai_model_dashboard.py -q`

Expected: FAIL con `ModuleNotFoundError: ai_model_dashboard`.

- [ ] **Step 3: Implementar series de entrenamiento**

Crear `PlotPoint` inmutable. Producir exactamente: `parameters_total_active`, `training_flop`, `accelerators_and_hours`, `power_or_energy_envelope`, `replacement_value`. Rechazar valores no positivos en log, mezclar GPU-h/TPU-h y combinar bases de potencia incompatibles.

- [ ] **Step 4: Implementar series de inferencia**

Producir: `artifact_or_weight_floor`, `h100_capacity_equivalents`, `accelerator_tdp_scenario`, `accelerator_capex_scenario`, `parameters_total_active`. Usar `ceil(bytes / 80e9)` sólo como piso físico; guardar `claim_scope` y no emitir throughput.

- [ ] **Step 5: Escribir pruebas rojas de Pareto**

```python
def test_pareto_marks_safe_and_possible_frontiers():
    result = pareto_frontier([
        ParetoPoint("A", cost_low=10, cost_high=12, score_low=70, score_high=72),
        ParetoPoint("B", cost_low=20, cost_high=22, score_low=69, score_high=71),
        ParetoPoint("C", cost_low=18, cost_high=30, score_low=71, score_high=75),
    ])
    assert result.safe_ids == ("A",)
    assert set(result.possible_ids) == {"A", "C"}
```

- [ ] **Step 6: Implementar dominancia con intervalos**

Frontera segura exige dominancia por extremos adversos; frontera posible evalúa si existe una realización no dominada. Orden estable por costo y año. Prohibir comparar filas sin ECI o costo.

- [ ] **Step 7: Verificar y commit**

```bash
python3 -m pytest tools/test_ai_model_dashboard.py -q
git add tools/ai_model_dashboard.py tools/test_ai_model_dashboard.py
git commit -m "feat(unidad-3): calcula series y Pareto de IA"
```

---

### Task 3: Doce SVG temporales y Pareto

**Files:**
- Create: `tools/gen_ai_model_dashboard.py`
- Modify: `tools/test_diagramas.py`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-dashboard-*.svg` (12 archivos generados)
- Modify: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`

**Interfaces:**
- `render_dashboard(ledger_path: Path, eci_path: Path, assets_dir: Path) -> list[Path]`
- Produces: cinco `ai-training-*`, cinco `ai-inference-*`, `ai-pareto-training.svg`, `ai-pareto-inference.svg`.

- [ ] **Step 1: Escribir prueba roja del contrato de assets**

```python
EXPECTED = {
    "ai-training-parameters.svg", "ai-training-flop.svg",
    "ai-training-accelerators.svg", "ai-training-power.svg",
    "ai-training-replacement-value.svg", "ai-inference-memory.svg",
    "ai-inference-accelerators.svg", "ai-inference-power.svg",
    "ai-inference-capex.svg", "ai-inference-parameters.svg",
    "ai-pareto-training.svg", "ai-pareto-inference.svg",
}

def test_dashboard_generator_produces_exactly_twelve_assets(tmp_path):
    produced = render_dashboard(DATA, ECI, tmp_path)
    assert {path.name for path in produced} == EXPECTED
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_diagramas.py -q -k dashboard`

- [ ] **Step 3: Implementar composición temporal mobile-first**

ViewBox máximo 640, título y nota fuera de la región de datos, año en X, ticks Y logarítmicos, bandas de estimación, marcas redundantes y etiquetas directas seleccionadas. Serializar `data-model-id`, `data-status`, `data-source-ids`, valor y unidad.

- [ ] **Step 4: Implementar Pareto**

Paneles muestran todos los puntos identificables, frontera segura sólida y posible punteada. Ejes dicen `CAPEX/valor de reemplazo` y `Capacidad general ECI`; nunca `inteligencia`. Incluir snapshot ECI en `desc` y fallback.

- [ ] **Step 5: Probar semántica y geometría**

```python
def test_dashboard_svg_is_mobile_legible_and_not_color_only(path):
    root = ET.parse(path).getroot()
    width = float(root.attrib["viewBox"].split()[2])
    scale = min(1, 390 / width)
    sizes = [float(n.attrib["font-size"]) for n in root.iter() if "font-size" in n.attrib]
    assert min(sizes) * scale >= 16
    assert {n.attrib["data-status"] for n in root.iter() if "data-status" in n.attrib}
    assert all("data-source-ids" in n.attrib for n in quantitative_nodes(root))
```

Añadir test Chromium/getBBox sobre casos de etiqueta larga y bandas; no limitarlo a assets committed.

- [ ] **Step 6: Probar determinismo y commit**

```bash
python3 tools/gen_ai_model_dashboard.py
python3 -m pytest tools/test_diagramas.py tools/test_ai_model_dashboard.py -q
git diff --check
git add tools/gen_ai_model_dashboard.py tools/test_diagramas.py course/3_arquitectura_de_computadoras/_assets
git commit -m "feat(unidad-3): genera dashboard temporal y Pareto"
```

---

### Task 4: Página principal enseñable y anexo técnico

**Files:**
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`
- Create: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/1_evidencia_dashboard/0_index.md`
- Modify: `tools/test_arquitectura.py`
- Modify: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- Main route embeds 12 SVG and links `[[evidencia-dashboard-ia]]`.
- Annex owns full cell-level tables, formulas, sources and negative results.

- [ ] **Step 1: Escribir guardas editoriales rojas**

```python
def test_dashboard_main_route_is_short_visual_and_model_rich():
    main = dashboard_section(body(AI_PAGE))
    assert 900 <= len(main.split()) <= 1400
    expected_assets = {
        "ai-training-parameters.svg", "ai-training-flop.svg",
        "ai-training-accelerators.svg", "ai-training-power.svg",
        "ai-training-replacement-value.svg", "ai-inference-memory.svg",
        "ai-inference-accelerators.svg", "ai-inference-power.svg",
        "ai-inference-capex.svg", "ai-inference-parameters.svg",
        "ai-pareto-training.svg", "ai-pareto-inference.svg",
    }
    assert {name for name in expected_assets if name in main} == expected_assets
    assert "[[evidencia-dashboard-ia]]" in main
    assert "data-source-ids" not in main
    assert not re.search(r"\b(?:S|DM|T|V)_[A-Z0-9_]{4,}\b", main)

def test_dashboard_annex_preserves_complete_evidence():
    annex = body(DASHBOARD_ANNEX)
    for model in load_yaml(DATA)["dashboard_models"]:
        assert model["id"] in annex
    assert "Metodología de frontera de Pareto" in annex
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_arquitectura.py -q -k dashboard`

- [ ] **Step 3: Reemplazar, no acumular, el bloque actual**

Eliminar desde `## Costo físico del hardware` hasta antes de la práctica/cierre correspondiente. Escribir ruta de 8–12 pantallas: tarjeta “En 30 segundos”, tabla maestra compacta, entrenamiento, inferencia, Pareto, advertencias y recapitulación. Cada gráfica recibe máximo tres frases.

- [ ] **Step 4: Crear tabla maestra mobile-first**

Dividir por tarjetas/familias; máximo dos columnas en móvil. Mostrar modelos cerrados con ausencia explícita, no filas gigantes. El resumen debe permitir encontrar organización, año, open/closed, arquitectura y estado de entrenamiento/inferencia.

- [ ] **Step 5: Crear anexo completo**

Mover/reescribir todas las derivaciones auditadas: estados, IDs, fechas, entrenamiento, potencia, valoraciones, artefactos, inferencia, ECI, Pareto y fuentes. Usar registros verticales por modelo y encabezados de reentrada.

- [ ] **Step 6: Probar ausencia de duplicación**

La prueba cuenta cada resultado principal una sola vez en la ruta oral y exige que su precisión completa exista en el anexo. Prohibir las cinco gráficas anteriores de costos si quedaron reemplazadas y retirar sus embeds/créditos sólo cuando no tengan consumidores.

- [ ] **Step 7: Verificar y commit**

```bash
python3 -m pytest tools/test_arquitectura.py tools/test_ai_hardware_costs.py -q
git add course/3_arquitectura_de_computadoras/4_ai_escala_y_decision tools/test_arquitectura.py tools/test_ai_hardware_costs.py
git commit -m "docs(unidad-3): convierte costos IA en dashboard docente"
```

---

### Task 5: Auditoría adversarial, render y publicación

**Files:**
- Modify: `tools/data/ai_hardware_costs.yaml`
- Modify: `tools/data/eci_snapshot_2026-08-18.yaml`
- Modify: `tools/ai_model_dashboard.py`
- Modify: `tools/gen_ai_model_dashboard.py`
- Modify: `tools/test_ai_model_dashboard.py`
- Modify: `tools/test_ai_hardware_costs.py`
- Modify: `tools/test_diagramas.py`
- Modify: `tools/test_arquitectura.py`
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/1_evidencia_dashboard/0_index.md`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-training-parameters.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-training-flop.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-training-accelerators.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-training-power.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-training-replacement-value.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-inference-memory.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-inference-accelerators.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-inference-power.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-inference-capex.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-inference-parameters.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-pareto-training.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/ai-pareto-inference.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`

**Interfaces:**
- Produces: cuatro revisiones `APPROVE`, artifact válido, producción con el commit final.

- [ ] **Step 1: Ejecutar cuatro revisiones adversariales**

Revisores independientes:

1. evidencia y actualidad;
2. matemáticas, unidades y Pareto;
3. pedagogía/ADHD y densidad;
4. accesibilidad/visual/móvil.

Resolver todos los Critical/Important y repetir revisión focal.

- [ ] **Step 2: Verificación completa**

```bash
python3 -m pytest tools/ -q
python3 tools/gen_ai_model_dashboard.py
git diff --check
```

Desde Raya pinned:

```bash
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate /home/uumami/itam/fdd_o26/.worktrees/ai-hardware-costs
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build /home/uumami/itam/fdd_o26/.worktrees/ai-hardware-costs
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect /home/uumami/itam/fdd_o26/.worktrees/ai-hardware-costs/artifact
```

- [ ] **Step 3: Chromium móvil y escritorio**

A 390×844 y 1440×900 comprobar:

- `scrollWidth == clientWidth`;
- ruta principal de 8–12 pantallas;
- 12 SVG cargados, texto efectivo ≥16 px y `getBBox` sin recorte;
- ninguna tabla principal >2 columnas en móvil ni palabra partida carácter por carácter;
- anexo navegable y puntos de reentrada;
- frontera segura/posible y leyenda entendibles sin color.

- [ ] **Step 4: Simular lectura**

Profesor novato debe narrar la ruta en 20–30 minutos; estudiante ADHD debe recuperar el punto después de cada encabezado; estudiante técnico debe reproducir cualquier cifra desde el anexo.

- [ ] **Step 5: Commit, push y producción**

```bash
git add course/3_arquitectura_de_computadoras tools
git commit -m "fix(unidad-3): cierra auditoría del dashboard IA"
git push origin main
gh run list --limit 3
```

Monitorear Pages hasta `success`. Verificar la página principal, anexo y doce SVG con HTTP 200 y confirmar que producción contiene el commit.
