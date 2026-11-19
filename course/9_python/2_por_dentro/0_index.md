---
id: python-por-dentro
title: "Python por dentro"
nav_title: "2. Python por dentro"
summary: "Qué hace Python cuando corre tu código, para pedirle bien a la IA y revisar lo que te entrega. Cinco síntomas de un script hecho con IA guían la clase."
status: ready
tags: [python, interprete, objetos, gil, ia, prompt, notebook]
---

# Python por dentro

**Sección 2** · 5 páginas y 1 anexo · unos 90 min · sesión del martes 6 de octubre, 19:00–20:30

Meta: saber qué hace Python cuando corre tu código, para pedirle bien a la IA y revisar lo que te entrega.

## En corto

- **La IA escribe la sintaxis; tú tienes que saber qué hace al correr.**
- **Cinco síntomas de un script hecho con IA guían la clase**: cada página explica uno.
- **El notebook se prepara antes de clase**: en clase no hay tiempo.

## Antes de clase: cuatro casillas

1. **Extensiones Python y Jupyter** de Microsoft en VS Code. Listo cuando aparecen en el panel de extensiones (Ctrl+Shift+X).
2. **El ritual** (más abajo: Paso 0 y El ritual). Listo cuando `uv sync` termina sin error.
3. **El kernel** (más abajo: Abre el notebook): el Python con el que el notebook corre sus celdas. Listo cuando el notebook muestra arriba a la derecha el `.venv` de `por_dentro`.
4. **Una celda corrida.** Escribe `1 + 1` en la celda 1.0 y córrela (Shift+Enter): sale `2` (luego la sobrescribes).

## Paso 0 · ¿dónde estás?

Abre tu fork en VS Code y, en su terminal:

```bash
git status
echo "$GHUSER"
```

**Qué hace cada pieza:**

- `git status` — dice en qué branch estás y si tienes cambios sin commit.
- `echo "$GHUSER"` — imprime tu usuario de GitHub, guardado en tu shell desde la unidad de Git. El ritual lo usa para armar la ruta de tu carpeta.

| Si `git status` dice… | Haces… |
|---|---|
| `On branch main` y nada que commitear | Sigue con el Haz 1 |
| `On branch main` con sólo archivos sin seguir (`Untracked files`) | Sigue con el Haz 1 |
| Otra branch, sin cambios (p. ej. `tarea-09-uv-docker`) | Sigue con el Haz 1 |
| Otra branch con cambios (p. ej. `tarea-09-uv-docker`) | Commit en **esa** branch primero; luego sigue |
| `On branch tarea-09-por-dentro` | **Ya hiciste el ritual: no lo repitas.** Salta al Haz 3 (primero `cd {tu_fork_de_la_clase}`) |

Si `echo "$GHUSER"` imprime una línea vacía, vuelve a guardarlo como en [[el-ritual-del-curso]] y abre una terminal nueva antes de seguir.

## El ritual, del Haz 1 al Haz 3

En los comandos, `{tu_fork_de_la_clase}` es la carpeta donde clonaste tu fork. Escribe la tuya, **sin las llaves**.

**Haz 1 · actualiza main:**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge --ff-only upstream/main
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — entras a tu fork.
- `git switch main` — te pones en tu branch `main`.
- `&&` — corre lo de la derecha sólo si lo de la izquierda salió bien.
- `git fetch upstream` — descarga lo nuevo de `upstream`, el repo del curso (lo agregaste en la unidad de Git), sin tocar tus archivos.
- `git merge --ff-only upstream/main` — avanza tu `main` hasta el del curso. `--ff-only` (*fast-forward only*) sólo lo hace si tu `main` no tiene commits propios.

**Deberías ver** `Fast-forward` y una lista de archivos, o `Already up to date.`

Si dice `Not possible to fast-forward`, **detente y pide ayuda**: tu `main` tiene commits que no son del curso, y seguir los mezclaría con tu entrega.

**Haz 2a · la branch de la entrega:**

```bash
[ -n "$GHUSER" ] && git switch -c tarea-09-por-dentro
```

**Qué hace cada pieza:**

- `[ -n "$GHUSER" ]` — comprueba que `$GHUSER` no está vacío (`-n`: no vacío). **Si está vacío, todo se detiene aquí**; sin esta prueba, la carpeta acabaría en `estudiantes/09_python/`, fuera de la tuya.
- `git switch -c tarea-09-por-dentro` — `-c` crea la branch de esta entrega y te cambia a ella. **Es la branch de toda la sección**: en ella haces la clase y la tarea, y ésa es la que subes el 13 de octubre con el curso, el ejercicio y el notebook terminado ([[entregas-por-dentro]]).

**Deberías ver:**

```text
Switched to a new branch 'tarea-09-por-dentro'
```

Si no sale nada y el comando terminó, `$GHUSER` estaba vacío: vuelve al paso 0.

**Haz 2b · copia y commit de la plantilla:**

```bash
[ -n "$GHUSER" ] && mkdir -p estudiantes/$GHUSER/09_python \
  && cp -r codigo/09_python/por_dentro estudiantes/$GHUSER/09_python/ \
  && git add estudiantes/$GHUSER/09_python/por_dentro \
  && git commit -m "unidad 09: plantilla de por_dentro"
```

**Qué hace cada pieza:**

- `[ -n "$GHUSER" ]` — la misma prueba del Haz 2a, para que este Haz tampoco escriba fuera de tu carpeta.
- `\` al final de una línea — dice «el comando sigue en la línea siguiente». Las cuatro líneas son un solo comando.
- `mkdir -p estudiantes/$GHUSER/09_python` — crea `09_python/` si no hiciste los labs de la 9.1; `-p` no falla si ya existe.
- `cp -r codigo/09_python/por_dentro estudiantes/$GHUSER/09_python/` — copia **la carpeta** `por_dentro` (`-r`: con todo lo que tiene adentro) dentro de tu `09_python/`. Por eso **no** lleva `/.` al final: con `/.` copiaría su contenido suelto en `09_python/`.
- `git add estudiantes/$GHUSER/09_python/por_dentro` — prepara sólo esa carpeta, nunca `09_python` entero: ahí también vive tu entrega de uv y Docker.
- `git commit -m "…"` — guarda la plantilla ya, antes de tocarla. Así tu pull request muestra después sólo lo que tú cambiaste.

**Deberías ver:**

```text
[tarea-09-por-dentro 98a9d59] unidad 09: plantilla de por_dentro
 13 files changed, 2865 insertions(+)
 create mode 100644 estudiantes/ana/09_python/por_dentro/.python-version
 create mode 100644 estudiantes/ana/09_python/por_dentro/certificado.md
 create mode 100644 estudiantes/ana/09_python/por_dentro/gil.py
 …
```

- En lugar de `ana` verás tu usuario; el número `98a9d59` es otro en tu máquina, y la cifra de `insertions` puede variar si la plantilla cambió.

**Haz 3 · el ambiente:**

```bash
cd estudiantes/$GHUSER/09_python/por_dentro && uv sync
```

**Qué hace cada pieza:**

- `cd estudiantes/$GHUSER/09_python/por_dentro` — entras a tu copia de la plantilla. Desde aquí corres todo lo de esta sección.
- `uv sync` — crea `.venv/` e instala lo que fija `uv.lock` (la sección 1 lo explica en [[ambientes-python]]).

**Deberías ver:**

```text
Using CPython 3.14.0
Creating virtual environment at: .venv
Resolved 34 packages in 0.91ms
Installed 29 packages in 263ms
 + asttokens==3.0.2
 …
 + ipykernel==7.4.0
 …
```

- En `3.14.0`, el último número puede ser otro. La primera vez, uv descarga antes Python 3.14: tarda un minuto.
- `ipykernel` es el paquete que deja a VS Code usar este `.venv` como kernel. **No corras `uv add ipykernel`: ya viene.**

## Abre el notebook

Desde `por_dentro/`, escribe `code .`: VS Code abre **esa carpeta**. Luego `por_dentro.ipynb` → *Select Kernel* → *Python Environments* → `.venv`.

Abrir `por_dentro/` como carpeta, y no el fork entero, hace que VS Code encuentre el `.venv` sin buscarlo cuatro niveles abajo.

> [!WARNING]
> `09_python/` ya tiene tu entrega de uv y Docker. Son **dos branches y dos pull requests**: en esta branch sólo se sube `09_python/por_dentro/`. Si cambias a otra branch y ves `por_dentro/` con sólo `.venv/` y `__pycache__/` adentro, es normal: lo ignorado por git no se va al cambiar de branch.

## Dónde corre tu notebook, y cómo encuentra `trabajo.py`

El kernel del notebook corre en una carpeta: la **carpeta de trabajo**. Es el `pwd` de Python, y VS Code la pone en la carpeta donde está el notebook: `por_dentro/`. Todo lo que una celda nombra **sin ruta** —`trabajo.py`, `revisa_esto.py`, `ventas.csv`— se busca ahí.

**Haz (celda 0.0):** antes de cualquier otra celda.

```python
import os
print(os.getcwd())
print(sorted(os.listdir()))
```

**Qué hace cada línea:**

- `import os` — trae el módulo que habla con el sistema operativo.
- `os.getcwd()` — la carpeta de trabajo (*get current working directory*): lo mismo que `pwd` en la terminal.
- `sorted(os.listdir())` — los archivos de esa carpeta, en orden alfabético.

**Deberías ver:** una ruta que termina en `09_python/por_dentro`, y en la lista `trabajo.py`, `revisa_esto.py` y `ventas.csv`.

```text
…/estudiantes/ana/09_python/por_dentro
['.python-version', '.venv', 'certificado.md', 'gil.py', 'por_dentro.ipynb', 'prompt.md', 'puntaje.py', 'pyproject.toml', 'resume_ventas.py', 'revisa_esto.py', 'revision.md', 'trabajo.py', 'uv.lock', 'ventas.csv']
```

**Cómo funciona `from trabajo import calcula`.** Python recorre una lista de carpetas, `sys.path`, en orden, y usa el primer `trabajo.py` que encuentra. En el kernel esa lista trae la librería estándar, luego la carpeta de trabajo (en `sys.path` aparece como `''`, «aquí») y luego los paquetes del `.venv/`. `trabajo.py` sólo está en la carpeta de trabajo: si ésa no es `por_dentro/`, Python no lo encuentra.

::: figure {#py-import title="Dónde busca Python lo que importas"}
![Arriba, la celda from trabajo import calcula. Debajo, dos columnas con las carpetas de sys.path en el orden en que Python las recorre. Izquierda, el kernel corre en por_dentro: la librería estándar no tiene trabajo.py, la carpeta de trabajo sí y gana. Derecha, el kernel corre en la raíz del fork: ninguna de las tres carpetas lo tiene y sale ModuleNotFoundError. Al pie: os.getcwd dice cuál es la carpeta de trabajo, y un nombre sin ruta se busca ahí.](../_assets/py-import.svg)
:::

**Si algo falla en el notebook**, corre primero la celda 0.0: casi siempre la carpeta de trabajo es otra.

| Ves… | Por qué | Haces… |
|---|---|---|
| `ModuleNotFoundError: No module named 'trabajo'` | La carpeta de trabajo no es `por_dentro/`, o `trabajo.py` no está ahí | Celda 0.0: ¿la ruta termina en `por_dentro`? ¿La lista trae `trabajo.py`? |
| `can't open file '…/revisa_esto.py'` | Lo mismo: el nombre sin ruta se busca en la carpeta de trabajo | Celda 0.0 |
| La lista de la celda 0.0 no trae `trabajo.py`, pero la ruta sí es `por_dentro` | Copiaste la plantilla antes de la actualización | La sección «Si hiciste el ritual antes…», abajo |
| Cambiaste `trabajo.py` y el notebook sigue usando la versión vieja | Python importa un módulo una sola vez por kernel | *Restart* del kernel (barra de arriba del notebook) y vuelve a correr las celdas |

Si la ruta de la celda 0.0 no es `por_dentro`, cámbiala desde el notebook.

**Haz (celda 0.0, debajo de lo anterior):** con la ruta que te da `pwd` en la terminal, dentro de tu carpeta `por_dentro/`.

```python
os.chdir("{ruta_de_tu_por_dentro}")
print(os.getcwd())
```

**Qué hace cada línea:**

- `os.chdir("…")` — cambia la carpeta de trabajo del kernel (*change directory*): lo mismo que `cd` en la terminal. Escribe tu ruta, sin las llaves.
- `print(os.getcwd())` — confirma el cambio.

**Deberías ver:** la ruta que termina en `09_python/por_dentro`. Desde ahí `from trabajo import calcula` funciona, sin reiniciar el kernel. Para no volver a hacerlo, abre VS Code dentro de `por_dentro/` (`code .`, como en «Abre el notebook»).

**Tres cosas más, para cuando algo no cuadra:**

**Haz (celda 0.0, debajo de lo anterior):** verifica **qué** `trabajo.py` usó Python.

```python
import trabajo
print(trabajo.__file__)
```

**Qué hace cada línea:**

- `import trabajo` — importa el módulo completo, no sólo una función.
- `trabajo.__file__` — la ruta del archivo de donde salió. Si no es el de tu `por_dentro/`, estás usando otro.

**Deberías ver:**

```text
…/estudiantes/ana/09_python/por_dentro/trabajo.py
```

**Haz (celda 0.0, debajo de lo anterior):** dile a Python dónde buscar, sin cambiar la carpeta de trabajo.

```python
import sys
sys.path.insert(0, "{ruta_de_tu_por_dentro}")
```

**Qué hace cada línea:**

- `sys.path.insert(0, "…")` — pone tu carpeta al **principio** de la lista donde Python busca módulos. Escribe tu ruta, sin las llaves.

**Deberías ver:** nada; desde ahí `from trabajo import calcula` funciona. **Sólo arregla los `import`**: `revisa_esto.py` y `ventas.csv` se siguen buscando en la carpeta de trabajo. Por eso el arreglo completo es `os.chdir`.

**Haz (celda 0.0, debajo de lo anterior):** fuerza a Python a volver a leer `trabajo.py` después de cambiarlo, sin reiniciar el kernel.

```python
import importlib
importlib.reload(trabajo)
from trabajo import calcula
```

**Qué hace cada línea:**

- `importlib.reload(trabajo)` — vuelve a leer el archivo; sin esto, el kernel sigue con la versión que importó la primera vez.
- `from trabajo import calcula` — vuelve a tomar `calcula` del módulo recién leído: el nombre viejo apuntaba a la función vieja.

**Deberías ver:** nada; desde ahí `calcula` es la versión nueva. Si dudas, *Restart* del kernel hace lo mismo y más.

## Si algo sale mal

| Ves… | Por qué | Haces… |
|---|---|---|
| `No interpreter found for Python 3.14` | Tu uv no descarga Pythons solo | `uv python install 3.14` y repite el Haz 3 |
| `warning: VIRTUAL_ENV=… does not match the project environment` | Tienes activado otro ambiente | `deactivate`; el aviso no rompe nada |
| El `.venv` no aparece en *Select Kernel* | VS Code no lo encontró | Recarga la lista; si no, *Select Another Kernel* → *Python Environments* → *Enter interpreter path* → `.venv/bin/python` |
| `nothing to commit` en el Haz 2b | La plantilla ya estaba en tu branch | Sigue con el Haz 3 |
| `fatal: a branch named 'tarea-09-por-dentro' already exists` | Ya empezaste esta entrega | `git switch tarea-09-por-dentro` y sigue con el Haz 3 |
| `'upstream' does not appear to be a git repository` | Falta el remoto del curso | Agrégalo como en [[el-ritual-del-curso]] |

**Si hiciste el ritual antes de las 18:00 del 6 de octubre**, a tu copia le falta `trabajo.py` y tu notebook no trae las celdas 0.1, 3.1 a 3.4 ni 5.1. Tráelos del curso, sólo si tu notebook sigue vacío (este `cp` lo reemplaza):

**Haz (terminal, en tu fork, en la branch `tarea-09-por-dentro`):**

```bash
git fetch upstream && git merge upstream/main
cp codigo/09_python/por_dentro/trabajo.py codigo/09_python/por_dentro/por_dentro.ipynb estudiantes/$GHUSER/09_python/por_dentro/
```

**Qué hace cada pieza:**

- `git fetch upstream && git merge upstream/main` — trae a tu branch lo nuevo del curso, con `trabajo.py` y el notebook actualizado.
- `cp … trabajo.py … por_dentro.ipynb …/por_dentro/` — copia esos dos archivos a tu carpeta. Si ya pegaste código en tu notebook, copia sólo `trabajo.py` y agrega a mano las celdas que te falten.

**Deberías ver:** ninguna salida del `cp`; `ls estudiantes/$GHUSER/09_python/por_dentro` ya lista `trabajo.py`.

## Las páginas

| # | Página | Qué agrega | Min | Dónde |
|---:|---|---|---:|---|
| 1 | [[que-es-python]] | Cuándo descubre Python un error, y cómo un `except` lo esconde | 15 | clase + lectura |
| 2 | [[nombres-y-objetos]] | `=` no copia; qué cambia y qué no; el valor por defecto mutable | 15 | clase |
| 3 | [[el-gil]] | Qué es el GIL, cuándo estorba y qué usar en su lugar | 15 | clase + lectura |
| 4 | [[lo-que-escribe-la-ia]] | Truthiness y floats en clase; comprehensions, `zip` y encoding de lectura | 10 | clase + lectura |
| 5 | [[trabajar-con-ia]] | Pedir, leer y probar, con dos prompts y sus respuestas | 25 | clase |

## Los cinco síntomas

La clase arranca con todos corriendo `revisa_esto.py` desde el notebook.

**Haz (celda 0.1):**

```python
import sys
!{sys.executable} revisa_esto.py
```

**Qué hace cada línea:**

- `import sys` — trae el módulo que sabe qué Python corre el notebook.
- `!` — al inicio de una línea de celda, manda esa línea a la terminal en lugar de a Python.
- `{sys.executable}` — se cambia por la ruta del Python del kernel, el de tu `.venv/`: así el script corre con el mismo Python que el notebook.

**Deberías ver:** totales por región, clientes, puntajes y, al final, `La contabilidad NO cuadra`. Su salida tiene cinco cosas raras:

| # | Síntoma en la salida de `revisa_esto.py` | Dónde lo ves | Lo explica |
|---:|---|---|---|
| 1 | Una venta no aparece en el total, sin aviso | Carla Ríos no sale en `norte`, y no hay ningún mensaje de error | Página 1 |
| 2 | La segunda región lista clientes de la primera | `norte` lista a Fátima López y Gael Muñoz, que sólo compran en `centro` | Página 2 |
| 3 | «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido | `puntaje con hilos` y `puntaje sin hilos` (en la nuestra, 2.51 s y 1.76 s; cambian en cada corrida) | Página 3 |
| 4 | Un descuento de 0 se cobró como 5 % | Con una cuenta a mano (abajo) | Página 4 |
| 5 | La contabilidad está en centavos; comparar el total sin redondear con `==` falla | La última línea, `La contabilidad NO cuadra`; la seguiría diciendo aunque los montos fueran los correctos | Página 4 |

**La cuenta a mano del síntoma 4.** En `ventas.csv`, Beto Peña (`norte`) tiene descuento `0`:

- Sin descuento, su venta con IVA es 200.20 × 1.16 = 232.23.
- Ana Núñez, la otra venta de `norte` que sí aparece, da 104.50 con su descuento de 10 %.
- `norte` sin Carla debería dar 104.50 + 232.23 = 336.73. La salida dice 325.12.

**Lo que no cambia en el síntoma 3.** Tus segundos cambian con la carga de tu máquina; lo que no cambia es que 4 hilos no bajan a un cuarto el tiempo, y 4 procesos sí bajan (a menos de la mitad; página 3).

**El síntoma 5 no es sólo el `float`.** Ni `float` ni `Decimal` dan exactamente 2722.27 sin redondear: el total exacto, con `Decimal`, es 2722.270020. Lo que cuadra es el total redondeado a centavos.

Esta tabla dice **qué** se ve, no qué línea lo causa: encontrar la línea y la causa es la tarea.

## El anexo

| Anexo | Qué es | Cuándo lo abres | Min |
|---|---|---|---:|
| [[entregas-por-dentro]] | La entrega: DataCamp, `revision.md` y `prompt.md`, con branch y carpeta | Antes de entregar | 8 |
