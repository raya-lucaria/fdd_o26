---
id: proyecto-final
title: "Proyecto 2: el proyecto final"
nav_title: "2. Proyecto final"
summary: "Un proyecto completo y relevante para la clase, en un repo público con Docker, que se presenta con demo en vivo el día del examen final."
status: ready
estimated_time: 12m
tags: [proyectos, proyecto-final, docker, entrega, evidencia]
prerequisites: [proyectos]
---

# Proyecto 2: el proyecto final

**Equipo de 1 o 2 · se entrega el día del examen final · se presenta con demo en vivo.**

Si quieres un equipo de otro tamaño, lo hablas conmigo y yo decido.

## Qué puede ser

Cualquier tema **relevante para la clase**: un videojuego, benchmarks, back-end o front-end, un dashboard, un harness. Tiene que estar bien pensado, ser interesante y estar completo de punta a punta.

**No se vale algo hecho con vibe coding el día antes de entregar.** Antes de empezar, vienes a hablar conmigo para que yo autorice el proyecto. Si lo suben, se asume que lo hablamos; si no, lo veo yo y ajusto.

## Requisitos

- Repo de GitHub **público**, open source, con licencia.
- **Docker o Docker Compose**, con instrucciones cortas y directas en el README para correrlo.
- Accesible desde la web, o que corra fácil en cualquier máquina. Los videojuegos, en línea.
- La demo puede vivir **fuera de GitHub** (Supabase, un plan gratuito, otro hosting), o como acordemos si no aplica. Si el hosting sale caro, buscamos juntos una opción gratis.
- Evita los datos simulados, salvo que sean necesarios: por ejemplo, un dashboard para comparar muchas bases de datos.
- Un harness no tiene que estar en la web, pero sí funcionar dentro de un contenedor.

## Qué entregas (personal, aunque el proyecto sea del equipo)

**Cada integrante** abre su propio pull request, desde su fork, en la rama `tarea-12-proyecto-final`, con un archivo:

```text
estudiantes/<tu-login>/proyecto-final/proyecto.yaml
```

```yaml
proyecto: nombre-corto
titulo: Título del proyecto
repo: https://github.com/usuario-a/nombre-corto
demo: https://...            # puede estar fuera de GitHub
equipo: [usuario-a, usuario-b]
```

Los pull requests del mismo equipo se juntan por `proyecto` y `repo`, así que **deben coincidir en los dos**. Sin presentación en GitHub.

## Evidencia de que trabajaron

Quiero ver que cada integrante trabajó, sin que sea complicado. Lo que GitHub ya sabe (commits, pull requests, issues, reviews) se toma de GitHub y no lo escribes a mano.

Para lo que no deja commits (un robot, hardware, diseño, pruebas), lleva una `BITACORA.md` en el repo, con una línea por entrada: fecha, quién, qué hizo y un **link o un archivo commiteado** (foto, video). Sin link ni archivo, la línea no cuenta como evidencia. No subas caras ni datos personales: el repo es público.

## Qué se revisa

- Que el repo sea público y traiga licencia, README y Docker.
- Que el Compose sea válido y la demo responda, si declaras una.
- Que cada integrante del equipo tenga su pull request con los mismos datos.
- Que cada integrante tenga evidencia de trabajo por algún canal.

Los reportes dicen hechos verificables, por ejemplo cuántos commits tiene cada quien. Nunca acusan a nadie.

## Cómo se presenta

Demo en vivo y platicar todo el proceso. **No se muestra código.** Las diapositivas se recomiendan, pero no son obligatorias. Cuenta:

1. Qué es, a grandes rasgos.
2. Cómo funciona y su arquitectura.
3. Qué se les hizo difícil y qué problemas tuvieron.
4. La demo, funcionando.
5. El proceso completo: qué hay detrás de lo que se ve.
