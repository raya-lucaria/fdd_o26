# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Cristopher Góngora
- Usuario de GitHub: cristoredentor
- Usuario de Docker Hub: cristophergongs

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text

docker version

Client: Docker Engine - Community
 Version:           29.8.1
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        4a63305
 Built:             Tue Sep 15 16:25:42 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.8.1
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       464cd50
  Built:            Tue Sep 15 16:25:42 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.3.5
  GitCommit:        1294c24a7da8e5a793ed378161673abe94118892
 runc:
  Version:          1.5.1
  GitCommit:        v1.5.1-0-g8f2685a4
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0


docker images
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
cristophergongs/hola:v1   b8fbf3117ec8       12.1MB         3.63MB        
hola:latest               b8fbf3117ec8       12.1MB         3.63MB        
ubuntu:latest             da6fc2be5478        160MB         45.3MB    U   


docker history <tu-usuario>/<tu-imagen>
cris@laptop-cris:~/fdd/docker-lab/hola$ docker history cristophergongs/hola:v1
IMAGE          CREATED        CREATED BY                                      SIZE      COMMENT
b8fbf3117ec8   5 months ago   CMD ["echo" "hola desde mi imagen"]             0B        buildkit.dockerfile.v0
<missing>      5 months ago   CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      5 months ago   ADD alpine-minirootfs-3.20.10-x86_64.tar.gz …   8.47MB    buildkit.dockerfile.v0


```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1.Utiliza python latest, lo cual está mal porque la imágen de hoy no es la de mañana porque latest se va actualizando, aparte hace que la imágen pese más. 
Lo que hice fue cambiarlo  por `python:3.12-slim` para fijar la versión y reducir el tamaño.

2.Tiene copy .. antes del run pip install, esto esta mál pues cualquier cambio en tu código invalidaría la caché y reinstalaría todas las
 dependencias cada vez.  Separé primero `COPY requirements.txt .`, después `RUN pip install -r requirements.txt` y al final `COPY . .`.

 
3.No hay ninguna instricción user, por lo que el programa se ejecutaba como `root`. Creé el usuario `app`, le di acceso a `/app` y agregué `USER app`.
 Lo comprobé con `docker run --rm roto-arreglado:v1 id`, que mostró `uid=1000(app)`. 

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.

Hasta ahora no me he dado cuenta de algo que se me haya roto. La parte que más se me complicó fue entender la anatomia del docker run  y entender porque  ejecutar dentro de un contenedor no cuesta. 
