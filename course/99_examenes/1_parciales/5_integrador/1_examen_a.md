---
id: parcial-integrador-a
title: "Parcial 5 · Integrador · Examen A"
nav_title: "Examen A"
summary: "El examen A del parcial integrador, pregunta por pregunta, con la respuesta explicada debajo: el programa precio/envio, un modelo de 20B en la nube, accesos.log, el script nocturno con pandas y el repo tienda/."
status: ready
estimated_time: 75m
tags: [examen, parcial, arquitectura, terminal, regex, git, docker, volumenes]
---

# Parcial 5 · Integrador · Examen A

**[PDF del examen A, sin respuestas](../../_assets/parcial-integrador-a.pdf)** · 75 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Donde dice **Porqué**, una respuesta sin porqué vale cero. Donde se pide **Cuenta**, un número sin cuenta vale la mitad.

Las rutas se comprobaron con `os.path.normpath`, las regex con `grep -E`, y todo el bloque 4 se corrió con Git y Docker 29.6 (`alpine:3.20`).

## 1. Arquitectura (3 puntos)

### 1a · Del SSD al registro (1.5 puntos)

Modelo simplificado. La CPU sólo calcula con lo que tiene en sus **registros**. `LOAD` copia un dato a un registro: si el dato está en la **caché** (dentro del chip, pequeña, guarda lo que se usó hace poco), lo toma de ahí; si no, va hasta la **RAM** (fuera del chip, grande y mucho más lenta) y **deja una copia en la caché**. Los tiempos de la tabla son el total de cada instrucción, y nada se borra de la caché durante el ejercicio.

| Instrucción | Qué hace | Tarda |
|---|---|---|
| `LOAD  r, [x]` | trae x a un registro | 2 ns si x está en caché · 100 ns si va a RAM |
| `ADD   r, r, r` | suma dos registros | 1 ns |
| `STORE [x], r` | guarda un registro | 2 ns |

```text
LOAD  r1, [precio]  ; en caché
LOAD  r2, [envio]   ; NO en caché
ADD   r3, r1, r2
STORE [total], r3
```

::: problem {#pia-1a-i title="1a (i) · El orden de la jerarquía (0.25)"}
Ordena estos niveles de la jerarquía, desde donde se guarda el dato hasta donde la CPU lo usa: **L1 · RAM · registro · SSD · L3**.
:::

::: answer {of="pia-1a-i"}
**SSD → RAM → L3 → L1 → registro.**

Todo o nada. El orden contrario (registro → … → SSD) valía cero, porque no es lo que se pidió: la pregunta dice **desde donde se guarda** el dato.
:::

::: problem {#pia-1a-ii title="1a (ii) · Una tras otra (0.25)"}
La CPU ejecuta las cuatro instrucciones **una tras otra**. ¿Cuántos ns tarda?
:::

::: answer {of="pia-1a-ii"}
2 + 100 + 1 + 2 = **105 ns**.

El `LOAD` de `precio` está en caché (2 ns) y el de `envio` va a RAM (100 ns).
:::

::: problem {#pia-1a-iii title="1a (iii) · Otra vez (0.5)"}
Enseguida corres **otra vez** las cuatro instrucciones, con la caché como la dejó (ii). ¿Cuántos ns tarda? **Porqué** cambió.
:::

::: answer {of="pia-1a-iii"}
2 + 2 + 1 + 2 = **7 ns**.

**Porqué:** el primer `LOAD` de `envio` dejó una copia en la caché, así que la segunda vez ya no va a RAM.

0.25 por el número y 0.25 por el porqué. Sin porqué no pasaba de 0.25.
:::

::: problem {#pia-1a-iv title="1a (iv) · El doble de GHz (0.5)"}
Otra CPU, con el **doble de GHz**, corre el programa desde el inicio (`envio` NO está en caché). `ADD`, `STORE` y un `LOAD` desde caché tardan la mitad; un `LOAD` que va a RAM sigue tardando 100 ns. ¿Cuántos ns tarda? **Porqué** no tarda la mitad.
:::

::: answer {of="pia-1a-iv"}
1 + 100 + 0.5 + 1 = **102.5 ns**.

**Porqué:** lo que pasa dentro del chip se acelera, pero la espera a la RAM no. Casi todo el tiempo era esa espera: 100 de los 105 ns.

0.25 por el número y 0.25 por el porqué. Con el número mal, pero un porqué que dice que la RAM no se acelera, valía 0.25.
:::

### 1b · Elegir una máquina en la nube (1.5 puntos)

| Máquina | vCPU | RAM | GPU (memoria) | USD/hora |
|---|---|---|---|---|
| `std-8` | 8 | 32 GB | — | 0.40 |
| `mem-64` | 64 | 512 GB | — | 3.20 |
| `gpu-rtx4000` | 8 | 64 GB | 1 NVIDIA RTX 4000 Ada (20 GB) | 1.10 |
| `gpu-l40s` | 16 | 128 GB | 1 NVIDIA L40S (48 GB) | 2.90 |

Vas a rentar una máquina para servir a un chatbot un modelo de lenguaje de **20B parámetros en INT8**. La inferencia es, sobre todo, multiplicar matrices, y los pesos deben caber completos en la memoria de la GPU. Además de los pesos, reserva **20 %** extra (caché KV y temporales).

Memoria de los pesos = parámetros × bytes por parámetro. FP16 = 2 bytes · INT8 = 1 byte · INT4 = 0.5 bytes. 20B = 20 × 10⁹ parámetros. 1 GB = 10⁹ bytes.

::: problem {#pia-1b-i title="1b (i) · Los pesos (0.25)"}
¿Cuántos GB ocupan los pesos? Cuenta.
:::

::: answer {of="pia-1b-i"}
20 × 10⁹ × 1 byte = **20 GB**.
:::

::: problem {#pia-1b-ii title="1b (ii) · Con el 20 % extra (0.25)"}
¿Cuántos GB necesitas con el 20 % extra? Cuenta.
:::

::: answer {of="pia-1b-ii"}
20 × 1.2 = **24 GB**.

Con (i) mal, pero (ii) igual a «su número × 1.2», valía completo.
:::

::: problem {#pia-1b-iii title="1b (iii) · ¿Cabe? (0.25)"}
¿Cabe en la GPU de `gpu-rtx4000`? ¿Y en la de `gpu-l40s`? Porqué.
:::

::: answer {of="pia-1b-iii"}
- **`gpu-rtx4000`: no.** Su RTX 4000 Ada tiene 20 GB, y 20 < 24.
- **`gpu-l40s`: sí.** Su L40S tiene 48 GB, y 48 ≥ 24.

**La trampa:** quien olvida el 20 % extra compara 20 con 20 y dice que sí cabe en la RTX 4000. Eso valía cero. Se calificaba contra el número que cada quien dio en (ii).
:::

::: problem {#pia-1b-iv title="1b (iv) · ¿Qué máquina rentas? (0.5)"}
¿Qué máquina rentas? Porqué no cada una de las otras tres.
:::

::: answer {of="pia-1b-iv"}
**`gpu-l40s`.** Hay que descartar las otras tres:

- **`std-8`** no tiene GPU, y además sus 32 GB de RAM apenas cubren los 24 GB.
- **`mem-64`** tiene RAM de sobra, pero no tiene GPU, y la inferencia es multiplicar matrices.
- **`gpu-rtx4000`** tiene GPU, pero sus 20 GB no alcanzan para 24.

`gpu-l40s` con las tres razones valía 0.5. Con una o dos, 0.25.
:::

::: problem {#pia-1b-v title="1b (v) · Usar la máquina chica (0.25)"}
Para usar `gpu-rtx4000` sin cambiar los 20B: ¿qué formato, y cuántos GB con el 20 %? Cuenta. ¿Qué pierdes?
:::

::: answer {of="pia-1b-v"}
**INT4**: 20 × 0.5 = 10 GB, que con el 20 % son **12 GB** y caben en 20.

Es el único formato que cabe: INT8 es el formato actual (24 GB) y FP16 ocupa más. Se puede perder algo de **calidad o precisión** en las respuestas.

Hacían falta las tres cosas: formato, GB y qué se pierde. Con dos de ellas, 0.15.
:::

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]] e [[ia-escala-decision|IA, escala y selección de hardware]].

## 2. Terminal y regex (2 puntos)

### 2a · Rutas (1 punto, 0.25 cada una)

```text
/
├── home/
│   └── ana/
│       └── fdd/
│           ├── datos/
│           │   └── accesos.log
│           └── scripts/
│               └── limpia.sh
└── tmp/
    └── respaldo/
```

Quieres copiar `accesos.log` a la carpeta `respaldo/`. En cada caso escribe el `cp` con el tipo de ruta que pide la tabla. Una ruta absoluta empieza en `/` y no depende de dónde estés; una relativa parte del directorio actual: `..` sube un nivel y `.` es donde estás.

| # | Estás en | Origen | Destino |
|---|---|---|---|
| 1 | `/` | relativa | relativa |
| 2 | `/home/ana/fdd/scripts/` | relativa | absoluta |
| 3 | `/tmp/respaldo/` | absoluta | relativa |
| 4 | `/home/ana/fdd/datos/` | relativa | relativa |

::: problem {#pia-2a-1 title="2a · 1 · Desde /, relativa → relativa"}
Escribe el `cp`.
:::

::: answer {of="pia-2a-1"}
```bash
cp home/ana/fdd/datos/accesos.log tmp/respaldo/
```

Parado en `/`, la ruta relativa es la absoluta sin la primera `/`. Si empieza con `/`, ya es absoluta: valía cero.
:::

::: problem {#pia-2a-2 title="2a · 2 · Desde scripts/, relativa → absoluta"}
Escribe el `cp`.
:::

::: answer {of="pia-2a-2"}
```bash
cp ../datos/accesos.log /tmp/respaldo/
```

`..` sube de `scripts/` a `fdd/`, y de ahí se baja a `datos/`.
:::

::: problem {#pia-2a-3 title="2a · 3 · Desde respaldo/, absoluta → relativa"}
Escribe el `cp`.
:::

::: answer {of="pia-2a-3"}
```bash
cp /home/ana/fdd/datos/accesos.log .
```

El destino es **donde ya estás**: `.` (también valía `./`).
:::

::: problem {#pia-2a-4 title="2a · 4 · Desde datos/, relativa → relativa"}
Escribe el `cp`.
:::

::: answer {of="pia-2a-4"}
```bash
cp accesos.log ../../../../tmp/respaldo/
```

Se sube **cuatro** veces: `datos` → `fdd` → `ana` → `home` → `/`. Contar tres `..` valía cero.
:::

En los cuatro, todo o nada por renglón, y la `/` final del destino es opcional.

### 2b · Regex (1 punto, 0.5 cada una)

No importa el comando: escribe sólo la expresión. Usa `[ ]`, `{ }`, `( )`, `?`, `*`, `+`, `^` y `$`, no `\d`.

::: problem {#pia-2b-i title="2b (i) · Construye la regex (0.5)"}
Las claves de producto tienen **tres letras mayúsculas**, un guion y **de 2 a 4 dígitos**; algunas terminan además en `-MX`. Escribe una regex que acepte **toda** la clave y nada más.

- Válidas: `ABC-12` · `XYZ-2026-MX` · `QRS-905`
- Inválidas: `AB-123` · `abc-12` · `ABCD-12` · `ABC-12345` · `ABC-12-US`
:::

::: answer {of="pia-2b-i"}
```text
^[A-Z]{3}-[0-9]{2,4}(-MX)?$
```

0.1 por cada pieza: `[A-Z]{3}`, `-`, `[0-9]{2,4}`, `(-MX)?` y las anclas `^…$`.

- **Las anclas** son las que dejan fuera `ABCD-12`, `ABC-12345` y `ABC-12-US`. Sin ellas, esas tres pasan (comprobado con `grep -E`): la regex encuentra una clave válida **dentro** de la cadena.
- `\d` valía cero en esa pieza, porque el enunciado lo prohibía.
- `[A-Z][A-Z][A-Z]` y `[0-9][0-9][0-9]?[0-9]?` valían completo.
:::

::: problem {#pia-2b-ii title="2b (ii) · Lee la regex (0.5, 0.125 cada cadena)"}
Para cada cadena di si la regex `^[a-z]+[0-9]*\.(csv|txt)$` la acepta completa, y porqué: qué pieza la deja pasar o en qué carácter falla.

`ventas2026.csv` · `Ventas.csv` · `reporte.txt` · `datos.csv.bak`
:::

::: answer {of="pia-2b-ii"}
| Cadena | ¿La acepta? | Porqué |
|---|---|---|
| `ventas2026.csv` | **Sí** | `ventas` son minúsculas (`+`), `2026` son los dígitos (`*`), `\.` es el punto y `csv` es una de las dos extensiones. |
| `Ventas.csv` | **No** | La `V` mayúscula no está en `[a-z]`, y `^` obliga a que la cadena empiece con minúscula. |
| `reporte.txt` | **Sí** | `*` permite **cero** dígitos. |
| `datos.csv.bak` | **No** | Después de `csv` viene `.bak`, y `$` exige que la cadena termine ahí. |

Sin porqué, cada cadena valía cero.
:::

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]], [[archivos-y-comandos|Archivos y comandos]], [[piezas-de-un-patron|Las piezas de un patrón]], [[cuantas-veces|Cuántas veces]] y [[grupos-y-captura|Grupos y captura]].

## 3. Criticar una propuesta (2 puntos, 0.4 cada punto)

Un equipo de cuatro personas mantiene un script de Python que cada noche descarga las ventas de una API, las limpia con `pandas` y deja un CSV que lee el dashboard. Hoy cada quien lo corre en su laptop, y la semana pasada el CSV salió vacío: alguien había actualizado `pandas` en su máquina y el script cambió de comportamiento. Un compañero propone cinco puntos.

Para cada punto, di si lo aceptas. Si no, di qué problema causa y propón otra forma; si sí, di por qué está bien. Sin porqué vale cero.

Es una pregunta abierta. Cada punto valía 0.15 por decidir bien si se acepta y 0.25 por el porqué, que tenía que nombrar el problema y una alternativa, o decir por qué el punto está bien. Se aceptaban otras propuestas razonables si resolvían el problema que se nombraba.

::: problem {#pia-3-1 title="Punto 1 · Commit directo a main"}
Todos hacen commit directo a `main` y push en cuanto terminan, para no perder tiempo.
:::

::: answer {of="pia-3-1"}
**No.** Sin revisión, cualquiera rompe `main` y nadie se entera antes de que corra en la noche. Además, con cuatro personas empujando a la misma rama, los cambios chocan.

**Propuesta:** cada cambio en su rama y un pull request con revisión (y, si se puede, pruebas automáticas) antes de mergear a `main`.
:::

::: problem {#pia-3-2 title="Punto 2 · Dependencias sin versiones"}
Las dependencias se instalan con `pip install pandas requests`, sin versiones, para tener siempre lo más nuevo.
:::

::: answer {of="pia-3-2"}
**No.** Es justo lo que vació el CSV: cada quien instala una versión distinta, y una actualización cambia el comportamiento sin que nadie lo decida.

**Propuesta:** fijar las versiones (`pandas==…` en un archivo de dependencias, o un lockfile con `uv`) y actualizarlas a propósito, con un commit y probándolas.
:::

::: problem {#pia-3-3 title="Punto 3 · La imagen desde el repo"}
La imagen de Docker se construye desde el repo, y la misma imagen que se prueba es la que se despliega.
:::

::: answer {of="pia-3-3"}
**Sí.** Este es el punto que estaba bien a propósito. Construir desde el repo hace que la imagen sea reproducible, porque no depende de la laptop de nadie. Y desplegar **la misma** imagen que se probó garantiza que lo que corre es lo que se revisó.

Bastaba con una de las dos razones bien dicha.
:::

::: problem {#pia-3-4 title="Punto 4 · La clave en el Dockerfile"}
La clave de la API va escrita en el `Dockerfile` (`ENV API_KEY=...`), así nadie tiene que configurarla.
:::

::: answer {of="pia-3-4"}
**No.** La clave queda en el repo, en su historial y dentro de la imagen: cualquiera que tenga una de las dos la ve, y cambiarla obliga a reconstruir.

**Propuesta:** dejarla fuera de Git y pasarla al contenedor al correrlo, como variable de entorno o como un archivo que no se versiona.
:::

::: problem {#pia-3-5 title="Punto 5 · El CSV dentro del contenedor"}
El CSV se escribe en `/app/salida/`, dentro del contenedor. En cada cambio se borra el contenedor y se crea otro con la imagen nueva.
:::

::: answer {of="pia-3-5"}
**A medias, y se calificaba como «no».**

Recrear el contenedor con la imagen nueva **sí** está bien: los contenedores son desechables. Pero el CSV vive dentro del contenedor y **se pierde al borrarlo**, y el dashboard no lo puede leer desde fuera.

**Propuesta:** escribirlo en un volumen o en una carpeta montada, que sobreviven al contenedor. Valía completo quien rechazara el punto por el CSV y dijera dónde guardarlo.
:::

**Repasa:** [[branches-en-serio]], [[el-problema-de-los-ambientes]], [[los-archivos-del-ambiente]], [[lo-que-no-se-sube]] y [[donde-vive-cada-byte]].

## 4. Git y Docker juntos (3 puntos, 0.375 cada fila)

En `tienda/`, Git versiona `Dockerfile` (igual en todas las ramas), `README.md` e `iva.sh`, que sólo hace un print: en `prod` es `echo 15`; `dev` tiene un commit más que lo cambia a `echo 16`.

```dockerfile
FROM alpine:3.20
WORKDIR /app
COPY iva.sh .
CMD ["sh", "iva.sh"]
```

Empiezas en `prod`, sin imágenes, contenedores ni volúmenes. Se evalúa qué contiene cada lugar (tu carpeta, cada rama, la imagen, cada contenedor, el volumen), no los comandos. Los pasos corren en orden desde `tienda/`, y ningún `sleep 600` termina antes. Los tramos 2 y 3 son dos escenarios distintos que parten, los dos, de cómo terminó el tramo 1. En el **Porqué** di qué contiene cada lugar.

El puntaje de cada fila se reparte entre sus subincisos, y cada uno necesita su porqué. Dentro de un tramo, si un paso arrastraba un error de otro paso del **mismo** tramo, se calificó contra lo que se contestó. Entre el tramo 1 y los tramos 2 y 3 no: la herencia es a propósito, porque quien no domina lo básico falla también después.

### Tramo 1 · lo básico

::: problem {#pia-4-1 title="Fila 1 · ¿Qué muestra (a) el primer run y (b) el segundo?"}
```bash
docker build -t tienda:1 .
docker run --rm tienda:1
git switch dev
docker run --rm tienda:1
```
:::

::: answer {of="pia-4-1"}
**(a) 15 · (b) 15.**

La imagen se construyó en `prod` (15). `git switch` cambia tu carpeta, no la imagen.
:::

::: problem {#pia-4-2 title="Fila 2 · ¿Qué muestra (a) el run y (b) el cat?"}
```bash
docker build -t tienda:1 .
docker run --rm tienda:1
cat iva.sh
```
:::

::: answer {of="pia-4-2"}
**(a) 16 · (b) `echo 16`.**

El build copia lo que hay en tu carpeta en ese momento, que es `dev` (16).
:::

::: problem {#pia-4-3 title="Fila 3 · ¿Qué muestra (a) el exec de app1 y (b) el de app2?"}
```bash
git switch prod
docker run -d --name app1 tienda:1 sleep 600
docker run -d --name app2 -v "$(pwd)":/app tienda:1 sleep 600
docker exec app1 sh iva.sh
docker exec app2 sh iva.sh
```
:::

::: answer {of="pia-4-3"}
**(a) 16 · (b) 15.**

`app1` se creó con la copia de la imagen (16). `app2` monta tu carpeta, y el `switch` la regresó a `prod` (15).
:::

Así termina el tramo 1, y de aquí parten los otros dos: tu carpeta en `prod` (15), la imagen en 16, `app1` con su copia (16) y `app2` con tu carpeta montada.

### Tramo 2 · parte del final del tramo 1

Ana sacó la rama `ana` de `dev` e hizo un commit que cambia `iva.sh` a `echo 17`. En `prod`, alguien hizo un commit que sólo cambia `README.md`. Sigues en `prod`.

::: problem {#pia-4-4 title="Fila 4 · (a) exec, (b) run, (c) ramas con el commit de Ana, (d) ¿llegó el 16?"}
```bash
git merge ana
docker exec app2 sh iva.sh
docker run --rm tienda:1
```

¿Qué muestra **(a)** el `exec` y **(b)** el `run`? **(c)** ¿En qué ramas está ahora el commit de Ana? **(d)** ¿Llegó a `prod` el commit de `dev` que pone `echo 16`?
:::

::: answer {of="pia-4-4"}
**(a) 17 · (b) 16 · (c) `ana` y `prod` · (d) sí.**

- **(a)** El merge trae a `prod` el 17 de Ana. No hay conflicto, porque `prod` sólo tocó el README. `app2` lee tu carpeta.
- **(b)** Nadie ha hecho build: la imagen sigue en 16.
- **(c)** El merge sólo movió `prod`: `dev` no tiene el commit de Ana.
- **(d)** Sí, porque `ana` salió de `dev`: al mergear `ana` llegan todos sus commits, también el 16 de `dev`.
:::

::: problem {#pia-4-5 title="Fila 5 · (a) exec de app3, (b) de app2, (c) run, (d) README"}
```bash
docker build -t tienda:1 .
git switch dev
docker run -d --name app3 tienda:1 sleep 600
docker build -t tienda:1 .
docker exec app3 sh iva.sh
docker exec app2 sh iva.sh
docker run --rm tienda:1
```

¿Qué muestra **(a)** el `exec` de `app3`, **(b)** el de `app2` y **(c)** el `run`? **(d)** ¿El `README.md` de tu carpeta trae el cambio que se hizo en `prod`?
:::

::: answer {of="pia-4-5"}
**(a) 17 · (b) 16 · (c) 16 · (d) no.**

- **(a)** `app3` se creó con la imagen construida en `prod` (17). El build siguiente no la cambia: un contenedor guarda la imagen con la que nació.
- **(b)** `app2` lee tu carpeta, que está en `dev` (16).
- **(c)** El segundo build se hizo en `dev` (16).
- **(d)** No: el merge sólo movió `prod`, y tu carpeta está en `dev`.
:::

### Tramo 3 · parte del final del tramo 1 (no del 2)

Beto sacó la rama `beto` de `prod` e hizo un commit que cambia `iva.sh` a `echo 18`. Sigues en `prod`.

::: problem {#pia-4-6 title="Fila 6 · ¿Qué pasa con (a) el primer run, (b) el segundo y (c) el tercero?"}
```bash
docker volume create datos
docker run --rm -v datos:/app tienda:1
mkdir vacia
docker run --rm -v "$(pwd)/vacia":/app tienda:1
git switch beto
docker build -t tienda:1 .
docker run --rm -v datos:/app tienda:1
```
:::

::: answer {of="pia-4-6"}
**(a) 16 · (b) error: `sh` no encuentra `iva.sh` · (c) 16.**

- **(a)** El volumen `datos` es nuevo y está vacío: la primera vez que se monta, se llena con lo que trae la imagen (16).
- **(b)** Una carpeta montada **nunca** se llena: `vacia/` tapa `/app` y no tiene `iva.sh`. Docker responde `sh: can't open 'iva.sh': No such file or directory`.
- **(c)** El build en `beto` deja la imagen en 18, pero el volumen ya tiene contenido y lo conserva (16).
:::

::: problem {#pia-4-7 title="Fila 7 · (a) ¿Git junta las ramas solo? (b) y (c) ¿qué sale en el cat?"}
```bash
git switch dev
git merge beto
cat iva.sh
```

**(a)** ¿Git junta las ramas él solo? En el `cat`, **(b)** ¿qué número sale primero y de qué rama es? **(c)** ¿Cuál sale después y de qué rama es?
:::

::: answer {of="pia-4-7"}
**(a) No: hay conflicto · (b) 16, de `dev` · (c) 18, de `beto`.**

`dev` y `beto` cambiaron la misma línea, la del 15. Git no elige: deja las dos versiones en el archivo, con marcas.

```text
<<<<<<< HEAD
echo 16
=======
echo 18
>>>>>>> beto
```

Primero (`HEAD`) está lo que ya tenías, la rama donde estás: `dev`. Después está lo que viene: `beto`. Decir «`HEAD`» valía sólo si decía que es `dev`.
:::

::: problem {#pia-4-8 title="Fila 8 · Con el conflicto abierto: (a) app2, (b) app1, (c) run, (d) prod"}
```bash
docker exec app2 cat iva.sh
docker exec app1 sh iva.sh
docker run --rm tienda:1
```

Con el conflicto sin resolver, ¿qué muestra **(a)** el `exec` de `app2`, **(b)** el de `app1` y **(c)** el `run`? **(d)** ¿Qué número tiene `iva.sh` en la rama `prod`?
:::

::: answer {of="pia-4-8"}
**(a) el archivo con los dos números y las marcas · (b) 16 · (c) 18 · (d) 15.**

- **(a)** `app2` ve tu carpeta en vivo, también con el conflicto abierto.
- **(b)** `app1` conserva la copia de su creación (16).
- **(c)** La imagen es la del build de la fila 6, en `beto` (18).
- **(d)** Nadie tocó `prod`: el commit de Beto está en su rama, y el merge, a medias, está en `dev`.
:::

**Repasa:** [[branches-y-merge]], [[trabajo-en-paralelo]], [[donde-vive-cada-byte]], [[lab-con-volumen]], [[named-volumes-y-postgres]] y [[los-ocho-casos]].
