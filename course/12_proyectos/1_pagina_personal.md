---
id: pagina-personal
title: "Proyecto 1: tu página personal en GitHub Pages"
nav_title: "1. Página personal"
summary: "Una página tuya, con el estilo que quieras, publicada en la raíz de tu dominio github.io y con tus links funcionando."
status: ready
estimated_time: 8m
tags: [proyectos, github-pages, pagina-personal, entrega]
prerequisites: [proyectos]
---

# Proyecto 1: tu página personal en GitHub Pages

**Individual · fecha de entrega por definirse · se presenta en persona, sin diapositivas.**

Es **tu página** y tú decides qué hacer con ella. No tiene que ser un CV formal. Puede tener una cara formal y otra libre. Cabe lo que te guste: videojuegos, reseñas de comida, gráficas, visualizaciones, cosas muy tuyas.

## Lo mínimo que debe tener

- Quién eres.
- Tus **redes sociales**: link a tu GitHub y a tu LinkedIn, y las demás que quieras.
- Link a tu CV, en PDF.
- **Todos esos links tienen que funcionar.** Es lo que más se va a revisar.

## La URL

```text
https://<tu-usuario>.github.io/              ← así
https://<tu-usuario>.github.io/mi-repo/      ← así no
```

La página carga en la raíz de tu dominio de GitHub, sin subcarpeta. Eso exige que el repositorio se llame exactamente `<tu-usuario>.github.io`, con tu usuario tal como está en GitHub.

**Si no funciona online, no cuenta.** Abrirla en tu computadora no es evidencia. Comprueba en una ventana de incógnito, en el navegador, con la URL pública.

Lo que más rompe una página que en local sí funcionaba:

- Rutas que apuntan a tu computadora (`C:\...`, `file://`).
- Mayúsculas y minúsculas distintas entre el nombre del archivo y el link: el servidor sí las distingue.
- Imágenes o PDF que nunca se subieron al repositorio.

## Qué entregas

Un pull request, desde tu fork, en la rama `tarea-12-pagina`, con un solo archivo:

```text
estudiantes/<tu-login>/pagina/pagina.yaml
```

```yaml
nombre: Nombre Apellido
url: https://<tu-login>.github.io/
```

Nada más: ni presentación, ni capturas, ni el código de la página, que vive en su propio repositorio.

## Qué se revisa

- Que el pull request cumpla lo de siempre: tu carpeta, tu login, la rama.
- Que la URL sea exactamente la de arriba y cargue online.
- Que la página tenga los links de arriba y funcionen. El de LinkedIn rechaza a los programas automáticos, así que ese lo reviso a mano.
- Que no haya imágenes rotas ni rutas locales.

## Cómo se presenta

Abres tu página en vivo y platicas cómo la hiciste. Sin diapositivas.
