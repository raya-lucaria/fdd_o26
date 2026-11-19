# Unidad 11 · Cómputo y concurrencia — replanteo (clase de hoy, 2026-10-27)

> **Sólo la clase de hoy.** 10.3 (patrones y protocolos) y 10.4 (arquitectura de APIs) quedan fuera hasta nuevo aviso.
> Este documento es el **plan**; no se ha modificado ninguna página. Reemplaza a `2026-10-27-unidad-10-computo-y-arquitectura.md` en lo que contradiga.
> Anexos con el detalle (léelos antes de ejecutar): `2026-10-27-unidad-11-anexos/{A_matematica,B_arquitectura,C_diseno_y_enjambre}.md`.

## 1 · Lo que pidió el profesor (decisiones fijadas)

1. **Unidad propia**, fuera de `10_apis`.
2. **Matemática del curso anterior** (T, τ, exec, wait, ExecutingAt, P, concurrencia, asíncrono, paralelo…) introducida paso a paso, con notación **consistente y correcta**.
3. **Orden de cada concepto:** qué es (formal/claro) → diagrama, lista o tabla (otro punto de vista) → matemática → ejemplo → **patrón de arquitectura + ejemplo** → **código hasta el final**.
4. **Mucha arquitectura**, presente desde la primera página (cuándo sí, cuándo no, qué significa); «elegir estrategia» queda al final pero se va construyendo.
5. **El código es lo último y lo que menos pesa:** párrafos breves, comentarios por línea, ejecuciones, trazas o diagramas simplificados; explicar lo que no es Python clásico (`async`, `await`, `Semaphore`, `gather`, `run_in_executor`…) para entender **qué hace y por qué**, no la sintaxis. `gather` y `Semaphore` se explican con Gantt y diagramas de flujo, no con bullets línea por línea.
6. **Event loop explicado mejor.**
7. **Notebook nuevo:** ahí sí verbose y repetido, construido por tema, expandiéndose hasta el último paso.
8. Sin analogías. Textos largos → listas, tablas, diagramas. Acortar sólo lo que no pierde calidad.

## 2 · Hallazgos de la auditoría (swarm de revisión) que cambian el contenido

**Matemática (detalle en `A_matematica.md`).**

| # | Hallazgo | Consecuencia |
|---|---|---|
| 1 | Con las definiciones de p26, **paralelo ⇒ concurrente** (teorema). | La celda «paralelo sin concurrente» de `cmp-matriz-2x2` está **vacía por teorema**; NumPy no la llena (`arr*arr` usa un núcleo; SIMD es paralelismo de datos por debajo del modelo de tareas; BLAS reparte en hilos, que son paralelos *y* concurrentes a su escala). Se reemplaza por `cmp-conjuntos` + una 2×2 correcta (ver §5). |
| 2 | p26 usa intervalos cerrados: dos tareas consecutivas «se tocan» y salen concurrentes. | **Intervalos semiabiertos** `[start, end)`. |
| 3 | «Asíncrono ≡ exec(τⱼ)∩wait(τᵢ)≠∅» también lo cumplen los hilos e implica concurrencia. | **Asíncrono = mecanismo** (la llamada regresa antes del resultado y quien espera cede su hilo con `await`), no una celda del Gantt. Lo medible es «solapa esperas» y, dentro del mismo hilo, sólo es posible si se cedió el control. Cooperativo (loop) vs preventivo (hilos/GIL). |
| 4 | «CPU-bound ≡ wait=∅» vuelve I/O-bound cualquier tarea con un byte de E/S. | Razón **ρ = \|exec\|/d**, medida con la tarea sola. |
| 5 | exec ∪ wait no cubre la vida; falta el estado **lista** (ready). | **Partición** exec/wait/ready; prueba operativa: «si le doy una CPU libre ahora, ¿avanza?». |
| 6 | `T` designaba tres cosas; `S` era fracción serial y speedup. | `t` instante, `T` makespan, `f` fracción serial, `S(N)` speedup, `E(N)` eficiencia. |
| 7 | P = «cores físicos»; GIL «nunca se libera». | P = CPU lógicas; el GIL se cede cada 5 ms, lo que nunca hay es simultaneidad. |
| 8 | Jerarquía «Distribuido ⊇ Paralelo ⊇ Concurrente» al revés. | Paralelo ⊆ concurrente; distribuido es otro eje (no se desarrolla hoy). |
| 9 | La Ley de Little sí hace falta. | Entra: dimensionar `Semaphore`, pool o cola es aplicar L = λ·W. |

**Errores en nuestras páginas a corregir al reescribir:** p1:31 (reloj = suma de **tres** tramos, aislada ready=0); p2:170 (el «ideal» 2.34/4 supone f=0: usar el ajuste T(N)=a+b/N → f≈0.24, techo≈4.2×, una corrida, 3 puntos); p3:151 («tandas»: el semáforo es una ventana deslizante; usar Little); p4:200 (`S`→`f`); p4:244 (un costo fijo **sí** entra en f).

**Arquitectura (detalle en `B_arquitectura.md`).** 17 patrones con cuándo sí/no/riesgo/sistema real; Ley de Little cuadra con las mediciones (32 hilos × 500 llamadas: ideal 160/s, medido 151/s; cota ⌈500/32⌉·0.2 = 3.2 s vs 3.32 s medido); el servidor de la clase es un caso real de **hilo por conexión sin tope** con un único `Lock`; 6 diagramas `cmp-arq-*`; 3 casos (scraper de 10 000 URLs, API que sirve un modelo —cifras de ese caso son supuestos y se rotulan—, pipeline de 3 APIs).

### 2b · Lo que añadieron los tres revisores de Codex (anexos D, E, F)

Coinciden con los de Claude en lo central (paralelo ⇒ concurrente, intervalos semiabiertos, event loop por estados, mover el código al final, 17 patrones de arquitectura). Lo nuevo, ya incorporado al plan:

- **Convención de inicio:** separar `arrival` (llega la solicitud) de `start` (se admite). `latencia = end − arrival`; `end − start = e + w + r + b`. Hay que fijarla en la fase 0 porque cambia cómo se dibuja la cola. Adoptamos la de Codex (todas llegan y se admiten en 0, la espera de turno es `ready` rayado); las figuras actuales (`cmp-gantt-asyncio`: 280 ms) cuadran con ella.
- **Quinto estado `blocked`** (esperando un permiso: semáforo, lock) distinto de `wait` (E/S); se introduce hasta la página de `Semaphore`.
- **GIL formal:** `exec_Python(τ) ⊆ exec(τ)`; por intérprete con GIL, a lo más una tarea ejecuta Python a la vez. No impone P=1 ni limita código nativo que libera el GIL (NumPy).
- **Speedup con referencia explícita:** `speedup_pool(k) = D_pool(1)/D_pool(k)` vs `speedup_aplicación(k) = D_secuencial_directa/D_pool(k)`. Con n trabajos iguales indivisibles: `D_pool(k) ≈ ⌈n/min(k,P)⌉·c + h(k)`. Las mediciones 2.34/1.45/1.00 s **no** identifican f por sí solas; el ajuste T(N)=a+b/N se presenta como ilustración de una corrida.
- **Ejemplo de Amdahl con carga exclusivamente de CPU** (preparación serial 40 ms + dos tareas de 100 ms; D=140, speedup 12/7; el techo 1/f=6 sólo vale si el resto es divisible). No mezclar con el solapamiento de E/S.
- **Errores numéricos de p26** que no deben heredarse: tabla de Amdahl (1.07/1.08 → 1.08/1.10), «3.6 s vs 0.6 s» de ocio (3.6/0.8 = 4.5×).
- **Cortar de las páginas** el 10.91 s de `asyncio` con 100 conexiones (corrida única confundida por pool, CPU y sin repeticiones): pasa al notebook como ejercicio con repeticiones. También sale «100 hilos o 1000 corrutinas es válido» (depende de sockets, memoria, dependencia remota).
- **Mover al índice y quitar de las páginas:** «Antes de la clase» y «Arranque de la sección» (hoy duplicados); y retirar «Qué no cubre» salvo lo realmente fuera de alcance.
- **Arquitectura desde el inicio:** capacidad, latencia de servicio vs latencia de cola, throughput, p99 y Ley de Little se introducen *durante* la unidad, no al final; `gather`, semáforo y cola son **tres decisiones distintas** (agrupar, acotar, desacoplar).
- **Tabla de propiedades verificable con el Gantt** (7 ejecuciones ilustradas × vidas solapadas / ejecución durante espera ajena / máximo ejecutando / paralela / interfaz asíncrona) y la regla «no deduzcas paralelismo de una reducción del tiempo total». Va en `A_notacion.md`.
- **Cuidado al presentar 99.3 %:** es el tiempo sin CPU del cliente (espera + turno), no Σw exacta; `process_time` cuenta todo el proceso.

## 3 · Estructura de la unidad

Unidad plana (como `6_expresiones_regulares/`), **mismo id `computo-y-concurrencia`** (así `session-17` no cambia).

| Qué | Antes | Después |
|---|---|---|
| Directorio | `course/10_apis/2_computo_y_concurrencia/` | `course/11_computo_y_concurrencia/` (`git mv`) |
| URL | `/apis/computo-y-concurrencia/` | `/computo-y-concurrencia/` (**el enlace que se está leyendo hoy cambia**; valorar `aliases`) |
| Figuras | `course/10_apis/_assets/` | `course/11_computo_y_concurrencia/_assets/` (+ `CREDITOS.md`); rutas en páginas `_assets/…` |
| Código del alumno | `codigo/10_apis/{computo.ipynb,trabajo_computo.py}` | `codigo/11_computo/` con `computo.ipynb`, `trabajo_computo.py`, `gantt.py` (nuevo), copias idénticas de `servidor.py` y `cable.py` (test que las vigila), `pyproject.toml` (+`matplotlib`) y `uv.lock` propios |
| `10_apis/0_index.md` | 2 secciones | 1 sección + una línea que enlaza a la unidad nueva |
| Rama del alumno | `clase-10-computo` | `clase-11-computo`, sin PR (**confirmar con el profesor**) |
| Docs | `CLAUDE.md`/`AGENTS.md` mencionan 10.2 | actualizar ambos en el mismo commit |

## 4 · Plantilla de página (la que pidió el profesor)

Cada concepto es un `##` con **etiquetas fijas, en orden**; el código vive **sólo** en un `## Código` final.

```
# Título · Pregunta · Meta · tabla-glosario de la página
## En corto (3 viñetas)
## <Concepto>
   ::: definition      qué es, formal o claro
   **Otro ángulo.**    Gantt / tabla / lista / diagrama
   **Matemática.**     $…$ con la notación de A_notacion (si aplica)
   **Ejemplo.**        números concretos (Gantt ilustrativo o medición real)
   **Arquitectura.**   patrón: qué es, cuándo sí, cuándo no, qué cuesta, sistema real
## La decisión hasta aquí     (tabla acumulativa que crece por página)
## Código                      (≤15 líneas por celda, comentario por línea no obvia,
                               "Qué pasó": traza/Gantt/tabla, "Deberías ver")
## Al diseñar / al revisar código de IA, busca…
```

Tests nuevos que lo protegen: `test_codigo_solo_al_final`, `test_etiquetas_en_orden`, `test_notacion` (todo símbolo usado aparece en `A_notacion.md`; no `S` como fracción serial).

## 5 · Páginas de hoy (≈115 min de material para una sesión de 90: el corte está marcado)

| # | id (archivo) | Min | Conceptos | Matemática | **Arquitectura** | Figuras (nuevas en **negrita**) |
|---:|---|---:|---|---|---|---|
| 1 | `donde-pasa-el-tiempo` | 12 | tarea, estados exec/espera/lista, CPU-bound/I/O-bound, secuencial | t, τ, vida, exec, wait, ready, partición, ρ, T=Σd; ejemplo único 3 tareas (20/200/20 ms) | **presupuesto de latencia** de un endpoint (BD 50 ms + API 1.5 s + CPU 1 ms); «mide antes de elegir» | **cmp-estados-tarea**, **cmp-intervalos**, cmp-gantt-secuencial |
| 2 | `secuencial-concurrente-paralelo` | 22 | proceso/hilo/CPU/GIL (tabla + `[[el-gil]]`), concurrente, paralelo, teorema, carrera | def. concurrente y paralelo; paralelo ⇒ concurrente; cotas de T; \|E(t)\|≤P (GIL: ≤1 por intérprete); S(N), E(N) | **hilo por conexión** vs **prefork** (el servidor de la clase como caso); cuándo no | cmp-gantt-hilos, cmp-gantt-procesos, **cmp-conjuntos** (reemplaza matriz) |
| 3 | `asincrono-y-el-event-loop` | 22 | asíncrono (mecanismo), corrutina, `Task`, `create_task`, **event loop tick a tick** | solapa esperas ⇒ concurrente; cooperativo vs preventivo; ready en el loop | **servidor event loop** (miles de conexiones en un hilo); cuándo no: manejador que calcula | **cmp-event-loop-ticks** (reemplaza `cmp-event-loop`), cmp-gantt-asyncio, cmp-gantt-await-en-serie, **cmp-matriz-asincrono** (2×2 correcta: bloqueante/asíncrono × concurrente), **cmp-create-task** |
| 4 | `concurrencia-acotada` | 18 | `gather`, `Semaphore(k)`, límite del cliente, tope ≠ rate limit | ⌈N/k⌉·(e+w); **Little** L=λ·W y λ≤k/W; ejemplo 500 llamadas | **scatter-gather**, **backpressure**, dimensionar el tope (cuánto acepta el servidor) | **cmp-gantt-gather**, **cmp-gantt-semaforo**, **cmp-flujo-semaforo** |
| 5 | `calcular-en-paralelo` | 15 | bloquear el loop, `run_in_executor`, procesos, carrera + `Lock`, Amdahl | f, S(N)=1/(f+(1−f)/N), ajuste T(N)=a+b/N | **offload**: loop + pool de procesos; cola de trabajos; cuántos workers | cmp-bloqueo-del-loop, **cmp-run-in-executor**, cmp-amdahl, **cmp-arq-offload** |
| 6 | `vectorizar` | 10 | vectorizar, `float64` vs `int64`, cuándo no | T≈N·c_py vs c₀+N·c_C | **empujar el cálculo al motor** (NumPy/Polars/SQL) antes de repartir | cmp-vectorizar |
| 7 | `arquitectura-y-estrategia` | 16 | **arquitectura de un servicio** + árbol de decisión + anti-patrones | integra: ρ, f, Little | los **3 modelos de servidor** lado a lado; **3 casos** (scraper 10 000 URLs; API que sirve un modelo —cifras supuestas, rotuladas—; pipeline de 3 APIs) | **cmp-arq-servidores**, cmp-arbol-decision, cmp-arq-little |
| A | `notacion-computo` (`A_notacion.md`) | — | hoja de símbolos única | tabla de símbolos | — | — |

**Corte** en clase: p6 a lectura → Amdahl (p5) → anti-patrones (p7). Las páginas 2–4 no se recortan.

**Matriz 2×2 (decisión):** se reemplaza por tres casos (secuencial | concurrente sin paralelo: hilos con GIL y `asyncio` | concurrente y paralelo: procesos) + la nota: «lo que a veces se llama paralelo sin concurrente es un cambio de escala (una operación que por dentro reparte); SIMD es paralelismo de datos, no de tareas; asíncrono no es una fila, es *cómo* cede el control quien espera».

### Event loop (explicación nueva, página 3)

Definición operativa: un **tick** = (1) correr, una tras otra, todas las tareas de la **cola de listas** hasta su siguiente `await` o su fin; (2) preguntar al sistema qué esperas ya se cumplieron (`select`) con timeout = el temporizador más próximo; (3) pasar a listas las que despertaron. Traza `gather(A,B,C)`, cada una 10 ms ejecuta + `sleep(d)` + 10 ms (d_A=0.3, d_B=0.1, d_C=0.2): tabla por tick con columnas *ejecutando / cola de listas / esperando (vence) / qué pasó* (ver `C_diseno_y_enjambre.md` §4) y la figura **`cmp-event-loop-ticks`** (carriles ejecutando/listas/esperando con fichas que se mueven; fila de CPU debajo). Las cuatro primitivas (`create_task`, `gather`, `Semaphore`, `run_in_executor`) se explican con **una figura cada una** (§5, tabla de figuras), no con viñetas por línea.

### Código (siempre al final de la página)

- ≤ 15 líneas por celda, comentario por línea no obvia, sin bullets «qué hace cada línea».
- Un cuadro «**Python que quizá no has visto**» por celda: `async def`, `await`, `async with`, `asyncio.gather(*…)`, `Semaphore`, `run_in_executor`, `if __name__ == "__main__"`: qué es, qué hace, **por qué hace falta aquí**.
- «Qué pasó»: traza o Gantt simplificado de **esa** ejecución; «Deberías ver»: salida real.
- «La versión larga está en el notebook, tema k.»
- Cada `**Haz (celda k.m)**` debe aparecer literal en el notebook.

### Notebook nuevo (`codigo/11_computo/computo.ipynb`)

Fuente propia (no las páginas): `tools/notebook_computo/NN_tema.py` en formato percent (`# %%`), parseada por `tools/gen_notebook_computo.py`. Un archivo por tema (`00_arranque`, `01_tiempo`, `02_hilos_procesos`, `03_event_loop`, `04_cliente_500`, `05_paralelo`, `06_vectorizar`, `07_estrategia`). **Verbose y repetido a propósito:** el cliente de 500 llamadas aparece en 5 versiones (for+`requests` → hilos → `gather` sin tope → `gather`+`Semaphore` → +reintento y `Queue`), cada una con el código completo de la anterior y `# NUEVO:` marcando el cambio; cada tema cierra con un `assert` y un Gantt medido (`gantt.py`: `registra()` + `dibuja()` con matplotlib), y una tabla final v1…v5. Cargas: ≤ 500 llamadas, ≤ 4 procesos.

## 6 · Ejecución en enjambre (se lanza sólo tras tu visto bueno)

Rama `feat/unidad-11-computo`; una worktree por agente de la fase 2. **No lanzar `pytest tools/` desde varios agentes: una corrida al final.** Revisores leen, no ejecutan. Carga de CPU de mediciones: ≤ 4 procesos.

| Fase | Agente(s) | Archivos (disjuntos) | Modelo |
|---|---|---|---|
| 0 · secuencial | Yo (mover y congelar contrato) | `git mv` de directorio, `_assets`, `trabajo_computo.py`; `codigo/11_computo/` + `uv lock`; `0_index` + `A_notacion.md` (**notación congelada**); rutas en `gen_computo.py`/`test_gen_computo.py`; `10_apis/0_index.md` | Opus 5.5 |
| 1 · secuencial | Figuras | `gen_computo.py` (≈ 14 nuevas, quitar `cmp-matriz-2x2` y `cmp-event-loop`), `test_gen_computo.py`, `CREDITOS.md`, SVG regenerados | Codex `gpt-6-astra` (determinista, mucho SVG) |
| 2 · paralelo | P1…P7 | una página cada uno (`1_…md`…`7_…md`) | Opus 5.5 en P2, P3, P4, P5 (matemática y event loop); Sonnet 5.5 en P1, P6, P7 |
| 2 · paralelo | NB-a / NB-b | `tools/notebook_computo/00–03` / `04–07` + `gantt.py` | Sonnet 5.5 |
| 2 · paralelo | gen-nb | `gen_notebook_computo.py`, `test_computo_curriculum.py` (reescritura) | Codex `gpt-5.6-sol` |
| 3 · secuencial | Yo | regenerar notebook; correr celdas con cargas chicas → «Deberías ver» reales (una vez); sustituir marcadores; `CLAUDE.md`+`AGENTS.md`; calendario | Opus 5.5 |
| 4 · adversarial | R1 matemática · R2 plantilla/pedagogía/sin analogías/verbosidad · R3 CI/ids/rutas · R4 arquitectura | sólo lectura, hallazgos con línea y reemplazo exacto | R1 Opus 5.5 + Codex `gpt-6-astra`; R2 Codex `gpt-6-astra` (`codex exec … < /dev/null`); R3 Sonnet 5.5; R4 Opus 5.5 |
| 5 · secuencial | Yo | aplicar hallazgos; `raya validate`; **una** `pytest tools/ -q`; commit `feat(unidad-11): …`; push; verificar el deploy | — |

Congelar antes de la fase 2: notación (`A_notacion.md`), ids de figura y ids de página. Los agentes de página no tocan `_assets/` ni `gen_*`.

## 7 · Riesgos

- **ids course-wide:** `cmp-*` se mueven, no se duplican; borrar del catálogo **y** del disco las figuras que se reemplazan (huérfano falla `test_gen_computo`). `vectorizar` ya existe como id: se mueve, no se copia. Ids de definición con prefijo `cmp-def-`.
- **Tests que fallan al mover:** `test_gen_computo` (`ASSETS`, `UNIDAD`), `test_computo_curriculum` (`SECCION`, `PLANTILLA`, numeración que usa `nombre[0]`), `test_creditos`, `test_wikilinks`.
- **CI sin dependencias:** el job `checks` no instala `httpx`/`numpy`/`matplotlib`/`requests`: toda prueba que los importe usa `pytest.importorskip` (ya nos mordió una vez).
- **`$` en prosa:** el renderizador carga `dollarmath`; nunca un `$` suelto fuera de math o de un code span (añadirlo a `CLAUDE.md` junto a la regla del `@`).
- **Cambio de URL** en un sitio que ya está publicado: ver pregunta 3.
- **Sesión de 90 min vs ~115 min de material.**
- **Medir procesos con `process_time`** da ≈ 0 (no cuenta hijos): usar `os.times()` (campos *children*) o dejar la columna CPU fuera de la tabla de procesos.

## 8 · Decisiones que necesito de ti antes de lanzar

1. **Duración real de hoy:** ¿90 min (corte marcado) o 120? Si son 120 se mueven calendario, `course/0_index.md` y `README.md` juntos.
2. **Rama de la clase:** `clase-11-computo` sin PR (mi propuesta) o seguir con `clase-10-apis`.
3. **URL del sitio:** al mover la unidad, `/apis/computo-y-concurrencia/` deja de existir. ¿Pongo `aliases` para que el enlace actual siga funcionando mientras reescribimos?
4. **LaTeX con `$…$`** para la matemática (lo recomiendan los dos auditores; la unidad 3 ya lo usa). ¿De acuerdo?
5. **Página 7:** la arquitectura ocupa una página propia (`arquitectura-y-estrategia`). ¿La dejo ahí o la reparto sólo dentro de las otras?
