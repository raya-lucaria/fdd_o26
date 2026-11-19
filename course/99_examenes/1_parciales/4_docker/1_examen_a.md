---
id: parcial-docker-a
title: "Parcial 4 · Docker · Examen A"
nav_title: "Examen A"
summary: "El examen A de Docker, pregunta por pregunta, con la respuesta explicada debajo de cada una: llevar el repo clima/ a una imagen, y seguir qué cambia entre tu carpeta, la imagen y cada contenedor."
status: ready
estimated_time: 25m
tags: [examen, parcial, docker, dockerfile, volumenes, cache]
---

# Parcial 4 · Docker · Examen A

**[PDF del examen A, sin respuestas](../../_assets/parcial-docker-a.pdf)** · 25 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Todas las respuestas se comprobaron corriendo los comandos con Docker 29.6.

## Ejercicio 1 · Del repo a la imagen (4 puntos)

```text
clima/            ← estás aquí
├── Dockerfile
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   └── utils.py
└── data/
    └── clima.csv
```

`clima/` es un repo de Python. El programa es `app/main.py`, y usa `app/utils.py`. En tu máquina los datos están en `data/`; dentro del contenedor el programa los lee de `/clima/data` y escribe ahí un resumen. Queremos la imagen `clima:1`, así:

- dentro de la imagen se trabaja en `/clima`, y ahí van `/clima/requirements.txt` y `/clima/app/`;
- al arrancar, el contenedor corre `python app/main.py` parado en `/clima`;
- `data/` **no** entra a la imagen: al correr, se monta en `/clima/data`.

En cada `COPY`, el origen es una ruta **relativa** a `clima/` (el contexto del build) y el destino es una ruta **absoluta** dentro de la imagen.

```text
FROM     python:3.12-slim
WORKDIR  (a) ________
COPY     requirements.txt (b) ________
RUN      pip install -r requirements.txt
COPY     (c) ________ /clima/app
CMD      (d) ________
```

::: problem {#pda-ad title="a–d · Completa el Dockerfile (0.25 cada hueco)"}
Llena los cuatro huecos.
:::

::: answer {of="pda-ad"}
```dockerfile
FROM python:3.12-slim
WORKDIR /clima
COPY requirements.txt /clima/
RUN pip install -r requirements.txt
COPY app /clima/app
CMD ["python", "app/main.py"]
```

- **(a) `/clima`.** `WORKDIR` fija dónde corre todo lo que sigue, en el build y al arrancar, y crea la carpeta si no existe. También valía `/clima/`.
- **(b) `/clima/`.** Con la barra final, el archivo queda como `/clima/requirements.txt`, justo donde lo busca el `pip install`. También valían `/clima/requirements.txt` y `/clima`. `.` funciona, pero el enunciado pedía ruta absoluta.
- **(c) `app`.** El origen se lee **del contexto**, que es `clima/`. También valían `app/` y `./app`. `.` valía cero: mete `data/` y `README.md`, y anida mal (`/clima/app/app/`).
- **(d) `["python", "app/main.py"]`.** `CMD` es lo que corre **al arrancar**, y hace falta el intérprete. También valían la ruta absoluta, `python3` o la forma shell. `RUN` en lugar de `CMD` valía cero: correría el programa una sola vez, durante el build.
:::

Escribe cada comando completo. Tu terminal está en `clima/`.

::: problem {#pda-e title="e · Construye la imagen clima:1 (0.5)"}
Escribe el comando.
:::

::: answer {of="pda-e"}
```bash
docker build -t clima:1 .
```

`-t clima:1` le pone nombre y etiqueta. El `.` final es el **contexto**: la carpeta cuyos archivos puede ver el build. Sin el `.`, el comando falla (cero). Sin `-t`, la imagen queda sin nombre (la mitad).
:::

::: problem {#pda-f title="f · Corre con los datos montados (0.5)"}
El programa lee los datos de `/clima/data`. Corre `clima:1` en un contenedor que se borre al terminar y que monte tu carpeta `data/` en `/clima/data`.
:::

::: answer {of="pda-f"}
```bash
docker run --rm -v "$(pwd)/data":/clima/data clima:1
```

- `--rm` borra el contenedor al terminar.
- `-v carpeta-de-tu-máquina:ruta-del-contenedor` monta tu carpeta.
- La imagen va al final, sin nada detrás: lo que va detrás reemplaza al `CMD`.

**También valía:** `$PWD/data`, `./data`, la ruta absoluta, o `--mount type=bind,…`.

**La trampa:** `-v data:/clima/data`, sin `./`, **no** monta tu carpeta. Un nombre sin `/` crea un named volume vacío, y el programa no encuentra `clima.csv` (comprobado: `FileNotFoundError`).
:::

::: problem {#pda-g title="g · Una terminal en un contenedor nuevo (0.5)"}
Abre una terminal `bash` en un contenedor **nuevo** de `clima:1`, que se borre al salir, para revisar `/clima`.
:::

::: answer {of="pda-g"}
```bash
docker run --rm -it clima:1 bash
```

`bash` después de la imagen reemplaza al `CMD`. `-it` le da una terminal y le conecta tu teclado; sin eso, bash termina en el acto (la mitad). Sin `bash` corre el programa (la mitad). `docker exec` valía cero: entra a un contenedor que **ya** está corriendo, y aquí no hay ninguno.
:::

::: problem {#pda-h title="h · ¿Qué queda dentro de la imagen? (0.5)"}
Con el Dockerfile ya completo, ¿qué archivos del repo quedan **dentro de la imagen**? `Dockerfile` · `README.md` · `requirements.txt` · `app/main.py` · `app/utils.py` · `data/clima.csv`
:::

::: answer {of="pda-h"}
**Sólo `requirements.txt`, `app/main.py` y `app/utils.py`.** A la imagen entra lo que un `COPY` mete, nada más. Nadie copia el Dockerfile ni el README, y `data/` se monta al correr.
:::

::: problem {#pda-i title="i · Build desde clima/app/ (0.5)"}
Alguien entra a `clima/app/` (`cd app`) y desde ahí corre `docker build -t clima:1 -f ../Dockerfile .` ¿El build termina bien? ¿Por qué?
:::

::: answer {of="pda-i"}
**No.** Falla en un `COPY` con `"/requirements.txt": not found` o `"/app": not found` (comprobado).

**Por qué.** El `.` es el contexto, y parado en `app/` el contexto es `clima/app/`: ahí no hay `requirements.txt` ni una carpeta `app/`. `-f ../Dockerfile` sólo dice qué instrucciones leer; **no** mueve el contexto.

**También valía** explicar que funcionaría con `..` como contexto. «No encuentra el Dockerfile» valía poco: `-f` sí lo encuentra.
:::

::: problem {#pda-j title="j · ¿Dónde queda lo que escribe el programa? (0.5)"}
En f), el programa escribe `/clima/data/resumen.csv` y luego el contenedor se borra. ¿Dónde existe ahora ese archivo: en tu carpeta `data/`, en la imagen o en ningún lado? ¿Y si lo hubiera escrito en `/clima/resumen.csv`?
:::

::: answer {of="pda-j"}
- **`/clima/data/resumen.csv`: en tu carpeta `data/`.** Era tu carpeta montada, y borrar el contenedor no toca tu disco.
- **`/clima/resumen.csv`: en ningún lado.** Cayó en la capa de escritura del contenedor, que se borra con él.

Un contenedor **nunca** escribe en la imagen: «en la imagen» valía cero.
:::

**Repasa:** [[el-dockerfile-por-dentro]], [[rutas-en-docker]], [[anatomia-de-docker-run]] y [[donde-vive-cada-byte]].

## Ejercicio 2 · ¿Qué cambió? (6 puntos, 0.5 por casilla)

En `lab/` hay sólo este Dockerfile y `nota.txt`, cuyo texto es la palabra **uno**:

```dockerfile
FROM alpine:3.20
WORKDIR /w
COPY nota.txt .
CMD ["cat", "nota.txt"]
```

No existen imágenes, contenedores, volúmenes ni caché previos. Los comandos se corren **en orden**, todos desde `lab/`, y ningún `sleep 600` alcanza a terminar. Cada fila parte de lo que dejó la anterior. Contesta con una palabra, o **error** si crees que un comando falla.

Antes de empezar, ten en cuenta que hay tres lugares que guardan un `nota.txt`:

| Lugar | Cambia cuando… |
|---|---|
| Tu carpeta `lab/` | la editas tú, o la escribe un contenedor que la tiene montada |
| La imagen `nota:1` | corres `docker build`, que copia lo que hay en tu carpeta en ese momento |
| La capa de escritura de cada contenedor | ese contenedor escribe en una ruta que no está montada |

::: problem {#pda-2-1 title="Fila 1 · ¿Qué contiene nota.txt en tu carpeta?"}
```bash
docker build -t nota:1 .
docker run -d --name c1 nota:1 sleep 600
docker exec c1 sh -c 'echo dos > nota.txt'
```
:::

::: answer {of="pda-2-1"}
**`uno`.** c1 no tiene nada montado, así que escribió en **su** capa de escritura. Tu carpeta no se enteró.
:::

::: problem {#pda-2-2 title="Fila 2 · ¿El COPY sale de la caché? ¿Por qué?"}
```bash
docker build -t nota:1 .
```
:::

::: answer {of="pda-2-2"}
**Sale de la caché.** El build lee **tu carpeta**, y ahí `nota.txt` sigue diciendo `uno`. Lo que hay dentro de c1 no es parte del contexto. Valía «caché», «CACHED» o «no se ejecuta», con ese porqué.

**Compruébalo:** `docker build --progress=plain -t nota:1 .` imprime `CACHED` debajo del `COPY`.
:::

::: problem {#pda-2-3 title="Fila 3 · ¿Qué imprime el run? ¿Y el exec? (dos casillas)"}
```bash
echo tres > nota.txt
docker run --rm nota:1
docker exec c1 cat nota.txt
```
:::

::: answer {of="pda-2-3"}
- **run: `uno`.** Un contenedor nuevo lee la imagen, y no ha habido build desde que editaste tu carpeta.
- **exec: `dos`.** c1 sigue vivo y conserva su capa de escritura.
:::

::: problem {#pda-2-4 title="Fila 4 · ¿Qué imprime el run?"}
```bash
docker build -t nota:1 .
docker run --rm nota:1
```
:::

::: answer {of="pda-2-4"}
**`tres`.** Ahora sí hubo build, y copió tu carpeta, que dice `tres`.
:::

::: problem {#pda-2-5 title="Fila 5 · ¿Qué contiene nota.txt en tu carpeta?"}
```bash
docker run -d --name c2 -v "$(pwd)":/w nota:1 sleep 600
docker exec c2 sh -c 'echo cuatro > nota.txt'
```
:::

::: answer {of="pda-2-5"}
**`cuatro`.** c2 tiene tu carpeta montada en `/w`: escribir ahí es escribir en tu disco.
:::

::: problem {#pda-2-6 title="Fila 6 · ¿Qué imprime?"}
```bash
docker run --rm nota:1
```
:::

::: answer {of="pda-2-6"}
**`tres`.** Contenedor nuevo, sin montaje: lee la imagen, y el último build fue el de la fila 4.
:::

::: problem {#pda-2-7 title="Fila 7 · ¿Qué imprime el exec?"}
```bash
echo cinco > nota.txt
docker exec c2 cat nota.txt
```
:::

::: answer {of="pda-2-7"}
**`cinco`.** El montaje funciona en las dos direcciones: c2 lee tu disco al instante, sin build ni reinicio.
:::

::: problem {#pda-2-8 title="Fila 8 · El texto dos, ¿dónde existe ahora?"}
```bash
docker rm -f c1 c2
```

Opciones: tu carpeta, la imagen, en ningún lado.
:::

::: answer {of="pda-2-8"}
**En ningún lado.** `dos` sólo vivía en la capa de escritura de c1, y `docker rm` se la llevó. Tu carpeta dice `cinco` y la imagen dice `tres`.
:::

::: problem {#pda-2-9 title="Fila 9 · ¿Qué imprime?"}
```bash
echo seis > extra.txt
docker run --rm -v "$(pwd)/extra.txt":/w/nota.txt nota:1
```
:::

::: answer {of="pda-2-9"}
**`seis`.** También se puede montar **un archivo** suelto: `extra.txt` tapa el `nota.txt` de la imagen.
:::

::: problem {#pda-2-10 title="Fila 10 · ¿Qué imprime el run?"}
```bash
docker build -t nota:1 .
docker run --rm -v almacen:/w nota:1
```
:::

::: answer {of="pda-2-10"}
**`cinco`.**

1. El build copió tu carpeta, que dice `cinco`.
2. `almacen` es un named volume que no existía. Docker lo crea **vacío**, y por estar vacío le copia lo que la imagen tiene en `/w`.
:::

::: problem {#pda-2-11 title="Fila 11 · ¿Qué imprime el run?"}
```bash
echo siete > nota.txt
docker build -t nota:1 .
docker run --rm -v almacen:/w nota:1
```
:::

::: answer {of="pda-2-11"}
**`cinco`.** La imagen ya dice `siete`, pero `almacen` ya **no** está vacío: tapa a la imagen, y Docker no lo vuelve a llenar. Por eso un volumen sobrevive a una imagen nueva, que es lo que permite actualizar una base de datos sin perder sus datos.
:::

**Repasa:** [[lab-sin-volumen]], [[lab-con-volumen]], [[capas-y-cache]], [[named-volumes-y-postgres]] y [[los-ocho-casos]].
