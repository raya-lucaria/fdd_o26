---
id: el-flujo-del-curso
title: "El flujo del curso"
nav_title: "El flujo del curso"
summary: "La zona roja y la verde, la regla del mirror que elimina toda ambigüedad sobre dónde copiar el código, y qué revisa el robot antes de aceptar tu entrega."
status: ready
estimated_time: 15m
tags: [flujo, mirror, estudiantes, github-actions, disciplina]
prerequisites: [dos-personas-un-archivo]
---

# El flujo del curso

**GitHub · página 5 de 6** · 15 min

Meta: que nunca tengas que preguntar dónde va un archivo ni cómo se llama tu carpeta.

::: figure {#git-el-mirror title="Tu carpeta es un espejo"}
![Dos árboles de archivos lado a lado: a la izquierda en rojo la carpeta de código del curso que es de sólo lectura, y a la derecha en verde tu carpeta dentro de estudiantes con tu nombre de usuario de GitHub, con los mismos nombres de subcarpeta y archivo en los dos lados](../_assets/git-el-mirror.svg)
:::

## En corto

- El repositorio tiene una **zona roja**, que sólo se lee, y una **zona verde**, que es tuya.
- Tu carpeta es un **espejo** de la carpeta de código: misma ruta, mismo nombre, sin excepciones.
- Tu carpeta se llama exactamente como tu login de GitHub, y ese nombre sale de un comando.
- Un robot revisa cada entrega. Aquí está qué revisa, antes de que te rechace algo.

## Las dos zonas

::: table {#git-zonas title="Qué puedes tocar"}

| Carpeta | Qué es | Puedes escribir |
|---|---|---|
| `course/` | El contenido del sitio que estás leyendo | No |
| `codigo/` | El código que yo publico para cada unidad | No |
| `tools/`, `skins/` | La maquinaria del sitio | No |
| `estudiantes/tu-login/` | Tuya | Sí, y **sólo** ahí |

:::

La razón no es jerárquica, es la de la página anterior. Si treinta personas editan `codigo/`, cada actualización mía choca con el trabajo de todos. Con una carpeta por persona, los treinta pull requests de la semana se mergean sin que nadie resuelva un conflicto.

## La regla del mirror

Ésta es la regla que se repite igual en todas las unidades del resto del curso. Vale la pena leerla dos veces:

> **Tu carpeta es un espejo de `codigo/`. Misma ruta, mismo nombre, sin excepciones.**
> Yo publico en `codigo/07_git/` y tú copias a `estudiantes/tu-login/07_git/`.

No se inventa el nombre. No se traduce al español. No se decide dónde va. No se pregunta. Si en `codigo/` se llama `07_git`, en tu carpeta se llama `07_git`.

## Paso 1: averigua tu login y crea tu carpeta

**Haz:** desde la raíz del repositorio, siempre.

```bash
cd ~/fdd/fdd_o26
U=$(gh api user --jq .login)
echo "$U"
```

**Deberías ver** tu usuario de GitHub, con sus mayúsculas exactas. Si sale vacío, vuelve al paso 2 de la página anterior.

**Haz:**

```bash
mkdir -p estudiantes/$U
touch estudiantes/$U/.gitkeep
ls estudiantes/$U
```

**Deberías ver** el `.gitkeep` que creaste. Es el truco de la página 5: Git no rastrea carpetas vacías, así que hace falta un archivo dentro para que la carpeta llegue a existir en el repositorio.

> [!WARNING]
> El nombre tiene que ser **idéntico** a tu login: mismas mayúsculas, mismos guiones. El robot lo compara contra el autor del pull request. El semestre pasado alguien creó una carpeta con guion bajo, y los logins de GitHub no admiten guion bajo, así que era un nombre imposible. Por eso se usa `$U` y no el teclado.

## Paso 2: copia el código

**Haz:**

```bash
mkdir -p estudiantes/$U/07_git
cp -r codigo/07_git/. estudiantes/$U/07_git/
ls estudiantes/$U/07_git
```

**Deberías ver** los mismos archivos que hay en `codigo/07_git/`.

Fíjate en la **barra y el punto** al final del origen. No es un adorno:

::: table {#git-cp-punto title="La diferencia que arruina la entrega"}

| Comando | Si el destino no existe | Si el destino ya existe |
|---|---|---|
| `cp -r codigo/07_git dest/07_git` | Correcto | **Crea `07_git/07_git/`** |
| `cp -r codigo/07_git/. dest/07_git/` | Correcto | Correcto |

:::

Sin la barra y el punto, `cp` copia **la carpeta**; con ellos copia **su contenido**. La segunda vez que lo corras, porque publiqué un archivo nuevo, la primera forma te va a anidar la carpeta dentro de sí misma. Y el robot lo aceptaría, porque técnicamente está dentro de tu carpeta, así que el error pasaría desapercibido hasta que yo revise.

> [!WARNING]
> No copies arrastrando en el Finder ni en el Explorador de Windows. Producen `07_git copia` y `07_git - copia`, que no son el nombre del espejo. Usa la terminal.

## Paso 3: trabaja sólo ahí dentro

Editas los archivos que están en `estudiantes/$U/07_git/`. Nunca los de `codigo/`.

Si por accidente editaste algo en la zona roja, se deshace así:

```bash
git restore codigo/
```

## Qué revisa el robot

Cada pull request dispara una revisión automática antes de que yo lo vea. No es un misterio y no está para reprobarte: está para que un error se detecte en treinta segundos y no en una semana.

::: table {#git-robot title="Las revisiones automáticas"}

| Revisa | Qué rechaza |
|---|---|
| La ubicación | Cualquier archivo fuera de `estudiantes/tu-login/` |
| El nombre de tu carpeta | Que no coincida con tu login de GitHub |
| El nombre del espejo | Una subcarpeta que no exista igual en `codigo/` |
| La basura | `.DS_Store`, `__pycache__/`, `.env`, `node_modules/` y compañía, **incluso dentro de tu carpeta** |
| La branch | Un pull request que venga de tu `main` en vez de una branch de tarea |

:::

Cuando algo falla, el mensaje dice qué archivo y qué hacer. Y hay una cosa que casi nadie sabe:

> [!NOTE]
> **Un pull request rechazado se corrige haciendo `push` a la misma branch.** No abras otro. El pull request se actualiza solo con tus commits nuevos y la revisión se vuelve a correr.

![Un corredor técnico largo y estrecho partido en dos mitades por un umbral iluminado en ámbar: la mitad cercana es cálida y ordenada, con estantes alineados, y la lejana se disuelve en azul frío; en primer plano, de espaldas y en silueta, una figura se detiene un paso antes del umbral, sin cruzarlo.](../_assets/ilus-git-disciplina.jpg)

## Por qué tanta insistencia

Vale la pena decirlo directo. Este flujo se pide con una precisión que puede parecer excesiva, y hay dos razones.

La primera es práctica: **el flujo es la parte que se automatiza.** Yo no reviso a mano dónde pusiste cada archivo; lo revisa un programa, y un programa no interpreta intenciones. Una carpeta con un nombre parecido es una carpeta equivocada.

La segunda es que esto es exactamente cómo se trabaja después. En cualquier equipo, un pull request que no pasa las revisiones automáticas no se mergea, sin importar qué tan bueno sea el código. Aprender el hábito aquí, donde el costo de equivocarse es volver a intentar, es barato.

> [!WARNING]
> **Sobre el examen.** El flujo de trabajo se pregunta de memoria. No de forma aproximada: los tres bloques de la página siguiente, en orden, sabiendo qué hace cada uno y qué comando le corresponde. Todas las tareas del resto del curso se entregan así, y una desviación del flujo cuenta como entrega no hecha. Vale la pena que lo hagas hasta que salga sin pensar.

::: problem {#git-p11-rechazo title="Me rechazaron por un archivo que borré"}
Un compañero se dio cuenta de que había subido un `.DS_Store` la semana pasada. Lo borra, hace commit, y abre un pull request. El robot se lo rechaza mencionando ese mismo `.DS_Store`.

¿Qué está pasando, y qué le dirías que haga?
:::

::: hint {of="git-p11-rechazo"}
La lista de archivos de un pull request incluye todo lo que cambió. Piensa en si un archivo borrado aparece en esa lista y en cómo se ve desde fuera.
:::

::: answer {of="git-p11-rechazo"}
Una revisión ingenua mira **la lista de archivos tocados** por el pull request, y un archivo borrado aparece en esa lista igual que uno agregado. Si la revisión sólo pregunta "¿está prohibido este nombre?", va a rechazar a alguien que está haciendo exactamente lo correcto.

Es un falso positivo, y de los peores, porque castiga la acción que uno quiere fomentar.

Lo que le diría depende de quién arregla qué. Al compañero: que lo reporte, porque el error es de la revisión y no suyo. Y del lado del robot, la corrección es mirar **el tipo de cambio** además del nombre, e ignorar los borrados al buscar basura prohibida.

Es un buen recordatorio de que estas revisiones son programas escritos por alguien, con sus errores. Si una te rechaza algo que estás seguro de haber hecho bien, dilo.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** misma ruta, mismo nombre. Si en `codigo/` se llama `07_git`, en tu carpeta se llama `07_git`.

## Cierre

Ya sabes las reglas. En [[el-ritual-del-curso|El ritual]] están los comandos exactos, en orden, para ejecutarlas.
