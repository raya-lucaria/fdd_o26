---
id: posiciones
title: Posiciones
nav_title: Posiciones
summary: "Quién se hace responsable de cada tramo del pipeline, y por qué en una empresa chica una sola persona hace siete de estos papeles."
status: ready
estimated_time: 9m
tags: [roles, carrera, equipos]
prerequisites: [cuando-se-rompe]
---

# Posiciones

::: figure {#ilus-oficios title="Siete estaciones, siete instrumentales distintos"}
![Taller industrial vacío con siete estaciones de trabajo contiguas, cada una con su banco y su tablero de herramientas colgadas: llaves, manómetros, soldadura, instrumentos de medición](../_assets/ilus-oficios.jpg)
:::

## En corto

- Un pipeline roto a las tres de la mañana tiene una pregunta más urgente que la técnica: **a quién se le avisa**.
- **Los títulos no son estables**: aprende el mapa de responsabilidades, no la nomenclatura.
- El papel más reciente y peor entendido es el **analytics engineer**, y lo creó dbt.
- Desde 2023 hay papeles nuevos alrededor de los modelos de lenguaje; siguen siendo trabajo de datos.
- En una empresa chica, **una sola persona hace siete de estos papeles a la vez**.

## El reparto sobre el pipeline

| Rol | Tramo del pipeline | Su pregunta |
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

Sobre `ventas.csv`: rechazar o aceptar el `04/08/2026` y no duplicar la corrida del 4, ingeniere de datos; normalizar `D.F.` a `CDMX`, analytics engineer; el pedido 1003 en cero, analista de datos.

> [!NOTE]
> **Los títulos no son estables.** La misma responsabilidad se llama distinto en dos empresas, y el mismo título cubre trabajos muy distintos. Lo que se mantiene es el reparto de responsabilidades.

## Lo que la tabla no dice

### Ingeniere de datos

**Es quien se lleva la llamada de las tres de la mañana.** Todo [[cuando-se-rompe|Cuando se rompe]] describe su trabajo: idempotencia, contratos, reintentos y costo son sus problemas antes que los de nadie. Su stack es SQL, Python, un orquestador y la nube de la empresa.

### Analytics engineer

Es el papel más reciente y el que menos se entiende. Nació de una brecha concreta: el ingeniere entrega tablas crudas, el analista necesita tablas con significado de negocio, y durante años esa capa intermedia la hacía cada analista por su cuenta, con su propia definición de «cliente activo». El resultado eran **cinco números distintos en la misma junta**.

El analytics engineer construye esa capa como **código versionado, probado y documentado**: la T de ELT, dentro del warehouse. La creó **dbt**, que llevó al SQL esas prácticas de software, más linaje explícito. Si te interesa dónde se tocan la ingeniería de software y el análisis, este es el papel.

### Analista y científique de datos

La diferencia no es de jerarquía ni de sofisticación: **el analista responde qué pasó; el científique, qué va a pasar** o qué causaría un cambio.

El valor del analista está en saber qué pregunta vale la pena hacer y en decir «esos datos no permiten concluir eso» cuando toca. Y buena parte del trabajo real del científique, cosa que sorprende a quien llega desde un curso de modelos, es EDA y preparación de datos.

### ML engineer y MLOps

Un modelo en un notebook y uno respondiendo diez mil peticiones por minuto son objetos distintos. El **ML engineer** sostiene el segundo, que es tanto ingeniería de software como aprendizaje máquina.

**MLOps** es más práctica que puesto, aunque se contrate como puesto: reproducibilidad del entrenamiento, registro de versiones, monitoreo de la degradación y capacidad de revertir cuando el modelo nuevo empeora las cosas. Es **la idempotencia y la observabilidad del capítulo anterior, aplicadas a modelos**.

### DevOps, backend, frontend

**DevOps y SRE** automatizan construcción, prueba y despliegue. Cuando el pipeline corre en contenedores sobre una nube, esta gente es la razón de que corra.

El **backend** construye las APIs y bases operacionales que alimentan el pipeline: es, muy a menudo, **el origen del que hablaba el contrato de datos**, y por eso esa relación es la que más se beneficia de que el contrato exista.

El **frontend** y **UX/UI** deciden cómo se presenta el resultado. Un modelo excelente presentado de forma incomprensible produce cero decisiones: lo mismo que produce un modelo malo.

### Product owner y project manager

El **product owner** debería poder responder «¿qué decisión va a cambiar por tener esto?» antes de que se escriba una línea de código.

El **project manager** gestiona tiempos, recursos y riesgos, y —con franqueza— también es quien presiona. Sostener una estimación honesta, explicar por qué un backfill de cinco meses no se hace en dos días y poner límites sin volverlo un conflicto es **una habilidad tan real como saber SQL**.

## Los papeles de la era de los modelos de lenguaje

Desde 2023 hay títulos nuevos alrededor de los sistemas construidos sobre
modelos de lenguaje: **AI engineer**, que construye aplicaciones sobre modelos
que no entrenó; **ingeniere de plataforma de modelos**, que los despliega y
optimiza; y **evaluación de sistemas de IA**, que mide si funcionan. Trátalos
como responsabilidades emergentes, no como carreras consolidadas.

Ninguno reemplaza a los anteriores, y los tres son más parecidos a lo que ya
leíste de lo que su nombre sugiere: la recuperación aumentada, vista de cerca,
**es un pipeline de datos** —extraer documentos, fragmentarlos, cargarlos a un
índice, mantenerlos al día—. Quien la construye sigue necesitando que alguien
garantice que esos documentos llegan completos y actualizados.

## La honestidad que falta en estas listas

Todo lo anterior describe una organización grande. En una startup o en la mayoría de los primeros trabajos, **una sola persona hace siete de estos papeles a la vez**: escribe la extracción, la orquesta, la transforma, hace el EDA, entrena el modelo, arma el tablero y lo explica en la junta. No por experta en las siete cosas, sino porque no hay nadie más.

- **La especialización temprana es un riesgo.** Si solo sabes entrenar modelos, en un equipo de tres eres inservible seis días de cada siete.
- **Las habilidades transversales te desbloquean.** Terminal, Git, Docker, SQL, Python, saber leer un log: son lo que te permite hacer el trabajo interesante sin depender de que otro te habilite el entorno. Ese conjunto es, exactamente, el temario de este curso.
- **No elijas por el título ni por el salario de una encuesta**, que envejece más rápido que la tecnología. Elige por qué pregunta de la tabla te resulta interesante contestar a las tres de la mañana.

## Hacia adelante

La última página, [[presentacion-pipeline|Presentación]], deja a la mano el material del semestre anterior, para comparar qué se conservó y qué se reescribió.

## Qué te llevas

- Aprende **el reparto de responsabilidades**, no los títulos: cambian de empresa a empresa.
- El **analytics engineer** es donde la ingeniería de software entra al análisis de datos, y dbt es su herramienta.
- En equipos chicos haces de todo, así que **las habilidades transversales son las que te desbloquean**.
