---
id: ejercicios-arquitectura
title: "Ejercicios extra de arquitectura y SO"
nav_title: "Arquitectura y SO"
summary: "Ejercicios con la forma del parcial 1, cada uno con una pista y su respuesta plegadas: jerarquía de memoria, localidad, CPU contra GPU, FLOPS y tiempos, el techo de la memoria, GHz, ISA y el sistema operativo."
status: ready
estimated_time: 40m
tags: [ejercicios, arquitectura, memoria, cpu, gpu, flops, sistemas-operativos]
---

# Ejercicios extra de arquitectura y SO

**[PDF sin respuestas, para imprimir](../_assets/practica-arquitectura.pdf)** · unos 40 minutos · sin apuntes

Miden lo mismo que el [[parcial-arquitectura|parcial 1]] con casos nuevos. Debajo de cada pregunta hay dos cosas plegadas:

- **la pista**: ábrela sólo si llevas un rato atorado;
- **la respuesta**, con su explicación.

Varias preguntas piden una cuenta. Hazla en papel: son órdenes de magnitud, y lo que importa es el razonamiento.

## Parte 1 · Memoria

::: problem {#xa-1 title="1 · Ordena por velocidad"}
Ordena del más rápido al más lento: SSD, caché L2, registro, RAM, red, caché L1, caché L3. ¿Qué pasa con la capacidad en ese mismo orden?
:::

::: hint {of="xa-1"}
Piensa en la distancia al lugar donde se hace la cuenta. Lo que está dentro del núcleo es lo más rápido.
:::

::: answer {of="xa-1"}
**Respuesta:**

- Velocidad, del más rápido al más lento: **registro → caché L1 → caché L2 → caché L3 → RAM → SSD → red**.
- Capacidad en ese mismo orden: **va al revés, crece**. El registro guarda unos cuantos bytes; la red, casi lo que quieras.

**Por qué:**

1. La cuenta se hace en las unidades de ejecución, dentro del núcleo de la CPU. Los registros están ahí mismo.
2. Las cachés L1, L2 y L3 están dentro del chip. Cada una está un poco más lejos que la anterior, y es más grande.
3. La RAM está fuera del chip. El SSD está detrás de su controlador. La red está en otra máquina.
4. La memoria cercana y rápida es cara por byte, así que se pone poca. La lejana es barata, así que se pone mucha.

**La regla:** **jerarquía de memoria: cuanto más cerca del cómputo está un nivel, más rápido, más pequeño y más caro por byte es.** No existe una memoria rápida, grande y barata a la vez; por eso hay niveles. Lo enseña [[memoria-y-datos|Memoria y movimiento de datos]].

Las cifras orientativas de esa página (1 µs = 1,000 ns; 1 ms = 1,000 µs):

| Nivel | Latencia orientativa | Capacidad común |
|---|---|---|
| Registro | menos de 1 ns | bytes a KB por núcleo |
| Caché L1 | cerca de 1 ns | decenas a cientos de KB |
| Caché L2 | 3–5 ns | cientos de KB a unos MB |
| Caché L3 | 10–30 ns | decenas a cientos de MB |
| RAM | 60–150 ns | GB a TB |
| SSD | 50–300 µs | cientos de GB a TB |
| Red | 0.5–100 ms | remota, hasta PB |

**Error común:** poner la RAM antes que la caché L3 porque la RAM es «la memoria principal». Principal quiere decir que guarda los datos activos de los programas, no que sea rápida: la L3 responde en 10–30 ns y la RAM en 60–150 ns.
:::

::: problem {#xa-2 title="2 · No cupo"}
Tu laptop tiene 16 GB de RAM. Procesar una tabla de 2 GB tarda 10 segundos. Una tabla de 40 GB, con el mismo procesamiento, tarda mucho más que 20 veces eso. ¿Por qué no escala en proporción?
:::

::: hint {of="xa-2"}
¿Dónde quedan los 40 GB si la RAM tiene 16? ¿Qué nivel de la jerarquía toca entonces cada acceso?
:::

::: answer {of="xa-2"}
**Respuesta:** **Los 40 GB no caben en los 16 GB de RAM. La parte que no cabe vive en el SSD, y cada acceso que no encuentra su dato en RAM y tiene que ir al SSD cuesta del orden de mil veces más que un acceso a RAM. No hiciste 20 veces el mismo trabajo: hiciste el trabajo un nivel más abajo en la jerarquía de memoria.**

**Por qué:**

1. Si el tiempo escalara en proporción, 40 GB tardarían 20 veces lo de 2 GB: 20 × 10 s = 200 s.
2. La tabla de 2 GB cabe completa en la RAM. Todos sus accesos pagan latencia de RAM.
3. La tabla de 40 GB no cabe: al menos 40 − 16 = 24 GB quedan fuera de la RAM, en el SSD.
4. Mientras el programa avanza, el sistema operativo saca pedazos de la RAM al SSD y vuelve a traerlos cuando el programa los toca otra vez.
5. Cada acceso que falla en RAM (su pedazo está en el SSD) paga la latencia del SSD, no la de la RAM.

**La regla:** **capacidad: si los datos no caben en un nivel de la jerarquía, los accesos bajan al nivel siguiente, y el costo de cada acceso salta de golpe, no en proporción.** Es el síntoma «no cabe» de [[memoria-y-datos|Memoria y movimiento de datos]].

| Tabla | ¿Cabe en 16 GB de RAM? | Dónde ocurren los accesos | Tiempo |
|---|---|---|---|
| 2 GB | Sí | sólo en RAM | 10 s (dato del enunciado) |
| 40 GB | **No** | en RAM y **en el SSD** | **mucho más** que 200 s |

Con las latencias orientativas del curso, RAM 60–150 ns y SSD 50–300 µs, un acceso que va al SSD es unas 830–2,000 veces más lento (50 µs ÷ 60 ns ≈ 830; 300 µs ÷ 150 ns = 2,000): del orden de **mil veces**.

Lo que sí arregla un problema de capacidad: procesar por pedazos que quepan en RAM, cargar sólo las columnas necesarias, o una máquina con más RAM.

**Compruébalo:** `python3 -c "print(50e-6/60e-9, 300e-6/150e-9)"` → `833.3333333333335 2000.0`

**Error común:** «20 veces más datos, 20 veces más tiempo: 200 s». Esa cuenta supone que cada acceso cuesta lo mismo, y eso sólo vale mientras todos los datos quepan en el mismo nivel.
:::

::: problem {#xa-3 title="3 · En orden o al azar"}
Dos programas leen los mismos 1,000 millones de números de un arreglo en RAM. Uno los recorre **en orden** y el otro **saltando al azar**. Leen la misma cantidad de datos. ¿Cuál termina antes, y por qué?
:::

::: hint {of="xa-3"}
Cuando la CPU trae un dato de la RAM, no trae sólo ese: trae un bloque con sus vecinos. ¿A cuál de los dos programas le sirven los vecinos?
:::

::: answer {of="xa-3"}
**Respuesta:** **El que recorre en orden termina antes, por mucho. Los dos leen los mismos números, pero el que va en orden hace unas ocho veces menos viajes a la RAM.**

**Por qué:**

1. La CPU no trae de la RAM un número suelto: trae a la caché un **bloque** de números contiguos, llamado línea de caché.
2. En muchos procesadores una línea mide 64 bytes: 8 números de 8 bytes. Para el ejemplo, un bloque = 8 números.
3. El programa en orden usa los 8 números de cada bloque: paga 1 viaje a la RAM y hace 7 lecturas desde la caché.
4. Además, el procesador detecta el recorrido en orden y pide el bloque siguiente antes de que el programa lo necesite.
5. El programa al azar usa 1 número de cada bloque y salta a otro: paga casi un viaje a la RAM por lectura y desperdicia los otros 7 números.

**La regla:** **localidad: los datos contiguos llegan juntos, así que leer en el orden en que están guardados aprovecha cada viaje; saltar al azar convierte cada lectura en un viaje.** Un recorrido en orden queda limitado por el **ancho de banda** de la RAM; uno al azar, por su **latencia**. Lo enseña [[memoria-y-datos|Memoria y movimiento de datos]].

Las primeras lecturas de cada programa (las posiciones al azar son ejemplos):

| Lectura | En orden lee | ¿Estaba en caché? | Al azar lee | ¿Estaba en caché? |
|---|---|---|---|---|
| 1ª | posición 0 | No: viaje a RAM, trae 0–7 | posición 512,334,019 | No: viaje a RAM |
| 2ª | posición 1 | **Sí**, llegó con el bloque 0–7 | posición 88,120 | No: viaje a RAM |
| 3ª | posición 2 | **Sí**, llegó con el bloque 0–7 | posición 730,005,411 | No: viaje a RAM |
| 4ª a 7ª | posiciones 3 a 6 | **Sí**, llegaron con el bloque 0–7 | cuatro posiciones más, al azar | No: un viaje a RAM cada una |
| 8ª | posición 7 | **Sí**, llegó con el bloque 0–7 | posición 41,999,876 | No: viaje a RAM |

En orden, 7 de cada 8 lecturas (87.5 %) ya están en la caché. Al azar, con mil millones de números, casi ninguna lo está: el arreglo es muchísimo más grande que las cachés.

**Error común:** «leen la misma cantidad de datos, así que tardan lo mismo». El tiempo no lo fija cuántos números usas, sino cuántos viajes a la RAM haces para conseguirlos.
:::

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]].

## Parte 2 · CPU, GPU y FLOPS

::: problem {#xa-4 title="4 · ¿CPU o GPU?"}
Para cada tarea, elige CPU o GPU y di por qué en una frase:

a) Compilar un programa.

b) Multiplicar dos matrices de 10,000 × 10,000.

c) Un servidor web que atiende solicitudes pequeñas, cada una con su lógica.

d) Aplicar el mismo filtro a un millón de imágenes.

e) Leer un JSON con estructura irregular y validar cada campo.
:::

::: hint {of="xa-4"}
Pregúntate en cada caso: ¿es la misma operación sobre muchos datos independientes, o son decisiones distintas paso a paso?
:::

::: answer {of="xa-4"}
**Respuesta:**

| Tarea | Elige | Por qué, en una frase |
|---|---|---|
| a) Compilar un programa | **CPU** | Está lleno de decisiones y ramas, y cada paso depende del anterior. |
| b) Multiplicar matrices de 10,000 × 10,000 | **GPU** | Es un billón (10¹²) de multiplicaciones iguales e independientes entre sí. |
| c) Servidor web con solicitudes pequeñas | **CPU** | Cada solicitud tiene su propia lógica, y lo que importa es la latencia de cada una. |
| d) El mismo filtro a un millón de imágenes | **GPU** | Es la misma operación sobre muchísimos píxeles independientes. |
| e) JSON irregular, validar cada campo | **CPU** | Cada campo se valida distinto: el control es irregular. |

**Por qué:**

1. Una CPU tiene pocos núcleos muy flexibles: son rápidos para tomar decisiones y para pasos que dependen del anterior.
2. Una GPU tiene muchísimas unidades más simples, que aplican la misma operación a muchos datos a la vez.
3. Si cada dato toma una rama distinta, parte de las unidades de la GPU espera, y se pierde su ventaja.
4. Usar una GPU dedicada cuesta copiar los datos a su memoria (la VRAM). Sólo conviene si hay volumen suficiente para pagar esa copia.

**La regla:** **forma del trabajo: la misma operación sobre muchos datos independientes va a la GPU (importa el throughput, cuántos datos terminas por segundo); decisiones distintas, pasos dependientes o la latencia de cada petición van a la CPU.** Lo enseña [[paralelismo-performance-energia|Paralelismo, performance y energía]].

El billón sale de 10,000³: cada uno de los 10⁸ resultados necesita 10,000 multiplicaciones. En b) y d) la GPU gana sólo si el volumen justifica copiar los datos; con pocas imágenes, la copia puede tardar más que el cálculo (ejercicio 7).

**Error común:** «la GPU tiene más núcleos, así que siempre gana». En a), c) y e) cada paso decide algo distinto, y la mayoría de las unidades de la GPU no tendría nada útil que hacer.
:::

::: problem {#xa-5 title="5 · ¿Cuánto tarda el entrenamiento?"}
Entrenar un modelo requiere **6 × 10¹⁸ FLOP**. Tu GPU anuncia **300 TFLOPS**, pero en la práctica tu código aprovecha sólo el **40 %**. ¿Cuánto tarda, en horas?
:::

::: hint {of="xa-5"}
FLOP es trabajo y FLOPS es ritmo: tiempo = trabajo / ritmo. ¿Cuánto vale «tera»? Aplica el 40 % al ritmo.
:::

::: answer {of="xa-5"}
**Respuesta:** **Unas 13.9 horas (5 × 10⁴ segundos).**

**Por qué:**

1. **FLOP** es trabajo: cuántas operaciones hay que hacer. **FLOPS** es ritmo: cuántas operaciones por segundo.
2. Los 300 TFLOPS anunciados (tera = 10¹²) son un **pico**: el máximo del chip.
3. Tu código sólo aprovecha una fracción del pico. El ritmo real es el pico × esa fracción (40 %).
4. El tiempo es el trabajo ÷ el ritmo real. Sale en segundos; ÷ 3,600 lo pasa a horas.

**La regla:** **tiempo = trabajo (FLOP) ÷ ritmo real (FLOPS anunciados × fracción aprovechada).** Aprovechar menos baja el ritmo, así que el tiempo sube. Lo enseña [[paralelismo-performance-energia|Paralelismo, performance y energía]].

| Paso | Cuenta | Resultado |
|---|---|---|
| Ritmo anunciado | 300 × 10¹² FLOP/s | 3 × 10¹⁴ FLOP/s |
| Ritmo real (40 %) | 3 × 10¹⁴ × 0.4 | **1.2 × 10¹⁴ FLOP/s** |
| Tiempo en segundos | 6 × 10¹⁸ ÷ 1.2 × 10¹⁴ | **5 × 10⁴ s** |
| Tiempo en horas | 5 × 10⁴ ÷ 3,600 | **≈ 13.9 h** |

El 40 % es realista: el código espera datos, sincroniza y no usa todas las unidades todo el tiempo.

Matiz: el pico suele anunciarse en una precisión baja (BF16, 2 bytes por número); en FP32 (4 bytes por número) el mismo chip hace menos FLOP por segundo y tarda más.

**Compruébalo:** `python3 -c "print(6e18 / (300e12 * 0.4) / 3600)"` → `13.88888888888889`

**Error común:**

- Multiplicar el tiempo por 0.4 en vez de multiplicar el ritmo: da ≈ 2.2 h, menos que usando el 100 % del chip. Aprovechar menos el chip no puede terminar antes.
- Olvidar el 40 %: da ≈ 5.6 h, que es el tiempo al ritmo pico, un ritmo que tu código no alcanza.
:::

::: problem {#xa-6 title="6 · El techo de la memoria"}
Un chip hace **2 TFLOPS** y su memoria entrega **100 GB/s**. Calculas `C[i] = A[i] + B[i]` con números FP32, de 4 bytes. Por cada suma lees A y B y escribes C.

a) ¿Cuántos FLOP haces por byte movido?

b) ¿Cuántos GFLOPS logras como máximo?

c) ¿Ayuda cambiar a un chip con el doble de FLOPS y la misma memoria?
:::

::: hint {of="xa-6"}
Una suma es 1 FLOP. ¿Cuántos bytes mueves por suma? Si cada byte permite tantos FLOP y llegan 100 GB por segundo, ¿cuántos FLOP por segundo alcanzas?
:::

::: answer {of="xa-6"}
**Respuesta:**

- a) **1/12 ≈ 0.083 FLOP por byte movido.**
- b) **≈ 8.3 GFLOPS como máximo.**
- c) **No.** El límite es la memoria; el doble de FLOPS sube un techo que no es el que manda. Lo que ayudaría es más ancho de banda de memoria.

**Por qué:**

1. Cada suma `C[i] = A[i] + B[i]` es 1 FLOP.
2. Cada suma mueve tres números FP32 por la memoria: lee `A[i]`, lee `B[i]` y escribe `C[i]`.
3. La **intensidad aritmética** es FLOP ÷ bytes movidos. Eso contesta a).
4. El **techo de memoria** es ancho de banda × intensidad: cuántos FLOP por segundo alcanza a alimentar la memoria. Los bytes se cancelan: (bytes/s) × (FLOP/byte) = FLOP/s.
5. El **techo de cómputo** es lo que el chip podría calcular si nunca esperara datos.
6. El rendimiento es el **menor** de los dos techos. Eso contesta b).

**La regla:** **Roofline: rendimiento máximo = el menor entre el techo de cómputo y (ancho de banda × intensidad aritmética). Mejorar el techo que no manda no cambia nada.** [[paralelismo-performance-energia|Paralelismo, performance y energía]] hace exactamente esta suma con estos números.

| Paso | Cuenta | Resultado |
|---|---|---|
| Bytes por suma | 4 (leer A) + 4 (leer B) + 4 (escribir C) | 12 bytes |
| FLOP por suma | una suma | 1 FLOP |
| a) Intensidad | 1 FLOP ÷ 12 bytes | **1/12 ≈ 0.083 FLOP/byte** |
| Techo de memoria | 100 GB/s × 1/12 FLOP/byte | 8.3 GFLOPS |
| Techo de cómputo | 2 TFLOPS | 2,000 GFLOPS |
| b) Manda el menor | el menor de 8.3 y 2,000 | **8.3 GFLOPS** |

8.3 GFLOPS es menos del 0.5 % de los 2,000 GFLOPS: el chip pasa casi todo el tiempo esperando datos.

**c)** Cambia un techo a la vez y vuelve a tomar el menor:

| Chip | Techo de memoria | Techo de cómputo | Manda |
|---|---|---|---|
| Original | 8.3 GFLOPS | 2,000 GFLOPS | 8.3 GFLOPS |
| Doble de FLOPS | 8.3 GFLOPS | **4,000 GFLOPS** | 8.3 GFLOPS (sin cambio) |
| Doble de ancho de banda (200 GB/s) | **16.7 GFLOPS** | 2,000 GFLOPS | **16.7 GFLOPS** |

Los dos techos se igualan en 2,000 GFLOPS ÷ 100 GB/s = 20 FLOP/byte. Por debajo de esa intensidad manda la memoria. Esta suma tiene 0.083 FLOP/byte: 240 veces por debajo.

**Compruébalo:** `python3 -c "print(100e9 * (1/12) / 1e9)"` → `8.333333333333332`

**Error común:**

- Contar sólo las lecturas (8 bytes): da 0.125 FLOP/byte y 12.5 GFLOPS. Escribir `C[i]` también cruza la memoria: son 12 bytes.
- Contestar b) con 2 TFLOPS: ése es el techo de cómputo, y aquí nunca se alcanza.
:::

::: problem {#xa-7 title="7 · ¿Vale la pena la copia?"}
Tienes 1 GB de datos en RAM. La GPU los procesa en 5 ms, y la CPU en 200 ms. Copiar a la GPU viaja a unos 25 GB/s, y el resultado de vuelta es pequeño.

a) ¿Quién termina antes?

b) ¿Y si la CPU tardara 30 ms?
:::

::: hint {of="xa-7"}
El tiempo de la GPU no es sólo su cálculo: suma lo que tarda el viaje de los datos hasta ella.
:::

::: answer {of="xa-7"}
**Respuesta:**

- a) **Termina antes la GPU: 45 ms contra 200 ms de la CPU.**
- b) **Termina antes la CPU: 30 ms contra 45 ms de la GPU.**

**Por qué:**

1. Los datos empiezan en la RAM. La GPU calcula sobre datos en su propia memoria, la VRAM, así que primero hay que copiarlos.
2. El tiempo de copia es el tamaño de los datos ÷ la velocidad de la copia.
3. El tiempo total de la GPU es copiar + calcular + traer el resultado (pequeño, así que ≈ 0). Ese total es el mismo en a) y en b), porque sólo cambia la CPU.
4. En cada caso se compara el total de la GPU contra el tiempo de la CPU. Gana el menor.

**La regla:** **compara caminos completos: tiempo de la GPU = copiar los datos + calcular + devolver el resultado. La GPU conviene sólo si la CPU tarda más que ese total** (aquí, más de 45 ms). Lo enseña [[memoria-y-datos|Memoria y movimiento de datos]], en «Dos caminos hacia el cómputo».

| Paso en la GPU | Cuenta | Tiempo |
|---|---|---|
| Copiar 1 GB a la GPU | 1 GB ÷ 25 GB/s = 0.04 s | 40 ms |
| Calcular en la GPU | dato del enunciado | 5 ms |
| Traer el resultado | es pequeño | ≈ 0 ms |
| **Total GPU** | 40 + 5 | **45 ms** |

| Caso | CPU | GPU (copia + cálculo) | Gana |
|---|---|---|---|
| a) | 200 ms | 45 ms | **GPU** |
| b) | 30 ms | 45 ms | **CPU** |

En b), la copia sola (40 ms) ya tarda más que todo el trabajo en la CPU (30 ms).

Por eso un trabajo corto rara vez conviene en la GPU, y por eso conviene dejar los datos en la GPU entre un paso y el siguiente en vez de copiarlos de ida y vuelta.

**Compruébalo:** `python3 -c "print(1e9 / 25e9 * 1000 + 5)"` → `45.0`

**Error común:** comparar sólo cálculo contra cálculo (5 ms en GPU contra 30 ms en CPU) y elegir la GPU en b). Esos 5 ms ignoran los 40 ms de copia, que se pagan sí o sí.
:::

::: problem {#xa-8 title="8 · GHz contra trabajo"}
El chip X corre a **5 GHz** y termina en promedio **2 instrucciones por ciclo**. El chip Y corre a **3.5 GHz** y termina **4 instrucciones por ciclo**. Para un programa de un solo hilo que no espera a la memoria, ¿cuál es más rápido?
:::

::: hint {of="xa-8"}
Instrucciones por segundo = ciclos por segundo × instrucciones por ciclo.
:::

::: answer {of="xa-8"}
**Respuesta:** **El chip Y. Termina 14 × 10⁹ instrucciones por segundo contra 10 × 10⁹ del chip X: un 40 % más, aunque tiene menos GHz.**

**Por qué:**

1. GHz son miles de millones de ciclos de reloj por segundo. Dicen qué tan seguido hay un tick, no cuánto trabajo sale de cada tick.
2. Las instrucciones por ciclo dicen cuántas instrucciones termina el chip en cada tick. Dependen de su microarquitectura, la organización interna del chip.
3. El trabajo por segundo es el producto de los dos números. Se comparan los productos, no los GHz.

**La regla:** **instrucciones por segundo = frecuencia (ciclos por segundo) × instrucciones por ciclo. Los GHz solos no comparan dos chips distintos.** Lo enseña [[compute-instrucciones-cpu|Compute, instrucciones y CPU]], en «Instrucciones, ciclos y pipeline».

| Chip | Ciclos por segundo | Instrucciones por ciclo | Instrucciones por segundo |
|---|---|---|---|
| X | 5 GHz = 5 × 10⁹ | 2 | 5 × 10⁹ × 2 = 10 × 10⁹ |
| Y | 3.5 GHz = 3.5 × 10⁹ | 4 | 3.5 × 10⁹ × 4 = **14 × 10⁹** |

14 × 10⁹ ÷ 10 × 10⁹ = 1.4: Y termina 40 % más instrucciones por segundo.

La cuenta vale por las dos condiciones del enunciado. Con **un solo hilo**, cuenta un solo núcleo, así que no importa cuántos núcleos tenga cada chip. **Sin esperar a la memoria**, el núcleo nunca se queda parado; si el programa esperara datos, mandaría la memoria y ninguno de los dos números.

**Compruébalo:** `python3 -c "print(3.5e9 * 4 / (5e9 * 2))"` → `1.4`

**Error común:** elegir X porque 5 GHz es más que 3.5 GHz. Eso compara sólo uno de los dos factores: X tiene 1.43 veces más reloj, pero Y termina el doble de instrucciones por ciclo.
:::

**Repasa:** [[paralelismo-performance-energia|Paralelismo, performance y energía]] y [[compute-instrucciones-cpu|Compute, instrucciones y CPU]].

## Parte 3 · ISA y sistema operativo

::: problem {#xa-9 title="9 · El binario que no corre"}
Compilas un programa en C en tu laptop x86-64 y copias el ejecutable a una Raspberry Pi, que es ARM. ¿Corre? ¿Y un script de Python copiado igual?
:::

::: hint {of="xa-9"}
¿En qué está escrito un ejecutable compilado? ¿Y quién lee un script de Python?
:::

::: answer {of="xa-9"}
**Respuesta:**

- El binario de C: **no corre.** Está escrito en instrucciones x86-64 y la CPU de la Pi entiende instrucciones ARM. Hay que recompilar el código fuente (aquí lo llamamos `hola.c`) para ARM.
- El script de Python: **sí corre, si la Pi tiene Python instalado.**

**Por qué:**

1. Compilar traduce tu código C a instrucciones de máquina de **una ISA concreta**; en tu laptop, x86-64.
2. La ISA es el contrato entre el software y el procesador: qué instrucciones existen y cómo se escriben en bytes. x86-64 y ARM son contratos distintos.
3. La CPU ARM de la Pi no entiende instrucciones x86-64, y el sistema operativo de la Pi rechaza el ejecutable sin correrlo.
4. Un script de Python no contiene instrucciones de máquina: es texto que lee el **intérprete** `python3`.
5. El intérprete de la Pi ya está compilado para ARM. Por eso el mismo texto corre en las dos máquinas.

**La regla:** **ISA: un ejecutable compilado sólo corre en la ISA para la que se compiló. Lo que se lleva de una ISA a otra es el código fuente o el script, no el ejecutable.** Lo enseña [[compute-instrucciones-cpu|Compute, instrucciones y CPU]], en «La ISA es el contrato».

**Compruébalo:** el comando `file` dice para qué ISA está compilado un ejecutable.

```text
$ gcc hola.c -o hola
$ file hola
hola: ELF 64-bit LSB pie executable, x86-64, ...
```

Copiado a la Pi y ejecutado, bash lo rechaza:

```text
$ ./hola
bash: ./hola: cannot execute binary file: Exec format error
```

Matiz del script: si usa bibliotecas con partes compiladas, como numpy, esas partes también deben existir en versión ARM. Por eso a veces `pip install` funciona en una máquina y en otra no.

**Error común:** «C es portable, así que el ejecutable también». Lo portable es el código fuente: `hola.c` recompilado en la Pi sí corre. El archivo `hola` ya compilado para x86-64, no.
:::

::: problem {#xa-10 title="10 · ¿Quién habla con el disco?"}
En Python escribes `open("datos/ventas.csv").read()`. ¿Tu programa le habla al disco directamente? Nombra dos cosas que hace el sistema operativo en ese momento.
:::

::: hint {of="xa-10"}
Recuerda la definición del curso: el sistema operativo es el intermediario. ¿Qué traduce, qué controla y qué reparte?
:::

::: answer {of="xa-10"}
**Respuesta:**

- ¿Tu programa le habla al disco directamente? **No.** Python le pide al sistema operativo que abra y lea el archivo, y el sistema operativo es quien habla con el disco.
- Dos cosas que hace el sistema operativo en ese momento: **cualesquiera dos de los pasos 2 a 6 de abajo, bien explicadas.** Por ejemplo, **traduce el nombre `datos/ventas.csv` a los bloques del disco donde están esos bytes** y **revisa si tu usuario tiene permiso de leerlo**.

**Por qué:**

1. `open(...)` y `.read()` se convierten en peticiones al sistema operativo: «abre este archivo» y «dame sus bytes».
2. El sistema operativo **traduce la ruta** `datos/ventas.csv` a los bloques del disco donde viven esos bytes. Esa traducción es el **sistema de archivos**.
3. El sistema operativo **revisa los permisos**: si tu usuario puede leer ese archivo.
4. El sistema operativo **controla el disco** a través de su driver, si los bytes no están ya en memoria.
5. El sistema operativo **pone los bytes en la memoria de tu programa**; `.read()` te los entrega como texto.
6. Mientras el disco responde, el sistema operativo **reparte la CPU**: deja correr a otros programas.

**La regla:** **el sistema operativo es el intermediario: ningún programa habla con el hardware; le pide al sistema operativo, que administra memoria y almacenamiento, reparte la CPU, controla los periféricos y expone un sistema de archivos.** Lo enseña [[software-libre-y-sistemas-operativos|Software libre y sistemas operativos]], en «Qué es realmente un sistema operativo».

**Compruébalo:** quítale los permisos al archivo (como usuario normal, no root) y repite la lectura. Python no decide nada: recibe el rechazo del sistema operativo (`Errno 13`).

```text
$ chmod 000 datos/ventas.csv
$ python3 -c 'open("datos/ventas.csv").read()'
Traceback (most recent call last):
...
PermissionError: [Errno 13] Permission denied: 'datos/ventas.csv'
$ chmod 644 datos/ventas.csv
```

El último `chmod 644` le devuelve al archivo sus permisos de lectura.

Por esta mediación, la misma línea de Python puede comportarse distinto en Windows y en Linux: cambian las rutas, los permisos y el sistema de archivos.

**Error común:** «Python abre el archivo y lo lee del disco». Python ni siquiera decide si puedes leerlo: el `PermissionError` de arriba lo decidió el sistema operativo.
:::

::: problem {#xa-11 title="11 · ¿Dónde está el cuello de botella?"}
Un ETL nocturno lee **2 TB** de CSV desde un SSD que entrega unos **2 GB/s**, filtra filas con una condición simple y escribe un resultado pequeño. Alguien propone comprar una GPU para acelerarlo. ¿Ayudaría?
:::

::: hint {of="xa-11"}
Calcula cuánto tarda sólo en **leer** los 2 TB. Luego pregúntate cuánto cálculo hay por cada byte leído.
:::

::: answer {of="xa-11"}
**Respuesta:** **Casi seguro que no. Sólo leer los 2 TB del SSD tarda 1,000 s (unos 17 minutos), y una GPU no baja ese tiempo: el cuello de botella es el ancho de banda del almacenamiento, no el cálculo.**

**Por qué:**

1. El tiempo de lectura es el tamaño de los datos ÷ el ancho de banda del SSD.
2. Ningún procesador termina antes de que le lleguen los datos. Con CPU o con GPU, ese tiempo de lectura es el mínimo.
3. Filtrar con una condición simple es muy poco cálculo por cada byte leído: es un trabajo de intensidad aritmética muy baja, como la suma del ejercicio 6.
4. Con GPU, los bytes siguen saliendo del SSD a 2 GB/s y además hay que copiarlos de la RAM a la GPU. El total no baja del tiempo de lectura.

**La regla:** **un trabajo va al ritmo de su recurso más lento. Antes de comprar hardware, identifica qué se agota primero (capacidad, latencia, ancho de banda o cálculo) y mejora ése.** Aquí se agota el ancho de banda del SSD. Lo enseñan [[memoria-y-datos|Memoria y movimiento de datos]], en «Diagnosticar antes de comprar», y la guía de decisión de [[ia-escala-decision|IA, escala y selección de hardware]].

| Paso | Cuenta | Resultado |
|---|---|---|
| Leer 2 TB a 2 GB/s | 2,000 GB ÷ 2 GB/s | **1,000 s ≈ 17 min** |
| Cálculo por byte leído | una condición simple por fila | muy poco |
| Con GPU | los datos siguen llegando a 2 GB/s, más la copia a la GPU | **≥ 1,000 s** |

Lo que sí ayuda, porque ataca la lectura:

- un formato **columnar** como Parquet, para leer sólo las columnas necesarias;
- comprimir, para leer menos bytes;
- un almacenamiento más rápido;
- repartir la lectura entre varias máquinas.

**Compruébalo:** `python3 -c "print(2e12 / 2e9 / 60)"` → `16.666666666666668` (minutos)

**Error común:** «la GPU tiene muchos más FLOPS, así que filtra más rápido». Más FLOPS sube el techo de cálculo, y aquí ese techo no es el que manda: el SSD entrega los mismos 2 GB/s a cualquier procesador.
:::

**Repasa:** [[compute-instrucciones-cpu|Compute, instrucciones y CPU]], [[software-libre-y-sistemas-operativos|Software libre y sistemas operativos]] y [[ia-escala-decision|IA, escala y selección de hardware]].
