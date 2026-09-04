---
id: seccion-github
title: "GitHub"
nav_title: "GitHub"
summary: "Lo que GitHub le agrega a Git: hospedaje, forks y pull requests. Aquí vive el flujo con el que se entrega el resto del curso."
status: ready
estimated_time: 102m
tags: [github, ssh, fork, upstream, origin, pull-request, flujo]
prerequisites: [trabajo-en-paralelo]
---

# GitHub

**Sección 2 de 2** · 6 páginas · unos 102 min

Meta: dejar tu máquina hablando con dos repositorios, y saber de memoria el flujo de entrega.

## En corto

- GitHub **no es Git**: es una empresa que hospeda repositorios y les agrega cosas encima.
- Las dos primeras páginas son el setup que se pidió antes de clase. Si ya lo hiciste, sólo compruébalo.
- Aquí aparece el fork, y con él la distinción entre `upstream` y `origin`.
- Acaba en el flujo de entrega, que se pregunta de memoria en el examen.

## Dónde empieza y dónde acaba

Empieza donde acaba Git: ya sabes commitear, ramificar y mergear en tu máquina. **Todo lo que agrega esta sección es la red.**

Acaba cuando tienes un pull request abierto contra el repositorio del curso, con la revisión automática en verde. Ése es el formato de todas las entregas de aquí a diciembre.

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 1 | [[cuenta-y-llave|Cuenta y llave]] | La cuenta y el par de llaves SSH. **Setup previo a clase** | 25 min |
| 2 | [[clonar-y-actualizar|Clonar y mantener al día]] | El repositorio del curso en tu disco. **Setup previo a clase** | 20 min |
| 3 | [[git-no-es-github|Git no es GitHub]] | El fork, `upstream` y `origin`, y arreglar tus remotes | 25 min |
| 4 | [[dos-personas-un-archivo|Dos personas, un archivo]] | Qué pasa cuando dos trabajan a la vez, y quién gana | 12 min |
| 5 | [[el-flujo-del-curso|El flujo del curso]] | La zona roja y la verde, y la regla del mirror | 15 min |
| 6 | [[el-ritual-del-curso|El ritual]] | Los tres bloques, en orden, con sus comandos | 10 min |

## Sobre las dos primeras páginas

Son el setup que se entregó como tarea antes de la clase, y están aquí porque **eso es lo que son: configuración de GitHub**. Crear una cuenta y una llave SSH no tiene nada que ver con Git como herramienta.

Si ya las hiciste, compruébalo en treinta segundos y pasa a la página 3:

```bash
ssh -T git@github.com
ls ~/fdd/fdd_o26
```

El primero debe saludarte por tu nombre de usuario. El segundo debe listar el repositorio del curso.

## Qué te llevas

- Tu fork, con `upstream` y `origin` bien configurados y comprobados.
- Saber por qué un push rechazado casi nunca significa conflicto.
- El flujo de entrega, en tres bloques, que vas a repetir cada semana.

## Cierre

Al terminar, ten a mano el [[cheatsheet-git|cheatsheet]]. Está para consultarlo, con la única excepción de los tres bloques del ritual.
