# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: Domdimad0m
- Usuario de Docker Hub: dominiqueont

## El paquete que agregaste

Paquete: humanize

Para qué lo usa tu fila: Captura el valor del tamaño del ambiente en bits y lo imprime de forma legible para el humano.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
                                  Mi ambiente
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué                 ┃ Valor                                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python              │ 3.14.7                                                │
│ Intérprete          │ /home/dominiqueont/fdd_o26_domdom/estudiantes/Domdima │
│                     │ d0m/09_python/uv_docker/.venv/bin/python              │
│ sys.prefix          │ /home/dominiqueont/fdd_o26_domdom/estudiantes/Domdima │
│                     │ d0m/09_python/uv_docker/.venv                         │
│ ¿En un ambiente?    │ sí                                                    │
│ Sistema             │ Linux x86_64                                          │
│ Tamaño del ambiente │ 7.3 MB                                                │
└─────────────────────┴───────────────────────────────────────────────────────┘
    Paquetes instalados
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Paquete        ┃ Versión ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Pygments       │ 2.21.0  │
│ humanize       │ 4.16.0  │
│ markdown-it-py │ 4.2.0   │
│ mdurl          │ 0.1.2   │
│ rich           │ 15.0.0  │
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
```

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

Las versiones de los paquetes dentro y fuera del contenedor que necesita el código para funcionar en cualquier pc.
Cambió la versión del intérprete de Python, las rutas del ambiente y el tamaño del ambiente. Esto ocurre porque son dos ambientes distintos, uno creado en mi compu y otro creado dentro de Docker.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/dominiqueont/reporte

Digest: sha256:939e80d12654175516a413db65c2bbec61734a5dfdfbbe47da8ff713f80f8793

Comando para correrla: docker run --rm --platform linux/amd64 dominiqueont/reporte

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
dominiqueont@Domdom:~/fdd_o26_domdom/estudiantes/Domdimad0m/09_python/uv_docker$ docker push dominiqueont/reporte
Using default tag: latest
The push refers to repository [docker.io/dominiqueont/reporte]
a5ff7a8c363a: Pushed
7e7563f2ddb6: Pushed
49ae429f6151: Pushed
f57b05ac8fd9: Pushed
6b37362b3da7: Mounted from library/python
ed7de4b37c73: Pushed
b14f2539d39c: Pushed
1ba68a759a2f: Pushed
43562c428e08: Pushed
f39667d58a76: Pushed
latest: digest: sha256:939e80d12654175516a413db65c2bbec61734a5dfdfbbe47da8ff713f80f8793 size: 856

dominiqueont@Domdom:~/fdd_o26_domdom/estudiantes/Domdimad0m/09_python/uv_docker$ docker logout
Removing login credentials for https://index.docker.io/v1/


dominiqueont@Domdom:~/fdd_o26_domdom/estudiantes/Domdimad0m/09_python/uv_docker$ docker rmi -f dominiqueont/reporte
Untagged: dominiqueont/reporte:latest
Deleted: sha256:939e80d12654175516a413db65c2bbec61734a5dfdfbbe47da8ff713f80f8793


dominiqueont@Domdom:~/fdd_o26_domdom/estudiantes/Domdimad0m/09_python/uv_docker$ docker run --rm --platform linux/amd64 dominiqueont/reporte
Unable to find image 'dominiqueont/reporte:latest' locally
latest: Pulling from dominiqueont/reporte
a5ff7a8c363a: Pull complete
f57b05ac8fd9: Pull complete
ed7de4b37c73: Pull complete
43562c428e08: Pull complete
1ba68a759a2f: Pull complete
f39667d58a76: Download complete
Digest:   digest: sha256:939e80d12654175516a413db65c2bbec61734a5dfdfbbe47da8ff713f80f8793 size: 856
Status: Downloaded newer image for dominiqueont/reporte:latest
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
