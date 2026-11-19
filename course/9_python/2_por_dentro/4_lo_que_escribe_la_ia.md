---
id: lo-que-escribe-la-ia
title: "Lo que escribe la IA"
nav_title: "Lo que escribe la IA"
summary: "Cosas que la IA escribe en casi cada respuesta y que fallan sin error: el 0 tomado como vacío, el dinero en float, zip y el encoding; y cómo leer una comprehension."
status: ready
estimated_time: 10m
tags: [truthiness, float, decimal, comprehension, zip, encoding]
prerequisites: [el-gil]
---

# Lo que escribe la IA

**Página 4 de 5 · Python por dentro**

Meta: reconocer lo que la IA escribe en cada respuesta y falla sin error.

**En `revisa_esto.py`:** esto explica los síntomas 4 y 5.

## En corto

- **`if not x` trata el `0` como «vacío»**, igual que a `None` y a `""`.
- **El dinero no va en `float`**: `0.1 + 0.2 == 0.3` da `False`.
- **Hay cosas que fallan sin error**: `zip` con listas de largos distintos y un archivo leído con otro encoding (lectura).

## `if not x` trata el `0` como vacío

El síntoma 4 de `revisa_esto.py` dice que un descuento de 0 se cobró como 5 %, sin ningún error.
La **truthiness** es la regla con la que Python decide si un valor cuenta como verdadero o falso cuando lo pones en un `if`. `bool(valor)` te dice qué decide.

**Haz (celda 4.1):**

```python
print(bool(0), bool(0.0), bool(""), bool([]), bool({}), bool(None))
print(bool("0"), bool([0]))
```

**Qué hace cada línea:**

- `bool(0)`, `bool("")`, `bool([])`… — `True` si un `if` tomaría ese valor como verdadero, `False` si no. `""` es el texto vacío; `[]` la lista vacía; `{}` el diccionario vacío. `bool("0")` y `bool([0])` prueban el texto con un cero y la lista con un cero.

**Deberías ver:**

```text
False False False False False False
True True
```

- **El número `0` es falso**, igual que `None`: un `if` no los distingue. `"0"` y `[0]` son verdaderos: tienen un elemento.

**Haz (celda 4.2):**

```python
edad = 0
if not edad:
    print("if not edad:     sin edad")
if edad is None:
    print("if edad is None: sin edad")
else:
    print("if edad is None: edad", edad)
```

**Qué hace cada línea:**

- `edad = 0` — un bebé de 0 años: un dato válido, no un dato faltante.
- `if not edad:` — entra si `edad` es falso; la celda 4.1 mostró que `0` lo es.
- `if edad is None:` — entra sólo si `edad` es `None`, el valor que Python usa para «no hay dato». `is` compara si es el mismo objeto ([[nombres-y-objetos]]); `else:` corre cuando ese `if` no entró.

**Deberías ver:**

```text
if not edad:     sin edad
if edad is None: edad 0
```

- La misma `edad` da dos respuestas. **Sólo `is None` respeta el `0`.** La IA escribe `if not x` porque es corto. Falla cuando `0` es un valor válido: un descuento, un saldo, una edad.
- Busca en `revisa_esto.py` dónde se decide el descuento.

## `0.1 + 0.2` no es `0.3`

El síntoma 5: la contabilidad está en centavos; comparar el total sin redondear con `==` falla.

**Haz (celda 4.3):**

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
```

**Qué hace cada línea:**

- `0.1 + 0.2` — suma dos `float`, el tipo de Python para números con decimales; `== 0.3` compara si el resultado es exactamente `0.3`.

**Deberías ver:**

```text
0.30000000000000004
False
```

- Un `float` guarda la fracción en binario, y `0.1` no tiene representación exacta en binario: se guarda el binario más cercano. **El error es diminuto, pero `==` lo ve**: dos montos «iguales» salen distintos.

**Haz (celda 4.4):**

```python
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal(0.1))
```

**Qué hace cada línea:**

- `from decimal import Decimal` — trae **`Decimal`** del módulo estándar `decimal` (viene con Python): guarda el número en base 10 con los dígitos que le das.
- `Decimal("0.1")` — lo construye **desde texto**: guarda exactamente esos dígitos. `Decimal(0.1)` lo construye desde el `float`, que ya trae el error binario.

**Deberías ver:**

```text
0.3
True
0.1000000000000000055511151231257827021181583404541015625
```

- `print` muestra el `Decimal` como texto: `0.3`, exacto, y la comparación da `True`. **`Decimal(0.1)` hereda el error del float**: la tercera línea es lo que el float guardaba de verdad.

El dinero no va en `float`, pero `Decimal` solo no arregla el síntoma 5: ni `float` ni `Decimal` dan exactamente 2722.27 sin redondear (con `Decimal`, el total exacto es 2722.270020). El arreglo pide las dos cosas: montos con `Decimal` y comparar el total redondeado a centavos.

— Hasta aquí en clase; lo demás es lectura —

## Lectura · Una comprehension es un `for` en una línea

Una **comprehension** es una expresión que construye una lista recorriendo cualquier iterable (una lista, un `range`, un archivo), con un filtro opcional. La IA la escribe en casi cada respuesta.

**Haz (celda 4.5):**

```python
precios = [10, -3, 25]
dobles = []
for p in precios:
    if p > 0:
        dobles.append(p * 2)
print(dobles, [p * 2 for p in precios if p > 0])
```

**Qué hace cada línea:**

- `dobles = []` — una lista vacía donde el `for` junta los resultados; `dobles.append(p * 2)` agrega `p * 2` al final, sólo si pasó el `if p > 0`.
- `[p * 2 for p in precios if p > 0]` — la comprehension: lo mismo que las cuatro líneas de arriba. Se lee «`p * 2`, para cada `p` de `precios`, si `p > 0`».

**Deberías ver:**

```text
[20, 50] [20, 50]
```

- Las dos listas son iguales: el `-3` no pasó el filtro. Para leer una comprehension de la IA, reescríbela como ese `for`.

## Lectura · `zip` se detiene en la lista más corta

**Haz (celda 4.6):**

```python
nombres = ["ana", "beto", "carla"]
edades = [20, 31]
print(list(zip(nombres, edades)))
print(list(zip(nombres, edades, strict=True)))
```

**Qué hace cada línea:**

- `zip(nombres, edades)` — junta las dos listas por posición, en parejas `(nombre, edad)`; `list(...)` las vuelve lista para imprimirlas.
- `strict=True` — pide a `zip` que falle si las listas no miden lo mismo. Existe desde Python 3.10 (2021, PEP 618).

**Deberías ver:** (la segunda línea es la última del error)

```text
[('ana', 20), ('beto', 31)]
ValueError: zip() argument 2 is shorter than argument 1
```

- **`carla` desapareció sin aviso**: `zip` se detuvo cuando se acabaron las edades. Con `strict=True` el mismo código truena con un `ValueError` que dice cuál lista es la corta.

## Lectura · Leer un archivo con otro encoding cambia las letras sin error

Un **encoding** es la regla que convierte bytes en letras. UTF-8 escribe la `ñ` con dos bytes; si lees esos bytes con otra regla, salen dos letras distintas.

**Haz (celda 4.7):**

```python
with open("acentos.csv", "w", encoding="utf-8") as f:
    f.write("año,mañana,café")
with open("acentos.csv", encoding="latin-1") as f:
    print(f.read())
import os; os.remove("acentos.csv")
```

**Qué hace cada línea:**

- `with open("acentos.csv", "w", encoding="utf-8") as f:` — abre (y crea) el archivo para escribir (`"w"`) con la regla UTF-8; `with` lo cierra al terminar el bloque. `f.write(...)` escribe el texto en `por_dentro/`.
- `open("acentos.csv", encoding="latin-1")` — lo abre para leer con otra regla, latin-1. `import os; os.remove("acentos.csv")` borra el archivo, para que no termine en tu entrega.

**Deberías ver:**

```text
aÃ±o,maÃ±ana,cafÃ©
```

- No salió ningún error: **salió otro texto**. Cada letra con acento se volvió dos letras.

En Python 3.14, `open()` **sin** `encoding` usa la regla del sistema. cp1252 es la regla de Windows en español e inglés:

| Sistema | `open()` sin `encoding` lee con |
|---|---|
| Linux y macOS | UTF-8 |
| Windows en español o inglés | cp1252, salvo que actives el modo UTF-8 de Python |
| Python 3.15 (sale el 2026-10-09, PEP 686) | UTF-8 por defecto, salvo que lo apagues |

En 3.15, la variable de entorno `PYTHONUTF8=0` apaga ese UTF-8 por defecto.

Leer UTF-8 como cp1252 a veces da letras rotas sin error (`aÃ±o`) y a veces truena, según la letra: `Ángel` da `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 1: character maps to <undefined>`. Por eso **escribe siempre `encoding="utf-8"`**.

**Al revisar código de IA, busca:**

- `if not x` donde `0` es un valor válido (un monto, un descuento, una edad).
- Montos en `float` comparados con `==`.

**Al pedírselo a la IA, dile:**

- «Un `0` es un valor válido; usa `is None` para el dato faltante.»
- «Montos con `Decimal` y compara el total redondeado a centavos; el archivo es UTF-8.»

::: problem {#py-dentro-zip title="El cliente que no aparece"}
Juntas con `zip` una lista de 1000 clientes y una de 999 montos. El reporte sale sin ningún error y con 999 renglones. ¿Qué pasó con el cliente que falta?
:::

::: hint {of="py-dentro-zip"}
¿Qué hace `zip` cuando una de las listas se acaba antes que la otra?
:::

::: answer {of="py-dentro-zip"}
- `zip` se detiene en la lista más corta: el último cliente desaparece sin aviso.
- Con `strict=True` habría salido un `ValueError` en lugar de un reporte incompleto.
- Arreglo: usa `zip(..., strict=True)` y compara los largos con `len()` antes de juntar.
:::

Sigue con [[trabajar-con-ia]]: le pides a la IA un script, lo lees buscando estas cosas y lo pruebas.

> [!NOTE]
> **Si sólo recuerdas una cosa:** lo peligroso no es el error: es lo que falla sin error.
