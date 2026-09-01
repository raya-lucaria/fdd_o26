# Unidad 6 — Expresiones regulares

Fecha: 2026-09-01 · Estado: aprobado en chat

## Qué es

Una unidad de una sesión (1–1.5 h) que lleva a alguien que **nunca** ha visto
una regex desde «una cadena literal ya es una regex» hasta filtrar y limpiar
texto con `grep -E`, `sed -E` y dos líneas de `awk`. Sesión `session-07`,
2026-09-01, 19:00–20:30.

Sin tarea, sin flashcards, sin quizzes: **sólo contenido**. Los objetos
oficiales se agregan después, si se agregan.

## Idea que sostiene toda la unidad

> La regex es una cabeza lectora que avanza de izquierda a derecha y no
> regresa gratis.

Cada construcción nueva se introduce como respuesta a un fallo concreto de esa
cabeza, nunca como definición suelta. Los edge cases no son adorno: son el
método. `grep -o 'aa'` sobre `aaaa` da dos coincidencias, y esa sorpresa es lo
que hace visible el modelo mental.

## Estructura

Archivos planos, como `ia_o26/course/3_computabilidad`, no directorios con
`0_index.md`. Un solo `_assets/` en la raíz de la unidad.

| Archivo | Página | Minutos |
|---|---|---:|
| `0_index.md` | mapa, laboratorio, ritmo | — |
| `1_que_es_una_regex.md` | historia y primer `grep` | 10 |
| `2_leer_izquierda_derecha.md` | la cabeza lectora | 15 |
| `3_clases_y_repeticion.md` | `[]` `?` `*` `+` `{n,m}` | 15 |
| `4_taquigrafia_perl.md` | `\d \w \s \b` y POSIX | 12 |
| `5_grupos_y_captura.md` | `()` `|` `\1`, `sed -E`, email | 15 |
| `6_grep_awk_en_serio.md` | banderas, `history`, `awk` | 15 |
| `A_chuleta.md` | referencia, fuera de la lección | — |

## Decisiones de contenido

- **`grep -E` siempre.** La trampa BRE/ERE se muestra una vez, temprano, y
  después la unidad vive en ERE. `-P` sólo se menciona para decir que no existe
  en macOS.
- **`grep -o` desde la página 2.** Es lo que separa «grep imprime la línea» de
  «la regex encontró esta subcadena». Sin eso, todo lo demás confunde.
- **POSIX al lado de Perl.** `\d` se enseña porque se ve en todos lados;
  `[[:digit:]]` se enseña porque siempre funciona.
- **Acentos.** `\w` y `[a-z]` no casan `ñ` ni `á`. Con nombres en español eso
  muerde en el primer ejercicio, así que se plantó un `Muñoz` en los datos.
- **Honestidad al cerrar.** Ninguna regex valida un email (RFC 5322); regex no
  es un parser de CSV/HTML/JSON. Sirve para encontrar y filtrar.

## La traza como tabla

El recurso pedagógico central es una `::: table` que muestra la cabeza lectora
intentando desde cada posición, copiando `comp-traza-acepta` de `ia_o26`. Se
repite con la misma forma en las páginas 2, 3 y 5.

## Laboratorio

`~/fdd/regex-lab`, creado con un heredoc `<<'EOF'`. Tres archivos con las
trampas **ya plantadas en los datos**, para que ningún ejemplo se sienta de
juguete:

- `contactos.txt` — `Ana`/`Mariana`, mayúsculas, `+tag`, punto final, dos
  arrobas, sin parte local, teléfonos en tres formatos, un `Muñoz`.
- `bitacora.log` — niveles ERROR/WARN/INFO, una línea malformada, una palabra
  repetida para `\1`, y `<a> y <b>` para el caso goloso.
- `precios.csv` — un `N/A`, uno con `$`, y una coma dentro de comillas.

## Reglas anti-dispersión

Encargo explícito: la unidad tiene que funcionar para alguien con déficit de
atención. Reglas duras, verificadas por `tools/test_regex_curriculum.py`:

- ≤ 160 líneas por página (el techo se movió de 130 a 160 al escribir: 160 son unas tres pantallas y la unidad 5 llegaba a 268).
- Cada página abre con **Meta (una línea) → diagrama → «En corto» (3 viñetas)**.
- «Página N de 6» arriba.
- Cada misión crea su propio input: se puede entrar por cualquier página.
- Exactamente un `problem`+`hint`+`answer` por página.
- Un `::: note` de una frase al cerrar: «Si sólo recuerdas una cosa…».
- Toda la referencia larga vive en `A_chuleta.md`, no dentro de la lección.

## Diagramas

`tools/gen_regex.py`, determinista, con las primitivas de
`ia_o26/tools/gen_computabilidad.py` (`marco`, `estado`, `curva`, `bucle`) y la
paleta de `skins/fdd-eva.yaml`. Prefijo `rx-` porque los ids de objeto numerado
son únicos en todo el curso.

| Id | Qué muestra |
|---|---|
| `rx-que-es` | patrón + texto → motor → líneas que pasan |
| `rx-cabeza` | la cinta, un intento fallido y uno exitoso |
| `rx-automata-ana` | autómata de `ana`, con el regreso a q0 |
| `rx-cuantificadores` | `?`, `*`, `+` como tres autómatas diminutos |
| `rx-goloso` | `.*` contra `[^>]*` sobre el mismo texto |
| `rx-clases` | tira de caracteres con las bandas `\d`, `\w`, `\s` |
| `rx-alternancia` | `^ana\|beto$` contra `^(ana\|beto)$` |
| `rx-automata-email` | el autómata de cinco estados: la lámina central |

Guarda: `tools/test_gen_regex.py` regenera antes de comparar, exige el prefijo
`rx-` y las cinco convenciones de la raíz `<svg>` (`width`, `height`,
`viewBox`, `role`, `aria-label`) más el fondo horneado.

`tools/test_creditos.py` se generaliza a todas las unidades con un mapa
`ASSETS_POR_UNIDAD`, como `ia_o26/tools/unidades.py`: hoy sólo vigila
`2_pipeline_de_datos`, y eso deja sin protección a la unidad 5 y a esta.

## Calendario

`session-07`, 2026-09-01, 19:00–20:30, `page: expresiones-regulares`.


## Tres cosas que sólo aparecieron al construir

**`[^X]` colisiona con la sintaxis de nota al pie.** Raya busca referencias con
`(?<!\\)\[\^([^\]\s]+)\]` sobre el cuerpo al que sólo le quita los bloques
cercados: un code span en línea **no** protege. Como la clase negada es la
construcción más útil de la unidad, tumbaba el build entero con «Missing
footnote definition» en cuatro páginas. La regla que quedó: las clases negadas
se muestran dentro de un bloque ```` ```bash ````, y en prosa y en tablas se
nombran en palabras. `tools/test_regex_curriculum.py` lo vigila.

**`note` no es una familia de objeto numerado.** El cierre de cada página va
como callout `> [!NOTE]`, igual que los avisos de la unidad 5.

**El locale cambia el resultado más de lo previsto.** El plan decía que `\w` y
`[a-z]` no cubren letras acentuadas. Medido con GNU grep 3.7 en UTF‑8, `[a-z]+`
sobre `Sofía Muñoz_3` devuelve `ofía` y `uñoz` —sí acepta la `í` y la `ñ`, y
tira las mayúsculas— mientras que `LC_ALL=C` con `\w+` sí las parte. La lección
real no es «los acentos no entran» sino «un rango se resuelve según el orden
del locale, así que el mismo patrón responde distinto en dos máquinas». El
diagrama `rx-clases` marca esa columna con `?` en vez de con vacío.

## Diagrama que se agregó

`rx-tuberia` (noveno): la limpieza como cadena de cinco eslabones, señalando
que sólo el segundo usa una expresión regular. Nació porque la página 6 se
quedaba sin ancla visual.

## Estado

Nueve diagramas, ocho páginas, tres guardas nuevas o ampliadas
(`test_gen_regex.py`, `test_regex_curriculum.py`, `test_creditos.py`
generalizado). `pytest tools/`: 385 pasan. `raya build` con el SHA que fija CI
(`9f17ce9`): sin errores.

Pendiente deliberado: la unidad no trae tarea, flashcards ni quizzes.
