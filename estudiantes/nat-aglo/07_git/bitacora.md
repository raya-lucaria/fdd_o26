# Bitácora de la unidad 07

Llena este archivo en **tu copia**, dentro de `estudiantes/<tu-login>/07_git/`.
No edites el original.

## Quién soy

- Nombre: Natalia Agredo López
- Usuario de GitHub: nat-aglo

## Qué corrí

Pega aquí la salida de estos dos comandos, tal como te respondieron:

```text
git remote -v
origin	git@github.com:nat-aglo/fdd_o26_nat-aglo.git (fetch)
origin	git@github.com:nat-aglo/fdd_o26_nat-aglo.git (push)
upstream	git@github.com:raya-lucaria/fdd_o26.git (fetch)
upstream	git@github.com:raya-lucaria/fdd_o26.git (push)

git log --oneline -3
e1a3881 (HEAD -> tarea-07-git, upstream/main, upstream/HEAD, origin/main, main) Merge pull request #32 from goldzweigarie-bit/tarea-certificacion-git-intermedio
9ed4f59 feat(certificaciones): entrega Intermediate Git de DataCamp
97d3c44 Merge pull request #26 from butronand-png/07_datacamp

```

## Una cosa que se me rompió

Todo esto se me rompio horrible. Mi bitacora salia vacia. Intente algo que ahora pensandolo mejor estuvo muy mal: rm -r 07_git para deshacerme de lo que estaba mal. No me salio, ni supe porque no. Le pregunte mejor a gemini con contexto de mi situacion(imagenes, explicacion, su explicacion) y me pidio verificara contenido de $GHUSER. Segun yo si verifique, pero al hacerlo de nuevo estaba vacia y me indico que probablemente al no estar en mi raiz del repositorio y por la variable, copie una carpeta vacia y obvio lo demas saldria en blanco. Me indico que regresara a mi raiz (miusuario-copiadefddsuyo) asignara la variable y sincronizara con el main.
