---
id: presentacion-pipeline
title: Presentación
nav_title: Presentación
summary: "El deck de 33 diapositivas del semestre pasado, disponible como material histórico, y el mapa de qué se conservó y qué se reescribió."
status: ready
estimated_time: 5m
tags: [material-historico, presentacion]
prerequisites: [pipeline-de-datos]
---

# Presentación

::: figure {#ilus-archivo title="Material histórico, conservado y consultable"}
![Estantería de archivo metálica con cajones abiertos, carretes de microfilm, planos enrollados y láminas apiladas cubiertas de una capa fina de polvo](_assets/ilus-archivo.jpg)
:::

## En corto

- Hasta Primavera 2026 esta unidad se daba con un deck de **33 diapositivas**. Aquí está.
- Es **material histórico, no material de estudio**: las seis páginas anteriores lo reemplazan.
- El temario conceptual se conservó entero, redistribuido entre esas páginas.
- Ocho omisiones motivaron el rediseño, y son una lista de errores comunes en cualquier material sobre pipelines.

## El archivo

**[Abrir la presentación en el navegador](_assets/01_pipeline_de_datos.pdf)** — el visor de PDF la muestra sin descargarla.

**[Descargar el archivo](_assets/01_pipeline_de_datos.pdf)** — es el mismo archivo, guardado con «Guardar como». Son **4.2 MB**, así que conviene saberlo si estás con datos móviles.

> [!WARNING]
> **Es material del semestre pasado, y las seis páginas anteriores lo reemplazan.** No es un resumen ni una versión condensada para repasar antes del examen. Lo que se evalúa es el texto, no las diapositivas.

### Por qué se conserva

- **Continuidad**: hay quien conoce el material por otra generación, y esconder la versión anterior no ayuda a nadie.
- **Comparación**: ver qué se conservó y qué se tiró es una lección sobre cómo envejece el material técnico.
- **Utilidad puntual**: el deck tiene buenas definiciones compactas que sirven de recordatorio rápido.

## Qué se conservó

| Tema del deck | Dónde vive ahora |
|---|---|
| El flujo general de los datos, en nueve pasos | [[pipeline-de-datos]], como DAG y como ciclo |
| Datalake, base de datos, data warehouse | [[el-viaje-de-los-datos]] |
| Pre-procesamiento contra procesamiento | [[el-viaje-de-los-datos]] |
| Algoritmo contra modelo | [[el-viaje-de-los-datos]] |
| Las cuatro etapas: ETL, EDA, entrenamiento, producción | [[pipeline-de-datos]] |
| Extract y Transform en detalle | [[etl-y-elt]] |
| Datos tabulares y tidy data | [[etl-y-elt]] |
| EDA, viabilidad y calidad de los datos | [[eda]] |
| El catálogo de posiciones | [[posiciones]] |

Se conservó también una de sus mejores advertencias, repetida en esta unidad: todos estos conceptos son **abstracciones útiles para poder hablar**, no categorías con fronteras naturales.

## Qué se reescribió, y por qué

### Lo que faltaba sobre mover datos

| Omisión | Por qué importa | Ahora en |
|---|---|---|
| **No mencionaba ELT** | Daba ETL como *la* forma de mover datos, sin la historia económica que invirtió el orden | [[etl-y-elt]] |
| **No explicaba la L** | La carga es donde ocurren los errores que duplican dinero | [[etl-y-elt]] |
| **Lake contra warehouse, binario** | El lakehouse colapsó esa distinción, y el eje real —schema-on-write contra schema-on-read— no aparecía | [[el-viaje-de-los-datos]] |

### Lo que faltaba sobre sostener un pipeline

| Omisión | Por qué importa | Ahora en |
|---|---|---|
| **Solo contemplaba batch** | Ni streaming ni CDC, salvo una imagen ajena que decía «CDC» sin explicarlo | [[cuando-se-rompe]] |
| **Nada de lo que rompe un pipeline** | Faltaban idempotencia, backfills, contratos, orquestación, linaje, observabilidad y costo | [[cuando-se-rompe]] |
| **El pipeline como una flecha** | Es un grafo: de su forma dependen el paralelismo, la propagación de fallas y el reinicio | [[pipeline-de-datos]] |
| **Le faltaban roles** | Ni analytics engineer ni los papeles de la era de los modelos de lenguaje | [[posiciones]] |

Hay una octava corrección, más pequeña y más instructiva: el deck **citaba el 60 % del tiempo sin fecha**. El dato viene de una encuesta de CrowdFlower de alrededor de 2016, y en [[eda|EDA]] se cita con su año y se marca como lo que es —folklore reciclado de la industria—. El argumento funciona sin el número.

## Sobre las imágenes

Ninguna imagen del deck se reutilizó. Los diagramas de esta unidad los genera un script del repositorio, en español y con los colores del curso, lo que los hace **reproducibles y corregibles**: si uno está mal, se corrige el generador.

Las del deck eran arte de plantilla y capturas de terceros sin licencia clara, justo el tipo de dependencia que no conviene arrastrar de un semestre al siguiente.

Es el mismo principio que [[pipeline-de-datos|abre la unidad]]: la fuente es el generador, la imagen es el artifact, y el artifact se regenera. Una imagen que no se puede volver a producir es un dato sin linaje.

## Qué te llevas

- El deck está aquí como **archivo, no como resumen**: lo que se evalúa es el texto de esta unidad.
- El conceptual se conservó entero; lo que se añadió es **todo lo que ocurre cuando el pipeline ya está en producción**.
- **La fuente es el generador, no el resultado.** Vale para diagramas igual que para datos.
