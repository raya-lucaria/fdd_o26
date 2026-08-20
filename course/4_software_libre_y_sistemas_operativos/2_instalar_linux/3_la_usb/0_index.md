---
id: la-usb-de-instalacion
title: "Parada 3 — La USB de instalación"
nav_title: "3. La USB"
summary: "Descargar la imagen, verificar que no llegó corrupta, grabar la USB y arrancar en modo prueba sin instalar nada."
status: ready
estimated_time: 12m
tags: [usb, iso, checksum, live-usb, uefi, instalacion]
prerequisites: [elige-tu-distribucion]
---

# Parada 3 — La USB de instalación

## En corto

- Descargas un archivo **`.iso`**: un disco de instalación completo en un solo archivo.
- **Verifica el checksum.** Una descarga a medias produce errores que parecen fallas de hardware.
- Grabar la USB **borra todo lo que tenga**. No es copiar el archivo: es escribir un disco.
- El resultado es una **Live USB**: arranca Linux sin tocar tu disco. Puedes probarlo todo antes de instalar.
- **Esta parada no modifica tu computadora.** Es el momento de perder el miedo.

## Qué es una ISO

::: definition {#def-iso title="Imagen ISO"}
Un archivo que contiene la copia byte a byte de un disco entero: el sistema de archivos, los archivos y la estructura de arranque.

No se «abre»: se **escribe** sobre un medio físico para reconstruir el disco original.
:::

Por eso no basta con copiar el `.iso` a la USB. Copiarlo deja un archivo dentro de la USB, y el firmware no sabe qué hacer con un archivo. Hay que **escribir su contenido crudo sobre el dispositivo**, sobreescribiendo la tabla de particiones. De ahí que se borre todo.

## Descarga

Baja la imagen **sólo del sitio oficial de la distribución**. No de un espejo que encontraste en un blog, no de un torrent que no sea el que publica la propia distribución.

Elige la variante de **64 bits para PC (`amd64` / `x86_64`)** salvo que tu investigación de la parada 2 diga otra cosa. Si tienes una Mac con chip Apple, la arquitectura es `arm64` — y de nuevo, en Mac esta guía no te toca.

Son entre 2 y 5 GB. Con wifi lento tarda.

## Verifica el checksum, en serio

Esta es la parte que todo el mundo se salta y es la que produce las historias más frustrantes.

::: definition {#def-checksum title="Checksum"}
Una huella digital del archivo: una función que le asigna una cadena corta y prácticamente única.

Si un solo bit cambió durante la descarga, **la huella cambia por completo**.
:::

Una ISO corrupta no falla al descargarse: falla después, durante la instalación, con errores que parecen hardware defectuoso. Vas a pasar dos horas culpando a tu disco duro por un archivo incompleto. La verificación toma treinta segundos.

En la página de descarga hay un archivo con las sumas (`SHA256SUMS` o similar). Compara.

**En Windows**, PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 .\<nombre-de-tu-imagen>.iso
```

**En macOS o Linux**:

```bash
shasum -a 256 <nombre-de-tu-imagen>.iso
```

La cadena que sale debe ser **idéntica** a la publicada. Si no lo es, descarga otra vez.

## Grabar la USB

| Herramienta | Sistema | Notas |
|---|---|---|
| **Rufus** | Windows | El estándar. Muchas opciones, y hay que entender dos de ellas |
| **balenaEtcher** | Windows, macOS, Linux | Tres clics, casi sin opciones. Buena si Rufus te intimida |
| **Ventoy** | Todos | Copia varias ISOs a la misma USB y eliges al arrancar. Muy conveniente si vas a probar distribuciones |
| **`dd`** | macOS, Linux | Una línea, cero red de seguridad. **Un dispositivo equivocado borra tu disco** |

Si usas **Rufus**, las dos opciones que importan:

- **Esquema de partición**: `GPT` si tu firmware es UEFI —lo es, en cualquier equipo de los últimos diez años—. `MBR` sólo para máquinas viejas con BIOS heredado. Este dato lo sacaste en la parada 1 con `msinfo32`.
- **Sistema de destino**: `UEFI (no CSM)` para acompañar a GPT.

Cuando Rufus pregunte entre modo «Imagen ISO» y modo «DD», acepta el recomendado. Y va a advertirte que se borrará todo en el dispositivo — es correcto, es lo que estás pidiendo.

> [!WARNING]
> **Verifica dos veces cuál es la unidad de destino.** Es el único momento de toda la guía en el que un clic equivocado borra datos de verdad. Desconecta cualquier otro disco externo antes de grabar, para que sólo haya una opción posible.

## Prueba sin instalar

Aquí está el regalo que casi nadie aprovecha: **la USB arranca un Linux completo, funcionando, sin escribir una sola cosa en tu disco duro**.

::: definition {#def-live-usb title="Live USB"}
Un sistema que corre íntegramente desde la memoria USB y la RAM.

Puedes navegar, abrir la terminal, conectarte al wifi y probar el hardware. Al apagar, no queda rastro: **tu disco no se tocó**.
:::

Reinicia y entra al **menú de arranque** —la tecla la averiguaste en la parada 1; suele ser `F12`, `F9`, `Esc` o `F2`— y elige la USB. Cuando el instalador ofrezca «Probar Ubuntu» o «Try», elige eso, **no** «Instalar».

Y una vez adentro, prueba exactamente las cosas que te preocupan:

- **¿Funciona el wifi?** Conéctate a una red. Este es *el* punto de falla más común.
- **¿Se ve bien la pantalla?** Resolución correcta, sin parpadeo, brillo ajustable.
- **¿Hay sonido?** Reproduce algo.
- **¿Funcionan el touchpad, el teclado, la cámara?**
- **¿El instalador ve tu disco duro?** Ábrelo con la herramienta de discos. Si tu SSD no aparece, tienes RAID/RST activado en el firmware y hay que cambiarlo antes de instalar.

Si algo de esto falla, **ese es el problema que hay que resolver antes de instalar**, con el bucle de siempre:

> **Prompt:**
> «Estoy en una sesión Live USB de `[distribución y versión]` en una `[modelo exacto]`. `[Descripción exacta de lo que falla]`. Mi tarjeta es `[modelo del componente]`.
>
> 1. ¿Cuál es la causa más probable?
> 2. Dame los comandos para diagnosticarlo desde esta sesión en vivo y explícame qué debería ver si funcionara bien.
> 3. ¿Esto se arregla después de instalar —por ejemplo instalando un driver— o es un bloqueo real que debo resolver antes?
> 4. ¿Qué debo buscar en Reddit para confirmarlo?»

> [!TIP]
> **Si todo funciona en la sesión en vivo, va a funcionar instalado.** La Live USB es lento porque corre desde USB, no porque Linux sea lento — instalado en tu SSD vuela.

## Qué te llevas

- **La ISO se escribe, no se copia**, y por eso la USB se borra entera.
- **Verificar el checksum toma treinta segundos** y te ahorra horas culpando al hardware equivocado.
- **GPT + UEFI** salvo que tu equipo sea muy viejo.
- **Prueba en vivo antes de instalar.** Wifi, pantalla, sonido y que el instalador vea tu disco.
- Con todo funcionando, sigue a [[dual-boot]].
