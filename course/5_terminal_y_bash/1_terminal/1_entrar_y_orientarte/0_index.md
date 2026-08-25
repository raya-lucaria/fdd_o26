---
id: entrar-y-orientarte
title: "Entrar y orientarte"
nav_title: "Orientarte"
summary: "Abre una terminal, identifica tu entorno y prepara un laboratorio local."
status: ready
estimated_time: 15m
tags: [terminal, shell, bash, ubuntu, wsl2, macos]
prerequisites: [terminal-directa]
---

# Entrar y orientarte

Una terminal es una ventana de texto para dar instrucciones al sistema. La *shell* lee la línea que escribes, la interpreta y ejecuta programas; Bash es una shell frecuente.

Las terminales nacieron para conversar con computadoras a distancia y hoy siguen siendo una interfaz rápida, precisa y automatizable.

::: definition {#terminal-shell-bash title="Tres nombres, tres papeles"}
La **terminal** muestra texto y recibe el teclado; la **shell** interpreta los comandos; **Bash** es una shell concreta. Puedes abrir una terminal que use otra shell y, aun así, ejecutar `bash` cuando lo necesites.
:::

## El árbol familiar, en 30 segundos

| Momento | Qué importa hoy |
|---|---|
| **Thompson shell** | Uno de los primeros intérpretes de órdenes de Unix, escrito por Ken Thompson. |
| **Bourne shell (`sh`)** | Stephen Bourne consolidó una sintaxis para uso interactivo y scripts; muchas shells posteriores conservan esa base. |
| **GNU Bash** | GNU necesitaba una shell libre compatible con `sh`. Bash significa *Bourne Again Shell*: un juego de palabras con Bourne y *born again*. |

Bash hereda ideas de esa familia, pero no todas las shells aceptan exactamente la misma sintaxis. La [introducción del manual de GNU Bash](https://www.gnu.org/software/bash/manual/html_node/What-is-Bash_003f.html) cuenta el parentesco completo.

## Abre el entorno correcto

- En **Ubuntu**, abre «Terminal»; normalmente ya estás en una shell Unix.
- En **WSL2**, abre tu distribución de Ubuntu, no el símbolo de sistema de Windows. Trabajas dentro de Linux, aunque tus archivos de Windows estén disponibles en `/mnt/c/`.
- En **macOS**, abre «Terminal»; su shell predeterminada suele ser zsh, pero Bash también está disponible.

No copies a ciegas un prompt: el texto antes del cursor es información sobre el usuario, equipo y carpeta. El signo final suele ser `$` para una cuenta normal y `#` para una cuenta con privilegios elevados.

::: example {#primer-mapa-terminal title="Identifica tu sesión"}
Ejecuta estas consultas; ninguna modifica archivos.

```bash
whoami
pwd
uname -s
bash --version
```

`whoami` dice qué cuenta ejecuta el comando, `pwd` imprime la carpeta actual y `uname -s` identifica el sistema. `bash --version` pregunta por el programa Bash que se puede ejecutar.
:::

## Tu laboratorio local

No necesitas haber visitado otra estación. Crea una carpeta de práctica y entra en ella:

```bash
mkdir -p "$HOME/fdd/terminal-lab"
cd "$HOME/fdd/terminal-lab"
pwd
```

`$HOME` representa tu carpeta personal; las comillas protegen la ruta si contiene espacios. A partir de aquí, los ejemplos de esta estación pueden repetirse sin afectar archivos fuera de `~/fdd/terminal-lab`.

::: example {#orientacion-laboratorio title="Comprueba tu punto de partida"}
En tu laboratorio, ejecuta `pwd` y `whoami`. Di en voz alta qué parte de la salida cambia si otra persona abre una sesión distinta y qué parte cambiaría si usaras `cd` para entrar a otra carpeta.
:::

## Ventanas, pestañas y portapapeles

Estos son valores comunes, no promesas globales: la aplicación de terminal, el escritorio y tus preferencias pueden cambiarlos. Si uno no responde, abre el menú de la aplicación y busca la acción por nombre.

| Entorno | Abrir | Nueva pestaña | Copiar / pegar |
|---|---|---|---|
| Ubuntu | `Ctrl-Alt-T` suele abrir Terminal; también puedes buscar «Terminal» en el lanzador. | `Ctrl-Shift-T` suele crearla. | Selecciona texto y usa `Ctrl-Shift-C` / `Ctrl-Shift-V`. |
| WSL2 | Abre Windows Terminal y elige el perfil de Ubuntu. | El botón `+` siempre queda visible; `Ctrl-Shift-T` es el valor común. | `Ctrl-Shift-C` / `Ctrl-Shift-V` son valores comunes de Windows Terminal. |
| macOS | `Cmd-Espacio`, escribe «Terminal» y pulsa Enter. | `Cmd-T`. | Selecciona texto y usa `Cmd-C` / `Cmd-V`. |

No confundas copiar con interrumpir: dentro de una terminal Unix, `Ctrl-C` suele detener el proceso actual. Por eso Linux y Windows Terminal agregan `Shift` al atajo de copiar.

## Atajos dentro de la línea

| Atajo | Efecto |
|---|---|
| `Tab` | Completa un nombre de archivo o comando; presiónalo dos veces para ver opciones. |
| `↑` y `↓` | Recorren líneas que ya escribiste. |
| `Ctrl-A` / `Ctrl-E` | Van al inicio / final de la línea actual. |
| `Ctrl-L` | Limpia la vista sin borrar tu historial. |
| `Ctrl-C` | Interrumpe el programa que está en primer plano; no borra archivos. |
| `Ctrl-R` | Busca hacia atrás en el historial; escribe parte del comando y pulsa otra vez para seguir buscando. |
| `Ctrl-D` | Envía fin de entrada; con la línea vacía suele cerrar la shell actual. |

::: example {#atajos-sin-riesgo title="Haz, comprueba, pausa"}
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

Ya tienes un lugar seguro para practicar y cuatro preguntas de orientación: quién eres, dónde estás, qué sistema usas y qué Bash está disponible. Continúa con [[archivos-y-comandos|Archivos y comandos]].
