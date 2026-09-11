---
id: branches-en-serio
title: "Branches, en serio"
nav_title: "Branches"
summary: "Por qué el curso pide una branch por tarea: qué le hace switch a tus archivos, qué pasa cuando dos branches tocan lo mismo, y cómo se rescata una branch que nació atrasada."
status: ready
estimated_time: 35m
tags: [git, branch, switch, merge, conflicto, flujo]
prerequisites: [el-fork]
---

# Branches, en serio

**GitHub · página 3 de 6** · 35 min

Meta: que crear, cambiar y borrar branches deje de dar miedo, porque el resto del curso se entrega desde una.

## En corto

- Ya sabes que una branch es **una etiqueta que apunta a un commit**. Aquí ves qué te hace *en el disco*.
- `git switch` **reescribe los archivos de tu carpeta** para que coincidan con la branch a la que llegas.
- Una branch por tarea no es burocracia: **una branch es un nombre para un intento**, y en `main` sólo tienes uno.
- Una branch nacida de un `main` atrasado arrastra basura a tu pull request. Se rescata con un comando.
- Y resolver un conflicto es **editar el archivo y borrar los marcadores**. Git no comprueba que lo hayas hecho.

Todo lo de esta página se hace en el repositorio de verdad, dentro de tu carpeta. Al final se limpia.

---

## 1 · La branch cambia lo que ves

::: figure {#git-branch-disco title="Cambiar de branch reescribe tu carpeta"}
![La misma carpeta vista desde dos branches: parado en la branch de tarea el archivo de trabajo aparece en el listado, y al cambiarse a main el mismo listado ya no lo muestra, aunque el archivo no se borró de la historia](../_assets/git-branch-disco.svg)
:::

```bash
cd ~/fdd/fdd_o26
echo "$GHUSER"                    # si sale vacío, redefínela
git switch main              # arranca siempre desde main
git switch -c practica-a     # -c = create: créala Y muévete
git branch --show-current    # → practica-a

echo "escrito en practica-a" > estudiantes/$GHUSER/nota.txt
git add estudiantes/$GHUSER/nota.txt   # por ruta, nunca "."
git commit -m "practica: nota en la branch a"
ls estudiantes/$GHUSER            # nota.txt está

git switch main
ls estudiantes/$GHUSER            # NO está  ← lo importante

git switch practica-a
ls estudiantes/$GHUSER            # volvió
```

```text
git switch -c practica-a
       │    │      └── el nombre, lo pones tú
       │    └───────── -c: créala si no existe
       └────────────── cámbiate de branch, y ajusta el disco
```

**No se borró.** Sigue guardado en el commit de `practica-a`. Lo que hizo `switch` fue poner en tu carpeta el contenido que corresponde a `main`, y en `main` ese archivo nunca existió.

> Una branch no es una carpeta ni una copia. Es un punto de la historia, y `git switch` **sincroniza tu carpeta con ese punto**.

> [!WARNING]
> Con cambios sin commitear, Git **puede** negarse a cambiar de branch:
> ```text
> error: Your local changes to the following files
> would be overwritten by checkout:
> ```
> Sólo se niega si ese archivo **difiere** entre las dos branches; si es igual, te deja pasar y se lleva la edición contigo. No te regaña: te avisa de que el switch la borraría. Salidas: `git commit` o `git stash`.

---

## 2 · Dos branches tuyas también chocan

Esto ya lo hiciste en [[branches-y-merge|Branches y merge]], con su laboratorio de juguete. Aquí sólo cambia el escenario: las dos branches son tuyas y el archivo está en tu carpeta. **El mecanismo es idéntico**, y por eso no lo repetimos.

```bash
git switch main          # las dos nacen del MISMO punto
git switch -c practica-b
echo "escrito en practica-b" > estudiantes/$GHUSER/nota.txt
git add estudiantes/$GHUSER/nota.txt
git commit -m "practica: nota en la branch b"

git merge practica-a     # → CONFLICT (add/add)
```

Resuélvelo como en 7.1: edita hasta que no quede ningún marcador, comprueba con `grep -c '^[<=>]\{7\}' <archivo>` que dice `0`, y cierra con `git add` y `git commit`. O sal con `git merge --abort`.

> [!NOTE]
> Lo que acabas de provocarte a solas es lo que pasa cuando dos personas tocan el mismo archivo. La única forma de que no aparezca nunca es que nadie toque las líneas de nadie, y de ahí sale la regla de la página 4.

## 3 · La branch atrasada, que es la que rompe entregas

::: figure {#git-branch-atrasada title="Una branch nacida de un main viejo"}
![Dos escenarios comparados: arriba la branch nace de un main atrasado y el pull request muestra como diferencia propia todos los commits del curso que faltaban; abajo la misma branch después de traer main con un merge, y el pull request muestra sólo los archivos del estudiante](../_assets/git-branch-atrasada.svg)
:::

Éste es el error más caro del semestre y **no da ningún mensaje**. Simúlalo:

```bash
git switch main
git switch -c practica-atrasada   # nace del main de ahorita

# haz algo en tu branch, como en una tarea de verdad
echo "mi trabajo" > estudiantes/$GHUSER/tarea.txt
git add estudiantes/$GHUSER/tarea.txt
git commit -m "practica: mi trabajo de la tarea"

# ahora simulamos que el curso avanzó mientras tú trabajabas.
# El avance va en su propia branch: tu main no se toca en toda
# la práctica, y por eso la limpieza del final es indolora.
git switch -c curso-simulado main
echo "avance del curso" > estudiantes/$GHUSER/simulacion.txt
git add estudiantes/$GHUSER/simulacion.txt
git commit -m "practica: simulo que el curso avanzó"

git switch practica-atrasada

# el comando que lo DIAGNOSTICA: qué le falta a tu branch
git log --oneline practica-atrasada..curso-simulado

# el RESCATE, un solo comando
git merge curso-simulado

# ahora la lista sale vacía
git log --oneline practica-atrasada..curso-simulado
```

```text
git log --oneline practica-atrasada..curso-simulado
                  │                  └── ...hasta este otro
                  └──────────────── qué le falta a éste...
```

**Si esa lista no está vacía, tu branch nació atrasada.**

Aquí se compara contra `curso-simulado` porque ahí pusimos el avance. **En la vida real se compara contra `upstream/main`**, que es donde de verdad avanza el curso: tu `main` local puede estar tan atrasado como tu branch, y entonces `..main` te sale vacío y te miente.

Por qué importa: el pull request **no compara tu branch contra el curso de hoy**, sino contra el punto donde las dos historias se separaron.

Si tu branch nació de un `main` de hace dos semanas, GitHub muestra como diferencia tuya todo lo que publiqué en esas dos semanas. Tú no lo escribiste. Pero desde fuera tu propuesta dice *"revierte esos nueve archivos"*.

Por eso el flujo empieza por ponerse al día, y no a la mitad.

---

## Limpieza

```bash
git switch main
git branch -D practica-a practica-b \
              practica-atrasada curso-simulado
git branch                      # sólo main
git status                      # sólo tu carpeta, untracked
```

Todo lo que creaste vivía en branches, así que borrarlas basta: **tu `main` nunca se tocó**, y por eso aquí no hace falta ningún comando destructivo. Ésa es justamente la ventaja de trabajar en branches, vivida en carne propia.

> [!NOTE]
> `-D` con mayúscula borra aunque la branch tenga commits sin mergear. Aquí es lo que queremos, porque era práctica. En una branch de tarea de verdad se usa `-d`, que se niega si hay trabajo sin guardar en ningún lado.

## El ciclo de vida de una branch

::: table {#git-branch-cuando title="Cuándo se crea, cuándo se borra"}

| Momento | Comando | Qué hace |
|---|---|---|
| Empiezas una tarea | `git switch -c tarea-07-git` | La crea desde donde estás. **Párate en `main` actualizado** |
| Te mueves | `git switch <nombre>` | Reescribe tu carpeta con el contenido de esa branch |
| No sabes dónde estás | `git branch --show-current` | Imprime el nombre. Cuesta cero, úsalo |
| Nació atrasada | `git merge main` | Le trae lo que le faltaba |
| ¿Nació atrasada? | `git log --oneline <branch>..upstream/main` | Si no sale vacío, sí |
| Ya te mergearon el PR | `git branch -d tarea-07-git` | La borra **sólo si ya está mergeada** |
| Era práctica, tírala | `git branch -D practica-a` | La borra aunque tenga trabajo sin mergear |

:::

`-d` **se niega** si la branch tiene commits que no están en ningún lado. Esa negativa es una protección: cuando aparece hay que leerla, no escalarla a `-D`.

## Por qué una branch por tarea

Hasta aquí podrías pensar que entregar desde `main` daría igual: tu trabajo se acumula ahí y ya. Se acumula, sí, y de hecho no pasa nada malo **el mismo día**. El problema llega después.

**Una branch es un nombre para un intento.** Puedes tener varios, tirar uno, y entregar uno mientras empiezas otro. En `main` tienes exactamente un intento, para siempre, y entregar y seguir trabajando son la misma acción: cualquier cosa que subas a `main` se mete sola al pull request que dejaste abierto.

Y hay una razón más dura, que no depende de tu disciplina sino de un botón que aprieta otra persona:

> **Tu `main` es tu copia del curso.** Si le metes tu trabajo, deja de serlo. Y cuánto se estropee depende de cómo yo mergee tu pull request, que es algo que tú ni ves ni controlas.

Con el botón *Create a merge commit*, tu commit entra tal cual y tu siguiente sincronización sigue siendo un fast-forward. Con el de junto, *Squash and merge*, lo que llega al curso es un commit **nuevo, con otro hash**: el tuyo deja de estar en la historia, tu `main` se bifurca del mío **para siempre**, y de ahí en adelante cada `git merge upstream/main` te crea un commit de merge.

Entregando desde una branch eso no puede pasar, porque tu `main` nunca es lo que se mergea. Sigue siendo una copia exacta del curso, y el bloque A siempre es un fast-forward.

## Cómo se llaman en este curso

```text
tarea-07-git      tarea-08-python      tarea-09-sql
```

Sin espacios, sin acentos, en minúsculas. Y **nunca se entrega desde `main`**, por lo de arriba: un pull request que sale de tu `main` lo rechaza la revisión automática.

> [!NOTE]
> **Si sólo recuerdas una cosa:** una branch por tarea, nacida de un `main` recién actualizado. Si `git log --oneline tu-branch..upstream/main` no sale vacío, tu pull request va a incluir cosas que no son tuyas.

## Cierre

Ya sabes moverte entre branches. Falta **dónde** van tus archivos: [[el-flujo-del-curso|La zona roja y tu espejo]].
