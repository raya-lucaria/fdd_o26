# Clase 11.2 (jueves 29 oct, 19:00) · Plan detallado de ejecución · v2 (tras la revisión de Astra)

Cubre las páginas 9–12, D1 y D2, el notebook, la integración y el enjambre. Parte de `2026-10-29-unidad-11-bloques-2-3.md`.

## A. Diagnóstico de la forma de la 11.1
Las ocho páginas tienen 2 700–7 600 palabras (media ≈ 5 700, contando código y metadatos): definiciones de 4–8 líneas con excepciones dentro, «Otro ángulo», la misma figura repetida en tabla de texto, y conceptos vecinos que se cuelan. Meta de las nuevas: 500–800 palabras **de contenido** (sin código, metadatos ni alt), una pregunta, una respuesta directa.

## B. Patrones de escritura
Orden por concepto fijado por el profesor: definición → figura/tabla/lista → matemática → ejemplo → arquitectura → código al final (en el notebook).

1. **Respuesta directa primero.** Bajo el título: la pregunta y, en una o dos frases, su respuesta. Cada concepto termina con **qué decisión permite tomar**.
2. **Una página, una pregunta, un caso principal** con parámetros compartidos entre figura, cuenta y notebook. Un segundo cálculo se admite si se justifica en una frase.
3. **Por concepto, en este orden y sólo las partes que aporten:** `**Definición.**` (con su explicación, siempre) · `**Figura.**` (figura, tabla o lista) · `**Cuenta.**` (si hay cuenta: fórmula display, los pasos necesarios para entenderla y la misma cuenta con números) · `**Ejemplo.**` · `**Arquitectura.**` (Qué es · Cuándo sí · Cuándo no · Qué cuesta · sistema real). **Cada página trae al menos un bloque de arquitectura**; por concepto, cuando aporte.
4. **Definición:** una frase «X es Y que Z», con el término en negrita; las condiciones sin las que sería falsa se quedan dentro; excepciones y variantes van a «Si hay tiempo». Más de 25 palabras es señal de revisar, no prohibición.
5. **Carga cognitiva:** a lo más 4 términos nuevos por concepto; los prerrequisitos se listan aparte en una línea de recordatorio con su definición literal.
6. **La figura se lee sola:** título = conclusión, pie de una línea, alt accesible. No se duplica en tabla ni se narra paso a paso; sí se permite una línea de «cómo leerla».
7. **Frases cortas** (señal a 22 palabras), párrafos de pocas frases (orientación), sin preámbulos («como vimos», «vale la pena notar»), sin «Otro ángulo», sin énfasis adjetival.
8. **Prosa para definir y explicar; tabla para comparar; lista para pasos.** Tablas ≤ 5 columnas.
9. **Cifras clasificadas:** cada número es *supuesto*, *calculado*, *documentado* o *medido*, y el texto lo dice (p. ej. «medido en 8 CPU», «supuesto del ejemplo»). Las mediciones se escriben `{{m:clave}}` hasta sustituirlas.
10. **Matemática:** un significado por símbolo dentro de una frontera explícita (los de `A_notacion.md`); fórmula display y la cuenta con números en la línea siguiente; se muestran los pasos necesarios para entender la cuenta, no demostraciones.
11. **Supuestos junto a la afirmación**, nunca en «Si hay tiempo» cuando la vuelven verdadera.
12. **Sin código en las notas;** la página cita «celda N.M» y la salida esperada.
13. **Sin analogías.** Comparaciones técnicas con número o comando.
14. **Lo que no contesta la pregunta se borra o se enlaza** con `[[id]]` a la 11.1.

**Antes / después** (de `4_concurrencia_acotada`, `gather`): antes, un bloque de ~110 palabras con fan-out, fan-in y tres viñetas de fallos; después, «`gather(c₁…cₙ)` agenda las n corrutinas como tareas y, cuando todas terminan sin error, entrega sus resultados en el orden de los argumentos.» (la condición se queda); el caso de fallo pasa a «Si hay tiempo».

**Guardas mecánicas** (`test_computo_forma.py`, páginas ≥ 9): aviso > 800 palabras de contenido · partes en orden y definición/figura/arquitectura presentes · sin «Otro ángulo» ni frases de relleno · sin bloques de código · aviso en definiciones > 25 palabras y frases > 22 · ≥ 1 figura, tabla o lista por concepto (se cuentan tablas, pies y texto dentro de SVG por separado) · cada `{{m:…}}` sustituido · referencias resueltas (celda única, enlace, figura, alt, crédito) · párrafos duplicados normalizados (excepto definiciones canónicas) · parámetros página–figura–notebook iguales como *nombre–valor–unidad–supuesto*.
**Prueba humana:** el revisor-alumno, sólo con los prerrequisitos declarados, debe explicar la conclusión y resolver una variación del ejemplo.

## C. Especificación por página (con las correcciones de Astra)
Parámetros y glosario, en el contrato.

### Página 9 · `sistemas-distribuidos` (11.1) · 8 min · celda 9.1
Pregunta: *¿por qué una petición sin respuesta no dice si falló?* Respuesta: porque sin reloj común ni garantía de entrega, un timeout sólo dice que se dejó de esperar.
- **A. Relojes y causalidad.** Definiciones: componente, mensaje, reloj local, *precede* (A precede a B si es anterior en el mismo componente, si A envía y B recibe ese mensaje, o por transitividad: orden parcial). Figura `cmp-dist-relojes`: Gantt de dos componentes; reloj de B 40 ms atrás. Cuenta (parámetros del ejemplo): latencia 20 ms **supuesta**; envío marcado 100 en A, llegada marcada 80 en B; $80-100=-20=20-40$ ms: la diferencia de marcas no da la latencia sin conocer el desfase y su incertidumbre. Arquitectura: el orden de eventos entre máquinas se reconstruye con mensajes, no con relojes.
- **B. Resultado desconocido.** Definiciones: fallo parcial, resultado desconocido, plazo $t_{\max}$ (duración máxima que el cliente espera; no $d$, que es duración de una tarea). Figura `cmp-dist-tres-causas`: tres explicaciones posibles (se perdió la ida, se perdió la respuesta, el servidor tarda; también cabe que ejecutó y cayó antes de responder). Arquitectura: el plazo vencido no prueba fracaso ni cancela el trabajo; de ahí timeouts, reintentos e idempotencia (enlaza `arquitectura-y-estrategia`). Sin medición.

### Página 10 · `capas-de-ejecucion` · 12 min · celda 10.1 · **página modelo (se escribe primero)**
Pregunta: *cuando algo corre, ¿quién lo ejecuta y quién decide su turno?* Respuesta: lo ejecutan hilos, los asigna el SO a CPU lógicas y el runtime reparte tareas entre hilos; lo que cabe a la vez lo fija esa cadena, no el tamaño del pool.
- **A. Quién ejecuta y quién planifica.** Prerrequisitos: proceso, hilo, tarea (`[[secuencial-concurrente-paralelo]]`). Nuevos: runtime, planificador, CPU lógica, exclusión global. Figura `cmp-capas`: pertenencia (máquina→proceso→hilo→tarea) separada de ejecución (el SO planifica hilos en CPU; el runtime reparte tareas entre hilos, que pueden migrar). Figura `cmp-gantt-tres-planificaciones`: mismo trabajo, **4 tareas independientes de 100 ms, disponibles en $t=0$, sin costos extra (tiempos ideales)**: (a) tareas cooperativas en un hilo; (b) 4 hilos con exclusión global; (c) 4 hilos en 4 CPU. Cuenta: $T_{\text{ideal}}=\lceil n/p_{\text{ef}}\rceil\,e$ con $p_{\text{ef}}=1,\ 1,\ 4$ → 400, 400, 100 ms; $p_{\text{ef}}$ depende de trabajo disponible, hardware, runtime, exclusiones y tamaño del pool; no es ley general. Arquitectura: el tamaño del pool puede limitar el paralelismo; por sí solo no lo determina.
- **B. Leer una configuración.** Nuevos: paralelismo posible, tope admitido, ocupación (de un recurso en un momento), rendimiento (trabajos por unidad y ventana de tiempo). Tabla de las cuatro con el ejemplo `uvicorn app:app --workers 2` en CPython con GIL, 8 CPU: a lo sumo **dos hilos ejecutan bytecode** Python a la vez (un intérprete por worker, GIL habilitado; no limita la CPU total: las extensiones nativas pueden usar más; sin GIL no aplica); el comando no fija un tope de admisión (se muestra). Una línea: `--cpus` limita presupuesto de CPU y `--cpuset-cpus` cuáles. Tabla de runtimes → «Si hay tiempo». Notebook 10.1: PID e hilos de 4 hilos y de 2 procesos.

### Página 11 · `componer-un-servidor` · 25 min (incluye D1, 8 min) · celdas 11.1–11.2
Pregunta: *de una configuración, ¿cuántos procesos, hilos y conexiones resultan?* Respuesta: cada worker crea su pool local, `def` y `async def` se ejecutan en sitios distintos, y los topes locales se multiplican.
- **A. Pool local por worker.** Definiciones: worker, réplica, pool local. Figura `cmp-ancla-servidor` (familia «ruta de una petición»): $N$ workers con loop y pool propios; un backend de Postgres por conexión directa; con PgBouncer, dos poblaciones (cliente→pooler y pooler→Postgres). Cuenta: conexiones, consultas activas y CPU usadas son tres cantidades. Cada worker crea su pool local; compartirlo entre hilos depende de la biblioteca y entre procesos no debe suponerse. Arquitectura: no se supone que un pool se comparta entre procesos (enlaza `pools-y-recursos`).
- **B. `async def` y `def` (D1).** Definiciones: loop, limitador de hilos (AnyIO: 40 tokens por loop, configurable, compartidos), desplazar. Figura `cmp-async-vs-def`. Parámetros de D1 (**declarados**): **un worker**, 12 solicitudes simultáneas de espera $w$ con `time.sleep`, ≥ 12 tokens, cliente capaz de 12 conexiones, $w=0{,}5$ s, **13.ª conexión independiente** para la sonda, $t=0$ = momento en que se lanzan las 12 (se registra el lanzamiento real de la sonda, nominal $0{,}25\,w$), lectura ≥ $2\cdot12w$. Cuenta: $T_{\text{async}}\approx12w$, $T_{\text{def}}\approx\lceil12/40\rceil w=w$ (aproximaciones; el loop queda **bloqueado**, no la CPU). Medidos: total y latencia de la sonda. Arquitectura: un `def` llamado desde un `async def` no se desplaza.
- **C. Presupuesto de conexiones.** Tabla (no figura) $R,N,k$ → máximo configurado. Cuenta: $R\times N\times k=3\times4\times10=120$ **si 10 es el máximo total por pool**, todas contra el mismo servidor. Es capacidad potencial: Postgres suele estar en `max_connections=100`; con 3 plazas de superusuario y `reserved_connections=0` quedan 97 para el resto, y otros consumidores las reducen (se comprueba con `SHOW`). Arquitectura: escalar réplicas multiplica la presión sobre la BD (enlaza `arquitectura-y-estrategia`). Notebook 11.1 (D1), 11.2 (la cuenta).

### Página 12 · `como-llegan-los-resultados` · 20 min (incluye D2, 6 min) · celda 12.1
Pregunta: *si la respuesta no está lista cuando preguntas, ¿cómo te enteras?* Respuesta: preguntando (polling, long polling) o recibiendo un aviso (SSE, WebSocket, webhook); cambia cuántas peticiones haces, cuánto tardas en enterarte y qué recurso retiene el servidor.
- **A. Preguntar.** Definiciones: petición, conexión, polling, long polling. Figura `cmp-gantt-resultados`: evento en $T=10$ s; polling con $\Delta=3$ s (relojes monotónicos, sin deriva), long polling, SSE. Cuenta **sin consulta inicial**, consultas en 3, 6, 9, 12: sin novedades $\lceil T/\Delta\rceil-1=3$, totales 4, demora $\Delta\lceil T/\Delta\rceil-T=2$ s (en este ejemplo determinista; $\Delta/2$ sólo vale con fase uniforme). 20 clientes: 60 sin novedades y 80 totales. Medidos (D2): peticiones pendientes y sockets abiertos **por separado** (polling con keep-alive también conserva conexiones).
- **B. Que te avisen.** Definiciones: flujo (stream), SSE (respuesta HTTP continua servidor→cliente), WebSocket (canal bidireccional que el cliente establece), webhook (el emisor llama al receptor). Figura `cmp-push-webhook` y tabla: quién inicia · qué queda abierto · recurso retenido · unidad que ejecuta · falla típica. Cuenta (Little): sesiones abiertas (promedio) $=$ tasa de aperturas × duración media, misma población y frontera; no es máximo instantáneo; vale en régimen estable con promedios bien definidos, o con la contabilidad completa de una ventana finita (una corrida aislada no demuestra estabilidad). Arquitectura: el mecanismo no decide si se retiene un hilo o una tarea. gRPC, GraphQL, SOAP → «Si hay tiempo».

Cierre: ejercicio de elección (15 min) sobre una configuración; margen 10.

## D. Mediciones (8 CPU; **un solo worker en D1 y D2**; ≤ 146 llamadas por corrida, ≤ 3 corridas)
`m_pid_hilos` · `m_d1_async`, `m_d1_def` (total y sonda) · `m_d2_polling`, `_long`, `_sse` (pendientes, sockets, demora). Timeouts de HTTPX configurados (lectura ≥ 12 s) y plazo global finito por demo. Se guardan en `_reviewed/` con fecha, máquina y versión.

## E. Infraestructura
- `codigo/11_computo/app_arq.py` (FastAPI): `/def-bloqueante`, `/async-bloqueante`, `/quien`, `/inicia`, `/listo`, `/espera`, `/eventos` (SSE, `text/event-stream`, cierre al desconectar). **Contrato HTTP** en la Fase 0: parámetros, respuestas, errores, estado en memoria (por eso un worker), reinicio, inicio del reloj.
- Lanzamiento desde el notebook: `sys.executable -m uvicorn app_arq:app`, sin `--reload`, puerto configurable, espera con plazo, detección de salida temprana y de puerto ocupado, cierre en `finally` (`terminate`, `wait`, escalamiento acotado). **Pruebas explícitas:** interrupción del kernel a mitad de demo, desconexión de un cliente SSE y segunda ejecución del notebook (puerto libre y sin procesos huérfanos).
- Dependencias: `fastapi` y `uvicorn` en el `pyproject`; **`uv lock` y prueba de `uv sync --locked --offline` en la Ola 0** (el aula no tiene internet); alternativa con salida capturada.
- Notebook `arquitectura.ipynb` generado por `tools/gen_notebook_arquitectura.py` desde `tools/notebook_arquitectura/*.py`, sin salidas.
- Figuras: **8** (`cmp-dist-relojes`, `cmp-dist-tres-causas`, `cmp-capas`, `cmp-gantt-tres-planificaciones`, `cmp-ancla-servidor`, `cmp-async-vs-def`, `cmp-gantt-resultados`, `cmp-push-webhook`) en `tools/gen_computo_c.py` (p9–10) y `tools/gen_computo_d.py` (p11–12), registradas en el catálogo principal (`DIAGRAMAS.update`) y con sus tests. Reglas de los Gantt de la 11.1 (CPU/hilo y razón de espera rotulados, sin dígitos sueltos, nada fuera del `viewBox`).
- Integración: calendario, `course/0_index.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`, índice de la unidad, `A_notacion.md` (símbolos $R,N,k,p_{\text{ef}},t_{\max},T,\Delta$ revisados contra los existentes; «asíncrono» en tres planos).
- Guardas: `test_computo_curriculum.py` generalizado (glob `[1-8]` y `nombre[0]`), separando las reglas del notebook antiguo («Haz» y código en páginas) de las páginas nuevas sin código; `test_computo_forma.py` nuevo; catálogo de figuras en `test_gen_computo.py`.
- **Regla para cambiar el contrato:** sólo yo lo edito, versionado en el propio archivo; los agentes reportan discrepancias en el buzón y no las resuelven por su cuenta.
- **Criterios de aceptación por entrega:** `raya validate` verde · tests de la ola verdes · enlaces/figuras/alt/créditos resueltos · CI verde · el sitio publicado responde 200 **y contiene la frase marcador** de la versión (no sólo 200).

## F. Enjambre en olas (cada ola termina en algo publicable; el profesor revisa mientras la siguiente corre)
**Reglas.** Archivos disjuntos por carril. Ningún agente corre `pytest tools/` completo ni más de un servidor a la vez; el `pytest` completo es mío, al cierre; el CI lo repite como compuerta. `CREDITOS.md`, notación, `uv.lock` e índice: un solo dueño (yo). Commits con rutas explícitas (nunca `estudiantes/uumami/`). Buzón de comentarios del profesor: `docs/superpowers/plans/2026-10-29-buzon-revision.md`. Contenido **congelado a las 17:45**.

**Tubería por página:** redacta (Opus) → **Codex sol, solo lectura (`-o`), propone una reescritura de forma con rúbrica** (frases más cortas, respuesta primero, términos nuevos ≤ 4; sin tocar parámetros, supuestos, fórmulas ni definiciones) → yo reviso el diff completo y corro las guardas sobre el resultado → revisión (alumno y técnico, **dos revisores reutilizables** por todas las páginas) → arreglos. Codex es una propuesta editorial, no una garantía de conservación. Una **revisión final de integración** al cierre, no una por página.

**Carriles:** K1 calendario/docs/índice · K2 guardas · K3 `app_arq.py`, `pyproject`, `uv lock` · F1 figuras p9–10 · F2 figuras p11–12 · W9 W10 W11 W12 redactores · M mediciones · N notebook y su ensayo (interrupción, segunda ejecución) · **P publicación** (agente dedicado: prepara commits con rutas explícitas, corre las comprobaciones de cada entrega y verifica el sitio publicado) · yo: contrato, integración y decisiones.

| Ola | Ventana | En paralelo | Publicación |
|---|---|---|---|
| **0** | 15:55–16:30 | contrato mínimo y propietarios (yo, 10 min) → K1, K2, K3, F1, F2 y **W10 (página modelo) empieza a las 16:05** con el contrato y los patrones, W9, W11 y W12 empiezan al mismo tiempo siguiendo los patrones | **D0 ≈ 16:30:** calendario, índice (sin enlaces a páginas inexistentes), guardas, notación |
| **1** | 16:30–17:00 | pase Codex y revisión de p10 · revisión de p9 · M mediciones D1/D2 · N notebook · p11 y p12 avanzan con el contrato técnico; si el modelo pide ajustes de forma, se aplican a las demás | **D1 ≈ 17:00:** páginas 9 y 10 con figuras |
| **2** | 17:00–17:45 | cierre de p11 y p12 con cifras sustituidas · pases Codex · revisiones · notebook ensayado · **congelación de contenido a las 17:45** | **D2 ≈ 17:50:** páginas 11 y 12, `app_arq.py`, notebook, dependencias |
| **3** | 17:50–18:30 | Astra (técnica, 9–12) · revisión final de integración · correcciones únicamente necesarias · `pytest tools/` completo (una vez), `raya validate` y `build`, vistas móvil/escritorio | **D3 ≈ 18:40:** final |
| **4** | 18:40–19:00 | verificación del sitio publicado, respaldo capturado de D1 y D2, `uv sync --offline` en entorno limpio | margen |

**La aprobación del modelo no es una barrera:** p10 se publica en D1 aunque la revisión sea posterior; tus comentarios entran por el buzón y los aplica la ola siguiente. Si el modelo muestra un defecto de forma, se corrige en las páginas aún no congeladas.

**Paralelismo.** Ola 0: 6 redactores y generadores trabajando a la vez. Lo estrictamente secuencial: contrato → redactores; K3 → M y N; M → cifras; congelación → suite completa → D3.

## G. Escalera de recortes
1. Sin pase de Codex en la página 9.
2. D2 pasa a salida capturada.
3. El notebook sólo trae D1; D2 y 10.1 quedan como capturas.
4. La página 12 sale con el bloque A y el B sólo como tabla.
5. Mínimo publicable: calendario, índice, páginas 10 y 11 y D1.

## H. Qué NO se hace hoy
Páginas 13–15, D3 y D4, tarea FastAPI, alt texts de la 11.1.
