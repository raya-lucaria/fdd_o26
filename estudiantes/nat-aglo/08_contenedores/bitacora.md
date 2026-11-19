# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre:Natalia Agredo López
- Usuario de GitHub:nat-aglo
- Usuario de Docker Hub:nataglo

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```
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

docker images                                                                                                                             i Info →   U  In Use
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.20                     d9e853e87e55       12.2MB         3.71MB        
hello-world:latest              5e2309035332       25.9kB         9.49kB        
nataglo/primera_imagen:latest   1bfc3e0dc5d3        177MB         43.3MB    U   
postgres:16                     a3b7f434b2dc        642MB          166MB        
postgres:17                     f4c66b820c6f        646MB          167MB        
python:3.12-slim                2f17fc044b57        179MB         45.4MB        
ubuntu:24.04                    008173c23f95        119MB         31.7MB    U  

docker history nataglo/primera_imagen:latest
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
1bfc3e0dc5d3   7 minutes ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      7 minutes ago   USER app                                        0B        buildkit.dockerfile.v0
<missing>      7 minutes ago   RUN /bin/sh -c useradd -m app && chown -R ap…   81.9kB    buildkit.dockerfile.v0
<missing>      7 minutes ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      2 hours ago     WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      3 days ago      CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      3 days ago      ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;  apt-get update;  a…   4.95MB    buildkit.dockerfile.v0
<missing>      3 days ago      ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      4 days ago      # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.6MB    debuerreotype 0.17
```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. La primera línea del FROM sólo decía latest como version, lo cual no me garantiza que mas adelante me vuelva a funcionar y/o que a otra
persona le funcione igual. Mejor asegurarse de ello indicando la version que quiero usar.
2. El COPY . . Pensandolo en sus capas, si se modifica app.py tendría que volver a copiar (pues ya no contiene las modificaciones) y volveria
a correr el archivo .txt siendo que no se modifico, saltandose la opcion de usar su cache. En cambio, si se parte COPY en dos para copiar
el .txt , le damos RUN con su comando al .txt , copiamos ahora si nuestras instrucciones y terminamos nuevamente con el CMD, si se modifica el .py solo repetira desde el segundo COPY, aprovechando el cache de requirements.txt  y ahorrandonos tiempo. 
3. No tiene USER, entonces por default estaria en root lo cual no es una buena practica, tengo demasiados permisos. Los necesito para las
primera instalaciones, pero luego lo mejor seria crear un usuario con permiso para modificaciones de los archivos del contenedor y cambiar a 
el.

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.
En la correccion del Dockerfile no entendia que hacia el COPY . . y porque estaba mal. En su repo, en los temas de Contenedores busque si
decia algo y encontre por que se debian dividir para aprovechar cache de uno suponiendo que se modifica el script.Igual aprovecho para 
comentar que me saco mucho de onda crear mi imagen, no me sentia preparada. Vi el scrip de un compañero y nada que ver, le metio cosas que no 
entiendo. Creo que ando atrasada o no se, vi cosas como LABEL y usos de ARG y ENV que no entendi.

