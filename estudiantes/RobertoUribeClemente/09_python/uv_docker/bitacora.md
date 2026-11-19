# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub: RobertoUribeClemente
- Usuario de Docker Hub: bobuc05

## El paquete que agregaste

Paquete: numpy

Para qué lo usa tu fila: Instancia una matriz bidimensional 2x2 mediante np.array([[1, 2], [3, 4]]) 
y muestra su contenido en la tabla del ambiente.

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
Mi ambiente                              
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                                           ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.14.4                                          │
│ Intérprete       │ /home/bobuc05/fdd/fdd_o26_RobertoUribeClemente/ │
│                  │ estudiantes/RobertoUribeClemente/09_python/     │
│                  │ uv_docker/.venv/bin/python                      │
│ sys.prefix       │ /home/bobuc05/fdd/fdd_o26_RobertoUribeClemente/ │
│                  │ estudiantes/RobertoUribeClemente/09_python/     │
│                  │ uv_docker/.venv                                 │
│ ¿En un ambiente? │ sí                                              │
│ Sistema          │ Linux x86_64                                    │
│ NumPy            │ Matriz 2x2: [[1, 2], [3, 4]]                    │
└──────────────────┴─────────────────────────────────────────────────┘
     Paquetes instalados     
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Paquete        ┃ Versión  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Pygments       │ 2.21.0   │
│ markdown-it-py │ 4.2.0    │
│ mdurl          │ 0.1.2    │
│ numpy          │ 2.5.3    │
│ rich           │ 15.0.0   │
└────────────────┴──────────┘

```

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text
Mi ambiente                    
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16                      │
│ Intérprete       │ /app/.venv/bin/python        │
│ sys.prefix       │ /app/.venv                   │
│ ¿En un ambiente? │ sí                           │
│ Sistema          │ Linux x86_64                 │
│ NumPy            │ Matriz 2x2: [[1, 2], [3, 4]] │
└──────────────────┴──────────────────────────────┘
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

- Igual: Las versiones de todos los paquetes (numpy 2.5.3, rich 15.0.0, Pygments 2.21.0, markdown-it-py 4.2.0, mdurl 0.1.2) y el valor de la fila propia.
- Distinto: La versión de Python (3.14.4 vs 3.13.16) y las rutas de Intérprete y sys.prefix (/home/bobuc05/.../uv_docker/.venv vs /app/.venv).
- Por qué: uv.lock fija determinísticamente las librerías, pero el runtime de Python y las rutas dependen del sistema operativo anfitrión y de la imagen base.

## Tu imagen en Docker Hub

URL pública: https://hub.docker.com/r/bobuc05/uv-reporte

Digest: sha256:a2a71496f3b5689db9900e9da4acb05b0c256877210577819bbe38fb0a745460

Comando para correrla: docker run --rm docker.io/bobuc05/uv-reporte

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/09_python/uv_docker$ podman logout docker.io
Removed login credentials for docker.io
bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/09_python/uv_docker$ podman rmi -f bobuc05/uv-reporte
Untagged: docker.io/bobuc05/uv-reporte:latest
Deleted: ceb921f59ba9a69fa4310588b82816d53f259410486297590ea732b574ef6169
bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/09_python/uv_docker$ podman run --rm docker.io/bobuc05/uv-reporte
Trying to pull docker.io/bobuc05/uv-reporte:latest...
Getting image source signatures
Copying blob 250d581ae02d done   | 
Copying blob 8f7fd95a5c00 done   | 
Copying blob 831e2d1de284 done   | 
Copying blob 09d73ce1bb12 done   | 
Copying blob 6c70cdcc3aff done   | 
Copying blob 530dbdf15a3a done   | 
Copying blob 5631e31764f3 done   | 
Copying blob 6f49827d0a31 done   | 
Copying blob 1864feb8bee3 done   | 
Copying config ceb921f59b done   | 
Writing manifest to image destination
                    Mi ambiente                    
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Qué              ┃ Valor                        ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Python           │ 3.13.16                      │
│ Intérprete       │ /app/.venv/bin/python        │
│ sys.prefix       │ /app/.venv                   │
│ ¿En un ambiente? │ sí                           │
│ Sistema          │ Linux x86_64                 │
│ NumPy            │ Matriz 2x2: [[1, 2], [3, 4]] │
└──────────────────┴──────────────────────────────┘
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
