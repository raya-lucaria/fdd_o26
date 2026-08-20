---
id: primer-arranque
title: "Parada 5 — Primer arranque"
nav_title: "5. Primer arranque"
summary: "Actualizar, resolver lo que quedó a medias con ayuda del LLM, y dejar la máquina lista para el resto del curso."
status: ready
estimated_time: 12m
tags: [post-instalacion, apt, drivers, terminal, git, configuracion]
prerequisites: [dual-boot]
---

# Parada 5 — Primer arranque

## En corto

- Lo primero: **actualizar**. Muchos problemas se arreglan solos ahí.
- **Algo va a estar a medias.** Es normal, no es un fracaso, y tiene arreglo.
- El bucle de la parada 1 sigue funcionando, ahora con **mensajes de error concretos** que pegar en el prompt.
- Al final de esta parada tienes lo que el resto del curso asume: terminal, Python y Git.

## Lo primero, siempre

Abre la terminal —`Ctrl` + `Alt` + `T` en la mayoría de escritorios— y corre:

```bash
sudo apt update && sudo apt upgrade -y
```

En Fedora, `sudo dnf upgrade --refresh`.

Vale la pena entender qué son esos dos comandos en vez de teclearlos de memoria:

- **`update`** refresca el catálogo: le pregunta a los repositorios qué versiones existen hoy. **No instala nada.**
- **`upgrade`** instala lo que el catálogo dice que está más nuevo que lo tuyo.
- **`sudo`** ejecuta como administrador. Va a pedir tu contraseña, y —otra vez— no vas a ver puntos mientras la escribes.

Reinicia si actualizó el kernel. Es común en la primera actualización, y es justamente la que arregla drivers.

## La lista de verificación

Prueba estas siete cosas y anota cuáles fallan. No las arregles todavía: primero levanta la lista completa.

| Prueba | Cómo |
|---|---|
| Wifi | Conéctate a una red y abre una página |
| Sonido | Reproduce un video |
| Cámara y micrófono | Abre la app de cámara; prueba una videollamada |
| Suspensión | Cierra la tapa, espera un minuto, ábrela |
| Batería | ¿Aparece el porcentaje? ¿Dura algo parecido a lo de Windows? |
| Brillo | Las teclas de función |
| Bluetooth | Empareja unos audífonos |

> [!NOTE]
> **Que falle algo aquí es lo normal, no la excepción.** Casi nadie tiene una instalación perfecta al primer arranque. La diferencia entre quien se queda con Linux y quien se rinde no es que a uno le haya funcionado todo: es que uno trató la lista como pendientes y el otro como veredicto.

## El bucle, ahora con evidencia

La ventaja de este momento sobre la parada 1 es que ya no adivinas: **tienes mensajes de error, salidas de comandos y logs**. Eso convierte al LLM de consejero general en depurador útil.

Los comandos que producen la evidencia:

```bash
inxi -Fxz                  # resumen completo del hardware y sus drivers
lspci -k                   # dispositivos y qué módulo del kernel usa cada uno
journalctl -p 3 -b         # errores de este arranque
dmesg | tail -50           # últimos mensajes del kernel
uname -r                   # versión del kernel
```

Si `inxi` no está: `sudo apt install inxi`.

Y el prompt:

> **Prompt:**
> «Acabo de instalar `[distribución y versión]` en una `[modelo exacto]`. `[Qué falla, con el detalle que puedas]`.
>
> Aquí está la salida de `inxi -Fxz`:
>
> ```
> [pega la salida]
> ```
>
> Y los errores de `journalctl -p 3 -b`:
>
> ```
> [pega la salida]
> ```
>
> 1. Explícame qué me dicen estas salidas sobre el problema, señalando las líneas concretas.
> 2. Dame la solución más probable, paso a paso, explicando qué hace cada comando antes de que lo corra.
> 3. Dime cómo revertir cada paso si empeora.
> 4. Si esto requiere un driver propietario, dime cuál y por qué no venía incluido.»

Las preguntas 2 y 3 son las que importan de verdad. **No corras comandos que no entiendes**, sobre todo con `sudo`. Pedir la explicación antes y la reversión después es lo que separa aprender de copiar y pegar hasta que algo cambie.

> [!TIP]
> Si el LLM te da un comando y no te explicó qué hace, pregúntale: «explícame ese comando parte por parte, incluyendo cada bandera, antes de que lo ejecute». Vas a aprender más en esa respuesta que en toda la instalación.

## Los dos problemas clásicos

**Wifi que no aparece.** Casi siempre es un chip Realtek sin driver incluido. El problema es circular —necesitas internet para bajar el driver de internet— y se rompe con un cable ethernet, con el celular en modo USB tethering, o bajando el paquete en Windows y pasándolo por USB. Con tu modelo de tarjeta exacto, es media hora.

**Pantalla negra o resolución rara con NVIDIA.** El driver libre `nouveau` no siempre alcanza. La solución es el driver propietario, y en Ubuntu está en «Controladores adicionales», a un par de clics. Si ni siquiera llegas al escritorio, se arranca con un parámetro temporal del kernel desde GRUB — pregunta cómo, con tu modelo.

## Deja la máquina lista para el curso

Cuatro cosas y terminas.

**Uno, comprueba Python:**

```bash
python3 --version
```

**Dos, instala lo básico de compilación** —muchas librerías de Python lo necesitan:

```bash
sudo apt install build-essential git curl
```

**Tres, configura Git con tu identidad:**

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@itam.mx"
```

**Cuatro, mira tu sistema:**

```bash
sudo apt install neofetch && neofetch
```

Es puro adorno. Vale la pena de todos modos: es la primera vez que la computadora te dice qué es sin que tengas que buscarlo.

> [!TIP]
> Un último prompt, para arrancar la unidad siguiente:
>
> «Ya tengo `[distribución]` instalado y actualizado. Enséñame los comandos para moverme por el sistema de archivos —`pwd`, `ls`, `cd`, `mkdir`, `rm`—, explicando qué hace cada uno y cuál es peligroso y por qué. Después dime cómo está organizado el sistema de archivos de Linux: qué son `/home`, `/etc`, `/usr`, `/var` y `/mnt`.»

## Qué te llevas

- **Actualizar es el primer movimiento** y arregla más de lo que parece.
- **Algo va a fallar, y está bien.** Levanta la lista completa antes de arreglar nada.
- **Ahora tienes evidencia**: `inxi`, `lspci`, `journalctl`. Pégala en el prompt.
- **Pide la explicación antes y la reversión después** de cada comando con `sudo`.
- **Ya está.** Tienes la misma clase de sistema que corre la nube que vas a usar el resto del semestre.
