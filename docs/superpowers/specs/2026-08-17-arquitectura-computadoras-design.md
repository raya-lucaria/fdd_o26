# Unidad 3: Arquitectura de computadoras — diseño

## Objetivo

Adaptar el módulo `fdd_p26@cf8b543:clase/15_arquitectura_de_computadoras/` al contrato vigente de Raya Lucaria y al curso *Fuentes de Datos — Otoño 2026*. La unidad debe ser legible por estudiantes con TDAH, conservar el rigor y terminar con toda la práctica agrupada.

## Estructura

La unidad vivirá en `course/3_arquitectura_de_computadoras/`: un índice, cuatro lecciones numeradas, `_assets/`, `_official/` y un notebook en `code/`. Cada página tendrá frontmatter Raya, una función pedagógica clara y navegación por el árbol del curso. La sesión del 18 de agosto apuntará al índice estable `arquitectura-de-computadoras`.

## Contenido y pedagogía

Se conservarán aproximadamente 6,000 palabras, 125 minutos, siete modelos mentales y las etiquetas FACT, DERIVED y ESTIMATE. Para reducir carga de memoria de trabajo, cada lección abrirá con una pregunta concreta, usará párrafos breves, tablas de decisión y encabezados descriptivos. No habrá preguntas intercaladas: seis preguntas conceptuales, tres escenarios y quince tarjetas aparecerán al final mediante objetos oficiales Raya.

## Tarea y notebook

La tarea oficial con vencimiento `2026-08-18` pedirá descargar, ejecutar y entregar en Canvas `code/01_arquitectura.ipynb`. El notebook conservará resultados revisables y situará la práctica únicamente en su sección final, rotulada como postclase. `requirements.txt` acompañará al notebook como referencia reproducible.

## Imágenes y atribución

Los ocho SVG se migrarán como fuente propia y se ajustarán a la paleta del skin sin depender de CSS de `fdd_p26`. Las tres fotografías se conservarán sólo con licencia y atribución verificables. La hero se regenerará con Codex para armonizar con la identidad azul medianoche/turquesa del curso. Toda imagen tendrá texto alternativo, fallback textual y registro en `_assets/CREDITOS.md`.

## Validación

La entrega exige pytest, `raya validate`, build, inspección de artifact, ejecución limpia del notebook, auditoría de enlaces/assets/objetos, y revisión Chromium a 1440×900 y 390×844 sin overflow. Después se integrará en `main`, se enviará al remoto, se monitoreará Pages y se abrirán en producción la tarea y las cinco rutas de la unidad.
