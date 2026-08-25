---
id: bash-scripting
title: "Bash scripting"
nav_title: "Bash scripting"
summary: "Tres estaciones para leer cómo Bash prepara una línea y escribir un script pequeño y comprobable."
status: ready
estimated_time: 45m
tags: [bash, shell, scripting, linux, wsl2, macos]
prerequisites: [terminal-directa]
---

# Bash scripting

![Escritorio nocturno en tonos azul y verde: una terminal, una hoja de script y una carpeta de reportes aparecen conectadas por flechas luminosas; la mitad izquierda queda oscura y despejada.](../_assets/hero-bash-original.png)

## Meta

Entender cómo Bash transforma una línea antes de ejecutarla y convertir pasos repetidos en un script breve que recibe una ruta y produce un reporte.

## Las tres estaciones

| Estación | Tiempo | Terminas cuando… |
|---|---:|---|
| 4. [[como-lee-bash|Cómo lee Bash]] | 15 min | puedes anticipar cómo Bash separa y expande los argumentos. |
| 5. [[variables-comillas-y-salida|Variables, comillas y salida]] | 15 min | eliges comillas y variables sin perder rutas ni texto. |
| 6. [[de-pasos-a-script|De pasos a script]] | 15 min | ejecutas y depuras un script que valida una carpeta y escribe un reporte. |

El script vive en `~/fdd/terminal-lab`, tu espacio local de práctica; no necesita un repositorio.

## Del comando a sus salidas

![Flujo vertical: una tecla llega a Bash, Bash expande la línea, un programa recibe los argumentos y produce stdout como salida normal o stderr como diagnóstico.](../_assets/d-shell-flujo.svg)

**Lectura visual:** Bash no entrega una línea al programa sin cambios. Primero interpreta separadores y comillas, expande variables o patrones y después inicia el programa; por eso conviene predecir los argumentos antes de ejecutar una acción.
