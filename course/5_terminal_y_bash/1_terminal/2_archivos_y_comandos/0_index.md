---
id: archivos-y-comandos
title: "Archivos y comandos"
nav_title: "Archivos y comandos"
summary: "Nombra rutas, pide ayuda y modifica archivos de práctica con vista previa."
status: ready
estimated_time: 15m
tags: [terminal, archivos, rutas, comandos, seguridad]
prerequisites: [entrar-y-orientarte]
---

# Archivos y comandos

Esta estación vuelve a preparar sus propios archivos, así que puedes iniciarla directamente. Todo ocurre dentro de `~/fdd/terminal-lab`.

## El árbol y las rutas

Las carpetas forman un árbol: `/` es la raíz; cada carpeta puede contener archivos y otras carpetas. Una ruta absoluta empieza en `/`, como `/home/ana/fdd/terminal-lab`; una ruta relativa parte de donde estás. `.` significa «esta carpeta» y `..`, «la carpeta contenedora».

Los nombres que empiezan con punto, como `.config`, son archivos ocultos por convención. Para verlos usa `ls -a`; para ver detalles, `ls -la`.

::: definition {#forma-de-comando title="La forma de una orden"}
Muchos comandos siguen la forma `command [options] [arguments]`: el comando indica la acción, las opciones cambian cómo actúa y los argumentos nombran sus datos o destinos. Los corchetes solo muestran partes opcionales; no se escriben.
:::

::: example {#prepara-y-muestra-archivos title="Crea antes de leer"}
Este bloque crea todos los archivos de práctica antes de listarlos o leerlos.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' 'Beto' 'Ana' > nombres.txt
printf '%s\n' 'faltó una columna' 'archivo no encontrado' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
ls -la
cat nombres.txt
cat 'dos palabras.txt'
```

Las comillas conservan `dos palabras.txt` como un solo argumento.
:::

## Opciones y ayuda

Una opción corta suele empezar con un guion (`-l`); una larga, con dos (`--all`); y algunas reciben valor (`--color=auto`). El marcador `--` termina las opciones: es útil si un archivo empieza con guion.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' 'Beto' > nombres.txt
printf '%s\n' 'falló una prueba' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
printf '%s\n' 'archivo que empieza con guion' > -- -borrador.txt
ls -l -- -borrador.txt
```

Primero pregunta antes de adivinar: `man ls` abre el manual (sales con `q`) en las tres plataformas. En Ubuntu y WSL2, `ls --help` también muestra ayuda breve; en macOS usa `man ls` como ruta de ayuda para ese comando. `type -a cd` revela si un nombre es parte de la shell, una función o un programa; `command -v ls` muestra qué se ejecutaría al escribir `ls`.

::: activity {#consulta-ayuda-comando title="Pregunta antes de cambiar"}
Ejecuta `type -a cd`, `command -v ls` y `man ls`. Si usas Ubuntu o WSL2, añade `ls --help`. Escribe una diferencia entre una orden integrada a la shell y un programa encontrado en una ruta del sistema.
:::

## Crear, copiar, mover y revisar

::: example {#archivos-sin-suposiciones title="Opera sobre un laboratorio recién creado"}
Cada archivo que se lee aquí acaba de crearse en el mismo bloque.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' 'Beto' 'Ana' > nombres.txt
printf '%s\n' 'faltó una columna' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
cp nombres.txt reportes/nombres-copia.txt
mv errores.txt reportes/errores.txt
wc -l nombres.txt reportes/errores.txt
cat reportes/nombres-copia.txt
```
:::

`mkdir` crea carpetas; `cp` copia; `mv` mueve o renombra; `cat` muestra contenido breve; `wc -l` cuenta líneas. Lee la línea completa antes de pulsar Enter: cambiar el orden de origen y destino cambia el resultado.

## Borrar es una decisión, no un atajo

Dentro del laboratorio, primero lista exactamente lo que coincide y luego actúa solo sobre un nombre explícito:

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' > nombres.txt
printf '%s\n' 'falló una prueba' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
mkdir -p reportes/vacio reportes/para-revisar
printf '%s\n' -- *
rm -i -- 'dos palabras.txt'
printf '%s\n' -- reportes/*
rmdir -- reportes/vacio
printf '%s\n' -- reportes/*
rm -r -- reportes/para-revisar
```

La primera vista previa `printf '%s\n' -- *` te deja revisar los nombres antes de que `rm -i` pida confirmación para un único archivo. Las dos vistas previas `printf '%s\n' -- reportes/*` listan el contenido real de `reportes` antes de cada borrado de carpeta. `rmdir` solo borra carpetas vacías; `rm -r` borra el contenido de la carpeta indicada, por lo que aquí se limita a una carpeta recién creada dentro de `~/fdd/terminal-lab`. `--` trata lo que sigue como nombre, incluso si comenzara con un guion. Detente si la lista no coincide con tu intención: nunca combines borrado recursivo con la opción de forzar, ni uses borrados masivos o comandos cuyo alcance no puedas explicar.

::: problem {#ruta-relativa-o-absoluta title="Ubica el archivo"}
Estás en `~/fdd/terminal-lab` y quieres leer el archivo `errores.txt` que está dentro de `reportes`. Escribe una ruta relativa y una ruta que use `$HOME` para nombrarlo.
:::

::: hint {of="ruta-relativa-o-absoluta"}
La ruta relativa empieza desde la carpeta actual. La otra empieza en tu carpeta personal, no en el texto literal `~` dentro de comillas.
:::

::: answer {of="ruta-relativa-o-absoluta"}
La ruta relativa es `reportes/errores.txt`. Una ruta basada en la carpeta personal es `"$HOME/fdd/terminal-lab/reportes/errores.txt"`; las comillas mantienen la ruta como un argumento.
:::

::: problem {#doble-guion-protege-nombres title="Desactiva las opciones"}
Existe un archivo llamado `-borrador.txt`. ¿Por qué `ls -l -- -borrador.txt` es más claro que `ls -l -borrador.txt`?
:::

::: hint {of="doble-guion-protege-nombres"}
Piensa en cómo suele interpretar un programa los argumentos que comienzan con `-`.
:::

::: answer {of="doble-guion-protege-nombres"}
Sin `--`, el programa puede interpretar `-borrador.txt` como una combinación de opciones. `--` indica que las opciones terminaron y que el texto siguiente es un nombre de archivo.
:::

Continúa con [[flujos-procesos-y-herramientas|Flujos, procesos y herramientas]].
