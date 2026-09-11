---
id: cheatsheet-git
title: "Cheatsheet"
nav_title: "Chuleta"
summary: "Todos los comandos de la unidad en una sola página, agrupados por lo que quieres hacer, con el enlace a donde se explicó cada uno."
status: ready
estimated_time: 5m
tags: [git, github, referencia, comandos, cheatsheet]
prerequisites: [el-ritual-del-curso]
---

# Cheatsheet

**Apéndice** · para consultar, no para memorizar

Aquí sólo están los comandos que esta unidad enseñó. Si un comando no aparece, es a propósito: no lo necesitas todavía.

La única parte que sí se memoriza son los tres bloques de [[el-ritual-del-curso|El ritual]], y están completos aquí abajo.

## El flujo, completo

Lo único de esta página que se memoriza. Son dos bloques: el paso 0 va una vez en el semestre, y A–C en cada entrega. Explicados en [[el-ritual-del-curso|El ritual]].

```bash
# ═══ PASO 0 · UNA VEZ EN EL SEMESTRE ══════════════════
# Primero el fork, en el navegador:
#   github.com/raya-lucaria/fdd_o26

cd ~/fdd/fdd_o26                 # el paso 0 va aquí dentro
# ¿ya lo hice?  si imprime SALTA, brinca al bloque A
git remote -v | grep -q upstream && echo SALTA

# tu login, una vez en la vida, en el perfil de tu shell.
# Sale de la URL de tu fork. ~/.bashrc si usas bash.
echo 'export GHUSER=tu-login' >> ~/.zshrc
exec $SHELL                      # recarga el perfil
echo "$GHUSER"                   # tiene que salir tu login

git remote rename origin upstream   # el curso: aquí BAJAS
git remote add origin \
  git@github.com:$GHUSER/fdd_o26_$GHUSER.git
git remote -v                    # 4 líneas, 2 nombres
```

Y esto es lo de cada entrega. **Éste es el bloque que se copia cada semana**; el de arriba no se vuelve a tocar.

```bash
# ═══ CADA VEZ QUE ENTREGAS ════════════════════════════
cd ~/fdd/fdd_o26                 # siempre desde la raíz
echo "$GHUSER"                   # tu login, del perfil


# ─── A · PONTE AL DÍA ──────────────────────────────────
git switch main                  # párate en main
git fetch upstream               # baja. NO toca tus archivos
git merge upstream/main          # mételo. Aquí SÍ cambian
git push origin main             # tu fork, al día


# ─── B · ABRE TU ESPACIO ───────────────────────────────
git switch -c tarea-NN-nombre    # nace del main al día
mkdir -p estudiantes/$GHUSER/NN_nombre
cp -r codigo/NN_nombre/. estudiantes/$GHUSER/NN_nombre/
#   ... trabajas SÓLO dentro de estudiantes/$GHUSER/ ...


# ─── C · ENTREGA ───────────────────────────────────────
git status                       # ¿qué cambió? míralo
git add estudiantes/$GHUSER/NN_nombre # por ruta, nunca "."
git status                       # eso, y nada más
git commit -m "unidad NN: entrega"
git push -u origin tarea-NN-nombre
#   → navegador: Compare & pull request
#     base repository: raya-lucaria/fdd_o26   base: main
#     head repository: tu-login/fdd_o26_tu-login
#     compare:         tarea-NN-nombre
#
#   Al mergearse, el pull request te ofrece "Delete branch".
#   No hay cuarto bloque: el A ya te devuelve a main.
```

## Orientarte

::: table {#git-cs-orientar title="Antes de hacer nada"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber qué cambió y en qué zona está | `git status` | [[tu-primer-repositorio|Git · 2]] |
| Ver la historia | `git log --oneline` | [[tu-primer-repositorio|Git · 2]] |
| Ver lo que edité y no he apartado | `git diff` | [[tu-primer-repositorio|Git · 2]] |
| Ver lo que sí va a entrar al commit | `git diff --staged` | [[tu-primer-repositorio|Git · 2]] |
| Saber en qué branch estoy | `git branch` | [[branches-y-merge|Git · 6]] |
| Saber a qué repositorios hablo | `git remote -v` | [[el-fork|GitHub · 2]] |

:::

## Guardar

::: table {#git-cs-guardar title="Las dos puertas"}

| Quiero | Comando | Dónde |
|---|---|---|
| Empezar un repositorio | `git init` | [[tu-primer-repositorio|Git · 2]] |
| Apartar un archivo para el próximo commit | `git add <ruta>` | [[tu-primer-repositorio|Git · 2]] |
| Guardar lo apartado | `git commit -m "mensaje"` | [[tu-primer-repositorio|Git · 2]] |

:::

Nunca `git add .`. La regla es agregar una ruta que puedas nombrar y que acabes de ver en `git status`.

## Deshacer

::: table {#git-cs-deshacer title="Depende de dónde está el cambio"}

| El cambio está en | Quiero | Comando | Dónde |
|---|---|---|---|
| Working directory | Descartar la edición | `git restore <archivo>` | [[deshacer-en-git|Git · 5]] |
| Staging area | Sacarlo sin perderlo | `git restore --staged <archivo>` | [[deshacer-en-git|Git · 5]] |
| Último commit | Deshacerlo, conservar el trabajo | `git reset --soft HEAD~1` | [[deshacer-en-git|Git · 5]] |
| Último commit | Deshacerlo y tirar el trabajo | `git reset --hard HEAD~1` | [[deshacer-en-git|Git · 5]] |
| Estorba, lo quiero después | Apartarlo | `git stash` | [[deshacer-en-git|Git · 5]] |
| Está en el stash | Traerlo de vuelta | `git stash pop` | [[deshacer-en-git|Git · 5]] |
| Creí haberlo perdido | Buscarlo | `git reflog` | [[deshacer-en-git|Git · 5]] |

:::

`git restore` y `git reset --hard` son los que borran sin red de seguridad. `reset` además reescribe la historia: sobre algo que ya subiste, no lo uses.

## Branches

::: table {#git-cs-branches title="Trabajar en varias líneas"}

| Quiero | Comando | Dónde |
|---|---|---|
| Crear una branch y saltar a ella | `git switch -c <nombre>` | [[branches-y-merge|Git · 6]] |
| Saltar a una que ya existe | `git switch <nombre>` | [[branches-y-merge|Git · 6]] |
| Traer otra branch a la mía | `git merge <nombre>` | [[branches-y-merge|Git · 6]] |
| Salir de un merge que se complicó | `git merge --abort` | [[branches-y-merge|Git · 6]] |
| Borrar una branch ya mergeada | `git branch -d <nombre>` | [[branches-y-merge|Git · 6]] |
| Borrarla aunque no esté mergeada | `git branch -D <nombre>` | [[branches-en-serio|GitHub · 3]] |
| Saber en qué branch estoy, sólo el nombre | `git branch --show-current` | [[branches-en-serio|GitHub · 3]] |
| Saber si mi branch nació atrasada | `git log --oneline <branch>..upstream/main` | [[branches-en-serio|GitHub · 3]] |
| Rescatar una branch atrasada | `git merge main` | [[branches-en-serio|GitHub · 3]] |
| Borrar la branch también del fork | `git push origin --delete <nombre>` | [[el-ritual-del-curso|GitHub · 5]] |

:::

Para resolver un conflicto: edita el archivo hasta que no queden marcadores, `git add` al archivo, y `git commit`.

## Hablar con GitHub

::: table {#git-cs-github title="Los dos remotes"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber mi login exacto | está en la URL de tu fork | [[el-fork|GitHub · 2]] |
| Bajar lo nuevo del curso | `git fetch upstream` | [[el-fork|GitHub · 2]] |
| Juntarlo con mi branch | `git merge upstream/main` | [[el-fork|GitHub · 2]] |
| Subir a mi fork | `git push origin main` | [[el-fork|GitHub · 2]] |
| Subir una branch por primera vez | `git push -u origin <nombre>` | [[el-ritual-del-curso|GitHub · 5]] |
| Bajar y juntar de un jalón | `git pull` | [[el-fork|GitHub · 2]] |
| Poner mi fork al día desde el navegador | botón **Sync fork** | [[el-fork|GitHub · 2]] |
| …y después bajarlo a mi máquina | `git pull origin main` | [[el-fork|GitHub · 2]] |

:::

## Lo que no se sube

::: table {#git-cs-ignorar title="Basura y credenciales"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber por qué un archivo no aparece | `git check-ignore -v <archivo>` | [[lo-que-no-se-sube|Git · 4]] |
| Dejar de rastrear algo, sin borrarlo | `git rm --cached <archivo>` | [[lo-que-no-se-sube|Git · 4]] |
| Que una carpeta vacía exista | `touch <carpeta>/.gitkeep` | [[que-guarda-un-commit|Git · 3]] |

:::

Patrones útiles de `.gitignore`: `.DS_Store`, `__pycache__/`, `*.pyc`, `.env`, `node_modules/`, `.ipynb_checkpoints/`.

## Mensajes que vas a ver, y qué significan

::: table {#git-cs-errores title="Errores frecuentes"}

| Mensaje | Qué pasó | Qué haces |
|---|---|---|
| `nothing added to commit but untracked files present` | Git ve archivos que nunca ha guardado | `git add <ruta>` |
| `! [rejected] main -> main (fetch first)` | Tu copia está atrasada | `git pull`, resolver si hace falta, y `git push` |
| `! [rejected] ... (non-fast-forward)` | Lo mismo, después de un fetch | Igual que el anterior. Nunca `--force` |
| `Permission denied` o `403` al hacer push | Tu `origin` apunta al repositorio del curso | `git remote -v`, y arregla los remotes |
| `Permission denied (publickey)` | GitHub no reconoce tu llave | [[cuenta-y-llave|Apéndice]] |
| `CONFLICT (content): Merge conflict in ...` | Dos versiones de la misma línea | Edita, `git add`, `git commit`. O `git merge --abort` |
| `Your local changes would be overwritten` | Quieres cambiar de branch con trabajo sin guardar | `git commit` o `git stash` |
| `fatal: ambiguous argument 'HEAD~1'` | Estás en el primer commit, no hay padre | Nada que deshacer |
| `did not match any file(s) known to git` | El archivo nunca ha estado en un commit | `git restore` no aplica a untracked |

:::

## Las reglas del curso

1. `git status` antes y después de cada `git add`.
2. Nunca `git add .`.
3. Sólo escribes dentro de `estudiantes/tu-login/`.
4. Tu carpeta es un espejo de `codigo/`: misma ruta, mismo nombre.
5. Una branch por tarea, nacida de un `main` recién actualizado. Nunca entregues desde `main`.
6. Un pull request rechazado se corrige con `push` a la misma branch, no abriendo otro.
8. Todo se entrega por GitHub. No hay Canvas.
