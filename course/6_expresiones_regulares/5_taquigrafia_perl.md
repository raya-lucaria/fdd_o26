---
id: taquigrafia-perl
title: "La taquigrafía de Perl"
nav_title: "Taquigrafía"
summary: "Las abreviaturas que verás en todos lados, cuáles funcionan en grep y cuáles son las portátiles."
status: ready
estimated_time: 12m
tags: [regex, grep, perl, posix, locale, acentos]
prerequisites: [cuantas-veces]
---

# La taquigrafía de Perl

**Página 5 de 7** · 12 min

Meta: leer los patrones abreviados que hay en internet, y escribir los que sí funcionan en tu terminal.

::: figure {#rx-clases title="Qué cubre cada clase"}
![Ocho caracteres en fila y tres bandas debajo que marcan cuáles cubre cada clase: barra d sólo el dígito, barra w las letras el dígito y el guion bajo, barra s sólo el espacio; la columna de la eñe queda marcada con un signo de interrogación porque depende del locale](_assets/rx-clases.svg)
:::

## En corto

- `\d` `\w` `\s` son abreviaturas de clases que se repiten mucho. Perl las inventó en 1987 y hoy están en todos lados.
- **`\d` no funciona en `grep -E`** — y no avisa: busca una `d` literal.
- Las clases POSIX (`[[:digit:]]`) sí funcionan en todas partes. Son las que conviene escribir.

## Prepara

```bash
mkdir -p ~/fdd/regex-lab && cd ~/fdd/regex-lab
printf '%s\n' 'a1' 'ad' 'Sofía Muñoz_3' > clases.txt
cat clases.txt
```

## Misión 1: el atajo que traiciona

**Haz:**

```bash
grep -E '\d' clases.txt
grep -E '[0-9]' clases.txt
```

**Deberías ver:** la primera devuelve `ad` — la única línea con una letra `d`. La segunda devuelve `a1` y `Sofía Muñoz_3`, las dos que sí traen un dígito. **El patrón que parecía buscar dígitos no encontró ninguno.**

`grep -E` no conoce `\d`. Cuando ve `\d`, entiende «una `d` escapada», o sea: una `d` literal. No lanza ningún error — simplemente busca otra cosa. Es el fallo silencioso más común de esta unidad.

| Abreviatura | ¿Funciona en `grep -E`? |
|---|---|
| `\w` `\s` `\b` | **Sí**, son extensiones de GNU. |
| `\d` `\D` `\S` `\W` | **No.** Se leen como el carácter literal. |
| `[[:digit:]]` `[[:alpha:]]` `[[:space:]]` | **Sí**, son POSIX y están en el estándar. |

Existe `grep -P`, que sí entiende toda la taquigrafía de Perl — pero **no viene en macOS**. Un patrón con `-P` deja de funcionar en la mitad de la clase.

## Misión 2: la tabla que sí vas a usar

| Abreviatura | Significa | Escríbelo así |
|---|---|---|
| `\d` | un dígito | `[0-9]` o `[[:digit:]]` |
| `\w` | letra, dígito o `_` | `[[:alnum:]_]` |
| `\s` | espacio, tabulador, salto | `[[:space:]]` |
| `\D` `\W` `\S` | lo contrario de cada una | la misma clase con un `^` al principio |

**Haz:** una fecha y un teléfono, escritos de la forma portátil.

```bash
grep -Eo '^[0-9]{4}-[0-9]{2}-[0-9]{2}' bitacora.log | sort -u
grep -Eo '[0-9]{2}[ -][0-9]{4}[ -][0-9]{4}' contactos.txt
```

**Deberías ver:** dos fechas distintas, y tres teléfonos de los cuatro que hay. El de Sofía, `5511223344`, no aparece: no tiene separadores.

**Pausa:** para incluirlo, el separador tendría que ser opcional. Prueba `'[0-9]{2}[ -]?[0-9]{4}[ -]?[0-9]{4}'` y observa qué cambia — ese `?` es el de la página 4.

## Misión 3: acentos y locale

Esta muerde en español, y no muerde como esperarías.

**Haz:**

```bash
grep -Eo '[a-z]+' clases.txt
grep -Eo '\w+'    clases.txt
LC_ALL=C grep -Eo '\w+' clases.txt
```

**Deberías ver** tres respuestas distintas para el mismo archivo:

| Comando | Sobre `Sofía Muñoz_3` devuelve |
|---|---|
| `[a-z]+` | `ofía`, `uñoz` — **sí** aceptó la `í` y la `ñ`, pero tiró la `S` y la `M` |
| `\w+` | `Sofía`, `Muñoz_3` — las palabras completas |
| `LC_ALL=C \w+` | `Sof`, `a`, `Mu`, `oz_3` — **aquí sí** se partieron |

Lo importante no es cuál gana, sino **por qué son tres**. Un rango como `[a-z]` no significa «estos 26 caracteres»: significa «de la `a` a la `z` **según el orden de tu locale**», y en UTF‑8 ese orden mete la `í` y la `ñ` en medio. Con `LC_ALL=C` el orden es el de la tabla ASCII, y quedan fuera.

**Pausa:** el mismo patrón, el mismo archivo, dos máquinas configuradas distinto, dos resultados. Si un script tiene que dar siempre lo mismo, fija el locale al principio en vez de confiar en el que traiga la computadora.

Regla práctica para esta unidad: con texto en español **usa `\w` o `[[:alpha:]]`, no `[a-z]`**. `[a-z]` te va a tirar las mayúsculas sin avisarte, que es el error que sí vas a cometer hoy.

## Misión 4: `\b`, la tercera ancla

Ahora que «carácter de palabra» tiene definición, se puede cerrar la familia que empezó en la página 2. `\b` marca la frontera entre un carácter de palabra y uno que no lo es. Como `^` y `$`, **no consume nada**: marca una posición, y por eso tampoco admite cuantificador.

| Ancla | Exige estar… |
|---|---|
| `^` | al principio de la línea |
| `$` | al final de la línea |
| `\b` | en el borde de una palabra |

**Haz:**

```bash
grep -o   'ana'     contactos.txt | wc -l
grep -Eo '\bana\b'  contactos.txt | wc -l
grep -c  -w 'Ana'   contactos.txt
```

**Deberías ver:** `5`, luego `3`, luego `3`.

Las cinco incluyen el `ana` que está dentro de `Mariana` y el de `mariana.solis`. Las tres son los correos `ana` seguidos de la arroba: ni el `<` ni la arroba son caracteres de palabra, así que ahí sí hay frontera.

`grep -w` hace lo mismo pero como bandera, y **funciona también en macOS**. Cuando quieras palabra completa y no estés seguro del sistema, usa `-w`.

::: problem {#rx-p4-frontera title="¿Por qué tres y no dos?"}
Sólo hay dos líneas que empiezan con `Ana Ruiz`. ¿De dónde sale la tercera coincidencia de `\bana\b`?
:::

::: hint {of="rx-p4-frontera"}
Revisa la línea del Equipo 3 con `grep -n 'Equipo' contactos.txt`.
:::

::: answer {of="rx-p4-frontera"}
De la línea del Equipo 3, que también contiene el correo `ana` seguido de arroba. `\b` no distingue posición dentro de la línea: sólo pide que a los lados no haya caracteres de palabra. Es un buen recordatorio de que el anclaje de palabra y el anclaje de línea (`^`, `$`) son cosas distintas.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** Cuando un patrón con `\d` no encuentre nada raro pero tampoco lo correcto, cámbialo por `[0-9]` antes de seguir buscando el error en otro lado.

## Cierre

Ya distingues la abreviatura cómoda de la portátil y tienes las tres anclas. Continúa con [[grupos-y-captura|Grupos y captura]], donde el patrón deja de sólo buscar y empieza a extraer.
