---
id: fdd-o26-unidad-para-principiantes-design
title: Pipeline de Datos — versión para principiantes
status: aprobado
workflow: superpowers
created: 2026-08-12
---
# Pipeline de Datos — versión para principiantes

## Problema

La unidad está bien pensada y mal explicada para quien llega sin contexto. Tres
defectos concretos, medidos sobre las siete páginas:

**1. Seis términos sin definición alguna.** `upsert`, `append`, `schema`,
«sistema distribuido», Iceberg y Delta se usan como si el lector ya los supiera.
`upsert` y `append` son el peor caso: aparecen como *la solución* a la
idempotencia, y son justo lo que un principiante no conoce.

**2. Las otras ~26 definiciones existen pero están enterradas.** El patrón se
repite: anécdota, luego el término en negrita, y la definición como una cláusula
a media frase. Ejemplo real de `4_cuando_se_rompe.md`:

> Faltaba la **idempotencia**: correr el proceso una vez o cinco sobre la misma
> entrada deja el sistema igual.

La definición está ahí, pero llega después del ejemplo, comparte línea con el
diagnóstico y no tiene forma visual propia. Quien relee no la encuentra.

**3. No hay glosario.** No existe un lugar al que volver.

El resultado es una unidad que se entiende si ya sabes el tema y se resbala si no.

## Objetivo

Que alguien que nunca oyó «pipeline» termine la unidad sabiendo **qué significa
cada palabra que usó**. Sin bajar el nivel: los conceptos se quedan completos, lo
que cambia es que cada uno se define antes de usarse y se puede volver a
consultar.

Segundo objetivo, igual de explícito: **que se grabe**. De ahí el cambio de
estética.

## Decisión 1 — Tarjeta de término

Cada término nuevo estrena una **tarjeta**: un blockquote con forma fija de tres
partes, siempre igual, siempre antes del primer uso en prosa.

```markdown
> **Idempotencia** — correr el proceso una vez o cinco veces deja el sistema
> exactamente igual.
>
> Sin ella no puedes reintentar nada, y en un sistema distribuido los reintentos
> no son opcionales.
```

Las tres partes, en orden fijo:

| Parte | Qué contesta | Largo |
|---|---|---|
| Definición | Qué es | 1 frase |
| Consecuencia | Por qué importa / qué pasa sin ella | 1 frase |
| Ejemplo mínimo | Cómo se ve en concreto | tabla o 2 líneas, **fuera** del blockquote |

El ejemplo mínimo va en una tabla normal justo después de la tarjeta, porque una
tabla dentro de un blockquote no renderiza de forma confiable en CommonMark.
Para idempotencia:

| Corres dos veces con… | Filas al final |
|---|---|
| `append` | 200 ❌ |
| `upsert` | 100 ✅ |

**Por qué blockquote y no callout.** Los callouts `> [!NOTE]` renderizan su
etiqueta en inglés («Note»), y una página en español llena de «Note» se lee mal.
El blockquote no impone etiqueta.

### Términos que reciben tarjeta

Los seis sin definición son obligatorios. Los demás reciben tarjeta cuando
sostienen el argumento de su página; el resto vive solo en el glosario.

| Página | Tarjetas |
|---|---|
| `0_index` | pipeline, DAG, idempotencia (adelanto de una línea) |
| `1_el_viaje` | schema, schema-on-write vs schema-on-read, data lake, data warehouse, lakehouse |
| `2_etl_elt` | ETL, ELT, `append`, `upsert`, partición, tidy data |
| `3_eda` | EDA, calidad de datos |
| `4_cuando_se_rompe` | idempotencia (completa), backfill, contrato de datos, batch, streaming, CDC, latencia, orquestador, linaje |
| `5_posiciones` | analytics engineer |
| `7_glosario` | todos |

Tope: **máximo 2 tarjetas por sección `##`**. El tope es por sección, no por
página, porque `4_cuando_se_rompe` recorre seis fallas y cada una estrena su
propio vocabulario: nueve tarjetas repartidas en siete secciones están bien;
nueve seguidas serían un diccionario. Si una sección necesita más de dos, hay que
partirla.

## Decisión 2 — Página de glosario

Nueva página `7_glosario.md`, `id: glosario`, última de la unidad.

Una tabla alfabética: término, definición de una línea, y wikilink a la página
donde se explica. Es la página de repaso antes del control, y el destino de los
enlaces cuando un término reaparece en una página posterior a la que lo definió.

No duplica las tarjetas: la tarjeta enseña, el glosario recuerda.

## Decisión 3 — Estética

**Cel anime de los 90, cyberpunk pintado a mano.** Un solo lenguaje visual para
las siete ilustraciones.

| Elemento | Decisión |
|---|---|
| Sombreado | Cel duro, bordes definidos. Sin degradados suaves |
| Fondo | Pintado a mano, grano de película 35 mm |
| Luz | Una sola fuente dramática: monitor CRT, neón, ventana |
| Detalle | Denso — cables, racks, terminales, tuberías |
| Figura humana | De espaldas, en silueta o recortada por la luz. **Sin rostros** |
| Paleta | Limitada por escena; se conserva la identidad de color por página |

De las referencias que pidió el usuario —Ghost in the Shell, Serial Experiments
Lain, Akira, Frieren— las tres primeras apuntan al mismo lugar: cel noventero,
paleta fría, grano. Frieren es otro registro (acuarela cálida) y se reserva para
las dos páginas calmadas.

> **Restricción no negociable.** No se generan personajes con derechos ni
> personas reales. `tools/test_ilustraciones.py` ya lo bloquea y esa prueba corre
> en CI. La regla juega a favor del estilo: GITS y Lain construyen sus planos
> más reconocibles con figuras de espaldas y siluetas, así que la limitación es
> también la decisión estética correcta.

### Escenas

| Página | Escena | Registro | Paleta |
|---|---|---|---|
| Portada | Sala de máquinas nocturna, tuberías de datos luminosas | GITS | verde terminal + ámbar |
| El viaje | Cuatro depósitos en un paisaje urbano de noche | GITS | azul profundo + turquesa |
| ETL y ELT | Dos rutas espejadas en una intersección de neón | Akira | magenta + violeta |
| EDA | Figura de espaldas ante un muro de monitores CRT | Lain | cian frío |
| Cuando se rompe | Fuga de datos, alarma roja, cables reventados | Akira | rojo sobre acero |
| Posiciones | Taller cálido con estaciones de trabajo | Frieren | latón y cobre |
| Presentación | Archivo polvoriento, luz de tarde | Frieren | sepia |

## Decisión 4 — Diagramas con menos texto

Los ocho SVG se conservan (son deterministas y hay prueba que los verifica), pero
se aligeran: **menos prosa dentro del diagrama, más viñeta**. Un diagrama que hay
que leer como párrafo no está funcionando.

Regla: ningún texto dentro de un SVG pasa de **8 palabras**. Lo que hoy son
frases explicativas se mueve al pie de figura o al cuerpo de la página.

Además, **un diagrama nuevo**: `d-append-upsert.svg` — la misma tabla tras dos
corridas, una con `append` y otra con `upsert`. Es el diagrama que hace clic con
la idempotencia, y hoy ese contraste solo existe en prosa.

Y **uno modificado**: `d-schema.svg` pasa a mostrar schema-on-write vs
schema-on-read como eje explícito del diagrama, no como una etiqueta más.

## Decisión 5 — CSS de blockquote en el framework

Los blockquotes tienen estilo **solo para impresión**; en pantalla salen con el
sangrado por defecto del navegador, sin borde ni fondo. Una tarjeta de término
sin forma visual propia no cumple su función.

Se añade a `packages/static/src/raya_static/rendering.py`, junto al CSS de tabla
que ya se agregó ahí, scope `.raya-main-article blockquote`: borde izquierdo con
el color de acento, fondo sutil, padding. Requiere merge y push a
`raya-lucaria.github.io` y subir el SHA fijado en `pages.yml`.

`ia_o26` hereda la mejora.

## Lo que no cambia

- El contenido conceptual completo: ELT y su historia económica, la L de Load,
  lakehouse, contratos de datos, orquestación, linaje, costo, analytics engineer,
  el hilo del sitio del curso como pipeline.
- La estructura ADHD ya aplicada: «En corto» al abrir, «Qué te llevas» al cerrar,
  párrafos de máximo 4 líneas, listas de máximo 5.
- Los `id` de página, los wikilinks y las figuras numeradas existentes.
- El calendario, las tres tareas y la evaluación.

## Presupuesto de palabras

Las tarjetas y el glosario **añaden** texto. Para que la unidad no vuelva a
crecer, el presupuesto es firme:

| | Hoy | Meta |
|---|---:|---:|
| Prosa de las 7 páginas | 8 125 | ≤ 7 500 |
| Tarjetas de término | 0 | ~700 |
| Glosario (página nueva) | 0 | ~500 |
| **Total unidad** | **8 125** | **≤ 8 700** |

Es decir: por cada palabra de definición que entra, sale al menos una de prosa.
La prosa que se recorta es la que la tarjeta ya dice.

## Verificación

```bash
cd ~/itam/raya_lucaria/.worktrees/native-course-calendar
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build    ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Terminado cuando:

1. `validate` y `build` pasan, y `pytest tools/` sigue en verde.
2. **Cero términos sin definición**: se reejecuta la auditoría de jerga y los
   seis huecos quedan cerrados.
3. Cada término con tarjeta la tiene **antes** de su primer uso en prosa.
4. El glosario lista todos los términos y cada entrada enlaza a una página real.
5. Las siete ilustraciones se regeneraron en la estética nueva, sin rostros ni
   personajes con derechos, y `test_ilustraciones.py` pasa.
6. Ningún texto dentro de un SVG pasa de 8 palabras.
7. La unidad no supera las 8 700 palabras.

## Riesgos

- **`gpt-image-2` no es determinista y el cel anime es más difícil de acertar que
  el grabado técnico.** Se revisa cada imagen a ojo; máximo dos reintentos por
  escena antes de aceptar la mejor.
- **Las tarjetas pueden volverse ruido** si se aplican a términos que no lo
  merecen. De ahí el tope de 4 por página.
- **El presupuesto de palabras puede empujar a borrar matices.** Si un recorte
  quita una idea en vez de una repetición, se conserva la idea y se acepta pasar
  del presupuesto en esa página, dejándolo dicho.
