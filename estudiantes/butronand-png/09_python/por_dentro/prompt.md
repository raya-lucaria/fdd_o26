# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Necesito un script de Python que calcule el precio promedio de la gasolina por estado. Antes de escribir código, dame una lista corta de los supuestos que haces sobre los datos. Si alguno contradice lo que te digo abajo, pregúntame antes de seguir.

**Entorno y cómo se corre**

- Python 3.14, sólo con la biblioteca estándar (`csv`, `decimal`, `pathlib`, `sys`). Nada de pandas ni de otras dependencias.
- Un solo archivo, `promedio_gasolina.py`, que se corre con `uv run promedio_gasolina.py gasolina.csv`.
- La ruta del CSV llega como argumento. Sin argumento, el script explica cómo se usa y termina con código 2.

**Qué entra**

- `gasolina.csv`, en UTF-8 y con encabezado, con tres columnas: `estado`, `fecha` y `precio`. Puede traer BOM, así que ábrelo con `encoding="utf-8-sig"`.
- Léelo con `csv.DictReader`. No partas las líneas por comas: los precios con coma de miles vienen entre comillas.

**Qué sale**

- Por la salida estándar, una tabla con tres columnas, ordenada alfabéticamente por estado: el estado, cuántos precios válidos tiene y el precio promedio. El promedio va redondeado a centavos con `ROUND_HALF_UP`.
- Por la salida de errores, un aviso por cada fila descartada, con su número de línea en el archivo y el motivo.
- Al final, también por la salida de errores, un resumen: cuántas filas leyó, cuántas fueron válidas y cuántas descartó.
- Código de salida 0 si terminó. Código 1 si no pudo abrir el archivo o si le falta alguna de las tres columnas.

**Casos borde y qué hacer en cada uno**

- Precio vacío o con sólo espacios: la fila no cuenta para el promedio y se reporta como descartada. No es un cero.
- Precio con coma de miles, como `"1,234.50"`: quita las comas y conviértelo. Es un precio válido.
- Precio que no es número aun sin comas, como `abc` o `n/d`: descarta la fila y repórtala con su línea, sin detener el script.
- Precio cero o negativo: descarta la fila y repórtala.
- Estado vacío: descarta la fila y repórtala.
- Estado con espacios en los extremos: quítalos. No cambies mayúsculas ni minúsculas.
- Estado que se queda sin ningún precio válido: aparece en la tabla con 0 precios y `sin datos` en el promedio, no con una división entre cero.
- La columna `fecha` no se usa en el cálculo; no la valides.

**Reglas para el código**

- Usa `Decimal` para los precios y la suma, creado desde el texto y nunca desde un `float`.
- No escribas `except` vacíos ni `except Exception: pass`. Atrapa sólo el error que esperas, `decimal.InvalidOperation`, y repórtalo.
- Ningún argumento de función con una lista o un diccionario como valor por defecto.
- Nada de hilos ni de procesos: el archivo es chico.
- Separa el cálculo de la lectura y de la impresión. Haz una función `promedios(filas)` que reciba las filas ya leídas y regrese un diccionario `{estado: (n, promedio)}`, para poder probarla sola.

**Cómo lo voy a verificar**

Escribe también `test_gasolina.py`, con pytest, y dime el comando exacto para correrlo con uv. Las pruebas usan estas filas, cuyo resultado ya calculé a mano:

```csv
estado,fecha,precio
CDMX,2026-10-01,24.10
CDMX,2026-10-02,
CDMX,2026-10-03,24.31
Jalisco,2026-10-01,"1,200.00"
Jalisco,2026-10-02,1000.00
Oaxaca,2026-10-01,abc
```

Lo que espero:

- CDMX: 2 precios y promedio 24.21. El promedio exacto es 24.205: con `float` sale 24.20, y con el redondeo por omisión de `Decimal` también sale 24.20. Sólo con `ROUND_HALF_UP` sale 24.21.
- Jalisco: 2 precios y promedio 1100.00. Prueba la coma de miles.
- Oaxaca: 0 precios y `sin datos`. Prueba el precio que no es número.
- Resumen: 6 filas leídas, 4 válidas y 2 descartadas, las de las líneas 3 y 7 del archivo.

Al final, explícame en cinco líneas qué decide el script en cada caso borde, para revisarlo contra esta lista. Después lo voy a correr con el archivo real y voy a comprobar a mano el promedio de un estado.
