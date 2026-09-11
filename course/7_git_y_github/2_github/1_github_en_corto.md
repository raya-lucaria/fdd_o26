---
id: github-en-corto
title: "GitHub, en corto"
nav_title: "GitHub, en corto"
summary: "De dónde sale el flujo del curso —el ciclo de contribución de código abierto—, qué le agrega GitHub a Git, y las dos comprobaciones que te dicen si ya puedes seguir."
status: ready
estimated_time: 15m
tags: [github, git, remote, setup, comprobacion]
prerequisites: [seccion-github]
---

# GitHub, en corto

**GitHub · página 1 de 6** · 15 min

Meta: ver de dónde sale el flujo del curso, y comprobar que tu máquina está lista.

## En corto

- Git corre en tu máquina. **GitHub es un servidor donde se guardan repositorios de Git**, con cosas encima que Git no tiene.
- La sección pasada fue sin conexión. Ésta es toda red.
- Hoy no se instala nada: se comprueba y se trabaja.
- Dos comprobaciones, y las dos son de `git`.

## Corre esto antes de leer nada más

```bash
# 1. ¿GitHub me reconoce?
ssh -T git@github.com

# 2. ¿tengo el repositorio del curso en el disco?
cd ~/fdd/fdd_o26 && git log --oneline -3

```

Con esas dos basta. **Todo el curso se hace con `git` y un navegador**; no hace falta instalar nada más.

::: table {#git-compuertas title="Qué hacer con cada resultado"}

| Comando | Bien si | Si falla, ve a |
|---|---|---|
| `ssh -T` | dice `Hi <tu-usuario>!` | [[cuenta-y-llave|Apéndice: cuenta y llave]] |
| `git log` | te muestra tres commits | [[clonar-y-actualizar|Apéndice: clonar]] |

:::

> [!NOTE]
> El mensaje de `ssh -T` **también** dice que GitHub no da acceso a una shell. Eso es parte de la respuesta correcta, no un error.

## Esto no lo inventó el curso

Antes de nada, para que lo que sigue no parezca burocracia de la materia.

::: figure {#git-contribucion title="Así se contribuye a cualquier proyecto de código abierto"}
![El ciclo con el que se contribuye a cualquier proyecto de codigo abierto: el repositorio del proyecto donde no tienes permiso de escritura, un fork que lo copia a tu cuenta, un clone que lo baja a tu maquina, una branch donde commiteas, un push que sube esa branch a tu fork, y un pull request que propone tus commits de vuelta al proyecto, cerrando el ciclo](../_assets/git-contribucion.svg)
:::

Nadie tiene permiso de escritura en Linux, ni en Python, ni en GitHub mismo. **Se propone, y alguien con permiso decide.** Esos cinco pasos —fork, clone, branch, push, pull request— son cómo entra un cambio a cualquier proyecto de código abierto del mundo.

El flujo de este curso **es ése**, sin adornos. El repositorio de la materia hace de proyecto, tú haces de contribuidor, y lo que propones vive dentro de tu carpeta para que treinta propuestas no choquen. Lo que aprendas aquí lo vas a usar igual el día que mandes tu primer parche a un proyecto que no es tuyo.

## Git vs GitHub, de una vez

Git es un programa, de 2005. GitHub es una empresa, de 2008, que Microsoft compró en 2018.

::: table {#git-vs-github title="Qué es de cada uno"}

| Es de Git | Es de GitHub |
|---|---|
| `commit`, `branch`, `merge`, `stash` | El **fork** |
| `push`, `pull`, `fetch`, `remote` | El **pull request** |
| El hash, la historia, la carpeta `.git` | Los issues y la revisión de código |
| Funciona sin internet | Actions y Pages |

:::

La columna izquierda existiría igual si GitHub cerrara mañana. La derecha no.

Y el matiz que más confunde: **Git sí sabe clonar.** Lo que agrega GitHub es hacer ese clone *en su servidor, dentro de tu cuenta*, y **recordar de dónde vino**. Ese recuerdo es lo que hace posible el pull request.

## El orden de la clase

```text
  1. GitHub, en corto   ← estás aquí
  2. El fork            → tu copia y tus dos remotes
  3. Branches           → practicarlas hasta que no den miedo
  4. Tu espejo          → dónde va cada archivo, y por qué
  5. El ritual          → los tres bloques del flujo
  6. El pull request    → la entrega de verdad
```

Al final de la página 6 vas a tener un pull request abierto. **Ése es el formato de todas las entregas de aquí a diciembre.**

> [!NOTE]
> **Si sólo recuerdas una cosa:** Git es el programa, GitHub es el servidor. El fork y el pull request son de GitHub; todo lo demás que aprendiste es de Git.

## Cierre

Con las tres comprobaciones en verde, sigue con [[el-fork|El fork y tus dos remotes]].
