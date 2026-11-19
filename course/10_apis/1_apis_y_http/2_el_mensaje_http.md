---
id: el-mensaje-http
title: "El mensaje HTTP"
nav_title: "El mensaje HTTP"
summary: "Lo que viaja por la red cuando llamas una API: una línea inicial, headers, una línea en blanco y un body, en texto. Qué es cada parte, para qué sirve, y qué se rompe si falta. Más la URL, parte por parte."
status: ready
estimated_time: 25m
tags: [http, protocolo, headers, body, url, https, tcp]
prerequisites: [que-es-una-api]
---

# El mensaje HTTP

**Página 2 de 4 · APIs y HTTP**

Meta: poder leer —y escribir a mano— una petición y una respuesta HTTP, sabiendo para qué sirve cada parte.

| Término | Qué es | Lo ves con |
|---|---|---|
| **protocolo** | Las reglas que dos programas siguen para entenderse: qué se manda, en qué orden y en qué formato | esta página |
| **TCP** | El protocolo que entrega bytes, completos y en orden, entre dos programas en la red | `a_mano()` |
| **socket** | El objeto con el que un programa abre una conexión TCP y manda o recibe bytes | `cable.py` |
| **HTTP** | El protocolo de la web y de casi todas las APIs: define el formato de petición y respuesta | celda 2.1 |
| **petición** | El mensaje que manda el cliente | celda 2.1 |
| **respuesta** | El mensaje que regresa el servidor | celda 2.1 |
| **header** | Una línea `Nombre: valor` con información *sobre* el mensaje | celda 2.3 |
| **body** | Los datos que lleva el mensaje, si lleva | celda 2.4 |

## En corto

- **Un mensaje HTTP tiene cuatro partes, en este orden**: línea inicial, headers, una línea en blanco y el body (que puede faltar).
- **Los headers describen el mensaje; el body son los datos.** Si un header miente, el body se lee mal.
- **Todo viaja en claro**, salvo que uses HTTPS: un token en `http://` lo lee cualquiera que vea la red.

## Protocolo, TCP y HTTP

**Definición.** Un **protocolo** son las reglas que dos programas siguen para comunicarse: qué mensajes existen, en qué orden se mandan y con qué formato. **HTTP** (*Hypertext Transfer Protocol*) es el protocolo de la web; lo definen documentos públicos de la IETF, el organismo que publica los estándares de internet, llamados **RFC** (el de la semántica de HTTP es el RFC 9110, de 2022).

En esta clase, HTTP/1.1 viaja sobre **TCP**, que entrega los bytes en orden y sin huecos mientras la conexión siga viva; si la conexión se cae, TCP reporta el error, no lo arregla. HTTP decide **qué bytes** mandar; TCP, **cómo llegan**.

```text
  tu código          requests.get(...)            ← tú
  ─────────────────────────────────────────
  HTTP               "GET /ventas HTTP/1.1 ..."   ← el formato del mensaje
  ─────────────────────────────────────────
  TCP                bytes completos y en orden   ← la conexión (un socket)
  ─────────────────────────────────────────
  red                paquetes, wifi, cables
```

Esta página muestra **HTTP/1.1**, donde la línea inicial y los headers son texto que puedes leer. **HTTP/2** manda la misma información en tramas binarias sobre TCP, y **HTTP/3** sobre **QUIC**, otro transporte construido sobre UDP. No tienen una línea inicial de texto, pero el significado de métodos, headers, body y códigos de estado es el mismo: lo que aprendas aquí vale para las tres.

## Las cuatro partes de un mensaje

Petición y respuesta tienen la misma forma:

| Parte | Qué es | Para qué sirve |
|---|---|---|
| **Línea inicial** | La primera línea | En la petición dice qué quieres; en la respuesta, cómo le fue |
| **Headers** | Cero o más líneas `Nombre: valor` | Describen el mensaje: formato, tamaño, quién eres, qué aceptas |
| **Línea en blanco** | Una línea vacía | Marca dónde terminan los headers y empieza el body |
| **Body** | Bytes de datos, opcional | Lo que mandas o recibes: un JSON, un CSV, una imagen |

Cada línea termina con dos caracteres, `\r\n` (retorno de carro y salto de línea), no sólo con `\n`. Así lo exige el estándar.

```text
  PETICIÓN                                    RESPUESTA

  POST /ventas HTTP/1.1          ← línea      HTTP/1.1 201 Created          ← línea
  Host: 127.0.0.1:8026           ┐            Location: /ventas/5           ┐
  Content-Type: application/json │ headers    Content-Type: application/json│ headers
  Content-Length: 75             │            Content-Length: 80            │
  Authorization: Bearer fdd-2026 ┘                                          ┘
                                 ← en blanco                                ← en blanco
  {"tienda": "Norte", ...}       ← body       {"id": 5, "tienda": ...}      ← body
```

**Haz (celda 2.1):** escribe una petición HTTP a mano y mándala por un socket.

```python
peticion = (
    "GET /ventas/1 HTTP/1.1\r\n"
    "Host: 127.0.0.1:8026\r\n"
    "Connection: close\r\n"
    "\r\n"
)
print(a_mano("127.0.0.1", 8026, peticion))
```

**Qué hace cada línea:**

- `"GET /ventas/1 HTTP/1.1\r\n"` — la línea de petición: quiero **leer** (`GET`) la venta 1, y hablo HTTP versión 1.1.
- `"Host: 127.0.0.1:8026\r\n"` — a qué servidor va dirigida. Es el único header obligatorio en HTTP/1.1.
- `"Connection: close\r\n"` — pide al servidor que cierre la conexión al terminar; así `a_mano` sabe cuándo dejar de leer.
- `"\r\n"` — la línea en blanco: aquí terminan los headers. Un `GET` no lleva body.
- `a_mano(...)` — abre un socket TCP al puerto 8026, manda el texto tal cual y regresa lo que llegue.

**Deberías ver** (la fecha y el ETag cambian):

```text
HTTP/1.1 200 OK
Server: VentasFDD/1.0
Date: Tue, 20 Oct 2026 22:52:05 GMT
ETag: "d788c34b28aa"
Vary: Accept
Content-Type: application/json
Content-Length: 81

{"id": 1, "tienda": "Centro", "producto": "café", "cantidad": 3, "precio": 45.0}
```

- **No hubo librería de por medio**: escribiste texto, el servidor lo entendió y contestó texto. Eso es todo HTTP/1.1.
- La respuesta tiene las cuatro partes: línea de estado, seis headers, una línea en blanco y el body en JSON.
- En la terminal del servidor aparece tu petición con sólo dos headers: los que escribiste.

**Haz (celda 2.2):** lo mismo, contra un servidor real de internet.

```python
print(a_mano("example.com", 80,
             "HEAD / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"))
```

**Qué hace cada línea:**

- `"example.com", 80` — el sitio de ejemplo oficial de internet, en el puerto 80, el de HTTP sin cifrar.
- `HEAD /` — el método `HEAD` pide sólo la línea de estado y los headers de `/`, sin el body.

**Deberías ver** (varios valores cambian):

```text
HTTP/1.1 200 OK
Date: Tue, 20 Oct 2026 22:52:05 GMT
Content-Type: text/html; charset=utf-8
Connection: close
Server: cloudflare
Last-Modified: Tue, 13 Oct 2026 22:05:48 GMT
Allow: GET, HEAD
Accept-Ranges: bytes
Age: 5
cf-cache-status: HIT
```

- Un servidor que no conoces entendió tu texto escrito a mano: eso es un **protocolo**.
- `Server: cloudflare` y `cf-cache-status: HIT`: no contestó el servidor de example.com, sino una copia guardada en Cloudflare, una empresa que se pone en medio. La página 4 explica por qué eso es posible.

## La línea inicial

**En la petición** (la **línea de petición**) hay tres campos separados por espacios:

| Campo | Ejemplo | Qué dice |
|---|---|---|
| **Método** | `GET`, `POST`, `PUT`, `DELETE` | Qué quieres hacer. La página 3 dice qué promete cada uno |
| **Ruta** (*request-target*) | `/ventas/1?formato=csv` | Sobre qué recurso de ese servidor |
| **Versión** | `HTTP/1.1` | Qué versión del protocolo hablas |

**En la respuesta** (la **línea de estado**) también hay tres:

| Campo | Ejemplo | Qué dice |
|---|---|---|
| **Versión** | `HTTP/1.1` | Qué versión habla el servidor |
| **Código de estado** | `201` | Cómo le fue, en un número de tres dígitos. **Es lo que lee tu programa** |
| **Frase** | `Created` | El mismo resultado en palabras, para humanos. Los programas la ignoran |

## Headers: información sobre el mensaje

**Definición.** Un **header** es una línea `Nombre: valor` que da información sobre el mensaje, no los datos mismos. El nombre no distingue mayúsculas: `content-type` y `Content-Type` son el mismo header.

**Para qué existen.** Para que el receptor sepa **cómo leer** el body y **qué hacer** con el mensaje sin tener que adivinar. Agrupados por propósito:

| Propósito | Header | Ejemplo | Qué dice |
|---|---|---|---|
| **Destino** | `Host` | `api.github.com` | A qué sitio va. Una sola máquina sirve muchos sitios; con esto sabe cuál |
| **Describir el body** | `Content-Type` | `application/json` | En qué formato está el body |
| | `Content-Length` | `75` | Cuántos bytes mide el body: así el receptor sabe dónde termina el mensaje |
| **Negociar** | `Accept` | `text/csv` | En qué formatos aceptas la respuesta |
| **Identificarte** | `Authorization` | `Bearer fdd-2026` | Tu credencial: un **token**, una cadena secreta que prueba quién eres |
| | `User-Agent` | `python-requests/2.34.2` | Qué programa hace la petición |
| **Caché** | `ETag` / `If-None-Match` | `"d788c34b28aa"` | Una huella de la versión de los datos (página 4) |
| **Siguiente paso** | `Location` | `/ventas/5` | Dónde quedó lo que creaste |
| | `Allow` | `GET, HEAD` | Qué métodos acepta ese recurso |
| | `Retry-After` | `30` | Cuántos segundos esperar antes de reintentar |

**En la vida real** las APIs agregan headers propios:

- **GitHub** pide `Accept: application/vnd.github+json` (un formato JSON propio) y `X-GitHub-Api-Version: 2022-11-28` para fijar la versión del contrato; así un cambio futuro no rompe tu código.
- **Banxico** (su API de series económicas) recibe el token en un header propio, `Bmx-Token`.
- **GitHub** rechaza con `403` toda petición sin `User-Agent`. `requests` lo manda solo; un socket escrito a mano, no.

El prefijo `X-` en nombres de headers propios es una costumbre vieja; el RFC 6648 (2012) recomienda ya no usarlo, pero sigue en muchas APIs.

**Haz (celda 2.3):** una petición con `requests`, vista con `ver()`.

```python
r = requests.get(f"{URL}/ventas/1")
ver(r)
```

**Qué hace cada línea:**

- `requests.get(...)` — arma y manda la misma petición que escribiste a mano en la 2.1.
- `ver(r)` — imprime con `>>` lo que se mandó y con `<<` lo que llegó, en formato HTTP.

**Deberías ver:**

```text
>> GET /ventas/1 HTTP/1.1
>> User-Agent: python-requests/2.34.2
>> Accept-Encoding: gzip, deflate, zstd
>> Accept: */*
>> Connection: keep-alive
>>

<< HTTP/1.1 200 OK
<< Server: VentasFDD/1.0
<< Date: Tue, 20 Oct 2026 22:52:06 GMT
<< ETag: "d788c34b28aa"
<< Vary: Accept
<< Content-Type: application/json
<< Content-Length: 81
<<
<< {"id": 1, "tienda": "Centro", "producto": "café", "cantidad": 3, "precio": 45.0}
```

- **`requests` agregó cuatro headers sin que se los pidieras**: quién eres (`User-Agent`), qué compresión entiendes (`Accept-Encoding`), qué formatos aceptas (`*/*`: cualquiera) y que la conexión siga abierta (`keep-alive`).
- `ver()` no muestra `Host`: lo agrega la capa de abajo de `requests` justo antes de mandar. En la terminal del servidor sí aparece.

## Body: los datos

**Definición.** El **body** es la secuencia de bytes que va después de la línea en blanco. Es opcional: un `GET` normalmente no lleva; un `POST` que crea algo, sí.

Dos headers dicen cómo interpretarlo y dónde termina:

- **`Content-Type`** dice **cómo interpretar** los bytes (JSON, CSV, HTML, imagen).
- **`Content-Length`** dice **cuántos** bytes son, para que el receptor sepa dónde termina este mensaje y empieza el siguiente en la misma conexión.

**Haz (celda 2.4):** crea una venta mandando un body JSON.

```python
nueva = {"tienda": "Norte", "producto": "café", "cantidad": 2, "precio": 45.0}
r = requests.post(f"{URL}/ventas", json=nueva, headers=TOKEN)
ver(r)
```

**Qué hace cada línea:**

- `json=nueva` — `requests` **serializa** el dict a texto JSON, lo pone en el body y agrega `Content-Type: application/json` y `Content-Length`.
- `headers=TOKEN` — agrega `Authorization: Bearer fdd-2026`; este servidor sólo deja escribir a quien trae ese token.

**Deberías ver:**

```text
>> POST /ventas HTTP/1.1
>> User-Agent: python-requests/2.34.2
>> Accept-Encoding: gzip, deflate, zstd
>> Accept: */*
>> Connection: keep-alive
>> Authorization: Bearer fdd-2026
>> Content-Length: 75
>> Content-Type: application/json
>>
>> {"tienda": "Norte", "producto": "caf\u00e9", "cantidad": 2, "precio": 45.0}

<< HTTP/1.1 201 Created
<< Server: VentasFDD/1.0
<< Date: Tue, 20 Oct 2026 22:52:06 GMT
<< Location: /ventas/5
<< Content-Type: application/json
<< Content-Length: 80
<<
<< {"tienda": "Norte", "producto": "café", "cantidad": 2, "precio": 45.0, "id": 5}
```

- **`201 Created` y `Location: /ventas/5`**: el servidor creó la venta y te dice dónde quedó.
- `caf\u00e9` — en la petición, `requests` escribe la `é` como la secuencia JSON `\u00e9` (por eso el body mide 75 bytes). El servidor la convierte en el mismo texto y responde con la `é` literal: es la misma palabra.
- **Mira la terminal del servidor**: ahí está tu token, `Bearer fdd-2026`, en texto plano.

### HTTPS: HTTP cifrado

Todo lo que viste viajó **en claro**: cualquier equipo entre tu máquina y el servidor (el router del wifi, tu proveedor de internet) puede leerlo, token incluido. **HTTPS** es HTTP dentro de **TLS**, un protocolo que:

- **cifra** el mensaje, para que nadie en medio lo lea;
- **verifica** que el servidor es quien dice ser, con un certificado;
- **detecta** si alguien alteró el mensaje en el camino.

Los mensajes HTTP son idénticos; sólo viajan dentro de TLS, normalmente por el puerto 443. **Regla:** un token o un dato personal sólo viaja por `https://`. Este servidor usa `http://` porque nunca sale de tu máquina.

**Haz (celda 2.5):** pide la misma información en dos formatos.

```python
for formato in ["application/json", "text/csv"]:
    r = requests.get(f"{URL}/ventas", params={"tienda": "Centro"},
                     headers={"Accept": formato})
    print(f"Accept: {formato}  →  Content-Type: {r.headers['Content-Type']}")
    print(r.text)
    print()
```

**Qué hace cada línea:**

- `params={"tienda": "Centro"}` — `requests` agrega `?tienda=Centro` a la URL: sólo las ventas del Centro.
- `headers={"Accept": formato}` — le dice al servidor en qué formato quieres la respuesta.
- `r.headers['Content-Type']` — en qué formato contestó de verdad.

**Deberías ver:**

```text
Accept: application/json  →  Content-Type: application/json
[{"id": 1, "tienda": "Centro", "producto": "café", "cantidad": 3, "precio": 45.0}]

Accept: text/csv  →  Content-Type: text/csv; charset=utf-8
id,tienda,producto,cantidad,precio
1,Centro,café,3,45.0
```

- **Misma URL, mismos datos, dos formatos.** El cliente pidió con `Accept`; el servidor avisó qué mandó con `Content-Type`. Esto se llama **negociación de contenido**.

**Haz (celda 2.6):** un endpoint viejo que omite un dato en `Content-Type`.

```python
r = requests.get(f"{URL}/exportar")
print("Content-Type:", r.headers["Content-Type"])
print("requests decodificó con:", r.encoding)
print(r.text.splitlines()[1])
r.encoding = "utf-8"
print(r.text.splitlines()[1])
```

**Qué hace cada línea:**

- `r.headers["Content-Type"]` — el formato que declaró el servidor.
- `r.encoding` — la **codificación** que `requests` usó para convertir los bytes del body en texto.
- `r.text.splitlines()[1]` — la primera fila de datos del CSV.
- `r.encoding = "utf-8"` — le decimos a `requests` la codificación correcta y volvemos a leer.

**Deberías ver:**

```text
Content-Type: text/csv
requests decodificó con: ISO-8859-1
1,Centro,cafÃ©,3,45.0
1,Centro,café,3,45.0
```

- **El body es bytes; para volverlo texto hay que saber la codificación.** La `é` en UTF-8 son dos bytes. Leídos con otra codificación (ISO-8859-1), salen dos caracteres: `Ã©`.
- El servidor mandó `text/csv` **sin** `charset=utf-8`. Sin ese dato, `requests` aplica la regla vieja de HTTP para texto: ISO-8859-1.
- **Si lo ignoras**: tu pipeline guarda `cafÃ©` sin ningún error, y nadie lo nota hasta que una cuenta por producto sale mal.

## La URL, parte por parte

**Definición.** Una **URL** (*Uniform Resource Locator*) dice dónde está un recurso y cómo llegar a él. El navegador, `requests` y `curl` la parten para armar la petición.

```text
  https://api.github.com:443/repos/python/cpython/issues?state=open&per_page=2#comentarios
  └─┬─┘   └─────┬──────┘ └┬┘└────────────┬────────────┘ └────────┬────────┘ └────┬────┘
 esquema       host    puerto          ruta (path)           query          fragmento
```

| Parte | Qué es | ¿Viaja al servidor? |
|---|---|---|
| **Esquema** | Qué protocolo usar: `http` o `https` | Decide cómo conectarse; no va en el mensaje |
| **Host** | El nombre del servidor; se traduce a una dirección IP | Sí, en el header `Host` |
| **Puerto** | En qué puerto escucha. Si se omite: 80 para `http`, 443 para `https` | Decide a dónde conectarse |
| **Ruta** | Qué recurso, dentro de ese servidor | Sí, en la línea de petición |
| **Query** | Pares `clave=valor` después de `?`, separados por `&` | Sí, en la línea de petición |
| **Fragmento** | Lo que va después de `#`: una posición dentro del documento | **No.** Lo usa sólo el navegador |

**La costumbre**: la ruta **identifica** el recurso (`/repos/python/cpython/issues`) y la query lo **filtra o pagina** (`state=open`, `per_page=2`). Es una convención de diseño, no una regla del protocolo.

**Haz (celda 2.7):** parte una URL real con la librería estándar.

```python
from urllib.parse import parse_qs, urlsplit

url = "https://api.github.com:443/repos/python/cpython/issues?state=open&per_page=2#comentarios"
partes = urlsplit(url)
print("esquema:  ", partes.scheme)
print("host:     ", partes.hostname)
print("puerto:   ", partes.port)
print("ruta:     ", partes.path)
print("query:    ", parse_qs(partes.query))
print("fragmento:", partes.fragment)
```

**Qué hace cada línea:**

- `urlsplit(url)` — parte la URL en sus piezas.
- `parse_qs(partes.query)` — convierte `state=open&per_page=2` en un dict; cada valor es una lista porque una clave puede repetirse.

**Deberías ver:**

```text
esquema:   https
host:      api.github.com
puerto:    443
ruta:      /repos/python/cpython/issues
query:     {'state': ['open'], 'per_page': ['2']}
fragmento: comentarios
```

- Con `requests` no armes la query a mano: pásala en `params=`, como en la 2.5. `requests` se encarga de **codificar** los caracteres especiales (en la query, un espacio viaja como `+` o como `%20`).

> [!NOTE]
> **Si sólo recuerdas una cosa:** una petición HTTP es texto con cuatro partes —línea inicial, headers, línea en blanco, body—; los headers dicen cómo leer el body, y si mienten u omiten algo, los datos llegan mal sin ningún error.

Sigue con [[metodos-y-status]].
