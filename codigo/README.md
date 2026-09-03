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
U=$(gh api user --jq .login) && echo "$U"
mkdir -p estudiantes/$U/07_git
cp -r codigo/07_git/. estudiantes/$U/07_git/
```

Fíjate en la barra y el punto al final del origen. Sin ellos, `cp` copia la
carpeta en vez de su contenido, y la segunda vez que lo corras acabas con
`07_git` dentro de `07_git`.

El nombre de la subcarpeta no se inventa ni se traduce. Si aquí se llama
`07_git`, en tu carpeta se llama `07_git`.

Todo esto está explicado en la unidad: https://rayalucaria.org/fdd_o26/git-y-github/github/el-flujo-del-curso/
