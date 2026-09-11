# github

Aquí va la evidencia de las certificaciones de Git y GitHub.

Como todo lo demás, esta carpeta se copia a la tuya respetando el mirror:

```bash
cd ~/fdd/fdd_o26
U=$(gh api user --jq .login) && echo "$U"
mkdir -p estudiantes/$U/github
cp -r codigo/github/. estudiantes/$U/github/
```

Después trabajas en `estudiantes/$U/github/`, nunca aquí.

## Qué debe quedar dentro

Son **dos entregas** sobre esta misma carpeta, en dos fechas distintas.

| Entrega | Archivos que deben estar | Curso |
|---|---|---|
| Primera | `certificaciones.md` con la primera sección llena, y `introduccion-a-git.png` | Introduction to Git |
| Segunda | Lo anterior, más `certificaciones.md` completo y `git-intermedio.png` | Intermediate Git |

Los nombres no se inventan ni se traducen. Si tu captura es `.jpg` en vez de
`.png`, está bien, pero el resto del nombre se respeta.

La segunda entrega no borra la primera: se le agrega encima.

## Cómo tomar la captura

La que sirve es la de la **página del curso terminado**, donde se vea tu
nombre y el 100 %. No sirve una del certificado en PDF sin contexto, ni una
donde no se distinga de qué curso es.

Recorta lo que sobre, pero deja visible el nombre del curso y tu usuario.
