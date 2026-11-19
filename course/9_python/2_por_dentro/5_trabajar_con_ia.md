---
id: trabajar-con-ia
title: "Trabajar con IA: pedir, leer, probar"
nav_title: "Trabajar con IA"
summary: "Un prompt vago produce un script con cinco síntomas; un prompt que dice versión, entradas, casos borde y cómo verificar los evita. Lo que regresa se lee y se corre antes de creerle."
status: ready
estimated_time: 25m
tags: [ia, prompt, especificacion, type-hints, revision-de-codigo]
prerequisites: [lo-que-escribe-la-ia]
---

# Trabajar con IA: pedir, leer, probar

**Página 5 de 5 · Python por dentro**

Meta: escribir un prompt que evite los cinco síntomas, y revisar lo que regresa.

## En corto

- **El prompt es una especificación**: versión, entradas, salidas, casos borde y cómo se verifica.
- **Lo que regresa se lee y se corre** antes de creerle.
- **Pide primero las firmas** —la línea `def nombre(entradas) -> salida` de cada función— y los casos borde; después el código.

::: figure {#py-sintomas title="La salida de revisa_esto.py y sus cinco síntomas"}
![La salida de revisa_esto.py con cinco recuadros numerados. 1: la región norte no lista a Carla Ríos y no hay ningún mensaje de error. 2: norte lista a Fátima López y Gael Muñoz, clientes de centro. 3: puntaje con hilos 2.51 s y puntaje sin hilos 1.76 s. 4: el total de norte, 325.12, donde la cuenta a mano da 336.73 sin Carla. 5: la última línea, La contabilidad NO cuadra. La figura no señala líneas de código ni causas.](../_assets/py-sintomas.svg)
:::

## Paso 1 · El prompt vago

Éste es el prompt que produjo el script de la clase:

```text
Hazme un script en Python que lea ventas.csv y, por región, dé el total con IVA
(16 %) y la lista de clientes. Usa la función puntaje(cliente) de puntaje.py
para el puntaje de cada cliente. Al final, que diga si el total cuadra con la
contabilidad, que es 2722.27. Que sea rápido.
```

No dice qué versión de Python, cómo vienen los montos, qué hacer con una fila mal escrita ni qué significa «rápido». Tampoco menciona la columna `descuento`, y la respuesta del modelo, sin editar, la ignoró.

La respuesta original no viene en tu plantilla: se publica al vencer la tarea. Éstas son las últimas 4 líneas de su salida, la conciliación:

```text
Total sin IVA:     $2,501.91
Total con IVA:     $2,902.22
Contabilidad:      $2,722.27
NO CUADRA: diferencia de $179.95 (calculado - contabilidad).
```

- La diferencia de 179.95 son los descuentos que el script nunca restó.
- **Lo que no pides no aparece**: el modelo no adivinó una columna que el prompt no nombró.

## Paso 2 · Leer

**Haz (celda 0.1):** ya la corriste al arrancar la clase; si no ves su salida, córrela otra vez.

```python
import sys
!{sys.executable} revisa_esto.py
```

**Qué hace cada línea:**

- `!{sys.executable} revisa_esto.py` — corre el script de la clase con el Python del notebook: la respuesta al prompt vago con cinco errores plantados a mano (la nota de abajo dice cómo se hizo).

**Deberías ver:** (los segundos cambian en tu máquina)

```text
== centro ==
Total con IVA: $503.82
Clientes:
  - Fátima López
  - Gael Muñoz
  - Beto Peña

== norte ==
Total con IVA: $325.12
Clientes:
  - Fátima López
  - Gael Muñoz
  - Beto Peña
  - Ana Núñez
…
puntaje con hilos: 2.51 s
puntaje sin hilos: 1.76 s

== Conciliación ==
Total con IVA:     $1,388.26
Contabilidad:      $2,722.27
La contabilidad NO cuadra
```

- «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario del código promete 4× más rápido. Tus segundos cambian en cada corrida.

Los cinco síntomas y la cuenta del síntoma 4 están en [[python-por-dentro]]; tenla abierta.

**Haz (editor, 5 min):** abre `revisa_esto.py` en VS Code. Para cada síntoma, anota en `revision.md` la línea que crees que lo produce. Si en 5 min no la encuentras, sigue: la tarea te da más tiempo.

## Paso 3 · El prompt como especificación

Tres cosas en este paso: el prompt, las firmas que regresó el modelo y la corrida.

Cada síntoma se evita con una frase en el prompt, sin decirle a la IA qué línea falló:

| Para evitar el síntoma… | Le dices |
|---|---|
| 1 · Una venta desaparece sin aviso | «una fila mal formada se reporta, nunca se salta en silencio» |
| 2 · Una región lista clientes de otra | «ninguna función modifica lo que recibe ni usa valores por defecto mutables» |
| 3 · Los hilos no aceleran | «puntaje calcula (CPU): usa ProcessPoolExecutor con la guarda `if __name__ == "__main__":`, y mide el tiempo» |
| 4 · El descuento 0 se cobra como 5 % | «un 0 es un valor válido: sin descuento» |
| 5 · El total sin redondear no cuadra | «montos con Decimal y comparar el total redondeado a centavos» |
| Que no corra igual en otra máquina | «Python 3.14; se corre con `uv run`»; «ventas.csv, UTF-8» |

Un **type hint** es la anotación que dice qué entra y qué sale de una función: `def total(montos: list[Decimal]) -> Decimal`. Python **no lo verifica al correr**, pero tú lo lees en 10 segundos.

`Decimal` sola no arregla el síntoma 5: el total exacto con `Decimal` es 2722.270020, no 2722.27. Por eso el prompt pide comparar el total **redondeado a centavos**.

Lo general sigue en pie: el dinero no va en `float` (`0.1 + 0.2` da `0.30000000000000004`).

El prompt completo:

```text
Escribe resume_ventas.py para Python 3.14; se corre con `uv run resume_ventas.py`
en un proyecto uv, sólo con la biblioteca estándar.
Entrada: ventas.csv, UTF-8, columnas region,cliente,monto,descuento. monto es
texto con dos decimales y puede traer coma de miles ("1,200.00") o venir mal
escrito. descuento es una fracción entre 0 y 1; un 0 es un valor válido: sin
descuento.
Salida: por región, el total con IVA (16 %) y sus clientes; el puntaje de cada
cliente con puntaje(cliente) de puntaje.py; las filas que no se pudieron leer,
con su número de línea y el motivo; y si el total general, redondeado a
centavos, es igual a Decimal("2722.27").
Reglas: montos con Decimal, nunca float. Ninguna función modifica lo que recibe
ni usa valores por defecto mutables. Una fila mal formada se reporta, nunca se
salta en silencio. puntaje calcula (CPU): usa ProcessPoolExecutor con la guarda
if __name__ == "__main__":, y mide el tiempo.
Antes del código, dame la firma de cada función con type hints y un caso de
prueba por rama, incluidos: archivo vacío, monto con coma de miles, descuento 0.
```

Antes del código, el modelo regresó las firmas de doce funciones. Se leen sin correr nada; éstas son seis (todas están en `resume_ventas.py`):

```text
type Puntaje = float
def parsear_monto(texto: str) -> Decimal                       # ValueError(motivo)
def parsear_fila(campos: Sequence[str], linea: int) -> Venta | FilaInvalida
def redondear_centavos(valor: Decimal) -> Decimal
def cuadra(total: Decimal, esperado: Decimal = ESPERADO) -> bool   # default inmutable
def calcular_puntajes(clientes: Iterable[str]) -> Puntajes
```

- `-> Decimal` en `parsear_monto`: los montos no pasan por `float`. `-> Venta | FilaInvalida` (`|` se lee «o»): una fila puede salir mal, y la firma ya lo dice.
- Ojo: la firma dice `Puntaje = float`, pero `puntaje()` devuelve `int`; Python no lo verifica. Leer la firma no basta: hay que correrla.

**Haz (celda 5.1):**

```python
import sys
!{sys.executable} resume_ventas.py
```

**Qué hace cada línea:**

- `!{sys.executable} resume_ventas.py` — corre la respuesta del modelo al prompt del paso 3, sin editar, con el Python del notebook. Va como script y no pegada en una celda porque lanza procesos, y un proceso nuevo no puede leer una celda (lo viste en [[el-gil]]).

**Deberías ver:** (los segundos cambian en tu máquina)

```text
== Totales por región (con IVA 16 %) ==
centro: 503.82  clientes: Beto Peña, Fátima López, Gael Muñoz
norte: 1659.14  clientes: Ana Núñez, Beto Peña, Carla Ríos
sur: 559.31  clientes: Ana Núñez, Dana Ibáñez, Emilio Sáenz

== Puntaje por cliente ==
…
(puntajes calculados en 1.200 s)

== Filas no leídas: 0 ==

Total general: 2722.27
¿Igual a 2722.27? sí
Tiempo total: 1.200 s
```

- Carla Ríos aparece en `norte`, y `Filas no leídas: 0` dice que ninguna fila se perdió.
- Cada región lista sólo sus clientes, y `¿Igual a 2722.27? sí`.
- **Los síntomas desaparecieron sin editar el código a mano: cambió el prompt.** Aun así lo corriste antes de creerle.

> [!NOTE]
> **De dónde salen los scripts.** `resume_ventas.py` es la respuesta de claude-opus-5-5 (2026-10-06) al prompt del paso 3, **sin editar**. `revisa_esto.py` **no** es la salida literal de un modelo: partimos de la respuesta de claude-opus-5-5 (2026-10-06) al prompt del paso 1, le **plantamos a mano cinco errores**, cada uno de un tipo que aparece en código generado por IA, y para plantarlos reescribimos y añadimos otras partes. La respuesta original, sin editar, y el detalle de lo que cambiamos se publican el 2026-10-13, cuando vence la tarea: antes serían la clave.

::: problem {#py-dentro-prompt title="Lo que le falta a un prompt"}
Vas a pedirle a la IA un script que lea un CSV de una API pública. ¿Qué tres datos le faltan a «léelo y dame el promedio»?
:::

::: hint {of="py-dentro-prompt"}
Recorre la tabla del paso 3: ¿qué fila no cubre esa frase?
:::

::: answer {of="py-dentro-prompt"}
- La versión de Python y cómo se corre (`uv run`).
- El encoding del archivo, y qué hacer con las filas mal escritas.
- Arreglo: agrégalos al prompt, con un caso de prueba por rama, y pide las firmas antes que el código.
:::

Sigue con [[entregas-por-dentro]]: qué entregas y cómo.

> [!NOTE]
> **Si sólo recuerdas una cosa:** un buen prompt dice versión, entradas, casos borde y cómo verificar; lo que regresa se corre antes de creerle.
