---
id: eda
title: EDA
nav_title: EDA
summary: El análisis exploratorio como control de viabilidad del proyecto, y las seis dimensiones que definen si un dato sirve.
status: ready
estimated_time: 20m
tags: [eda, calidad-de-datos, viabilidad]
prerequisites: [etl-y-elt]
---

# EDA

::: figure {#ilus-eda title="Inspeccionar el material antes de confiar en él"}
![Tramo de tubería transparente abierto sobre una mesa de inspección iluminada, rodeado de lentes de aumento y calibradores que examinan el caudal antes de dejarlo seguir](_assets/ilus-eda.jpg)
:::

Un equipo dedica seis semanas a construir un modelo de predicción de abandono de
clientes. En la semana siete, alguien pregunta cuántos clientes de la base
efectivamente se dieron de baja el año pasado. La respuesta es once. Con once
casos positivos no hay modelo posible, y eso se podía saber el primer día con
una consulta de dos líneas.

Ese es el argumento entero de esta página. El **análisis exploratorio de datos**
—EDA, *exploratory data analysis*— no es el paso decorativo donde se hacen
histogramas bonitos antes del trabajo serio. Es **el control de viabilidad del
proyecto**: la etapa cuya función es decir «esto no se puede hacer con estos
datos» mientras cancelar todavía es barato.

## Qué se está preguntando de verdad

El EDA consiste en examinar los datos de forma sistemática y visual, con
estadística descriptiva y con gráficas, para descubrir patrones, valores
atípicos, relaciones entre variables y problemas de calidad. Esa es la
definición estándar y no dice lo importante. Lo importante es que el EDA
responde a cuatro preguntas, en este orden:

**¿El proyecto es viable?** ¿Existe la variable que hay que predecir? ¿Hay
suficientes casos de la clase que interesa? ¿La ventana de tiempo cubre lo que
se quiere estudiar? ¿La granularidad alcanza —hay datos por cliente o solo por
sucursal—? Si la respuesta a cualquiera de estas es no, el proyecto se
redefine o se cancela, y cada semana que pasa antes de descubrirlo cuesta.

**¿Qué está pasando en el negocio?** Los datos son un registro de un proceso
real, y ese proceso tiene reglas que nadie escribió. Un pico de pedidos todos
los días 15 no es una anomalía estadística: es la quincena. Un hueco de tres
semanas en 2025 no es un problema de captura: es cuando cambiaron de sistema.
Sin ese conocimiento, cualquier hallazgo se interpreta mal.

**¿Cómo se ven los datos?** Aquí entran las gráficas, y su función no es
ilustrar sino detectar: distribuciones sesgadas, colas largas, bimodalidades que
delatan dos poblaciones mezcladas, correlaciones que anuncian redundancia o
fuga de información.

**¿Qué hay que preguntarle a quien sabe?** El producto más subestimado del EDA
es una lista de preguntas para las personas expertas del dominio. «¿Por qué el
12 % de los pedidos tiene monto cero?» es una pregunta que ninguna estadística
responde y que alguien de operaciones contesta en treinta segundos.

## Calidad de datos: seis dimensiones

::: figure {#calidad title="Las seis dimensiones de la calidad de los datos"}
![Diagrama de seis dimensiones de calidad de datos: completitud, unicidad, validez, consistencia, exactitud y oportunidad](_assets/d-calidad.svg)
:::

«Los datos están sucios» no es un diagnóstico accionable. Descomponer la calidad
en dimensiones sí lo es, porque cada una se mide distinto y se arregla distinto.

**Completitud.** ¿Faltan valores? ¿En qué columnas y en qué proporción? Y la
pregunta que casi nadie hace: ¿los faltantes son aleatorios o tienen patrón? Que
falte el ingreso justo en los clientes de mayor facturación no es ruido, es una
señal sobre el proceso de captura, y tratarlo como ruido sesga todo lo que venga
después.

**Unicidad.** ¿Hay registros duplicados? La parte difícil no es contar filas
idénticas sino decidir qué cuenta como duplicado cuando la misma persona aparece
con dos correos y el nombre escrito de dos maneras.

**Validez.** ¿Los valores respetan las reglas de su dominio? Fechas de
nacimiento en el futuro, edades de 200 años, códigos postales de tres dígitos,
una columna categórica con un valor que no está en el catálogo.

**Consistencia.** ¿Los datos se contradicen entre sí o entre sistemas? Un pedido
marcado como entregado con fecha de entrega vacía. Un total que no es la suma de
sus partes. La cifra de ventas del reporte financiero que no coincide con la del
tablero de operaciones —la contradicción más política de todas—.

**Exactitud.** ¿El dato corresponde a la realidad? Es la dimensión más difícil,
porque no se puede verificar desde dentro de la tabla: exige una fuente externa
o alguien que conozca el terreno. Un dato puede ser completo, único, válido y
consistente, y estar equivocado.

**Oportunidad.** ¿El dato está disponible cuando se necesita y refleja un momento
suficientemente reciente? Un tablero perfecto que se actualiza con 48 horas de
retraso no sirve para decidir hoy. Esta dimensión es la puerta de entrada a la
discusión sobre latencia que abre [[cuando-se-rompe|Cuando se rompe]].

Estas seis dimensiones son el borrador natural de un **contrato de datos**: si
puedes escribirlas como reglas verificables, puedes ejecutarlas automáticamente
en cada corrida en vez de descubrir el problema leyendo una gráfica.

## Sobre el 60 % del tiempo

Hay una cifra que aparece en casi todas las presentaciones de ciencia de datos:
que las personas que trabajan con datos dedican alrededor del 60 % de su tiempo
a limpiar y organizar datos. La fuente original es una **encuesta de CrowdFlower
de alrededor de 2016**, hecha sobre una muestra autoseleccionada de
profesionales que respondieron un cuestionario en línea.

Vale la pena decir tres cosas al respecto. La primera es que tiene diez años, y
en diez años cambió el ecosistema entero de herramientas que precisamente ataca
ese problema. La segunda es que a estas alturas la cifra se cita casi siempre
sin fuente ni año: es **folklore reciclado de la industria**, repetido de
presentación en presentación porque suena bien y confirma lo que todo el mundo
ya cree. La tercera es que la citamos aquí no como dato duro sino porque el
orden de magnitud coincide con lo que vas a experimentar tú mismo en las tareas
de este curso.

El argumento no necesita el número. La preparación de datos domina el tiempo de
un proyecto porque es la única etapa que no se puede saltar, no se puede
automatizar del todo y depende de contexto que no está en los datos. Si en tu
primer proyecto la limpieza te toma más de lo que esperabas, no lo estás
haciendo mal: así es el trabajo.

Y ya que estamos con las citas repetidas, una que sí vale la pena, porque
describe la falla que el EDA previene. Arthur Conan Doyle, en boca de Sherlock
Holmes: «Es un error capital teorizar antes de contar con los datos.
Imperceptiblemente, uno comienza a torcer los hechos para que se ajusten a las
teorías, en lugar de ajustar las teorías a los hechos.»

## Herramientas

No hay una herramienta de EDA; hay tres capas que casi siempre se combinan.

**Manipulación tabular.** pandas es el estándar por inercia y por ecosistema;
polars es la alternativa más reciente, más rápida y con una API más
consistente. Para volúmenes que no caben en memoria, SQL directo contra el
warehouse suele ser mejor idea que traerse todo a la laptop.

**Visualización.** matplotlib como base, seaborn para estadística descriptiva
rápida, plotly cuando hace falta interactividad, ggplot en el mundo de R,
Tableau o Power BI cuando el consumidor no escribe código.

**Estadística.** No es una biblioteca, es lo que hace que las dos capas
anteriores signifiquen algo. Saber cuándo la media miente porque la
distribución tiene cola larga, cuándo una correlación alta es una fuga de
información, y por qué una prueba estadística sobre datos que ya viste cien
veces no prueba lo que crees, es lo que distingue un EDA de una galería de
gráficas.

Hay generadores de reportes automáticos —`ydata-profiling` y similares— que
producen en una línea un documento con distribuciones, faltantes y
correlaciones. Son un buen punto de partida y una mala conclusión: dan el
inventario, no el juicio. La pregunta de viabilidad sigue siendo tuya.

## Cuándo se hace EDA

La respuesta corta es: siempre, y más de una vez. Se hace antes de transformar,
para saber qué hay. Se hace después de transformar, para verificar que la
transformación hizo lo que se creía. Se vuelve a hacer cuando el modelo da un
resultado raro, y otra vez cuando en producción el comportamiento cambia. Es una
de las flechas de retorno del ciclo, no una casilla que se marca una vez.

## Hacia adelante

Todo lo que esta página describe —perfilar, verificar reglas, comparar contra lo
esperado— se puede escribir como código que corre en cada ejecución. Esa idea es
la que conecta el EDA con el módulo de testing: una prueba de datos es una
afirmación sobre la realidad que se verifica automáticamente, y es lo que
convierte un hallazgo de hoy en una garantía permanente.

La siguiente página, [[cuando-se-rompe|Cuando se rompe]], es la que justifica el
rediseño de esta unidad: qué pasa cuando el pipeline ya está en producción y el
mismo código, sobre los mismos datos, da otro número.
