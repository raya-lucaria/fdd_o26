# Roofline simple y compacto Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconstruir Roofline como una explicación corta, progresiva y visualmente compacta para principiantes.

**Architecture:** Texto y SVG formarán una secuencia única sin repetición. La aritmética vivirá en el texto; el SVG resumirá solamente la comparación entre techos. Revisores independientes atacarán contenido, explicación y formato.

**Tech Stack:** Markdown de Raya, SVG accesible, pytest, Raya y Playwright.

## Global Constraints

- Empezar con un elemento antes de escalar a 1,000.
- Explicar cada operación aritmética y cada unidad con palabras.
- Definir intensidad y `min` verbalmente antes de la fórmula.
- Eliminar acumulación, tarjeta duplicada, cocina y “ejemplo de juguete”.
- SVG móvil de 350–450 px de alto, con dimensiones intrínsecas y fallback equivalente.
- Preservar exactitud: 12 bytes por elemento, 12,000 bytes, 1,000 FLOP, 0.083 FLOP/byte, 8.3 frente a 2,000 GFLOPS y quiebre 20 FLOP/byte.

---

### Task 1: Ataque adversarial previo

**Files:** spec, sección Roofline y SVG actuales.

- [ ] Revisar independientemente contenido, explicación y formato.
- [ ] Consolidar únicamente hallazgos Critical/Important demostrables.

### Task 2: Pruebas en rojo

**Files:**
- Modify: `tools/test_arquitectura.py`

- [ ] Exigir ejemplo de un elemento, escala a 1,000, tabla de techos y definición verbal de `min`.
- [ ] Rechazar la tarjeta SVG y altura móvil mayor a 450 px.
- [ ] Ejecutar la guarda y confirmar fallo antes de reescribir.

### Task 3: Reescritura limpia

**Files:**
- Modify: `course/3_arquitectura_de_computadoras/3_paralelismo_performance_energia/0_index.md`
- Rewrite: `course/3_arquitectura_de_computadoras/_assets/roofline-lite.svg`

- [ ] Eliminar la sección acumulada y escribir una sola progresión desde `C[0]`.
- [ ] Crear tabla de tres filas y fórmula únicamente al final.
- [ ] Rehacer SVG horizontal compacto sin tarjeta de cuentas.
- [ ] Ejecutar guardas, XML y autoauditoría.

### Task 4: Ataque final, validación y publicación

**Files:** resultado completo y artefacto Raya.

- [ ] Revisar contenido, explicación y formato con agentes distintos al implementador.
- [ ] Resolver todo Critical/Important y repetir revisión.
- [ ] Ejecutar suite completa, Raya validate/build/inspect y Chromium 390/1440.
- [ ] Integrar en `main`, publicar, monitorear Pages y verificar producción.
