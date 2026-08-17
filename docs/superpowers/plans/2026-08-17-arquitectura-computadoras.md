# Unidad 3: Arquitectura de computadoras Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar una Unidad 3 nativa de Raya con notebook, tarea, práctica oficial e imágenes accesibles.

**Architecture:** El contenido se modela como un quantum de unidad con cuatro quanta hijos, assets colocados y objetos oficiales al final. Raya valida y genera navegación, tareas, calendario y práctica desde IDs estables y YAML fuente.

**Tech Stack:** Markdown CommonMark, YAML, Jupyter Notebook, Python/pytest, Raya Lucaria/Glintstone, Chromium.

**Spec:** `docs/superpowers/specs/2026-08-17-arquitectura-computadoras-design.md`

## Global Constraints

- Curso y prosa en español; IDs técnicos y nombres de archivo estables en inglés.
- Aproximadamente 6,000 palabras y 125 minutos; siete modelos mentales.
- Toda práctica aparece al final: 6 preguntas, 3 escenarios y 15 tarjetas.
- Cifras importantes llevan FACT, DERIVED o ESTIMATE y fuentes primarias vigentes.
- No editar `artifact/` ni copiar configuración o HTML crudo de `fdd_p26`.
- Ninguna vista desktop o móvil puede tener overflow horizontal.

---

### Task 1: Contrato del repositorio y tarea del 18 de agosto

**Files:**
- Create: `AGENTS.md`
- Modify: `course/2_pipeline_de_datos/_official/assignments/1_videos_hardware.yaml`
- Modify: `course/_official/calendar/1_2026-o26.yaml`

**Interfaces:**
- Consumes: contrato de objetos oficiales y calendario de Raya.
- Produces: tarea `notebook-arquitectura` fechada y sesión enlazada a la nueva unidad.

- [ ] Escribir una guarda que exija ID, fecha, enlace al notebook y entrega en Canvas; ejecutarla y confirmar que falla.
- [ ] Reemplazar la tarea de videos por la entrega del notebook y actualizar la sesión 3.
- [ ] Crear `AGENTS.md` de 200–400 palabras con estructura, comandos, estilo, pruebas y commits.
- [ ] Ejecutar la guarda y `python3 -m pytest tools/ -q`.

### Task 2: Páginas, notebook y recursos

**Files:**
- Create: `course/3_arquitectura_de_computadoras/{0_index.md,1_compute_instrucciones_cpu/0_index.md,2_memoria_y_datos/0_index.md,3_paralelismo_performance_energia/0_index.md,4_ai_escala_y_decision/0_index.md}`
- Create: `course/3_arquitectura_de_computadoras/code/{01_arquitectura.ipynb,requirements.txt}`
- Create: `course/3_arquitectura_de_computadoras/_assets/*`

**Interfaces:**
- Consumes: contenido del commit `cf8b543`, IDs y directivas Raya.
- Produces: cinco rutas renderizadas y un notebook local enlazable.

- [ ] Escribir guardas de estructura, frontmatter, conteo de palabras, tiempo, siete modelos, etiquetas de cifras, ausencia de HTML y posición postclase.
- [ ] Migrar y editar las cinco páginas al patrón `0_index.md` con enlaces estables y figuras nativas.
- [ ] Migrar el notebook y comprobar ejecución desde un entorno limpio con sus dependencias.
- [ ] Ejecutar las guardas hasta que pasen.

### Task 3: Práctica oficial e imágenes

**Files:**
- Create: `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/_official/{quizzes,examples,cards}/*.yaml`
- Create: `course/3_arquitectura_de_computadoras/_assets/CREDITOS.md`
- Modify: `tools/ilustraciones.json`
- Modify: `tools/gen_ilustraciones.py`

**Interfaces:**
- Consumes: contenido de repaso y assets fuente.
- Produces: 6 preguntas conceptuales, 3 escenarios, 15 tarjetas y 12 assets acreditados.

- [ ] Escribir guardas que cuenten familias/objetos y exijan alt, fallback y créditos exactos.
- [ ] Convertir la práctica final a YAML oficial sin preguntas en las páginas anteriores.
- [ ] Adaptar los SVG y generar una hero nueva con Codex; conservar fotografías licenciadas.
- [ ] Ejecutar guardas y revisar visualmente todos los assets.

### Task 4: Build y revisión integral

**Files:**
- Modify: cualquier archivo de las Tasks 1–3 que falle la auditoría.

**Interfaces:**
- Consumes: unidad completa y framework Raya.
- Produces: artifact válido y evidencia desktop/móvil.

- [ ] Ejecutar pytest, `raya validate`, `raya build` y `raya artifacts inspect`.
- [ ] Auditar enlaces, referencias del notebook, assets, navegación, tareas, calendario y práctica generada.
- [ ] Abrir las cinco rutas, Tasks y Schedule en Chromium 1440×900 y 390×844; comprobar overflow y legibilidad.
- [ ] Corregir todos los hallazgos y repetir la matriz completa.

### Task 5: Integración y producción

**Files:**
- Modify: sólo archivos necesarios por hallazgos de producción.

**Interfaces:**
- Consumes: commit verificado en la rama actual.
- Produces: `main` remoto desplegado y producción comprobada.

- [ ] Revisar diff, estado y commits; integrar sin sobrescribir cambios ajenos.
- [ ] Hacer push de `main` y monitorear el workflow de GitHub Pages hasta estado terminal.
- [ ] Abrir producción y verificar la tarea y las cinco rutas; corregir y repetir si falla algo.
