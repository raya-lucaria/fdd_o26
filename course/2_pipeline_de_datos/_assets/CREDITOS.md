# Créditos de imágenes

Procedencia y licencia de cada imagen de la unidad. Toda imagen del directorio
debe tener una fila aquí — `tools/test_creditos.py` falla si falta alguna.

Los diagramas `d-*.svg` los produce `tools/gen_diagramas.py` de forma
determinista. No se editan a mano: se regeneran.

Las ilustraciones `ilus-*.jpg` se generan con la API de imágenes de OpenAI a
partir de los prompts de `tools/ilustraciones.json`. **Ninguna ilustración
representa personas reales, rostros reconocibles ni personajes con derechos**:
todas son escenas industriales abstractas y `tools/test_ilustraciones.py` falla
si algún prompt pide lo contrario.

| Archivo | Descripción | Autor / origen | Licencia |
|---|---|---|---|
| d-dag.svg | El pipeline como grafo dirigido acíclico: las etapas se bifurcan y vuelven a converger | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-schema.svg | Schema-on-write frente a schema-on-read: base de datos, data lake, data warehouse y lakehouse | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-etl-elt.svg | ETL frente a ELT, con la caída del costo del almacenamiento como causa del cambio de orden | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-tidy.svg | Tidy data: variables en columnas, observaciones en filas, valores en celdas | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-calidad.svg | Las seis dimensiones de la calidad de los datos y su falla típica | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-idempotencia.svg | La misma corrida dos veces: idempotente da el mismo resultado, no idempotente duplica | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-tiempo.svg | Batch, micro-batch, streaming y CDC sobre una línea de tiempo, con su latencia | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-ciclo.svg | Ciclo de vida de un proyecto de datos como lazo de seis etapas | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| ilus-portada.jpg | Circuito industrial cerrado: el mismo caudal recorre el trazo una y otra vez | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-viaje.jpg | Cuatro depósitos de forma distinta conteniendo el mismo caudal de maneras diferentes | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-etl-elt.jpg | Dos rutas paralelas que recorren las mismas estaciones en orden invertido | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-eda.jpg | Tramo de tubería abierto sobre una mesa de inspección, con lentes y calibradores | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-ruptura.jpg | Tubería fracturada con el caudal escapando, junto al collarín que la repara | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-oficios.jpg | Taller vacío con siete estaciones de trabajo, cada una con su instrumental distinto | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-archivo.jpg | Estantería de archivo con cajones abiertos, microfilm y planos enrollados | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
