---
name: crear_tarea
description: Crea una tarea nueva de fdd_o26 que se entrega por pull request, completa y consistente — ficha TOML, objeto oficial YAML, plantilla en codigo/, entrada en TAREAS del workflow, fila en el tablero de la unidad, y patrones propios con sus tests — llenando la ficha con el profesor (lo que no se sabe se pregunta), verificando que las seis piezas digan lo mismo y sometiéndola a revisión adversarial con agentes. Úsala cuando el profesor pida crear, diseñar, publicar o agregar una tarea, entrega o assignment nuevo.
---

# Crear una tarea

Una tarea son **seis piezas que dicen lo mismo**. Cada error real que hemos
tenido con alumnos vino de dos piezas que decían cosas distintas, o de una
que decía algo que no existía. Esta skill existe para que eso no pase.

**Regla cero: lo que no se sabe se pregunta, no se inventa.** Una fecha, un
nombre de archivo, una política de IA inventados llegan a treinta alumnos.

## 1 · Las seis piezas

| # | Pieza | Ruta | La lee |
|---|---|---|---|
| 1 | **Ficha** | `.github/tareas/<branch>.toml` | CI (`revisa_ficha.py`) y quien revisa |
| 2 | **Objeto oficial** | `course/<unidad>/_official/assignments/N_<nombre>.yaml` | El sitio y el calendario |
| 3 | **Plantilla** | `codigo/<carpeta>/` | El alumno, que la copia |
| 4 | **Workflow** | `TAREAS` en `.github/workflows/entregas.yml` | CI (`revisa_entrega.py`) |
| 5 | **Tablero** | la página de entregas de la unidad (modelo: `course/8_contenedores/7_D_entregas.md`) | El alumno, en forma de tabla |
| 6 | **Tests** | `tools/test_revisa_ficha.py` | CI (`pytest tools/`) |

## 2 · Lee el modelo antes de escribir

La unidad 8 es la referencia. Lee **enteros**:

- `course/8_contenedores/_official/assignments/*.yaml`
- `course/8_contenedores/7_D_entregas.md`
- `codigo/docker/` y `codigo/08_contenedores/`
- `.github/tareas/README.md` (el esquema de la ficha) y una ficha real
- `.github/workflows/entregas.yml` y `CLAUDE.md` (sección CI)

## 3 · Llena la ficha con el profesor

Pregunta **todo** lo que no esté escrito. Sin respuesta no hay pieza.

| Pregunta | Ejemplo | Termina en |
|---|---|---|
| ¿Qué se entrega, archivo por archivo, con nombre exacto? | `certificaciones.md`, `intermedio-1-2.png` | ficha `requeridos`/`capturas`, YAML, plantilla, tablero |
| ¿En qué carpeta? ¿Nueva o compartida con otra tarea? | `docker/` (compartida por tres) | ficha `carpeta`, `TAREAS`, `codigo/` |
| ¿Cómo se llama la branch? | `tarea-09-consultas` | nombre de la ficha, `TAREAS`, YAML, tablero |
| ¿Cuándo abre y cuándo vence? | `2026-10-01` / `2026-10-06` | ficha, YAML (deben coincidir; hay test) |
| ¿Cuántos puntos? ¿Cómo se penaliza tarde? | `10`; `"1/dia"` | YAML `points`; ficha `penalizacion_tarde` |
| ¿Política de IA? | `permitida` · `permitida-revisada` · `prohibida` | ficha `ia`, YAML, tablero |
| ¿Qué debe poder **explicar** sin ayuda? | «qué hace `EXPOSE` y qué no» | ficha `debe_explicar`, YAML |
| ¿Qué evidencia vale y cuál no? | captura con nombre y 100 %; no un ejercicio suelto | YAML, ficha `[revision]` |
| ¿Qué **no** se entrega? | `predicciones.md`, `output.txt` | ficha `prohibidos`, YAML, tablero, **y la plantilla** (§ 5) |
| ¿Qué artefacto exacto se publica? | «la imagen construida desde `roto/`» | YAML, tablero |
| ¿Hay algo que dependa del tiempo o de su máquina? | «la fecha de construcción» | § 6 |
| ¿Qué página enseña cada cosa? | `arreglar-un-dockerfile` | ficha `donde_investigar`, patrones `investiga` |
| ¿Cuál es **la** página de la tarea, para los mensajes genéricos? | «Página «Las cinco entregas» (URL)» | ficha `pagina` |

Toda fecha: **`AAAA-MM-DD`**, en la ficha, en el YAML y en lo que se le pide
escribir al alumno. En una tarea nueva, toda sección con fecha lleva
`pide = ["fecha-iso"]`. `pide = ["fecha"]` (cualquier formato legible) es
**heredado**: sólo lo usan las fichas migradas del catálogo viejo
(`tarea-08-datacamp-inter-1`, `-inter-2`), para no endurecerles las reglas a
media entrega. No lo copies de ahí.

## 4 · Genera las piezas, en este orden

### 4.1 · La plantilla `codigo/<carpeta>/`

- **Regla del curso: todo se trabaja en `estudiantes/<login>/`.** Labs, ejercicios y entregas viven en la carpeta del alumno, copiados de `codigo/` con el mirror; nunca en una carpeta fuera del repo (`~/lab-…`). Los labs viajan en el pull request de la tarea que comparte su subcarpeta. Lo generado (`.venv/`, `__pycache__/`) queda fuera por `.gitignore` y por la lista de basura.
- **Marcadores detectables**: rótulos que terminan en `:` y quedan vacíos,
  títulos `##` con una aguja única por sección, bloques ` ```text ` vacíos,
  `<tu-usuario>` en lo que se reemplaza. `revisa_ficha.py` reconoce «sin
  llenar» por esos rótulos y por las líneas de la plantilla.
- **Todo lo que las instrucciones mandan tocar existe en la plantilla.** Si el
  YAML dice «borra el `echo` de depuración», ese `echo` está en el archivo.
  Compruébalo con `grep` antes de publicar.
- **Lo que no se entrega no vive en la carpeta que el ritual copia y sube.**
  Si el ritual es `cp -r codigo/X/. …` y `git add estudiantes/$GHUSER/X`, todo
  lo de `codigo/X/` viaja. Ponlo fuera, o dilo en la ficha como `prohibidos`
  y en el ritual.
- Las capturas ya enlazadas desde el `.md`, con el nombre exacto.
- Una fila en `codigo/README.md` si la carpeta es nueva.

### 4.2 · El objeto oficial (YAML)

`content.instructions` se escapa a **texto plano**: sin tablas ni listas. Por
eso existe el tablero. Aun así, legible, en este orden, un párrafo corto por
idea:

1. Qué hacer y para qué (una frase).
2. **Carpeta** y cómo se copia (espejo de `codigo/`).
3. **Qué entregar**, archivo por archivo, con nombre exacto.
4. **Qué no se entrega.**
5. **Branch exacta**, nacida de `main` actualizado; un PR, una carpeta.
6. **Fecha** en `AAAA-MM-DD` si el alumno escribe una.
7. **Política de IA** y **qué debe poder explicar**.
8. «Sabrás que terminaste cuando…» y qué significa (y qué no) el verde.

Además:

- `available` y `due` entre comillas, `AAAA-MM-DD`.
- En `resources`, la nota del tablero dice literal «branch tarea-NN-…» (con o
  sin comillas invertidas): `registro.py` encuentra el `due` de las tareas sin
  ficha por esa frase.
- **No escribas la fecha en el calendario**: el objeto con `due` genera su
  ocurrencia solo (ver `CLAUDE.md`, «The calendar»).
- Recuerda `CLAUDE.md`: comillas en valores con `:`, nada de HTML crudo, `@`
  literal dentro de código.

### 4.3 · La ficha `.github/tareas/<branch>.toml`

Sigue `.github/tareas/README.md` al pie de la letra. Lo que más cuesta:

- `pagina`: la página de la tarea (tablero o anexo), con su URL.
- `[[secciones]]` con fecha: `pide = ["fecha-iso"]` (§ 3).
- `debe_explicar`: preguntas que el alumno contesta **sin ayuda**. Es el
  centro de la política de IA.
- `[revision]`: `foco`, `igual_es_normal`, `debe_ser_propio`, `senales`,
  `donde_investigar`, **las cinco siempre**. En `igual_es_normal`, sólo una
  entrada que es **entera** una ruta o un glob (`"info/*.sh"`) se excluye al
  comparar con `compara.py`; una en prosa sólo se le muestra a quien revisa.
- `senales`: hechos verificables, nunca sospechas.

### 4.4 · El workflow

Agrega `<branch>=<carpeta>` a `TAREAS` en `.github/workflows/entregas.yml`.
La misma carpeta que la ficha (hay test).

### 4.5 · El tablero de la unidad

- Una fila en la tabla resumen: #, entrega, vence, vale, **branch**, carpeta.
- Una sección con la tabla **Vence / Vale / Branch / Carpeta**, «Entregas N
  archivos» en lista, **el ritual** en un bloque, lo que **no** se entrega y
  «Acabaste cuando…».
- El ritual se prueba mentalmente línea por línea: ¿qué sube el `git add`?

### 4.6 · Los patrones propios y sus tests

Cada `[[patrones]]` de la ficha:

- `que` / `porque` / `investiga`: **QUÉ** está mal, **POR QUÉ** es un error (la
  consecuencia), **DÓNDE INVESTIGAR** (página + una pregunta). **Nunca el
  cómo**: el test `test_los_mensajes_de_la_ficha_no_dan_el_como` rechaza
  comandos, backticks y recetas.
- `nivel = "aviso"` si no estás seguro de que no dé falsos positivos.

Y en `tools/test_revisa_ficha.py`, con la ficha **real** cargada:

- el patrón en **las dos direcciones**: un texto realista que debe fallar y
  uno que debe pasar, tomados de la plantilla llena como la llenaría un alumno;
- **ninguna prueba depende de la fecha de hoy**: pasa `hoy=` fijo al revisor.

## 5 · Checklist de consistencia

Cada dato, en cada pieza donde aparece. Una celda que no coincide es un bug.

| Dato | Ficha | YAML | Plantilla | Tablero | Workflow | Página que lo enseña |
|---|---|---|---|---|---|---|
| Branch | nombre del archivo y `branch` | instrucciones y nota | — | tabla y ritual | `TAREAS` | — |
| Carpeta | `carpeta` | instrucciones | existe `codigo/<carpeta>/` | tabla y ritual | `TAREAS` | — |
| Archivos requeridos | `requeridos` | instrucciones | existen | lista | — | — |
| Captura | `[[capturas]].nombre` | instrucciones | enlazada con ese nombre | lista | — | — |
| No se entrega | `prohibidos` | instrucciones | fuera de lo que sube el ritual | lista | — | — |
| `available` / `due` | `[tarea]` | `content` | — | «Vence» | — | — |
| Secciones que se llenan | `[[secciones]].aguja`, `pide` | instrucciones | `##` con esa aguja | lista | — | — |
| Algo a borrar o arreglar | patrón | instrucciones | **está en el archivo** | lista | — | explicado |
| IA y qué explicar | `ia`, `debe_explicar` | instrucciones | — | sección | — | enseñado |

Comprobaciones mecánicas:

```bash
b=tarea-NN-nombre; c=<carpeta>
grep -rn "$b" .github/ course/ | sort          # aparece en ficha, workflow, YAML, tablero
ls codigo/$c/                                   # lo que el ritual sube
grep -rn '<frase que el YAML manda borrar>' codigo/$c/   # debe existir
python3 -m pytest tools/test_revisa_ficha.py -q
python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

## 6 · Lo que depende del tiempo o de su máquina

Una fecha que produce su computadora **no es evidencia**: depende de su reloj.
Si la tarea pide algo así («imprime la fecha de construcción»):

- Di **cómo** debe quedar registrado (en la construcción, no al correr), pero
  **no lo uses como evidencia de tiempo**: cualquier fecha que salga de su
  máquina —lo que imprime el programa, `CREATED` de `docker images`, las
  fechas de `docker history`, la fecha del commit— depende de su reloj.
- Lo que sí es del servidor: `created_at` del PR, `last_updated` de Docker
  Hub, el orden de los pushes.

## 7 · Revisión adversarial con agentes

Antes de publicar, lanza **tres agentes en paralelo**, sólo lectura, cada uno
con las seis piezas y un papel:

| Agente | Papel | Pregunta que contesta |
|---|---|---|
| **Alumno literal** | Hace exactamente lo que dice cada palabra, en el orden escrito | ¿Dónde lo que dice una pieza choca con otra? ¿Qué sube el ritual que no debía? ¿Qué pide borrar que no existe? |
| **Alumno flojo** | Busca el mínimo que sale en verde | ¿Qué entrega vacía, a medias o inventada pasa el CI? ¿La ficha y `[revision]` la atrapan? |
| **Alumno con IA sin leer** | Pega la tarea en un modelo y entrega lo que salga, sin correr nada | ¿Qué incoherencias dejaría (salidas de otra versión, archivos que no existen)? ¿Están en `senales`? ¿`debe_explicar` lo separa de quien sí entendió? |

Pídeles hallazgos con **pieza, línea y consecuencia**. Consolida en **un
parche**, no los vuelques en crudo. Repite si el parche cambió algo grande.

## 8 · Legibilidad (lectores con ADHD)

- **La branch visible** en toda pieza que la mencione.
- Tabla antes que prosa; una idea por párrafo; párrafos de 3 líneas o menos
  en el tablero.
- **Negritas** sólo en lo que se rompe si no se lee.
- Siempre: qué se entrega, qué **no**, y «Acabaste cuando…».
- Un error frecuente se nombra **antes** de que ocurra («es `docker`, no
  `github`»).

## 9 · Errores reales que esto previene

| Error | Qué pasó | Lo previene |
|---|---|---|
| El «`echo` de depuración» que no existía | El YAML y el tablero mandaban borrarlo de `info.sh`, el script lo buscaba («las muchas oes»), y la plantilla nunca lo tuvo | § 4.1: todo lo que se manda tocar existe; § 5 `grep` |
| No decir qué imagen publicar | «Construye una imagen propia» con `info/` y `roto/` en la carpeta: se publicaron imágenes que no contenían el trabajo entregado | § 3 «¿qué artefacto exacto?» |
| Cómo grabar la fecha de construcción | Se pidió imprimir la fecha de construcción sin decir que debía fijarse al construir; `$(date)` imprime la de ejecución, y depende de su reloj | § 6 |
| `predicciones.md` que el ritual sube | «No se entrega», pero el `cp -r` y el `git add` de la carpeta lo suben siempre | § 4.1 y fila «No se entrega» de § 5 |
| Fechas sin formato fijo | «Cualquier formato legible» trajo «22 de septiembre», `22/09` y «hoy»: nada comparable contra la apertura del PR | § 3: `AAAA-MM-DD` y `pide = ["fecha-iso"]` |
| El test que dependía de la fecha de hoy | `test_hoy_una_branch_inventada_solo_avisa` usaba el reloj real y se puso rojo el 2026-09-22, el día que vencía la gracia (commit `5e5cb67`) | § 4.6: `hoy=` fijo |

## 10 · Lo que esta skill no hace

- **No hace commit** sin que el profesor lo pida; una tarea es un commit
  propio, sin mezclar con otra cosa.
- No decide puntos, fechas, penalización ni política de IA: los pregunta.
- No agrega la sesión al calendario: eso va con la unidad (ver `CLAUDE.md`).
