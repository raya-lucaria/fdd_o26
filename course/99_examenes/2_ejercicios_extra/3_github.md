---
id: ejercicios-github
title: "Ejercicios extra de GitHub"
nav_title: "GitHub"
summary: "Ejercicios nuevos con la forma del parcial de GitHub, cada uno con su respuesta explicada debajo: tres árboles de commits, siete errores reales de Git y un ritual con errores."
status: ready
estimated_time: 40m
tags: [ejercicios, git, github, ritual, branches, errores]
---

# Ejercicios extra de GitHub

**[PDF sin respuestas, para imprimir](../_assets/practica-github.pdf)** · unos 40 minutos · sin apuntes

Miden lo mismo que el parcial, con escenarios nuevos. Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado. Donde dice «con tus palabras», no escribas comandos. En `<login>` imagina el tuyo.

Casi todo sale de una idea: **un pull request muestra la diferencia entre tu rama y el punto donde se separó del `main` del curso**.

## Parte 1 · Lee el árbol

Los árboles se leen de izquierda a derecha: los commits viejos a la izquierda. Las letras son commits y los nombres de la derecha son ramas.

### Árbol 1 · Trabajó en main

Ana no creó rama: hizo sus commits M1 y M2 directamente en `main`, los subió a su fork y abrió el pull request desde `main`.

```text
o-o-o              upstream/main
     \
      M1---M2      main, origin/main
                   (pull request abierto desde main)
```

::: problem {#xg-1a title="Árbol 1a · ¿Qué muestra, y por qué sale en rojo?"}
¿Qué archivos muestra su pull request? Si todos están dentro de `estudiantes/ana/`, ¿por qué la revisión automática lo marca en rojo?
:::

::: hint {of="xg-1a"}
Además de los archivos, la revisión mira de qué rama sale el pull request.
:::

::: answer {of="xg-1a"}
**Respuesta:**

- **¿Qué archivos muestra?** **Los que cambian M1 y M2**, todos dentro de `estudiantes/ana/`.
- **¿Por qué sale en rojo?** **Porque el pull request sale de `main`**, la rama por defecto de su fork. La revisión automática rechaza cualquier pull request que salga de ahí, aunque los archivos estén bien.

**Por qué:**

1. El pull request compara el `main` de Ana contra el punto donde se separó de `upstream/main`: el último `o`.
2. Entre ese `o` y M2 sólo están M1 y M2. Eso es lo que muestra.
3. La revisión automática revisa, por separado, dónde están los archivos y de qué rama sale el pull request.
4. Los archivos pasan: están en `estudiantes/ana/`. La rama no pasa: es `main`.
5. La regla existe porque el `main` del fork tiene que ser una copia limpia del curso. De `main` nacen las ramas de todas las tareas; si `main` carga M1 y M2, cada tarea nueva los hereda.

**La regla:** **un pull request de entrega sale siempre de una rama de tarea (`tarea-NN-nombre`), nunca de `main`.**

**Error común:** «Si todos los archivos están en mi carpeta, pasa». No: la carpeta es una regla y la rama es otra, y las dos tienen que pasar.
:::

::: problem {#xg-1b title="Árbol 1b · ¿Cómo queda su main después de actualizar?"}
La semana siguiente el curso publica un commit P, y Ana hace el bloque A completo del ritual. ¿Cómo queda su `main`? ¿Sigue siendo una copia del curso?
:::

::: hint {of="xg-1b"}
Después de que el curso publica P, ¿están `main` y `upstream/main` en la misma línea, o ya se separaron?
:::

::: answer {of="xg-1b"}
**Respuesta:**

- **¿Cómo queda su `main`?** **Termina en un commit de merge nuevo, G**, que junta P (lo nuevo del curso) con M1 y M2 (lo de Ana). `origin/main` también queda en G, porque la última línea del bloque A sube G.
- **¿Sigue siendo una copia del curso?** **No.** Tiene M1, M2 y G, y el curso no tiene ninguno de los tres.

**Por qué:**

1. Antes del bloque A, `main` y `upstream/main` ya se separaron en el último `o` (el último commit del curso que Ana tenía): `main` tiene M1 y M2, y el curso tiene P.
2. `git fetch upstream` mueve `upstream/main` a P. No toca `main` ni los archivos.
3. `git merge upstream/main` no puede sólo avanzar `main` hasta P, porque dejaría fuera M1 y M2. Crea G, un commit con dos padres: M2 y P.
4. `git push origin main` sube G al fork.
5. Ahora `main` tiene todo lo del curso más M1, M2 y G. Una copia del curso tendría sólo lo del curso.

Antes del bloque A, con P ya publicado:

```text
o---o---o---P            upstream/main
         \
          M1---M2        main, origin/main
```

El bloque A, línea por línea («último `o`» es el último commit del curso que Ana tenía):

| Línea | HEAD | `main` | `origin/main` | `upstream/main` |
|---|---|---|---|---|
| Antes del bloque A | `main` | M2 | M2 | último `o` |
| `git switch main` | `main` | M2 | M2 | último `o` |
| `git fetch upstream` | `main` | M2 | M2 | **P** |
| `git merge upstream/main` | `main` | **G** | M2 | P |
| `git push origin main` | `main` | G | **G** | P |

Después:

```text
o---o---o-----------P        upstream/main
         \           \
          M1---M2-----G      main, origin/main
```

**La regla:** **el bloque A deja `main` igual al curso sólo si `main` no tiene commits propios. Si los tiene, el merge los conserva y agrega un commit de merge.**

**Compruébalo:**

- `git merge upstream/main` → `Merge made by the 'ort' strategy.` (hubo commit de merge).
- `git diff --stat upstream/main main` → lista los archivos de M1 y M2. En una copia limpia del curso no imprimiría nada.

**Error común:** «El bloque A deja `main` como el curso». No: `merge` junta las dos historias, no reemplaza una por otra.
:::

::: problem {#xg-1c title="Árbol 1c · ¿Qué arrastra la tarea siguiente?"}
Desde ese `main` crea la rama de la tarea siguiente. Si el primer pull request todavía no se ha mergeado, ¿qué arrastra el nuevo?
:::

::: hint {of="xg-1c"}
Una rama hereda todo lo del commit donde nace. ¿Qué tiene ese `main`?
:::

::: answer {of="xg-1c"}
**Respuesta:** **Arrastra M1, M2 y el commit de merge G**, además de los commits propios de la tarea nueva. Su pull request muestra los archivos de M1 y M2 junto con los de la tarea.

**Por qué:**

1. `git switch -c <rama-nueva>` crea la rama en el commit donde está `main`: G.
2. La historia de G incluye M1 y M2.
3. El pull request muestra todo lo que hay entre el punto donde la rama se separó del curso (P) y la punta de la rama.
4. El primer pull request no se ha mergeado, así que el curso no tiene M1, M2 ni G. Los tres aparecen.

Es el mismo problema del examen A del parcial, sólo que aquí la herencia viene de `main` y no de otra rama de tarea.

**La regla:** **una rama nace con toda la historia del commit donde la creas. Si `main` tiene commits que el curso no tiene, cada rama nueva los arrastra.**

**Compruébalo:** recién creada la rama, sin un solo commit propio todavía (`A..B` lista los commits que están en B y no en A):

```text
$ git log --oneline upstream/main..<rama-nueva>
3ca48f1 Merge remote-tracking branch 'upstream/main'
a347530 M2
94dca57 M1
```
:::

::: problem {#xg-1d title="Árbol 1d · ¿Cómo lo arreglas sin perder M1 y M2?"}
Con tus palabras.
:::

::: hint {of="xg-1d"}
Primero pon el trabajo a salvo en un lugar que no sea `main`, y después limpia `main`.
:::

::: answer {of="xg-1d"}
**Respuesta:** **Primero pon M1 y M2 a salvo en una rama de tarea y súbela al fork. Después regresa `main` al commit del curso (`upstream/main`) y reemplaza con él el `main` del fork.**

En comandos, partiendo del estado de b): `main` y `origin/main` en G, `upstream/main` en P. `tarea-NN-nombre` es el nombre de la tarea a la que pertenecen M1 y M2.

| Paso | HEAD | `main` | `tarea-NN-nombre` | `origin/main` | `upstream/main` |
|---|---|---|---|---|---|
| Antes | `main` | G | · | G | P |
| 1. `git switch -c tarea-NN-nombre` | **`tarea-NN-nombre`** | G | **G** | G | P |
| 2. `git push -u origin tarea-NN-nombre` | `tarea-NN-nombre` | G | G | G | P |
| 3. `git switch main` | **`main`** | G | G | G | P |
| 4. `git reset --hard upstream/main` | `main` | **P** | G | G | P |
| 5. `git push --force-with-lease origin main` | `main` | P | G | **P** | P |

Entre el paso 2 y el 3, en GitHub: abre el pull request desde `tarea-NN-nombre` y cierra el que salía de `main`. Eso no mueve ninguna rama.

Al final:

```text
o---o---o-----------P        main, origin/main, upstream/main
         \           \
          M1---M2-----G      tarea-NN-nombre
```

**Por qué:**

1. El paso 1 deja una rama, `tarea-NN-nombre`, apuntando a G. Desde ahí M1 y M2 ya no dependen de `main`.
2. El paso 2 copia esa rama al fork. Después del paso 2, M1 y M2 están en tu máquina y en GitHub.
3. El paso 4 mueve `main` a P: saca M1, M2 y G de `main`. `--hard` además pone en tu disco los archivos de P. Por eso va después de los pasos 1 y 2, nunca antes.
4. El paso 5 tiene que forzar. Un `git push origin main` normal se rechaza con `! [rejected] main -> main (non-fast-forward)`: el `main` del fork (G) tiene commits que tu `main` (P) ya no tiene.
5. El [[cheatsheet-git|cheatsheet]] dice «nunca `--force`» ante ese rechazo. Ésta es la única excepción: aquí quieres justo quitar G, M2 y M1 del `main` del fork, y no se pierden porque viven en `tarea-NN-nombre`.
6. `--force-with-lease` sobrescribe el `main` del fork sólo si sigue en G, lo último que tú viste de él. Si alguien lo movió, se niega con `! [rejected] main -> main (stale info)`.

**La regla:** **antes de quitar commits de una rama, deja otra rama apuntando a ellos y súbela; sólo entonces mueves la primera.**

**Compruébalo:** al final, `git ls-remote origin` lista `refs/heads/main` con el hash de P y `refs/heads/tarea-NN-nombre` con el hash de G.

**Error común:** correr `git pull` cuando un `git push origin main` normal se rechaza en el paso 5. Traería de vuelta G, M2 y M1 a tu `main` y desharía el paso 4.
:::

### Árbol 2 · Dos ramas hermanas

Beto actualizó `main` y desde ahí creó las dos ramas, una para cada tarea. El pull request de la 07 sigue abierto.

```text
       A---B       tarea-07-git (PR abierto)
      /
o-o-o              main = upstream/main
      \
       D---E       tarea-08-datacamp-intro
```

::: problem {#xg-2a title="Árbol 2a · ¿Qué muestra el pull request de la 08?"}
¿Qué archivos muestra el pull request de `tarea-08-datacamp-intro`?
:::

::: hint {of="xg-2a"}
¿Dónde se separó la 08 de `main`? Cuenta lo que hay entre ese punto y E.
:::

::: answer {of="xg-2a"}
**Respuesta:** **Los archivos que cambian D y E, y nada más.** A y B no aparecen.

**Por qué:**

1. `tarea-08-datacamp-intro` se separó de `main` en el último `o`.
2. Un pull request muestra lo que hay entre ese punto y la punta de la rama, E. Ahí sólo están D y E.
3. A y B están en `tarea-07-git`, otra rama que salió del mismo `o`. No están en el camino de ese `o` a E.

**La regla:** **un pull request muestra sólo los commits entre el punto donde la rama se separó de `main` y la punta de la rama.**

**Compruébalo:** `git diff --stat main...tarea-08-datacamp-intro` → lista sólo los archivos de D y E. Los tres puntos comparan contra el punto donde se separaron las ramas, igual que el pull request.
:::

::: problem {#xg-2b title="Árbol 2b · ¿Perdió la tarea 07?"}
Parado en `tarea-08-datacamp-intro`, Beto lista `estudiantes/beto/` y **no ve** `07_git/`. ¿Perdió su tarea 07? ¿Qué hizo `git switch` con esos archivos?
:::

::: hint {of="xg-2b"}
`git switch` cambia los archivos de tu disco por los de la rama a la que llegas.
:::

::: answer {of="xg-2b"}
**Respuesta:**

- **¿Perdió su tarea 07?** **No.** `07_git/` sigue guardada en los commits A y B de `tarea-07-git`, en su fork y en su pull request.
- **¿Qué hizo `git switch` con esos archivos?** **Los quitó del disco, porque puso ahí los archivos de la rama a la que llegó.** `tarea-08-datacamp-intro` nunca tuvo `07_git/`.

**Por qué:**

1. Cada rama apunta a un commit, y cada commit guarda el contenido completo de todos los archivos del repo en ese momento.
2. `git switch <rama>` cambia los archivos de tu disco por los del commit al que apunta esa rama.
3. El commit E, punta de `tarea-08-datacamp-intro`, tiene la carpeta de D y E y no tiene `07_git/`.
4. El commit B, punta de `tarea-07-git`, sí tiene `07_git/`.

| Comando | Rama donde quedas | `ls estudiantes/beto/` muestra |
|---|---|---|
| `git switch tarea-08-datacamp-intro` | `tarea-08-datacamp-intro` | la carpeta de D y E; **no** `07_git/` |
| `git switch tarea-07-git` | `tarea-07-git` | **`07_git/`** |

**La regla:** **tu disco muestra sólo la rama donde estás parado. Lo de otras ramas está guardado en sus commits, no borrado.**

**Compruébalo:** parado en `tarea-08-datacamp-intro`, `ls estudiantes/beto` no lista `07_git`; después de `git switch tarea-07-git`, sí la lista.
:::

::: problem {#xg-2c title="Árbol 2c · Si se mergea la 07, ¿cambia la 08?"}
Se mergea la tarea 07. ¿Cambia lo que muestra el pull request de la 08?
:::

::: hint {of="xg-2c"}
¿Cargaba la 08 algún commit de la 07?
:::

::: answer {of="xg-2c"}
**Respuesta:** **No.** El pull request de la 08 sigue mostrando D y E, y nada más.

**Por qué:**

1. `tarea-08-datacamp-intro` se separó de `main` en el último `o`.
2. Mergear la 07 agrega A, B y un commit de merge a `main`. El punto donde la 08 se separó sigue siendo el mismo `o`.
3. Entre ese `o` y E siguen estando sólo D y E.
4. La 08 nunca cargó A ni B, así que el merge de la 07 no le quita nada a su pull request.

**La regla:** **mergear una rama cambia el pull request de otra sólo si la otra cargaba commits de la primera.**

**Compruébalo:** después de mergear la 07 en `main`:

```text
$ git log --oneline main..tarea-08-datacamp-intro
8566467 E
29717f2 D
```
:::

::: problem {#xg-2d title="Árbol 2d · ¿Por qué en el examen A sí cambiaba?"}
En el examen A del parcial, la 08 nació de la 07. ¿Por qué allá mergear la 07 sí cambiaba el pull request y aquí no?
:::

::: hint {of="xg-2d"}
Compara dónde nació la 08 en cada caso.
:::

::: answer {of="xg-2d"}
**Respuesta:** **Por el lugar donde nació la 08.** En el examen A nació en C, la punta de `tarea-07-git`, así que cargaba A, B y C. Aquí nació en el último `o` de `main` y no carga nada de la 07.

**Por qué:**

1. En el examen A, el pull request de la 08 mostraba A, B, C y los commits propios de la 08: todos estaban entre `main` y la punta de la 08.
2. Al mergear la 07, A, B y C entraban a `main`, y el punto donde la 08 se separa de `main` pasaba a ser C.
3. Desde ese momento el pull request de la 08 mostraba sólo sus commits propios: A, B y C dejaban de aparecer.
4. Aquí la 08 nunca mostró A ni B, así que no hay nada que deje de aparecer.

| | Examen A | Árbol 2 |
|---|---|---|
| Dónde nace la 08 | En C, punta de `tarea-07-git` | En el último `o` de `main` |
| Pull request de la 08, antes de mergear la 07 | A, B, C, D, E | D, E |
| Pull request de la 08, después de mergear la 07 | **D, E** | D, E |

**La regla:** **mergear una rama cambia el pull request de otra sólo si la otra cargaba commits de la primera.**
:::

### Árbol 3 · Editó el archivo del curso

Carla no copió la plantilla a su carpeta: editó directo `codigo/docker/certificaciones.md` en su commit X. Mientras tanto el profesor cambió **esa misma línea** en el commit R.

```text
o---o---R          upstream/main
     \             (R cambia la línea 3)
      X            tarea-08-datacamp-intro
                   (X cambia la misma línea 3)
```

::: problem {#xg-3a title="Árbol 3a · ¿Qué dice la revisión automática?"}
¿Qué dice la revisión automática de su pull request, y por qué?
:::

::: hint {of="xg-3a"}
¿Qué regla de la revisión automática habla de la carpeta donde están los archivos?
:::

::: answer {of="xg-3a"}
**Respuesta:** **Rojo, porque el pull request toca `codigo/docker/certificaciones.md`, un archivo fuera de `estudiantes/carla/`.**

**Por qué:**

1. La primera regla de la revisión automática: cada archivo que toca el pull request tiene que estar en `estudiantes/<login del autor>/`.
2. X cambia `codigo/docker/certificaciones.md`, la plantilla que copia todo el grupo.
3. Si el pull request se mergeara, el cambio de Carla quedaría en la plantilla de todos.

**La regla:** **una entrega sólo toca archivos dentro de `estudiantes/<tu-login>/`. `codigo/` es del curso.**
:::

::: problem {#xg-3b title="Árbol 3b · ¿Merge limpio o conflicto?"}
Si alguien intentara mergearlo, ¿Git lo mezcla solo o hay conflicto? ¿Por qué?
:::

::: hint {of="xg-3b"}
¿Cuántos lados cambiaron la misma línea desde el ancestro común?
:::

::: answer {of="xg-3b"}
**Respuesta:** **Conflicto.** R y X cambiaron la misma línea 3 del mismo archivo, cada uno de forma distinta, y Git no puede decidir cuál texto se queda.

**Por qué:**

1. Para mezclar dos ramas, Git busca el ancestro común: el último commit que comparten. Aquí es el `o` donde se separaron, antes de R y de X.
2. Git compara cada lado contra ese ancestro, línea por línea.
3. Si sólo un lado cambió una línea, Git se queda con ese cambio sin preguntar.
4. Si los dos lados cambiaron la misma línea, Git no elige: marca conflicto y se detiene.

| Línea 3 de `codigo/docker/certificaciones.md` en… | Texto |
|---|---|
| El ancestro común | el original |
| R (el curso) | **cambiada** |
| X (Carla) | **cambiada, distinto que en R** |

**La regla:** **Git marca conflicto cuando los dos lados cambiaron las mismas líneas de un archivo desde el ancestro común. Si sólo un lado las cambió, mezcla solo.**

**Compruébalo:** lo que contesta `git merge`:

```text
Auto-merging codigo/docker/certificaciones.md
CONFLICT (content): Merge conflict in codigo/docker/certificaciones.md
Automatic merge failed; fix conflicts and then commit the result.
```
:::

::: problem {#xg-3c title="Árbol 3c · ¿Y si hubiera escrito en su copia?"}
Si hubiera escrito en `estudiantes/carla/docker/certificaciones.md`, ¿habría conflicto con R?
:::

::: hint {of="xg-3c"}
¿Es el mismo archivo, o son dos rutas distintas?
:::

::: answer {of="xg-3c"}
**Respuesta:** **No.** R cambiaría `codigo/docker/certificaciones.md` y X cambiaría otro archivo, `estudiantes/carla/docker/certificaciones.md`. Ningún archivo lo cambian los dos lados.

**Por qué:**

1. Git mezcla archivo por archivo, y un archivo es su ruta completa.
2. `codigo/docker/certificaciones.md` sólo lo cambia R: Git se queda con la versión de R.
3. `estudiantes/carla/docker/certificaciones.md` sólo lo crea X: Git se queda con la versión de X.
4. Que los dos archivos se llamen igual y tengan casi el mismo texto no importa: están en rutas distintas.

**La regla:** **si cada lado cambia un archivo distinto, no hay conflicto.**

**Compruébalo:** el merge termina solo, con `Merge made by the 'ort' strategy.`
:::

::: problem {#xg-3d title="Árbol 3d · ¿Qué regla lo evita?"}
¿Qué regla del curso evita esto, y por qué funciona aunque treinta personas entreguen la misma tarea?
:::

::: hint {of="xg-3d"}
Es la regla que dice dónde copias la plantilla y dónde trabajas.
:::

::: answer {of="xg-3d"}
**Respuesta:**

- **¿Qué regla?** **La regla del espejo**: copiar la plantilla de `codigo/` a `estudiantes/<login>/` con la misma ruta, y trabajar sólo en esa copia.
- **¿Por qué funciona con treinta?** **Porque cada quien escribe en una carpeta que nadie más toca, y nadie escribe en `codigo/`.** Treinta pull requests no comparten ni un archivo entre sí ni con las correcciones del curso, así que ninguno puede chocar.

**Por qué:**

1. Un conflicto sólo aparece cuando dos lados cambian las mismas líneas del mismo archivo.
2. Con el espejo, Ana escribe en `estudiantes/ana/…` y Beto en `estudiantes/beto/…`: rutas distintas.
3. Las correcciones del profesor van a `codigo/…`, donde ningún alumno escribe.
4. Ningún archivo lo tocan dos personas, sean tres o treinta. Por eso no hay conflicto posible.
:::

**Repasa:** [[branches-y-merge]], [[branches-en-serio]], [[el-flujo-del-curso]] y [[deshacer-en-git]].

## Parte 2 · Lee el error

Cada caso trae lo que la persona corrió y lo que Git contestó, tal cual. Escribe **qué pasó** y **cuál es el siguiente paso**.

::: problem {#xg-e1 title="Error 1 · Primer push de una rama nueva"}
```text
$ git push
fatal: The current branch tarea-09-uv-docker has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin tarea-09-uv-docker
```
:::

::: hint {of="xg-e1"}
«no upstream branch»: la rama nunca se ha subido. Git te sugiere el comando en el mismo mensaje.
:::

::: answer {of="xg-e1"}
**Respuesta:**

- **Qué pasó:** **la rama `tarea-09-uv-docker` existe en su máquina pero nunca se ha subido.** Un `git push` a secas no sabe a qué remoto ni a qué rama mandarla, y no sube nada.
- **Qué hacer:** **`git push -u origin tarea-09-uv-docker`**. Es el comando que sugiere el propio mensaje: `-u` es la forma corta de `--set-upstream`. De ahí en adelante, en esa rama basta `git push`.

**Por qué:**

1. Una rama creada con `git switch -c` sólo existe en tu máquina.
2. `git push` sin argumentos sube a la rama remota emparejada con la tuya (su *upstream*).
3. Esta rama todavía no tiene pareja. Git no adivina el destino, para no subirla a un lugar que no elegiste: se detiene.
4. `-u` sube la rama a `origin` y guarda la pareja: `tarea-09-uv-docker` con `origin/tarea-09-uv-docker`.

**La regla:** **el primer push de cada rama nueva es `git push -u origin <rama>`; los siguientes, `git push`.**

**Compruébalo:** `git push -u origin tarea-09-uv-docker` termina con `Branch 'tarea-09-uv-docker' set up to track remote branch 'tarea-09-uv-docker' from 'origin'.`
:::

::: problem {#xg-e2 title="Error 2 · Editó el README desde la página de GitHub"}
El día anterior editó el README de su fork **desde la página de GitHub**. Hoy, en su máquina:

```text
$ git push origin main
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:ana/fdd_o26_ana.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally.
```
:::

::: hint {of="xg-e2"}
«the remote contains work that you do not have locally»: ¿qué commit tiene el fork que tu máquina no?
:::

::: answer {of="xg-e2"}
**Respuesta:**

- **Qué pasó:** **el `main` de su fork tiene un commit que su máquina no tiene: la edición del README que hizo en la página de GitHub.** Git rechaza el push para no borrarlo.
- **Qué hacer:** traer ese commit, mezclarlo con su `main` y volver a subir:

```bash
git fetch origin
git merge origin/main
git push origin main
```

`git pull origin main` hace lo mismo que las dos primeras líneas de un jalón, porque el curso configuró `pull.rebase false` en [[clonar-y-actualizar]]. Si el merge da conflicto (los dos lados cambiaron las mismas líneas del README), lo resuelve, hace `git add` y `git commit`, y luego el `git push`.

**Por qué:**

1. Un push sólo puede **avanzar** la rama del fork: el commit que subes tiene que contener en su historia al que ya está ahí.
2. El commit de la web no está en la historia de su `main` local. Si Git aceptara el push, el `main` del fork pasaría al commit de Ana y el de la web quedaría fuera.
3. Git se niega para proteger ese commit. `fetch first` dice qué falta: traerlo primero.
4. `git fetch origin` baja el commit de la web a `origin/main` sin tocar sus archivos.
5. `git merge origin/main` lo mete en su `main`. Ahora su `main` contiene el commit de la web.
6. `git push origin main` ya avanza la rama del fork, y entra.

Es el bloque A del ritual, con `origin` en lugar de `upstream`.

**Ojo:** después del fetch y el merge, su `main` ya no es copia del curso: tiene el commit del README. Cada rama nueva lo arrastraría, y su pull request tocaría `README.md`, fuera de `estudiantes/<login>/`, y saldría en rojo por ubicación. Hay que limpiar `main` antes de la próxima rama (como en el árbol 1d), o mejor: no editar el fork desde la web.

**La regla:** **si el push se rechaza porque el remoto tiene algo que tú no, primero lo traes y lo mezclas, y después subes. Nunca `--force`.**

**Compruébalo:** después del `git merge origin/main`, `git push origin main` contesta con una línea `<hash>..<hash>  main -> main`, sin `rejected`.

**Error común:** `git push --force origin main`. Sube, pero borra del fork el commit de la web.
:::

::: problem {#xg-e3 title="Error 3 · Permiso denegado"}
Clonó el repositorio del curso y dejó para después la conexión con su fork.

```text
$ git push -u origin tarea-08-imagen
ERROR: Permission to raya-lucaria/fdd_o26.git denied to ana.
fatal: Could not read from remote repository.
```
:::

::: hint {of="xg-e3"}
¿A quién le intentaste subir? Lee el nombre del repositorio en el error.
:::

::: answer {of="xg-e3"}
**Respuesta:**

- **Qué pasó:** **`origin` apunta al repositorio del curso, `raya-lucaria/fdd_o26`, donde nadie del grupo puede escribir.** Lo dice el error: `Permission to raya-lucaria/fdd_o26.git denied to ana`.
- **Qué hacer:** terminar de conectar su fork y repetir el push:

```bash
git remote -v                       # confirma: origin es raya-lucaria/fdd_o26
git remote rename origin upstream   # el curso pasa a llamarse upstream
git remote add origin \
  git@github.com:$GHUSER/fdd_o26_$GHUSER.git
git remote -v                       # 4 líneas: origin es su fork, upstream el curso
git push -u origin tarea-08-imagen
```

**Por qué:**

1. `git clone` llama `origin` al repositorio que clonaste. Aquí clonó el del curso.
2. GitHub sólo acepta un push de quien tiene permiso de escritura en ese repositorio. En el del curso, sólo los profesores.
3. GitHub rechaza el push y protege el repositorio del curso: nadie del grupo puede subirle ramas.
4. Después de `rename` y `add`, `origin` es su fork, donde sí puede escribir, y `upstream` es el curso, de donde sólo baja.

**La regla:** **`origin` es tu fork (ahí subes) y `upstream` es el curso (de ahí bajas). `git remote -v` te dice a dónde apunta cada uno.**
:::

::: problem {#xg-e4 title="Error 4 · Cambiar de rama con trabajo sin guardar"}
Editó `notas.md` en la rama de la tarea, no hizo commit, y quiere volver a `main`.

```text
$ git switch main
error: Your local changes to the following files would be overwritten by checkout:
	estudiantes/ana/09_python/notas.md
Please commit your changes or stash them before you switch branches.
Aborting
```
:::

::: hint {of="xg-e4"}
Git se niega para no perder tu trabajo. ¿Cuáles son las dos formas de guardarlo antes de cambiar de rama?
:::

::: answer {of="xg-e4"}
**Respuesta:**

- **Qué pasó:** **`notas.md` tiene una edición sin commit, y en `main` ese archivo es distinto.** Cambiar de rama pondría en el disco la versión de `main` encima de la edición. Git se niega (`Aborting`): no cambió de rama ni tocó ningún archivo.
- **Qué hacer**, una de dos:
    - Si la edición ya está lista: `git add estudiantes/ana/09_python/notas.md`, luego `git commit -m "<mensaje>"`, y luego `git switch main`.
    - Si todavía no está lista: `git stash` y luego `git switch main`. Al volver: `git switch <rama-de-la-tarea>` y luego `git stash pop`.

**Por qué:**

1. `git switch` reescribe en el disco los archivos que son distintos entre las dos ramas.
2. `notas.md` es distinto, y la edición de Ana no está en ningún commit. Si Git reescribiera el archivo, la edición se perdería sin copia.
3. Git protege ese trabajo sin guardar: aborta antes de tocar nada.
4. `git commit` guarda la edición en la rama de la tarea. `git stash` la guarda aparte, en el stash (una pila de cambios guardados fuera de las ramas), y deja el disco igual al último commit.

**La regla:** **Git no te deja cambiar de rama si eso borraría trabajo sin commit. Guárdalo con `git commit` o apártalo con `git stash`.**

El camino con `stash`, paso por paso. `notas.md` tiene dos versiones en la rama de la tarea: **la guardada** (la del último commit) y **la editada** (la guardada más la edición sin commit). El Index es el staging area.

| Paso | Rama actual | `notas.md` en el disco | En el Index | En el último commit | Stash |
|---|---|---|---|---|---|
| Antes: `git switch main` falla | la de la tarea | **la editada** | la guardada | la guardada | vacío |
| `git stash` | la de la tarea | **la guardada** | la guardada | la guardada | **la edición** |
| `git switch main` | **`main`** | **la de `main`** | la de `main` | la de `main` | la edición |
| `git switch <rama-de-la-tarea>` | **la de la tarea** | **la guardada** | la guardada | la guardada | la edición |
| `git stash pop` | la de la tarea | **la editada** | la guardada | la guardada | **vacío** |

**Compruébalo:** `git stash` → `Saved working directory and index state WIP on <rama>: …`. `git stash pop` imprime el estado, con `modified: estudiantes/ana/09_python/notas.md`, y termina con `Dropped refs/stash@{0}`.

**Error común:** creer que Git siempre se niega a cambiar de rama con trabajo sin commit. Si `notas.md` fuera idéntico en las dos ramas, `git switch main` no fallaría: se llevaría la edición a `main` y avisaría con `M …/notas.md`.
:::

::: problem {#xg-e5 title="Error 5 · El .venv no aparece"}
Corrió `uv sync`, que creó `estudiantes/ana/09_python/uv_docker/.venv/` con cientos de archivos. Luego `git status --short` no muestra nada. ¿Se perdió el ambiente? ¿Es un problema?
:::

::: hint {of="xg-e5"}
¿Qué archivo del curso le dice a Git qué rutas no mirar?
:::

::: answer {of="xg-e5"}
**Respuesta:**

- **¿Se perdió el ambiente?** **No.** La carpeta `.venv/` sigue en el disco con todos sus archivos.
- **¿Es un problema?** **No: así debe ser.** El `.gitignore` del curso tiene la línea `.venv`, y Git no muestra lo que ese archivo le dice ignorar.

**Por qué:**

1. `.gitignore` es un archivo con patrones de rutas que Git no debe mirar.
2. El del curso incluye `.venv`, así que cualquier carpeta llamada `.venv` queda fuera de `git status`, de `git add` y de los commits.
3. Git no la borra: sólo deja de mostrarla.
4. `.venv/` no se sube porque cualquiera la recrea con `uv sync` a partir de `pyproject.toml` y `uv.lock`, que sí se suben.

**La regla:** **lo que se puede regenerar no se sube: se sube la receta (`pyproject.toml`, `uv.lock`), no el resultado (`.venv/`).**

**Compruébalo:** `git status --short --ignored` muestra también lo ignorado, marcado con `!!`:

```text
!! estudiantes/ana/09_python/uv_docker/.venv/
```
:::

::: problem {#xg-e6 title="Error 6 · Un .DS_Store apartado"}
Quiere sacar `.DS_Store` de lo que va a guardar **sin borrarlo** de su disco.

```text
$ git status
On branch tarea-09-uv-docker
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   estudiantes/ana/09_python/.DS_Store
	new file:   estudiantes/ana/09_python/uv_docker/pyproject.toml
```
:::

::: hint {of="xg-e6"}
El propio `git status` dice el comando entre paréntesis.
:::

::: answer {of="xg-e6"}
**Respuesta:**

- **Qué pasó:** **`git add` apartó `.DS_Store` junto con `pyproject.toml`**: los dos están en el Index (el staging area) y entrarían en el próximo commit.
- **Qué hacer:** **`git restore --staged estudiantes/ana/09_python/.DS_Store`**. Lo saca del Index y lo deja en el disco. `pyproject.toml` sigue apartado.

**Por qué:**

1. «Changes to be committed» lista lo que está en el Index: lo que entraría en el próximo commit.
2. `git restore --staged <ruta>` regresa esa ruta del Index a como está en el último commit. `.DS_Store` no estaba en ningún commit, así que sale del Index.
3. `--staged` sólo toca el Index. El archivo sigue en el disco.
4. `.DS_Store` es un archivo que macOS crea en cada carpeta que abres en Finder. No es parte de la entrega.
5. El `.gitignore` del curso ya lista `.DS_Store`: con esa línea, `git add estudiantes/ana/09_python` no lo aparta. Si quedó apartado, su copia no tenía esa línea (un `main` sin actualizar) o lo agregó con `git add -f`.

| Paso | Disco | Index (apartado, nuevo) | Último commit |
|---|---|---|---|
| Antes | `.DS_Store`, `pyproject.toml` | `.DS_Store`, `pyproject.toml` | ninguno de los dos |
| `git restore --staged …/.DS_Store` | `.DS_Store`, `pyproject.toml` | **sólo `pyproject.toml`** | ninguno de los dos |

**La regla:** **para sacar algo del Index sin borrarlo del disco: `git restore --staged <ruta>`.**

**Compruébalo:** antes, `git status --short` muestra dos líneas con `A` (`.DS_Store` y `pyproject.toml`); después, sólo la de `pyproject.toml`, y `ls -a estudiantes/ana/09_python` sigue listando `.DS_Store`. `git rm --cached` con la misma ruta hace lo mismo en este caso.
:::

::: problem {#xg-e7 title="Error 7 · Un commit que salió mal, sin push"}
Hizo commit y se dio cuenta de que le faltó un archivo y de que el mensaje está mal. **Todavía no hace push.** Quiere deshacer el commit pero conservar los cambios.
:::

::: hint {of="xg-e7"}
Necesitas deshacer el commit pero conservar los cambios apartados. En [[deshacer-en-git|Deshacer]] hay un `reset` que hace justo eso.
:::

::: answer {of="xg-e7"}
**Respuesta:**

- **Qué pasó:** **el último commit tiene un mensaje malo y le falta un archivo.** Todavía no hay push: ese commit sólo existe en su máquina.
- **Qué hacer:** **`git reset --soft HEAD~1`**, que deshace el commit y deja sus cambios apartados en el Index. Después: `git add <lo que faltaba>` y `git commit -m "<mensaje correcto>"`.

**Por qué:**

1. `HEAD~1` es el commit anterior al último.
2. `git reset` mueve la rama actual a ese commit: el commit malo deja de ser parte de la rama.
3. `--soft` no toca ni el Index ni el disco. Los cambios del commit malo quedan apartados, listos para el commit siguiente.
4. Se vale reescribir porque el commit sólo existe en su máquina: todavía no hace push.

C es el commit malo:

| Paso | Disco | Index | Último commit |
|---|---|---|---|
| Después del commit malo | lo editado | igual al commit | **C**: mensaje malo, le falta un archivo |
| `git reset --soft HEAD~1` | igual | igual: lo de C sigue apartado | **el anterior a C** |
| `git add <lo que faltaba>` | igual | **lo de C + lo que faltaba** | el anterior a C |
| `git commit -m "<mensaje correcto>"` | igual | igual al commit | **commit nuevo, completo** |

**La regla:** **antes del push, `git reset --soft HEAD~1` y rehaces el commit. Después del push, corriges con un commit nuevo**, porque reescribir un commit ya subido obliga a forzar el push y borra historia en tu fork.

**Compruébalo:** `git reset --soft HEAD~1` no imprime nada. Después, `git status --short` muestra los archivos de C con la letra en la primera columna (`A` o `M`): siguen apartados.

**Error común:** `git reset --hard HEAD~1`. También deshace el commit, pero borra sus cambios del Index y del disco.
:::

**Repasa:** [[deshacer-en-git]], [[lo-que-no-se-sube]] y la tabla de errores de [[cheatsheet-git]].

## Parte 3 · Encuentra los errores

Dani escribió este ritual para entregar `tarea-09-uv-docker`, cuya carpeta es `09_python/`. Lo corrió completo y **ningún comando falló**, pero la entrega salió mal. Ya tenía conectado su fork.

```text
 1   git switch -c tarea-09-uv-docker
 2   git switch main
 3   git fetch upstream
 4   git merge upstream/main
 5   git push origin main
 6   mkdir -p estudiantes/$GHUSER/09_python
 7   cp -r codigo/09_python estudiantes/$GHUSER/09_python/
 8   git status
 9   git add .
10   git commit -m "tarea 9"
11   git push -u origin main
```

::: problem {#xg-r1 title="a · Los cinco problemas"}
Hay **cinco** problemas: cuatro líneas mal y una que falta. Para cada uno, di la línea, qué se rompe y por qué.
:::

::: hint {of="xg-r1"}
Revisa cada línea contra el ritual del curso: el orden, el `cp`, el `add` y el `push`. Uno de los cinco es una línea que falta.
:::

::: answer {of="xg-r1"}
**Respuesta:** las líneas **1, 7, 9 y 11** están mal, y **falta un `git status` entre la 9 y la 10**.

- **Línea 1 · `git switch -c tarea-09-uv-docker`, antes de tiempo.** Qué se rompe: la rama nace del `main` viejo, sin lo último del curso, y nunca se usa: la línea 2 regresa a `main`, y el `add`, el commit y el push de las líneas 9 a 11 pasan en `main`. Por qué: `git switch -c` crea la rama donde estás parado en ese momento, y `git switch main` te saca de ella. Va después de la línea 5.
- **Línea 7 · `cp -r codigo/09_python estudiantes/$GHUSER/09_python/`.** Qué se rompe: los archivos quedan en `estudiantes/$GHUSER/09_python/09_python/`, y además llegan `por_dentro/` y `stack/`, que son de otras entregas. Por qué: `cp -r` sin `/.` copia la carpeta `09_python` misma, y como el destino ya existe (lo creó la línea 6) la mete adentro. `/.` arreglaría el `09_python/09_python`, pero seguiría trayendo `por_dentro/` y `stack/`; por eso aquí se copia por nombre, como en la página de entregas de 9.1. Lo correcto copia las dos carpetas de esta entrega por nombre: `cp -r codigo/09_python/ambientes codigo/09_python/uv_docker estudiantes/$GHUSER/09_python/`.
- **Línea 9 · `git add .`.** Qué se rompe: aparta todo lo que cambió en el repo, no sólo la entrega, incluida la carpeta duplicada y cualquier archivo que el `.gitignore` no excluya. Por qué: `.` es la carpeta donde estás, aquí la raíz del repo completo. Lo correcto aparta por ruta: `git add estudiantes/$GHUSER/09_python/ambientes estudiantes/$GHUSER/09_python/uv_docker`.
- **Falta un `git status` entre la 9 y la 10.** Qué se rompe: Dani hace el commit sin ver qué apartó, así que no ve la ruta duplicada `09_python/09_python/` ni las carpetas de otras entregas. Por qué: el segundo `git status` del ritual es la última revisión de lo apartado antes de guardarlo.
- **Línea 11 · `git push -u origin main`.** Qué se rompe: sube `main` con la entrega adentro, y el pull request saldría de `main`, que la revisión automática marca en rojo. Por qué: `git push` sube la rama que nombras. Lo correcto, ya con la línea 1 en su lugar: `git push -u origin tarea-09-uv-docker`.

**La regla:** **la rama nace después de actualizar `main`, y todo lo demás se nombra: la carpeta que copias, la ruta que apartas y la rama que subes.**
:::

::: problem {#xg-r2 title="b · ¿En qué rama quedaron los commits?"}
Después de correr todo, ¿en qué rama quedaron sus commits? ¿Qué rama subió a su fork?
:::

::: hint {of="xg-r2"}
Sigue con el dedo en qué rama estás después de cada `git switch`.
:::

::: answer {of="xg-r2"}
**Respuesta:**

- **¿En qué rama quedaron sus commits?** **En `main`.**
- **¿Qué rama subió a su fork?** **`main`, con la entrega adentro.** `tarea-09-uv-docker` se quedó en el commit donde nació, sin la entrega, y nunca se subió.

**Por qué:**

1. La línea 1 crea `tarea-09-uv-docker` y la deja como rama actual.
2. La línea 2 cambia a `main`. Ninguna línea posterior regresa a la rama de la tarea.
3. Un commit se guarda en la rama actual: el de la línea 10 va a `main`.
4. La línea 11 nombra `main`, y eso es lo que sube.

Supuestos de la tabla: Dani empieza en `main`, y su `main`, el de su fork y `upstream/main` están en el mismo commit, `o`. El curso ya publicó un commit P que Dani todavía no baja. T es el commit de la línea 10. `·` = la rama no existe.

| Línea | HEAD | `main` | `tarea-09-uv-docker` | `origin/main` | `upstream/main` |
|---|---|---|---|---|---|
| Antes | `main` | o | · | o | o |
| 1. `git switch -c tarea-09-uv-docker` | **`tarea-09-uv-docker`** | o | **o** | o | o |
| 2. `git switch main` | **`main`** | o | o | o | o |
| 3. `git fetch upstream` | `main` | o | o | o | **P** |
| 4. `git merge upstream/main` | `main` | **P** | o | o | P |
| 5. `git push origin main` | `main` | P | o | **P** | P |
| 6. `mkdir -p …` (no mueve ramas) | `main` | P | o | P | P |
| 7. `cp -r …` (no mueve ramas) | `main` | P | o | P | P |
| 8. `git status` (no mueve ramas) | `main` | P | o | P | P |
| 9. `git add .` (no mueve ramas) | `main` | P | o | P | P |
| 10. `git commit -m "tarea 9"` | `main` | **T** | o | P | P |
| 11. `git push -u origin main` | `main` | T | o | **T** | P |

Al final:

```text
o---P---T
```

| Commit | Ramas que apuntan ahí |
|---|---|
| o | `tarea-09-uv-docker` (sólo en su máquina) |
| P | `upstream/main` |
| T | `main`, `origin/main` |

Si el curso no hubiera publicado P, las líneas 3 a 5 no moverían nada, T quedaría justo después de `o`, y la conclusión sería la misma. Es el árbol 1 de esta misma página: trabajo hecho y subido desde `main`.

**La regla:** **un commit va a la rama donde estás parado. Antes de `git commit`, la primera línea de `git status` (`On branch …`) te dice cuál es.**

**Compruébalo:**

- `git ls-remote origin` no lista `refs/heads/tarea-09-uv-docker`: el fork sólo tiene `refs/heads/main` (más `HEAD`).
- `git log --oneline upstream/main..tarea-09-uv-docker` → no imprime nada: la rama de la tarea no tiene ni un commit que el curso no tenga.
:::

::: problem {#xg-r3 title="c · ¿Dónde quedó hola.py?"}
Escribe la ruta donde quedó `hola.py`, que en el curso está en `codigo/09_python/ambientes/hola.py`.
:::

::: hint {of="xg-r3"}
¿Qué hace `cp -r` sin `/.` cuando la carpeta destino ya existe?
:::

::: answer {of="xg-r3"}
**Respuesta:** **`estudiantes/<login>/09_python/09_python/ambientes/hola.py`**, con un `09_python` de más.

**Por qué:**

1. La línea 6 crea la carpeta vacía `estudiantes/<login>/09_python/`.
2. La línea 7 es `cp -r codigo/09_python estudiantes/<login>/09_python/`. Sin `/.` al final del origen, `cp -r` copia la carpeta `09_python` misma, no sólo su contenido.
3. Como el destino ya existe, `cp` pone la copia dentro de él: `estudiantes/<login>/09_python/09_python/`.
4. `hola.py` estaba en `codigo/09_python/ambientes/hola.py`, así que queda en `estudiantes/<login>/09_python/09_python/ambientes/hola.py`.
5. Ya no es espejo del curso. Aunque Dani subiera la rama correcta, la revisión de contenido de `tarea-09-uv-docker` buscaría `estudiantes/<login>/09_python/uv_docker/…` y no lo encontraría.

**La regla:** **`cp -r X Y/` con `Y/` ya creada deja la copia en `Y/X/`. `cp -r X/. Y/` deja el contenido de `X` directo en `Y/`.**

**Compruébalo:** con `GHUSER=dani`:

```text
$ find estudiantes -name hola.py
estudiantes/dani/09_python/09_python/ambientes/hola.py
```

**Error común:** contestar `estudiantes/<login>/09_python/ambientes/hola.py`. Ésa sería la ruta sólo si `estudiantes/<login>/09_python/` no existiera antes del `cp`, y la línea 6 la creó.
:::

::: problem {#xg-r4 title="d · El ritual corregido"}
Escribe el ritual corregido, completo y en orden.
:::

::: hint {of="xg-r4"}
Es el ritual del curso con `tarea-09-uv-docker` y `09_python`. Empieza por `main`.
:::

::: answer {of="xg-r4"}
**Respuesta:**

```bash
git switch main
git fetch upstream
git merge upstream/main
git push origin main
git switch -c tarea-09-uv-docker
mkdir -p estudiantes/$GHUSER/09_python
cp -r codigo/09_python/ambientes codigo/09_python/uv_docker estudiantes/$GHUSER/09_python/
git status
git add estudiantes/$GHUSER/09_python/ambientes estudiantes/$GHUSER/09_python/uv_docker
git status
git commit -m "unidad 09: labs de ambientes y mi ambiente uv en Docker"
git push -u origin tarea-09-uv-docker
```

Y al final, el pull request en el navegador: base `raya-lucaria/fdd_o26` · `main`, compare `tarea-09-uv-docker`.

**Por qué:**

1. Las cuatro primeras líneas son el bloque A: dejan `main` igual al curso, en tu máquina y en tu fork.
2. `git switch -c tarea-09-uv-docker` va después del bloque A, así que la rama nace del `main` ya actualizado. Desde aquí todo pasa en esa rama.
3. `mkdir -p` y `cp -r` copian por nombre las dos carpetas de esta entrega, `ambientes/` y `uv_docker/`, a `estudiantes/$GHUSER/09_python/`.
4. `git status`, `git add` por ruta y otra vez `git status`: ves qué cambió, apartas sólo la entrega y confirmas que no se coló nada más.
5. El commit queda en `tarea-09-uv-docker`, y `git push -u origin tarea-09-uv-docker` sube esa rama por primera vez.

**La regla:** **bloque A primero; después rama, copia, `status`-`add`-`status`, commit y push de la rama.**

**Compruébalo:** con este ritual, `find estudiantes -name hola.py` → `estudiantes/dani/09_python/ambientes/hola.py`, y el fork tiene `main` y `tarea-09-uv-docker`.
:::

**Repasa:** [[el-ritual-del-curso]].
