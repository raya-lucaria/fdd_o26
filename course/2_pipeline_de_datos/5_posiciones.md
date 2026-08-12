---
id: posiciones
title: Posiciones
nav_title: Posiciones
summary: Quién se hace responsable de cada tramo del pipeline, y por qué en una empresa chica una sola persona hace siete de estos papeles.
status: ready
estimated_time: 18m
tags: [roles, carrera, equipos]
prerequisites: [cuando-se-rompe]
---

# Posiciones

::: figure {#ilus-oficios title="Siete estaciones, siete instrumentales distintos"}
![Taller industrial vacío con siete estaciones de trabajo contiguas, cada una con su banco y su tablero de herramientas colgadas: llaves, manómetros, soldadura, instrumentos de medición](_assets/ilus-oficios.jpg)
:::

Un pipeline roto a las tres de la mañana tiene una pregunta más urgente que la
técnica: **a quién se le avisa**. Esta página recorre los papeles que existen en
un equipo de datos, no como catálogo de puestos para una feria de empleo, sino
como reparto de responsabilidades sobre el pipeline que llevamos cinco páginas
describiendo.

Conviene decir de entrada lo que casi ningún material dice: **los títulos no son
estables**. La misma responsabilidad se llama distinto en dos empresas, y el
mismo título cubre trabajos muy distintos. Lo que sí se mantiene entre
organizaciones es el conjunto de responsabilidades, así que vale más aprender el
mapa que la nomenclatura.

## El reparto sobre el pipeline

| Rol | Tramo del pipeline | Pregunta que le corresponde |
|---|---|---|
| Ingeniere de datos | Extract, Load, orquestación, almacenamiento | ¿Los datos llegan, completos y a tiempo? |
| Analytics engineer | Transform dentro del warehouse | ¿Las tablas significan lo que dicen significar? |
| Analista de datos | EDA, reportes, tableros | ¿Qué está pasando y qué decisión sugiere? |
| Científique de datos | Modelado, experimentación | ¿Qué se puede predecir o explicar? |
| ML engineer | Modelos en producción | ¿El modelo responde, escala y sigue siendo válido? |
| MLOps | Ciclo de vida del modelo | ¿Se puede reproducir, monitorear y revertir? |
| DevOps / SRE | Infraestructura y despliegue | ¿Está arriba y se puede desplegar sin miedo? |
| Backend | Sistemas que generan y sirven datos | ¿La API y la base aguantan? |
| Frontend / UX | Consumo humano del resultado | ¿Alguien entiende lo que ve? |
| Product owner | Qué se construye y en qué orden | ¿Esto resuelve un problema real? |
| Project manager | Tiempos, recursos, riesgos | ¿Llega, y a qué costo? |

## Los papeles, uno por uno

**Ingeniere de datos.** Diseña, construye y mantiene la infraestructura por la
que los datos se mueven: extracciones, cargas, almacenamiento, orquestación. Es
quien se lleva la llamada de las tres de la mañana. Todo el capítulo
[[cuando-se-rompe|Cuando se rompe]] describe, en buena medida, su trabajo: la
idempotencia, los contratos, los reintentos y el costo son sus problemas antes
que los de nadie. Su stack habitual es SQL, Python, un orquestador y las
herramientas de la nube en la que viva la empresa.

**Analytics engineer.** Es el papel más reciente de la lista y el que menos se
entiende. Nació de una brecha concreta: el ingeniere de datos entrega tablas
crudas, el analista necesita tablas con significado de negocio, y durante años
esa transformación intermedia la hacía cada analista por su cuenta, en su propia
consulta, con su propia definición de «cliente activo». El resultado predecible
eran cinco definiciones distintas de la misma métrica y cinco números distintos
en la misma junta.

El analytics engineer construye y mantiene esa capa de transformación como
**código versionado, probado y documentado** —la T de ELT, viviendo dentro del
warehouse—. La herramienta que creó el papel es **dbt**, que trajo al mundo del
SQL prácticas que ya eran normales en desarrollo de software: control de
versiones, pruebas automáticas sobre los datos, documentación generada y linaje
explícito entre modelos. Si te interesa el punto donde la ingeniería de software
y el análisis de datos se tocan, este es el papel.

**Analista de datos.** Examina los datos existentes para responder preguntas de
negocio y sostener decisiones: reportes, tableros, análisis puntuales. Es quien
más cerca está de la pregunta real y quien primero detecta cuando un número dejó
de tener sentido. Su valor no está en la herramienta sino en saber qué pregunta
vale la pena hacer, y en decir «esos datos no permiten concluir eso» cuando toca.

**Científique de datos.** Aplica estadística y aprendizaje máquina para
encontrar patrones, construir modelos predictivos y diseñar experimentos. La
diferencia con el analista no es de jerarquía ni de sofisticación: el analista
responde qué pasó y qué está pasando; el científique responde qué va a pasar o
qué causaría un cambio. Buena parte de su trabajo real, y esto sorprende a quien
llega desde un curso de modelos, es EDA y preparación de datos.

**ML engineer.** Lleva los modelos a producción y los mantiene ahí: latencia,
escala, versionado, servicio. Un modelo en un notebook y un modelo respondiendo
diez mil peticiones por minuto son dos objetos distintos, y el segundo es un
problema de ingeniería de software tanto como de aprendizaje máquina.

**MLOps.** Es más una práctica que un puesto, aunque se contrata como puesto.
Cubre el ciclo de vida completo del modelo: reproducibilidad del entrenamiento,
registro de versiones, monitoreo de la degradación —cuando los datos del mundo
dejan de parecerse a los del entrenamiento— y la capacidad de revertir a la
versión anterior cuando el modelo nuevo empeora las cosas. Es la idempotencia y
la observabilidad del capítulo anterior, aplicadas a modelos.

**DevOps y SRE.** Automatizan el ciclo de construcción, prueba y despliegue, y
sostienen la infraestructura. Integración continua, entrega continua,
infraestructura como código, monitoreo. Cuando el pipeline corre en contenedores
sobre una nube, esta gente es la razón de que corra.

**Developer, backend y frontend.** El **backend** construye los sistemas que
generan y sirven los datos: las APIs y las bases de datos operacionales que
alimentan el pipeline. Es, muy a menudo, el origen del que hablaba el contrato de
datos, y por eso la relación entre ingeniería de datos y backend es la que más se
beneficia de que ese contrato exista. El **frontend** construye la interfaz donde
el resultado se consume, con **UX/UI** decidiendo cómo se presenta. Un modelo
excelente presentado de forma incomprensible produce cero decisiones, que es
exactamente lo mismo que produce un modelo malo.

**Product owner.** Define y prioriza qué se construye y por qué, y traduce entre
el negocio y el equipo técnico. Es quien debería poder responder «¿qué decisión
va a cambiar por tener esto?» antes de que se escriba una línea de código.

**Project manager.** Gestiona tiempos, recursos y riesgos, y suele operar con
metodologías ágiles. Vale la pena decirlo con la misma franqueza con que lo decía
el material original: también es la persona encargada de presionar. Aprender a
sostener una estimación honesta, explicar por qué un backfill de cinco meses no
se hace en dos días y poner límites sin volverlo un conflicto es una habilidad
profesional tan real como saber SQL.

## Los papeles de la era de los modelos de lenguaje

Desde 2023 aparecieron títulos nuevos alrededor de los sistemas construidos sobre
modelos de lenguaje. Son recientes, y sus fronteras están menos asentadas que las
anteriores; conviene tratarlos como responsabilidades emergentes más que como
carreras consolidadas.

**AI engineer.** Construye aplicaciones sobre modelos que no entrenó: sistemas de
recuperación aumentada, agentes que usan herramientas, integraciones de modelos
con productos existentes. El trabajo se parece más a ingeniería de software y de
sistemas distribuidos que a aprendizaje máquina clásico. Y tiene un componente de
datos incómodo: la recuperación aumentada es, vista de cerca, **un pipeline de
datos** —extraer documentos, transformarlos en fragmentos, cargarlos a un índice
vectorial, mantenerlos actualizados—, con todos los problemas de esta unidad
intactos.

**Ingeniere de plataforma de modelos.** Despliega, sirve y optimiza modelos
propios o abiertos: cuantización, servicio en GPU, control de latencia y de
costo. Es MLOps con restricciones de hardware mucho más severas.

**Evaluación y calidad de sistemas de IA.** Diseña cómo se mide si un sistema
basado en modelos generativos está funcionando, cosa que no se resuelve con una
métrica de exactitud. Es un papel de datos: definir conjuntos de evaluación,
detectar regresiones entre versiones y monitorear el comportamiento en
producción.

Estos papeles no reemplazan a los anteriores. El equipo que construye un sistema
de recuperación aumentada sobre documentos corporativos sigue necesitando que
alguien garantice que esos documentos llegan completos, actualizados y con
permisos correctos, y eso es ingeniería de datos con otro nombre.

## La honestidad que falta en estas listas

Todo lo anterior describe una organización grande. En una empresa chica, en una
startup, o en la mayoría de los primeros trabajos, **una sola persona hace siete
de estos papeles a la vez**: escribe la extracción, la orquesta, la transforma,
hace el EDA, entrena el modelo, arma el tablero y explica el resultado en la
junta. No porque sea experta en las siete cosas, sino porque no hay nadie más.

Eso tiene una lectura práctica para lo que sigue en tu formación. La primera es
que la especialización temprana es un riesgo: si solo sabes entrenar modelos, en
un equipo de tres personas eres inservible seis días de cada siete. La segunda es
que el conjunto de habilidades que atraviesa todos estos papeles —terminal, Git,
Docker, SQL, Python, saber leer un log— no es infraestructura opcional alrededor
del trabajo interesante: **es lo que te permite hacer el trabajo interesante sin
depender de que otro te habilite el entorno**. Ese conjunto es, exactamente, el
temario de este curso.

La tercera lectura es sobre cómo elegir. No elijas por el título ni por el
salario reportado en una encuesta, que envejece más rápido que la tecnología.
Elige por qué pregunta de la tabla de arriba te resulta interesante contestar a
las tres de la mañana.

## Hacia adelante

La última página de la unidad, [[presentacion-pipeline|Presentación]], deja a la
mano el material del semestre anterior, para comparar qué se conservó y qué se
reescribió.
