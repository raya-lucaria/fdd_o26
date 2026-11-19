---
id: ejercicios-docker
title: "Ejercicios extra de Docker"
nav_title: "Docker"
summary: "Ejercicios nuevos con la forma del parcial de Docker, cada uno con su respuesta explicada debajo: un Dockerfile con .dockerignore y caché, una secuencia de volúmenes de doce filas y cinco errores reales."
status: ready
estimated_time: 40m
tags: [ejercicios, docker, dockerfile, dockerignore, volumenes, cache, errores]
---

# Ejercicios extra de Docker

**[PDF sin respuestas, para imprimir](../_assets/practica-docker.pdf)** · unos 40 minutos · sin apuntes

Miden lo mismo que el parcial, con escenarios nuevos. Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado. Todas las respuestas se comprobaron corriendo los comandos con Docker 29.6: si quieres, córrelos tú también.

## Parte 1 · Lee el Dockerfile

`encuestas/` es un repo de Python. El programa `limpiar.py` usa `reglas.py`, lee `crudos/respuestas.csv` y escribe `salida/limpio.csv`. Las dos rutas son relativas a la carpeta donde corre.

```text
encuestas/        ← estás aquí
├── .dockerignore
├── Dockerfile
├── README.md
├── requirements.txt
├── limpiar.py
├── reglas.py
├── notas/
│   └── ideas.md
├── crudos/
│   └── respuestas.csv
└── salida/
```

El `.dockerignore`:

```text
crudos/
notas/
salida/
```

El `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "limpiar.py"]
```

La imagen ya se construyó una vez con `docker build -t encuestas:1 .`.

::: problem {#xd-1a title="a · ¿Para qué se copia requirements.txt antes?"}
El `COPY . .` de la línea 5 ya copia `requirements.txt`. ¿Para qué se copia antes, por separado, en la línea 3?
:::

::: hint {of="xd-1a"}
Docker reusa una capa mientras no cambie lo que esa capa lee. ¿De qué depende el `pip install` si `requirements.txt` va solo?
:::

::: answer {of="xd-1a"}
**Respuesta:** **para que el `RUN pip install` salga de la caché cada vez que cambias sólo tu código.** El archivo se copia dos veces a propósito; la línea 3 no hace falta para que el build funcione, hace falta para que sea rápido.

**Por qué:**
1. Docker guarda el resultado de cada línea del Dockerfile como una capa.
2. En el siguiente build, Docker reusa una capa si no cambió nada de lo que esa línea lee, ni ninguna capa anterior.
3. La línea 3, `COPY requirements.txt .`, lee un solo archivo: `requirements.txt`.
4. La línea 4, `RUN pip install`, depende sólo de las capas 1 a 3. Mientras `requirements.txt` no cambie, sale de la caché.
5. Si cambias `limpiar.py`, lo único que cambia es lo que lee la línea 5, `COPY . .`. Se rehace la línea 5 y la instalación no se toca.
6. Sin la línea 3, el `pip install` tendría que ir después de `COPY . .`. Entonces cualquier cambio, aunque sea en `limpiar.py`, reinstalaría todos los paquetes.

**La regla:** **caché de capas por contenido: una capa se reusa mientras no cambie el contenido de lo que lee, y cuando una capa se rehace, se rehacen todas las que siguen.**

| Cambias `limpiar.py` y construyes | `RUN pip install` |
|---|---|
| Con la línea 3 (como está) | sale de la caché |
| Sin la línea 3 (sólo `COPY . .` y luego `pip install`) | **se rehace: reinstala todo** |

**Error común:** «se copia antes para que `requirements.txt` exista al instalar». Con un solo `COPY . .` antes del `pip install`, el archivo también existiría. La separación sólo sirve para la caché.
:::

::: problem {#xd-1b title="b · ¿Qué queda dentro de /app?"}
¿Qué archivos y carpetas quedan dentro de `/app` en la imagen?
:::

::: hint {of="xd-1b"}
`COPY . .` copia todo el contexto menos lo que excluye el `.dockerignore`. ¿Alguien excluyó el propio Dockerfile?
:::

::: answer {of="xd-1b"}
**Respuesta:** **`.dockerignore`, `Dockerfile`, `README.md`, `limpiar.py`, `reglas.py` y `requirements.txt`.** No hay `crudos/`, `notas/` ni `salida/`.

**Por qué:**
1. `WORKDIR /app` hace que el `.` de destino de cada `COPY` sea `/app`.
2. `COPY . .` copia el contexto del build, que es tu carpeta `encuestas/`, menos lo que lista el `.dockerignore`.
3. El `.dockerignore` excluye `crudos/`, `notas/` y `salida/`. Esas tres no entran.
4. Nadie excluyó el `Dockerfile` ni el propio `.dockerignore`. Los dos entran como cualquier otro archivo.
5. `requirements.txt` ya estaba en `/app` desde la línea 3. La línea 5 lo copia otra vez, con el mismo contenido.

| Archivo o carpeta | ¿Está en `/app`? | Por qué |
|---|---|---|
| `limpiar.py`, `reglas.py`, `README.md` | sí | `COPY . .` y no están en el `.dockerignore` |
| `requirements.txt` | sí | líneas 3 y 5 |
| `Dockerfile`, `.dockerignore` | sí | nadie los excluyó |
| `crudos/`, `notas/`, `salida/` | **no** | están en el `.dockerignore` |

**Compruébalo:** `docker run --rm encuestas:1 ls -A /app` → `.dockerignore`, `Dockerfile`, `README.md`, `limpiar.py`, `reglas.py`, `requirements.txt`.

**Error común:** dejar fuera el `Dockerfile` y el `.dockerignore`. El `.dockerignore` no se excluye a sí mismo: sólo excluye lo que tiene escrito.
:::

::: problem {#xd-1c title="c · Córrelo con las dos carpetas montadas"}
Escribe el comando que corre `encuestas:1` en un contenedor que se borre al terminar, con tu carpeta `crudos/` montada en `/app/crudos` y tu carpeta `salida/` montada en `/app/salida`.
:::

::: hint {of="xd-1c"}
Un `-v` por carpeta, los dos antes del nombre de la imagen.
:::

::: answer {of="xd-1c"}
**Respuesta:**

```bash
docker run --rm -v "$(pwd)/crudos":/app/crudos -v "$(pwd)/salida":/app/salida encuestas:1
```

**Por qué:**
1. `--rm` borra el contenedor cuando el programa termina.
2. `-v origen:destino` con una ruta absoluta como origen es un bind mount: el contenedor ve tu carpeta real. `"$(pwd)/crudos"` arma esa ruta absoluta desde `encuestas/`.
3. Los destinos salen del programa: `limpiar.py` usa `crudos/…` y `salida/…` relativas a donde corre, y corre en el `WORKDIR`, `/app`. Por eso van en `/app/crudos` y `/app/salida`.
4. Va un `-v` por carpeta, y los dos van **antes** del nombre de la imagen. Lo que escribas después de `encuestas:1` se toma como el comando.
5. El programa escribe en `/app/salida`, que es tu carpeta `salida/`. Al terminar, `salida/limpio.csv` queda en tu disco aunque el contenedor ya no exista.

**La regla:** **un montaje tapa lo que la imagen tiene en esa ruta.** Aquí la imagen no tiene nada en `/app/crudos` ni en `/app/salida`, así que en esas dos rutas sólo se ve tu disco.

**Compruébalo:** en la prueba, el `limpiar.py` de prueba imprimió `listo`, y después `ls salida` → `limpio.csv`.

**Error común:** `-v crudos:/app/crudos`, sin `$(pwd)/`. Un origen sin `/` es el nombre de un volumen: Docker crea un volumen con nombre `crudos`, vacío, y tu carpeta no se monta.
:::

::: problem {#xd-1d title="d · ¿Y sin montar nada?"}
Alguien corre `docker run --rm encuestas:1`, sin montar nada. ¿Qué pasa y por qué?
:::

::: hint {of="xd-1d"}
¿Está `crudos/` dentro de la imagen?
:::

::: answer {of="xd-1d"}
**Respuesta:** **truena con `FileNotFoundError: [Errno 2] No such file or directory: 'crudos/respuestas.csv'` y sale con código 1, porque la imagen no tiene `crudos/` y nadie la montó.**

**Por qué:**
1. No hay nada después del nombre de la imagen, así que corre el `CMD`: `python limpiar.py`, dentro de `/app`.
2. `limpiar.py` abre `crudos/respuestas.csv`. La ruta es relativa, así que busca `/app/crudos/respuestas.csv`.
3. El `.dockerignore` dejó `crudos/` fuera del contexto: `COPY . .` nunca la metió a la imagen.
4. Sin `-v`, el contenedor sólo ve la imagen. En `/app` no hay `crudos/`, y `open` falla.

**La regla:** **los datos se montan al correr, no se meten a la imagen.** Esa es la razón de tener `crudos/` en el `.dockerignore`.

**Compruébalo:** en la prueba, con el `limpiar.py` de prueba (el número de línea depende de tu archivo):

```text
$ docker run --rm encuestas:1
Traceback (most recent call last):
  File "/app/limpiar.py", line 3, in <module>
…
FileNotFoundError: [Errno 2] No such file or directory: 'crudos/respuestas.csv'
```
:::

::: problem {#xd-1e title="e · ¿Qué pasos se rehacen?"}
Después del primer build cambias **un solo** archivo y vuelves a construir. En cada caso, ¿qué pasos se rehacen y cuáles salen de la caché?

1. Agregas una línea a `notas/ideas.md`.
2. Cambias `reglas.py`.
3. Agregas un paquete a `requirements.txt`.
4. Corriges un typo en `README.md`.
:::

::: hint {of="xd-1e"}
Para cada archivo, pregúntate qué `COPY` lo lee, y si ese archivo existe para el build.
:::

::: answer {of="xd-1e"}
**Respuesta:** `FROM` y `WORKDIR` salen de la caché en los cuatro casos. Para las otras tres líneas:
- **Caso 1, `notas/ideas.md`: todo sale de la caché.**
- **Caso 2, `reglas.py`: sólo se rehace `COPY . .`.**
- **Caso 3, `requirements.txt`: se rehacen `COPY requirements.txt .`, `RUN pip install` y `COPY . .`.**
- **Caso 4, `README.md`: sólo se rehace `COPY . .`.**

**Por qué:**
1. `FROM` y `WORKDIR` no leen ningún archivo tuyo: nunca se rehacen por un cambio en tu carpeta.
2. Para cada archivo, busca qué `COPY` lo lee. `COPY requirements.txt .` lee sólo `requirements.txt`. `COPY . .` lee todo el contexto menos el `.dockerignore`.
3. Si el contenido de lo que lee un `COPY` cambió, ese `COPY` se rehace, y con él todas las líneas que siguen.
4. `notas/` está en el `.dockerignore`: para el build, `ideas.md` no existe, así que ningún `COPY` lo lee.

**La regla:** **caché de capas por contenido: una capa se reusa mientras no cambie el contenido de lo que lee, y cuando una capa se rehace, se rehacen todas las que siguen.**

| Cambio | Lo lee | `COPY requirements.txt .` | `RUN pip install` | `COPY . .` |
|---|---|---|---|---|
| 1. `notas/ideas.md` | ningún `COPY` (está en el `.dockerignore`) | caché | caché | caché |
| 2. `reglas.py` | `COPY . .` | caché | caché | **se rehace** |
| 3. `requirements.txt` | los dos `COPY` | **se rehace** | **se rehace** | **se rehace** |
| 4. `README.md` | `COPY . .` | caché | caché | **se rehace** |

**Compruébalo:** `docker build --progress=plain -t encuestas:1 .` marca `CACHED` en cada línea que sale de la caché. En el caso 1, las cuatro líneas después del `FROM` dicen `CACHED`.

**Error común:** en el caso 1, decir que `COPY . .` se rehace. El archivo cambió en tu disco, pero el `.dockerignore` lo deja fuera del build.
:::

::: problem {#xd-1f title="f · ¿Y si se olvida salida/ en el .dockerignore?"}
Alguien borra la línea `salida/` del `.dockerignore`. Corre el programa con la salida montada, como en c), y vuelve a construir. ¿Qué dos cosas cambian?
:::

::: hint {of="xd-1f"}
¿Qué escribe el programa en `salida/`, y qué copia `COPY . .` si ya no la excluye?
:::

::: answer {of="xd-1f"}
**Respuesta:**
- **Primera: `limpio.csv` entra a la imagen, en `/app/salida`.**
- **Segunda: `COPY . .` se rehace cada vez que una corrida deja un `limpio.csv` con contenido distinto.**

**Por qué:**
1. Sin la línea `salida/`, el `.dockerignore` ya no excluye esa carpeta: ahora es parte del contexto.
2. Al correr con `salida/` montada, el programa escribe `limpio.csv` en tu disco.
3. En el siguiente build, `COPY . .` copia todo el contexto, y eso incluye `salida/limpio.csv`. El archivo queda dentro de la imagen.
4. Ese primer build rehace `COPY . .` de todos modos, porque el `.dockerignore` también entra a la imagen y su contenido cambió.
5. Cada corrida que deja un `limpio.csv` distinto cambia lo que lee `COPY . .`, y el siguiente build lo rehace.
6. Si la corrida reescribe exactamente el mismo `limpio.csv`, el `COPY . .` sale de la caché: Docker compara el contenido, no la fecha del archivo.

**La regla:** **caché de capas por contenido.** Lo que el `.dockerignore` no excluye cuenta como parte del contenido.

| Paso | `salida/` en tu disco | `COPY . .` | `/app/salida` en la imagen |
|---|---|---|---|
| borras `salida/` del `.dockerignore` | vacía | no aplica (no es build) | no existe |
| corres con `salida/` montada | **`limpio.csv`** | no aplica (no es build) | no existe |
| `docker build` | `limpio.csv` | **se rehace** | **`limpio.csv`** |
| corres otra vez con los mismos datos | `limpio.csv` igual | no aplica (no es build) | `limpio.csv` |
| `docker build` | `limpio.csv` igual | **caché** | `limpio.csv` |
| corres con datos nuevos | **`limpio.csv` distinto** | no aplica (no es build) | `limpio.csv` viejo |
| `docker build` | `limpio.csv` distinto | **se rehace** | **`limpio.csv` nuevo** |

**Compruébalo:**

```text
$ docker run --rm encuestas:1 ls -A /app/salida
limpio.csv

# corres otra vez con los mismos datos y construyes
#9 [5/5] COPY . .
#9 CACHED

# corres con datos nuevos y construyes
#9 [5/5] COPY . .
#9 DONE 0.0s
```

Cuando corres con `salida/` montada no ves la copia de la imagen: **un montaje tapa lo que la imagen tiene en esa ruta.** Por eso el problema pasa desapercibido. Las carpetas de datos y de resultados van en el `.dockerignore` para que no viajen dentro de la imagen ni decidan cuándo se rehace una capa.
:::

::: problem {#xd-1g title="g · ¿Corre limpiar.py?"}
`docker run --rm encuestas:1 python reglas.py`, ¿corre `limpiar.py`? ¿Por qué?
:::

::: hint {of="xd-1g"}
¿Qué pasa con el `CMD` cuando escribes algo después del nombre de la imagen?
:::

::: answer {of="xd-1g"}
**Respuesta:** **no. Corre `python reglas.py` en lugar de `python limpiar.py`.**

**Por qué:**
1. El `CMD` es el comando que corre cuando no escribes nada después del nombre de la imagen.
2. Aquí sí hay algo después de `encuestas:1`: `python reglas.py`. Eso reemplaza al `CMD` completo; no se suma a él.
3. El contenedor corre en `/app`, donde está `reglas.py`, así que Python lo encuentra.
4. `limpiar.py` importa `reglas.py`, pero no al revés: correr `reglas.py` no ejecuta `limpiar.py`.
5. Lo que se imprima depende de lo que haga `reglas.py`. En la prueba, con un `reglas.py` que sólo define una función, no imprimió nada y salió con código 0.

**La regla:** **lo que escribes después del nombre de la imagen reemplaza al `CMD`.**

**Error común:** pensar que corren los dos, primero `reglas.py` y después el `CMD`. Sólo corre uno.
:::

**Repasa:** [[el-dockerfile-por-dentro]], [[capas-y-cache]] y [[rutas-en-docker]].

## Parte 2 · ¿Qué cambió?

En `lab/` hay sólo este Dockerfile y `saludo.txt`, cuyo texto es la palabra **hola**:

```dockerfile
FROM alpine:3.20
WORKDIR /s
COPY saludo.txt .
CMD ["cat", "saludo.txt"]
```

No existen imágenes, contenedores, volúmenes ni caché previos. Los comandos se corren **en orden**, todos desde `lab/`, y ningún `sleep 600` alcanza a terminar. Cada fila parte de lo que dejó la anterior.

En cada fila, pregúntate: ¿este contenedor lee la imagen, tu carpeta, un volumen o su propia capa de escritura?

::: problem {#xd-2-1 title="Fila 1 · ¿Qué imprime el último exec?"}
```bash
docker build -t saludo:1 .
docker run -d --name pa saludo:1 sleep 600
docker exec pa sh -c 'echo adios > saludo.txt'
docker stop pa
docker start pa
docker exec pa cat saludo.txt
```
:::

::: hint {of="xd-2-1"}
Estado al empezar:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| inicio | `hola` | no existe | ninguno | no existe |  |

¿Qué borra `docker stop`? ¿Qué borra `docker rm`?
:::

::: answer {of="xd-2-1"}
**Respuesta:** **`adios`.**

**Por qué:**
1. `docker build` copia tu `saludo.txt` (`hola`) a `/s` dentro de la imagen `saludo:1`.
2. `docker run -d --name pa … sleep 600` crea el contenedor `pa` con esa imagen y sin montajes. La capa escribible de `pa` empieza vacía.
3. `docker exec pa sh -c 'echo adios > saludo.txt'` corre en el `WORKDIR` del contenedor, `/s`. `pa` no monta nada en `/s`, así que el archivo nuevo se escribe en **la capa escribible de `pa`**. La imagen sigue diciendo `hola`.
4. `docker stop pa` detiene el proceso `sleep`. El contenedor `pa` y su capa siguen en disco.
5. `docker start pa` arranca el mismo contenedor `pa`, con la misma capa.
6. `docker exec pa cat saludo.txt` lee `/s/saludo.txt` dentro de `pa`. Dónde lee: la capa de `pa` tiene una versión del archivo, y esa versión es la que se ve; la de la imagen queda debajo. Imprime `adios`.

**La regla:** **La capa escribible sobrevive a `stop`/`start`, pero no a `rm`.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| inicio | `hola` | no existe | ninguno | no existe |  |
| `docker build -t saludo:1 .` | `hola` | **`hola` (build de la fila 1)** | ninguno | no existe |  |
| `docker run -d --name pa saludo:1 sleep 600` | `hola` | `hola` (build de la fila 1) | **`pa` corre; su capa está vacía.** | no existe |  |
| `docker exec pa sh -c 'echo adios > saludo.txt'` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene **`adios`**. | no existe |  |
| `docker stop pa` | `hola` | `hola` (build de la fila 1) | `pa` está **detenido**; su capa tiene `adios`. | no existe |  |
| `docker start pa` | `hola` | `hola` (build de la fila 1) | `pa` **corre otra vez**; su capa tiene `adios`. | no existe |  |
| `docker exec pa cat saludo.txt` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. | no existe | **`adios`** |

**Compruébalo:** `docker exec pa cat saludo.txt` → `adios`.

**Error común:** `hola`, pensando que `docker stop` borra lo que el contenedor escribió. Eso lo hace `docker rm`.
:::

::: problem {#xd-2-2 title="Fila 2 · ¿Qué imprime?"}
```bash
docker run --rm saludo:1
```
:::

::: hint {of="xd-2-2"}
Estado al terminar la fila 1, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 1 | la del inicio | la del build de la fila 1 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | no existe | lo que imprimió la fila 1 |

Un contenedor nuevo, sin montaje, ¿de dónde lee `/s/saludo.txt`?
:::

::: answer {of="xd-2-2"}
**Respuesta:** **`hola`.**

**Por qué:**
1. `docker run` crea un contenedor **nuevo**. Su capa escribible empieza vacía.
2. No hay `-v`: en `/s` este contenedor sólo ve lo que trae la imagen `saludo:1`, que dice `hola` desde el build de la fila 1.
3. No hay nada después de la imagen, así que corre el `CMD`: `cat saludo.txt`, en el `WORKDIR` `/s`. Dónde lee: la imagen. Imprime `hola`.
4. `adios` está en la capa de `pa`. Cada contenedor tiene su propia capa escribible, y ningún otro contenedor la ve.
5. Al terminar, `--rm` borra este contenedor nuevo. `pa` no se toca.

**La regla:** **cada contenedor tiene su propia capa escribible; uno nuevo empieza con la capa vacía y ve la imagen.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker exec pa cat saludo.txt` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. | no existe | **`adios`** |
| `docker run --rm saludo:1` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. El contenedor de este `run` se borra al salir. | no existe | **`hola`** |

**Compruébalo:** `docker run --rm saludo:1` → `hola`.

**Error común:** `adios`. Lo escribió `pa` en su propia capa, no en la imagen.
:::

::: problem {#xd-2-3 title="Fila 3 · ¿Qué imprime el último run?"}
```bash
docker run -d --name pb -v caja:/s saludo:1 sleep 600
docker exec pb sh -c 'echo luna > saludo.txt'
docker run --rm -v caja:/s saludo:1
```
:::

::: hint {of="xd-2-3"}
Estado al terminar la fila 2, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 2 | la del inicio | la del build de la fila 1 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | no existe | lo que imprimió la fila 2 |

¿Con qué llena Docker un volumen nuevo y vacío? ¿Qué ve otro contenedor que monta el mismo volumen?
:::

::: answer {of="xd-2-3"}
**Respuesta:** **`luna`.**

**Por qué:**
1. `docker run -d --name pb -v caja:/s …`: el volumen `caja` no existía, así que Docker lo crea vacío.
2. **Un volumen con nombre se llena desde la imagen sólo si está vacío.** `caja` está vacío y la imagen tiene `/s/saludo.txt` con `hola`: Docker copia `hola` al volumen.
3. **Un montaje tapa lo que la imagen tiene en esa ruta.** Dentro de `pb`, la carpeta `/s` es el volumen `caja`.
4. `docker exec pb sh -c 'echo luna > saludo.txt'` corre en el `WORKDIR` `/s` de `pb`. Dónde escribe: en el volumen `caja`, no en la capa de `pb`. Ahora `caja` dice `luna`.
5. El último `run` crea un contenedor nuevo que monta **el mismo** volumen `caja` en `/s`. `caja` ya no está vacío, así que Docker no le copia nada de la imagen.
6. El `CMD` `cat saludo.txt` lee `/s`. Dónde lee: el volumen `caja`. Imprime `luna`.

**Las reglas:** **Un volumen con nombre se llena desde la imagen sólo si está vacío.** **Un montaje tapa lo que la imagen tiene en esa ruta.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run -d --name pb -v caja:/s saludo:1 sleep 600` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. **`pb` corre y monta `caja` en `/s`.** | **`hola` (era nuevo y vacío: se copió de la imagen)** |  |
| `docker exec pb sh -c 'echo luna > saludo.txt'` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. `pb` corre y monta `caja` en `/s`. | **`luna` (lo escribió `pb` en la fila 3)** |  |
| `docker run --rm -v caja:/s saludo:1` | `hola` | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. `pb` corre y monta `caja` en `/s`. | `luna` (lo escribió `pb` en la fila 3) | **`luna`** |

**Compruébalo:**

```text
$ docker exec pb pwd
/s
$ docker inspect -f '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' pb
volume caja -> /s
$ docker run --rm -v caja:/s saludo:1
luna
```

**Error común:** `hola`, pensando que el último `run` lee la imagen. Monta `caja` en `/s`, y el volumen tapa a la imagen.
:::

::: problem {#xd-2-4 title="Fila 4 · ¿Qué imprime el run?"}
```bash
echo sol > saludo.txt
docker build -t saludo:1 .
docker run --rm -v caja:/s saludo:1
```
:::

::: hint {of="xd-2-4"}
Estado al terminar la fila 3, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 3 | la del inicio | la del build de la fila 1 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. `pb`: corre con la imagen de la fila 1 y monta `caja` en `/s`. | lo que escribió `pb` en la fila 3 | lo que imprimió la fila 3 |

¿Docker vuelve a llenar un volumen que ya tiene algo?
:::

::: answer {of="xd-2-4"}
**Respuesta:** **`luna`.**

**Por qué:**
1. `echo sol > saludo.txt` cambia tu carpeta. Nada más: ni la imagen, ni los contenedores, ni el volumen.
2. `docker build` lee tu `saludo.txt` (`sol`), arma una imagen nueva y le pone el nombre `saludo:1`. La imagen vieja (`hola`) sigue en disco, sin nombre.
3. **Un contenedor conserva la imagen con la que se creó.** `pa` y `pb` se crearon con la imagen vieja (`hola`) y siguen con ella.
4. El `run` crea un contenedor nuevo con la imagen nueva (`sol`) y monta `caja` en `/s`.
5. **Un volumen con nombre se llena desde la imagen sólo si está vacío.** `caja` ya tiene `luna` desde la fila 3, así que Docker no copia nada.
6. **Un montaje tapa lo que la imagen tiene en esa ruta.** El `CMD` `cat saludo.txt` lee `/s`. Dónde lee: el volumen `caja`, no la imagen. Imprime `luna`.

**Las reglas:** **Un contenedor conserva la imagen con la que se creó.** **Un volumen con nombre se llena desde la imagen sólo si está vacío.** **Un montaje tapa lo que la imagen tiene en esa ruta.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `echo sol > saludo.txt` | **`sol`** | `hola` (build de la fila 1) | `pa` corre; su capa tiene `adios`. `pb` corre y monta `caja` en `/s`. | `luna` (lo escribió `pb` en la fila 3) |  |
| `docker build -t saludo:1 .` | `sol` | **`sol` (build de la fila 4)** | **`pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa.** **`pb` corre con la imagen vieja (`hola`) y monta `caja` en `/s`.** | `luna` (lo escribió `pb` en la fila 3) |  |
| `docker run --rm -v caja:/s saludo:1` | `sol` | `sol` (build de la fila 4) | `pa`: igual; `pb`: igual | `luna` (lo escribió `pb` en la fila 3) | **`luna`** |

**Compruébalo:** `docker run --rm -v caja:/s saludo:1` → `luna`.

**Error común:** `sol`. La imagen nueva sí dice `sol`, pero en `/s` el volumen la tapa, y el volumen no se vuelve a llenar.
:::

::: problem {#xd-2-5 title="Fila 5 · ¿Qué imprime?"}
```bash
docker run --rm saludo:1
```
:::

::: hint {of="xd-2-5"}
Estado al terminar la fila 4, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 4 | lo que escribiste en la fila 4 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. `pb`: corre con la imagen de la fila 1 y monta `caja` en `/s`. | lo que escribió `pb` en la fila 3 | lo que imprimió la fila 4 |

Sin montaje, ¿qué dice la imagen después del último build?
:::

::: answer {of="xd-2-5"}
**Respuesta:** **`sol`.**

**Por qué:**
1. `docker run` crea un contenedor nuevo, con su capa escribible vacía.
2. No hay `-v`: en `/s` este contenedor sólo ve la imagen.
3. El nombre `saludo:1` apunta ahora a la imagen del build de la fila 4, que dice `sol`.
4. El `CMD` `cat saludo.txt` lee `/s`. Dónde lee: la imagen. Imprime `sol`.
5. El volumen `caja` (`luna`) existe, pero un volumen sólo se ve en el contenedor que lo monta.

**La regla:** **Un montaje tapa lo que la imagen tiene en esa ruta.** Sin montaje no hay nada que tape a la imagen.

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm -v caja:/s saludo:1` | `sol` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. `pb` corre con la imagen vieja (`hola`) y monta `caja` en `/s`. | `luna` (lo escribió `pb` en la fila 3) | **`luna`** |
| `docker run --rm saludo:1` | `sol` | `sol` (build de la fila 4) | `pa`: igual; `pb`: igual | `luna` (lo escribió `pb` en la fila 3) | **`sol`** |

**Compruébalo:** la misma imagen da dos respuestas según el montaje:

```text
$ docker run --rm -v caja:/s saludo:1
luna
$ docker run --rm saludo:1
sol
```

**Error común:** `luna`. El volumen `caja` no se ve si el `run` no lo monta.
:::

::: problem {#xd-2-6 title="Fila 6 · ¿Qué imprime?"}
```bash
docker exec pb cat saludo.txt
```
:::

::: hint {of="xd-2-6"}
Estado al terminar la fila 5, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 5 | lo que escribiste en la fila 4 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. `pb`: corre con la imagen de la fila 1 y monta `caja` en `/s`. | lo que escribió `pb` en la fila 3 | lo que imprimió la fila 5 |

¿Qué hay montado en `/s` dentro de `pb`?
:::

::: answer {of="xd-2-6"}
**Respuesta:** **`luna`.**

**Por qué:**
1. `docker exec pb` no crea un contenedor: corre `cat` dentro de `pb`, que sigue corriendo desde la fila 3.
2. `cat saludo.txt` usa una ruta relativa, así que lee en el `WORKDIR` del contenedor: `/s/saludo.txt`.
3. En `pb`, `/s` es el volumen `caja`: se montó con `-v caja:/s` en la fila 3. Dónde lee: el volumen `caja`.
4. `caja` dice `luna`. Lo escribió `pb` en la fila 3 con `echo luna > saludo.txt`, dentro de `/s`. Nadie lo cambió después: el `run` de la fila 4 no lo rellenó, porque **un volumen con nombre se llena desde la imagen sólo si está vacío** y `caja` ya tenía `luna`.
5. La imagen nueva (`sol`) no cuenta, por dos razones. Primera: **un contenedor conserva la imagen con la que se creó**, y `pb` se creó con la vieja (`hola`). Segunda: aunque `pb` usara la nueva, **un montaje tapa lo que la imagen tiene en esa ruta**.

**Las reglas:** **Un contenedor conserva la imagen con la que se creó.** **Un montaje tapa lo que la imagen tiene en esa ruta.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm saludo:1` | `sol` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. `pb` corre con la imagen vieja (`hola`) y monta `caja` en `/s`. | `luna` (lo escribió `pb` en la fila 3) | **`sol`** |
| `docker exec pb cat saludo.txt` | `sol` | `sol` (build de la fila 4) | `pa`: igual; `pb`: igual | `luna` (lo escribió `pb` en la fila 3) | **`luna`** |

**Compruébalo:**

```text
$ docker inspect -f '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' pb
volume caja -> /s
$ docker exec pb cat saludo.txt
luna
```

**Error común:** `sol`, pensando que `pb` ve la imagen del último build.
:::

::: problem {#xd-2-7 title="Fila 7 · ¿Qué imprime el run?"}
```bash
docker rm -f pb
docker volume rm caja
docker run --rm -v caja:/s saludo:1
```
:::

::: hint {of="xd-2-7"}
Estado al terminar la fila 6, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 6 | lo que escribiste en la fila 4 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. `pb`: corre con la imagen de la fila 1 y monta `caja` en `/s`. | lo que escribió `pb` en la fila 3 | lo que imprimió la fila 6 |

Si borras el volumen, el `caja` siguiente es nuevo. ¿Con qué se llena uno nuevo?
:::

::: answer {of="xd-2-7"}
**Respuesta:** **`sol`.**

**Por qué:**
1. `docker rm -f pb` detiene y borra `pb`. Hay que borrarlo primero: Docker no deja borrar un volumen que un contenedor usa (`volume is in use`).
2. `docker volume rm caja` borra el volumen, y con él `luna`.
3. El último `run` monta `caja` en `/s`. `caja` ya no existe, así que Docker crea uno **nuevo** y vacío con ese nombre.
4. **Un volumen con nombre se llena desde la imagen sólo si está vacío.** Este `caja` está vacío: Docker le copia el `/s` de la imagen actual, la del build de la fila 4, que dice `sol`.
5. El `CMD` `cat saludo.txt` lee `/s`. Dónde lee: el volumen `caja` nuevo. Imprime `sol`.
6. Al terminar, `--rm` borra el contenedor, pero **`--rm` no borra volúmenes con nombre**: `caja` sigue ahí, con `sol`.

**Las reglas:** **Un volumen con nombre se llena desde la imagen sólo si está vacío.** **`--rm` no borra volúmenes con nombre.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker rm -f pb` | `sol` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. **`pb` ya no existe.** | `luna` (lo escribió `pb` en la fila 3) |  |
| `docker volume rm caja` | `sol` | `sol` (build de la fila 4) | `pa`: igual | **no existe** |  |
| `docker run --rm -v caja:/s saludo:1` | `sol` | `sol` (build de la fila 4) | `pa`: igual | **`sol` (copiado de la imagen en la fila 7)** | **`sol`** |

**Compruébalo:**

```text
$ docker run --rm -v caja:/s saludo:1
sol
$ docker volume ls -q
caja
```

**Error común:** `luna`. El volumen que tenía `luna` se borró; el `caja` de este `run` es otro volumen con el mismo nombre.
:::

::: problem {#xd-2-8 title="Fila 8 · ¿Qué imprime?"}
```bash
docker exec pa cat saludo.txt
```
:::

::: hint {of="xd-2-8"}
Estado al terminar la fila 7, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 7 | lo que escribiste en la fila 4 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | lo que se copió de la imagen en la fila 7 | lo que imprimió la fila 7 |

¿Cambia un contenedor que ya existe cuando reconstruyes su imagen?
:::

::: answer {of="xd-2-8"}
**Respuesta:** **`adios`.**

**Por qué:**
1. `docker exec pa` corre `cat` dentro de `pa`, que existe desde la fila 1 y sigue corriendo.
2. **Un contenedor conserva la imagen con la que se creó.** `pa` nació en la fila 1 con la imagen `hola`. El build de la fila 4 movió el nombre `saludo:1` a una imagen nueva, pero no cambió a `pa`.
3. `pa` no monta nada: ni `caja` ni tu carpeta.
4. `cat saludo.txt` lee `/s/saludo.txt`. Dónde lee: la capa escribible de `pa`, donde está el `adios` de la fila 1, encima de la imagen vieja (`hola`). Imprime `adios`.

**Las reglas:** **Un contenedor conserva la imagen con la que se creó.** **La capa escribible sobrevive a `stop`/`start`, pero no a `rm`.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm -v caja:/s saludo:1` | `sol` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | **`sol` (copiado de la imagen en la fila 7)** | **`sol`** |
| `docker exec pa cat saludo.txt` | `sol` | `sol` (build de la fila 4) | `pa`: igual | `sol` (copiado de la imagen en la fila 7) | **`adios`** |

**Compruébalo:** la imagen de `pa` y la que hoy se llama `saludo:1` tienen identificadores distintos, y `pa` no tiene montajes:

```text
$ docker inspect -f '{{.Image}}' pa | cut -c1-19
sha256:2c54278b3d3f
$ docker image inspect -f '{{.Id}}' saludo:1 | cut -c1-19
sha256:03c95815ec57
$ docker inspect -f '{{len .Mounts}}' pa
0
$ docker exec pa cat saludo.txt
adios
```

**Error común:** `sol`, pensando que reconstruir la imagen actualiza los contenedores que ya existen.
:::

::: problem {#xd-2-9 title="Fila 9 · ¿Qué imprime cada run? (dos casillas)"}
```bash
echo nube > saludo.txt
docker run --rm -v "$(pwd)":/s saludo:1
docker run --rm saludo:1
```
:::

::: hint {of="xd-2-9"}
Estado al terminar la fila 8, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 8 | lo que escribiste en la fila 4 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | lo que se copió de la imagen en la fila 7 | lo que imprimió la fila 8 |

Con tu carpeta montada en `/s`, ¿qué lee? ¿Y sin montar nada?
:::

::: answer {of="xd-2-9"}
**Respuesta:**
- **Primer `run`: `nube`.**
- **Segundo `run`: `sol`.**

**Por qué:**
1. `echo nube > saludo.txt` cambia tu carpeta. La imagen no cambia: no hubo build.
2. El primer `run` monta tu carpeta `lab/` en `/s` con `-v "$(pwd)":/s`. Es un bind mount.
3. **Un montaje tapa lo que la imagen tiene en esa ruta.** En ese contenedor, `/s` es tu carpeta. Dónde lee: tu disco. Imprime `nube`.
4. El segundo `run` no monta nada. Dónde lee: la imagen `saludo:1`, que sigue siendo la del build de la fila 4. Imprime `sol`.

**La regla:** **Un montaje tapa lo que la imagen tiene en esa ruta.** Editar tu carpeta no cambia la imagen hasta el siguiente `docker build`.

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `echo nube > saludo.txt` | **`nube`** | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) |  |
| `docker run --rm -v "$(pwd)":/s saludo:1` | `nube` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`nube`** |
| `docker run --rm saludo:1` | `nube` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`sol`** |

**Compruébalo:**

```text
$ docker run --rm -v "$(pwd)":/s saludo:1
nube
$ docker run --rm saludo:1
sol
```

**Error común:** `nube` en el segundo. Tu carpeta sólo se ve dentro del contenedor que la monta.
:::

::: problem {#xd-2-10 title="Fila 10 · ¿El COPY sale de la caché?"}
```bash
docker build -t saludo:1 .
```
:::

::: hint {of="xd-2-10"}
Estado al terminar la fila 9, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 9 | lo que escribiste en la fila 9 | la del build de la fila 4 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | lo que se copió de la imagen en la fila 7 | lo que imprimió el segundo `run` de la fila 9 |

¿Cambió el contenido de tu `saludo.txt` desde el último build?
:::

::: answer {of="xd-2-10"}
**Respuesta:** **no, el `COPY saludo.txt .` se rehace.** El build no imprime ningún saludo; deja a `saludo:1` apuntando a una imagen nueva que dice `nube`.

**Por qué:**
1. `FROM alpine:3.20` y `WORKDIR /s` no leen tus archivos: salen de la caché.
2. `COPY saludo.txt .` lee tu `saludo.txt`, que ahora dice `nube` (fila 9).
3. El último build (fila 4) copió un `saludo.txt` que decía `sol`. No hay ninguna capa guardada con ese `COPY` y el contenido `nube`, así que el `COPY` se rehace.
4. El nombre `saludo:1` pasa a la imagen nueva (`nube`). **Un contenedor conserva la imagen con la que se creó.** `pa` sigue con la imagen `hola`.

**La regla:** **La caché de capas se busca por contenido.** Que el Dockerfile no haya cambiado no basta: también cuenta el contenido de lo que copia.

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm saludo:1` | `nube` | `sol` (build de la fila 4) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`sol`** |
| `docker build -t saludo:1 .` | `nube` | **`nube` (build de la fila 10)** | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | nada: es un build |

**Compruébalo:**

```text
$ docker build --progress=plain -t saludo:1 .
…
#6 [2/3] WORKDIR /s
#6 CACHED

#7 [3/3] COPY saludo.txt .
#7 DONE 0.0s
```

**Error común:** «sale de la caché porque el Dockerfile es el mismo». Docker compara el contenido de `saludo.txt`, no sólo las líneas del Dockerfile.

**Ojo al reproducirlo:** si ya corriste esta secuencia antes, los builds de las filas 4 y 10 pueden salir `CACHED`. La caché se busca por contenido, y una capa vieja con `sol` o con `nube` sigue guardada.
:::

::: problem {#xd-2-11 title="Fila 11 · ¿Qué imprime cada run? (dos casillas)"}
```bash
docker run --rm saludo:1 sh -c 'echo x > saludo.txt; cat saludo.txt'
docker run --rm saludo:1
```
:::

::: hint {of="xd-2-11"}
Estado al terminar la fila 10, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 10 | lo que escribiste en la fila 9 | la del build de la fila 10 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | lo que se copió de la imagen en la fila 7 | — |

¿De dónde lee un contenedor nuevo sin montaje?
:::

::: answer {of="xd-2-11"}
**Respuesta:**
- **Primer `run`: `x`.**
- **Segundo `run`: `nube`.**

**Por qué:**
1. En el primer `run`, `sh -c 'echo x > saludo.txt; cat saludo.txt'` va después de la imagen, y **lo que escribes después del nombre de la imagen reemplaza al `CMD`**.
2. Ese contenedor no monta nada. `echo x` escribe en `/s`, y eso cae en **la capa escribible de ese contenedor**. `cat` lee esa misma capa. Imprime `x`.
3. Al terminar, `--rm` borra el contenedor y, con él, su capa, porque **la capa escribible sobrevive a `stop`/`start`, pero no a `rm`**. La `x` desaparece.
4. El segundo `run` crea otro contenedor, con capa vacía y sin montajes. Corre el `CMD`. Dónde lee: la imagen `saludo:1`, que dice `nube` desde el build de la fila 10. Imprime `nube`.

**Las reglas:** **Lo que escribes después del nombre de la imagen reemplaza al `CMD`.** **La capa escribible sobrevive a `stop`/`start`, pero no a `rm`.**

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm saludo:1 sh -c 'echo x > saludo.txt; cat saludo.txt'` | `nube` | `nube` (build de la fila 10) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`x`** |
| `docker run --rm saludo:1` | `nube` | `nube` (build de la fila 10) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`nube`** |

**Compruébalo:**

```text
$ docker run --rm saludo:1 sh -c 'echo x > saludo.txt; cat saludo.txt'
x
$ docker run --rm saludo:1
nube
```

**Error común:** `x` en el segundo. Cada `docker run` crea un contenedor distinto, y la `x` vivía en la capa del primero.
:::

::: problem {#xd-2-12 title="Fila 12 · adios y luna, ¿dónde existen?"}
```bash
docker rm -f pa
```

Opciones: tu carpeta, la imagen, un volumen, en ningún lado.
:::

::: hint {of="xd-2-12"}
Estado al terminar la fila 11, escrito por su origen:

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| al terminar la fila 11 | lo que escribiste en la fila 9 | la del build de la fila 10 | `pa`: corre con la imagen de la fila 1; su capa tiene lo que escribió en la fila 1. | lo que se copió de la imagen en la fila 7 | lo que imprimió el segundo `run` de la fila 11 |

¿Dónde vivía cada palabra, y qué comando borró ese lugar?
:::

::: answer {of="xd-2-12"}
**Respuesta:**
- **`adios`: en ningún lado.**
- **`luna`: en ningún lado.**

**Por qué:**
1. `adios` vivía en la capa escribible de `pa` (fila 1). **La capa escribible sobrevive a `stop`/`start`, pero no a `rm`.** `docker rm -f pa` borró el contenedor `pa` y su capa.
2. `luna` vivía en el volumen `caja` de la fila 3. `docker volume rm caja` borró ese volumen en la fila 7.
3. El `caja` que existe hoy es otro volumen, creado en la fila 7, y dice `sol`.
4. Tu carpeta dice `nube`. La imagen `saludo:1` dice `nube`. Las imágenes viejas, sin nombre, dicen `hola` y `sol`: ninguna imagen tiene `adios` ni `luna`, porque ningún build copió esas palabras.

| Paso | `saludo.txt` en tu carpeta | Imagen `saludo:1` | Contenedores | Volumen `caja` | Imprime |
|---|---|---|---|---|---|
| `docker run --rm saludo:1` | `nube` | `nube` (build de la fila 10) | `pa` corre con la imagen vieja (`hola`) y tiene `adios` en su capa. | `sol` (copiado de la imagen en la fila 7) | **`nube`** |
| `docker rm -f pa` | `nube` | `nube` (build de la fila 10) | **ninguno** | `sol` (copiado de la imagen en la fila 7) |  |

| Lugar | Qué dice hoy | ¿`adios`? | ¿`luna`? |
|---|---|---|---|
| tu carpeta | `nube` | no | no |
| imagen `saludo:1` | `nube` | no | no |
| volumen `caja` | `sol` | no | no |
| contenedores | no queda ninguno | no | no |

**Compruébalo:**

```text
$ docker run --rm -v caja:/s saludo:1
sol
$ cat saludo.txt
nube
```

**Error común:** «`luna` sigue en un volumen». El volumen que la tenía se borró en la fila 7; el nombre `caja` lo reusa otro volumen.
:::

**Para recordar:**

- `stop` conserva la capa del contenedor; `rm` la borra.
- Un volumen vacío se llena con la imagen; uno con contenido tapa a la imagen.
- Un build nuevo no cambia los contenedores que ya existen.

**Repasa:** [[ciclo-de-vida-de-un-contenedor]], [[named-volumes-y-postgres]], [[donde-vive-cada-byte]] y [[los-ocho-casos]].

## Parte 3 · Lee el error

Cada caso trae el comando y lo que contestó Docker. Escribe **qué pasó** y **qué harías**.

::: problem {#xd-e1 title="Error 1 · Correr dos veces lo mismo"}
Justo después de la fila 1, alguien vuelve a correr la misma línea:

```text
$ docker run -d --name pa saludo:1 sleep 600
docker: Error response from daemon: Conflict. The container name "/pa" is already in use by container "94ec18da7a0a…". You have to remove (or rename) that container to be able to reuse that name.
```
:::

::: hint {of="xd-e1"}
Lee la palabra clave del mensaje: *Conflict*. ¿Qué ya existe?
:::

::: answer {of="xd-e1"}
**Respuesta:**
- **Qué pasó:** **ya existe un contenedor llamado `pa`, y dos contenedores no pueden tener el mismo nombre.** Docker no crea nada y sale con código 125. El `pa` de la fila 1 sigue igual.
- **Qué harías:** **si ya no lo necesitas, `docker rm -f pa` y vuelves a correr la línea; si sí lo necesitas, usa otro nombre en `--name`.**

**Por qué:**
1. La fila 1 creó el contenedor `pa` con `docker run -d --name pa …`. `pa` sigue corriendo, con `adios` en su capa.
2. `docker run` siempre intenta crear un contenedor nuevo. No reusa uno que ya existe, aunque el comando sea idéntico.
3. El nombre `pa` ya está ocupado: eso dice `Conflict … is already in use`.
4. `docker rm -f pa` libera el nombre, pero borra el contenedor y su capa: el `adios` se pierde.

**La regla:** **la capa escribible sobrevive a `stop`/`start`, pero no a `rm`.** Antes de liberar el nombre, decide si te importa lo que el contenedor escribió.

| Paso | Contenedor `pa` | Capa de `pa` |
|---|---|---|
| después de la fila 1 | corre | `adios` |
| `docker run -d --name pa …` otra vez | **el mismo**, corriendo: el nuevo no se crea | `adios` |
| `docker rm -f pa` | **no existe** | **borrada** |
| `docker run -d --name pa …` | **otro contenedor**, corriendo | **vacía** |

**Compruébalo:** después del error, `echo $?` → `125`.
:::

::: problem {#xd-e2 title="Error 2 · Un build que no arranca"}
```text
$ docker build -t saludo:1
ERROR: docker: 'docker buildx build' requires 1 argument

Usage:  docker buildx build [OPTIONS] PATH | URL | -
```
:::

::: hint {of="xd-e2"}
Compara con `docker build -t saludo:1 .`. ¿Qué falta?
:::

::: answer {of="xd-e2"}
**Respuesta:**
- **Qué pasó:** **falta el contexto, el `.` del final.** `docker build` necesita un argumento, la carpeta que se manda al build, y no recibió ninguno.
- **Qué harías:** **`docker build -t saludo:1 .`**

**Por qué:**
1. `-t saludo:1` es una opción: sólo dice qué nombre ponerle a la imagen.
2. Además de las opciones, `docker build` pide exactamente un argumento: el contexto (`PATH | URL | -` en el mensaje).
3. El contexto es la carpeta que Docker manda al build. Los `COPY` leen de ella, y por defecto el `Dockerfile` también se busca ahí.
4. `.` es la carpeta actual, `lab/`. Sin él, el build no sabe qué carpeta mandar y no arranca.
5. El mensaje dice `docker buildx build` porque en esta versión de Docker `docker build` corre a través de `buildx`. Es el mismo comando.
:::

::: problem {#xd-e3 title="Error 3 · Exec a un contenedor detenido"}
Después de `docker stop pa`:

```text
$ docker exec pa cat saludo.txt
Error response from daemon: container 94ec18da7a0a… is not running
```
:::

::: hint {of="xd-e3"}
¿En qué estado quedó pa después de `stop`? ¿En cuál tiene que estar para un `exec`?
:::

::: answer {of="xd-e3"}
**Respuesta:**
- **Qué pasó:** **`docker exec` sólo entra a un contenedor que está corriendo, y `pa` está detenido.**
- **Qué harías:** **`docker start pa` y luego el mismo `docker exec pa cat saludo.txt`.** Imprime `adios`.

**Por qué:**
1. `docker exec` corre un comando nuevo dentro de un contenedor que ya está corriendo. No arranca contenedores.
2. `docker stop pa` detuvo `pa`. El contenedor sigue existiendo, pero no corre: de ahí el `is not running`.
3. `docker start pa` lo vuelve a arrancar, con la misma capa.
4. La capa de `pa` todavía tiene `adios`, porque `stop` no la borró.

**La regla:** **la capa escribible sobrevive a `stop`/`start`, pero no a `rm`.**

| Paso | Estado de `pa` | Capa de `pa` | `docker exec pa cat saludo.txt` |
|---|---|---|---|
| `docker stop pa` | **detenido** | `adios` | falla: `is not running` |
| `docker start pa` | **corre** | `adios` | imprime `adios` |

**Compruébalo:** después del error, `echo $?` → `1`.
:::

::: problem {#xd-e4 title="Error 4 · Una terminal que no abre"}
```text
$ docker run --rm -it saludo:1 bash
docker: Error response from daemon: failed to create task for container: … exec: "bash": executable file not found in $PATH
```
:::

::: hint {of="xd-e4"}
¿Qué imagen base usa `saludo:1`, y qué shell trae esa imagen?
:::

::: answer {of="xd-e4"}
**Respuesta:**
- **Qué pasó:** **la imagen `saludo:1` está hecha sobre Alpine, y Alpine no trae `bash`: trae `sh`.**
- **Qué harías:** **`docker run --rm -it saludo:1 sh`.**

**Por qué:**
1. El Dockerfile de `saludo:1` empieza con `FROM alpine:3.20`. Todo lo que tiene la imagen viene de Alpine más el `saludo.txt` que copiaste.
2. `bash` va después del nombre de la imagen, así que **lo que escribes después del nombre de la imagen reemplaza al `CMD`**: Docker intenta ejecutar el programa `bash`.
3. Docker busca `bash` en las carpetas de `$PATH` dentro del contenedor y no lo encuentra: `executable file not found in $PATH`. El proceso no arranca.
4. Alpine trae `sh`. Con `sh`, `-it` te da una terminal dentro del contenedor.

**Error común:** pensar que el problema es `-it`. Sin `-it` el error es el mismo: lo que falta es el programa `bash` dentro de la imagen.
:::

::: problem {#xd-e5 title="Error 5 · Copiar desde fuera del contexto"}
Un Dockerfile en `proyecto/app/` tiene la línea `COPY ../datos /datos`, y se construye desde `proyecto/app/`:

```text
$ docker build -t app:1 .
ERROR: failed to build: failed to solve: failed to compute cache key: … "/datos": not found
```
:::

::: hint {of="xd-e5"}
¿Desde qué carpeta lee el build? ¿Puede un `COPY` salir de ella?
:::

::: answer {of="xd-e5"}
**Respuesta:**
- **Qué pasó:** **el contexto del build es `proyecto/app/`, y un `COPY` no puede leer nada fuera del contexto.** `../datos` no sube a `proyecto/`: Docker busca `datos` en la raíz del contexto, y en `proyecto/app/` no hay `datos`.
- **Qué harías:** **construir desde `proyecto/` con `docker build -t app:1 -f app/Dockerfile .`, y cambiar la línea a `COPY datos /datos`.** Si los datos son grandes o cambian seguido, mejor no copiarlos: montarlos al correr.

**Por qué:**
1. El `.` de `docker build -t app:1 .` es el contexto. Corriendo desde `proyecto/app/`, el contexto es `proyecto/app/`.
2. Docker sólo manda al build lo que hay dentro del contexto. Las rutas de origen de un `COPY` se leen desde la raíz del contexto.
3. Un `..` no puede pasar de esa raíz: Docker lo recorta y busca `/datos` en la raíz del contexto. Eso dice el mensaje: `"/datos": not found`.
4. Construyendo desde `proyecto/`, el contexto sí contiene `datos/`. `-f app/Dockerfile` le dice a Docker dónde está el Dockerfile, que ya no está en la carpeta del contexto.
5. Con el contexto nuevo, las rutas de origen de **todos** los `COPY` de ese Dockerfile se leen desde `proyecto/`. Por eso la línea pasa a `COPY datos /datos`; si hay otros `COPY`, también hay que ajustarlos.

**Compruébalo:** desde `proyecto/`, con la línea `COPY datos /datos`, `docker build -t app:1 -f app/Dockerfile .` termina sin error, y `/datos` dentro de la imagen tiene el contenido de `proyecto/datos/`.
:::

**Repasa:** [[anatomia-de-docker-run]], [[ciclo-de-vida-de-un-contenedor]] y [[las-cuatro-trampas]].
