# Unidad 11 · bloques 11.2 y 11.3 · Plan general (consensuado Claude + Codex astra, 2026-10-29)

**Meta.** Ante cualquier sistema (API, carga, pipeline): saber dónde corre cada cosa, qué se limita, cómo llegan los resultados y cómo decidir la configuración. General; Python, FastAPI, Postgres, Go y Elixir sólo son filas de ejemplo.

**Forma.** 400–650 palabras por página. Pregunta → definiciones → figura → cuenta → ejemplo → arquitectura → «si hay tiempo». Sin código en las notas (vive en el notebook del bloque). Enlaza la 11.1; no la repite. Una familia de diagramas «ruta de una petición» (cliente → balanceador → worker → pool → dependencia, con y sin cola) se repite resaltando la capa de cada página.

**Calendario.** Los asuetos de noviembre son lunes (2 y 16): hay clase martes 3 y martes 17. 11.2 = jueves 29 oct (`session-18`); 11.3 = martes 3 nov (`session-19`). Tarea: DataCamp *Introduction to FastAPI*, vence el 3 nov (se crea con `crear_tarea`).

## Páginas (planas en `course/11_computo_y_concurrencia/`)
| # | id | Bloque | Contenido |
|---:|---|---|---|
| 9 | `sistemas-distribuidos` | 11.1 | mensajes, causalidad, relojes locales, fallo parcial, resultado desconocido; Gantt con dos relojes |
| 10 | `capas-de-ejecucion` | 11.2 | máquina→proceso→hilo→tarea; quién planifica; cuatro cantidades; tres Gantt abstractos; leer una configuración |
| 11 | `componer-un-servidor` | 11.2 | propiedad de pools y estado, backend por conexión, $R\times N\times k$, `async def` vs `def`, desplazar trabajo |
| 12 | `como-llegan-los-resultados` | 11.2 | polling, long polling, SSE, WebSocket, webhook; recurso retenido vs unidad que ejecuta; Little con frontera |
| 13 | `presupuestar-una-carga` | 11.3 | LLM remoto/local, motor tabular, ETL, BD: recurso escaso, métrica |
| 14 | `trabajos-duraderos` | 11.3 | matriz persistencia × progreso, `202`, efecto/ack, reentrega, saturación, cancelación |
| 15 | `elegir-y-justificar` | 11.3 | siete preguntas por etapa, métricas por recurso, dos casos con datos, contracaso 2×2×5 |

## Demostraciones (máx. 2 por sesión)
D1 `async def` vs `def` con espera bloqueante (p11) · D2 polling/long polling/SSE con 20 clientes (p12) · D3 LLM simulado concurrencia vs cuota (p13) · D4 saturación y caída del consumidor antes del ack (p14). Opcionales: hilos vs procesos, Postgres en vivo, benchmark tabular, catálogos de runtimes y brokers, tercer caso.

## Tiempos
11.2: puente 8 · p10 12 · p11 25 · p12 20 · ejercicio 15 · margen 10. 11.3: recuperar 6 · p13 18 · p14 26 · taller p15 30 · margen 10.

## Precisiones técnicas acordadas
Un backend por conexión directa a Postgres (con PgBouncer, dos poblaciones); conexiones ≠ consultas activas ≠ CPU. AnyIO: 40 tokens por loop, compartidos. Hilos virtuales: sobre hilos portadores, sin pool. Ack del productor ≠ ack del consumidor; la deduplicación debe sobrevivir al reinicio y ser atómica con el efecto. `429` = política de tasa; `503` = indisponibilidad; cola llena no implica `429`. Polling sin consulta inicial: sin novedades $=\lceil T/\Delta\rceil-1$, demora $=\Delta\lceil T/\Delta\rceil-T$; la media $\Delta/2$ pide fase uniforme. Little con frontera y población explícitas.

## Qué entra hoy y qué no
Hoy: calendario, índice, guardas, notación, páginas 9–12, D1 y D2. Antes del 3 nov: páginas 13–15, D3 y D4, tarea FastAPI.

## Revisión
Astra: ronda 1 (plan v2) y ronda 2 (plan v3, `CONSENSO: SÍ`). Informes en el scratchpad de la sesión.
