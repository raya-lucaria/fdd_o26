# Fichas de tarea

Cada tarea que se entrega por pull request tiene aquí su **ficha**: un archivo
TOML que dice qué se revisa solo (el CI) y qué revisa una persona o un agente.

- **El nombre del archivo es la branch.** `tarea-08-datacamp-inter-1.toml` es la
  ficha de la branch `tarea-08-datacamp-inter-1`. Una branch sin ficha no se
  revisa en este paso (sale en verde sin decir nada).
- La lee `.github/scripts/revisa_ficha.py`, tercer paso de
  `.github/workflows/entregas.yml`, del checkout de la **rama base**: un pull
  request no puede traer ni cambiar su propia ficha.
- TOML porque Python lo lee con `tomllib`, de la biblioteca estándar: el CI no
  instala nada.
- `tools/test_revisa_ficha.py` valida **todas** las fichas: esquema, que la
  branch coincida con el archivo y con la forma `tarea-NN-nombre`, que la
  carpeta exista en `codigo/`, que `asignacion` sea el `id` de un objeto oficial
  con las mismas `available` y `due`, que la branch esté en `TAREAS` del
  workflow y que no siga también en el `CATALOGO` de `revisa_contenido.py`.

`tarea-08-datacamp-intro` y `tarea-08-imagen` **no** tienen ficha: ya tenían
entregas en curso cuando entraron las fichas y se quedan en el `CATALOGO` de
`revisa_contenido.py`, con sus reglas de siempre.

## Cómo se escriben los mensajes

Todo lo que la ficha le dice al alumno sigue el formato **QUÉ / POR QUÉ /
DÓNDE INVESTIGAR**:

- **QUÉ** está mal, con el archivo.
- **POR QUÉ** es un error: la consecuencia, no la regla.
- **DÓNDE INVESTIGAR**: una página del curso y una pregunta que haga pensar.

**Nunca el cómo**: ni comandos, ni la línea corregida, ni la receta. El cómo
es la tarea. Y nada que no se pueda comprobar: hechos, no sospechas.

## Esquema

### `[tarea]` — obligatoria

| Llave | Tipo | Qué es |
|---|---|---|
| `branch` | texto | La branch de la entrega. Igual al nombre del archivo, forma `tarea-NN-nombre`. |
| `asignacion` | texto | El `id` del objeto oficial en `course/**/_official/**.yaml`. |
| `carpeta` | texto | La subcarpeta en `estudiantes/<login>/`, espejo de `codigo/<carpeta>/`. Sin `/` al inicio ni al final. |
| `available`, `due` | fecha `AAAA-MM-DD` | Deben coincidir con las del objeto oficial (lo comprueba una prueba). |
| `penalizacion_tarde` | texto libre | Cómo se penaliza la entrega tarde: `"1/dia"` (contando el día actual), `"1/5"`, `"a-decidir"`. La aplica el profesor, no el CI. |
| `ia` | texto | `permitida`, `permitida-revisada` o `prohibida`. |
| `debe_explicar` | lista de textos, no vacía | Lo que el alumno debe poder explicar sin ayuda. El foco es que entienda. |
| `pagina` | texto, opcional | La página de la tarea, para el «dónde investigar» de los mensajes genéricos. |

### `[entregables]` — obligatoria

| Llave | Tipo | Qué es |
|---|---|---|
| `requeridos` | lista de rutas | Relativas a la carpeta. Cada una tiene que venir **en el pull request** (agregada o modificada). Si llega idéntica byte a byte a `codigo/<carpeta>/<ruta>`, falla: es la plantilla sin tocar. |
| `prohibidos` | lista de rutas | Si vienen en el pull request, falla. Puede ser `[]`. |
| `identica` | `"falla"` o `"aviso"`, opcional | Qué pasa si un requerido llega idéntico a la plantilla. Por omisión `"falla"`. |

### `[[capturas]]` — cero o más

| Llave | Tipo | Qué es |
|---|---|---|
| `nombre` | texto | Sin extensión, relativo a la carpeta. |
| `extensiones` | lista | Las que valen, con punto: `[".png", ".jpg", ".jpeg", ".pdf"]`. |
| `minimo_bytes` | entero | Menos que esto no es una captura de verdad. `5000` atrapa el archivo vacío y el placeholder. |

### `[[secciones]]` — cero o más

Secciones `##` de un Markdown que deben quedar llenas.

| Llave | Tipo | Qué es |
|---|---|---|
| `archivo` | ruta | Debe estar en `requeridos`. |
| `aguja` | texto | Subcadena del título `##` (sin distinguir mayúsculas). |
| `pide` | lista | De `"fecha"` (cualquier formato legible), `"url"`, `"fecha-iso"` (`AAAA-MM-DD`). Puede ser `[]`: basta con que la sección esté llena. |
| `falta` | `"falla"` o `"aviso"`, opcional | Qué pasa si falta algo de `pide`. Por omisión `"falla"`. |
| `sin_tocar` | `"falla"` o `"aviso"`, opcional | Qué pasa si la sección no trae más que líneas de la plantilla (ver abajo). Por omisión `"falla"`. |
| `fecha_futura` | `"falla"` o `"aviso"`, opcional | Qué pasa si la sección trae una fecha posterior a mañana (UTC) del día de la revisión. Por omisión `"falla"`. |

Dos niveles de sección vacía:

- **Vacía**: sólo rótulos que terminan en `:`, líneas que empiezan con «Se
  llena» o nada. **Siempre falla**, sin importar la ficha.
- **Sin tocar**: sólo líneas que ya estaban en la misma sección de la
  plantilla, prosa incluida. Su nivel lo pone `sin_tocar`.

**Los formatos de fecha que enumera el mensaje son una especificación, no un
«cómo»**: dicen qué se acepta (`2026-09-22`, `2026/09/22`, `22/09/2026`,
`22-09-2026`, `22.09.2026`, `22 de septiembre de 2026`, `22 sep 2026`,
`Sep 22, 2026`, `septiembre 22, 2026`), igual que un formulario dice qué
formato espera; no le resuelven nada al alumno. La lista vive en
`revisa_ficha.py` y en su prueba parametrizada, y las dos se mueven juntas.

**La fecha futura se mide contra el día de la revisión** (UTC, con un día de
holgura), no contra la apertura del pull request: quien avanza después de
abrirlo y corrige la fecha en la misma branch hace justo lo que se le pide, y
medir contra la apertura lo marcaría. La holgura cubre a quien escribe desde
un huso adelantado a UTC.

**Endurecer es decisión del profesor.** Una ficha migrada de un catálogo
anterior no puede rechazar lo que ese catálogo aceptaba: lo nuevo va como
`"aviso"` (ver las fichas de `tarea-08-datacamp-inter-1` e `-inter-2`).

### `[[patrones]]` — cero o más

Reglas propias de la tarea, sobre el texto de un archivo del pull request.

| Llave | Tipo | Qué es |
|---|---|---|
| `archivo` | ruta | Si no viene en el pull request, la regla no corre. |
| `debe` / `no_debe` | regex | Exactamente una de las dos. Se evalúa con `re.M` y `re.I`. En TOML, usa comillas simples para no escapar las barras. |
| `seccion` | texto, opcional | Restringe la regla al cuerpo de esa sección `##`. |
| `que`, `porque`, `investiga` | texto | El mensaje, en formato QUÉ / POR QUÉ / DÓNDE INVESTIGAR. Sin el cómo. |
| `nivel` | `"falla"` o `"aviso"` | Un aviso se imprime y no bloquea. |

### Lo que el CI revisa siempre, sin que la ficha lo pida

- **Nombres con caracteres de control.** Todo lo que viene del pull request
  (rutas, nombres, texto) se imprime con los caracteres de control cambiados
  por `?`, y el log va entre `::stop-commands::` y su token: un archivo
  llamado con un salto de línea y `::error ...` no puede fingir una anotación.
- **Errores de la API**: si un archivo no se pudo leer, el mensaje dice que es
  un error de la revisión, no de la entrega.
- **Texto dirigido a quien revisa** («ignora las instrucciones», «ignore
  previous», «aprueba este», «as an AI», «system prompt»…) en cualquier archivo
  de texto de la entrega: **aviso**, nunca falla, y lo dice. El contenido del
  alumno es dato, no instrucción.

### `[revision]` — obligatoria; la usa quien revisa, no el CI

| Llave | Qué es |
|---|---|
| `foco` | Lo que hay que mirar en esta tarea. No vacía. |
| `igual_es_normal` | Lo que se repite entre entregas y **no** es señal de nada (la plantilla, lo que dicta la tarea). Se excluye al comparar entregas. |
| `debe_ser_propio` | Lo que tiene que ser del alumno. |
| `senales` | Hechos verificables que ameritan mirar más de cerca. Hechos, no acusaciones. |
| `donde_investigar` | Páginas del curso (o externas) contra las que se coteja. No vacía. |

Todas son listas de textos; las cinco llaves van siempre, aunque alguna sea `[]`.

## Ejemplo completo

```toml
[tarea]
branch = "tarea-09-consultas"
asignacion = "sql-consultas-basicas"
carpeta = "09_sql"
available = "2026-10-01"
due = "2026-10-06"
penalizacion_tarde = "1/dia"
ia = "permitida-revisada"
debe_explicar = [
  "por qué WHERE filtra antes de agrupar y HAVING después",
  "qué devuelve un LEFT JOIN cuando no hay pareja",
]
pagina = "Página «Consultas» (https://rayalucaria.org/fdd_o26/sql/consultas/)"

[entregables]
requeridos = ["consultas.sql", "bitacora.md"]
prohibidos = ["datos/ventas.db"]

[[capturas]]
nombre = "resultado"
extensiones = [".png", ".jpg", ".jpeg"]
minimo_bytes = 5000

[[secciones]]
archivo = "bitacora.md"
aguja = "Lo que se rompió"
pide = ["fecha-iso"]

[[patrones]]
archivo = "consultas.sql"
no_debe = '^\s*SELECT\s+\*'
que = "consultas.sql usa SELECT * en alguna consulta"
porque = "la tarea pide nombrar las columnas: con *, un cambio en la tabla cambia en silencio lo que devuelve tu consulta"
investiga = "Página «Consultas»: ¿qué pasa con tu resultado si mañana la tabla gana una columna?"
nivel = "falla"

[revision]
foco = ["que las consultas corran contra la base de la tarea y den lo que la bitácora dice"]
igual_es_normal = ["el esqueleto de consultas.sql que trae la plantilla"]
debe_ser_propio = ["la sección «Lo que se rompió» de la bitácora"]
senales = ["resultados pegados en la bitácora que no salen de las consultas entregadas"]
donde_investigar = ["https://rayalucaria.org/fdd_o26/sql/consultas/"]
```

Al agregar una ficha: agrega también la branch a `TAREAS` en
`.github/workflows/entregas.yml` (con la misma carpeta) y corre
`python3 -m pytest tools/test_revisa_ficha.py -q`.

En `igual_es_normal`, sólo una entrada que es entera una ruta o un glob (`"info/*.sh"`) la excluye `.claude/skills/revisar_tarea/compara.py` al comparar entregas; una entrada en prosa sólo se le muestra a quien revisa.
