---
id: archivos-y-comandos
title: "Archivos y comandos"
nav_title: "Archivos y comandos"
summary: "Crea una nota, léela y practica cambios seguros dentro del laboratorio."
status: ready
estimated_time: 20m
tags: [terminal, archivos, comandos, seguridad]
prerequisites: [entrar-y-orientarte]
---

# Archivos y comandos

Vas a construir una lista real y a cuidarla. Cada bloque prepara lo que necesita dentro de `~/fdd/terminal-lab`; puedes empezar aquí aunque hayas cerrado la terminal anterior.

## Misión 1: crea una nota

`touch` crea un archivo vacío si no existe; si ya existe, no borra su contenido. `echo` produce una línea de texto y `>` envía esa salida al archivo: si ya tenía contenido, lo reemplaza.

**Haz:** prepara la carpeta, ubícate y escribe la primera tarea.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
pwd
touch lista.txt
echo "practicar rutas" > lista.txt
```

**Deberías ver:** `pwd` termina en `fdd/terminal-lab/notas/hoy`. `touch` y `echo` no imprimen nada cuando funcionan; la salida de `echo` quedó en `lista.txt`.

**Pausa:** antes de leerlo, predice qué pasaría con la primera línea si ejecutaras `echo "otra tarea" > lista.txt`.

## Misión 2: anexa y lee

`>>` agrega la salida al final sin borrar lo anterior. `cat` muestra completo un archivo breve.

**Haz:** este bloque también crea la carpeta y la primera línea, así que funciona por sí solo.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
echo "practicar rutas" > lista.txt
echo "leer la ayuda" >> lista.txt
cat lista.txt
```

**Deberías ver:** dos líneas, en el mismo orden en que las escribiste.

**Pausa:** explica en una frase la diferencia entre `>` y `>>`. Si no puedes hacerlo, no avances: repite el bloque cambiando sólo la segunda tarea.

## Misión 3: mira los extremos

Para texto largo, `head` muestra el inicio y `tail`, el final. La opción `-n 1` les entrega el argumento `1`: cuántas líneas mostrar.

**Haz:** prepara tres líneas y observa extremos distintos.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
echo "primera" > lista.txt
echo "segunda" >> lista.txt
echo "tercera" >> lista.txt
head -n 1 lista.txt
tail -n 1 lista.txt
```

**Deberías ver:** `primera` y después `tercera`.

**Pausa:** predice la salida de `head -n 2 lista.txt`; luego compruébala.

## Misión 4: descubre un archivo oculto

Un nombre que comienza con `.`, como `.secreto`, queda fuera del listado simple por convención. **Oculto no significa cifrado ni protegido.**

**Haz:** crea uno y compara los listados.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
touch .secreto
ls
ls -la
```

**Deberías ver:** el primer `ls` no muestra `.secreto`; `ls -la` sí lo muestra, junto con `.` y `..`.

**Pausa:** ¿un archivo oculto protege una contraseña? Responde antes de seguir.

## Opciones y ayuda

La forma habitual es `comando [opciones] [argumentos]`. No escribas los corchetes: sólo indican partes que pueden variar.

`printf` es una alternativa precisa para producir varias líneas con un formato repetible:

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
printf '%s\n' 'archivo que empieza con guion' > ./-borrador.txt
ls -l -- -borrador.txt
```

| Pieza | Ejemplo | Lectura |
|---|---|---|
| Opción corta | `ls -l` | `-l` cambia la forma del listado. |
| Opciones cortas juntas | `ls -la` | Equivale a usar `-l` y `-a`. |
| Opción con argumento | `head -n 2 lista.txt` | `-n` consume `2`; el archivo sigue después. |
| Fin de opciones | `ls -- -borrador.txt` | Después de `--`, el nombre ya no se interpreta como opción. |

**Haz:** abre la documentación de `ls` con `man ls`; desplázate y pulsa `q` para salir. En Ubuntu o WSL2 también prueba `ls --help`. En macOS, usa `man ls`: su versión de `ls` no ofrece la misma opción larga.

**Deberías ver:** una descripción y una lista de opciones. No supongas que `-h` siempre significa ayuda: en `ls -h` cambia el formato de los tamaños. Revisa `man` o `--help` para cada comando.

**Pausa:** en `head -n 2 lista.txt`, identifica comando, opción, argumento de la opción y archivo.

## Misión 5: copia y renombra

`cp -i` copia y pregunta antes de reemplazar un destino existente. `mv -i` mueve o renombra con el mismo freno.

**Haz:** crea una fuente, cópiala y renombra la copia.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy"
cd "$HOME/fdd/terminal-lab/notas/hoy"
printf '%s\n' "practicar rutas" "leer la ayuda" > lista.txt
cp -i -- lista.txt lista-copia.txt
mv -i -- lista-copia.txt lista-renombrada.txt
ls -l -- lista*.txt
```

**Deberías ver:** `lista.txt` y `lista-renombrada.txt`, ambos con contenido. Si repetiste el bloque, `-i` puede preguntar antes de reemplazar: lee el destino antes de responder.

**Pausa:** ¿cuál archivo es la fuente que conservó su nombre? Confírmalo con `cat`, no con una suposición.

`cp` copia un archivo; para copiar una carpeta completa necesita una opción recursiva que todavía no usaremos. `mv` puede renombrar archivos o carpetas. En ambos casos, primero va el origen y luego el destino.

## Misión 6: borra sólo lo que nombraste

`rm -i` elimina un archivo después de pedir confirmación. `rmdir` elimina exclusivamente una carpeta vacía. No son lo mismo.

**Haz:** crea dos objetivos desechables, verifica sus nombres y elimina uno de cada tipo.

```bash
mkdir -p "$HOME/fdd/terminal-lab/notas/hoy/caja-vacia"
cd "$HOME/fdd/terminal-lab/notas/hoy"
echo "desechable" > borrar-este.txt
ls -ld -- borrar-este.txt caja-vacia
rm -i -- borrar-este.txt
rmdir -- caja-vacia
ls -la
```

**Deberías ver:** `rm -i` pregunta por `borrar-este.txt`; confirma sólo si el nombre coincide. `rmdir` termina sin salida porque `caja-vacia` no contiene nada. El listado final conserva `lista.txt` y `.secreto` si hiciste las misiones anteriores.

**Pausa:** si `rmdir` dice que la carpeta no está vacía, detente y usa `ls -la caja-vacia`. No cambies a una orden más agresiva.

## Mapa de bolsillo

| Quiero… | Comando | Freno mental |
|---|---|---|
| Crear un archivo vacío | `touch nombre.txt` | Confirma primero con `pwd`. |
| Reemplazar texto | `echo "texto" > nombre.txt` | `>` borra el contenido anterior. |
| Anexar texto | `echo "texto" >> nombre.txt` | `>>` conserva y agrega. |
| Leer | `cat`, `head`, `tail` | Empieza con archivos breves. |
| Copiar / renombrar | `cp -i`, `mv -i` | Lee origen y destino en ese orden. |
| Borrar archivo / carpeta vacía | `rm -i`, `rmdir` | Un nombre explícito dentro del laboratorio. |

Continúa con [[flujos-procesos-y-herramientas|Flujos, procesos y herramientas]].
