# 08_contenedores

Aquí va el trabajo de la unidad: tu imagen propia y los laboratorios. Las
certificaciones de Docker **no** van aquí — ésas viven en `codigo/docker/`,
que se copia aparte.

Como todo lo demás, esta carpeta se copia a la tuya respetando el mirror. Ojo
con el nombre: la carpeta lleva **el cero adelante**, aunque la unidad se vea
como «8» en el sitio.

```bash
cd ~/fdd/fdd_o26
echo "$GHUSER"   # tu login, del perfil de tu shell
mkdir -p estudiantes/$GHUSER/08_contenedores estudiantes/$GHUSER/docker
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
cp -r codigo/docker/.          estudiantes/$GHUSER/docker/
```

Fíjate en la barra y el punto al final del origen. Sin ellos, `cp` copia la
carpeta en vez de su contenido, y la segunda vez que lo corras acabas con
`08_contenedores` dentro de `08_contenedores`. Tampoco copies arrastrando en
el Finder ni en el Explorador: eso produce nombres con la palabra «copia».

Después trabajas en `estudiantes/$GHUSER/08_contenedores/` y
`estudiantes/$GHUSER/docker/`, nunca aquí.

## Qué hay en cada carpeta

- `info/` — el ejemplo de la clase: un script que reporta el estado del
  sistema, empaquetado en una imagen. Punto de partida para leer un
  `Dockerfile` antes de escribir uno.
- `roto/` — un `Dockerfile` con tres defectos a propósito. Arréglalo; ésa es
  la entrega de la imagen.
- `volumenes/` — `app.py` para los ocho casos de bind mounts, y
  `predicciones.md` con la tabla ya armada.
- `donde_vive/` — un `app.py` y su `Dockerfile`, para ver dónde vive el
  código según cómo lo montes.
- `dev/` — un flujo de desarrollo con volumen, para iterar sin rebuild.
- `bitacora.md` y `mi-imagen.md` — se llenan en tu copia, no aquí.

`volumenes/predicciones.md` **no se entrega**. Es para llenar antes de correr
cada caso, no para calificar.
