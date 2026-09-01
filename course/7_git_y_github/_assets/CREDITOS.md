# Créditos de materiales de la unidad

Procedencia, ruta y condición de uso de cada material del directorio.

Los SVG salen de `tools/gen_git.py`, que es su única fuente de verdad: no se
editan a mano, se regeneran. La guarda `tools/test_gen_git.py` falla si un
archivo del disco deja de coincidir con lo que produce el generador.

| Archivo | Descripción y prompt resumido | Autor / origen | Fecha | Licencia |
|---|---|---|---|---|
| ilus-git-portada.jpg | Ruta: `course/7_git_y_github/_assets/ilus-git-portada.jpg`. Portada: sala de servidores nocturna donde una silueta de espaldas sostiene una pieza ámbar mientras una copia verde viaja por un haz de luz hasta encajar en un monolito, del que bajan cuatro líneas que se unen en una. Sin glifos legibles, sin logos, sin marcas de agua. | OpenAI Image Generation (gpt-image-2); generación original para el curso | 2026-09-01 | Uso docente del curso |
| git-llaves.svg | Ruta: `course/7_git_y_github/_assets/git-llaves.svg`. El par de llaves: la privada que no sale de `~/.ssh` y la pública que se pega en GitHub, con la comprobación de `ssh -T` de vuelta. | Diagrama original del curso, generado por `tools/gen_git.py` | 2026-09-01 | Uso docente del curso |
| git-flujo.svg | Ruta: `course/7_git_y_github/_assets/git-flujo.svg`. De clonar a publicar: rama, commits, push y pull request, con el atajo de push directo a `main` marcado como incorrecto. | Diagrama original del curso, generado por `tools/gen_git.py` | 2026-09-01 | Uso docente del curso |

Ninguna imagen de esta unidad procede de terceros. La portada fue generada con
OpenAI Image Generation el 2026-09-01 y, como el resto de las ilustraciones del
curso, **ninguna** representa personas reales, rostros reconocibles, personajes
con derechos, logotipos ni texto legible; se usa como ambientación y no como
fuente de información técnica.
