# Arquitectura Visual y Accesible Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la unidad completa como guion docente visual de 90 minutos, con comparaciones actuales y verificables.

**Architecture:** Cinco páginas Markdown conservan sus IDs y reciben una progresión visual común. SVG autocontenidos comunican relaciones; tablas Markdown contienen cifras auditables; pytest fija los invariantes editoriales y Raya genera la experiencia final.

**Tech Stack:** CommonMark, YAML, SVG 1.1, Python/pytest, Raya static builder, Playwright/Chromium.

**Spec:** `docs/superpowers/specs/2026-08-17-arquitectura-visual-adhd-design.md`

## Global Constraints

- Español para contenido estudiantil; IDs y nombres técnicos estables.
- Ruta principal total: 90 minutos; detalle adicional marcado opcional.
- Etiquetas cuantitativas: FACT, DERIVED y ESTIMATE.
- Sólo `videos-hardware` es entrega; notebook únicamente recurso.
- Cada SVG requiere title, desc, alt, fallback y crédito.
- Cero overflow horizontal, imágenes rotas o errores de consola.

---

### Task 1: Guardas editoriales

**Files:** Modify `tools/test_arquitectura.py`.

- [ ] Añadir pruebas que exijan 90 minutos, cinco resúmenes, los nuevos SVG, tablas, ejemplos de juguete, las tres etiquetas de evidencia y ausencia de tarea notebook.
- [ ] Ejecutar la prueba focal y confirmar RED por recursos ausentes.
- [ ] Conservar la prueba como contrato para las tareas siguientes.

### Task 2: Compute visual

**Files:** Modify `1_compute_instrucciones_cpu/0_index.md`; create `_assets/threads-cores-simd.svg` and `_assets/latencia-throughput.svg`.

- [ ] Reorganizar la lección como intuición, juguete, diagrama, tabla y resumen.
- [ ] Crear ambos SVG accesibles y fallback textual.
- [ ] Ejecutar pruebas focales y confirmar GREEN del bloque compute.

### Task 3: Memoria visual

**Files:** Modify `2_memoria_y_datos/0_index.md`, `_assets/jerarquia-memoria-datos.svg`; create `_assets/rutas-cpu-gpu.svg`.

- [ ] Añadir recorrido de un dato y tabla de registros/L1/L2/L3/RAM/SSD/red con rangos y analogía logarítmica.
- [ ] Rediseñar jerarquía y rutas CPU/GPU con texto alternativo equivalente.
- [ ] Verificar cifras, unidades y pruebas.

### Task 4: Roofline y energía

**Files:** Modify `3_paralelismo_performance_energia/0_index.md`, `_assets/roofline-lite.svg`, `_assets/escala-energia.svg`.

- [ ] Introducir Roofline con suma vectorial y reutilización matricial antes de fórmula.
- [ ] Añadir tabla de dispositivos/electrodomésticos y escenarios temporales.
- [ ] Redibujar plots, verificar cálculos y ejecutar pruebas.

### Task 5: IA desde diez parámetros

**Files:** Rewrite `4_ai_escala_y_decision/0_index.md`; create `_assets/precision-parametros.svg`, `_assets/dense-moe.svg`, `_assets/prefill-decode.svg`.

- [ ] Explicar parámetro, bit/byte, GB/GiB mediante juguete antes de fórmula.
- [ ] Separar inferencia/entrenamiento y visualizar memoria, precisión, MoE, caché KV y comunicación.
- [ ] Añadir tablas actuales de modelos y hardware con fuentes, supuestos y confianza.
- [ ] Verificar todas las derivaciones y enlaces primarios.

### Task 6: Índice, ritmo y créditos

**Files:** Modify `0_index.md`, `_assets/CREDITOS.md` y frontmatter de cuatro lecciones.

- [ ] Distribuir 90 minutos y señalar ruta principal/opcional.
- [ ] Añadir “Qué debes recordar” y transiciones en cada página.
- [ ] Registrar todos los SVG y confirmar notebook como recurso, no tarea.

### Task 7: Validación integral

**Files:** Generated `artifact/`; no commit.

- [ ] Ejecutar `python3 -m pytest tools/ -q`.
- [ ] Ejecutar `raya validate`, `raya build` y `raya artifacts inspect` con el framework fijado.
- [ ] Auditar palabras, tablas, SVG, fuentes, enlaces y objetos oficiales.
- [ ] Revisar cinco rutas y workspaces en Chromium 1440×900 y 390×844; corregir overflow, densidad, contraste y consola.

### Task 8: Publicación

**Files:** Commit sólo fuentes revisadas.

- [ ] Revisar `git diff --check`, commit y push a `main`.
- [ ] Vigilar GitHub Pages hasta estado terminal exitoso.
- [ ] Repetir la auditoría Chromium y de contenido sobre producción.
