# codigo

Aquí publico el código de cada unidad. **Esta carpeta es de sólo lectura.**

No edites nada de aquí. Si lo haces, tu pull request va a incluir cambios
fuera de tu carpeta y la revisión automática lo va a rechazar. Para deshacer
una edición accidental:

```bash
git restore codigo/
```

## La regla del mirror

Tu carpeta es un espejo de ésta. **Misma ruta, mismo nombre, sin excepciones.**

Lo que yo publico en `codigo/07_git/` tú lo copias a
`estudiantes/<tu-login>/07_git/`, y ahí trabajas.

```bash
cd ~/fdd/fdd_o26
echo "$GHUSER"   # tu login, del perfil de tu shell
mkdir -p estudiantes/$GHUSER/07_git
cp -r codigo/07_git/. estudiantes/$GHUSER/07_git/
```

Fíjate en la barra y el punto al final del origen. Sin ellos, `cp` copia la
carpeta en vez de su contenido, y la segunda vez que lo corras acabas con
`07_git` dentro de `07_git`.

El nombre de la subcarpeta no se inventa ni se traduce. Si aquí se llama
`07_git`, en tu carpeta se llama `07_git`.

Todo esto está explicado en la unidad: https://rayalucaria.org/fdd_o26/git-y-github/github/el-flujo-del-curso/

## Las carpetas

| Carpeta | Unidad | Qué contiene |
|---|---|---|
| `07_git/` | 07 — Git | Ejemplo y bitácora de la unidad de Git. |
| `github/` | 07 — GitHub | Certificaciones de Git y GitHub, de acumulación por entrega. |
| `08_contenedores/` | 08 — Contenedores | Laboratorios e imagen propia de la unidad. Ojo: el nombre lleva el cero adelante. |
| `docker/` | 08 — Contenedores | Certificaciones de Docker, de acumulación por entrega. |
| `09_python/` | 09 — Python | `ambientes/` (labs de clase), `uv_docker/` (entrega), `por_dentro/` (labs y entrega de la 9.2) y `stack/` (notebooks y entrega de la 9.3). Todo se trabaja en `estudiantes/<tu-login>/`. Ojo: el nombre lleva el cero adelante. |
| `python/` | 09 — Python | Certificaciones de Python, de acumulación por entrega. |
| `fastapi/` | 11 — Cómputo y concurrencia | Certificaciones de FastAPI (`certificaciones.md` y su captura). |
