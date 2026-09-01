---
id: git-y-github
title: "Git y GitHub"
nav_title: "Git y GitHub"
summary: "Deja tu computadora conectada a GitHub por SSH, clona el repositorio del curso y trabaja sin fricción."
status: ready
estimated_time: 45m
tags: [git, github, ssh, llaves, repositorio, setup]
prerequisites: [terminal-directa]
---

# Git y GitHub

![Sala de servidores nocturna en verde y ámbar: una silueta de espaldas sostiene contra el pecho una pieza que brilla en ámbar, mientras una copia verde de esa misma pieza viaja por un haz de luz hasta encajar en la ranura de un monolito al fondo; del monolito bajan cuatro líneas paralelas que se unen en una sola.](_assets/ilus-git-portada.jpg)

## En corto

- Vas a crear **un par de llaves**: una se queda para siempre en tu computadora, la otra se pega en tu cuenta de GitHub.
- Bien hecho, se configura **una vez** y no vuelve a pedirte contraseña.
- Al final tendrás el repositorio del curso clonado en `~/fdd/fdd_o26`, listo para trabajar.

## Por qué esta unidad importa más que las otras

Las demás unidades te enseñan a pensar sobre algo. Ésta te deja la mesa puesta.

A partir de ahora vas a **entregar trabajo dentro del repositorio del curso**, y si esto no queda bien configurado hoy, cada entrega se va a convertir en pelear con la herramienta en vez de con el problema. Son cuarenta y cinco minutos que te ahorran el resto del semestre.

## Las dos hojas

| # | Página | Terminas cuando… | Tiempo |
|---:|---|---|---:|
| 1 | [[cuenta-y-llave|Cuenta y llave]] | `ssh -T` te saluda por tu nombre de usuario | 25 min |
| 2 | [[clonar-y-trabajar|Clonar y trabajar]] | tienes el repositorio clonado y sabes cómo entra un cambio | 20 min |

## Antes de empezar

Necesitas la terminal que preparaste en [[terminal-directa|Terminal: uso directo]] —Ubuntu, Ubuntu dentro de WSL2 o macOS— y una conexión a internet. Nada más.

Comprueba que tienes las dos herramientas:

```bash
git --version
ssh -V
```

Las dos deberían responder con una versión. Si `git` no está, en Ubuntu y WSL2 se instala con `sudo apt update` y después `sudo apt install git`; en macOS, `git --version` suele ofrecerte instalar las herramientas de línea de comandos de Xcode, y aceptar es suficiente.

## Una regla que se repite las dos hojas

> [!WARNING]
> Tu llave **privada** no se comparte nunca: ni por correo, ni por WhatsApp, ni en una captura de pantalla, ni en una entrega. El único archivo que se copia a algún lado es el que termina en `.pub`. Si alguna vez la mandas por accidente, se borra el par y se genera otro; toma dos minutos y no pasa nada.

## Qué te llevas

- Una llave SSH que GitHub reconoce, y que sigue funcionando mañana y el mes que viene.
- El repositorio del curso clonado y con tu nombre configurado en cada commit.
- Saber qué hacer cuando formatees la computadora o cambies de máquina.
