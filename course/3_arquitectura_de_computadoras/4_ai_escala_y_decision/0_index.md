---
id: ia-escala-decision
title: "IA, escala y selección de hardware"
nav_title: "IA, escala y decisión"
summary: "Cómo presupuestar memoria, comunicación y operación antes de elegir hardware para IA."
status: ready
estimated_time: "55 minutos"
tags: [ia, memoria, escalamiento, hardware]
---

Un modelo de IA transforma entradas con parámetros. El hardware aloja y mueve su estado para cumplir latencia, throughput, energía y costo. **Los parámetros inician el presupuesto, no lo completan.**

**Glosario breve.** **HBM** es memoria de alto ancho de banda junto al acelerador. **TDP** es una envolvente térmica de diseño; **TGP**, la potencia total de una tarjeta gráfica. **CAPEX** es gasto de adquisición. **MFU** mide la fracción de FLOP del modelo frente a un pico declarado. **SLA** es un compromiso de nivel de servicio; **OOM**, un fallo por memoria insuficiente. **TP**, **PP** y **DP** son paralelismo tensorial, de pipeline y de datos: parten tensores, etapas o réplicas y cambian comunicación y memoria local. **TTFT** es el tiempo hasta el primer token.

La ruta principal ocupa 50–55 minutos; la consulta de evidencia y los ejercicios de extensión son opcionales dentro de una sesión total de 90 minutos.

## Ejemplo de juguete: diez parámetros

Un **parámetro** es un número aprendido. Imagina este modelo diminuto:

`[0.2, -0.7, 1.1, 0.0, 0.4, -0.3, 0.8, 0.5, -0.1, 0.9]`

Hay diez parámetros. Un **bit** puede valer 0 o 1; ocho bits forman un **byte**. Si cada número se guarda con 32 bits, ocupa 4 bytes porque $32\div8=4$. Los diez pesan $10\times4=40$ bytes. Con 16 bits pesan 20 bytes; con 8 bits, 10 bytes; con 4 bits, 5 bytes.

![Cinco representaciones del mismo conjunto de parámetros muestran que FP32 usa cuatro bytes por parámetro, BF16 dos, FP8 e INT8 uno e INT4 medio byte en promedio.](../_assets/precision-parametros.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** reducir bits reduce el almacenamiento de los pesos. No garantiza la misma calidad ni reduce automáticamente cachés, activaciones o temporales.

| Unidad | Cantidad exacta usada aquí | Intuición |
|---|---:|---|
| bit | 0 o 1 | La unidad mínima |
| byte | 8 bits | La unidad habitual de almacenamiento |
| GB | $10^9$ bytes | Convención decimal de fichas comerciales |
| GiB | $2^{30}$ bytes | Convención binaria frecuente en software |

**DERIVED:** 14 GB decimales equivalen a unos 13.04 GiB. No desapareció memoria; cambió la unidad.

## Inferencia y entrenamiento ocupan memoria distinta

![Comparación categórica: inferencia usa pesos, caché KV y temporales; entrenamiento añade activaciones, gradientes y estados del optimizador.](../_assets/memoria-ai.svg)

*Diagrama propio del curso, SVG accesible, 2026. Los bloques nombran componentes; sus tamaños no están a escala.*

**Lectura visual:** inferencia necesita pesos, caché KV y temporales. Entrenamiento añade activaciones, gradientes y estados del optimizador. El runtime reserva otros buffers.

En **inferencia**, *prefill* procesa el prompt y *decode* produce tokens reutilizando la **caché KV**. Evita recalcular la historia, pero ocupa memoria.

![Prefill procesa muchos tokens del prompt en paralelo y llena la caché KV; decode reutiliza esa caché y genera un token por paso.](../_assets/prefill-decode.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

| Fase | Entrada por paso | Trabajo dominante | Sensible a |
|---|---|---|---|
| Prefill | Muchos tokens del prompt | Cálculo matricial y creación de KV | Longitud del prompt, FLOP/s |
| Decode | Un token nuevo por secuencia | Leer pesos y KV repetidamente | Ancho de banda, batch, contexto |

**Ejemplo de juguete:** cuatro personas envían 1,000 tokens y piden 100 nuevos. Prefill absorbe 4,000 tokens de entrada; decode realiza 100 pasos por solicitud. Agruparlas puede aprovechar el chip, pero mantiene cuatro cachés KV y puede hacer esperar a la primera persona.

Más **contexto** aumenta caché KV y atención; suele empeorar latencia y throughput por solicitud. El máximo admitido no indica cuántas peticiones caben.

El **batching** agrupa secuencias: puede elevar throughput, pero consume memoria y suma espera. Contexto y batch se ajustan por separado con solicitudes reales.

En **entrenamiento**, *forward* crea activaciones, *backward* gradientes y el optimizador actualiza parámetros. *Recomputation* cambia memoria por cálculo. Partir estados reduce memoria local, pero obliga a comunicarlos.

## La cuenta mínima de los pesos

Primero definimos cada símbolo:

| Símbolo | Significado | Unidad |
|---|---|---|
| $N_p$ | número de parámetros del modelo | parámetros |
| $b$ | bits usados por cada parámetro | bits/parámetro |
| $M_{pesos}$ | memoria total ocupada sólo por los pesos | bytes |

### Por qué dividimos entre ocho

La precisión suele expresarse en **bits**, pero la memoria se cuenta en **bytes**. La conversión es:

`8 bits = 1 byte`

Por eso dividimos los bits entre ocho:

| Precisión | Bits por parámetro | Cuenta | Bytes por parámetro |
|---|---:|---:|---:|
| FP32 | 32 bits | `32 ÷ 8 = 4 bytes` | 4 bytes |
| BF16 | 16 bits | `16 ÷ 8 = 2 bytes` | 2 bytes |
| INT8 | 8 bits | `8 ÷ 8 = 1 byte` | 1 byte |
| INT4 | 4 bits | `4 ÷ 8 = 0.5 byte` | 0.5 byte en promedio |

Ahora usemos diez parámetros FP32:

`10 parámetros × 4 bytes = 40 bytes`

La fórmula general sólo abrevia esa misma cuenta. Primero convierte $b$ bits a bytes con $b\div8$; después multiplica por los $N_p$ parámetros:

$$M_{pesos}=N_p\times\frac{b}{8}$$

Se lee así: **memoria de los pesos = cantidad de parámetros × bytes por parámetro**.

> [!IMPORTANT]
> **Cuatro bytes describen el contenido numérico FP32, no el tamaño total de cualquier objeto que contenga ese número.** La fórmula calcula un mínimo lógico de los pesos. La representación usada por el lenguaje, el contenedor y el runtime puede añadir memoria.

| Representación | Contenido numérico | Memoria adicional |
|---|---|---|
| Valor FP32 almacenado directamente | 4 bytes | Depende del formato o contenedor |
| Un objeto `float` de Python | Python no exige FP32; en CPython guarda un `double` de C | Cabecera del objeto, tipo, referencias y alineación |
| Arreglo NumPy `float32` | 4 bytes por elemento en el buffer | Objeto del arreglo, dimensiones, *strides*, tipo y posible alineación |
| Tensor `float32` | 4 bytes por elemento en su almacenamiento | Cabecera y metadatos, asignador, alineación y buffers del runtime o dispositivo |

Por eso `10 × 4 = 40 bytes` responde cuánto pesa el **payload** FP32 de diez parámetros, no cuánto ocupa una lista de diez objetos Python. En Python, `sys.getsizeof` aplicado a `1.0` informa el tamaño directo de ese objeto en esa implementación; no convierte al objeto en FP32 ni suma automáticamente objetos referenciados. Para NumPy, `array.nbytes` cuenta los bytes consumidos por los elementos, no toda la cabecera del arreglo.

**FACT (convención decimal):** en nombres como 7B, B representa $10^9$ parámetros y T representa $10^{12}$. En tamaños de almacenamiento, GB y TB también se usan aquí en escala decimal.

**DERIVED (GB decimales, sólo pesos):**

- **7B:** BF16 = $7\times10^9\times2$ bytes = **14 GB**; INT8 = **7 GB**; INT4 = **3.5 GB**.
- **70B:** BF16 = **140 GB**; INT8 = **70 GB**; INT4 = **35 GB**.
- **1T:** BF16 = **2 TB**; INT8 = **1 TB**; INT4 = **0.5 TB**.

Son capacidades lógicas. GiB, escalas, *padding*, buffers y particionado cambian la memoria física.

| Escala | Pesos por precisión |
|---:|---|
| 10 parámetros | BF16: 20 B · INT8: 10 B · INT4: 5 B. Juguete visible. |
| 7B | BF16: 14 GB · INT8: 7 GB · INT4: 3.5 GB. Puede caber en una GPU, según overhead. |
| 70B | BF16: 140 GB · INT8: 70 GB · INT4: 35 GB. Exige más capacidad o particionado. |
| 1T | BF16: 2 TB · INT8: 1 TB · INT4: 0.5 TB. Escala de servidor o cluster. |

**DERIVED (presupuesto base de esta receta):** *mixed precision* con Adam clásico suma **~18 bytes por parámetro**: 2 de pesos BF16/FP16 + 4 de copia FP32 + 4 de gradiente FP32 + 8 de estados Adam FP32. Para 7B, 70B y 1T son **126 GB**, **1.26 TB** y **18 TB** de estado agregado del modelo, antes de activaciones y temporales.

No obliga a guardar 18 bytes completos en cada GPU. El **sharding** reparte estado y reduce memoria local a cambio de comunicación y buffers. Precisión, activaciones, temporales e implementación cambian el máximo real.

## Cuantizar cambia más que capacidad

![Barras comparan el almacenamiento de un modelo de 7B parámetros: FP32 usa 28 GB, BF16 14 GB, FP8 e INT8 7 GB e INT4 3.5 GB.](../_assets/precision-parametros.svg)

**Lectura visual:** cada reducción a la mitad de bits reduce a la mitad el piso de pesos. Las barras no incluyen KV, runtime ni calidad numérica.

Cuantizar pesos reduce bytes y tráfico, pero exige soporte y validación numérica; INT4 no duplica necesariamente la velocidad de INT8.

Cuantizar pesos no reduce automáticamente caché KV ni activaciones. Valida precisión, contexto, batch y calidad en el hardware real.

## Denso y MoE no cuentan lo mismo

Un modelo **denso** usa todos sus parámetros en cada token. Un **Mixture of Experts**, o **MoE**, contiene varios bloques expertos y un router selecciona algunos para cada token. Por eso se reportan dos cantidades:

- **Parámetros totales:** capacidad que debe almacenarse o repartirse.
- **Parámetros activos:** parte aproximada usada para procesar un token.

![Un modelo denso activa todos sus bloques; un modelo MoE almacena muchos expertos pero un router activa sólo dos para cada token.](../_assets/dense-moe.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** el modelo MoE conserva todos los expertos en memoria, mientras la ruta resaltada atraviesa sólo los elegidos para ese token.

**Ejemplo de juguete:** ocho expertos de 10 parámetros suman 80 almacenados. Si el router usa dos, activa 20 por token. Eso reduce cálculo frente a usar 80, pero no reduce el almacenamiento a 20; además añade ruteo y comunicación.

## Distribuir crea una segunda carga

Distribuir añade una segunda carga:

- **Paralelismo de datos:** replica el modelo y divide batches. En entrenamiento, **all-reduce** combina y redistribuye gradientes; en inferencia, réplicas atienden solicitudes distintas.
- El **paralelismo de modelo** es el paraguas para dividir un modelo entre dispositivos. Sus formas incluyen tensor y pipeline.
- **Paralelismo tensorial:** parte tensores de cada capa; colectivas como all-reduce o all-gather exigen enlaces rápidos.
- **Paralelismo de pipeline:** reparte grupos de capas; envía activaciones y puede crear burbujas.

Bandwidth, latencia y topología determinan el resultado. **Más dispositivos no prometen speedup lineal.**

## Del chip al centro de datos

![Escala de decisión: primero medir si limita memoria, cómputo o red; después pasar de equipo a servidor y cluster, aceptando más coordinación.](../_assets/escala-decision.svg)

*Diagrama propio del curso, SVG accesible, 2026.*

**Lectura visual:** primero se mide memoria, cómputo y comunicación; después se escala. Cada salto añade capacidad, coordinación, fallas y energía.

La cadena es **chip → board → servidor → rack → cluster → centro de datos**. Cada nivel añade memoria, red, potencia, refrigeración y operación.

| Escala | Lo que agrega | Nuevo límite posible |
|---|---|---|
| Chip | Unidades y memoria local | Capacidad o bandwidth local |
| Servidor | Varios chips y enlaces | PCIe/NVLink, CPU, alimentación |
| Rack | Decenas de aceleradores | Red interna y refrigeración |
| Cluster | Muchos racks | Colectivas, fallas y almacenamiento |
| Centro de datos | Energía e infraestructura | Red eléctrica, agua, operación |

**Sharding** reparte un tensor o estado entre dispositivos. Permite que algo grande quepa, pero cada capa puede necesitar intercambios. Si duplicar chips reduce a la mitad el cálculo local y duplica la espera de red, el tiempo total no se reduce a la mitad.

## Cuatro ejemplos representativos, no un ranking

- **FACT (límite de producto):** M5 Max admite hasta **128 GB unificados** y **614 GB/s**; no son benchmark ni TDP.
- **FACT (referencia NVIDIA):** RTX 5090 tiene **32 GB GDDR7**, **1,792 GB/s de ancho de banda pico de memoria** y **575 W TGP**. Pesos, cachés y temporales comparten capacidad; tarjetas de ensambladores pueden variar.
- **FACT (picos por chip):** TPU7x ofrece **192 GiB HBM**, **7,380 GB/s**, **2,307 TFLOP/s BF16** y **4,614 TFLOP/s FP8**; un pod llega a **9,216 chips**. No es desempeño observado.
- **FACT (sistema oficial, máximos agregados):** DGX GB300 integra **72 GPU Blackwell Ultra**, **36 CPU Grace**, **20 TB de memoria GPU**, hasta **576 TB/s** HBM y **130 TB/s NVLink**. El rack usa refrigeración líquida y admite hasta **142 kW**; es capacidad máxima, no consumo medido.

No son un ranking: la aplicación y la medición completa deciden.

## Costo físico del hardware

Aquí **costo** significa compra equivalente de hardware dentro de una frontera declarada. No es el costo total de crear u operar un modelo. Una cifra sin estado e ID no entra en las tablas.

La etiqueta dice qué sabemos: **FACT** fue publicado por la fuente responsable; **DERIVED** es una cuenta reproducible; **SCENARIO** es un supuesto docente; **NOT_FOUND** registra una búsqueda sin resultado; y **ESTIMATION_NOT_IDENTIFIABLE** indica que faltan observables para defender un rango. El ID permite volver al registro y a sus fuentes. **Confianza** no sustituye esa trazabilidad.

### De un acelerador a una cuenta visible

Tomemos un módulo NVIDIA H100 SXM con 80 GB de HBM física, pico aproximado de 989.5 TFLOP/s BF16 tensorial denso, acumulación FP32, derivado del pico sparse dividido entre dos, y TDP configurable de 700 W. Esas especificaciones pertenecen al módulo, no al servidor: **FACT** para HBM y potencia, **DERIVED** para la tasa densa; `H_NVIDIA_H100_SXM_80GB`, `S_NVIDIA_H100_PAGE`.

Supongamos ocho módulos. La cantidad y el precio unitario son **SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`, `S_COURSE_DESIGN`.

- HBM física: `8 × 80 GB = 640 GB` (**DERIVED** desde cantidad **SCENARIO** y especificación **FACT**; `D_H100_8X_24H`, `H_NVIDIA_H100_SXM_80GB`).
- Pico: `8 × 989.5 TFLOP/s = 7,916 TFLOP/s` aproximados (**DERIVED**; BF16 tensorial, dense, acumulación FP32; `D_H100_8X_24H`).
- Base de potencia: `8 × 700 W = 5,600 W` de TDP configurable (**DERIVED**; no es una medición; `D_H100_8X_24H`).
- Trabajo asignado: `8 × 24 h = 192 H100-h` (**DERIVED**; `D_H100_8X_24H`); los accelerator-hours no son energía.
- Energía bajo esa envolvente: `5.6 kW × 24 h = 134.4 kWh` (**SCENARIO**, no energía medida; `D_H100_8X_24H`).
- CAPEX `accelerator-only`: `8 × USD 30,000 = USD 240,000` (**DERIVED** desde precio unitario **SCENARIO**; `D_H100_8X_24H`, `V_H100_30K_DIDACTIC_SCENARIO`). Compra ocho módulos hipotéticos con su HBM incorporada; excluye servidor, CPU, RAM, chasis, red, almacenamiento, envío, impuestos y soporte.

El puente de potencia a energía conserva las unidades: `1,000 W = 1 kW`, `1,000 kW = 1 MW` y `kW × h = kWh`. En el escenario matemático, sostener 5.6 kW durante 24 h daría 134.4 kWh (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`); afirmar consumo real requeriría potencia medida durante el intervalo. Los 192 H100-module-hours sólo describen asignación de hardware y no se renombran kWh.

La cuenta general aparece después del ejemplo:

`HBM física instalada = aceleradores × HBM física por acelerador`

`pico teórico homogéneo = aceleradores × FLOP/s pico por acelerador`

`base de potencia de aceleradores = aceleradores × W de la misma base por acelerador`

`accelerator-hours = aceleradores asignados promedio × horas calendario`

`CAPEX accelerator-only = aceleradores × precio de la unidad transable`

Dos preguntas evitan sobreinterpretar la suma. ¿Los 640 GB demuestran que hay 640 GB disponibles para una sola copia del modelo? No: **HBM física no es HBM utilizable**; faltan particionado, réplicas, estados y reserva del runtime (**ESTIMATION_NOT_IDENTIFIABLE**; `H_NVIDIA_H100_SXM_80GB`). ¿Los 7,916 TFLOP/s demuestran cuánto trabajo terminó? No: **FLOP es trabajo** y **FLOP/s es una tasa**; faltan utilización y medición sostenida.

### Casos con hardware documentado

La comparación esencial incluye sólo alcances cuyo creador publicó tipo y cantidad concurrente de aceleradores, más accelerator-hours o duración para el mismo entrenamiento. Se divide en dos subtablas estrechas para conservar la fila como unidad de lectura en móvil.

| Modelo y alcance | Hardware concurrente | Accelerator-hours |
|---|---|---|
| BLOOM 176B, corrida completa (**FACT**; `M_BLOOM_176B`, `T_BLOOM_176B_TRAINING`) | 384 GPU A100 SXM 80 GB (**FACT**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_BIGSCIENCE_BLOOM_CARD`) | 1,082,990 A100 GPU-h (**FACT**; `S_BIGSCIENCE_BLOOM_CARBON`) |
| PaLM 540B, entrenamiento (**FACT**; `M_PALM_540B`, `T_PALM_540B_PRETRAINING`) | pico de 6,144 chips TPU v4 (**FACT**; `S_GOOGLE_PALM_PAPER`) | 8,404,992 TPU-v4-chip-h asignadas (**DERIVED**; `S_GOOGLE_PALM_PAPER`) |
| Llama 3.1 405B, preentrenamiento (**FACT**; `M_LLAMA31_405B`, `T_LLAMA31_405B_PRETRAINING`) | pico de 16,384 GPU H100 80 GB (**FACT**; `S_META_LLAMA31_PAPER`, `S_META_LLAMA31_CARD`) | 30,840,000 H100 GPU-h (**FACT**; `S_META_LLAMA31_CARD`) |
| DeepSeek-V3, preentrenamiento (**FACT**; `M_DEEPSEEK_V3`, `T_DEEPSEEK_V3_PRETRAINING`) | 2,048 GPU H800 80 GB (**FACT**; `S_DEEPSEEK_V3_PAPER`) | 2,664,000 H800 GPU-h (**FACT**; `S_DEEPSEEK_V3_PAPER`) |

#### Escala física y frontera económica

| Modelo y alcance | HBM física instalada | Base de potencia de aceleradores | CAPEX/base |
|---|---|---|---|
| BLOOM 176B, corrida completa (**FACT**; `M_BLOOM_176B`, `T_BLOOM_176B_TRAINING`) | 30,720 GB HBM2e (**DERIVED**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_NVIDIA_A100_DATASHEET`) | 153,600 W, suma de TDP estándar (**DERIVED**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_NVIDIA_A100_DATASHEET`) | **ESTIMATION_NOT_IDENTIFIABLE**; `T_BLOOM_176B_TRAINING` |
| PaLM 540B, entrenamiento (**FACT**; `M_PALM_540B`, `T_PALM_540B_PRETRAINING`) | 196,608 GiB HBM2 en el pico (**DERIVED**; `S_GOOGLE_PALM_PAPER`, `S_GOOGLE_TPU_V4_DOCS`) | 1,179,648 W, suma de máximos medidos por chip (**DERIVED**; `S_GOOGLE_PALM_PAPER`, `S_GOOGLE_TPU_V4_DOCS`) | **ESTIMATION_NOT_IDENTIFIABLE**; `T_PALM_540B_PRETRAINING` |
| Llama 3.1 405B, preentrenamiento (**FACT**; `M_LLAMA31_405B`, `T_LLAMA31_405B_PRETRAINING`) | 1,310,720 GB HBM en el pico (**DERIVED**; `S_META_LLAMA31_PAPER`, `S_NVIDIA_H100_PAGE`) | 11,468,800 W, suma de TDP configurables (**DERIVED**; `S_META_LLAMA31_PAPER`, `S_NVIDIA_H100_PAGE`) | **ESTIMATION_NOT_IDENTIFIABLE**; `T_LLAMA31_405B_PRETRAINING` |
| DeepSeek-V3, preentrenamiento (**FACT**; `M_DEEPSEEK_V3`, `T_DEEPSEEK_V3_PRETRAINING`) | 163,840 GB HBM física (**DERIVED**; `S_DEEPSEEK_V3_PAPER`, `S_NVIDIA_H800_RELEASE_NOTES`) | **ESTIMATION_NOT_IDENTIFIABLE**; `T_DEEPSEEK_V3_PRETRAINING` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_DEEPSEEK_V3_PRETRAINING` |

![Escala logarítmica de aceleradores concurrentes: BLOOM 176B, 384 aceleradores [FACT]; PaLM 540B, 6,144 aceleradores [FACT]; Llama 3.1 405B, 16,384 aceleradores [FACT]; DeepSeek-V3, 2,048 aceleradores [FACT].](../_assets/ai-aceleradores-entrenamiento.svg)

*Diagrama propio generado desde el ledger del curso, SVG accesible, 2026.*

**Lectura visual:** la distancia horizontal es multiplicativa. Cada marca conserva el caso y estado de su celda; las cantidades no conectan modelos como una serie temporal.

| Modelo | Aceleradores concurrentes | Estado y evidencia |
|---|---:|---|
| BLOOM 176B | 384 | **FACT**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_BIGSCIENCE_BLOOM_CARD` |
| PaLM 540B | 6,144 | **FACT**; `S_GOOGLE_PALM_PAPER` |
| Llama 3.1 405B | 16,384 | **FACT**; `S_META_LLAMA31_PAPER` |
| DeepSeek-V3 | 2,048 | **FACT**; `S_DEEPSEEK_V3_PAPER` |

![HBM física instalada posicionada en bytes canónicos y etiquetada en la unidad nativa: BLOOM 176B, 30,720 GB [DERIVED]; PaLM 540B, 196,608 GiB [DERIVED]; Llama 3.1 405B, 1,310,720 GB [DERIVED]; DeepSeek-V3, 163,840 GB [DERIVED]. HBM utilizable no es identificable y no se grafica.](../_assets/ai-hbm-entrenamiento.svg)

*Diagrama propio generado desde el ledger del curso, SVG accesible, 2026.*

**Lectura visual:** la posición convierte GB o GiB a bytes para compararlos; la etiqueta conserva la unidad publicada. Sólo representa HBM física instalada en el pico concurrente, no HBM utilizable.

| Modelo | HBM física instalada | Unidad conservada | Estado y evidencia |
|---|---:|---|---|
| BLOOM 176B | 30,720 | GB | **DERIVED**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_NVIDIA_A100_DATASHEET` |
| PaLM 540B | 196,608 | GiB | **DERIVED**; `S_GOOGLE_PALM_PAPER`, `S_GOOGLE_TPU_V4_DOCS` |
| Llama 3.1 405B | 1,310,720 | GB | **DERIVED**; `S_META_LLAMA31_PAPER`, `S_NVIDIA_H100_PAGE` |
| DeepSeek-V3 | 163,840 | GB | **DERIVED**; `S_DEEPSEEK_V3_PAPER`, `S_NVIDIA_H800_RELEASE_NOTES` |

![Bases de potencia no equivalentes en paneles separados: BLOOM 176B usa TDP estándar · envolvente, 153.6 kW [DERIVED]; PaLM 540B usa máximo medido · observación, 1.18 MW [DERIVED]; Llama 3.1 405B usa TDP configurable · envolvente, 11.47 MW [DERIVED]; DeepSeek-V3 usa base no identificable, sin valor identificable [ESTIMATION_NOT_IDENTIFIABLE].](../_assets/ai-potencia-hardware.svg)

*Diagrama propio generado desde el ledger del curso, SVG accesible, 2026.*

**Lectura visual:** el panel GPU/chip-only muestra sumas nominales comparables sólo en magnitud. El panel servidor/IT queda separado y sin puntos porque el ledger no identifica ese total; nunca se suma la parte al sistema que ya la contiene.

| Base | Modelo | Valor del ledger | Estado y evidencia |
|---|---|---:|---|
| TDP estándar | BLOOM 176B | 153,600 W | **DERIVED**; `S_BIGSCIENCE_BLOOM_PAPER`, `S_NVIDIA_A100_DATASHEET` |
| Máximo medido | PaLM 540B | 1,179,648 W | **DERIVED**; `S_GOOGLE_PALM_PAPER`, `S_GOOGLE_TPU_V4_DOCS` |
| TDP configurable | Llama 3.1 405B | 11,468,800 W | **DERIVED**; `S_META_LLAMA31_PAPER`, `S_NVIDIA_H100_PAGE` |
| No identificada | DeepSeek-V3 | No identificable | **ESTIMATION_NOT_IDENTIFIABLE**; `T_DEEPSEEK_V3_PRETRAINING` |

El panel servidor/IT no tiene una fila cuantitativa: no existe un valor correspondiente en el ledger aprobado.

Las bases de potencia no forman una sola serie: TDP estándar, máximo medido y TDP configurable responden preguntas distintas. Tampoco se suma potencia de aceleradores a una potencia de servidor que ya los contenga.

La HBM utilizable es **ESTIMATION_NOT_IDENTIFIABLE** en cada caso documentado; IDs `T_BLOOM_176B_TRAINING`, `T_PALM_540B_PRETRAINING`, `T_LLAMA31_405B_PRETRAINING` y `T_DEEPSEEK_V3_PRETRAINING`. La HBM física agregada no revela TP, PP, DP, réplicas, shards ni reserva del runtime. GB y GiB permanecen separados.

#### Ledger visible: escala del modelo y trabajo

Estas subtablas conservan detalles que volverían ilegible la comparación esencial. FLOP nombra trabajo de entrenamiento; TFLOP/s, mostrado arriba, nombra una tasa pico.

| Modelo/alcance | Parámetros y tokens | Precisión |
|---|---|---|
| BLOOM 176B (**FACT**; `M_BLOOM_176B`, `T_BLOOM_176B_TRAINING`) | 176.247B parámetros y 366B tokens (**FACT**; `S_BIGSCIENCE_BLOOM_PAPER`) | bfloat16 mixta (**FACT**; `S_BIGSCIENCE_BLOOM_PAPER`) |
| PaLM 540B (**FACT**; `M_PALM_540B`, `T_PALM_540B_PRETRAINING`) | 540.35B parámetros y 780B tokens (**FACT**; `S_GOOGLE_PALM_PAPER`) | bfloat16 (**FACT**; `S_GOOGLE_PALM_PAPER`) |
| Llama 3.1 405B (**FACT**; `M_LLAMA31_405B`, `T_LLAMA31_405B_PRETRAINING`) | 405B parámetros y 15.6T tokens (**FACT**; `S_META_LLAMA31_PAPER`) | BF16 mixta (**FACT**; `S_META_LLAMA31_PAPER`) |
| DeepSeek-V3 (**FACT**; `M_DEEPSEEK_V3`, `T_DEEPSEEK_V3_PRETRAINING`) | 671B parámetros totales, 37B activos y 14.8T tokens (**FACT**; `S_DEEPSEEK_V3_PAPER`) | FP8 mixta con componentes de mayor precisión (**FACT**; `S_DEEPSEEK_V3_PAPER`) |

##### Trabajo publicado y utilización

| Modelo/alcance | FLOP de entrenamiento publicado | MFU | ID del caso |
|---|---|---|---|
| BLOOM 176B | **NOT_FOUND**; `T_BLOOM_176B_TRAINING` | **NOT_FOUND**; `T_BLOOM_176B_TRAINING` | `T_BLOOM_176B_TRAINING` |
| PaLM 540B | 2.56 × 10^24 FLOP (**FACT**; `S_GOOGLE_PALM_PAPER`) | 46.2 % (**FACT**; `S_GOOGLE_PALM_PAPER`) | `T_PALM_540B_PRETRAINING` |
| Llama 3.1 405B | 3.8 × 10^25 FLOP (**FACT**; `S_META_LLAMA31_PAPER`) | 38–43 % (**FACT**; `S_META_LLAMA31_PAPER`) | `T_LLAMA31_405B_PRETRAINING` |
| DeepSeek-V3 | **NOT_FOUND**; `T_DEEPSEEK_V3_PRETRAINING` | **NOT_FOUND**; `T_DEEPSEEK_V3_PRETRAINING` | `T_DEEPSEEK_V3_PRETRAINING` |

PaLM usó dos fases: `6,144 × 1,200 h + 3,072 × 336 h = 8,404,992 TPU-v4-chip-h` (**DERIVED**; `T_PALM_540B_PRETRAINING`, `S_GOOGLE_PALM_PAPER`). La cantidad concurrente del cuadro es el pico, no una cantidad constante. BLOOM duró 2,837.68 h de pared (**DERIVED**; `T_BLOOM_176B_TRAINING`, `S_BIGSCIENCE_BLOOM_CARBON`); Llama no publica duración suficiente para reconstruirla (**ESTIMATION_NOT_IDENTIFIABLE**; `T_LLAMA31_405B_PRETRAINING`). Accelerator-hours, FLOP publicado y MFU conservan cuentas publicadas, pero no se reconstruyen algebraicamente entre sí: cambian alcance, ventana, downtime, pasos repetidos y la convención de pico. GPU-h y TPU-chip-h no se convierten, suman ni presentan como equivalentes.

### Modelos actuales: hechos y límites

El corte es 2026-08-18 (**FACT**; `tools/data/ai_hardware_costs.yaml`). “No divulgado” o **NOT_FOUND** no autoriza rellenar huecos. Para entrenamientos cerrados, sin tipo, cantidad y tiempo compatibles, el resultado físico y económico es **ESTIMATION_NOT_IDENTIFIABLE**, no una banda inventada.

| Modelo vigente o artefacto | Lanzamiento y disponibilidad | Parámetros públicos |
|---|---|---|
| GPT-5.6 Sol (**FACT**; `M_GPT56_SOL`) | 2026-06-26, productos alojados sin pesos (**FACT**; `S_OPENAI_GPT56_ANNOUNCEMENT`, `S_OPENAI_GPT56_AVAILABILITY`) | **NOT_FOUND**; `T_GPT56_SOL_TRAINING_AUDIT` |
| Claude Sonnet 5 (**FACT**; `M_CLAUDE_SONNET5`) | 2026-06-30, productos alojados sin pesos (**FACT**; `S_ANTHROPIC_SONNET5_ANNOUNCEMENT`) | **NOT_FOUND**; `T_CLAUDE_SONNET5_TRAINING_AUDIT` |
| Gemini 3.1 Pro (**FACT**; `M_GEMINI31_PRO`) | 2026-02-19, vista previa alojada sin pesos (**FACT**; `S_GOOGLE_GEMINI31_CARD`, `S_GOOGLE_GEMINI31_PAGE`) | **NOT_FOUND**; `T_GEMINI31_PRO_TRAINING_AUDIT` |
| Kimi K3 (**FACT**; `M_KIMI_K3`) | 2026-07-16, pesos abiertos y servicio alojado (**FACT**; `S_MOONSHOT_KIMI_K3_BLOG`, `S_MOONSHOT_KIMI_K3_REPOSITORY`, `S_MOONSHOT_KIMI_K3_CARD`) | 2.8T totales y 104.2B activos (**FACT**; `S_MOONSHOT_KIMI_K3_PAPER`) |
| Qwen3.8-Max, servicio (**FACT**; `M_QWEN38_MAX_SERVICE`) | 2026-08-03, alojado en QwenCloud (**FACT**; `S_QWEN38_ANNOUNCEMENT`) | 2.4T totales y 95B activos (**FACT**; `S_QWEN38_ANNOUNCEMENT`) |
| Qwen3.8-2.4T-A95B, artefacto base (**FACT**; `M_QWEN38_2_4T_A95B`) | 2026-08-12, pesos abiertos en ModelScope (**FACT**; `S_QWEN38_MODELSCOPE`) | 2.4T totales y 95B activos (**FACT**; `S_QWEN38_MODELSCOPE`) |

| Modelo vigente o artefacto | Hardware y tiempo publicados | CAPEX atribuido |
|---|---|---|
| GPT-5.6 Sol | **NOT_FOUND**; `T_GPT56_SOL_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_GPT56_SOL_TRAINING_AUDIT` |
| Claude Sonnet 5 | **NOT_FOUND**; `T_CLAUDE_SONNET5_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_CLAUDE_SONNET5_TRAINING_AUDIT` |
| Gemini 3.1 Pro | **NOT_FOUND**; `T_GEMINI31_PRO_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_GEMINI31_PRO_TRAINING_AUDIT` |
| Kimi K3 | **NOT_FOUND**; `T_KIMI_K3_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_KIMI_K3_TRAINING_AUDIT` |
| Qwen3.8-Max, servicio | **NOT_FOUND**; `T_QWEN38_MAX_SERVICE_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_QWEN38_MAX_SERVICE_TRAINING_AUDIT` |
| Qwen3.8-2.4T-A95B, artefacto base | **NOT_FOUND**; `T_QWEN38_2_4T_A95B_TRAINING_AUDIT` | **ESTIMATION_NOT_IDENTIFIABLE**; `T_QWEN38_2_4T_A95B_TRAINING_AUDIT` |

Los parámetros verificables de un artefacto abierto permiten calcular un piso de pesos. No revelan por sí solos aceleradores concurrentes, duración, HBM utilizable, potencia observada ni precio de compra del entrenamiento real.

**Identidad y fechas.** Kimi K3 separa lanzamiento (2026-07-16), repositorio/model card y consulta (2026-08-18), pero el corpus no fija un commit o manifiesto inmutable: **NOT_FOUND** para identidad versionada, por lo que aquí no se afirma una revisión de artefacto. Qwen separa el servicio Qwen3.8-Max (lanzamiento 2026-08-03) del artefacto base observado en ModelScope, actualizado 2026-08-12 y consultado 2026-08-18; su manifiesto mínimo observado contiene índice, configuración y shards, pero la URL no fija hash inmutable. Evidencia: `M_KIMI_K3`, `S_MOONSHOT_KIMI_K3_REPOSITORY`, `M_QWEN38_2_4T_A95B`, `S_QWEN38_MODELSCOPE`.

**Fecha o intervalo del entrenamiento.** BLOOM: 2022-03-11 a 2022-07-06 (**FACT**; `S_BIGSCIENCE_BLOOM_CARBON`). DeepSeek-V3: menos de dos meses, sin fechas calendario (**FACT**, límite publicado; `S_DEEPSEEK_V3_PAPER`). GPT-3, PaLM, Llama 3.1, GPT-5.6 Sol, Claude Sonnet 5, Gemini 3.1 Pro, Kimi K3 y ambos registros Qwen: **NOT_FOUND** en el corpus de cada caso; no se sustituye por la fecha de lanzamiento.

### Escenarios equivalentes, no entrenamientos atribuidos

Un escenario responde “¿qué compraría bajo estos supuestos?”, no “¿qué costó entrenar el modelo?”. Por eso esta tabla no contiene nombres de modelos.

| Atribución | Hardware hipotético | Asignación | HBM física |
|---|---|---|---|
| Sin modelo atribuido (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) | 8 módulos H100 SXM 80 GB (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`; especificaciones `H_NVIDIA_H100_SXM_80GB`) | 192 H100-module-hours para 24 h (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) | 640 GB (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) |

| Atribución | Pico teórico y potencia nominal | CAPEX/base |
|---|---|---|
| Sin modelo atribuido (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) | 7,916 TFLOP/s BF16 denso y 5.6 kW de módulos (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) | USD 240,000, `accelerator-only` (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`) |

La valoración supone USD 30,000 por módulo, unidad transable “module”, cantidad mínima uno, condición nueva hipotética, fecha 2026-08-18 y base didáctica en USD (**SCENARIO**; `V_H100_30K_DIDACTIC_SCENARIO`). Incluye el módulo y su HBM; excluye los componentes enumerados en el ejemplo. No existe aquí una valoración `system-based`, y no se suma un sistema completo sobre estos módulos.

![CAPEX en fronteras y bases separadas: accelerator-only · supuesto docente 2026, USD 240,000 [DERIVED]; system-based · reposición 2026, sin precio identificable [ESTIMATION_NOT_IDENTIFIABLE].](../_assets/ai-capex-hardware.svg)

*Diagrama propio generado desde el ledger del curso, SVG accesible, 2026.*

**Lectura visual:** el punto es el total `8 × USD 30,000 = USD 240,000`; USD 30,000 sólo es el input unitario. La base `system-based` de reposición permanece sin punto porque falta una cotización persistente.

| Frontera y base | Unidad transable | Total graficado | Estado y evidencia |
|---|---|---:|---|
| accelerator-only · supuesto docente 2026 | 8 módulos H100 SXM a USD 30,000 c/u | USD 240,000 | **DERIVED**; `D_H100_8X_24H`, `S_COURSE_DESIGN` |
| system-based · reposición 2026 | Servidor | No identificable | **ESTIMATION_NOT_IDENTIFIABLE**; `V_THINKMATE_QH14_H100_REPLACEMENT_20260818`, `S_THINKMATE_HGX_H100_CONFIGURATOR` |

**Registro de valoración accelerator-only.** Fecha: 2026-08-18; geografía: base docente estadounidense; canal: supuesto docente; mínimo: un módulo; condición: nuevo hipotético; impuestos, envío, soporte, red y almacenamiento: excluidos. Incluye módulo H100 SXM y su HBM física. Estado del precio unitario: **SCENARIO**; estado del total para ocho: **DERIVED**. Evidencia: `V_H100_30K_DIDACTIC_SCENARIO`, `D_H100_8X_24H`, `S_COURSE_DESIGN`.

**Registro de valoración system-based histórica.** Corte: 2026-08-18; geografía: tienda en línea de Estados Unidos; canal: configurador del vendedor; unidad: servidor. Precio persistente, cantidad mínima, condición, impuestos, soporte, red, almacenamiento y componentes incluidos/excluidos: **ESTIMATION_NOT_IDENTIFIABLE** porque no hay URL parametrizada, cotización identificada ni captura persistente. No se reproduce ni completa una configuración Thinkmate. Evidencia: `V_THINKMATE_QH14_H100_REPLACEMENT_20260818`, `S_THINKMATE_HGX_H100_CONFIGURATOR`.

### Inferencia de capacidad: cabe, sin SLA

Dimensionar inferencia comienza por una cuenta de memoria, no por FLOP/s. El ejemplo usa el artefacto abierto y versionado `Qwen/Qwen2.5-32B-Instruct-GPTQ-Int8` en el commit `eddc13f573fd3648cc8a4741fdf1b70e8d6fc5c1`. Sus nueve shards suman 35,068,693,560 bytes y su configuración declara 32,763,876,352 parámetros, GPTQ de 8 bits con grupos de 128, 64 capas, 8 cabezas KV, hidden size 5,120 y 40 cabezas de atención; `5,120 ÷ 40 = 128` elementos por cabeza (**FACT** y **DERIVED**; `I_QWEN25_32B_GPTQ_INT8_CAPACITY`, `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`).

La etiqueta **cabe, sin SLA** es una evaluación **SCENARIO**: sólo significa que el presupuesto por componentes queda bajo la capacidad física elegida con estos supuestos. No demuestra ausencia de OOM, HBM utilizable, latencia o throughput. La cuenta se presenta como registro vertical para que cada componente conserve ancho legible en móvil.

| Dato | Valor | Estado y evidencia |
|---|---|---|
| Artefacto y revisión | Qwen2.5-32B-Instruct-GPTQ-Int8, `eddc13f…` | **FACT**; `I_QWEN25_32B_GPTQ_INT8_CAPACITY`, `S_QWEN25_32B_GPTQ_INT8_ARTIFACT` |
| Formato | GPTQ INT8, nueve shards `safetensors`; tensores I32/F16 | **FACT**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT` |
| Pesos | Piso uniforme 32.763876352 GB + diferencial de pesos/bias FP16 1.558254592 GB = 34.322130944 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT` |
| Escalas/metadata | Escalas FP16 0.487587840 GB + qzeros 0.243793920 GB + g_idx 0.014942208 GB + headers 0.000238648 GB = 0.746562616 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT` |
| Runtime | 4 GB, vLLM 0.7.1 | **SCENARIO**; `S_COURSE_DESIGN`, `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_VLLM_071_QUANTIZATION_HARDWARE` |
| KV | 9.663676416 GB para 16 × 2,304 tokens, FP16 | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` |
| Workspace | 4 GB | **SCENARIO**; `S_COURSE_DESIGN` |
| Reserva | 10 % = 5.27323699760 GB | **SCENARIO** y **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` |
| Total derivado | 58.00560697360 GB = 54.022 GiB | **DERIVED**; `I_QWEN25_32B_GPTQ_INT8_CAPACITY`, `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` |
| Evaluación: cabe, sin SLA | 58.00560697360 GB < 80 GB físicos | **SCENARIO**; `I_QWEN25_32B_GPTQ_INT8_CAPACITY`, `S_COURSE_DESIGN` |
| Sistema mínimo del corpus | 1 NVIDIA DGX H100 adquirido; TP=1, PP=1, DP=1, una réplica y un shard activo con 80 GB físicos por réplica/shard; los 16 contextos KV viven en ese shard | **SCENARIO**; `S_COURSE_DESIGN`, `S_NVIDIA_DGX_H100_DATASHEET` |
| Compatibilidad | Artefacto/vLLM/GPTQ/Hopper/DGX | `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_VLLM_071_QUANTIZATION_HARDWARE`, `S_NVIDIA_DGX_H100_DATASHEET` |
| HBM utilizable | No identificable con el corpus | **ESTIMATION_NOT_IDENTIFIABLE**; `I_QWEN25_32B_GPTQ_INT8_CAPACITY` |

![Piso de capacidad de inferencia para Qwen2.5-32B GPTQ Int8: Pesos y metadata, 35.069 GB [DERIVED]; Runtime, 4 GB [SCENARIO]; Caché KV, 9.664 GB [DERIVED]; Workspace, 4 GB [SCENARIO]; Reserva 10 %, 5.273 GB [DERIVED]; Total presupuestado, 58.006 GB [DERIVED]; Capacidad física por shard, 80 GB físicos [SCENARIO]; Mínimo adquirible, 1 NVIDIA DGX H100 [SCENARIO]. Cabe en capacidad física, sin afirmar SLA ni HBM utilizable.](../_assets/ai-inferencia-capacidad.svg)

*Diagrama propio generado desde el ledger del curso, SVG accesible, 2026.*

**Lectura visual:** el piso suma componentes por réplica y shard, luego compara 58.00560697360 GB presupuestados con 80 GB físicos. “Cabe” es una evaluación de capacidad; no demuestra HBM utilizable, ausencia de OOM, throughput, latencia ni SLA.

| Componente o límite | Valor del ledger | Estado y evidencia | Lectura |
|---|---:|---|---|
| Pesos y metadata | 35.068693560 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT` | Shards completos |
| Runtime | 4 GB | **SCENARIO**; `S_COURSE_DESIGN` | Presupuesto docente |
| Caché KV | 9.663676416 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` | Piso de payload para 16 contextos |
| Workspace | 4 GB | **SCENARIO**; `S_COURSE_DESIGN` | Presupuesto docente |
| Reserva 10 % | 5.27323699760 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` | Aplicada al subtotal |
| Total presupuestado | 58.00560697360 GB | **DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_COURSE_DESIGN` | Piso de capacidad |
| Capacidad física por shard | 80 GB | **SCENARIO**; `S_COURSE_DESIGN`, `S_NVIDIA_DGX_H100_DATASHEET` | No se renombra HBM utilizable |
| Mínimo adquirible | 1 NVIDIA DGX H100 | **SCENARIO**; `S_COURSE_DESIGN`, `S_NVIDIA_DGX_H100_DATASHEET`, `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_VLLM_071_QUANTIZATION_HARDWARE` | Topología completa del corpus |

La reconstrucción conserva cada sumando:

`piso uniforme = 32,763,876,352 parámetros × 8 bit/parámetro ÷ 8 bit/byte ÷ 1,000,000,000 byte/GB = 32.763876352 GB`

Los headers de `safetensors` permiten clasificar el diferencial de 2.304817208 GB. Hay 1,558,254,592 elementos de pesos o bias FP16 que consumen un byte adicional frente al piso uniforme: `1,558,254,592 × (2 − 1) bytes = 1.558254592 GB`. Eso sigue siendo **peso**, no metadata.

La metadata y el formato sí se desglosan: `0.487587840 GB de escalas FP16 + 0.243793920 GB de qzeros + 0.014942208 GB de g_idx + 0.000238648 GB de headers = 0.746562616 GB`. Así, `34.322130944 GB de pesos + 0.746562616 GB de metadata/formato = 35.068693560 GB de shards` (**DERIVED**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`).

Para KV, cada capa, token y solicitud requiere `2 K/V × 8 cabezas KV × 128 elementos/cabeza × 2 byte/FP16 = 4,096 bytes`. Con entrada de 2,048 tokens y salida máxima de 256, `4,096 byte × 64 capas × 2,304 tokens × 16 solicitudes ÷ 1,000,000,000 = 9.663676416 GB`. Es piso de payload: bloques, padding y fragmentación del runtime todavía pueden aumentarlo.

`subtotal = 35.068693560 + 4 + 9.663676416 + 4 = 52.732369976 GB`

`reserva = 52.732369976 GB × 0.10 = 5.27323699760 GB`

`total = 52.732369976 + 5.27323699760 = 58.00560697360 GB`

GB es decimal: `1 GB = 1,000,000,000 bytes`. GiB es binario: `1 GiB = 1,073,741,824 bytes`; por eso el mismo total es 54.0219312287867069244384765625 GiB. No se intercambian las etiquetas.

El sistema completo es la unidad adquirible considerada, no una GPU suelta imputada. El escenario fija **TP=1, PP=1, DP=1 y una réplica**: pesos, runtime, workspace y los 16 contextos KV viven en un único shard sobre una H100. Por tanto, el presupuesto de 58.00560697360 GB se compara con **80 GB físicos por réplica/shard**; las otras siete GPU del DGX quedan ociosas en este escenario. Los 640 GB físicos agregados describen el sistema adquirido, pero no sustituyen la memoria del shard ni se usan como umbral de “cabe” (**SCENARIO**; `S_COURSE_DESIGN`, `S_NVIDIA_DGX_H100_DATASHEET`).

La cadena de compatibilidad también queda explícita: el artefacto recomienda vLLM; vLLM 0.7.1 declara GPTQ sobre Hopper; y la ficha NVIDIA identifica ocho H100 dentro del DGX (`S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_VLLM_071_QUANTIZATION_HARDWARE`, `S_NVIDIA_DGX_H100_DATASHEET`). Es una configuración docente defendible, no una ejecución medida. La HBM física no equivale a HBM utilizable: faltan pico del allocator, memoria reservada por driver y pico medido por shard. “Un DGX” es el mínimo entre las topologías completas de este corpus, no un mínimo mundial ni una valoración de precio.

### Inferencia operacional: el SLA requiere una medición conjunta

Ahora cambia la pregunta: no basta con que una réplica quepa. El escenario fijo pide 16 solicitudes concurrentes, 2,048 tokens de entrada, hasta 256 de salida, 100 output tokens/s agregados, TTFT p95 ≤ 2 s y utilización ≤ 70 %. La redundancia es N servidores activos + 1 servidor en otro dominio de falla (**SCENARIO**; `I_PRODUCTION_DIDACTIC_TARGET`, `S_COURSE_DESIGN`).

| Resultado parcial disponible | Cumplimiento | Servidores y redundancia | CAPEX operacional |
|---|---|---|---|
| No se halló throughput de salida y TTFT p95 medidos juntos bajo el gate completo (**NOT_FOUND**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`, `S_VLLM_071_QUANTIZATION_HARDWARE`) | **ESTIMATION_NOT_IDENTIFIABLE**; `I_PRODUCTION_DIDACTIC_TARGET` | N activos + 1 en otro dominio: cantidad N **ESTIMATION_NOT_IDENTIFIABLE**; `I_PRODUCTION_DIDACTIC_TARGET` | **ESTIMATION_NOT_IDENTIFIABLE**; `I_PRODUCTION_DIDACTIC_TARGET` |

La misma ejecución debe fijar artefacto y revisión, runtime y versión, topología de hardware, scheduler, batch, warmup, longitudes de entrada y salida, contexto, concurrencia y utilización. Después debe registrar conjuntamente throughput de **salida** y la distribución de TTFT, incluido p95. Dos benchmarks separados no pasan el gate.

Sin esa medición no se calcula N, no se añade el servidor de reserva y no se multiplica por un precio. Pico teórico en FLOP/s tampoco sustituye throughput observado: esta página no infiere rendimiento, costo por token ni CAPEX operacional desde FLOP/s.

El README oficial fijado de Qwen2.5 aporta un **resultado parcial** de velocidad/memoria con A100 80 GB, batch 1 y longitudes de prompt declaradas por sus casos, bajo las versiones de Transformers/AutoGPTQ que enumera (**FACT**; `S_QWEN25_32B_GPTQ_INT8_ARTIFACT`). No publica conjuntamente TTFT p95, scheduler, warmup, concurrencia 16 ni utilización ≤70 %. Por eso el gate conjunto sigue **NOT_FOUND**, cumplimiento/N/CAPEX siguen **ESTIMATION_NOT_IDENTIFIABLE**, y ese parcial no alimenta N ni CAPEX.

## Guía de decisión

1. **Define la carga:** inferencia o entrenamiento, precisión, contexto, concurrencia, latencia y volumen.
2. **Presupuesta memoria:** pesos más caché KV o activaciones, gradientes, optimizador, temporales y margen del runtime.
3. **Mide:** utilización, memoria máxima, bytes, latencia, throughput, potencia de pared y calidad.
4. **Ataca el límite:** capacidad para OOM; localidad o bandwidth para datos; compute para unidades saturadas; interconexión para comunicación.
5. **Escala el tramo útil:** batching, cuantización validada y cluster sólo cuando capacidad o servicio lo exige.
6. **Incluye operación:** software, disponibilidad, confiabilidad, seguridad, costo total y energía.

## Antes de practicar

La decisión no comienza con una marca o una ficha técnica. Comienza con una carga concreta y una medición comparable. Primero se separa capacidad de velocidad: si el trabajo no cabe, la ejecución falla o descarga estado a una capa más lenta. Si cabe, todavía puede esperar datos, coordinación o unidades de cómputo. Esa separación evita comprar FLOP/s para un problema de memoria o añadir memoria a un problema dominado por comunicación.

Después se identifica la escala donde aparece el límite. Dentro de un core importan instrucciones, pipeline y caché. Entre CPU y acelerador importan copias, sincronización y tamaño de lote. Entre dispositivos o racks importan las colectivas, la red y el trabajo que queda disponible entre sincronizaciones. El mismo síntoma —GPU con baja utilización— puede venir de causas distintas en cada escala.

Por último se conserva el contexto de la cifra. Un máximo de producto es **FACT**, una cuenta explícita es **DERIVED** y una configuración hipotética es **SCENARIO**. Un rango construido con supuestos declarados es **ESTIMATE**. Ninguna etiqueta convierte el número en rendimiento observado.

La práctica oficial aparece a continuación, al final de la unidad. Incluye seis preguntas conceptuales, tres escenarios de decisión y quince flashcards. Los escenarios se resuelven en tres grupos pequeños, en paralelo, durante siete minutos; las tarjetas quedan como recuperación postclase y no añaden tiempo al bloque presencial.

## Qué debes recordar

- Divide bits entre ocho para obtener bytes; declara siempre si usas GB o GiB.
- Pesos son sólo el piso: inferencia añade KV y temporales; entrenamiento añade activaciones, gradientes y optimizador.
- Parámetros totales determinan almacenamiento; activos aproximan trabajo por token en MoE.
- Más contexto, batch o chips cambian memoria, espera y comunicación; no garantizan aceleración lineal.
- FACT, DERIVED, ESTIMATE y SCENARIO responden preguntas distintas. “No divulgado” evita convertir rumores en hechos.
- Potencia es una tasa con base declarada; energía integra esa potencia durante un tiempo. TDP, TGP y máximos medidos no son equivalentes.
- CAPEX sólo se compara con la misma frontera: aceleradores solos o sistema completo, con inclusiones, fecha y canal visibles.
- HBM física no es HBM utilizable; que un presupuesto quepa tampoco demuestra ausencia de OOM ni cumplimiento de SLA.
- **NOT_FOUND** significa que el corpus revisado no contiene el observable; **ESTIMATION_NOT_IDENTIFIABLE** significa que, por faltar observables, el resultado no puede calcularse defendiblemente.

## Fuentes

- [Python C API — objetos de punto flotante](https://docs.python.org/3/c-api/float.html) y [`sys.getsizeof`](https://docs.python.org/3/library/sys.html#sys.getsizeof): `float` de CPython, `double` de C y alcance de la medición directa del objeto.
- [NumPy — `ndarray.nbytes`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.nbytes.html): bytes consumidos por los elementos frente a atributos no incluidos.
- [Hugging Face Transformers — GPU memory usage](https://huggingface.co/docs/transformers/model_memory_anatomy): pesos mixed precision, gradientes, estados Adam, activaciones y temporales.
- [NVIDIA NIM — Troubleshooting GPU Memory OOM](https://docs.nvidia.com/nim/large-language-models/latest/troubleshooting/memory.html): fórmula de pesos, KV cache, contexto y overhead de inferencia.
- [NVIDIA Megatron Bridge — Parallelisms Guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/parallelisms.html): paralelismo de datos/modelo y comunicación colectiva.
- [Apple Newsroom — MacBook Pro con M5 Pro y M5 Max](https://www.apple.com/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/): memoria unificada y bandwidth del M5 Max.
- [NVIDIA — GeForce RTX 5090](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/): capacidad y TGP; [arquitectura RTX Blackwell](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf): bandwidth.
- [Google Cloud — TPU7x Ironwood](https://docs.cloud.google.com/tpu/docs/tpu7x): HBM, picos por precisión, interconexión y tamaño de pod.
- [NVIDIA — DGX GB300](https://www.nvidia.com/en-us/data-center/dgx-gb300/): composición, memoria y bandwidth; [NVL72 System Components](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html): NVLink, refrigeración y potencia máxima.
- [NVIDIA H100](https://www.nvidia.com/es-la/data-center/h100/) y [A100 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf): HBM, tasas pico por precisión y potencia del módulo; [Cloud TPU v4](https://docs.cloud.google.com/tpu/docs/v4): HBM, tasa BF16 y potencia medida por chip.
- Entrenamientos documentados: [paper de BLOOM](https://arxiv.org/abs/2211.05100), [model card de BLOOM](https://huggingface.co/bigscience/bloom/blob/main/README.md), [horas de BLOOM](https://arxiv.org/abs/2211.02001), [PaLM](https://arxiv.org/abs/2204.02311), [paper de Llama 3](https://ai.meta.com/research/publications/the-llama-3-herd-of-models/), [model card de Llama 3.1 405B](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct) y [DeepSeek-V3](https://arxiv.org/abs/2412.19437).
- [NVIDIA H800 — notas técnicas](https://docs.nvidia.com/590trd1-trusted-computing-solutions-release-notes.pdf): identificación del módulo H800 de 80 GB usada en la derivación de HBM física de DeepSeek-V3.
- [OpenAI — GPT-5.6 Sol](https://openai.com/index/previewing-gpt-5-6-sol/) y [disponibilidad de GPT-5.6](https://openai.com/index/gpt-5-6/): nombre, lanzamiento, disponibilidad y región.
- [Anthropic — Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5): nombre, lanzamiento y disponibilidad; [model card de Gemini 3.1 Pro](https://deepmind.google/models/model-cards/gemini-3-1-pro/) y [página de Gemini 3.1 Pro](https://deepmind.google/models/gemini/pro/): ficha y disponibilidad.
- [Moonshot AI — Kimi K3](https://www.kimi.com/blog/kimi-k3), [reporte técnico](https://arxiv.org/abs/2607.24653), [repositorio](https://github.com/MoonshotAI/Kimi-K3) y [model card](https://huggingface.co/moonshotai/Kimi-K3): lanzamiento, parámetros y artefacto abierto.
- [Qwen — Qwen3.8-Max](https://qwen.ai/blog?id=qwen3.8) y [Qwen3.8-2.4T-A95B](https://www.modelscope.cn/models/Qwen/Qwen3.8-2.4T-A95B): servicio alojado y artefacto base abierto, tratados como registros distintos.
- [Qwen2.5-32B-Instruct-GPTQ-Int8, revisión `eddc13f`](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct-GPTQ-Int8/tree/eddc13f573fd3648cc8a4741fdf1b70e8d6fc5c1): parámetros, configuración GPTQ/GQA y bytes de los nueve shards usados en el piso de inferencia.
- [vLLM 0.7.1 — hardware de cuantización](https://docs.vllm.ai/en/v0.7.1/features/quantization/supported_hardware.html): compatibilidad GPTQ con Hopper; [NVIDIA DGX H100](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/nvidia-dgx-h100-datasheet.pdf): sistema de ocho H100 y HBM física total.
