---
id: parcial-arquitectura-b
title: "Parcial 1 · Arquitectura y SO · Examen B"
nav_title: "Examen B"
summary: "El examen B de arquitectura y sistemas operativos, pregunta por pregunta, con la respuesta explicada debajo: qué es un sistema operativo, qué es un FLOP, por qué la GPU no sirve para todo, si más GHz es más rápido, y las partes de una computadora."
status: ready
estimated_time: 15m
tags: [examen, parcial, arquitectura, sistemas-operativos, flops, gpu]
---

# Parcial 1 · Arquitectura y SO · Examen B

**[PDF del examen B, sin respuestas](../../_assets/parcial-arquitectura-b.pdf)** · 15 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. Son preguntas de explicar, así que hay varias respuestas correctas. Cada respuesta dice qué tenía que aparecer y qué otras formas también valían.

::: problem {#pab-1 title="1 · El sistema operativo (2 puntos)"}
Define qué es, qué hace y por qué es importante un sistema operativo.
:::

::: answer {of="pab-1"}
**Qué es.** El software que se pone **entre tus programas y el hardware**. Ningún programa que escribas habla directo con el disco: le pide al sistema operativo que lo haga por él.

**Qué hace:**

- **reparte la CPU** entre los programas que corren a la vez, que no se conocen entre sí;
- **administra la memoria y el almacenamiento**: cuánta RAM le toca a cada programa, y dónde quedan los datos;
- **controla los periféricos**: teclado, pantalla, red y discos, a través de sus drivers;
- **expone un sistema de archivos**: traduce bytes en un disco a nombres y carpetas que una persona puede escribir.

**Por qué importa.**

- Es la razón por la que el mismo programa se comporta distinto en dos máquinas: cada sistema operativo media de otra forma.
- Decide qué puedes instalar y cómo se escriben tus rutas.
- En datos importa en particular porque la nube corre casi toda en Linux.

**Lo que tenía que aparecer:** la idea de intermediario entre programas y hardware, al menos dos de sus funciones, y una razón de por qué importa.

**También valía:**

- Hablar del **núcleo** o *kernel*, que es la parte que hace la mediación.
- Separar el núcleo de la **distribución**: núcleo, utilerías, gestor de paquetes y escritorio.

**Repasa:** [[software-libre-y-sistemas-operativos|Software libre y sistemas operativos]].
:::

::: problem {#pab-2 title="2 · El FLOP (2 puntos)"}
¿Qué es un FLOP, y por qué son importantes?
:::

::: answer {of="pab-2"}
**Qué es.** Un **FLOP** es **una operación de punto flotante**: una suma o una multiplicación entre números con decimales. **FLOPS**, con S mayúscula, es cuántas de esas operaciones se hacen **por segundo**.

En corto: **FLOP es trabajo; FLOPS es ritmo.** Los prefijos son los de siempre: GFLOPS = 10⁹, TFLOPS = 10¹² y PFLOPS = 10¹⁵ por segundo.

**Por qué importan.**

- Casi todo el cómputo numérico (ciencia de datos, simulación, redes neuronales) es aritmética de punto flotante, así que los FLOPS miden la **capacidad de cálculo** de un chip.
- Sirven para **comparar** hardware y para **estimar tiempos**: si un entrenamiento necesita 10¹⁸ FLOP y tu GPU da 10¹⁴ FLOPS, son unos 10⁴ segundos en el mejor caso.

**Matices que suman:**

- La **precisión** es parte de la unidad. Un chip da muchos más FLOPS en FP16 que en FP64, así que hay que comparar en la misma precisión.
- Más FLOPS **no ayuda** si el trabajo está limitado por la memoria: si los datos no llegan a tiempo, las unidades de cálculo esperan.

**Repasa:** [[paralelismo-performance-energia|Paralelismo, performance y energía]].
:::

::: problem {#pab-3 title="3 · ¿Por qué no usar la GPU para todo? (2 puntos)"}
Si el GPU es tan superior en FLOPS, ¿por qué no se usa para todas las tareas de cómputo?
:::

::: answer {of="pab-3"}
Porque los FLOPS sólo cuentan cuando el problema tiene **la forma** que la GPU sabe aprovechar. Cualquiera de estas razones valía; dos bien explicadas daban el punto completo:

1. **Control irregular y trabajo secuencial.** La GPU gana aplicando la misma operación a muchos datos. Si cada dato toma un camino distinto (ramas, decisiones), sus unidades se esperan unas a otras. Una tarea que es una sola cadena de pasos no se puede repartir.
2. **El costo de llegar a la GPU.** Hay que copiar los datos de la RAM a la VRAM, lanzar el trabajo y sincronizar. En un trabajo corto, esa copia tarda más que el cálculo.
3. **El límite es la memoria, no el cálculo.** Si el trabajo hace pocas operaciones por cada byte que mueve, las unidades esperan datos, y más FLOPS no cambian nada.
4. **Memoria y costo.** Lo que no cabe en la VRAM no se puede procesar ahí de una vez. Y una GPU cuesta y consume mucho más que una CPU.

Por eso el reparto habitual es que la **CPU coordina** y la **GPU procesa los lotes** grandes y regulares.
:::

::: problem {#pab-4 title="4 · 6 GHz contra 4 GHz (2 puntos)"}
Si un procesador corre a 6 GHz y otro a 4 GHz, ¿podemos garantizar que el primero completará las tareas más rápido? ¿Sí o no? ¿Por qué? ¿Bajo qué circunstancias?
:::

::: answer {of="pab-4"}
**No.** Los GHz dicen cuántos ciclos da el reloj por segundo, no cuánto trabajo útil sale de cada ciclo. **El reloj asigna pasos; no garantiza trabajo.**

El trabajo terminado depende también de:

- **la microarquitectura**: cuántas instrucciones termina por ciclo. Un chip a 4 GHz que termina el doble de instrucciones por ciclo le gana a uno a 6 GHz;
- **el paralelismo**: cuántos núcleos y unidades tiene, si la tarea se puede repartir;
- **las esperas por datos**: si la tarea vive esperando a la memoria, los ciclos extra se gastan esperando;
- **el calor**: un chip que se calienta baja su frecuencia para protegerse, y los 6 GHz no se sostienen;
- **la ISA y el software**: el mismo programa compilado para otra ISA genera otras instrucciones.

**¿Cuándo sí?** Si los dos procesadores son **iguales en todo lo demás** (misma microarquitectura, mismos núcleos, misma memoria) y la tarea está limitada por el cálculo, entonces 6 GHz termina antes. Fuera de ese caso controlado, no se puede garantizar.

**Lo que tenía que aparecer:** el «no», al menos un factor además de la frecuencia, y la condición de «todo lo demás igual».

**Repasa:** [[compute-instrucciones-cpu|Compute, instrucciones y CPU]].
:::

::: problem {#pab-5 title="5 · Las partes de una computadora (2 puntos)"}
¿Cuáles son todos los componentes de una computadora? No la jerarquía de memoria, sino sus partes.
:::

::: answer {of="pab-5"}
Las del curso, que ve la máquina como **un sistema, no un chip**:

| Componente | Qué hace |
|---|---|
| **CPU** | Ejecuta instrucciones generales y decide el flujo del programa |
| **RAM** | Mantiene las instrucciones y los datos activos mientras se usan |
| **Almacenamiento** (SSD o disco) | Conserva los datos aunque se apague la máquina |
| **Acelerador** (GPU, NPU) | Hace en paralelo un tipo de cálculo específico |
| **Entrada, salida y red** | Teclado, pantalla, tarjeta de red y puertos: cómo entra y sale la información |
| **Interconexiones** | Los caminos que unen todo lo anterior; ninguna pieza sirve aislada |

**También valía**, porque son partes reales aunque el curso no las detalló:

- **tarjeta madre**, que es donde viven las interconexiones;
- **fuente de poder**;
- **enfriamiento**;
- **buses**, el nombre clásico de las interconexiones.

**Lo que tenía que aparecer:** como mínimo CPU, memoria (RAM), almacenamiento y entrada y salida. Confundir RAM con almacenamiento era el error que más costaba.

**Repasa:** [[compute-instrucciones-cpu|Compute, instrucciones y CPU]].
:::
