---
id: conoce-tu-maquina
title: "Parada 1 — Conoce tu máquina"
nav_title: "1. Conoce tu máquina"
summary: "Cómo averiguar el modelo exacto, el firmware y los componentes de tu computadora, y por qué ese dato decide todo lo demás."
status: ready
estimated_time: 10m
tags: [hardware, diagnostico, llm, instalacion]
prerequisites: [instalar-linux]
---

# Parada 1 — Conoce tu máquina

## En corto

- «Tengo una HP» no sirve. **«HP Pavilion Laptop 15-eh1021la»** sirve.
- El dato está en tres lugares: **la etiqueta de abajo, el firmware y un comando**.
- Lo que necesitas anotar son **seis datos**, y caben en una nota del celular.
- Con esos seis datos, todas las preguntas siguientes se vuelven respondibles.

## Por qué el modelo exacto lo decide todo

Un fabricante vende diez variantes del mismo nombre comercial. Cambian el chip de wifi, cambian el controlador de almacenamiento, cambian el firmware. **Dos laptops que se llaman igual pueden necesitar instalaciones distintas**, y la única forma de saber cuál te tocó es el identificador largo y feo, el que trae letras y números.

Ese identificador es la llave de todo lo que sigue. Con él encuentras el manual del fabricante, la tecla exacta para entrar al firmware, los reportes de otras personas con tu mismo equipo y la lista de drivers que vas a necesitar.

## Los seis datos

Abre una nota y llénala. Vas a copiar y pegar esto en cada pregunta que hagas de aquí en adelante.

| Dato | Ejemplo | Para qué sirve |
|---|---|---|
| Marca y modelo exacto | `Lenovo IdeaPad 3 15ITL6 82H8` | Todo |
| Procesador | `Intel Core i5-1135G7` | Compatibilidad y arquitectura |
| RAM | `8 GB` | Qué distribución aguanta |
| Almacenamiento y espacio libre | `SSD NVMe 512 GB, 180 GB libres` | Si cabe el dual boot |
| Tarjeta gráfica | `Intel Iris Xe` / `NVIDIA GTX 1650` | El punto que más problemas da |
| Tarjeta de red inalámbrica | `Intel AX201` / `Realtek RTL8821CE` | El segundo punto que más problemas da |

> [!WARNING]
> **Los dos últimos son los importantes.** El noventa por ciento de las historias de terror de instalación de Linux son una de dos cosas: una NVIDIA que necesita driver propietario, o un chip de wifi Realtek que no trae driver incluido. Si sabes cuál tienes **antes** de instalar, dejas de ser una historia de terror y pasas a ser un procedimiento.

## Dónde encontrarlos

### En la etiqueta

Voltea la computadora. Hay una etiqueta pegada con el modelo, el número de serie y a veces un código de producto. Tómale foto: es la fuente más confiable porque viene del fabricante.

Si la etiqueta se borró —pasa mucho—, el modelo suele estar también bajo la batería, en el marco de la pantalla, o impreso en la caja original.

### Preguntándole a la computadora

Este es el punto del bucle auto-referencial. La máquina sabe qué es; sólo hay que preguntárselo.

**En Windows**, abre PowerShell y corre:

```powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model
Get-CimInstance Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate
Get-CimInstance Win32_VideoController | Select-Object Name
Get-NetAdapter | Select-Object Name, InterfaceDescription
```

También sirve escribir `msinfo32` en el menú de inicio: abre «Información del sistema», que trae todo junto y además te dice si el firmware es **UEFI** o **BIOS heredado** —dato que vas a necesitar en la parada 3.

**En macOS**, el menú Apple y luego «Acerca de esta Mac». Pero si estás en Mac, ya viste que no necesitas esta guía.

**Si ya tienes un Linux a la mano** (una USB en vivo, por ejemplo):

```bash
sudo dmidecode -s system-product-name
lscpu
lspci | grep -Ei 'vga|3d|network'
free -h
```

### Preguntándole al LLM cómo preguntarle a la computadora

Y este es el movimiento que de verdad importa aprender, porque funciona para cualquier cosa que no sepas hacer todavía. **No preguntes el dato: pregunta cómo obtener el dato.**

> **Prompt:**
> «Tengo una laptop con Windows 11 y no sé el modelo exacto. Dame tres formas distintas de averiguarlo desde el propio sistema —comandos de PowerShell, herramientas gráficas incluidas en Windows y dónde buscar la etiqueta física—. Explícame qué significa cada campo del resultado y cuál es el identificador que debo usar para buscar guías de instalación de Linux, porque hay varios números y no sé cuál es el bueno.»

Fíjate en la última cláusula. **Le estás diciendo al modelo cuál es tu confusión real**, no sólo lo que quieres. Esa frase es la que convierte un volcado de datos en una respuesta que puedes usar.

## El prompt de diagnóstico

Cuando ya tengas los seis datos, esta es la pregunta que abre la parada siguiente:

> **Prompt:**
> «Estos son los datos de mi computadora:
>
> - Modelo: `[pega aquí]`
> - Procesador: `[pega aquí]`
> - RAM: `[pega aquí]`
> - Almacenamiento y espacio libre: `[pega aquí]`
> - Gráficos: `[pega aquí]`
> - Wifi: `[pega aquí]`
> - Firmware: `[UEFI o BIOS heredado]`
>
> Quiero instalar Linux en dual boot con Windows. Antes de elegir distribución, dime:
>
> 1. ¿Qué problemas de compatibilidad son conocidos para este hardware específico —wifi, gráficos, audio, lector de huella, suspensión—? Sé concreto sobre cuáles requieren pasos extra y cuáles funcionan de fábrica.
> 2. ¿Tiene este modelo alguna particularidad de firmware que complique arrancar desde USB, como RAID/RST activado en el controlador de almacenamiento?
> 3. ¿Qué tecla abre el menú de arranque y cuál abre la configuración de firmware en este modelo?
> 4. Dime también qué NO puedes saber con certeza sobre este equipo, para que yo lo verifique con usuarios reales.»

La pregunta 4 no es un adorno. **Un modelo de lenguaje va a responderte con confianza sobre un modelo que nunca vio.** Pedirle explícitamente que marque su incertidumbre te dice qué tienes que ir a confirmar a Reddit, que es justo lo que hace la parada siguiente.

## Qué te llevas

- **El identificador largo y feo es el que sirve**, no el nombre comercial.
- **Gráficos y wifi son los dos que fallan.** Averígualos antes, no durante.
- **Pregúntale al LLM cómo obtener el dato**, no el dato — así el método te sirve la próxima vez.
- **Pídele que marque lo que no sabe.** Esa lista es tu tarea en [[elige-tu-distribucion]].
