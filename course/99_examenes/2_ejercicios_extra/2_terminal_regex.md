---
id: ejercicios-terminal
title: "Ejercicios extra de terminal y regex"
nav_title: "Terminal y regex"
summary: "Ejercicios con la forma del parcial 2, cada uno con una pista y su respuesta plegadas: leer y escribir regex, nombrar comandos, y moverse y mover archivos con rutas absolutas y relativas."
status: ready
estimated_time: 40m
tags: [ejercicios, terminal, bash, regex, rutas]
---

# Ejercicios extra de terminal y regex

**[PDF sin respuestas, para imprimir](../_assets/practica-terminal.pdf)** · unos 40 minutos · sin apuntes

Miden lo mismo que el [[parcial-terminal|parcial 2]] con casos nuevos. Debajo de cada pregunta hay dos cosas plegadas:

- **la pista**: ábrela sólo si llevas un rato atorado; si la abres de inmediato, el ejercicio pierde su chiste;
- **la respuesta**, con su explicación.

Las regex se probaron con `grep -E` y las rutas en un árbol de carpetas real. Si tienes una terminal a la mano, compruébalo tú también.

## Parte 1 · Leer y escribir regex

Todas las regex van para `grep -E`. Ahí `\d` **no** funciona (busca una `d` literal), así que los dígitos se escriben `[0-9]`.

::: problem {#xt-r1 title="R1 · Lee el patrón"}
¿Cuáles de estas líneas acepta `^[A-Z]{3}-[0-9]{4}$`?

`ABC-1234` · `AB-1234` · `ABC-12345` · `abc-1234` · `ABCD-1234`
:::

::: hint {of="xt-r1"}
Lee de izquierda a derecha y cuenta: ¿cuántas letras exige antes del guion, de qué tipo, y cuántos dígitos después? ¿Qué hacen `^` y `$`?
:::

::: answer {of="xt-r1"}
**Respuesta:** sólo `ABC-1234`.

**Por qué:**

1. `^`: la coincidencia empieza en el primer carácter de la línea.
2. `[A-Z]{3}`: exactamente tres letras mayúsculas.
3. `-`: un guion literal.
4. `[0-9]{4}`: exactamente cuatro dígitos.
5. `$`: la línea termina justo después del cuarto dígito.

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `ABC-1234` | **sí** | `ABC` son tres mayúsculas, luego `-`, luego `1234` son cuatro dígitos, y ahí acaba la línea |
| `AB-1234` | no | Después de `AB` viene `-`; `[A-Z]{3}` pedía una tercera letra |
| `ABC-12345` | no | Después de `1234` viene un `5`; `$` exigía que la línea terminara ahí |
| `abc-1234` | no | `[A-Z]` sólo acepta mayúsculas, y `a` es minúscula |
| `ABCD-1234` | no | `^` fija `A`, `B`, `C` como las tres letras; luego el patrón pide `-` y encuentra `D` |

**La regla:** **para validar una línea completa se ponen los dos anclajes, `^` al inicio y `$` al final; sin ellos basta con que un pedazo de la línea cumpla.**

**Compruébalo:**

```text
$ printf '%s\n' ABC-1234 AB-1234 ABC-12345 abc-1234 ABCD-1234 | grep -E '^[A-Z]{3}-[0-9]{4}$'
ABC-1234
```

**Error común:** creer que `ABCD-1234` pasa porque contiene `BCD-1234`. Eso sólo ocurre si quitas el `^`: grep vuelve a intentar desde la `B` y encuentra un pedazo que cumple. `-o` imprime sólo ese pedazo:

```text
$ echo ABCD-1234 | grep -Eo '[A-Z]{3}-[0-9]{4}$'
BCD-1234
```

Lo mismo con `ABC-12345` si quitas el `$`: `grep -Eo '^[A-Z]{3}-[0-9]{4}'` imprime `ABC-1234`.
:::

::: problem {#xt-r2 title="R2 · Código postal"}
Escribe una regex que acepte un código postal mexicano: exactamente **cinco dígitos**, nada más. Acepta `01000`; rechaza `1000`, `123456` y `0100A`.
:::

::: hint {of="xt-r2"}
Necesitas una clase para «un dígito», un cuantificador para «exactamente cinco», y anclas para que no sobre nada.
:::

::: answer {of="xt-r2"}
**Respuesta:** `^[0-9]{5}$`. También vale `^[[:digit:]]{5}$`, que significa lo mismo.

**Por qué:**

1. `[0-9]` es un dígito cualquiera.
2. `{5}` repite la pieza anterior exactamente cinco veces.
3. `^` impide que haya algo antes del primer dígito.
4. `$` impide que haya algo después del quinto dígito.

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `01000` | **sí** | Cinco dígitos y nada más |
| `1000` | no | Sólo cuatro dígitos: `{5}` pide un quinto y la línea ya se acabó |
| `123456` | no | Después del quinto dígito viene un `6`; `$` exigía fin de línea |
| `0100A` | no | El quinto carácter es `A`, que no está en `[0-9]` |

**La regla:** **«exactamente N de algo» se escribe clase + `{N}` + anclajes `^` y `$`; el `{N}` solo no limita la línea.**

**Compruébalo:**

```text
$ printf '%s\n' 01000 1000 123456 0100A | grep -E '^[0-9]{5}$'
01000
```

**Error común:** dos versiones del mismo descuido.

- `^[0-9]+$` acepta cualquier cantidad de dígitos, porque `+` significa «una o más veces»: deja pasar `01000`, `1000` y `123456`.
- `[0-9]{5}` sin anclajes deja pasar `123456`, porque esa línea **contiene** cinco dígitos seguidos:

```text
$ printf '%s\n' 01000 1000 123456 0100A | grep -E '[0-9]{5}'
01000
123456
```
:::

::: problem {#xt-r3 title="R3 · Hora de 24 horas"}
Escribe una regex para una hora `HH:MM` de 24 horas: de `00:00` a `23:59`, siempre con dos dígitos. Acepta `07:30` y `23:59`; rechaza `24:00`, `7:30` y `12:60`.
:::

::: hint {of="xt-r3"}
Las horas no se pueden describir con una sola clase por dígito: de `00` a `19` el segundo dígito es libre, pero con `2` adelante sólo llega a `3`. Parte las horas en dos casos con `|`. Con los minutos basta mirar el primer dígito.
:::

::: answer {of="xt-r3"}
**Respuesta:** `^([01][0-9]|2[0-3]):[0-5][0-9]$`

**Por qué:**

1. Las horas tienen dos casos. Si el primer dígito es `0` o `1`, el segundo puede ser cualquiera: `[01][0-9]` cubre de `00` a `19`.
2. Si el primer dígito es `2`, el segundo sólo llega a `3`: `2[0-3]` cubre de `20` a `23`.
3. `|` acepta uno u otro caso. Los paréntesis encierran los dos casos para que el `|` sólo aplique a la hora.
4. `:` son los dos puntos, literales.
5. En los minutos basta el primer dígito: `[0-5][0-9]` cubre de `00` a `59`.
6. `^` y `$` impiden que haya algo antes de la hora o después de los minutos.

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `07:30` | **sí** | `07` entra por `[01][0-9]`; `30` entra por `[0-5][0-9]` |
| `23:59` | **sí** | `23` entra por `2[0-3]`; `59` entra por `[0-5][0-9]` |
| `24:00` | no | `[01][0-9]` falla en el `2`; `2[0-3]` falla en el `4` |
| `7:30` | no | El primer carácter es `7`: ningún caso de la hora empieza con `7` (los dos exigen `0`, `1` o `2`) |
| `12:60` | no | La hora `12` cumple, pero el `6` de los minutos no está en `[0-5]` |

**La regla:** **si un rango no se puede describir con una clase por dígito, se parte en casos con `|`, y los casos van entre paréntesis para que el `|` no parta el patrón entero.**

**Compruébalo:**

```text
$ printf '%s\n' 07:30 23:59 24:00 7:30 12:60 | grep -E '^([01][0-9]|2[0-3]):[0-5][0-9]$'
07:30
23:59
```

**Error común 1:** `^[0-2][0-9]:[0-5][0-9]$`. Acepta `24:00` y `29:00`, porque deja que el segundo dígito sea cualquiera aunque el primero sea `2`.

**Error común 2:** olvidar los paréntesis. Sin ellos, el `|` parte **todo** el patrón en dos: `^[01][0-9]|2[0-3]:[0-5][0-9]$` significa «la línea empieza con `00`–`19`» **o** «la línea termina en `20:00`–`23:59`». La primera opción ya no mira los minutos:

```text
$ printf '%s\n' 07:30 24:00 7:30 12:60 19xyz | grep -E '^[01][0-9]|2[0-3]:[0-5][0-9]$'
07:30
12:60
19xyz
```

`12:60` y `19xyz` pasan sólo porque empiezan con `12` y `19`.
:::

::: problem {#xt-r4 title="R4 · Fecha AAAA-MM-DD"}
Escribe una regex para fechas `AAAA-MM-DD`, con mes de `01` a `12` y día de `01` a `31`. Luego contesta: ¿tu regex acepta `2026-02-30`? ¿Está mal por eso?
:::

::: hint {of="xt-r4"}
Es la misma idea de R3, aplicada dos veces: el mes y el día tienen casos distintos según su primer dígito.
:::

::: answer {of="xt-r4"}
**Respuesta:**

- **La regex:** `^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$`
- **¿Acepta `2026-02-30`?** **Sí.**
- **¿Está mal por eso?** **No.** Una regex revisa la forma del texto, no el calendario.

**Por qué:**

1. `[0-9]{4}`: el año, cuatro dígitos cualesquiera.
2. `-`: guion literal.
3. `(0[1-9]|1[0-2])`: el mes. Con `0` adelante, el segundo dígito va de `1` a `9` (meses `01`–`09`; así se excluye `00`). Con `1` adelante, va de `0` a `2` (meses `10`–`12`).
4. `-`: guion literal.
5. `(0[1-9]|[12][0-9]|3[01])`: el día. Tres casos: `01`–`09`, `10`–`29` y `30`–`31`.
6. `^` y `$`: nada antes del año ni después del día.
7. En `2026-02-30`, cada pieza cumple por separado: `2026` es el año, `02` entra por `0[1-9]`, `30` entra por `3[01]`. La regex no relaciona el día con el mes, así que no puede saber que febrero tiene 28 días (29 en año bisiesto).

Otras fechas, para ver qué sí rechaza:

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `2026-02-30` | **sí** | Forma correcta; el día 30 no existe en febrero, pero la regex no lo sabe |
| `2026-12-31` | **sí** | Mes `12` por `1[0-2]`, día `31` por `3[01]` |
| `2026-13-01` | no | Mes `13`: con `1` adelante, `1[0-2]` no acepta el `3` |
| `2026-1-05` | no | Mes de un dígito: después del `1` viene `-`, y los dos casos del mes piden dos dígitos |

**La regla:** **una regex comprueba la forma (qué caracteres y cuántos); si el valor existe de verdad lo comprueba el programa.**

**Compruébalo:** Python sí rechaza la fecha al convertirla:

```text
$ python3 -c 'import datetime; datetime.date.fromisoformat("2026-02-30")'
ValueError: day is out of range for month
```

(Python imprime antes dos líneas de `Traceback`; aquí se omiten.) Usar la regex como primer filtro y el programa para lo demás es lo normal.

**Error común:** contestar «sí, está mal» y querer arreglarla dentro de la regex. Haría falta un caso por grupo de meses: para febrero, `02-(0[1-9]|1[0-9]|2[0-8])` (del `01` al `28`); para abril, junio, septiembre y noviembre, días hasta el `30`; para los demás, hasta el `31`. Y aun así el `29` de febrero queda fuera, porque depende de si el año es bisiesto, algo que se calcula con el año completo. El patrón se vuelve ilegible sin ganar nada sobre convertir el texto a fecha.
:::

::: problem {#xt-r5 title="R5 · Correo institucional"}
Escribe una regex que acepte correos que terminan exactamente en `@itam.mx`, con un usuario de minúsculas, dígitos, punto o guion bajo. Acepta `ana.perez@itam.mx`; rechaza `ana@itamxmx` y `ana@itam.mx.com`.
:::

::: hint {of="xt-r5"}
Hay un carácter en `itam.mx` que en una regex no significa lo que parece. ¿Qué acepta `.` sin escapar?
:::

::: answer {of="xt-r5"}
**Respuesta:** `^[a-z0-9._]+@itam\.mx$`

**Por qué:**

1. `^`: empieza en el primer carácter de la línea.
2. `[a-z0-9._]+`: el usuario. Uno o más caracteres, cada uno una minúscula, un dígito, un punto o un guion bajo. **Dentro** de los corchetes el `.` es un punto literal.
3. `@itam`: esos cinco caracteres, literales.
4. `\.`: un punto literal. **Fuera** de los corchetes, un `.` sin barra acepta cualquier carácter; la barra le quita ese significado.
5. `mx`: literal.
6. `$`: la línea termina justo después de `mx`.

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `ana.perez@itam.mx` | **sí** | `ana.perez` entra por `[a-z0-9._]+` (el punto está en la clase); luego `@itam`, un punto, `mx` y fin de línea |
| `ana@itamxmx` | no | Después de `itam` viene una `x`, y `\.` exige un punto |
| `ana@itam.mx.com` | no | Después de `mx` viene `.com`, y `$` exigía fin de línea |

**La regla:** **fuera de corchetes, un punto literal se escribe `\.`; dentro de corchetes, `.` ya es literal.**

**Compruébalo:**

```text
$ printf '%s\n' ana.perez@itam.mx ana@itamxmx ana@itam.mx.com | grep -E '^[a-z0-9._]+@itam\.mx$'
ana.perez@itam.mx
```

**Error común:** olvidar la barra. Sin ella, el `.` de `itam.mx` acepta cualquier carácter, también la `x` de `itamxmx`:

```text
$ printf '%s\n' ana.perez@itam.mx ana@itamxmx ana@itam.mx.com | grep -E '^[a-z0-9._]+@itam.mx$'
ana.perez@itam.mx
ana@itamxmx
```
:::

::: problem {#xt-r6 title="R6 · La palabra repetida"}
En un texto hay errores de dedo como «el el gato». ¿Qué imprime `grep -Eo '\b(\w+) \1\b'` con estas líneas?

```text
el el gato
la casa
esto es es raro
los losas
```
:::

::: hint {of="xt-r6"}
`(\w+)` captura una palabra, y `\1` exige **la misma** otra vez. `\b` marca dónde empieza o termina una palabra. ¿Termina una palabra justo después de `los` en «losas»?
:::

::: answer {of="xt-r6"}
**Respuesta:** imprime dos líneas:

```text
el el
es es
```

**Por qué:**

1. `\b`: un borde de palabra. Está entre un carácter de palabra (`\w`: letra, dígito o `_`) y uno que no lo es, o en el inicio o fin de la línea.
2. `(\w+)`: una palabra (una o más letras, dígitos o guiones bajos). Los paréntesis la **capturan**: guardan el texto exacto que coincidió.
3. ` `: un espacio literal.
4. `\1`: la **retro-referencia**. Exige otra vez el mismo texto que capturó el grupo 1, letra por letra.
5. `\b`: la repetición debe terminar donde termina una palabra.
6. `-o` hace que grep imprima sólo el pedazo que coincidió, no la línea completa.

| Línea | Imprime | Por qué |
|---|---|---|
| `el el gato` | `el el` | El grupo captura `el`; sigue un espacio; sigue otra vez `el`; después hay un espacio, que es borde de palabra |
| `la casa` | nada | Después de `la` viene `casa`, no `la`; y después de `casa` la línea se acaba sin repetir nada |
| `esto es es raro` | `es es` | Desde `esto` no sirve: después del espacio viene `es`, no `esto`. Desde la primera `es`: captura `es`, espacio, `es` otra vez, y luego un espacio |
| `los losas` | nada | El grupo captura `los`; sigue un espacio; `\1` coincide con las tres primeras letras de `losas`, pero después viene una `a`, no un borde de palabra, y el `\b` final falla |

**La regla:** **`\1` repite el texto capturado, no el patrón; y el `\b` final evita aceptar una palabra que sólo empieza igual.**

**Compruébalo:**

```text
$ printf '%s\n' 'el el gato' 'la casa' 'esto es es raro' 'los losas' | grep -Eo '\b(\w+) \1\b'
el el
es es
```

**Error común:** olvidar el `\b` final. Sin él, `\1` acepta las tres primeras letras de `losas` y `los losas` sí coincide:

```text
$ printf '%s\n' 'los losas' | grep -Eo '\b(\w+) \1'
los los
```

**Ojo con `\d`:** que `\w` y `\b` funcionen en `grep -E` no significa que `\d` funcione. GNU grep agrega `\w`, `\s` y `\b` como extensión propia; `\d` no está en esa lista y se lee como una `d` literal:

```text
$ printf '%s\n' a1 ad | grep -nE '\d'
2:ad
```

Encontró `ad` (tiene una `d`), no `a1` (tiene un dígito). La lista completa está en [[taquigrafia-perl|La taquigrafía de Perl]].
:::

::: problem {#xt-r7 title="R7 · Enteros sin ceros a la izquierda"}
¿Qué líneas acepta `^(0|[1-9][0-9]*)$`? `0` · `7` · `10` · `007` · `00` · `120` · `-3`. Explica con una frase qué describe.
:::

::: hint {of="xt-r7"}
Hay dos caminos separados por `|`. ¿Con qué puede empezar el segundo? ¿Qué permite `*`?
:::

::: answer {of="xt-r7"}
**Respuesta:**

- **Acepta:** `0`, `7`, `10` y `120`.
- **Qué describe:** **los enteros no negativos escritos sin ceros a la izquierda.**

**Por qué:**

1. `^( … )$`: la línea completa, de principio a fin, tiene que ser uno de los dos caminos que están dentro de los paréntesis.
2. Camino 1, `0`: la línea es exactamente un cero.
3. Camino 2, `[1-9][0-9]*`: un primer dígito de `1` a `9`, y luego cero o más dígitos de `0` a `9` (`*` significa «cero o más veces»).
4. Ningún camino tiene lugar para un signo `-`.

| Línea | ¿Pasa? | Por qué |
|---|---|---|
| `0` | **sí** | Camino 1: un cero y fin de línea |
| `7` | **sí** | Camino 2: `7` entra por `[1-9]`; `[0-9]*` acepta cero dígitos más |
| `10` | **sí** | Camino 2: `1` por `[1-9]`, `0` por `[0-9]*` |
| `007` | no | Camino 1 acepta el primer `0`, pero después viene otro `0` y `$` exigía fin de línea. Camino 2 no puede empezar con `0` |
| `00` | no | Igual que `007`: después del primer `0` hay otro carácter |
| `120` | **sí** | Camino 2: `1` por `[1-9]`, `2` y `0` por `[0-9]*` |
| `-3` | no | El `-` no está en ninguna de las clases |

**La regla:** **para prohibir ceros a la izquierda, el primer dígito va en `[1-9]`, y el cero solo se acepta como un camino aparte.**

**Compruébalo:**

```text
$ printf '%s\n' 0 7 10 007 00 120 -3 | grep -E '^(0|[1-9][0-9]*)$'
0
7
10
120
```

**Error común:** quitar los paréntesis. `^0|[1-9][0-9]*$` significa «empieza con `0`» **o** «termina en un dígito de `1` a `9` seguido de cero o más dígitos». Con eso pasan las siete líneas: `007` y `00` empiezan con `0`, y `-3` termina en `3`.

Es la misma idea que el importe del [[parcial-terminal-b|examen B del parcial]]: separar el caso del cero.
:::

**Repasa:** [[piezas-de-un-patron|Las piezas de un patrón]], [[cuantas-veces|Cuántas veces]], [[taquigrafia-perl|La taquigrafía de Perl]] y [[grupos-y-captura|Grupos y captura]].

## Parte 2 · El comando de cada acción

::: problem {#xt-c1 title="C · Diez acciones, diez comandos"}
Escribe el comando para cada acción:

1. Listar los archivos de la carpeta, **incluidos los ocultos**.
2. Ver el contenido completo de un archivo.
3. Ver sólo las primeras líneas de un archivo grande.
4. Contar cuántas líneas tiene un archivo.
5. Buscar las líneas que contienen una palabra.
6. Crear `a/b/c` de una vez, aunque `a` no exista.
7. Renombrar `viejo.txt` a `nuevo.txt`.
8. Subir a la carpeta madre.
9. Mandar la salida de un comando como entrada de otro.
10. Borrar una carpeta **vacía**.
:::

::: hint {of="xt-c1"}
Casi todos son abreviaturas en inglés: *list*, *concatenate*, *word count*, *make directory*, *move*, *change directory*, *remove directory*. El 9 no es un comando, es un símbolo.
:::

::: answer {of="xt-c1"}
Cada inciso lleva su respuesta y por qué.

**1 · Listar los archivos, incluidos los ocultos**

- **Respuesta:** `ls -a`
- **Por qué:** un archivo oculto es uno cuyo nombre empieza con punto, como `.gitignore`. `ls` solo no los muestra; con `-a` (*all*) sí. También vale `ls -la`, que además muestra permisos, tamaño y fecha.
- **Compruébalo:** en una carpeta con `.oculto` y `visible`, `ls` imprime sólo `visible`; `ls -a` imprime `.`, `..`, `.oculto` y `visible`.

**2 · Ver el contenido completo de un archivo**

- **Respuesta:** `cat archivo`
- **Por qué:** `cat` (*concatenate*) imprime el archivo entero en la terminal. Para un archivo largo, `less archivo` deja moverse con las flechas; se sale con `q`.

**3 · Ver sólo las primeras líneas de un archivo grande**

- **Respuesta:** `head archivo`
- **Por qué:** `head` imprime las 10 primeras líneas; `head -n 3 archivo` imprime las 3 primeras. `tail` hace lo mismo con las últimas.
- **Compruébalo:** `seq 20 > n.txt` crea un archivo con los números del 1 al 20, uno por línea; `head n.txt | wc -l` imprime `10`.

**4 · Contar cuántas líneas tiene un archivo**

- **Respuesta:** `wc -l archivo`
- **Por qué:** `wc` (*word count*) con `-l` (*lines*) cuenta sólo líneas. Sin `-l` imprime tres números: líneas, palabras y bytes.
- **Compruébalo:** con un archivo `f.txt` que tiene `a`, `b` y `c` en tres líneas, `wc -l f.txt` imprime `3 f.txt` y `wc f.txt` imprime `3 3 6 f.txt`.

**5 · Buscar las líneas que contienen una palabra**

- **Respuesta:** `grep palabra archivo`
- **Por qué:** `grep` imprime cada línea del archivo que contiene ese texto. `grep -c palabra archivo` cuenta esas líneas en vez de mostrarlas.
- **Error común:** olvidar que distingue mayúsculas de minúsculas. En un archivo con las líneas `Hola` y `hola mundo`, `grep hola` sólo encuentra `hola mundo`; `grep -i hola` encuentra las dos.

**6 · Crear `a/b/c` de una vez, aunque `a` no exista**

- **Respuesta:** `mkdir -p a/b/c`
- **Por qué:** `mkdir` (*make directory*) crea una carpeta; `-p` (*parents*) crea también las carpetas intermedias que falten, aquí `a` y `a/b`.
- **Error común:** `mkdir a/b/c` sin `-p`. Si `a` no existe, falla: `mkdir: cannot create directory ‘a/b/c’: No such file or directory`.

**7 · Renombrar `viejo.txt` a `nuevo.txt`**

- **Respuesta:** `mv viejo.txt nuevo.txt`
- **Por qué:** en la terminal se renombra con `mv` (*move*): mover el archivo a otro nombre dentro de la misma carpeta es renombrarlo.
- **Compruébalo:** después del `mv`, `ls` muestra `nuevo.txt` y ya no muestra `viejo.txt`.

**8 · Subir a la carpeta madre**

- **Respuesta:** `cd ..`
- **Por qué:** `cd` (*change directory*) cambia de carpeta, y `..` es el nombre de la carpeta madre dentro de cualquier carpeta. Desde `…/sub/dir`, `cd ..` te deja en `…/sub`.
- **Error común:** `cd` a secas no sube un nivel: te lleva a tu home. `cd /` te lleva a la raíz.

**9 · Mandar la salida de un comando como entrada de otro**

- **Respuesta:** `|`, la tubería. No es un comando: es un símbolo que va entre dos comandos, `comando1 | comando2`.
- **Por qué:** lo que `comando1` imprime no sale a la pantalla; entra a `comando2`. Ejemplos: `history | grep cd` busca en tu historial los comandos con `cd`; `ls | wc -l` cuenta cuántos archivos lista `ls`.
- **Error común:** usar `>` en lugar de `|`. `ls > wc` no corre `wc`: crea un archivo llamado `wc` con la lista adentro.

**10 · Borrar una carpeta vacía**

- **Respuesta:** `rmdir carpeta`
- **Por qué:** `rmdir` (*remove directory*) sólo borra carpetas vacías y se niega con las que tienen algo. Es la versión segura.
- **Compruébalo:** con una carpeta llena y otra vacía:

  ```text
  $ mkdir llena vacia
  $ touch llena/x
  $ rmdir llena
  rmdir: failed to remove 'llena': Directory not empty
  $ rmdir vacia
  $ ls
  llena
  ```

- **Error común:** `rm carpeta` no sirve, ni siquiera con una carpeta vacía: responde `rm: cannot remove 'vacia': Is a directory`. `rm -r carpeta` sí la borra, pero también borra todo lo que tenga dentro.
:::

**Repasa:** [[archivos-y-comandos|Archivos y comandos]] y [[flujos-procesos-y-herramientas|Historial, tuberías y herramientas]].

## Parte 3 · Rutas

Todas las preguntas usan este árbol:

```text
/home/ana/
├── proyecto/
│   ├── datos/
│   │   └── crudo.csv
│   └── scripts/
└── descargas/
    └── nuevo.csv
```

::: problem {#xt-p1 title="P1 · Las dos relativas"}
Estás en `/home/ana/proyecto/scripts/`. Mueve `nuevo.csv` a la carpeta `datos/` usando **rutas relativas** en origen y destino.
:::

::: hint {of="xt-p1"}
Desde `scripts/`, ¿cuántos niveles subes para llegar a `ana/`? ¿Y para llegar a `proyecto/`?
:::

::: answer {of="xt-p1"}
**Respuesta:** `mv ../../descargas/nuevo.csv ../datos/`

**Por qué:**

1. Estás en `/home/ana/proyecto/scripts`. Una ruta relativa (sin `/` al inicio) se lee desde ahí.
2. El origen es `/home/ana/descargas/nuevo.csv`. `descargas` cuelga de `ana`, que está dos niveles arriba de `scripts`: el origen necesita dos `..`.
3. El destino es `/home/ana/proyecto/datos`. `datos` cuelga de `proyecto`, que está un nivel arriba de `scripts`: el destino necesita un `..`.

Origen, pedazo por pedazo, empezando en `/home/ana/proyecto/scripts`:

| Pedazo | Qué hace | Quedas en |
|---|---|---|
| `..` | sube un nivel | `/home/ana/proyecto` |
| `..` | sube otro nivel | `/home/ana` |
| `descargas` | baja a `descargas` | `/home/ana/descargas` |
| `nuevo.csv` | nombra el archivo | `/home/ana/descargas/nuevo.csv` |

Destino, pedazo por pedazo, empezando otra vez en `/home/ana/proyecto/scripts`:

| Pedazo | Qué hace | Quedas en |
|---|---|---|
| `..` | sube un nivel | `/home/ana/proyecto` |
| `datos` | baja a `datos` | `/home/ana/proyecto/datos` |

**La regla:** **cada `..` sube un nivel desde donde estás; sube hasta la carpeta que contiene a tu destino y desde ahí baja por nombres.**

**Compruébalo:** en una copia del árbol, después del `mv`, `ls ../datos` imprime `crudo.csv` y `nuevo.csv`, y `ls ../../descargas` ya no imprime nada.

**Error común:** un solo `..` en el origen. `../descargas/nuevo.csv` apunta a `/home/ana/proyecto/descargas/nuevo.csv`, que no existe:

```text
$ mv ../descargas/nuevo.csv ../datos/
mv: cannot stat '../descargas/nuevo.csv': No such file or directory
```
:::

::: problem {#xt-p2 title="P2 · Las dos absolutas"}
Mismo lugar, misma acción, ahora con **rutas absolutas**.
:::

::: hint {of="xt-p2"}
Una ruta absoluta no depende de dónde estés: empieza en `/` y baja nombre por nombre.
:::

::: answer {of="xt-p2"}
**Respuesta:** `mv /home/ana/descargas/nuevo.csv /home/ana/proyecto/datos/`

**Por qué:**

1. Una ruta absoluta empieza con `/`, la raíz del sistema, y baja nombre por nombre.
2. Por eso no importa dónde estés: el mismo comando funciona desde `scripts/` o desde cualquier otra carpeta.

Cada ruta, pedazo por pedazo desde la raíz:

- Origen: `/` → `home` → `ana` → `descargas` → `nuevo.csv`, es decir, `/home/ana/descargas/nuevo.csv`.
- Destino: `/` → `home` → `ana` → `proyecto` → `datos`, es decir, `/home/ana/proyecto/datos`.

También vale `mv ~/descargas/nuevo.csv ~/proyecto/datos/` si la usuaria es `ana`: la shell cambia `~` por su home, `/home/ana`, antes de correr el comando.

**La regla:** **una ruta que empieza con `/` es absoluta: se lee desde la raíz, sin importar en qué carpeta estés.**

**Compruébalo:** en una copia del árbol, el mismo `mv` con las dos rutas absolutas, corrido desde `/` (otra carpeta), deja `crudo.csv` y `nuevo.csv` en `datos/`.
:::

::: problem {#xt-p3 title="P3 · Renombrar sin mover"}
Estás en `/home/ana/`. Cambia el nombre de `crudo.csv` a `ventas.csv` sin sacarlo de `datos/`.
:::

::: hint {of="xt-p3"}
`mv` no distingue entre mover y renombrar: sólo cambia la ruta de un archivo. ¿Qué ruta debe tener al final?
:::

::: answer {of="xt-p3"}
**Respuesta:** `mv proyecto/datos/crudo.csv proyecto/datos/ventas.csv`

**Por qué:**

1. Estás en `/home/ana`.
2. El archivo está en `/home/ana/proyecto/datos/crudo.csv`. Desde `ana`, la ruta relativa baja a `proyecto` y luego a `datos`: `proyecto/datos/crudo.csv`.
3. Al final debe estar en `/home/ana/proyecto/datos/ventas.csv`: la misma carpeta, otro nombre. Desde `ana`: `proyecto/datos/ventas.csv`.
4. `mv` deja el archivo exactamente en la ruta del destino. Si origen y destino sólo difieren en el último nombre, el archivo no cambia de carpeta: se renombra.

| Ruta | Carpeta | Nombre |
|---|---|---|
| origen `proyecto/datos/crudo.csv` | `/home/ana/proyecto/datos` | `crudo.csv` |
| destino `proyecto/datos/ventas.csv` | `/home/ana/proyecto/datos` (la misma) | **`ventas.csv`** |

También vale con rutas absolutas: `mv /home/ana/proyecto/datos/crudo.csv /home/ana/proyecto/datos/ventas.csv`.

**La regla:** **para renombrar sin mover, el destino repite la carpeta del origen y sólo cambia el nombre.**

**Compruébalo:** en una copia del árbol, después del `mv`, `ls proyecto/datos` imprime sólo `ventas.csv`.

**Error común:** dos versiones.

- `mv crudo.csv ventas.csv`: en `/home/ana` no hay ningún `crudo.csv`, así que falla con `mv: cannot stat 'crudo.csv': No such file or directory`.
- `mv proyecto/datos/crudo.csv ventas.csv`: el destino `ventas.csv` es relativo a `/home/ana`, así que el archivo queda en `/home/ana/ventas.csv`. Lo renombra **y** lo saca de `datos/`.
:::

::: problem {#xt-p4 title="P4 · ¿Dónde quedaste?"}
Estás en `/home/ana/proyecto/datos/` y corres `cd ../scripts/../../descargas`. ¿Qué imprime `pwd`?
:::

::: hint {of="xt-p4"}
Avanza pedazo por pedazo, separando en cada `/`. Cada `..` deshace un paso.
:::

::: answer {of="xt-p4"}
**Respuesta:** `/home/ana/descargas`

**Por qué:**

1. Empiezas en `/home/ana/proyecto/datos`.
2. La ruta `../scripts/../../descargas` no empieza con `/`: es relativa, se lee desde donde estás.
3. Se parte en cada `/` y se aplica un pedazo a la vez, de izquierda a derecha.
4. Cada `..` sube un nivel; cada nombre baja a esa carpeta.

| Pedazo | Qué hace | Quedas en |
|---|---|---|
| (inicio) | — | `/home/ana/proyecto/datos` |
| `..` | sube un nivel | `/home/ana/proyecto` |
| `scripts` | baja a `scripts` | `/home/ana/proyecto/scripts` |
| `..` | sube un nivel | `/home/ana/proyecto` |
| `..` | sube un nivel | `/home/ana` |
| `descargas` | baja a `descargas` | `/home/ana/descargas` |

**La regla:** **una ruta con varios `..` se resuelve pedazo por pedazo; entrar a una carpeta y salir enseguida con `..` te deja donde estabas.**

**Compruébalo:** en una copia del árbol, `cd ../scripts/../../descargas` seguido de `pwd` termina en `/home/ana/descargas`.

**Error común:** subir tres niveles porque hay tres `..`. Desde `datos`, tres niveles arriba es `/home`, y `/home/descargas` no existe. El `..` que sigue a `scripts` sólo deshace la entrada a `scripts`: en total subes dos niveles, de `datos` a `ana`.
:::

::: problem {#xt-p5 title="P5 · El error de la diagonal"}
Estás en `/home/ana/proyecto/` y corres:

```text
$ mv /datos/crudo.csv scripts/
mv: cannot stat '/datos/crudo.csv': No such file or directory
```

El archivo sí existe. ¿Qué pasó, y cuál es el comando correcto?
:::

::: hint {of="xt-p5"}
¿Qué significa una `/` al **principio** de una ruta?
:::

::: answer {of="xt-p5"}
**Respuesta:**

- **Qué pasó:** `/datos/crudo.csv` empieza con `/`, así que es una ruta **absoluta**: `mv` busca una carpeta `datos` que cuelgue directamente de la raíz. Esa carpeta, `/datos`, no existe; la `datos` real es `/home/ana/proyecto/datos`.
- **Comando correcto:** **`mv datos/crudo.csv scripts/`**

**Por qué:**

1. Estás en `/home/ana/proyecto`.
2. Con la `/` inicial, `mv` no usa la carpeta donde estás: lee la ruta desde la raíz `/`.
3. «cannot stat» significa que `mv` no pudo leer la información de ese archivo: en esa ruta no hay nada.
4. Sin la `/` inicial, `datos/crudo.csv` es relativa: se lee desde `/home/ana/proyecto`.
5. El destino `scripts/` también es relativo: `/home/ana/proyecto/scripts`.

| Ruta escrita | Se lee desde | Llega a | ¿Existe? |
|---|---|---|---|
| `/datos/crudo.csv` | la raíz, `/` | `/datos/crudo.csv` | no |
| `datos/crudo.csv` | `/home/ana/proyecto` | `/home/ana/proyecto/datos/crudo.csv` | **sí** |

También vale la ruta absoluta completa: `mv /home/ana/proyecto/datos/crudo.csv scripts/`.

**La regla:** **una `/` al principio de una ruta significa «desde la raíz», no «desde aquí».**

**Compruébalo:** en una copia del árbol, `mv datos/crudo.csv scripts/` funciona y `ls scripts` imprime `crudo.csv`. En una terminal en español, el error original dice «No existe el archivo o el directorio».
:::

::: problem {#xt-p6 title="P6 · mv con destino que existe o no existe"}
Estás en `datos/`, que contiene `crudo.csv`. ¿Qué hace `mv crudo.csv respaldo` en cada caso?

a) No existe nada llamado `respaldo`.

b) `respaldo/` ya existe y es una carpeta.
:::

::: hint {of="xt-p6"}
`mv` mira el destino antes de decidir: si es una carpeta, mete el archivo adentro.
:::

::: answer {of="xt-p6"}
**Respuesta:**

- **a)** Lo **renombra**: en `datos/` queda un archivo llamado `respaldo`, sin extensión, y ya no hay `crudo.csv`.
- **b)** Lo **mete en la carpeta**: queda `respaldo/crudo.csv`, con su nombre original.

**Por qué:**

1. `mv` revisa el destino antes de actuar.
2. Si el destino no existe, `mv` lo toma como el nuevo nombre del archivo (caso a).
3. Si el destino existe y es una carpeta, `mv` deja el archivo dentro de ella, con su mismo nombre (caso b).

**La regla:** **si el destino es una carpeta que existe, `mv` mueve adentro; si el destino no existe, `mv` renombra.**

**Compruébalo:** `ls -F` marca las carpetas con `/` al final. Caso a), en una carpeta vacía:

```text
$ touch crudo.csv
$ mv crudo.csv respaldo
$ ls -F
respaldo
```

Caso b), en otra carpeta vacía:

```text
$ mkdir respaldo
$ touch crudo.csv
$ mv crudo.csv respaldo
$ ls -F
respaldo/
$ ls respaldo
crudo.csv
```

**Error común:** escribir `mv crudo.csv respaldo` creyendo que existe la carpeta `respaldo`, cuando no existe. El archivo queda renombrado como `respaldo`, sin aviso. Si esperas una carpeta, escribe el destino con diagonal final: `mv` lee la `/` final como «esto es una carpeta» y, como no existe, se niega en vez de renombrar:

```text
$ mv crudo.csv respaldo/
mv: cannot move 'crudo.csv' to 'respaldo/': Not a directory
```
:::

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]] y [[archivos-y-comandos|Archivos y comandos]].
