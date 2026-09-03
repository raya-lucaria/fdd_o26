---
id: git-no-es-github
title: "Git no es GitHub"
nav_title: "Git no es GitHub"
summary: "Qué le agrega GitHub a Git, cómo arreglar el remote que te quedó apuntando al repositorio del curso, y qué son upstream y origin."
status: ready
estimated_time: 25m
tags: [github, fork, remote, upstream, origin, fetch, pull-request]
prerequisites: [branches-y-merge]
---

# Git no es GitHub

**Página 9 de 12** · 25 min

Meta: dejar tu máquina hablando con dos repositorios distintos y entender cuál es cuál.

::: figure {#git-tres-repos title="Tres repositorios, y sólo en dos puedes escribir"}
![Tres repositorios y las flechas entre ellos: arriba a la izquierda el del curso llamado upstream que sólo se lee, arriba a la derecha tu fork llamado origin donde sí escribes, y abajo tu copia en el disco. Una flecha baja lo nuevo con git fetch, otra sube tu trabajo con git push, y una punteada representa el pull request](_assets/git-tres-repos.svg)
:::

## En corto

- Todo lo de la clase pasada funcionó **sin conexión**. Eso es Git.
- GitHub es una empresa que hospeda repositorios y les agrega cosas que Git no tiene.
- Al clonar quedaste apuntando al repositorio del curso, donde **no puedes escribir**. Hay que arreglarlo hoy.
- Vas a terminar con dos remotes: `upstream` para bajar y `origin` para subir.

## La diferencia, dicha de una vez

Git se escribió en 2005 y es un programa que corre en tu máquina. GitHub se fundó en 2008, es una empresa, y Microsoft la compró en 2018. Son cosas distintas y se confunden porque casi nadie usa una sin la otra.

::: table {#git-vs-github title="Qué es de cada uno"}

| Es de Git | Es de GitHub |
|---|---|
| `commit`, `branch`, `merge`, `stash` | El fork |
| `push`, `pull`, `fetch`, `remote` | El pull request |
| El hash, la historia, la carpeta `.git` | Los issues y la revisión de código |
| Funciona sin internet | Actions y Pages |

:::

La columna izquierda existiría igual si GitHub cerrara mañana. La derecha no: son servicios construidos encima.

Un matiz sobre el fork, porque es el que más confunde: **Git sí sabe clonar**. Lo que agrega GitHub es hacer ese clone **en su servidor, dentro de tu cuenta**, y recordar de dónde vino, que es lo que después hace posible el pull request.

## Paso 1: haz tu fork

Esto se hace en el navegador. No hay comando.

**Haz:** entra a `https://github.com/raya-lucaria/fdd_o26`, presiona el botón **Fork** de arriba a la derecha, deja el nombre como está y confirma.

**Deberías ver**, unos segundos después, el mismo repositorio pero bajo tu cuenta, con una línea pequeña que dice que viene de `raya-lucaria/fdd_o26`.

Eso es tuyo. Ahí sí tienes permiso de escritura.

## Paso 2: averigua tu login exacto

Suena tonto y no lo es: cada semestre alguien crea su carpeta con el nombre equivocado y el robot se la rechaza. Tu **login** no es tu nombre de perfil.

**Haz:**

```bash
gh api user --jq .login
```

**Deberías ver** una sola palabra: tu usuario de GitHub, con sus mayúsculas exactas.

Si no tienes `gh` instalado, tu login es lo que aparece en `https://github.com/settings/profile`, en el campo *Username*. También es lo que sale en la URL de tu perfil.

**Haz:** guárdalo en una variable, y úsala de aquí en adelante en vez de teclearlo:

```bash
U=$(gh api user --jq .login)
echo "$U"
```

> [!WARNING]
> Esa variable vive sólo mientras la terminal esté abierta. Si cierras la ventana, la vuelves a definir. Cada vez que un comando de esta unidad diga `$U`, tiene que haber un `echo "$U"` correcto antes.

## Paso 3: arregla los remotes

Aquí está el paso que va a hacer fallar todo si lo saltas.

Cuando clonaste el repositorio del curso, Git guardó esa dirección con el nombre **`origin`**, que es su nombre por omisión. Pero `origin` es donde uno **sube** su trabajo, y en el repositorio del curso no tienes permiso.

**Haz:** mira cómo estás ahora.

```bash
cd ~/fdd/fdd_o26
git remote -v
```

**Deberías ver** dos líneas, las dos con `raya-lucaria/fdd_o26`. Ese es el problema: tu único remote apunta a un lugar donde no puedes escribir.

Un `remote` no es más que **un apodo para una URL**. `origin` no es una palabra reservada de Git: es una convención. Y como es sólo un apodo, se puede renombrar.

**Haz:**

```bash
git remote rename origin upstream
git remote add origin git@github.com:$U/fdd_o26.git
git remote -v
```

**Deberías ver** cuatro líneas: dos de `origin` con **tu** usuario, y dos de `upstream` con `raya-lucaria`.

```text
origin    git@github.com:tu-login/fdd_o26.git (fetch)
origin    git@github.com:tu-login/fdd_o26.git (push)
upstream  git@github.com:raya-lucaria/fdd_o26.git (fetch)
upstream  git@github.com:raya-lucaria/fdd_o26.git (push)
```

**Pausa:** si algo salió raro, la salida de rescate es borrar la carpeta y clonar tu fork directamente, que ya viene con el `origin` correcto:

```bash
cd ~/fdd && rm -rf fdd_o26
git clone git@github.com:$U/fdd_o26.git
cd fdd_o26 && git remote add upstream git@github.com:raya-lucaria/fdd_o26.git
```

## Paso 4: los nombres, y qué significan

::: table {#git-tres-nombres title="Quién es quién"}

| Nombre | Qué es | Puedes escribir |
|---|---|---|
| `upstream` | `raya-lucaria/fdd_o26`, el repositorio del curso | No, y no lo necesitas |
| `origin` | Tu fork, en tu propia cuenta | Sí |
| Tu disco | `~/fdd/fdd_o26` | Sí, es donde trabajas |

:::

La palabra `upstream` es una metáfora de río: el material fluye **de arriba hacia abajo**, del curso hacia ti. Tú nunca empujas río arriba con un comando; para eso está el pull request.

## Paso 5: trae lo nuevo del curso

**Haz:**

```bash
git switch main
git fetch upstream
git merge upstream/main
```

**Deberías ver** que `fetch` baja objetos y que `merge` responde `Already up to date` o hace un fast-forward.

Se enseñan por separado a propósito, porque hacen dos cosas distintas:

- **`git fetch upstream`** baja lo que hay en el curso y lo deja aparte, en `upstream/main`. **No toca tus archivos.** Es siempre seguro.
- **`git merge upstream/main`** toma eso y lo junta con la rama donde estás parado. Aquí sí cambian tus archivos, y aquí sí puede haber conflicto.

Ese conflicto se resuelve exactamente como el de la página anterior, con los mismos marcadores y con `git merge --abort` como salida.

`git pull` es un atajo que hace las dos cosas de un jalón. Funciona, y con la configuración que dejamos puesta en la primera clase equivale exactamente a `fetch` más `merge`. Pero mientras aprendes conviene separarlas, porque cuando algo falla necesitas saber cuál de las dos falló.

## Paso 6: sube a tu fork

**Haz:**

```bash
git push origin main
```

**Deberías ver** que sube sin pedirte nada, gracias a la llave SSH de la primera clase. Y en el navegador, tu fork ahora tiene los mismos commits que el curso.

Ese es el ciclo completo: **bajas del curso, subes a tu fork.** Tu disco habla con los dos, cada uno para una cosa.

## El pull request, y la historia compartida

El pull request **no es un comando de Git**. Es un botón de GitHub que dice, más o menos: tengo unos commits en mi rama, ¿los quieres en la tuya? La otra persona los revisa, comenta, y decide.

Y ahora que existe algo compartido, la línea de la página 7 empieza a importar.

Mientras trabajabas solo, reescribir la historia con `reset` era gratis. En el momento en que haces `push`, tus commits están en un lugar donde otros pueden verlos y bajarlos. Si después reescribes esa historia y fuerzas la subida, la copia de los demás deja de coincidir con la tuya, y arreglarlo es doloroso para ellos, no para ti.

Por eso hay dos herramientas para deshacer algo ya compartido:

- **`git revert <hash>`** crea un commit nuevo que hace lo contrario del anterior. No borra nada, y por eso es seguro. Es lo correcto casi siempre.
- **`git push --force`** impone tu versión y descarta lo que hubiera. Es lo que rompe el trabajo ajeno.

Existe `git push --force-with-lease`, que al menos se niega si alguien subió algo que tú no has visto. Lo menciono para que sepas que existe: **no lo vas a necesitar en este curso**, y si crees que lo necesitas, es señal de que hay que revisar el flujo, no de forzar.

::: problem {#git-p9-remote title="Permission denied al hacer push"}
Un compañero hizo su fork, clonó el repositorio del curso la semana pasada, y hoy corre `git push origin main`. GitHub le responde con un error de permisos y un 403. Insiste en que su llave SSH funciona, y tiene razón: `ssh -T` lo saluda por su nombre.

¿Qué está pasando y qué comando lo diagnostica?
:::

::: hint {of="git-p9-remote"}
La llave dice quién eres, no a dónde estás mandando. El error no es de identidad, es de destino.
:::

::: answer {of="git-p9-remote"}
Su `origin` **sigue apuntando al repositorio del curso**, no a su fork. Clonó de `raya-lucaria/fdd_o26` y Git guardó esa dirección con el nombre `origin`. Haber hecho el fork en el navegador no cambia nada en su máquina: son dos cosas separadas.

Así que el push va contra `raya-lucaria/fdd_o26`, donde nadie le dio permiso de escritura. GitHub lo reconoce perfectamente por su llave, y justo por eso puede decirle que esa persona no tiene permiso ahí.

Se diagnostica con `git remote -v`. Si las cuatro líneas dicen `raya-lucaria`, ése es el problema.

Se arregla con los dos comandos del paso 3: `git remote rename origin upstream` y `git remote add origin` con la URL de su fork. Después `git remote -v` debe mostrar los dos nombres distintos.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** `upstream` es de donde bajas y `origin` es a donde subes. Si `git remote -v` no muestra los dos, nada del flujo va a funcionar.

## Cierre

Ya tienes los tres repositorios conectados. Antes de usarlos, en [[dos-personas-un-archivo|Dos personas, un archivo]] vas a ver qué pasa cuando dos personas trabajan a la vez.
