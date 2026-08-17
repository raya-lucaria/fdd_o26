---
id: arquitectura-de-computadoras
title: "Arquitectura de computadoras"
nav_title: "Arquitectura"
summary: "Cómo el cómputo, la memoria y el movimiento de datos determinan qué puede hacer una máquina y a qué costo."
status: ready
estimated_time: "125 minutos"
tags: [hardware, memoria, cpu, gpu, arquitectura]
---

Un programa no trabaja en el vacío. **Calcula**, **guarda** y **mueve datos** sobre una máquina física. El desempeño aparece cuando esas tres acciones encajan; el cuello de botella aparece cuando una de ellas no alcanza a las otras.

![Ciudad retrofuturista vista desde arriba: una torre central de cómputo conectada por rutas luminosas a distritos de memoria y almacenamiento.](_assets/hero-arquitectura.webp)

*Creación original generativa para este curso, producida con OpenAI, 2026.*

**Lectura visual:** el núcleo de cómputo no está aislado. Depende de capas de memoria, almacenamiento y rutas capaces de llevarle datos.

Esta unidad construye un mapa para leer una laptop, una GPU o un centro de datos según cuatro dimensiones: ubicación de los datos, unidad que los transforma, costo de moverlos y recurso que se satura primero.

## Notebook de la unidad

[Descarga el notebook de arquitectura](code/01_arquitectura.ipynb) y conserva una copia propia. El recorrido reproduce mediciones pequeñas de hardware, vectorización, caché, multiplicación de matrices y memoria de modelos. Las celdas explicativas se pueden ejecutar durante la lectura; la única práctica que debes entregar está rotulada **«Práctica FINAL — post-clase»** y aparece al final.

Para reproducir el entorno, instala las dependencias listadas en `code/requirements.txt`. Los tiempos cambiarán entre máquinas: esa variación es parte del dato, no un error que debas ocultar.

## Al terminar

Podrás explicar por qué un programa compatible necesita la ISA correcta; distinguir reloj, ciclos, latencia y throughput; razonar sobre RAM, VRAM, caché y almacenamiento; y elegir una dirección de optimización a partir de mediciones, no de slogans.

## Ruta en dos sesiones

**ESTIMATE (diseño docente):** la ruta requiere 125 minutos netos en dos sesiones nominales de 90. Los escenarios se trabajan en grupos pequeños y en paralelo; las flashcards quedan para después de clase.

### Sesión 1 — De la máquina al movimiento

1. **Orientación** — este mapa de la unidad (~5 min).
2. [[compute-instrucciones-cpu|**Compute, instrucciones y CPU**]] — piezas físicas, ISA, reloj, ciclos, cores, threads y SIMD (~20 min).
3. [[memoria-y-datos|**Memoria y movimiento de datos**]] — jerarquía, latencia, ancho de banda y rutas CPU↔GPU (~25 min).

### Sesión 2 — Del paralelismo a la decisión

1. [[paralelismo-performance-energia|**Paralelismo, performance y energía**]] — CPU, GPU, aceleradores, Roofline y potencia (~43 min).
2. [[ia-escala-decision|**IA, escala y selección de hardware**]] — memoria de modelos, comunicación, selección y repaso final (~32 min).

## Siete modelos mentales

1. **La computadora es un sistema de especialistas.** CPU, memoria, almacenamiento, red y aceleradores colaboran mediante interconexiones.
2. **La ISA es un contrato.** Define qué instrucciones entiende un procesador; no es lo mismo que el lenguaje en el que escribiste el programa.
3. **El reloj asigna pasos, no garantiza trabajo útil.** Los ciclos pueden ocuparse en cálculo, espera o coordinación.
4. **La proximidad de los datos tiene precio.** Cerca del cómputo suele significar menor latencia, pero menor capacidad y mayor costo por byte.
5. **El paralelismo tiene forma.** Pocos flujos complejos y muchos flujos regulares necesitan arquitecturas distintas.
6. **El cuello de botella decide la métrica.** Más FLOPS no ayuda si faltan memoria, ancho de banda o comunicación.
7. **Escalar amplifica movimiento y energía.** Chip, servidor, rack y centro de datos son niveles del mismo sistema.

## Cómo leer las cifras

- **FACT**: dato reportado directamente por una fuente identificada.
- **DERIVED**: resultado reproducible a partir de datos o una fórmula mostrada.
- **ESTIMATE**: supuesto o escenario útil, no una medición.

Estas etiquetas importan: una especificación máxima, una derivación y una observación real no responden la misma pregunta.
