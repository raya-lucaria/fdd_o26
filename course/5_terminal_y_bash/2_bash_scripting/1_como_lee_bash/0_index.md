---
id: como-lee-bash
title: "Cómo lee Bash"
nav_title: "Cómo lee Bash"
summary: "Anticipa cómo Bash separa, expande y conecta una línea antes de llamar a un programa."
status: ready
estimated_time: 15m
tags: [bash, shell, argumentos, globbing, seguridad]
prerequisites: [bash-scripting]
---

# Cómo lee Bash

Bash no entrega tu línea al programa tal como la tecleaste. Primero reconoce separadores, sustituye variables y construye argumentos; después llama al programa. Anticipar esas transformaciones evita sorpresas con rutas y nombres de archivos.

![Flujo vertical: una tecla llega a Bash, Bash expande la línea, un programa recibe los argumentos y produce stdout como salida normal o stderr como diagnóstico.](../../_assets/d-shell-flujo.svg)

**Lectura visual:** Bash no entrega una línea al programa sin cambios. Primero interpreta separadores y comillas, expande variables o patrones y después inicia el programa; por eso conviene predecir los argumentos antes de ejecutar una acción.

## Una shell ahora; un script después

Una **shell interactiva** espera una línea, la ejecuta y muestra otro prompt. Un **script** guarda varias líneas para que Bash las lea en orden. Los dos usan las reglas de Bash cuando ejecutas `bash`; no dependen de cuál sea la shell predeterminada de la terminal.

En macOS suele abrirse zsh; en Ubuntu y WSL2 puede abrirse Bash; Fish tiene otra sintaxis en varios puntos. Para que los ejemplos de estas estaciones signifiquen lo mismo, inicia Bash si tu prompt viene de otra shell:

```bash
bash
printf '%s\n' "Ahora esta sesión usa: $BASH_VERSION"
```

Para volver a la shell anterior, escribe `exit`. Más adelante, un archivo que empiece con `#!/usr/bin/env bash` declarará también que debe interpretarse con Bash.

::: definition {#linea-y-argumentos title="De caracteres a argumentos"}
Un **argumento** es una pieza de texto que Bash entrega a un programa. Por defecto, los espacios separan argumentos; las comillas pueden conservar espacios dentro de uno solo. Antes de invocar al programa, Bash también puede expandir variables y patrones de nombres.
:::

## Separa acciones según su resultado

Prueba estas líneas en un laboratorio recién preparado. `true` termina con éxito y `false` termina con error; sirven para observar el control sin modificar tus archivos.

```bash
mkdir -p "$HOME/fdd/terminal-lab/lectura-bash"
cd "$HOME/fdd/terminal-lab/lectura-bash"
printf '%s\n' 'primera; segunda'
printf '%s\n' 'primera' ; printf '%s\n' 'segunda'
true && printf '%s\n' 'esto ocurre porque true tuvo éxito'
false || printf '%s\n' 'esto ocurre porque false falló'
(cd /; pwd)
pwd
```

`;` separa dos órdenes que Bash intentará ejecutar una tras otra. `&&` ejecuta lo que sigue solo si la orden anterior tuvo éxito; `||`, solo si falló. Los paréntesis crean una **subshell**: el `cd /` dentro de ella cambia de carpeta solo para esa subshell. Por eso el último `pwd` sigue mostrando `~/fdd/terminal-lab/lectura-bash` (aunque la ruta completa de tu cuenta será distinta).

## Globbing: Bash busca nombres antes de llamar al programa

Un asterisco en una línea de Bash puede ser un patrón de nombres, llamado *globbing*. Prepara archivos, incluida una ruta con espacio, y mira los argumentos que recibe `printf`:

```bash
mkdir -p "$HOME/fdd/terminal-lab/lectura-bash"
cd "$HOME/fdd/terminal-lab/lectura-bash"
printf '%s\n' 'una línea' > 'nota de hoy.txt'
printf '%s\n' 'otra línea' > resumen.txt
printf '<%s>\n' -- *
```

La forma solicitada para inspeccionar la expansión es `printf '%s\n' -- *`; aquí se usan `<` y `>` para hacer visibles los límites. Verás primero `<-->`, porque `printf` recibe e imprime el argumento literal `--`, y después `<nota de hoy.txt>` y `<resumen.txt>` (en el orden de tu sistema). Aunque el primer nombre contiene un espacio, Bash lo entrega como un solo argumento: el patrón se expande después de que Bash separa la línea original. El programa recibe nombres ya expandidos; no decide qué significa `*`.

Si no hay coincidencias, Bash normalmente deja el `*` literal; zsh y Fish pueden tratar ese caso de otro modo. No uses un patrón como destino de una acción hasta haberlo inspeccionado y entendido. En las estaciones siguientes, las variables con rutas siempre irán entre comillas.

::: problem {#espacios-y-expansion title="¿Cuántos argumentos recibe printf?"}
Después de crear `nota de hoy.txt` y `resumen.txt`, predice qué argumentos recibe `printf` en esta línea y por qué el espacio no parte el primer nombre en dos:

```bash
printf '<%s>\n' -- *
```
:::

::: hint {of="espacios-y-expansion"}
Bash divide la línea que escribiste antes de reemplazar el patrón por nombres de archivos.
:::

::: answer {of="espacios-y-expansion"}
`printf` recibe el argumento literal `--` y un argumento por cada nombre que coincida con `*`, por lo que su primera línea es `<-->`. Uno de los argumentos siguientes es exactamente `nota de hoy.txt`, no dos argumentos. Bash hizo la expansión del patrón antes de iniciar `printf`; por eso el programa no ve un asterisco que tenga que interpretar.
:::

## Una comprobación antes de seguir

::: activity {#lee-una-linea title="Explica el orden"}
En `lectura-bash`, crea un archivo llamado `plan semanal.txt`. Ejecuta `printf '<%s>\n' -- *.txt` y señala qué parte de la línea interpreta Bash, cuál llega como formato a `printf` y cuáles son los argumentos producidos por el patrón. Si el resultado no enumera los nombres que esperabas, detente y revisa la carpeta con `pwd` y `printf '<%s>\n' -- *`.
:::

## Cierre

Ya puedes leer una línea en dos niveles: lo que Bash transforma y el programa que finalmente recibe argumentos. Continúa con [[variables-comillas-y-salida|Variables, comillas y salida]] para controlar de forma explícita esas transformaciones.
