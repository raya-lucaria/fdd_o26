# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: Meyer03
- Usuario de Docker Hub: meyer03

## El paquete que agregaste

Paquete: platformdirs

Para qué lo usa tu fila: `user_cache_dir("reporte")` devuelve la carpeta donde el sistema operativo guardaría la caché de un programa llamado `reporte`. Sirve para ver que el mismo paquete, con la misma versión, responde distinto según el sistema en el que corre.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
                                                       Mi ambiente                                                       
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                              ┃ Valor                                                                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                           │ 3.13.5                                                                             │
│ Intérprete                       │ /Users/macnx/fdd/fdd_o26/estudiantes/Meyer03/09_python/uv_docker/.venv/bin/python3 │
│ sys.prefix                       │ /Users/macnx/fdd/fdd_o26/estudiantes/Meyer03/09_python/uv_docker/.venv             │
│ ¿En un ambiente?                 │ sí                                                                                 │
│ Sistema                          │ Darwin arm64                                                                       │
│ Caché del usuario (platformdirs) │ /Users/macnx/Library/Caches/reporte                                                │
└──────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ platformdirs   │ 4.12.3  │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
```

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text
                        Mi ambiente                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                              ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                           │ 3.13.16               │
│ Intérprete                       │ /app/.venv/bin/python │
│ sys.prefix                       │ /app/.venv            │
│ ¿En un ambiente?                 │ sí                    │
│ Sistema                          │ Linux x86_64          │
│ Caché del usuario (platformdirs) │ /root/.cache/reporte  │
└──────────────────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ platformdirs   │ 4.12.3  │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
```

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

- **Igual:** las versiones de todos los paquetes (rich 15.0.0, platformdirs 4.12.3, markdown-it-py 4.2.0, mdurl 0.1.2, Pygments 2.21.0), porque `uv.lock` fija la versión exacta de cada uno y el Dockerfile crea el ambiente con `uv sync --locked`.
- **Distinto:** Python 3.13.5 en mi Mac contra 3.13.16 en el contenedor, Darwin arm64 contra Linux x86_64, y las rutas del intérprete y de mi fila (`/Users/macnx/Library/Caches/reporte` contra `/root/.cache/reporte`).
- **Por qué:** el lock fija paquetes, no el intérprete. `requires-python = ">=3.13"` acepta cualquier 3.13 y el contenedor usa el Python que trae `python:3.13-slim`. Mi fila cambia porque platformdirs sigue la convención de cada sistema operativo.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/meyer03/reporte

Digest: sha256:498a2833ced04b16011611a34a2a9efbcd8786abf4a2fac3b2751f94a52fad65

Comando para correrla: `docker run --rm --platform linux/amd64 meyer03/reporte`

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
$ docker logout
Removing login credentials for https://index.docker.io/v1/
$ docker rmi -f meyer03/reporte
Untagged: meyer03/reporte:latest
Deleted: sha256:498a2833ced04b16011611a34a2a9efbcd8786abf4a2fac3b2751f94a52fad65
Unable to find image 'meyer03/reporte:latest' locally
latest: Pulling from meyer03/reporte
221de9519945: Pulling fs layer
2a90c10bc160: Pulling fs layer
6ad7127f9180: Pulling fs layer
14deef4d6a0d: Pulling fs layer
d2e25b362b9e: Pulling fs layer
44136fa355b3: Download complete
221de9519945: Already exists
2a90c10bc160: Already exists
6ad7127f9180: Already exists
14deef4d6a0d: Already exists
d2e25b362b9e: Already exists
0fbf24176c37: Download complete
2a90c10bc160: Pull complete
6ad7127f9180: Pull complete
14deef4d6a0d: Pull complete
221de9519945: Pull complete
d2e25b362b9e: Pull complete
Digest: sha256:498a2833ced04b16011611a34a2a9efbcd8786abf4a2fac3b2751f94a52fad65
Status: Downloaded newer image for meyer03/reporte:latest
                        Mi ambiente                         
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                              ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python                           │ 3.13.16               │
│ Intérprete                       │ /app/.venv/bin/python │
│ sys.prefix                       │ /app/.venv            │
│ ¿En un ambiente?                 │ sí                    │
│ Sistema                          │ Linux x86_64          │
│ Caché del usuario (platformdirs) │ /root/.cache/reporte  │
└──────────────────────────────────┴───────────────────────┘
    Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ platformdirs   │ 4.12.3  │
│ rich           │ 15.0.0  │
└────────────────┴─────────┘
```
```
