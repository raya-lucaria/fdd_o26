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

1. **Separa el patrón en piezas** de izquierda a derecha. Una pieza es un carácter literal, un `.`, una clase `[…]` o un grupo `(…)`.
2. **Marca los cuantificadores.** Cada uno pertenece a la pieza que tiene justo a la izquierda, y todos son un rango: `?`=`{0,1}`, `*`=`{0,}`, `+`=`{1,}`. Si el mínimo es cero, esa pieza no filtra nada.
3. **Localiza las anclas.** `^` `$` `\b` no consumen nada: sólo exigen estar en cierta posición.
4. **Pruébalo con dos o tres cadenas inline.** Lo que imprime es lo que el patrón realmente encuentra:

```bash
printf '%s\n' 'casa que sí' 'casa que no' | grep -nE 'patrón'
```

`-n` numera la entrada, así ves cuáles pasaron y deduces cuáles no. Con `-o` ves además **qué pedazo** se llevó.

Está aplicado paso a paso, sobre el patrón de correo, en [[grupos-y-captura|la página 6]].

## Las dos clases de cosas que hay en un patrón

| | Se lleva caracteres | Ejemplos |
|---|---|---|
| **Pieza** | sí | `a` · `.` · `[0-9]` · `(ab)` |
| **Ancla** | no, sólo mira la posición | `^` · `$` · `\b` |

Un cuantificador se pega a **una pieza**; una ancla no admite cuantificador porque no hay nada que repetir.

## El mismo símbolo, según dónde esté

| Símbolo | Suelto | Dentro de `[ … ]` |
|---|---|---|
| `.` | cualquier carácter | un punto literal |
| `*` `+` `?` | cuantifican | literales |
| `^` | inicio de línea | niega, **sólo** si va primero |
| `-` | guion literal | rango, salvo en los extremos |
| `]` | corchete literal | cierra, salvo si va primero |

`\` ante un metacarácter lo vuelve literal. Ante cualquier otra cosa el resultado lo decide el motor: por eso `\d` en `grep -E` busca una `d`.

## Sintaxis

| Escribes | Significa | Dónde |
|---|---|---|
| `abc` | esos tres caracteres, en ese orden | [[que-es-una-regex|1]] |
| `.` | un carácter cualquiera menos el salto de línea | [[leer-izquierda-derecha|2]] |
| `\.` | un punto literal; `\` escapa cualquier metacarácter | [[leer-izquierda-derecha|2]] |
| `^` `$` | inicio y fin de línea | [[leer-izquierda-derecha|2]] |
| `[abc]` | uno de esos caracteres | [[piezas-de-un-patron|3]] |
| `[a-z]` | un rango, según el locale | [[piezas-de-un-patron|3]] |
| `[abc]` con `^` al principio | uno que **no** sea de esos | [[piezas-de-un-patron|3]] |
| `?` | `{0,1}` — cero o una vez | [[cuantas-veces|4]] |
| `*` | `{0,}` — cero o más veces | [[cuantas-veces|4]] |
| `+` | `{1,}` — una o más veces | [[cuantas-veces|4]] |
| `{2,4}` | entre dos y cuatro veces | [[cuantas-veces|4]] |
| `ε` | la cadena vacía: cero caracteres. Es lo que casa una pieza cuyo mínimo es cero | [[cuantas-veces|4]] |
| `\w` `\s` `\b` | palabra, espacio, frontera de palabra | [[taquigrafia-perl|5]] |
| `[[:digit:]]` | la clase POSIX portátil | [[taquigrafia-perl|5]] |
| `(ab)` | un grupo: una sola pieza, y se captura | [[grupos-y-captura|6]] |
| `a\|b` | alternancia; parte la expresión completa | [[grupos-y-captura|6]] |
| `\1` | lo que capturó el primer grupo | [[grupos-y-captura|6]] |

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
