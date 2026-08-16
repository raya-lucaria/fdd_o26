# Créditos de imágenes

Procedencia y licencia de cada imagen de la unidad. Toda imagen del directorio
debe tener una fila aquí — `tools/test_creditos.py` falla si falta alguna.

Los diagramas `d-*.svg` los produce `tools/gen_diagramas.py` de forma
determinista. No se editan a mano: se regeneran. En todos, el color es
**semántico**: separa lo que el lector tiene que distinguir —las ramas de un
DAG, los cuatro almacenamientos, ETL frente a ELT, las seis dimensiones de
calidad— y nunca es decorativo.

Las ilustraciones `ilus-*.jpg` se generan con la API de imágenes de OpenAI a
partir de los prompts de `tools/ilustraciones.json`. Comparten un mismo lenguaje
visual —animación cel de ciencia ficción urbana pintada a mano: sombreado de
bordes duros, grano de película, aberración cromática leve y una sola fuente
de luz dramática por lámina, con las figuras siempre de espaldas o en silueta,
nunca de frente— pero **cada una lleva su propia paleta**, para que ninguna
página se confunda con otra: verde terminal y ámbar en la portada, azul
medianoche y turquesa en el viaje, magenta y violeta en ETL/ELT, cian de
laboratorio en el EDA, rojo de alarma sobre gris hierro en la ruptura, latón y
cobre en los oficios, sepia y ocre en el archivo.

**Ninguna ilustración representa personas reales, rostros reconocibles ni
personajes con derechos**: todas son escenas industriales abstractas y
`tools/test_ilustraciones.py` falla si algún prompt pide lo contrario.

| Archivo | Descripción | Autor / origen | Licencia |
|---|---|---|---|
| d-dag.svg | El pipeline como DAG: un color por rama que se bifurca y ámbar en el nodo donde reconvergen | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-schema.svg | Schema-on-write frente a schema-on-read, con un color propio para cada uno de los cuatro almacenamientos | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-etl-elt.svg | ETL en cian y ELT en naranja, con Transform resaltado al cambiar de lugar y la curva de costo en violeta | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-tidy.svg | Tidy data: variables en cian, observaciones en ámbar y valores en violeta, cada concepto teñido en la tabla | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-calidad.svg | Las seis dimensiones de la calidad de los datos, cada una con su color y su falla típica | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-idempotencia.svg | La misma corrida dos veces: verde la idempotente, rojo las filas que duplica la que no lo es | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-tiempo.svg | Batch, micro-batch y streaming sobre una línea de tiempo, coloreados con una rampa de latencia | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| d-ciclo.svg | Ciclo de vida de un proyecto de datos: seis etapas con un gradiente de color que avanza y cierra el lazo | Diagrama propio, generado por `tools/gen_diagramas.py` | Material del curso |
| ilus-portada.jpg | Verde terminal y ámbar sobre una ciudad nocturna: un grafo de nodos luminosos que se bifurca y reconverge, no una tubería | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-viaje.jpg | Azul medianoche y turquesa: cuatro edificios-depósito de arquitectura distinta, el mismo caudal de luz entrando de forma diferente en cada uno | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-etl-elt.jpg | Magenta y violeta sobre carbón: un cruce de neón con dos rutas espejadas que recorren las mismas tres estaciones en orden invertido | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-eda.jpg | Cian frío y blanco azulado: una figura de espaldas ante un muro de monitores CRT, midiendo antes de decidir | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-ruptura.jpg | Gris hierro con rojo de alarma: un cable troncal reventado con la luz escapando, y la sala de control detrás en alerta | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-oficios.jpg | Latón, cobre y madera cálida: siete estaciones de trabajo contiguas, cada una con su instrumental distinto, sin nadie en ellas | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
| ilus-archivo.jpg | Sepia y ocre desaturado: un archivo polvoriento de cintas y planos, luz de tarde atravesando el polvo | Generada con gpt-image-2 a partir de `tools/ilustraciones.json` | Material del curso |
