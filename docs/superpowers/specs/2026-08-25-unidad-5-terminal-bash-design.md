# Diseño: unidad 5 — Terminal y Bash

**Estado:** propuesto y aprobado para planificación por el responsable del curso el
2026-08-25.  **Alcance:** contenido, objetos oficiales y calendario; no incluye
flashcards ni actividad con estado del estudiante.

## Propósito

La unidad convierte una terminal recién instalada en una herramienta cotidiana.
Todo ocurre en una carpeta local de práctica, sin repositorio, Git, GitHub,
Docker ni dependencias de desarrollo. No pretende formar administradores de
sistemas ni cubrir Bash completo.

El lector debe poder, al terminar:

1. Abrir una terminal Unix y orientarse en su directorio de trabajo.
2. Leer un comando como programa, opciones y argumentos; pedir ayuda y
   reconocer sus efectos antes de ejecutarlo.
3. Crear, revisar, mover y borrar con cuidado archivos dentro de un laboratorio
   propio; conectar programas por flujos estándar.
4. Explicar cómo Bash transforma una línea (espacios, variables, comillas,
   sustitución de comandos y globbing) antes de invocar un programa.
5. Escribir, ejecutar y depurar un script Bash pequeño que recibe una ruta y
   produce un reporte.

## Calendario y evaluación

La unidad conserva dos sesiones y no desplaza el examen:

| Fecha | Sesión | Producto o evento |
|---|---|---|
| 2026-08-25 | Terminal: usar la shell directamente | Se inicia el laboratorio y Bandit. |
| 2026-08-27 | Bash scripting: automatizar pasos repetidos | Examen escrito corto de Arquitectura de computadoras, Sistemas operativos y Pipeline de datos; vence Bandit 0–5. |

El examen es presencial y escrito. Debe ser un objeto oficial `exam` en
`course/5_terminal_y_bash/_official/exams/`, separado de Bandit y sin URL de
entrega. El calendario incorpora un evento `kind: exam` independiente de la
sesión. Bandit es un objeto oficial `assignment` con vencimiento 2026-08-27.

## Arquitectura de contenido

Se crea `course/5_terminal_y_bash/` con dos subtemas, pero no con dos
capítulos-muro. Cada subtema contiene tres estaciones consecutivas. La página
índice de cada subtema funciona como mapa y las estaciones son páginas breves.

```
course/5_terminal_y_bash/
├── 0_index.md
├── 1_terminal/
│   ├── 0_index.md
│   ├── 1_entrar_y_orientarte/0_index.md
│   ├── 2_archivos_y_comandos/0_index.md
│   └── 3_flujos_procesos_y_herramientas/0_index.md
├── 2_bash_scripting/
│   ├── 0_index.md
│   ├── 1_como_lee_bash/0_index.md
│   ├── 2_variables_comillas_y_salida/0_index.md
│   └── 3_de_pasos_a_script/0_index.md
├── _assets/
│   ├── CREDITOS.md
│   ├── d-shell-flujo.svg
│   └── d-terminal-lab.svg
└── _official/
    ├── assignments/1_bandit.yaml
    └── exams/1_examen-unidad-inicial.yaml
```

La numeración de la unidad se confirma contra el árbol actual al implementar;
el nombre estable del concepto será `terminal-y-bash`. Las páginas mantienen
frontmatter en español, IDs y nombres técnicos en inglés, y prerrequisito
`software-libre-y-sistemas-operativos`.

## Forma lectora y componentes Raya

Cada estación debe caber en 12–18 minutos de lectura activa y repetir esta
estructura visible:

1. **Haz esto ahora · X min · listo cuando…**: una actividad inicial de una
   sola acción comprobable.
2. **Modelo mínimo**: una tabla pequeña, definición o diagrama; no más de una
   idea nueva por pantalla visual.
3. **Ejemplo resuelto**: uno a cinco renglones de código.
4. **Predice → ejecuta → explica**: `::: problem`, seguido de `::: hint` y
   `::: answer` cerrados por defecto. Las respuestas no aparecen hasta que el
   estudiante decide verlas.
5. **Punto de parada**: una frase que indica qué debe existir o verse antes de
   continuar.

Se usarán `definition` únicamente para conceptos que se reutilizan, `example`
para código explicado, `activity` para acciones concretas, y `problem` para
predicción. `hint` y `answer` deben declarar `of="..."`. Las advertencias
CommonMark (`[!WARNING]`) quedan reservadas para borrado, privilegios,
redirección que sobrescribe y contraseñas. No se usan formularios, progreso,
scoring, juegos con estado ni prompts a LLM.

El código es corto y copiable. Las instrucciones nunca asumen que copiar es
comprender: cada bloque ejecutable nombra el resultado esperado. Las listas no
deben exceder cinco elementos sin agruparlas en "ahora" y "después".

### Política de ejemplos

Los ejemplos son el centro de la unidad. Cada estación trabaja sobre archivos
inventados dentro de `~/fdd/terminal-lab`: `nombres.txt`, `errores.txt`,
`dos palabras.txt` y un directorio `reportes/`. No se necesita instalar un
editor, crear cuenta, inicializar repositorio ni entender una herramienta que
aún no se ha enseñado. Un ejemplo introduce una acción; el siguiente pide
predecir una variante; la actividad final mezcla sólo las dos o tres acciones
ya vistas. Las rutas y los archivos se crean en el propio bloque antes de
usarse, para que cualquier estación pueda retomarse sin memoria de la anterior.

## Estaciones

### Terminal 1 — Entrar y orientarte

**Meta visible:** «Puedo abrir mi entorno y sé dónde estoy.»

- Preflight por plataforma: Ubuntu, Ubuntu dentro de WSL2 y macOS. Linux es la
  referencia; macOS y WSL2 son tarjetas de diferencia, no cursos paralelos.
- Terminal (la ventana) frente a shell (intérprete) y Bash (una shell). Breve
  historia: Thompson shell → Bourne shell → GNU Bash, “Bourne Again SHell”.
  macOS inicia Zsh por defecto; `bash` sigue disponible para los scripts del
  módulo.
- Prompt, `whoami`, `pwd`, `uname -s`, `echo "$SHELL"` (indicador de shell de
  login, no prueba infalible de la shell actual) y `bash --version`.
- Atajos cotidianos: `Tab`, flechas, `Ctrl-R`, `Ctrl-C`, `Ctrl-L`, `Ctrl-D`.
  Copiar/pegar y pestañas se presentan como funciones del emulador: se da la
  convención Linux/WSL2 `Ctrl-Shift-C/V` y macOS `Cmd-C/V`, sin prometer
  atajos universales de pestañas.
- Crear el único espacio de práctica. Es una carpeta local desechable, no un
  repositorio ni una estructura que deban conservar:

  ```bash
  mkdir -p ~/fdd/terminal-lab
  cd ~/fdd/terminal-lab
  ```

### Terminal 2 — Archivos y comandos

**Meta visible:** «Puedo construir y revisar mi laboratorio sin miedo.»

- Modelo de árbol y rutas: absoluta, relativa, `~`, `.`, `..`, `-`; diferencia
  entre `/`, `/root` y el home del usuario; nombres con espacios y archivos
  ocultos.
- Forma de comando: `command [options] [arguments]`; opciones cortas, largas,
  agrupadas, con valor y `--` final de opciones. Se declara que las opciones no
  son universales entre programas.
- Ayuda y descubrimiento: `--help`, `man`, `tldr`, `type -a`, `command -v`.
- Laboratorio: `ls -la`, `mkdir -p`, `touch`, `cp -i`, `mv -i`, `cat` para
  archivo pequeño, `less`, `head`, `tail`, `wc`, `find` por nombre y glob `*`.
- Borrado seguro: `rmdir`, `rm -i`; `rm -r` sólo en `terminal-lab`, después de
  vista previa con `find` o `printf '%s\n' -- *`. Explicar que `rm` no suele ir
  a la papelera. Nunca ejecutar ni recomendar `sudo rm -rf`, comodines con
  `sudo` o borrado fuera del laboratorio.

### Terminal 3 — Flujos, procesos y herramientas

**Meta visible:** «Puedo conectar programas e inspeccionar mi máquina.»

- Diagrama `tecla → shell → programa → stdout/stderr`; presentar `stdin`,
  `stdout`, `stderr` y estado de salida `$?`.
- Primero `>`, `>>`, `2>` y `2>&1`; después `|`, `tee`, `&&`, `||`. El ejemplo
  usa un archivo local y enseña que stderr no entra a un pipe por defecto.
- Secuencia pequeña `sort | uniq -c`; `grep` aparece como filtro, sin enseñar
  regex aún. No usar `cat` inútilmente en pipes.
- Procesos: `ps`, `top`/`htop`, relación con CPU, cores y RAM; `Ctrl-C` cancela
  el proceso de primer plano.
- Paquetes como tarjeta opcional y explicada: Ubuntu/WSL2 `sudo apt update &&
  sudo apt install fastfetch htop`; macOS, instalar Homebrew desde su sitio
  oficial y luego `brew install fastfetch htop`. `apt` es para uso interactivo;
  `apt-get` se menciona como interfaz histórica/scriptable. `sudo` significa
  elevar privilegios; no se usa para esconder errores. `fastfetch` reemplaza a
  `neofetch`.
- Cierre: preparación explícita para Bandit y cómo buscar documentación sin
  buscar walkthroughs.

### Bash 1 — Cómo lee Bash

**Meta visible:** «Puedo predecir qué argumentos recibe un programa.»

- Bash como lenguaje interactivo y como intérprete de scripts. `sh`, Bash,
  Zsh y Fish: comandos externos comunes no garantizan sintaxis idéntica.
- La shell separa palabras, expande y finalmente llama al programa. No se
  formaliza el orden completo de expansiones; se usa como modelo para predecir
  errores reales.
- Espacios, globbing `*`, comillas y el separador `--` como entrada al bloque
  siguiente. Ejercicio: antes de borrar, comparar `printf '%s\n' -- *` con lo
  que recibiría `rm`.
- Separadores `;`, `&&`, `||` y `(...)` como subshell, con una sola demostración
  de que un `cd` dentro de paréntesis no cambia el directorio exterior.

### Bash 2 — Variables, comillas y salida

**Meta visible:** «Puedo explicar `$`, comillas y errores.»

- Asignación `nombre=Ana` sin espacios; lectura `$nombre` y `${nombre}`.
  Explicar `$HOME` y `$PATH`, sin editar perfiles ni enseñar configuración
  persistente.
- Comillas: simples literal, dobles expanden y sin comillas permite separación
  y globbing. Predicciones con archivo de dos palabras y con `'$HOME'`,
  `"$HOME"` y `$HOME`.
- `$(command)` para sustitución, preferida sobre backticks. Distinguirla de
  `$((...))` con un único ejemplo de aritmética. Llaves: `${var}` es variable;
  `{a,b}` es brace expansion; no son la misma herramienta.
- Reforzar stdout/stderr y `$?` con una actividad que separa una salida exitosa
  de un error a archivos distintos.

### Bash 3 — De pasos a script

**Meta visible:** «Tengo un script que recibe una carpeta y produce un reporte.»

- Archivo `.sh`; primero `bash archivo.sh`, después `chmod +x` y `./archivo.sh`.
  Comparar las dos rutas de ejecución.
- Shebang `#!/usr/bin/env bash`, con nota de que fuerza Bash y evita depender
  de que la shell interactiva sea Bash. `#!/bin/bash` se explica como ruta
  frecuente, no como única opción portátil.
- Plantilla mínima: `set -u`, `printf`, argumentos `$1` y `"$@"`, `read -r`,
  `if [[ -d "$1" ]]`, mensaje de uso y `exit 1`. No presentar `set -e` como
  seguridad automática.
- Producto: `inventario.sh directorio` verifica un directorio, lista `.txt`,
  cuenta líneas y escribe `reporte.txt`. Se muestra `bash -x inventario.sh ...`
  para leer expansión y depuración.
- Condicionales sí; loops y funciones quedan como “después”, sin requerirlos
  para el producto.

## Práctica y tarea

Los problemas priorizan predicción, no recetas. Deben incluir como mínimo:

- `$archivo` frente a `"$archivo"` cuando vale `dos palabras.txt`.
- `echo '$HOME'`, `echo "$HOME"` y `echo $HOME`.
- `x${n}z` frente a `x$n z`.
- `echo "$(pwd)"` frente a `(cd /; pwd); pwd`.
- `printf 'b\na\nb\n' | sort | uniq -c`.
- `ls inexistente > salida 2> errores` y el pipe engañoso `ls inexistente | wc -l`.

Bandit cubre niveles 0–5 y pide evidencia de poder entrar al nivel 6, sin
contraseña ni captura de contraseña. La bitácora pide para cada nivel:
hipótesis, documentación consultada, comandos probados y ajuste hecho. Prohíbe
walkthroughs y respuestas de LLM; permite `man`, `--help`, documentación del
comando, búsquedas sobre el comando y pistas oficiales de Bandit.

## Visuales y créditos

El diseño usa dos portadas raster originales y dos diagramas funcionales. Las
portadas conservan el ambiente anime-tech nocturno de P26 sin copiar personajes
ni franquicias; los diagramas son la fuente de verdad para conceptos técnicos.
Todo se registra en `_assets/CREDITOS.md`:

- `hero-terminal-original.png`: estudiante anónimo ante una terminal, espacio
  negativo para el título.
- `hero-bash-original.png`: terminal → script → reporte, espacio negativo para
  el título.

- `d-shell-flujo.svg`: entrada, expansión de Bash, proceso, stdout y stderr.
- `d-terminal-lab.svg`: árbol seguro bajo `~/fdd/terminal-lab`.

Las dos portadas originales se generaron con OpenAI Image Generation el
2026-08-25, sin texto legible, logos o personajes reconocibles. Las imágenes de
P26 se revisaron visualmente, pero no se reutilizan porque el material fuente no
conserva prompts ni créditos/licencias verificables. No se copian las imágenes
anime como secuencia pedagógica ni se crean imágenes adicionales sin una
función explicativa.

## Fuera de alcance

Regex real (la siguiente unidad), `sed`, `awk`, `xargs`, `find -exec`,
here-documents, arrays, `eval`, `source`, aliases, RC files, permisos octales
profundos, ownership, SSH distinto al uso mínimo de Bandit, cron, redes,
usuarios, discos, Docker, Git, GitHub y configuración persistente del PATH.

## Verificación al implementar

1. Ejecutar `python3 -m pytest tools/ -q` y añadir guardas editoriales sólo si
   protegen un invariante nuevo.
2. Ejecutar Raya `validate` y `build` contra `../fdd_o26` desde el checkout
   hermano indicado por el repositorio.
3. Confirmar que los objetos `assignment` y `exam` aparecen por separado en
   tasks y schedule, y que el evento del calendario no duplica la tarea.
4. Inspeccionar las seis estaciones en Chromium de escritorio y móvil: código
   no desborda; `hint`/`answer` inicia cerrado; tabla de plataforma y avisos se
   pueden escanear.
5. Verificar créditos de cada asset y no editar ni versionar `artifact/`.
