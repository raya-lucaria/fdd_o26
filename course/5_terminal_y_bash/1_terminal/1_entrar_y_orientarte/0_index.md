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

En una línea de historia: las terminales nacieron para conversar con computadoras a distancia y hoy siguen siendo una interfaz rápida, precisa y automatizable.

::: definition {#terminal-shell-bash title="Tres nombres, tres papeles"}
La **terminal** muestra texto y recibe el teclado; la **shell** interpreta los comandos; **Bash** es una shell concreta. Puedes abrir una terminal que use otra shell y, aun así, ejecutar `bash` cuando lo necesites.
:::

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

::: activity {#orientacion-laboratorio title="Comprueba tu punto de partida"}
En tu laboratorio, ejecuta `pwd` y `whoami`. Di en voz alta qué parte de la salida cambia si otra persona abre una sesión distinta y qué parte cambiaría si usaras `cd` para entrar a otra carpeta.
:::

## Atajos que usarás todos los días

| Atajo | Efecto |
|---|---|
| `Tab` | Completa un nombre de archivo o comando; presiónalo dos veces para ver opciones. |
| `↑` y `↓` | Recorren líneas que ya escribiste. |
| `Ctrl-A` / `Ctrl-E` | Van al inicio / final de la línea actual. |
| `Ctrl-L` | Limpia la vista sin borrar tu historial. |
| `Ctrl-C` | Interrumpe el programa que está en primer plano; no borra archivos. |

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
