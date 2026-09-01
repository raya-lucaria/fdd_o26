---
id: leer-izquierda-derecha
title: "Leer de izquierda a derecha"
nav_title: "Izquierda a derecha"
summary: "Cómo recorre el motor una línea, por qué nunca regresa, y los tres primeros metacaracteres."
status: ready
estimated_time: 15m
tags: [regex, grep, automata, anclas, escapes]
prerequisites: [que-es-una-regex]
---

# Leer de izquierda a derecha

**Página 2 de 7** · 15 min

Meta: predecir qué encuentra un patrón antes de ejecutarlo.

::: figure {#rx-cabeza title="La cabeza avanza; nunca regresa"}
![La palabra Mariana en una cinta de siete celdas; debajo, cinco intentos del patrón ana empezando cada uno una celda más a la derecha: los cuatro primeros fallan y el quinto acierta](_assets/rx-cabeza.svg)
:::

## En corto

- El motor intenta desde la posición 0. Si falla, **avanza una posición** y vuelve a intentar desde cero.
- Cuando encuentra una coincidencia, **sigue desde donde terminó**: no vuelve a mirar lo que ya consumió.
- `grep -o` imprime **lo que encontró**, no la línea. Es la herramienta para ver qué está pasando.

## El banco de pruebas de toda la unidad

De aquí en adelante, cada construcción nueva se prueba con cadenas escritas en la propia línea, sin archivo de por medio:

```bash
printf '%s\n' 'ana' 'anaconda' 'Mariana' | grep -n 'ana'
```

`printf '%s\n'` convierte cada argumento en una línea, `|` se las entrega a `grep`, y `-n` **numera las líneas de entrada** para que veas cuáles pasaron y deduzcas cuáles no. Aquí pasan la 1 y la 2, y también la 3: `Mariana` contiene `ana`.

Cambia las cadenas y vuelve a correr. Ese es el ciclo de toda la unidad.

## Misión 1: mira la coincidencia, no la línea

**Haz:**

```bash
printf 'Mariana\n' | grep    'ana'
printf 'Mariana\n' | grep -o 'ana'
```

**Deberías ver:** la primera devuelve `Mariana` —la línea entera— y la segunda devuelve `ana`, sólo el pedazo.

**Pausa:** esa diferencia es la que confunde a todo el mundo al principio. `grep` **decide por línea** pero **casa por subcadena**. Usa `-o` cada vez que no entiendas por qué una línea pasó.

## Misión 2: la cabeza no regresa

**Haz:**

```bash
printf 'aaaa\n' | grep -o 'aa'
printf 'aaaa\n' | grep -o 'aa' | wc -l
printf 'aaaa\n' | grep -o 'aaa'
```

**Deberías ver:** **dos** coincidencias de `aa`, no tres. Y una sola de `aaa`.

En `aaaa` hay tres lugares donde empieza un `aa`: las posiciones 0, 1 y 2. El motor encuentra el de la posición 0, **consume esos dos caracteres** y reanuda en la 2, donde encuentra el segundo. La posición 1 nunca se prueba porque ya quedó atrás.

::: table {#rx-traza-aaaa title="Por qué `aa` sobre `aaaa` da dos coincidencias y no tres"}

| Posición de la cabeza | Qué hace | Siguiente posición |
|---:|---|---:|
| 0 | casa `aa` → coincidencia 1 | 2 |
| 2 | casa `aa` → coincidencia 2 | 4 |
| 4 | fin de línea, se detiene | — |
:::

## Misión 3: el punto casa cualquier cosa

`.` significa **un carácter cualquiera** (menos el salto de línea). Es el primer metacarácter.

**Haz:**

```bash
printf '%s\n' '3.14' '3x14' '3-14' | grep -n '3.14'
printf '%s\n' '3.14' '3x14' '3-14' | grep -n '3\.14'
```

**Deberías ver:** el primero pasa **las tres** —el punto acepta la `x` y el guion igual que el punto—. El segundo pasa **sólo la 1**.

La barra invertida **escapa** el punto: le quita su significado especial y lo vuelve un punto literal.

::: definition {#rx-def-metacaracter title="Metacarácter"}
Un carácter que la regex **no** interpreta literalmente, sino como una instrucción. Son estos trece:

```text
.  ^  $  [  ]  (  )  {  }  *  +  ?  |
```

Para buscar cualquiera de ellos tal cual, se escapa con `\`. Cualquier otro carácter es literal por sí solo y **no** hace falta escaparlo: `\` delante de algo que no es metacarácter no significa «literal», significa «lo que decida el motor». En la página 5 verás qué caro sale eso.
:::

## Misión 4: anclas

`^` significa «aquí empieza la línea» y `$` significa «aquí termina». Ninguna de las dos se lleva un carácter: **marcan una posición**.

**Haz:**

```bash
printf '%s\n' 'ana' 'anaconda' 'Mariana' 'Ana' | grep -n 'ana'
printf '%s\n' 'ana' 'anaconda' 'Mariana' 'Ana' | grep -n '^ana'
printf '%s\n' 'ana' 'anaconda' 'Mariana' 'Ana' | grep -n '^ana$'
```

**Deberías ver:** el primero pasa 1, 2 y 3. El segundo pasa 1 y 2 — `Mariana` cae porque no **empieza** con `ana`. El tercero pasa sólo la 1: es la única línea que **es** exactamente `ana`.

Esa diferencia parte en dos todo lo que puede ir en un patrón, y conviene fijarla desde ya:

| | Qué hace | Ejemplos |
|---|---|---|
| **Consume** | se lleva caracteres del texto | `a`, `.`, `[0-9]` |
| **No consume** | sólo exige algo de la posición | `^`, `$`, y `\b` de la página 5 |

**Pausa:** `^…$` es la forma de pasar de «lo contiene» a «es exactamente». Lo usarás cada vez que quieras validar en lugar de buscar. La página siguiente le pone nombre a la primera columna.

::: problem {#rx-p2-anclaje title="¿Cuál devuelve más líneas?"}
Ahora sobre un archivo de verdad. Sin ejecutarlos, ordena estos tres de más a menos coincidencias:

```bash
cd ~/fdd/regex-lab
grep -c 'Ana'     contactos.txt
grep -c '^Ana'    contactos.txt
grep -c '^Ana.*$' contactos.txt
```
:::

::: hint {of="rx-p2-anclaje"}
Fíjate en cuál exige que la línea **empiece** con el patrón, y en si `.*` agrega alguna restricción o ninguna.
:::

::: answer {of="rx-p2-anclaje"}
`'Ana'` devuelve más (3): lo encuentra en cualquier parte, incluida la línea del Equipo 3, donde `Ana Ruiz` va a media línea. Los otros dos devuelven lo mismo (2): sólo las líneas que **empiezan** con `Ana`. `.*$` no agrega nada — «cualquier cosa, cero o más veces, hasta el final» es una condición que toda línea cumple. Un patrón que no descarta nada es un patrón que sobra.
:::

## El mismo patrón, dibujado

Un patrón es una máquina de estados. `ana` son cuatro estados y las flechas dicen qué carácter mueve la máquina de uno a otro.

::: figure {#rx-automata-ana title="El autómata que reconoce `ana`"}
![Autómata de cuatro estados: q0 avanza a q1 al leer a, q1 avanza a q2 al leer n, q2 avanza al estado de aceptación al leer a; cualquier otro carácter devuelve la máquina a q0](_assets/rx-automata-ana.svg)
:::

**Lectura visual:** el bucle ámbar es el detalle fino. Si estás en q1 —ya viste una `a`— y llega **otra** `a`, la máquina **no** vuelve al principio: esa nueva `a` puede ser el inicio de la coincidencia buena. Compruébalo con `printf 'aana\n' | grep -o 'ana'`.

> [!NOTE]
> **Si sólo recuerdas una cosa:** cuando un patrón encuentre de más o de menos, pruébalo con dos o tres cadenas inline y `grep -o`, y pregúntate desde qué posición empezó la cabeza.

## Cierre

Ya sabes cómo recorre el motor una línea y tienes `.`, `^`, `$` y el escape. Continúa con [[piezas-de-un-patron|Las piezas de un patrón]], donde el patrón deja de ser una fila de caracteres y pasa a ser una fila de piezas.
