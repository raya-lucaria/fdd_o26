---
id: que-es-una-api
title: "Qué es una API"
nav_title: "Qué es una API"
summary: "Una API es un contrato entre programas: qué puedes pedir, con qué datos y qué te regresa. Cuando el otro programa vive en otra máquina, la llamada cruza la red, y eso cambia la latencia, las fallas y quién controla el contrato."
status: ready
estimated_time: 10m
tags: [api, contrato, cliente, servidor, latencia, red]
prerequisites: [apis-y-http]
---

# Qué es una API

**Página 1 de 4 · APIs y HTTP**

Meta: saber qué es una API, en qué se distingue una API de biblioteca de una API web, y qué cambia cuando una llamada cruza la red.

| Término | Qué es | Lo ves con |
|---|---|---|
| **API** | Las operaciones que un programa ofrece a otros, con las reglas para usarlas | la celda 1.1 |
| **contrato** | Lo que la API promete: qué entra, qué sale, qué errores puede dar | el JSON de la celda 1.1 |
| **implementación** | El código que cumple el contrato; quien usa la API no lo ve | `servidor.py` |
| **cliente** | El programa que pide | tu notebook |
| **servidor** | El programa que recibe la petición y contesta | la terminal del servidor |
| **endpoint** | Una dirección concreta de una API web donde se pide una operación | `GET /ventas` |
| **latencia** | El tiempo entre que pides algo y te llega la respuesta | la celda 1.2 |
| **JSON** | Un formato de texto para datos: objetos `{…}`, listas `[…]`, números, texto, `true`/`false` y `null` | la respuesta de la celda 1.1 |

## En corto

- **Una API es un contrato**: dice *qué* puedes pedir y *qué* te regresa, nunca *cómo* lo calcula.
- **Una API web agrega red y serialización a cada llamada**: en una operación pequeña ese costo domina (miles de veces más lenta que una función, en la celda 1.2), y aparecen fallas que una función no tiene.
- **El contrato lo controla otro**: puede cambiarlo, cobrarlo o apagarlo.

## Una API es un contrato

**Definición.** Una **API** (*Application Programming Interface*, interfaz de programación de aplicaciones) es el conjunto de operaciones que un programa ofrece a otros programas, junto con las reglas para usarlas.

Las reglas forman el **contrato**. Un contrato completo dice cinco cosas:

| Parte | Pregunta que contesta | En `len()` de Python |
|---|---|---|
| **Operación** | ¿Qué puedo pedir? | el largo de algo |
| **Entrada** | ¿Qué datos mando y en qué forma? | un objeto con largo: lista, texto, dict |
| **Salida** | ¿Qué me regresa? | un entero ≥ 0 |
| **Errores** | ¿Qué pasa si pido mal? | `TypeError` si el objeto no tiene largo |
| **Reglas de uso** | ¿Límites, permisos, costo? | ninguna |

**Para qué existe.** Separa **interfaz** (el contrato) de **implementación** (el código que lo cumple). Quien usa la API depende sólo del contrato; quien la mantiene puede cambiar la implementación —otro algoritmo, otra base de datos, otro lenguaje— sin romper a nadie, mientras el contrato siga igual.

**Si lo ignoras.** Si tu código depende de un detalle que el contrato no promete (el orden en que llegan los resultados, un campo que «siempre» viene), se rompe el día que cambia la implementación, aunque nadie haya roto el contrato.

**Haz (celda 1.1):** pídele al servidor la lista de operaciones que ofrece.

```python
r = requests.get(f"{URL}/")
print(r.status_code)
for ruta, que_hace in r.json()["endpoints"].items():
    print(f"{ruta:22} {que_hace}")
```

**Qué hace cada línea:**

- `requests.get(f"{URL}/")` — pide la raíz del servidor, `/`, donde este servidor publica la lista de lo que ofrece.
- `r.status_code` — el número con el que el servidor dice cómo le fue; `200` es «bien». La página 3 los explica todos.
- `r.json()["endpoints"]` — convierte la respuesta, que llegó como texto JSON, en un dict de Python, y toma la parte `endpoints`.
- `f"{ruta:22} …"` — imprime cada endpoint alineado a 22 caracteres.

**Deberías ver:**

```text
200
GET /ventas            lista las ventas (filtra con ?tienda=Norte)
GET /ventas/{id}       una venta
POST /ventas           crea una venta (pide token)
PUT /ventas/{id}       reemplaza una venta completa (pide token)
DELETE /ventas/{id}    borra una venta (pide token)
GET /exportar          las ventas en CSV, desde un endpoint viejo
GET /panel             una página HTML con enlaces
GET /borrar?id={id}    borra con GET (mal diseño, a propósito)
POST /reiniciar        regresa los datos al inicio
```

- **Esto es una parte del contrato**: las operaciones. Un contrato completo también fija entradas, salidas, errores y reglas; las páginas 2 y 3 los muestran en acción. Nada de esto dice cómo guarda las ventas: eso es implementación.
- Las APIs reales publican su contrato en una página de documentación, y muchas también en un archivo que las máquinas leen (el formato más común se llama **OpenAPI**).

## API de biblioteca y API web

Hay dos tipos de API según **dónde corre** el código que la cumple.

| | API de biblioteca | API web |
|---|---|---|
| **Dónde corre** | En tu mismo proceso | En otro programa, casi siempre en otra máquina |
| **Cómo la llamas** | Llamas una función: `len(x)` | Mandas un mensaje por la red: `GET /ventas` |
| **Cómo viajan los datos** | Como objetos de Python, en memoria | Como bytes: hay que **serializarlos** (convertirlos a texto o bytes, p. ej. JSON) y deserializarlos |
| **Cuánto tarda** | Nanosegundos | Milisegundos o segundos |
| **Cómo falla** | Un error, al instante | Error, silencio, o respuesta que nunca llega |
| **Quién la cambia** | Tú decides cuándo actualizas la librería | El dueño del servidor, cuando él quiera |

```text
  API de biblioteca                    API web

  ┌─ tu proceso ───────────┐         ┌─ tu proceso ─┐                ┌─ otro proceso ─┐
  │  tu código             │         │  tu código   │   petición     │  servidor      │
  │     │ len(x)           │         │  (cliente)   │ ─────────────▶ │                │
  │     ▼                  │         │              │   respuesta    │                │
  │  código de Python      │         │              │ ◀───────────── │                │
  └────────────────────────┘         └──────────────┘      red       └────────────────┘
```

**Cliente** y **servidor** son *papeles*, no máquinas: el cliente es quien pide y el servidor quien contesta. Tu laptop es cliente cuando le pides datos a una API, y servidor cuando corres `servidor.py`. Hoy es las dos cosas.

Un **endpoint** es la combinación de método y ruta donde la API web ofrece una operación: `GET /ventas` y `POST /ventas` son dos endpoints distintos sobre la misma ruta.

## Lo que cambia al cruzar la red

**Haz (celda 1.2):** la misma consulta, como función y como llamada a la API.

```python
VENTAS = {1: {"id": 1, "producto": "café", "precio": 45.0}}

def venta(i):
    return VENTAS[i]

inicio = time.perf_counter()
for _ in range(1000):
    venta(1)
funcion = (time.perf_counter() - inicio) / 1000

sesion = requests.Session()
inicio = time.perf_counter()
for _ in range(200):
    sesion.get(f"{URL}/ventas/1")
red = (time.perf_counter() - inicio) / 200

print(f"función: {funcion * 1e6:10.3f} µs")
print(f"red:     {red * 1e6:10.3f} µs")
print(f"la red fue {red / funcion:,.0f} veces más lenta")
```

**Qué hace cada línea:**

- `def venta(i)` — la consulta como función: busca la venta en un dict en memoria.
- `time.perf_counter()` — un reloj de alta precisión; la resta de dos lecturas da segundos.
- `for _ in range(1000): venta(1)` — llama la función mil veces y luego divide entre mil: el tiempo de una llamada.
- `requests.Session()` — un cliente que reutiliza la misma conexión de red entre peticiones; sin él, cada petición abriría una conexión nueva y tardaría todavía más.
- `sesion.get(f"{URL}/ventas/1")` — la misma consulta, pero al servidor, por la red. 200 veces.
- `* 1e6` — convierte segundos a microsegundos (µs, millonésimas de segundo).

**Deberías ver** (en la máquina del profesor; tus números cambian, la proporción se parece):

```text
función:      0.127 µs
red:       1125.267 µs
la red fue 8,890 veces más lenta
```

- **Para una consulta así de pequeña, miles de veces más lenta, y sin salir de tu máquina.** Si el servidor hace algo pesado (un cálculo de minutos), la red pesa menos en el total; la proporción depende del trabajo y del entorno. El servidor corre en la misma laptop; con un servidor en otro país hay que sumar decenas o cientos de milisegundos de viaje.
- En la terminal del servidor pasaron 200 peticiones. Cada una se **serializó** a texto, viajó, se leyó, se respondió y se volvió a convertir en dict.

**Por qué importa al diseñar.** Un ciclo que llama una API una vez por fila es razonable con 100 filas y una catástrofe con un millón. Por eso las APIs ofrecen pedir muchos datos en una sola petición, y por eso conviene guardar en disco lo que ya descargaste.

### Tres supuestos falsos sobre la red

En 1994, Peter Deutsch, en Sun Microsystems, escribió una lista de supuestos que los programadores hacen sin darse cuenta y que siempre fallan; se conocen como las **falacias de la computación distribuida** (eran siete; James Gosling agregó la octava hacia 1997). Tres bastan para hoy:

| Supuesto falso | Lo que pasa en realidad | Dónde lo ves en esta clase |
|---|---|---|
| **La red es confiable** | Una petición puede perderse, o llegar y que se pierda la respuesta | celdas 3.3 y 3.4 |
| **La latencia es cero** | Cada llamada cuesta milisegundos, no nanosegundos | celda 1.2 |
| **El ancho de banda es infinito** | Bajar 300 KB por cada consulta se nota en el tiempo y en el costo | celda 4.1 |

La segunda fila tiene una consecuencia que la página 3 trabaja a fondo: una **falla parcial**. Cuando no llega la respuesta, el cliente no sabe si el servidor hizo el trabajo o no. En una función eso no existe: o regresó, o lanzó un error.

## El contrato es de otro

Cuando consumes una API web, el contrato y el servidor son de alguien más. Puede cambiarlo, cobrarlo o apagarlo, y tu código no tiene voto.

- **Twitter, febrero de 2023.** Anunció el 2 de febrero que el acceso gratuito a su API terminaba el 9 de febrero, con una semana de aviso; semanas antes ya había cortado a las apps de terceros como Tweetbot.
- **Reddit, junio de 2023.** Empezó a cobrar US$0.24 por cada 1,000 llamadas. El autor de Apollo, una app muy usada para leer Reddit, estimó que eso le costaría unos US$20 millones al año, y la cerró el 30 de junio de 2023.

**Para una fuente de datos esto significa:** guarda la respuesta cruda de cada descarga (el JSON tal como llegó) antes de transformarla. Si mañana la API cambia o desaparece, tus datos de ayer siguen ahí y puedes reprocesarlos.

## ¿API o archivo?

Muchas fuentes ofrecen las dos cosas: una API y un archivo descargable (CSV, Parquet). Elegir es una decisión de diseño.

| Si… | Conviene | Por qué |
|---|---|---|
| Los datos cambian seguido y necesitas lo último | **API** | El archivo envejece en cuanto lo bajas |
| Necesitas una parte pequeña de algo enorme | **API** | Pides sólo esa parte (filtros en la URL) |
| Necesitas todo el histórico, una vez | **Archivo** | Una descarga contra miles de llamadas |
| Vas a repetir el análisis muchas veces | **Archivo** (o guarda lo de la API) | No dependes de que el servidor siga ahí ni pagas cada lectura |
| La API tiene límite de peticiones | **Archivo**, si existe | El límite no aplica a una descarga única |

> [!NOTE]
> **Si sólo recuerdas una cosa:** una API web es un contrato que se cumple por la red; cada llamada es miles de veces más lenta que una función, puede fallar a medias, y el contrato lo controla otro.

Sigue con [[el-mensaje-http]].
