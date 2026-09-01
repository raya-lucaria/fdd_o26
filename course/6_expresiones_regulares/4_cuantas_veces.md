---
id: cuantas-veces
title: "Cuántas veces"
nav_title: "Cuántas veces"
summary: "Los cuatro cuantificadores son uno solo: un rango de repeticiones. Qué significa «cero veces» y hasta dónde llega la repetición."
status: ready
estimated_time: 15m
tags: [regex, grep, kleene, cuantificadores, epsilon, backtracking]
prerequisites: [piezas-de-un-patron]
---

# Cuántas veces

**Página 4 de 7** · 15 min

Meta: saber a qué se pega un cuantificador y hasta dónde llega.

::: figure {#rx-cuantificadores title="Los tres cuantificadores, dibujados"}
![Tres autómatas pequeños lado a lado: a con interrogación acepta cero o una a; a con asterisco acepta cero o más y su estado inicial ya es de aceptación; a con más exige al menos una a antes de aceptar](_assets/rx-cuantificadores.svg)
:::

## En corto

- Los cuatro cuantificadores son **uno solo**: un rango `{mínimo, máximo}` de repeticiones.
- «Cero veces» significa que la pieza puede **no aparecer**: eso es `ε`, la cadena vacía.
- La repetición toma todo lo que puede y después **cede** hasta que el resto del patrón encaja.

## Prepara

```bash
mkdir -p ~/fdd/regex-lab && cd ~/fdd/regex-lab
printf '%s\n' 'gto' 'gato' 'gaaato' 'color' 'colour' > formas.txt
printf '%s\n' 'a' 'aa' 'aaa' > n.txt
cat formas.txt
```

## Misión 1: los cuatro son el mismo

`{n,m}` es la forma general: «al menos `n` veces, como mucho `m`». Los otros tres son atajos suyos.

| Escribes | Es realmente | mínimo | máximo |
|---|---|---:|---:|
| `?` | `{0,1}` | 0 | 1 |
| `*` | `{0,}` | 0 | sin límite |
| `+` | `{1,}` | 1 | sin límite |
| `{2,4}` | `{2,4}` | 2 | 4 |

**Haz:** comprueba que el atajo y la forma larga son la misma cosa.

```bash
grep -cE '^a?$'    n.txt
grep -cE '^a{0,1}$' n.txt
grep -cE '^a+$'    n.txt
grep -cE '^a{1,}$' n.txt
```

**Deberías ver:** `1`, `1`, `3`, `3`. Cada atajo cuenta exactamente lo mismo que su rango.

**Pausa:** `*` es la *cerradura de Kleene* de la página 1 — la idea de 1951, escrita con un asterisco. Ahora ya sabes que es sólo el rango «de cero a lo que sea».

## Misión 2: a qué pieza se pega

Un cuantificador actúa sobre **la pieza que tiene inmediatamente a su izquierda**. A ninguna otra.

**Haz:**

```bash
printf '%s\n' 'ab' 'abbb' 'ababab' > repes.txt
grep -E '^ab*$'   repes.txt
grep -E '^(ab)*$' repes.txt
```

**Deberías ver:** `ab*` encuentra `ab` y `abbb` — repite **la `b`**, porque la pieza a su izquierda es la `b`. `(ab)*` encuentra `ab` y `ababab` — repite **el grupo entero**.

Como una clase y un grupo son **una** pieza, el cuantificador se aplica a todo el conjunto:

| Patrón | La pieza es | Repite |
|---|---|---|
| `ab*` | la `b` | sólo la `b` |
| `[ab]*` | la clase | una `a` **o** una `b`, en cualquier orden |
| `(ab)*` | el grupo | el bloque `ab` completo |

**Pausa:** los tres se escriben casi igual y no casan lo mismo. Compruébalo con `printf '%s\n' 'baba' | grep -Eo '[ab]*'` y luego con `(ab)*`.

## Misión 3: qué significa «cero veces»

::: definition {#rx-def-epsilon title="ε, la cadena vacía"}
`ε` (épsilon) es el nombre de **la cadena de longitud cero**: un texto sin ningún carácter. No es un espacio ni algo que puedas teclear — es la ausencia de caracteres.

En un autómata, un **salto ε** es una flecha que la máquina recorre **sin leer nada de la cinta**. Eso es literalmente lo que significa «cero veces»: existe un camino hasta la aceptación que no consume ningún carácter. En el dibujo de arriba, el autómata de `a?` tiene ese salto, y el de `a*` ya acepta en su estado inicial.

**Consecuencia:** una pieza cuyo mínimo es cero puede casar **en cualquier posición**, incluso donde no hay nada.
:::

**Haz:**

```bash
printf '%s\n' 'bbb' '' 'aaa' > vacio.txt
grep -nE '^a*$' vacio.txt
grep -cE 'x*'   formas.txt
```

**Deberías ver:** el primero devuelve la línea 2 —**la línea vacía**— y la 3, pero no `bbb`. El segundo devuelve `5`: **las cinco líneas**, aunque no haya una sola `x` en el archivo.

Ese `5` es la prueba de que `ε` no es una curiosidad teórica. `x*` pide «cero o más `x`», y cero `x` es algo que ocurre en todas partes. Un patrón cuyo mínimo es cero **no descarta nada**.

**Pausa:** por eso `.*$` al final de un patrón casi siempre sobra, como viste en la página 2.

## Misión 4: hasta dónde llega la repetición

::: figure {#rx-backtracking title="El goloso toma de más y después cede"}
![Sobre el texto menor a mayor que, el punto asterisco toma ocho caracteres y falla porque después no queda ningún mayor que; cede uno y entonces sí encaja, dejando una sola coincidencia que abarca todo el renglón](_assets/rx-backtracking.svg)
:::

Un cuantificador es **goloso**: primero intenta llevarse todo lo que pueda, y sólo si el resto del patrón no encaja va **cediendo** un carácter a la vez.

**Haz:**

```bash
cd ~/fdd/regex-lab
grep -Eo '<.*>'    contactos.txt | tail -1
grep -Eo '<[^>]*>' contactos.txt | tail -2
```

**Deberías ver:** el goloso devuelve, en la línea del Equipo 3, **una** coincidencia gigante del primer `<` al último `>`. La clase negada devuelve **dos**, una por correo.

> [!WARNING]
> Esto **no** contradice la página 2. Ahí lo que no retrocede es **dónde empieza** el intento: una posición descartada no se reintenta. Aquí lo que se mueve es **hasta dónde llega la repetición dentro de un mismo intento**. Son dos cosas distintas y sólo la segunda cede terreno.

`.` también casa el `>`, así que `.*` se lo pasa de largo, llega al final, y retrocede hasta encontrar el último `>`. Una clase que niega el `>` no puede pasarlo: se detiene sola, sin vaivén.

::: problem {#rx-p4-cero title="¿Por qué cinco y no cero?"}
`formas.txt` no contiene ninguna `x`. ¿Por qué `grep -cE 'x*' formas.txt` devuelve `5` y no `0`? ¿Y qué patrón habrías querido escribir?
:::

::: hint {of="rx-p4-cero"}
Traduce `x*` a su rango: `{0,}`. ¿Qué exige, como mínimo, ese patrón?
:::

::: answer {of="rx-p4-cero"}
Porque `x*` es `x{0,}` y su mínimo es **cero**: el patrón se satisface sin leer nada, así que casa en la posición 0 de cualquier línea. No pide una `x`; pide «cero o más», y cero siempre se cumple. El patrón que querías es `x+`, con mínimo uno, que devuelve `0`. La regla general: **un cuantificador de mínimo cero nunca puede, por sí solo, descartar una línea** — necesita algo obligatorio a su lado.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** traduce todo cuantificador a su rango `{mínimo, máximo}`. Si el mínimo es cero, esa pieza no está filtrando nada.

## Cierre

Ya sabes cuántas veces se repite una pieza y hasta dónde llega. Continúa con [[taquigrafia-perl|La taquigrafía de Perl]], que abrevia las clases más frecuentes.
