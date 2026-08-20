---
id: elige-tu-distribucion
title: "Parada 2 — Elige tu distribución"
nav_title: "2. Elige distribución"
summary: "Cómo escoger distribución a partir de tu hardware y de lo que reportan usuarios reales, en vez de a partir de una lista de opiniones."
status: ready
estimated_time: 12m
tags: [distribuciones, ubuntu, fedora, mint, reddit, investigacion]
prerequisites: [conoce-tu-maquina]
---

# Parada 2 — Elige tu distribución

## En corto

- Todas las distribuciones son **el mismo Linux**. Cambia el empaquetado, no el sistema.
- Para este curso, cualquiera de las tres primeras de la tabla funciona. **No optimices esta decisión.**
- Lo que sí hay que investigar no es «cuál es mejor» sino **qué le pasa a la gente con tu modelo exacto**.
- Reddit vale porque publica los fracasos. Las guías oficiales sólo publican los éxitos.

## Todas son el mismo Linux

Vale la pena repetirlo porque la cantidad de opciones paraliza. El núcleo es el mismo. Las utilerías GNU son las mismas. Bash es Bash. Python es Python. Lo que cambia entre distribuciones es:

- **El gestor de paquetes** — `apt`, `dnf`, `pacman`: cómo instalas cosas.
- **El ciclo de versiones** — estable y viejo, o nuevo y con filo.
- **El escritorio por defecto** — GNOME, KDE, Cinnamon: cómo se ve.
- **Cuánto software propietario incluyen de fábrica** — drivers, códecs, firmware.

Ese último punto es el que importa para ti esta semana. Una distribución que incluye drivers propietarios te ahorra la pelea con la NVIDIA y con el Realtek.

## Las candidatas razonables

| Distribución | Base | Para quién | El detalle |
|---|---|---|---|
| **Ubuntu LTS** | Debian | El default sensato | Cada guía de internet asume Ubuntu. Cuando busques un error, vas a encontrar la respuesta |
| **Linux Mint** | Ubuntu | Quien viene de Windows | Escritorio familiar, drivers y códecs de fábrica, muy poca fricción |
| **Fedora Workstation** | Propia | Quien quiere lo nuevo | Software más reciente, buen soporte de hardware moderno; `dnf` en vez de `apt` |
| **Pop!_OS** | Ubuntu | Laptops con NVIDIA | Trae una imagen con los drivers NVIDIA ya incluidos |
| **Debian estable** | — | Servidores | Viejo a propósito. Excelente decisión para un servidor, incómoda para una laptop nueva |
| **Arch** | — | Todavía no | Es una gran manera de aprender y una pésima manera de tener la tarea lista el martes |

> [!TIP]
> **Si no quieres pensarlo: Ubuntu LTS.** Si tu equipo trae NVIDIA: Pop!_OS. Si vienes de Windows y quieres que se sienta parecido: Mint. Las tres te dejan hacer el curso completo. **La distribución no es la parte importante de esta tarea.**

::: definition {#def-lts title="LTS — Long Term Support"}
Una versión con soporte extendido, típicamente cinco años, que recibe parches de seguridad pero no cambios grandes.

Para una máquina de trabajo es lo que quieres: **no quieres que tu sistema operativo sea interesante**.
:::

## La investigación que sí importa

Elegida la candidata, viene la parte que no se puede saltar: **averiguar qué le pasa a la gente que tiene tu modelo**.

### Por qué Reddit y no la documentación oficial

La documentación oficial describe el camino feliz. Está bien escrita, es correcta y no menciona que en tu modelo hay que desactivar una opción del firmware o el instalador no ve el disco. **Nadie documenta oficialmente los baches de un modelo específico**, porque no hay nadie cuyo trabajo sea hacerlo.

Los usuarios sí. Alguien con tu misma laptop ya se topó con el problema, ya lo peleó y ya escribió el hilo. Búscalo.

### Dónde buscar

- **`r/linuxquestions`, `r/linux4noobs`, `r/Ubuntu`, `r/linuxmint`, `r/Fedora`** — los subreddits de la distribución y de principiantes.
- **`r/<marca>`** — hay subreddits por fabricante (`r/thinkpad`, `r/Dell`, `r/HPLaptops`) llenos de gente instalando Linux.
- **Los foros de la distribución** — `askubuntu.com`, el foro de Linux Mint, `discussion.fedoraproject.org`.
- **La base de datos de hardware certificado** de Ubuntu, para ver si tu modelo está probado oficialmente.
- **La Arch Wiki** — aunque no vayas a usar Arch. Es la mejor documentación de hardware que existe en Linux y aplica casi entera a cualquier distribución.

### Cómo buscar

Búsquedas literales, con el modelo pegado tal cual:

```text
"ThinkPad E14 Gen 4" Ubuntu install reddit
"HP Pavilion 15-eh1021la" linux wifi not working
"Realtek RTL8821CE" ubuntu driver
site:reddit.com Lenovo IdeaPad 3 15ITL6 dual boot
```

Lee **cinco hilos, no uno**. Uno te dice qué le pasó a una persona; cinco te dicen si es un patrón. Y lee los comentarios, no sólo el post: la solución casi nunca está en la pregunta.

> [!NOTE]
> **Vas a encontrar hilos de gente furiosa.** Es normal: quien tuvo una instalación sin problemas no escribe un post sobre eso. Estás leyendo una muestra sesgada hacia lo que falla — que es exactamente lo que necesitas, siempre que no confundas «esto puede fallar» con «esto va a fallar».

### El prompt de investigación

> **Prompt:**
> «Estoy considerando instalar `[distribución y versión]` en dual boot en una `[modelo exacto]` con `[gráficos]` y `[wifi]`.
>
> 1. Resume los problemas que reportan usuarios reales con este modelo o con modelos de la misma familia, y di de cuándo son —un problema de 2019 puede estar resuelto hace años.
> 2. ¿Cuáles de esos problemas se arreglan solos con una versión reciente del kernel y cuáles requieren intervención manual?
> 3. ¿Hay alguna distribución que resuelva de fábrica los problemas específicos de este hardware?
> 4. Dame los términos de búsqueda exactos que debería usar en Reddit y en foros para verificar esto por mi cuenta.»

La pregunta 4 cierra el bucle. **No delegues la verificación**: pídele al modelo las búsquedas y hazlas tú. Vas a encontrar cosas que él no sabía, y vas a aprender a buscarlas sola la próxima vez.

## Cuándo cambiar de candidata

Cambia de distribución si la investigación te dice una de estas tres cosas, y sólo si te dice una de estas tres cosas:

1. **Tu tarjeta de red no funciona sin driver propietario** → una distribución que los incluya (Mint, Pop!_OS, Ubuntu marcando «instalar software de terceros»).
2. **Tu hardware es muy nuevo** —procesador o gráficos de este año— y los hilos hablan de kernel demasiado viejo → Fedora o una Ubuntu no-LTS.
3. **Tienes NVIDIA dedicada** y los hilos están llenos de pantallas negras → Pop!_OS.

Cualquier otra razón —«leí que es más rápida», «se ve mejor»— **no es razón esta semana**. Instala, termina la tarea, y experimenta después con calma.

## Qué te llevas

- **La distribución importa mucho menos de lo que sugiere la cantidad de opciones.**
- **Ubuntu LTS es la respuesta por defecto** porque maximiza la probabilidad de que tu error ya esté respondido en internet.
- **Reddit publica los fracasos; la documentación oficial, los éxitos.** Necesitas los dos.
- **Lee cinco hilos y fíjate en la fecha.** Un problema de hace seis años probablemente ya no existe.
- Con la distribución elegida, sigue a [[la-usb-de-instalacion]].
