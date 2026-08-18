# Costos de hardware para modelos de IA

## Propósito

Ampliar `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md` para que una persona sin experiencia pueda dimensionar físicamente el entrenamiento y la inferencia de modelos reales. La comparación debe mostrar aceleradores, memoria, cómputo, potencia y costo de compra equivalente sin presentar estimaciones como hechos.

## Frontera económica

La unidad estimará CAPEX de hardware, no costo total del proyecto.

Incluye:

- aceleradores y sistemas necesarios;
- CPU, RAM, red y chasis cuando haya precios o factores públicos defendibles;
- costo de compra equivalente del cluster de entrenamiento;
- hardware mínimo de una réplica de inferencia;
- ejemplo de inferencia de producción con redundancia y concurrencia.

Excluye:

- precio API;
- electricidad y demanda eléctrica facturada;
- personal, datos, edificios, desarrollo y financiamiento.

Los watts sí se mostrarán como demanda física. Se distinguirán potencia nominal del acelerador, potencia del servidor y potencia aproximada del cluster. No se convertirán automáticamente en consumo medido.

## Taxonomía de evidencia

- `FACT`: cifra publicada por el creador, proveedor de hardware, paper o model card primario.
- `DERIVED`: operación reproducible aplicada a hechos publicados.
- `ESTIMATE`: rango construido con supuestos declarados.
- `UNDISCLOSED`: el proveedor no publicó el dato.

Cada fila incluirá fecha de consulta, fuente, confianza alta/media/baja y notas de frontera. Una estimación conservará ambos extremos; no se reemplazará por un punto medio sin mostrar el rango.

## Modelos

### Casos documentados

Investigar y conservar sólo los casos cuyas fuentes primarias permitan reconstruir una parte material del hardware: GPT-3, BLOOM, PaLM, Llama 3.1 405B, DeepSeek-V3 y cualquier caso adicional con mejor divulgación.

### Modelos actuales

Auditar los nombres vigentes en la página y verificar su existencia, versión y fecha antes de conservarlos. Cubrir las familias actuales de OpenAI, Anthropic, Gemini, Kimi y Qwen. Los modelos cerrados usarán rangos comparables anclados en hardware y entrenamientos documentados; los abiertos usarán parámetros, precisión y memoria verificables cuando estén publicados.

## Recorrido docente

1. Definir GPU/TPU, VRAM/HBM, FLOP, FLOPS, watts, GPU-hora y costo de compra equivalente.
2. Resolver un ejemplo de ocho aceleradores con aritmética visible.
3. Mostrar casos documentados.
4. Mostrar modelos actuales estimados.
5. Separar entrenamiento, inferencia mínima e inferencia de producción.
6. Enseñar a leer rangos, escala logarítmica y confianza.
7. Cerrar con límites: capacidad, throughput, redundancia y comunicación.

## Cálculos mínimos

Para cada escenario, cuando haya entradas suficientes:

```text
HBM agregada = aceleradores × HBM por acelerador
FLOPS pico agregado = aceleradores × FLOPS pico por acelerador
potencia nominal GPU = aceleradores × watts por acelerador
GPU-horas = aceleradores × horas de entrenamiento
CAPEX GPU = aceleradores × precio unitario estimado
CAPEX sistema = número de sistemas × precio por sistema
```

Los FLOPS especificarán precisión y si son dense/sparse. El número de GPU no se inferirá únicamente de parámetros. El costo del acelerador suelto y el del sistema completo serán columnas distintas cuando ambos existan.

## Tablas

1. Glosario de magnitudes y errores comunes.
2. Ejemplo trazable de ocho aceleradores.
3. Entrenamientos documentados: modelo, fecha, parámetros, tokens, hardware, cantidad, duración/GPU-horas, HBM, precisión, FLOPS, watts y CAPEX equivalente.
4. Modelos actuales estimados con las mismas unidades, rango, evidencia y confianza.
5. Inferencia: precisión, memoria de pesos, margen runtime/KV, GPU mínima, servidor mínimo, réplica de producción, potencia y CAPEX.
6. Supuestos de precio por acelerador y sistema, con fecha y fuente.

Las celdas sin evidencia dirán `UNDISCLOSED`; nunca quedarán vacías.

## Gráficas

Crear SVG accesibles, no decorativos, con tabla equivalente:

- aceleradores de entrenamiento por modelo, eje logarítmico;
- HBM agregada, eje logarítmico;
- potencia de aceleradores y sistema en kW/MW;
- CAPEX equivalente en USD, eje logarítmico;
- memoria mínima de inferencia y número de aceleradores;
- bandas de rango para modelos cerrados y marcadores distintos para `FACT` y `ESTIMATE`.

No conectar puntos de modelos distintos como serie temporal. Los ejes declararán unidades, escala y frontera. El color sólo reforzará etiquetas, patrones y formas.

## Inferencia

La configuración mínima representa una réplica capaz de cargar pesos más margen explícito para runtime y KV bajo un contexto/batch declarado. La configuración de producción añadirá al menos redundancia y concurrencia ilustrativa. No se inferirá costo por token a partir de CAPEX sin utilización, vida útil y throughput medidos.

## Accesibilidad y formato

- Párrafos breves y una idea por bloque.
- Fórmulas después de un ejemplo numérico.
- Tablas con scroll interno móvil, sin overflow de página.
- SVG con `title`, `desc`, alt equivalente y texto efectivo legible a 390 px.
- Cada visual nuevo tendrá crédito en `_assets/CREDITOS.md`.

## Validación

- Guardas editoriales para columnas, etiquetas de evidencia, supuestos y fuentes.
- Comprobación programática de aritmética y unidades.
- `pytest tools/ -q`, XML, `raya validate`, `raya build` y `raya artifacts inspect`.
- Chromium a 390 y 1440 px; comprobar tablas, SVG, overflow y densidad.
- Revisión adversarial separada de fuentes, matemáticas, pedagogía y formato.

## Criterios de aceptación

Una persona principiante debe poder:

- explicar qué compran USD 30,000 de GPU frente a un servidor completo;
- reconstruir HBM, FLOPS, watts, GPU-horas y CAPEX de un ejemplo;
- distinguir hardware documentado de hardware equivalente estimado;
- dimensionar una réplica mínima de inferencia sin confundir pesos con memoria total;
- explicar por qué potencia nominal, energía consumida y costo eléctrico no son equivalentes;
- identificar qué supuestos dominan cada rango.
