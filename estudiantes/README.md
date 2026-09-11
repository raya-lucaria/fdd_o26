# estudiantes

Una carpeta por persona. **La tuya se llama exactamente como tu usuario de
GitHub**, con sus mismas mayúsculas y sus mismos guiones.

Ese nombre no se teclea, se obtiene:

```bash
cd ~/fdd/fdd_o26
echo "$GHUSER"   # tu login, del perfil de tu shell
mkdir -p estudiantes/$GHUSER
touch estudiantes/$GHUSER/.gitkeep
```

Tu login sale de la URL de tu fork, y se guarda una vez con
`export GHUSER=tu-login` en `~/.zshrc` o `~/.bashrc`.

## Las reglas

1. Sólo escribes dentro de `estudiantes/<tu-login>/`. Nada fuera.
2. Tu carpeta es un espejo de `codigo/`: misma ruta, mismo nombre.
3. Una branch por tarea. Nunca entregues desde `main`.
4. Nada de `.DS_Store`, `__pycache__/`, `.env` ni `node_modules/`, ni siquiera
   dentro de tu carpeta.
5. Un pull request rechazado se corrige con `push` a la misma branch. No abras
   otro.

Una revisión automática comprueba en cada pull request las reglas 1, 3 y 4, y
dice qué archivo falló y qué hacer. La regla 2, la del espejo, la reviso yo:
una subcarpeta con el nombre equivocado pasa en verde y de todos modos está
mal entregada. El flujo completo está en https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/
