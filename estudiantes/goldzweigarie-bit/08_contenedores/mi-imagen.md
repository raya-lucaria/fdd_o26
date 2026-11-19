# Mi imagen en Docker Hub

## Quién soy, en los dos lados

- Usuario de GitHub: goldzweigarie-bit
- Usuario de Docker Hub: goldz177

## La URL pública

URL: https://hub.docker.com/r/goldz177/app-docker

## El digest

```text
$ docker buildx imagetools inspect goldz177/app-docker:latest | grep -m1 Digest
Digest:    sha256:4f2bb0ecd65ff4d51a3adc34ae8204bd24e30249de1a6913ef3f263d6dac5596
```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm --platform linux/amd64 goldz177/app-docker:latest
```

Salida que debo esperar (el hostname, la fecha de ejecución, los procesos y la
memoria cambian en cada corrida; las tres últimas líneas son las de `info.sh`):

```text
=== Información del sistema ===
Hostname: 4ca1defec166
Usuario: root
Directorio: /app
Fecha: Thu Nov 19 17:06:04 UTC 2026
Kernel: 6.12.76-linuxkit

=== Procesos ===
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1 37.5  0.1 226656  6644 ?        Ss   17:06   0:00 /run/rosetta/rosetta /bin/bash /bin/bash ./info.sh
root        12 50.0  0.1 230188  7384 ?        R    17:06   0:00 /usr/bin/ps ps aux

=== Memoria ===
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       663Mi       2.5Gi        19Mi       852Mi       3.2Gi
Swap:          1.0Gi          0B       1.0Gi

=== Disco ===
Filesystem      Size  Used Avail Use% Mounted on
overlay         224G   15G  198G   7% /
GitHub: goldzweigarie-bit
Fecha de build: 2026-11-19 17:05:21 UTC
Dato extra: arquitectura x86_64, 8 CPUs
```

## La prueba de que se baja del registro

```text
$ docker logout
$ docker rmi -f goldz177/app-docker:latest
$ docker run --rm --platform linux/amd64 goldz177/app-docker:latest
Removing login credentials for https://index.docker.io/v1/
Untagged: goldz177/app-docker:latest
Deleted: sha256:4f2bb0ecd65ff4d51a3adc34ae8204bd24e30249de1a6913ef3f263d6dac5596
Unable to find image 'goldz177/app-docker:latest' locally
latest: Pulling from goldz177/app-docker
030f6b49a70a: Pulling fs layer
f0aa858f5bcc: Pulling fs layer
ef579fe15e0e: Pulling fs layer
f0aa858f5bcc: Already exists
ef579fe15e0e: Already exists
44136fa355b3: Already exists
030f6b49a70a: Already exists
f0aa858f5bcc: Pull complete
ef579fe15e0e: Pull complete
030f6b49a70a: Pull complete
21fe7c88dd6a: Download complete
Digest: sha256:4f2bb0ecd65ff4d51a3adc34ae8204bd24e30249de1a6913ef3f263d6dac5596
Status: Downloaded newer image for goldz177/app-docker:latest
=== Información del sistema ===
Hostname: 4ca1defec166
Usuario: root
Directorio: /app
Fecha: Thu Nov 19 17:06:04 UTC 2026
Kernel: 6.12.76-linuxkit

=== Procesos ===
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1 37.5  0.1 226656  6644 ?        Ss   17:06   0:00 /run/rosetta/rosetta /bin/bash /bin/bash ./info.sh
root        12 50.0  0.1 230188  7384 ?        R    17:06   0:00 /usr/bin/ps ps aux

=== Memoria ===
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       663Mi       2.5Gi        19Mi       852Mi       3.2Gi
Swap:          1.0Gi          0B       1.0Gi

=== Disco ===
Filesystem      Size  Used Avail Use% Mounted on
overlay         224G   15G  198G   7% /
GitHub: goldzweigarie-bit
Fecha de build: 2026-11-19 17:05:21 UTC
Dato extra: arquitectura x86_64, 8 CPUs
```

## El tamaño

```text
$ docker images goldz177/app-docker
IMAGE                        ID             DISK USAGE   CONTENT SIZE   EXTRA
goldz177/app-docker:latest   4f2bb0ecd65f        117MB         29.8MB        
```
