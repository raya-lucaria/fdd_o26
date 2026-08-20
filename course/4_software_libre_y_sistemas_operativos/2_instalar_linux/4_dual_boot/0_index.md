---
id: dual-boot
title: "Parada 4 — Dual boot"
nav_title: "4. Dual boot"
summary: "Hacer espacio sin borrar Windows, ajustar el firmware, y qué botón del instalador es el correcto y cuál es el peligroso."
status: ready
estimated_time: 14m
tags: [dual-boot, particiones, uefi, secure-boot, grub, instalacion]
prerequisites: [la-usb-de-instalacion]
---

# Parada 4 — Dual boot

## En corto

- Encoges la partición de Windows **desde Windows**, no desde el instalador de Linux.
- Entras al firmware a desactivar **Fast Startup** —esto es obligatorio— y quizá **Secure Boot**.
- En el instalador eliges **«Instalar junto a Windows Boot Manager»**. Nunca «Borrar disco».
- Al terminar aparece **GRUB**: un menú al prender que te deja elegir sistema.
- Windows sigue completo. Sólo tiene menos espacio libre.

## Qué es realmente un dual boot

::: definition {#def-dual-boot title="Dual boot"}
Dos sistemas operativos instalados en particiones distintas del mismo disco, con un gestor de arranque que pregunta cuál iniciar.

**No corren al mismo tiempo.** Eliges uno al prender; para cambiar, reinicias.
:::

Tu disco es un espacio continuo dividido en **particiones**: tramos que el sistema trata como discos independientes. Windows ocupa hoy casi todo. Lo que vas a hacer es encogerlo para abrir un tramo vacío, e instalar Linux ahí. Los archivos de Windows no se mueven ni se tocan: **sólo dejan de tener tanto espacio libre por delante**.

## Antes de tocar nada

1. **El respaldo.** Ya lo mencionamos dos veces. Es la tercera y última.
2. **Batería y corriente.** Un corte de luz en mitad del particionado es la única forma realista de perder datos aquí.
3. **La clave de BitLocker.** Si tu Windows tiene cifrado de disco —común en equipos de trabajo y en muchas laptops nuevas—, ve a tu cuenta de Microsoft, **descarga la clave de recuperación y guárdala en otro lado**. Cambiar el arranque puede hacer que Windows la pida en el siguiente inicio, y sin ella no entras.
4. **Anota cuánto espacio libre tienes.** Necesitas dejar al menos 60 GB para Linux y no bajar de 30 GB libres en Windows.

> [!WARNING]
> **BitLocker es la causa número uno de sustos evitables.** No es que borre nada: es que Windows detecta un cambio en el arranque y pide una clave que nunca supiste que existía. Descárgala ahora, antes de continuar.

## Paso 1 — Encoge Windows desde Windows

Hazlo con la herramienta de Windows, no con la de Linux. Windows entiende su propio sistema de archivos mejor que nadie y puede mover sus estructuras internas con seguridad.

Busca **«Crear y formatear particiones del disco duro»** en el menú de inicio. Ahí:

1. Clic derecho en la partición grande de Windows (`C:`).
2. **«Reducir volumen»**.
3. Escribe cuánto quieres liberar, **en megabytes**: 60 GB son `61440`.
4. Aplica. Queda un bloque marcado como **«No asignado»**.

Ese espacio no asignado es la casa de Linux. **Déjalo así**: no lo formatees, no le asignes letra. El instalador de Linux lo va a encontrar y usar.

> [!NOTE]
> Windows a veces se niega a reducir tanto como quieres, aunque haya espacio libre. La causa son archivos inamovibles al final del disco. Pregunta:
>
> «Windows sólo me deja reducir `C:` hasta `[X] GB` aunque tengo `[Y] GB` libres. ¿Qué archivos inamovibles causan esto y cómo desactivo temporalmente la hibernación, el archivo de paginación y la protección del sistema para poder reducir más? Dime también cómo volver a activarlos después.»

## Paso 2 — El firmware

Reinicia y entra a la configuración de firmware (la tecla que averiguaste en la parada 1). Busca tres cosas.

| Opción | Qué hacer | Por qué |
|---|---|---|
| **Fast Startup / Inicio rápido** | **Desactivar** — está en Windows, en «Opciones de energía», no siempre en el firmware | Windows no se apaga del todo; deja el sistema de archivos marcado como en uso y Linux se niega a montarlo o lo corrompe |
| **Secure Boot** | Desactivar **si** el instalador no arranca | Ubuntu y Fedora lo soportan y suelen funcionar con él activo. Es lo primero que se desactiva si algo falla |
| **SATA mode / Intel RST / RAID** | Cambiar a **AHCI** si el instalador no ve tu disco | Con RAID/RST activo, Linux no encuentra el SSD. **Investiga antes de cambiarlo**: en algunos equipos Windows deja de arrancar si se cambia sin preparación |

> [!WARNING]
> **La tercera fila es la única que puede dejarte sin arrancar Windows.** Si tu instalador no ve el disco y crees que necesitas cambiar a AHCI, para y pregunta primero cómo preparar Windows para ese cambio en tu modelo específico. Hay un procedimiento (arrancar Windows en modo seguro una vez) y saltárselo es lo que rompe cosas.

**Fast Startup no es opcional.** Es la causa de la mitad de los «Linux no ve mis archivos de Windows» y de una buena parte de las corrupciones de partición compartida. Desactívalo.

## Paso 3 — Instala

Arranca desde la USB otra vez y ahora sí elige **«Instalar»**.

Cuando llegue la pantalla de tipo de instalación, esta es **la única decisión peligrosa de toda la guía**:

| Opción | Qué hace |
|---|---|
| **«Instalar junto a Windows Boot Manager»** | ← **Esta.** Usa el espacio no asignado y deja Windows intacto |
| «Borrar disco e instalar» | **Borra todo.** Windows, tus archivos, todo |
| «Algo más» / «Manual» | Particionado a mano. Control total y responsabilidad total |

> [!WARNING]
> **Si no aparece «Instalar junto a Windows», detente.** No improvises con «Borrar disco» ni con el modo manual. Que no aparezca significa algo concreto —Fast Startup sigue activo, el disco es GPT y arrancaste en modo heredado, o el instalador no reconoce la instalación de Windows— y cada causa tiene su arreglo. Pregunta:
>
> «Estoy instalando `[distribución]` en dual boot en una `[modelo]`. El instalador **no** muestra la opción "Instalar junto a Windows Boot Manager", sólo `[lista lo que sí ves]`. Windows está en `[GPT o MBR]` y arranqué la USB en modo `[UEFI o heredado]`. ¿Cuáles son las causas posibles, cómo distingo cuál es la mía, y qué hago en cada caso? No quiero borrar Windows.»

Marca también **«Instalar software de terceros»** cuando lo ofrezca: ahí van los drivers de wifi y gráficos que pueden ahorrarte la pelea de la parada siguiente.

El resto son preguntas fáciles: zona horaria, distribución del teclado —prueba la `ñ` y los acentos antes de continuar—, nombre de usuario y contraseña.

> [!TIP]
> **Al escribir la contraseña en una terminal de Linux no aparecen puntos ni asteriscos.** Parece que no estás escribiendo. Sí lo estás. Escribe y presiona Enter.

## Paso 4 — GRUB

Al reiniciar aparece un menú de texto con Ubuntu arriba y Windows más abajo. Eso es **GRUB**, el gestor de arranque de GNU que viste en la unidad: elige qué sistema iniciar, con unos segundos de espera y un default.

Que aparezca es la señal de que salió bien. **Arranca Windows una vez**, ahora mismo, para confirmar que sigue entero. Luego vuelve a Linux.

Si GRUB no aparece y la máquina arranca directo a Windows, no perdiste nada: la instalación está ahí y el firmware está eligiendo el gestor equivocado. Se arregla desde el menú de arranque y desde el orden de arranque del firmware. Pregunta con tu modelo en la mano.

## Qué te llevas

- **Encoge desde Windows; instala desde Linux.** Cada sistema mueve lo suyo.
- **Fast Startup desactivado, siempre.** Y descarga la clave de BitLocker antes de empezar.
- **«Instalar junto a Windows Boot Manager» es el botón.** Si no está, para y averigua por qué.
- **GRUB es la prueba de que funcionó.** Arranca Windows una vez para confirmarlo.
- Ya tienes Linux. Falta dejarlo usable: [[primer-arranque]].
