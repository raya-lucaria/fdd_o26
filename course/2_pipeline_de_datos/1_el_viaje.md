---
id: el-viaje-de-los-datos
title: "El viaje de los datos"
nav_title: "El viaje"
summary: "Dónde viven los datos y por qué hay cuatro respuestas distintas: el eje real es esquema al escribir contra esquema al leer."
status: ready
estimated_time: 20m
tags: [almacenamiento, datalake, warehouse, lakehouse, esquema]
prerequisites: [pipeline-de-datos]
---

# El viaje de los datos

Un dato nace en algún lado —un formulario que alguien llenó, un sensor, una API
de un proveedor, un log de un servidor— y termina en otro lado —una gráfica, una
decisión, un modelo—. Entre esos dos puntos hay un viaje, y en cada escala hay
que decidir dónde se queda a dormir. Esta página trata de esas escalas.

La pregunta que ordena todo el capítulo es más pequeña de lo que parece:
**¿cuándo se le exige forma a un dato, al escribirlo o al leerlo?** De esa
pregunta —y de una segunda sobre costo— se derivan las cuatro respuestas que la
industria ha ido inventando.

## La falla que abre el tema

Llega un archivo nuevo de un proveedor. Trae una columna extra y una fecha en
formato distinto. Hay dos comportamientos posibles y ambos existen en la
práctica.

En el primero, el sistema lo rechaza: «la columna `region_code` no está
declarada, la carga falla». Nada entra roto, pero el dato de hoy no está
disponible hasta que alguien arregle el esquema, y ese alguien quizá esté de
vacaciones.

En el segundo, el sistema lo acepta tal cual, lo guarda como llegó, y el
problema aparece tres semanas después, cuando alguien hace una consulta que
promedia una columna donde ahora conviven `"2026-01-05"` y `"05/01/2026"`.

Ninguno de los dos es el correcto en abstracto. Son dos ubicaciones distintas
del mismo costo: **schema-on-write** paga por adelantado y falla temprano;
**schema-on-read** difiere el pago y falla tarde, cuando ya hay tres años de
datos heterogéneos acumulados. Casi todas las decisiones de arquitectura de
datos son alguna versión de esta.

## Las cuatro escalas

::: figure {#schema title="Schema-on-write contra schema-on-read: base de datos, lake, warehouse y lakehouse"}
![Diagrama comparativo de cuatro sistemas de almacenamiento situados según cuándo imponen esquema y para qué carga de trabajo están optimizados](_assets/d-schema.svg)
:::

### Base de datos operacional

Es el sistema que sostiene una aplicación mientras corre: el carrito de compras,
el registro de usuarios, el inventario. Guarda **el estado actual** del negocio y
está optimizada para escrituras y lecturas pequeñas y muy frecuentes —insertar
un pedido, leer un usuario por su identificador—. Impone esquema al escribir:
las columnas están declaradas, los tipos se verifican, las llaves foráneas
existen. En el mundo relacional son PostgreSQL, MySQL, SQL Server.

Su limitación aparece en cuanto alguien pide un análisis: una consulta que
recorre tres años de pedidos para calcular una tendencia compite por recursos
con la aplicación que está atendiendo clientes en ese momento. La base de datos
operacional no está mal diseñada; está diseñada para otra cosa.

### Data lake

Es un repositorio que guarda **datos en bruto, en su formato original**, sin
imponer estructura al momento de escribir. CSV, JSON, Parquet, imágenes, logs
sin parsear: todo entra. Técnicamente suele ser almacenamiento de objetos
—Amazon S3, Google Cloud Storage— con archivos organizados en carpetas.

Su virtud es que no obliga a decidir de antemano qué se va a hacer con el dato.
Cuando la pregunta de negocio todavía no existe, imponer un esquema es apostar a
ciegas por una interpretación futura, y guardar el crudo conserva la opción de
interpretarlo distinto después. Su riesgo tiene nombre propio en la industria:
el **data swamp**, el pantano de datos. Un lake sin catálogo, sin metadatos y sin
gobierno es un disco duro gigante donde nadie sabe qué hay, quién lo puso ni si
sigue siendo válido.

### Data warehouse

Es una base de datos especializada en análisis. Guarda datos **estructurados,
limpios y ya modelados**, casi siempre con historia —no solo el estado actual,
sino cómo se llegó a él— y está optimizada para consultas que recorren muchas
filas y pocas columnas: sumas, promedios, agrupaciones sobre millones de
registros. Snowflake, BigQuery, Redshift.

Impone esquema al escribir, como la base de datos operacional, pero por una
razón distinta: no para garantizar la consistencia de una transacción, sino para
que las consultas analíticas sean rápidas y para que todo el mundo en la empresa
esté midiendo lo mismo cuando dice «ingreso mensual».

### Lakehouse

Aquí es donde el material que esta unidad reemplaza se quedó corto. Presentar
lake y warehouse como una elección binaria describe la arquitectura de hace una
década, no la de hoy.

El problema práctico de tener los dos era la duplicación: los mismos datos
vivían en el lake en crudo y en el warehouse ya modelados, con un proceso de
copia en medio que había que mantener, que se atrasaba y que era una fuente
constante de discrepancias entre dos números que deberían ser el mismo.

El **lakehouse** colapsa la distinción: se conserva el almacenamiento barato y
abierto del lake, y encima se le añaden las garantías que hacían útil al
warehouse —transacciones, evolución controlada de esquema, viajes en el tiempo
sobre versiones anteriores de una tabla—. Los formatos de tabla que lo hacen
posible son Delta Lake, Apache Iceberg y Apache Hudi. La idea central es simple:
el esquema deja de ser una propiedad del sistema de almacenamiento y pasa a ser
**metadatos versionados encima de archivos**.

| | Base de datos | Data lake | Data warehouse | Lakehouse |
|---|---|---|---|---|
| Esquema | Al escribir | Al leer | Al escribir | Al escribir, versionado |
| Qué guarda | Estado actual | Crudo, cualquier formato | Estructurado e histórico | Crudo y curado en el mismo lugar |
| Optimizado para | Muchas operaciones pequeñas | Guardar barato | Consultas analíticas | Ambas cosas |
| Falla típica | Se satura con consultas analíticas | Se vuelve un pantano | Duplica el dato y se atrasa | Complejidad operativa mayor |

## Pre-procesamiento contra procesamiento

Hay una distinción que se usa poco y que ahorra discusiones enteras. Llamamos
**pre-procesamiento** a toda transformación que no altera las decisiones ni los
supuestos estadísticos: convertir una fecha a formato ISO, normalizar
mayúsculas, unir dos tablas por su llave, renombrar una columna. Llamamos
**procesamiento** a toda transformación que sí los altera: imputar los valores
faltantes con la media, eliminar los valores atípicos, agregar por semana,
recortar la cola de una distribución.

La regla práctica que se deriva de ahí: **si el proceso está diseñado para
guardar datos crudos, no metas decisiones estadísticas en él.** El momento en
que alguien decide, dentro de la extracción, que los pedidos mayores a cien mil
pesos «son errores» y los filtra, es el momento en que el dato deja de ser crudo
y nadie aguas abajo se entera. Tres meses después, cuando el equipo de fraude
pregunte por los pedidos grandes, no van a existir.

Cuando una transformación toma una decisión estadística, hay que dejarla
escrita: en el código, en la documentación y en los metadatos del proceso. La
página [[cuando-se-rompe|Cuando se rompe]] retoma esto bajo el nombre de linaje.

## Algoritmo contra modelo

Dos palabras que se usan como sinónimos y no lo son. Un **algoritmo** es el
proceso abstracto que se va a aplicar a los datos: una regresión logística, un
árbol de decisión, un mecanismo de atención. Existe antes de ver un solo dato y
es el mismo para todos los proyectos que lo usan.

Un **modelo** es ese algoritmo **ya entrenado** con datos concretos: los
parámetros ajustados, congelados, listos para producir predicciones. El
algoritmo es la receta; el modelo es el pan que salió de esta harina.

La distinción importa por una consecuencia práctica: el algoritmo se elige, pero
el modelo **se versiona**. Dos modelos del mismo algoritmo entrenados con datos
de meses distintos son objetos distintos, y confundirlos —o no saber cuál está
respondiendo en producción— es una de las formas más comunes de que un sistema
dé un número que nadie puede explicar.

## Hacia adelante

Este capítulo dejó implícito un problema que el resto del curso ataca de frente:
los datos llegan como **archivos**, en máquinas que no son la tuya. Moverlos,
inspeccionarlos sin abrirlos enteros, encadenar transformaciones sobre ellos y
programar que eso ocurra sin nadie mirando es exactamente para lo que existen la
terminal y el shell, y por eso son el módulo que viene poco después.

La siguiente página, [[etl-y-elt|ETL y ELT]], toma estas escalas y cuenta cómo se
mueven los datos entre ellas —y por qué el orden en que se hace cambió cuando
cambió el precio de guardar un terabyte.
