# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escríbeme un script de Python 3.14 que use solo la biblioteca estándar (csv, decimal, sys). Se corre así: `uv run promedio_gasolina.py gasolina.csv`.

Entrada: un CSV en UTF-8 con encabezado `estado,fecha,precio`. La fecha viene como AAAA-MM-DD. El precio es en pesos por litro. Algunas filas traen el precio vacío y otras traen coma de miles, por ejemplo "1,250.50".

Salida: por pantalla, una línea por estado, ordenada alfabéticamente, con el formato `estado,precio_promedio` y el promedio con 2 decimales. Al final, un resumen con cuántas filas leyó, cuántas usó y cuántas descartó.

Casos borde:
- Precio vacío: no cuenta para el promedio, pero la fila se anota como descartada.
- Coma de miles: quítala antes de convertir el número.
- Precio que no sea número, o que sea cero o negativo: descarta la fila y avísame en stderr el número de fila y el motivo.
- Estado con espacios de más o con mayúsculas distintas ("Jalisco", " jalisco "): trátalos como el mismo estado.
- Estado sin ningún precio válido: que aparezca en la salida como "sin datos".
- Archivo que no existe o sin las tres columnas: mensaje claro y código de salida distinto de 0.

Reglas de código: usa Decimal para el dinero, no float, y redondea a centavos solo al final. No uses un `except` vacío: captura solo el error que esperas y dime qué falló. No uses listas ni diccionarios como valor por defecto en las funciones. No afirmes que algo es más rápido sin medirlo.

Cómo voy a verificar que funciona: entrégame también pruebas con pytest sobre un CSV chico de ejemplo, con las respuestas calculadas a mano (3 estados, una fila con precio vacío, una con coma de miles y una con el estado en otras mayúsculas). Incluye un caso con un archivo vacío y otro con un estado cuyos precios están todos vacíos. Las pruebas deben comprobar que filas leídas = filas usadas + filas descartadas. Yo voy a correr las pruebas y a comparar a mano el promedio de al menos un estado antes de creerle al script.

Responde con el código del script, el de las pruebas y una lista corta de las suposiciones que hiciste.