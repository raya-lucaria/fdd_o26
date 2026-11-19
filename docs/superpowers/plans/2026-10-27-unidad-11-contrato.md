# Contrato de ejecución · Unidad 11 «Cómputo y concurrencia»

Lo leen **todos** los agentes. Manda sobre `2026-10-27-unidad-11-computo-replan.md` si hay diferencias. Anexos de fondo (léelos según tu tarea): `2026-10-27-unidad-11-anexos/{A_matematica,B_arquitectura,C_diseno_y_enjambre,D_codex_sol_estructura,E_codex_astra_matematica,F_codex_astra_arquitectura}.md`. Reglas del repo: `/home/uumami/itam/fdd_o26/CLAUDE.md`.

Decisiones del profesor (28-oct): clase de 90 min **no importa el recorte, él se ajusta** · rama de trabajo `feat/unidad-11-computo`, rama del alumno `clase-11-computo` sin PR · el enlace viejo se mantiene con una página «se mudó» · LaTeX `$…$` · arquitectura **repartida en todas las páginas** (se vale repetir visual y pedagógicamente) **y** una página final que resume y añade extras · agregar el tema **pool de conexiones** · **no mucha prisa por acortar**: se quita sólo lo que no aporta.

## 1 · Qué hay (estado tras la fase 0)

- Unidad plana `course/11_computo_y_concurrencia/` (id de la unidad `computo-y-concurrencia`), figuras en su `_assets/` (se referencian como `_assets/cmp-….svg`), código del alumno en `codigo/11_computo/` (`servidor.py`, `cable.py`, `trabajo_computo.py`, `pyproject.toml` con requests, httpx, numpy, matplotlib). Los `servidor.py`/`cable.py` de `codigo/11_computo` y `codigo/10_apis` son **idénticos** (un test lo vigila).
- Páginas viejas (1–5) siguen en la carpeta y **se reescriben**: reutiliza lo bueno (definiciones ya revisadas, mediciones, tablas), cambia el orden y la forma.
- `course/10_apis/2_computo_y_concurrencia/0_index.md` es una página «se mudó» (id `computo-se-mudo`): no la toques.

## 2 · Páginas (ids y archivos CONGELADOS)

| # | archivo | id | min |
|---:|---|---|---:|
| 0 | `0_index.md` | `computo-y-concurrencia` | — |
| 1 | `1_donde_pasa_el_tiempo.md` | `donde-pasa-el-tiempo` | 12 |
| 2 | `2_secuencial_concurrente_paralelo.md` | `secuencial-concurrente-paralelo` | 20 |
| 3 | `3_asincrono_y_el_event_loop.md` | `asincrono-y-el-event-loop` | 20 |
| 4 | `4_concurrencia_acotada.md` | `concurrencia-acotada` | 15 |
| 5 | `5_pools_y_recursos.md` | `pools-y-recursos` | 18 |
| 6 | `6_calcular_en_paralelo.md` | `calcular-en-paralelo` | 15 |
| 7 | `7_vectorizar.md` | `vectorizar` | 8 |
| 8 | `8_arquitectura_y_estrategia.md` | `arquitectura-y-estrategia` | 15 |
| A | `A_notacion.md` | `notacion-computo` | — |

Los archivos viejos `2_concurrente_paralelo_asincrono.md`, `3_asyncio_y_el_event_loop.md`, `4_vectorizar.md`, `5_elegir_la_estrategia.md` los **borra el que escribe la página que los reemplaza** (`git rm`). Ids viejos `concurrente-paralelo-asincrono`, `asyncio-y-el-event-loop`, `elegir-la-estrategia` **desaparecen**: no los enlaces.

## 3 · Figuras (ids CONGELADOS; dueño en paréntesis)

Se conservan (se pueden redibujar para mostrar `lista` rayada y la convención de A_notacion): `cmp-gantt-secuencial`, `cmp-gantt-hilos`, `cmp-gantt-procesos`, `cmp-gantt-asyncio`, `cmp-gantt-await-en-serie`, `cmp-bloqueo-del-loop`, `cmp-vectorizar`, `cmp-amdahl`, `cmp-arbol-decision`. Se **eliminan** `cmp-matriz-2x2` y `cmp-event-loop`.

Nuevas, en `tools/gen_computo.py` (F1): `cmp-estados-tarea` (p1: nueva→lista→ejecutando→esperando→lista→terminada), `cmp-intervalos` (p1: intervalo semiabierto, dos vidas que se tocan no se solapan), `cmp-conjuntos` (p2: secuencial ⊂ … paralelo ⊂ concurrente), `cmp-arq-servidor-clase` (p2: `ThreadingHTTPServer`: un hilo por conexión, un único `Lock`, cola `listen` 1024), `cmp-matriz-asincrono` (p3: modelo de escritura bloqueante/asíncrono × concurrente no/sí → secuencial, hilos, `await` en serie, `gather`), `cmp-event-loop-ticks` (p3: carriles ejecutando / cola de listas / esperando, por tick, con fichas A, B, C; traza de `gather(A,B,C)`; fila de CPU), `cmp-create-task` (p3), `cmp-gantt-gather` (p4), `cmp-flujo-semaforo` (p4: acquire/release con contador, cola de espera), `cmp-gantt-semaforo` (p4: 8 tareas, k=3, franja «espera permiso» distinta de «espera red»).

Nuevas, en `tools/gen_computo_b.py` como dict `DIAGRAMAS_B` (F2, importa helpers de `gen_computo`; `gen_computo.py` ya hace `DIAGRAMAS.update(DIAGRAMAS_B)`): `cmp-roles-recursos` (p5: cuatro columnas **Event loop = quién corre · Semáforo = quién entra · Pool = qué conexión usas · Servidor/BD = quién ejecuta**, con una petición recorriéndolas), `cmp-ciclo-conexion` (p5: conexión del pool: libre → prestada/en vuelo → libre; keep-alive: se reutiliza; cuándo se cierra), `cmp-gantt-pool` (p5: pool de 5 conexiones, 20 peticiones de 0.2 s: carriles por conexión, 4 olas, la 6.ª petición espera en la cola del pool), `cmp-pool-soltar-antes` (p5: la misma BD con k=3 conexiones, retener la conexión durante una llamada lenta vs soltarla antes), `cmp-run-in-executor` (p6), `cmp-arq-offload` (p6: loop + pool de procesos + cola), `cmp-arq-servidores` (p8: hilo por conexión · event loop · prefork/multiproceso, lado a lado), `cmp-arq-little` (p8: L = λ·W con las cifras medidas).

Todas con `aria-label` ≥ 80 caracteres, `width`/`height` en la raíz, paleta de `svg_base.py`, fuente ≥ 13 px, fila en `_assets/CREDITOS.md`. En las páginas: `::: figure {#cmp-… title="…"}` con `![alt largo](_assets/cmp-….svg)` y `:::`.

## 4 · Notación y matemática

La fija `A_notacion.md` (la escribe el agente N desde los anexos A y E) y **manda sobre todo lo demás**. Resumen: intervalos semiabiertos `[a,b)`; `t` instante; tarea τᵢ; `vida(τ)=[start,end)`; `arrival` vs `start`; `exec`, `wait`, `ready`, `blocked` (disjuntos, suman la vida); `ρ=e/d`; `ExecutingAt(t)`; `P` = CPU lógicas; `T` makespan; secuencial / concurrente / paralelo como propiedades de la traza; **paralelo ⇒ concurrente** (teorema); **asíncrono = mecanismo (la llamada regresa antes del resultado y quien espera cede el hilo)**, no una celda del Gantt; GIL por intérprete (`exec_Python`); `f` fracción serial, `S(N)=1/(f+(1−f)/N)`, `E(N)`, `speedup_pool` vs `speedup_aplicación`; Ley de Little `L=λ·W`; cota de semáforo `⌈N/k⌉·(e+w)`.

Renderizado (el sitio pre-renderiza `$…$` y `$$…$$` con MathJax en el build): nunca un `$` suelto en prosa (precios, `$GHUSER`): code span; **dentro de una tabla markdown no uses `|` ni `\|` en math** (usa `\lvert … \rvert`, `\mid` o `\operatorname{card}`); funciones con `\mathrm{exec}`/`\operatorname{…}`; las tablas de símbolos usan `$…$` por celda como en `course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`; los Gantt en tabla se escriben como texto, no como math.

## 5 · Plantilla de página (orden obligatorio dentro de cada concepto)

```
# Título
**Página k de 8 · Cómputo y concurrencia** · Pregunta · Meta
| Término | Definición de una línea | Símbolo |
## En corto (3 viñetas)
## <Concepto>            ← uno por concepto nuevo
  ::: definition {#cmp-def-… title="…"}     qué es, formal o claro   :::
  **Otro ángulo.**   figura (Gantt, flujo, estados) / tabla / lista
  **Matemática.**    $…$ (sólo si aplica; evalúa con números del ejemplo único)
  **Ejemplo.**       números concretos (traza ilustrativa o medición real)
  **Arquitectura.**  patrón: qué es · cuándo sí · cuándo no · qué cuesta · sistema real
## La decisión hasta aquí     ← tabla acumulativa (crece por página)
## Código                      ← SIEMPRE al final, después de todo lo conceptual
## Al diseñar / al revisar código de IA, busca…
Sigue con [[id]].
```

- **Ningún bloque ```python antes de `## Código`.**
- Etiquetas `Otro ángulo / Matemática / Ejemplo / Arquitectura` con esos nombres, en ese orden.
- Ejemplo único de la unidad: 3 tareas, cada una 20 ms ejecuta + 200 ms espera + 20 ms ejecuta (traza ilustrativa), más las mediciones reales de abajo.
- `::: definition` ids con prefijo `cmp-def-` (únicos en todo el curso).
- Se permite repetir ideas entre páginas (visual y pedagógicamente); no se acorta a costa de comprensión. Sí se evita: bloques largos de prosa donde cabe lista, tabla o diagrama; «Qué hace cada línea» bullet por bullet.
- Sin analogías (nada de restaurante/cocina/mesero/«es como»/«imagina»).
- Frontmatter: `id, title, nav_title, summary (entrecomillada), status: ready, estimated_time, tags, prerequisites`.

### Código (sección final de cada página)
- Celdas **≤ 15 líneas**, comentario por línea no obvia, marcadas `**Haz (celda k.m):** una línea`. Después: **Qué pasó** (traza, Gantt simplificado o tabla de ESA ejecución) y **Deberías ver** (`text`).
- Cuadro «**Python que quizá no has visto**» por celda con lo no clásico (`async def`, `await`, `async with`, `gather(*…)`, `Semaphore`, `run_in_executor`, `if __name__ == "__main__"`, `Session`, `Limits`): qué es, qué hace y **por qué hace falta aquí**.
- Cierra con «La versión larga y paso a paso está en el notebook, tema k.» Cada `Haz (celda k.m)` debe existir literal en el notebook (celda que empieza con `# celda k.m`).
- `await` de nivel superior en celdas; `asyncio.run` nunca en celdas. Procesos: la función vive en `trabajo_computo.py`.

## 6 · Marcadores de cifras (nunca se inventan números ni salidas)

`{{m:clave}}` (inline) y `{{salida:nombre}}` (contenido de un bloque «Deberías ver»). Los sustituye `.superpowers/medidas-10-2/sustituir.py` con `medidas.json` y `salidas/`. **Claves ya medidas:** cpus, seq20_s, hilos32_20_s, hilos32_100_s, hilos32_500_s, async32_20_s, async32_100_s, async32_500_s, hilos100_500_s, async100_500_s, calc_1proc_s, calc_2proc_s, calc_4proc_s, carrera_esperado, carrera_obtenido, bloqueo_loop_s, bucle_s, numpy_s, numpy_x, seq20_espera_pct. **Salidas ya medidas:** seq20, hilos, asyncio, await_en_serie, carrera, carrera_lock, bloqueo_loop, trace_loop, procesos, vectorizar, cpu_o_espera, cmp_asincrono, sleep_bloqueante, bloqueo_loop_executor, arreglo, desborde_int64, amdahl, lambda_procesos, pool_por_llamada. **Nuevas a medir (pool, las produce el agente M):** m: `pool5_20_s`, `pool5_puertos`, `sinsesion_puertos`, `sesion_puertos`, `sinsesion_s`, `sesion_s`, `retiene_s`, `suelta_s`; salidas: `pool_puertos`, `pool_sesion`, `pool_olas`, `pool_cola_simple`, `pool_retener_vs_soltar`, `semaforo_vs_pool`. Si necesitas otra, usa `{{m:NUEVO_x}}`/`{{salida:nuevo_x}}` y repórtala.

Mediciones de referencia (esta máquina, 8 CPU lógicas, una corrida): 20 llamadas `?lento=0.2` en serie 4.04 s (99.3 % sin CPU del cliente); 32 hilos 0.23 s; `asyncio`+Semaphore(32) 0.24 s; 500 llamadas 3.32 s (hilos) y 3.41 s (asyncio); `calcula` 4 tareas con 1/2/4 procesos 2.34/1.45/1.00 s; bucle vs NumPy 0.188/0.0119 s (16×); pool por llamada 0.73 s vs 0.07 s. Cargas: ≤ 500 llamadas, ≤ 4 procesos de cálculo.

## 7 · Lo nuevo: pools y recursos (página 5; la idea)

**Pregunta.** Pool de 5 conexiones, 5 peticiones en vuelo esperando respuesta: ¿la sexta puede usar una de esas conexiones? ¿Una conexión se reutiliza al terminar su petición? ¿Qué libera `await`?

**Conceptos y orden:**
1. **Recurso.** Cosa finita que una tarea ocupa: hilo, conexión, permiso, CPU, el hilo del loop.
2. **Cuatro roles distintos** (`cmp-roles-recursos`): *event loop* = quién corre (planifica tareas sin bloquear un hilo mientras esperan); *semáforo* = quién entra (cuenta permisos, no guarda objetos); *pool* = qué conexión usas (guarda **objetos reales reutilizables**: abre, presta, recupera, cierra, valida/reemplaza rotas); *servidor/BD* = quién ejecuta. Tabla semáforo vs pool (limita concurrencia: ambos; guarda conexiones reales: sólo pool; reutiliza: sólo pool; abre/cierra: sólo pool; detecta rotas: pool; hace esperar si está lleno: ambos). Un pool ≈ semáforo + objetos + ciclo de vida; **el event loop es opcional** (los pools existen en código síncrono con hilos; ahí el hilo se bloquea esperando conexión).
3. **Qué libera `await`** (tabla): el hilo del loop → **sí** (otras tareas corren); la conexión prestada → **no** (sigue ocupada hasta que se suelta); el permiso del semáforo → **no** (sigue tomado hasta salir del bloque); un hilo bloqueado en `time.sleep`/`requests.get` → **no**; una conexión devuelta al pool → **sí**, otra tarea la puede tomar.
4. **Ciclo de una conexión** (`cmp-ciclo-conexion`): libre → prestada (en vuelo: HTTP/1.1 y una conexión de BD llevan **una** petición a la vez; HTTP/2 puede multiplexar varias) → libre. La conexión terminada **sí se reutiliza** (keep-alive): evita el costo de abrir (TCP, TLS, autenticación). Con 5 conexiones y 5 en vuelo, la 6.ª **no** puede usar ninguna de las 5 mientras sigan en vuelo: espera en la cola **del pool**; en cuanto una vuelve, la toma (`cmp-gantt-pool`: 20 peticiones de 0.2 s con 5 conexiones → 4 olas ≈ 0.8 s).
5. **Medición con el servidor de la clase** (`GET /quien` → puerto del cliente y nombre del hilo del servidor): `requests.get` suelto abre una conexión nueva por llamada (N puertos distintos); `requests.Session` reutiliza (1 puerto); `httpx.AsyncClient(limits=Limits(max_connections=5))` con 20 peticiones usa **≤ 5 puertos** y tarda ≈ 0.8 s. El servidor atiende cada conexión con un hilo: **conexiones abiertas del cliente = hilos ocupados del servidor** (enlace con p2 y Little).
6. **Soltar el recurso antes de la espera larga** (`cmp-pool-soltar-antes`): no retengas la conexión de la BD mientras esperas una llamada lenta a otra API (60 s): consulta, **suelta**, espera, y toma otra si hace falta. Medición con un pool simple `asyncio.Queue` de k conexiones simuladas: retener vs soltar.
7. **Pool simple en 12 líneas** (`asyncio.Queue` con k ids: `get` = prestar, `put` = devolver) para ver que un pool es una cola de objetos, y un semáforo sólo cuenta.
8. **Tres topes distintos que se confunden:** tope de tareas (`gather` sin límite = miles de corrutinas baratas), tope de entrada (`Semaphore`), tope de recursos reales (pool: conexiones, hilos). Dimensionarlos: pool ≤ lo que acepta el servidor/BD; semáforo ≥ pool no ayuda (la cola está en el pool); Little: conexiones en uso = λ·W.
9. **Pool de hilos y de procesos** son el mismo patrón (`ThreadPoolExecutor`, `ProcessPoolExecutor`): trabajadores reutilizables; **pool por llamada** = anti-patrón (0.73 s vs 0.07 s).
10. **Arquitectura:** el API server con 1000 peticiones HTTP y 10 conexiones a PostgreSQL (el event loop atiende las 1000, el pool limita a 10 las que hablan con la BD, PgBouncer como pool externo); dimensionar el pool con la BD, no con el tráfico; qué pasa si la dependencia pasa de 0.2 s a 2 s (Little: ×10 conexiones en uso, el pool se agota, la cola crece: timeout y backpressure).
11. **Código:** `Session` vs suelto con `/quien`; `Limits(max_connections=5)`; pool simple con `Queue`; retener vs soltar. Comentarios por línea.

## 8 · Arquitectura repartida (qué patrón en qué página)

| Pág | Patrones |
|---|---|
| 1 | presupuesto de latencia de un endpoint (BD 50 ms + API 1.5 s + CPU 1 ms); servidor secuencial como línea base: λ = 1/W; cola FIFO |
| 2 | hilo por conexión vs prefork (servidor de la clase como caso real: un hilo por conexión sin tope, un `Lock`); memoria compartida vs aislada; región crítica = serialización deliberada |
| 3 | servidor con event loop (miles de conexiones en un hilo); cuándo no: manejador que calcula; un loop por worker |
| 4 | scatter-gather; concurrencia acotada; backpressure; tope ≠ rate limit; bulkhead (un semáforo por dependencia) |
| 5 | pool de conexiones; soltar antes; PgBouncer; dimensionar con Little; pool por llamada |
| 6 | offload: loop + pool de procesos + cola; cuántos workers (min(k,P)); IPC/serialización |
| 7 | empujar el cálculo al motor (NumPy/Polars/SQL) antes de repartir; copias y temporales |
| 8 | resumen + extras: los 3 modelos de servidor lado a lado, Little y capacidad, p99 y cola, timeouts/deadlines, thundering herd, escalado vertical/horizontal y estado compartido; 3 casos (scraper de 10 000 URLs; API que sirve un modelo —cifras supuestas, rotuladas—; pipeline de 3 APIs) y el árbol de decisión |

Cada página lleva **su** bloque `**Arquitectura.**` por concepto y su fila en «La decisión hasta aquí». Repetir está bien.

## 9 · Reglas de coordinación

- Archivos **disjuntos** por agente. Los de página no tocan `_assets/`, `tools/gen_*`, tests ni `codigo/`. Nadie hace commit ni `git add`. No ejecutes `pytest tools/` ni benchmarks (los corre un agente de medición una vez, ≤ 4 procesos). Revisores leen.
- Si el contrato no alcanza, decide con el criterio del profesor (compacto, arquitectónico, sin analogías) y repórtalo en ≤ 120 palabras al terminar.
