
# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Dominique Ontiveros Arriaga
- Usuario de GitHub:Domdimad0m
- Usuario de Docker Hub:dominiqueont1. 

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version


docker images


docker history <tu-usuario>/<tu-imagen>


```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. La imagen base usaba `python:latest`. Esto hacía que la versión pudiera cambiar y además generaba una imagen más pesada. Lo cambié por `python:3.12-slim` para fijar la versión y reducir el tamaño.

2. Se hacía `COPY . .` antes de instalar las dependencias. Esto provoca que un cambio en el código pueda invalidar esa capa y obligar a instalar las dependencias otra vez. Separé primero `COPY requirements.txt .`, después `RUN pip install -r requirements.txt` y al final `COPY . .`.

3. No se especificaba un usuario, por lo que el programa se ejecutaba como `root`. Creé el usuario `app`, le di acceso a `/app` y agregué `USER app`. Lo comprobé con `docker run --rm roto-arreglado:v1 id`, que mostró `uid=1000(app)`.


## Una cosa que se me rompió

Al principio Docker estaba instalado en Windows, pero el comando no funcionaba desde mi terminal de WSL porque no estaba habilitada la integración. Después de activarla, Docker ya era reconocido, pero apareció un error de permisos al intentar conectarse a `/var/run/docker.sock`. Revisé mis grupos y vi que mi usuario no pertenecía al grupo `docker`. Lo agregué al grupo y después `docker version` ya pudo mostrar tanto Client como Server.
