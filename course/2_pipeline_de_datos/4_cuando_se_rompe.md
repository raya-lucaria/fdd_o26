---
id: cuando-se-rompe
title: "Cuando se rompe"
nav_title: "Cuando se rompe"
summary: "Idempotencia, contratos, latencia, orquestación, linaje y costo: lo que separa correr un notebook de sostener un pipeline."
status: ready
estimated_time: 25m
tags: [idempotencia, contratos, streaming, orquestacion, linaje, costo]
prerequisites: [etl-y-elt]
---

# Cuando se rompe

Las páginas anteriores describen un pipeline que funciona. Esta describe uno que
lleva ocho meses corriendo, que alimenta un reporte que alguien mira todos los
lunes, y del que dependen decisiones. Es la página que justifica que esta unidad
se haya reescrito, porque es lo que separa a alguien que corrió un notebook de
alguien que sostiene un sistema de datos.

Seis problemas, en el orden en que suelen aparecer.

## 1. El mismo código dio otro número

::: figure {#idempotencia title="Idempotencia: la misma corrida dos veces"}
![Diagrama que contrasta un pipeline no idempotente, donde correr dos veces duplica filas, con uno idempotente que produce el mismo estado final](_assets/d-idempotencia.svg)
:::

El pipeline falló a mitad de la carga del martes. Alguien lo volvió a lanzar. El
miércoles, las ventas del martes aparecen duplicadas.

La propiedad que faltaba se llama **idempotencia**: correr el proceso una vez o
correrlo cinco veces sobre la misma entrada deja el sistema en el mismo estado.
No es una virtud abstracta, es la condición sin la cual **no puedes reintentar
nada**, y en un sistema distribuido los reintentos no son opcionales: la red se
cae, el proveedor devuelve un error transitorio, el orquestador reinicia una
tarea que creía muerta y en realidad seguía viva.

Se consigue de tres maneras, casi siempre combinadas: escribir con `upsert` en
lugar de `append`, de modo que la segunda escritura actualice en vez de
duplicar; **particionar por período** y sobrescribir la partición completa, de
modo que reprocesar el 5 de agosto reemplace exactamente los datos del 5 de
agosto; y hacer que cada corrida esté **parametrizada por su período**, no por
«hoy». Un pipeline que internamente llama a la función que devuelve la fecha
actual no se puede reejecutar para el pasado: da otro resultado cada día que
corre.

Y reejecutar el pasado es exactamente lo que hace falta cuando aparece el
**backfill**: descubres que la lógica de conversión de moneda estaba mal desde
marzo y hay que recalcular cinco meses. Con un pipeline idempotente y
particionado, un backfill es un bucle sobre fechas. Sin él, es un proyecto de
dos semanas con intervención manual, y cada intervención manual es una nueva
oportunidad de introducir una inconsistencia distinta.

El sitio de este curso es idempotente por construcción: `raya build` sobre la
misma fuente produce el mismo `artifact/`, hoy y en tres meses. Por eso
`artifact/` está en el `.gitignore` —no tiene sentido versionar algo
reproducible— y por eso la publicación no depende de que nadie recuerde qué
pasos corrió.

## 2. Alguien cambió una columna

El lunes el pipeline funcionaba. El martes falla, o peor, no falla: el equipo
que mantiene el sistema origen renombró `user_id` a `customer_id`, y tu `join`
ahora no casa con nada, así que produce una tabla vacía y un reporte que dice
cero.

Esto se llama **evolución de esquema**, y es inevitable: los sistemas origen
cambian porque el negocio cambia. Lo que no es inevitable es enterarse tarde. Los
cambios se clasifican en dos:

- **Compatibles hacia atrás** — añadir una columna nueva, ampliar un tipo. El
  consumidor que no la conoce sigue funcionando.
- **Incompatibles** — renombrar, borrar, cambiar el tipo, cambiar el significado
  de un valor sin cambiar su nombre. Esta última es la peor, porque no hay error:
  solo números distintos.

La respuesta organizacional es el **contrato de datos**: un acuerdo explícito y
verificable entre quien produce el dato y quien lo consume, que declara qué
campos existen, de qué tipo son, qué garantías de calidad ofrecen y con qué
aviso previo pueden cambiar. Lo importante no es el documento sino que sea
**ejecutable**: un contrato que solo vive en una wiki es una intención; uno que
corre como validación en cada carga y detiene el pipeline es un contrato.

Otra vez, el sitio del curso es el ejemplo más cercano. `raya validate` es el
contrato: si una página no declara `id`, si dos páginas declaran el mismo, si un
wikilink apunta a un identificador que no existe, la validación falla y el build
no ocurre. La alternativa —publicar un sitio con enlaces rotos y descubrirlo
cuando un alumno hace clic— es exactamente la falla silenciosa que un contrato
previene.

## 3. Tres mentiras distintas sobre cuándo un dato es verdad

::: figure {#tiempo title="Batch, micro-batch, streaming y CDC: cuándo un dato es verdad"}
![Diagrama comparativo de cuatro regímenes temporales de procesamiento, con la latencia entre el evento y su disponibilidad](_assets/d-tiempo.svg)
:::

«El dato de ayer» y «el dato de ahora» no son el mismo problema con distinta
velocidad: son arquitecturas distintas. Hay cuatro regímenes, y cada uno cuenta
una mentira distinta sobre en qué momento algo es verdad.

**Batch.** Se procesa un lote completo cada cierto tiempo, típicamente una vez
al día. La mentira es que **el mundo se detiene a medianoche**: el reporte dice
«ventas del 4 de agosto» como si el 4 de agosto fuera un objeto cerrado, cuando
en realidad hubo devoluciones el día 5 que corrigen esas ventas. Es el régimen
más simple, el más barato y el que basta para la enorme mayoría de los casos.

**Micro-batch.** El mismo modelo, con lotes de minutos en vez de días. No cambia
la naturaleza del problema, solo su tamaño. Es el compromiso pragmático más
frecuente, porque da casi la sensación de tiempo real con casi la simplicidad del
batch.

**Streaming.** Cada evento se procesa conforme llega. La mentira aquí es más
sutil: **que los eventos llegan en orden**. No lo hacen. Un evento generado a las
10:00 en un teléfono sin señal puede llegar al servidor a las 14:00. Eso obliga a
distinguir entre el **tiempo del evento** —cuándo ocurrió— y el **tiempo de
procesamiento** —cuándo lo vimos—, y a decidir cuánto se espera a los rezagados
antes de cerrar una ventana. Esa decisión es un compromiso entre exactitud y
latencia que no tiene solución correcta, solo una elegida a conciencia.

**CDC** (*change data capture*). En lugar de consultar la base origen, se lee su
registro de transacciones y se replican los cambios. La mentira es que **hay un
solo estado actual**: el consumidor siempre está viendo el pasado, con un retraso
de replicación que existe aunque sea de milisegundos. CDC resuelve elegantemente
el problema de las modificaciones que la extracción incremental no detecta —una
fila vieja que alguien editó ayer no tiene fecha de creación nueva, pero sí
aparece en el log de transacciones— y a cambio acopla tu pipeline a los detalles
internos del sistema origen.

La regla práctica: **elige el régimen por el tiempo de la decisión, no por la
tecnología**. Si nadie va a actuar sobre ese número hasta la junta del lunes,
streaming es un costo operativo sin beneficio. Si el sistema decide en tiempo
real si una transacción es fraude, batch no es una opción.

## 4. Quién corre qué, y qué pasa si falla

Un pipeline con un solo paso se resuelve con una tarea programada en el sistema
operativo. Con veinte pasos que dependen entre sí, no.

Aquí vuelve el DAG de la primera página, ahora con consecuencias operativas. Un
**orquestador** —Airflow, Dagster, Prefect, o el propio motor de GitHub Actions
para casos pequeños— es el componente que conoce el grafo y responde cinco
preguntas que a mano no se sostienen: en qué orden corre cada nodo; cuáles pueden
correr en paralelo; qué se reintenta y cuántas veces cuando algo falla; qué queda
bloqueado aguas abajo de un nodo caído; y a quién se le avisa.

La pregunta que revela si un pipeline está orquestado de verdad no es «¿corre
solo?» sino **«¿qué pasa si el paso 4 de 9 falla a las 3 de la mañana?»**. Las
respuestas malas son: nadie se entera hasta el lunes; los pasos 5 a 9 corren
igual sobre datos incompletos; alguien tiene que recordar qué pasos ya
terminaron para lanzar el resto a mano. Las respuestas buenas dependen todas de
la idempotencia del punto 1.

El despliegue de este sitio es un DAG orquestado mínimo pero real: un trabajo de
verificación, un trabajo de construcción que declara `needs` sobre el anterior, y
una publicación que solo ocurre si los dos anteriores pasaron. Es el mismo
principio que Airflow, con tres nodos en vez de doscientos.

## 5. De dónde salió este número

Alguien en una junta señala una cifra en un tablero y pregunta de dónde sale. La
respuesta honesta en muchas organizaciones es que nadie lo sabe con certeza sin
dedicarle medio día a rastrear consultas.

**Linaje** es la respuesta a esa pregunta: el mapa de qué tabla se construyó a
partir de qué tablas, con qué transformación y en qué corrida. Sirve en dos
direcciones. Hacia atrás, para auditar un número. Hacia adelante, para el
**análisis de impacto**: si voy a cambiar esta columna, ¿qué se rompe? Sin
linaje, esa pregunta se responde con una búsqueda de texto y con esperanza.

**Observabilidad** es lo que hace que un problema se note antes de que lo note el
consumidor. Un pipeline observable registra, en cada corrida, cuánto tardó,
cuántas filas procesó, cuántas se rechazaron, y **cómo se comparan esos números
con los de las corridas anteriores**. Esa última parte es la que detecta las
fallas silenciosas: un pipeline que normalmente carga cien mil filas y hoy cargó
ochocientas no lanzó ningún error, y aun así algo se rompió.

Conviene distinguir dos formas de fallar. La **ruidosa** —una excepción, un
proceso que se muere— es incómoda y benigna: se nota. La **silenciosa** —el
`join` que devuelve vacío, la columna que ahora llega en nulos, el filtro que
descarta de más— es la peligrosa, porque alimenta decisiones durante semanas.
Casi toda la ingeniería de observabilidad existe para convertir fallas
silenciosas en ruidosas.

## 6. Por qué la consulta bonita costó 400 dólares

En un warehouse elástico, el cómputo se paga por uso, y el uso lo genera
cualquiera con acceso a una consola. Alguien escribe un `SELECT *` sobre una
tabla de varios terabytes para «echarle un ojo», y esa curiosidad aparece en la
factura del mes. Alguien programa un tablero que refresca cada cinco minutos una
consulta que recorre el histórico completo, y esa consulta corre 288 veces al
día para responderle a nadie de madrugada.

El costo es una propiedad del diseño, no un detalle administrativo, y hay cuatro
palancas concretas:

- **Particionar** por fecha y **filtrar por partición**, para que la consulta
  toque solo el trozo relevante en lugar de la tabla entera.
- **Seleccionar columnas** en vez de `SELECT *`; en formatos columnares como
  Parquet, leer tres columnas de cien es leer el 3 % de los bytes.
- **Materializar** los resultados intermedios que se consultan muchas veces, en
  lugar de recalcularlos en cada consulta.
- **Ajustar la frecuencia a la decisión**: un tablero que se mira una vez al día
  no necesita refrescarse cada cinco minutos.

Hay una consecuencia cultural que vale la pena nombrar. Cuando el cómputo era
fijo, una consulta ineficiente era lenta y el castigo era esperar. Ahora es
rápida y el castigo llega treinta días después en una factura que nadie asocia
con quién la escribió. Por eso el costo dejó de ser problema del área de
finanzas y pasó a ser criterio de ingeniería.

## Hacia adelante

Reproducibilidad, aislamiento y «corre igual aquí que allá» son la razón por la
que **Docker** aparece en este curso. Un pipeline idempotente cuyo entorno de
ejecución cambia entre tu laptop y el servidor no es idempotente: es un pipeline
con una variable oculta más.

La siguiente página, [[posiciones|Posiciones]], reparte todo lo que llevamos
—extracción, transformación, contratos, orquestación, modelos, costo— entre las
personas que en una organización se hacen responsables de cada trozo.
