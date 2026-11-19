# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub:geraVillV
- Usuario de Docker Hub:geraplayer

## El paquete que agregaste

Paquete:humanize

Para qué lo usa tu fila: Para convertir el número 1000000 a una representación más legible con separadores de miles: 1,000,000.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

                                                 Mi ambiente                                                 
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                                                                                  ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.14.7                                                                                 │
│ Intérprete       │ /home/geralinux/fdd/fdd_o26/estudiantes/geraVillV/09_python/uv_docker/.venv/bin/python │
│ sys.prefix       │ /home/geralinux/fdd/fdd_o26/estudiantes/geraVillV/09_python/uv_docker/.venv            │
│ ¿En un ambiente? │ sí                                                                                     │
│ Sistema          │ Linux x86_64                                                                           │
│ Humanize         │ 1,000,000                                                                              │
└──────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ Pygments       │ 2.21.0  │
│ humanize       │ 4.16.0  │
│ humanize       │ 4.16.0  │
│ markdown-it-py │ 4.2.0   │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ mdurl          │ 0.1.2   │
│ rich           │ 15.0.0  │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘


## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

                Mi ambiente                 
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16               │
│ Intérprete       │ /app/.venv/bin/python │
│ sys.prefix       │ /app/.venv            │
│ ¿En un ambiente? │ sí                    │
│ Sistema          │ Linux x86_64          │
│ Humanize         │ 1,000,000             │
└──────────────────┴───────────────────────┘
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


## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

Las versiones de los paquetes fueron iguales dentro y fuera del contenedor porque uv.lock fija las versiones exactas de las dependencias.
El intérprete cambió: en mi máquina se usó Python 3.14.7 y dentro del contenedor Python 3.13.16, porque pyproject.toml permite Python >=3.13 y la imagen base usa python:3.13-slim.
También cambiaron las rutas del ambiente: localmente vive dentro de mi repositorio y en el contenedor está en /app/.venv, pero ambos corren dentro de un ambiente virtual.

<!-- que cambio -->

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/geraplayer/uv-reporte

Digest: geraplayer/uv-reporte@sha256:50add242cfb099d924bf431bdb0b9b0f39fa5dd9cd922cc75fcabbe85087dd05 size: 856


Comando para correrla: docker run --rm geraplayer/uv-reporte:latest

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

docker logout
Removing login credentials for https://index.docker.io/v1/

docker rmi -f geraplayer/uv-reporte:latest
Untagged: geraplayer/uv-reporte:latest
Deleted: sha256:50add242cfb099d924bf431bdb0b9b0f39fa5dd9cd922cc75fcabbe85087dd05


docker run --rm geraplayer/uv-reporte:latest
Unable to find image 'geraplayer/uv-reporte:latest' locally
latest: Pulling from geraplayer/uv-reporte
65a67aec859c: Pull complete 
3a5db7051419: Pull complete 
2e26907f3067: Pull complete 
66be4a4de672: Pull complete 
c11c6cfc49c0: Pull complete 
dc050f4de2dc: Pull complete 
2f5b06adfd91: Pull complete 
0b2def5265bb: Pull complete 
ecc510c1e359: Pull complete 
44136fa355b3: Already exists 
10c14793df22: Download complete 
Digest: sha256:50add242cfb099d924bf431bdb0b9b0f39fa5dd9cd922cc75fcabbe85087dd05
Status: Downloaded newer image for geraplayer/uv-reporte:latest
                Mi ambiente                 
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16               │
│ Intérprete       │ /app/.venv/bin/python │
│ sys.prefix       │ /app/.venv            │
│ ¿En un ambiente? │ sí                    │
│ Sistema          │ Linux x86_64          │
│ Humanize         │ 1,000,000             │
└──────────────────┴───────────────────────┘
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

