# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: FerArGo56
- Usuario de Docker Hub: ferargo

## El paquete que agregaste

Paquete: humanize

Para qué lo usa tu fila: mi fila "Tamaño del ambiente" usa `humanize.naturalsize()` para mostrar en formato legible (por ejemplo, 7.2 MB) cuántos bytes ocupa la carpeta del ambiente (`sys.prefix`), que se mide con la función `tamano()`.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
                                  Mi ambiente                                   
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                                                  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.11                                                │
│ Intérprete          │ /Users/anamari/itam/fdd_o26_FerArGo56/estudiantes/FerA │
│                     │ rGo56/09_python/uv_docker/.venv/bin/python3            │
│ sys.prefix          │ /Users/anamari/itam/fdd_o26_FerArGo56/estudiantes/FerA │
│                     │ rGo56/09_python/uv_docker/.venv                        │
│ ¿En un ambiente?    │ sí                                                     │
│ Sistema             │ Darwin x86_64                                          │
│ Tamaño del ambiente │ 7.2 MB                                                 │
└─────────────────────┴────────────────────────────────────────────────────────┘
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

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text
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

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

- Igual: las versiones de los cinco paquetes (rich 15.0.0, humanize 4.16.0, Pygments 2.21.0, markdown-it-py 4.2.0, mdurl 0.1.2), que estemos en un ambiente y su tamaño (7.2 MB).
- Distinto: la versión de Python (3.13.11 en mi Mac contra 3.13.16 en el contenedor), la ruta del intérprete y de sys.prefix (/Users/... contra /app/.venv) y el sistema (Darwin contra Linux).
- Por qué: uv.lock fija la versión exacta y el hash de cada paquete, así que se instalan los mismos en los dos lados; pero no fija el intérprete ni el sistema operativo: en mi Mac el Python lo pone uv y en el contenedor sale de la imagen base python:3.13-slim.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/ferargo/reporte

Digest: sha256:613253770f287594cf3b4291c027cb2c256e91a9a4d99f7cbe9fc0fa5df198e4

Comando para correrla:

```bash
docker run --rm --platform linux/amd64 ferargo/reporte
```

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
$ docker logout
Removing login credentials for https://index.docker.io/v1/
$ docker rmi -f
Untagged: ferargo/reporte:latest
Deleted: sha256:613253770f287594cf3b4291c027cb2c256e91a9a4d99f7cbe9fc0fa5df198e4
$ docker run
Unable to find image 'ferargo/reporte:latest' locally
latest: Pulling from ferargo/reporte
44136fa355b3: Already exists
ce7f6c5a94de: Pulling fs layer
e429aa722133: Pulling fs layer
30a9b69a8d9c: Pulling fs layer
1315b46eb740: Pulling fs layer
a3233247dfce: Pulling fs layer
ce7f6c5a94de: Already exists
e429aa722133: Already exists
30a9b69a8d9c: Already exists
1315b46eb740: Already exists
a3233247dfce: Already exists
a2f32df26a13: Download complete
30a9b69a8d9c: Pull complete
e429aa722133: Pull complete
a3233247dfce: Pull complete
ce7f6c5a94de: Pull complete
1315b46eb740: Pull complete
Digest: sha256:613253770f287594cf3b4291c027cb2c256e91a9a4d99f7cbe9fc0fa5df198e4
Status: Downloaded newer image for ferargo/reporte:latest
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
