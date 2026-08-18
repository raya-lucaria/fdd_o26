---
id: paralelismo-performance-energia
title: "Paralelismo, performance y energía"
nav_title: "Paralelismo y energía"
summary: "Por qué CPU, GPU y aceleradores favorecen trabajos distintos y cómo separar cómputo, memoria y energía."
status: ready
estimated_time: "21 minutos"
tags: [paralelismo, gpu, roofline, energia]
---

CPU, GPU y aceleradores organizan el paralelismo de maneras distintas. **El procesador se elige por forma y límite**. El pico es un techo.

## CPU y GPU intercambian flexibilidad por amplitud

![Comparación conceptual: una CPU concentra pocas rutas flexibles y una GPU reúne muchas rutas paralelas para trabajo regular.](../_assets/cpu-vs-gpu.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** la CPU dedica más recursos a pocos flujos con decisiones y baja latencia. La GPU reúne muchas unidades para aplicar operaciones parecidas a numerosos datos. Ninguna forma sirve para todo problema.

Una CPU favorece control irregular, trabajo secuencial y solicitudes pequeñas. Una GPU favorece **throughput** si hay trabajo independiente. Ramas o accesos divergentes dejan unidades esperando; lanzar kernels, copiar y sincronizar también cuesta. A menudo la CPU coordina y la GPU procesa lotes, por lo que se mide el flujo completo.

![Acercamiento de una Palit GeForce RTX 5090 GameRock: carcasa ondulada y ventiladores de la tarjeta gráfica.](../_assets/real-rtx-5090.webp)

**FACT (objeto fotografiado):** Palit RTX 5090 GameRock. Foto de [PantheraLeo1359531, Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Palit_GeForce_RTX_5090_Gamerock_20250530_HOF3973-HDR_RAW-Export.png), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0); redimensionada a WebP.

**FACT (especificación NVIDIA de referencia):** la RTX 5090 publica **575 W TGP** para la tarjeta, no para el equipo. El diseño Palit fotografiado puede variar.

## Los aceleradores especializan el trabajo

Un **acelerador** optimiza hardware para un dominio, con recursos propios, compartidos o unificados.

**NPU** es una etiqueta industrial para operadores neuronales, no una arquitectura única. Un operador no soportado puede volver a CPU o GPU.

**TPU** nombra una familia de ASIC de Google, no una categoría genérica. **FACT (pico, no benchmark):** cada TPU7x Ironwood publica **2,307 TFLOPS BF16**, **4,614 TFLOPS FP8**, **192 GiB HBM** y **7,380 GB/s** HBM. La precisión cambia tasa, memoria, tráfico y comportamiento numérico; los picos no forman un ranking entre precisiones o sistemas.

Especializar intercambia flexibilidad por eficiencia; importan operadores, compilador, memoria, lote, transferencias y disponibilidad.

## FLOP es trabajo; FLOPS es tasa

Un **FLOP** es una operación de punto flotante. **FLOPS** significa operaciones de punto flotante por segundo. **FACT (convención SI decimal):** GFLOPS, TFLOPS y PFLOPS multiplican esa tasa por $10^9$, $10^{12}$ y $10^{15}$. Un total de FLOP describe trabajo; FLOPS describe ritmo.

La precisión es parte de la unidad de comparación:

- **FP64** conserva más precisión para ciertos cálculos científicos.
- **FP32** ofrece precisión y soporte general.
- **FP16 y BF16** reducen bytes y aprovechan unidades matriciales.
- **FP8 e INT8** reducen más tráfico, con técnicas numéricas apropiadas.

Menos bits no garantiza calidad. Un pico *sparse* supone ceros aprovechables y no equivale al pico *dense*. TOPS enteros y FLOPS flotantes tampoco son intercambiables.

## Roofline conecta cómputo y memoria

Roofline responde una pregunta concreta: **queremos saber si este trabajo queda limitado por la velocidad de la memoria o por la capacidad de cálculo del chip.** Sigamos una suma real, primero en una posición y después en una lista completa.

### 1. Una posición: qué entra y qué sale

Tenemos tres listas de números: `A`, `B` y `C`. Los corchetes indican una posición; `[0]` es la **primera posición**.

`C[0] = A[0] + B[0]`

Cada número está en **FP32**, un formato que ocupa **4 bytes**. Para hacer una cuenta sencilla, contamos dos lecturas y una escritura entre la memoria y el chip:

1. leer `A[0]`: 4 bytes;
2. leer `B[0]`: 4 bytes;
3. sumar ambos números: 1 FLOP;
4. guardar `C[0]`: 4 bytes.

Por tanto, mueve 4 + 4 + 4 = **12 bytes** y hace **1 FLOP**. Movemos muchos datos para hacer poco cálculo.

### 2. La misma cuenta para 1,000 posiciones

Para **1,000 elementos**, multiplicamos ambas cantidades por 1,000:

- datos: 12 bytes × 1,000 = **12,000 bytes**;
- cálculo: 1 FLOP × 1,000 = **1,000 FLOP**.

La proporción no cambia: `1,000 ÷ 12,000 = 1 ÷ 12 ≈ 0.083`. En palabras: hacemos **1 suma por cada 12 bytes movidos**. Su abreviatura es **0.083 FLOP/byte**. Esa proporción entre cálculo y datos se llama **intensidad aritmética**.

### 3. Cuánto trabajo puede alimentar la memoria

Supongamos un hardware hipotético con dos límites:

- **100 GB/s:** datos que la memoria puede entregar por segundo;
- **2 TFLOPS FP32 = 2,000 GFLOPS:** operaciones que el chip podría calcular por segundo.

Ahora calculamos cuántas operaciones por segundo puede sostener la memoria para esta suma.

`100 GB/s × 0.083 FLOP/byte ≈ 8.3 GFLOPS`

Los bytes se cancelan: `(bytes/s) × (FLOP/byte) = FLOP/s`. Aquí usamos prefijos decimales: 1 GB son $10^9$ bytes y 1 GFLOP son $10^9$ FLOP.

### 4. Elegir el techo que realmente limita

| Techo | Resultado para esta suma |
|---|---:|
| Memoria | 8.3 GFLOPS |
| Cómputo del chip | 2,000 GFLOPS |
| **Limita memoria: elige el menor** | **8.3 GFLOPS** |

`min` significa **escoger el número menor**. En este caso, `min(2,000, 8.3) = 8.3`. El chip podría calcular mucho más rápido, pero la memoria sólo puede entregarle datos suficientes para sostener unos 8.3 GFLOPS.

![Resumen Roofline de hardware hipotético con 100 GB/s y 2 TFLOPS FP32, equivalentes a 2,000 GFLOPS: para una suma de intensidad 0.083 FLOP/byte, el techo de memoria es 8.3 GFLOPS y limita el rendimiento; ambos techos se igualan en 20 FLOP/byte.](../_assets/roofline-lite.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** la línea inclinada es lo que puede alimentar la memoria; la línea horizontal es lo que puede calcular el chip. El punto de la suma cae en 8.3 GFLOPS. Como está muy por debajo del techo de 2,000 GFLOPS, limita la memoria. El **quiebre, 20 FLOP/byte**, es el punto donde ambos techos se igualan; no hace falta calcularlo para entender esta suma.

### Cómo interpretar la altura y la meseta

En el eje vertical, estar más arriba significa poder terminar más operaciones por segundo. Pero la línea Roofline muestra un **techo**, no el rendimiento que el programa alcanzó realmente.

Con el mismo hardware del ejemplo, multiplicamos la intensidad por 100 GB/s hasta encontrar el máximo del chip:

| Intensidad del trabajo | Techo por memoria | Techo que manda |
|---:|---:|---:|
| 1 FLOP/byte | 100 GFLOPS | 100 GFLOPS, memoria |
| 10 FLOP/byte | 1,000 GFLOPS | 1,000 GFLOPS, memoria |
| 20 FLOP/byte | 2,000 GFLOPS | 2,000 GFLOPS, ambos |
| 30 FLOP/byte | 3,000 GFLOPS | **2,000 GFLOPS, chip** |

La línea sube mientras la memoria es el límite: reutilizar datos permite hacer más operaciones con los mismos bytes. En 20 FLOP/byte llegamos al máximo de 2,000 GFLOPS del chip. A partir de ahí aparece la **meseta**: la memoria podría sostener más trabajo, pero el chip no puede ejecutar más de 2,000 GFLOPS.

### Cuándo puede decirse que un resultado es bueno

Una intensidad alta **no significa por sí sola** que un programa sea bueno, rápido o eficiente. Algunos algoritmos necesitan mover muchos datos y naturalmente tienen intensidad baja. Tampoco sería válido cambiar el resultado que se calcula sólo para subir en la gráfica.

La comparación útil mantiene el **mismo trabajo**, hardware y precisión, y mide qué fracción del techo correspondiente se alcanzó. Por ejemplo, para nuestra suma el techo es 8.3 GFLOPS:

- rendimiento medido de 6 GFLOPS: `6 ÷ 8.3 ≈ 72% del techo`;
- rendimiento medido de 7.5 GFLOPS: `7.5 ÷ 8.3 ≈ 90% del techo`.

Ese **porcentaje del techo** permite decir que 90% aprovecha mejor este hardware que 72%. No permite afirmar que la suma sea mejor algoritmo que otro programa ni que 7.5 GFLOPS sea rápido en cualquier computadora.

### Resumen opcional: la fórmula general

La intensidad $I$ es el número de FLOP dividido entre los bytes movidos:

$$I = \frac{\text{FLOP}}{\text{bytes movidos}}$$

$$P \leq \min(P_{pico},\ B_{memoria}\times I)$$

$P$ es el rendimiento posible, $P_{pico}$ es el techo de cálculo y $B_{memoria}\times I$ es el techo impuesto por la memoria. La función $\min$ elige el menor de esos dos techos.

Roofline da una **estimación favorable**, no un rendimiento medido. Los 12 bytes son una cuenta mínima de dos lecturas y una escritura; las cachés y la forma de guardar los datos pueden cambiar el tráfico real. La máquina también pierde tiempo al iniciar y coordinar el trabajo.

## Pico, benchmark y aplicación son capas distintas

El **pico teórico** combina unidades, operaciones por ciclo y frecuencia bajo supuestos de precisión, instrucciones y densidad. Puede omitir entrada, copias y coordinación.

En MLPerf, una comparación válida usa el mismo benchmark: la misma tarea o modelo, el mismo dataset y el mismo objetivo de calidad. También alinea escenario, métrica y división; la división *Closed* exige el modelo de referencia, mientras *Open* permite cambios que deben interpretarse como tales.

Precisión, lote, software y disponibilidad dan contexto. Cuando una entrega incluye potencia, MLPerf mide el sistema completo mediante AC en la pared durante ese benchmark; TDP y potencia nominal de la fuente no equivalen.

La **aplicación observada** incluye el pipeline; sus métricas deben compartir contexto.

## Potencia y energía responden cosas distintas

![Relación potencia por tiempo igual a energía, con escalas de watts para chip, kilowatts para rack y megawatts para centro de datos.](../_assets/escala-energia.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** watts por horas producen watt-hora. Un dispositivo suele expresarse en W, un rack en kW, un centro de datos en MW y la generación agregada puede llegar a GW. Al integrar tiempo aparecen Wh, kWh, MWh, GWh o TWh.

El **watt** mide potencia, una tasa instantánea. El **watt-hora** mide energía acumulada. **FACT (convención SI decimal):** $1\ \mathrm{kW}=10^3\ \mathrm{W}$, $1\ \mathrm{MW}=10^6\ \mathrm{W}$ y $1\ \mathrm{GW}=10^9\ \mathrm{W}$. Mantener 1 kW durante una hora consume 1 kWh.

TGP referencia una tarjeta; TDP guía diseño térmico y varía por fabricante. La potencia **AC en la pared** añade componentes y pérdidas. No son equivalentes.

**DERIVED (escenario, no consumo medido):** 575 W sostenidos durante una hora equivalen a **0.575 kWh** para la tarjeta. El host y las pérdidas quedan fuera. La duración transforma una tasa en energía.

| Término | Responde | Ejemplo correcto | No significa |
|---|---|---|---|
| W | Potencia en un instante | Una tarjeta opera cerca de 575 W | Energía anual |
| Wh o kWh | Potencia integrada en tiempo | 100 W × 10 h = 1 kWh | Potencia máxima |
| TDP | Referencia térmica del fabricante | Dimensionar enfriamiento de un chip | Consumo exacto de pared |
| TGP | Potencia de la tarjeta gráfica | RTX 5090 de referencia: 575 W | Consumo del servidor |
| Pared AC | Sistema completo y pérdidas | Medidor del enchufe durante una tarea | Potencia exclusiva del chip |

### Escalas conocidas para construir intuición

| Equipo o aparato | Potencia orientativa | Duración de ejemplo | Energía derivada |
|---|---:|---:|---:|
| Foco LED | 8–12 W | 5 h | 0.04–0.06 kWh |
| SoC/CPU móvil | 5–30 W | 8 h | 0.04–0.24 kWh |
| Laptop completa | 30–100 W | 8 h | 0.24–0.80 kWh |
| Refrigerador, mientras comprime | 100–300 W | Ciclos, no 24 h continuas | Depende del ciclo |
| CPU de escritorio | 65–250 W | 2 h | 0.13–0.50 kWh |
| RTX 5090, TGP | hasta 575 W | 1 h | hasta 0.575 kWh |
| Microondas | 1–1.8 kW | 10 min | 0.17–0.30 kWh |
| Aire acondicionado | 1–5 kW | 6 h | 6–30 kWh |
| Rack GB300 NVL72 | hasta 142 kW | 1 día | hasta 3.408 MWh |
| Centro de datos | MW–GW | 1 año | potencia × 8,760 h |

**FACT** identifica especificaciones publicadas de RTX 5090 y GB300. **ESTIMATE (confianza media)** identifica rangos ilustrativos de aparatos: modelo, clima, ciclo y carga cambian el consumo. **DERIVED** identifica las multiplicaciones de potencia por tiempo. Un refrigerador es el recordatorio importante: su potencia activa no permanece constante todo el día.

La comparación incluye un foco LED, un microondas y un aire acondicionado para anclar las escalas; no implica que sus perfiles de uso sean iguales a los de un chip.

## El power wall cambió la estrategia

**FACT (síntesis histórica):** durante décadas, reducir el tamaño de los transistores permitió elevar frecuencia sin aumentar igual la densidad de potencia. Al fallar ese escalamiento de voltaje, cerca de 2005, calor y potencia limitaron la frecuencia. La respuesta combinó multicore, SIMD, aceleradores y eficiencia.

El **power wall** cambió el progreso: más transistores no implican activarlos todos al máximo. Software, paralelismo y especialización deciden cuánto hardware resulta útil.

![Interior de un nodo de TSUBAME 4.0 con cuatro GPU NVIDIA H100, tuberías de refrigeración y módulos de memoria.](../_assets/real-tsubame4-node.webp)

**FACT (objeto fotografiado):** nodo de TSUBAME 4.0 con cuatro GPU NVIDIA H100. La foto ilustra un nodo multi-GPU, no un sistema GB300 actual. Foto de [Fukumoto en Wikimedia Commons](https://commons.wikimedia.org/wiki/File:TSUBAME4.0_P5160984.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0); redimensionada y convertida a WebP para el curso.

## Del dispositivo a la generación

La escala encadena dispositivo en W, rack en kW y centro de datos en MW. Cada nivel añade red, almacenamiento, enfriamiento, conversión y redundancia.

**FACT (capacidad máxima, no consumo observado):** NVIDIA documenta que un rack GB300 NVL72 integra 72 GPU y 36 CPU, usa refrigeración líquida y requiere hasta **142 kW**. **DERIVED (escenario de placa):** 142 kW constantes durante 24 horas serían **3.408 MWh**; durante 8,760 horas serían **1.244 GWh**. El cálculo supone carga constante y excluye infraestructura exterior al rack.

En el nivel global se acumula energía, no sólo potencia. **ESTIMATE (IEA 2026, proyección central):** el consumo eléctrico de centros de datos pasa de **485 TWh en 2025** a alrededor de **950 TWh en 2030**; dentro de esa proyección, el consumo de centros enfocados en IA se triplica. Son estimaciones con incertidumbre, no lecturas de medidor ni potencia instantánea.

Escalar amplifica movimiento, refrigeración y energía. Sigue [[ia-escala-decision|IA, escala y selección de hardware]].

## Qué debes recordar

- Roofline compara dos techos: datos que memoria puede entregar y operaciones que el chip puede ejecutar.
- FLOP es trabajo; FLOPS es tasa; FLOP/byte mide reutilización.
- Pico teórico, benchmark y aplicación observada son evidencias distintas.
- W mide potencia; Wh y kWh miden energía acumulada. Siempre declara frontera y duración.

## Fuentes

- [Berkeley Lab — Roofline Performance Model](https://amcr.lbl.gov/departments/computer-science-department/ppan/roofline-performance-model/): intensidad, ancho de banda y techo de cómputo.
- [NVIDIA — RTX Blackwell GPU Architecture](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf): TGP, precisión y calificadores dense/sparse de la RTX 5090.
- [Google Cloud — TPU7x Ironwood](https://docs.cloud.google.com/tpu/docs/tpu7x): picos por precisión y HBM oficiales.
- [MLCommons — MLPerf Inference: Datacenter](https://mlcommons.org/benchmarks/inference-datacenter/): escenarios, calidad y medición AC del sistema completo.
- [BIPM — The International System of Units](https://www.bipm.org/en/publications/si-brochure): watt, prefijos SI y relación entre potencia y energía.
- [Microsoft Research — Dark silicon and the end of multicore scaling](https://www.microsoft.com/en-us/research/publication/dark-silicon-and-the-end-of-multicore-scaling/): escalamiento de Dennard y límite de potencia.
- [NVIDIA — NVL72 AI Factory, System Hardware and Components](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html): composición, refrigeración y potencia máxima del rack GB300 NVL72.
- [IEA — Key Questions on Energy and AI, executive summary (2026)](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary): proyección central 2025–2030 para electricidad de centros de datos y centros enfocados en IA, CC BY 4.0.
- [Wikimedia Commons — Palit GeForce RTX 5090 GameRock](https://commons.wikimedia.org/wiki/File:Palit_GeForce_RTX_5090_Gamerock_20250530_HOF3973-HDR_RAW-Export.png): fotografía de PantheraLeo1359531, CC BY 4.0.
- [Wikimedia Commons — TSUBAME 4.0](https://commons.wikimedia.org/wiki/File:TSUBAME4.0_P5160984.jpg): fotografía de Fukumoto, CC BY-SA 4.0.
