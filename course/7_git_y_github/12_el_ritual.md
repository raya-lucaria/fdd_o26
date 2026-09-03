---
id: el-ritual-del-curso
title: "El ritual"
nav_title: "El ritual"
summary: "Los tres bloques del flujo, en orden y con sus comandos exactos. Ésta es la página que se pregunta en el examen."
status: ready
estimated_time: 10m
tags: [flujo, ritual, pull-request, examen, disciplina]
prerequisites: [el-flujo-del-curso]
---

# El ritual

**Página 12 de 12** · 10 min

Meta: que esto salga sin pensar, siempre en el mismo orden.

::: figure {#git-el-ritual title="Tres bloques, siempre en este orden"}
![Tres carriles verticales con el flujo completo: el primero, ponte al día, sincroniza main con el repositorio del curso y actualiza tu fork; el segundo, abre tu espacio, crea la branch de la tarea y copia el código a tu carpeta; el tercero, entrega, revisa el estado, agrega por ruta, commitea, sube la branch y abre el pull request](_assets/git-el-ritual.svg)
:::

## En corto

- Son **tres bloques con nombre**, no doce comandos sueltos. Memoriza los bloques.
- Siempre en este orden, siempre desde la raíz del repositorio.
- Los dos `git status` del bloque C no son adorno.
- No entregaste hasta que la revisión automática esté en verde.

## Paso 0: una sola vez en la vida

Esto se hace la primera vez y nunca más. Ya lo hiciste en la página 9; está aquí para que la página sea completa.

Primero el **fork**, en el navegador. Después, en la terminal:

```bash
cd ~/fdd/fdd_o26
U=$(gh api user --jq .login) && echo "$U"
git remote rename origin upstream
git remote add origin git@github.com:$U/fdd_o26.git
git remote -v
```

**Deberías ver** cuatro líneas: `origin` con tu usuario, `upstream` con `raya-lucaria`.

## Bloque A: ponte al día

Siempre lo primero, antes de tocar nada. Deja tu `main` idéntico al del curso.

```bash
cd ~/fdd/fdd_o26
git switch main
git fetch upstream
git merge upstream/main
git push origin main
```

**Deberías ver** que el merge dice `Already up to date` o hace un fast-forward, y que el push sube sin pedirte nada.

**Por qué existe:** si empiezas a trabajar sobre una copia atrasada, tu pull request va a arrastrar diferencias que no son tuyas. Ponerte al día primero cuesta cinco segundos y evita eso.

## Bloque B: abre tu espacio

Una branch nueva por tarea, y el código copiado a tu carpeta.

```bash
git switch -c tarea-07-git
mkdir -p estudiantes/$U/07_git
cp -r codigo/07_git/. estudiantes/$U/07_git/
```

Y a partir de aquí **trabajas sólo dentro de `estudiantes/$U/07_git/`**.

**Deberías ver**, con `git status`, tu carpeta como untracked y nada más.

**Por qué existe:** la branch mantiene tu `main` limpio, que es lo que el bloque A necesita la próxima semana. Y la copia es el espejo de la página anterior, con su barra y su punto.

> [!WARNING]
> Si abriste una terminal nueva, `$U` está vacía. Compruébalo con `echo "$U"` antes de correr los comandos, o vas a crear una carpeta llamada `estudiantes//07_git`.

## Bloque C: entrega

```bash
git status
git add estudiantes/$U/07_git
git status
git commit -m "unidad 07: mi copia de trabajo"
git push -u origin tarea-07-git
```

**Deberías ver**, en el segundo `git status`, tus archivos en verde y **nada más en la lista**.

**Por qué existen los dos `git status`:** el primero te dice qué hay antes de agregar, para que veas si se coló basura. El segundo te dice qué vas a guardar exactamente. Son el hábito que separa una entrega limpia de una con un `.DS_Store` dentro. Míralos de verdad; no son decorativos.

El `-u` del push conecta tu branch local con la del fork. Gracias a eso, si tienes que corregir algo, el siguiente `git push` a secas ya funciona.

## Y después, el pull request

Esto es navegador. Entra a tu fork en GitHub y presiona **Compare & pull request**.

**Antes de crearlo, revisa las cuatro casillas de arriba.** Aquí es donde más gente se equivoca:

::: table {#git-pr-casillas title="La barra de selección del pull request"}

| Casilla | Debe decir |
|---|---|
| base repository | `raya-lucaria/fdd_o26` |
| base | `main` |
| head repository | `tu-login/fdd_o26` |
| compare | `tarea-07-git` |

:::

El error clásico es dejar `base repository` apuntando a tu propio fork. El pull request se crea, se ve bien, y **no me llega**. Si la barra no dice `raya-lucaria` del lado izquierdo, todavía no entregaste.

Ponle un título que diga qué es y créalo.

## El último paso, que casi nadie hace

Espera a que la revisión automática termine y **comprueba que quedó en verde**.

Si sale roja, lee el mensaje: dice qué archivo y qué hacer. Corriges, y:

```bash
git add <lo que corregiste>
git commit -m "corrijo lo que marcó la revisión"
git push
```

El pull request se actualiza solo. **No abras otro.**

> [!NOTE]
> Entregado significa: pull request abierto antes de la fecha, con la revisión en verde. Que yo lo mergee es un trámite posterior y no depende de ti.

## El resumen que hay que saber

::: table {#git-ritual-resumen title="Los tres bloques"}

| Bloque | Qué hace | Cómo termina |
|---|---|---|
| **A. Ponte al día** | Trae lo nuevo del curso y actualiza tu fork | Tu `main` es idéntico al del curso |
| **B. Abre tu espacio** | Branch de la tarea y copia del código | Estás en tu branch, con tu carpeta lista |
| **C. Entrega** | Revisa, agrega, commitea y sube | Pull request abierto y en verde |

:::

> [!WARNING]
> **Esto se pregunta en el examen, de memoria.** Los tres bloques, en orden, qué hace cada uno y con qué comandos. Así se entregan todas las tareas del resto del curso, y una desviación del flujo cuenta como entrega no hecha. La forma de aprendérselo no es leerlo: es hacerlo hasta que salga solo.

::: problem {#git-p12-orden title="Se me olvidó el bloque A"}
Trabajaste toda la tarde. Hiciste la branch, copiaste el código, editaste, commiteaste y pusheaste. Al abrir el pull request, GitHub te muestra que tu rama toca **once archivos**, y sólo dos son tuyos: los otros nueve están en `course/` y son cambios que yo publiqué el martes.

¿Qué te saltaste, por qué produce ese resultado, y cómo lo arreglas?
:::

::: hint {of="git-p12-orden"}
Piensa desde qué punto de la historia nació tu branch, y qué había pasado en el repositorio del curso mientras tanto.
:::

::: answer {of="git-p12-orden"}
Te saltaste el **bloque A**. Tu branch nació de un `main` atrasado, de la última vez que sincronizaste.

El pull request no compara tu branch contra el estado actual del curso, sino contra el punto donde las dos historias se separaron. Como tu `main` no tenía mis commits del martes, todo lo que yo publiqué después aparece como diferencia de tu rama. No los escribiste tú, pero desde fuera tu propuesta incluye "revertir esos nueve archivos".

El robot te lo va a rechazar, y con razón: hay cambios fuera de tu carpeta.

Se arregla poniéndote al día ahora, sin perder tu trabajo:

```bash
git switch main
git fetch upstream
git merge upstream/main
git push origin main
git switch tarea-07-git
git merge main
```

Ese último merge trae mis commits a tu branch. Si hay conflicto, se resuelve como en la página 8. Después haces `push` y el pull request se actualiza solo: ahora sólo va a mostrar tus dos archivos.

Por eso el bloque A va primero y no en medio. Hacerlo después funciona, pero cuesta más.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** A, B, C. Ponte al día, abre tu espacio, entrega. Nunca en otro orden.

## Cierre

Eso es todo el flujo. Ten a mano el [[cheatsheet-git|cheatsheet]]: está para consultarlo, no para memorizarlo, con la única excepción de los tres bloques de esta página.
