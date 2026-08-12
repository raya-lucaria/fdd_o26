---
id: presentacion-pipeline
title: Presentación
nav_title: Presentación
summary: El deck de 33 diapositivas del semestre pasado, disponible como material histórico, y el mapa de qué se conservó y qué se reescribió.
status: ready
estimated_time: 8m
tags: [material-historico, presentacion]
prerequisites: [pipeline-de-datos]
---

# Presentación

Hasta el semestre de Primavera 2026, esta unidad se daba con una presentación de
**33 diapositivas**. Esa presentación sigue disponible aquí, y esta página
explica en qué condición se ofrece.

## El archivo

**[Abrir la presentación en el navegador](_assets/01_pipeline_de_datos.pdf)** —
el visor de PDF del navegador la muestra sin descargarla.

**[Descargar el archivo](_assets/01_pipeline_de_datos.pdf)** — es el mismo
archivo; el navegador lo guarda si eliges «Guardar como» desde el visor o desde
el menú contextual del enlace. Son **4.2 MB** y 33 diapositivas, así que conviene
saberlo antes si estás con datos móviles.

## Material histórico, no material de estudio

Conviene ser explícito sobre el estatus de este archivo: **es material del
semestre pasado, y las seis páginas anteriores de esta unidad lo reemplazan.**
No es un resumen de la unidad ni una versión condensada para repasar antes del
examen. Lo que se evalúa, lo que se discute en clase y lo que sostiene el resto
del semestre es el texto, no las diapositivas.

Se conserva por tres razones. La primera es de continuidad: hay quien tomó el
curso antes o conoce el material por otra generación, y esconder la versión
anterior no ayuda a nadie. La segunda es que la comparación es útil: ver qué se
conservó y qué se tiró es una lección sobre cómo envejece el material técnico.
La tercera es que el deck tiene, honestamente, buenas definiciones compactas de
varios conceptos, y a alguien le puede servir como recordatorio rápido.

## Qué se conservó

El temario conceptual del deck sigue completo en esta unidad, redistribuido:

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

También se conservó una de sus mejores advertencias, y esta unidad la repite más
de una vez: todos estos conceptos son **abstracciones útiles para poder hablar**,
no categorías con fronteras naturales. Ninguna definición aquí es perfecta ni
inmutable, y el proceso no es lineal.

## Qué se reescribió, y por qué

Siete cosas motivaron el rediseño. Vale la pena leerlas porque son, además, una
lista de errores comunes en cualquier material sobre pipelines de datos.

**No mencionaba ELT.** Presentaba ETL como *la* forma de mover datos, cuando el
orden se invirtió al abaratarse el almacenamiento y volverse elástico el cómputo
del warehouse. Esa historia económica está ahora en [[etl-y-elt|ETL y ELT]] y es
lo más interesante de esa página.

**No explicaba la L.** Saltaba de la transformación a tidy data sin decir nunca
qué significa cargar. La carga es donde ocurren los errores que duplican dinero,
así que ahora tiene su propia sección, con append, overwrite, upsert y
sobrescritura por partición.

**Trataba lake y warehouse como binario.** El lakehouse colapsó esa distinción,
y el eje real —schema-on-write contra schema-on-read— nunca aparecía. Está en
[[el-viaje-de-los-datos|El viaje de los datos]].

**Solo contemplaba batch.** No había streaming ni CDC, más allá de una imagen de
terceros que decía «CDC» sin explicarlo. Los cuatro regímenes temporales están
ahora en [[cuando-se-rompe|Cuando se rompe]].

**No decía nada de lo que realmente rompe un pipeline.** Idempotencia,
backfills, evolución de esquema, contratos de datos, orquestación, linaje,
observabilidad y costo no aparecían en ninguna diapositiva. Toda la página
[[cuando-se-rompe|Cuando se rompe]] es nueva, y es la que justifica el rediseño:
es lo que separa a alguien que corrió un notebook de alguien que sostiene un
pipeline.

**Dibujaba el pipeline como una flecha.** Un pipeline es un grafo dirigido
acíclico —se bifurca y reconverge—, y de esa forma dependen el paralelismo, la
propagación de fallas y por dónde se reanuda. El deck nunca lo decía.

**Citaba el 60 % del tiempo sin fecha.** El dato viene de una encuesta de
CrowdFlower de alrededor de 2016. En [[eda|EDA]] se cita con su año y se marca
como lo que es a estas alturas: folklore reciclado de la industria, no un hecho
fresco. El argumento sobre por qué la limpieza domina el tiempo de un proyecto
funciona sin el número.

**Le faltaban roles.** No estaba el analytics engineer —el papel que creó dbt— ni
ninguno de los que aparecieron con los modelos de lenguaje. Y sobre todo, no
decía lo más útil para alguien que va a buscar su primer trabajo: que en una
empresa chica una sola persona hace siete de esos papeles. [[posiciones]] lo dice.

## Sobre las imágenes

Ninguna imagen del deck se reutilizó en esta unidad. Los diagramas que ves aquí
se generan con un script propio del repositorio, en español y con los colores del
curso, lo que los hace reproducibles y corregibles: si un diagrama está mal, se
corrige el generador y se vuelve a producir. Las del deck original eran arte de
plantilla y capturas de terceros sin licencia clara, que es exactamente el tipo
de dependencia que no conviene arrastrar de un semestre al siguiente.

Es, de paso, el mismo principio que [[pipeline-de-datos|abre la unidad]]: la
fuente es el generador, la imagen es el artifact, y el artifact se regenera. Una
imagen que no se puede volver a producir es un dato sin linaje, y ya sabemos qué
pasa con esos.
