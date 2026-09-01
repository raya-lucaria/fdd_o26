---
id: cuenta-y-llave
title: "Cuenta y llave"
nav_title: "Cuenta y llave"
summary: "Crea tu cuenta de GitHub, genera un par de llaves SSH y déjalo configurado para que no vuelva a pedirte nada."
status: ready
estimated_time: 25m
tags: [github, ssh, ssh-keygen, ssh-agent, llaves]
prerequisites: [git-y-github]
---

# Cuenta y llave

**Hoja 1 de 2** · 25 min

Meta: que `ssh -T` te salude por tu nombre de usuario.

::: figure {#git-llaves title="Dos llaves: una se queda, la otra viaja"}
![A la izquierda, la carpeta .ssh de tu computadora con dos archivos: la llave privada, que nunca sale de ahí, y la pública. A la derecha, GitHub. Una flecha lleva sólo la llave pública hacia GitHub, y otra de vuelta representa la comprobación con ssh -T](_assets/git-llaves.svg)
:::

## En corto

- Una llave SSH son **dos archivos**: uno privado que se queda en tu disco y uno público que se pega en GitHub.
- Se generan con un comando y se configuran una vez.
- Si pierdes la privada no se recupera: se genera otra. Eso es normal, no un accidente.

## Paso 1: la cuenta

Crea tu cuenta en [github.com/signup](https://github.com/signup) si aún no tienes una.

| Decisión | Recomendación |
|---|---|
| Correo | Usa uno **personal**, no el del ITAM. El institucional deja de funcionar cuando te gradúas y con él se va el acceso a tu historial. |
| Nombre de usuario | Algo que puedas decir en voz alta en una entrevista. Es una dirección pública y vas a cargar con él años. |
| Verificación en dos pasos | Actívala. GitHub la exige y recuperar una cuenta sin ella es un trámite lento. |

Cuando termines, anota tu **nombre de usuario** y tráelo a clase: lo vamos a necesitar más adelante, cuando cada quien monte su propio fork del repositorio.

## Paso 2: genera el par de llaves

**Haz:** cambia el correo por el tuyo. El primer comando crea la carpeta, porque en una instalación recién hecha puede no existir y `ssh-keygen` **no** la crea por ti.

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "tu-correo@ejemplo.com"
```

Te va a preguntar tres cosas:

| Pregunta | Qué contestar |
|---|---|
| Dónde guardar | Enter. El valor por omisión, `~/.ssh/id_ed25519`, es el correcto. |
| Passphrase | **Escribe una.** Es la contraseña de la llave; protege tu cuenta si alguien se lleva tu laptop. No se ve mientras la escribes. |
| Repetirla | La misma. |

**Comprueba:**

```bash
ls -l ~/.ssh/id_ed25519*
```

**Deberías ver** dos archivos: `id_ed25519` con permisos `-rw-------` y `id_ed25519.pub` con `-rw-r--r--`. Esa diferencia no es casual: la privada sólo la puede leer tu usuario.

`ed25519` es el tipo de llave. Si encuentras tutoriales que dicen `-t rsa -b 4096`, no están mal, pero son de antes: ed25519 es más corta, más rápida y la que GitHub recomienda hoy.

## Paso 3: que no te la vuelva a pedir

Sin esto, cada vez que `git` hable con GitHub te va a pedir la passphrase. El **agente** la guarda en memoria; el archivo `~/.ssh/config` le dice a `ssh` que la use sola.

**Haz:**

```bash
cat >> ~/.ssh/config <<'EOF'

Host github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  AddKeysToAgent yes
EOF
chmod 600 ~/.ssh/config
```

En **macOS**, agrega además `UseKeychain yes` debajo de esas líneas: guarda la passphrase en el llavero del sistema y sobrevive a reiniciar.

En **WSL2**, el agente no sigue vivo al cerrar la terminal. Si te vuelve a pedir la frase cada vez que abres una ventana nueva, agrega esto al final de `~/.bashrc`:

```bash
if [ -z "$SSH_AUTH_SOCK" ]; then eval "$(ssh-agent -s)" >/dev/null; fi
```

En **Ubuntu de escritorio** normalmente no hace falta nada: el escritorio ya trae un agente corriendo.

## Paso 4: pega la pública en GitHub

**Haz:** imprime la llave pública. Es **una sola línea**, y empieza con `ssh-ed25519`.

```bash
cat ~/.ssh/id_ed25519.pub
```

Selecciónala completa —desde `ssh-ed25519` hasta el correo del final— y cópiala. Después, en GitHub: **Settings → SSH and GPG keys → New SSH key**. Ponle un título que te diga de qué máquina es, por ejemplo «laptop personal», pega la línea en *Key* y guarda.

> [!WARNING]
> Fíjate en el `.pub` antes de copiar. Si el contenido empieza con `-----BEGIN OPENSSH PRIVATE KEY-----` estás mirando la privada: cancela, no la pegues en ningún lado, y vuelve a `cat` el archivo correcto.

## Paso 5: la comprobación

**Haz:**

```bash
ssh -T git@github.com
```

La primera vez te pregunta si confías en el servidor: escribe `yes`. Después:

```text
Hi tu-usuario! You've successfully authenticated, but GitHub does not provide shell access.
```

**Eso es un éxito, no un error.** Dice literalmente «no te doy acceso a una shell» porque GitHub no es un servidor donde te conectes a trabajar: la llave sirve para que `git` hable con GitHub, nada más. Si aparece tu nombre de usuario, terminaste.

::: problem {#git-p1-fallo title="Permission denied (publickey)"}
Corres `ssh -T git@github.com` y responde `Permission denied (publickey).` ¿Cuáles son las tres causas más probables, en orden?
:::

::: hint {of="git-p1-fallo"}
El mensaje dice que el servidor no reconoció ninguna llave. Piensa en las tres cosas que pudieron fallar: que no exista, que no la esté ofreciendo, o que del otro lado no esté.
:::

::: answer {of="git-p1-fallo"}
Primero, que **la pública no esté en GitHub**: se pegó a medias, se pegó en el campo del título, o se guardó en otra cuenta. Revisa Settings → SSH and GPG keys y compara la huella con la que da `ssh-keygen -lf ~/.ssh/id_ed25519.pub`.

Segundo, que **`ssh` esté ofreciendo otra llave**: si tienes varias, sin la línea `IdentityFile` del paso 3 puede intentar con la equivocada. `ssh -vT git@github.com` te muestra cuál probó.

Tercero, que **pegaste la privada o un pedazo**. GitHub rechaza lo que no tenga la forma de una llave pública. La buena es una línea que empieza con `ssh-ed25519`.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** el archivo que se copia a algún lado siempre termina en `.pub`. El otro nunca sale de tu computadora.

## Cierre

Ya tienes la llave y GitHub te reconoce. Continúa con [[clonar-y-actualizar|Clonar y mantener al día]] para bajar el repositorio del curso.
