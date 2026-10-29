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

**Página 9 · Cómputo y concurrencia** · Pregunta: **¿por qué una petición sin respuesta no dice si falló?** · Respuesta: **la red no acota el retardo ni garantiza la entrega, así que un plazo vencido solo indica que el cliente dejó de esperar.**

Recordatorio: $d$ es la duración de la vida de una tarea ([[notacion-computo]]). Ese tiempo se reparte entre ejecutar y esperar ([[donde-pasa-el-tiempo]]).

## A. Relojes y causalidad

| Término | Definición |
|---|---|
| **Componente** | Un **componente** es un proceso o una máquina independiente. |
| **Mensaje** | Un **mensaje** consiste en datos enviados entre componentes. |
| **Reloj local** | Un **reloj local** es el reloj propio de cada componente; dos componentes no lo comparten. |

**Definición.** **A precede a B** cuando A ocurre antes que B en el mismo componente, cuando A envía el mensaje que B recibe, o cuando hay una cadena de estas dos relaciones; es un orden parcial.

Dos eventos son **concurrentes** si ninguno precede al otro según la relación anterior: el modelo no les asigna orden.

::: figure {#cmp-dist-relojes title="Con relojes desfasados, restar marcas no da el tiempo de tránsito"}
![Dos componentes, A y B, con el reloj de B 40 ms atrás; A envía en su marca 100 ms, el mensaje tarda 20 ms y B lo recibe en su marca 80 ms](_assets/cmp-dist-relojes.svg)
Cómo leerla: ambos ejes representan el mismo instante real con números distintos; la flecha causal va de A a B.
:::

**Cuenta.** Restar la marca de envío en A a la marca de llegada en B mezcla el tiempo de tránsito del mensaje y el desfase entre relojes.

$$\text{marca}_B-\text{marca}_A=\text{tránsito}+\text{desfase}$$

Con los valores del ejemplo, el tiempo de tránsito es 20 ms y el desfase de B es −40 ms, ambos **supuestos**. El cálculo da $80-100=-20$ ms $=20\ \text{ms}+(-40\ \text{ms})$.

La resta es negativa: según las marcas, el mensaje llegó antes de enviarse. Sin conocer el desfase y su incertidumbre, la diferencia no mide el tiempo de tránsito.

**Ejemplo.** El registro de A dice «envié a las 100 ms» y el de B dice «recibí a las 80 ms». Ordenarlos por marca coloca la recepción antes del envío, aunque el envío precede a la recepción por definición.

**Arquitectura.**
- **Qué es:** reconstruir el orden entre máquinas mediante mensajes, no mediante relojes. Cada evento se ordena por lo que recibió o envió antes.
- **Cuándo sí:** cuando el orden determina el resultado, como identificar la última escritura o qué evento causó otro.
- **Cuándo no:** para medir duraciones dentro de un componente, porque basta un solo reloj local monotónico.
- **Qué cuesta:** cada mensaje lleva información de orden, que el sistema debe mantener. Dos eventos concurrentes no tienen orden causal: uno ocurrió antes en tiempo real, pero el sistema no puede determinarlo.
- **Sistema real:** el identificador de petición que un servicio pasa a los siguientes permite ordenar eventos por causa, no por marca, en trazas distribuidas.

**Decisión que permite:** no comparar marcas de máquinas distintas para ordenar eventos ni para medir tiempos de tránsito.

## B. Resultado desconocido

| Término | Definición |
|---|---|
| **Plazo** | El **plazo** $t_{\max}$ es el tiempo máximo que espera el cliente; no es $d$. |
| **Fallo parcial** | Un **fallo parcial** ocurre cuando falla un componente o un mensaje, pero el resto continúa. |
| **Operación idempotente** | Una **operación idempotente** produce el mismo efecto al repetirse que al ejecutarse una vez. |

**Definición.** Un **resultado desconocido** es el estado del cliente que, al vencer $t_{\max}$ sin respuesta, ignora si la operación se ejecutó.

Ocurre por un fallo parcial y porque la red no acota el retardo ni garantiza la entrega; un reloj común no lo resolvería, porque $t_{\max}$ se mide con el reloj local del cliente.

::: figure {#cmp-dist-tres-causas title="Tres fallos distintos se ven igual para el cliente"}
![Tres carriles de una misma petición sin respuesta tras el plazo: se pierde la ida, el servidor ejecuta y se pierde la respuesta, el servidor tarda más que el plazo](_assets/cmp-dist-tres-causas.svg)
Cómo leerla: el cliente observa lo mismo en los tres carriles; solo cambia lo ocurrido del otro lado.
:::

**Ejemplo.** Un cliente pide «cobrar 100 pesos» y no recibe respuesta en $t_{\max}$. Caben tres explicaciones, las del dibujo: la petición se perdió y no hubo cobro; el servidor cobró y la respuesta se perdió (lo mismo ocurre si cayó justo después de cobrar); o el servidor sigue trabajando. En los tres casos el cliente observa lo mismo.

**Arquitectura.**
- **Qué es:** interpretar el plazo vencido como «dejé de esperar», no como «falló». El servidor puede seguir trabajando porque el plazo no cancela la operación.
- **Cuándo sí:** en toda llamada por red. El plazo evita esperas ilimitadas (ver timeouts en [[arquitectura-y-estrategia]]) y libera recursos del cliente, como los permisos de [[concurrencia-acotada]].
- **Cuándo no:** para concluir que la operación no ocurrió o repetir sin precaución una operación con efectos.
- **Qué cuesta:** reintentar sin más puede ejecutar la operación dos veces. La idempotencia lo evita, pero exige reconocer la repetición, por ejemplo mediante una clave reutilizada al reintentar.
- **Sistema real:** las APIs de pagos aceptan una clave de idempotencia para que un reintento tras un plazo vencido no cobre dos veces.

**Decisión que permite:** poner un plazo en cada llamada, reintentar solo operaciones idempotentes y consultar el estado cuando el resultado es desconocido.

## Si hay tiempo

- Los relojes lógicos (Lamport, 1978) asignan a cada evento un contador que respeta «precede»: si A precede a B, el contador de A es menor; la inversa no vale.

## Notebook

- Celda 9.1: simula dos relojes, el de B 40 ms atrás, y muestra la resta de marcas de un mensaje enviado en 100 ms con tiempo de tránsito de 20 ms. Salida esperada: -20 ms.
