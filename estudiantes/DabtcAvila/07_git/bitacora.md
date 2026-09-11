# Bitácora de la unidad 07

## Quién soy

- Nombre: David Fernando Ávila Díaz
- Usuario de GitHub: DabtcAvila

## Qué corrí

```text
git remote -v
origin	git@github.com:DabtcAvila/fdd_o26dabtc.git (fetch)
origin	git@github.com:DabtcAvila/fdd_o26dabtc.git (push)
upstream	git@github.com:raya-lucaria/fdd_o26.git (fetch)
upstream	git@github.com:raya-lucaria/fdd_o26.git (push)

git log --oneline -3
c6bbd9c added my directory lol
76c4d43 docs(unidad-7): que hace cada comando del ritual, uno por uno
29f44cf docs(unidad-7): explica para que sirve el grep de los marcadores
```

## Una cosa que se me rompió

Se me rompieron dos cosas seguidas. Primero, `git remote -v` tenía los apodos
al revés: `origin` apuntaba a un repositorio que no existía y `upstream`
apuntaba a mi propio fork, así que `git fetch upstream` no bajaba nada del
curso. Lo arreglé con `git remote set-url` para cada uno y volví a revisar
que `origin` fuera mi fork y `upstream` el de raya-lucaria. Después, al hacer
`git push origin`, GitHub respondió `Permission denied (publickey)`: mi Mac
tenía llaves SSH para otras máquinas, pero ninguna registrada en GitHub.
Generé una nueva con `ssh-keygen -t ed25519`, pegué la pública en
Settings → SSH and GPG keys, y con `ssh -T git@github.com` confirmé que ya
me reconocía.
