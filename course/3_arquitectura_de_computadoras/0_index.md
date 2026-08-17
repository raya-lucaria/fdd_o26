---
id: arquitectura-de-computadoras
title: "Arquitectura de computadoras"
nav_title: "Arquitectura"
summary: "Cómo el cómputo, la memoria y el movimiento de datos determinan qué puede hacer una máquina y a qué costo."
status: ready
estimated_time: "90 minutos"
tags: [hardware, memoria, cpu, gpu, arquitectura]
---

Un programa no trabaja en el vacío. **Calcula**, **guarda** y **mueve datos** sobre una máquina física. El desempeño aparece cuando esas tres acciones encajan; el cuello de botella aparece cuando una de ellas no alcanza a las otras.

![Ciudad retrofuturista vista desde arriba: una torre central de cómputo conectada por rutas luminosas a distritos de memoria y almacenamiento.](_assets/hero-arquitectura.webp)

*Creación original generativa para este curso, producida con OpenAI, 2026.*

**Lectura visual:** el núcleo de cómputo no está aislado. Depende de capas de memoria, almacenamiento y rutas capaces de llevarle datos.

Esta unidad construye un mapa para leer una laptop, una GPU o un centro de datos según cuatro dimensiones: ubicación de los datos, unidad que los transforma, costo de moverlos y recurso que se satura primero.

## Notebook de la unidad

[Descarga el notebook de arquitectura](code/01_arquitectura.ipynb) si quieres experimentar. El recorrido reproduce mediciones pequeñas de hardware, vectorización, caché, multiplicación de matrices y memoria de modelos. Es un recurso opcional: **no es una entrega**. La única tarea publicada para esta unidad es ver los tres videos de preparación.

Para reproducir el entorno, instala las dependencias listadas en `code/requirements.txt`. Los tiempos cambiarán entre máquinas: esa variación es parte del dato, no un error que debas ocultar.

## Al terminar

Podrás explicar por qué un programa compatible necesita la ISA correcta; distinguir reloj, ciclos, latencia y throughput; razonar sobre RAM, VRAM, caché y almacenamiento; y elegir una dirección de optimización a partir de mediciones, no de slogans.

## Ruta principal de 90 minutos

**ESTIMATE (diseño docente):** los tiempos son una guía, no una obligación. La página de IA contiene material opcional adicional para que el profesor elija profundidad sin perder el hilo principal.

| Minutos | Parada | Pregunta que organiza la explicación | Si falta tiempo |
|---:|---|---|---|
| 0–5 | Este mapa | Lo que una computadora calcula, guarda y mueve | Conservar |
| 5–23 | [[compute-instrucciones-cpu|Compute, instrucciones y CPU]] | Conversión de un programa en trabajo físico | Conservar juguetes y diagramas |
| 23–40 | [[memoria-y-datos|Memoria y movimiento de datos]] | Costo de acercar un dato | Omitir detalles de DMA |
| 40–61 | [[paralelismo-performance-energia|Paralelismo, performance y energía]] | Diagnóstico entre memoria, cómputo y potencia | Conservar Roofline de juguete |
| 61–86 | [[ia-escala-decision|IA, escala y selección de hardware]] | Recursos para alojar y servir un modelo | Usar sólo tabla comparativa |
| 86–90 | Cierre | Evidencia necesaria antes de comprar hardware | Conservar |

> [!TIP]
> Para una lectura ADHD-friendly, detente después de cada visual y di en una frase qué cambió. La meta no es memorizar números: es aprender a localizar el costo.

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

## Qué debes recordar

- Todo programa necesita **cómputo, memoria y movimiento**.
- El recurso más lento en la ruta determina qué optimización ayuda.
- Las cifras sólo son comparables cuando conservan tarea, unidad y frontera del sistema.
- La ruta esencial dura 90 minutos; las ampliaciones quedan disponibles para elegir en clase.
