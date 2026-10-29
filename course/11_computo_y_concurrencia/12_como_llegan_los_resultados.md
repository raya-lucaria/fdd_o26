---
id: como-llegan-los-resultados
title: "Cómo llegan los resultados"
nav_title: "Cómo llegan los resultados"
summary: "Cuando la respuesta no está lista, el cliente pregunta (polling, long polling) o recibe un aviso (SSE, WebSocket, webhook): cada opción cambia cuántas peticiones haces, cuánto tardas en enterarte y qué recurso retiene el servidor, con una cuenta de Little y la demostración D2."
status: ready
estimated_time: 20m
tags: [concurrencia, polling, long-polling, sse, websocket, webhook, little]
prerequisites: [asincrono-y-el-event-loop, pools-y-recursos]
---

# Cómo llegan los resultados

**Página 12 · Cómputo y concurrencia** · Pregunta: **si la respuesta no está lista cuando preguntas, ¿cómo te enteras?** · Respuesta: **pregunta mediante polling o long polling, o recibe un aviso mediante SSE, WebSocket o webhook. Cada opción cambia las peticiones, la demora y los recursos retenidos.**

Una **tarea** es un flujo secuencial de trabajo que un runtime o el programa trata como unidad.

## A. Preguntar

**Definición.**

- El **polling** repite una petición cada $\Delta$ segundos.
- El **long polling** retiene una consulta hasta que haya una novedad o venza un plazo.
- Una **conexión** es un canal abierto entre dos programas; su extremo en cada programa es un **socket** (el "enchufe" que el programa usa para enviar y recibir).
- **Keep-alive** deja la conexión abierta después de una respuesta, para mandar la siguiente petición sin abrir otra.

**Figura.** Un mismo evento, tres formas de enterarse.

::: figure {#cmp-gantt-resultados title="El polling se entera en la siguiente consulta; long polling y SSE, al ocurrir el evento"}
![Tres carriles con un evento a los 10 s: el polling consulta en 3, 6, 9 y 12 s y se entera en la cuarta; el long polling mantiene una consulta pendiente que responde al evento; SSE mantiene una respuesta abierta que lo recibe a los 10 s.](_assets/cmp-gantt-resultados.svg)
Cómo leerla: cada barra representa una conexión o consulta; el rombo marca el evento.
:::

**Cuenta.** Tres cantidades salen de dos datos: cuántas consultas haces en total, cuántas llegan sin novedades y cuánto tardas en enterarte.

::: definition {#cmp-def-polling title="Consultas y demora del polling"}
**Qué dice.** El cliente consulta cada $\Delta$ segundos, empezando en $\Delta$. Se entera en la primera consulta que cae en el evento o después de él. Todas las consultas anteriores llegan sin novedades, y la demora es el tiempo que falta para esa consulta.

**Variables.**

- $T_{\text{evt}}$: instante en que ocurre el evento, en segundos desde que el cliente empieza a consultar.
- $\Delta$: intervalo entre consultas, en segundos. La primera consulta ocurre en $\Delta$; no hay consulta inicial.
- $\text{totales}$: número de consultas hasta enterarse (incluida la que trae la novedad), sin unidad.
- $\text{sin novedades}$: consultas que llegan antes del evento y responden "nada todavía", sin unidad.
- $\text{demora}$: segundos entre el evento y el momento en que el cliente lo sabe.

**Fórmulas.**

$$\text{totales}=\left\lceil \frac{T_{\text{evt}}}{\Delta}\right\rceil,\qquad \text{sin novedades}=\left\lceil \frac{T_{\text{evt}}}{\Delta}\right\rceil-1,\qquad \text{demora}=\Delta\left\lceil \frac{T_{\text{evt}}}{\Delta}\right\rceil-T_{\text{evt}}$$

**Por qué es así.**

- Las consultas ocurren en $\Delta,2\Delta,3\Delta,\ldots$ La consulta $j$ cae en $j\Delta$.
- El cliente se entera en la primera $j$ con $j\Delta\ge T_{\text{evt}}$, es decir $j\ge T_{\text{evt}}/\Delta$. Esa $j$ es el entero más pequeño que cumple la desigualdad: el techo ⌈ ⌉. Redondear hacia abajo daría una consulta anterior al evento. Si $T_{\text{evt}}$ es múltiplo exacto de $\Delta$, la consulta cae justo en el evento y lo ve.
- Sin novedades es totales menos una: la última consulta es la que trae la novedad.
- La demora es el instante de esa consulta, $\Delta\lceil T_{\text{evt}}/\Delta\rceil$, menos el instante del evento: lo que falta para llegar a la siguiente consulta.
:::

**Ejemplo paso a paso.**

1. **Datos.** $T_{\text{evt}}=10$ s y $\Delta=3$ s (parámetros del ejemplo).
2. **Techo.** $10/3=3.33\ldots$ y $\lceil 3.33\ldots\rceil=4$.
3. **Instantes.** Las consultas ocurren en 3, 6, 9 y 12 s.
4. **Totales y sin novedades.** Totales: 4. Sin novedades: $4-1=3$ (las de 3, 6 y 9 s).
5. **Demora.** $3\times4-10=2$ s (la consulta de 12 s menos el evento de 10 s).
6. **Con 20 clientes.** Suponemos que todos arrancan en $t=0$ (supuesto). Totales: $20\times4=80$. Sin novedades: $20\times3=60$.
7. **Lectura.** De 80 consultas, 60 no sirvieron de nada y cada cliente esperó 2 s de más.

**Ejemplo medido.** La celda 12.1 lanza 20 clientes por modalidad contra `/listo` (polling), `/espera` (long polling) y `/eventos` (SSE) de `app_arq.py`, con un worker. El evento ocurre a los 10 s después de llamar a `/inicia`. Los intervalos se miden con reloj monotónico. Medido en 8 CPU: los 20 clientes de polling hicieron 80 consultas (calculado: 80), con demora 2.03 s. Long polling y SSE se enteraron con demora 0.05 s cada uno. Conexiones y peticiones se miden por separado porque representan recursos distintos. Polling con keep-alive conservó 20 sockets abiertos, aunque casi ninguna petición quedó pendiente. Long polling mantuvo 20 peticiones pendientes.

**Arquitectura.**

- **Qué es:** polling pregunta periódicamente; long polling espera en una consulta.
- **Cuándo sí:** usa polling si toleras la demora $\Delta$ y el servidor no puede retener conexiones. Esto ocurre con pocos clientes o proxies que cortan conexiones abiertas. Usa long polling si necesitas baja demora sin un protocolo de canal dedicado.
- **Cuándo no:** evita polling con muchos clientes y eventos raros, porque casi todas las consultas llegan sin novedades.
- **Qué cuesta:** reducir $\Delta$ baja la demora, pero aumenta las peticiones inútiles. Long polling mantiene una petición pendiente por cliente.
- **Sistema real:** una API de trabajos asíncronos devuelve un identificador que el cliente consulta.

Decisión: usa polling si toleras $\Delta$; usa long polling si necesitas baja demora sin un protocolo de canal dedicado.

## B. Que te avisen

**Definición.**

- **SSE** es una respuesta HTTP continua que envía eventos del servidor al cliente.
- Un **stream** es una respuesta que continúa enviando datos por la misma conexión.
- Un **WebSocket** es un canal bidireccional que el cliente establece sobre HTTP.
- Un **webhook** es un mecanismo donde el emisor del evento llama al receptor registrado.

**Figura.** Quién inicia y qué queda abierto.

::: figure {#cmp-push-webhook title="SSE y WebSocket los inicia el cliente y dejan una conexión abierta; el webhook lo inicia el emisor y no deja ninguna petición pendiente entre eventos"}
![Tres diagramas de secuencia: en SSE el cliente abre y el servidor envía eventos; en WebSocket el cliente abre y ambos envían; en el webhook el emisor llama al receptor.](_assets/cmp-push-webhook.svg)
Cómo leerla: la flecha de apertura marca quién inicia; la línea continua indica qué queda abierto.
:::

| Mecanismo | Quién inicia | Qué queda abierto | Recurso retenido y unidad que ejecuta | Falla típica |
|---|---|---|---|---|
| SSE | el cliente | una respuesta HTTP | una sesión por cliente; hilo o tarea, según el manejador | cliente lento: el servidor acumula envíos pendientes |
| WebSocket | el cliente | un canal bidireccional | igual que SSE | cliente lento |
| webhook | el emisor | ninguna petición pendiente entre eventos (puede conservarse una conexión keep-alive) | ninguna petición pendiente entre eventos | el emisor no puede acceder al receptor |

**Cuenta.** Cuántas sesiones tiene abiertas el servidor a la vez sale de la ley de Little ([[arquitectura-y-estrategia]]).

::: definition {#cmp-def-little-sesiones title="Ley de Little para sesiones abiertas"}
**Qué dice.** El promedio de sesiones abiertas es la rapidez con que se abren sesiones multiplicada por cuánto dura una sesión en promedio.

**Variables.**

- $L$: sesiones abiertas en promedio, en sesiones.
- $\lambda$: aperturas de sesión por segundo, en sesiones/s.
- $W$: duración media de una sesión, de que se abre a que se cierra, en segundos.

**Fórmula.**

$$L=\lambda W$$

**Por qué es así.**

- Cada segundo entran $\lambda$ sesiones y cada una se queda $W$ segundos. En un instante cualquiera siguen abiertas las que entraron durante los últimos $W$ segundos: $\lambda\times W$.
- Condición 1: régimen estable. Entran tantas sesiones como salen y $\lambda$ no cambia durante la ventana. Una corrida aislada no demuestra estabilidad.
- Condición 2: $\lambda$, $W$ y $L$ cuentan la misma población y la misma frontera (todas las sesiones SSE de un servidor, no una mezcla con otras).
- $L$ es un promedio, no el máximo instantáneo: planea con margen sobre $L$.
:::

**Ejemplo paso a paso.**

1. **Datos (supuestos del ejemplo, no medidos).** $\lambda=5$ sesiones/s y $W=40$ s.
2. **Cuenta.** $L=5\times40=200$ sesiones abiertas en promedio.
3. **Segunda situación.** Hay 2000 clientes conectados a la vez: $L=2000$. Con la misma fórmula despejamos $\lambda=L/W$. Si cada sesión dura $W=40$ s, $\lambda=2000/40=50$ aperturas/s.
4. **Lectura.** El servidor debe sostener 200 sesiones en el primer caso y 2000 en el segundo. Con la misma $W$, más aperturas por segundo significa más sesiones abiertas.
5. **Medido.** En D2 hubo `20` sesiones SSE abiertas con 20 clientes.

**Arquitectura.**

- **Qué es:** SSE y WebSocket mantienen una conexión iniciada por el cliente; un webhook envía una petición desde el emisor.
- **Cuándo sí:** usa SSE para un flujo solo del servidor al cliente. Usa WebSocket si el cliente también envía continuamente. Usa webhook entre servicios cuando el receptor tiene una dirección accesible.
- **Cuándo no:** evita SSE o WebSocket si el servidor no puede sostener tantas conexiones abiertas como $L$. Evita webhook si el emisor no puede acceder al receptor.
- **Qué cuesta:** SSE y WebSocket retienen una conexión y memoria por sesión. Un webhook exige idempotencia para tolerar duplicados. El manejador decide si cada sesión retiene un hilo o una tarea (ver [[asincrono-y-el-event-loop]]). Acota las sesiones como en [[concurrencia-acotada]].
- **Sistema real:** notificaciones de pago por webhook; tableros en vivo por SSE.

Decisión: usa SSE para servidor→cliente, WebSocket para comunicación bidireccional y webhook entre servicios con un receptor accesible.

## Si hay tiempo

- **Detalles que las cuentas omiten:** la media de la demora es $\Delta/2$ solo si el evento cae en un momento al azar entre consultas; las cuentas suponen relojes monotónicos sin deriva; con HTTP/2 varias sesiones comparten una conexión; para reanudar SSE tras reconectar, el cliente manda `Last-Event-ID` y el servidor debe haber emitido `id:` y conservar los eventos.
- **gRPC, GraphQL y SOAP** describen el contrato entre cliente y servidor, no un patrón equivalente a polling.
- **gRPC** admite llamadas unarias y tres variantes de streaming: del servidor, del cliente y bidireccional.
- **GraphQL** permite elegir los campos de la respuesta; sus suscripciones usan un canal como WebSocket o SSE.

## Katas

::: problem {#cmp-kata-p12-1 title="Kata 1 · Progreso de un trabajo de 10 minutos"}
Un solo usuario lanza un trabajo que dura 10 minutos y quiere ver el avance en su pantalla. El avance solo va del servidor al navegador. ¿Polling, long polling, SSE, WebSocket o webhook?
:::

::: answer {of="cmp-kata-p12-1"}
**Elige:** SSE. **Porque:** el flujo es solo servidor→cliente y hay un solo cliente: $L=1$ sesión abierta, un costo trivial (caja de Little). **Descarta:** WebSocket (no necesitas el canal de vuelta); webhook (el navegador no tiene dirección accesible para que el servidor lo llame); polling (funciona, pero con $\Delta=5$ s serían hasta $\lceil 600/5\rceil=120$ consultas); long polling (sirve, pero SSE ya trae reconexión y formato de eventos).
:::

::: problem {#cmp-kata-p12-2 title="Kata 2 · Aviso de precio a 10 000 usuarios"}
Una tienda quiere avisar a 10 000 navegadores que cambió un precio. Los 10 000 están conectados a la vez. Cada servidor aguanta 5 000 conexiones abiertas. ¿Qué eliges y cuántos servidores necesitas? Compara con polling a $\Delta=60$ s.
:::

::: answer {of="cmp-kata-p12-2"}
**Elige:** SSE con 2 servidores. **Porque:** el aviso va solo del servidor al cliente. Con 10 000 clientes conectados, $L=10\,000$ sesiones abiertas y $10\,000/5\,000=2$ servidores. Con polling a $\Delta=60$ s serían $10\,000/60\approx167$ consultas por segundo y hasta 60 s de demora, sin sesiones abiertas: es la alternativa si no quieres sostener conexiones y toleras la demora. **Descarta:** webhook (los clientes son navegadores, sin dirección accesible); WebSocket (no hay mensajes del cliente al servidor).
:::

::: problem {#cmp-kata-p12-3 title="Kata 3 · Aviso de un cobro de la pasarela de pagos"}
Una pasarela de pagos (un tercero) confirma un cobro 95 s después de que lo pides. Tu servidor tiene dirección pública. Compara: ¿webhook o polling con $\Delta=10$ s? ¿Cuántas consultas gastaría el polling y qué demora tendría?
:::

::: answer {of="cmp-kata-p12-3"}
**Elige:** webhook. **Porque:** el emisor es otro servicio y tu receptor es accesible. Con polling: $\lceil 95/10\rceil=10$ consultas, $10-1=9$ sin novedades y demora $10\times10-95=5$ s. El webhook no deja ninguna petición pendiente entre eventos. **Trampa:** el emisor puede reenviar el aviso; el receptor debe ser idempotente (el mismo cobro dos veces no se cuenta dos veces). **Descarta:** SSE y WebSocket (obligarían a mantener una conexión abierta con un tercero durante todo el cobro).
:::

::: problem {#cmp-kata-p12-4 title="Kata 4 · Un chat y el costo del polling"}
(a) Un chat donde 2000 usuarios envían y reciben mensajes a la vez; cada sesión de chat dura 1000 s. (b) Alguien propone polling cada 2 s durante 5 minutos (300 s) para esperar un evento que llega al final, frente a long polling con plazo de 30 s. ¿Qué eliges en (a)? En (b), ¿cuántas consultas sin novedades gasta cada uno?
:::

::: answer {of="cmp-kata-p12-4"}
**Elige:** (a) WebSocket; (b) long polling antes que polling. **Porque:** (a) el tráfico va en los dos sentidos, y con $W=1000$ s la ley de Little da $L=2000$ sesiones con $\lambda=2$ aperturas/s. (b) Polling: $\lceil 300/2\rceil=150$ consultas totales y $149$ sin novedades, demora $0$ porque 300 es múltiplo de 2. Long polling con plazo de 30 s: cada consulta dura a lo más el plazo de 30 s y al vencer se lanza otra; es la cuenta del polling con $\Delta=30$ s, así que $\lceil 300/30\rceil=10$ consultas totales y $9$ vencen sin novedades, y se entera al ocurrir el evento. **Descarta:** SSE en (a) (necesitarías otra petición para enviar); webhook (sin receptor accesible).
:::

## Notebook

- **Celda 12.1:** arranca `app_arq.py`, llama a `/inicia` y ejecuta 20 clientes por modalidad contra `/listo`, `/espera` y `/eventos`. Imprime consultas, demora, sockets abiertos, peticiones pendientes y sesiones SSE, con el evento a 10 s.
