---
id: parcial-github-b
title: "Parcial 3 · GitHub · Examen B"
nav_title: "Examen B"
summary: "El examen B de GitHub, pregunta por pregunta, con la respuesta explicada debajo de cada una: la rama que nació vieja, y el ritual del curso en orden."
status: ready
estimated_time: 30m
tags: [examen, parcial, git, github, ritual, branches]
---

# Parcial 3 · GitHub · Examen B

**[PDF del examen B, sin respuestas](../../_assets/parcial-github-b.pdf)** · 30 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte.

## Pregunta 1 · Lee el árbol (3 puntos)

Un compañero hizo su fork el primer día y creó de inmediato la rama de la tarea. Mientras él trabajaba, el profesor corrigió `codigo/docker/certificaciones.md` y le agregó una sección: ése es el commit **R**. Él copió la plantilla el primer día y no volvió a sincronizar. Contesta con tus palabras, sin comandos.

```text
o-o-o-o---P---Q---R    upstream/main
      |
      +---X---Y        tarea-08-datacamp-intro
      |
      main, origin/main
```

::: problem {#pgb-1a title="1a · ¿Por qué le falta la sección? (0.75)"}
Su `certificaciones.md` no tiene la sección nueva, y él nunca la borró. Explica por qué, en términos de **dónde nació su rama**.
:::

::: answer {of="pgb-1a"}
**Respuesta.** Porque **nunca la tuvo**: su rama nació en el cuarto commit, **antes** de R.

**Por qué.** Lo que hay en una rama es el estado del commit donde nació más lo que pusiste encima. La sección vive en R, que está después de ese punto, y además copió la plantilla el primer día: su copia es la versión vieja. No le falta porque la haya quitado; le falta porque nunca llegó.

**También valía.** «No actualizó», sin ligarlo a dónde nació la rama, valía la mitad. «La borró» valía cero.
:::

::: problem {#pgb-1b title="1b · Dos cosas que hizo bien (0.75)"}
Di **dos cosas que hizo bien**. Sí las hay: quien sólo busque errores se va a quedar corto.
:::

::: answer {of="pgb-1b"}
Cualquier par de éstas:

1. Trabajó en una rama y no en `main`: su `main` sigue siendo copia exacta del curso, y por eso arreglarlo es barato.
2. Respetó la regla del espejo: copió la plantilla a su carpeta en vez de editar `codigo/`.
3. Hizo el fork y conectó su copia desde el primer día.
4. El nombre de la rama es el que la tarea asignó.

**Por qué se pregunta.** Para diagnosticar hay que saber qué no tocar; quien sólo ve errores propone empezar de cero.

**También valía.** Una sola cosa, la mitad. «Nada», cero.
:::

::: problem {#pgb-1c title="1c · ¿Se puede mergear? ¿Qué problema trae? (0.75)"}
Entrega así. ¿Se puede mergear su pull request? ¿Qué problema trae aunque se pueda? ¿Cómo se evita?
:::

::: answer {of="pgb-1c"}
- **Sí se puede**, y casi seguro sin conflicto. X e Y sólo tocan `estudiantes/<login>/`, y P, Q y R sólo tocan `codigo/`: nadie cambió las mismas líneas.
- **El problema no es de Git, es de contenido.** Entregó trabajo hecho sobre una plantilla vieja: le falta lo que pide la sección nueva, aunque la revisión automática salga en verde. El verde dice «no rompiste las reglas del repositorio», no «tu tarea está completa».
- **Se evita** actualizando `main` antes de crear la rama, y volviendo a copiar el espejo cuando el curso publica una corrección.

**También valía.** Cada una de las tres partes valía un tercio.
:::

::: problem {#pgb-1d title="1d · git merge upstream/main dentro de su rama (0.75)"}
En vez de haber sincronizado antes, corre `git merge upstream/main` **dentro** de su rama de entrega. ¿Se actualiza su copia del archivo? ¿Cambia lo que el pull request muestra? Justifica las dos.
:::

::: answer {of="pgb-1d"}
**¿Se actualiza su copia? No.** El merge trae P, Q y R, así que `codigo/docker/certificaciones.md` queda al día. Pero **su** copia es `estudiantes/<login>/docker/certificaciones.md`: otro archivo, en otra ruta. Git no sabe que uno es espejo del otro. Hay que volver a copiarlo.

**¿Cambia el pull request? No cambia la lista de archivos.** Antes la base era el cuarto commit y ya mostraba sólo su carpeta; después la base es R y sigue mostrando sólo su carpeta. Su rama nunca tuvo archivos del curso, así que mover la base no le quita nada.

**Contraste con el examen A.** Allá mover la base **sí** cambiaba el pull request, porque la rama cargaba commits de otra tarea.

**También valía.** Cada mitad valía la mitad del inciso. «Sí se actualiza» confunde el archivo del curso con su copia.
:::

**Repasa:** [[branches-y-merge]], [[branches-en-serio]] y [[el-flujo-del-curso]].

## Pregunta 2 · El ritual, en orden (7 puntos)

Las mismas instrucciones que en el examen A; los pasos venían en otro desorden. Usa la rama `tarea-08-imagen` y su carpeta `08_contenedores/` como ejemplo. Para cada paso escribe el **orden** (1 a 8), **qué hace y por qué**, y sus **comandos**.

1. Revisar qué cambió y apartar sólo lo tuyo, por ruta.
2. Incorporar eso a tu main y dejar tu fork al día.
3. Guardar lo apartado y subir tu rama a tu fork.
4. Crear tu carpeta de la unidad y copiar ahí el material del curso.
5. Proponerle tu trabajo al curso desde el navegador.
6. Crear la rama de esta tarea y moverte a ella.
7. Traerte lo que el curso publicó, sin tocar todavía tus archivos.
8. Conectar tu copia con el repositorio del curso. (Una sola vez en el semestre.)

::: problem {#pgb-2 title="2 · El ritual (7 puntos: orden 2, explicación 2, comandos 3)"}
Escribe el orden, qué hace cada paso y sus comandos.
:::

::: answer {of="pgb-2"}
**Orden de los renglones impresos:** 6 · 3 · 7 · 5 · 8 · 4 · 2 · 1. Es decir, el primer renglón («Revisar qué cambió») es el paso 6, el segundo es el 3, y así.

Los pasos ya en orden son **los mismos que en el examen A**. Están explicados uno por uno, con sus comandos, en la respuesta de la pregunta 2 de [[parcial-github-a]]. En corto:

```bash
# 1 · conectar (una vez): fork en el navegador, y luego
git remote rename origin upstream
git remote add origin git@github.com:$GHUSER/fdd_o26_$GHUSER.git
# 2 · traerte lo del curso
git switch main
git fetch upstream
# 3 · incorporarlo y dejar tu fork al día
git merge upstream/main
git push origin main
# 4 · crear la rama
git switch -c tarea-08-imagen
# 5 · tu carpeta y el espejo
mkdir -p estudiantes/$GHUSER/08_contenedores
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
# 6 · mirar, apartar por ruta, volver a mirar
git status
git add estudiantes/$GHUSER/08_contenedores
git status
# 7 · guardar y subir la rama
git commit -m "unidad 08: mi imagen"
git push -u origin tarea-08-imagen
# 8 · abrir el pull request en el navegador (sin comando)
```

**Cuidado:** no uses el orden del examen A para calificar el B: los renglones venían en otro desorden.
:::

**Repasa:** [[el-ritual-del-curso]].
