# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escribe un script de Python 3.13, `promedio_gasolina.py`, que se corra con
`uv run promedio_gasolina.py gasolina.csv` dentro de un proyecto de uv. Usa sólo
la biblioteca estándar (`csv`, `decimal`, `sys`); no agregues dependencias. Si
crees que hace falta una librería, dímelo antes con su nombre exacto en PyPI.

**Entrada.** Un CSV en UTF-8 con encabezado y tres columnas: `estado` (texto),
`fecha` (`AAAA-MM-DD`) y `precio` (pesos por litro, texto). Ábrelo con
`newline=""` y `encoding="utf-8"`. La ruta llega como primer argumento.

**Salida.** Una línea por estado, ordenada alfabéticamente, con el formato
`estado: promedio (n precios)`, y el promedio redondeado a dos decimales.
Al final, una línea con cuántas filas se descartaron y por qué.

**Casos borde, uno por uno:**

- Precio vacío o sólo espacios: la fila **no** cuenta para el promedio (no es
  un precio de 0) y se reporta como descartada.
- Precio con coma de miles (`"1,234.50"`): quita las comas antes de convertir.
- Precio que no es un número después de eso: se descarta y se reporta con su
  número de fila. Atrapa sólo `decimal.InvalidOperation`/`ValueError`; nada de
  `except Exception: pass`.
- Espacios alrededor de `estado`: quítalos, para que `"Jalisco "` y `"Jalisco"`
  sean el mismo estado.
- Un estado sin ningún precio válido aparece con `sin datos`, no con 0 ni con
  un error de división.
- Para el dinero usa `Decimal` construido desde el texto, nunca `float`.
- No uses listas ni diccionarios mutables como valores por defecto de una
  función.

**Cómo lo voy a verificar.** Antes de dar el código, escribe 3 o 4 líneas de un
`gasolina.csv` de prueba con un precio vacío, uno con coma de miles y un estado
con espacio al final, y la salida exacta que debe dar tu script con ellas,
calculada a mano. Después dame pruebas con `pytest` para esos tres casos. Yo
voy a correr el script y las pruebas y a comparar contra tu salida esperada.
