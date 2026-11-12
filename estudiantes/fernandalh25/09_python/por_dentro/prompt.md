# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escribe un script en Python 3.14 que lea el archivo gasolina.csv en UTF-8. El archivo tiene las columnas estado, fecha y precio.

El programa debe calcular el precio promedio de gasolina por estado e indicar para cada estado cuántas observaciones válidas se usaron.

Al leer el archivo, algunas filas pueden tener el precio vacío o contener comas de miles. Esas filas no deben provocar que el programa falle: los valores vacíos deben identificarse como datos faltantes y los precios con comas deben convertirse correctamente antes de hacer los cálculos. Asimismo, considera que las fechas pueden venir en distintos formatos, estanadriza con yyyy-mm-dd. Todo lo relacionado a importes ponlo con Decimal. Por último, para la columna de estados no diferencíes entre mayúsculas y minúsculas, ni acentos.

La salida debe mostrar, para cada estado, su precio promedio y el número de registros utilizados. Si un estado no tiene precios válidos, también debe indicarse. Al usar try-catch manda uin mensaje desarrollando qué pasó, no sólo omitas.

El script se ejecutará con uv run gasolina.py

Antes de escribir el código, indica brevemente qué funciones usarías, qué recibe y devuelve cada una y qué condicioes especiales de datos considerarías.

Para verificar que funciona, incluye pruebas con un precio normal, un precio vacío,  un precio con coma de miles y un estado sin precios válidos.

