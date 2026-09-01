---
id: chuleta-regex
title: "Chuleta"
nav_title: "Chuleta"
summary: "La referencia completa de la unidad, en un solo lugar: sintaxis, banderas y los errores frecuentes."
status: ready
estimated_time: 5m
tags: [regex, grep, referencia, chuleta]
prerequisites: [grep-awk-en-serio]
---

# Chuleta

Apéndice · para consultar, no para memorizar

Todo lo de esta unidad, junto. Si algo de aquí no te suena, la columna «dónde» te dice a qué página volver.

## Cómo leer una regex que no escribiste

1. **Separa el patrón en piezas** de izquierda a derecha. Cada pieza es un carácter, una clase `[…]` o un grupo `(…)`.
2. **Marca los cuantificadores.** Cada `? * + {n,m}` pertenece a la pieza que tiene justo a la izquierda.
3. **Localiza los anclajes.** `^` `$` `\b` no consumen nada: sólo exigen estar en cierta posición.
4. **Pruébalo con `grep -o`** sobre un archivo pequeño. Lo que imprime es lo que el patrón realmente encuentra.

## Sintaxis

| Escribes | Significa | Dónde |
|---|---|---|
| `abc` | esos tres caracteres, en ese orden | [[que-es-una-regex|1]] |
| `.` | un carácter cualquiera menos el salto de línea | [[leer-izquierda-derecha|2]] |
| `\.` | un punto literal; `\` escapa cualquier metacarácter | [[leer-izquierda-derecha|2]] |
| `^` `$` | inicio y fin de línea | [[leer-izquierda-derecha|2]] |
| `[abc]` | uno de esos caracteres | [[clases-y-repeticion|3]] |
| `[a-z]` | un rango, según el locale | [[clases-y-repeticion|3]] |
| `[abc]` con `^` al principio | uno que **no** sea de esos | [[clases-y-repeticion|3]] |
| `?` | cero o una vez | [[clases-y-repeticion|3]] |
| `*` | cero o más veces | [[clases-y-repeticion|3]] |
| `+` | una o más veces | [[clases-y-repeticion|3]] |
| `{2,4}` | entre dos y cuatro veces | [[clases-y-repeticion|3]] |
| `\w` `\s` `\b` | palabra, espacio, frontera de palabra | [[taquigrafia-perl|4]] |
| `[[:digit:]]` | la clase POSIX portátil | [[taquigrafia-perl|4]] |
| `(ab)` | un grupo: una sola pieza, y se captura | [[grupos-y-captura|5]] |
| `a\|b` | alternancia; parte la expresión completa | [[grupos-y-captura|5]] |
| `\1` | lo que capturó el primer grupo | [[grupos-y-captura|5]] |

## Banderas de `grep`

Todas se usan en [[grep-awk-en-serio|la página 6]].

| Bandera | Qué hace |
|---|---|
| `-E` | dialecto extendido — úsala siempre |
| `-o` | imprime la coincidencia, no la línea |
| `-i` | ignora mayúsculas |
| `-v` | invierte: deja pasar lo que no casa |
| `-c` | cuenta **líneas**, no coincidencias |
| `-n` | antepone el número de línea |
| `-w` | palabra completa, portátil |
| `-h` | oculta el nombre del archivo |
| `-r` | recorre un directorio |
| `-F` | texto literal, sin interpretar nada |

## Los siete errores que sí vas a cometer

| Síntoma | Causa | Arreglo |
|---|---|---|
| Un patrón con `?` o `+` no encuentra nada | falta `-E`: `grep` a secas habla BRE | agrega `-E` |
| `\d` no encuentra dígitos | `grep -E` lee `\d` como una `d` literal | `[0-9]` o `[[:digit:]]` |
| La coincidencia se comió media línea | `.*` es goloso | una clase que niegue el carácter de cierre |
| El filtro deja pasar todo | falta un paréntesis alrededor de la alternancia | `^(a\|b)$`, no `^a\|b$` |
| Encuentra `ana` dentro de `Mariana` | la regex casa subcadenas | `\bana\b` o `grep -w` |
| El patrón desapareció o cambió | Bash lo expandió antes de `grep` | comillas simples |
| `$` no casa al final | el archivo trae `\r` de Windows | `cat -A` para verlo, `tr -d '\r'` para limpiarlo |

## Recetas

```bash
# Extraer y normalizar correos de un archivo sucio
grep -Eoih '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}' entrada.txt \
  | tr 'A-Z' 'a-z' | sort -u > correos.txt

# Cuántas líneas tienen ERROR, y en qué renglón está cada una
grep -c 'ERROR' bitacora.log
grep -n 'ERROR' bitacora.log

# Quedarse con las líneas que NO son comentarios ni están vacías
grep -Ev '^\s*(#|$)' config.txt

# Buscar en un proyecto sin entrar en .git
grep -rn --exclude-dir=.git -E 'TODO|FIXME' .

# Palabras repetidas
grep -Eo '\b(\w+) \1\b' texto.txt

# Quedarse sólo con el dominio de cada correo
sed -E 's/^[^@]+@(.+)$/\1/' correos.txt
```

## Dónde deja de servir

Una expresión regular describe un lenguaje **regular**: no puede contar niveles de anidamiento. Por eso no sirve para separar campos de un CSV con comillas, ni para recorrer HTML o JSON. Para eso hay parsers. La regex se usa **dentro** de un campo que un parser ya extrajo.

Y ninguna regex valida un correo electrónico. Filtra candidatos; lo único que demuestra que una dirección funciona es mandarle un mensaje.

## Para seguir

- [Manual de GNU grep](https://www.gnu.org/software/grep/manual/grep.html) — la referencia oficial, con la diferencia entre BRE y ERE.
- [Manual de GNU sed](https://www.gnu.org/software/sed/manual/sed.html) — sustitución y captura.
- [Manual de GNU awk](https://www.gnu.org/software/gawk/manual/gawk.html) — columnas, patrones y acciones.
