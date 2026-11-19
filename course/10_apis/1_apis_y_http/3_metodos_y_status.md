---
id: metodos-y-status
title: "Métodos y códigos de estado"
nav_title: "Métodos y status"
summary: "El método dice qué le pides al servidor y el status dice cómo le fue. Seguro, idempotente y cacheable son promesas que leen todos los programas que están en medio: de ellas depende si una petición se puede repetir sin daño."
status: ready
estimated_time: 28m
tags: [http, methods, safe, idempotent, status-codes, timeout, retries, idempotency-key]
prerequisites: [el-mensaje-http]
---

# Métodos y códigos de estado

**Página 3 de 4 · APIs y HTTP**

Meta: saber qué promete cada método, qué dice cada status y cuándo es seguro repetir una petición.

| Término | Qué es | Lo ves con |
|---|---|---|
| **método** | La primera palabra de la línea de petición: qué le pides al servidor que haga con el recurso | la celda 3.1 |
| **método seguro** | Un método con el que el cliente **no pide cambiar nada** en el servidor (sólo leer) | la celda 3.2 |
| **método idempotente** | Un método que, repetido N veces igual, deja el servidor **en el mismo estado** que una sola vez | la celda 3.1 |
| **cacheable** | Una respuesta que un programa intermedio puede guardar y reusar sin volver a preguntar | la página 4 |
| **status** | El número de tres dígitos de la línea de estado: cómo le fue a la petición | la celda 3.6 |
| **timeout** | El tiempo máximo que el cliente espera una respuesta antes de rendirse | la celda 3.3 |
| **reintento** | Mandar otra vez la misma petición porque la primera falló o no contestó | la celda 3.4 |
| **`Idempotency-Key`** | Un header con un identificador único por operación, para que el servidor reconozca un reintento | la celda 3.5 |

## En corto

- **El método es una promesa pública**: navegadores, cachés, crawlers y librerías de reintento la leen y actúan sin conocer tu aplicación.
- **Idempotente habla del estado del servidor, no de la respuesta**: un segundo `DELETE` responde 404 y sigue siendo idempotente.
- **Un timeout significa «no sé», no «no pasó»**: reintentar sólo es seguro si la operación es idempotente.

## Las tres propiedades de un método

HTTP (RFC 9110, 2022) no sólo da nombres a los métodos: les asigna **propiedades** que el resto del mundo puede leer sin preguntarte.

- **Seguro.** **Definición:** el cliente no solicita ningún cambio de estado en el servidor. El servidor puede escribir un log o contar visitas; lo que importa es que el cliente no pidió cambiar nada.
- **Idempotente.** **Definición:** el efecto **sobre el estado del servidor** de N peticiones idénticas es el mismo que el de una. La **respuesta** puede cambiar: borrar algo dos veces da 204 y luego 404, y el servidor queda igual en ambos casos (sin ese recurso).
- **Cacheable.** **Definición:** la respuesta se puede guardar y reusar para una petición igual, sin volver al servidor.

**Para qué existen.** Entre tu programa y el servidor hay programas que **no conocen tu aplicación**: el navegador, una caché, un proxy, un crawler, la librería que reintenta. Ninguno sabe qué hace `/ventas/2`, pero todos saben qué promete `GET`. Con eso deciden si pueden adelantarse, guardar o repetir.

| Método | Qué pide | Seguro | Idempotente | Cacheable |
|---|---|:---:|:---:|:---:|
| **GET** | Dame el recurso | sí | sí | sí |
| **HEAD** | Dame sólo los headers de lo que GET daría | sí | sí | sí |
| **OPTIONS** | ¿Qué puedo hacer con este recurso? | sí | sí | no |
| **POST** | Procesa estos datos según la lógica del recurso (crear, enviar, calcular) | no | no | en la práctica, no |
| **PUT** | Reemplaza el recurso completo con esto (o créalo en esa URL) | no | sí | no |
| **PATCH** | Cambia sólo estas partes del recurso | no | no garantizado | no |
| **DELETE** | Borra el recurso | no | sí | no |

- **Todo método seguro es idempotente**: si no cambias nada, repetirlo tampoco cambia nada.
- **POST no significa «crear»**: significa «procesa esto». Crear es su uso más común, no su definición.
- **PUT es idempotente porque reemplaza**: mandar el mismo reemplazo tres veces deja lo mismo. **POST no lo es**: tres POST pueden crear tres cosas.

**Haz (celda 3.1):** repite cada método tres veces y cuenta cuántas ventas quedan.

```python
requests.post(f"{URL}/reiniciar")  # sólo para la demo: vuelve a las 4 ventas iniciales

nueva = {"tienda": "Sur", "producto": "té", "cantidad": 1, "precio": 30.0}
reemplazo = {"tienda": "Norte", "producto": "pan dulce", "cantidad": 10, "precio": 18.5}
pruebas = [
    ("GET",    lambda: requests.get(f"{URL}/ventas/2")),
    ("PUT",    lambda: requests.put(f"{URL}/ventas/2", json=reemplazo, headers=TOKEN)),
    ("POST",   lambda: requests.post(f"{URL}/ventas", json=nueva, headers=TOKEN)),
    ("DELETE", lambda: requests.delete(f"{URL}/ventas/2", headers=TOKEN)),
]
print(f"{'método':7} {'status de cada llamada':24} ventas al final")
for metodo, llamada in pruebas:
    statuses = [llamada().status_code for _ in range(3)]
    print(f"{metodo:7} {str(statuses):24} {total()}")
```

**Qué hace cada línea:**

- `requests.post(f"{URL}/reiniciar")` — regresa el servidor a sus 4 ventas, para que todos vean los mismos números.
- `pruebas = [...]` — una lista de pares (nombre, función); `lambda: …` guarda la llamada sin hacerla todavía.
- `[llamada().status_code for _ in range(3)]` — hace la misma petición tres veces y junta los tres status.
- `total()` — pregunta con un `GET` cuántas ventas hay ahora (viene de `cable.py`).

**Deberías ver:**

```text
método  status de cada llamada   ventas al final
GET     [200, 200, 200]          4
PUT     [200, 200, 200]          4
POST    [201, 201, 201]          7
DELETE  [204, 404, 404]          6
```

- **GET y PUT**: tres llamadas, el mismo estado que con una. **POST**: tres llamadas, tres ventas nuevas (de 4 a 7).
- **DELETE**: responde 204 y luego 404, **pero el servidor queda igual** después de la primera (sin la venta 2). Por eso es idempotente: la propiedad habla del estado, no de la respuesta.
- En la terminal del servidor ves las 12 peticiones, una por una.

## Seguro: lo que pasa cuando un GET cambia algo

**Si lo ignoras.** Un programa que sigue enlaces cree, con razón, que `GET` no cambia nada, y los sigue todos.

**En la vida real.**

- **2005, Google Web Accelerator.** Esta extensión descargaba por adelantado los enlaces de cada página, para que abrieran más rápido. Algunas aplicaciones web, entre ellas productos de 37signals, borraban datos con enlaces `GET`. El acelerador «visitó» esos enlaces y se perdieron datos de usuarios. Google respondió que esas aplicaciones no respetaban el estándar.
- **Hoy, escáneres de correo.** Los filtros de seguridad corporativos abren los enlaces de los correos para revisarlos. Un enlace de inicio de sesión de un solo uso que se consume con un `GET` queda gastado antes de que la persona lo abra. La solución que documentan Supabase y Stytch: el `GET` sólo muestra una página con un botón, y el botón manda un `POST`.

En el servidor de la clase, `GET /borrar?id=…` borra una venta. **Es mal diseño, a propósito**: sirve para ver el daño. `GET /panel` es una página HTML con un enlace a `/borrar` por cada venta.

**Haz (celda 3.2):** un crawler de cinco líneas que sigue todos los enlaces del panel.

```python
requests.post(f"{URL}/reiniciar")  # sólo para la demo

print("antes:  ", total(), "ventas")
panel = requests.get(f"{URL}/panel").text
enlaces = re.findall(r'href="(.*?)"', panel)
for enlace in enlaces:
    requests.get(f"{URL}{enlace}")
    print("  seguí", enlace)
print("después:", total(), "ventas")
```

**Qué hace cada línea:**

- `requests.get(f"{URL}/panel").text` — descarga el HTML del panel como texto.
- `re.findall(r'href="(.*?)"', panel)` — saca con una expresión regular la dirección de cada enlace (`href="…"`); `(.*?)` captura lo que hay entre las comillas, lo menos posible.
- `requests.get(f"{URL}{enlace}")` — visita cada enlace con `GET`, que es lo que hace cualquier crawler o prefetcher.

**Deberías ver:**

```text
antes:   4 ventas
  seguí /borrar?id=1
  seguí /borrar?id=2
  seguí /borrar?id=3
  seguí /borrar?id=4
después: 0 ventas
```

- El crawler no hizo nada incorrecto: siguió enlaces `GET`, que prometen no cambiar nada. **El error es del servidor**, que rompió la promesa.
- **Regla de diseño:** lo que cambia estado va en `POST`, `PUT`, `PATCH` o `DELETE`. Nunca en `GET`.

## Timeout: cuando no llega respuesta

**Definición.** Un **timeout** es el límite de tiempo que el cliente espera; al pasarlo, deja de esperar y reporta un error.

**Para qué existe.** Sin límite, un servidor lento o caído deja a tu programa esperando para siempre. **`requests` no tiene timeout por defecto**: si no pasas `timeout=`, espera indefinidamente.

**Haz (celda 3.3):** pide algo a un servidor que tarda 3 segundos, con un límite de 1.

```python
inicio = time.perf_counter()
try:
    requests.get(f"{URL}/ventas", params={"lento": 3}, timeout=1)
except requests.Timeout as e:
    print("Timeout:", type(e).__name__)
print(f"esperé {time.perf_counter() - inicio:.1f} s")
```

**Qué hace cada línea:**

- `params={"lento": 3}` — agrega `?lento=3` a la URL; el servidor de la clase espera 3 segundos antes de contestar.
- `timeout=1` — límite para conectarse y para cada espera de datos durante la lectura; **no** es un límite de la duración total. Aquí vence porque en 1 segundo no llega ningún byte.
- `except requests.Timeout` — atrapa el error que `requests` lanza al vencer el límite.

**Deberías ver:**

```text
Timeout: ReadTimeout
esperé 1.0 s
```

- `ReadTimeout`: la conexión se abrió, pero la respuesta no llegó a tiempo. **El servidor sí recibió la petición** y siguió trabajando.

## Reintentar: el cobro doble

Un timeout sólo dice que **no sabes** qué pasó. Hay tres posibilidades y el cliente no puede distinguirlas:

```text
(a) cliente ── POST ──────X                        servidor   (nunca llegó)
(b) cliente ── POST ─────────────────────────────▶ servidor   (la guardó)
    cliente ◀──────X──────── 201 ──────────────── servidor   (la respuesta se perdió)
(c) cliente ── POST ─────────────────────────────▶ servidor   (sigue trabajando)

    En los tres casos el cliente sólo ve lo mismo: 1 s sin respuesta → timeout, «no sé».
```

Si reintentas y era (b) o (c), **la operación se hace dos veces**. Con un `GET` o un `PUT` no importa: son idempotentes. Con un `POST` que crea una venta, o que cobra una tarjeta, sí importa.

**Haz (celda 3.4):** un POST lento, con timeout, y un reintento.

```python
requests.post(f"{URL}/reiniciar")  # sólo para la demo

venta_nueva = {"tienda": "Centro", "producto": "café", "cantidad": 1, "precio": 45.0}
for intento in [1, 2]:
    try:
        requests.post(f"{URL}/ventas", params={"lento": 2}, json=venta_nueva,
                      headers=TOKEN, timeout=1)
        print(f"intento {intento}: llegó la respuesta")
    except requests.Timeout:
        print(f"intento {intento}: timeout, no sé si se guardó")
time.sleep(2.5)
print("ventas:", total(), "(había 4)")
```

**Qué hace cada línea:**

- `params={"lento": 2}` con `timeout=1` — el servidor tarda 2 segundos; el cliente se rinde al segundo.
- `for intento in [1, 2]` — el reintento ingenuo: si falló, mándalo otra vez.
- `time.sleep(2.5)` — espera a que el servidor, que sigue trabajando, termine las dos peticiones antes de contar.

**Deberías ver:**

```text
intento 1: timeout, no sé si se guardó
intento 2: timeout, no sé si se guardó
ventas: 6 (había 4)
```

- El cliente cree que **ninguna** se guardó; el servidor guardó **las dos**. En su terminal ves los dos `POST /ventas` completos y dos `respondí 201`.
- Ésta es la forma más común de duplicar un pedido o un cobro.

## La solución: `Idempotency-Key`

**Definición.** `Idempotency-Key` es un header con un identificador que **el cliente genera una vez por operación** y repite en cada reintento. El servidor guarda la primera respuesta para esa llave; si la llave vuelve, **devuelve la respuesta guardada sin repetir la operación**.

**Para qué existe.** Convierte un `POST` en algo que se puede reintentar sin daño.

**En la vida real.** Stripe, la plataforma de pagos, lo usa en sus `POST`, guarda la respuesta y marca las repetidas. Hubo un borrador del IETF para estandarizarlo, pero **expiró en 2026 sin convertirse en estándar**. Es una convención extendida, no una regla de HTTP.

**Haz (celda 3.5):** el mismo POST tres veces, con la misma llave.

```python
requests.post(f"{URL}/reiniciar")  # sólo para la demo

llave = {"Idempotency-Key": "pedido-7f3a", **TOKEN}
for intento in [1, 2, 3]:
    r = requests.post(f"{URL}/ventas", json=venta_nueva, headers=llave)
    print(f"intento {intento}: {r.status_code}  id={r.json()['id']}  "
          f"repetida={r.headers.get('Idempotent-Replayed', 'no')}")
print("ventas:", total(), "(había 4)")
```

**Qué hace cada línea:**

- `{"Idempotency-Key": "pedido-7f3a", **TOKEN}` — un diccionario de headers con la llave y el token; `**TOKEN` copia el header `Authorization`.
- `r.headers.get('Idempotent-Replayed', 'no')` — el servidor de la clase, igual que Stripe, marca con este header las respuestas que repitió de su memoria.

**Deberías ver:**

```text
intento 1: 201  id=5  repetida=no
intento 2: 201  id=5  repetida=true
intento 3: 201  id=5  repetida=true
ventas: 5 (había 4)
```

- Tres envíos, **una sola venta** (`id=5` las tres veces). Los intentos 2 y 3 no tocaron los datos.
- La llave la genera el cliente **antes** del primer intento; si la cambias en cada intento, no protege nada.

## Códigos de estado: quién tiene que actuar

**Definición.** El **status** es un número de tres dígitos en la línea de estado. El primer dígito es la **clase**; los otros dos, el caso.

**Para qué existe.** Un programa decide qué hacer **sin leer el body**. La clase da la primera orientación; el código exacto y sus headers deciden: corregir, autenticarse, esperar, resolver un conflicto o reintentar.

| Clase | Significa | Quién actúa |
|---|---|---|
| **1xx** | Información intermedia; la respuesta final viene después | nadie (casi nunca lo ves) |
| **2xx** | Éxito | nadie: usa la respuesta |
| **3xx** | El recurso está en otro lado, o no cambió | el cliente sigue `Location` o usa su copia |
| **4xx** | El servidor rechazó la petición por algo del cliente o del estado actual del recurso | **el cliente**: según el código, corrige, se autentica, espera (429) o resuelve el conflicto (409) |
| **5xx** | El servidor no pudo completar una petición válida | **el cliente** reintenta más tarde, **sólo** si la operación es idempotente o lleva una `Idempotency-Key` |

| Código | Nombre | Cuándo |
|---|---|---|
| **200** | OK | Funcionó; el body trae el resultado |
| **201** | Created | Se creó un recurso; `Location` dice su URL |
| **202** | Accepted | Recibido, se procesará después; todavía no está hecho |
| **204** | No Content | Funcionó y no hay body (típico de `DELETE`) |
| **304** | Not Modified | Tu copia sigue vigente; no se manda body (página 4) |
| **400** | Bad Request | La petición está mal formada (body que no es JSON) |
| **401** | Unauthorized | **No autenticado**: falta credencial o no es válida. Lleva `WWW-Authenticate` |
| **403** | Forbidden | El servidor entendió la petición y **se niega a atenderla**; casi siempre, por falta de permiso |
| **404** | Not Found | Ese recurso no existe |
| **405** | Method Not Allowed | El recurso existe, ese método no. Lleva `Allow` con los permitidos |
| **409** | Conflict | Choca con el estado actual del recurso |
| **429** | Too Many Requests | Demasiadas peticiones; `Retry-After` dice cuándo volver |
| **500** | Internal Server Error | Error no previsto en el servidor |
| **503** | Service Unavailable | El servidor no puede atender ahora (sobrecarga, mantenimiento) |

- **401 se llama «Unauthorized» pero significa no autenticado**: el servidor no sabe quién eres. **403** significa que el servidor entendió y se niega; en este servidor, porque tu token sólo puede leer.

**En la vida real.**

- **Kubernetes** responde **409** si intentas reemplazar un objeto que alguien cambió desde que lo leíste (lo detecta con su campo `resourceVersion`). El mecanismo estándar de HTTP para lo mismo es mandar `If-Match` con la versión que leíste y recibir **412 Precondition Failed** si cambió.
- **GitHub**, al pasarte del límite de peticiones, responde **403 o 429** según el caso: el mismo problema con dos códigos.
- **Banxico** (su API SIE) respondió **400** a un token inválido el 2026-10-20, no 401. Funciona, pero un cliente genérico no sabrá que el problema es la credencial.

**Haz (celda 3.6):** provoca seis status distintos en el servidor de la clase.

```python
casos = [
    ("GET /ventas/1",          lambda: requests.get(f"{URL}/ventas/1")),
    ("POST /ventas sin token", lambda: requests.post(f"{URL}/ventas", json={})),
    ("POST /ventas lector",    lambda: requests.post(f"{URL}/ventas", json={},
                                         headers={"Authorization": "Bearer lector"})),
    ("POST /ventas body malo", lambda: requests.post(f"{URL}/ventas", data="hola", headers=TOKEN)),
    ("GET /ventas/99",         lambda: requests.get(f"{URL}/ventas/99")),
    ("PATCH /ventas/1",        lambda: requests.patch(f"{URL}/ventas/1", json={})),
]
for nombre, llamada in casos:
    r = llamada()
    print(f"{nombre:25} {r.status_code} {r.reason:20} "
          f"{r.json()['error'] if r.status_code >= 400 else ''}")
r = requests.patch(f"{URL}/ventas/1", json={})
print("Allow:", r.headers["Allow"])
```

**Qué hace cada línea:**

- `"Bearer lector"` — un token que el servidor reconoce, pero sólo con permiso de lectura.
- `data="hola"` — manda texto plano como body donde el servidor espera JSON.
- `r.reason` — la frase de la línea de estado (`Not Found`), para humanos.
- `r.json()['error']` — el servidor de la clase explica cada error en un JSON con la llave `error`.

**Deberías ver:**

```text
GET /ventas/1             200 OK
POST /ventas sin token    401 Unauthorized         falta el token o no es válido
POST /ventas lector       403 Forbidden            tu token es válido, pero sólo puede leer
POST /ventas body malo    400 Bad Request          el body no es JSON válido
GET /ventas/99            404 Not Found            no hay venta 99
PATCH /ventas/1           405 Method Not Allowed   este servidor no implementa PATCH
Allow: GET, HEAD, PUT, DELETE
```

- 401 contra 403: misma petición, distinta credencial, distinto culpable.
- El 405 dice qué **sí** puedes hacer (`Allow`). Un buen error orienta al cliente.

## El status es una promesa, no una prueba

El servidor escribe el status; nada obliga a que sea verdad. **jsonplaceholder** es una API pública de pruebas que acepta escrituras y responde 201, pero no guarda nada (lo comprobamos el 2026-10-20).

**Haz (celda 3.7):** crea un recurso y búscalo.

```python
r = requests.post("https://jsonplaceholder.typicode.com/posts", json={"title": "hola"}, timeout=5)
print("POST:", r.status_code, r.reason, "· Location:", r.headers.get("Location"))
r2 = requests.get(r.headers["Location"], timeout=5)
print("GET :", r2.status_code, r2.reason)
```

**Qué hace cada línea:**

- `requests.post(...)` — pide crear un recurso en una API real de internet.
- `r.headers["Location"]` — la URL donde, según el 201, quedó el recurso nuevo.
- `requests.get(...)` — va a buscarlo ahí.

**Deberías ver:**

```text
POST: 201 Created · Location: https://jsonplaceholder.typicode.com/posts/101
GET : 404 Not Found
```

- El servidor dijo «creado, está aquí» y ahí no hay nada. En un pipeline de datos, **verifica lo que importa** (vuelve a leerlo, cuenta filas) en vez de confiar sólo en el 2xx.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el método promete y los demás programas actúan sobre esa promesa; antes de reintentar, pregúntate si la operación es idempotente, porque un timeout sólo te dice «no sé».

Sigue con [[http-rest-y-crud]].
