# Fuentes de Datos — Otoño 2026 (ITAM)

**Sitio del curso: https://rayalucaria.org/fdd_o26/**

Este repositorio es la fuente del sitio. No es una copia de respaldo: el sitio se
construye a partir de estos archivos en cada push a `main`, así que lo que lees en
la web y lo que está aquí son la misma cosa vista de dos maneras.

**Las tareas se entregan por pull request a este repositorio**, desde la unidad 7
(8 de septiembre de 2026) en adelante. El flujo completo está en
https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/

Las entregas anteriores a esa fecha fueron por Canvas.

## Datos del curso

| | |
|---|---|
| Horario | Martes y jueves, 19:00–20:30 |
| Semestre | 11 de agosto – 1 de diciembre de 2026 (32 sesiones) |
| Contacto | mario.vazquez.corte@itam.mx |

Hay dos excepciones al horario en todo el semestre: el **jueves 17 de
septiembre** y el **jueves 1 de octubre**, las dos de **19:00 a 20:00**.

El único día sin clase del semestre es el **martes 15 de septiembre**. El asueto
del **2 de noviembre** y el descanso obligatorio del **16 de noviembre** (del
ITAM) caen en lunes y no afectan al curso: hay clase los martes 3 y 17 de
noviembre. El calendario completo, con el tema de cada sesión y las fechas de entrega, está en
[el calendario del sitio](https://rayalucaria.org/fdd_o26/_raya/schedule/).

## Evaluación

| Peso | Componente |
|---:|---|
| 30 % | Proyecto final |
| 30 % | **El mínimo** entre el promedio de tareas y el promedio de controles |
| 8 % | Examen parcial 1 |
| 8 % | Examen parcial 2 |
| 8 % | Proyecto 1 |
| 8 % | Proyecto 2 |
| 8 % | Participación |

Ese 30 % es la **menor** de las dos notas, no el promedio. La explicación está en
[El curso](https://rayalucaria.org/fdd_o26/introduccion/el-curso/).

## Estructura

```
course/          contenido del curso (Markdown + YAML)
  _official/     calendario del semestre
  1_introduccion/
  2_pipeline_de_datos/
skins/           tema visual
tools/           generadores de imágenes y sus pruebas
raya.yaml        configuración del curso
artifact/        salida generada — gitignorada, nunca se edita a mano
```

## Construir el sitio localmente

El CLI `raya` vive en el repositorio del framework
([raya-lucaria](https://github.com/raya-lucaria/raya-lucaria.github.io)) y se
invoca desde ahí con la ruta de este repo:

```bash
cd ../raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya preview ../fdd_o26
```

Las guardas de contenido corren desde aquí:

```bash
python3 -m pytest tools/ -q
```

`CLAUDE.md` documenta el contrato de autoría completo.
