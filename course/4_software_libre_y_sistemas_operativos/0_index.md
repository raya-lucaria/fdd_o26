---
id: software-libre-y-sistemas-operativos
title: "Software libre y sistemas operativos"
nav_title: "Software libre y SO"
summary: "Por qué casi todo el stack de datos corre sobre software que alguien regaló, y qué es realmente un sistema operativo."
status: ready
estimated_time: 22m
tags: [software-libre, fsf, gnu, linux, licencias, sistemas-operativos]
prerequisites: [arquitectura-de-computadoras]
---

# Software libre y sistemas operativos

## En corto

- El stack que vas a usar todo el semestre —la terminal, Python, Git, Docker, Postgres— es **software que alguien decidió regalar**, y eso no fue un accidente.
- El software libre no se define por el precio sino por **cuatro libertades**; el *copyleft* es la maña legal que las vuelve permanentes.
- Un sistema operativo es el **intermediario** entre tus programas y el hardware de la unidad anterior.
- **GNU tenía todo menos el núcleo. Linux era un núcleo sin sistema.** Se encontraron en 1991 y de ahí sale casi toda la nube.
- Elegir sistema operativo **no es una preferencia estética**: decide qué puedes instalar, cómo se llaman tus rutas y qué tan parecida es tu máquina a la máquina donde el código va a correr de verdad.

## Todo lo que instalas es de alguien

Detente en la unidad pasada un segundo. Ya sabes qué hace una CPU, dónde vive un dato y cuánto cuesta moverlo. Falta la capa que nadie menciona porque parece agua: **el software que reparte esa máquina entre programas que no se conocen entre sí**.

Y hay un hecho raro sobre esa capa. Cuando levantas un contenedor de Postgres, cuando escribes `ls`, cuando `pip` resuelve dependencias, cuando un notebook importa NumPy: nada de eso lo pagaste, nada de eso lo licenciaste y en casi todos los casos puedes leer su código fuente completo. **La infraestructura sobre la que se construyó la industria de los datos es, en su mayoría, regalada.** Vale la pena entender por qué, porque las razones no son las que parecen.

## 1985: el software libre como imperativo moral

Richard Stallman funda la **Free Software Foundation** en 1985. No es una asociación de programadores generosos: es una posición ética. Stallman lo dice sin rodeos.

> «Podría haber ganado dinero de esta manera, y quizás me hubiera divertido escribiendo código. Pero sabía que al final de mi carrera, miraría hacia atrás a años de construir muros para dividir a las personas, y sentiría que había pasado mi vida empeorando el mundo.»
>
> — Richard Stallman

::: definition {#def-software-libre title="Software libre — las cuatro libertades"}
Un programa es **libre** si su licencia te concede cuatro cosas:

0. **Usarlo** para cualquier propósito.
1. **Estudiarlo** —lo que exige acceso al código fuente— y modificarlo.
2. **Compartirlo**, redistribuyendo copias.
3. **Mejorarlo** y publicar tus mejoras.

Nótese lo que *no* aparece en la lista: el precio. *Free* es libre, no gratis.
:::

La libertad 1 es la que arrastra a las demás. Si no puedes leer el código, no puedes modificarlo; si no puedes modificarlo, las otras tres son decorativas. Por eso «tener el código fuente» no es un detalle técnico del arreglo: es su condición de existencia.

## Copyleft: la trampa legal que sostiene todo

Aquí está el problema práctico. Si liberas tu código sin más, cualquiera puede tomarlo, mejorarlo, cerrarlo y vender el resultado. La versión buena del programa deja de ser libre y tu regalo terminó financiando un muro.

::: definition {#def-copyleft title="Copyleft"}
Es la cláusula de **herencia**: quien distribuya una obra derivada está obligado a distribuirla bajo la misma licencia.

Usa el derecho de autor en contra de su propósito habitual. En vez de reservar derechos, los impone hacia adelante.
:::

La **GPL** es la implementación canónica de esa idea. No pide confianza: pide una condición contractual que se propaga sola. Es la diferencia entre pedir que el software siga siendo libre y **hacer que no pueda dejar de serlo**.

## Software libre y open source no son sinónimos

Se usan como si lo fueran y describen posiciones distintas sobre el mismo código.

| | Software libre (FSF) | Open source |
|---|---|---|
| **Argumento** | Ético: el usuario merece control sobre lo que corre en su máquina | Práctico: el código abierto produce mejor software |
| **Licencias típicas** | Copyleft fuerte — GPL, AGPL | Permisivas — MIT, Apache, BSD |
| **Componentes propietarios** | Los rechaza | Los acepta si conviene |
| **Ejemplos** | GNU, `gcc`, Bash, LibreOffice, Firefox, VLC | Python, Android, Git, Docker, VS Code, PostgreSQL |

Fíjate en la fila de ejemplos, porque es la que te toca. **Casi todo tu stack de datos vive en la columna derecha.** El movimiento que lo hizo posible está en la izquierda; la licencia bajo la que lo usas, casi nunca.

## El mapa de licencias que vas a firmar sin leer

Cada dependencia que instalas trae una. Vale la pena distinguirlas por lo que te obligan a hacer, no por su nombre.

| Licencia | Qué exige | Cuándo aparece |
|---|---|---|
| **MIT** | Conservar el aviso de copyright. Nada más. | Librerías que quieren adopción máxima, incluso dentro de software cerrado |
| **Apache 2.0** | Como MIT, más una concesión expresa de patentes que se revoca si demandas | Proyectos corporativos grandes (Android) |
| **GPL** | Si distribuyes una obra derivada, **todo** el proyecto va bajo GPL | El núcleo de Linux, `gcc`, Bash |
| **AGPL** | Como GPL, pero **interactuar por red cuenta como distribuir** | Software que corre como servicio y no quiere ser cerrado por SaaS |
| **MPL** | Copyleft archivo por archivo; puedes mezclar con código propietario | Punto medio (Firefox) |
| **Creative Commons** | No es para software: obras creativas, en módulos BY / NC / ND / SA | Datasets, documentación, imágenes |

> [!WARNING]
> El agujero de la GPL clásica es que **la obligación se dispara al distribuir el ejecutable**. Si tu servicio corre en tu servidor y el usuario sólo lo consume por HTTP, nunca distribuiste nada y nunca debiste el código. La **AGPL** existe exactamente para tapar ese hueco, y por eso aparece cada vez más en bases de datos y herramientas de datos.

## Qué es realmente un sistema operativo

::: definition {#def-so title="Sistema operativo"}
El software que se interpone entre tus programas y el hardware: **administra memoria y almacenamiento, reparte la CPU, controla los periféricos y expone un sistema de archivos**.

Ningún programa que escribas habla con el disco. Le pide al sistema operativo que hable con el disco.
:::

Esa mediación es la razón por la que el mismo Python te da resultados distintos en dos máquinas: no cambió el lenguaje, cambió quién atiende sus llamadas.

## Unix, GNU, Linux: tres nombres para una sola historia

**Unix** (años setenta) fija las ideas que todo lo demás heredó: todo es un archivo, programas pequeños que se encadenan, un sistema de archivos jerárquico. macOS, Android y Linux descienden de ese diseño; Windows lo tomó prestado a medias.

**GNU** —«GNU is Not Unix», un chiste recursivo— es el proyecto de Stallman para construir un sistema operativo completo, compatible con Unix, sin una sola línea de software propietario. Para 1991 tenía casi todo:

| Pieza de GNU | Qué es | Dónde la vas a encontrar |
|---|---|---|
| `gcc` | Compilador de C, C++ y Fortran | Debajo de casi todo lo que instalas compilado |
| **Bash** | El intérprete de comandos por defecto | La terminal del resto del curso |
| **GRUB** | Gestor de arranque | La pantalla que elige entre Windows y Linux en un dual boot |
| **coreutils** | `ls`, `cp`, `mv`, `rm`, `cat`… | Cada comando que teclees |

Le faltaba una sola pieza: **el núcleo**. Y en 1991 un estudiante finlandés publicó un núcleo que no tenía sistema alrededor. GNU tenía todo menos el núcleo; **Linux** era un núcleo sin todo lo demás. La combinación es el sistema operativo que hoy corre casi todos los servidores del mundo, y la razón por la que hay gente que insiste en llamarlo *GNU/Linux*.

Una **distribución** es un empaquetado concreto de ese conjunto: núcleo, utilerías GNU, gestor de paquetes, escritorio y decisiones por defecto. Ubuntu, Debian, Fedora, Arch, Mint y Red Hat son distribuciones distintas del mismo material.

## Sistemas de archivos: dónde esto se vuelve tu problema

::: definition {#def-fs title="Sistema de archivos"}
La forma en que un dispositivo organiza los datos: dónde se coloca cada archivo, cómo se registra su ubicación y cómo se recupera después.

Es una capa de **traducción entre bytes en un disco y nombres que un humano puede escribir**.
:::

| Sistema | De quién es | Lo que conviene saber |
|---|---|---|
| **NTFS** | Windows | Maneja particiones muy grandes; Linux lo lee sin drama |
| **APFS** | macOS | Copia en escritura, clonación, cifrado fuerte |
| **ext4** | Linux | Registro por diario para sobrevivir a cortes de luz; el default sensato |
| **FAT32 / exFAT** | Todos | El terreno neutral. FAT32 **no puede guardar archivos de más de 4 GB** |

Tres consecuencias que te van a pegar esta semana:

- **Linux lee todo.** Desde Linux vas a poder abrir tu partición de Windows; al revés es incómodo y necesita herramientas extra.
- **Si quieres una partición compartida entre dos sistemas, va en exFAT** (o FAT32, con el límite de 4 GB encima).
- **Tu USB de instalación se va a formatear**, y el formato lo elige la herramienta que la grabe. Todo lo que tenga adentro se pierde.

## Por qué esto no es historia

Si esta unidad fuera sólo genealogía, no ocuparía una sesión. Ocupa una porque tres decisiones prácticas salen de aquí:

1. **La nube es Linux.** Los contenedores que vas a construir corren sobre un núcleo Linux. Desarrollar en Windows nativo significa desarrollar en un sistema que no se parece al de destino, y descubrirlo en producción.
2. **Las rutas, los permisos y la terminal son parte del contrato.** `/home/tu-usuario` no es una preferencia; es donde el resto del curso asume que estás parado.
3. **La licencia de una dependencia es una decisión de arquitectura.** Meter una librería AGPL en un servicio propietario no es un descuido de legal: puede obligarte a publicar tu código.

## La ruta

| Parada | Qué encontrarás |
|---|---|
| [[presentacion-fsf-os]] | El deck de 41 diapositivas del que sale esta unidad |
| [[instalar-linux]] | La guía larga: cómo conseguir un Linux de verdad en tu máquina |

## Qué te llevas

- **Libre no significa gratis**: significa usar, estudiar, compartir y mejorar.
- **El copyleft es lo que impide que un bien común se privatice**; la GPL lo hace exigible y la AGPL cierra el hueco de la nube.
- **Software libre y open source coinciden en el código y discrepan en el porqué.** Tu stack es open source; la infraestructura que lo hizo posible es libre.
- **El sistema operativo es el intermediario**, y GNU/Linux es la combinación que terminó siendo el estándar de la infraestructura.
- **La tarea de esta sesión es tener Linux funcionando** antes del martes. Sigue a [[instalar-linux]].
