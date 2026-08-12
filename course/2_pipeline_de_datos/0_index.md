---
id: pipeline-de-datos
title: Pipeline de datos
nav_title: Pipeline de datos
summary: Qué separa un pipeline de un script que funcionó una vez, y por qué el resto del semestre existe para sostenerlo.
status: ready
estimated_time: 90m
tags: [pipeline, dag, mapa-del-curso]
---

# Pipeline de datos

::: figure {#ilus-portada title="Un pipeline es lo que vuelve a correr mañana"}
![Circuito industrial cerrado de tuberías y válvulas donde el caudal luminoso sale por un extremo y vuelve a entrar por el otro, recorriendo el mismo trazo una y otra vez](_assets/ilus-portada.jpg)
:::

Un viernes por la tarde alguien abre un notebook, lee tres archivos, los cruza,
limpia lo que estorba y produce un número. El número es correcto. Lo pega en una
presentación y se va a casa. El lunes le piden el mismo número con los datos de
la semana nueva, y ahí empieza el problema real: el archivo de esta semana trae
una columna más, la ruta al segundo archivo era el Escritorio de una laptop
concreta, y en la celda 14 hay un filtro escrito a mano que nadie —ni quien lo
escribió— recuerda por qué está.

El notebook no estaba mal. Simplemente no era un pipeline. La diferencia no es
de tamaño ni de herramientas: **un pipeline es un proceso que vuelve a correr
mañana, sin ti, y da el mismo resultado o falla de forma que se note.** Todo lo
que esta unidad presenta —etapas, formatos, contratos, orquestación— existe para
sostener esa frase.

## El eje de esta unidad

Cada concepto que sigue aparece **como respuesta a una falla concreta**, no como
definición de diccionario. No vas a encontrar aquí una lista de términos para
memorizar; vas a encontrar problemas que ocurren de verdad y el nombre que la
industria le puso a la solución. Cuando alguien te dice «hay que hacerlo
idempotente» y no sabes qué falla evita, la palabra es ruido. Cuando sabes qué
falla evita, la palabra es una herramienta.

## No es una flecha, es un grafo

::: figure {#dag title="El pipeline como grafo de dependencias"}
![Diagrama de un pipeline como DAG: nodos que se bifurcan y reconvergen](_assets/d-dag.svg)
:::

Casi todos los diagramas de pipeline que vas a ver en internet son una fila de
cajas conectadas por flechas de izquierda a derecha. Es una mentira cómoda. Un
pipeline real se bifurca —de una extracción salen tres transformaciones que no
dependen entre sí— y vuelve a converger —el reporte final necesita las tres—.
Esa forma tiene nombre: **DAG**, *directed acyclic graph*, grafo dirigido
acíclico. Dirigido porque las flechas tienen sentido: la carga depende de la
transformación, no al revés. Acíclico porque no puede haber ciclos: si A depende
de B y B depende de A, nada puede empezar.

La forma no es un detalle estético. De ella se derivan tres cosas que la fila de
cajas esconde. Primero, **qué puede correr en paralelo**: dos ramas que no
dependen entre sí pueden ejecutarse al mismo tiempo, y eso suele ser la
diferencia entre veinte minutos y tres horas. Segundo, **qué se cae cuando algo
se cae**: si el nodo de extracción falla, todo lo que está aguas abajo queda
inválido, y todo lo que está en otra rama no. Tercero, **por dónde volver a
empezar**: cuando se corrige un error, no hay que recorrer el pipeline entero,
solo el subgrafo que depende del nodo corregido.

Cada vez que en este curso digamos «pipeline», la imagen mental correcta es
@dag, no una tubería.

## El sitio de este curso es un pipeline

Este es el hilo conductor de toda la unidad, y no es una metáfora: el sitio que
estás leyendo se produce con un pipeline que puedes inspeccionar entero en
[https://github.com/raya-lucaria/fdd_o26](https://github.com/raya-lucaria/fdd_o26).

La fuente son archivos de texto: Markdown para las páginas, YAML para las tareas
y el calendario. Esa fuente pasa por tres etapas:

```bash
raya validate .   # el contrato: ¿la fuente cumple las reglas?
raya build .      # la transformación: fuente -> artifact/
raya preview .    # el consumo: ver el producto antes de publicarlo
```

`raya validate` es un **contrato de datos**: exige que cada página tenga un `id`
en kebab-case, que ese `id` sea único en todo el curso, que cada enlace interno
apunte a un `id` que existe, que cada directorio tenga su página índice. Si algo
no cumple, el build no ocurre. No produce un sitio a medias con enlaces rotos:
falla, y dice dónde.

`raya build` es la transformación: convierte la fuente en `artifact/`, el
producto. Y es **idempotente**: la misma fuente produce el mismo artifact, hoy y
en tres meses, en mi máquina y en la de GitHub. Por eso `artifact/` no se
versiona en el repositorio —sería guardar algo que se puede regenerar en
cualquier momento a partir de lo que sí está versionado—.

El despliegue lo orquesta GitHub Actions, y es un DAG con los nodos etiquetados:
un trabajo de pruebas, un trabajo de build, un trabajo de publicación que
declara `needs: checks`. Esa línea es lo que convierte una prueba en compuerta
real: sin ella los dos trabajos corren en paralelo y el sitio se publica aunque
la suite falle.

Todo lo que vamos a nombrar en las siguientes páginas —fuente, contrato,
transformación, producto, orquestación, idempotencia— ya está corriendo cada vez
que alguien hace push a ese repositorio. Cuando un concepto suene abstracto,
vuelve a abrirlo: es el pipeline más pequeño y más inspeccionable que vas a
tener a la mano este semestre.

## Las cuatro etapas, y la advertencia

::: figure {#ciclo title="El ciclo de vida de un proyecto de datos"}
![Diagrama del ciclo de vida de un proyecto de datos: ETL, EDA, entrenamiento y producción conectados en ciclo, con retornos entre etapas](_assets/d-ciclo.svg)
:::

Un proyecto de datos se suele describir en cuatro etapas.

| Etapa | Qué produce | Pregunta que responde |
|---|---|---|
| ETL / ELT | Datos disponibles y en forma utilizable | ¿Dónde están los datos y cómo los muevo? |
| EDA | Entendimiento de los datos y del negocio | ¿El proyecto es siquiera viable? |
| Entrenamiento o análisis | Un modelo, un reporte, una respuesta | ¿Qué se puede concluir o predecir? |
| Producción | Un proceso que corre solo y sostiene el resultado | ¿Cómo sobrevive esto sin mí? |

Y ahora la advertencia, que importa más que la tabla: **esto no es una secuencia
lineal.** En la práctica el EDA descubre que faltan columnas y manda de vuelta a
la extracción; el entrenamiento revela que la variable objetivo estaba mal
definida y manda de vuelta al EDA; producción descubre que el modelo se degrada
con datos nuevos y manda de vuelta al principio. Las flechas de retorno de
@ciclo no son excepciones ni signos de mal trabajo: son el modo normal de
operación.

Tratar un proceso cíclico como si fuera lineal tiene un costo concreto y
predecible: se planea el proyecto como si cada etapa se hiciera una vez, se
estima el tiempo sumando etapas, y se llega tarde. Nadie estimó las tres
vueltas que en realidad hacen falta.

Conviene además desconfiar de la nitidez de cualquier taxonomía de este tipo,
incluida esta. Son abstracciones para tener de qué agarrarse al hablar, no
categorías naturales con fronteras precisas. La pregunta útil no es «¿esto es
EDA o es transformación?», sino «¿qué falla estoy tratando de evitar aquí?».

## Por qué esta unidad es el mapa del semestre

Lo que sigue en el curso no es una lista de herramientas de moda. Cada módulo
existe porque alguna parte del pipeline lo exige:

- La **terminal** y el **shell**, porque los datos llegan en archivos que hay que
  mover, inspeccionar, renombrar y encadenar en un servidor donde no hay ratón.
- **Git** y **GitHub**, porque las transformaciones son código, y código sin
  historia es código que nadie puede auditar cuando el número sale distinto.
- **Docker**, porque un pipeline tiene que correr igual en tu máquina y en el
  servidor, y «en mi computadora sí funcionaba» no es un estado válido.
- **Python**, **testing**, **logging** y **configuración**, porque cada nodo del
  DAG es un programa que hay que poder probar, observar y parametrizar.
- **Concurrencia** y **arquitectura de sistemas**, porque las ramas paralelas del
  grafo y el volumen de los datos acaban obligando a pensar en ellas.

Si en algún momento del semestre te preguntas por qué estamos aprendiendo algo,
la respuesta casi siempre está en esta unidad.

## Recorrido

1. [[el-viaje-de-los-datos|El viaje de los datos]] — dónde viven los datos, y qué
   decide entre un lake, una base de datos, un warehouse o un lakehouse.
2. [[etl-y-elt|ETL y ELT]] — por qué el orden de las letras se invirtió, y qué
   hace cada una de las tres.
3. [[eda|EDA]] — el análisis exploratorio como control de viabilidad, y las seis
   dimensiones de la calidad de los datos.
4. [[cuando-se-rompe|Cuando se rompe]] — idempotencia, contratos, tiempo,
   orquestación, linaje y costo. La página que justifica todas las demás.
5. [[posiciones|Posiciones]] — quién es responsable de qué, y qué pasa cuando la
   empresa es chica.
6. [[presentacion-pipeline|Presentación]] — el material histórico que esta unidad
   reemplaza.
