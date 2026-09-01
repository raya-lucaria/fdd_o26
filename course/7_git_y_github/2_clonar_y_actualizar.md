---
id: clonar-y-actualizar
title: "Clonar y mantener al día"
nav_title: "Clonar y actualizar"
summary: "Clona el repositorio del curso, configura tu identidad en git y compruébate que puedes traer lo nuevo con git pull."
status: ready
estimated_time: 20m
tags: [git, clone, pull, https, respaldo]
prerequisites: [cuenta-y-llave]
---

# Clonar y mantener al día

**Hoja 2 de 2** · 20 min

Meta: tener el repositorio del curso en tu disco y poder traer lo nuevo con un comando.

::: figure {#git-flujo title="Este repositorio lo lees; no escribes en él"}
![A la izquierda el repositorio del curso en GitHub; a la derecha tu copia local. Una flecha baja el código con git clone la primera vez y otra lo actualiza con git pull cada vez que hay algo nuevo. Una tercera flecha roja de vuelta aparece marcada como que no aplica. Abajo, una caja punteada anuncia que el trabajo se hará sobre un fork propio, más adelante](_assets/git-flujo.svg)
:::

## En corto

- `git clone` se corre **una vez**; después `git pull` trae lo nuevo.
- En este repositorio **sólo lees**. No tienes permiso de escritura y no lo necesitas.
- Cuando toque trabajar será sobre un **fork** tuyo. Eso lo vemos en clase.

## Paso 1: quién eres

Git firma cada commit con un nombre y un correo. Todavía no vas a hacer commits aquí, pero esto se configura una vez por computadora y conviene dejarlo listo desde ahora.

**Haz:** usa el mismo correo de tu cuenta de GitHub, para que los commits se asocien a tu perfil.

```bash
git config --global user.name  "Tu Nombre"
git config --global user.email "tu-correo@ejemplo.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global --list
```

**Deberías ver** las cuatro líneas que acabas de poner. `--global` significa «para todos los repositorios de esta computadora»: se hace una vez en la vida de la máquina.

## Paso 2: clona el repositorio

**Haz:**

```bash
mkdir -p ~/fdd && cd ~/fdd
git clone git@github.com:raya-lucaria/fdd_o26.git
cd fdd_o26
git remote -v
git log --oneline -5
```

**Deberías ver** el clonado bajando objetos, después dos líneas de `remote -v` que terminan en `fdd_o26.git`, y los últimos cinco commits del curso.

Si prefieres no usar SSH, `git clone https://github.com/raya-lucaria/fdd_o26.git` también funciona para **leer**, porque el repositorio es público. Pero para subir te va a pedir un token cada vez. Por eso hicimos la llave.

**Pausa:** ya tienes el curso completo en tu disco. `ls` te muestra `course/`, `tools/`, `skins/`. Todo el sitio que has estado leyendo sale de ahí.

## Paso 3: trae lo nuevo

Durante el semestre el repositorio va a cambiar: páginas nuevas, correcciones, material. `git pull` trae esos cambios a tu copia.

**Haz:**

```bash
cd ~/fdd/fdd_o26
git status
git pull
git log --oneline -3
```

**Deberías ver** que `git status` dice que tu rama está limpia, que `git pull` responde `Already up to date.` —o baja lo que falte— y que `git log` te muestra los commits más recientes.

Con eso terminaste: **si `git pull` funciona, tu configuración está bien.** Ése es el único comando que necesitas de aquí a que veamos el resto en clase.

| Comando | Qué hace |
|---|---|
| `git pull` | trae lo nuevo del repositorio |
| `git status` | te dice si tu copia está limpia |
| `git log --oneline -5` | los últimos cinco commits |

## Sobre este repositorio no vas a trabajar

Vale la pena decirlo claro para que nadie lo intente y se frustre: **no tienes permiso de escritura aquí, ni te hace falta.** Un `git push` te va a responder `Permission denied` o `403`, y eso es lo esperado, no un error tuyo.

Cuando llegue el momento de entregar trabajo, cada quien va a tener su **fork** —una copia del repositorio en su propia cuenta, donde sí escribes— y desde ahí se proponen los cambios. Eso tiene su propio orden y lo vemos en clase; por ahora no hagas nada al respecto.

## Paso 4: qué pasa cuando formatees la computadora

Esta es la pregunta que casi nadie hace a tiempo.

Tu llave privada **no se respalda y no se recupera**. Vive en `~/.ssh/` y si borras el disco, se va con él. Y está bien: no es un documento, es una credencial.

| Situación | Qué haces |
|---|---|
| Formateaste, o estrenas computadora | Repites la [[cuenta-y-llave|hoja 1]]: generas un par nuevo y lo agregas a la misma cuenta. Toma dos minutos. |
| Trabajas en dos máquinas | Una llave **por máquina**, las dos en la misma cuenta. Nunca copies la privada de una a otra. |
| Perdiste una laptop | Entra a GitHub y borra esa llave de Settings. Lo que estaba en `main` sigue en GitHub, intacto. |

Tu trabajo no vive en la llave: vive en GitHub. Mientras hayas hecho `push`, formatear no te quita nada.

::: problem {#git-p2-pull title="git pull dice que no puede"}
Corres `git pull` y responde que hay cambios locales que se perderían, o que tu copia diverge. No has tocado nada a propósito. ¿Qué pasó y qué miras primero?
:::

::: hint {of="git-p2-pull"}
`git pull` sólo se queja cuando tu copia tiene algo que él no puede reconciliar solo. Hay un comando que te dice exactamente qué.
:::

::: answer {of="git-p2-pull"}
Casi siempre es que abriste un archivo del repositorio y tu editor lo guardó con algún cambio —un salto de línea, un formateo automático—, o que corriste algo que escribió dentro de la carpeta.

Lo primero es `git status`, que te lista exactamente qué archivos difieren. Si no reconoces ninguno como tuyo, `git restore .` los devuelve a como estaban y `git pull` vuelve a funcionar.

`git restore .` **descarta** cambios sin confirmar, así que léelo con calma: aquí es seguro porque en este repositorio no estás trabajando, sólo leyendo. Si algún día ves ahí un archivo que sí escribiste tú, no lo descartes: cópialo fuera antes.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** `git pull` antes de ponerte a leer. Es el único comando que necesitas en este repositorio.

## Cierre

Ya tienes el repositorio y tu identidad configurada. No hay nada que subir: la unidad se da por terminada cuando `ssh -T` te saluda por tu nombre de usuario y `git pull` funciona dentro de `~/fdd/fdd_o26`. El resto —el fork, y cómo se proponen cambios— lo vemos en clase.
