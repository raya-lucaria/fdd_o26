# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escríbelo aquí. Debe decir, como mínimo: la versión de Python y cómo se corre,
qué entra y qué sale, qué hacer con los casos borde, y cómo vas a verificar
que funciona.

Escribe un script en Python llamado gasolina.py que calcule el precio promedio de la gasolina por estado.

CÓMO SE CORRE
- Con `uv run gasolina.py`, usando Python 3.14.
- Sólo biblioteca estándar.

ENTRADA
- Un archivo gasolina.csv, en la misma carpeta que el script, codificado en UTF-8.
- Columnas: estado, fecha, precio.

SALIDA
1. Los estados en orden alfabético. Para cada estado, la lista de sus fechas y precios, y al final su Precio_promedio_estado con dos decimales.
2. Después, las filas no leídas: número de línea y motivo de cada una, con un aviso al usuario para que verifique los datos de precio.

REGLAS Y CASOS BORDE
- Estructura: una clase llamada `gasolinas` que recorre las filas con un for y las agrupa por estado.
- Ninguna función usa valores por defecto mutables ni modifica lo que recibe.
- Precios con Decimal, nunca float.
- Un precio con coma de miles o con signo de pesos se convierte ("2,000" y "$300" son válidos). Un precio vacío, "None" o no numérico ("3ooo") no detiene el programa: la fila se reporta en las filas no leídas.
- Dos nombres de estado son el mismo estado aunque difieran en espacios sobrantes, mayúsculas o acentos (" Estado de México" y "estado de mexico" se agrupan juntos). En la salida, muestra el nombre como aparece la primera vez en el archivo, sin espacios sobrantes.
- Una fila sin estado se reporta en las filas no leídas.
- Un estado sin precios válidos aparece en la salida como "sin precios válidos", sin promedio.
- Si gasolina.csv no existe, imprime "Archivo gasolina.csv no encontrado" y termina.
- Si gasolina.csv está vacío (sin contenido o sólo con encabezado), imprime "El archivo gasolina.csv está vacío" y termina.

VERIFICACIÓN
Antes del código, dame la firma de cada función con type hints y un caso de prueba por rama, incluidos: archivo vacío, precio vacío, precio con coma de miles y estado sin precios válidos.
