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
   otro. La excepción: si lo rechazado es la branch misma (sale de `main` o su
   nombre no es de entrega), la entrega va en una branch nueva y cierras el viejo.

Una revisión automática corre en cada pull request. Comprueba que sólo
escribas dentro de tu carpeta y que se llame exactamente como tu login (1),
que no entregues desde `main` (3), que no subas basura (4), que el nombre de
tu branch tenga la forma `tarea-NN-nombre` en minúsculas y con guiones, y
que — cuando tu branch ya tiene carpeta asignada en el curso — la carpeta de
primer nivel que tocaste sea esa. Dice qué archivo falló, por qué y dónde
investigar.

Además, cada tarea nueva trae su propia revisión de contenido: que estén los
archivos que pide, llenos, y sus reglas propias. Esos mensajes dicen qué está
mal, por qué y dónde investigar; el cómo te toca a ti.

Lo que no comprueba es el resto del espejo (2): que la subcarpeta más
profunda se llame igual que en `codigo/`, y si lo que dice tu entrega es
cierto y está bien hecho. Eso lo reviso yo; la aprobación es la etiqueta
`entrega-aceptada`. El flujo completo está en https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/
