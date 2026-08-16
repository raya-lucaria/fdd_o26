---
id: cuando-se-rompe
title: "Cuando se rompe"
nav_title: "Cuando se rompe"
summary: "Idempotencia, contratos, latencia, orquestación, linaje y costo: lo que separa correr un notebook de sostener un pipeline."
status: ready
estimated_time: 16m
tags: [idempotencia, contratos, streaming, orquestacion, linaje, costo]
prerequisites: [etl-y-elt]
---

# Cuando se rompe

::: figure {#ilus-ruptura title="Toda fractura tiene su collarín de reparación"}
![Un cable troncal metálico reventado con chispas y luz roja escapando, y detrás, tras un cristal, una sala de control en penumbra con luces de alarma y una silueta de espaldas](../_assets/ilus-ruptura.jpg)
:::

## En corto

- Esta página trata **un pipeline que ya lleva ocho meses corriendo**.
- Seis fallas, en orden, con su remedio.
- **La idempotencia sostiene todo lo demás**: sin ella no puedes reintentar nada.
- Las fallas **silenciosas** son las peligrosas: no lanzan ningún error.
- En un warehouse elástico, **el costo es una decisión de diseño**.

## El mapa de las seis fallas

| Síntoma | Causa | Qué lo evita |
|---|---|---|
| El 4 de agosto sale duplicado | Se relanzó una corrida que escribe con `append` | **Idempotencia** |
| El reporte dice cero y nadie ve un error | El origen renombró una columna | **Contrato de datos** ejecutable |
| «El dato de ahora» significa cosas distintas | Régimen temporal mal elegido | **Batch, micro-batch o streaming** según la decisión |
| El paso 4 falló y los pasos 5 a 9 corrieron | Nadie conoce el grafo | Un **orquestador** |
| Nadie sabe de dónde sale la cifra | No hay registro de qué produjo qué | **Linaje** y **observabilidad** |
| La factura del mes se disparó | Consultas que recorren todo, a destiempo | **Particionar y materializar** |

## 1. El mismo código dio otro número

::: definition {#def-idempotencia title="Idempotencia"}
Un paso es idempotente si correrlo una o cinco veces deja el sistema igual.

Sin idempotencia no se puede reintentar con seguridad.
:::

::: figure {#idempotencia title="Idempotencia: la misma corrida dos veces"}
![Diagrama que contrasta un pipeline no idempotente, donde correr dos veces duplica filas, con uno idempotente que produce el mismo estado final](../_assets/d-idempotencia.svg)

El reintento no es un caso raro: es la operación normal de cualquier
orquestador. Sin idempotencia, cada reintento inventa datos que nadie produjo.
:::

La corrida del 4 de agosto sobre `ventas.csv` falla a la mitad; al relanzarla, sus tres pedidos aparecen dos veces: seis filas en vez de tres. Faltaba la **idempotencia**.

::: definition {#def-sistema-distribuido title="Sistema distribuido"}
Es un sistema cuyas piezas corren en máquinas distintas y se hablan por la red:
tu proceso, la base origen, el almacenamiento y el orquestador.

La consecuencia práctica: la red **se cae**, y eso es normal, no una excepción.
:::

### Cómo se consigue

- **Escribir con `upsert`**, no `append`, para que la segunda escritura actualice.
- **Particionar por período** y sobrescribir la partición entera: reprocesar el 5 de agosto reemplaza ese día.
- **Parametrizar cada corrida por su período**, no por «hoy». Un pipeline que pregunta la fecha actual no se puede reejecutar para el pasado.

### Para qué sirve: el backfill

La conversión de moneda estaba mal desde marzo: hay que recalcular cinco meses. Con un pipeline idempotente y particionado, ese **backfill** es un bucle sobre fechas; sin él, dos semanas a mano, con una inconsistencia nueva cada vez.

> [!NOTE]
> El sitio de este curso es idempotente por construcción, como ya viste: `raya build` repetido sobre la misma fuente no cambia el resultado.

## 2. Alguien cambió una columna

El lunes el pipeline funcionaba, el martes no: el origen renombró `user_id` a `customer_id`, y tu `join` ya no casa.

Esto es **evolución de esquema**: inevitable porque el negocio cambia. Lo que no es inevitable es enterarse tarde.

| Tipo de cambio | Ejemplos | Efecto |
|---|---|---|
| **Compatible hacia atrás** | Añadir columna, ampliar un tipo | Quien no la conoce sigue funcionando |
| **Incompatible** | Renombrar, borrar, cambiar el tipo | Se rompe con error visible |
| **Incompatible silencioso** | Cambiar el significado de un valor | No hay error: solo números distintos. Es la peor |

### El contrato de datos

Es un acuerdo verificable entre quien produce el dato y quien lo consume: qué campos existen, de qué tipo, qué calidad garantizan y con cuánto aviso pueden cambiar.

Lo importante no es el documento sino que sea **ejecutable**. Un contrato en una wiki es una intención; uno que corre en cada carga y detiene el pipeline es un contrato.

`raya validate` es el de este sitio: un `id` inexistente detiene el build, en vez de publicar un enlace roto.

## 3. Tres mentiras distintas sobre cuándo un dato es verdad

::: figure {#tiempo title="Batch, micro-batch y streaming: cuándo un dato es verdad"}
![Diagrama comparativo de tres regímenes temporales de procesamiento, con la latencia entre el evento y su disponibilidad](../_assets/d-tiempo.svg)

Elegir el modo es elegir cuánta frescura se paga: más frescura, más
maquinaria que sostener.
:::

«El dato de ayer» y «el dato de ahora» no son el mismo problema: **son arquitecturas distintas**, y cada régimen miente distinto sobre cuándo algo es verdad.

| Régimen | Latencia | Su mentira | Cuándo conviene |
|---|---|---|---|
| **Batch** | Horas o un día | Que el mundo se detiene a medianoche: hay devoluciones el día 5 que corrigen el 4 | Lo más simple y barato; basta casi siempre |
| **Micro-batch** | Minutos | La misma, más pequeña | Casi tiempo real con casi la simplicidad del batch |
| **Streaming** | Segundos | Que los eventos llegan en orden. No lo hacen | Cuando la decisión ocurre en el momento |

### Streaming y CDC, con más detalle

En **streaming** hay que distinguir el **tiempo del evento** —cuándo ocurrió— del **tiempo de procesamiento** —cuándo lo vimos—: un evento sin señal a las 10:00 puede llegar hasta las 14:00, y hay que decidir cuánto esperar a los rezagados antes de cerrar una ventana, un compromiso sin solución correcta.

**CDC no es un cuarto régimen: es una forma de *capturar* los cambios**, que
luego se entrega por batch o por streaming. En vez de consultar la base
origen, lee su registro de transacciones, y así detecta hasta la fila vieja
que alguien editó ayer sin fecha de creación nueva. A cambio, **acopla tu
pipeline a los detalles internos del origen**.

> [!TIP]
> Elige el régimen por **el tiempo de la decisión**, no por la tecnología: streaming sin nadie que actúe a tiempo es costo sin beneficio; fraude en tiempo real no admite batch.

## 4. Quién corre qué, y qué pasa si falla

Un pipeline de un paso se resuelve con una tarea programada. Con veinte pasos que dependen entre sí, no.

Aquí vuelve el DAG con consecuencias operativas. Un **orquestador** —Airflow, Dagster, Prefect— conoce el grafo y responde lo que a mano no se sostiene: qué orden, qué va en paralelo, qué se reintenta, qué queda bloqueado aguas abajo y a quién se le avisa.

La pregunta que revela si está orquestado no es «¿corre solo?», sino **«¿qué pasa si el paso 4 de 9 falla a las 3 de la mañana?»**.

Respuestas malas: nadie se entera hasta el lunes. Las buenas dependen de la idempotencia del punto 1.

## 5. De dónde salió este número

**Linaje** es el mapa de qué tabla salió de qué tablas, con qué transformación y en qué corrida: sin él, saber de dónde sale una cifra cuesta medio día, no un clic. Sirve hacia atrás, para **auditar** un número, y hacia adelante, para el **análisis de impacto**: si cambio esta columna, ¿qué se rompe? Sin linaje, se adivina.

### Observabilidad y las dos formas de fallar

Un pipeline **observable** registra en cada corrida cuánto tardó, cuántas filas procesó y cuántas rechazó, y **compara esos números con las corridas anteriores**.

| Forma de fallar | Ejemplos | Por qué |
|---|---|---|
| **Ruidosa** | Una excepción, un proceso que muere | Incómoda y benigna: se nota |
| **Silenciosa** | El `join` vacío, la columna que llega en nulos, el filtro que descarta de más | Peligrosa: alimenta decisiones durante semanas |

Casi toda la observabilidad existe para **convertir fallas silenciosas en ruidosas**.

## 6. Por qué la consulta bonita costó 400 dólares

En un warehouse elástico el cómputo se paga por uso, y el uso lo genera cualquiera con una consola. Un `SELECT *` sobre varios terabytes «para echarle un ojo» aparece en la factura.

### Cuatro palancas

::: definition {#def-materializar title="Materializar"}
Materializar es guardar el resultado de una consulta como una tabla, en vez de
recalcularlo cada vez que alguien pregunta.

Sin materializar, un tablero que se consulta cien veces al día recorre cien
veces el mismo histórico y lo cobra cien veces.
:::

- **Particionar** por fecha y **filtrar por partición**, para tocar solo el trozo relevante.
- **Seleccionar columnas** en vez de `SELECT *`: un formato columnar solo lee
  las columnas que pediste.
- **Materializar** los resultados intermedios que se consultan muchas veces.
- **Ajustar la frecuencia a la decisión**: un tablero diario no se refresca cada cinco minutos.

Con cómputo fijo, una consulta ineficiente era lenta y el castigo era esperar; ahora es rápida, y el castigo llega treinta días después en una factura que nadie asocia con quién la escribió. Por eso **el costo pasó de problema de finanzas a criterio de ingeniería**.

## Hacia adelante

Reproducibilidad y «corre igual aquí que allá» son la razón por la que **Docker** aparece en este curso. Un pipeline idempotente cuyo entorno cambia entre tu laptop y el servidor no es idempotente: tiene una variable oculta más.

La siguiente página, [[posiciones|Posiciones]], reparte todo lo anterior entre las personas responsables de cada trozo.

## Qué te llevas

- **La idempotencia sostiene todo lo demás.**
- **El contrato que cuenta es el que se ejecuta.**
- Lo que hay que cazar es **la falla silenciosa**.

**Una acción:** corre dos veces un proceso tuyo que escriba datos. Si se duplica, ya sabes qué arreglar primero.
