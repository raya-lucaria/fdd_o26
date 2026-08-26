---
id: entrar-y-orientarte
title: "Entrar y orientarte"
nav_title: "Orientarte"
summary: "Ejecuta `pwd` y `ls`: ubícate antes de moverte por la terminal."
status: ready
estimated_time: 15m
tags: [terminal, shell, bash, ubuntu, wsl2, macos]
prerequisites: [terminal-directa]
---

# Entrar y orientarte

Meta: ubícate con `pwd`, recorre rutas y termina en `~/fdd/terminal-lab/notas/hoy/`.

## Misión 1: mira antes de moverte

**Haz:** ejecuta estas dos consultas. Ninguna modifica archivos.

```bash
pwd
ls
```

`pwd` viene de *print working directory*: imprime la ruta de la carpeta en la que estás. `ls` muestra el contenido de la carpeta actual; no imprime su nombre.

**Deberías ver:** una ruta en la primera salida, por ejemplo `/home/ana` o `/Users/ana`. La segunda puede mostrar nombres o no mostrar nada si la carpeta está vacía.

**Pausa:** señala en la salida de `pwd` cuál es la carpeta actual. Antes de avanzar, explica por qué `ls` puede producir una salida distinta en otra computadora.

## Misión 2: construye una ruta y recórrela

**Haz:** crea de una vez las carpetas del laboratorio y recorre la ruta en ambos sentidos.

```bash
mkdir -p ~/fdd/terminal-lab/notas/hoy
cd ~/fdd/terminal-lab
pwd
cd notas/hoy
pwd
cd ..
pwd
cd ~/fdd/terminal-lab/notas/hoy
pwd
```

`mkdir -p` crea todas las carpetas que falten en la ruta y no se queja si ya existen. `cd` cambia la carpeta actual. El atajo `~` representa tu carpeta personal; `cd ..` sube a la carpeta madre.

**Deberías ver:** las cuatro salidas de `pwd` terminan, en orden, en `terminal-lab`, `notas/hoy`, `notas` y `notas/hoy`.

**Pausa:** sin ejecutar otro comando, dibuja la cadena `fdd → terminal-lab → notas → hoy` y marca dónde quedaste. Si una salida no coincide, usa `pwd` antes de repetir el `cd` que corresponda.

## Misión 3: compara formas de nombrar un lugar

**Haz:** esta misión prepara su propio punto de partida. Crea la ruta si falta, entra en ella, muestra también las entradas ocultas y visita los mismos lugares con distintas clases de ruta.

```bash
mkdir -p ~/fdd/terminal-lab/notas/hoy
cd ~/fdd/terminal-lab/notas/hoy
ls -la
cd ~/fdd/terminal-lab
ls -la notas/hoy
ls -la "$HOME/fdd/terminal-lab/notas/hoy"
ls -la .
ls -la ..
cd ~/fdd/terminal-lab/notas/hoy
pwd
```

En `ls -la`, la opción `-l` muestra detalles y `-a` incluye nombres ocultos.

- Una **ruta absoluta** empieza en la raíz `/`, como `/home/ana/fdd`. La variable `$HOME` se expande a una ruta absoluta; las comillas conservan esa ruta como un solo argumento.
- Una **ruta relativa** empieza en la carpeta actual. Desde `terminal-lab`, `notas/hoy` llega a la carpeta que acabas de crear.
- `.` nombra la carpeta actual y `..` nombra su carpeta madre.
- `...` no es una ruta ni una sintaxis especial en Bash: es sólo un nombre literal y únicamente funcionará como ruta si existe una entrada llamada `...`. A diferencia de `.` y `..`, para subir dos niveles debes escribir `../..`.
- `~` es el atajo que la shell expande a tu carpeta personal antes de ejecutar el comando.

**Deberías ver:** los tres primeros listados de la misión muestran el mismo contenido de `notas/hoy`; como todavía está vacía, incluyen al menos `.` y `..`. `ls -la .` muestra el contenido de `terminal-lab`; `ls -la ..` muestra el de su carpeta madre, `fdd`. El último `pwd` termina en `fdd/terminal-lab/notas/hoy`.

**Pausa:** predice desde qué carpeta funcionarían `ls -la notas/hoy`, `ls -la .` y `ls -la ..`. Comprueba tu respuesta con `pwd`, no con el texto del *prompt*.

::: example {#entorno-correcto title="Tarjeta: abre el entorno correcto"}
- En **Ubuntu**, abre «Terminal»; normalmente ya estás en una shell Unix.
- En **WSL2**, abre tu distribución de Ubuntu, no el símbolo de sistema de Windows. Trabajas dentro de Linux, aunque tus archivos de Windows estén disponibles en `/mnt/c/`.
- En **macOS**, abre «Terminal»; su shell predeterminada suele ser zsh, pero Bash también está disponible.
:::

::: definition {#terminal-shell-bash title="Tarjeta: terminal, shell y Bash"}
La **terminal** muestra texto y recibe el teclado; la **shell** interpreta los comandos; **Bash** es una shell concreta. Puedes abrir una terminal que use otra shell y, aun así, ejecutar `bash` cuando lo necesites.

No copies a ciegas un *prompt*: el texto antes del cursor suele resumir usuario, equipo y carpeta. El signo final suele ser `$` para una cuenta normal y `#` para una cuenta con privilegios elevados.
:::

::: example {#primer-mapa-terminal title="Tarjeta: identifica tu sesión"}
Estas consultas tampoco modifican archivos:

```bash
whoami
pwd
uname -s
bash --version
```

`whoami` dice qué cuenta ejecuta el comando, `uname -s` identifica el sistema y `bash --version` pregunta por el programa Bash que se puede ejecutar.
:::

::: example {#historia-shell title="Tarjeta: el árbol familiar, en 30 segundos"}
Las terminales nacieron para conversar con computadoras a distancia y hoy siguen siendo una interfaz rápida, precisa y automatizable.

| Momento | Qué importa hoy |
|---|---|
| **Thompson shell** | Uno de los primeros intérpretes de órdenes de Unix, escrito por Ken Thompson. |
| **Bourne shell (`sh`)** | Stephen Bourne consolidó una sintaxis para uso interactivo y scripts; muchas shells posteriores conservan esa base. |
| **GNU Bash** | GNU necesitaba una shell libre compatible con `sh`. Bash significa *Bourne Again Shell*: un juego de palabras con Bourne y *born again*. |

Bash hereda ideas de esa familia, pero no todas las shells aceptan exactamente la misma sintaxis. La [introducción del manual de GNU Bash](https://www.gnu.org/software/bash/manual/html_node/What-is-Bash_003f.html) cuenta el parentesco completo.
:::

::: example {#atajos-terminal title="Tarjeta: ventanas, portapapeles y edición"}
Estos son valores comunes, no promesas globales: la aplicación de terminal, el escritorio y tus preferencias pueden cambiarlos. Si uno no responde, abre el menú de la aplicación y busca la acción por nombre.


| Entorno | Abrir | Nueva pestaña | Copiar / pegar |
|---|---|---|---|
| Ubuntu | `Ctrl-Alt-T` suele abrir Terminal; también puedes buscar «Terminal» en el lanzador. | `Ctrl-Shift-T` suele crearla. | Selecciona texto y usa `Ctrl-Shift-C` / `Ctrl-Shift-V`. |
| WSL2 | Abre Windows Terminal y elige el perfil de Ubuntu. | El botón `+` siempre queda visible; `Ctrl-Shift-T` es el valor común. | `Ctrl-Shift-C` / `Ctrl-Shift-V` son valores comunes de Windows Terminal. |
| macOS | `Cmd-Espacio`, escribe «Terminal» y pulsa Enter. | `Cmd-T`. | Selecciona texto y usa `Cmd-C` / `Cmd-V`. |

No confundas copiar con interrumpir: dentro de una terminal Unix, `Ctrl-C` suele detener el proceso actual. Por eso Linux y Windows Terminal agregan `Shift` al atajo de copiar.

| Atajo | Efecto |
|---|---|
| `Tab` | Completa un nombre de archivo o comando; presiónalo dos veces para ver opciones. |
| `↑` y `↓` | Recorren líneas que ya escribiste. |
| `Ctrl-A` / `Ctrl-E` | Van al inicio / final de la línea actual. |
| `Ctrl-L` | Limpia la vista sin borrar tu historial. |
| `Ctrl-C` | Interrumpe el programa que está en primer plano; no borra archivos. |
| `Ctrl-R` | Busca hacia atrás en el historial; escribe parte del comando y pulsa otra vez para seguir buscando. |
| `Ctrl-D` | Envía fin de entrada; con la línea vacía suele cerrar la shell actual. |

**Haz:** ejecuta `history`, pulsa `Ctrl-R` y busca `pwd`. **Comprueba:** la línea aparece sin ejecutarse; pulsa Enter sólo después de leerla. **Pausa:** en una segunda pestaña, usa `Ctrl-D` con la línea vacía y explica por qué se cerró esa shell, no toda la aplicación.
:::

::: problem {#prompt-como-pista title="Lee el prompt"}
Observa este prompt hipotético:

```text
ana@laptop:~/fdd/terminal-lab$
```

¿Qué datos puedes inferir antes de escribir un comando y qué carácter señala que la cuenta no está elevada?
:::

::: hint {of="prompt-como-pista"}
Separa el texto antes de `@`, el texto entre `@` y `:`, y la ruta antes del último carácter.
:::

::: answer {of="prompt-como-pista"}
La cuenta es `ana`, el equipo se llama `laptop` y la carpeta indicada es `~/fdd/terminal-lab`. El `$` final suele señalar una cuenta normal; no es parte de un comando.
:::

::: problem {#shell-no-es-version-bash title="Shell actual y Bash disponible"}
Predice qué clase de información entrega cada línea y explica por qué no tienen que producir el mismo nombre:

```bash
echo "$SHELL"
bash --version
```
:::

::: hint {of="shell-no-es-version-bash"}
Una variable de entorno describe la shell de inicio o configurada; la segunda línea consulta un ejecutable llamado `bash`.
:::

::: answer {of="shell-no-es-version-bash"}
`echo "$SHELL"` imprime la ruta de la shell de inicio o configurada para la sesión, por ejemplo `/bin/zsh`. No identifica de forma fiable la shell actual si después ejecutaste `bash` desde esa sesión. `bash --version` informa la versión de Bash disponible en el sistema. En macOS es común que la primera indique zsh y la segunda siga funcionando.
:::

## Cierre

Ya sabes mirar antes de actuar, cambiar de carpeta y distinguir varias maneras de nombrar una ruta. Tu laboratorio quedó en `~/fdd/terminal-lab/notas/hoy/`. Continúa con [[archivos-y-comandos|Archivos y comandos]].
