---
id: instalar-linux
title: "Instalar Linux"
nav_title: "Instalar Linux"
summary: "Guía para llegar a un Linux de verdad en tu propia máquina, investigando tu hardware en vez de seguir pasos ajenos."
status: ready
estimated_time: 12m
tags: [linux, instalacion, dual-boot, usb, wsl2, tarea]
prerequisites: [software-libre-y-sistemas-operativos]
---

# Instalar Linux

## En corto

- La meta de esta semana es **Linux corriendo de verdad en tu máquina**, arrancando desde tu propio disco.
- No te vamos a dar los pasos. Te vamos a enseñar a **averiguar los pasos para tu computadora**, que es lo único que sirve.
- El método es **auto-referencial**: primero le preguntas a tu computadora qué es, y con esa respuesta le preguntas al LLM y a Reddit cómo instalarle Linux.
- **Dual boot** significa que Windows sigue ahí. No borras nada. Eliges al prender.
- Necesitas **una USB de 8 GB o más** y un respaldo. Nada más.
- **Nadie se arrepiente.**

## Primero, lo que da miedo

Vas a leer, en algún foro, que instalar Linux borró el disco de alguien. Es cierto que puede pasar. También es cierto que pasa por una razón concreta y evitable: **la persona apretó «borrar disco e instalar» en vez de «instalar junto a Windows»**, y no tenía respaldo.

Así que el miedo tiene una forma útil y una inútil.

- **La forma útil**: hoy, antes de empezar, copia a la nube o a un disco externo lo que no puedes perder. Tesis, fotos, el proyecto de otra materia. Media hora.
- **La forma inútil**: no intentarlo. Vas a seguir sin poder correr la mitad del stack del semestre y vas a pelear con rutas de Windows durante cuatro meses.

> [!TIP]
> **El dual boot no reemplaza nada.** Le encoges espacio a Windows, Linux se instala en ese espacio, y al prender la computadora aparece un menú (GRUB) que te pregunta cuál quieres. Windows sigue completo, con tus archivos y tus programas, exactamente donde estaba.

## Por qué Linux de verdad y no un sucedáneo

WSL2 existe y funciona. Es un Linux que corre dentro de Windows y para muchas cosas alcanza. Pero conviene ser honestos sobre lo que se pierde.

| | Linux instalado | WSL2 | Nube (Codespaces) |
|---|---|---|---|
| Es el sistema que corre en producción | Sí | Casi — kernel real, entorno traducido | Sí |
| Hardware directo — GPU, USB, red, sensores | Sí | Parcial y con fricción | No |
| Funciona sin internet | Sí | Sí | No |
| Rendimiento de disco en tu proyecto | Nativo | Se desploma si el proyecto vive en `/mnt/c` | Depende del plan |
| Te enseña cómo funciona una computadora | Sí, a la fuerza | A medias | Casi nada |
| Se puede borrar por accidente | Sí, si te saltas el respaldo | No | No |

La última fila es la única a favor de WSL2, y se neutraliza con un respaldo.

Lo demás pesa del otro lado. **La razón de fondo es la de la unidad anterior**: la nube corre Linux, los contenedores que vas a construir corren sobre un núcleo Linux, y desarrollar sobre un sistema que se parece al de destino en vez de traducirse a él te ahorra una clase entera de bugs que sólo aparecen al desplegar.

Y hay una razón menos técnica pero igual de real: **instalar tu propio sistema operativo es la primera vez que la computadora deja de ser un electrodoméstico**. Después de esta semana vas a saber qué es una partición, qué es el firmware, qué es un gestor de arranque y qué es un sistema de archivos — no como definiciones de la unidad anterior sino porque los tocaste.

> [!NOTE]
> **Si tienes Mac, ya terminaste la parte difícil.** macOS es un Unix certificado: tienes terminal, tienes rutas POSIX, tienes casi todo. No instales nada raro. Ve directo a [[planes-b]], que tiene la media hora de configuración que sí te toca.

## El método: pregúntale a tu máquina, luego pregunta por tu máquina

Aquí está lo que separa esta guía de las mil que hay en internet. **Las guías genéricas fallan porque tu computadora no es genérica.** El wifi de un modelo necesita un driver que otro no; el firmware de una marca esconde la opción de arranque en otro menú; hay laptops con un chip de almacenamiento que Linux no ve hasta que cambias una opción en el BIOS.

Así que el procedimiento no es «sigue estos pasos». Es un bucle de tres movimientos que vas a repetir en cada parada de la guía:

1. **Pregúntale a tu computadora qué es.** Modelo exacto, versión de firmware, tarjeta de red. Hay comandos para eso, y hay una etiqueta abajo del equipo.
2. **Pregúntale al LLM con ese dato en la mano.** No «¿cómo instalo Linux?» sino «¿cómo instalo Linux en una Lenovo ThinkPad E14 Gen 4 con AMD Ryzen 5 5625U?». La diferencia entre esas dos preguntas es la diferencia entre una respuesta inútil y una respuesta que funciona.
3. **Verifica con humanos que ya lo hicieron.** Reddit, foros de la distribución, listas de hardware certificado. El LLM te da el mapa; los usuarios reales te dicen dónde está el bache.

::: definition {#def-autorreferencial title="El bucle auto-referencial"}
Usar la computadora para averiguar qué es la computadora, y usar esa respuesta para averiguar qué hacer con ella.

Suena tonto hasta que lo necesitas: **es la única forma de obtener instrucciones que apliquen a tu máquina y no al promedio de las máquinas**.
:::

Este bucle no se acaba con la instalación. Es exactamente cómo vas a resolver todo lo que se rompa después: la webcam, el sonido, la batería que dura menos de lo que debería. **Nada de eso es un fracaso de la instalación; es la lista de pendientes normal**, y se resuelve preguntando con el modelo exacto en la mano.

## Lo que necesitas antes de empezar

- **Una memoria USB de 8 GB o más.** Se va a borrar por completo. Saca lo que tenga.
- **Un respaldo de lo que no puedes perder.** Nube, disco externo, lo que sea. No es opcional.
- **Al menos 60 GB libres** en el disco para la partición de Linux.
- **Dos horas sin prisa**, con la computadora conectada a la corriente.
- **Un segundo dispositivo** —celular o tablet— para leer la guía y preguntarle al LLM mientras la computadora está reiniciando.

> [!WARNING]
> **No empieces esto media hora antes de una entrega.** Si algo sale raro, y a una de cada cuatro personas le sale algo raro, vas a necesitar tiempo para resolverlo con calma. Hazlo el fin de semana.

## Las cinco paradas

| Parada | Qué haces | Cuánto toma |
|---|---|---|
| 1. [[conoce-tu-maquina]] | Averiguas el modelo exacto y qué hay adentro | 15 min |
| 2. [[elige-tu-distribucion]] | Investigas qué distribución le queda y qué problemas reporta la gente | 30 min |
| 3. [[la-usb-de-instalacion]] | Descargas la imagen, la verificas y grabas la USB | 30 min |
| 4. [[dual-boot]] | Haces espacio, entras al firmware, instalas junto a Windows | 60 min |
| 5. [[primer-arranque]] | Actualizas, arreglas lo que falte, dejas la máquina lista | 45 min |

Si en algún punto te bloqueas: [[planes-b]] tiene WSL2 y la opción de nube, para que **nunca dejes de poder hacer la tarea del curso** mientras resuelves la instalación.

## La tarea

La entrega de esta sesión es exactamente esto: **tener un Linux funcionando antes de la clase del martes 25 de agosto**. La definición completa, con la evidencia que hay que subir a Canvas, está en el objeto de tarea de esta unidad.

## Qué te llevas

- **El dual boot no borra Windows.** Le encoge el espacio y agrega un menú al arrancar.
- **Los pasos genéricos fallan; los pasos con tu modelo exacto funcionan.** Esa es toda la técnica.
- **Los problemas post-instalación son la norma, no la señal de que fallaste**, y se resuelven con el mismo bucle.
- **Nadie que haya hecho esto se arrepiente.** Empieza por [[conoce-tu-maquina]].
