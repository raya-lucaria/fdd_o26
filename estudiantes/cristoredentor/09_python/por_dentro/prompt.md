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

Consideraciones iniciales: 

Para las siguientes instrucciones no te salgas de la carpeta fdd_o26/estudiantes/cristoredentor/09_python/por_dentro. Todo lo que te pido hacer hazlo ahí adentro.

Sobre el código:

Usando Python 3.14 quiero que escribas un scrpit llamado gasolina.py que calcule el precio promedio de gasolina por estado.

En el .venv encontrarás más información sobre las librerias y sus versiones.

Para correrlo quiero que uses uv run gasolina.py.

Entradas y salidas:

EL script tendrá como entrada as columnas estado, fecha y precio de gasolina.csv que está en la carpeta por_dentro (la misma que te dije que no te salieras) y quiero que lo codifiques en UTF-8.

Como salida quiero el precio promedio. 

Casos a considerar: 

- Considera que algunas columnas tienen precio vacio, si representan menos del 1% eliminalas, si no cambia su precio por la mediana.

- Algunas columnas tienen comas, quitalas.

Verificación:

Quiero que hagas un archivo test que sirva para usar pytest y verificar que cumple con los casos esquina, de esa manera lo verificaremos.