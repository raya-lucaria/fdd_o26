---
id: el-curso
title: El curso
nav_title: El curso
summary: "De qué trata Fuentes de Datos, cómo está organizado, cómo se califica y qué hay que hacer para la segunda clase."
status: ready
estimated_time: 8m
tags: [curso, evaluacion, temario, tareas]
---

# El curso

## En corto

- El curso trata de **cómo los datos llegan desde donde se generan hasta donde se responde una pregunta**, y de hacer ese viaje repetible.
- No es un catálogo de tecnologías: **cada módulo responde a una falla concreta**.
- Son **32 sesiones en cinco fases**; el temario es provisional, el calendario no.
- El 20 % de tareas y controles es **el mínimo de los dos**, no el promedio.
- Hay **dos tareas para la segunda clase**, ambas del jueves 13 de agosto de 2026.

## De qué trata

Fuentes de Datos trata del viaje de los datos **desde donde se generan hasta donde se responde una pregunta**, y de las herramientas que lo hacen posible y, sobre todo, **repetible**.

Esa segunda palabra es la que cuesta. Casi cualquiera obtiene un número una vez, en su máquina, con los datos que descargó el martes. Lo difícil es que el mismo proceso vuelva a correr mañana, con datos nuevos, en una máquina que no es la tuya, y dé un resultado que puedas defender.

Por eso el curso no es un catálogo de tecnologías. **Cada módulo responde a una falla concreta del viaje.**

| Módulo | La falla que lo hace necesario |
|---|---|
| Terminal y shell | Los datos llegan en archivos que hay que mover y transformar sin abrirlos a mano |
| Git y GitHub | Un proceso que solo vive en tu carpeta no es reproducible ni colaborable |
| Docker | «En mi máquina sí funciona» es una respuesta inaceptable |
| Python profesional | Un script que nadie puede leer ni verificar es una deuda, no un activo |
| Concurrencia y arquitectura | El volumen y la latencia rompen lo que funcionaba cuando el archivo cabía en memoria |

Lo que el curso quiere dejarte no es una lista de comandos, sino **el criterio para mirar un flujo de datos y saber dónde se va a romper**.

## Temario

Son **32 sesiones en cinco fases**, con una progresión deliberada: primero la máquina, luego la disciplina de trabajo, luego el lenguaje bien usado, y al final lo que pasa cuando el problema deja de caber en una computadora.

> [!NOTE]
> El temario **es provisional**: se ajustará según el ritmo del grupo. El calendario ya está completo, y ahí aparece el tema de cada sesión.

### Fase 1 — Fundamentos de infraestructura

La máquina antes del código.

| # | Tema | De qué va |
|:-:|---|---|
| 1 | Introducción | Presentación del curso, objetivos y metodología |
| 2 | Pipeline de datos | Arquitectura de flujos de datos, ETL y ELT, principios de diseño |
| 3 | Sistemas operativos | Procesos, memoria, sistema de archivos, permisos |
| 4 | Terminal | Línea de comandos, navegación, manipulación de archivos |
| 5 | Bash & Shell | Scripting, variables, control de flujo, automatización |
| 6 | Regex | Expresiones regulares, patrones, búsqueda y transformación de texto |

### Fase 2 — Control de versiones y contenedores

Cómo se vuelve reproducible y colaborable lo que haces.

| # | Tema | De qué va |
|:-:|---|---|
| 7 | Git | Control de versiones, commits, ramas, merges |
| 8 | GitHub | Colaboración, pull requests, revisión de código, CI/CD |
| 9 | Docker I | Contenedores, imágenes, Dockerfile |
| 10 | Docker II | Docker Compose, redes, volúmenes, orquestación básica |

### Fase 3 — Python profesional

De escribir Python a sostenerlo.

| # | Tema | De qué va |
|:-:|---|---|
| 11 | Python básico | Sintaxis, tipos de datos, estructuras de control |
| 12 | IDEs | Entornos de desarrollo, depuración, extensiones |
| 13 | Gestión de dependencias | Entorno profesional con `uv`, ambientes virtuales, `pyproject.toml` |
| 14 | Memoria y referencias | Mecánica interna de Python, mutabilidad, referencias |
| 15 | Pydantic | Modelado de datos, validación, serialización |
| 16 | Patrones funcionales | Iteradores, generadores, comprehensions, `functools` |
| 17 | Metaprogramación | Decoradores, context managers, descriptores |
| 18 | Logging | Robustez y observabilidad, logging estructurado |
| 19 | Configuración | Variables de entorno, gestión de configuración, 12-Factor App |
| 20 | Arquitectura de software | Patrón repositorio, servicios, clean architecture |
| 21 | Testing | Testing profesional, `pytest`, mocking, fixtures |
| 22 | Despliegue | Docker multi-stage, producción, pipelines de CI/CD |

### Fase 4 — Computación y concurrencia

Qué hace la máquina de verdad, y qué pasa cuando el problema crece.

| # | Tema | De qué va |
|:-:|---|---|
| 23 | Arquitectura de computadoras | CPU, memoria, caché, fundamentos de hardware |
| 24 | Concurrencia I | Asíncrono vs concurrente vs paralelo |
| 25 | Concurrencia II | Threading, multiprocessing, el GIL |
| 26 | Concurrencia III | `asyncio`, event loops, `async`/`await` |
| 27 | Arquitectura de sistemas I | Diseño de sistemas distribuidos, escalabilidad |
| 28 | Arquitectura de sistemas II | Patrones de comunicación, APIs, microservicios |
| 29 | Arquitectura de sistemas III | Bases de datos, caching, colas de mensajes |

### Fase 5 — Integración

| # | Tema | De qué va |
|:-:|---|---|
| 30 | Por determinar | Tema avanzado según los intereses del grupo |
| 31 | Por determinar | Tema avanzado según los intereses del grupo |
| 32 | Cierre y proyecto final | Síntesis del curso y entrega del proyecto final |

## Evaluación

| Peso | Componente |
|---:|---|
| 30 % | Proyecto final |
| 20 % | **El mínimo** entre el promedio de tareas y el promedio de controles |
| 10 % | Examen parcial 1 |
| 10 % | Examen parcial 2 |
| 10 % | Proyecto 1 |
| 10 % | Proyecto 2 |
| 10 % | Participación |

### El 20 % es el mínimo, no el promedio

Si terminas con 9 en tareas y 6 en controles, el componente se calcula **sobre 6**.

Las tareas se hacen con tiempo, con apuntes y con ayuda; los controles se responden solo y en el momento. Cuando una nota es muy superior a la otra, casi siempre significa que el trabajo se entregó pero no se entendió, o que se entendió pero no se practicó.

### El resto

- **Los proyectos son la mitad de la calificación.** Este es un curso sobre construir cosas que funcionan más de una vez, y eso no se demuestra en un examen.
- **Los dos exámenes** cubren lo que hay que tener en la cabeza sin consultar: qué hace cada herramienta, qué supone, cuándo aplica y cuándo no.
- **La participación** depende de que llegues con el entorno funcionando y el material leído.

## Dónde vive todo

- **El repositorio**: https://github.com/raya-lucaria/fdd_o26 — la fuente: notas en Markdown, calendario, definición de cada tarea y código de ejemplo.
- **Este sitio** — el repositorio construido y publicado. Se regenera en cada push, así que nunca está desincronizado.

Es **el primer pipeline de datos del curso y lo tienes enfrente**: fuente en texto plano, validación que falla si algo no cumple el contrato, construcción determinista y despliegue automático.

### Cómo se entregan las tareas

Las tareas se entregan **en Canvas**. El repositorio y este sitio son de dónde sacas el material; Canvas es a dónde subes la evidencia de que hiciste el trabajo.

**Entrega de esta semana:** https://itam.instructure.com/courses/17979/assignments/225402

## Las primeras dos tareas

Ambas vencen el **jueves 13 de agosto de 2026**, para la segunda clase. Sin ellas, la segunda sesión no te va a servir de mucho.

### Tarea 1 — Crear cuentas: LLMs y DataCamp

Este curso usa modelos de lenguaje **como herramienta de trabajo**, y conviene conocer más de uno porque no se comportan igual. Crea cuenta en todas estas plataformas:

- **Google Gemini** — https://gemini.google/ — hay **plan gratuito de un año para estudiantes**: https://gemini.google/mx/students/?hl=es-419
- **OpenAI (ChatGPT)** — https://chatgpt.com/
- **Anthropic (Claude)** — https://claude.ai/
- **Mistral AI** — https://mistral.ai/
- **Perplexity** — https://www.perplexity.ai/
- **DeepSeek** — https://deepseek.com/

Además, **verifica que Google Colab te funcione**: entra a https://colab.google/, crea un notebook y ejecuta una celda. No basta con que cargue la página: lo que se verifica es que **puedas correr código**.

Después, la cuenta de **DataCamp con acceso institucional**, obligatoriamente con tu correo `@itam.mx`:

1. Entra a https://app.datacamp.com/ e inicia sesión con tu correo `@itam.mx`. **Si tienes otra sesión abierta, ciérrala antes** — es el error más común, y deshacerlo es una molestia.
2. Ya con la sesión correcta, únete al grupo de la clase: https://www.datacamp.com/groups/shared_links/af811a55e5f91a7c05c65caeafacc2bd784d36a969bc062cc73c7397fb47ce6f
3. Verifica abriendo cualquier curso. Con que abra, basta: por ahora no hay ninguno asignado, solo comprobamos que la cuenta quedó conectada.

### Tarea 2 — Curso: Claude 101

Completa el curso [Claude 101](https://academy.claude.com/courses/claude-101) de Claude Academy.

**La evidencia de haberlo completado se sube a Canvas**, en la entrega de esta semana: https://itam.instructure.com/courses/17979/assignments/225402

Hazlo **ahora**: las tareas de las siguientes semanas dan por hecho que sabes pedirle código a un modelo y, más importante, **revisar lo que te devuelve**.

## Qué te llevas

- El curso enseña a hacer **repetible** un proceso de datos; cada módulo responde a una falla concreta.
- **Los proyectos pesan la mitad**, y el bloque de tareas y controles se cuenta por el mínimo de los dos.
- **Este sitio es el primer pipeline del curso**: fuente en texto, validación, build determinista, despliegue automático.

**Una acción:** crea hoy las cuentas de la Tarea 1 y termina Claude 101 antes del jueves 13 de agosto.
