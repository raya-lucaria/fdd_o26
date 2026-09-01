# Créditos de materiales de la unidad

Procedencia, ruta y condición de uso de cada material del directorio.

Los nueve SVG salen de `tools/gen_regex.py`, que es su única fuente de verdad:
no se editan a mano, se regeneran. La guarda `tools/test_gen_regex.py` falla si
un archivo del disco deja de coincidir con lo que produce el generador.

| Archivo | Descripción y prompt resumido | Autor / origen | Fecha | Licencia |
|---|---|---|---|---|
| rx-que-es.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-que-es.svg`. Diagrama funcional: un patrón y un archivo entran a un motor de expresiones regulares y salen sólo las líneas que coinciden. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-cabeza.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-cabeza.svg`. Cinta de siete celdas con la palabra «Mariana» y cinco intentos sucesivos del patrón `ana`, cada uno una posición más a la derecha. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-automata-ana.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-automata-ana.svg`. Autómata finito de cuatro estados que reconoce la subcadena `ana`, con los bucles y los regresos al estado inicial. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-cuantificadores.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-cuantificadores.svg`. Tres autómatas diminutos lado a lado para `a?`, `a*` y `a+`. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-goloso.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-goloso.svg`. El mismo renglón con dos patrones: `<.*>` marca una coincidencia que abarca todo y `<[^>]*>` marca dos cortas. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-clases.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-clases.svg`. Ocho caracteres y tres bandas que marcan qué cubre `\d`, `\w` y `\s`; la columna de la eñe queda marcada como dependiente del locale. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-alternancia.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-alternancia.svg`. Dos autómatas que comparan dónde caen los anclajes con y sin paréntesis alrededor de la alternancia. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-automata-email.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-automata-email.svg`. Autómata de cinco estados del patrón de correo, con cuatro cadenas de prueba y su resultado. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |
| rx-tuberia.svg | Ruta: `course/6_expresiones_regulares/_assets/rx-tuberia.svg`. Cadena de cinco eslabones de una limpieza, señalando que sólo el segundo usa una expresión regular. | Diagrama original del curso, generado por `tools/gen_regex.py` | 2026-09-01 | Uso docente del curso |

Ninguna imagen de esta unidad procede de terceros: los nueve diagramas se
escriben desde el generador, con la paleta de `skins/fdd-eva.yaml`.
