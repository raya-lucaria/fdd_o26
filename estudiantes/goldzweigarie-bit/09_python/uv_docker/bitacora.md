# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: goldzweigarie-bit
- Usuario de Docker Hub: goldz177

## El paquete que agregaste

Paquete: requests

Para qué lo usa tu fila: Lo usé para demostrar que un paquete externo se instala correctamente tanto en mi máquina como en el contenedor, y para tener una fila propia en el reporte.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text

                  Mi ambiente                  
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.2                │
│ Intérprete          │ /Users/ariegoldzweig/fdd/fdd_o26/fdd_o26_goldzweigarie-bit/estudiantes/goldzweigarie-bit/09_python/uv_docker/.venv/bin/python3 │
│ sys.prefix          │ /Users/ariegoldzweig/fdd/fdd_o26/fdd_o26_goldzweigarie-bit/estudiantes/goldzweigarie-bit/09_python/uv_docker/.venv │
│ ¿En un ambiente?    │ sí                    │
│ Sistema             │ Darwin arm64          │
│ Versión de Requests │ 2.34.2                │
└─────────────────────┴───────────────────────┘
       Paquetes instalados        
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Paquete            ┃ Versión   ┃
━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Pygments           │ 2.21.0    │
│ certifi            │ 2026.7.22 │
│ charset-normalizer │ 3.5.2     │
│ idna               │ 3.20      │
│ markdown-it-py     │ 4.2.0     │
│ mdurl              │ 0.1.2     │
│ requests           │ 2.34.2    │
│ rich               │ 15.0.0    │
│ urllib3            │ 2.8.0     │
└────────────────────┴───────────┘

```

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text

Unable to find image 'goldz177/uv-docker:latest' locally
latest: Pulling from goldz177/uv-docker
b9a2dbd7c8c7: Pull complete 
3c7dd35fd5c6: Pull complete 
3bc819c10bcd: Pull complete 
f27ecdf90668: Pull complete 
3f59dd987f58: Pull complete 
44136fa355b3: Already exists 
c9272815eca4: Download complete 
Digest: sha256:5022ac346eb9d71bcf40a203b181ed94ffb1dcf7e2fb18f97e6fe16c7cfd4d90
Status: Downloaded newer image for goldz177/uv-docker:latest
                  Mi ambiente                  
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.16               │
│ Intérprete          │ /app/.venv/bin/python │
│ sys.prefix          │ /app/.venv            │
│ ¿En un ambiente?    │ sí                    │
│ Sistema             │ Linux x86_64          │
│ Versión de Requests │ 2.34.2                │
└─────────────────────┴───────────────────────┘
       Paquetes instalados        
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Paquete            ┃ Versión   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Pygments           │ 2.21.0    │
│ certifi            │ 2026.7.22 │
│ charset-normalizer │ 3.5.2     │
│ idna               │ 3.20      │
│ markdown-it-py     │ 4.2.0     │
│ mdurl              │ 0.1.2     │
│ requests           │ 2.34.2    │
│ rich               │ 15.0.0    │
│ urllib3            │ 2.8.0     │
└────────────────────┴────────

```

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

Las versiones de los paquetes (rich 15.0.0, requests 2.34.2 y todas sus dependencias) son exactamente las mismas gracias a que uv.lock fija las versiones precisas.
La ruta del "Intérprete" y el valor de "sys.prefix". En mi máquina (Mac Apple Silicon) apunta a /Users/ariegoldzweig/.../.venv y muestra Darwin arm64, mientras que en el contenedor apunta a /app/.venv y muestra Linux x86_64.
Porque uv sync --frozen crea un ambiente virtual aislado dentro del contenedor, independiente del sistema operativo anfitrión, pero el lock file garantiza que las versiones de los paquetes sean idénticas en ambos ambientes.

## Tu imagen en Docker Hub

URL pública:https://hub.docker.com/r/goldz177/uv-docker 

Digest:sha256:5022ac346eb9d71bcf40a203b181ed94ffb1dcf7e2fb18f97e6fe16c7cfd4d90

Comando para correrla: docker run --rm --platform linux/amd64 goldz177/uv-docker:latest

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
$ docker logout
Removing login credentials for https://index.docker.io/v1/

$ docker rmi -f goldz177/uv-docker:latest
Untagged: goldz177/uv-docker:latest
Deleted: sha256:5022ac346eb9d71bcf40a203b181ed94ffb1dcf7e2fb18f97e6fe16c7cfd4d90

$ docker run --rm --platform linux/amd64 goldz177/uv-docker:latest
Unable to find image 'goldz177/uv-docker:latest' locally
latest: Pulling from goldz177/uv-docker
b9a2dbd7c8c7: Pull complete 
3c7dd35fd5c6: Pull complete 
3bc819c10bcd: Pull complete 
f27ecdf90668: Pull complete 
3f59dd987f58: Pull complete 
44136fa355b3: Already exists 
c9272815eca4: Download complete 
Digest: sha256:5022ac346eb9d71bcf40a203b181ed94ffb1dcf7e2fb18f97e6fe16c7cfd4d90
Status: Downloaded newer image for goldz177/uv-docker:latest
                  Mi ambiente                  
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.13.16               │
│ Intérprete          │ /app/.venv/bin/python │
│ sys.prefix          │ /app/.venv            │
│ ¿En un ambiente?    │ sí                    │
│ Sistema             │ Linux x86_64          │
│ Versión de Requests │ 2.34.2                │
└─────────────────────┴───────────────────────┘
       Paquetes instalados        
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Paquete            ┃ Versión   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Pygments           │ 2.21.0    │
│ certifi            │ 2026.7.22 │
│ charset-normalizer │ 3.5.2     │
│ idna               │ 3.20      │
│ markdown-it-py     │ 4.2.0     │
│ mdurl              │ 0.1.2     │
│ requests           │ 2.34.2    │
│ rich               │ 15.0.0    │
│ urllib3            │ 2.8.0     │
└────────────────────┴───────────┘
```
