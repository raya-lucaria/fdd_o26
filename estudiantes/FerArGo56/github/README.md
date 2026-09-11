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

Tres archivos, con estos nombres exactos:

| Archivo | Qué es |
|---|---|
| `certificaciones.md` | La plantilla, llena con tus datos |
| `introduccion-a-git.png` | Captura de haber terminado el primer curso |
| `git-intermedio.png` | Captura de haber terminado el segundo curso |

Los nombres no se inventan ni se traducen. Si tu captura es `.jpg` en vez de
`.png`, está bien, pero el resto del nombre se respeta.

## Cómo tomar la captura

La que sirve es la de la **página del curso terminado**, donde se vea tu
nombre y el 100 %. No sirve una del certificado en PDF sin contexto, ni una
donde no se distinga de qué curso es.

Recorta lo que sobre, pero deja visible el nombre del curso y tu usuario.
