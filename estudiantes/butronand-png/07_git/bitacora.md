# Bitácora de la unidad 07

## Quién soy

- Nombre: Andre Butron
- Usuario de GitHub: butronand-png

## Qué corrí

```text
git remote -v
origin    git@github.com:butronand-png/fdd_o26.git (fetch)
origin    git@github.com:butronand-png/fdd_o26.git (push)
upstream  git@github.com:raya-lucaria/fdd_o26.git (fetch)
upstream  git@github.com:raya-lucaria/fdd_o26.git (push)

git log --oneline -3
c2b9ba4 (HEAD -> 07_git, upstream/main, upstream/HEAD, main) feat(unidad-7): tarea de las dos certificaciones de DataCamp
11044ad feat(unidad-7): el trabajo en paralelo, explicado con diagramas
d8f27d4 refactor(unidad-7): parte la unidad en dos secciones, Git y GitHub
```

## Una cosa que se me rompió

Mi único remote era `origin` y apuntaba al repositorio del profesor por HTTPS,
así que después de hacer el fork no tenía a dónde hacer push. Lo resolví
renombrando ese remote a `upstream`, cambiándole la dirección a SSH con
`git remote set-url`, y agregando un `origin` nuevo hacia mi fork. Lo que
aprendí es que `origin` no significa "el original": es sólo una etiqueta, y el
nombre no dice nada sobre a dónde apunta.
