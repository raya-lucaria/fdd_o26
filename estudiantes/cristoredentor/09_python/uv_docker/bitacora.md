# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: cristoredentor
- Usuario de Docker Hub: cristophergongs

## El paquete que agregaste

Paquete: numpy

Para qué lo usa tu fila: para dar el promedio de un arreglo de numeros

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                                                                                                             ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.15                                                                                                           │
│ Intérprete       │ /home/cris/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/uv_docker/.venv/bin/python │
│ sys.prefix       │ /home/cris/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/uv_docker/.venv            │
│ ¿En un ambiente? │ sí                                                                                                                │
│ Sistema          │ Linux x86_64                                                                                                      │
│ numpy            │ 2.5.3 (promedio del array: 3.0)                                                                                                            │
└──────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
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

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                           ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16                         │
│ Intérprete       │ /app/.venv/bin/python           │
│ sys.prefix       │ /app/.venv                      │
│ ¿En un ambiente? │ sí                              │
│ Sistema          │ Linux x86_64                    │
│ numpy            │ 2.5.3 (promedio del array: 3.0) │
└──────────────────┴─────────────────────────────────┘
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

Lo que cambio fue el tipo de python y el intérprete, antes era la carpeta en la cual tengo guardado el repositorio del curso y ahora quedo configurado desde app,
los paquetes quedaron iguales, igual el sistema y mi línea. La razón de esos cambios es que  en el docker tu especificas el intérprete para que no cambie de 
computadora a computadora a partir del directorio app/ y con python 3.13.16


## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/cristophergongs/reporte

Digest: sha256:e892cafc879d17d0b0861ed8f4fa7128ba56da12f9bc01ba3ce944902d54b9c3

Comando para correrla: docker run --rm cristophergongs/reporte

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
<!-- prueba de pull -->

cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/uv_docker$ docker logout
Removing login credentials for https://index.docker.io/v1/
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/uv_docker$ docker rmi -f cristophergongs/reporte
Untagged: cristophergongs/reporte:latest
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/uv_docker$ docker run --rm --platform linux/amd64 cristophergongs/reporte
Unable to find image 'cristophergongs/reporte:latest' locally
latest: Pulling from cristophergongs/reporte
Digest: sha256:e892cafc879d17d0b0861ed8f4fa7128ba56da12f9bc01ba3ce944902d54b9c3
Status: Downloaded newer image for cristophergongs/reporte:latest
                     Mi ambiente                      
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                           ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16                         │
│ Intérprete       │ /app/.venv/bin/python           │
│ sys.prefix       │ /app/.venv                      │
│ ¿En un ambiente? │ sí                              │
│ Sistema          │ Linux x86_64                    │
│ numpy            │ 2.5.3 (promedio del array: 3.0) │
└──────────────────┴─────────────────────────────────┘
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

