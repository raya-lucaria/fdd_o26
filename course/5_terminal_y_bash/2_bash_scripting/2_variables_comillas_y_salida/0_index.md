---
id: variables-comillas-y-salida
title: "Variables, comillas y salida"
nav_title: "Variables y salida"
summary: "Guarda texto, protege argumentos y separa la salida normal de los diagnósticos."
status: ready
estimated_time: 15m
tags: [bash, variables, comillas, stdout, stderr, seguridad]
prerequisites: [como-lee-bash]
---

# Variables, comillas y salida

Una variable guarda texto para reutilizarlo; las comillas indican qué transformaciones puede hacer Bash sobre ese texto. La combinación más frecuente para una ruta es `"$variable"`: expande su valor y lo conserva como un solo argumento.

## Asigna sin espacios y expande con precisión

En Bash la asignación no lleva espacios alrededor de `=`. El bloque siguiente prepara todo lo que usa y muestra una variable, su valor junto a otros caracteres, la carpeta personal, una variable de entorno y dos expansiones útiles.

```bash
mkdir -p "$HOME/fdd/terminal-lab/variables-bash"
cd "$HOME/fdd/terminal-lab/variables-bash"
archivo='notas de clase.txt'
n=3
printf '%s\n' 'tres líneas' > "$archivo"
printf 'Archivo: %s\n' "$archivo"
printf 'Nombre construido: %s\n' "x${n}z"
printf 'Tu carpeta personal: %s\n' "$HOME"
printf 'Ruta de programas: %s\n' "$PATH"
carpeta="$(pwd)"
total=$((n + 2))
printf 'Carpeta: %s; total: %s\n' "$carpeta" "$total"
printf '%s\n' informe-{lunes,martes}.txt
```

`$archivo` y `${archivo}` nombran el valor de la variable. Las llaves hacen claro dónde termina el nombre: en `x${n}z`, Bash busca la variable `n` y deja las letras `x` y `z` fuera. `$(pwd)` sustituye la salida de un comando y `$((n + 2))` calcula una expresión aritmética. `{lunes,martes}` no lee archivos: es una expansión de llaves de Bash que genera dos textos antes de ejecutar `printf`.

`$HOME` y `$PATH` son variables de entorno: la primera suele nombrar tu carpeta personal y la segunda una lista de carpetas donde la shell busca programas. Imprímelas para comprenderlas; no las reasignes en esta práctica.

## Tres formas de citar texto

| Forma | Qué conserva o expande | Uso seguro típico |
|---|---|---|
| Sin comillas: `$archivo` | Bash puede dividir el valor en varios argumentos y expandir patrones. | Solo texto controlado que no sea una ruta. |
| Comillas simples: `'$HOME'` | Conservan cada carácter; no expanden variables ni comandos. | Texto literal. |
| Comillas dobles: `"$archivo"` | Expanden variables y `$(...)`, pero conservan espacios como parte de un argumento. | Rutas y texto guardado en variables. |

::: example {#cuatro-predicciones-de-expansion title="Predice antes de ejecutar"}
En una terminal Bash, anota primero el resultado o los argumentos que esperas. Luego crea las variables indicadas y ejecuta cada bloque.

```bash
archivo='nota de hoy.txt'
printf '<%s>\n' $archivo
printf '<%s>\n' "$archivo"
```

```bash
echo '$HOME'
echo "$HOME"
echo $HOME
```

```bash
n=7
printf '<%s>\n' "x${n}z"
printf '<%s>\n' "x$n z"
```

```bash
echo "$(pwd)"
(cd /; pwd); pwd
```
:::

::: answer {of="cuatro-predicciones-de-expansion"}
Sin comillas, `$archivo` se divide por el espacio y `printf` recibe `nota`, `de` y `hoy.txt`; con `"$archivo"` recibe un solo argumento, `nota de hoy.txt`. `echo '$HOME'` imprime los caracteres `$HOME`; `echo "$HOME"` expande la variable y mantiene su valor como un argumento; `echo $HOME` también intenta expandirla, pero deja que Bash divida el resultado y expanda patrones, por lo que no es la forma segura de pasar una ruta.

Con `n=7`, `x${n}z` produce `x7z`. En `x$n z`, el espacio acaba el primer argumento: `$n` se une a `x` y produce `x7`; `z` es otro argumento. `echo "$(pwd)"` imprime la carpeta actual sin cambiarla. `(cd /; pwd); pwd` imprime primero `/` desde una subshell y luego la carpeta original desde la shell que continuó intacta.
:::

Aunque `echo` sirve para explorar, `printf` es más predecible para scripts: puedes elegir el formato y siempre entrecomillar los valores que inserta.

## Salida normal y diagnósticos

Los programas suelen escribir resultados en **stdout** y avisos o errores en **stderr**. Puedes guardar cada flujo por separado; prepara los archivos antes de consultarlos:

```bash
mkdir -p "$HOME/fdd/terminal-lab/variables-bash"
cd "$HOME/fdd/terminal-lab/variables-bash"
printf '%s\n' 'contenido correcto' > entrada.txt
cat entrada.txt > salida.txt
ls inexistente > salida-error.txt 2> diagnostico.txt
printf '%s\n' '--- salida normal ---'
cat salida.txt
printf '%s\n' '--- diagnóstico ---'
cat diagnostico.txt
```

`>` guarda stdout y `2>` guarda stderr. Aquí `salida-error.txt` queda vacío porque `ls` no pudo listar el nombre; el diagnóstico se conserva en `diagnostico.txt`. Revisa ambos archivos antes de concluir que un programa terminó como esperabas.

::: problem {#ruta-con-espacios title="Protege una ruta"}
La variable `archivo` vale `nota de hoy.txt`. ¿Qué versión debes usar para pedir a `cat` que lea un solo archivo y por qué?

```bash
cat $archivo
cat "$archivo"
```
:::

::: hint {of="ruta-con-espacios"}
Cuenta los argumentos que tendría `cat` después de que Bash expanda la variable.
:::

::: answer {of="ruta-con-espacios"}
Usa `cat "$archivo"`. Las comillas dobles expanden la variable pero conservan sus espacios dentro de un solo argumento. Sin ellas, Bash puede entregar tres nombres distintos a `cat`.
:::

## Cierre

Ya puedes decidir cuándo expandir un valor y cuándo preservarlo. En la siguiente estación convertirás estas decisiones en un script que recibe una carpeta y deja un reporte verificable.
