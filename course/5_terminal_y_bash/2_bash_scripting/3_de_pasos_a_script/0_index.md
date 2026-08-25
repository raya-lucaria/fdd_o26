---
id: de-pasos-a-script
title: "De pasos a script"
nav_title: "De pasos a script"
summary: "Escribe, ejecuta y depura un script Bash que valida una carpeta y deja un reporte."
status: ready
estimated_time: 15m
tags: [bash, scripts, argumentos, depuracion, seguridad]
prerequisites: [variables-comillas-y-salida]
---

# De pasos a script

Un script convierte una secuencia comprobable en un archivo que Bash puede volver a leer. Su entrada son los argumentos que le pasas; su salida debe decir qué produjo o por qué no pudo continuar.

## Dos maneras de ejecutar el mismo archivo

Guarda este primer script en el laboratorio. El bloque usa una construcción que copia literalmente las líneas entre `EOF`, así que no necesitas depender de un editor instalado.

```bash
mkdir -p "$HOME/fdd/terminal-lab"
cd "$HOME/fdd/terminal-lab"
cat > muestra-argumentos.sh <<'EOF'
#!/usr/bin/env bash
printf 'Primer argumento: %s\n' "$1"
printf 'Cada argumento recibido:\n'
printf '  <%s>\n' "$@"
EOF
bash muestra-argumentos.sh 'dos palabras' final
chmod +x muestra-argumentos.sh
./muestra-argumentos.sh 'dos palabras' final
```

`bash archivo.sh` pide explícitamente a Bash que lea el archivo. La primera línea, `#!/usr/bin/env bash`, se llama *shebang*: al ejecutar `./archivo.sh`, indica qué intérprete buscar. `chmod +x` añade permiso de ejecución y `./` aclara que el archivo está en la carpeta actual. Ambos métodos producen el mismo resultado para este script.

`$1` es el primer argumento y `"$@"` conserva cada argumento como una unidad. Por eso `dos palabras` se imprime entre un solo par de signos `<` y `>`; no se parte en dos.

## Lee texto y responde con `printf`

Cuando una persona debe introducir un valor, `read -r` lo lee sin tratar las barras invertidas como escapes. Este script no modifica archivos:

```bash
cd "$HOME/fdd/terminal-lab"
cat > saluda.sh <<'EOF'
#!/usr/bin/env bash
read -r -p 'Escribe tu nombre: ' nombre
printf 'Hola, %s.\n' "$nombre"
EOF
bash saluda.sh
```

Prueba con un nombre que contenga un espacio. `printf` conserva el valor entrecomillado y hace visible el salto de línea indicado por `\n`.

## Un script completo: inventario de textos

El siguiente script exige exactamente una carpeta existente. Si la recibe, busca solo archivos `.txt` directamente dentro de ella, cuenta sus líneas y reemplaza `reporte.txt` en esa misma carpeta. Los nombres y rutas se entrecomillan, y el reporte tiene un destino explícito.

```bash
cd "$HOME/fdd/terminal-lab"
cat > inventario.sh <<'EOF'
#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    printf 'Uso: %s DIRECTORIO_EXISTENTE\n' "${0##*/}" >&2
    exit 1
fi

if [[ -d "$1" ]]; then
    directorio=$(cd -- "$1" && pwd -P)
else
    printf 'Error: no existe el directorio: %s\n' "$1" >&2
    exit 1
fi

reporte="$directorio/reporte.txt"
find "$directorio" -type d ! -path "$directorio" -prune -o -type f -name '*.txt' ! -name 'reporte.txt' -exec wc -l {} + > "$reporte"

if [[ ! -s "$reporte" ]]; then
    printf '%s\n' 'No se encontraron archivos .txt directamente en el directorio.' > "$reporte"
fi

printf 'Reporte escrito: %s\n' "$reporte"
EOF
chmod +x inventario.sh
```

La prueba `if [[ -d "$1" ]]` comprueba que el primer argumento sea una carpeta antes de pedir trabajo a otras herramientas. En el caso de error, el mensaje va a stderr (`>&2`) y `exit 1` señala que no hubo éxito. `find` limita la búsqueda a esa carpeta: cuando encuentra una subcarpeta, `-prune` evita entrar en ella. `wc -l` escribe un conteo por cada `.txt`; el archivo `reporte.txt` queda excluido para que una ejecución posterior no se cuente a sí misma.

`find`, `wc` y Bash están disponibles en Ubuntu, WSL2 y macOS. El script evita opciones específicas de una sola plataforma y no necesita que el nombre de un archivo carezca de espacios.

## Caso correcto y caso de error

Cada bloque prepara sus propias entradas. Ejecuta primero el caso correcto y revisa el reporte; después prueba una ruta que no existe.

```bash
mkdir -p "$HOME/fdd/terminal-lab/inventario-prueba"
printf '%s\n' 'Ana' 'Beto' > "$HOME/fdd/terminal-lab/inventario-prueba/nombres.txt"
printf '%s\n' 'una' 'dos' 'tres' > "$HOME/fdd/terminal-lab/inventario-prueba/dos palabras.txt"
cd "$HOME/fdd/terminal-lab"
./inventario.sh "$HOME/fdd/terminal-lab/inventario-prueba"
cat "$HOME/fdd/terminal-lab/inventario-prueba/reporte.txt"
```

El reporte debe contener un conteo de `2` para `nombres.txt` y uno de `3` para `dos palabras.txt`; el orden puede variar. Vuelve a ejecutar el script: el reporte se reemplaza y sigue sin contarse a sí mismo.

```bash
cd "$HOME/fdd/terminal-lab"
./inventario.sh "$HOME/fdd/terminal-lab/carpeta-que-no-existe"
printf 'Estado de salida: %s\n' "$?"
```

Verás el mensaje de error y después `Estado de salida: 1`. No se crea un reporte para una carpeta inexistente.

::: problem {#argumento-requerido-por-inventario title="Detecta la entrada inválida"}
¿Qué ocurrirá si ejecutas `./inventario.sh` sin argumentos, y por qué es preferible a que el script intente buscar en una ubicación implícita?
:::

::: hint {of="argumento-requerido-por-inventario"}
Mira primero la condición que compara `$#` con `1`.
:::

::: answer {of="argumento-requerido-por-inventario"}
El script imprime una línea de uso en stderr y termina con `exit 1`. Exigir una carpeta explícita reduce el riesgo de producir un reporte en una ubicación distinta de la que la persona quiso analizar.
:::

## Depura sin adivinar

Si el resultado no coincide con tu predicción, pide a Bash que muestre cada línea expandida justo antes de ejecutarla:

```bash
cd "$HOME/fdd/terminal-lab"
bash -x inventario.sh "$HOME/fdd/terminal-lab/inventario-prueba"
```

La traza puede incluir rutas y argumentos, así que léela antes de compartirla. Busca dónde se asigna `directorio`, qué valor llega a `reporte` y qué orden se ejecuta después de cada `if`.

## Cierre

Ahora tienes un patrón pequeño y comprobable: validar la entrada, escribir una salida explícita y detenerse con un estado de error cuando no puede cumplir su tarea. Vuelve a [[bash-scripting|Bash scripting]] para repasar las tres estaciones.
