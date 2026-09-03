---
id: git-y-github
title: "Git y GitHub"
nav_title: "Git y GitHub"
summary: "Dos clases: primero Git en tu propia máquina, sin internet, y después GitHub y el flujo con el que se entrega todo el resto del curso."
status: ready
estimated_time: 197m
tags: [git, github, ssh, commit, branch, merge, fork, pull-request, flujo]
prerequisites: [expresiones-regulares]
---

# Git y GitHub

![Sala de servidores nocturna en verde y ámbar: una silueta de espaldas sostiene contra el pecho una pieza que brilla en ámbar, mientras una copia verde de esa misma pieza viaja por un haz de luz hasta encajar en la ranura de un monolito al fondo; del monolito bajan cuatro líneas paralelas que se unen en una sola.](_assets/ilus-git-portada.jpg)

## En corto

- **Git es una herramienta que vive en tu máquina y no sabe qué es internet.** GitHub es una empresa que hospeda repositorios de Git y le agrega encima lo que Git no tiene.
- Ésa es la idea que sostiene la unidad entera. La primera clase no toca la red ni una vez.
- La segunda clase conecta las dos cosas y termina en el flujo con el que se entrega **todo el resto del curso**.
- Al final vas a abrir un pull request. Ése es el examen práctico de la unidad.

## Por qué esta unidad importa más que las otras

Las demás unidades te enseñan a pensar sobre algo. Ésta te deja la mesa puesta.

De aquí en adelante todo se entrega por Git, así que lo que aprendas en estas dos clases lo vas a usar cada semana hasta diciembre. Y hay una parte, el flujo de la última página, que se pide con una precisión que puede parecer exagerada: es porque un programa lo revisa automáticamente, y un programa no interpreta intenciones.

## El mapa de la unidad

**Setup.** Lo hiciste antes de clase. Si algo no quedó, arréglalo hoy.

| # | Página | Terminas cuando… | Tiempo |
|---:|---|---|---:|
| 1 | [[cuenta-y-llave|Cuenta y llave]] | `ssh -T` te saluda por tu nombre de usuario | 25 min |
| 2 | [[clonar-y-actualizar|Clonar y mantener al día]] | clonaste el repositorio y `git pull` te trae lo nuevo | 20 min |

**Primera clase: Git, sin internet.** Un repositorio de juguete que existe para romperse.

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 3 | [[de-donde-viene-git|De dónde viene Git]] | Qué problema resuelve, y por qué es distribuido | 8 min |
| 4 | [[tu-primer-repositorio|Tu primer repositorio]] | Las tres zonas: `status`, `add`, `commit`, `log`, `diff` | 30 min |
| 5 | [[que-guarda-un-commit|Qué guarda un commit]] | Blob, tree y commit; el hash sale del contenido | 12 min |
| 6 | [[lo-que-no-se-sube|Lo que no se sube]] | Por qué `git add .` es la peor costumbre; el `.gitignore` | 12 min |
| 7 | [[deshacer-en-git|Deshacer]] | `restore`, `reset`, `stash` y la red de seguridad | 20 min |

**Segunda clase: GitHub y el flujo.** Aquí aparece la red.

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 8 | [[branches-y-merge|Branches y merge]] | La branch como etiqueta; provócate un conflicto y resuélvelo | 25 min |
| 9 | [[git-no-es-github|Git no es GitHub]] | El fork, `upstream` y `origin`, y arreglar tus remotes | 25 min |
| 10 | [[dos-personas-un-archivo|Dos personas, un archivo]] | Qué pasa cuando dos trabajan a la vez, y quién gana | 12 min |
| 11 | [[el-flujo-del-curso|El flujo del curso]] | La zona roja y la verde, y la regla del mirror | 15 min |
| 12 | [[el-ritual-del-curso|El ritual]] | Los tres bloques, en orden, con sus comandos | 10 min |

**Para consultar después.**

| Página | Qué es |
|---|---|
| [[cheatsheet-git|Cheatsheet]] | Todos los comandos de la unidad, agrupados por lo que quieres hacer |

## Antes de empezar

Necesitas la terminal de [[terminal-directa|Terminal: uso directo]] y el setup de las dos primeras páginas ya hecho. Comprueba las tres cosas:

```bash
git --version
ssh -T git@github.com
ls ~/fdd/fdd_o26
```

La versión de Git tiene que ser **2.23 o más nueva**, de 2019, porque la unidad usa `git switch` y `git restore`. El `ssh -T` debe saludarte por tu nombre de usuario, y ese saludo dice que GitHub no da acceso a una shell, lo cual es parte de la respuesta correcta.

## Una regla que atraviesa las dos clases

> [!WARNING]
> Tu llave **privada** no se comparte nunca. El único archivo que se copia a algún lado es el que termina en `.pub`.

Y una segunda, que empieza a aplicar en la clase 2:

> [!WARNING]
> En el repositorio del curso sólo escribes dentro de `estudiantes/` y en la carpeta que lleva **tu** nombre de usuario. Todo lo demás es de lectura.

## Qué te llevas

- Saber qué guarda Git y por qué, no sólo qué comandos teclear.
- Un repositorio de juguete donde ya rompiste cosas y las arreglaste: conflictos, `reset`, `stash`.
- Tu fork del repositorio del curso, con `upstream` y `origin` bien configurados.
- El flujo de entrega, que vas a repetir cada semana hasta diciembre.
