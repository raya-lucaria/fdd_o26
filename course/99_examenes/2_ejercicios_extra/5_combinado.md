---
id: ejercicio-combinado
title: "Ejercicio combinado: Git, bash y Docker"
nav_title: "Combinado: Git, bash y Docker"
summary: "Un repo con un script de bash, un Dockerfile y datos; tres ramas que entran por fast-forward, por commit de merge y con conflicto; y builds cuyo resultado depende de qué se mezcló. Cada pregunta con su respuesta explicada debajo."
status: ready
estimated_time: 45m
tags: [ejercicios, git, merge, conflictos, bash, docker]
prerequisites: [ejercicios-github, ejercicios-docker]
---

# Ejercicio combinado: Git, bash y Docker

**[PDF sin respuestas, para imprimir](../_assets/practica-combinada.pdf)** · unos 45 minutos · sin apuntes

En los parciales cada herramienta se preguntó sola. Aquí van juntas: el script vive en Git, el Dockerfile lo copia, y lo que imprime el contenedor depende de qué ramas mezclaste y de qué había en tu disco al construir. Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado. Todo se comprobó corriendo el escenario completo con Git 2.34, bash 5.2 y Docker 29.6.

La idea que atraviesa el ejercicio: **Git, bash y Docker no se avisan entre sí**. Git guarda commits, `docker build` copia lo que hay en tu disco, y bash corre lo que le den.

## El repo

`reporte/` cuenta ventas. En `main` hay un solo commit, **B**, con esto:

```text
reporte/          ← estás aquí
├── Dockerfile
├── contar.sh
└── datos/
    └── ventas.csv
```

`contar.sh`, con sus números de línea:

```text
1  archivo="$1"
2  if [[ ! -f "$archivo" ]]; then
3      printf 'no existe: %s\n' "$archivo" >&2
4      exit 1
5  fi
6  printf 'filas: %s\n' "$(wc -l < "$archivo")"
```

`Dockerfile` (la imagen `bash:5.2` es Alpine con bash instalado):

```dockerfile
FROM bash:5.2
WORKDIR /r
COPY contar.sh .
CMD ["bash", "contar.sh", "datos/ventas.csv"]
```

`datos/ventas.csv`, cuatro renglones:

```text
MX,10
US,5
MX,7
CA,3
```

Tres personas crearon una rama cada una, todas desde B, con un commit cada una:

```text
   +---F      filtro
   |
   +---T      titulo
   |
   +---I      imagen
   |
   B          main
```

| Rama | Commit | Qué cambia |
|---|---|---|
| `filtro` | F | `contar.sh`, línea 6: `wc -l < "$archivo"` pasa a `grep -c MX "$archivo"` |
| `titulo` | T | `contar.sh`, línea 6: `'filas: %s\n'` pasa a `'total: %s\n'` |
| `imagen` | I | `Dockerfile`: agrega `COPY datos/ datos/` después de `COPY contar.sh .` |

`grep -c MX` cuenta los renglones que contienen `MX`; `wc -l` cuenta todos.

## Parte 1 · Antes de mezclar nada

Estás en `main`, con B tal cual.

::: problem {#xc-1a title="a · El script en tu máquina"}
¿Qué imprime `bash contar.sh datos/ventas.csv`?
:::

::: hint {of="xc-1a"}
¿Cuántos renglones tiene el archivo, y qué cuenta `wc -l`?
:::

::: answer {of="xc-1a"}
**Respuesta:** imprime **`filas: 4`**.

**Por qué:**
1. `datos/ventas.csv` existe, así que la prueba de la línea 2 es falsa y el script no sale en la línea 4.
2. La línea 6 corre `wc -l < "$archivo"`, que cuenta los renglones del archivo.
3. El archivo tiene cuatro renglones: `MX,10`, `US,5`, `MX,7` y `CA,3`.
4. `printf` escribe `filas: ` seguido de ese número.

**La regla:** **`wc -l` cuenta todos los renglones, sin mirar qué dicen.**

**Compruébalo:** `wc -l datos/ventas.csv` → `4 datos/ventas.csv`
:::

::: problem {#xc-1b title="b · Un archivo que no existe"}
¿Qué imprime `bash contar.sh datos/mayo.csv`, y qué imprime justo después `echo $?`? ¿Por qué ese número?
:::

::: hint {of="xc-1b"}
Sigue el `if` de la línea 2. ¿Qué número le deja `exit` a `$?`?
:::

::: answer {of="xc-1b"}
**Respuesta:**
- `bash contar.sh datos/mayo.csv` imprime **`no existe: datos/mayo.csv`**.
- `echo $?` imprime **`1`**.
- **Es `1` porque el script terminó con `exit 1`**, y `$?` guarda el código de salida del último comando.

**Por qué:**
1. `datos/mayo.csv` no existe, así que `[[ ! -f "$archivo" ]]` es verdadero y bash entra al `if`.
2. La línea 3 escribe el mensaje en stderr (`>&2`). Stderr también sale en tu terminal.
3. La línea 4, `exit 1`, termina el script con código 1. La línea 6 nunca corre.
4. `echo $?` lee el código de salida del comando anterior, `bash contar.sh …`, que fue 1.

**La regla:** **`$?` es el código de salida del último comando: `0` significa que salió bien y cualquier otro número, que falló.**
:::

::: problem {#xc-1c title="c · La imagen sin datos"}
Corres `docker build -t rep:0 .` y luego `docker run --rm rep:0`. ¿Qué imprime, y por qué, si `datos/ventas.csv` sí existe en tu carpeta?
:::

::: hint {of="xc-1c"}
¿Qué copia el Dockerfile de B? ¿Ve un contenedor tu carpeta si nadie se la monta?
:::

::: answer {of="xc-1c"}
**Respuesta:** imprime **`no existe: datos/ventas.csv`**, porque **el archivo está en tu carpeta pero no dentro de la imagen**.

**Por qué:**
1. El Dockerfile de B sólo tiene `COPY contar.sh .`: la imagen `rep:0` trae el script en `/r` y nada más.
2. El `CMD` corre `bash contar.sh datos/ventas.csv` dentro de `/r`, el `WORKDIR`. Busca `/r/datos/ventas.csv`.
3. Ese archivo no existe dentro del contenedor. La prueba de la línea 2 es verdadera y el script sale con `exit 1`.
4. `docker run` devuelve el código del proceso tal cual: `echo $?` daría `1`.

**La regla:** **un contenedor sólo ve lo que trae la imagen y lo que le montes; tu carpeta no entra sola.**

**Error común:** pensar que, como corres `docker run` desde `reporte/`, el contenedor ve `reporte/`. La carpeta desde donde lanzas `docker run` no se monta en ningún lado.
:::

::: problem {#xc-1d title="d · Hazlo funcionar sin reconstruir"}
Escribe un `docker run` que haga funcionar `rep:0` sin reconstruir la imagen. ¿Qué imprime?
:::

::: hint {of="xc-1d"}
¿Dónde busca el `CMD` el archivo, si el `WORKDIR` es `/r`? Monta tu carpeta justo ahí.
:::

::: answer {of="xc-1d"}
**Respuesta:**

```bash
docker run --rm -v "$(pwd)/datos":/r/datos rep:0
```

Imprime **`filas: 4`**.

**Por qué:**
1. El `CMD` busca `datos/ventas.csv` relativo al `WORKDIR`, o sea `/r/datos/ventas.csv`.
2. `-v "$(pwd)/datos":/r/datos` pone tu carpeta `reporte/datos` dentro del contenedor en `/r/datos`.
3. Ahora `/r/datos/ventas.csv` existe y tiene tus cuatro renglones. El script de B los cuenta con `wc -l`.

**La regla:** **`-v ruta-en-tu-disco:ruta-en-el-contenedor` pone tu carpeta en esa ruta del contenedor; la ruta de la derecha debe ser donde el programa busca.**

También funciona `docker run --rm -v "$(pwd)":/r rep:0`: monta toda `reporte/` en `/r`, donde están el `contar.sh` y el `datos/` que busca el `CMD`. Imprime lo mismo, `filas: 4`.

**Error común:** escribir `-v datos:/r/datos`. Sin `/` ni `$(pwd)`, Docker entiende `datos` como un volumen con nombre `datos`, no como tu carpeta; aquí ese volumen está vacío, y el contenedor vuelve a imprimir `no existe: datos/ventas.csv`.
:::

**Repasa:** [[variables-comillas-y-salida]] y [[lab-con-volumen]].

## Parte 2 · La secuencia

Los comandos se corren **en orden**, todos desde `reporte/` y empezando en `main`. Cada fila parte de lo que dejó la anterior.

::: problem {#xc-2-1 title="Fila 1 · ¿Fast-forward o commit de merge?"}
```bash
git merge filtro
```
:::

::: hint {of="xc-2-1"}
Las tres ramas (`filtro`, `titulo`, `imagen`) están en tu clon, y las tres nacieron de B.

| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | B |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta todos los renglones (`wc -l`) |
| ¿El `Dockerfile` copia `datos/`? | No |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro |

¿`filtro` nació de la punta actual de `main`, o hay algo que juntar?
:::

::: answer {of="xc-2-1"}
**Respuesta:** **fast-forward.** `main` avanza de B a F y Git no crea ningún commit nuevo.

**Por qué:**
1. `main` apunta a B.
2. `filtro` apunta a F, y F es B más un commit.
3. Todo lo que tiene `main` ya está en `filtro`: no hay nada que juntar.
4. Git sólo mueve la etiqueta `main` de B a F y actualiza tu disco con la línea 6 de F.

**La regla:** **si la rama que mezclas ya contiene la punta de tu rama, el merge es fast-forward: Git sólo mueve la etiqueta y no crea commit de merge.**

**Cambia:** `main` pasa de B a F, y con él cambia la línea 6 de `contar.sh` en tu disco.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | B | **F** |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta todos los renglones (`wc -l`) | **`filas:` y cuenta los renglones con `MX` (`grep -c MX`)** |
| ¿El `Dockerfile` copia `datos/`? | No | No |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro | `rep:0`: sin `datos/` adentro |

**Compruébalo:**

```text
$ git merge filtro
Updating e788dc1..d0d102a
Fast-forward
 contar.sh | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

La palabra `Fast-forward` lo confirma. Los hashes cambian en cada máquina.
:::

::: problem {#xc-2-2 title="Fila 2 · ¿Y ahora? ¿Por qué es distinto?"}
```bash
git merge imagen
```
:::

::: hint {of="xc-2-2"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | F |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | No |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro |

¿`imagen` sigue colgando de la punta de `main`?
:::

::: answer {of="xc-2-2"}
**Respuesta:** **commit de merge, sin conflicto.** Es distinto porque ahora **las dos ramas tienen un commit que la otra no tiene**.

**Por qué:**
1. Después de la fila 1, `main` está en F.
2. `imagen` está en I, e I nació de B, no de F.
3. `main` tiene F, que `imagen` no tiene. `imagen` tiene I, que `main` no tiene.
4. Mover la etiqueta ya no basta: si `main` saltara a I, perdería F.
5. Git crea un commit nuevo con **dos padres**, F e I, que junta los dos cambios.
6. No hay conflicto: F cambió `contar.sh` e I cambió `Dockerfile`.

**La regla:** **si cada rama tiene commits que la otra no tiene, Git crea un commit de merge con dos padres. Sólo hay conflicto si las dos cambiaron las mismas líneas del mismo archivo.**

**Cambia:** `main` apunta a un commit de merge nuevo, y el `Dockerfile` ya copia `datos/`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | F | **un commit de merge nuevo, con padres F e I** |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | No | **Sí** |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro | `rep:0`: sin `datos/` adentro |

**Compruébalo:** Git abre el editor para el mensaje del merge; al cerrarlo aparece:

```text
$ git merge imagen
Merge made by the 'ort' strategy.
 Dockerfile | 1 +
 1 file changed, 1 insertion(+)
```

**Error común:** decir «fast-forward otra vez, porque `imagen` también salió de B». Lo que importa no es de dónde salió la rama, sino si contiene la punta **actual** de `main`, que ya es F.
:::

::: problem {#xc-2-3 title="Fila 3 · ¿Qué imprime el run?"}
```bash
docker build -t rep:1 .
docker run --rm rep:1
```
:::

::: hint {of="xc-2-3"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro |

¿Qué copia el `Dockerfile` de `main`, y qué cuenta la línea 6?
:::

::: answer {of="xc-2-3"}
**Respuesta:** imprime **`filas: 2`**.

**Por qué:**
1. `docker build` copia `contar.sh` de tu disco. Su línea 6 ya trae el `grep -c MX` de F.
2. El `Dockerfile` ya trae el `COPY datos/ datos/` de I, así que `rep:1` lleva `/r/datos/ventas.csv` adentro.
3. `grep -c MX` cuenta los renglones con `MX`: `MX,10` y `MX,7`. Son 2.
4. El texto sigue siendo `filas:`, porque T (el que cambia a `total:`) todavía no se mezcla.

**La regla:** **lo que imprime un contenedor depende de qué se mezcló antes del build: la imagen lleva el script y los datos de ese momento.**

**Cambia:** sólo la última imagen construida: ahora es `rep:1`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I | un commit de merge nuevo, con padres F e I |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:0`: sin `datos/` adentro | **`rep:1`: script con `filas:` y `grep -c MX`; `datos/` copiado en la fila 3, con 2 `MX`** |

**Compruébalo:**

```text
$ docker run --rm rep:1
filas: 2
$ grep -c MX datos/ventas.csv
2
```

**Error común:** contestar `total: 2`. La rama `titulo` todavía no entra a `main`.
:::

::: problem {#xc-2-4 title="Fila 4 · ¿Qué imprime cada run? (dos casillas)"}
```bash
echo "MX,1" >> datos/ventas.csv
docker run --rm rep:1
docker run --rm -v "$(pwd)/datos":/r/datos rep:1
```
:::

::: hint {of="xc-2-4"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit |
| `git status --short` | No muestra nada: el disco es igual al último commit |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 |

¿Cuándo se copiaron los datos a `rep:1`? ¿Qué tapa un montaje?
:::

::: answer {of="xc-2-4"}
**Respuesta:**
- El primer `docker run` (sin montaje) imprime **`filas: 2`**.
- El segundo `docker run` (con montaje) imprime **`filas: 3`**.

**Por qué:**
1. `echo "MX,1" >> datos/ventas.csv` agrega un renglón **a tu disco**. El archivo queda con 5 renglones, 3 con `MX`.
2. `rep:1` copió `datos/` en la fila 3, cuando había 2 `MX`. Cambiar tu disco después no cambia la imagen.
3. Sin montaje, el contenedor lee la copia de la imagen: `filas: 2`.
4. Con `-v "$(pwd)/datos":/r/datos`, tu carpeta tapa el `/r/datos` de la imagen. El contenedor lee tu archivo de ahora: `filas: 3`.
5. Para Git, `ventas.csv` ahora es distinto del último commit: queda modificado y **sin commit**.

**La regla:** **una imagen es una copia hecha en el momento del build; un montaje muestra tu disco tal como está al correr.**

**Cambia:** `datos/ventas.csv` en tu disco gana el `MX,1`, y `git status --short` lo marca con ` M`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I | un commit de merge nuevo, con padres F e I |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | 4 renglones, 2 con `MX`; igual que en el commit | **5 renglones, 3 con `MX`; el `MX,1` está sin commit** |
| `git status --short` | No muestra nada: el disco es igual al último commit | **` M datos/ventas.csv`** |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 | `rep:1`: script con `filas:` y `grep -c MX`; `datos/` copiado en la fila 3, con 2 `MX` |

**Compruébalo:**

```text
$ docker run --rm rep:1 cat datos/ventas.csv
MX,10
US,5
MX,7
CA,3
$ git status --short
 M datos/ventas.csv
```

El `MX,1` no aparece en ningún `git log`, pero cambia lo que pasa en las filas 5, 7, 8 y 10.

**Error común:** contestar `filas: 3` en el primero, como si la imagen leyera tu disco al correr.
:::

::: problem {#xc-2-5 title="Fila 5 · ¿Qué responde Git?"}
```bash
git merge titulo
```

¿Te deja intentarlo aunque `datos/ventas.csv` tiene un cambio sin commit?
:::

::: hint {of="xc-2-5"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | ` M datos/ventas.csv` |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 |

¿Qué línea cambió F, y cuál T? ¿Toca T el archivo de datos?
:::

::: answer {of="xc-2-5"}
**Respuesta:**
- Git responde con un **conflicto en `contar.sh`**.
- **Sí te deja intentarlo**: tu cambio en `datos/ventas.csv` no estorba.

**Por qué:**
1. `main` ya tiene la línea 6 de F (`filas:` con `grep -c MX`). T, que nació de B, cambió **la misma línea 6** a `total:` con `wc -l`.
2. Las dos versiones de la misma línea son distintas. Git no sabe cuál quieres y escribe las dos en el archivo, entre marcadores.
3. El merge queda **a medias**: `main` no se mueve hasta que tú hagas el commit.
4. Git sólo se niega a empezar un merge si éste tendría que reescribir un archivo con cambios sin commit. T no toca `datos/ventas.csv`, así que Git lo deja en paz y tu `MX,1` sigue ahí.

**La regla:** **hay conflicto cuando las dos ramas cambiaron las mismas líneas de forma distinta. Un archivo sin commit sólo bloquea el merge si el merge tiene que tocar ese archivo.**

**Cambia:** la línea 6 queda con marcadores de conflicto, el merge con `titulo` queda a medias y `git status --short` agrega `UU contar.sh`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | un commit de merge nuevo, con padres F e I | **el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias** |
| Línea 6 de `contar.sh` en tu disco | `filas:` y cuenta los renglones con `MX` (`grep -c MX`) | **marcadores de conflicto con las dos versiones** |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit | 5 renglones, 3 con `MX`; el `MX,1` está sin commit |
| `git status --short` | ` M datos/ventas.csv` | **`UU contar.sh` y ` M datos/ventas.csv`** |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 | `rep:1`: script con `filas:` y `grep -c MX`; `datos/` copiado en la fila 3, con 2 `MX` |

`UU` significa «en conflicto»; ` M`, modificado y sin agregar.

**Compruébalo:**

```text
$ git merge titulo
Auto-merging contar.sh
CONFLICT (content): Merge conflict in contar.sh
Automatic merge failed; fix conflicts and then commit the result.
$ git status --short
UU contar.sh
 M datos/ventas.csv
```

**Error común:** contestar que Git se niega por el ` M datos/ventas.csv`. Eso sólo pasa cuando la rama que mezclas cambia ese mismo archivo; entonces Git aborta con `Your local changes to the following files would be overwritten by merge`.
:::

::: problem {#xc-2-6 title="Fila 6 · ¿Cómo se ve el archivo? ¿Cuál lado es HEAD?"}
```bash
cat contar.sh
```

Escribe cómo se ven ahora las últimas líneas.
:::

::: hint {of="xc-2-6"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias |
| Línea 6 de `contar.sh` en tu disco | marcadores de conflicto con las dos versiones |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | `UU contar.sh` y ` M datos/ventas.csv` |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 |

Los marcadores son `<<<<<<<`, `=======` y `>>>>>>>`. ¿Qué rama es `HEAD`?
:::

::: answer {of="xc-2-6"}
**Respuesta:** las últimas líneas son:

```text
<<<<<<< HEAD
printf 'filas: %s\n' "$(grep -c MX "$archivo")"
=======
printf 'total: %s\n' "$(wc -l < "$archivo")"
>>>>>>> titulo
```

**El lado de arriba es `HEAD`**: la versión de `main`.

**Por qué:**
1. `HEAD` es el commit en el que estás parado. Estás en `main`, así que `HEAD` es la punta de `main`: el commit de merge de la fila 2.
2. Entre `<<<<<<< HEAD` y `=======` va la línea 6 de `HEAD`. Trae el `grep -c MX` de F, que entró en la fila 1.
3. Entre `=======` y `>>>>>>> titulo` va la línea 6 de T. T nació de B, así que conserva el `wc -l` de B y sólo cambió el texto a `total:`.
4. Las líneas 1 a 5 salen normales: nadie las cambió. Los marcadores empiezan donde estaba la línea 6.

**La regla:** **en un conflicto, el lado de arriba (`HEAD`) es la rama donde estás parado y el de abajo es la rama que estás mezclando.**

La tabla de estado no cambia: `cat` sólo lee.

**Error común:** escribir el lado de `titulo` como `total:` con `grep -c MX`. T nunca vio el `grep`: ese cambio vive en F, que está del lado de `HEAD`.
:::

::: problem {#xc-2-7 title="Fila 7 · ¿El build? ¿El run? ¿El código?"}
```bash
docker build -t rep:2 .
docker run --rm -v "$(pwd)/datos":/r/datos rep:2
echo $?
```
:::

::: hint {of="xc-2-7"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias |
| Línea 6 de `contar.sh` en tu disco | marcadores de conflicto con las dos versiones |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | `UU contar.sh` y ` M datos/ventas.csv` |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 |

¿Le importa a `COPY` lo que dice el archivo? ¿Cómo lee bash una línea que empieza con `<<<`?
:::

::: answer {of="xc-2-7"}
**Respuesta:**
- **El build termina bien.**
- **El run imprime este error de sintaxis de bash:**

```text
contar.sh: line 6: syntax error near unexpected token `<<<'
contar.sh: line 6: `<<<<<<< HEAD'
```

- **`echo $?` imprime `2`.**

**Por qué:**
1. `docker build` copia lo que hay en tu disco: el `contar.sh` con marcadores y tu `datos/` con el `MX,1`.
2. `COPY` copia bytes. No sabe qué es un marcador de conflicto, así que no se queja.
3. Al correr, bash lee las líneas 1 a 5 sin problema y llega a la línea 6, `<<<<<<< HEAD`.
4. Bash parte `<<<<<<<` en tres operadores de redirección: `<<<`, `<<<` y `<`.
5. Después del primer `<<<`, bash espera una palabra (el texto que se le pasa al comando). Encuentra otro `<<<`: eso es `syntax error near unexpected token` con `<<<` como token.
6. Bash sale con código `2` por el error de sintaxis, y `docker run` devuelve ese código tal cual.

**La regla:** **ni Git ni Docker impiden empaquetar un archivo a medio resolver; `COPY` copia sin leer, y sólo bash falla, cuando ya lo está corriendo.**

**Cambia:** sólo la última imagen construida: ahora es `rep:2`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias |
| Línea 6 de `contar.sh` en tu disco | marcadores de conflicto con las dos versiones | marcadores de conflicto con las dos versiones |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit | 5 renglones, 3 con `MX`; el `MX,1` está sin commit |
| `git status --short` | `UU contar.sh` y ` M datos/ventas.csv` | `UU contar.sh` y ` M datos/ventas.csv` |
| Última imagen construida | `rep:1`: script y `datos/` copiados de tu disco en el build de la fila 3 | **`rep:2`: script con marcadores; `datos/` copiado en la fila 7, con 3 `MX`** |

**Compruébalo:**

```text
$ docker run --rm -v "$(pwd)/datos":/r/datos rep:2
contar.sh: line 6: syntax error near unexpected token `<<<'
contar.sh: line 6: `<<<<<<< HEAD'
$ echo $?
2
```

`rep:2` también guardó tu `datos/` con el `MX,1`. Esto importa en la fila 9:

```text
$ docker run --rm rep:2 cat datos/ventas.csv
MX,10
US,5
MX,7
CA,3
MX,1
```

**Error común:** contestar que el build falla. `docker build` nunca corre el script; sólo lo copia.
:::

::: problem {#xc-2-8 title="Fila 8 · Resuelve quedándote con los dos cambios"}
```bash
# editas contar.sh y resuelves el conflicto
git add contar.sh
git commit
```

Escribe la línea 6 resuelta. ¿Qué muestra después `git status --short`?
:::

::: hint {of="xc-2-8"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias |
| Línea 6 de `contar.sh` en tu disco | marcadores de conflicto con las dos versiones |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | `UU contar.sh` y ` M datos/ventas.csv` |
| Última imagen construida | `rep:2`: script y `datos/` copiados de tu disco en el build de la fila 7 |

«Los dos cambios» es el texto de uno y el conteo del otro, en una sola línea. ¿Qué pasa con `ventas.csv` si sólo le haces `git add` a `contar.sh`?
:::

::: answer {of="xc-2-8"}
**Respuesta:**
- La línea 6 resuelta es:

```bash
printf 'total: %s\n' "$(grep -c MX "$archivo")"
```

- `git status --short` muestra **sólo ` M datos/ventas.csv`**.

**Por qué:**
1. El cambio de T es el texto: `filas:` pasa a `total:`.
2. El cambio de F es el conteo: `wc -l` pasa a `grep -c MX`.
3. Quedarte con los dos es una sola línea con `total:` y `grep -c MX`. Borras las tres líneas de marcadores y las dos versiones viejas.
4. `git add contar.sh` le dice a Git que el conflicto de ese archivo está resuelto. `UU contar.sh` desaparece.
5. `git commit` cierra el merge: crea un commit con dos padres, el merge de la fila 2 y T. `main` avanza a ese commit.
6. `datos/ventas.csv` no se agregó, así que no entra al commit. El `MX,1` sigue en tu disco, sin commit.

**La regla:** **en un merge con conflicto, `git add` marca un archivo como resuelto y `git commit` cierra el merge; lo que no agregaste se queda fuera del commit.**

**Cambia:** `main` avanza al segundo commit de merge, la línea 6 queda resuelta y `UU contar.sh` desaparece de `git status --short`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | el commit de merge de la fila 2 (padres F e I); el merge con `titulo` está a medias | **un commit de merge nuevo, con padres el merge de la fila 2 y T** |
| Línea 6 de `contar.sh` en tu disco | marcadores de conflicto con las dos versiones | **`total:` y cuenta los renglones con `MX` (`grep -c MX`)** |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit | 5 renglones, 3 con `MX`; el `MX,1` está sin commit |
| `git status --short` | `UU contar.sh` y ` M datos/ventas.csv` | **` M datos/ventas.csv`** |
| Última imagen construida | `rep:2`: script y `datos/` copiados de tu disco en el build de la fila 7 | `rep:2`: script con marcadores; `datos/` copiado en la fila 7, con 3 `MX` |

**Compruébalo:**

```text
$ git commit
[main 03d2014] Merge branch 'titulo'
$ git status --short
 M datos/ventas.csv
```

**Error común:** usar `git add .` o `git commit -a`. Los dos meterían también el `MX,1` en el commit de merge, un cambio que no tiene nada que ver con el conflicto.
:::

::: problem {#xc-2-9 title="Fila 9 · ¿Qué sale de la caché?"}
```bash
docker build -t rep:3 .
```
:::

::: hint {of="xc-2-9"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres el merge de la fila 2 y T |
| Línea 6 de `contar.sh` en tu disco | `total:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | ` M datos/ventas.csv` |
| Última imagen construida | `rep:2`: script y `datos/` copiados de tu disco en el build de la fila 7 |

Compara tu disco con el que había al construir `rep:2` en la fila 7. ¿Qué archivo es distinto?
:::

::: answer {of="xc-2-9"}
**Respuesta:** **`FROM` usa la imagen base ya descargada (BuildKit no lo marca `CACHED`); `WORKDIR` sale `CACHED`; los dos `COPY` se rehacen.**

**Por qué:**
1. Docker busca, paso por paso, una capa de **cualquier** build anterior que coincida: misma instrucción, mismas capas antes y, en un `COPY`, mismos archivos. El build más reciente con este `Dockerfile` es el de `rep:2`, en la fila 7.
2. `FROM bash:5.2` usa la imagen base, que ya está descargada. `WORKDIR /r` no cambió y nada antes de él cambió: sale `CACHED`.
3. `COPY contar.sh .` lee `contar.sh`. En la fila 7 tenía marcadores; ahora está resuelto. El archivo cambió: **se rehace**.
4. `COPY datos/ datos/` lee `datos/`, que es **idéntico** al de la fila 7: el `MX,1` ya estaba ahí cuando se construyó `rep:2`.
5. Aun así **se rehace**, sólo porque va después de una capa que se rehízo.

**La regla:** **Docker reutiliza una capa sólo si ni ella ni ninguna capa anterior cambió; en cuanto una capa se rehace, todas las que siguen se rehacen.**

| Paso del Dockerfile | ¿Caché o se rehace? | Por qué |
|---|---|---|
| `FROM bash:5.2` | Usa la base descargada (sin la palabra `CACHED`) | La imagen base ya está en tu máquina |
| `WORKDIR /r` | `CACHED` | No cambió, y nada antes de él cambió |
| `COPY contar.sh .` | **Se rehace** | `contar.sh` cambió: en `rep:2` tenía marcadores; ahora está resuelto |
| `COPY datos/ datos/` | **Se rehace** | Viene después de una capa que se rehízo. `datos/` es idéntico al de `rep:2` |

**Cambia:** sólo la última imagen construida: ahora es `rep:3`.

| Lugar | Antes de esta fila | Después de esta fila |
|---|---|---|
| `main` apunta a | un commit de merge nuevo, con padres el merge de la fila 2 y T | un commit de merge nuevo, con padres el merge de la fila 2 y T |
| Línea 6 de `contar.sh` en tu disco | `total:` y cuenta los renglones con `MX` (`grep -c MX`) | `total:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit | 5 renglones, 3 con `MX`; el `MX,1` está sin commit |
| `git status --short` | ` M datos/ventas.csv` | ` M datos/ventas.csv` |
| Última imagen construida | `rep:2`: script y `datos/` copiados de tu disco en el build de la fila 7 | **`rep:3`: script resuelto; `datos/` copiado en la fila 9, con 3 `MX` (idéntico al de `rep:2`)** |

**Compruébalo:** con `--progress=plain`, sólo `WORKDIR` dice `CACHED`:

```text
$ docker build --progress=plain -t rep:3 .
#6 [2/4] WORKDIR /r
#6 CACHED
#7 [3/4] COPY contar.sh .
#8 [4/4] COPY datos/ datos/
```

Prueba de que `datos/` no fue la causa: si vuelves a poner en disco el `contar.sh` con marcadores y construyes, los dos `COPY` salen `CACHED`.

**Error común:** decir que `COPY datos/` se rehace «porque agregaste el `MX,1`». El `MX,1` se agregó en la fila 4, antes de construir `rep:2`. Entre la fila 7 y la fila 9 sólo cambió `contar.sh`.
:::

::: problem {#xc-2-10 title="Fila 10 · ¿total: 2 o total: 3?"}
```bash
docker run --rm rep:3
```

¿Por qué, si el cambio de la fila 4 nunca se commiteó?
:::

::: hint {of="xc-2-10"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres el merge de la fila 2 y T |
| Línea 6 de `contar.sh` en tu disco | `total:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | ` M datos/ventas.csv` |
| Última imagen construida | `rep:3`: lo que había en tu disco en el build de la fila 9 |

¿De dónde copia `docker build`: del último commit o de tu disco?
:::

::: answer {of="xc-2-10"}
**Respuesta:**
- Imprime **`total: 3`**.
- **Porque `docker build` copia tu disco, no el último commit**, y el `MX,1` estaba en tu disco al construir `rep:3`.

**Por qué:**
1. `rep:3` tiene el script resuelto: `total:` con `grep -c MX`.
2. `rep:3` copió `datos/ventas.csv` de tu disco en la fila 9. Ese archivo tiene el `MX,1` sin commit: 3 renglones con `MX`.
3. `docker build` no le pregunta nada a Git. No sabe qué tiene commit y qué no.
4. El último commit de `main` tiene el `ventas.csv` de B, con 2 `MX`. Quien clone el repo y construya obtiene `total: 2`.

**La regla:** **`docker build` copia lo que hay en tu disco, no lo que hay en el último commit; una imagen puede llevar cambios que no están en Git.**

La tabla de estado no cambia: `docker run --rm` lee la imagen y no escribe en tu disco.

**Compruébalo:**

```text
$ docker run --rm rep:3
total: 3
$ git clone . ../clon && cd ../clon
$ docker build -t rep:clon . && docker run --rm rep:clon
total: 2
```

**Error común:** contestar `total: 2` pensando que la imagen sale del commit. Eso sólo es cierto para quien construye desde un clon limpio.
:::

::: problem {#xc-2-11 title="Fila 11 · ¿Cuántos commits de merge?"}
```bash
git log --oneline --graph
```

¿Cuántos commits de merge tiene `main`? ¿Por qué no hay uno para `filtro`?
:::

::: hint {of="xc-2-11"}
| Lugar | Antes de esta fila |
|---|---|
| `main` apunta a | un commit de merge nuevo, con padres el merge de la fila 2 y T |
| Línea 6 de `contar.sh` en tu disco | `total:` y cuenta los renglones con `MX` (`grep -c MX`) |
| ¿El `Dockerfile` copia `datos/`? | Sí |
| `datos/ventas.csv` en tu disco | los 4 renglones del commit más el `MX,1` de la fila 4, sin commit |
| `git status --short` | ` M datos/ventas.csv` |
| Última imagen construida | `rep:3`: lo que había en tu disco en el build de la fila 9 |

¿Cuál de los tres merges fue fast-forward?
:::

::: answer {of="xc-2-11"}
**Respuesta:**
- `main` tiene **dos** commits de merge: el de `imagen` (fila 2) y el de `titulo` (fila 8).
- **No hay uno para `filtro` porque entró por fast-forward** en la fila 1: Git sólo movió `main` de B a F.

**Por qué:**
1. Fila 1: `main` estaba en B y `filtro` era B más F. Git movió la etiqueta. F quedó en la línea de `main` como un commit normal, sin merge.
2. Fila 2: `main` (en F) e `imagen` (en I) tenían cada una un commit propio. Git creó el primer commit de merge, con padres F e I.
3. Fila 8: `main` (en ese merge) y `titulo` (en T) tenían cada una commits propios. Tu `git commit` creó el segundo commit de merge.

**La regla:** **un fast-forward no deja commit de merge en la historia; sólo los merges que juntan dos ramas con commits propios dejan un commit con dos padres.**

**Compruébalo:** cada commit lleva al lado su letra. Las flechas `<-` y las letras no las imprime Git:

```text
$ git log --oneline --graph
*   03d2014 Merge branch 'titulo'     <- merge de la fila 8 (padres: merge de la fila 2 y T)
|\
| * 0ab1acd titulo total              <- T
* |   251b255 Merge branch 'imagen'   <- merge de la fila 2 (padres: F e I)
|\ \
| * | d21d449 datos en la imagen      <- I
| |/
* / d0d102a solo MX                   <- F
|/
* e788dc1 base                        <- B
```

Los mensajes son los que usamos al crear los commits: «base» es B, «solo MX» es F, «datos en la imagen» es I y «titulo total» es T. Tus mensajes y hashes serán otros.

La tabla de estado no cambia: `git log` sólo lee.

**Error común:** contestar «tres, uno por rama». El fast-forward de la fila 1 no creó commit.
:::

**Repasa:** [[branches-y-merge]], [[capas-y-cache]] y [[rutas-en-docker]].

## Parte 3 · Las comillas

::: problem {#xc-3a title="a · Sin comillas dentro del script"}
Alguien le quita las comillas a la variable en la línea 6 del script ya resuelto: `grep -c MX $archivo`. Luego corre `bash contar.sh "datos/ventas mayo.csv"` sobre un archivo que sí existe con ese nombre. ¿Qué imprime? ¿Qué da `echo $?`? ¿Por qué ese número es peligroso?
:::

::: hint {of="xc-3a"}
Sin comillas, ¿qué hace bash con un espacio dentro del valor de una variable? ¿Cuál es el último comando que corre el script?
:::

::: answer {of="xc-3a"}
**Respuesta:**
- Imprime:

```text
grep: datos/ventas: No such file or directory
grep: mayo.csv: No such file or directory
total:
```

- `echo $?` da **`0`**.
- **Es peligroso porque `0` dice «todo salió bien»** aunque el conteo salió vacío. Un `&&` o un pipeline de datos sigue adelante con un `total:` sin número.

**Por qué:**
1. Al llamarlo con comillas, `$1` vale `datos/ventas mayo.csv`, con el espacio adentro.
2. La línea 2 usa `"$archivo"` con comillas: prueba el nombre completo, que sí existe, y el script sigue.
3. La línea 6 usa `$archivo` sin comillas. Bash parte el valor en el espacio y `grep` recibe **dos** nombres: `datos/ventas` y `mayo.csv`.
4. Ninguno de los dos existe. `grep` escribe los dos errores en stderr y no imprime ningún número.
5. `printf` imprime `total: ` seguido de nada, y termina bien.
6. `printf` es el último comando del script, así que el script sale con su código: `0`. El fallo de `grep` se pierde.

**La regla:** **sin comillas, bash parte el valor de una variable en cada espacio; y el código de salida de un script es el de su último comando.**

**Compruébalo:** el mismo resultado sale en tu máquina y dentro de `bash:5.2`, con `docker run --rm -v "$(pwd)":/w -w /w bash:5.2 bash contar.sh "datos/ventas mayo.csv"`.

**Error común:** pensar que `echo $?` da distinto de `0` porque `grep` falló. El código de `grep` se pierde dentro del `$( )`, y después corre `printf`.
:::

::: problem {#xc-3b title="b · Sin comillas al llamarlo"}
Con el script correcto, alguien corre `bash contar.sh datos/ventas mayo.csv`, sin comillas al llamarlo. ¿Qué imprime y por qué?
:::

::: hint {of="xc-3b"}
Sin comillas al llamarlo, ¿cuántos argumentos recibe el script? ¿Cuál mira?
:::

::: answer {of="xc-3b"}
**Respuesta:** imprime **`no existe: datos/ventas`**, porque **sin comillas el script recibe dos argumentos y sólo mira el primero**.

**Por qué:**
1. Bash parte la línea de comandos en los espacios: el script recibe `$1` = `datos/ventas` y `$2` = `mayo.csv`.
2. La línea 1 guarda sólo `$1` en `archivo`. `$2` se ignora.
3. `datos/ventas` no existe. La prueba de la línea 2 es verdadera, el script imprime el error y sale con `exit 1`.

**La regla:** **las comillas deciden cuántos argumentos llegan; hacen falta al llamar al script y también dentro del script.**
:::

::: problem {#xc-3c title="c · ¿Quién te avisó del conflicto?"}
En la parte 2, ¿qué herramienta te habría avisado del conflicto antes de construir la imagen de la fila 7: Git, bash o Docker? ¿Con qué comando?
:::

::: hint {of="xc-3c"}
¿Cuál de los tres avisó algo en la fila 5?
:::

::: answer {of="xc-3c"}
**Respuesta:** **Git.** Avisó al correr `git merge titulo` (fila 5) con el mensaje `CONFLICT`, y **`git status`** lo sigue avisando: marca `contar.sh` con `UU`.

**Por qué:**
1. Git es el único de los tres que sabe que hay un merge a medias.
2. Docker no lee el contenido: `COPY` copió el archivo con marcadores sin quejarse (fila 7).
3. Bash sí falla, pero sólo al correr el script, cuando la imagen rota ya existe.

**La regla:** **antes de construir, revisa `git status`: un `UU` significa que hay un conflicto sin resolver, y ni Docker ni bash te lo van a decir a tiempo.**
:::

**Repasa:** [[variables-comillas-y-salida]] y [[como-lee-bash]].
