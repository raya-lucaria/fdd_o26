# Dashboard Seaborn de modelos de IA

## Propósito

Reemplazar las doce láminas SVG artesanales por gráficas Seaborn/Matplotlib legibles. El ledger YAML y `tools/ai_model_dashboard.py` siguen siendo la fuente de verdad. La ruta principal enseña una comparación a la vez; el anexo conserva el corpus completo y la trazabilidad.

## Ruta docente

Antes del corpus aparece un ejemplo guiado de tres modelos reales en dos pasos: primero año, total/activo y estado de evidencia; después “cabe en memoria” frente a “funciona con un SLA”. No pretende representar todo el mercado.

La ruta esencial contiene cinco gráficas, cada una con una pregunta y un solo eje Y:

1. **¿Cuántos parámetros almacena o activa el modelo?** Total y activo por año; explica dense/MoE y que, para un dense, activo equivale al total aunque no se duplique el punto.
2. **¿Cuánto trabajo requirió el entrenamiento?** FLOP por año. Las ausencias no se dibujan como cero: un resumen puro cuenta `UNDISCLOSED`, `NOT_FOUND` y `ESTIMATION_NOT_IDENTIFIABLE`, con fecha de búsqueda y acceso abierto/cerrado.
3. **¿Cuánta memoria mínima requieren los pesos?** Bytes del artefacto publicado o piso teórico, nunca memoria operativa completa.
4. **¿Qué hardware mínimo sugiere ese piso?** H100 por capacidad. La misma tabla muestra, como transformaciones del conteo, TDP accelerator-only y CAPEX accelerator-only; no son tres hallazgos independientes ni potencia de pared/costo real.
5. **¿Qué opciones quedan en la frontera costo–ECI?** Pareto de inferencia con costo en X y ECI en Y. ECI se presenta como un índice específico, no “inteligencia” universal.

La profundización opcional vive físicamente en la página del anexo, no debajo de la ruta esencial. Contiene cuatro gráficas independientes: aceleradores concurrentes de entrenamiento, valor de reemplazo de esas flotas, piso de potencia de inferencia y CAPEX de inferencia. Tras la quinta gráfica, la página principal dice: **“Fin de la ruta esencial. Continúa al anexo sólo si deseas profundizar.”** No se dibuja el Pareto de entrenamiento vacío: una nota explica que no existe una intersección exacta entre flotas documentadas y variantes ECI elegibles.

## Secuencia de cada bloque

Cada gráfica sigue: **pregunta → visual → conclusión → “Di esto” → “No concluyas esto” → tabla → límite**. La lectura oral prevista es 30–60 segundos.

En la ruta principal, la tabla visible tiene 4–6 casos y dos columnas (`Modelo` y `Lectura`: cifra, estado y significado). La tabla maestra de 39 modelos se mueve al anexo. Inmediatamente junto a cada gráfica hay un enlace estable a su tabla equivalente completa; ésta enumera cada marca con modelo, año exacto, valor/rango, unidad, estado, confianza, alcance y fuente(s).

## Contrato de datos

Un `FigureSpec` puro y serializable controla selección, exclusiones, panel, escalas, etiquetas, tabla compacta, tabla completa y alt text. Gráfica y tablas no mantienen listas paralelas.

El generador consume las series positivas existentes y nuevos resúmenes puros de ausencia; `PlotPoint` no se usa para fabricar ceros. Las selecciones docentes son deterministas y documentadas. La ruta esencial muestra como máximo 12–15 marcas y cinco etiquetas por gráfica; el anexo puede mostrar el corpus completo a tamaño propio.

Para años coincidentes se usa un desplazamiento simétrico determinista dentro de una banda estrecha del año. El año exacto permanece en la tabla y el desplazamiento no representa tiempo. No hay jitter aleatorio, agregación, estimador, intervalo Seaborn, regresión ni línea que una modelos distintos.

## Gramática visual y escalas

- Año: eje X lineal con ticks enteros 2018–2026; nunca logarítmico.
- Magnitudes temporales: Y `log10` sólo si todos los límites son positivos y el rango declarado cruza al menos dos órdenes; si no, escala lineal.
- Pareto: costo X logarítmico y ECI Y lineal.
- Los límites incluyen extremos `low/high`; usan padding multiplicativo en log y aditivo en lineal. Ningún intervalo puede recortarse.
- Los ticks usan SI decimal y unidad inequívoca: `mil millones de parámetros` (no `B`), `GB` decimales, `FLOP`, `W` y `USD`.
- Estado de evidencia usa color y borde redundantes: `FACT` relleno sólido+borde continuo; `DERIVED` relleno claro+borde continuo; `ESTIMATE` sin relleno+borde continuo; `SCENARIO` sin relleno+borde doble. Una prueba monocroma exige que cada par siga siendo distinguible. Total/activo y artefacto/piso usan panel o símbolo interior ortogonal, no el código del estado. La leyenda sólo muestra roles presentes y no excede dos líneas.

Pareto dibuja el rectángulo o barras de incertidumbre de cada candidato; `safe`, `possible` y `dominated` se distinguen también por borde. No conecta centros ni esquinas. Etiqueta directamente como máximo cinco casos: frontera, extremos y uno o dos dominados. Los ocho candidatos llevan claves numéricas cortas ligadas a una tabla contigua, nunca nombres completos apilados. Incluye fecha del snapshot. Las clasificaciones se reconstruyen desde los mismos límites usados por `pareto_frontier`. Sin ampliar, debe poder identificarse la frontera.

## Archivos y migración

SVG es el único formato; PNG requeriría otro diseño y no es fallback automático. `tools/gen_ai_model_dashboard.py` se reescribe en vez de añadir un segundo generador. Absorbe la escritura de `gen_ai_dashboard_confidence.py`; éste se elimina cuando no queden consumidores.

| Asset nuevo | Ruta | `FigureSpec` / serie | Tabla |
|---|---|---|---|
| `ai-dashboard-parameters.svg` | esencial | `parameters` | `#tabla-parametros` |
| `ai-dashboard-training-flop.svg` | esencial | `training_flop` | `#tabla-flop-entrenamiento` |
| `ai-dashboard-inference-memory.svg` | esencial | `artifact_or_weight_floor` | `#tabla-memoria-inferencia` |
| `ai-dashboard-inference-hardware.svg` | esencial | `h100_capacity_floor` | `#tabla-hardware-inferencia` |
| `ai-dashboard-pareto-inference.svg` | esencial | `pareto_inference` | `#tabla-pareto-inferencia` |
| `ai-dashboard-training-accelerators.svg` | anexo | `training_accelerators` | `#tabla-aceleradores-entrenamiento` |
| `ai-dashboard-training-replacement.svg` | anexo | `training_replacement_value` | `#tabla-reemplazo-entrenamiento` |
| `ai-dashboard-inference-power.svg` | anexo | `inference_tdp_floor` | `#tabla-potencia-inferencia` |
| `ai-dashboard-inference-capex.svg` | anexo | `inference_capex_floor` | `#tabla-capex-inferencia` |

Se retiran exactamente: `ai-training-parameters.svg`, `ai-training-flop.svg`, `ai-training-accelerators.svg`, `ai-training-power.svg`, `ai-training-replacement-value.svg`, `ai-inference-parameters.svg`, `ai-inference-memory.svg`, `ai-inference-accelerators.svg`, `ai-inference-power.svg`, `ai-inference-capex.svg`, `ai-pareto-training.svg` y `ai-pareto-inference.svg`.

Antes de borrar se inventariarán consumidores con `rg`: Markdown principal/anexo, `CREDITOS.md`, ambos generadores, pruebas de arquitectura/diagramas/dashboard/DOM, comentarios CI e inventarios. Un test negativo busca cada basename retirado sólo en consumidores activos (`course/**`, `tools/**`, `.github/**`, `raya.yaml` y `README.md`); excluye los planes/especificaciones históricos. Otra aserción exige que los doce archivos retirados no existan. Se eliminan sólo esas doce láminas y créditos; los cinco visuales de hardware ajenos permanecen. El cambio de assets, Markdown, anexo, créditos y pruebas es atómico.

`FigureSpec` es el único escritor de tablas. El generador reemplaza bloques Markdown entre sentinelas estables `AI_DASHBOARD:<id>:START/END` en principal y anexo; una regeneración con diff falla CI. Las filas completas provienen de los mismos registros serializados que se dibujan.

## Entorno reproducible

Crear `tools/ai_dashboard_requirements.in` y una clausura transitiva Linux completa `tools/ai_dashboard_requirements.lock`, generada con `uv pip compile --python-version 3.12 --generate-hashes ...` e instalada con `uv pip sync --require-hashes`. CI usa Python 3.12.11. La igualdad byte a byte se exige dentro del mismo job y versión de imagen reportada por GitHub; dos procesos aislados coinciden con el asset versionado. No se reutiliza el Python 3.10 local observado durante diseño. Raya sólo consume assets y no requiere plotting deps.

El generador fuerza backend `Agg`, `TZ=UTC`, `LC_ALL=C.UTF-8`, tamaño/DPI y orden estable. Usa `tools/fonts/DejaVuSans.ttf` vendida con licencia/crédito y `svg.fonttype='none'`. Fija `svg.hashsalt`, elimina fecha, establece `Creator` constante y canonicaliza namespaces, atributos, IDs y serialización. Dos procesos aislados regeneran bytes idénticos.

## Accesibilidad y móvil

El alt de Markdown/Raya y la tabla equivalente son la interfaz accesible principal. Cada SVG además recibe por postproceso determinista `role="img"`, un solo `<title>` y `<desc>` con IDs estables referidos por `aria-labelledby`; regenerar no duplica nodos. El texto permanece como texto. El alt resume en 2–4 frases la pregunta, tendencia y límite, no recita la tabla.

A 390 px: una gráfica por fila, tipografía efectiva mínima 16 px, sin scroll horizontal, recortes ni colisiones. Criterio docente: la pregunta y conclusión deben entenderse en diez segundos. La tabla compacta usa dos columnas o fichas verticales; el detalle ancho vive en el anexo.

## Pruebas

TDD sustituye, no acumula, supuestos del SVG manual. Se conservan pruebas puras de membresía, unidades, rangos, estados, confianza, ausencias y Pareto; se reemplazan pruebas de geometría/data-attributes artesanales.

Las nuevas guardas verifican:

- manifiesto exacto de nueve assets, rutas/anclas correctas y ausencia de consumidores de los doce retirados;
- una sola fuente `FigureSpec` para marcas y filas completas;
- pertenencia, selección, rangos, desplazamiento determinista y ausencia de líneas/regresión;
- reconstrucción de Pareto y nombres de sus ocho candidatos;
- alt en DOM construido, tablas completas equivalentes y créditos sin huérfanos en unidad 3;
- escalas/ticks/unidades, texto, intervalos y etiquetas sin colisión;
- principal con cinco imágenes, 4–6 filas visibles por tabla, 900–1,400 palabras y 8–12 viewports móviles; anexo con cuatro imágenes opcionales, tabla maestra y tablas completas sin límite artificial de altura; ambas a 390×844 y 1440×900 sin overflow y con tipografía mínima;
- hashes idénticos en dos procesos limpios.

CI añade un job obligatorio `dashboard-assets` sobre Python 3.12.11: instala el lock con hashes, regenera dos veces en procesos limpios, compara assets/Markdown, ejecuta pruebas puras, instala Playwright fijado y `python -m playwright install --with-deps chromium`, y corre DOM móvil/escritorio sin `importorskip`. Un job obligatorio `course-build` obtiene Raya en el mismo commit `dd1fdba4e16cb79fa5515eb689fabbc74014f3b6` fijado por el workflow reusable y ejecuta `validate`, `build` y `uv run raya artifacts inspect <artifact-path>` sin skip por checkout ausente. Pages depende del job existente `checks`, de `dashboard-assets` y de `course-build`. Localmente también se ejecuta `python3 -m pytest tools/ -q`.

## Publicación y reversión

La migración se integra atómicamente. Antes de publicar se registra el SHA de producción, se inspecciona el artifact y se validan nueve rutas locales. Tras `main`, se espera el éxito terminal de checks y Pages y se exige HTTP 200/contenido correcto para página, anexo y nueve URLs. Si falla, se crea `git revert <commit-de-migración>`, se publica ese nuevo commit y se verifica que Pages restauró página/assets anteriores; nunca se hace reset/force-push ni se edita `artifact/`.

## Criterio de éxito

Sin ampliar la imagen, una persona novata puede decir qué mide la gráfica, identificar 2–3 casos, distinguir publicación de inferencia/escenario y nombrar al menos una conclusión válida y una inválida. El corpus exhaustivo sigue disponible y reconstruible sin saturar la ruta docente.
