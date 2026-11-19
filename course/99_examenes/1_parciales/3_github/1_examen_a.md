---
id: parcial-github-a
title: "Parcial 3 · GitHub · Examen A"
nav_title: "Examen A"
summary: "El examen A de GitHub, pregunta por pregunta, con la respuesta explicada debajo de cada una: la rama que nació de otra rama, y el ritual del curso en orden."
status: ready
estimated_time: 30m
tags: [examen, parcial, git, github, ritual, branches]
---

# Parcial 3 · GitHub · Examen A

**[PDF del examen A, sin respuestas](../../_assets/parcial-github-a.pdf)** · 30 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte.

## Pregunta 1 · Lee el árbol (3 puntos)

Un compañero terminó la tarea 07 y abrió su pull request. **Ese pull request sigue abierto: nadie se lo ha mergeado todavía.** Sin moverse de `tarea-07-git`, creó desde ahí la rama de la tarea 08 y trabajó en ella. Contesta con tus palabras, sin comandos.

```text
              D---E   tarea-08-datacamp-intro
             /
     A---B---C        tarea-07-git (PR abierto)
    /
o-o-o                 main = upstream/main
```

::: problem {#pga-1a title="1a · ¿Qué archivos lista el pull request de la 08? (0.75)"}
¿Qué archivos va a listar el pull request de `tarea-08-datacamp-intro`? Describe qué aparece y por qué aparece.
:::

::: answer {of="pga-1a"}
**Respuesta.** Los **cinco** commits, A, B, C, D y E, y por lo tanto las **dos** carpetas: `estudiantes/<login>/07_git/…` y `estudiantes/<login>/docker/…`.

**Por qué.** Un pull request muestra la diferencia entre tu rama y el punto donde se separó de `main`, y ese punto es el último `o`. Todo lo que hay entre ese `o` y E entra, incluidos A, B y C. No aparecen porque los haya vuelto a tocar: la rama los **hereda** del commit donde nació.

**También valía.** Contestar en commits en vez de carpetas, si dice de dónde salen. Listar las dos carpetas sin explicar la herencia valía la mitad. «Sólo lo de la tarea 08» valía cero.
:::

::: problem {#pga-1b title="1b · Una cosa bien y una mal (0.75)"}
Di **una cosa que hizo bien** y **una que hizo mal**. La que hizo mal, explícala en términos de **dónde nació la rama**.
:::

::: answer {of="pga-1b"}
**Bien**, cualquiera de éstas:

- trabajó en una rama y no en `main`;
- puso cada tarea en su carpeta del espejo;
- el nombre de la rama tiene la forma `tarea-NN-nombre`.

**Mal:** la rama de la 08 nació de `tarea-07-git` y no de `main`.

**Por qué.** Una rama arranca con **todo** el estado del commit donde nace. Si nace en C, su punto de partida ya trae A, B y C. Lo que una rama carga no depende de lo que tocaste después, sino de dónde nació. Por eso la revisión automática la rechaza con la regla de «una sola carpeta».

**También valía.** Si el «mal» no hablaba de dónde nació la rama («subió archivos de más»), valía la mitad.
:::

::: problem {#pga-1c title="1c · ¿Cómo se evita? (0.75)"}
¿Cómo se evita? Explica por qué eso lo resuelve.
:::

::: answer {of="pga-1c"}
**Respuesta.** Volviendo a un `main` **al día** (el bloque A completo del ritual) antes de crear la rama de cada tarea. Las ramas de las tareas son hermanas que cuelgan de `main`, nunca una encadenada a otra.

**Por qué lo resuelve.** Si la rama nace en la punta de `main`, entre ese punto y la rama sólo queda lo que escribiste para la 08, y eso es lo único que lista el pull request.

**También valía.** Para arreglarlo hoy: crear otra vez la rama desde `main` y llevar ahí sólo el trabajo de la 08. Decir «que nazca de `main`» sin explicar por qué eso cambia lo que muestra el pull request valía la mitad.
:::

::: problem {#pga-1d title="1d · Si le mergean la 07 antes, ¿cambia? (0.75)"}
Si le mergean la tarea 07 **antes** de que abra el segundo pull request, ¿cambia lo que ese pull request contiene? Justifica.
:::

::: answer {of="pga-1d"}
**Respuesta.** **Sí.** Ahora lista sólo D y E: sólo la tarea 08.

**Por qué.** Al mergear la 07, A, B y C pasan a estar en `upstream/main`, y el punto donde las dos historias se separan se vuelve C. La rama de la 08 no cambió ni un bit; lo que se movió es **la base** contra la que se compara.

**Matiz.** Esto funciona porque el curso mergea con commit de merge, que conserva A, B y C con sus hashes. Con *Squash and merge* llegaría a `main` un commit nuevo con otro hash, la base no se movería y el pull request seguiría mostrando todo.

**También valía.** «Sí» sin explicar que se movió la base valía la mitad. «No» valía cero.
:::

**Repasa:** [[branches-y-merge]], [[branches-en-serio]] y [[trabajo-en-paralelo]].

## Pregunta 2 · El ritual, en orden (7 puntos)

Los ocho pasos están **desordenados**. Uno ocurre una sola vez en el semestre; los otros siete, en cada entrega. Usa la rama `tarea-08-imagen` y su carpeta `08_contenedores/` como ejemplo. Para cada paso escribe:

- **Orden**: el número que le toca (1 a 8);
- **Qué hace y por qué**: qué logra y qué se rompe si falta;
- **Comandos**: los comandos exactos, en orden. Si no hay comando, dilo.

Los pasos, tal como venían impresos:

1. Crear tu carpeta de la unidad y copiar ahí el material del curso.
2. Proponerle tu trabajo al curso desde el navegador.
3. Traerte lo que el curso publicó, sin tocar todavía tus archivos.
4. Conectar tu copia con el repositorio del curso. (Una sola vez en el semestre.)
5. Revisar qué cambió y apartar sólo lo tuyo, por ruta.
6. Guardar lo apartado y subir tu rama a tu fork.
7. Incorporar eso a tu main y dejar tu fork al día.
8. Crear la rama de esta tarea y moverte a ella.

::: problem {#pga-2 title="2 · El ritual (7 puntos: orden 2, explicación 2, comandos 3)"}
Escribe el orden, qué hace cada paso y sus comandos.
:::

::: answer {of="pga-2"}
**Orden de los renglones impresos:** 5 · 8 · 2 · 1 · 6 · 7 · 3 · 4. Es decir, el primer renglón («Crear tu carpeta») es el paso 5, el segundo es el 8, y así.

Ya en orden:

**1 · Conectar tu copia con el curso (una vez).** `upstream` es de donde **bajas** (el curso) y `origin` es a donde **subes** (tu fork). Sin esto no hay de dónde ponerte al día ni a dónde subir.

```bash
# en el navegador: fork de github.com/raya-lucaria/fdd_o26
git remote rename origin upstream
git remote add origin git@github.com:$GHUSER/fdd_o26_$GHUSER.git
echo 'export GHUSER=tu-login' >> ~/.zshrc
git remote -v
```

**2 · Traerte lo del curso.** `switch main` te para en `main` vengas de donde vengas. `fetch` baja los commits y los deja **aparte**: no toca tus archivos.

```bash
git switch main
git fetch upstream
```

**3 · Incorporarlo y dejar tu fork al día.** El merge es donde **sí** cambian tus archivos. El push deja tu fork igual al curso. Si falta, tu rama nace atrasada.

```bash
git merge upstream/main
git push origin main
```

**4 · Crear la rama.** Nace del commit donde estás parado, por eso va después de actualizar. Nunca se entrega desde `main`.

```bash
git switch -c tarea-08-imagen
```

**5 · Tu carpeta y el espejo.** Misma ruta, mismo nombre, dentro de tu carpeta: así nadie toca las líneas de nadie. El `/.` copia el **contenido**.

```bash
mkdir -p estudiantes/$GHUSER/08_contenedores
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
```

**6 · Mirar, apartar por ruta, volver a mirar.** El primer `status` dice qué cambió; el segundo, qué vas a guardar. El `add` por ruta evita subir basura.

```bash
git status
git add estudiantes/$GHUSER/08_contenedores
git status
```

**7 · Guardar y subir la rama.** Se sube **la rama**, no `main`. El `-u` la empareja con la de tu fork.

```bash
git commit -m "unidad 08: mi imagen"
git push -u origin tarea-08-imagen
```

**8 · Abrir el pull request.** **No tiene comando**: es en el navegador. Base `raya-lucaria/fdd_o26` · `main`; compare `tarea-08-imagen`. El error clásico es dejar la base apuntando a tu propio fork.

**También valía:** `git checkout -b` por `git switch -c`; tu login en vez de `$GHUSER`; la URL `https://`; `git pull upstream main` en lugar de los pasos 2 y 3 juntos. **Nunca valía** `git add .` ni `git add -A`.

**Se descontaba siempre:** el paso de conectar en otro lugar que no fuera el 1; entregar desde `main`; `git add .`; y actualizar `main` después de crear la rama.
:::

**Repasa:** [[el-ritual-del-curso]].
