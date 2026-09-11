# Bitácora de la unidad 07

Llena este archivo en **tu copia**, dentro de `estudiantes/<tu-login>/07_git/`.
No edites el original.

## Quién soy

- Nombre: José Roberto Uribe Clemente
- Usuario de GitHub: RobertoUribeClemente

## Qué corrí

Pega aquí la salida de estos dos comandos, tal como te respondieron:

```text
git remote -v
origin    git@github.com:RobertoUribeClemente/fdd_o26_RobertoUribeClemente.git (fetch)

origin    git@github.com:RobertoUribeClemente/fdd_o26_RobertoUribeClemente.git (push)

upstream    git@github.com:raya-lucaria/fdd_o26.git (fetch)

upstream    git@github.com:raya-lucaria/fdd_o26.git (push) 



git log --oneline -3

366cb30 (HEAD -> entrega-07-git, origin/main, main) added my directory

76c4d43 (upstream/main, upstream/HEAD) docs(unidad-7): que hace cada comando del ritual, uno por uno

29f44cf docs(unidad-7): explica para que sirve el grep de los marcadores 


```

## Una cosa que se me rompió

Describe en tres o cuatro líneas algo que te haya salido mal durante la
unidad y cómo lo resolviste. Puede ser un conflicto, un push rechazado, un
archivo que no aparecía en `git status`, lo que sea. Si de verdad no se te
rompió nada, dilo y explica qué parte te costó más entender.


Durante la práctica se me rompió la sincronización del repositorio local al intentar empujar
cambios directamente a la rama main en lugar de aislar el trabajo en una rama dividida. La revisión
automática lo rechazó con un error. Lo resolví haciendo un reset duro a la rama principal de upstream
para limpiar el árbol de trabajo, creando una rama dedicada con git checkout -b y volviendo a enviar
los cambios por el flujo completo.
