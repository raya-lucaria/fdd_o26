# Créditos de imágenes

Procedencia y licencia de cada imagen de la unidad. Toda imagen del directorio
debe tener una fila aquí — `tools/test_creditos.py` falla si falta alguna.

Los diagramas `d-*.svg` los produce `tools/gen_diagramas.py` de forma
determinista. No se editan a mano: se regeneran.

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
