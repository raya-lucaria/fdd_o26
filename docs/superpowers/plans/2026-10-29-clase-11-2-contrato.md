# Contrato de la clase 11.2 · v1 (lo edita sólo Claude; los agentes reportan discrepancias, no las resuelven)

Fuente de las reglas de forma: `2026-10-29-clase-11-2-detalle.md` secciones B y C. Este archivo fija ids, glosario, símbolos, parámetros, figuras, celdas y propietarios.

## 1. Páginas (carpeta `course/11_computo_y_concurrencia/`)
| Archivo | id | nav_title | Celda | Redactor |
|---|---|---|---|---|
| `9_sistemas_distribuidos.md` | `sistemas-distribuidos` | Sistemas distribuidos | 9.1 | W9 |
| `10_capas_de_ejecucion.md` | `capas-de-ejecucion` | Capas de ejecución | 10.1 | W10 |
| `11_componer_un_servidor.md` | `componer-un-servidor` | Componer un servidor | 11.1, 11.2 | W11 |
| `12_como_llegan_los_resultados.md` | `como-llegan-los-resultados` | Cómo llegan los resultados | 12.1 | W12 |
Frontmatter: `id`, `title`, `nav_title`, `summary` (entre comillas), `status: ready`, `estimated_time` (9: 8m, 10: 12m, 11: 25m, 12: 20m), `tags`, `prerequisites` (ids existentes). Primera línea tras el título: `**Página N · Cómputo y concurrencia** · Pregunta: **…** · Respuesta: **…**`.
Ids existentes enlazables: `computo-y-concurrencia`, `notacion-computo`, `donde-pasa-el-tiempo`, `secuencial-concurrente-paralelo`, `asincrono-y-el-event-loop`, `concurrencia-acotada`, `pools-y-recursos`, `calcular-en-paralelo`, `vectorizar`, `arquitectura-y-estrategia`. Ids de definiciones/figuras nuevos con prefijo `cmp-` (únicos en todo el curso): definiciones `cmp-def-<tema>`, figuras como en §4.

## 2. Símbolos (ya existentes en `A_notacion.md`; no se redefinen)
$P$ CPU lógicas · $N$ trabajadores · $k$ tope real (permisos, conexiones, procesos) · $T$ duración del lote · $e,w,r,b$ duraciones ejecuta/espera/lista/bloqueada · $d$ duración de la vida de una tarea · $L,\lambda,W$ Little · $\rho$ · $n=|\mathcal T|$.
**Nuevos** (se agregan a `A_notacion.md`, los agrega Claude): $R$ réplicas · $p_{\text{ef}}$ unidades que **de hecho** avanzan a la vez (paralelismo efectivo del ejemplo) · $t_{\max}$ plazo (duración máxima que el cliente espera) · $\Delta$ intervalo de polling · $T_{\text{evt}}$ instante del evento medido desde $t=0$ (en el ejemplo: 10 s).
**Prohibido** reutilizar: $d$ (duración de vida), $W$ (tiempo medio) con otro sentido. En SVG: nada de letras griegas (la guarda las prohíbe: «lambda», «Delta»).

## 3. Glosario (definiciones literales; los redactores las copian y pueden afinar sin cambiar el significado)
- **proceso**: programa en ejecución con su propia memoria y al menos un hilo. · **hilo**: secuencia de instrucciones que el sistema operativo asigna a una CPU lógica; comparte la memoria de su proceso. · **tarea**: flujo secuencial de trabajo que un runtime o el programa trata como unidad (corrutina, goroutine, proceso ligero). · **runtime**: biblioteca o máquina virtual que reparte tareas entre hilos. · **planificador**: componente que decide qué unidad usa cada recurso en cada instante. · **CPU lógica**: unidad de ejecución que el sistema operativo ve (núcleo o hilo de hardware). · **exclusión global**: candado que permite a lo sumo un hilo ejecutando cierto código a la vez (el GIL de CPython).
- **paralelismo posible**: unidades que pueden ejecutar a la vez según hardware, runtime, exclusiones y configuración. · **tope admitido**: máximo de tareas que el sistema acepta en curso. · **ocupación**: fracción del tiempo que un recurso está en uso, medida en un momento o ventana. · **rendimiento**: trabajos terminados por unidad de tiempo en una ventana.
- **worker**: proceso que atiende peticiones con su propio loop o hilos. · **réplica**: copia del servicio, en otra máquina o contenedor, detrás de un balanceador. · **pool local**: conjunto de conexiones u objetos que crea y usa un worker. · **loop**: hilo que ejecuta las tareas asíncronas por turnos. · **desplazar**: ejecutar un trabajo bloqueante o de CPU fuera del loop (hilo o proceso). · **limitador de hilos**: tope de hilos que un framework usa para las funciones síncronas (AnyIO: 40 por omisión, por loop).
- **componente**: proceso o máquina que ejecuta de forma independiente. · **mensaje**: datos que un componente envía a otro por la red. · **reloj local**: reloj de un componente; dos componentes no comparten reloj. · **precede**: A precede a B si A es anterior en el mismo componente, si A envía el mensaje que B recibe, o por transitividad; es un orden parcial. · **fallo parcial**: falla un componente o un mensaje y el resto sigue. · **resultado desconocido**: tras vencer el plazo, el cliente no sabe si la operación se ejecutó. · **plazo** ($t_{\max}$).
- **petición**: mensaje que pide algo. · **conexión**: canal abierto entre dos programas (p. ej. un socket TCP). · **polling**: el cliente repite una consulta cada $\Delta$. · **long polling**: el cliente consulta y el servidor retiene la respuesta hasta que haya novedad o venza el plazo. · **flujo (stream)**: respuesta que sigue enviándose por la misma conexión. · **SSE**: respuesta HTTP continua servidor→cliente con eventos. · **WebSocket**: canal bidireccional que el cliente establece sobre HTTP. · **webhook**: el emisor del evento hace una petición HTTP al receptor registrado.

## 4. Figuras (8; generadas por `tools/gen_computo_c.py` [F1] y `tools/gen_computo_d.py` [F2]; ids de figura = nombre del archivo sin `.svg`)
Reglas de la unidad: paleta de `tools/svg_base.py`; `width`/`height` en la raíz; sin letras griegas ni dígitos sueltos fuera de rótulos con unidad; nada fuera del `viewBox`; los Gantt rotulan CPU/hilo y la razón de cada espera; cada módulo exporta un dict (`DIAGRAMAS_C`, `DIAGRAMAS_D`) que `gen_computo.py` mezcla con `DIAGRAMAS.update`, como hace `gen_computo_b.py`; tests propios (`tools/test_gen_computo_c.py`, `…_d.py`) y fila de créditos reportada a Claude (no tocar `CREDITOS.md`). Estilos de barra de la 11.1: ejecuta relleno, espera con contorno, lista rayada, bloqueada ámbar.
| Figura | Página | Contenido exacto |
|---|---|---|
| `cmp-dist-relojes` | 9 | Gantt de dos componentes, A (reloj 0) y B (reloj de B = reloj real − 40 ms). Mensaje A→B enviado en reloj A = 100 ms, latencia real 20 ms, recibido en reloj B = 80 ms. Dos ejes (reloj A, reloj B) alineados al instante real; flecha causal A→B; rótulo «B marca 80, A marcó 100: 80−100 = −20 ms = 20 ms − 40 ms». |
| `cmp-dist-tres-causas` | 9 | Tres carriles de la misma petición sin respuesta tras $t_{\max}$: (1) la ida se pierde; (2) el servidor ejecuta y la respuesta se pierde; (3) el servidor tarda más que $t_{\max}$. Cliente igual en los tres: «espero $t_{\max}$ y no sé cuál fue». |
| `cmp-capas` | 10 | Dos columnas: pertenencia (máquina → proceso → hilo → tarea) y ejecución (el SO asigna hilos a CPU lógicas; el runtime reparte tareas entre hilos; una tarea puede migrar de hilo). Quién planifica cada flecha. |
| `cmp-gantt-tres-planificaciones` | 10 | Tres paneles, mismo trabajo: 4 tareas independientes de 100 ms de cálculo, disponibles en 0, sin costos extra (tiempos ideales). (a) cooperativas en 1 hilo, 4 CPU libres: 400 ms; (b) 4 hilos con exclusión global: 400 ms, tareas «lista: espera la exclusión global» en rayado; (c) 4 hilos en 4 CPU: 100 ms. Cada barra dice en qué hilo/CPU corre y por qué espera. Cuenta al pie: ⌈4/1⌉·100, ⌈4/1⌉·100, ⌈4/4⌉·100. |
| `cmp-ancla-servidor` | 11 | Ruta de una petición: cliente → balanceador → réplica con N workers; cada worker con su loop y su pool local; cada conexión del pool → un backend propio en Postgres. Variante con PgBouncer anotada (dos poblaciones). Resalta el pool dentro de su worker. |
| `cmp-async-vs-def` | 11 | Dos paneles: `async def` con espera bloqueante (12 peticiones de w = 0.5 s ejecutan una tras otra en el loop: 12·w = 6 s; sonda lanzada en 0.125 s espera hasta que el loop se libere) y `def` (las 12 en hilos del limitador: ≈ w = 0.5 s; la sonda responde de inmediato). Barras de loop y de hilos rotuladas. |
| `cmp-gantt-resultados` | 12 | Un evento en $T_{\text{evt}}$ = 10 s; tres carriles: polling $\Delta$ = 3 s (consultas en 3, 6, 9, 12 s; 3 sin novedades, la 4.ª con resultado; demora 2 s), long polling (una consulta pendiente que responde al evento), SSE (una respuesta abierta; evento llega en 10 s). Rotula conexión abierta y consultas. |
| `cmp-push-webhook` | 12 | Diagramas de secuencia lado a lado: SSE (cliente abre, servidor envía eventos), WebSocket (el cliente abre; ambos envían), webhook (el emisor llama al receptor). Marca quién inicia y qué queda abierto en cada uno. |

## 5. Parámetros (nombre–valor–unidad–supuesto)
| Nombre | Valor | Unidad | Naturaleza |
|---|---|---|---|
| tareas del Gantt 10 | 4 × 100 | ms | supuesto del ejemplo (ideal, sin costos) |
| $p_{\text{ef}}$ (a, b, c) | 1, 1, 4 | unidades | calculado del modelo |
| $T_{\text{ideal}}$ (a, b, c) | 400, 400, 100 | ms | calculado |
| desfase reloj B | −40 | ms | supuesto |
| latencia del mensaje | 20 | ms | supuesto |
| marcas | A=100, B=80 | ms | supuesto |
| $w$ (D1) | 0.5 | s | parámetro de la demo |
| peticiones D1 | 12 (+1 sonda, 13.ª conexión) | — | parámetro |
| $T$ D1 async / def | ≈ 12·w = 6 / ≈ w = 0.5 | s | calculado (aprox.); el medido va en `{{m:d1_async_total}}`, `{{m:d1_def_total}}`, `{{m:d1_async_sonda}}`, `{{m:d1_def_sonda}}` |
| limitador de hilos | 40 | tokens/loop | documentado (AnyIO, configurable) |
| $R,N,k$ | 3, 4, 10 → 120 | réplicas, workers, conexiones | supuesto; contra 97 (Postgres con `max_connections=100`, 3 reservadas) |
| $T_{\text{evt}}$, $\Delta$ | 10, 3 | s | parámetro |
| consultas polling | 4 totales, 3 sin novedades, demora 2 s | — | calculado; 20 clientes: 80 y 60 |
| medidos D2 | `{{m:d2_poll_consultas}}`, `{{m:d2_poll_demora}}`, `{{m:d2_long_demora}}`, `{{m:d2_sse_demora}}`, `{{m:d2_sockets_poll}}`, `{{m:d2_pend_long}}`, `{{m:d2_sesiones_sse}}` | — | medido (8 CPU, un worker) |
| `{{m:pid_hilos_*}}` | PID e hilos de 4 hilos y de 2 procesos | — | medido |
Criterios de éxito de las mediciones (cualitativos, con tolerancia): D1 async def ≥ 8·$w$ y def ≤ 3·$w$; la sonda en `async def` espera más de 4 s y en `def` menos de 0.5 s; D2 demora de polling entre 1.5 y 3.0 s, long polling y SSE < 0.5 s; si una medición cae fuera, se repite hasta 3 veces y se reporta.

## 6. Notebook (`codigo/11_computo/arquitectura.ipynb`, lo genera N desde `tools/notebook_arquitectura/*.py`)
Celdas rotuladas `# celda N.M` únicas: 9.1 (relojes: simula dos relojes con desfase y muestra la resta de marcas), 10.1 (PID e hilos: 4 hilos vs 2 procesos), 11.1 (D1), 11.2 (cuenta $R\times N\times k$ y comparación con 97), 12.1 (D2). Servidor: `app_arq.py` de K3. Etapa 1 (D1): 9.1 y 10.1; etapa 2 (D2): 11.x y 12.1.

## 7. Propietarios y reglas
`CREDITOS.md`, `A_notacion.md`, índice de la unidad, `uv.lock` (lo genera K3, lo integra Claude): sólo Claude. Cada redactor sólo escribe su `.md`. F1/F2 sólo sus módulos y tests. Nadie edita `estudiantes/uumami/`. Nadie hace commit. Aceptación de una entrega: `raya validate` verde + tests de la ola + referencias, figuras, alt y créditos resueltos + CI verde + el sitio responde 200 y contiene la frase marcador.
