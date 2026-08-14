---
id: fdd-o26-pipeline-de-datos-rediseno-design
title: Pipeline de datos — rediseño para principiantes
status: aprobado
workflow: superpowers
created: 2026-08-13
supersedes: fdd-o26-unidad-para-principiantes-design
---
# Pipeline de datos — rediseño para principiantes

> Este spec **reemplaza** a `2026-08-12-unidad-para-principiantes-design.md`, que
> una revisión adversarial invalidó: afirmaba que `append` y `upsert` no estaban
> definidos —lo están, en `2_etl_elt.md:89-91`—, daba un conteo de palabras
> equivocado, y se contradecía sobre el tope de tarjetas por sección. Las cifras
> de aquí se midieron sobre los archivos.

## Estado medido

Siete páginas, **8 789 palabras**, 15 figuras (8 SVG + 7 ilustraciones), 121
filas de tabla, 9 callouts, 6 flashcards, 1 quiz, 2 prompts, **0 ejercicios**.

| Página | Palabras |
|---|---:|
| `0_index.md` | 1 248 |
| `1_el_viaje.md` | 1 050 |
| `2_etl_elt.md` | 1 349 |
| `3_eda.md` | 1 254 |
| `4_cuando_se_rompe.md` | 1 792 |
| `5_posiciones.md` | 1 306 |
| `6_presentacion.md` | 790 |

La sesión que usa esta unidad es el **13 de agosto de 2026, 19:00**
(`course/_official/calendar/1_2026-o26.yaml`). El alcance aprobado es completo
aunque el despliegue caiga después de la clase.

## Problema

Tres defectos, en orden de gravedad.

**1. Hay cuatro errores técnicos, y uno está calificado en producción.**
Detallados en el bloque H.

**2. El vocabulario no está definido.** Doce términos se usan como si el lector
ya los supiera —`partición`, `Parquet`, `staging`, transacción y atómico, `llave`,
`join`, corrida, materializar, fuga de información, sistema distribuido, y los
formatos Iceberg/Delta/Hudi— y otros dos, idempotencia y esquema, se definen en
mitad de un párrafo sin forma visual propia, así que quien relee no los
encuentra. No hay glosario.

**3. Nada compone.** Cada página estrena una empresa ficticia distinta y tira el
contexto de la anterior, así que el alumno reinicia siete veces en vez de
acumular.

Y un defecto de presentación que anula el trabajo ya hecho: **los ocho diagramas
son ilegibles en celular**. Están autorados a 880 px con texto de 11.5 px, y
`img { max-width: 100% }` los reduce, así que en un viewport de 390 px ese texto
renderiza a unos 5 px.

## Objetivo

Que alguien que llega sin contexto termine la unidad **sabiendo qué significa
cada palabra que usó**, con un solo caso que atraviese las siete páginas, y con
diagramas que se lean en el teléfono. Sin bajar el nivel: los conceptos se
quedan completos.

No entra ejercicio ejecutable. Es la segunda sesión del curso: todavía no ven
terminal, Git ni Docker.

---

## A · Vocabulario con `::: definition`

El framework ya trae la familia `definition`
(`packages/schema/src/raya_schema/numbered_objects.py:31`). Se configura en
`raya.yaml`:

```yaml
render:
  numbered_objects:
    sequences:
      definicion: { label: "Definición", style: scannable }
    families:
      definition: { sequence: definicion, label: "Definición" }
```

Da una caja numerada con CSS propio (`.raya-numbered-object--definition`,
`rendering.py:6190`) y **referenciable con `@id`** desde páginas posteriores. No
requiere cambios de framework, a diferencia de las tarjetas-blockquote del spec
anterior: los blockquotes solo tienen estilo en `@media print`.

**Forma fija, dos frases.** Qué es, y qué pasa sin eso. Nada más.

```markdown
::: definition {#def-particion title="Partición"}
Una partición es un trozo de una tabla separado por el valor de una columna,
casi siempre la fecha: los datos del 5 de agosto viven aparte de los del 6.

Sin particiones, corregir un solo día obliga a reescribir la tabla entera.
:::
```

**Regla dura: una definición solo puede usar términos ya definidos.** De ahí que
el orden sea de dependencia, no alfabético.

| Página | Definiciones | Nuevas |
|---|---|:-:|
| `0_index` — «Vocabulario mínimo» | tabla / fila / columna, llave, `join`, corrida | 4 |
| `1_el_viaje` | esquema, formato de tabla abierto (cubre Iceberg, Delta, Hudi) | 2 |
| `2_etl_elt` | partición, Parquet, `staging`, transacción y atómico | 4 |
| `3_eda` | fuga de información | 1 |
| `4_cuando_se_rompe` | idempotencia, sistema distribuido, materializar | 3 |

Son **14**. Doce nunca estuvieron definidas; idempotencia y esquema existen en
prosa y se promueven a caja, borrando la definición inline que las duplicaba.

**Tope: 4 definiciones por página**, que es lo que consumen las dos páginas más
cargadas del reparto de arriba. Si al escribir aparece una quinta, es señal de
que el término pertenece a otra página, no de que haya que subir el tope.

### `7_glosario.md`

Página nueva, `id: glosario`, última de la unidad. Tabla alfabética: término,
definición de una línea, y referencia `@id` a la caja donde se explica. Es la
página de repaso antes del control. **No duplica las definiciones**: la caja
enseña, el glosario recuerda.

## B · El caso único: `ventas.csv`

Un solo conjunto ficticio —ventas de una cafetería, cinco columnas, seis filas
visibles— sustituye las seis anécdotas. Cada página le suma una capa sobre el
mismo material.

| Página | Qué le pasa al CSV |
|---|---|
| `1_el_viaje` | Llega crudo: `"CDMX"` y `"D.F."` conviven, y las fechas vienen en dos formatos |
| `2_etl_elt` | Se normaliza, y se carga primero con `append` y luego con `upsert` |
| `3_eda` | El 12 % de los pedidos trae monto 0 → pregunta para quien conoce el dominio |
| `4_cuando_se_rompe` | Se relanza la corrida y el martes sale duplicado |
| `5_posiciones` | Quién es responsable de cada uno de esos cuatro momentos |

`0_index` presenta el CSV una vez; `6_presentacion` y `7_glosario` no lo usan.

Se muestra como tabla Markdown en la prosa. **No se ejecuta nada** y no se
publica ningún archivo de datos.

## C · Presupuesto de palabras

| | Palabras |
|---|---:|
| Hoy | 8 789 |
| + 14 definiciones (~45 c/u) | +630 |
| + glosario | +450 |
| + 8 pies de figura que salen del SVG | +170 |
| − `6_presentacion`: se va el changelog editorial | −540 |
| − recortes de prosa | −700 |
| **Meta** | **≤ 8 800** |

Los 700 de recorte salen de tres sitios identificados, no de un adelgazamiento
general:

1. **`0_index.md:110-122`** — la tabla «Por qué esta unidad es el mapa del
   semestre» duplica la de `1_introduccion/1_el_curso/0_index.md:29-36`. Se
   reduce a un wikilink y dos frases.
2. **`5_posiciones.md:83-93`** — la sección de papeles de la era de los modelos
   de lenguaje son tres fichas de ~100 palabras que dicen lo mismo tres veces.
3. **`4_cuando_se_rompe.md`** — es la página más larga (1 792) y repite en prosa
   lo que ya dicen sus tres tablas.

Si un recorte quita una idea en vez de una repetición, se conserva la idea y se
acepta pasar del presupuesto en esa página, dejándolo dicho en el PR.

## D · Diagramas legibles en celular

Se **borra `pie()`** (`tools/gen_diagramas.py:183`), usada en los 8 diagramas
para pintar una frase explicativa de hasta 20 palabras a 11.5 px dentro del SVG.
Esas 8 frases pasan a ser párrafo dentro del bloque `::: figure`:

```markdown
::: figure {#dag title="El pipeline como grafo de dependencias"}
![Nodos que se bifurcan y reconvergen](_assets/d-dag.svg)

Si una rama falla, solo se vuelve a correr esa rama: no hace falta rehacer el
pipeline entero.
:::
```

Así son texto HTML real —seleccionable, escalable, legible a cualquier ancho— en
vez de píxeles.

Dentro del SVG queda solo etiqueta de nodo, **máximo 4 palabras**. Los
encabezados (`encabezado()`) y las leyendas (`leyenda()`) se conservan.

**No hay noveno diagrama.** `tools/test_diagramas.py:27` fija la lista de ocho
slugs, y esa prueba es correcta. El contraste `append` contra `upsert` entra
dentro de `d-idempotencia`, que ya es el diagrama de ese tema.

## E · Ilustraciones: cel anime de los noventa

Un solo registro visual —Ghost in the Shell, Serial Experiments Lain, Akira—
para las siete, con **paleta distinta por página**.

| Elemento | Decisión |
|---|---|
| Sombreado | Cel duro, bordes definidos. Sin degradados suaves |
| Fondo | Pintado a mano, grano de película 35 mm |
| Luz | Una sola fuente dramática: monitor CRT, neón, ventana |
| Detalle | Denso: cables, racks, terminales |
| Figura humana | De espaldas o en silueta, **sin rostros identificables** |
| Paleta | Distinta en cada página; nunca la misma dos veces |

**Cada escena representa el concepto de su página, no una tubería genérica.** La
portada de una página cuyo argumento es «no es una flecha, es un grafo» deja de
ser un dibujo de tubos.

### Dos cambios en las guardas, ambos necesarios

- **`tools/test_ilustraciones.py:81`** exige hoy que el estilo contenga
  `"sin figuras humanas"`, lo que prohíbe las siluetas que este registro
  necesita. Pasa a exigir `"sin rostros identificables"`, que es la restricción
  real que hay que sostener.
- **`PROHIBIDOS`** (`:20-24`) hoy lista catorce nombres y **no incluye ninguno de
  los personajes de estas obras**, así que el hueco que la prueba dice cubrir
  está abierto. Se añaden los títulos y personajes protegidos de las tres
  referencias.

Ninguna imagen pide personas reales ni personajes con derechos. Se revisa cada
salida a ojo; máximo dos reintentos por escena antes de aceptar la mejor.

## F · La evaluación, junto a lo evaluado

Hoy las 6 tarjetas, el quiz y los 2 prompts cuelgan de la raíz de la unidad, así
que solo aparecen en el índice y en `/_raya/practice/`. Quien termina de leer
`cuando-se-rompe` no recibe ninguna comprobación.

Un objeto colocado **debe** apuntar a la página índice de su directorio
(`packages/schema/src/raya_schema/official.py`, `_resolve_scope`), así que cada
página pasa a ser directorio con su propio soporte:

```
2_pipeline_de_datos/
  4_cuando_se_rompe/
    0_index.md
    _official/cards/…
    _official/quizzes/…
```

**Las URLs no cambian**: `4_cuando_se_rompe.md` y `4_cuando_se_rompe/0_index.md`
resuelven ambos a `/pipeline-de-datos/cuando-se-rompe/`.

`_assets/` se queda en la raíz de la unidad. El contrato permite leer del propio
quantum o de un ancestro, **pero la ruta escrita en el Markdown sí cambia**: el
resolutor hace resolución relativa literal y sólo comprueba que la ruta ya
resuelta caiga bajo un `_assets/` válido — no busca el archivo en ancestros. Las
seis páginas promovidas pasan de `_assets/x.svg` a `../_assets/x.svg`; la
`0_index.md` de la raíz de la unidad se queda igual.

**Dos tarjetas y dos preguntas por página de contenido** —índice, viaje,
ETL/ELT, EDA, cuando se rompe, posiciones—, es decir 12 y 12. `6_presentacion`
y `7_glosario` no llevan ninguna: no enseñan concepto nuevo.

Las 6 tarjetas y las 6 preguntas que ya existen se reubican en la página que
enseña su tema y se completan las 12 restantes. Las tarjetas además se
reescriben: hoy parafrasean la prosa de su página, y una tarjeta debe forzar
recuperación, no resumir.

Esto no toca el presupuesto del bloque C: los objetos oficiales son YAML, no
prosa de página.

## G · Framework: dos arreglos y un SHA

1. **Callouts en español.** `rendering.py:8150` fija `Note`/`Tip`/`Warning`/
   `Caution` en inglés, y la unidad tiene 9 callouts en un curso que declara
   `language: "es"` en `raya.yaml`. Se localiza por ese campo →
   Nota / Consejo / Advertencia / Precaución, con el inglés como respaldo.
2. **Blockquotes en pantalla.** Solo tienen estilo bajo `@media print`
   (`rendering.py:7671`). Se les añade regla de pantalla junto al CSS de tabla
   ya agregado en `:6130`. Con franqueza: **ninguna página de este curso usa hoy
   un blockquote suelto** —los diez que aparecen son cuerpos de callout—, así
   que este arreglo no lo exige el rediseño. Viaja gratis con el anterior
   (mismo archivo, mismo merge, mismo SHA) y evita que el primer blockquote que
   alguien escriba salga sin forma.

Merge y push a `raya-lucaria.github.io`, y subir el SHA fijado en
`.github/workflows/pages.yml:34`. `ia_o26` hereda ambos arreglos.

## H · Errores técnicos

| # | Dónde | Corrección |
|:-:|---|---|
| 1 | `_official/quizzes/1_pipeline.yaml`, `dag-no-lineal`, opción 2 | Dice que una cadena estrictamente lineal no sería un DAG. **Sí lo es.** El distractor se reescribe. Está calificado y en producción |
| 2 | `4_cuando_se_rompe.md:88-93` | CDC sale de la tabla de regímenes temporales: es una **técnica de captura**, entregada por batch o por streaming, no un cuarto régimen con latencia propia |
| 3 | `4_cuando_se_rompe.md:138` | Se borra «tres columnas de cien es el 3 % de los bytes»: en columnar los bytes dependen de ancho, codificación y compresión |
| 4 | `2_etl_elt.md:24` y `_official/cards/5_tidy_data.yaml:12` | Tidy data deja de ser «el objetivo de la T». Es una forma útil para análisis tabular; en warehouse la T apunta a modelo dimensional |
| 5 | `0_index.md` frontmatter | `estimated_time: 60m` → `6m`. Hoy el lector suma 127 minutos porque el índice cuenta la unidad entera y los hijos vuelven a contarse |

El error 4 tiene una consecuencia de contenido: `d-dag.svg` ya dibuja «Dimensión
producto» y «Tabla de hechos» sin que la unidad nombre nunca el modelado
dimensional. Se añade una frase que lo nombre, sin abrir el tema.

## Lo que no cambia

- El contenido conceptual completo: ELT y su historia económica, la L de Load,
  lakehouse, contratos de datos, orquestación, linaje, costo, analytics
  engineer, el hilo del sitio del curso como pipeline.
- La estructura ya aplicada: «En corto» al abrir, «Qué te llevas» al cerrar,
  párrafos de máximo 4 líneas, listas de máximo 5.
- Los `id` de página, las URLs, los wikilinks y las rutas de `_assets/`.
- El PDF histórico y sus dos enlaces (ver y descargar).
- El calendario, las tres tareas y la evaluación.

## Verificación

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build    ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Terminado cuando:

1. `validate` y `build` pasan, y `pytest tools/` queda en verde.
2. Los cinco errores del bloque H están corregidos, y el distractor del quiz es
   falso de verdad.
3. Las 14 definiciones existen como `::: definition`, **cada una antes de su
   primer uso en prosa**, y ninguna usa un término aún no definido.
4. El glosario lista los 14 y cada entrada referencia una caja existente.
5. `ventas.csv` aparece en las cinco páginas de la tabla del bloque B, y no
   queda ninguna de las seis anécdotas viejas.
6. `grep -n "def pie" tools/gen_diagramas.py` no devuelve nada, y ningún `<text>`
   de los 8 SVG pasa de 4 palabras salvo encabezado y leyenda.
7. Las 7 ilustraciones se regeneraron en el registro nuevo, con paleta distinta
   entre sí, sin rostros identificables ni personajes con derechos.
8. Cada una de las 7 páginas es directorio con su propio `_official/`, y las
   URLs publicadas son las mismas de antes.
9. Los callouts renderizan en español y los blockquotes tienen estilo en
   pantalla, con el SHA de `pages.yml` actualizado.
10. La unidad no supera el tope declarado en `tools/test_presupuesto.py`, y ese
    tope lleva escrita la razón de su valor.

    **Cerró en 9 380, no en 8 800.** La unidad partía de 8 789 y ganó las 14
    cajas de definición, una página de glosario y el caso único; el recorte se
    llevó 797 palabras de repetición —el changelog editorial de
    `6_presentacion`, una tabla duplicada, ecos entre páginas— y se detuvo ahí.
    Lo que queda por encima de 8 800 en `2_etl_elt` y `4_cuando_se_rompe`
    —streaming y CDC, el contrato de datos, el backfill— no está en ninguna
    tabla ni en otra página: cortarlo habría sido cortar ideas, que es lo que
    la regla del bloque C prohíbe. El intercambio neto es +591 palabras a
    cambio de todo el andamiaje de vocabulario, y se acepta dicho.

## Riesgos

- **`gpt-image-2` no es determinista, y el cel anime es más difícil de acertar
  que el grabado técnico.** Mitigación: dos reintentos por escena y se acepta la
  mejor; si una escena no sale, se conserva la ilustración actual de esa página
  y se deja anotado.
- **Mover 7 páginas a directorios toca todas las rutas de la unidad.** El riesgo
  es un `0_index.md` faltante, que rompe el build con «missing index page».
  Mitigación: `git mv` página por página, con `raya validate` entre cada una.
- **Cambiar `test_ilustraciones.py` afloja una guarda mientras se aprieta otra.**
  Queda explícito: se sustituye «sin figuras humanas» por «sin rostros
  identificables» y en el mismo cambio se cierra el hueco de `PROHIBIDOS`, que
  hoy no protege nada de estas obras.
- **El presupuesto de palabras puede empujar a borrar matices.** La regla del
  bloque C aplica: si el recorte quita una idea, se conserva la idea.
