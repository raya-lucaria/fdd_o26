---
id: cheatsheet-git
title: "Cheatsheet"
nav_title: "Cheatsheet"
summary: "Todos los comandos de la unidad en una sola página, agrupados por lo que quieres hacer, con el enlace a donde se explicó cada uno."
status: ready
estimated_time: 5m
tags: [git, github, referencia, comandos, cheatsheet]
prerequisites: [el-ritual-del-curso]
---

# Cheatsheet

**Apéndice** · para consultar, no para memorizar

Aquí sólo están los comandos que esta unidad enseñó. Si un comando no aparece, es a propósito: no lo necesitas todavía.

La única parte que sí se memoriza son los tres bloques de [[el-ritual-del-curso|El ritual]].

## Orientarte

::: table {#git-cs-orientar title="Antes de hacer nada"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber qué cambió y en qué zona está | `git status` | [[tu-primer-repositorio|Página 4]] |
| Ver la historia | `git log --oneline` | [[tu-primer-repositorio|Página 4]] |
| Ver lo que edité y no he apartado | `git diff` | [[tu-primer-repositorio|Página 4]] |
| Ver lo que sí va a entrar al commit | `git diff --staged` | [[tu-primer-repositorio|Página 4]] |
| Saber en qué branch estoy | `git branch` | [[branches-y-merge|Página 8]] |
| Saber a qué repositorios hablo | `git remote -v` | [[git-no-es-github|Página 9]] |

:::

## Guardar

::: table {#git-cs-guardar title="Las dos puertas"}

| Quiero | Comando | Dónde |
|---|---|---|
| Empezar un repositorio | `git init` | [[tu-primer-repositorio|Página 4]] |
| Apartar un archivo para el próximo commit | `git add <ruta>` | [[tu-primer-repositorio|Página 4]] |
| Guardar lo apartado | `git commit -m "mensaje"` | [[tu-primer-repositorio|Página 4]] |

:::

Nunca `git add .`. La regla es agregar una ruta que puedas nombrar y que acabes de ver en `git status`.

## Deshacer

::: table {#git-cs-deshacer title="Depende de dónde está el cambio"}

| El cambio está en | Quiero | Comando | Dónde |
|---|---|---|---|
| Working directory | Descartar la edición | `git restore <archivo>` | [[deshacer-en-git|Página 7]] |
| Staging area | Sacarlo sin perderlo | `git restore --staged <archivo>` | [[deshacer-en-git|Página 7]] |
| Último commit | Deshacerlo, conservar el trabajo | `git reset --soft HEAD~1` | [[deshacer-en-git|Página 7]] |
| Último commit | Deshacerlo y tirar el trabajo | `git reset --hard HEAD~1` | [[deshacer-en-git|Página 7]] |
| Estorba, lo quiero después | Apartarlo | `git stash` | [[deshacer-en-git|Página 7]] |
| Está en el stash | Traerlo de vuelta | `git stash pop` | [[deshacer-en-git|Página 7]] |
| Ya lo compartí | Deshacerlo sin reescribir | `git revert <hash>` | [[git-no-es-github|Página 9]] |
| Creí haberlo perdido | Buscarlo | `git reflog` | [[deshacer-en-git|Página 7]] |

:::

`git restore` es el único que borra sin red de seguridad. `reset` reescribe la historia; sobre algo ya compartido, usa `revert`.

## Branches

::: table {#git-cs-branches title="Trabajar en varias líneas"}

| Quiero | Comando | Dónde |
|---|---|---|
| Crear una branch y saltar a ella | `git switch -c <nombre>` | [[branches-y-merge|Página 8]] |
| Saltar a una que ya existe | `git switch <nombre>` | [[branches-y-merge|Página 8]] |
| Traer otra branch a la mía | `git merge <nombre>` | [[branches-y-merge|Página 8]] |
| Salir de un merge que se complicó | `git merge --abort` | [[branches-y-merge|Página 8]] |
| Borrar una branch ya mergeada | `git branch -d <nombre>` | [[branches-y-merge|Página 8]] |

:::

Para resolver un conflicto: edita el archivo hasta que no queden marcadores, `git add` al archivo, y `git commit`.

## Hablar con GitHub

::: table {#git-cs-github title="Los dos remotes"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber mi login exacto | `gh api user --jq .login` | [[git-no-es-github|Página 9]] |
| Bajar lo nuevo del curso | `git fetch upstream` | [[git-no-es-github|Página 9]] |
| Juntarlo con mi rama | `git merge upstream/main` | [[git-no-es-github|Página 9]] |
| Subir a mi fork | `git push origin main` | [[git-no-es-github|Página 9]] |
| Subir una branch por primera vez | `git push -u origin <nombre>` | [[el-ritual-del-curso|Página 12]] |
| Bajar y juntar de un jalón | `git pull` | [[dos-personas-un-archivo|Página 10]] |

:::

## Lo que no se sube

::: table {#git-cs-ignorar title="Basura y credenciales"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber por qué un archivo no aparece | `git check-ignore -v <archivo>` | [[lo-que-no-se-sube|Página 6]] |
| Dejar de rastrear algo, sin borrarlo | `git rm --cached <archivo>` | [[lo-que-no-se-sube|Página 6]] |
| Que una carpeta vacía exista | `touch <carpeta>/.gitkeep` | [[que-guarda-un-commit|Página 5]] |

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
| `Permission denied (publickey)` | GitHub no reconoce tu llave | [[cuenta-y-llave|Página 1]] |
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
5. Una branch por tarea. Nunca entregues desde `main`.
6. Un pull request rechazado se corrige con `push` a la misma branch, no abriendo otro.
