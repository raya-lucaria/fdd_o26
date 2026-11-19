---
id: parcial-docker-b
title: "Parcial 4 · Docker · Examen B"
nav_title: "Examen B"
summary: "El examen B de Docker, pregunta por pregunta, con la respuesta explicada debajo de cada una: llevar el repo ventas/ a una imagen, y seguir qué cambia entre tu carpeta, la imagen y cada contenedor."
status: ready
estimated_time: 25m
tags: [examen, parcial, docker, dockerfile, volumenes, cache]
---

# Parcial 4 · Docker · Examen B

**[PDF del examen B, sin respuestas](../../_assets/parcial-docker-b.pdf)** · 25 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Todas las respuestas se comprobaron corriendo los comandos con Docker 29.6.

## Ejercicio 1 · Del repo a la imagen (4 puntos)

```text
ventas/           ← estás aquí
├── Dockerfile
├── README.md
├── requirements.txt
├── src/
│   ├── cargar.py
│   └── formatos.py
└── entrada/
    └── enero.csv
```

`ventas/` es un repo de Python. El programa es `src/cargar.py`, y usa `src/formatos.py`. En tu máquina los CSV están en `entrada/`; dentro del contenedor el programa los lee de `/datos` y escribe ahí uno limpio. Queremos la imagen `ventas:1`, así:

- dentro de la imagen se trabaja en `/ventas`, y ahí van `/ventas/requirements.txt` y `/ventas/src/`;
- al arrancar, el contenedor corre `python src/cargar.py` parado en `/ventas`;
- `entrada/` **no** entra a la imagen: al correr, se monta en `/datos`.

En cada `COPY`, el origen es una ruta **relativa** a `ventas/` (el contexto del build) y el destino es una ruta **absoluta** dentro de la imagen.

```text
FROM     python:3.12-slim
WORKDIR  (a) ________
COPY     requirements.txt (b) ________
RUN      pip install -r requirements.txt
COPY     (c) ________ /ventas/src
CMD      (d) ________
```

::: problem {#pdb-ad title="a–d · Completa el Dockerfile (0.25 cada hueco)"}
Llena los cuatro huecos.
:::

::: answer {of="pdb-ad"}
```dockerfile
FROM python:3.12-slim
WORKDIR /ventas
COPY requirements.txt /ventas/
RUN pip install -r requirements.txt
COPY src /ventas/src
CMD ["python", "src/cargar.py"]
```

- **(a) `/ventas`.** Dónde corre todo lo que sigue, en el build y al arrancar. También valía `/ventas/`.
- **(b) `/ventas/`.** El archivo queda donde lo busca el `pip install`. También valían `/ventas/requirements.txt` y `/ventas`. `.` funciona, pero se pedía ruta absoluta.
- **(c) `src`.** Se lee del contexto, `ventas/`. También valían `src/` y `./src`. `.` valía cero: mete `entrada/` y `README.md`, y anida mal.
- **(d) `["python", "src/cargar.py"]`.** Lo que corre al arrancar, con su intérprete. `RUN` en lugar de `CMD` valía cero.
:::

Escribe cada comando completo. Tu terminal está en `ventas/`.

::: problem {#pdb-e title="e · Construye la imagen ventas:1 (0.5)"}
Escribe el comando.
:::

::: answer {of="pdb-e"}
```bash
docker build -t ventas:1 .
```

El `.` final es el contexto: sin él, el comando falla. Sin `-t`, la imagen queda sin nombre.
:::

::: problem {#pdb-f title="f · Una terminal en un contenedor nuevo (0.5)"}
Abre una terminal `bash` en un contenedor **nuevo** de `ventas:1`, que se borre al salir, para revisar `/ventas`.
:::

::: answer {of="pdb-f"}
```bash
docker run --rm -it ventas:1 bash
```

`bash` reemplaza al `CMD`, y `-it` le conecta tu teclado. `docker exec` valía cero: no hay ningún contenedor vivo. Ojo: en el examen A, este inciso era el g).
:::

::: problem {#pdb-g title="g · Corre con los datos montados (0.5)"}
El programa lee los datos de `/datos`. Corre `ventas:1` en un contenedor que se borre al terminar y que monte tu carpeta `entrada/` en `/datos`.
:::

::: answer {of="pdb-g"}
```bash
docker run --rm -v "$(pwd)/entrada":/datos ventas:1
```

**También valía:** `$PWD`, `./entrada`, la ruta absoluta, o `--mount type=bind,…`.

**La trampa:** `-v entrada:/datos`, sin `./`, crea un named volume vacío llamado `entrada`, y el programa no encuentra `enero.csv` (comprobado).
:::

::: problem {#pdb-h title="h · ¿Qué queda dentro de la imagen? (0.5)"}
Con el Dockerfile ya completo, ¿qué archivos del repo quedan **dentro de la imagen**? `Dockerfile` · `README.md` · `requirements.txt` · `src/cargar.py` · `src/formatos.py` · `entrada/enero.csv`
:::

::: answer {of="pdb-h"}
**Sólo `requirements.txt`, `src/cargar.py` y `src/formatos.py`.** Lo que mete un `COPY`, nada más.
:::

::: problem {#pdb-i title="i · Build desde ventas/src/ (0.5)"}
Alguien entra a `ventas/src/` (`cd src`) y desde ahí corre `docker build -t ventas:1 -f ../Dockerfile .` ¿El build termina bien? ¿Por qué?
:::

::: answer {of="pdb-i"}
**No.** Parado en `src/`, el contexto es `ventas/src/`, donde no hay `requirements.txt` ni una carpeta `src/`. Falla en un `COPY` con `"/requirements.txt": not found` o `"/src": not found`. `-f ../Dockerfile` no mueve el contexto.

(La clave impresa para calificar decía `"/app"` en este inciso; en el examen B la carpeta es `src`.)
:::

::: problem {#pdb-j title="j · ¿Dónde queda lo que escribe el programa? (0.5)"}
En g), el programa escribe `/datos/limpio.csv` y luego el contenedor se borra. ¿Dónde existe ahora ese archivo: en tu carpeta `entrada/`, en la imagen o en ningún lado? ¿Y si lo hubiera escrito en `/ventas/limpio.csv`?
:::

::: answer {of="pdb-j"}
- **`/datos/limpio.csv`: en tu carpeta `entrada/`**, porque `/datos` era tu carpeta montada.
- **`/ventas/limpio.csv`: en ningún lado.** Cayó en la capa de escritura, que se borró con el contenedor.
:::

**Repasa:** [[el-dockerfile-por-dentro]], [[rutas-en-docker]], [[anatomia-de-docker-run]] y [[donde-vive-cada-byte]].

## Ejercicio 2 · ¿Qué cambió? (6 puntos, 0.5 por casilla)

En `cfg/` hay sólo este Dockerfile y `color.txt`, cuyo texto es la palabra **rojo**:

```dockerfile
FROM alpine:3.20
WORKDIR /cfg
COPY color.txt .
CMD ["cat", "color.txt"]
```

No existen imágenes, contenedores, volúmenes ni caché previos. Los comandos se corren **en orden**, todos desde `cfg/`, y ningún `sleep 600` alcanza a terminar. Cada fila parte de lo que dejó la anterior. Contesta con una palabra, o **error** si crees que un comando falla.

En cada fila, pregúntate: ¿este contenedor lee la imagen, tu carpeta, un volumen o su propia capa de escritura?

::: problem {#pdb-2-1 title="Fila 1 · ¿Qué imprime el exec?"}
```bash
docker build -t color:1 .
docker run -d --name k1 -v "$(pwd)":/cfg color:1 sleep 600
echo verde > color.txt
docker exec k1 cat color.txt
```
:::

::: answer {of="pdb-2-1"}
**`verde`.** k1 tiene tu carpeta montada en `/cfg`: lee tu disco al instante, sin build.
:::

::: problem {#pdb-2-2 title="Fila 2 · ¿Qué imprime?"}
```bash
docker run --rm color:1
```
:::

::: answer {of="pdb-2-2"}
**`rojo`.** Contenedor nuevo, sin montaje: lee la imagen, que se construyó cuando tu carpeta decía `rojo`.
:::

::: problem {#pdb-2-3 title="Fila 3 · ¿Qué contiene color.txt en tu carpeta?"}
```bash
docker build -t color:1 .
docker run -d --name k2 color:1 sleep 600
docker exec k2 sh -c 'echo azul > color.txt'
```
:::

::: answer {of="pdb-2-3"}
**`verde`.** El build metió `verde` en la imagen, y el `azul` cayó en la capa de escritura de k2, que no tiene nada montado.
:::

::: problem {#pdb-2-4 title="Fila 4 · ¿El COPY sale de la caché? ¿Por qué?"}
```bash
docker build -t color:1 .
```
:::

::: answer {of="pdb-2-4"}
**Sale de la caché.** Tu carpeta no cambió desde el build de la fila 3: sigue diciendo `verde`. Lo que escribió k2 no es parte del contexto.
:::

::: problem {#pdb-2-5 title="Fila 5 · ¿Qué imprime el run? ¿Y el exec? (dos casillas)"}
```bash
docker run --rm color:1
docker exec k2 cat color.txt
```
:::

::: answer {of="pdb-2-5"}
- **run: `verde`.** La imagen tiene `verde`.
- **exec: `azul`.** k2 conserva su capa de escritura.
:::

::: problem {#pdb-2-6 title="Fila 6 · ¿Qué contiene color.txt en tu carpeta?"}
```bash
docker exec k1 sh -c 'echo gris > color.txt'
```
:::

::: answer {of="pdb-2-6"}
**`gris`.** k1 escribe en `/cfg`, que es tu carpeta.
:::

::: problem {#pdb-2-7 title="Fila 7 · ¿Qué imprime?"}
```bash
docker run --rm color:1
```
:::

::: answer {of="pdb-2-7"}
**`verde`.** La imagen no se enteró: no ha habido build desde la fila 3.
:::

::: problem {#pdb-2-8 title="Fila 8 · El texto azul, ¿dónde existe ahora?"}
```bash
docker rm -f k1 k2
```

Opciones: tu carpeta, la imagen, en ningún lado.
:::

::: answer {of="pdb-2-8"}
**En ningún lado.** `azul` vivía sólo en la capa de k2, y `docker rm` se la llevó. Tu carpeta dice `gris` y la imagen `verde`.
:::

::: problem {#pdb-2-9 title="Fila 9 · ¿Qué imprime?"}
```bash
echo negro > otro.txt
docker run --rm -v "$(pwd)/otro.txt":/cfg/color.txt color:1
```
:::

::: answer {of="pdb-2-9"}
**`negro`.** Montar un archivo: `otro.txt` tapa el `color.txt` de la imagen.
:::

::: problem {#pdb-2-10 title="Fila 10 · ¿Qué imprime el run?"}
```bash
docker build -t color:1 .
docker run --rm -v bodega:/cfg color:1
```
:::

::: answer {of="pdb-2-10"}
**`gris`.** El build metió `gris`, lo que había en tu carpeta, en la imagen. `bodega` no existía: Docker lo crea vacío y le copia el `/cfg` de la imagen.
:::

::: problem {#pdb-2-11 title="Fila 11 · ¿Qué imprime el run?"}
```bash
echo blanco > color.txt
docker build -t color:1 .
docker run --rm -v bodega:/cfg color:1
```
:::

::: answer {of="pdb-2-11"}
**`gris`.** La imagen ya dice `blanco`, pero `bodega` ya no está vacío: tapa a la imagen.
:::

**Repasa:** [[lab-sin-volumen]], [[lab-con-volumen]], [[capas-y-cache]], [[named-volumes-y-postgres]] y [[los-ocho-casos]].
