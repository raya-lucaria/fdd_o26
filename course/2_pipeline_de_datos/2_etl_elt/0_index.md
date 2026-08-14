---
id: etl-y-elt
title: ETL y ELT
nav_title: ETL y ELT
summary: "Por qué el orden de las tres letras se invirtió cuando cambió el precio del almacenamiento, y qué hace cada una."
status: ready
estimated_time: 13m
tags: [etl, elt, tidy-data, transformacion]
prerequisites: [el-viaje-de-los-datos]
---

# ETL y ELT

::: figure {#ilus-etl-elt title="Las mismas estaciones, recorridas en orden invertido"}
![Dos rutas de tubería paralelas que atraviesan las mismas tres estaciones en orden opuesto, una imagen especular de la otra](../_assets/ilus-etl-elt.jpg)
:::

## En corto

- **E**xtract, **T**ransform, **L**oad: sacar los datos, darles forma, escribirlos donde se consumen.
- Lo interesante no son las letras: es que **su orden cambió, por razones económicas**.
- ELT guarda el crudo, así que permite **rehacer el pasado**. ETL no.
- La **L** es la letra que nadie explica, y es donde ocurren los errores que duplican dinero.
- Para análisis tabular, la forma que se busca tiene nombre: **tidy data**.

## La historia económica del orden

::: figure {#etl-elt title="ETL contra ELT: el mismo trabajo en distinto orden"}
![Comparación lado a lado de un flujo ETL y uno ELT, con la curva descendente del costo de almacenamiento como eje de la transición](../_assets/d-etl-elt.svg)
:::

### Por qué ETL era lo único razonable

Durante décadas el almacenamiento fue **caro** y el cómputo del warehouse fue **fijo**: se compraba un servidor con una capacidad, y esa era la capacidad, en el pico y en el valle.

Así que se extraía, se transformaba en una máquina intermedia de *staging* —más barata— y se cargaba **solo lo que se iba a usar, limpio y agregado**. Nadie pagaba por guardar crudo en el sistema caro ni gastaba cómputo escaso en limpiar texto.

### Qué cambió

Dos cosas, ninguna técnica: el **costo por gigabyte** cayó hasta volverse despreciable, y el warehouse pasó de máquina a servicio **elástico** que se paga por consulta y escala a cero.

Con las condiciones invertidas, el cálculo se invirtió. Transformar dentro del warehouse pasó a ser lo más barato y rápido: ese motor está optimizado para recorrer millones de filas. Así nació **ELT**: extraer, cargar el crudo tal cual, y transformar después con SQL, dentro del destino.

| | ETL | ELT |
|---|---|---|
| Dónde transforma | En un sistema intermedio | Dentro del destino |
| Qué guarda | Solo lo transformado | El crudo y lo transformado |
| Cuándo decide la forma | Antes de cargar | Después, y se puede cambiar |
| Rehacer una transformación | Exige volver a extraer del origen | Se rehace sobre el crudo ya cargado |
| Supone que | Guardar es caro, el cómputo es fijo | Guardar es barato, el cómputo es elástico |

La fila que más cuesta entender es la penúltima. En **ETL**, un error de lógica descubierto seis meses después es irreparable: el crudo que lo habría corregido nunca se guardó. En **ELT** sigue ahí. Esa capacidad de **rehacer el pasado** reaparece en [[cuando-se-rompe|Cuando se rompe]] como *backfill*.

> [!NOTE]
> ETL no está muerto. Sigue siendo lo correcto cuando el dato no puede cruzar un límite sin transformarse —anonimizar datos personales, requisitos de residencia— o cuando el volumen no compensa cargarlo entero. La pregunta no es cuál es mejor, sino **qué es caro en tu caso**.

## Extract

Extraer es obtener los datos de donde vivan: bases relacionales, CSV, JSON, APIs, colas de eventos, scrapers, hojas de cálculo hechas a mano. Es lo más aburrido de explicar y **lo que más falla en producción**, porque depende de sistemas que no controlas.

**Credenciales.** Cada origen exige contraseña, llave de API, token o certificado, y **nada de eso se escribe en el código**: vive en variables de entorno o en un gestor de secretos. Un token en un repositorio es un incidente esperando su turno.

**Completa contra incremental.** Traer toda la tabla es simple y no escala. Traer solo lo nuevo escala y obliga a definir «nuevo»: ¿las filas creadas después del último corte? ¿Y las viejas que alguien modificó ayer? Esa pregunta lleva a CDC, en [[cuando-se-rompe|Cuando se rompe]].

**Metadatos.** Cada extracción registra de dónde vino, cuándo, cómo y cuántas filas trajo. Suena burocrático hasta el día en que un número sale raro y la única pista es que esa corrida trajo la mitad.

## Transform

Transformar es aplicar reglas para limpiar, combinar, filtrar y cambiar la estructura. Se le suele llamar «estandarizar», palabra demasiado vaga: lo que se busca es que dos filas que representan lo mismo se vean igual, que **una columna signifique una sola cosa**, y que el resultado se una con otras tablas sin adivinar.

El trabajo real casi siempre es:

- unificar formatos de fecha y de número;
- resolver que «CDMX», «Ciudad de México» y «D.F.» son lo mismo;
- deduplicar registros que llegaron dos veces;
- unir por llave y descubrir que el diez por ciento no casa;
- decidir qué hacer con los nulos.

Esa última es donde muerde la distinción anterior. Rellenar nulos con la media es **procesamiento, no pre-procesamiento**: cambia la distribución y altera cualquier prueba posterior. Se puede hacer, pero **explícito, documentado y aguas abajo del crudo**.

## Load: la letra que nadie explica

Casi todo el material salta de la transformación a *tidy data* sin decir qué es cargar. Es una omisión rara: la carga es donde ocurren los errores que **duplican dinero**.

### Cómo se escribe

| Estrategia | Qué hace | Su riesgo |
|---|---|---|
| **Append** | Añade las filas nuevas al final | Si la corrida se repite, los datos se duplican |
| **Overwrite** | Borra todo y escribe de nuevo | Destruye el histórico; si falla a la mitad, queda incompleta |
| **Upsert** o *merge* | Actualiza si la llave existe, inserta si no | Es lo que casi siempre se quiere, y exige una llave única de verdad |
| **Overwrite por partición** | Reescribe solo el período procesado | Base práctica de la idempotencia |

### Visibilidad y verificación

Si el consumidor lee la tabla mientras se escribe, verá **estados intermedios**: medio día cargado. Por eso los destinos serios ofrecen transacciones, o se escribe a una tabla temporal y se intercambia de forma atómica al final.

La carga es también donde ocurre la **verificación de llegada**: contar filas escritas, compararlas con las esperadas, confirmar que no hay llaves duplicadas. Un pipeline que no verifica lo que cargó es un pipeline que confía.

## Tidy data: qué forma debe tener el resultado

::: figure {#tidy title="Tidy data: variables en columnas, observaciones en filas, un valor por celda"}
![Diagrama de una tabla desordenada transformada en una tabla tidy, con variables como columnas y observaciones como filas](../_assets/d-tidy.svg)
:::

Que unos datos sean **tabulares** no los hace utilizables: una hoja con años como columnas, totales intercalados y celdas combinadas es tabular y es inservible.

**Tidy data** es una forma concreta de tabla, con tres reglas:

1. Cada **variable** es una columna.
2. Cada **observación** es una fila.
3. Cada **valor** ocupa una celda, y cada tabla contiene un solo tipo de unidad observacional.

El caso típico de datos no tidy es la tabla con una columna por año: `2024`, `2025`, `2026`. El año no es tres variables, es una variable con tres valores. En forma tidy hay dos columnas —`anio` y `valor`— y tres filas.

La razón no es estética: **todas las herramientas del ecosistema esperan esa forma**, del `GROUP BY` de SQL al `groupby` de polars, de seaborn a la matriz de entrada de casi cualquier algoritmo. Con datos tidy, agregar por año es una línea; sin ellos, un script que se reescribe cada vez que aparece un año nuevo.

Tidy no es la única forma de destino. Cuando lo que se alimenta es un warehouse,
la transformación suele apuntar a un **modelo dimensional**: una tabla de hechos
con las métricas y varias tablas de dimensión con sus atributos. @dag ya dibuja
hechos y dimensiones, y el tema se ve a fondo más adelante en el curso.

## Hacia adelante

Toda la lógica de esta página es **código**: reglas que alguien va a leer, discutir y corregir. Por eso Git es parte del pipeline y no un módulo administrativo: sin historia versionada, «¿qué cambió entre el lunes y el martes?» no tiene respuesta.

La siguiente página, [[eda|EDA]], trata el análisis exploratorio como el control de viabilidad que decide si el proyecto se puede hacer.

## Qué te llevas

- El orden ETL/ELT no es preferencia técnica: **responde a qué es caro en tu caso**, guardar o rehacer.
- Guardar el crudo compra la opción de **rehacer el pasado**: la ventaja estructural de ELT.
- **La carga tiene estrategia.** Append duplica; overwrite por partición hace segura una reejecución.
