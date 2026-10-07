# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub:nat-aglo
- Usuario de Docker Hub:nataglo

## El paquete que agregaste

Paquete:numpy

Para qué lo usa tu fila:calcular la media de numeros dentro de una tupla

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
<!-- salida local -->
nat@nat-Latitude-7490:~/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker$ uv run reporte.py
                                                         Mi ambiente
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                        ┃ Valor                                                                                        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                     │ 3.13.16                                                                                      │
│ Intérprete                 │ /home/nat/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker/.venv/bin/python │
│ sys.prefix                 │ /home/nat/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker/.venv            │
│ ¿En un ambiente?           │ sí                                                                                           │
│ Sistema                    │ Linux x86_64                                                                                 │
│ Media de tupla de números: │ 6.0                                                                                          │
└────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ numpy          │ 2.5.3   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘

```


## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text
<!-- salida contenedor -->
nat@nat-Latitude-7490:~/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker$ docker run --rm --platform linux/amd64 nataglo/reporte                     Mi ambiente                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                        ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                     │ 3.13.16               │
│ Intérprete                 │ /app/.venv/bin/python │
│ sys.prefix                 │ /app/.venv            │
│ ¿En un ambiente?           │ sí                    │
│ Sistema                    │ Linux x86_64          │
│ Media de tupla de números: │ 6.0                   │
└────────────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ numpy          │ 2.5.3   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘

```

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

<!-- que cambio
Igual: los paquetes con sus versiones, porque uv.lock las fija y uv sync --locked instaló esas mismas en el contenedor; también el sistema (Linux x86_64),porque el contenedor comparte el kernel de mi pc. Python salió 3.13.16 en ambos por el FROM python:3.13-slim de la imagen.
Distinto: el intérprete y el sys.prefix porque el contenedor trae su propio sistema de archivos y el WORKDIR es /app, donde copié pyproject.toml, uv.lock y reporte.py con "atajo" ./; como mi .venv no entró, uv creó otro ahí, en /app/.venv.
 -->

## Tu imagen en Docker Hub

URL pública:https://hub.docker.com/r/nataglo/reporte

Digest:sha256:a49d3edf47502de4d6eb1f4f2143a807623fc0a2b81fcd33ed37b57c204a7851

Comando para correrla:

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
<!-- prueba de pull -->
nat@nat-Latitude-7490:~/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker$ docker logout
Removing login credentials for https://index.docker.io/v1/
nat@nat-Latitude-7490:~/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker$ docker rmi -f nataglo/reporte
Untagged: nataglo/reporte:latest
Deleted: sha256:a49d3edf47502de4d6eb1f4f2143a807623fc0a2b81fcd33ed37b57c204a7851
nat@nat-Latitude-7490:~/Fuentes/fdd_o26_nat-aglo/estudiantes/nat-aglo/09_python/uv_docker$ docker run --rm --platform linux/amd64 nataglo/reporte
Unable to find image 'nataglo/reporte:latest' locally
latest: Pulling from nataglo/reporte
44136fa355b3: Already exists 
7bb6ccaaa5d7: Pull complete 
204d0e0744d9: Pull complete 
21ec4f411a88: Pull complete 
38140727eca3: Pull complete 
ae53c7cf0da1: Pull complete 
e4c663b964dd: Download complete 
Digest: sha256:a49d3edf47502de4d6eb1f4f2143a807623fc0a2b81fcd33ed37b57c204a7851
Status: Downloaded newer image for nataglo/reporte:latest
                     Mi ambiente                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                        ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                     │ 3.13.16               │
│ Intérprete                 │ /app/.venv/bin/python │
│ sys.prefix                 │ /app/.venv            │
│ ¿En un ambiente?           │ sí                    │
│ Sistema                    │ Linux x86_64          │
│ Media de tupla de números: │ 6.0                   │
└────────────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ numpy          │ 2.5.3   │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘

```
