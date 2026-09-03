---
id: git-y-github
title: "Git y GitHub"
nav_title: "Git y GitHub"
summary: "Dos secciones. Primero Git en tu propia máquina, sin internet. Después GitHub, y el flujo con el que se entrega todo el resto del curso."
status: ready
estimated_time: 214m
tags: [git, github, ssh, commit, branch, merge, fork, pull-request, flujo]
prerequisites: [expresiones-regulares]
---

# Git y GitHub

![Sala de servidores nocturna en verde y ámbar: una silueta de espaldas sostiene contra el pecho una pieza que brilla en ámbar, mientras una copia verde de esa misma pieza viaja por un haz de luz hasta encajar en la ranura de un monolito al fondo; del monolito bajan cuatro líneas paralelas que se unen en una sola.](_assets/ilus-git-portada.jpg)

## En corto

- **Git es una herramienta que vive en tu máquina y no sabe qué es internet.** GitHub es una empresa que hospeda repositorios de Git y le agrega encima lo que Git no tiene.
- Son cosas distintas, y por eso la unidad está partida en **dos secciones**.
- La primera no toca la red ni una vez. La segunda es toda red.
- Al final vas a abrir un pull request. Ése es el examen práctico de la unidad.

## Las dos secciones

::: table {#git-mapa-unidad title="Dónde empieza y dónde acaba cada una"}

| Sección | Empieza en | Acaba cuando | Páginas | Tiempo |
|---|---|---|---:|---:|
| **[[seccion-git|1. Git]]** | La historia del problema, en 2005 | Resolviste un conflicto entre dos branches, sin conexión | 6 | 107 min |
| **[[seccion-github|2. GitHub]]** | Tu cuenta y tu llave SSH | Tu pull request está abierto y en verde | 6 | 102 min |

:::

La línea que las separa es exacta: **en la sección de Git no existe la red.** No hay fork, no hay `push`, no hay `origin`, no hace falta cuenta. Todo lo que aparece ahí funcionaría en una máquina desconectada para siempre.

En la sección de GitHub aparece todo eso de golpe, y con ello la parte que se usa cada semana: cómo se entrega el trabajo de este curso.

### Sección 1 — Git

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 1 | [[de-donde-viene-git|De dónde viene Git]] | Qué problema resuelve, y por qué es distribuido | 8 min |
| 2 | [[tu-primer-repositorio|Tu primer repositorio]] | Las tres zonas: `status`, `add`, `commit`, `log`, `diff` | 30 min |
| 3 | [[que-guarda-un-commit|Qué guarda un commit]] | Blob, tree y commit; el hash sale del contenido | 12 min |
| 4 | [[lo-que-no-se-sube|Lo que no se sube]] | Por qué `git add .` es la peor costumbre; el `.gitignore` | 12 min |
| 5 | [[deshacer-en-git|Deshacer]] | `restore`, `reset`, `stash` y la red de seguridad | 20 min |
| 6 | [[branches-y-merge|Branches y merge]] | La branch como etiqueta; provócate un conflicto y resuélvelo | 25 min |

### Sección 2 — GitHub

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 1 | [[cuenta-y-llave|Cuenta y llave]] | La cuenta y el par de llaves SSH. **Setup previo a clase** | 25 min |
| 2 | [[clonar-y-actualizar|Clonar y mantener al día]] | El repositorio del curso en tu disco. **Setup previo a clase** | 20 min |
| 3 | [[git-no-es-github|Git no es GitHub]] | El fork, `upstream` y `origin`, y arreglar tus remotes | 25 min |
| 4 | [[dos-personas-un-archivo|Dos personas, un archivo]] | Qué pasa cuando dos trabajan a la vez, y quién gana | 12 min |
| 5 | [[el-flujo-del-curso|El flujo del curso]] | La zona roja y la verde, y la regla del mirror | 15 min |
| 6 | [[el-ritual-del-curso|El ritual]] | Los tres bloques, en orden, con sus comandos | 10 min |

### Para consultar después

| Página | Qué es |
|---|---|
| [[cheatsheet-git|Cheatsheet]] | Todos los comandos de la unidad, agrupados por lo que quieres hacer |

## En qué orden leerlas

Las dos primeras páginas de la sección de GitHub son el setup que se pidió **antes** de clase, así que en el calendario van primero. Están archivadas bajo GitHub porque eso es lo que son: crear una cuenta y una llave no tiene nada que ver con Git como herramienta.

Para leer la unidad completa, el orden natural es el de arriba: Git entero, y después GitHub. **La sección de Git no necesita nada de la de GitHub**, ni siquiera la llave SSH.

## Por qué esta unidad importa más que las otras

Las demás unidades te enseñan a pensar sobre algo. Ésta te deja la mesa puesta.

De aquí en adelante todo se entrega por Git, así que lo que aprendas aquí lo vas a usar cada semana hasta diciembre. Y hay una parte, el ritual de la última página, que se pide con una precisión que puede parecer exagerada: es porque un programa lo revisa automáticamente, y un programa no interpreta intenciones.

## Antes de empezar

Necesitas la terminal de [[terminal-directa|Terminal: uso directo]] y Git instalado:

```bash
git --version
```

Tiene que ser **2.23 o más nueva**, de 2019, porque la unidad usa `git switch` y `git restore`. Para la sección de Git no hace falta nada más.

## Dos reglas

> [!WARNING]
> Tu llave **privada** no se comparte nunca. El único archivo que se copia a algún lado es el que termina en `.pub`.

> [!WARNING]
> En el repositorio del curso sólo escribes dentro de `estudiantes/` y en la carpeta que lleva **tu** nombre de usuario. Todo lo demás es de lectura.

## Qué te llevas

- Saber qué guarda Git y por qué, no sólo qué comandos teclear.
- Un repositorio de juguete donde ya rompiste cosas y las arreglaste: conflictos, `reset`, `stash`.
- Tu fork del repositorio del curso, con `upstream` y `origin` bien configurados.
- El flujo de entrega, que vas a repetir cada semana hasta diciembre.
