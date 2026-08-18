# Costos de hardware para modelos de IA

## Propósito

Ampliar `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md` para que una persona sin experiencia pueda dimensionar físicamente el entrenamiento y la inferencia de modelos reales. La comparación debe mostrar aceleradores, memoria, cómputo, potencia y costo de compra equivalente sin presentar estimaciones como hechos.

## Frontera económica

La unidad estimará CAPEX de hardware, no costo total del proyecto.

Cada escenario elegirá exactamente una de dos fronteras mutuamente excluyentes:

- `accelerator-only`: cantidad × precio del acelerador; excluye servidor, CPU, RAM y red;
- `system-based`: sistemas completos + red intersistema no incluida en ellos; no vuelve a sumar sus aceleradores, CPU, RAM o chasis.

Está prohibido sumar `CAPEX GPU + CAPEX sistema`. Cada total enumerará componentes incluidos y excluidos. La unidad transable —tarjeta, módulo, servidor o rack— y la cantidad mínima de compra serán explícitas; un precio imputado desde un sistema no se presentará como precio de mercado del acelerador.

Cada valoración declarará fecha, moneda, geografía, condición nuevo/usado, canal —MSRP, OEM, distribuidor, contrato o secundario—, impuestos, soporte, red y almacenamiento incluidos o excluidos. Precio histórico de adquisición y costo de reposición a una fecha de corte aparecerán en paneles separados; no formarán una misma serie.

Excluye:

- precio API;
- electricidad y demanda eléctrica facturada;
- personal, datos, edificios, desarrollo y financiamiento.

Los watts sí se mostrarán como demanda física en fronteras no acumulables: potencia nominal de aceleradores; potencia de entrada/nameplate del servidor, que ya los incluye; carga IT del cluster, con CPU/red/almacenamiento enumerados; y potencia de instalación sólo si se presenta aparte con PUE declarado. Nunca se sumará potencia GPU sobre potencia de servidor. Se enseñará `1,000 W = 1 kW`, `1,000 kW = 1 MW` y `kW × h = kWh`; accelerator-hours no equivale a kWh.

## Taxonomía de evidencia

- `FACT`: cifra publicada por una fuente primaria para esa afirmación: creador del modelo para entrenamiento, fabricante para especificaciones y vendedor/cotización para precio.
- `DERIVED`: operación reproducible aplicada a hechos publicados.
- `ESTIMATE`: rango construido con supuestos declarados.
- `SCENARIO`: configuración hipotética equivalente, no atribuida al entrenamiento real de un modelo.
- `UNDISCLOSED_BY_CREATOR`: el creador declara que no divulga el dato.
- `NOT_FOUND`: no hallado en el corpus y fecha de búsqueda registrados.
- `ESTIMATION_NOT_IDENTIFIABLE`: faltan observables para construir un rango defendible.
- `NOT_APPLICABLE`: la magnitud no corresponde.

La evidencia será por cifra, no por fila. Un ledger asignará IDs a hechos, derivaciones y escenarios; conservará fuente, fecha, fórmula, entradas, unidades, confianza y frontera. Una estimación usará escenarios bajo/base/alto internamente coherentes, nombrará variables dominantes y conservará extremos; no combinará mínimos independientes ni ocultará el rango con un punto medio.

El corpus mínimo por modelo será model card, system card, paper técnico, repositorio/configuración y anuncio oficial. Papers de terceros serán corroboración secundaria. Rumores, filtraciones, prensa y analistas no alimentarán cálculos ni gráficas. Precio API, calidad y benchmarks no se usarán para inferir parámetros o hardware.

## Modelos

### Casos documentados

Investigar GPT-3, BLOOM, PaLM, Llama 3.1 405B, DeepSeek-V3 y casos adicionales, pero incluir sólo los que tengan fuente primaria para tipo y cantidad concurrente de aceleradores más accelerator-hours o duración del mismo alcance. Cada campo conservará su propia evidencia. Pretraining, post-training y familia completa no se mezclarán.

### Modelos actuales

La fecha de corte será 2026-08-18. Auditar nombres canónicos, versión, lanzamiento, disponibilidad, región y URL primaria de OpenAI, Anthropic, Gemini, Kimi y Qwen. Para un entrenamiento cerrado faltante se mostrará `ESTIMATION_NOT_IDENTIFIABLE`; un comparable sólo podrá aparecer como `SCENARIO` separado y sin banda asociada al nombre real. Los abiertos usarán artefacto/versionado y parámetros verificables.

## Recorrido docente

1. Definir GPU/TPU, VRAM/HBM, FLOP —trabajo—, FLOP/s —tasa—, watts, accelerator-hours y costo de compra equivalente.
2. Resolver un ejemplo de ocho aceleradores concretos con análisis dimensional y dos preguntas sobre lo que HBM agregada y pico teórico no demuestran.
3. Mostrar casos documentados.
4. Mostrar por separado hechos de modelos actuales y escenarios equivalentes.
5. Separar entrenamiento, inferencia mínima e inferencia de producción.
6. Enseñar a leer rangos, escala logarítmica y confianza.
7. Cerrar con límites: capacidad, throughput, redundancia y comunicación.

## Cálculos mínimos

Para cada escenario, cuando haya entradas suficientes:

```text
HBM física instalada = aceleradores × HBM por acelerador
rendimiento pico teórico = aceleradores homogéneos × FLOP/s pico por acelerador
potencia nominal de aceleradores = aceleradores × watts nominales por acelerador
accelerator-hours = aceleradores asignados promedio × horas calendario
CAPEX accelerator-only = aceleradores × precio de la unidad transable
CAPEX system-based = sistemas completos + red intersistema no incluida
```

El pico teórico sólo se sumará para hardware homogéneo con idéntica precisión, modalidad tensorial, dense/sparse y acumulación; FP64, TF32, FP16, BF16 y FP8 serán series distintas. Nunca se tratará como rendimiento observado ni se multiplicará por tiempo para afirmar cómputo real; el cómputo de entrenamiento en FLOP aparecerá sólo publicado o derivado con eficiencia explícita. Se añadirá MFU o tasa sostenida únicamente si existe fuente.

HBM física instalada no equivale a HBM utilizable. Se separarán HBM total, HBM por réplica/shard y memoria utilizable para pesos/estado, declarando TP, PP, DP, réplicas y reserva. GB/GiB y TB/TiB, bits por parámetro, parámetros totales/activos y reglas de redondeo serán explícitos. Accelerator-hours declarará tipo de chip y si son asignadas, activas o estimadas; GPU-h y TPU-h no se convertirán ni sumarán entre sí.

## Tablas

1. Glosario de magnitudes y errores comunes.
2. Ejemplo trazable de ocho aceleradores.
3. Entrenamientos documentados, divididos en tabla esencial y ledger: modelo, alcance, fecha, parámetros, tokens, hardware, aceleradores concurrentes, accelerator-hours, duración, HBM física, pico teórico por precisión, watts y CAPEX con base homogénea.
4. Modelos actuales: hechos públicos y estados de no-identificabilidad; escenarios comparables en una tabla separada, nunca atribuidos al modelo.
5. Inferencia de capacidad: artefacto, formato, piso de pesos, escalas/metadata, runtime, KV por capa/token, batch, contexto, activaciones/workspace, reserva, topología y sistema adquirible mínimo; se rotulará “cabe, sin SLA”.
6. Inferencia operacional: sólo con throughput medido/publicado; carga docente fija, tokens entrada/salida, concurrencia, TTFT/p95, batch, contexto, utilización máxima, interconexión y N+1. Sin throughput se omitirá el CAPEX de producción comparable.
7. Supuestos de precio con `price_basis`, fecha, moneda, región, condición, canal, impuestos, soporte y componentes.

Las celdas usarán los estados definidos; nunca quedarán vacías. Una fila podrá mezclar estados porque cada cifra conservará su ID de evidencia.

## Gráficas

Crear SVG accesibles, no decorativos, con tabla equivalente:

- aceleradores de entrenamiento por modelo, eje logarítmico;
- HBM física instalada; HBM utilizable sólo en panel aparte cuando sea defendible;
- potencia con paneles o dumbbell explícito GPU-only frente a servidor/IT, nunca suma parte+todo;
- CAPEX en paneles separados por frontera y base de valoración;
- piso de memoria de inferencia y mínimo de capacidad, no SLA;
- bandas sólo para `ESTIMATE` identificable; `SCENARIO` y estados ausentes usarán forma propia.

No conectar modelos distintos como serie temporal. Una serie exigirá misma frontera, fecha/base de valoración, unidad y método. Ejes log usarán ticks en potencias de diez y la nota “igual distancia = multiplicación”; cero y estados ausentes no se graficarán, no habrá barras log desde un origen arbitrario y rangos abiertos usarán flechas. Cada valor tendrá etiqueta directa y la tabla seguirá el mismo orden. El color sólo reforzará etiquetas, patrones y formas.

## Inferencia

La capacidad mínima se calculará por componentes y se redondeará a una topología realmente adquirible; “cabe” no implica latencia o throughput aceptable. El escenario docente de producción usará 16 solicitudes concurrentes, 2,048 tokens de entrada y hasta 256 de salida, objetivo agregado de 100 tokens/s, TTFT p95 máximo de 2 s, utilización máxima de 70 % y redundancia N+1. Sólo se dimensionará cuando exista throughput observado compatible para el artefacto, runtime y hardware; de lo contrario se mostrará `ESTIMATION_NOT_IDENTIFIABLE`. No se inferirá throughput desde FLOP/s pico ni costo por token desde CAPEX sin utilización, vida útil y medición.

## Accesibilidad y formato

- Párrafos breves y una idea por bloque.
- Fórmulas después de un ejemplo numérico.
- Tablas esenciales estrechas; detalles en subtablas. En móvil tendrán scroll señalado y primera columna pegajosa, sin overflow de página.
- SVG con `title`, `desc`, alt equivalente y tabla equivalente; a 390 px no requerirán zoom horizontal, usarán texto renderizado de al menos 16 px y no tendrán etiquetas recortadas o superpuestas.
- Cada visual nuevo tendrá crédito en `_assets/CREDITOS.md`.

## Validación

- Guardas editoriales para columnas, etiquetas de evidencia, supuestos y fuentes.
- Comprobación programática de aritmética, análisis dimensional, componentes mutuamente excluyentes, estados por celda y unidades.
- `pytest tools/ -q`, XML, `raya validate`, `raya build` y `raya artifacts inspect`.
- Chromium a 390 y 1440 px; comprobar tablas, SVG, overflow y densidad.
- Revisión adversarial separada de fuentes, matemáticas, pedagogía y formato.

## Criterios de aceptación

Una persona principiante debe poder:

- explicar qué compran USD 30,000 de GPU frente a un servidor completo;
- reconstruir HBM física, FLOP, FLOP/s, watts, accelerator-hours y CAPEX de un ejemplo;
- explicar por qué HBM agregada no es memoria utilizable y pico teórico no es trabajo realizado;
- distinguir hardware documentado de hardware equivalente estimado;
- dimensionar una réplica mínima de inferencia sin confundir pesos con memoria total;
- explicar por qué potencia nominal, energía consumida y costo eléctrico no son equivalentes;
- identificar qué supuestos dominan cada rango.
