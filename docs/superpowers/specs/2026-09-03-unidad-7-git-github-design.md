# Unidad 7 — Git y GitHub

Diseño de la unidad. Dos sesiones de clase, una sola unidad publicada.

Versión 2. La versión 1 pasó por cuatro revisiones adversariales (pedagogía,
exactitud técnica de Git, un estudiante torpe contra el flujo, y el contrato
técnico del repo). Los hallazgos están incorporados; la sección final lista
lo que quedó abierto.

## Qué es

Una unidad de dos clases que lleva a alguien que nunca ha usado Git desde la
historia del problema hasta abrir un pull request correcto contra el
repositorio del curso.

Sesiones: `session-08` jueves 2026-09-03 y `session-09` martes 2026-09-08.
La tarea se entrega en la clase inmediata siguiente, `session-10`, jueves
2026-09-10.

## Idea que sostiene toda la unidad

**Git es una herramienta que vive en tu máquina y no sabe qué es internet.
GitHub es una empresa que hospeda repositorios de Git y le agrega encima lo
que Git no tiene.**

Durante toda la clase 1 nadie se conecta a nada: se trabaja en un laboratorio
desechable con `git init`, y `commit` no sube nada. Cuando en la clase 2
aparece GitHub, la pregunta "¿ya se ve en la nube?" tiene respuesta obvia.

El alumno llega a esta unidad habiendo hecho ya cuenta de GitHub, `ssh-keygen`
y `git clone`, así que la frase suena falsa si no se maneja. La página 3 abre
nombrando la contradicción y convirtiéndola en gancho: ya clonaste de GitHub;
hoy vas a construir un repositorio que nunca verá internet, y el martes vas a
entender por qué eso fue posible.

Registro heredado de las unidades 5 y 6: el concepto llega **después** de la
falla concreta. Español para la prosa, inglés para los términos técnicos
(commit, push, pull, merge, branch, staging, fork, pull request, stash). Se
dice "mergear". Se dice "cheatsheet", no "chuleta".

## Qué corregimos del curso pasado

Del análisis de `fdd_p26/clase/06_git/`, de los decks del profesor y del
estado real de `fdd_p26/estudiantes/`:

1. **Se enseñaba una receta, no Git.** Staging, branches y conflictos vivían
   en un archivo opcional fuera del flujo.
2. **El conflicto se evitaba, no se resolvía.** Aquí se provoca a propósito.
3. **El mirror del código era ambiguo.** Ninguno de los 30 alumnos usó los
   nombres de `codigo/`. Un alumno inventó 16 carpetas. Aquí hay una regla y
   además se verifica mecánicamente.
4. **El GitHub Action era invisible.** Aquí se explica antes de reprobar.
5. **El cheatsheet contradecía el flujo.** Aquí sólo lista lo que se enseñó.
6. **Nadie sabía su login exacto de GitHub.** Existe
   `fdd_p26/estudiantes/regina_cortes/`, un nombre imposible porque GitHub no
   admite guion bajo en logins, y 18 logins abrieron PR sin tener carpeta.
   Aquí el login se obtiene con un comando y se guarda en una variable.

## Estructura

Layout plano, como la unidad 6. El orden cambió respecto a la versión 1 por
dos razones de dependencia: la página de commits ahora va **después** del
primer repositorio, para que el hash que se explica sea uno que el alumno ya
produjo; y la página de la carrera entre dos personas ahora va **después** de
la de GitHub, porque su vocabulario entero (remote, push rechazado) se define
ahí.

| Archivo | id | Página | Min |
|---|---|---|---:|
| `0_index.md` | `git-y-github` | Git y GitHub | — |
| `1_cuenta_y_llave.md` | `cuenta-y-llave` | Cuenta y llave (existe) | 25 |
| `2_clonar_y_actualizar.md` | `clonar-y-actualizar` | Clonar y mantener al día (existe) | 20 |
| `3_de_donde_viene.md` | `de-donde-viene-git` | De dónde viene Git | 8 |
| `4_tu_primer_repositorio.md` | `tu-primer-repositorio` | Tu primer repositorio | 30 |
| `5_que_guarda_un_commit.md` | `que-guarda-un-commit` | Qué guarda un commit | 12 |
| `6_lo_que_no_se_sube.md` | `lo-que-no-se-sube` | Lo que no se sube | 12 |
| `7_deshacer.md` | `deshacer-en-git` | Deshacer | 20 |
| `8_branches_y_merge.md` | `branches-y-merge` | Branches y merge | 25 |
| `9_git_no_es_github.md` | `git-no-es-github` | Git no es GitHub | 25 |
| `10_dos_personas_un_archivo.md` | `dos-personas-un-archivo` | Dos personas, un archivo | 12 |
| `11_el_flujo_del_curso.md` | `el-flujo-del-curso` | El flujo del curso | 15 |
| `12_el_ritual.md` | `el-ritual-del-curso` | El ritual | 10 |
| `A_cheatsheet.md` | `cheatsheet-git` | Cheatsheet | 5 |

Clase 1 son las páginas 3 a 7, unos 82 minutos. Clase 2 son las páginas 8 a
12, unos 87 minutos. Los tiempos de la versión 1 estaban subestimados cerca
del doble en las páginas 4, 7, 8 y 9; estos ya son realistas y por eso la
página 3 se recortó a 8 minutos.

Los ids `deshacer` y `el-ritual` de la versión 1 se cambiaron a
`deshacer-en-git` y `el-ritual-del-curso`: el namespace de wikilinks es
global al curso e incluye `title` y `nav_title`, así que un id genérico
produce `Ambiguous wikilink reference` más adelante. No usar `git-deshacer`,
que colisiona con el id de la figura.

Esqueleto de página igual que en las unidades 5 y 6: frontmatter compacto,
`# Título`, línea `Página N de M · X min`, `Meta:` de una frase, figura de
apertura, `## En corto` con 3 a 5 bullets, cuerpo con el ritmo `**Haz:**` →
bloque de código → `**Deberías ver:**` → `**Pausa:**`, un `::: problem` con
su `hint` y su `answer`, un `> [!NOTE]` de "Si sólo recuerdas una cosa", y
`## Cierre` con wikilink. **Todas** las páginas llevan `::: problem`,
incluidas la 3, la 11 y la 12, que en la versión 1 lo omitían y rompían el
ritmo.

Ids de figure, table y problem con prefijo `git-`, únicos en todo el curso.
Los problems arrancan en **`git-p3-`**: `git-p1-fallo` y `git-p2-pull` ya
están ocupados por las páginas 1 y 2.

## Trampas de Markdown que tumban el build

Se listan aquí porque tres páginas las van a pisar:

- Los marcadores de conflicto van **dentro** de un bloque cercado ```` ```text ````.
  Una línea de `=======` bajo un párrafo es un encabezado setext, y `>>>>>>>`
  al inicio de línea es blockquote.
- Un `[^...]` o `[!...]` fuera de bloque cercado se lee como footnote y falla
  con "Missing footnote definition". Un code span en línea **no** protege:
  raya sólo quita bloques cercados antes de buscar. Afecta a la página 6
  (patrones de `.gitignore`) y al cheatsheet.
- El `@` suelto es referencia a objeto numerado. `git@github.com` va siempre
  en code span. En las `instructions` del assignment, que son prosa plana sin
  Markdown, se escribe en palabras, como ya hace `github-ssh-setup`.
- Cualquier valor de frontmatter o de YAML con dos puntos va entrecomillado.

## Contenido por página

### 3. De dónde viene Git

Recortada a 8 minutos. Sin comandos, así que es la única página que puede ser
corta de verdad.

El problema antes de la herramienta: el kernel de Linux usaba BitKeeper bajo
una licencia gratuita que prohibía trabajar en herramientas competidoras. En
abril de 2005 Andrew Tridgell escribió un cliente libre por ingeniería
inversa y BitMover anunció el fin de la versión gratuita. **Precisión: no fue
"de un día para otro".** El anuncio fue el 5 de abril con efecto en julio.
Torvalds tuvo margen y decidió no gastarlo.

Fechas: desarrollo iniciado el 3 de abril de 2005, Git autohospedado el 7 de
abril, versión 1.0 el 21 de diciembre. El primer commit es
`e83c5163316f89bfbde7d9ab23ca2e25604af290`, con mensaje
`Initial revision of "git", the information manager from hell`. **Comillas
dobles en el original.**

La cita del nombre, Computerworld, 20 de abril de 2005: "I'm an egotistical
bastard, so I name all my projects after myself. First Linux, now git."

Tabla de lo que había antes:

| Año | Sistema | Modelo | Qué no resolvía |
|---|---|---|---|
| 1972 | SCCS | Local, un archivo, con lock | Nadie más lo toca mientras tú lo tienes |
| 1982 | RCS | Local, un archivo, con lock | Sin red, sin commits de varios archivos |
| 1986 | CVS | Centralizado | Commits no atómicos, no versiona renombrados |
| 2000 | Subversion | Centralizado | Todo pasa por el servidor; mergear duele |
| 2000 | BitKeeper | Distribuido, propietario | La licencia |
| 2005 | Git y Mercurial | Distribuido, libre | |

**Corrección de la versión 1:** decía "branches caras" de Subversion. Es
falso. SVN branchea con *cheap copies*, en tiempo constante. Lo caro es el
merge, que no tuvo merge-tracking hasta 1.5 en 2008, y el round-trip al
servidor en cada operación.

Sólo tres cifras, cada una con año y fuente:

- **93 %** de los desarrolladores usan Git, encuesta de Stack Overflow 2022,
  según el blog de Stack Overflow. Es el último año en que se preguntó. La
  versión 1 decía 93.87 %; circulan tres cifras distintas según el
  subconjunto de encuestados y ésta es la única que la fuente publica como
  suya.
- **180 millones** de desarrolladores y **986 millones** de commits empujados,
  Octoverse 2025.
- El monorepo de Windows pesaba unos **300 GB** en **2017**, cuando Microsoft
  anunció GVFS. El año importa y la versión 1 lo omitía, violando la propia
  regla del curso de fechar las cifras.

Se cortan de la versión 1: la fecha de Hamano, el epílogo de Apache 2.0, la
nota de SHA-256, los 7 500 millones de la compra y los commits del kernel.
Ninguno ayuda a abrir un pull request.

`::: problem {#git-p3-...}` — por qué un sistema centralizado no le servía al
kernel de Linux.

Figura: `git-linea-del-tiempo.svg`. Ilustración: `ilus-git-historia.jpg`.

### 4. Tu primer repositorio

**Movida antes de "Qué guarda un commit".** En la versión 1 la taxonomía
blob/tree/commit llegaba antes de que el alumno hubiera hecho un solo commit,
que es plumbing antes de porcelain y viola el registro del curso.

Laboratorio desechable en `~/fdd/git-lab`, mismo patrón que `terminal-lab` y
`regex-lab`. Advertencia explícita de no correr `git init` dentro de `~` ni
dentro de `~/fdd/fdd_o26`, y el comando para borrar y reempezar.

`git init` y qué es `.git/`. Las tres zonas: working directory, staging area,
repositorio local. `git status` y **cómo leer sus tres secciones**, que es un
tema en sí mismo y la versión 1 no lo listaba pese a que los pasos de
verificación del ritual dependen de él.

`git add`, `git commit -m`, `git log --oneline`, `git diff` contra
`git diff --staged`.

Aquí se definen **`HEAD` y la sintaxis `~N`**, que la versión 1 usaba en la
página de deshacer sin haberlos presentado nunca. `HEAD` ya aparece en la
salida de `git status`, así que es el lugar natural.

El staging se justifica con un caso: arreglaste un bug y de paso renombraste
tres cosas, y quieres dos commits separados.

Verificación de versión mínima de Git: `git switch` y `git restore` existen
desde 2.23, de 2019. Se comprueba aquí, no se asume.

`::: problem` — modificas, haces `add`, vuelves a modificar, haces `commit`.
¿Qué versión quedó guardada?

Figura: `git-tres-zonas.svg`, con las flechas de vuelta bien etiquetadas. En
el deck del semestre pasado la de regreso decía `git push`, que es un error.

### 5. Qué guarda un commit

Ahora explica el hash que el alumno **ya produjo** en la página 4. Se
verifica en vivo con `git cat-file -p` y `git hash-object`.

Los tres objetos: blob es el contenido de un archivo sin su nombre, tree es
un directorio, commit apunta a un tree raíz más su padre, autor, fecha y
mensaje.

**Precisión obligatoria sobre el snapshot.** La frase "un commit guarda una
foto completa, no diferencias" es cierta en el modelo y falsa en el disco,
porque los packfiles sí almacenan deltas. Se escribe anclada al nivel
correcto: el modelo de Git es una foto completa; al empaquetar, Git comprime
con deltas por eficiencia, y eso es almacenamiento, no el modelo. Sin esa
aclaración el alumno que abra un packfile en tercer semestre concluye que le
mintieron.

Dos archivos con el mismo contenido son el mismo blob, **dentro del mismo
repositorio y con el mismo modo**. El `::: problem` debe decirlo así.

De ahí sale que **Git rastrea archivos, no carpetas**, y de ahí el
`.gitkeep`, que es una convención sin ningún significado para Git.

Figura: `git-objetos.svg`.

### 6. Lo que no se sube

`git add .` barre lo que no miraste: `.DS_Store`, `__pycache__/`,
`.ipynb_checkpoints/`, `node_modules/`, `.env`, y en WSL2 los
`:Zone.Identifier` que aparecen al copiar desde `/mnt/c/`. Los tres últimos
están documentados en carpetas reales del semestre pasado.

**La regla que sustituye a la prohibición.** La versión 1 heredaba "nunca
`git add .`" sin dar alternativa, y el resultado predecible es que el alumno
lo usa igual cuando tiene ocho archivos. La regla correcta es: *agrega una
ruta que puedas nombrar y que acabas de ver en `git status`*. Eso permite
`git add estudiantes/$U/07_git` y sigue prohibiendo `git add .`, que se
dispara desde la raíz del repo e incluye lo que nunca miraste.

`.gitignore`: patrones glob, no expresiones regulares. Alcance por
directorio. **Dos reglas que faltaban:** no aplica a archivos ya rastreados, y
no puedes desiginorar un archivo si su directorio padre está ignorado.

Credenciales, con los dos casos separados, que la versión 1 mezclaba:

| Estado del `.env` | Qué hacer |
|---|---|
| Sólo en staging | `git rm --cached` basta |
| Ya commiteado | `git rm --cached`, y **rotar la credencial**. La historia no se limpia |

Se enseña `git rm --cached` y no `commit --amend`, que reescribe historia.

Nota sobre el `.gitignore` de la raíz del repo del curso, que ignora `lib/`,
`build/`, `dist/`, `venv/`, `env/`, `*.log` y `.env`. Un alumno cuyo trabajo
caiga en `estudiantes/$U/07_git/venv/` lo verá desaparecer en silencio. Es
irónico en esta página y por eso va aquí.

Figura: `git-lo-que-no-se-sube.svg`.

### 7. Deshacer

La pregunta que ordena la página: **dónde está el cambio que quiero
deshacer.**

| Dónde está | Qué quiero | Comando |
|---|---|---|
| Working directory, archivo ya rastreado | Descartar lo que edité | `git restore <archivo>` |
| Staging area | Sacarlo del staging, sin perderlo | `git restore --staged <archivo>` |
| Último commit, que no es un merge | Deshacerlo, conservar los cambios | `git reset --soft HEAD~1` |
| Último commit, que no es un merge | Deshacerlo y tirar los cambios | `git reset --hard HEAD~1` |
| En medio de algo | Guardar y volver después | `git stash` y `git stash pop` |

Correcciones sobre la versión 1, todas verificadas:

- `git restore` **no toca archivos no rastreados**. La celda lo dice. Para
  eso es `git clean`, que la unidad no enseña, y eso se declara.
- `git reset --hard HEAD~1` **truena en el primer commit** con
  `fatal: ambiguous argument 'HEAD~1'`. Un alumno en su `git-lab` recién
  iniciado lo va a pegar. Se advierte.
- `HEAD~1` sobre un **merge commit** es el primer padre, así que descarta la
  rama entera que se mergeó. Por eso la tabla dice "que no es un merge".
- `git reset --hard` descarta además los cambios sin commitear del working
  directory, no sólo el commit. Sólo el commit es recuperable por reflog.
- `git stash pop` **con conflicto no borra el stash**. Sale con código 1,
  deja marcadores, y `stash@{0}` sigue en la lista, así que un `pop` posterior
  duplica el trabajo. Se enseña `git stash list` y `git stash drop`.

`git reflog` como red de seguridad, con los dos matices que faltaban: son 30
días para lo inalcanzable y 90 para el resto, y **el reflog es local**, así
que se va con la carpeta si el alumno borra y vuelve a clonar.

**`revert`, `push --force` y `--force-with-lease` se sacan de esta página.**
Hablan de trabajo ya compartido, que no existe todavía en la clase 1. Se
mudan a la página 9, donde ya hay remotes. `--force-with-lease` se nombra una
sola vez y con "no lo van a necesitar en este curso": mencionarlo más es
regalar el arma.

La línea que divide la página se conserva: **lo que reescribe historia y lo
que no.**

`::: problem` — corriste `git reset --hard` y perdiste un commit. ¿Se
recupera?

Figura: `git-deshacer.svg`. Ilustración: `ilus-git-memoria.jpg`.

### 8. Branches y merge

**Una branch es un puntero movible a un commit, no una copia.** Es un archivo
de 41 bytes en `.git/refs/heads/`. Por eso crearla es instantáneo.

`git switch -c`, `git switch`, `git branch`, `git branch -d`. Se enseña
`switch` y no `checkout`. Se menciona `checkout` una vez porque aparece en
todos los tutoriales viejos.

`git merge`: fast-forward contra commit de merge. **Un merge sin fast-forward
abre un editor**, y nadie ha enseñado a salir de vim. Se configura
`core.editor` aquí, o se usa `-m`. La versión 1 dejaba esta trampa abierta.

El conflicto, provocado contra ti mismo: dos branches que tocan la misma
línea. Marcadores en bloque cercado, qué mitad es cuál, `git add` para marcar
resuelto, commit. Y la salida: `git merge --abort`.

`::: problem` corregido. La versión 1 preguntaba qué pasa al hacer `switch`
con cambios sin commitear, esperando "no te deja". **Es falso:** funciona y
los arrastra cuando el archivo no difiere entre las dos ramas, y sólo falla
cuando sí difiere. La respuesta correcta es condicional.

Figuras: `git-branches.svg` y `git-conflicto.svg`.

### 9. Git no es GitHub

Página larga y central, 25 minutos. Incluye lo que la versión 1 dejaba fuera
y que habría reventado la clase 2 entera.

La diferenciación explícita:

| Es de Git | Es de GitHub |
|---|---|
| commit, branch, merge, stash | fork, que es un clone del lado del servidor más el enlace que hace posible el pull request |
| push, pull, fetch, remote | pull request |
| el hash, la historia, `.git/` | issues, code review |
| funciona sin internet | Actions, Pages |

Un `remote` es un apodo para una URL.

**El bloque que faltaba: arreglar el `origin` que ya tienen.** El prework
clonó `raya-lucaria/fdd_o26`, así que en la máquina del alumno `origin` es el
repo del curso, donde no tiene escritura. Sin este paso, `git fetch upstream`
falla con `'upstream' does not appear to be a git repository` y
`git push origin main` da 403. Para los treinta, el mismo martes.

Primero el fork, que es una acción de navegador y la versión 1 nunca lo
decía. Después:

```bash
cd ~/fdd/fdd_o26
U=$(gh api user --jq .login); echo "$U"
git remote rename origin upstream
git remote add origin git@github.com:$U/fdd_o26.git
git remote -v
```

Con su **Deberías ver:** de cuatro líneas. Alternativa de rescate si quedó
enredado: borrar la carpeta y clonar el fork.

El comando del login no es opcional: es lo que evita `estudiantes/regina_cortes/`.
Alternativa sin `gh`: el campo *Username* en la página de perfil de GitHub.

Los tres repositorios:

| Nombre | Qué es | Permiso |
|---|---|---|
| `upstream` | `raya-lucaria/fdd_o26`, el del curso | Sólo lectura |
| `origin` | `<tu-login>/fdd_o26`, tu fork | Escribes |
| local | `~/fdd/fdd_o26` en tu disco | Escribes |

`git fetch upstream` y `git merge upstream/main` por separado, no `pull`.
**Matiz honesto:** `pull` equivale a esos dos por la configuración
`pull.rebase false` que el prework ya dejó puesta, no por naturaleza de Git.
Se dice así.

El pull request no es un comando de Git, es un botón. Y aquí van `revert`,
`push --force` y por qué reescribir historia compartida rompe el trabajo
ajeno, mudados desde la página 7.

Figura: `git-tres-repos.svg`.

### 10. Dos personas, un archivo

**Movida después de la página de GitHub**, porque todo su vocabulario se
define allá.

Tres escenarios, con la corrección del revisor técnico:

- **A.** Cada quien toca un archivo distinto. Funciona.
- **B.** Los dos tocan el mismo archivo en líneas **suficientemente
  separadas**. Funciona. La versión 1 decía "líneas distintas", que es falso:
  Git mergea por hunks con contexto, así que líneas adyacentes sí conflictúan.
  Un alumno lo reproduce en clase y descubre el error.
- **C.** Los dos tocan la misma línea. Conflicto.

Quién gana: el primer push entra. El segundo es rechazado. **Mensaje literal
corregido:** en este escenario exacto Git imprime
`! [rejected] main -> main (fetch first)`. El `(non-fast-forward)` de la
versión 1 sale después, cuando ya hiciste fetch y sigues detrás. Se listan
los dos y cuándo sale cada uno, porque el cheatsheet promete literalidad.

Las dos salidas incorrectas: `push --force`, y borrar la carpeta y volver a
clonar, que además se lleva el reflog.

Conexión con la página 11: cada quien en su carpeta hace imposible el
escenario C.

Figura: `git-race.svg`. Ilustración: `ilus-git-colaboracion.jpg`.

### 11. El flujo del curso

Zona roja y zona verde. `course/`, `codigo/` y `tools/` son de lectura.
`estudiantes/<tu-login>/` es tuya.

**La regla del mirror:**

> Tu carpeta es un mirror de `codigo/`. Misma ruta, mismo nombre, sin
> excepciones. Yo publico en `codigo/07_git/` y tú copias a
> `estudiantes/<tu-login>/07_git/`.

**El comando corregido.** La versión 1 decía
`cp -r codigo/07_git estudiantes/tu-usuario/07_git`, que es el peor bug del
diseño anterior. `cp -r` sólo renombra si el destino **no existe**; si existe,
anida y produce `07_git/07_git/`. Y el destino siempre existe, porque la
tarea pide crear la carpeta antes. Peor: el Action lo aprobaría en verde,
porque la ruta anidada sigue cayendo bajo la carpeta del alumno. La forma
correcta e idempotente:

```bash
cd ~/fdd/fdd_o26
mkdir -p estudiantes/$U/07_git
cp -r codigo/07_git/. estudiantes/$U/07_git/
```

La barra punto copia el *contenido*, no el directorio. Se explica esa
diferencia en una línea, porque es exactamente el tipo de detalle que esta
unidad enseña a notar.

Se prohíbe por escrito copiar arrastrando en Finder o Explorador, que produce
`07_git copia` y `07_git - copia`. Hay evidencia real de esto en el semestre
pasado.

El nombre de tu carpeta sale de `$U`, nunca del teclado.

Qué revisa el Action, con el mensaje de error que van a ver y qué hacer. Y el
punto que nadie les dijo: **se corrige haciendo push a la misma branch, no
abriendo otro pull request.**

`::: problem` — te rechazaron el PR por un archivo que borraste. ¿Por qué?

Figura: `git-el-mirror.svg`. Ilustración: `ilus-git-disciplina.jpg`.

### 12. El ritual

Los doce pasos **agrupados en tres bloques con nombre**. Doce ítems planos
son tres actividades distintas disfrazadas de lista, y recordar tres bloques
nombrados es una tarea factible donde recordar doce líneas no lo es.

**Paso 0, una sola vez en la vida.** Fork en el navegador, y después el
bloque de `remote rename` de la página 9.

**Bloque A — Ponte al día.**

```bash
cd ~/fdd/fdd_o26
git switch main
git fetch upstream
git merge upstream/main
git push origin main
```

**Bloque B — Abre tu espacio.**

```bash
git switch -c tarea-07-git
mkdir -p estudiantes/$U/07_git
cp -r codigo/07_git/. estudiantes/$U/07_git/
```

Y trabajar sólo ahí dentro.

**Bloque C — Entrega.**

```bash
git status
git add estudiantes/$U/07_git
git status
git commit -m "unidad 07: copia de trabajo"
git push -u origin tarea-07-git
```

Después, en el navegador: abrir el pull request verificando que
base sea `raya-lucaria/fdd_o26` en `main` y head sea tu fork en
`tarea-07-git`. **Ese selector de base es donde se equivocan** y abren el PR
contra su propio fork, así que lleva su propia figura.

Paso final: **verificar que el Action esté en verde.** Sin él, el alumno cree
que entregó.

Detalles corregidos respecto a la versión 1: hay `cd` explícito, el `push`
lleva `-u` para que el ciclo de corrección funcione, el mensaje de commit es
un ejemplo real y no `"..."`, y el paso 7 dejó de ser una celda vacía.

Los dos `git status` no son decorativos: son el hábito que evita subir
basura.

Aviso de examen en `> [!WARNING]`, sin fecha.

Figura: `git-el-ritual.svg`, dibujada como **tres carriles**, no doce filas.

### A. Cheatsheet

Sólo los comandos que la unidad enseñó, agrupados por tarea, con columna
"Dónde" que enlaza a la página de origen, igual que la unidad 6. Sección de
errores frecuentes con el mensaje literal y qué hacer, incluidos los dos
mensajes de push rechazado.

## La evaluación

El profesor pidió que el flujo se pregunte de memoria absoluta, paso por
paso. La revisión pedagógica objetó con tres argumentos que quedan
registrados aquí porque la decisión es del profesor, no del diseño:

1. Es incoherente con la tesis de la unidad. El diseño critica que el curso
   pasado enseñara una receta; un examen de recuerdo literal premia la receta
   por encima del modelo.
2. Evalúa algo que nadie hace de memoria, y califica la memorización de un
   documento de consulta que el propio curso reparte.
3. Selecciona en contra del rasgo que la unidad dice acomodar: el recuerdo
   secuencial ordenado bajo presión es memoria de trabajo, que es el canal
   comprometido en el TDAH. Y es redundante: si el PR salió verde, los doce
   pasos ocurrieron.

**Propuesta de compromiso, que conserva la exigencia y mejora el constructo:**
mantener la memorización pero sobre los **tres bloques con nombre** y no
sobre doce líneas sueltas, y repartir el resto del peso en ordenar los pasos
barajados, en identificar en qué zona vive un cambio, y en triage de errores
literales (`! [rejected] ... (fetch first)`, `Permission denied (publickey)`,
`nothing added to commit but untracked files present`). El triage es lo que
de verdad hace un profesional.

Queda como decisión abierta.

## La tarea

Assignment con id **`mirror-y-pull-request`**, colocado en
`course/7_git_y_github/_official/assignments/` para poder omitir
`scope.quantum`. Vence el **2026-09-10**.

Contenido: hacer el fork, arreglar los remotes, crear tu carpeta con
`.gitkeep`, copiar `codigo/07_git/` respetando el mirror, y abrir el pull
request con el Action en verde.

**Criterio de entrega, que la versión 1 no definía:** entregado es un pull
request abierto antes de la fecha con el check en verde. El merge es
administrativo y posterior. En Canvas se pega la URL del pull request, y eso
es lo único que se califica ahí.

Sigue la convención del repo: `instructions` en prosa plana sin Markdown,
arrobas escritas en palabras, línea final con la URL de Canvas, y el primer
`resource` titulado "Entrega en Canvas". Falta el id de Canvas.

## El GitHub Action

Se diseña aquí y se implementa después.

**Cambio de arquitectura respecto a la versión 1.** Con trigger
`pull_request`, GitHub ejecuta el workflow **tal como viene en el PR**, así
que un alumno puede editar el YAML, poner `exit 0` y pasar en verde. Va con
`pull_request_target`, que corre la versión de `main`, **sin checkout del
head**, obteniendo la lista de archivos por API. Y como check requerido en
branch protection.

Reglas:

1. Excepción total para `uumami` y para el dueño del repositorio. Se declara
   explícitamente si la excepción también salta la regla 5.
2. Toda ruta debe empezar con `estudiantes/<login>/`, **con la barra**, para
   que `estudiantes/DavidVarHOTRO/` no pase la validación de `DavidVarH`. Se
   rechaza la ruta que sea exactamente `estudiantes/<login>` y cualquiera que
   contenga `/../`. La comparación normaliza a minúsculas, porque GitHub
   acepta el login en cualquier caso, pero el mensaje de error imprime el
   login canónico esperado.
3. Basura prohibida, comparada en minúsculas y a cualquier profundidad:
   `.DS_Store`, `._*`, `Thumbs.db`, `desktop.ini`, `__pycache__/`,
   `.ipynb_checkpoints/`, `node_modules/`, `.env`, `.env.*`, `*.pyc`, `*.pyo`,
   `*.swp`, `*.swo`, `*~`, `*.save`, `.venv/`, `venv/`, `.vscode/`, `.idea/`,
   `.vs/`, `*.egg-info/`, y **`*:Zone.Identifier`**, que apareció de verdad en
   tres carpetas el semestre pasado. Más un límite de tamaño por archivo.
4. **Regla nueva: el mirror se verifica.** Si el PR toca
   `estudiantes/<login>/NN_algo/`, ese `NN_algo` debe existir en `codigo/`.
   Es lo que convierte la regla del mirror de exhortación en mecanismo. Sin
   esto, los 30 alumnos vuelven a inventar 30 nombres.
5. Rechazo si la branch de origen es `main`, **con guion de rescate en el
   mensaje**, no con un `exit 1` a secas. En el semestre pasado 71 de 574
   merges vinieron de `main`, un 12 %, con alumnos reincidentes. No es
   descuido aislado, es el estado por omisión de quien clona. El alumno que
   ya commiteó en `main` queda en un pozo del que no sale solo, así que el
   mensaje incluye los comandos literales: crear la branch desde donde está,
   pushearla, y devolver `main` a ser espejo del upstream. Es el único lugar
   del curso donde `--force-with-lease` está justificado. Además: avisar en
   el primer PR y fallar a partir del segundo.
6. Rechazo de symlinks (modo `120000`), de gitlinks o submódulos (modo
   `160000`), de `.gitattributes` fuera de la raíz, y de toda ruta bajo
   `.github/`.
7. Un PR sin archivos tocados **falla**, no pasa en verde. Es el caso que el
   bug del contador enmascaraba en la versión anterior.

Detalles de implementación que ya causaron problemas reales:

- Rutas con caracteres no ASCII salen C-quoted de `git diff --name-only`,
  con comillas y escapes, y el regex no matchea: rechazo injusto. Hay
  evidencia real, incluido un archivo con espacio no separable U+202F. Se usa
  `core.quotePath=false` o la API.
- Las eliminaciones se ignoran en la lista de prohibidos, con `--name-status`.
  Castigar a quien borra su basura es el peor falso positivo posible.
- Los globs se comparan con `case`, sin comillas. `[[ $f == "*.pyc" ]]` nunca
  coincide, y ése es uno de los tres bugs heredados.
- El contador es `COUNT=$((COUNT+1))`. `((COUNT++))` devuelve estado 1 en
  cero y aborta el job.
- Bloque `permissions:` explícito, mínimo.
- Paginar la lista de archivos, o fallar si llega al límite de la API.
- Nunca sugerir `commit --amend` como remedio.

## Operación

Cosas que hay que resolver o el flujo no funciona aunque las páginas estén
perfectas:

- **`estudiantes/` y `codigo/` no existen en `fdd_o26`.** Hay que crearlos,
  con `estudiantes/.gitkeep`, **antes de la sesión 09**. Es bloqueante, no un
  pendiente menor. `codigo/` no va en `.gitignore`: es material que el alumno
  necesita en su clone.
- **Un `.gitattributes` en la raíz** con `* text=auto`, o los finales de
  línea de Windows producen diffs de archivo completo que revientan el Action
  sin que nadie entienda por qué.
- **Auto-merge.** Treinta merges a mano por tarea, por quince tareas, son 574
  merges como el semestre pasado. Con `gh pr merge --squash --auto` y el
  check como requerido se mergean solos al pasar. Hay que **desactivar**
  "Require branches to be up to date before merging", o treinta alumnos
  tendrían que rebasear.
- **Saber quién entregó** sin leer treinta PRs a mano: un job que liste los
  PRs con autor, branch y estado.

## Imágenes

**Diagramas.** Once SVG nuevos en `tools/gen_git.py`, que ya existe y genera
`git-llaves.svg` y `git-flujo.svg`.

| Archivo | Página | Qué muestra |
|---|---|---|
| `git-linea-del-tiempo.svg` | 3 | De 1972 a hoy, con el modelo de cada sistema |
| `git-tres-zonas.svg` | 4 | working, staging, local, con ida y vuelta |
| `git-objetos.svg` | 5 | commit, tree, blob y el hash del contenido |
| `git-lo-que-no-se-sube.svg` | 6 | Qué barre `git add .` |
| `git-deshacer.svg` | 7 | Árbol de decisión según dónde está el cambio |
| `git-branches.svg` | 8 | La branch como puntero; fast-forward contra merge |
| `git-conflicto.svg` | 8 | Los marcadores y qué mitad es cuál |
| `git-tres-repos.svg` | 9 | upstream, origin, local, y por dónde va cada flecha |
| `git-race.svg` | 10 | Los tres escenarios y el push rechazado |
| `git-el-mirror.svg` | 11 | Los dos árboles lado a lado, zona roja y verde |
| `git-el-ritual.svg` | 12 | Los tres bloques en carriles, no doce filas |

Más una figura del selector de base del pull request, dentro de
`git-el-ritual.svg` o aparte.

Checklist real para cada SVG, verificado contra `test_gen_git.py`:

1. Entrada en `DIAGRAMAS` con clave que empieza con `git-`.
2. El archivo se produce corriendo el generador, **nunca a mano**: el test
   compara byte a byte con lo que devuelve la función.
3. Ningún `.svg` en `_assets/` sin entrada en `DIAGRAMAS`.
4. La cadena `<clave>.svg` aparece en un `.md` de la **raíz** de la unidad. El
   test usa `glob`, no `rglob`: si una página se promueve a directorio, su
   figura deja de contar. Otra razón para el layout plano.
5. `aria-label` de 80 caracteres o más, sin acentos.
6. Colores importados de `svg_base`, nunca hex literal. **Corrección de la
   versión 1:** `test_los_colores_salen_del_skin` no mira los SVG, sólo
   comprueba que las constantes de `svg_base` estén en el skin. Un hex a mano
   pasa pytest y revienta después en la validación de contraste.
7. **Las flechas sólo admiten ocho colores**, los de `COLORES_FLECHA`. Usar
   `TINTE`, `PANEL` o `FONDO` en `flecha()`, `arco()` o `curva()` produce un
   marcador sin definir: flecha sin punta, y ningún test lo detecta. Afecta
   directamente a `git-tres-repos`, `git-race` y `git-tres-zonas`, que son
   casi puras flechas.
8. Fila en `CREDITOS.md` con las cinco columnas.

**Ilustraciones.** Cuatro nuevas, más la portada que ya existe. Paleta libre
por lámina, que es lo que el estilo compartido ya permite. El registro visual
se cita, el personaje y el título nunca: `test_ilustraciones.py` ya lista esas
obras como prohibidas, con esa lógica escrita en un comentario.

| Nombre | Página | Registro y paleta |
|---|---|---|
| `git-portada` | 0 | Existe. Sala de servidores, verde y ámbar |
| `git-historia` | 3 | Suburbio al anochecer, tendido eléctrico, brillo de tubo catódico. Sepia lavado y violeta |
| `git-memoria` | 7 | Escala larga: una silueta pequeña vuelve a un lugar que ya visitó, estaciones superpuestas. Verdes suaves, cielo acuarela |
| `git-colaboracion` | 10 | Ciudad densa bajo lluvia, dos siluetas en torres separadas, un solo cable entre ellas. Teal y concreto |
| `git-disciplina` | 11 | Un umbral iluminado y un pasillo que no se cruza. Ámbar contra azul frío |

Checklist verificado contra `test_ilustraciones.py`:

1. Clave en `ilustraciones` con valor **string**, nunca dict. El test itera
   `prompt.lower()` y el generador concatena el valor al prompt.
2. Entrada en `unidades` → `7_git_y_github`. **Las cuatro faltaban en la
   versión 1** y el test las exige una por una.
3. Archivo de 1024 px de ancho y menos de 400 000 bytes.
4. La cadena `_assets/ilus-<nombre>.jpg` usada en alguna página. En la versión
   1 `git-disciplina` no tenía página asignada; ahora va en la 11.
5. Fila en `CREDITOS.md`, que debe seguir conteniendo `generada`, `ninguna` y
   `personas reales`.
6. Ninguna palabra prohibida en **todo** el JSON, porque el test serializa el
   catálogo entero. El registro pastoral es justo donde se escapa un nombre de
   obra o de estudio. Describir la atmósfera, nunca nombrarla.
7. Ninguna palabra de `PROHIBIDOS_EN_PROMPT` en el prompt. Ojo: "sin rostros
   identificables" **falla** si se escribe en un prompt; vive sólo en
   `estilo`.

**Para que `git-memoria` pueda salirse del registro urbano** hacen falta dos
parches exactos, porque la forma que proponía la versión 1 rompía los tests:

- `ilustraciones.json` gana un mapa hermano de `unidades` llamado `estilos`,
  de nombre a string. **No** un dict dentro de `ilustraciones`.
- `gen_ilustraciones.generar` usa
  `datos.get("estilos", {}).get(nombre, datos["estilo"])`.
- `test_catalogo_tiene_las_llaves_esperadas` compara por igualdad estricta y
  hay que relajarlo a contención, exigiendo las cuatro llaves obligatorias y
  admitiendo `estilos`.
- Conviene extender `test_el_estilo_prohibe_texto_y_rostros_identificables` a
  cada valor de `estilos`, o el estilo nuevo queda sin guarda.

Quince filas nuevas en `CREDITOS.md`, de cinco celdas cada una. Y hay que
corregir la fila de `git-flujo.svg`, que describe un diagrama que ya no
existe.

## Calendario

Se agrega **al final**, cuando las páginas existan. `page` que no resuelve
tumba el build entero, y `el-flujo-del-curso` no existe todavía.

```yaml
  - id: session-08
    kind: session
    date: "2026-09-03"
    start_time: "19:00"
    end_time: "20:30"
    title: "Git: qué guarda y cómo se deshace"
    page: git-y-github

  - id: session-09
    kind: session
    date: "2026-09-08"
    start_time: "19:00"
    end_time: "20:30"
    title: "GitHub: branches, forks y el flujo del curso"
    page: branches-y-merge
```

La versión 1 apuntaba `session-09` a `el-flujo-del-curso`, que es la página
11, cuando la clase 2 empieza en la 8. Corregido.

La tarea no se escribe como evento: su `content.due` genera la ocurrencia.

## Fuera de alcance

Flashcards, quizzes y el examen. El deck de la presentación. La
implementación del Action. El contenido de `codigo/07_git/`.

## Decisiones abiertas

1. **La evaluación.** Memorización literal de doce pasos contra el compromiso
   descrito arriba. Es decisión del profesor.
2. **Id de Canvas** para el assignment.
3. **Renumeración del prework.** Las páginas 1 y 2 dicen "Hoja 1 de 2" y el
   índice dice "Las dos hojas". Con catorce páginas hay que reescribir esas
   líneas. Trabajo que la versión 1 no contabilizaba al decir que no se
   tocaban.
4. **`git-flujo.svg`** queda conceptualmente obsoleto cuando aparece el fork,
   no sólo su fila en CREDITOS.
5. **Doble nombre en el curso:** la unidad 6 publica `chuleta-regex` y ésta
   publicará `cheatsheet-git`. Queda inconsistente hasta que se unifique.

## Correcciones pendientes en CLAUDE.md

- Dice que los ids de figura son únicos por página. Son únicos en todo el
  curso: el builder mantiene un solo conjunto de ids vistos.
- Dice que la última sesión del calendario es `session-06`. Ya existe
  `session-07`.
