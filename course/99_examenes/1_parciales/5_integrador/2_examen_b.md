---
id: parcial-integrador-b
title: "Parcial 5 · Integrador · Examen B"
nav_title: "Examen B"
summary: "El examen B del parcial integrador, pregunta por pregunta, con la respuesta explicada debajo: el programa tasa/monto, un modelo de 24B en la nube, ventas.csv, el reporte de los lunes con polars y el repo banco/."
status: ready
estimated_time: 75m
tags: [examen, parcial, arquitectura, terminal, regex, git, docker, volumenes]
---

# Parcial 5 · Integrador · Examen B

**[PDF del examen B, sin respuestas](../../_assets/parcial-integrador-b.pdf)** · 75 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Donde dice **Porqué**, una respuesta sin porqué vale cero. Donde se pide **Cuenta**, un número sin cuenta vale la mitad.

Las rutas se comprobaron con `os.path.normpath`, las regex con `grep -E`, y todo el bloque 4 se corrió con Git y Docker 29.6 (`alpine:3.20`).

## 1. Arquitectura (3 puntos)

### 1a · Del SSD al registro (1.5 puntos)

Modelo simplificado. La CPU sólo calcula con lo que tiene en sus **registros**. `LOAD` copia un dato a un registro: si el dato está en la **caché** (dentro del chip, pequeña, guarda lo que se usó hace poco), lo toma de ahí; si no, va hasta la **RAM** (fuera del chip, grande y mucho más lenta) y **deja una copia en la caché**. Los tiempos de la tabla son el total de cada instrucción, y nada se borra de la caché durante el ejercicio.

| Instrucción | Qué hace | Tarda |
|---|---|---|
| `LOAD  r, [x]` | trae x a un registro | 3 ns si x está en caché · 120 ns si va a RAM |
| `ADD   r, r, r` | suma dos registros | 1 ns |
| `STORE [x], r` | guarda un registro | 3 ns |

```text
LOAD  r1, [tasa]    ; NO en caché
LOAD  r2, [monto]   ; en caché
ADD   r3, r1, r2
STORE [pago], r3
```

::: problem {#pib-1a-i title="1a (i) · El orden de la jerarquía (0.25)"}
Ordena estos niveles de la jerarquía, desde donde la CPU usa el dato hasta donde se guarda: **RAM · L1 · SSD · L2 · registro**.
:::

::: answer {of="pib-1a-i"}
**registro → L1 → L2 → RAM → SSD.**

Todo o nada. Aquí el orden va al revés que en el examen A: la pregunta dice **desde donde la CPU usa** el dato. El orden contrario (SSD → … → registro) valía cero.
:::

::: problem {#pib-1a-ii title="1a (ii) · Una tras otra (0.25)"}
La CPU ejecuta las cuatro instrucciones **una tras otra**. ¿Cuántos ns tarda?
:::

::: answer {of="pib-1a-ii"}
120 + 3 + 1 + 3 = **127 ns**.

El `LOAD` de `tasa` va a RAM (120 ns) y el de `monto` está en caché (3 ns).
:::

::: problem {#pib-1a-iii title="1a (iii) · Otra vez (0.5)"}
Enseguida corres **otra vez** las cuatro instrucciones, con la caché como la dejó (ii). ¿Cuántos ns tarda? **Porqué** cambió.
:::

::: answer {of="pib-1a-iii"}
3 + 3 + 1 + 3 = **10 ns**.

**Porqué:** el primer `LOAD` de `tasa` dejó una copia en la caché, así que la segunda vez ya no va a RAM.

0.25 por el número y 0.25 por el porqué. Sin porqué no pasaba de 0.25.
:::

::: problem {#pib-1a-iv title="1a (iv) · El doble de GHz (0.5)"}
Otra CPU, con el **doble de GHz**, corre el programa desde el inicio (`tasa` NO está en caché). `ADD`, `STORE` y un `LOAD` desde caché tardan la mitad; un `LOAD` que va a RAM sigue tardando 120 ns. ¿Cuántos ns tarda? **Porqué** no tarda la mitad.
:::

::: answer {of="pib-1a-iv"}
120 + 1.5 + 0.5 + 1.5 = **123.5 ns**.

**Porqué:** lo que pasa dentro del chip se acelera, pero la espera a la RAM no. Casi todo el tiempo era esa espera: 120 de los 127 ns.

0.25 por el número y 0.25 por el porqué. Con el número mal, pero un porqué que dice que la RAM no se acelera, valía 0.25.
:::

### 1b · Elegir una máquina en la nube (1.5 puntos)

| Máquina | vCPU | RAM | GPU (memoria) | USD/hora |
|---|---|---|---|---|
| `gpu-a100` | 12 | 85 GB | 1 NVIDIA A100 (40 GB) | 3.70 |
| `std-16` | 16 | 64 GB | — | 0.80 |
| `gpu-l4` | 8 | 32 GB | 1 NVIDIA L4 (24 GB) | 0.85 |
| `mem-96` | 96 | 768 GB | — | 4.80 |

Vas a rentar una máquina para servir a un chatbot un modelo de lenguaje de **24B parámetros en INT8**. La inferencia es, sobre todo, multiplicar matrices, y los pesos deben caber completos en la memoria de la GPU. Además de los pesos, reserva **25 %** extra (caché KV y temporales).

Memoria de los pesos = parámetros × bytes por parámetro. FP16 = 2 bytes · INT8 = 1 byte · INT4 = 0.5 bytes. 24B = 24 × 10⁹ parámetros. 1 GB = 10⁹ bytes.

::: problem {#pib-1b-i title="1b (i) · Los pesos (0.25)"}
¿Cuántos GB ocupan los pesos? Cuenta.
:::

::: answer {of="pib-1b-i"}
24 × 10⁹ × 1 byte = **24 GB**.
:::

::: problem {#pib-1b-ii title="1b (ii) · Con el 25 % extra (0.25)"}
¿Cuántos GB necesitas con el 25 % extra? Cuenta.
:::

::: answer {of="pib-1b-ii"}
24 × 1.25 = **30 GB**.

Con (i) mal, pero (ii) igual a «su número × 1.25», valía completo.
:::

::: problem {#pib-1b-iii title="1b (iii) · ¿Cabe? (0.25)"}
¿Cabe en la GPU de `gpu-a100`? ¿Y en la de `gpu-l4`? Porqué.
:::

::: answer {of="pib-1b-iii"}
- **`gpu-a100`: sí.** Su A100 tiene 40 GB, y 40 ≥ 30.
- **`gpu-l4`: no.** Su L4 tiene 24 GB, y 24 < 30.

**La trampa:** quien olvida el 25 % extra compara 24 con 24 y dice que sí cabe en la L4. Eso valía cero. Se calificaba contra el número que cada quien dio en (ii).
:::

::: problem {#pib-1b-iv title="1b (iv) · ¿Qué máquina rentas? (0.5)"}
¿Qué máquina rentas? Porqué no cada una de las otras tres.
:::

::: answer {of="pib-1b-iv"}
**`gpu-a100`**, la primera fila del catálogo. Hay que descartar las otras tres:

- **`std-16`** no tiene GPU. Sus 64 GB de RAM alcanzan para los pesos, pero la inferencia es multiplicar matrices, y sin GPU es lenta.
- **`mem-96`** tiene RAM de sobra, pero tampoco tiene GPU, y es la más cara.
- **`gpu-l4`** tiene GPU, pero sus 24 GB no alcanzan para 30.

`gpu-a100` con las tres razones valía 0.5. Con una o dos, 0.25.
:::

::: problem {#pib-1b-v title="1b (v) · Usar la máquina chica (0.25)"}
Para usar `gpu-l4` sin cambiar los 24B: ¿qué formato, y cuántos GB con el 25 %? Cuenta. ¿Qué pierdes?
:::

::: answer {of="pib-1b-v"}
**INT4**: 24 × 0.5 = 12 GB, que con el 25 % son **15 GB** y caben en 24.

Es el único formato que cabe: INT8 es el formato actual (30 GB) y FP16 ocupa más. Se puede perder algo de **calidad o precisión** en las respuestas.

Hacían falta las tres cosas: formato, GB y qué se pierde. Con dos de ellas, 0.15.
:::

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]] e [[ia-escala-decision|IA, escala y selección de hardware]].

## 2. Terminal y regex (2 puntos)

### 2a · Rutas (1 punto, 0.25 cada una)

```text
/
├── home/
│   └── luis/
│       └── proyecto/
│           ├── bin/
│           │   └── carga.sh
│           └── entrada/
│               └── ventas.csv
└── var/
    └── copias/
```

Quieres copiar `ventas.csv` a la carpeta `copias/`. En cada caso escribe el `cp` con el tipo de ruta que pide la tabla. Una ruta absoluta empieza en `/` y no depende de dónde estés; una relativa parte del directorio actual: `..` sube un nivel y `.` es donde estás.

| # | Estás en | Origen | Destino |
|---|---|---|---|
| 1 | `/home/luis/proyecto/entrada/` | relativa | relativa |
| 2 | `/var/copias/` | absoluta | relativa |
| 3 | `/` | relativa | relativa |
| 4 | `/home/luis/proyecto/bin/` | relativa | absoluta |

::: problem {#pib-2a-1 title="2a · 1 · Desde entrada/, relativa → relativa"}
Escribe el `cp`.
:::

::: answer {of="pib-2a-1"}
```bash
cp ventas.csv ../../../../var/copias/
```

Se sube **cuatro** veces: `entrada` → `proyecto` → `luis` → `home` → `/`. Contar tres `..` valía cero.
:::

::: problem {#pib-2a-2 title="2a · 2 · Desde copias/, absoluta → relativa"}
Escribe el `cp`.
:::

::: answer {of="pib-2a-2"}
```bash
cp /home/luis/proyecto/entrada/ventas.csv .
```

El destino es **donde ya estás**: `.` (también valía `./`).
:::

::: problem {#pib-2a-3 title="2a · 3 · Desde /, relativa → relativa"}
Escribe el `cp`.
:::

::: answer {of="pib-2a-3"}
```bash
cp home/luis/proyecto/entrada/ventas.csv var/copias/
```

Parado en `/`, la ruta relativa es la absoluta sin la primera `/`. Si empieza con `/`, ya es absoluta: valía cero.
:::

::: problem {#pib-2a-4 title="2a · 4 · Desde bin/, relativa → absoluta"}
Escribe el `cp`.
:::

::: answer {of="pib-2a-4"}
```bash
cp ../entrada/ventas.csv /var/copias/
```

`..` sube de `bin/` a `proyecto/`, y de ahí se baja a `entrada/`.
:::

En los cuatro, todo o nada por renglón, y la `/` final del destino es opcional.

### 2b · Regex (1 punto, 0.5 cada una)

No importa el comando: escribe sólo la expresión. Usa `[ ]`, `{ }`, `( )`, `?`, `*`, `+`, `^` y `$`, no `\d`.

::: problem {#pib-2b-i title="2b (i) · Construye la regex (0.5)"}
Los folios tienen **dos letras mayúsculas**, un guion y **de 3 a 5 dígitos**; algunos terminan además en `-R`. Escribe una regex que acepte **todo** el folio y nada más.

- Válidas: `MX-123` · `QZ-90210-R` · `AB-4501`
- Inválidas: `M-123` · `ab-123` · `XAB-123` · `AB-123456` · `AB-123-RX`
:::

::: answer {of="pib-2b-i"}
```text
^[A-Z]{2}-[0-9]{3,5}(-R)?$
```

0.1 por cada pieza: `[A-Z]{2}`, `-`, `[0-9]{3,5}`, `(-R)?` y las anclas `^…$`.

- **Las anclas** son las que dejan fuera `XAB-123`, `AB-123456` y `AB-123-RX`. Sin ellas, esas tres pasan (comprobado con `grep -E`): la regex encuentra un folio válido **dentro** de la cadena.
- `\d` valía cero en esa pieza, porque el enunciado lo prohibía.
- `[A-Z][A-Z]` y `[0-9][0-9][0-9][0-9]?[0-9]?` valían completo.
:::

::: problem {#pib-2b-ii title="2b (ii) · Lee la regex (0.5, 0.125 cada cadena)"}
Para cada cadena di si la regex `^[A-Z][a-z]*_[0-9]+\.(json|log)$` la acepta completa, y porqué: qué pieza la deja pasar o en qué carácter falla.

`ventas_7.log` · `X_9.log` · `Ventas_2026.json` · `Datos_3.json.gz`
:::

::: answer {of="pib-2b-ii"}
| Cadena | ¿La acepta? | Porqué |
|---|---|---|
| `ventas_7.log` | **No** | La `v` minúscula no está en `[A-Z]`, y `^` obliga a que la cadena empiece con mayúscula. |
| `X_9.log` | **Sí** | `X` es la mayúscula, `*` permite **cero** minúsculas, `9` cumple `[0-9]+` y `log` es una de las dos extensiones. |
| `Ventas_2026.json` | **Sí** | `V` es la mayúscula, `entas` son minúsculas (`*`), luego `_`, `2026` son dígitos (`+`), `\.` y `json`. |
| `Datos_3.json.gz` | **No** | Después de `json` viene `.gz`, y `$` exige que la cadena termine ahí. |

Sin porqué, cada cadena valía cero.
:::

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]], [[archivos-y-comandos|Archivos y comandos]], [[piezas-de-un-patron|Las piezas de un patrón]], [[cuantas-veces|Cuántas veces]] y [[grupos-y-captura|Grupos y captura]].

## 3. Criticar una propuesta (2 puntos, 0.4 cada punto)

Un equipo de tres personas publica cada lunes un reporte: cada lunes llega un CSV nuevo de 2 GB, y un script de Python lo lee, calcula totales con `polars` y sube un PDF al drive del área. Corre en un servidor que comparten varios proyectos, y el lunes pasado falló: otro proyecto actualizó una librería en el Python del sistema y rompió el script. Una compañera propone cinco puntos.

Para cada punto, di si lo aceptas. Si no, di qué problema causa y propón otra forma; si sí, di por qué está bien. Sin porqué vale cero.

Es una pregunta abierta. Cada punto valía 0.15 por decidir bien si se acepta y 0.25 por el porqué, que tenía que nombrar el problema y una alternativa, o decir por qué el punto está bien. Se aceptaban otras propuestas razonables si resolvían el problema que se nombraba.

::: problem {#pib-3-1 title="Punto 1 · Ramas y pull requests"}
Cada quien trabaja en su propia rama y abre un pull request; otra persona lo revisa antes de mergear a `main`.
:::

::: answer {of="pib-3-1"}
**Sí.** Este es el punto que estaba bien a propósito. Cada cambio pasa por la revisión de otra persona antes de llegar a `main`, así que nadie rompe lo que corre el lunes sin que alguien lo vea. Y los cambios de tres personas no chocan en la misma rama.
:::

::: problem {#pib-3-2 title="Punto 2 · sudo pip install en el sistema"}
Instalar las librerías con `sudo pip install` en el Python del sistema del servidor, para que todos los proyectos las compartan.
:::

::: answer {of="pib-3-2"}
**No.** Es justo lo que rompió el script: el Python del sistema lo comparten todos los proyectos, y una actualización de uno rompe a los demás. Además, `sudo pip` puede romper el propio sistema.

**Propuesta:** un ambiente aislado por proyecto (un `venv`, `uv` o un contenedor) con las versiones fijas.
:::

::: problem {#pib-3-3 title="Punto 3 · El CSV de 2 GB en el repo"}
Subir el CSV de 2 GB al repo, para que todos tengan los mismos datos.
:::

::: answer {of="pib-3-3"}
**No.** Git es para código, no para datos grandes: el archivo se queda para siempre en el historial, cada clon pesa 2 GB más y GitHub rechaza archivos de más de 100 MB.

**Propuesta:** dejar los datos fuera del repo, en el drive o en un almacenamiento compartido, y versionar sólo el código y de dónde salen los datos.
:::

::: problem {#pib-3-4 title="Punto 4 · La contraseña en config.py"}
La contraseña del drive va en `config.py`, dentro del repo; no pasa nada porque el repo es privado.
:::

::: answer {of="pib-3-4"}
**No.** «Privado» no es secreto: la contraseña la ve cualquiera con acceso al repo, y queda en el historial aunque luego se borre.

**Propuesta:** dejarla fuera de Git y pasarla al correr, como variable de entorno o como un archivo que no se versiona.
:::

::: problem {#pib-3-5 title="Punto 5 · El CSV dentro de la imagen"}
Cada lunes se corre `docker run --rm` con una imagen construida desde el repo, y el CSV se mete en la imagen con `COPY` en el `Dockerfile`.
:::

::: answer {of="pib-3-5"}
**A medias, y se calificaba como «no».**

Correr con `--rm` una imagen construida desde el repo **sí** está bien: es reproducible y no deja contenedores viejos. Pero meter con `COPY` un CSV de 2 GB que llega nuevo cada lunes obliga a reconstruir la imagen cada lunes y la hace enorme.

**Propuesta:** montar los datos al correr, con un volumen o una carpeta montada (`-v`), y dejar en la imagen sólo el código. Valía completo quien rechazara el punto por el CSV y dijera cómo pasarlo.
:::

**Repasa:** [[branches-en-serio]], [[el-problema-de-los-ambientes]], [[las-piezas-de-un-ambiente]], [[lo-que-no-se-sube]] y [[donde-vive-cada-byte]].

## 4. Git y Docker juntos (3 puntos, 0.375 cada fila)

En `banco/`, Git versiona `Dockerfile` (igual en todas las ramas), `README.md` y `tasa.sh`, que sólo hace un print: en `main` es `echo 40`; `nueva` tiene un commit más que lo cambia a `echo 37`.

```dockerfile
FROM alpine:3.20
WORKDIR /app
COPY tasa.sh .
CMD ["sh", "tasa.sh"]
```

Empiezas en `main`, sin imágenes, contenedores ni volúmenes. Se evalúa qué contiene cada lugar (tu carpeta, cada rama, la imagen, cada contenedor, el volumen), no los comandos. Los pasos corren en orden desde `banco/`, y ningún `sleep 600` termina antes. Los tramos 2 y 3 son dos escenarios distintos que parten, los dos, de cómo terminó el tramo 1. En el **Porqué** di qué contiene cada lugar.

El puntaje de cada fila se reparte entre sus subincisos, y cada uno necesita su porqué. Dentro de un tramo, si un paso arrastraba un error de otro paso del **mismo** tramo, se calificó contra lo que se contestó. Entre el tramo 1 y los tramos 2 y 3 no: la herencia es a propósito, porque quien no domina lo básico falla también después.

### Tramo 1 · lo básico

::: problem {#pib-4-1 title="Fila 1 · ¿Qué muestra (a) el run y (b) el cat?"}
```bash
docker build -t banco:2 .
git switch nueva
docker run --rm banco:2
cat tasa.sh
```
:::

::: answer {of="pib-4-1"}
**(a) 40 · (b) `echo 37`.**

- **(a)** La imagen se construyó en `main` (40). `git switch` cambia tu carpeta, no la imagen.
- **(b)** La carpeta ya está en `nueva`.
:::

::: problem {#pib-4-2 title="Fila 2 · ¿Qué muestra (a) el run y (b) el exec?"}
```bash
docker run -d --name web1 -v "$(pwd)":/app banco:2 sleep 600
docker build -t banco:2 .
git switch main
docker run --rm banco:2
docker exec web1 sh tasa.sh
```
:::

::: answer {of="pib-4-2"}
**(a) 37 · (b) 40.**

- **(a)** El build se hizo con la carpeta en `nueva` (37).
- **(b)** `web1` no tiene copia: lee tu carpeta, y el `switch` la regresó a `main` (40). Que `web1` se haya creado con la imagen vieja no importa.
:::

::: problem {#pib-4-3 title="Fila 3 · ¿Qué muestra (a) el exec de web2 y (b) el de web1?"}
```bash
docker run -d --name web2 banco:2 sleep 600
docker exec web2 sh tasa.sh
docker exec web1 sh tasa.sh
```
:::

::: answer {of="pib-4-3"}
**(a) 37 · (b) 40.**

- **(a)** `web2` copió la imagen al crearse (37), aunque tu carpeta diga 40: `docker run` no mira la carpeta. Es la trampa del tramo.
- **(b)** `web1` lee tu carpeta, en `main`.
:::

Así termina el tramo 1, y de aquí parten los otros dos: tu carpeta en `main` (40), la imagen en 37, `web2` con su copia (37) y `web1` con tu carpeta montada.

### Tramo 2 · parte del final del tramo 1

Carla sacó la rama `carla` de `nueva` e hizo un commit que cambia `tasa.sh` a `echo 52`. En `main`, alguien hizo un commit que sólo cambia `README.md`. Sigues en `main`.

::: problem {#pib-4-4 title="Fila 4 · (a) ramas con el commit de Carla, (b) ¿llegó el 37?, (c) run, (d) exec"}
```bash
git merge carla
docker run --rm banco:2
docker exec web1 sh tasa.sh
```

**(a)** ¿En qué ramas está ahora el commit de Carla? **(b)** ¿Llegó a `main` el commit de `nueva` que pone `echo 37`? ¿Qué muestra **(c)** el `run` y **(d)** el `exec`?
:::

::: answer {of="pib-4-4"}
**(a) `carla` y `main` · (b) sí · (c) 37 · (d) 52.**

- **(a)** El merge sólo movió `main`: `nueva` no tiene el commit de Carla.
- **(b)** Sí, porque `carla` salió de `nueva`: al mergearla llegan todos sus commits, también el 37.
- **(c)** Nadie ha hecho build: la imagen sigue en 37.
- **(d)** `web1` lee tu carpeta, que el merge dejó en 52. No hay conflicto, porque `main` sólo tocó el README.
:::

::: problem {#pib-4-5 title="Fila 5 · (a) run, (b) exec de web1, (c) de web3, (d) main"}
```bash
docker build -t banco:2 .
git switch nueva
docker run -d --name web3 banco:2 sleep 600
docker build -t banco:2 .
docker run --rm banco:2
docker exec web1 sh tasa.sh
docker exec web3 sh tasa.sh
```

¿Qué muestra **(a)** el `run`, **(b)** el `exec` de `web1` y **(c)** el de `web3`? **(d)** ¿Qué número da `tasa.sh` en la rama `main`?
:::

::: answer {of="pib-4-5"}
**(a) 37 · (b) 37 · (c) 52 · (d) 52.**

- **(a)** El segundo build se hizo en `nueva` (37).
- **(b)** `web1` lee tu carpeta, que está en `nueva`.
- **(c)** `web3` se creó con la imagen construida en `main` ya mergeado (52), aunque la carpeta ya estuviera en `nueva`. El build posterior no la cambia: un contenedor guarda la imagen con la que nació.
- **(d)** El merge dejó `main` en 52.
:::

### Tramo 3 · parte del final del tramo 1 (no del 2)

Diego sacó la rama `diego` de `main` e hizo un commit que cambia `tasa.sh` a `echo 29`. Sigues en `main`.

::: problem {#pib-4-6 title="Fila 6 · ¿Qué pasa con (a) el primer run, (b) el segundo y (c) el tercero?"}
```bash
docker volume create cache
mkdir nada
docker run --rm -v "$(pwd)/nada":/app banco:2
docker run --rm -v cache:/app banco:2
git switch diego
docker build -t banco:2 .
docker run --rm -v cache:/app banco:2
```
:::

::: answer {of="pib-4-6"}
**(a) error: `sh` no encuentra `tasa.sh` · (b) 37 · (c) 37.**

- **(a)** Una carpeta montada **nunca** se llena: `nada/` tapa `/app` y no tiene `tasa.sh`. Docker responde `sh: can't open 'tasa.sh': No such file or directory`.
- **(b)** El volumen `cache` es nuevo y está vacío: la primera vez que se monta, se llena con lo que trae la imagen (37).
- **(c)** El build en `diego` deja la imagen en 29, pero el volumen ya tiene contenido y lo conserva (37).
:::

::: problem {#pib-4-7 title="Fila 7 · En el cat, (a) y (b) ¿qué sale?, (c) ¿Git junta las ramas solo?"}
```bash
git switch nueva
git merge diego
cat tasa.sh
```

En el `cat`, **(a)** ¿qué número sale primero y de qué rama es? **(b)** ¿Cuál sale después y de qué rama es? **(c)** ¿Git pudo juntar las ramas él solo?
:::

::: answer {of="pib-4-7"}
**(a) 37, de `nueva` · (b) 29, de `diego` · (c) no: hay conflicto.**

`nueva` y `diego` cambiaron la misma línea, la del 40. Git no elige: deja las dos versiones en el archivo, con marcas.

```text
<<<<<<< HEAD
echo 37
=======
echo 29
>>>>>>> diego
```

Primero (`HEAD`) está lo que ya tenías, la rama donde estás: `nueva`. Después está lo que viene: `diego`. Decir «`HEAD`» valía sólo si decía que es `nueva`.
:::

::: problem {#pib-4-8 title="Fila 8 · Con el conflicto abierto: (a) web2, (b) web1, (c) run, (d) main"}
```bash
docker exec web2 sh tasa.sh
docker exec web1 cat tasa.sh
docker run --rm banco:2
```

Con el conflicto sin resolver, ¿qué muestra **(a)** el `exec` de `web2`, **(b)** el de `web1` y **(c)** el `run`? **(d)** ¿Qué número tiene `tasa.sh` en la rama `main`?
:::

::: answer {of="pib-4-8"}
**(a) 37 · (b) el archivo con los dos números y las marcas · (c) 29 · (d) 40.**

- **(a)** `web2` conserva la copia de su creación (37).
- **(b)** `web1` ve tu carpeta en vivo, también con el conflicto abierto.
- **(c)** La imagen es la del build de la fila 6, en `diego` (29).
- **(d)** Nadie tocó `main`: el commit de Diego está en su rama, y el merge, a medias, está en `nueva`.
:::

**Repasa:** [[branches-y-merge]], [[trabajo-en-paralelo]], [[donde-vive-cada-byte]], [[lab-con-volumen]], [[named-volumes-y-postgres]] y [[los-ocho-casos]].
