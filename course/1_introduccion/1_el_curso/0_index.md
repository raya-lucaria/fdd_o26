---
id: el-curso
title: El curso
nav_title: El curso
summary: De qué trata Fuentes de Datos, cómo está organizado, cómo se califica y qué hay que hacer para la segunda clase.
status: ready
estimated_time: 10m
tags: [curso, evaluacion, temario, tareas]
---

# El curso

Fuentes de Datos trata de **cómo los datos llegan desde donde se generan hasta
donde se responde una pregunta**, y de las herramientas que hacen ese viaje
posible y, sobre todo, repetible. La tesis del curso es que esa segunda palabra
es la que cuesta: casi cualquiera puede obtener un número una vez, en su máquina,
con los datos que descargó el martes. Lo difícil es que el mismo proceso vuelva a
correr mañana, con datos nuevos, en una máquina que no es la tuya, y dé un
resultado que puedas defender.

Por eso el curso no es un catálogo de tecnologías. Cada módulo aparece como
respuesta a una falla concreta del viaje. La terminal y el shell existen porque
los datos llegan en archivos que hay que mover, inspeccionar y transformar sin
abrirlos a mano. Git y GitHub existen porque un proceso que solo vive en tu
carpeta no es reproducible ni colaborable. Docker existe porque «en mi máquina
sí funciona» es una respuesta inaceptable. Python profesional —tipos, validación,
pruebas, logging, configuración— existe porque un script que nadie puede leer ni
verificar es una deuda, no un activo. Y la concurrencia y la arquitectura de
sistemas existen porque el volumen y la latencia acaban rompiendo cualquier
solución que funcionaba bien cuando el archivo cabía en memoria.

Lo que el curso quiere dejarte no es una lista de comandos, sino el criterio para
mirar un flujo de datos y saber dónde se va a romper.

## Temario

El temario está organizado en cinco fases. **Es provisional**: se va a ajustar
durante el semestre según el ritmo del grupo y los temas que resulten más útiles.
El calendario, en cambio, sí está completo desde hoy, y ahí aparece el tema
asignado a cada sesión.

| Fase | De qué va |
|---|---|
| **1. Fundamentos de infraestructura** | La máquina antes del código: pipeline de datos, sistemas operativos, terminal, bash y shell scripting, expresiones regulares |
| **2. Control de versiones y contenedores** | Git y GitHub como el sustrato del trabajo reproducible; Docker e imágenes como la forma de que el entorno viaje con el proceso |
| **3. Python profesional** | De escribir Python a sostenerlo: gestión de dependencias con uv, memoria y referencias, Pydantic, patrones funcionales, metaprogramación, logging, configuración, arquitectura, testing y despliegue |
| **4. Computación y concurrencia** | Qué hace la máquina de verdad: arquitectura de computadoras, concurrencia y paralelismo, y diseño de sistemas distribuidos, APIs y almacenamiento |
| **5. Integración** | Temas avanzados según los intereses del grupo, y el cierre con el proyecto final |

La progresión es deliberada: primero la máquina, luego la disciplina de trabajo,
luego el lenguaje bien usado, luego lo que pasa cuando el problema deja de caber
en una sola computadora.

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

### Cómo funciona el 20 % de tareas y controles

Ese componente **no es el promedio de las dos cosas: es la menor de las dos**. Si
terminas el semestre con 9 de promedio en tareas y 6 en controles, el componente
se calcula sobre 6.

La razón es directa. Las tareas se hacen con tiempo, con apuntes y con ayuda —de
compañeros, de documentación y de modelos de lenguaje—; los controles se
responden solo y en el momento. Cuando una nota es muy superior a la otra, casi
siempre significa que el trabajo se entregó pero no se entendió, o que se entendió
pero no se practicó. Este esquema hace que ninguna de las dos rutas alcance por sí
sola: hay que sostener las dos.

### El resto

**Los proyectos son la mitad de la calificación** —30 % el final más 10 % de cada
uno de los dos parciales—. La proporción es deliberada: este es un curso sobre
construir cosas que funcionan más de una vez, y eso no se demuestra en un examen.

**Los dos exámenes parciales** suman 20 % y cubren lo que hay que tener en la
cabeza sin consultar: qué hace cada herramienta, qué supone, y cuándo aplica y
cuándo no.

**La participación** es 10 %. Varias sesiones son prácticas y dependen de que
llegues con el entorno funcionando y con el material leído.

## Dónde vive todo

El curso tiene dos caras de la misma moneda:

- **El repositorio**: https://github.com/raya-lucaria/fdd_o26 — la fuente. Ahí
  están las notas en Markdown, el calendario, la definición de cada tarea y el
  código de ejemplo.
- **Este sitio** — el repositorio construido y publicado. Se regenera solo en
  cada push, así que nunca está desincronizado con la fuente.

Vale la pena que notes lo que eso implica, porque es el primer pipeline de datos
que vas a ver en el curso y lo tienes enfrente: una fuente en texto plano, un
paso de validación que falla si algo no cumple el contrato, una construcción
determinista y un despliegue automático. Misma fuente, mismo resultado, todas las
veces.

### Cómo se entregan las tareas

Las tareas se entregan **en el repositorio, mediante un pull request** contra él.
No hay correo de entrega ni plataforma paralela. El mecanismo completo —clonar,
ramificar, commitear, abrir el pull request— se ve en el módulo de Git, y hasta
entonces no se te va a pedir que lo uses. Las dos tareas de esta primera semana no
requieren entregar nada por esa vía todavía; requieren que dejes tu entorno listo.

## Las primeras dos tareas

Ambas vencen el **jueves 13 de agosto de 2026**, es decir, para la segunda clase.
Son de preparación: sin ellas, la segunda sesión no te va a servir de mucho.

### Tarea 1 — Crear cuentas: LLMs y DataCamp

Este curso usa modelos de lenguaje como herramienta de trabajo, no como
curiosidad, y conviene que conozcas más de uno porque no se comportan igual. Crea
cuenta en todas estas plataformas:

- **Google Gemini** — https://gemini.google/ — hay un **plan gratuito de un año
  para estudiantes**, aprovéchalo: https://gemini.google/mx/students/?hl=es-419
- **OpenAI (ChatGPT)** — https://chatgpt.com/
- **Anthropic (Claude)** — https://claude.ai/
- **Mistral AI** — https://mistral.ai/
- **Perplexity** — https://www.perplexity.ai/
- **DeepSeek** — https://deepseek.com/

Además, **verifica que Google Colab te funcione**: entra a https://colab.google/,
crea un notebook nuevo y ejecuta una celda. No basta con que cargue la página; lo
que se verifica es que puedas correr código.

Después, la cuenta de **DataCamp con acceso institucional**. Es obligatorio usar
tu correo `@itam.mx`:

1. Entra a https://app.datacamp.com/ e inicia sesión con tu correo `@itam.mx`.
   **Si tienes otra sesión de DataCamp abierta, ciérrala antes de continuar** —
   este es el error más común, y si te unes al grupo con la cuenta equivocada,
   deshacerlo es una molestia.
2. Ya con la sesión correcta, únete al grupo de la clase con este enlace de
   invitación:
   https://www.datacamp.com/groups/shared_links/af811a55e5f91a7c05c65caeafacc2bd784d36a969bc062cc73c7397fb47ce6f
3. Verifica el acceso abriendo cualquier curso. Te sugiero abrir directamente el
   de la tarea siguiente para matar dos pájaros de un tiro.

### Tarea 2 — Curso: AI Assisted Coding for Developers

En DataCamp, completa **solo las dos primeras unidades** del curso
[AI Assisted Coding for Developers](https://app.datacamp.com/learn/courses/ai-assisted-coding-for-developers):

1. *Unlocking the Power of AI in Code*
2. *Prompt Engineering for Real-World Coding Tasks*

La evidencia de haberlo hecho se sube más adelante, al cerrar el módulo de Git,
cuando ya sepas abrir un pull request. El curso, en cambio, hay que hacerlo
**ahora**: las tareas de las siguientes semanas dan por hecho que sabes pedirle
código a un modelo y, más importante, revisar lo que te devuelve.
