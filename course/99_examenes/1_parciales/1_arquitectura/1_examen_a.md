---
id: parcial-arquitectura-a
title: "Parcial 1 · Arquitectura y SO · Examen A"
nav_title: "Examen A"
summary: "El examen A de arquitectura de computadoras, pregunta por pregunta, con la respuesta explicada debajo: jerarquía de memoria, CPU contra GPU, elegir hardware para dos necesidades, y la ISA y los ciclos de reloj."
status: ready
estimated_time: 15m
tags: [examen, parcial, arquitectura, memoria, cpu, gpu]
---

# Parcial 1 · Arquitectura y SO · Examen A

**[PDF del examen A, sin respuestas](../../_assets/parcial-arquitectura-a.pdf)** · 15 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Son preguntas de explicar, así que hay varias respuestas correctas. Cada respuesta dice qué tenía que aparecer y qué otras formas también valían.

::: problem {#paa-1 title="1 · La jerarquía de memoria (2 puntos)"}
Dibuja la jerarquía de memoria de una computadora moderna, desde registros hasta disco. Para cada nivel indica si su velocidad es alta o baja y si su capacidad es grande o pequeña. Incluye la GPU.
:::

::: answer {of="paa-1"}
De arriba (junto al cómputo) hacia abajo:

```text
            CPU                              GPU
   registros                        registros de la GPU
   caché L1                         cachés de la GPU
   caché L2                               |
   caché L3                               |
   RAM  <---- interconexión (PCIe) ---->  VRAM
   SSD / disco
   red / almacenamiento remoto
```

| Nivel | Velocidad | Capacidad |
|---|---|---|
| Registros | la más alta, menos de 1 ns | la más pequeña: bytes a KB |
| L1 → L2 → L3 | muy alta, de ~1 ns a ~30 ns | pequeña: de KiB a cientos de MiB |
| RAM y VRAM | media, ~100 ns | grande: GB a TB |
| SSD | baja, ~100 µs | muy grande: cientos de GB a TB |
| Red | la más baja, de ms | casi ilimitada |

Los números son órdenes de magnitud del curso, no se pedían. Lo que se califica es **la regla**: al acercarse al cómputo, cada nivel es más rápido, más pequeño y más caro por byte.

**La GPU.** Tiene su propia memoria, la **VRAM**, al mismo nivel que la RAM, con sus propias cachés y registros encima. Para que la GPU use un dato que está en RAM, primero hay que **copiarlo** a la VRAM por la interconexión. Ese viaje extra es un costo que la CPU no paga.

**También valía:**

- Separar HDD y SSD: el HDD queda abajo del SSD, más lento.
- Llamar HBM a la VRAM de los aceleradores grandes.
- Mencionar la memoria unificada, como en los chips de Apple, donde CPU y GPU comparten la misma memoria y se evita esa copia.

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]].
:::

::: problem {#paa-2 title="2 · CPU contra GPU (2 puntos)"}
¿En qué se diferencia la filosofía de diseño de un CPU frente a la de un GPU? ¿Qué tipo de tareas resuelve mejor cada uno y por qué?
:::

::: answer {of="paa-2"}
**La CPU** dedica sus recursos a **pocos flujos complejos**: pocos núcleos muy capaces, con mucha lógica para decidir, predecir saltos y esperar poco. Optimiza la **latencia** de una tarea.

**La GPU** junta **muchas unidades sencillas** que aplican la misma operación a muchos datos a la vez. Optimiza el **throughput**: cuánto trabajo termina por segundo.

| | CPU | GPU |
|---|---|---|
| Diseño | pocos núcleos flexibles | miles de unidades simples |
| Optimiza | latencia | throughput |
| Le va bien | control irregular, decisiones, trabajo secuencial, solicitudes pequeñas | operaciones regulares e independientes sobre lotes grandes |
| Ejemplos | un servidor web, un compilador, el sistema operativo | multiplicar matrices, entrenar redes, procesar imágenes |

**Por qué.** Si cada dato necesita una decisión distinta, las unidades de la GPU se quedan esperando unas a otras: es la **divergencia**. Si todos los datos llevan la misma cuenta, miles de unidades en paralelo terminan mucho antes que unos pocos núcleos.

**Lo que tenía que aparecer:** latencia contra throughput, o su equivalente («pocos flujos flexibles» contra «muchos flujos regulares»), y un tipo de tarea para cada uno con su porqué.

**Repasa:** [[paralelismo-performance-energia|Paralelismo, performance y energía]].
:::

## Pregunta 3 · Elegir hardware (2 puntos cada inciso)

**Necesidad 1:** un sistema de búsqueda que recorre un índice de **300 GB en RAM**. Las consultas son irregulares: cada una toca partes distintas del índice. Requiere **baja latencia**, menos de 10 ms.

**Necesidad 2:** un servicio de recomendaciones que hace inferencia de una red neuronal. El modelo pesa **8 GB** y recibe **500 solicitudes por segundo**.

::: problem {#paa-3a title="3a · Necesidad 1: ¿qué componente y qué procesador?"}
¿Qué componente de hardware es el más crítico (CPU, RAM, GPU o disco), y por qué? ¿Qué tipo de procesador (CPU, GPU o NPU) es más adecuado para este patrón de acceso irregular? Justifica.
:::

::: answer {of="paa-3a"}
**Componente crítico: la RAM**, por dos razones:

1. **Capacidad.** Los 300 GB tienen que **caber**. Si no caben, cada consulta baja al SSD, que es unas mil veces más lento, y los 10 ms no se cumplen.
2. **Latencia.** Cada consulta salta a un lugar distinto, así que las cachés casi no ayudan. Lo que domina es cuánto tarda cada acceso a RAM, no cuántos bytes por segundo pasan.

**Procesador: CPU.**

- El acceso es irregular y con decisiones: seguir un índice es ir de un dato al siguiente según lo que encontraste. Eso es «control irregular y baja latencia», justo lo que hace bien una CPU.
- Una GPU perdería por tres lados. Sus unidades divergen, porque cada consulta toma otro camino. Los 300 GB **no caben** en la VRAM de una GPU normal (decenas de GB). Y copiar datos de RAM a VRAM agrega espera a cada consulta.
- Una NPU está hecha para operaciones de redes neuronales, no para recorrer un índice.

**También valía:**

- Decir «RAM y latencia» como el cuello de botella, o hablar de «localidad».
- Proponer una CPU **con muchos núcleos** para atender varias consultas a la vez: cada consulta sigue siendo secuencial, pero muchas consultas son independientes entre sí.

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]].
:::

::: problem {#paa-3b title="3b · Necesidad 2: ¿qué procesador?"}
¿Qué tipo de procesador es más adecuado (CPU, GPU, NPU, TPU o RAM)? ¿Por qué?
:::

::: answer {of="paa-3b"}
**GPU**, la respuesta esperada.

- La inferencia de una red neuronal son **multiplicaciones de matrices**: la misma operación sobre muchos datos, el caso ideal de la GPU.
- El modelo de 8 GB **cabe** en la VRAM de una GPU común, así que se carga una vez y se queda ahí.
- 500 solicitudes por segundo es un problema de **throughput**. La GPU puede agrupar solicitudes en un **batch** y procesarlas juntas: sube el throughput, a cambio de un poco más de espera por solicitud.

**También valía, si se justificaba:**

- **TPU**: el acelerador de Google, hecho para redes neuronales. Sólo existe en la nube de Google.
- **NPU**: aceleradores de operaciones neuronales. Sirve si el modelo usa operaciones que la NPU soporta; si no, el trabajo vuelve a la CPU o a la GPU.

**No valía:**

- **RAM**: no es un procesador. Era una opción trampa, y elegirla mostraba confundir memoria con cómputo.
- **CPU**, sin más: puede correr un modelo pequeño, pero para 500 solicitudes por segundo su throughput se queda corto.

**Repasa:** [[ia-escala-decision|IA, escala y selección de hardware]].
:::

::: problem {#paa-4 title="4 · El ensamblador y los ciclos de reloj (2 puntos)"}
¿Qué es el ASL/ensamblador? ¿En qué afecta, y cómo está relacionado con los ciclos de reloj?
:::

::: answer {of="paa-4"}
En el curso esto se vio como la **ISA** (*instruction set architecture*). «ASL» se interpreta como esa idea.

**Qué es.**

- La **ISA** es el contrato entre el software y el procesador: qué instrucciones existen, qué registros hay y cómo se escriben las órdenes. x86-64, ARM y RISC-V son ISA distintas.
- El **ensamblador** (*assembly*) es esa misma lista de instrucciones escrita en texto legible, una por línea: `add`, `mov`, `load`.
- Un programa en C o en Rust se **compila** a instrucciones de una ISA concreta.

**En qué afecta.** Un binario sólo corre en un procesador que implemente **su** ISA. Por eso un programa para x86-64 no corre tal cual en un ARM.

**Relación con los ciclos de reloj.**

- El reloj marca el ritmo. A 3 GHz, cada tick dura 1/(3×10⁹) s, unos 0.33 ns.
- Cada instrucción pasa por **buscar, decodificar y ejecutar**, y eso toma uno o varios ciclos. **No** es una instrucción por tick: una suma simple puede tomar un ciclo, una división o un acceso a memoria muchos más.
- El *pipeline* traslapa instrucciones para terminar más por segundo, pero una dependencia, un salto mal predicho o un dato que no llega lo obligan a esperar.
- Por eso el mismo programa tarda distinto según **cuántas** instrucciones genera, **cuáles** son y la **microarquitectura** que las ejecuta, no sólo según los GHz.

**Lo que tenía que aparecer:** que son las instrucciones que entiende el procesador, y que cada instrucción consume ciclos de reloj, no necesariamente uno.

**Repasa:** [[compute-instrucciones-cpu|Compute, instrucciones y CPU]].
:::
