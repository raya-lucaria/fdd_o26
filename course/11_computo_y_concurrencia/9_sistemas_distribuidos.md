---
id: sistemas-distribuidos
title: "Sistemas distribuidos"
nav_title: "Sistemas distribuidos"
summary: "Por qué una petición sin respuesta no dice si falló: las marcas de relojes distintos no ordenan eventos entre máquinas, y como la red no acota el retardo ni garantiza la entrega, un plazo vencido solo dice que el cliente dejó de esperar."
status: ready
estimated_time: 8m
tags: [concurrencia, sistemas-distribuidos, relojes, causalidad, timeouts, idempotencia]
prerequisites: [donde-pasa-el-tiempo, arquitectura-y-estrategia]
---

# Sistemas distribuidos

**Página 9 · Cómputo y concurrencia** · Pregunta: **¿por qué una petición sin respuesta no dice si falló?** · Respuesta: **la red no acota el retardo ni garantiza la entrega. Un plazo vencido solo indica que el cliente dejó de esperar.**

## A. Relojes y causalidad

| Término | Definición |
|---|---|
| **Componente** | Proceso o máquina independiente. |
| **Mensaje** | Datos enviados entre componentes. |
| **Reloj local** | Reloj propio de cada componente; no se comparte. |

::: definition {#cmp-def-precede title="La relación «precede» entre eventos"}
**Definición.** **X precede a Y** cuando una cadena causal permite afirmar que X ocurrió antes que Y, sin mirar relojes. Es un orden parcial: no todo par de eventos queda ordenado.

**Variables.**

- $X$: un evento cualquiera, sin unidad.
- $Y$: un evento cualquiera, sin unidad.
- $m$: un mensaje, sin unidad; enviarlo y recibirlo son eventos distintos.
- $Z$: un evento intermedio, sin unidad.

**Reglas.** $X$ precede a $Y$ si se cumple al menos una:

1. **Orden local.** Ambos eventos ocurren en un componente y $X$ ocurre antes que $Y$.
2. **Envío y recepción.** $X$ envía un mensaje $m$ e $Y$ recibe ese mismo $m$.
3. **Transitividad.** Existe un evento $Z$ tal que $X$ precede a $Z$ y $Z$ precede a $Y$.

**Por qué es así.**

- Un componente observa sus eventos en una sola secuencia.
- Un mensaje no puede recibirse antes de enviarse.
- La transitividad encadena ambas reglas sin usar marcas de tiempo.

**Concurrentes.** Dos eventos son **concurrentes** si ninguno precede al otro según estas reglas.
:::

**Ejemplo paso a paso.** Tres eventos y dos mensajes.

1. **Datos.** Componentes A, B y C. A envía $m_1$ en $a$; B envía $m_2$ en $b$. C recibe ambos mensajes en $c$.
2. **Regla 2 sobre $m_1$.** $a$ envía $m_1$ y $c$ lo recibe → $a$ precede a $c$.
3. **Regla 2 sobre $m_2$.** $b$ envía $m_2$ y $c$ lo recibe → $b$ precede a $c$.
4. **Par $a$ y $b$.** No comparten componente, mensaje ni cadena causal → ninguno precede al otro.
5. **Lectura.** $a$ y $b$ son concurrentes. El modelo no puede determinar cuál ocurrió primero en tiempo real.

::: figure {#cmp-dist-relojes title="Con relojes desfasados, restar marcas no da el tiempo de tránsito"}
![Dos componentes, A y B, con el reloj de B 40 ms atrás; A envía en su marca 100 ms, el mensaje tarda 20 ms y B lo recibe en su marca 80 ms](_assets/cmp-dist-relojes.svg)
Cómo leerla: ambos ejes representan el mismo instante real con números distintos; la flecha causal va de A a B.
:::

::: definition {#cmp-def-resta-marcas title="Resta de marcas entre relojes distintos"}
**Qué dice.** Restar la marca de llegada de B menos la marca de envío de A no mide el tránsito. Mide el tránsito más la diferencia entre ambos relojes.

**Variables.**

- $\text{marca}_A$: lectura del reloj local de A al enviar, en ms.
- $\text{marca}_B$: lectura del reloj local de B al recibir, en ms.
- $\text{tránsito}$: tiempo real de llegada, en ms (el que se quería medir).
- $\text{desfase}$: reloj de B menos reloj real, en ms; es negativo si B va atrasado.

**Fórmula.**

$$\text{marca}_B-\text{marca}_A=\text{tránsito}+\text{desfase}$$

**Por qué es así.**

- Se supone que el reloj de A marca la hora real.
- $\text{marca}_A=t_{\text{envío}}$ y $\text{marca}_B=t_{\text{envío}}+\text{tránsito}+\text{desfase}$.
- Al restar, $t_{\text{envío}}$ se cancela; quedan el tránsito y el desfase.
:::

**Ejemplo paso a paso.**

1. **Datos (supuestos).** El reloj de B va 40 ms atrás, así que $\text{desfase}=-40$ ms. El tránsito real es 20 ms.
2. **Marca de envío.** A envía cuando su reloj marca $\text{marca}_A=100$ ms.
3. **Marca de llegada.** El mensaje llega 20 ms después; B marca $100+20-40=80$ ms.
4. **Resta.** $\text{marca}_B-\text{marca}_A=80-100=-20$ ms.
5. **Comprobación.** $\text{tránsito}+\text{desfase}=20+(-40)=-20$ ms, igual a la resta.
6. **Lectura.** Las marcas colocan la llegada antes del envío. Sin conocer el desfase y su incertidumbre, la resta no mide el tránsito.

**Ejemplo.** A registra «envié a las 100 ms» y B registra «recibí a las 80 ms». Ordenar por marca invierte el orden causal.

**Arquitectura.**
- **Qué es:** reconstruir el orden mediante mensajes; cada evento se ordena por lo enviado o recibido antes.
- **Cuándo sí:** cuando importa identificar la última escritura o qué evento causó otro.
- **Cuándo no:** para medir duraciones dentro de un componente; basta un reloj local monotónico.
- **Qué cuesta:** cada mensaje lleva información que el sistema mantiene. Los eventos concurrentes carecen de orden causal.
- **Sistema real:** un identificador de petición propagado entre servicios ordena por causa las trazas distribuidas.

**Decisión que permite:** no comparar marcas de máquinas distintas para ordenar eventos ni medir tiempos de tránsito.

## B. Resultado desconocido

| Término | Definición |
|---|---|
| **Plazo** | El **plazo** $t_{\max}$ es el tiempo máximo que espera el cliente. |
| **Fallo parcial** | Falla un componente o mensaje, pero el resto continúa. |
| **Operación idempotente** | Repetirla produce el mismo efecto que ejecutarla una vez. |

**Definición.** Un **resultado desconocido** aparece cuando vence $t_{\max}$ sin respuesta. El cliente ignora si la operación se ejecutó.

Ocurre por un fallo parcial y porque la red no acota el retardo ni garantiza la entrega. Un reloj común no lo resolvería: $t_{\max}$ usa el reloj local del cliente.

::: figure {#cmp-dist-tres-causas title="Tres fallos distintos se ven igual para el cliente"}
![Tres carriles de una misma petición sin respuesta tras el plazo: se pierde la ida, el servidor ejecuta y se pierde la respuesta, el servidor tarda más que el plazo](_assets/cmp-dist-tres-causas.svg)
Cómo leerla: el cliente observa lo mismo en los tres carriles; solo cambia lo ocurrido del otro lado.
:::

::: definition {#cmp-def-plazo title="Plazo vencido y sus tres causas"}
**Qué dice.** El **plazo** $t_{\max}$ es el tiempo que el cliente espera. Si vence sin respuesta, solo sabe que dejó de esperar.

**Variables.**

- $t_{\max}$: plazo del cliente, en ms, medido con su reloj local.

**Condición.** Hay plazo vencido cuando el cliente espera $t_{\max}$ sin recibir respuesta.

**Causas posibles.** Las tres producen la misma observación:

1. **Se perdió la ida.** La petición no llegó; la operación no se ejecutó.
2. **Se perdió la vuelta.** El servidor ejecutó, o cayó justo después, pero la respuesta no llegó.
3. **Servidor lento.** Sigue trabajando y responderá después de $t_{\max}$.

**Por qué es así.**

- La red no acota el retardo ni garantiza la entrega; solo la causa 1 implica que la operación no ocurrió.
:::

**Ejemplo paso a paso.**

1. **Datos.** El cliente pide «cobrar 100 pesos» y espera $t_{\max}=2000$ ms sin recibir respuesta.
2. **Causa 1.** La petición se perdió → cobro: 0 pesos.
3. **Causa 2.** El servidor cobró y la respuesta se perdió → cobro: 100 pesos.
4. **Causa 3.** El servidor sigue procesando → cobro: 100 pesos al terminar.
5. **Lectura.** El cliente observa lo mismo; el resultado real va de 0 a 100 pesos. Reintentar sin protección puede cobrar 200.

**Arquitectura.**
- **Qué es:** interpretar el plazo vencido como «dejé de esperar», no como «falló». El plazo no cancela la operación.
- **Cuándo sí:** en toda llamada por red. Evita esperas ilimitadas y libera recursos, incluidos permisos de [[concurrencia-acotada]].
- **Cuándo no:** para concluir que la operación no ocurrió o repetir sin protección una operación con efectos.
- **Qué cuesta:** reintentar puede duplicar efectos. La idempotencia exige reconocer repeticiones mediante una clave reutilizada.
- **Sistema real:** las APIs de pagos aceptan claves de idempotencia para evitar cobros dobles tras un plazo vencido.

**Decisión que permite:** poner un plazo en cada llamada, reintentar solo operaciones idempotentes y consultar resultados desconocidos. Ver [[arquitectura-y-estrategia]].

## Si hay tiempo

- Los relojes lógicos (Lamport, 1978) usan contadores: si A precede a B, el contador de A es menor; la inversa no vale.

## Katas

::: problem {#cmp-kata-p9-1 title="Kata 1 · ¿Puedo reintentar el cobro?"}
Un cliente envía «cobrar 100 pesos» con $t_{\max}=2000$ ms y no recibe respuesta. No lleva clave de idempotencia. ¿Reintentas de inmediato? ¿Qué harías?
:::

::: answer {of="cmp-kata-p9-1"}
**Elige:** no reintentar; consultar primero el estado. Si el servicio acepta idempotencia, reintentar con la misma clave es seguro.

**Porque:** las causas 2 y 3 ya pueden haber cobrado 100 pesos; repetir cobraría 200 pesos.

**Descarta:** reintentar sin protección o concluir «no se cobró»; esto último solo ocurre en la causa 1.
:::

::: problem {#cmp-kata-p9-2 title="Kata 2 · ¿Qué plazo pongo?"}
Una consulta tarda normalmente 30 ms y, en el 99 % de los casos, menos de 120 ms. Sin plazo, el servidor deja de responder. ¿Cuándo se entera el cliente? ¿Qué plazo pondrías?
:::

::: answer {of="cmp-kata-p9-2"}
**Elige:** un plazo finito, por ejemplo $t_{\max}=300$ ms. El valor exacto es una decisión, no una fórmula.

**Porque:** sin plazo espera indefinidamente y retiene recursos, incluidos permisos de [[concurrencia-acotada]]. La consulta no tiene efectos; reintentar es seguro.

**Descarta:** $t_{\max}=30$ ms, porque vencería durante llamadas sanas, y no poner plazo.
:::

::: problem {#cmp-kata-p9-3 title="Kata 3 · ¿Cuál ocurrió antes?"}
Una tienda tiene dos servidores. Un log dice «pago recibido 14:03:07»; otro, «pedido creado 14:03:05». Los relojes no están sincronizados y el desfase se desconoce. ¿Cuál ocurrió antes? ¿Qué necesitas saber?
:::

::: answer {of="cmp-kata-p9-3"}
**Elige:** no concluir nada por las marcas. Necesitas una relación causal, como un identificador del pedido registrado al recibir el pago.

**Porque:** cada marca incluye el desfase de su reloj. Un desfase de 3 s puede invertir 14:03:05 y 14:03:07.

**Descarta:** ordenar por marca o interpretar su resta como tránsito. La regla 2 de «precede» establece el orden sin relojes.
:::

## Notebook

- Celda 9.1: simula dos relojes, con B 40 ms atrás. Envía en 100 ms con tránsito de 20 ms; salida esperada: -20 ms.
