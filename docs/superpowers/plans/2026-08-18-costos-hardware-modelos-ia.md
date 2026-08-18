# Costos de hardware para modelos de IA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir una comparación verificable y visual de aceleradores, HBM, FLOP/s, watts y CAPEX para entrenamientos documentados, modelos actuales y escenarios de inferencia.

**Architecture:** Un ledger YAML conservará cada cifra, estado, fuente, unidad y frontera. Un módulo Python validará y derivará magnitudes; un generador consumirá el ledger para producir SVG. Pruebas cruzadas impedirán que datos, texto y visuales diverjan.

**Tech Stack:** Markdown de Raya, YAML, Python 3, pytest, SVG accesible, Chromium/Playwright y Raya CLI.

**Spec:** `docs/superpowers/specs/2026-08-18-costos-hardware-modelos-ia-design.md`

## Global Constraints

- Corte `2026-08-18`; fuentes primarias por afirmación; secundarios sólo como corroboración.
- Excluir rumores, filtraciones, API, electricidad, personal, datos y edificios de CAPEX.
- Evidencia por cifra: `FACT`, `DERIVED`, `ESTIMATE`, `SCENARIO`, `UNDISCLOSED_BY_CREATOR`, `NOT_FOUND`, `ESTIMATION_NOT_IDENTIFIABLE` o `NOT_APPLICABLE`.
- `accelerator-only` y `system-based` son fronteras mutuamente excluyentes.
- Separar FLOP/FLOP/s, HBM instalada/utilizable y potencia GPU/servidor/cluster/sitio.
- Un modelo cerrado sin observables suficientes no recibe un rango atribuido.
- Tablas y SVG sin overflow a 390 px; texto SVG renderizado ≥16 px.

---

### Task 1: Ledger de evidencia y corpus

**Files:**
- Create: `tools/data/ai_hardware_costs.yaml`
- Create: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- Produces: claves YAML `cutoff`, `sources`, `hardware`, `models`, `training_cases`, `inference_scenarios`, `valuations`.
- Produces: IDs `S_*`, `H_*`, `M_*`, `T_*`, `V_*` para cálculos, tablas y SVG.

- [ ] **Step 1: Escribir la prueba fallida del esquema**

```python
ALLOWED = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO",
           "UNDISCLOSED_BY_CREATOR", "NOT_FOUND",
           "ESTIMATION_NOT_IDENTIFIABLE", "NOT_APPLICABLE"}

def test_ledger_has_cutoff_and_cell_level_evidence():
    data = load_yaml(DATA)
    assert data["cutoff"] == "2026-08-18"
    assert {"sources", "hardware", "models", "training_cases",
            "inference_scenarios", "valuations"} <= data.keys()
    for case in data["training_cases"]:
        for field in case["metrics"].values():
            assert field["status"] in ALLOWED
            assert field.get("source_ids") or field["status"] in {
                "NOT_FOUND", "ESTIMATION_NOT_IDENTIFIABLE", "NOT_APPLICABLE"}
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_ai_hardware_costs.py -q`

Expected: FAIL porque el ledger no existe.

- [ ] **Step 3: Crear el esquema completo**

```yaml
cutoff: "2026-08-18"
sources:
  S_META_LLAMA31:
    claim_owner: model_creator
    title: "The Llama 3 Herd of Models"
    url: "https://ai.meta.com/research/publications/the-llama-3-herd-of-models/"
    accessed: "2026-08-18"
    primary_for: [training_hardware, accelerator_hours]
models:
  - id: M_LLAMA31_405B
    canonical_name: "Llama 3.1 405B"
    availability: open_weights
    source_ids: [S_META_LLAMA31]
```

- [ ] **Step 4: Investigar el corpus mínimo**

Cubrir OpenAI, Anthropic, Gemini, Kimi, Qwen, GPT-3, BLOOM, PaLM, Llama 3.1 405B y DeepSeek-V3. Revisar anuncio, model/system card, paper, repositorio/configuración y fabricante. Registrar alcance, parámetros, tokens, aceleradores concurrentes, accelerator-hours, duración, precisión y cómputo publicado. Registrar resultados negativos con su estado; nunca usar snippets de buscador.

- [ ] **Step 5: Registrar valoraciones**

Cada precio declara unidad transable, cantidad mínima, fecha, región, moneda, condición, canal, impuestos, soporte y componentes. Separar precio histórico y reposición.

- [ ] **Step 6: Verificar y commit**

```bash
python3 -m pytest tools/test_ai_hardware_costs.py -q
git add tools/data/ai_hardware_costs.yaml tools/test_ai_hardware_costs.py
git commit -m "data(unidad-3): documenta evidencia de hardware IA"
```

---

### Task 2: Motor de cálculos y fronteras

**Files:**
- Create: `tools/ai_hardware_costs.py`
- Modify: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- `installed_hbm_gb(count, hbm_gb) -> Decimal`
- `peak_rate_tflops(count, per_chip_tflops, convention) -> Decimal`
- `aggregate_peaks(entries) -> Decimal`, sólo para entradas con la misma convención de precisión, sparsity y acumulación.
- `accelerator_hours(count, wall_hours) -> Decimal`
- `accelerator_capex(count, unit_price_usd) -> Decimal`
- `system_capex(systems, system_price_usd, network_parts) -> Decimal`
- `weight_floor_gb(parameters, bits) -> Decimal`

- [ ] **Step 1: Escribir pruebas fallidas dimensionales**

```python
def test_eight_accelerator_example():
    assert installed_hbm_gb(8, 80) == Decimal("640")
    assert accelerator_hours(8, 24) == Decimal("192")
    assert accelerator_capex(8, 30000) == Decimal("240000")

def test_system_capex_counts_each_component_once():
    network = [(2, Decimal("12000")), (1, Decimal("8000"))]
    assert system_capex(4, Decimal("400000"), network) == Decimal("1632000")

def test_mixed_peak_conventions_are_rejected():
    with pytest.raises(ValueError, match="homogeneous peak convention"):
        aggregate_peaks([{"precision": "BF16"}, {"precision": "FP8"}])
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_ai_hardware_costs.py -q`

- [ ] **Step 3: Implementar con `Decimal`**

```python
def installed_hbm_gb(count: int, hbm_gb: Decimal) -> Decimal:
    return Decimal(count) * Decimal(hbm_gb)

def system_capex(systems: int, price: Decimal,
                 network_parts: list[tuple[int, Decimal]]) -> Decimal:
    return Decimal(systems) * price + sum(
        Decimal(quantity) * unit_price
        for quantity, unit_price in network_parts
    )
```

Validar no negativos, precisión, dense/sparse, acumulación, hardware homogéneo, `price_basis` y exclusión mutua de fronteras.

- [ ] **Step 4: Probar conversiones y semántica**

Añadir casos `1000 W = 1 kW`, `1000 kW = 1 MW`, `32 bits = 4 bytes`, GB/GiB y la prohibición de etiquetar accelerator-hours como kWh o pico×tiempo como trabajo real.

- [ ] **Step 5: Verificar y commit**

```bash
python3 -m pytest tools/test_ai_hardware_costs.py -q
git add tools/ai_hardware_costs.py tools/test_ai_hardware_costs.py
git commit -m "feat(unidad-3): calcula fronteras de hardware IA"
```

---

### Task 3: Tablas docentes de entrenamiento

**Files:**
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`
- Modify: `tools/test_arquitectura.py`
- Modify: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- Consumes: ledger y cálculos de Tasks 1–2.
- Produces: `Costo físico del hardware`, `Casos con hardware documentado`, `Modelos actuales: hechos y límites`, `Escenarios equivalentes, no entrenamientos atribuidos`.

- [ ] **Step 1: Escribir guardas editoriales en rojo**

```python
def test_ai_hardware_tables_separate_facts_from_scenarios():
    section = body(PAGES[4]).split("## Costo físico del hardware", 1)[1]
    assert "8 × 80 GB = 640 GB" in section
    assert "8 × USD 30,000 = USD 240,000" in section
    assert "Casos con hardware documentado" in section
    assert "Modelos actuales: hechos y límites" in section
    assert "Escenarios equivalentes, no entrenamientos atribuidos" in section
    assert "ESTIMATION_NOT_IDENTIFIABLE" in section
```

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_arquitectura.py -q -k ai_hardware_tables`

- [ ] **Step 3: Reemplazar, no acumular, la tabla actual**

Eliminar la tabla que mezcla API y hardware. Abrir con un acelerador concreto y cuentas visibles de HBM física, pico BF16, potencia nominal y CAPEX `accelerator-only`; explicar qué no demuestran esas sumas.

- [ ] **Step 4: Crear tabla esencial y ledger visible**

Tabla principal: modelo/alcance, hardware concurrente, accelerator-hours o duración, HBM física, potencia nominal y CAPEX/base. Subtablas: parámetros/tokens, precisión, FLOP publicado, MFU y IDs. Cada cifra conserva estado propio.

- [ ] **Step 5: Separar modelos actuales y escenarios**

Verificar nombres al corte. Para cerrados, mostrar hechos y `ESTIMATION_NOT_IDENTIFIABLE`; para abiertos, datos reproducibles. Los `SCENARIO` viven en otra tabla y nunca dicen “el modelo costó”.

- [ ] **Step 6: Verificar y commit**

```bash
python3 -m pytest tools/test_arquitectura.py tools/test_ai_hardware_costs.py -q
git add course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md tools/test_arquitectura.py tools/test_ai_hardware_costs.py
git commit -m "docs(unidad-3): compara hardware de entrenamiento IA"
```

---

### Task 4: Inferencia de capacidad y operación

**Files:**
- Modify: `tools/data/ai_hardware_costs.yaml`
- Modify: `tools/ai_hardware_costs.py`
- Modify: `tools/test_ai_hardware_costs.py`
- Modify: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`

**Interfaces:**
- `inference_capacity_floor(parameters, bits, quant_overhead, runtime_gb, kv_gb, workspace_gb, reserve_fraction) -> dict[str, Decimal]`
- Produces: tabla `cabe, sin SLA`; tabla operacional sólo con mediciones conjuntas compatibles.

- [ ] **Step 1: Escribir prueba fallida por componentes**

```python
def test_capacity_floor_keeps_components_visible():
    result = inference_capacity_floor(
        parameters=Decimal("35e9"), bits=8,
        quant_overhead=Decimal("0.15"), runtime_gb=Decimal("4"),
        kv_gb=Decimal("8"), workspace_gb=Decimal("4"),
        reserve_fraction=Decimal("0.10"))
    assert result["weights_gb"] == Decimal("35")
    assert result["quantized_weights_gb"] == Decimal("40.25")
    assert result["before_reserve_gb"] == Decimal("56.25")
```

- [ ] **Step 2: Confirmar RED e implementar**

Run: `python3 -m pytest tools/test_ai_hardware_costs.py -q -k capacity_floor`

Implementar pesos, escalas/metadata, runtime, KV, workspace y reserva como componentes separados.

- [ ] **Step 3: Investigar artefactos abiertos versionados**

Registrar tamaño real, dtype, escalas, runtime/versión, KV para contexto/batch y topologías adquiribles. Si sólo hay aritmética de pesos, decir `piso de almacenamiento`, no GPU mínima.

- [ ] **Step 4: Crear tabla de capacidad**

Columnas: artefacto, formato, pesos, metadata, runtime, KV, workspace, reserva, total y sistema mínimo; etiqueta visible “cabe, sin SLA”.

- [ ] **Step 5: Aplicar regla operacional**

Escenario: 16 concurrentes, 2,048 entrada, 256 salida, 100 output tokens/s, TTFT p95 ≤2 s, utilización ≤70 %, N servidores +1 en otro dominio. Sólo calcular CAPEX con throughput y TTFT medidos conjuntamente bajo configuración compatible; si falta algo, `ESTIMATION_NOT_IDENTIFIABLE`.

- [ ] **Step 6: Verificar y commit**

```bash
python3 -m pytest tools/test_ai_hardware_costs.py tools/test_arquitectura.py -q
git add tools/data/ai_hardware_costs.yaml tools/ai_hardware_costs.py tools/test_ai_hardware_costs.py course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md
git commit -m "docs(unidad-3): dimensiona inferencia por capacidad"
```

---

### Task 5: Gráficas generadas y accesibles

**Files:**
- Create: `tools/gen_ai_hardware_costs.py`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-aceleradores-entrenamiento.svg`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-hbm-entrenamiento.svg`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-potencia-hardware.svg`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-capex-hardware.svg`
- Create: `course/3_arquitectura_de_computadoras/_assets/ai-inferencia-capacidad.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`
- Modify: `tools/test_diagramas.py`
- Modify: `tools/test_ai_hardware_costs.py`

**Interfaces:**
- `render_all(data_path: Path, assets_dir: Path) -> list[Path]` produce cinco SVG deterministas.

- [ ] **Step 1: Escribir pruebas visuales en rojo**

```python
AI_SVGS = [
    ASSETS / "ai-aceleradores-entrenamiento.svg",
    ASSETS / "ai-hbm-entrenamiento.svg",
    ASSETS / "ai-potencia-hardware.svg",
    ASSETS / "ai-capex-hardware.svg",
    ASSETS / "ai-inferencia-capacidad.svg",
]

@pytest.mark.parametrize("path", AI_SVGS)
def test_ai_hardware_svg_is_accessible_and_mobile_legible(path):
    root = ET.parse(path).getroot()
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    viewbox_width = float(root.attrib["viewBox"].split()[2])
    assert viewbox_width <= 640
    sizes = [float(node.attrib["font-size"])
             for node in root.iter() if "font-size" in node.attrib]
    mobile_scale = min(1, 390 / viewbox_width)
    assert sizes and min(sizes) * mobile_scale >= 16

def test_log_charts_explain_scale_and_exclude_invalid_values():
    for chart in load_generated_chart_metadata():
        if chart["scale"] == "log":
            assert chart["ticks"] == sorted(chart["ticks"])
            assert all(tick > 0 for tick in chart["ticks"])
            assert chart["scale_note"] == "Igual distancia representa multiplicación."
            assert not ({"UNDISCLOSED_BY_CREATOR", "NOT_FOUND",
                         "ESTIMATION_NOT_IDENTIFIABLE"} & set(chart["plotted_statuses"]))
```

Además, comprobar etiquetas directas, orden igual al ledger y formas distintas por estado. Los intervalos válidos usan extremos completos; los valores ausentes o no identificables quedan en la tabla equivalente, nunca como barras o puntos.

- [ ] **Step 2: Confirmar RED**

Run: `python3 -m pytest tools/test_diagramas.py tools/test_ai_hardware_costs.py -q -k ai_hardware`

- [ ] **Step 3: Implementar utilidades puras**

Crear `log_position`, `format_si`, `marker_for_status`, `svg_header`; generar XML con `xml.etree.ElementTree`. CAPEX separa fronteras/bases; potencia usa paneles GPU-only y servidor/IT; HBM dice física; inferencia dice piso/capacidad.

- [ ] **Step 4: Integrar SVG, alt y créditos**

Cada visual tendrá alt equivalente, lectura visual, tabla textual y fila en `CREDITOS.md`.

- [ ] **Step 5: Probar determinismo**

```bash
python3 tools/gen_ai_hardware_costs.py
sha256sum course/3_arquitectura_de_computadoras/_assets/ai-*.svg > /tmp/ai-hardware-1.sha
python3 tools/gen_ai_hardware_costs.py
sha256sum course/3_arquitectura_de_computadoras/_assets/ai-*.svg > /tmp/ai-hardware-2.sha
diff -u /tmp/ai-hardware-1.sha /tmp/ai-hardware-2.sha
```

- [ ] **Step 6: Verificar y commit**

```bash
python3 -m pytest tools/test_diagramas.py tools/test_ai_hardware_costs.py tools/test_creditos.py -q
git add tools/gen_ai_hardware_costs.py tools/test_diagramas.py tools/test_ai_hardware_costs.py course/3_arquitectura_de_computadoras/_assets course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md
git commit -m "feat(unidad-3): visualiza escala de hardware IA"
```

---

### Task 6: Auditoría, render y publicación

**Files:**
- Modify as required: ledger, calculator, page, generator, SVG and tests.

**Interfaces:**
- Produces: cuatro revisiones aprobadas, artifact válido y producción verificada.

- [ ] **Step 1: Ejecutar cuatro revisiones adversariales**

Revisores separados: fuentes/evidencia; matemáticas/unidades; CAPEX/potencia; pedagogía/formato. Resolver todo Critical/Important y repetir hasta `APPROVE`.

- [ ] **Step 2: Verificación completa**

```bash
python3 -m pytest tools/ -q
python3 tools/gen_ai_hardware_costs.py
git diff --check
```

Desde el checkout Raya fijado:

```bash
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate /home/uumami/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build /home/uumami/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect /home/uumami/itam/fdd_o26/artifact
```

- [ ] **Step 3: Auditar Chromium**

A 390×844 y 1440×900 comprobar `scrollWidth == clientWidth`, tablas con señal de scroll/primera columna, SVG sin recortes, texto ≥16 px y fallbacks equivalentes. Capturar y revisar cada visual.

- [ ] **Step 4: Simular lectura principiante**

Debe reconstruir 8×GPU, distinguir FLOP/FLOP/s, HBM física/utilizable, watts/kWh, dos fronteras CAPEX y no-identificabilidad de modelos cerrados.

- [ ] **Step 5: Commit, push y Pages**

```bash
git add course/3_arquitectura_de_computadoras tools
git commit -m "docs(unidad-3): completa costos de hardware IA"
git push origin main
gh run list --limit 1
```

Monitorear con `gh run watch <run-id> --exit-status`. Verificar en producción página, cinco SVG, tablas, estados y render móvil. No declarar publicación antes de que Pages termine y producción contenga el commit.
