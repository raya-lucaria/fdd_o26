# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: butronand-png
- Usuario de Docker Hub: abutrxn

## El paquete que agregaste

Paquete: humanize

Para qué lo usa tu fila: la fila "Tamaño del ambiente" suma con `tamano(sys.prefix)` los bytes de la carpeta del ambiente activo, y `humanize.naturalsize()` los convierte a un valor legible.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

````text
                                            Mi ambiente                                             
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                                                                      ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.5                                                                     │
│ Intérprete          │ /Users/andrebutron/Code/itam/fdd_o26/estudiantes/butronand-png/09_python/u │
│                     │ v_docker/.venv/bin/python3                                                 │
│ sys.prefix          │ /Users/andrebutron/Code/itam/fdd_o26/estudiantes/butronand-png/09_python/u │
│                     │ v_docker/.venv                                                             │
│ ¿En un ambiente?    │ sí                                                                         │
│ Sistema             │ Darwin arm64                                                               │
│ Tamaño del ambiente │ 7.2 MB                                                                     │
└─────────────────────┴────────────────────────────────────────────────────────────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ humanize       │ 4.16.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
````

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

````text
                  Mi ambiente                  
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.16               │
│ Intérprete          │ /app/.venv/bin/python │
│ sys.prefix          │ /app/.venv            │
│ ¿En un ambiente?    │ sí                    │
│ Sistema             │ Linux x86_64          │
│ Tamaño del ambiente │ 7.2 MB                │
└─────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ humanize       │ 4.16.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
````

## Qué cambió y qué no

- Igual: las versiones de los cinco paquetes (rich 15.0.0, humanize 4.16.0, markdown-it-py 4.2.0, mdurl 0.1.2, Pygments 2.21.0), porque las dos instalaciones salieron del mismo uv.lock. El tamaño del ambiente también coincide: 7.2 MB.
- Distinto: Python 3.13.5 en mi Mac contra 3.13.16 en el contenedor; el intérprete y sys.prefix (el .venv de mi carpeta contra /app/.venv); y el sistema, Darwin arm64 contra Linux x86_64.
- Por qué: el lock fija paquetes, versiones y hashes, pero no el intérprete. pyproject.toml sólo pide Python >=3.13; en el contenedor el intérprete viene de la imagen base python:3.13-slim y en mi Mac lo puso uv.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/abutrxn/reporte-uv

Digest: sha256:f2e8154d34516434212bbc977b480cec51112970b8da76af1e467621a1350eab

Comando para correrla: `docker run --rm --platform linux/amd64 abutrxn/reporte-uv:latest`

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

````text
$ docker logout
Removing login credentials for https://index.docker.io/v1/
$ docker rmi -f abutrxn/reporte-uv:latest reporte-uv
Untagged: abutrxn/reporte-uv:latest
Untagged: reporte-uv:latest
Deleted: sha256:f2e8154d34516434212bbc977b480cec51112970b8da76af1e467621a1350eab
$ docker run --rm --platform linux/amd64 abutrxn/reporte-uv:latest
Unable to find image 'abutrxn/reporte-uv:latest' locally
latest: Pulling from abutrxn/reporte-uv
d403a2f4c72a: Pulling fs layer
a02920c686df: Pulling fs layer
ce6e6ffe9521: Pulling fs layer
d4ebc021ed7c: Pulling fs layer
db3c45ee5a24: Pulling fs layer
d4ebc021ed7c: Already exists
db3c45ee5a24: Already exists
d403a2f4c72a: Already exists
a02920c686df: Already exists
ce6e6ffe9521: Already exists
d4ebc021ed7c: Pull complete
db3c45ee5a24: Pull complete
ce6e6ffe9521: Pull complete
d403a2f4c72a: Pull complete
a02920c686df: Pull complete
94fa4d0cf395: Download complete
Digest: sha256:f2e8154d34516434212bbc977b480cec51112970b8da76af1e467621a1350eab
Status: Downloaded newer image for abutrxn/reporte-uv:latest
                  Mi ambiente                  
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.16               │
│ Intérprete          │ /app/.venv/bin/python │
│ sys.prefix          │ /app/.venv            │
│ ¿En un ambiente?    │ sí                    │
│ Sistema             │ Linux x86_64          │
│ Tamaño del ambiente │ 7.2 MB                │
└─────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ humanize       │ 4.16.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
```
