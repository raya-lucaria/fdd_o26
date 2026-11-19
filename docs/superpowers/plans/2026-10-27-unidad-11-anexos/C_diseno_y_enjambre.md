# Diseño · Unidad 11 «Cómputo y concurrencia» (replanteo de 10.2)

Leí: las 6 páginas de `course/10_apis/2_computo_y_concurrencia/`, `tools/gen_computo.py` (11 figuras), `tools/gen_notebook_computo.py`, `tools/test_computo_curriculum.py`, `tools/test_gen_computo.py`, `course/9_python/0_index.md`, `course/6_expresiones_regulares/` (unidad plana), el calendario, `fdd_p26/clase/16_computo/02,03,05`. Raya ya renderiza `$…$`/`$$…$$` (lo usa `3_arquitectura_de_computadoras/3_…/0_index.md`) y `::: definition {#id title=…}` (lo usa regex).

## 1 · Estructura

**Unidad plana (sin secciones), como `6_expresiones_regulares/`:** 7 páginas + hoja de notación caben en una sesión; secciones serían sobrestructura.

| Qué | Antes | Después |
|---|---|---|
| Directorio | `course/10_apis/2_computo_y_concurrencia/` | `course/11_computo_y_concurrencia/` (`git mv` + reescritura) |
| id de la unidad | `computo-y-concurrencia` (sección) | **el mismo id** → `session-17` sigue resolviendo sin tocar `page` |
| URL | `/apis/computo-y-concurrencia/` | `/computo-y-concurrencia/` (actualizar el enlace del notebook) |
| Figuras | `course/10_apis/_assets/cmp-*.svg` + `CREDITOS.md` | `git mv course/10_apis/_assets course/11_computo_y_concurrencia/_assets` (10.1 no tiene imágenes: el directorio sale entero). Rutas en páginas: `_assets/cmp-….svg` (ya no `../`) |
| `course/10_apis/0_index.md` | 2 secciones, 190 min | 1 sección (90 min); una línea «Cómputo y concurrencia es ahora la unidad [[computo-y-concurrencia]]» |
| Generador SVG | `tools/gen_computo.py` → `10_apis/_assets` | mismo archivo, `ASSETS = RAIZ / "course/11_computo_y_concurrencia/_assets"`; docstring «unidad 11» |
| Test SVG | `tools/test_gen_computo.py` (`ASSETS`, `UNIDAD`) | mismas dos constantes a la ruta nueva |
| Plantilla | `codigo/10_apis/{computo.ipynb, trabajo_computo.py}` | `codigo/11_computo/`: `computo.ipynb`, `trabajo_computo.py` (`git mv`), `gantt.py` (nuevo), `servidor.py` + `cable.py` (**copias byte a byte** de `10_apis`, con guarda), `pyproject.toml` (`requests`, `httpx`, `numpy`, `matplotlib`; dev `ipykernel`), `uv.lock` nuevo |
| `codigo/10_apis/` | | se queda `servidor.py`, `cable.py`, `apis.ipynb`, `pyproject.toml` (sólo cambia `description`; deps intactas para no regenerar el lock) |
| Rama del alumno | `clase-10-computo` | `clase-11-computo`, sin PR; carpeta `estudiantes/<login>/11_computo/` |
| Calendario | `session-17` 2026-10-27, `page: computo-y-concurrencia` | igual (título: «Cómputo y concurrencia: esperar, calcular y repartir»). Si se re-imparte, `session-18` real, nunca placeholder |
| `CLAUDE.md` + `AGENTS.md` | «Section 10.2 has…» | «Unit 11 has `gen_computo.py` (→ `course/11_computo_y_concurrencia/_assets/`) and `gen_notebook_computo.py` (source `tools/notebook_computo/*.py` → `codigo/11_computo/computo.ipynb`)»; regla de carpeta: `11_computo/` va en `clase-11-computo` sin PR. Los dos archivos en el mismo commit |

Por qué copiar `servidor.py` y no importarlo de `../10_apis`: el alumno corre `uv sync` y el servidor desde **una** carpeta; un `sys.path` hacia otra unidad se rompe con la regla del mirror. La duplicación la vigila `test_servidor_y_cable_son_los_de_10_apis`.

## 2 · Plantilla de página

Cada concepto nuevo es un `##` con **cinco etiquetas fijas, en este orden**; el código vive **sólo** en un `## Código` final.

```
---  (id, title, nav_title, summary, status, estimated_time, tags, prerequisites)
# Título
**Página k de 7 · Cómputo y concurrencia** · Pregunta: … · Meta: …
| Término | Definición en una línea | Símbolo |        ← glosario de la página
## En corto  (3 bullets)
## <Concepto 1>
  ::: definition {#cmp-def-…}  definición formal/clara  :::
  **Otro ángulo.**   figura Gantt / tabla / lista (::: figure {#cmp-…})
  **Matemática.**    $…$ con la notación de A_notacion; sólo si aplica
  **Ejemplo.**       números concretos (Gantt ilustrativo o medición)
  **Arquitectura.**  patrón: cuándo sí / cuándo no / qué cuesta + ejemplo de sistema
## <Concepto 2> …
## La decisión hasta aquí      ← tabla acumulativa (crece de página en página)
## Código
  párrafo de 2 líneas: qué demuestra
  **Haz (celda k.m):** …  ```python (≤ 15 líneas, comentario por línea no obvia)```
  **Qué pasó:** traza/Gantt simplificado o tabla  ·  **Deberías ver:** ```text```
  «La versión larga está en el notebook, tema k.»
## Al diseñar / al revisar código de IA, busca…
Sigue con [[…]].
```

**Página-modelo (esqueleto) · `concurrencia-acotada`:**

- *Pregunta:* 500 llamadas; la API acepta 32 a la vez. ¿Cuánto tardas y cómo no la tumbas?
- *`gather` — Definición:* recibe $n$ awaitables, los convierte en `Task`, devuelve la lista de resultados **en el orden de los argumentos**. *Otro ángulo:* Gantt fan-out/fan-in (`cmp-gantt-gather`). *Matemática:* sin tope, $T \approx \max_i |life(\tau_i)|$. *Ejemplo:* 20 × 0.2 s → 0.24 s. *Arquitectura:* **scatter-gather** (agregador que consulta $n$ servicios); cuándo no: llamadas dependientes, $n$ sin cota.
- *`Semaphore(k)` — Definición:* contador con $k$ permisos; `acquire` resta o encola, `release` suma y despierta al primero. *Otro ángulo:* diagrama de flujo `cmp-flujo-semaforo` + Gantt `cmp-gantt-semaforo` (8 tareas, $k=3$, franja «espera permiso»). *Matemática:* $T \approx \lceil N/k \rceil (e+w)$; $X = k/(e+w)$ (Little). Verificación: $\lceil 500/32\rceil \cdot 0.2 = 3.2$ s vs 3.41 s medidos. *Arquitectura:* **concurrencia acotada / backpressure**; tope ≠ rate limit (un `429` sigue posible), pool de conexiones del cliente.
- *Decisión hasta aquí:* fila «muchas esperas independientes → `gather` + `Semaphore(k)`, $k$ = lo que acepta el servidor, medido».
- *Código:* celda 4.1 (`lote(n)` actual de 3.3, compacto); celda 4.2 (`await` en serie como contraejemplo).

## 3 · Páginas (≈120 min; la sesión es de 90: corte marcado)

| # | id (archivo) | Min | Conceptos | Figuras (reuso / **nueva**) | Matemática | Arquitectura | Código en página → notebook |
|---:|---|---:|---|---|---|---|---|
| 1 | `donde-pasa-el-tiempo` (`1_…`) | 15 | tarea, estados (lista/ejecuta/espera/terminada), CPU-bound, I/O-bound, secuencial | **cmp-estados-tarea**, **cmp-intervalos**, cmp-gantt-secuencial | $T$, $\tau_i$, $life$, $exec$, $wait$, $ready$, partición; $\rho_i$; $T_{seq}=\sum$ | presupuesto de latencia de un endpoint (BD 50 ms + API 1.5 s + CPU 1 ms); «mide antes de elegir» | 1.1 dos relojes; 1.2 20 en serie → tema 1 (versión 1 del cliente) |
| 2 | `secuencial-concurrente-paralelo` | 25 | proceso/hilo/CPU/GIL (tabla + [[el-gil]]), concurrente, paralelo, teorema | cmp-gantt-hilos, cmp-gantt-procesos, **cmp-conjuntos** (reemplaza cmp-matriz-2x2) | def. concurrente y paralelo; Paralelo ⇒ Concurrente; cotas de $T$; $\lvert E(t)\rvert\le P$, con GIL $\le 1$ por intérprete | servidor **hilo por conexión** (`ThreadingHTTPServer`) vs **pre-fork** (varios procesos) | 2.1 20 con 32 hilos; 2.2 1/2/4 procesos → tema 2 (versión 2) |
| 3 | `asincrono-y-el-event-loop` | 25 | asíncrono (modelo de programación), esperas aprovechadas, corrutina, `Task`, `create_task`, event loop por tick | **cmp-event-loop-ticks** (reemplaza cmp-event-loop), cmp-gantt-asyncio, cmp-gantt-await-en-serie, **cmp-matriz-asincrono**, **cmp-create-task** | $Aprov(i,j) \iff exec(\tau_j)\cap wait(\tau_i)\ne\emptyset$; asíncrono ⊥ concurrente | servidor **event loop** (miles de conexiones, un hilo); cuándo no: manejador que calcula | 3.1 corrutina sin/con await; 3.2 traza A/B/C → tema 3 |
| 4 | `concurrencia-acotada` | 20 | `gather`, `Semaphore`, límite del cliente (`httpx.Limits`), rate limit ≠ concurrencia | **cmp-gantt-gather**, **cmp-gantt-semaforo**, **cmp-flujo-semaforo** | $\lceil N/k\rceil(e+w)$; Little | scatter-gather; backpressure; productor-consumidor con `asyncio.Queue` (sólo notebook) | 4.1 lote 20/100/500; 4.2 await en serie → tema 4 (versiones 3-5) |
| 5 | `calcular-en-paralelo` | 15 | bloquear el loop, `run_in_executor`/`to_thread`, carrera + `Lock`, Amdahl | cmp-bloqueo-del-loop, **cmp-run-in-executor**, cmp-amdahl, **cmp-arq-offload** | Amdahl con $s$ (fracción serial) y $S_P$ (speedup) | **descargar el cálculo**: loop + pool de procesos; cola de trabajos; map-reduce | 5.1 latido bloqueado; 5.2 latido + proceso; 5.3 carrera; 5.4 Lock → tema 5 |
| 6 | `vectorizar` | 12 | vectorizar, `float64` vs `int64`, cuándo no | cmp-vectorizar | costo por elemento: $T \approx N\,c_{py}$ vs $c_0 + N\,c_{C}$ | **empujar el cálculo al motor** (NumPy/Polars/SQL) antes de repartir | 6.1 bucle vs NumPy; 6.2 int64 → tema 6 |
| 7 | `elegir-la-estrategia` | 8 | árbol, costos medidos, anti-patrones | cmp-arbol-decision, **cmp-arq-servidores** (3 modelos de servidor) | — | integra las 6 filas «decisión hasta aquí»; caso: ETL que baja 500 páginas de API y agrega | 7.1 lambda a proceso; 7.2 pool por llamada → tema 7 |
| A | `notacion-computo` (`A_notacion.md`) | 0 | hoja de símbolos | — | tabla única de símbolos | — | — |

Corte en clase: página 6 a lectura, luego Amdahl (5), luego `cmp-arq-servidores` (7). Las páginas 2–4 no se recortan.

**Notación (única, en `A_notacion.md`; se corrige la de p26):** $T=[0,\infty)$; $\mathcal{T}=\{\tau_1..\tau_n\}$; $life(\tau)=[start,end)$ **semiabierto** (con cerrados, dos tareas en secuencia que se tocan en un punto serían «concurrentes»); $life = exec \,\dot\cup\, wait \,\dot\cup\, ready$; $E(t)=\{\tau: t\in exec(\tau)\}$, $|E(t)|\le P$; $e_i=|exec(\tau_i)|$, $w_i=|wait(\tau_i)|$; $\rho_i=w_i/|life(\tau_i)|$. Concurrente: $\exists i\ne j: life_i\cap life_j\neq\emptyset$. Paralelo: $\exists t: |E(t)|\ge2$ (exige $P\ge2$). Cotas: $\max_i(e_i+w_i)\le T\le\sum_i(e_i+w_i+r_i)$ y $T\ge\sum_i e_i/P$. Speedup $S_P=T_{seq}/T_P$. Amdahl: $S_P=1/(s+(1-s)/P)$ — **`s` minúscula**: hoy `4_vectorizar.md` usa `S` para la fracción serial y `5_…` llama `S` a otra cosa.

**La contradicción del 2×2.** Con estas definiciones, Paralelo ⇒ Concurrente es teorema ($t\in exec_i\cap exec_j\subseteq life_i\cap life_j$), así que la celda «paralelo y no concurrente» de `cmp-matriz-2x2` es **vacía**. NumPy no es excepción: es el mismo teorema a otra granularidad (sus subtareas internas son las $\tau$). Se reemplaza por `cmp-conjuntos` (secuencial | concurrente ⊃ paralelo) y por `cmp-matriz-asincrono`, una 2×2 **correcta**: *modelo de escritura* (bloqueante / asíncrono) × *concurrente* (no / sí) → secuencial, hilos, `await` en serie, `gather`. «Asíncrono» es propiedad del código (la llamada regresa antes del resultado y se cede con `await`), no del conjunto de intervalos; lo medible es $Aprov(i,j)$, que implica concurrencia.

## 4 · El event loop

Definición operativa: un **tick** = (1) correr, una tras otra, todas las tareas de la **cola de listas** hasta su siguiente `await` o su fin; (2) pedir al SO las esperas cumplidas (`select`) con timeout = el temporizador más próximo; (3) pasar a listas las que despertaron.

Traza (`gather(A, B, C)`; cada una ejecuta 10 ms, `await asyncio.sleep(d)`, ejecuta 10 ms; $d_A=0.3$, $d_B=0.1$, $d_C=0.2$):

| tick | t (s) | ejecutando | cola de listas | esperando (vence) | qué pasó |
|---:|---:|---|---|---|---|
| 0 | 0.00 | main | — | — | `gather` crea 3 `Task`; main hace `await` |
| 1 | 0.00–0.03 | A → B → C | [A,B,C] → [] | A(0.31) B(0.12) C(0.23) | cada una corre hasta su `sleep` |
| — | 0.03–0.12 | nadie | [] | A, B, C | `select` duerme hasta el más próximo; CPU libre |
| 2 | 0.12 | B | [B] | A, C | B termina; gather guarda su resultado |
| 3 | 0.23 | C | [C] | A | C termina |
| 4 | 0.31 | A | [A] | — | A termina; el futuro de gather se completa → main a listas |
| 5 | 0.32 | main | [main] | — | recibe `[rA, rB, rC]`: orden de argumentos, no de llegada |

**Figura nueva `cmp-event-loop-ticks`:** columnas = ticks; tres carriles (ejecutando / listas / esperando) con fichas A, B, C que se mueven; abajo la fila de CPU. Sustituye a `cmp-event-loop` (diagrama de flujo sin tiempo).

Las cuatro primitivas, con dibujo en vez de bullets:

| Primitiva | Figura | Qué muestra |
|---|---|---|
| `create_task` | `cmp-create-task` | dos Gantt: `c = f()` (objeto inerte, no aparece en «listas») vs `create_task(f())` (entra a listas en el tick siguiente aunque nadie la espere) |
| `gather` | `cmp-gantt-gather` | fan-out en un tick, esperas solapadas, fan-in: main queda en «esperando» hasta la última |
| `Semaphore(k)` | `cmp-flujo-semaforo` + `cmp-gantt-semaforo` | flujo acquire/release con contador; Gantt de 8 tareas, $k=3$: tandas y una franja ámbar «espera permiso» distinta de «espera red» |
| `run_in_executor` | `cmp-run-in-executor` | carril del hilo del loop (latidos cada 100 ms siguen) + carril del proceso trabajador (cálculo 2 s); flecha `Future` de vuelta |

Todas usan `_gantt()` de `gen_computo.py` (agregar el tipo `"permiso"` a `_segmento`).

## 5 · Notebook nuevo

**Fuente propia, no las páginas:** `tools/notebook_computo/` con un archivo por tema en formato *percent* (`# %%` código, `# %% [markdown]` texto), parseado por el generador sin dependencias:

```
tools/notebook_computo/00_arranque.py   comprobar servidor, gantt.py
01_tiempo.py     relojes; v1 del cliente (for + requests) con traza y Gantt medido
02_hilos_procesos.py  v2 (ThreadPoolExecutor); 1/2/4 procesos; gráfica speedup vs P y Amdahl
03_event_loop.py  corrutina/Task/create_task; traza por tick instrumentada (loop.call_soon, prints con tick)
04_cliente_500.py v3 gather sin tope (20) → v4 gather+Semaphore(32) (20/100/500, gráfica T vs N contra ⌈N/k⌉·0.2) → v5 Semaphore + reintento ante error + Queue productor-consumidor; tabla final v1..v5
05_paralelo.py   latido bloqueado, run_in_executor, carrera, Lock
06_vectorizar.py 07_estrategia.py
```

Reglas: verbose; **cada versión repite el código completo de la anterior y marca con `# NUEVO:` lo que cambia**; cada tema cierra con una celda `assert` (p. ej. `assert set(codigos) == {200}`, `assert t_v4 < t_v1 / 5`) y con un Gantt medido por `gantt.py` (`registra(nombre, inicio, fin, tipo)` + `dibuja()` con matplotlib). Cargas: ≤ 500 llamadas, ≤ 4 procesos.

`tools/gen_notebook_computo.py`: `FUENTE = RAIZ / "tools/notebook_computo"`, `DESTINO = RAIZ / "codigo/11_computo/computo.ipynb"`; une los temas en orden. Vínculo con las páginas: toda celda de página `**Haz (celda k.m)**` debe aparecer **literal** en el notebook en una celda que empiece con `# celda k.m`.

`tools/test_computo_curriculum.py` (reescritura): rutas nuevas; notebook == generador; sin salidas; cada `Haz` de página está literal en el notebook; numeración k.m por página; ningún `asyncio.run(`; compila con top-level await; lo que va a procesos sale de `trabajo_computo`; `servidor.py`/`cable.py` idénticos a `10_apis`; `pyproject` pide `httpx`, `numpy`, `matplotlib` + `uv.lock`; sin analogías; **nuevo** `test_codigo_solo_al_final` (ningún ```` ```python ```` antes de `## Código`); **nuevo** `test_etiquetas_en_orden` (Otro ángulo/Matemática/Ejemplo/Arquitectura nunca desordenadas dentro de un `##`); **nuevo** `test_notacion` (no `S =` como fracción serial; todo `\tau`, `exec`, `wait`, `ready`, `E(t)` usado aparece en `A_notacion.md`); celda 1.1 contra servidor real (como hoy).

## 6 · Ejecución en enjambre

Rama `feat/unidad-11-computo`, una worktree por agente de fase 2.

| Fase | Agente | Archivos (disjuntos) | Modelo |
|---|---|---|---|
| 0 secuencial | yo | `git mv` de directorio/_assets/trabajo_computo; esqueleto `0_index`, `A_notacion.md` (notación congelada); rutas en `gen_computo.py`, `test_gen_computo.py`; `codigo/11_computo/` + `uv lock` (red); `10_apis/0_index.md` | Opus 5.5 |
| 1 secuencial | figuras | `gen_computo.py` (8 nuevas, quitar `cmp-matriz-2x2`/`cmp-event-loop`), `test_gen_computo.py`, `CREDITOS.md`, regenerar SVG | Codex gpt-6-astra (determinista, mucho SVG) |
| 2 paralelo | P1…P7 | una página cada uno (`1_…md` … `7_…md`) | Opus 5.5 en 2, 3, 4 (matemática, event loop); Sonnet 5.5 en 1, 5, 6, 7 |
| 2 paralelo | NB-a / NB-b | `notebook_computo/00–03` / `04–07` + `gantt.py` | Sonnet 5.5 |
| 2 paralelo | gen-nb | `gen_notebook_computo.py`, `test_computo_curriculum.py` | Codex gpt-5.6-sol |
| 3 secuencial | yo | regenerar notebook; correr celdas con cargas chicas para «Deberías ver» reales; `CLAUDE.md`+`AGENTS.md`; calendario | Opus 5.5 |
| 4 adversarial | R1 matemática · R2 pedagogía/plantilla/sin analogías · R3 CI/ids/rutas | sólo lectura, hallazgos con línea | R1 Opus 5.5 · R2 Codex astra (`codex exec … < /dev/null`) · R3 Sonnet 5.5 |
| 5 | yo | arreglos, `pytest tools/ -q`, `raya validate`, `raya build`, commit `feat(unidad-11): …` | — |

Puntos de sincronía: la notación (fase 0) y los ids de figura (fase 1) se congelan antes de la fase 2; los agentes de página no tocan `_assets/` ni `gen_*`.

## 7 · Riesgos

- **Ids course-wide:** `cmp-*` se mueven, no se duplican; borrar `cmp-matriz-2x2`/`cmp-event-loop` del catálogo **y** del disco (huérfano falla `test_gen_computo`). Ids de definición con prefijo `cmp-def-`. Ids de página nuevos no deben chocar (`vectorizar` ya existe: se mueve, no se copia).
- **Tests que fallarán al mover:** `test_gen_computo.py` (`ASSETS`, `UNIDAD`), `test_computo_curriculum.py` (`SECCION`, `PLANTILLA`, `test_numeracion_consecutiva` que usa `nombre[0]`; `A_notacion.md` no empieza con dígito), `test_creditos.py` (CREDITOS viaja con el directorio), `test_wikilinks.py` (`[[computo-y-concurrencia]]` en `10_apis/0_index.md` sigue válido), `test_svg_tamano_intrinseco.py` (glob global, OK).
- **`raya validate`:** `prerequisites` de la unidad (`apis-y-http`, `el-gil`) deben existir; `$` en prosa fuera de math (`$GHUSER`) va en code span; `@` en code span; quotes en `summary` con dos puntos; wikilinks en tablas sin `\|`.
- **CI sin dependencias:** el job `checks` no instala `httpx`/`numpy`/`matplotlib`: toda prueba que los importe usa `pytest.importorskip`.
- **Alumnos con `clase-10-computo` ya copiado:** su copia queda; el `0_index` de la unidad explica copiar `codigo/11_computo/` (incluye servidor) y `uv sync` con red (matplotlib es descarga nueva).
- **Sesión de 90 min vs 120 de material:** corte declarado en el `0_index`; confirmar con el profesor si `session-17` se reprograma.
- **URL cambia:** el notebook y cualquier enlace externo a `/apis/computo-y-concurrencia/` quedan rotos; actualizar el texto del notebook.
