---
id: planes-b
title: "Planes B — WSL2, Mac y la nube"
nav_title: "Planes B"
summary: "Qué hacer si no puedes instalar Linux hoy, y la media hora de configuración que sí le toca a quien tiene Mac."
status: ready
estimated_time: 10m
tags: [wsl2, windows, macos, codespaces, respaldo]
prerequisites: [instalar-linux]
---

# Planes B

## En corto

- **Nunca dejes de poder hacer la tarea del curso.** Si la instalación se atora, hay salidas.
- **WSL2** es Linux dentro de Windows: dos comandos y estás adentro.
- **La nube** —Codespaces— es la salida si la computadora no es tuya o no puedes instalar nada.
- **Mac ya es Unix.** Aquí está la media hora que sí te toca.
- Estas opciones **son un puente, no un destino**. Vuelve a [[instalar-linux]] el fin de semana.

## Cuándo usar un plan B

Hay tres situaciones legítimas:

1. **La computadora no es tuya** —de la escuela, de la familia, del trabajo— y no puedes reparticionarla.
2. **La instalación se atoró** en algo que necesita más tiempo del que tienes hoy.
3. **Es tu única máquina y hay una entrega esta semana.** Prudente. Instala el sábado.

Lo que *no* es una situación legítima: «me da flojera». Ya leíste la guía; la parte difícil es empezar.

> [!NOTE]
> Aun cuando instales Linux, **vale la pena tener un plan B configurado**. Una computadora se cae, un cargador se olvida. Tener Codespaces listo es media hora que te salva una entrega algún día.

## WSL2 — Linux dentro de Windows

::: definition {#def-wsl2 title="WSL2"}
Un núcleo Linux real corriendo en una máquina virtual ligera, integrada con Windows.

No es un emulador ni una traducción: **es Linux**, con su propio sistema de archivos, hablando con Windows por un puente.
:::

La analogía útil: si tu computadora es una casa (Windows), WSL2 es un cuarto anexo con reglas distintas. Lo que instalas ahí vive ahí. Windows ve los archivos, pero no entiende los programas.

### Instalación

**PowerShell como administrador:**

```powershell
wsl --install
```

Instala Ubuntu por defecto. Reinicia. Al volver se abre una terminal que pide usuario y contraseña —sin espacios, en minúsculas, y la contraseña no muestra puntos mientras la escribes—.

Si falla, casi siempre es virtualización desactivada en el firmware:

> **Prompt:**
> «Tengo una `[modelo exacto]` con Windows `[10 u 11, versión]`. `wsl --install` falla con `[mensaje exacto]`.
>
> 1. ¿Cómo verifico si la virtualización está activada, y cómo la activo en el firmware de este modelo específico?
> 2. ¿Cómo activo "Plataforma de máquina virtual" y "Subsistema de Windows para Linux" desde las características opcionales?
> 3. ¿Qué más puede causar este error exacto?»

### Las dos cosas que hay que saber

**Los archivos viven en dos mundos.**

| | Ruta |
|---|---|
| Windows | `C:\Users\TuNombre\Documentos` |
| WSL2 | `/home/tunombre/` |
| Tu disco de Windows, visto desde WSL2 | `/mnt/c/` |

Y desde WSL2, `explorer.exe .` abre la carpeta actual en el explorador de Windows.

> [!WARNING]
> **Guarda tus proyectos en `/home/tunombre/`, nunca en `/mnt/c/`.** El puente entre los dos sistemas de archivos es lentísimo: un proyecto de Python en `/mnt/c` puede tardar diez veces más en instalar dependencias. Es el error número uno de quien empieza con WSL2, y no da ningún síntoma más que lentitud inexplicable.

Después de instalar: `sudo apt update && sudo apt upgrade -y`, y verifica con `python3 --version`.

## macOS — la media hora que sí te toca

Buenas noticias: macOS es un Unix certificado, descendiente de la misma familia que viste en la unidad. Tienes terminal, tienes rutas POSIX, tienes casi todo. No instales Linux, no uses una máquina virtual.

Lo que sí te falta:

**Uno, las herramientas de línea de comandos de Apple:**

```bash
xcode-select --install
```

**Dos, Homebrew**, el gestor de paquetes que macOS no trae. Sigue las instrucciones de `brew.sh` — incluyen un paso para agregarlo al `PATH` que la gente se salta y luego `brew` «no existe».

**Tres, lo básico:**

```bash
brew install git python@3.12
```

**Cuatro, configura Git:**

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@itam.mx"
```

> [!TIP]
> **Dos diferencias con Linux que te van a morder.** El sistema de archivos de macOS **no distingue mayúsculas de minúsculas** por defecto: `Datos.csv` y `datos.csv` son el mismo archivo para tu Mac y dos archivos distintos para el servidor Linux donde va a correr tu código. Y varios comandos —`sed`, `date`, `ls`— son la variante BSD, con banderas distintas a las de GNU que aparecen en las guías. Cuando un comando de internet no funcione igual, esa suele ser la razón.

## La nube — cuando no puedes instalar nada

**GitHub Codespaces** te da VS Code en el navegador con una máquina Linux detrás. No instalas nada en la computadora.

1. Crea tu cuenta de GitHub, si no la tienes.
2. Solicita el **GitHub Student Developer Pack** con tu comprobante de inscripción del ITAM. Es gratis y sube bastante tus horas de Codespaces.
3. Abre cualquier repositorio y crea un Codespace.

Lo que pierdes: no funciona sin internet, las horas gratuitas se acaban, y no aprendes nada sobre cómo funciona una computadora. Es una red de seguridad, no un lugar donde vivir.

## Vuelve a intentarlo

Si estás aquí porque algo se atoró, no lo dejes así. Anota exactamente dónde te quedaste y en qué mensaje, y retómalo con tiempo:

> **Prompt:**
> «Intenté instalar `[distribución]` en dual boot en una `[modelo exacto]` y me atoré en `[paso exacto]` con `[mensaje o síntoma exacto]`. Ya probé `[lo que hiciste]`.
>
> 1. ¿Qué está pasando, exactamente?
> 2. ¿Cuáles son las opciones para resolverlo, de la menos riesgosa a la más riesgosa?
> 3. ¿Qué debo respaldar antes de intentar cada una?
> 4. ¿Qué le pregunto a Reddit y en qué subreddit, para que alguien con este mismo modelo me conteste?»

## Qué te llevas

- **Un plan B es un puente.** Configúralo, entrega la tarea, y vuelve a la instalación con calma.
- **WSL2 sirve, con una regla**: los proyectos van en `/home`, jamás en `/mnt/c`.
- **En Mac ya casi terminaste**: `xcode-select`, Homebrew, Git, y ojo con mayúsculas y con BSD.
- **Codespaces es la red de seguridad** para quien no puede instalar nada.
- La meta sigue siendo la misma: [[instalar-linux]] de verdad.
