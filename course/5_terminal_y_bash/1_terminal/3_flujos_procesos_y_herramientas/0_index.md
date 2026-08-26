---
id: flujos-procesos-y-herramientas
title: "Historial, tuberías y herramientas"
nav_title: "Historial y tuberías"
summary: "Recupera comandos, filtra texto y prepara las herramientas de tu terminal."
status: ready
estimated_time: 15m
tags: [terminal, history, pipes, procesos, stdout, stderr]
prerequisites: [archivos-y-comandos]
---

# Historial, tuberías y herramientas

Tu terminal ya recuerda lo que escribiste. En esta estación vas a **encontrar un comando anterior**, contar coincidencias y guardar el resultado.

## Misión 1: recupera un comando

`history` muestra comandos recientes de esta sesión. No modifica archivos.

::: example {#recupera-tu-historial title="Mira y recupera tu historial"}
**Haz:**

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas"
cd "$HOME/fdd/terminal-lab"
pwd
history
```

**Deberías ver:** el número y el texto de comandos recientes. La cantidad cambia en cada computadora.

**Pausa:** ¿reconoces el `pwd` que acabas de ejecutar?
:::

Para reutilizar sin teclear todo:

| Gesto | Resultado |
|---|---|
| ↑ / ↓ | Recorre comandos anteriores y posteriores. |
| `Ctrl-R` | Busca hacia atrás; escribe unas letras y pulsa `Enter`. |
| `Ctrl-C` | Cancela la búsqueda o el comando actual y devuelve el prompt. |

Revisa el comando recuperado **antes** de pulsar `Enter`: el historial también recuerda errores.

## Misión 2: encuentra sólo los `pwd`

`grep texto` conserva las líneas que contienen ese texto. El símbolo `|` conecta dos programas de izquierda a derecha.

::: example {#filtra-tu-historial title="Conecta history con grep"}
**Haz:** ejecuta primero `pwd` para producir una coincidencia propia y después filtra el historial.

```bash
pwd
history | grep pwd
```

**Deberías ver:** una o más líneas que incluyen `pwd`.

**Pausa:** ¿qué lado produce muchas líneas y qué lado decide cuáles pasan?
:::

Como el comando del filtro también contiene `pwd`, el resultado **puede incluir la propia línea del filtro**. No es otra ejecución de `pwd`; es texto guardado en el historial.

Lee `history | grep pwd` así:

```text
history  ──texto por stdout──>  |  ──texto por stdin──>  grep pwd
muchas líneas                                      sólo coincidencias
```

La tubería mueve **texto**, no archivos. `grep` no cambia el historial ni el directorio.

::: problem {#cambia-el-filtro title="Predice antes de filtrar"}
¿Qué esperarías si cambias `pwd` por `cd` en `history | grep pwd`?
:::

::: hint {of="cambia-el-filtro"}
Piensa qué texto busca el programa de la derecha.
:::

::: answer {of="cambia-el-filtro"}
`grep cd` conservaría las líneas del historial que contienen los caracteres `cd`. No ejecutaría esos comandos.
:::

## Misión 3: cuenta coincidencias

`wc -l` cuenta líneas. Puede recibir el texto de otra tubería.

::: example {#cuenta-tu-historial title="Agrega un tercer paso"}
**Haz:**

```bash
pwd
history | grep pwd | wc -l
```

**Deberías ver:** un número. Es el total de líneas que llegaron a `wc -l`, no el total de archivos.

**Pausa:** tapa el resultado y predice si crecerá después de ejecutar otro `pwd`.
:::

Cada `|` entrega la salida del programa izquierdo al siguiente. Puedes leer la línea completa como una frase: **recuerda, filtra, cuenta**.

## Misión 4: guarda una búsqueda

Ya conoces `>` y `>>`: aquí guardan el resultado final de la tubería.

::: example {#guarda-la-busqueda title="Crea una bitácora pequeña"}
**Haz — paso A:** reemplaza el reporte con una búsqueda nueva.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas" "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
pwd
history | grep pwd > reportes/comandos-pwd.txt
cat reportes/comandos-pwd.txt
```

**Deberías ver:** las coincidencias guardadas. `>` reemplaza el contenido anterior.

**Pausa:** ¿el archivo contiene el texto de `history` completo o sólo lo que dejó pasar `grep`?
:::

::: example {#anexa-la-busqueda title="Agrega y cuenta la bitácora"}
**Haz — paso B:** agrega otra búsqueda y cuenta las líneas.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
pwd
history | grep pwd >> reportes/comandos-pwd.txt
wc -l reportes/comandos-pwd.txt
```

**Deberías ver:** un conteo. `>>` agrega sin borrar lo anterior y también crearía el archivo si faltara.

**Pausa:** ¿por qué el segundo conteo puede ser mayor que el primero?
:::

## Sólo para reconocer después

No necesitas memorizar esta tarjeta hoy.

| Pieza | Idea mínima |
|---|---|
| **stdin** | Texto que recibe un programa. |
| **stdout** | Salida normal; `|`, `>` y `>>` trabajan con ella. |
| **stderr** | Diagnóstico; `2>` puede guardarlo por separado. |
| `$?` | Estado del comando anterior: `0` suele indicar éxito. |
| `tee` | Muestra texto y además guarda una copia. |
| `set -o pipefail` | Hace visible una falla en cualquier parte de una tubería. |

::: example {#prepara-salida-normal title="Opcional A: prepara una salida normal"}

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas" "$HOME/fdd/terminal-lab/reportes"
ls "$HOME/fdd/terminal-lab/notas" > "$HOME/fdd/terminal-lab/reportes/listado.txt" 2> "$HOME/fdd/terminal-lab/reportes/error.txt"
cat "$HOME/fdd/terminal-lab/reportes/listado.txt"
```

La carpeta `notas` existe, así que su listado viaja por stdout hacia `listado.txt`.
:::

::: example {#salida-y-error-separados title="Opcional: separa salida y diagnóstico"}

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas" "$HOME/fdd/terminal-lab/reportes"
ls "$HOME/fdd/terminal-lab/no-existe" > "$HOME/fdd/terminal-lab/reportes/listado-vacio.txt" 2> "$HOME/fdd/terminal-lab/reportes/error.txt"
estado=$?
cat "$HOME/fdd/terminal-lab/reportes/error.txt"
echo "$estado"
```

El segundo `ls` manda su diagnóstico a `error.txt`. El ejemplo guarda `$?` inmediatamente porque cualquier comando posterior lo reemplaza.
:::

::: example {#cuenta-y-registra-nombres title="Transforma una entrada preparada"}
Este bloque opcional crea su propia entrada y conserva el resultado de una tubería más larga.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
printf '%s\n' 'Ana' 'Beto' 'Ana' > "$HOME/fdd/terminal-lab/nombres.txt"
set -o pipefail
sort "$HOME/fdd/terminal-lab/nombres.txt" | uniq -c | tee "$HOME/fdd/terminal-lab/reportes/conteos.txt"
set +o pipefail
```

`sort` junta nombres iguales, `uniq -c` los cuenta y `tee` muestra y guarda. `pipefail` sólo permanece activo durante esta ampliación. Puedes volver al bloque cuando las cuatro misiones anteriores ya sean naturales.
:::

## Procesos: mirar y recuperar el prompt

`ps` toma una instantánea de procesos. `btop` ofrece una vista interactiva de CPU, memoria y procesos; sales con `q`. Si un programa en primer plano no termina, `Ctrl-C` solicita interrumpirlo: recupera el prompt, pero **no deshace** cambios ya realizados.

## Prepara Bash y dos herramientas

Primero comprueba; instala sólo lo que falte.

```bash
command -v bash
bash --version
echo "$SHELL"
```

`$SHELL` suele indicar tu shell de inicio. En macOS puede decir `zsh` aunque Bash esté disponible: no es un error.

| Plataforma | Ruta corta |
|---|---|
| Ubuntu | `sudo apt update` actualiza el catálogo; `apt search btop` permite revisar; `sudo apt install btop` instala. Prueba `apt search fastfetch` antes de instalarlo porque su disponibilidad depende de la versión. |
| WSL2 + Ubuntu | Usa la misma ruta dentro de Ubuntu. Los paquetes quedan en esa distribución WSL2. |
| macOS | Comprueba `command -v brew`. Si Homebrew ya funciona: `brew install btop fastfetch`. Para una versión reciente de Bash: `brew install bash`; compruébala sin cambiar todavía tu shell de inicio. |

`apt` está pensado para uso interactivo. `apt-get` es la interfaz tradicional y estable que aparece mucho en scripts y documentación; **no necesitas ejecutar ambos** para instalar el mismo paquete. `brew` es el gestor de paquetes de Homebrew en macOS y normalmente no se ejecuta con `sudo`.

Ejecuta `btop` para observar CPU y memoria; pulsa `q` para salir. `fastfetch` resume sistema, kernel, shell y hardware en una sola pantalla.

La práctica continúa en [OverTheWire Bandit](https://overthewire.org/wargames/bandit/). La entrega oficial pide preparar Bash/SSH y completar sólo **0→1, 1→2 y 2→3**.
