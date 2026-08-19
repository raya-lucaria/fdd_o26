# Dashboard comparativo de modelos de IA — diseño

## Propósito

Reemplazar el bloque actual de costos y hardware de IA por una experiencia visual simple: una tabla amplia de modelos, varias gráficas temporales y dos fronteras de Pareto. La ruta principal debe permitir mirar, comparar e interpretar; la metodología, las fuentes, las fórmulas y los IDs vivirán en un anexo técnico enlazado.

La referencia visual es una gráfica temporal de puntos con año en X, escala logarítmica en Y, modelos seleccionados etiquetados y bandas para incertidumbre. El rediseño no eliminará datos: cambiará su jerarquía.

## Resultado docente

Al terminar, un estudiante podrá:

1. distinguir dato publicado, cálculo reproducible, estimación y ausencia;
2. describir cómo cambiaron parámetros, cómputo y escala física con el tiempo;
3. separar entrenamiento de inferencia y capacidad de SLA;
4. interpretar una frontera de Pareto sin convertirla en un ranking universal;
5. explicar por qué modelos cerrados aparecen en la tabla aunque falten sus cifras físicas.

## Arquitectura de contenido

### Página principal

La página principal conservará una ruta de 8–12 pantallas móviles:

1. **En 30 segundos:** tres conclusiones y leyenda visual.
2. **Tabla maestra:** 30–35 modelos, columnas esenciales y filtros visuales estáticos.
3. **Entrenamiento a través del tiempo:** cinco small multiples.
4. **Inferencia local a través del tiempo:** cinco small multiples.
5. **Fronteras de Pareto:** dos paneles y explicación breve.
6. **Cómo leer sin sobreinterpretar:** tres advertencias.
7. **Qué debes recordar:** cinco conclusiones.

La prosa principal tendrá 900–1,400 palabras. Cada gráfica tendrá un comentario de dos o tres frases: qué cambia, qué modelos destacan y qué no permite concluir.

### Anexo técnico

Un subdirectorio renderizado bajo la lección contendrá:

- tabla completa por modelo y por celda;
- fuentes primarias y fecha de consulta;
- fórmulas, supuestos y rangos;
- metodología de ECI y Pareto;
- casos `NOT_FOUND`, `UNDISCLOSED` y `ESTIMATION_NOT_IDENTIFIABLE`;
- reconstrucciones de entrenamiento e inferencia;
- artefactos, revisiones, shards, hardware y bases de valoración.

La página principal enlazará el anexo desde cada visual. No mostrará IDs técnicos dentro de la ruta oral.

## Corpus

La tabla maestra cubrirá, como mínimo:

- históricos: BERT-Large, T5-11B, GPT-3, Gopher, LaMDA, Chinchilla, OPT-175B, PaLM, BLOOM;
- Meta: Llama 1 65B, Llama 2 70B, Llama 3.1 8B/70B/405B, Llama 4 cuando exista evidencia comparable;
- Google: Gemma 7B, Gemma 2 27B, Gemma 3 27B y Gemini actuales;
- DeepSeek: LLM 67B, V2, V3 y R1;
- Qwen: 72B, Qwen2/2.5 72B, Qwen3 30B/235B y Qwen3.8;
- Kimi: K2 y K3;
- Mistral: Mistral 7B, Mixtral 8×7B y Large 2;
- xAI: Grok-1 y modelos actuales;
- OpenAI y Anthropic actuales, aunque sus magnitudes físicas estén sin divulgar.

Cada modelo tendrá identidad exacta, organización, año, apertura, arquitectura densa/MoE y estado por celda. Una ausencia no se convertirá en cero ni en un punto inventado.

## Tabla maestra

La vista principal usará bloques por modelo o una tabla de máximo cuatro columnas por panel:

- modelo, organización y año;
- abierto/cerrado y denso/MoE;
- parámetros totales/activos;
- resumen de entrenamiento;
- resumen de inferencia;
- capacidad general ECI cuando exista;
- estado dominante de evidencia.

En móvil, ningún bloque tendrá más de dos columnas simultáneas. La tabla detallada del anexo podrá dividirse por familias de métricas. No se usará `overflow-wrap:anywhere` para comprimir IDs.

## Lenguaje visual

El estado se codificará de forma redundante:

| Estado | Color | Forma/estilo | Significado |
|---|---|---|---|
| `FACT` | verde | círculo sólido | publicado por una fuente aplicable |
| `DERIVED` | azul | cuadrado | cálculo reproducible |
| `ESTIMATE` | naranja | rombo y banda/error bars | rango con supuestos |
| `SCENARIO` | violeta | triángulo | comparación docente, no historia real |
| ausencia | gris | cruz o fila sin punto | no divulgado/no identificable |

Modelo abierto y cerrado se distinguirán además por contorno sólido o hueco. Las etiquetas directas se reservarán para 8–12 modelos por gráfica; todos permanecerán en la tabla equivalente.

## Gráficas de entrenamiento

Todas usarán año de publicación en X. Y será logarítmico salvo que la métrica no lo justifique. Cada panel tendrá cobertura distinta y declarará `n`.

1. **Parámetros totales y activos.** Aproximadamente 30 modelos; pares total/activo para MoE.
2. **Trabajo de entrenamiento (FLOP).** Publicado o `DERIVED` mediante `6NT` para densos; MoE sólo como `ESTIMATE` con rango y advertencia.
3. **Chips concurrentes y accelerator-hours.** Paneles separados o símbolos distintos; nunca se sumarán GPU-h y TPU-chip-h.
4. **Suma de TDP o energía envolvente.** Sólo configuraciones compatibles; `n × TDP` no será consumo medido ni potencia de pared.
5. **Valor de reemplazo del hardware.** Serie `SCENARIO` con fecha/base común. Nunca se titulará “costo real de entrenar el modelo”. El CAPEX histórico real permanecerá ausente salvo evidencia de adquisición.

Los modelos cerrados actuales aparecerán como marcas grises en el eje temporal o filas sin punto cuantitativo.

## Gráficas de inferencia

Se separarán dos preguntas.

### Capacidad sin SLA

Para modelos open-weight y artefactos versionados:

1. tamaño del artefacto o piso de pesos;
2. aceleradores H100-equivalentes por capacidad física;
3. suma de TDP accelerator-only bajo escenario común;
4. CAPEX accelerator-equivalent bajo precio común;
5. parámetros totales y activos.

El número de aceleradores será un piso de capacidad, no una topología recomendada. Runtime, KV, workspace y reserva se mostrarán en ejemplos auditables, no se ocultarán dentro de “GPU mínima”.

Los modelos cerrados figurarán como `UNDISCLOSED`/`NOT_IDENTIFIABLE`; no se inferirá hardware local desde precios API o clusters de entrenamiento.

### Operación medida

Throughput y TTFT vivirán en una gráfica aparte, sólo cuando coincidan modelo/revisión, artefacto, precisión, hardware, topología, runtime, batch/concurrencia y longitudes. No formarán una línea temporal comparable si esas condiciones difieren.

## Pareto

El eje de capacidad será **Epoch Capabilities Index (ECI)**, rotulado “capacidad general según ECI”, con snapshot y fecha. ECI no se llamará inteligencia ni IQ. LiveBench podrá aparecer como comprobación independiente; sus scores no se mezclarán algebraicamente con ECI.

### Panel A: entrenamiento

- X: CAPEX de hardware documentado o valor de reemplazo claramente rotulado, en USD y escala log.
- Y: ECI y su intervalo cuando esté disponible.
- Sólo entran modelos con intersección defendible de ambas métricas.
- Modelos cerrados sin costo identificable permanecen en la tabla, fuera de la frontera.

### Panel B: inferencia local

- X: CAPEX mínimo de capacidad bajo un escenario fijo.
- Y: ECI.
- Sólo modelos open-weight.
- BF16 e INT4 se separan en small multiples; el score original no se atribuirá automáticamente a un artefacto cuantizado si no se evaluó esa variante.

Un modelo A domina B cuando `costo_A <= costo_B` y `ECI_A >= ECI_B`, con al menos una desigualdad estricta. Con rangos:

- frontera segura: no dominado incluso con extremos adversos;
- frontera posible: no dominado para alguna realización del intervalo.

La segura será sólida y la posible punteada. No se usará el punto medio para decidir dominancia.

## Datos y generación

El ledger será la única fuente de verdad. Se ampliará sin romper los datos ya auditados. Cada métrica tendrá:

- valor/rango y unidad;
- estado;
- fuente aplicable;
- fórmula y entradas cuando sea derivada;
- fecha o versión;
- frontera física/económica;
- confianza definida por celda cuando corresponda.

Un generador Python producirá SVG deterministas, tablas equivalentes y metadatos. Los SVG incluirán `title`, `desc`, etiquetas directas, `data-source-ids` y estados. Los estados ausentes nunca se colocarán en ejes logarítmicos.

## Fuentes

Prioridad:

1. papers, model/system cards y repositorios del creador;
2. fichas del fabricante para hardware;
3. Epoch ECI y su metodología/dataset versionado para capacidad;
4. LiveBench versionado sólo como sensibilidad;
5. valoraciones con fecha, región, canal, condición e inclusiones.

No se usarán rumores, filtraciones, snippets ni prensa para poblar puntos. Una fuente secundaria sólo corroborará una afirmación ya apoyada.

## Accesibilidad y legibilidad

- SVG con texto efectivo mínimo de 16 px a 390 px.
- Sin recortes, solapamientos ni dependencia exclusiva de color.
- Tabla equivalente inmediata o enlace claro al anexo.
- En móvil, tarjetas de una o dos columnas; ninguna palabra o ID partido carácter por carácter.
- La página principal completa tendrá puntos de reentrada y “qué estás comparando” antes de cada grupo.
- Los detalles exactos no repetirán cinco veces el mismo valor en gráfica, prosa y tabla.

## Pruebas de aceptación

1. La tabla maestra contiene al menos 30 modelos y las organizaciones requeridas.
2. Existen cinco gráficas de entrenamiento, cinco de inferencia y dos de Pareto.
3. Todos los ejes temporales usan año en X y declaran unidad/escala en Y.
4. `FACT`, `DERIVED`, `ESTIMATE`, `SCENARIO` y ausencias son distinguibles sin color.
5. Ningún modelo cerrado recibe parámetros, costo o hardware inferidos sin método reproducible y rango.
6. La frontera se reproduce desde datos y algoritmo probados.
7. Main route de 900–1,400 palabras; metodología completa en el anexo.
8. Chromium 390×844 y 1440×900 sin overflow, recortes, tablas comprimidas o texto menor al mínimo.
9. Pytest completo, Raya validate/build/inspect y determinismo pasan.
10. Producción contiene el commit publicado y todos los assets responden correctamente.

## Fuera de alcance

- ranking universal de calidad;
- costo total de desarrollo de una empresa;
- costo API mezclado con CAPEX local;
- energía de pared inferida únicamente desde TDP;
- predicción de parámetros o arquitectura de modelos cerrados sin evidencia;
- afirmar SLA desde capacidad o FLOP/s pico.
