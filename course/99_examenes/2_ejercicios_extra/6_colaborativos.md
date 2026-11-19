---
id: ejercicios-colaborativos
title: "Ejercicios colaborativos: GitHub y Docker en equipo"
nav_title: "Colaborativos: GitHub y Docker"
summary: "Dos ejercicios largos donde tres personas trabajan el mismo repositorio a la vez: pushes rechazados, conflictos, merges limpios que rompen, y lo que eso le hace a cada imagen, contenedor y volumen. Con pista y respuesta plegadas."
status: ready
estimated_time: 90m
tags: [ejercicios, git, github, merge, conflictos, docker, volumenes, postgres, equipo]
prerequisites: [ejercicios-github, ejercicios-docker]
---

# Ejercicios colaborativos: GitHub y Docker en equipo

**[PDF sin respuestas, para imprimir](../_assets/practica-colaborativos.pdf)** · unos 90 minutos · sin apuntes

En los parciales, una sola persona cambiaba un archivo y seguías qué pasaba. Aquí trabajan **tres a la vez**: Ana, Beto y Caro. Cada quien tiene su clon, su máquina, sus imágenes, sus contenedores y sus volúmenes. Los cambios llegan de una máquina a otra **sólo** a través de GitHub, con `push` y `pull`.

Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado.

Los dos escenarios se reprodujeron completos: un repositorio local hizo de GitHub, hubo tres clones, y cada comando corrió con Git 2.34 y Docker 29.6. Las salidas que ves son las reales.

**Cómo leerlos.** Cada fila dice quién actúa y en qué orden; cada fila parte de lo que dejaron las anteriores. Las preguntas usan sólo comandos que ya viste en los parciales. Al final de cada ejercicio no se piden comandos: se pregunta **qué práctica** lo habría evitado.

**Una diferencia con el curso.** Aquí el equipo comparte **un solo repositorio** donde los tres pueden escribir, como en un proyecto de trabajo. En el curso cada quien tiene su fork y propone por pull request. Con un repositorio compartido aparece algo que con forks casi no pasa: dos personas empujando a la misma rama.

## Ejercicio 1 · El umbral

### El punto de partida

El equipo mantiene `alertas/`, un servicio que imprime el umbral con el que filtra. En GitHub, `main` tiene un solo commit, **B**:

```text
alertas/
├── Dockerfile
├── alerta.sh
└── config.env
```

`config.env`:

```text
UMBRAL=5
```

`alerta.sh` carga ese archivo e imprime el valor:

```bash
. ./config.env
echo "umbral: $UMBRAL"
```

`Dockerfile`: la configuración se **copia dentro de la imagen**.

```dockerfile
FROM alpine:3.20
WORKDIR /app
COPY config.env alerta.sh ./
CMD ["sh", "alerta.sh"]
```

Los tres ya clonaron el repositorio y, cada uno en su máquina, corrieron:

```bash
docker build -t alertas:1 .
docker run -d --name alerta alertas:1 sleep 600
```

Así que cada quien tiene una imagen `alertas:1` y un contenedor `alerta` encendido, los dos con `UMBRAL=5`. Ningún `sleep 600` termina durante el ejercicio.

### La secuencia

::: problem {#xco1-1 title="Fila 1 · Ana cambia y sube"}
```bash
# Ana
echo "UMBRAL=10" > config.env
git commit -am "umbral 10"
git push origin main
docker run --rm alertas:1
```

¿Qué `UMBRAL` hay ahora en GitHub, en el clon de Beto y en la imagen de Ana? ¿Qué imprime el `docker run` de Ana?
:::

::: hint {of="xco1-1"}
Estado antes de la fila 1. Cada columna es una máquina; GitHub sólo guarda commits:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | `B` | `B` | `B` | `B` |
| `config.env` | el de `B` | el de `B` | el de `B` | el de `B` |
| Imagen `alertas:1` | no hay | construida al inicio desde `B` | construida al inicio desde `B` | construida al inicio desde `B` |

Un `push` cambia GitHub. ¿Qué celda cambia con un `docker build`, y lo corrió Ana?
:::

::: answer {of="xco1-1"}
**Respuesta:**

- En GitHub: **`UMBRAL=10`**.
- En el clon de Beto: **`UMBRAL=5`**.
- En la imagen de Ana: **`UMBRAL=5`**.
- El `docker run` de Ana imprime **`umbral: 5`**.

**Por qué:**

1. Actúa Ana. `echo` cambia `config.env` en su disco y `git commit` guarda ese cambio en su `main` local como el commit «umbral 10».
2. `git push` copia «umbral 10» a GitHub. Ahora `main` en GitHub tiene `UMBRAL=10`.
3. El push no llega a las máquinas de Beto ni de Caro: en sus discos sigue `UMBRAL=5`. Lo recibirán cuando ellos hagan `pull`.
4. Ana no corrió `docker build`. Su imagen `alertas:1` sigue siendo la que construyó al inicio, desde `B`, con `UMBRAL=5` copiado adentro.
5. `docker run --rm alertas:1` crea un contenedor de esa imagen vieja: imprime 5.

**La regla:** **los cambios sólo viajan entre máquinas por `push` y `pull`, y la imagen sólo cambia con `docker build`.** Ni `commit` ni `push` reconstruyen nada.

Estado después de la fila 1:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | **«umbral 10»** | **«umbral 10»** | `B` | `B` |
| `config.env` | **`UMBRAL=10`** | **`UMBRAL=10`** | `UMBRAL=5` | `UMBRAL=5` |
| Imagen `alertas:1` | no hay | construida al inicio desde `B`: `UMBRAL=5` | construida al inicio desde `B`: `UMBRAL=5` | construida al inicio desde `B`: `UMBRAL=5` |

Los tres contenedores `alerta` nacieron al inicio de la imagen de `B`, con `UMBRAL=5`. Ninguna fila los borra ni los recrea, hasta el final (fila 9): por eso las tablas no los muestran.

**Compruébalo:** `docker run --rm alertas:1` → `umbral: 5`. En el clon de Beto, `cat config.env` → `UMBRAL=5`.

**Error común:** responder que la imagen de Ana ya tiene 10 «porque Ana ya subió el cambio». Subir mueve commits a GitHub; la imagen es otra copia, y nadie la reconstruyó.
:::

::: problem {#xco1-2 title="Fila 2 · Ana reconstruye"}
```bash
# Ana
docker build -t alertas:1 .
docker run --rm alertas:1
docker exec alerta sh alerta.sh
```

¿Qué imprime el run? ¿Y el exec?
:::

::: hint {of="xco1-2"}
Estado antes de la fila 2:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | `B` | `B` |
| `config.env` | el de «umbral 10» | el de «umbral 10» | el de `B` | el de `B` |
| Imagen `alertas:1` | no hay | construida al inicio desde `B` | construida al inicio desde `B` | construida al inicio desde `B` |

¿De qué imagen nace el contenedor del `run`? ¿Y de cuál nació `alerta`?
:::

::: answer {of="xco1-2"}
**Respuesta:**

- El `docker run` imprime **`umbral: 10`**.
- El `docker exec` imprime **`umbral: 5`**.

**Por qué:**

1. Actúa Ana, sólo en su máquina. `docker build` copia el `config.env` de **su disco**, que desde la fila 1 dice `UMBRAL=10`. La etiqueta `alertas:1` pasa a apuntar a esa imagen nueva.
2. `docker run --rm alertas:1` crea un contenedor **nuevo** de la imagen nueva: imprime 10.
3. `docker exec alerta ...` no crea nada: entra al contenedor `alerta`, que existe desde el inicio y nació de la imagen construida desde `B`. Su copia de `config.env` dice 5.
4. En las máquinas de Beto y Caro no cambia nada: Docker no sube imágenes a GitHub, y nadie más corrió `build`.

**La regla:** **un contenedor se queda con la imagen de la que nació.** Reconstruir la imagen no toca los contenedores que ya existen; para usar la imagen nueva hay que borrar el contenedor y crear otro.

Estado después de la fila 2:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | `B` | `B` |
| `config.env` | `UMBRAL=10` | `UMBRAL=10` | `UMBRAL=5` | `UMBRAL=5` |
| Imagen `alertas:1` | no hay | **reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10`** | construida al inicio desde `B`: `UMBRAL=5` | construida al inicio desde `B`: `UMBRAL=5` |

Ana tiene ahora en su máquina dos versiones a la vez: su imagen dice 10 y su contenedor `alerta` dice 5.

**Compruébalo:**

```text
$ docker run --rm alertas:1
umbral: 10
$ docker exec alerta sh alerta.sh
umbral: 5
```

**Error común:** pensar que `alerta` ve el 10 porque «la imagen `alertas:1` ya cambió». El nombre `alertas:1` ahora apunta a otra imagen, pero `alerta` sigue usando la imagen con la que nació.
:::

::: problem {#xco1-3 title="Fila 3 · Beto, sin haber hecho pull"}
```bash
# Beto
echo "UMBRAL=20" > config.env
git commit -am "umbral 20"
git push origin main
```

Git le contesta:

```text
 ! [rejected]        main -> main (fetch first)
hint: Updates were rejected because the remote contains work that you do
```

¿Por qué lo rechaza? ¿Qué `UMBRAL` hay en GitHub? Si ahora Beto corre `docker build -t alertas:1 .` y `docker run --rm alertas:1`, ¿qué imprime?
:::

::: hint {of="xco1-3"}
Estado antes de la fila 3:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | `B` | `B` |
| `config.env` | el que subió Ana en la fila 1 | el de «umbral 10» | el de `B` | el de `B` |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | construida al inicio desde `B` | construida al inicio desde `B` |

¿Qué commit tiene GitHub que Beto no tiene? ¿De dónde copia el `build`: de GitHub o del disco de Beto?
:::

::: answer {of="xco1-3"}
**Respuesta:**

- Git lo rechaza porque **GitHub tiene un commit que Beto no tiene**: «umbral 10», de Ana.
- En GitHub sigue **`UMBRAL=10`**.
- El build y el run de Beto imprimen **`umbral: 20`**.

**Por qué:**

1. Actúa Beto. No hizo `pull` desde el inicio, así que su `main` local sigue en `B` y no conoce «umbral 10».
2. `git commit` crea «umbral 20» encima de `B`. Ese commit existe sólo en la máquina de Beto.
3. `git push` pide a GitHub que su `main` apunte a «umbral 20». Pero el `main` de GitHub está en «umbral 10», que no está en la historia de Beto. Si GitHub aceptara, «umbral 10» desaparecería de `main`. Por eso responde `rejected (fetch first)`.
4. Un push rechazado no cambia nada en GitHub: sigue en «umbral 10», con `UMBRAL=10`. Ana y Caro tampoco ven nada.
5. `docker build` copia **el disco de Beto** (`UMBRAL=20`), no GitHub. El run imprime 20: Beto tiene una imagen con un valor que no está en GitHub ni en ninguna otra máquina.

Con `D` = «umbral 10» (Ana) y `V` = «umbral 20» (Beto), las dos historias salen de `B`:

```text
B---D      main en GitHub
 \
  V        main de Beto
```

**La regla:** **GitHub rechaza tu push si tiene commits que tú no tienes** (primero hay que traerlos con `pull` e integrarlos), y **`docker build` copia lo que hay en tu disco, no lo que hay en GitHub.**

Estado después de la fila 3:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | **«umbral 20», sólo en su máquina (el push fue rechazado)** | `B` |
| `config.env` | `UMBRAL=10` | `UMBRAL=10` | **`UMBRAL=20`** | `UMBRAL=5` |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10` | **reconstruida en la fila 3 desde su disco: `UMBRAL=20`** | construida al inicio desde `B`: `UMBRAL=5` |

**Compruébalo:** el push termina con código de salida 1; `git log --oneline --all --graph` en la máquina de Beto muestra sólo `umbral 20` y `B`, porque Beto no ha traído el commit de Ana. El run imprime `umbral: 20`.

**Error común:** creer que, como el push falló, la imagen de Beto «no cuenta». El build no depende del push: copia el disco, y en el disco está el 20.
:::

::: problem {#xco1-4 title="Fila 4 · Caro se pone al día"}
```bash
# Caro
git pull origin main
docker run --rm alertas:1
docker run --rm -v "$(pwd)/config.env":/app/config.env alertas:1
```

¿Qué hace el pull? ¿Qué imprime cada run?
:::

::: hint {of="xco1-4"}
Estado antes de la fila 4:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | «umbral 20», sólo en su máquina (el push fue rechazado) | `B` |
| `config.env` | el de «umbral 10» | el de «umbral 10» | el de «umbral 20» | el de `B` |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | reconstruida en la fila 3 desde su disco | construida al inicio desde `B` |

¿Tiene Caro commits que GitHub no tenga? ¿Qué celdas de Caro puede cambiar un `pull`, y cuáles no? ¿Qué tapa un montaje?
:::

::: answer {of="xco1-4"}
**Respuesta:**

- El pull es un **fast-forward**: el `main` de Caro avanza de `B` a «umbral 10» y su disco queda con `UMBRAL=10`.
- El primer run imprime **`umbral: 5`**.
- El segundo run, con montaje, imprime **`umbral: 10`**.

**Por qué:**

1. Actúa Caro. No tiene commits propios, así que su `main` no se separó del de GitHub: sólo está atrasado. Git mueve su `main` hacia adelante hasta «umbral 10». Eso es un fast-forward: no hay nada que mezclar.
2. El pull cambia **dos** cosas en la máquina de Caro: su último commit y su `config.env` en disco. No toca su imagen ni su contenedor `alerta`.
3. El primer run usa su imagen, construida al inicio desde `B`: imprime 5.
4. El segundo run monta `$(pwd)/config.env` (el del disco, con 10) encima de `/app/config.env`. El montaje tapa la copia que trae la imagen, así que el script lee 10.
5. Beto no recibe nada: su push sigue rechazado y su máquina sigue igual. GitHub tampoco cambia: un pull sólo trae.

**La regla:** **`pull` cambia tu disco, no tu imagen.** Un montaje con `-v` tapa el archivo de la imagen con el de tu disco.

Estado después de la fila 4:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | «umbral 20», sólo en su máquina (el push fue rechazado) | **«umbral 10»** |
| `config.env` | `UMBRAL=10` | `UMBRAL=10` | `UMBRAL=20` | **`UMBRAL=10`** |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10` | reconstruida en la fila 3 desde su disco: `UMBRAL=20` | construida al inicio desde `B`: `UMBRAL=5` |

Mismo commit en el disco, dos resultados distintos según **cómo** corre el contenedor.

**Compruébalo:** el pull de Caro imprime `Updating 079d37d..7624c31` y `Fast-forward`; los dos runs imprimen `umbral: 5` y `umbral: 10`.
:::

::: problem {#xco1-5 title="Fila 5 · Beto integra"}
```bash
# Beto
git pull origin main
```

Git contesta:

```text
CONFLICT (content): Merge conflict in config.env
Automatic merge failed; fix conflicts and then commit the result.
```

¿Cómo se ve ahora `config.env` en el disco de Beto? ¿Qué imprime `docker exec alerta sh alerta.sh`? ¿Y `docker run --rm alertas:1`?
:::

::: hint {of="xco1-5"}
Estado antes de la fila 5:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | «umbral 20», sólo en su máquina (el push fue rechazado) | «umbral 10» |
| `config.env` | el de «umbral 10» | el de «umbral 10» | el de «umbral 20» | el de «umbral 10» |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | la que Beto reconstruyó en la fila 3, desde su disco | construida al inicio desde `B` |

Los dos cambiaron la misma línea desde `B`. ¿Qué celdas toca un `pull`? ¿Cuáles se construyeron antes?
:::

::: answer {of="xco1-5"}
**Respuesta:**

- `config.env` queda en el disco de Beto **con marcadores de conflicto**: las dos versiones, la de Beto (20) y la de Ana (10).
- `docker exec alerta sh alerta.sh` imprime **`umbral: 5`**.
- `docker run --rm alertas:1` imprime **`umbral: 20`**.

**Por qué:**

1. Actúa Beto. `git pull` trae «umbral 10» de GitHub e intenta mezclarlo con su «umbral 20».
2. Los dos commits cambiaron **la misma línea** de `config.env` desde `B`. Git no puede elegir: escribe las dos versiones en el archivo y deja el merge sin terminar.
3. Sale un merge con marcadores, y no otra cosa, porque el curso configuró `git config --global pull.rebase false` ([[clonar-y-actualizar]]).
4. El exec entra a `alerta`, que nació al inicio de la imagen de `B`: imprime 5.
5. El run usa la imagen que Beto construyó en la fila 3 con su disco de entonces: imprime 20.
6. GitHub, Ana y Caro no cambian: el merge sin terminar sólo existe en la máquina de Beto.

El archivo en el disco de Beto (salida real):

```text
<<<<<<< HEAD
UMBRAL=20
=======
UMBRAL=10
>>>>>>> 7624c311a90082e87f22ea92fd5ed4d1037efa0b
```

| Parte del archivo | De dónde viene |
|---|---|
| Entre `<<<<<<< HEAD` y `=======` | El commit de Beto, «umbral 20» |
| Entre `=======` y `>>>>>>>` | Lo que llegó de GitHub: «umbral 10», de Ana |
| El texto después de `>>>>>>>` | El hash completo del commit «umbral 10» que trajo el pull: con `git pull origin main`, Git pone ese hash y no un nombre de rama |

`git log --oneline origin/main` muestra ese hash abreviado: `7624c31 umbral 10`. En tu máquina será otro, porque depende del autor y de la fecha del commit.

**La regla:** **Git compara líneas: si dos personas cambian la misma línea, hay conflicto, y el conflicto vive sólo en el disco.**

Estado después de la fila 5:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | **«umbral 20» y un merge sin terminar (conflicto en `config.env`)** | «umbral 10» |
| `config.env` | `UMBRAL=10` | `UMBRAL=10` | **con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`)** | `UMBRAL=10` |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10` | reconstruida en la fila 3 desde su disco: `UMBRAL=20` | construida al inicio desde `B`: `UMBRAL=5` |

**Compruébalo:** `git status --short` → `UU config.env`: el archivo tiene un conflicto sin resolver y el merge no se ha terminado.
:::

::: problem {#xco1-6 title="Fila 6 · Beto «termina»"}
```bash
# Beto
git add config.env
git commit -m "listo"
docker build -t alertas:1 .
docker run --rm alertas:1
echo $?
git push origin main
```

Beto no editó el archivo. ¿Git acepta el commit? ¿El build termina bien? ¿Qué imprime el run y qué da `echo $?`? ¿GitHub acepta el push?
:::

::: hint {of="xco1-6"}
Estado antes de la fila 6:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral 10» | «umbral 10» | «umbral 20» y un merge sin terminar (conflicto en `config.env`) | «umbral 10» |
| `config.env` | el de «umbral 10» | el de «umbral 10» | el del merge sin terminar | el de «umbral 10» |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | reconstruida en la fila 3 desde su disco | construida al inicio desde `B` |

¿Revisa `git add` el contenido del archivo? ¿Le importa a `COPY`? ¿Qué hace `sh` con una línea que empieza con `<<<`?
:::

::: answer {of="xco1-6"}
**Respuesta:**

- **Sí**, Git acepta el commit.
- **Sí**, el build termina bien.
- El run **truena** con `syntax error: unexpected redirection`, y `echo $?` da **2**.
- **Sí**, GitHub acepta el push.

**Por qué:**

1. Actúa Beto. `git add config.env` le dice a Git «este conflicto ya está resuelto». Git no abre el archivo para ver si quedaron marcadores.
2. `git commit` crea «listo», el commit de merge, con el archivo tal cual: con marcadores.
3. `docker build` copia el disco de Beto. `COPY` copia bytes sin leerlos, así que no falla.
4. Al correr, `sh` carga `config.env` y lee `<<<<<<< HEAD` como una redirección mal escrita: error de sintaxis y código de salida 2.
5. El push entra porque el `main` de Beto ya contiene «umbral 10». Subir no borra nada de GitHub, así que no hay rechazo.
6. Ana y Caro no cambian: el archivo roto les llegará cuando hagan `pull`.

Con `M` = «listo», la historia en la máquina de Beto y en GitHub:

```text
B---V---M      main de Beto y main en GitHub
 \     /
  D----
```

(`D` = «umbral 10» de Ana, `V` = «umbral 20» de Beto.)

**La regla:** **ni Git, ni `docker build`, ni GitHub revisan si el contenido funciona.** Sólo correrlo lo revela.

Estado después de la fila 6:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | **«listo» (el merge de Beto)** | «umbral 10» | **«listo» (el merge de Beto)** | «umbral 10» |
| `config.env` | **con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`)** | `UMBRAL=10` | con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`) | `UMBRAL=10` |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10` | **reconstruida en la fila 6 con los marcadores: truena** | construida al inicio desde `B`: `UMBRAL=5` |

**Compruébalo:**

```text
$ docker run --rm alertas:1
alerta.sh: ./config.env: line 1: syntax error: unexpected redirection
$ echo $?
2
```

**Error común:** pensar que Git o GitHub impiden subir un archivo con marcadores. No lo impiden. Beto vio dos señales, el `CONFLICT` de la fila 5 y su propio contenedor tronando antes del push, y pudo pedir una tercera: `git status`, que marcaba `UU config.env`.
:::

::: problem {#xco1-7 title="Fila 7 · Caro vuelve a ponerse al día"}
```bash
# Caro
git pull origin main
docker run --rm alertas:1
docker run --rm -v "$(pwd)/config.env":/app/config.env alertas:1
```

¿Qué hace el pull? ¿Qué imprime cada run?
:::

::: hint {of="xco1-7"}
Estado antes de la fila 7:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «listo» (el merge de Beto) | «umbral 10» | «listo» (el merge de Beto) | «umbral 10» |
| `config.env` | el de «listo» (el merge de Beto) | el de «umbral 10» | el de «listo» (el merge de Beto) | el de «umbral 10» |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | reconstruida en la fila 6 con los marcadores | construida al inicio desde `B` |

¿Tiene Caro commits propios? ¿Qué trae ahora `main` en `config.env`? ¿Qué copia usa cada run?
:::

::: answer {of="xco1-7"}
**Respuesta:**

- El pull es un **fast-forward**: el `main` de Caro avanza de «umbral 10» a «listo», y su disco recibe el `config.env` con marcadores.
- El primer run imprime **`umbral: 5`**.
- El segundo run, con montaje, **truena** con el mismo error de la fila 6 (código 2).

**Por qué:**

1. Actúa Caro. Sigue sin commits propios, así que Git sólo adelanta su `main`. No hay merge ni conflicto en su máquina.
2. El pull cambia su último commit y su `config.env` en disco. No toca su imagen ni su contenedor.
3. El primer run usa su imagen, construida al inicio desde `B`: imprime 5. Por eso **parece que todo funciona**.
4. El segundo run monta el `config.env` del disco, el que tiene marcadores: `sh` truena.
5. Caro no hizo nada mal. Recibió el archivo roto porque estaba en `main` de GitHub.
6. GitHub, Ana y Beto no cambian: un pull sólo trae, y sólo a quien lo corre.

**La regla:** **un `pull` te trae lo que haya en `main`, roto o no.** Si sólo pruebas con tu imagen vieja, no lo ves.

Estado después de la fila 7:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «listo» (el merge de Beto) | «umbral 10» | «listo» (el merge de Beto) | **«listo» (el merge de Beto)** |
| `config.env` | con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`) | `UMBRAL=10` | con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`) | **con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`)** |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10»: `UMBRAL=10` | reconstruida en la fila 6 con los marcadores: truena | construida al inicio desde `B`: `UMBRAL=5` |

**Compruébalo:** el pull imprime `Updating 7624c31..5d17583` y `Fast-forward`; el segundo run imprime `alerta.sh: ./config.env: line 1: syntax error: unexpected redirection`.

**Error común:** concluir que en la máquina de Caro está todo bien porque el primer run imprime 5. Ese run usa la imagen del inicio, no el código que acaba de traer. Si Caro reconstruye, su imagen también queda rota.
:::

::: problem {#xco1-8 title="Fila 8 · Ana lo arregla"}
El equipo acuerda un umbral de 15.

```bash
# Ana
git pull origin main
echo "UMBRAL=15" > config.env
git commit -am "umbral acordado 15"
git push origin main
docker build -t alertas:1 .
docker run --rm alertas:1
```

¿Cómo sale el pull? ¿Qué imprime el run?
:::

::: hint {of="xco1-8"}
Estado antes de la fila 8:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «listo» (el merge de Beto) | «umbral 10» | «listo» (el merge de Beto) | «listo» (el merge de Beto) |
| `config.env` | el de «listo» (el merge de Beto) | el de «umbral 10» | el de «listo» (el merge de Beto) | el de «listo» (el merge de Beto) |
| Imagen `alertas:1` | no hay | reconstruida en la fila 2 desde «umbral 10» | reconstruida en la fila 6 con los marcadores | construida al inicio desde `B` |

¿Tiene Ana commits que GitHub no tenga?
:::

::: answer {of="xco1-8"}
**Respuesta:**

- El pull es un **fast-forward**: Ana recibe «listo», con el archivo roto.
- El run imprime **`umbral: 15`**.

**Por qué:**

1. Actúa Ana. No tiene commits nuevos desde «umbral 10», que ya está en GitHub. Git sólo adelanta su `main` hasta «listo», y su disco recibe los marcadores.
2. `echo "UMBRAL=15" > config.env` reemplaza el archivo completo: los marcadores desaparecen.
3. `git commit` crea «umbral acordado 15» encima de «listo».
4. El push entra sin rechazo: Ana partió del último commit de GitHub, así que GitHub no tiene nada que ella no tenga. `main` en GitHub vuelve a estar sano.
5. `docker build` copia su disco (15), y el run imprime 15.
6. Beto y Caro siguen con los marcadores en su disco hasta que hagan `pull`. Ninguna imagen ni contenedor de ellos cambia.

**La regla:** **si haces `pull` justo antes de trabajar, tu push no choca:** GitHub no tiene commits que tú no tengas.

Estado después de la fila 8:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | **«umbral acordado 15»** | **«umbral acordado 15»** | «listo» (el merge de Beto) | «listo» (el merge de Beto) |
| `config.env` | **`UMBRAL=15`** | **`UMBRAL=15`** | con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`) | con marcadores de conflicto (`UMBRAL=20` y `UMBRAL=10`) |
| Imagen `alertas:1` | no hay | **reconstruida en la fila 8: `UMBRAL=15`** | reconstruida en la fila 6 con los marcadores: truena | construida al inicio desde `B`: `UMBRAL=5` |

**Compruébalo:** el pull imprime `Fast-forward`; el push imprime `5d17583..1606eb8  main -> main`; el run imprime `umbral: 15`.
:::

::: problem {#xco1-9 title="Fila 9 · La foto final"}
Nadie más hace nada. Llena la tabla con lo que dice cada lugar: un número, «marcadores» o «truena».

| Lugar | ¿Qué dice? |
|---|---|
| `main` en GitHub | |
| Disco de Ana | |
| Disco de Beto | |
| Disco de Caro | |
| Imagen de Ana | |
| Imagen de Beto | |
| Imagen de Caro | |
| Contenedor `alerta` de Ana | |
| Contenedor `alerta` de Beto | |
| Contenedor `alerta` de Caro | |
:::

::: hint {of="xco1-9"}
Estado antes de la fila 9 (nadie hace nada más, así que también es el final). La fila de `config.env` no está: es parte de la pregunta.

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «umbral acordado 15» | «umbral acordado 15» | «listo» (el merge de Beto) | «listo» (el merge de Beto) |
| Imagen `alertas:1` | no hay | reconstruida por Ana en la fila 8 | reconstruida por Beto en la fila 6 | construida al inicio, desde `B` |

Traduce cada celda: ¿qué decía el disco cuando se hizo cada build? ¿De qué imagen nació cada `alerta`?
:::

::: answer {of="xco1-9"}
**Respuesta:**

| Lugar | ¿Qué dice? | Por qué |
|---|---|---|
| `main` en GitHub | **15** | El último commit es el arreglo de Ana, fila 8 |
| Disco de Ana | **15** | Ana lo escribió en la fila 8 |
| Disco de Beto | **marcadores** | Beto no ha hecho pull desde su commit «listo» de la fila 6 |
| Disco de Caro | **marcadores** | El último pull de Caro fue el de la fila 7, antes del arreglo |
| Imagen de Ana | **15** | Ana la reconstruyó en la fila 8, con 15 en el disco |
| Imagen de Beto | **truena** | Beto la reconstruyó en la fila 6, con marcadores en el disco |
| Imagen de Caro | **5** | Caro nunca reconstruyó: es la del inicio, desde `B` |
| Contenedor `alerta` de Ana | **5** | Nació al inicio de la imagen de `B` y nadie lo recreó |
| Contenedor `alerta` de Beto | **5** | Igual: nació al inicio de la imagen de `B` |
| Contenedor `alerta` de Caro | **5** | Igual: nació al inicio de la imagen de `B` |

**Por qué:**

1. Nadie actúa en esta fila: el estado es el mismo que dejó la fila 8.
2. Cada disco cambia sólo con el último `pull` o la última edición de su dueño.
3. Cada imagen guarda el disco del momento en que se construyó.
4. Cada contenedor guarda la imagen de la que nació.

**La regla:** **entre GitHub y lo que imprime un contenedor hay tres copias (disco, imagen, contenedor), y cada una se actualiza por separado.**

Hay **cuatro respuestas distintas** para la misma variable: 15, 5, marcadores y truena. De todo lo que se puede **correr** (imágenes y contenedores), sólo la imagen de Ana da el 15 que hay en GitHub. Si Beto hace pull y reconstruye, su imagen dará 15, pero su contenedor `alerta` seguirá en 5 hasta que lo borre y cree otro.

**Compruébalo:** en el escenario reproducido, `docker exec alerta sh alerta.sh` imprime `umbral: 5` en las tres máquinas; `git show main:config.env` en GitHub imprime `UMBRAL=15`.
:::

### Diagnóstico y prácticas

Aquí no se piden comandos: se pide entender qué falló y qué costumbre del equipo lo habría evitado.

::: problem {#xco1-d1 title="D1 · ¿Dónde entró el error?"}
¿En qué fila entró el archivo roto a `main`? ¿Quién pudo detenerlo antes, y con qué señal?
:::

::: hint {of="xco1-d1"}
¿En qué fila aceptó GitHub un commit con marcadores? ¿Cuántos avisos vio Beto antes?
:::

::: answer {of="xco1-d1"}
**Respuesta:**

- El archivo roto entró a `main` **en la fila 6**, con el push de Beto.
- **Beto** pudo detenerlo: **vio dos señales** y **pudo pedir una tercera** antes del push.

**Por qué:**

| Señal | Fila | ¿La vio? | Qué decía |
|---|---|---|---|
| El mensaje de `git pull` | 5 | Sí, salió solo | `CONFLICT (content): Merge conflict in config.env` |
| Su propio contenedor | 6 | Sí, lo corrió él | Truena con código 2, **antes** del `git push` |
| `git status --short` | 5 | Sólo si lo pedía | `UU config.env`: conflicto sin resolver |

1. Cualquiera de las tres bastaba para no subir.
2. Nadie más pudo detenerlo: el equipo subía directo a `main`, sin una revisión en medio.
3. Git y GitHub no podían: no revisan el contenido de los archivos.

**La regla:** **resolver un conflicto es editar el archivo y probarlo; `git add` sólo lo marca como resuelto.**
:::

::: problem {#xco1-d2 title="D2 · ¿Por qué cada quien ve otra cosa?"}
Al final hay cuatro valores distintos de `UMBRAL` en el equipo. Explica las **tres** razones por las que una persona puede estar corriendo una versión distinta de la que hay en GitHub.
:::

::: hint {of="xco1-d2"}
¿Cuántas copias hay entre GitHub y lo que imprime un contenedor?
:::

::: answer {of="xco1-d2"}
**Respuesta:** entre GitHub y lo que imprime un contenedor hay **tres copias**, y cada una puede estar atrasada:

1. **El disco está viejo**: sólo cambia con `pull`. Si no lo haces, trabajas sobre lo viejo: los discos de Beto y Caro al final tienen marcadores mientras GitHub tiene 15.
2. **La imagen está vieja o es distinta**: sólo cambia con `docker build`, y copia **tu disco**, no GitHub. Con cambios sin subir, o con un archivo roto en el disco, tu imagen no es igual a la de nadie, como la de Beto en las filas 3 y 6.
3. **El contenedor está viejo**: se queda con la imagen de la que nació. Reconstruir no lo actualiza; hay que borrarlo y crear otro, como los tres `alerta` del final.

**Por qué:**

| Copia | Qué la actualiza | De dónde copia |
|---|---|---|
| Disco | `git pull` | GitHub |
| Imagen | `docker build` | Tu disco |
| Contenedor | `docker rm` y `docker run` otra vez | Tu imagen |

**La regla:** **cada copia se actualiza sólo con su propio comando.** «En mi máquina funciona» suele significar que una de las tres copias está vieja.
:::

::: problem {#xco1-d3 title="D3 · Las prácticas que faltaron"}
Sin escribir comandos: ¿qué cuatro o cinco costumbres de equipo habrían evitado este ejercicio completo? Para cada una, di qué fila habría cambiado.
:::

::: hint {of="xco1-d3"}
Repasa las filas 3, 5, 6, 7 y 9: ¿qué debió pasar antes de cada una?
:::

::: answer {of="xco1-d3"}
**Respuesta:** cualquiera de éstas vale, siempre que la ligues a una fila:

| Práctica | Qué habría cambiado |
|---|---|
| **Ponerse al día antes de trabajar** (`pull` antes de editar) | Beto habría partido del 10 de Ana: sin rechazo en la fila 3 ni conflicto en la fila 5 |
| **Ramas y pull requests** | El commit roto de la fila 6 se queda en una rama; alguien lo revisa antes de que llegue a `main` y a Caro en la fila 7 |
| **Resolver el conflicto de verdad** | Abrir el archivo, quitar los marcadores y acordar qué valor gana: Beto no commitea marcadores en la fila 6 |
| **Probar antes de subir** | Una revisión automática que construya y **arranque** la imagen en cada pull request: el código 2 bloquea el merge de la fila 6 |
| **Configuración fuera de la imagen** | Montada o por variable de entorno: cambiar un número no exige reconstruir (filas 2, 4 y 9) |
| **Imagen con el commit en el nombre** | En lugar de `alertas:1` siempre, y recreando contenedores: se sabe qué versión corre cada uno (fila 9) |
| **Acordar quién decide un valor** | El 10 contra el 20 de las filas 3 y 5 era un desacuerdo entre personas, no un problema de Git |

**Por qué:** cada práctica corta una de las tres causas del ejercicio: trabajar sobre un disco viejo, subir sin probar, y correr imágenes o contenedores viejos.
:::

## Ejercicio 2 · La base de datos

### El punto de partida

El equipo mantiene `tienda/`, con una base Postgres. Los cambios a la base son archivos SQL versionados en Git:

```text
tienda/
└── sql/
    └── 001_clientes.sql
```

`001_clientes.sql`:

```sql
CREATE TABLE clientes (id serial PRIMARY KEY, nombre text);
```

Cada quien levanta la base en su máquina, desde la carpeta del repo, siempre con el mismo comando:

```bash
docker run -d --name db -e POSTGRES_PASSWORD=fdd \
  -v datos:/var/lib/postgresql/data \
  -v "$(pwd)/sql":/docker-entrypoint-initdb.d \
  postgres:16
```

- `datos` es un **named volume**: ahí vive la base, y sobrevive a `docker rm`.
- El segundo `-v` monta la carpeta `sql/` del repo donde la imagen busca scripts de arranque.

**Un dato que necesitas.** Al arrancar, la imagen de Postgres:

- corre los `.sql` de `/docker-entrypoint-initdb.d`, en orden alfabético, **sólo si el volumen de datos está vacío**;
- si el volumen ya tiene una base, se salta todos los scripts y arranca;
- si un script falla, se detiene, y el contenedor se apaga.

Para ver las tablas: `docker exec db psql -U postgres -c '\dt'`.

Los tres clonaron el repo y levantaron su base. Cada quien tiene un volumen `datos` con la tabla `clientes`.

### La secuencia

::: problem {#xco2-1 title="Fila 1 · Ana agrega la tabla ventas, en una rama"}
```bash
# Ana
git switch -c ventas
# crea sql/002_ventas.sql:
#   CREATE TABLE ventas (id serial PRIMARY KEY,
#                        cliente int REFERENCES clientes(id), total numeric);
git add sql
git commit -m "tabla ventas"
git push -u origin ventas
docker rm -f db
docker run -d --name db ... postgres:16      # el mismo comando de arriba
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve Ana?
:::

::: hint {of="xco2-1"}
Estado antes de la fila 1. «inicial» es el commit que sólo tiene `001`. Cada columna es una máquina; GitHub sólo guarda commits y ramas:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | existe sólo `main` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` | `001` | `001` |
| Contenedor `db` | no hay | encendido, creado al inicio | encendido, creado al inicio | encendido, creado al inicio |
| Volumen `datos` | no hay | creado al inicio | creado al inicio | creado al inicio |

¿`docker rm` borra el volumen? ¿Cuándo corre Postgres los scripts?
:::

::: answer {of="xco2-1"}
**Respuesta:** Ana ve **sólo `clientes`**. La tabla `ventas` no existe en su base.

**Por qué:**

1. Actúa Ana. `git switch -c ventas` crea la rama `ventas` en su máquina y se cambia a ella.
2. Ana crea `sql/002_ventas.sql`, lo commitea en `ventas` y `git push -u origin ventas` sube la rama a GitHub. `main` no cambia: ni en GitHub ni en la máquina de Ana.
3. `docker rm -f db` borra el contenedor `db`. **No** borra el volumen `datos`.
4. El nuevo `docker run` monta el mismo volumen `datos`, que ya tiene una base: la que se creó al inicio, con `001`.
5. Postgres ve una base existente y se salta **todos** los scripts, incluido `002_ventas.sql`, aunque esté montado ahí mismo.
6. Beto y Caro no cambian: la rama `ventas` existe en GitHub, pero nadie la ha traído; y sus contenedores y volúmenes viven en sus máquinas.

**La regla:** **`docker rm` borra el contenedor, no el volumen**, y **un volumen ya inicializado no vuelve a correr los scripts de initdb** (los de `/docker-entrypoint-initdb.d`): los scripts nuevos se ignoran.

Estado después de la fila 1:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | **existen `main` y `ventas`** | **está en `ventas`** | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | **`001` y `002`** | `001` | `001` |
| Contenedor `db` | no hay | **encendido, creado en la fila 1** | encendido, creado al inicio | encendido, creado al inicio |
| Volumen `datos` | no hay | creado al inicio: corrió `001` | creado al inicio: corrió `001` | creado al inicio: corrió `001` |

**Compruébalo:**

```text
$ docker logs db
PostgreSQL Database directory appears to contain a database; Skipping initialization
```

**Error común:** esperar `ventas` porque `002_ventas.sql` está en la carpeta montada. Los scripts sólo corren con un volumen vacío.
:::

::: problem {#xco2-2 title="Fila 2 · Ana prueba con un volumen nuevo"}
```bash
# Ana
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve ahora? ¿Qué perdió?
:::

::: hint {of="xco2-2"}
Estado antes de la fila 2:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main` y `ventas` | está en `ventas` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` y `002` | `001` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 1 | encendido, creado al inicio | encendido, creado al inicio |
| Volumen `datos` | no hay | creado al inicio | creado al inicio | creado al inicio |

Con el volumen borrado, ¿cómo llega el siguiente `run` a `datos`?
:::

::: answer {of="xco2-2"}
**Respuesta:**

- Ana ve **`clientes` y `ventas`**.
- Perdió **todo lo que tenía su base anterior**: la tabla `clientes` con todas las filas que hubiera guardado.

**Por qué:**

1. Actúa Ana, sólo en su máquina.
2. `docker volume rm datos` borra el volumen y la base que había dentro. No tiene papelera.
3. `docker run` no encuentra `datos` y crea un volumen nuevo, vacío.
4. Con el volumen vacío, Postgres corre los scripts de la carpeta montada en orden alfabético: `001` (crea `clientes`) y `002` (crea `ventas`).
5. La tabla `clientes` nueva está vacía: es otra tabla con el mismo nombre, no la de antes.
6. GitHub, Beto y Caro no cambian: los volúmenes no se suben a ningún lado.

**La regla:** **los scripts de initdb corren sólo sobre un volumen vacío; vaciarlo es borrar la base entera.**

Estado después de la fila 2:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main` y `ventas` | está en `ventas` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` y `002` | `001` | `001` |
| Contenedor `db` | no hay | **encendido, creado en la fila 2** | encendido, creado al inicio | encendido, creado al inicio |
| Volumen `datos` | no hay | **creado en la fila 2: corrieron `001` y `002`** | creado al inicio: corrió `001` | creado al inicio: corrió `001` |

**Compruébalo:**

```text
$ docker exec db psql -U postgres -c '\dt'
          List of relations
 Schema |   Name   | Type  |  Owner   
--------+----------+-------+----------
 public | clientes | table | postgres
 public | ventas   | table | postgres
(2 rows)
```

Satisfecha, Ana abre su pull request **#1** desde `ventas`.
:::

::: problem {#xco2-3 title="Fila 3 · Beto agrega reportes, en su rama"}
Al mismo tiempo, Beto necesita una tabla con ventas por mes:

```bash
# Beto
git switch -c reportes
# crea sql/003_ventas_mensuales.sql:
#   CREATE TABLE ventas (mes text PRIMARY KEY, total numeric);
git add sql
git commit -m "ventas mensuales"
git push -u origin reportes
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve Beto?
:::

::: hint {of="xco2-3"}
Estado antes de la fila 3:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main` y `ventas` | está en `ventas` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` y `002` | `001` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 2 | encendido, creado al inicio | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2 | creado al inicio | creado al inicio |

¿De qué commit nace `reportes`? ¿Está `002_ventas.sql` en la carpeta que monta Beto?
:::

::: answer {of="xco2-3"}
**Respuesta:** Beto ve **`clientes` y `ventas`**, pero **su** `ventas` tiene las columnas **`mes` y `total`**, no las de Ana.

**Por qué:**

1. Actúa Beto. Está en `main`, en «inicial», y nunca trajo la rama de Ana.
2. `git switch -c reportes` crea `reportes` desde «inicial». En el disco de Beto no existe `002_ventas.sql`.
3. Beto crea `sql/003_ventas_mensuales.sql`, que crea una tabla también llamada `ventas`, y sube la rama `reportes` a GitHub.
4. Borra su volumen. El `run` crea uno vacío y Postgres corre lo que hay en la carpeta montada: `001` y `003`.
5. El `003` crea **su** tabla `ventas`, con `mes` y `total`. No hay choque porque en esta base no existe otra `ventas`.
6. Ana y Caro no cambian. GitHub sólo gana la rama `reportes`; `main` sigue en «inicial».

**La regla:** **cada rama sólo ve sus propios archivos.** Dos ramas pueden crear la misma tabla y cada una funciona sola.

Estado después de la fila 3:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | **existen `main`, `ventas` y `reportes`** | está en `ventas` | **está en `reportes`** | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` y `002` | **`001` y `003`** | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 2 | **encendido, creado en la fila 3** | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | **creado en la fila 3: corrieron `001` y `003`** | creado al inicio: corrió `001` |

**Compruébalo:** `ls sql` en la máquina de Beto → `001_clientes.sql` y `003_ventas_mensuales.sql`.

```text
$ docker exec db psql -U postgres -c '\d ventas'
               Table "public.ventas"
 Column |  Type   | Collation | Nullable | Default 
--------+---------+-----------+----------+---------
 mes    | text    |           | not null | 
 total  | numeric |           |          | 
```

En su máquina todo funciona, y Beto abre su pull request **#2** desde `reportes`.
:::

::: problem {#xco2-4 title="Fila 4 · Se mergean los dos pull requests"}
En GitHub alguien mergea el #1 y luego el #2. ¿Hay conflicto? ¿Por qué? ¿Qué archivos hay ahora en `sql/` en `main`?
:::

::: hint {of="xco2-4"}
Estado antes de la fila 4:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | «inicial» | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main`, `ventas` y `reportes` | está en `ventas` | está en `reportes` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001` | `001` y `002` | `001` y `003` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 2 | encendido, creado en la fila 3 | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado al inicio |

¿Tocaron Ana y Beto algún archivo en común?
:::

::: answer {of="xco2-4"}
**Respuesta:**

- **No hay conflicto.**
- Porque Ana y Beto **crearon archivos distintos**: no hay ninguna línea que Git tenga que elegir.
- En `sql/` de `main` quedan **`001_clientes.sql`, `002_ventas.sql` y `003_ventas_mensuales.sql`**.

**Por qué:**

1. Actúa alguien en GitHub, no en una máquina. El merge del #1 mete `002_ventas.sql` en `main`.
2. El merge del #2 mete `003_ventas_mensuales.sql`. Ese archivo no existe en `main`, así que Git sólo lo agrega.
3. Git compara archivo por archivo y línea por línea. Nadie cambió una misma línea: no hay nada que decidir.
4. Git no lee SQL. No puede ver que **los dos archivos crean una tabla con el mismo nombre**.
5. Sólo cambia GitHub. Los discos, contenedores y volúmenes de Ana, Beto y Caro siguen igual hasta que hagan `pull`.

Con `I` = «inicial», `V` = «tabla ventas» (Ana), `R` = «ventas mensuales» (Beto), `M1` = merge del #1 y `M2` = merge del #2:

```text
    V              ventas
   / \
  I---M1---M2      main
   \       /
    R------        reportes
```

**La regla:** **Git compara líneas, no significado.** «Se mezcla sin conflicto» no quiere decir «funciona junto».

Estado después de la fila 4:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | **merge del pull request #2** | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main`, `ventas` y `reportes` | está en `ventas` | está en `reportes` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | **`001`, `002` y `003`** | `001` y `002` | `001` y `003` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 2 | encendido, creado en la fila 3 | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | creado al inicio: corrió `001` |

**Compruébalo:** en el escenario reproducido (merge local con `--no-ff`), los dos merges salen con `Merge made by the 'ort' strategy.`, sin `CONFLICT`; `ls sql` en `main` muestra los tres archivos.
:::

::: problem {#xco2-5 title="Fila 5 · Ana y Beto se ponen al día"}
Cada uno, en su máquina, con su volumen de la fila 2 y de la fila 3:

```bash
# Ana, y luego Beto
git switch main
git pull origin main
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\d ventas'
```

`\d ventas` muestra las columnas de la tabla. ¿Qué columnas ve cada uno? ¿Corrió algún script?
:::

::: hint {of="xco2-5"}
Estado antes de la fila 5:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | «inicial» | «inicial» | «inicial» |
| Ramas | existen `main`, `ventas` y `reportes` | está en `ventas` | está en `reportes` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001` y `002` | `001` y `003` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 2 | encendido, creado en la fila 3 | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado al inicio |

¿Están vacíos los volúmenes de Ana y de Beto?
:::

::: answer {of="xco2-5"}
**Respuesta:**

- Ana ve **`id`, `cliente`, `total`**.
- Beto ve **`mes`, `total`**.
- **No corrió ningún script**, en ninguna de las dos máquinas.

**Por qué:**

1. Actúan Ana y luego Beto, cada uno en su máquina.
2. `git switch main` y `git pull` son un fast-forward: el `main` de cada uno avanza hasta el merge del #2. Ahora los dos tienen en disco `001`, `002` y `003`.
3. `docker rm -f db` borra el contenedor, no el volumen. El `run` nuevo monta el volumen de siempre.
4. El volumen de Ana se creó en la fila 2 y el de Beto en la fila 3: los dos tienen base. Postgres se salta todos los scripts.
5. Cada tabla `ventas` es la que dejó la inicialización de su volumen: la de Ana con `002`, la de Beto con `003`.
6. Caro no cambia: no ha hecho pull. GitHub tampoco: un pull sólo trae.

**La regla:** **un volumen ya inicializado no vuelve a correr los scripts de initdb, aunque `git pull` traiga scripts nuevos.**

Estado después de la fila 5:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | **merge del pull request #2** | **merge del pull request #2** | «inicial» |
| Ramas | existen `main`, `ventas` y `reportes` | **está en `main`** | **está en `main`** | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | **`001`, `002` y `003`** | **`001`, `002` y `003`** | `001` |
| Contenedor `db` | no hay | **encendido, creado en la fila 5** | **encendido, creado en la fila 5** | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | creado al inicio: corrió `001` |

Los dos tienen el **mismo commit** en el disco y una tabla `ventas` **distinta** en la base. Y los dos dirían «en mi máquina funciona».

**Compruébalo:** los dos logs dicen `PostgreSQL Database directory appears to contain a database; Skipping initialization`.

**Error común:** pensar que el `pull` actualiza la base. El pull cambia los archivos del disco; la base vive en el volumen, y el volumen no se vuelve a inicializar.
:::

::: problem {#xco2-6 title="Fila 6 · Caro se pone al día"}
Caro todavía tiene su volumen del principio.

```bash
# Caro
git pull origin main
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve?
:::

::: hint {of="xco2-6"}
Estado antes de la fila 6:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | «inicial» |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | encendido, creado al inicio |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado al inicio |

¿Qué scripts corrieron en el volumen de Caro, y cuándo?
:::

::: answer {of="xco2-6"}
**Respuesta:** Caro ve **sólo `clientes`**.

**Por qué:**

1. Actúa Caro. El pull es un fast-forward: su disco ya tiene `001`, `002` y `003`.
2. Su volumen `datos` es el del inicio, donde sólo corrió `001`.
3. El volumen ya tiene base: Postgres se salta los tres scripts, aunque ahora estén montados.
4. Ana, Beto y GitHub no cambian.

**La regla:** **un volumen ya inicializado no vuelve a correr los scripts de initdb.**

Estado después de la fila 6:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | **merge del pull request #2** |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | **`001`, `002` y `003`** |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | **encendido, creado en la fila 6** |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | creado al inicio: corrió `001` |

Caro tiene el código más reciente y la base más vieja del equipo.

**Compruébalo:** `docker exec db psql -U postgres -c '\dt'` lista una sola tabla, `clientes`, y dice `(1 row)`.
:::

::: problem {#xco2-7 title="Fila 7 · Caro empieza desde cero"}
```bash
# Caro
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker ps
docker logs db
```

¿Aparece `db` en `docker ps`? ¿Qué dice el log?
:::

::: hint {of="xco2-7"}
Estado antes de la fila 7:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | encendido, creado en la fila 6 |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado al inicio |

¿Qué crea cada script, en orden?
:::

::: answer {of="xco2-7"}
**Respuesta:**

- **Justo después del `run`, sí**: `db` todavía aparece como `Up`. Unos segundos después, cuando falla el `003`, **ya no aparece**: el contenedor se apagó con código 3 (en el escenario se miró a los 25 s).
- El log, mirado justo después del `run`, puede no mostrar el error todavía. Cuando termina la inicialización, muestra que `001` y `002` corrieron bien y que **el `003` falló**: `relation "ventas" already exists`.

**Por qué:**

1. Actúa Caro. Borra el contenedor y el volumen. El `run` crea un volumen vacío.
2. Con el volumen vacío, Postgres corre los scripts en orden alfabético.
3. `001` crea `clientes`. `002` crea la `ventas` de Ana.
4. `003` intenta crear otra `ventas`, la de Beto. Ya existe una: error.
5. Los scripts tardan unos segundos. Mientras corren, `db` está encendido y `docker ps` lo lista.
6. Si un script falla, Postgres detiene la inicialización y el contenedor se apaga. `docker ps` sólo lista contenedores encendidos, así que desde ese momento `db` ya no aparece.
7. Ana, Beto y GitHub no cambian: sus volúmenes se inicializaron antes del merge y nunca corren el `003` junto con el `002`.

| Script | Resultado |
|---|---|
| `001` | Crea `clientes` |
| `002` | Crea la `ventas` de Ana |
| `003` | Intenta crear `ventas` otra vez: error, y Postgres detiene la inicialización |

**La regla:** **los scripts de initdb corren sólo sobre un volumen vacío, y el primero que falla apaga el contenedor.**

Estado después de la fila 7:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | **apagado con código 3, creado en la fila 7** |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | **creado en la fila 7: corrieron `001` y `002`; el `003` corrió y falló** |

Es la primera vez que alguien prueba **el resultado del merge** sobre una base nueva, y truena. Cada rama por separado funcionaba.

**Compruébalo:** `docker logs db` una vez terminada la inicialización (salida real, sin las líneas de `initdb`):

```text
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/001_clientes.sql
CREATE TABLE
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/002_ventas.sql
CREATE TABLE
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/003_ventas_mensuales.sql
2026-10-09 18:43:29.201 UTC [63] ERROR:  relation "ventas" already exists
psql:/docker-entrypoint-initdb.d/003_ventas_mensuales.sql:1: ERROR:  relation "ventas" already exists
```

A los 25 s, `docker ps` ya no lo lista y `docker ps -a` lo lista como `Exited (3)`.

**Error común:** concluir que todo está bien porque `docker run -d` no mostró error y el primer `docker ps` lista `db` como `Up`. Con `-d`, `docker run` sólo arranca el contenedor e imprime su ID; el `003` falla segundos después, dentro del contenedor. Hay que volver a mirar `docker ps` y `docker logs` cuando termine la inicialización.
:::

::: problem {#xco2-8 title="Fila 8 · Caro lo intenta otra vez"}
```bash
# Caro
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

No borró el volumen. ¿Arranca? ¿Qué tablas ve? ¿Por qué esto es **peor** que el error de la fila 7?
:::

::: hint {of="xco2-8"}
Estado antes de la fila 8:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | apagado con código 3, creado en la fila 7 |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado en la fila 7, en el arranque que falló |

Después del intento fallido, ¿quedó vacío el volumen?
:::

::: answer {of="xco2-8"}
**Respuesta:**

- **Sí arranca.**
- Ve **`clientes` y `ventas`**; esa `ventas` es la de Ana (`id`, `cliente`, `total`).
- **Es peor** porque ya no hay ningún error que ver: la base no tiene la tabla de Beto y nada se lo dice a Caro.

**Por qué:**

1. Actúa Caro. Borra el contenedor, pero **no** el volumen.
2. El volumen no quedó vacío en la fila 7: `001` y `002` ya habían creado sus tablas antes de que fallara el `003`.
3. Postgres ve una base, se salta todos los scripts y arranca sin avisar.
4. El error de la fila 7 sólo estaba en el log de aquel contenedor, y se borró con el `docker rm -f`.
5. Ana, Beto y GitHub no cambian.

**La regla:** **un volumen ya inicializado no vuelve a correr los scripts de initdb, aunque la inicialización anterior haya fallado a medias.**

Estado después de la fila 8:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | **encendido, creado en la fila 8** |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | creado en la fila 7: corrieron `001` y `002`; el `003` corrió y falló |

**Compruébalo:** salidas reales, recortadas:

```text
$ docker logs db
PostgreSQL Database directory appears to contain a database; Skipping initialization
...
$ docker exec db psql -U postgres -c '\dt'
 public | clientes | table | postgres
 public | ventas   | table | postgres
$ docker exec db psql -U postgres -c '\d ventas'
 id      | integer |           | not null | nextval('ventas_id_seq'::regclass)
 cliente | integer |           |          | 
 total   | numeric |           |          | 
```

**Error común:** creer que reintentar «arregló» algo. Nada cambió en los scripts; sólo se dejó de ver el error.
:::

::: problem {#xco2-9 title="Fila 9 · La contraseña"}
Beto sube por error un archivo con la contraseña real de producción, y en el siguiente commit lo borra:

```bash
# Beto
echo "POSTGRES_PASSWORD=Tienda2026!" > .env
git add .env
git commit -m "config local"
git push origin main
rm .env
git commit -am "quita .env"
git push origin main
```

Alguien clona el repo después. ¿Ve `.env` en su disco? ¿La contraseña sigue en GitHub?
:::

::: hint {of="xco2-9"}
Estado antes de la fila 9:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | encendido, creado en la fila 8 |
| Volumen `datos` | no hay | creado en la fila 2 | creado en la fila 3 | creado en la fila 7 |

¿Qué guarda Git de cada commit? ¿Un commit nuevo borra los anteriores?
:::

::: answer {of="xco2-9"}
**Respuesta:**

- **No**: en el disco de un clon nuevo no hay `.env`.
- **Sí**: la contraseña sigue en GitHub, en el historial de `main`.

**Por qué:**

1. Actúa Beto. El commit «config local» guarda `.env` completo, con la contraseña, y el push lo sube a GitHub.
2. `rm .env` y el commit «quita .env» crean un commit **nuevo** sin el archivo. «config local» sigue en la historia, debajo.
3. Un clon nuevo pone en el disco el último commit, «quita .env»: no hay `.env` a la vista.
4. Pero el clon trae toda la historia, y cualquiera puede pedir el archivo a «config local».
5. Ana y Caro todavía no tienen la contraseña en su máquina; la recibirán, dentro de la historia, en su próximo pull.

**La regla:** **un commit nuevo no borra los anteriores: lo que subiste una vez sigue en el historial.** Lo único seguro es dar la contraseña por filtrada y **cambiarla**.

Estado después de la fila 9:

| | GitHub | Ana | Beto | Caro |
|---|---|---|---|---|
| Último commit de `main` | **«quita .env»** | merge del pull request #2 | **«quita .env»** | merge del pull request #2 |
| Ramas | existen `main`, `ventas` y `reportes` | está en `main` | está en `main` | está en `main` |
| Scripts en `sql/` (lo que monta el segundo `-v`) | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` | `001`, `002` y `003` |
| Contenedor `db` | no hay | encendido, creado en la fila 5 | encendido, creado en la fila 5 | encendido, creado en la fila 8 |
| Volumen `datos` | no hay | creado en la fila 2: corrieron `001` y `002` | creado en la fila 3: corrieron `001` y `003` | creado en la fila 7: corrieron `001` y `002`; el `003` corrió y falló |

**Compruébalo:** desde un clon nuevo, `ls -a` no muestra `.env`, pero:

```text
$ git show HEAD~1:.env
POSTGRES_PASSWORD=Tienda2026!
```

**Error común:** creer que borrar el archivo en un commit nuevo «quita» el secreto. Sólo lo quita de la vista del último commit.
:::

### Diagnóstico y prácticas

::: problem {#xco2-d1 title="D1 · ¿Qué tiene cada base?"}
Después de la fila 8, ¿qué tablas y qué columnas de `ventas` tiene la base de Ana, la de Beto y la de Caro? ¿Cuál de las tres es «la correcta»?
:::

::: hint {of="xco2-d1"}
Junta las respuestas de las filas 5 y 8. ¿Qué scripts se aplicaron en cada volumen?
:::

::: answer {of="xco2-d1"}
**Respuesta:**

| Base | Scripts que corrieron en su volumen | Tablas | Columnas de `ventas` |
|---|---|---|---|
| Ana | `001` y `002`, en la fila 2 | `clientes`, `ventas` | `id`, `cliente`, `total` |
| Beto | `001` y `003`, en la fila 3 | `clientes`, `ventas` | `mes`, `total` |
| Caro | `001` y `002` en la fila 7; el `003` corrió y falló | `clientes`, `ventas` | `id`, `cliente`, `total` |

**Ninguna es «la correcta»**, porque `main` no describe una base posible: sus tres scripts no pueden correr completos.

**Por qué:**

1. Cada volumen se inicializó una sola vez, con los scripts que había en el disco de su dueño en ese momento.
2. La base de Caro tiene la misma estructura que la de Ana: el `003` sí corrió, pero falló sin crear nada (log de la fila 7, `\d ventas` de la fila 8). Nada dentro de la base registra que su inicialización falló.
3. Los tres tienen el mismo commit en el disco. Ese commit no dice qué hay en ningún volumen.

**La regla:** **cada volumen guarda la historia de cuándo se creó, no el código actual.**
:::

::: problem {#xco2-d2 title="D2 · Sin conflicto, pero roto"}
Git dijo «sin conflicto» en la fila 4. Explica por qué eso no garantizaba nada.
:::

::: hint {of="xco2-d2"}
¿Qué compara Git cuando mezcla?
:::

::: answer {of="xco2-d2"}
**Respuesta:** «sin conflicto» sólo quiere decir que **nadie cambió las mismas líneas**. No dice nada de si el resultado funciona.

**Por qué:**

1. Git compara **líneas de archivos**. Un conflicto aparece cuando dos personas cambian la misma línea del mismo archivo.
2. Ana y Beto crearon archivos distintos (`002` y `003`). Para Git no había nada que decidir.
3. El choque era de **significado**: los dos archivos crean una tabla llamada `ventas`.
4. Ese choque sólo aparece al **ejecutar** el resultado: la primera vez fue en la fila 7, sobre un volumen vacío.

**La regla:** **Git compara líneas, no significado.** «Se mezcla limpio» no es lo mismo que «funciona junto».
:::

::: problem {#xco2-d3 title="D3 · Las prácticas que faltaron"}
Sin escribir comandos: ¿qué costumbres habrían evitado los problemas de las filas 1, 5, 7, 8 y 9?
:::

::: hint {of="xco2-d3"}
Tres frentes: cómo se cambia una base que ya existe, qué se prueba antes de mergear, y qué nunca entra a Git.
:::

::: answer {of="xco2-d3"}
**Respuesta:**

| Práctica | Fila que arregla | Qué habría cambiado |
|---|---|---|
| **Migraciones, no scripts de arranque** | 1 y 5 (y 6) | Pasos numerados que se aplican una vez, en orden, sobre la base que ya existe; la base anota cuáles lleva. Nadie necesita borrar su volumen para ver un cambio |
| **Probar el resultado del merge** | 7 | Una revisión automática levanta la base desde un volumen vacío con el `main` que resultaría: el choque aparece en el pull request #2, antes del merge |
| **Revisar lo que hace un pull request** | 7 | No basta con que mezcle limpio. Quien revisa el #2 pregunta si `ventas` ya existe |
| **Coordinar nombres y numeración** | 3 y 7 | Un solo lugar donde se ven los cambios a la base en curso: nadie inventa la misma tabla a la vez |
| **Leer el error antes de reintentar** | 8 | No reintentar sobre un volumen que quedó a medias: Caro no tapa el error de la fila 7 |
| **Secretos fuera de Git** | 9 | `.env` en el `.gitignore` y un ejemplo sin valores reales en el repo; si uno se filtra, se cambia |
| **El volumen es estado** | 2 | Decidir en equipo cuándo se borra, y respaldar antes: Ana no pierde sus datos |

**Por qué:** las tres causas del ejercicio son que la base no se actualiza con el código, que nadie corrió el resultado del merge, y que lo que entra a Git se queda en la historia.
:::

**Repasa:** [[branches-y-merge]], [[el-flujo-del-curso]], [[named-volumes-y-postgres]], [[donde-vive-cada-byte]] y [[lo-que-no-se-sube]].
