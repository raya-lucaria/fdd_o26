---
id: seccion-git
title: "Git"
nav_title: "Git"
summary: "La herramienta que vive en tu máquina y no sabe qué es internet. Seis páginas sin conexión, en un repositorio de juguete que existe para romperse."
status: ready
estimated_time: 122m
tags: [git, commit, staging, branch, merge, deshacer]
prerequisites: [git-y-github]
---

# Git

**Sección 1 de 2** · 7 páginas · unos 122 min

Meta: entender qué guarda Git y por qué, trabajando en un repositorio que puedes destruir sin consecuencias.

## En corto

- **Nada de esta sección toca internet.** Ni una vez, ni siquiera para el primer commit.
- No necesitas cuenta de GitHub, ni llave SSH, ni conexión. Sólo `git` instalado.
- Vas a trabajar en `~/fdd/git-lab`, un repositorio de juguete que se borra y se rehace.
- Aquí se rompen cosas a propósito: un conflicto, un `reset --hard`, un archivo perdido.

## Dónde empieza y dónde acaba

Ésta es la primera de las dos mitades de la unidad. Empieza en la historia del problema y **acaba cuando puedes predecir un conflicto antes de provocarlo**, con el mecanismo del merge entendido.

Lo que **no** hay aquí: fork, pull request, `push`, `origin`, ni una sola conexión de red. Todo eso es la [[seccion-github|segunda sección]].

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 1 | [[de-donde-viene-git|De dónde viene Git]] | Qué problema resuelve, y por qué es distribuido | 8 min |
| 2 | [[tu-primer-repositorio|Tu primer repositorio]] | Las tres zonas: `status`, `add`, `commit`, `log`, `diff` | 30 min |
| 3 | [[que-guarda-un-commit|Qué guarda un commit]] | Blob, tree y commit; el hash sale del contenido | 12 min |
| 4 | [[lo-que-no-se-sube|Lo que no se sube]] | Por qué `git add .` es la peor costumbre; el `.gitignore` | 12 min |
| 5 | [[deshacer-en-git|Deshacer]] | `restore`, `reset`, `stash` y la red de seguridad | 20 min |
| 6 | [[branches-y-merge|Branches y merge]] | La branch como etiqueta; provócate un conflicto y resuélvelo | 25 min |
| 7 | [[trabajo-en-paralelo|Cuando dos avanzan a la vez]] | El merge de tres vías, los bloques de contexto y los casos raros | 15 min |

## Antes de empezar

Sólo una cosa, y es local:

```bash
git --version
```

Necesitas **2.23 o más nueva**, de 2019, porque la sección usa `git switch` y `git restore`.

> [!NOTE]
> Si ya hiciste el setup de la llave SSH que se pidió antes de clase, perfecto. Pero no hace falta para nada de esta sección: `git init` no le pregunta a nadie.

## Qué te llevas

- Un modelo mental de qué guarda Git, no una lista de comandos memorizados.
- Un repositorio donde ya rompiste cosas y las arreglaste.
- La costumbre de correr `git status` antes y después de cada `git add`.

## Cierre

Cuando termines las seis páginas, sigue con [[seccion-github|GitHub]], donde por fin aparece la red.
