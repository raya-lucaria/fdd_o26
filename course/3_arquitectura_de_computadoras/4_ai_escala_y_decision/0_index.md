---
id: ia-escala-decision
title: "IA, escala y selección de hardware"
nav_title: "IA, escala y decisión"
summary: "Cómo presupuestar memoria, comunicación y operación antes de elegir hardware para IA."
status: ready
estimated_time: "32 minutos"
tags: [ia, memoria, escalamiento, hardware]
---

Un modelo de IA transforma entradas con parámetros. El hardware aloja y mueve su estado para cumplir latencia, throughput, energía y costo. **Los parámetros inician el presupuesto, no lo completan.**

## Inferencia y entrenamiento ocupan memoria distinta

![Comparación categórica: inferencia usa pesos, caché KV y temporales; entrenamiento añade activaciones, gradientes y estados del optimizador.](../_assets/memoria-ai.svg)

*Diagrama propio del curso, SVG accesible, 2026. Los bloques nombran componentes; sus tamaños no están a escala.*

**Lectura visual:** inferencia necesita pesos, caché KV y temporales. Entrenamiento añade activaciones, gradientes y estados del optimizador. El runtime reserva otros buffers.

En **inferencia**, *prefill* procesa el prompt y *decode* produce tokens reutilizando la **caché KV**. Evita recalcular la historia, pero ocupa memoria.

Más **contexto** aumenta caché KV y atención; suele empeorar latencia y throughput por solicitud. El máximo admitido no indica cuántas peticiones caben.

El **batching** agrupa secuencias: puede elevar throughput, pero consume memoria y suma espera. Contexto y batch se ajustan por separado con solicitudes reales.

En **entrenamiento**, *forward* crea activaciones, *backward* gradientes y el optimizador actualiza parámetros. *Recomputation* cambia memoria por cálculo. Partir estados reduce memoria local, pero obliga a comunicarlos.

## La cuenta mínima de los pesos

Para parámetros almacenados con precisión uniforme, sea $N_p$ su cantidad y $b$ sus bits. **FACT (convención decimal):** B representa $10^9$ y T representa $10^{12}$; GB y TB aquí también son decimales.

$$M_{pesos}=N_p\times\frac{b}{8}$$

**DERIVED (GB decimales, sólo pesos):**

- **7B:** BF16 = $7\times10^9\times2$ bytes = **14 GB**; INT8 = **7 GB**; INT4 = **3.5 GB**.
- **70B:** BF16 = **140 GB**; INT8 = **70 GB**; INT4 = **35 GB**.
- **1T:** BF16 = **2 TB**; INT8 = **1 TB**; INT4 = **0.5 TB**.

Son capacidades lógicas. GiB, escalas, *padding*, buffers y particionado cambian la memoria física.

**DERIVED (presupuesto base de esta receta):** *mixed precision* con Adam clásico suma **~18 bytes por parámetro**: 2 de pesos BF16/FP16 + 4 de copia FP32 + 4 de gradiente FP32 + 8 de estados Adam FP32. Para 7B, 70B y 1T son **126 GB**, **1.26 TB** y **18 TB** de estado agregado del modelo, antes de activaciones y temporales.

No obliga a guardar 18 bytes completos en cada GPU. El **sharding** reparte estado y reduce memoria local a cambio de comunicación y buffers. Precisión, activaciones, temporales e implementación cambian el máximo real.

## Cuantizar cambia más que capacidad

Cuantizar pesos reduce bytes y tráfico, pero exige soporte y validación numérica; INT4 no duplica necesariamente la velocidad de INT8.

Cuantizar pesos no reduce automáticamente caché KV ni activaciones. Valida precisión, contexto, batch y calidad en el hardware real.

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

## Cuatro ejemplos representativos, no un ranking

- **FACT (límite de producto):** M5 Max admite hasta **128 GB unificados** y **614 GB/s**; no son benchmark ni TDP.
- **FACT (referencia NVIDIA):** RTX 5090 tiene **32 GB GDDR7**, **1,792 GB/s de ancho de banda pico de memoria** y **575 W TGP**. Pesos, cachés y temporales comparten capacidad; tarjetas de ensambladores pueden variar.
- **FACT (picos por chip):** TPU7x ofrece **192 GiB HBM**, **7,380 GB/s**, **2,307 TFLOPS BF16** y **4,614 TFLOPS FP8**; un pod llega a **9,216 chips**. No es desempeño observado.
- **FACT (sistema oficial, máximos agregados):** DGX GB300 integra **72 GPU Blackwell Ultra**, **36 CPU Grace**, **20 TB de memoria GPU**, hasta **576 TB/s** HBM y **130 TB/s NVLink**. El rack usa refrigeración líquida y admite hasta **142 kW**; es capacidad máxima, no consumo medido.

No son un ranking: la aplicación y la medición completa deciden.

## Guía de decisión

1. **Define la carga:** inferencia o entrenamiento, precisión, contexto, concurrencia, latencia y volumen.
2. **Presupuesta memoria:** pesos más caché KV o activaciones, gradientes, optimizador, temporales y margen del runtime.
3. **Mide:** utilización, memoria máxima, bytes, latencia, throughput, potencia de pared y calidad.
4. **Ataca el límite:** capacidad para OOM; localidad o bandwidth para datos; compute para unidades saturadas; interconexión para comunicación.
5. **Escala el tramo útil:** batching, cuantización validada y cluster sólo cuando capacidad o servicio lo exige.
6. **Incluye operación:** software, disponibilidad, confiabilidad, seguridad, costo total y energía.

## Antes de practicar

La decisión no comienza con una marca o una ficha técnica. Comienza con una carga concreta y una medición comparable. Primero se separa capacidad de velocidad: si el trabajo no cabe, la ejecución falla o descarga estado a una capa más lenta. Si cabe, todavía puede esperar datos, coordinación o unidades de cómputo. Esa separación evita comprar FLOPS para un problema de memoria o añadir memoria a un problema dominado por comunicación.

Después se identifica la escala donde aparece el límite. Dentro de un core importan instrucciones, pipeline y caché. Entre CPU y acelerador importan copias, sincronización y tamaño de lote. Entre dispositivos o racks importan las colectivas, la red y el trabajo que queda disponible entre sincronizaciones. El mismo síntoma —GPU con baja utilización— puede venir de causas distintas en cada escala.

Por último se conserva el contexto de la cifra. Un máximo de producto es **FACT**, una cuenta explícita es **DERIVED** y un escenario docente es **ESTIMATE**. Ninguna de esas etiquetas convierte el número en rendimiento observado. Una comparación útil mantiene constantes tarea, precisión, calidad, lote, contexto y frontera energética; luego registra capacidad máxima, latencia, throughput, bytes movidos y potencia de pared.

La práctica oficial aparece a continuación, al final de la unidad. Incluye seis preguntas conceptuales, tres escenarios de decisión y quince flashcards. Los escenarios se resuelven en tres grupos pequeños, en paralelo, durante siete minutos; las tarjetas quedan como recuperación postclase y no añaden tiempo al bloque presencial.

## Fuentes

- [Hugging Face Transformers — GPU memory usage](https://huggingface.co/docs/transformers/model_memory_anatomy): pesos mixed precision, gradientes, estados Adam, activaciones y temporales.
- [NVIDIA NIM — Troubleshooting GPU Memory OOM](https://docs.nvidia.com/nim/large-language-models/latest/troubleshooting/memory.html): fórmula de pesos, KV cache, contexto y overhead de inferencia.
- [NVIDIA Megatron Bridge — Parallelisms Guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/parallelisms.html): paralelismo de datos/modelo y comunicación colectiva.
- [Apple Newsroom — MacBook Pro con M5 Pro y M5 Max](https://www.apple.com/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/): memoria unificada y bandwidth del M5 Max.
- [NVIDIA — GeForce RTX 5090](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/): capacidad y TGP; [arquitectura RTX Blackwell](https://images.nvidia.com/aem-dam/Solutions/geforce/blackwell/nvidia-rtx-blackwell-gpu-architecture.pdf): bandwidth.
- [Google Cloud — TPU7x Ironwood](https://docs.cloud.google.com/tpu/docs/tpu7x): HBM, picos por precisión, interconexión y tamaño de pod.
- [NVIDIA — DGX GB300](https://www.nvidia.com/en-us/data-center/dgx-gb300/): composición, memoria y bandwidth; [NVL72 System Components](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html): NVLink, refrigeración y potencia máxima.
