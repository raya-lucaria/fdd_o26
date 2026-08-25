---
id: terminal-directa
title: "Terminal: uso directo"
nav_title: "Terminal"
summary: "Tres estaciones para orientarte, trabajar con archivos y conectar herramientas desde la shell."
status: ready
estimated_time: 45m
tags: [terminal, shell, comandos, linux, wsl2, macos]
prerequisites: [terminal-y-bash]
---

# Terminal: uso directo

![Escritorio nocturno en tonos azul y verde con una persona anónima vista de espaldas frente a una terminal retro; la mitad izquierda queda oscura y despejada.](../_assets/hero-terminal-original.png)

## Meta

Usar una terminal para explorar y modificar con cuidado un laboratorio local, entendiendo qué entra, qué sale y qué puede fallar.

## Las tres estaciones

| Estación | Tiempo | Terminas cuando… |
|---|---:|---|
| 1. [[entrar-y-orientarte|Entrar y orientarte]] | 15 min | abres tu entorno y sabes en qué carpeta estás. |
| 2. [[archivos-y-comandos|Archivos y comandos]] | 15 min | puedes crear, revisar, mover y borrar con cuidado dentro del laboratorio. |
| 3. [[flujos-procesos-y-herramientas|Flujos, procesos y herramientas]] | 15 min | conectas la salida de un programa con otro y reconoces un error. |

Trabaja siempre en `~/fdd/terminal-lab`: es una carpeta local de práctica, no un repositorio.

## Ritmo de trabajo

| Paso | Qué haces |
|---|---|
| **Haz** | Ejecuta un bloque corto dentro del laboratorio. |
| **Comprueba** | Mira `pwd`, la salida y los nombres antes de continuar. |
| **Pausa** | Predice la siguiente salida; si no coincide, explica la diferencia. |

No memorices una enciclopedia. Este es el kit que conviene reconocer y consultar:

| Necesidad | Comandos |
|---|---|
| Orientarte | `pwd`, `ls`, `cd` |
| Crear y modificar | `mkdir`, `touch`, `cp`, `mv`, `rm`, `rmdir` |
| Leer y buscar | `cat`, `less`, `head`, `tail`, `grep`, `wc` |
| Revisar tu sesión | `history`, `clear`, `date`, `ps` |
| Pedir ayuda | `man`, `type`, `command -v` |

Cuatro lecturas rápidas: `touch archivo.txt` crea un archivo vacío si no existe; `less archivo.txt` pagina texto y sale con `q`; `head` y `tail` muestran el inicio y el final; `grep patron archivo.txt` conserva las líneas que coinciden. `clear` sólo limpia la vista: `history` confirma que el historial sigue ahí.

`htop` vuelve interactiva la vista de procesos; `fastfetch` resume el equipo y el sistema. Son opcionales. Si quieres usarlos, instala sólo dentro del entorno donde trabajas:

| Plataforma | Comando |
|---|---|
| Ubuntu 25.04 o posterior | `sudo apt update` y después `sudo apt install htop fastfetch` |
| WSL2 con Ubuntu 25.04 o posterior | Los mismos comandos; afectan esa distribución de WSL2. |
| macOS con Homebrew | `brew install htop fastfetch` |

En una versión anterior de Ubuntu, `fastfetch` puede no estar en `apt`. Conserva `htop` y consulta la [instalación oficial de Fastfetch](https://github.com/fastfetch-cli/fastfetch#installation); no pegues instaladores de fuentes desconocidas.
