# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub:jpmedinae
- Usuario de Docker Hub:jpmedinae

## El paquete que agregaste

Paquete:humanize

Para qué lo usa tu fila:muestra el tamaño del ambiente virtual de forma legible

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
                                         Mi ambiente                                         
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                                                               ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.14.4                                                              │
│ Intérprete          │ /home/jp/itam/fdd_o26_jpmedinae/estudiantes/jpmedinae/09_python/uv_ │
│                     │ docker/.venv/bin/python                                             │
│ sys.prefix          │ /home/jp/itam/fdd_o26_jpmedinae/estudiantes/jpmedinae/09_python/uv_ │
│                     │ docker/.venv                                                        │
│ ¿En un ambiente?    │ sí                                                                  │
│ Sistema             │ Linux x86_64                                                        │
│ Tamaño del ambiente │ 7.5 MB                                                              │
└─────────────────────┴─────────────────────────────────────────────────────────────────────┘
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

Ambos corren en Linux x86_64  dentro del ambiente virtual y tienen las mismas versiones de los paquetes. Sin embargo, en mi compu corre Python 3.14.4 y en el contenedor corre Python 3.13.16. Esto porque el contenedor usa una imagen con esa versión.

## Tu imagen en Docker Hub

URL pública:https://hub.docker.com/r/jpmedinae/reporte

Digest:sha256:29137f8856b194525f8c4d442641652be21a1e926e14cfd953a3d0f5cd6c882d

Comando para correrla:docker run --rm --platform linux/amd64 jpmedinae/reporte

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
Removing login credentials for https://index.docker.io/v1/
Untagged: jpmedinae/reporte:latest
Deleted: sha256:29137f8856b194525f8c4d442641652be21a1e926e14cfd953a3d0f5cd6c882d
Unable to find image 'jpmedinae/reporte:latest' locally
latest: Pulling from jpmedinae/reporte
355556cac562: Pull complete 
da56fd6f2eb6: Pull complete 
5d3b2706ee65: Pull complete 
b8ad0c73f0ab: Pull complete 
68babbb907f7: Pull complete 
44136fa355b3: Already exists 
2d7a6645667d: Download complete 
Digest: sha256:29137f8856b194525f8c4d442641652be21a1e926e14cfd953a3d0f5cd6c882d
Status: Downloaded newer image for jpmedinae/reporte:latest
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
