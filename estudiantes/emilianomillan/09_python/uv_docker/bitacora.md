# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: emilianomillan
- Usuario de Docker Hub: emilianomillan

## El paquete que agregaste

Paquete: humanize

Para qué lo usa tu fila: mi fila "Tamaño del ambiente" calcula con la función `tamano()` cuántos bytes ocupa el ambiente (`sys.prefix`), y `humanize.naturalsize` los convierte a un texto legible, como 7.9 MB.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
                                Mi ambiente                                
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                                             ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.14.7                                            │
│ Intérprete          │ C:\Users\EmilianoMillan\fdd_o26_uvdocker\estudian │
│                     │ tes\emilianomillan\09_python\uv_docker\.venv\Scri │
│                     │ pts\python.exe                                    │
│ sys.prefix          │ C:\Users\EmilianoMillan\fdd_o26_uvdocker\estudian │
│                     │ tes\emilianomillan\09_python\uv_docker\.venv      │
│ ¿En un ambiente?    │ sí                                                │
│ Sistema             │ Windows AMD64                                     │
│ Tamaño del ambiente │ 7.9 MB                                            │
└─────────────────────┴───────────────────────────────────────────────────┘
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

Igual: las versiones de los cinco paquetes (humanize 4.16.0, rich 15.0.0, Pygments 2.21.0, markdown-it-py 4.2.0, mdurl 0.1.2), porque `uv.lock` las fija y la imagen instala con `uv sync --locked`.
Distinto: el intérprete (Python 3.14.7 en mi máquina, 3.13.16 en el contenedor), el sistema (Windows AMD64 contra Linux x86_64) y las rutas; el lock fija paquetes, no el intérprete: mi uv usó el Python que tenía y la imagen trae el de `python:3.13-slim`.
También cambió el tamaño del ambiente (7.9 MB contra 7.2 MB), probablemente porque Windows y Linux instalan archivos distintos para los mismos paquetes.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/emilianomillan/reporte

Digest: sha256:7056a0f76930d89de3f8c4840bad71e39f826756aae07640e8ec3e5c4f9751e1

Comando para correrla: docker run --rm --platform linux/amd64 emilianomillan/reporte

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
Removing login credentials for https://index.docker.io/v1/
Untagged: emilianomillan/reporte:latest
Deleted: sha256:7056a0f76930d89de3f8c4840bad71e39f826756aae07640e8ec3e5c4f9751e1
Unable to find image 'emilianomillan/reporte:latest' locally
latest: Pulling from emilianomillan/reporte
d1e9215a7366: Pull complete
6f7963b29166: Pull complete 
3322fb4172de: Pull complete 
d90344fd6d1d: Pull complete 
f2218136751d: Pull complete 
44136fa355b3: Download complete
c67d776a3cea: Download complete 
Digest: sha256:7056a0f76930d89de3f8c4840bad71e39f826756aae07640e8ec3e5c4f9751e1
Status: Downloaded newer image for emilianomillan/reporte:latest
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