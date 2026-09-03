# estudiantes

Una carpeta por persona. **La tuya se llama exactamente como tu usuario de
GitHub**, con sus mismas mayúsculas y sus mismos guiones.

Ese nombre no se teclea, se obtiene:

```bash
cd ~/fdd/fdd_o26
U=$(gh api user --jq .login) && echo "$U"
mkdir -p estudiantes/$U
touch estudiantes/$U/.gitkeep
```

Sin `gh` instalado, tu login es el campo *Username* de
https://github.com/settings/profile

## Las reglas

1. Sólo escribes dentro de `estudiantes/<tu-login>/`. Nada fuera.
2. Tu carpeta es un espejo de `codigo/`: misma ruta, mismo nombre.
3. Una branch por tarea. Nunca entregues desde `main`.
4. Nada de `.DS_Store`, `__pycache__/`, `.env` ni `node_modules/`, ni siquiera
   dentro de tu carpeta.
5. Un pull request rechazado se corrige con `push` a la misma branch. No abras
   otro.

Una revisión automática comprueba las cinco cosas en cada pull request. El
flujo completo está en https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/
