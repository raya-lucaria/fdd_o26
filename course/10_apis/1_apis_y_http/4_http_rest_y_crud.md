---
id: http-rest-y-crud
title: "HTTP, REST y CRUD"
nav_title: "HTTP, REST y CRUD"
summary: "HTTP, REST y CRUD son tres conceptos distintos: el protocolo que transporta los mensajes, el estilo con que se organiza una API y las operaciones que haces con los datos. Mezclarlas es la confusión más común al hablar de APIs."
status: ready
estimated_time: 17m
tags: [rest, crud, http, recurso, representacion, cache, sin-estado, rpc, fielding]
prerequisites: [metodos-y-status]
---

# HTTP, REST y CRUD

**Página 4 de 4 · APIs y HTTP**

Meta: distinguir los tres conceptos, saber qué exige REST y qué cuesta cumplirlo, y decidir entre REST y RPC sobre HTTP.

| Término | Qué es | Lo ves con |
|---|---|---|
| **recurso** | Cualquier cosa con nombre propio que una API expone: una venta, la lista de ventas, un usuario | la ruta /ventas/1 |
| **representación** | Los bytes que describen el estado de un recurso en un formato concreto: JSON, CSV, HTML | el header Content-Type |
| **URI** | El identificador de un recurso; una URL es una URI que además dice dónde y cómo pedirlo | la celda 2.7 |
| **estilo arquitectónico** | Un conjunto de reglas de diseño que, si las cumples, dan ciertas propiedades al sistema | la tesis de Fielding |
| **restricción** | Una de esas reglas: algo que el sistema **no** puede hacer, a cambio de una propiedad | la tabla de abajo |
| **REST** | *Representational State Transfer*: un estilo arquitectónico definido por seis restricciones | esta página |
| **sin estado** | Cada petición trae todo lo necesario para entenderla; el servidor no depende de lo que recuerde de una petición anterior. Sí puede guardar datos (ventas, usuarios, permisos) | la celda 4.2 |
| **caché** | Una copia guardada de una respuesta, para no volver a pedirla completa | la celda 4.1 |
| **hipermedia** | Respuestas que traen los enlaces a lo que puedes hacer después | el header Link de GitHub |
| **CRUD** | *Create, Read, Update, Delete*: las cuatro operaciones básicas sobre datos guardados | la celda 4.4 |
| **RPC** | *Remote Procedure Call*: llamar a una operación por su nombre en otra máquina | POST /reiniciar |

## En corto

- **HTTP, REST y CRUD son tres conceptos distintos**: cómo viaja el mensaje, cómo se organiza la API, qué haces con los datos.
- **REST es un estilo con seis restricciones**, cada una con un costo; casi ninguna API que se llama «REST» las cumple todas.
- **El mapeo CRUD → métodos HTTP es una convención**, no una equivalencia: hay operaciones que no son CRUD, y está bien.

## Tres conceptos, tres preguntas

La confusión clásica es decir «una API REST es una API que usa GET, POST, PUT y DELETE para hacer CRUD». Esa frase mezcla tres cosas distintas, que se combinan pero ninguna contiene a otra:

| Capa | Qué es | Pregunta que contesta | Lo define |
|---|---|---|---|
| **HTTP** | Un **protocolo**: el formato de los mensajes y sus reglas | ¿Cómo viaja una petición y su respuesta? | RFC 9110 y RFC 9112 |
| **REST** | Un **estilo arquitectónico**: reglas para organizar una API | ¿Cómo se diseña y se organiza la API? | La tesis de Roy Fielding (2000) |
| **CRUD** | Un **conjunto de operaciones** sobre datos guardados; viene de las bases de datos | ¿Qué le haces a los datos? | Nadie en particular: es vocabulario |

```text
┌─ HTTP ──────────────┐   ┌─ REST ──────────────┐   ┌─ CRUD ──────────────┐
│ cómo viaja cada     │   │ cómo se organiza    │   │ qué haces con los   │
│ mensaje             │   │ la API              │   │ datos               │
│                     │   │                     │   │                     │
│ línea inicial,      │   │ recursos con URI,   │   │ crear, leer,        │
│ headers, body,      │   │ representaciones,   │   │ actualizar, borrar  │
│ métodos, status     │   │ sin estado, caché…  │   │                     │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
   un protocolo              un estilo de diseño       un vocabulario
```

- **Cada capa existe sin las otras.** Puedes usar HTTP sin REST (las APIs de LLM lo hacen), diseñar REST sobre otro protocolo (Fielding no lo ata a HTTP), y hacer CRUD en SQL sin red.
- **Lo que las une es una convención**: REST se suele implementar sobre HTTP, y CRUD se suele mapear a sus métodos.

## Recurso, representación y URI

**Recurso.** Es la unidad de información que la API nombra. La venta 1 es un recurso; la lista de ventas de la tienda Centro es otro. Un recurso es la **idea**, no los bytes.

**Representación.** Son los bytes que el servidor manda para describir el **estado actual** de un recurso, en un formato. La misma venta puede representarse como JSON o como CSV: el recurso es uno, las representaciones son dos.

**URI** (*Uniform Resource Identifier*). Es el identificador de un recurso. `/ventas/1` es una referencia **relativa**: junto con la base `http://127.0.0.1:8026` forma la URI completa. Una **URL** es una URI que además dice cómo llegar (scheme, host, puerto).

**Ya lo viste.** En la celda 2.5 de [[el-mensaje-http]] pediste `/ventas?tienda=Centro` dos veces, cambiando sólo el header `Accept`: una respuesta llegó en JSON y la otra en CSV. **Mismo recurso, dos representaciones.** El header `Content-Type` de cada respuesta dijo cuál era cuál.

- **En la práctica**, muchas APIs públicas no usan `Accept` para esto: prefieren un parámetro (`?format=csv`) o una extensión (`/ventas.csv`). `Accept` es el mecanismo de HTTP; la extensión es más fácil de escribir en un navegador.

## REST: seis restricciones, cada una con un precio

REST lo definió **Roy Fielding en su tesis doctoral (2000)**, a partir de lo que hacía funcionar a la Web. No es un estándar ni una librería: es una lista de **restricciones**. Si tu sistema las cumple, gana ciertas propiedades; cada una cuesta algo.

| Restricción | Qué exige | Qué ganas | Qué cuesta |
|---|---|---|---|
| **Cliente-servidor** | Separar quien pide de quien guarda los datos | Cada lado evoluciona por su cuenta | Toda interacción cruza la red |
| **Sin estado** | Cada petición trae todo lo necesario; el servidor no guarda una sesión del cliente entre peticiones (los datos, sí) | Cualquier servidor puede contestar; escalar es agregar servidores | Cada petición repite datos (el token, los filtros) |
| **Caché** | Cada respuesta dice si se puede guardar y por cuánto tiempo | Menos peticiones y menos bytes | Puedes leer una copia vieja |
| **Interfaz uniforme** | Todos los recursos se manejan igual: URI, representaciones, mensajes autodescriptivos, hipermedia | Herramientas genéricas (navegadores, cachés, proxies) entienden cualquier API | Menos eficiente que una interfaz hecha a la medida |
| **Sistema en capas** | El cliente no sabe si habla con el servidor final o con un intermediario | Puedes poner cachés, balanceadores y firewalls en medio | Cada capa agrega latencia |
| **Código bajo demanda** (opcional) | El servidor puede mandar código que el cliente ejecuta | El cliente se extiende sin reinstalarse | Menos visibilidad; por eso es opcional |

La **interfaz uniforme** es la restricción central, y tiene cuatro partes:

1. **Identificación de recursos**: cada recurso tiene su URI.
2. **Manipulación por representaciones**: cambias un recurso mandando una representación (el JSON de un PUT), no llamando a una función del servidor.
3. **Mensajes autodescriptivos**: cada mensaje dice cómo leerlo (`Content-Type`, método, status).
4. **Hipermedia**: las respuestas traen los enlaces a los siguientes pasos.

### Caché: no volver a bajar lo que ya tienes

El servidor manda con cada respuesta un **ETag**: una huella del contenido. La próxima vez, el cliente la manda en `If-None-Match`. Si el recurso no cambió, el servidor contesta **304 Not Modified sin body**: «lo que tienes sigue siendo válido».

**Haz (celda 4.1):** pide la misma venta dos veces a tu servidor, y lo mismo a PokeAPI, una API pública real.

```python
r1 = requests.get(f"{URL}/ventas/1")
r2 = requests.get(f"{URL}/ventas/1", headers={"If-None-Match": r1.headers["ETag"]})
print(f"1a vez: {r1.status_code} {r1.reason:13} {len(r1.content):>7} bytes  ETag {r1.headers['ETag']}")
print(f"2a vez: {r2.status_code} {r2.reason:13} {len(r2.content):>7} bytes")

p = "https://pokeapi.co/api/v2/pokemon/pikachu"
r1 = requests.get(p, timeout=10)
r2 = requests.get(p, headers={"If-None-Match": r1.headers["ETag"]}, timeout=10)
print(f"pokeapi 1a vez: {r1.status_code} {len(r1.content):>7,} bytes")
print(f"pokeapi 2a vez: {r2.status_code} {len(r2.content):>7,} bytes")
print("Cache-Control:", r1.headers["Cache-Control"])
```

**Qué hace cada línea:**

- `r1.headers["ETag"]` — la huella que el servidor mandó con la primera respuesta.
- `headers={"If-None-Match": ...}` — la segunda petición dice «ya tengo esta versión; mándamela sólo si cambió».
- `len(r.content)` — cuántos bytes trajo el body.
- `timeout=10` — PokeAPI está en internet: si en 10 segundos no contesta, la celda se rinde en vez de colgarse (la página 3 explica por qué `requests` no pone uno solo).
- `r1.headers["Cache-Control"]` — cuánto tiempo dice el servidor que puedes guardar la respuesta.

**Deberías ver:**

```text
1a vez: 200 OK                 81 bytes  ETag "d788c34b28aa"
2a vez: 304 Not Modified        0 bytes
pokeapi 1a vez: 200 309,106 bytes
pokeapi 2a vez: 304       0 bytes
Cache-Control: public, max-age=86400, s-maxage=86400
```

- **309,106 bytes contra 0**: la segunda vez sólo viajaron los headers. Para una fuente de datos que consultas cada hora, esa es la diferencia entre bajar todo y bajar nada.
- `max-age=86400` — PokeAPI dice que la respuesta vale 86,400 segundos (un día).
- **Cada representación tiene su propio ETag**: el JSON y el CSV de la misma venta tienen huellas distintas. Por eso tu servidor manda también `Vary: Accept`, que avisa a las cachés que la respuesta depende del header `Accept` y no deben mezclar una con otra.
- **En la vida real**: la documentación de GitHub dice que una petición condicional contestada con 304 **no cuenta** contra tu límite principal de peticiones, siempre que vaya autenticada. Caché bien usada es cuota ahorrada.

### Sin estado: cualquier servidor puede contestar

Una API grande no corre en un servidor: corre en muchos, detrás de un **balanceador de carga** (un programa que reparte las peticiones entre servidores). Si el servidor A recordara que ya te autenticaste, tu siguiente petición tendría que ir **forzosamente** a A. Eso se llama *sticky session*.

- **En la vida real**: la guía *The Twelve-Factor App* (Heroku, ~2011) dice que los procesos son *stateless and share-nothing* y que las sticky sessions *should never be used or relied upon*. El estado vive en una base de datos, no en la memoria del servidor.
- **Si lo ignoras**: el día que A se cae, todos sus clientes pierden su sesión; y no puedes agregar servidores sin romper a los que ya estaban.

**Haz (celda 4.2):** una petición con token y la misma sin token.

```python
venta_nueva = {"tienda": "Centro", "producto": "café", "cantidad": 1, "precio": 45.0}

r = requests.post(f"{URL}/ventas", json=venta_nueva, headers=TOKEN)
print("con token:", r.status_code)
r = requests.post(f"{URL}/ventas", json=venta_nueva)
print("sin token:", r.status_code, "— el servidor no recuerda la petición anterior")
```

**Qué hace cada línea:**

- `venta_nueva = {...}` — la venta que vas a crear, como diccionario de Python.
- `requests.post(..., headers=TOKEN)` — crea la venta mandando el header `Authorization`.
- `requests.post(...)` sin `headers` — la misma petición, un instante después, sin token.

**Deberías ver:**

```text
con token: 201
sin token: 401 — el servidor no recuerda la petición anterior
```

- **El servidor no te «conoce» por haber entrado antes**: cada petición se juzga sola. Por eso el token viaja en **cada** petición.

### Sistema en capas: no sabes quién te contestó

En la celda 2.2 de [[el-mensaje-http]], `example.com` respondió con `Server: cloudflare` y `cf-cache-status: HIT`. **No te contestó el servidor de example.com**: te contestó una copia en un servidor de Cloudflare, una capa intermedia. Tu cliente no cambió nada para que eso pasara. Eso es la restricción de capas funcionando.

### Hipermedia: seguir el enlace, no construirlo

Una API con hipermedia te dice **a dónde ir después**. GitHub lo hace al paginar: la respuesta trae un header `Link` con la URL de la página siguiente, marcada `rel="next"`. Tu código sigue esa URL en lugar de armarla.

**Haz (celda 4.3):** sólo el profesor: GitHub permite 60 peticiones por hora por IP y todo el salón sale por la misma IP.

```python
r = requests.get("https://api.github.com/repos/python/cpython/issues", params={"per_page": 2},
                 headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}, timeout=10)
print(r.status_code)
print("Link:", r.headers.get("Link"))
print("te quedan:", r.headers.get("X-RateLimit-Remaining"), "de", r.headers.get("X-RateLimit-Limit"))
```

**Qué hace cada línea:**

- `params={"per_page": 2}` — pide los issues de dos en dos, para que haya página siguiente.
- `"Accept": "application/vnd.github+json"` — el tipo de representación propio de GitHub.
- `"X-GitHub-Api-Version": "2022-11-28"` — fija la versión del contrato de la API.
- `r.headers.get("Link")` — el enlace a la página siguiente.
- `X-RateLimit-Remaining` y `X-RateLimit-Limit` — cuántas peticiones te quedan esta hora y cuántas tienes.

**Deberías ver** (el cursor de la URL y el número que queda cambian):

```text
200
Link: <https://api.github.com/repositories/81598961/issues?per_page=2&after=Y3Vyc29yOnYyOpLPAAABoVt_7ajPAAAAAWKzxis%3D&page=2>; rel="next"
te quedan: 33 de 60
```

- **La URL de la página 2 trae un cursor (`after=...`) que no podrías inventar**: si construyeras la URL tú, tu código se rompería cuando GitHub cambie su forma de paginar. Siguiendo `rel="next"`, no.
- **Es hipermedia parcial**: GitHub enlaza la paginación, pero no todas las acciones posibles. Por eso es un ejemplo, no la regla.

## Qué tan REST es una API: el modelo de Richardson

Leonard Richardson propuso cuatro niveles (2008) para ubicar una API respecto a REST. Sirve para leer APIs reales sin pelearse por la etiqueta.

| Nivel | Qué hace la API | Ejemplo real |
|---|---|---|
| **0** | HTTP es sólo transporte: el nombre de la operación va en el body o en la ruta, casi siempre con POST | SOAP, JSON-RPC; Slack Web API, con una ruta por operación (/api/chat.postMessage) |
| **1** | Separa recursos con su URI, pero usa un solo método para todo | Poco común hoy; aparece en APIs internas viejas |
| **2** | Recursos + métodos HTTP con su significado + status correctos | GitHub, y la mayoría de las APIs «REST» |
| **3** | Además, hipermedia: las respuestas enlazan los siguientes pasos | Casi nadie completo; GitHub enlaza la paginación |

- **Casi ninguna «API REST» es REST en el sentido de Fielding**, porque casi ninguna llega al nivel 3. En la práctica, «API REST» quiere decir «API de nivel 2 sobre HTTP y JSON».
- **Las APIs de LLM** (`POST /v1/messages`) son **RPC sobre HTTP**: mandas una petición para que el servidor *calcule* una respuesta, no para crear un recurso que luego vas a leer. No es un defecto: es otro diseño.

## CRUD: cuatro operaciones y una convención

**CRUD** son las cuatro operaciones sobre datos guardados: **crear, leer, actualizar, borrar**. Vienen de las bases de datos (en SQL: INSERT, SELECT, UPDATE, DELETE). Al diseñar una API HTTP, se **acostumbra** mapearlas así:

| Operación CRUD | Método HTTP habitual | Status habitual | Nota |
|---|---|---|---|
| **Create** | POST a la colección | 201 Created + Location | PUT a una URI que el cliente ya conoce también crea (201) |
| **Read** | GET | 200 OK | Seguro: no cambia nada |
| **Update** | PUT (reemplaza completo) o PATCH (cambia una parte) | 200 OK o 204 | PUT es idempotente; PATCH no está obligado a serlo |
| **Delete** | DELETE | 204 No Content | La segunda vez: 404, y sigue siendo idempotente |

- **Es una convención, no una equivalencia.** POST no significa «crear»: significa «procesa esto según lo que defina el recurso». PUT puede crear. Y hay operaciones que no son ninguna de las cuatro.

**Haz (celda 4.4):** el ciclo completo sobre una venta, imprimiendo la tabla después de cada paso.

```python
# Regresa los datos al inicio: las celdas anteriores crearon y borraron ventas.
requests.post(f"{URL}/reiniciar")

def tabla():
    for v in requests.get(f"{URL}/ventas").json():
        print(f"   {v['id']:>2} {v['tienda']:8} {v['producto']:10} {v['cantidad']:>3} x {v['precio']}")

print("Create · POST /ventas")
r = requests.post(f"{URL}/ventas", json={"tienda": "Sur", "producto": "café", "cantidad": 5, "precio": 45.0}, headers=TOKEN)
print("   ", r.status_code, "Location:", r.headers["Location"])
nueva = r.headers["Location"]
print("Read · GET", nueva)
print("   ", requests.get(f"{URL}{nueva}").json())
print("Update · PUT", nueva)
requests.put(f"{URL}{nueva}", json={"tienda": "Sur", "producto": "café", "cantidad": 50, "precio": 45.0}, headers=TOKEN)
tabla()
print("Delete · DELETE", nueva)
print("   ", requests.delete(f"{URL}{nueva}", headers=TOKEN).status_code)
tabla()
```

**Qué hace cada línea:**

- `requests.post(f"{URL}/reiniciar")` — vuelve a las cuatro ventas iniciales, para que tu salida coincida con la de abajo.
- `def tabla()` — pide todas las ventas con GET y las imprime en columnas.
- `r.headers["Location"]` — la URI del recurso recién creado; el servidor te dice dónde quedó.
- `requests.put(...)` — reemplaza la venta completa: manda **todos** los campos, no sólo la cantidad.
- `requests.delete(...)` — borra la venta; 204 dice «hecho, no hay nada que devolver».

**Deberías ver:**

```text
Create · POST /ventas
    201 Location: /ventas/5
Read · GET /ventas/5
    {'tienda': 'Sur', 'producto': 'café', 'cantidad': 5, 'precio': 45.0, 'id': 5}
Update · PUT /ventas/5
    1 Centro   café         3 x 45.0
    2 Norte    pan dulce    6 x 18.5
    3 Sur      té           2 x 30.0
    4 Polanco  café         1 x 52.0
    5 Sur      café        50 x 45.0
Delete · DELETE /ventas/5
    204
    1 Centro   café         3 x 45.0
    2 Norte    pan dulce    6 x 18.5
    3 Sur      té           2 x 30.0
    4 Polanco  café         1 x 52.0
```

- **El cliente nunca inventó la URI `/ventas/5`**: la leyó del header `Location`.
- **`/reiniciar` no es CRUD**: es una acción con un verbo en la ruta. Es RPC sobre HTTP, puesto a propósito en este servidor para que lo reconozcas.

### Acciones que no son CRUD

Cancelar un pedido, enviar un correo, aprobar un pago: son **acciones**, no «crear, leer, actualizar, borrar». Hay dos salidas comunes:

- **Método personalizado.** Google (guía de diseño AIP-136) agrega la acción después de dos puntos: `POST /v1/pedidos/7:cancel`. Es RPC declarado, con POST porque cambia estado.
- **Convertir la acción en recurso.** `POST /pedidos/7/cancelaciones` crea una cancelación. Es nivel 2 puro, a costa de inventar un sustantivo.

## Decidir: ¿REST o RPC sobre HTTP?

No hay una respuesta correcta para todo. Cada diseño tiene ventajas y costos distintos:

| Si tu API… | Inclínate por | Por qué |
|---|---|---|
| Expone **entidades** que se crean, leen y cambian (ventas, usuarios, archivos) | **Orientada a recursos (nivel 2)** | Los métodos con su significado te dejan aprovechar herramientas genéricas; tú implementas sus garantías, defines la caché y decides qué se puede reintentar |
| Expone **acciones o cálculos** (generar texto, convertir un archivo, enviar un mensaje) | **RPC sobre HTTP** | No hay recurso que leer después; forzar un sustantivo complica sin ganar nada |
| Tiene **muchos consumidores que no conoces** | **Orientada a recursos** | La interfaz uniforme es la que todos ya saben leer |
| Tiene **pocos consumidores, conocidos** (tu equipo) | **Cualquiera**; RPC es más directo | El acuerdo cabe en una conversación |
| Necesita **caché** de lecturas | **GET sobre recursos** | Las cachés intermedias sólo guardan GET (y HEAD) sin configuración especial |
| Tiene **operaciones largas** (minutos) | **Un recurso para la operación** | Creas el trabajo, y su estado se consulta como cualquier otro recurso |

- **El costo de REST** es diseñar sustantivos y respetar la semántica de cada método.
- **El costo de RPC** es que los intermediarios no entienden tus operaciones: no pueden cachearlas ni saber si es seguro repetirlas. Todo eso lo tienes que resolver tú.

## Lo que esta clase no cubre

Para que sepas qué contestar si sale la pregunta: existe, y no es de esta clase.

- **Polling y webhooks** — cómo te enteras de que algo terminó: preguntando cada cierto tiempo, o dejando que el servidor te llame.
- **Streaming** — recibir una respuesta por partes mientras se genera, en lugar de esperar a que esté completa.
- **GraphQL** — un estilo donde el cliente escribe una consulta con los campos exactos que quiere.
- **gRPC** — RPC con mensajes binarios y un contrato escrito en un archivo `.proto`, común entre servicios internos.
- **OAuth** — un protocolo para que una aplicación actúe en tu nombre sin conocer tu contraseña.
- **Paginación a fondo** — partir respuestas grandes en páginas: por número de página o por cursor.
- **Versionado** — cómo cambia una API sin romper a quien ya la usa.

> [!NOTE]
> **Si sólo recuerdas una cosa:** HTTP dice cómo viaja el mensaje, REST cómo se organiza la API y CRUD qué haces con los datos; confundirlos es el error más común, y elegir REST o RPC es una decisión con costos, no una cuestión de moda.

Regresa al índice: [[apis-y-http]].
