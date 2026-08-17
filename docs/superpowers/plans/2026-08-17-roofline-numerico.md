# Roofline numérico Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sustituir la analogía de cocina por una derivación Roofline numérica, gradual y verificable.

**Architecture:** La lección, el SVG y la guarda editorial compartirán exactamente el mismo ejemplo de suma FP32. Tres revisiones adversariales independientes atacarán claridad, aritmética y accesibilidad antes y después de la implementación.

**Tech Stack:** Markdown de Raya, SVG accesible, pytest, CLI Raya y Playwright/Chromium.

## Global Constraints

- Usar 1,000 elementos FP32, 12,000 bytes mínimos y 1,000 FLOP.
- Derivar 0.083 FLOP/byte y, para 100 GB/s, 8.3 GFLOPS.
- Explicar cada unidad antes de la fórmula general.
- Eliminar analogías de cocina y la etiqueta “ejemplo de juguete” de Roofline.
- Mantener SVG accesible, fallback textual y ausencia de overflow móvil.

---

### Task 1: Revisión adversarial previa

**Files:**
- Review: `docs/superpowers/specs/2026-08-17-roofline-numerico-design.md`
- Review: `course/3_arquitectura_de_computadoras/3_paralelismo_performance_energia/0_index.md`
- Review: `course/3_arquitectura_de_computadoras/_assets/roofline-lite.svg`

- [ ] Despachar revisores independientes de pedagogía, aritmética y accesibilidad.
- [ ] Clasificar hallazgos por severidad y corregir la especificación si demuestran una ambigüedad.

### Task 2: Guarda editorial en rojo

**Files:**
- Modify: `tools/test_arquitectura.py`

- [ ] Exigir `12,000 bytes`, `1,000 FLOP`, `0.083 FLOP/byte` y `8.3 GFLOPS`.
- [ ] Rechazar “cocina” dentro de la página de rendimiento.
- [ ] Ejecutar `pytest -q tools/test_arquitectura.py` y confirmar que falla antes de editar la lección.

### Task 3: Explicación y visual sincronizados

**Files:**
- Modify: `course/3_arquitectura_de_computadoras/3_paralelismo_performance_energia/0_index.md`
- Modify: `course/3_arquitectura_de_computadoras/_assets/roofline-lite.svg`
- Modify: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`

- [ ] Reescribir la sección en la secuencia datos → bytes → FLOP → intensidad → hardware → `min` → fórmula.
- [ ] Añadir la cancelación `(byte/s) × (FLOP/byte) = FLOP/s` y aclarar las convenciones decimales.
- [ ] Contrastar con reutilización matricial sin fingir un benchmark universal.
- [ ] Actualizar el SVG con los mismos números y fallback.
- [ ] Ejecutar la guarda y confirmar que pasa.

### Task 4: Revisión adversarial final y publicación

**Files:**
- Verify: unidad completa y artefacto generado.

- [ ] Pedir a los tres revisores que ataquen el resultado final.
- [ ] Resolver todo hallazgo crítico o importante con evidencia.
- [ ] Ejecutar `pytest -q`, XML/JSON, `raya validate`, `raya build` y `raya artifacts inspect`.
- [ ] Revisar Chromium a 390 y 1440 px y confirmar `scrollWidth == clientWidth`.
- [ ] Integrar en `main`, publicar, monitorear Pages y verificar el texto nuevo en producción.
