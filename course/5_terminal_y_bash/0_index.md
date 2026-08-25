---
id: terminal-y-bash
title: "Terminal y Bash"
nav_title: "Terminal y Bash"
summary: "Seis estaciones para usar la shell con cuidado y convertir pasos repetidos en un script pequeño."
status: ready
estimated_time: 12m
tags: [terminal, bash, shell, linux, wsl2, macos]
prerequisites: [software-libre-y-sistemas-operativos]
---

# Terminal y Bash

## En corto

- La terminal es una forma directa de pedirle trabajo a tu computadora: lees el comando antes de ejecutarlo.
- Vas a practicar en `~/fdd/terminal-lab`, una carpeta local y desechable: **no es un repositorio**.
- Primero trabajas con comandos; después haces que Bash repita pasos claros por ti.

## Mapa de la unidad

**Progreso: 1–6 estaciones.** Recorre las estaciones en orden: cada una deja una acción pequeña que usarás en la siguiente.

| Bloque | Estaciones | Para qué sirve |
|---|---|---|
| [[terminal-directa|Terminal: uso directo]] | 1. [[entrar-y-orientarte|Entrar y orientarte]] · 2. [[archivos-y-comandos|Archivos y comandos]] · 3. [[flujos-procesos-y-herramientas|Flujos, procesos y herramientas]] | Ubicarte, cuidar archivos y conectar programas. |
| [[bash-scripting|Bash scripting]] | 4. [[como-lee-bash|Cómo lee Bash]] · 5. [[variables-comillas-y-salida|Variables, comillas y salida]] · 6. [[de-pasos-a-script|De pasos a script]] | Entender una línea de shell y automatizar un reporte pequeño. |

La carpeta `~/fdd/terminal-lab` es tu laboratorio: puedes crear, mover y borrar ahí sin tocar tu proyecto de clase. No inicialices Git ni conviertas esta práctica en un repositorio.

## Antes de empezar

Necesitas una terminal Unix: Ubuntu, Ubuntu dentro de WSL2 o macOS. Si vienes de la unidad anterior, ya tienes el contexto de Linux; ahora toca usarlo con intención.

## Qué te llevas

- Sabes dónde estás, qué hace un comando y cómo pedir ayuda antes de cambiar archivos.
- Puedes seguir el recorrido de texto, errores y salida entre programas.
- Puedes leer y ejecutar un script Bash breve sin depender de un repositorio.
