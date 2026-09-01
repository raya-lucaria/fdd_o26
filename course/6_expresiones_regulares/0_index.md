---
id: expresiones-regulares
title: "Expresiones regulares"
nav_title: "Regex"
summary: "Seis páginas para leer, escribir y depurar expresiones regulares con grep, desde cero."
status: ready
estimated_time: 97m
tags: [regex, grep, sed, awk, terminal, texto]
prerequisites: [bash-scripting]
---

# Expresiones regulares

![Sala de máquinas nocturna en verde y ámbar: una cinta horizontal de celdas luminosas la cruza de lado a lado; un cabezal de luz la recorre dejando apagadas las celdas ya consumidas y encendidas las que faltan, mientras tres hilos de luz se bifurcan hacia el fondo y vuelven a converger en un solo nodo.](_assets/ilus-regex-portada.jpg)

## En corto

- Una **regex** es un patrón que describe un conjunto de cadenas. `grep` la usa para decidir qué líneas pasan.
- Todo se explica con la misma imagen: **una cabeza que lee de izquierda a derecha y nunca regresa gratis**.
- Vas a practicar en `~/fdd/regex-lab`, una carpeta local y desechable: **no es un repositorio**.

## Mapa de la unidad

Siete páginas en orden. Cada una agrega **una sola** idea nueva sobre la anterior.

| # | Página | Qué agrega | Tiempo |
|---:|---|---|---:|
| 1 | [[que-es-una-regex|Qué es y de dónde salió]] | el primer `grep`, y por qué una cadena literal ya es una regex | 10 min |
| 2 | [[leer-izquierda-derecha|Leer de izquierda a derecha]] | la cabeza lectora · `.` · `^` `$` · el escape | 15 min |
| 3 | [[piezas-de-un-patron|Las piezas de un patrón]] | qué cuenta como **una** pieza · `[…]` · qué significa cada símbolo según dónde esté | 15 min |
| 4 | [[cuantas-veces|Cuántas veces]] | `?` `*` `+` `{n,m}` como un solo rango · `ε` · hasta dónde llega la repetición | 15 min |
| 5 | [[taquigrafia-perl|La taquigrafía de Perl]] | `\d`, `\w`, `\s`, `\b` y sus equivalentes POSIX | 12 min |
| 6 | [[grupos-y-captura|Grupos y captura]] | `(…)`, la alternancia, `\1`, y `sed -E` para reescribir | 15 min |
| 7 | [[grep-awk-en-serio|grep, history y awk]] | las banderas que sí usarás y una limpieza real | 15 min |

Al final está [[chuleta-regex|la chuleta]]: la referencia completa vive ahí, fuera de la lección, para que no tengas que buscarla entre los ejercicios.

## Ritmo de trabajo

| Paso | Qué haces |
|---|---|
| **Haz** | Ejecuta el bloque tal cual, dentro del laboratorio. |
| **Comprueba** | Compara la salida con lo que dice «Deberías ver». |
| **Pausa** | Cambia **una sola cosa** y explica por qué cambió el resultado. |

Cada página se puede abrir sola: todas empiezan preparando el archivo que van a usar. Si te distraes a la mitad, vuelve al principio de esa página y sigue desde ahí.

## Dos reglas que se repiten toda la unidad

1. **Comillas simples siempre** alrededor del patrón. Bash ve `*`, `$`, `?` y `\` antes que `grep`; las comillas simples le dicen que no toque nada. Esto es lo mismo que viste en [[como-lee-bash|Cómo lee Bash]].
2. **`grep -E` siempre.** `grep` sin `-E` habla un dialecto más viejo donde `+`, `?`, `(` y `|` necesitan barra invertida. La página 3 te muestra la trampa una vez y después no volvemos a ella.

Y una idea que se repite las siete páginas: un patrón es **una fila de piezas**, cada una con un cuantificador opcional. Casi toda duda se resuelve preguntando dónde empieza y dónde acaba una pieza.

## Antes de empezar

Necesitas una terminal Unix: Ubuntu, Ubuntu dentro de WSL2 o macOS, y `grep` — que ya viene instalado en las tres. Si vienes de [[terminal-y-bash|Terminal y Bash]], no necesitas nada más.

## Qué te llevas

- Puedes leer una regex que no escribiste y predecir qué va a encontrar.
- Sabes por qué un patrón encontró de más o de menos, y cómo acotarlo.
- Puedes escribir una tubería que extraiga y limpie datos de un archivo sucio.
