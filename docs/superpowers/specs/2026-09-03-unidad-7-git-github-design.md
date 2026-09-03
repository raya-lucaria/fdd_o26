# Unidad 7 — Git y GitHub

Diseño de la unidad. Dos sesiones de clase, una sola unidad publicada.

## Qué es

Una unidad de dos clases que lleva a alguien que nunca ha usado Git desde la
historia del problema hasta abrir un pull request correcto contra el
repositorio del curso. Las tres páginas que ya existen (`git-y-github`,
`cuenta-y-llave`, `clonar-y-actualizar`) son el prework de SSH y clone, ya
entregado como task el 2026-09-03, y no se tocan salvo para enlazar hacia
adelante.

Sesiones: `session-08` jueves 2026-09-03 y `session-09` martes 2026-09-08.
La tarea se entrega en la clase inmediata siguiente, `session-10`, jueves
2026-09-10.

## Idea que sostiene toda la unidad

**Git es una herramienta que vive en tu máquina y no sabe qué es internet.
GitHub es una empresa que hospeda repositorios de Git y le agrega encima lo
que Git no tiene.**

Esa frase es el esqueleto. Durante toda la clase 1 nadie se conecta a nada:
se trabaja en un laboratorio desechable con `git init`, y `commit` no sube
nada a ningún lado. Cuando en la clase 2 aparece GitHub, la pregunta "¿ya se
ve en la nube?" tiene respuesta obvia, porque ya quedó claro que el
repositorio local es completo por sí solo.

Registro heredado de las unidades 5 y 6: el concepto llega **después** de la
falla concreta, nunca como definición suelta. Español para la prosa, inglés
para los términos técnicos (commit, push, pull, merge, branch, staging, fork,
pull request, stash). Se dice "mergear", no "fusionar". Se dice "cheatsheet",
no "chuleta".

## Qué corregimos del curso pasado

Del análisis de `fdd_p26/clase/06_git/` y de los decks del profesor:

1. **Se enseñaba una receta, no Git.** Staging, branches y conflictos vivían
   en un archivo opcional (`07_arquitectura_git.md`) que quedaba fuera del
   flujo. Aquí el modelo va primero y el flujo se deriva de él.
2. **El conflicto se evitaba, no se resolvía.** La regla era "no trabajen
   sobre el mismo archivo" y dejaba al alumno indefenso cuando ocurría. Aquí
   se provoca un conflicto a propósito, se leen los marcadores y se sale con
   `git merge --abort`.
3. **El mirror del código era ambiguo.** "Copia el código de la clase a tu
   carpeta" no decía de dónde, ni cómo, ni con qué nombre. Resultado: treinta
   convenciones incompatibles en `estudiantes/`. Aquí hay una sola regla.
4. **El GitHub Action era invisible.** El alumno veía una tacha roja sin que
   nadie le hubiera dicho que existía. Aquí se explica antes de que repruebe.
5. **El cheatsheet contradecía el flujo** (`git pull origin main`, `git add .`,
   clone por HTTPS). Aquí el cheatsheet sólo lista lo que el flujo usa.

## Estructura

Layout plano, como la unidad 6. Archivos en la raíz de
`course/7_git_y_github/`, un solo `_assets/`.

| Archivo | id | Página | Min |
|---|---|---|---:|
| `0_index.md` | `git-y-github` | Git y GitHub (se reescribe el mapa) | — |
| `1_cuenta_y_llave.md` | `cuenta-y-llave` | Cuenta y llave (existe) | 25 |
| `2_clonar_y_actualizar.md` | `clonar-y-actualizar` | Clonar y mantener al día (existe) | 20 |
| `3_de_donde_viene.md` | `de-donde-viene-git` | De dónde viene Git | 10 |
| `4_que_guarda_un_commit.md` | `que-guarda-un-commit` | Qué guarda un commit | 10 |
| `5_tu_primer_repositorio.md` | `tu-primer-repositorio` | Tu primer repositorio | 15 |
| `6_lo_que_no_se_sube.md` | `lo-que-no-se-sube` | Lo que no se sube | 10 |
| `7_deshacer.md` | `deshacer` | Deshacer | 15 |
| `8_branches_y_merge.md` | `branches-y-merge` | Branches y merge | 15 |
| `9_dos_personas_un_archivo.md` | `dos-personas-un-archivo` | Dos personas, un archivo | 12 |
| `10_git_no_es_github.md` | `git-no-es-github` | Git no es GitHub | 13 |
| `11_el_flujo_del_curso.md` | `el-flujo-del-curso` | El flujo del curso | 15 |
| `12_el_ritual.md` | `el-ritual` | El ritual | 10 |
| `A_cheatsheet.md` | `cheatsheet-git` | Cheatsheet | 5 |

Clase 1 son las páginas 3 a 7. Clase 2 son las páginas 8 a 12.

Esqueleto de página, igual que en las unidades 5 y 6: frontmatter compacto,
`# Título`, línea `Página N de M · X min`, `Meta:` de una frase, figura de
apertura, `## En corto` con 3 a 5 bullets, cuerpo en pasos con el ritmo
`**Haz:**` → bloque de código → `**Deberías ver:**` → `**Pausa:**`, un
`::: problem` con su `hint` y su `answer`, un `> [!NOTE]` de "Si sólo
recuerdas una cosa", y `## Cierre` con wikilink a la siguiente.

Prefijo obligatorio `git-` en todos los ids de figure, table y problem.

## Contenido por página

### 3. De dónde viene Git

El problema antes de la herramienta. El kernel de Linux usaba BitKeeper bajo
una licencia gratuita que prohibía trabajar en herramientas competidoras. En
abril de 2005 Andrew Tridgell escribió un cliente libre por ingeniería
inversa, BitMover retiró la licencia, y el kernel se quedó sin sistema de
versiones de un día para otro.

Cronología con fechas exactas: desarrollo iniciado el 3 de abril de 2005,
Git autohospedado el 7 de abril, primer kernel gestionado con Git en junio,
Junio Hamano como mantenedor desde el 26 de julio, versión 1.0 el 21 de
diciembre. El primer commit es
`e83c5163316f89bfbde7d9ab23ca2e25604af290`, con mensaje "Initial revision of
'git', the information manager from hell".

La anécdota del nombre, con la cita de Torvalds a Computerworld en abril de
2005: "I'm an egotistical bastard, so I name all my projects after myself.
First Linux, now git."

Tabla de lo que había antes, con el modelo de cada uno y el problema que
heredaba al siguiente:

| Año | Sistema | Modelo | Qué no resolvía |
|---|---|---|---|
| 1972 | SCCS | Local, un archivo, con lock | Nadie más puede tocarlo mientras tú lo tienes |
| 1982 | RCS | Local, un archivo, con lock | Sin red, sin commits de varios archivos a la vez |
| 1986 | CVS | Centralizado | Commits no atómicos, no versiona renombrados |
| 2000 | Subversion | Centralizado | Todo pasa por el servidor; branches caras |
| 2000 | BitKeeper | Distribuido, propietario | La licencia |
| 2005 | Git y Mercurial | Distribuido, libre | |

Los tres requisitos que Torvalds puso, de la charla en Google de 2007:
distribuido, rápido, y con garantía de integridad. La frase "If you cannot
guarantee that the stuff I put into an SCM comes out exactly the same, you
are not worth using" es la que después justifica el hash de la página 4.

Números de hoy, cada uno con su año: Git al 93.87 % en la encuesta de Stack
Overflow de 2022, que es el último año en que se preguntó; 180 millones de
desarrolladores y 986 millones de commits empujados según Octoverse 2025;
1.48 millones de commits en el kernel de Linux; Microsoft compró GitHub en
2018 por 7 500 millones de dólares; el monorepo de Windows pesa unos 300 GB.
Epílogo: BitKeeper se liberó bajo Apache 2.0 en 2016, once años tarde.

Figura: `git-linea-del-tiempo.svg`. Ilustración: `ilus-git-historia.jpg`.

### 4. Qué guarda un commit

Un commit no guarda diferencias, guarda una foto completa del proyecto. Los
tres objetos: blob es el contenido de un archivo sin su nombre, tree es un
directorio que lista modo, tipo, hash y nombre, commit apunta a un tree raíz
más su padre, autor, fecha y mensaje.

El hash como dirección, no como número de serie. SHA-1, 160 bits, 40
caracteres hexadecimales, calculado sobre el contenido. Dos archivos con el
mismo contenido son el mismo blob aunque se llamen distinto y estén en
carpetas distintas. La cita de Pro Git: "Git is fundamentally a
content-addressable filesystem with a VCS user interface written on top of
it." Nota corta sobre la transición a SHA-256, experimental desde Git 2.29 en
2020 y todavía incompleta.

De ahí sale, sin esfuerzo, el hecho que confunde a todos: **Git rastrea
archivos, no carpetas.** Un tree sólo existe si hay algo adentro, así que una
carpeta vacía no se puede commitear. El `.gitkeep` es una convención de la
comunidad, no una característica de Git: es un archivo cualquiera puesto ahí
para que la carpeta exista. Esto se planta aquí y se cobra en la página 11.

`::: problem` — dos archivos idénticos en carpetas distintas: ¿cuántos blobs
hay en el repositorio?

Figura: `git-objetos.svg`.

### 5. Tu primer repositorio

Laboratorio desechable en `~/fdd/git-lab`, mismo patrón que `terminal-lab` y
`regex-lab`. Se rompe a propósito y se puede borrar entero.

`git init`, y qué es `.git/`. Las tres zonas: working directory, staging
area, repositorio local. `git status` como el comando que se corre siempre.
`git add` por archivo. `git commit -m`. `git log --oneline`. `git diff`
contra `git diff --staged`, que es la pareja que hace visible el staging.

El staging se justifica con un caso, no con una definición: arreglaste un bug
y de paso renombraste tres cosas, y quieres dos commits separados. Sin
staging no puedes.

Mensajes de commit: qué cambió y por qué. Tabla de malos contra buenos.

`::: problem` — modificas un archivo, haces `add`, lo vuelves a modificar y
haces `commit`. ¿Qué versión quedó guardada?

Figura: `git-tres-zonas.svg`, con las flechas de ida y de vuelta bien
etiquetadas. En el deck del semestre pasado la flecha de regreso decía
`git push`, que es un error.

### 6. Lo que no se sube

`git add .` es la peor costumbre y aquí se explica por qué, no se prohíbe y
ya. Barre lo que no miraste: `.DS_Store` que el Finder de macOS escribe en
cada carpeta que abres, `__pycache__/`, `.ipynb_checkpoints/`,
`node_modules/`, y el caso grave, `.env` con credenciales. Una credencial
subida a un repo público se considera comprometida aunque la borres después,
porque queda en la historia.

`.gitignore`: patrones glob, no expresiones regulares. Alcance por
directorio. Qué hacer con un archivo que ya quedó rastreado, con
`git rm --cached`. Se enseña ese camino y no `commit --amend`, que reescribe
historia y para alguien que empieza es peor que el problema.

El `.gitkeep`, cobrando lo que se plantó en la página 4.

`::: problem` — agregaste `.env` al `.gitignore` pero sigue apareciendo en
`git status`. ¿Por qué?

Figura: `git-lo-que-no-se-sube.svg`.

### 7. Deshacer

La pregunta que ordena la página no es qué comando quiero, es **dónde está el
cambio que quiero deshacer.** Tabla de decisión:

| Dónde está | Qué quiero | Comando |
|---|---|---|
| Working directory | Descartar lo que edité | `git restore <archivo>` |
| Staging area | Sacarlo del staging, sin perderlo | `git restore --staged <archivo>` |
| Último commit, sin push | Deshacerlo, conservar los cambios | `git reset --soft HEAD~1` |
| Último commit, sin push | Deshacerlo y tirar los cambios | `git reset --hard HEAD~1` |
| Commit ya pusheado | Deshacerlo sin reescribir historia | `git revert <hash>` |
| En medio de algo | Guardar y volver después | `git stash` y `git stash pop` |

`stash` y `pop` con su caso real: te piden revisar otra cosa a media edición
y no quieres commitear a medias.

La línea que divide la página: **lo que reescribe historia y lo que no.**
`reset` y `--amend` reescriben. `revert` no. Sobre una branch tuya que nadie
más usa, reescribir es barato. Sobre algo que ya compartiste, es lo que rompe
el trabajo de los demás, y ahí es donde `push --force` deja de ser un comando
y se vuelve un problema social. Se menciona `--force-with-lease` como el
menos malo, sin recomendarlo.

`git reflog` como la red de seguridad: casi nada se pierde de verdad durante
treinta días.

`::: problem` — corriste `git reset --hard` y perdiste un commit. ¿Se
recupera?

Figura: `git-deshacer.svg`, árbol de decisión.
Ilustración: `ilus-git-memoria.jpg`.

### 8. Branches y merge

**Una branch es un puntero movible a un commit, no una copia de los
archivos.** Ese es el punto entero de la página, y es lo que hace que crear
una branch sea instantáneo. `HEAD` es el puntero que dice en cuál estás.

`git switch -c` para crear, `git switch` para moverse, `git branch` para
listar. Se enseña `switch` y no `checkout`, que hace demasiadas cosas
distintas. Se menciona `checkout` una vez porque aparece en todos los
tutoriales viejos.

`git merge`: fast-forward cuando no hubo trabajo paralelo, commit de merge
cuando sí. Con diagrama, porque en texto no se entiende.

El conflicto, provocado a propósito y contra ti mismo: dos branches que
tocan la misma línea del mismo archivo. Se ven los marcadores `<<<<<<<`,
`=======`, `>>>>>>>`, se explica qué mitad es cuál, se edita el archivo, se
hace `git add` para marcarlo resuelto, y se commitea. Y la salida de
emergencia: `git merge --abort` deja todo como estaba.

`git branch -d` para limpiar después del merge.

`::: problem` — estás en una branch con cambios sin commitear e intentas
`switch` a otra. ¿Qué pasa?

Figura: `git-branches.svg` y `git-conflicto.svg`.

### 9. Dos personas, un archivo

Esta es la pieza socrática del deck del profesor, que era lo mejor que tenía
y nunca llegó al sitio. Se conserva la estructura de pregunta y respuesta.

Dos personas clonan el mismo repositorio. Escenario A: cada quien toca un
archivo distinto, ambos hacen push, y funciona, porque Git mergea por líneas
y no por archivos. Escenario B: los dos tocan el mismo archivo en líneas
distintas, y también funciona, lo cual sorprende. Escenario C: los dos tocan
la misma línea, y ahí sí colisiona.

Quién gana: el primer push entra, el segundo es rechazado con
`! [rejected]` y `non-fast-forward`. No es un castigo, es Git negándose a
tirar trabajo que no ha visto. La salida correcta es `git pull`, resolver si
hay conflicto, y volver a pushear.

Las dos salidas incorrectas, dichas con nombre: `push --force`, que borra el
trabajo del otro, y borrar la carpeta y volver a clonar, que es lo que hace
mucha gente en pánico.

Aquí se conecta con la regla de la página 11: la razón por la que cada quien
trabaja en su propia carpeta no es burocracia, es que hace imposible el
escenario C.

`::: problem` — tu push fue rechazado y no entiendes por qué si sólo
agregaste un archivo nuevo.

Figura: `git-race.svg`.
Ilustración: `ilus-git-colaboracion.jpg`.

### 10. Git no es GitHub

La página que hace la diferenciación explícita. Todo lo anterior funcionó sin
conexión. GitHub no es Git: es una empresa, fundada en 2008 y comprada por
Microsoft en 2018, que hospeda repositorios y agrega cosas que Git no tiene.

| Es de Git | Es de GitHub |
|---|---|
| commit, branch, merge, stash | fork |
| push, pull, fetch, remote | pull request |
| el hash, la historia, `.git/` | issues, code review |
| funciona sin internet | Actions, Pages |

Un `remote` es un apodo para una URL. `origin` no es una palabra reservada,
es sólo el nombre por omisión.

El fork: una copia del repositorio en tu propia cuenta, donde sí tienes
permiso de escritura. Los tres repositorios y sus nombres:

| Nombre | Qué es | Permiso |
|---|---|---|
| `upstream` | `raya-lucaria/fdd_o26`, el del curso | Sólo lectura |
| `origin` | `tu-usuario/fdd_o26`, tu fork | Escribes |
| local | `~/fdd/fdd_o26` en tu disco | Escribes |

`git remote add upstream`, `git remote -v`, `git fetch upstream`,
`git merge upstream/main`. Se enseñan `fetch` y `merge` por separado, no
`pull`, para que se vea que `pull` es exactamente esos dos.

El pull request: no es un comando de Git, es un botón de GitHub que dice
"tengo unos commits en mi branch, ¿los quieres en la tuya?".

Figura: `git-tres-repos.svg`, que es el concepto más difícil de la unidad y
en el deck del semestre pasado se explicaba sólo con texto.

### 11. El flujo del curso

La zona roja y la zona verde. `course/`, `codigo/`, `tools/` son de lectura.
`estudiantes/tu-usuario/` es tuya.

**La regla del mirror, que se enuncia una vez y se repite igual en todas las
unidades del resto del curso:**

> Tu carpeta es un mirror de `codigo/`. Misma ruta, mismo nombre, sin
> excepciones. Yo publico en `codigo/07_git/ejemplo.sh` y tú copias a
> `estudiantes/tu-usuario/07_git/ejemplo.sh`.

Un comando, sin decisiones:

```bash
cp -r codigo/07_git estudiantes/tu-usuario/07_git
```

No se inventa el nombre. No se decide dónde. No se pregunta. Esto requiere
crear `codigo/` en la raíz del repositorio, que hoy no existe, con
subdirectorios numerados a dos dígitos que empatan con las unidades.

El nombre de tu carpeta es **exactamente** tu usuario de GitHub, con las
mismas mayúsculas, porque el robot lo compara literalmente contra el login
del autor del pull request.

Qué revisa el GitHub Action, dicho antes de que repruebe a nadie, con el
mensaje de error que van a ver y qué hacer con él. Y el punto que nadie les
dijo el semestre pasado: **se corrige haciendo push a la misma branch, no
abriendo otro pull request.**

Figura: `git-el-mirror.svg`, con los dos árboles lado a lado.

### 12. El ritual

Página corta y deliberadamente memorizable. Los doce pasos, numerados, sin
prosa alrededor. Es la página que se pregunta en el examen.

| # | Paso | Comando |
|---|---|---|
| 1 | Ponerte en main | `git switch main` |
| 2 | Traer lo nuevo del curso | `git fetch upstream` |
| 3 | Mergearlo a tu main | `git merge upstream/main` |
| 4 | Actualizar tu fork | `git push origin main` |
| 5 | Branch con el nombre pedido | `git switch -c tarea-07-git` |
| 6 | Copiar el código al mirror | `cp -r codigo/07_git estudiantes/tu-usuario/07_git` |
| 7 | Trabajar sólo ahí dentro | |
| 8 | Revisar antes de agregar | `git status` |
| 9 | Agregar por archivo | `git add estudiantes/tu-usuario/07_git/ejemplo.sh` |
| 10 | Revisar otra vez | `git status` |
| 11 | Commitear con mensaje real | `git commit -m "..."` |
| 12 | Subir la branch y abrir el pull request | `git push origin tarea-07-git` |

Los pasos 8 y 10 no son decorativos: son el hábito que evita subir basura.

Aviso de examen, en `> [!WARNING]`, sin fecha todavía: el flujo se pregunta
de memoria, paso por paso, y una desviación cuenta como entrega no hecha.

Figura: `git-el-ritual.svg`.

### A. Cheatsheet

Sólo los comandos que el flujo usa, agrupados por tarea, con una columna
"Dónde" que enlaza a la página donde se explicó, igual que el cheatsheet de
la unidad 6. No se listan comandos que la unidad no enseñó. Sección final de
errores frecuentes con su mensaje literal y qué hacer.

## La tarea

Un `assignment` en `_official/assignments/`, que vence el **2026-09-10**.

Contenido: crear tu carpeta en `estudiantes/tu-usuario/` con un `.gitkeep`,
copiar un archivo de `codigo/07_git/` respetando el mirror, y abrir el pull
request. Nada difícil de contenido. Todo el peso está en que el flujo salga
perfecto y en que el Action pase en verde.

Sigue la convención del repo: `instructions` en un solo bloque de prosa sin
Markdown, porque llega a Canvas como texto; la línea final con la URL de
Canvas; y el primer `resource` titulado "Entrega en Canvas". Falta asignar el
id de Canvas.

## El GitHub Action

Se diseña aquí y se implementa después. Reglas:

1. Excepción total para `uumami` y para el dueño del repositorio.
2. Todo archivo tocado debe caer bajo `estudiantes/<login del autor>/`,
   comparado literalmente, distinguiendo mayúsculas.
3. Lista de basura prohibida incluso dentro de la carpeta propia:
   `.DS_Store`, `._*`, `Thumbs.db`, `desktop.ini`, `__pycache__/`,
   `.ipynb_checkpoints/`, `node_modules/`, `.env`, `.env.*`, `*.pyc`,
   `*.swp`, `*~`.
4. Rechazo si la branch de origen del pull request es `main`. Esto es lo que
   fuerza la disciplina de branches, y es nuevo respecto al semestre pasado.
5. La lista de archivos se obtiene con `gh pr diff --name-only`, no con
   `git diff` contra la base.
6. El mensaje de error dice qué hacer, y dice explícitamente que se corrige
   con push a la misma branch.

Tres bugs del action de `fdd_p26` que no se repiten: los patrones de glob
entre comillas, que nunca coinciden y dejaban pasar `*.pyc` y `*.swp`; el
contador `((COUNT++))`, que devuelve estado 1 en cero y abortaba el job; y el
consejo de arreglar con `commit --amend`.

## Imágenes

**Diagramas.** Once SVG nuevos en `tools/gen_git.py`, registrados en
`DIAGRAMAS`, con prefijo `git-`, en la paleta del skin `fdd-eva` porque
`test_gen_git.py` valida los colores contra ella y el sitio valida contraste.

| Archivo | Página | Qué muestra |
|---|---|---|
| `git-linea-del-tiempo.svg` | 3 | De 1972 a hoy, con el modelo de cada sistema |
| `git-objetos.svg` | 4 | commit, tree, blob y el hash del contenido |
| `git-tres-zonas.svg` | 5 | working, staging, local, remoto, ida y vuelta |
| `git-lo-que-no-se-sube.svg` | 6 | Qué barre `git add .` |
| `git-deshacer.svg` | 7 | Árbol de decisión según dónde está el cambio |
| `git-branches.svg` | 8 | La branch como puntero; fast-forward contra merge |
| `git-conflicto.svg` | 8 | Los marcadores y qué mitad es cuál |
| `git-race.svg` | 9 | Los tres escenarios y el push rechazado |
| `git-tres-repos.svg` | 10 | upstream, origin, local, y por dónde va cada flecha |
| `git-el-mirror.svg` | 11 | Los dos árboles lado a lado, zona roja y verde |
| `git-el-ritual.svg` | 12 | Los doce pasos en carriles |

**Ilustraciones.** Cuatro nuevas con `gpt-image-2`, más la portada que ya
existe. La paleta es libre por lámina, que es lo que el estilo compartido ya
permite: cada lámina declara su propia paleta y ésta domina la imagen.

El registro visual se cita, el personaje y el título nunca. `test_ilustraciones.py`
ya lista esas obras como prohibidas en el texto del prompt, con esa lógica
escrita en un comentario. Lo que se describe es la atmósfera: animación cel
pintada a mano, una sola fuente de luz por lámina, figuras siempre de
espaldas y en silueta.

| Nombre | Página | Registro y paleta |
|---|---|---|
| `git-portada` | 0 | Existe. Sala de servidores, verde y ámbar |
| `git-historia` | 3 | Suburbio japonés al anochecer, tendido eléctrico, brillo de tubo catódico. Sepia lavado y violeta apagado |
| `git-memoria` | 7 | Fantasía pastoral de escala larga: una silueta pequeña vuelve a un lugar que ya visitó, estaciones superpuestas. Verdes suaves y cielo acuarela |
| `git-colaboracion` | 9 | Ciudad densa bajo lluvia, dos siluetas en torres separadas y un solo cable entre ellas. Teal y concreto |
| `git-disciplina` | 11 | Un umbral iluminado y un pasillo que no se cruza. Ámbar contra azul frío |

La lámina `git-memoria` es de registro pastoral y no urbano, así que necesita
salirse del `estilo` compartido. Cambio pequeño en `gen_ilustraciones.py` y
en `ilustraciones.json`: una llave opcional `estilos` y un `estilo` por
ilustración, con el compartido como valor por omisión.

Toda imagen nueva necesita su fila en `_assets/CREDITOS.md` o
`test_creditos.py` reprueba. De paso hay que corregir la fila de
`git-flujo.svg`, que describe una versión anterior del diagrama.

## Calendario

Agregar dos sesiones a `course/_official/calendar/1_2026-o26.yaml`:

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
    page: el-flujo-del-curso
```

La tarea no se escribe como evento: su `content.due` genera la ocurrencia
sola.

## Fuera de alcance

Flashcards, quizzes y el examen. El deck de la presentación. La
implementación del GitHub Action. El contenido de `codigo/07_git/`. Todo eso
se hace después, en su propio ciclo.

## Pendientes por resolver

- Id de Canvas para el assignment.
- Confirmar que `codigo/` se crea en la raíz y con numeración a dos dígitos.
- La nota de `CLAUDE.md` que dice que la última sesión es `session-06` está
  desactualizada: el archivo ya va en `session-07`.
