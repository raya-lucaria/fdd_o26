---
id: nombres-y-objetos
title: "Nombres y objetos"
nav_title: "Nombres y objetos"
summary: "En Python, = no copia: pone otro nombre al mismo objeto. Si el objeto es mutable, un cambio se ve desde todos sus nombres."
status: ready
estimated_time: 15m
tags: [asignacion, mutabilidad, copy, deepcopy, argumento-por-defecto]
prerequisites: [que-es-python]
---

# Nombres y objetos

**Página 2 de 5 · Python por dentro**

Meta: predecir cuándo un cambio en una variable aparece en otra.

**En `revisa_esto.py`:** esto explica el síntoma 2.

## En corto

- **`=` no copia**: pone otro nombre (una variable) al mismo objeto (el dato que vive en memoria).
- **Listas, dicts y sets son mutables**, se pueden cambiar sin crear otro objeto: un cambio se ve desde todos los nombres que apuntan ahí.
- **`is` pregunta si es el mismo objeto**; `==`, si vale lo mismo.

::: figure {#py-nombres title="Nombres que apuntan a objetos"}
![Dos paneles. En el primero, los nombres a y b tienen flechas hacia la misma lista [1, 2, 3, 4]; el nombre c, creado con c = a.copy(), apunta a otra lista distinta. En el segundo, el nombre datos apunta a un dict y copia, creado con datos.copy(), apunta a otro dict; pero la llave "ventas" de los dos dicts tiene una flecha hacia la misma lista interna [10, 20, 30]. Al pie: .copy() copia un nivel; lo de adentro se comparte.](../_assets/py-nombres.svg)
:::

## `=` no copia

**Haz (celda 2.1):**

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a, a is b)
```

**Qué hace cada línea:**

- `a = [1, 2, 3]` — crea una lista y le pone el nombre `a`.
- `b = a` — le pone un segundo nombre, `b`, a **esa misma** lista. No se crea ninguna lista nueva.
- `b.append(4)` — `.append` agrega un elemento al final de la lista que nombra `b`.
- `print(a, a is b)` — imprime `a` y si `a` y `b` son el mismo objeto.

**Deberías ver:**

```text
[1, 2, 3, 4] True
```

- Cambiaste `b` y apareció el `4` en `a`: hay **una sola lista** con dos nombres.
- `True` lo confirma: `is` compara identidad, no contenido. **Usa `is` con `None`** (`if x is None`) y con otros objetos únicos; para comparar valores, `==`.

Lo inmutable no cambia: se reemplaza. Los objetos **inmutables** (`int`, `str`, tuplas que no contienen listas) no se pueden cambiar: `x += 1` crea otro número y mueve el nombre `x`. Una tupla con una lista adentro sí ve cambiar esa lista.

## Copiar es explícito, y de un nivel

**Haz (celda 2.2):**

```python
datos = {"ventas": [10, 20]}
copia = datos.copy()
copia["ventas"].append(30)
print(datos)
```

**Qué hace cada línea:**

- `datos = {"ventas": [10, 20]}` — un dict con una llave, `"ventas"`, cuyo valor es una lista.
- `copia = datos.copy()` — `.copy()` crea un dict nuevo con las mismas llaves; los valores **no se copian**: el dict nuevo apunta a los mismos objetos.
- `copia["ventas"].append(30)` — agrega `30` a la lista que guarda `copia`.
- `print(datos)` — imprime el dict original.

**Deberías ver:**

```text
{'ventas': [10, 20, 30]}
```

- El original cambió: los dos dicts son distintos, pero su lista `"ventas"` es la misma (el panel 2 de la figura).

**Haz (celda 2.2, debajo del código anterior, sin borrarlo):** pega esto y vuelve a correr la celda.

```python
import copy
datos = {"ventas": [10, 20]}
copia = copy.deepcopy(datos)
copia["ventas"].append(30)
print(datos)
```

**Qué hace cada línea:**

- `import copy` — trae el módulo `copy` de la biblioteca estándar.
- `copy.deepcopy(datos)` — copia el dict **y todo lo que tiene adentro**, a cualquier profundidad. Las otras líneas son las de arriba.

**Deberías ver:** la celda imprime las dos líneas.

```text
{'ventas': [10, 20, 30]}
{'ventas': [10, 20]}
```

- Con `deepcopy`, el original queda en `[10, 20]`: ahora sí hay dos listas.

| Para copiar una lista `a` | ¿Copia? |
|---|---|
| `b = a` | ❌ otro nombre, mismo objeto |
| `a.copy()`, `list(a)`, `a[:]` | ✅ un nivel: lo de adentro se comparte |
| `copy.deepcopy(a)` | ✅ todo |

## La función recibe el mismo objeto

**Haz (celda 2.3):**

```python
def duplica(nums):
    for i in range(len(nums)):
        nums[i] = nums[i] * 2

originales = [100, 200]
duplica(originales)
print(originales)
```

**Qué hace cada línea:**

- `def duplica(nums):` — define una función; `nums` es el nombre que recibe lo que le pases.
- `for i in range(len(nums)):` — recorre las posiciones `0, 1, …` de la lista.
- `nums[i] = nums[i] * 2` — cambia el elemento en la posición `i` **dentro de la lista recibida**.
- `duplica(originales)` — llama a la función con tu lista. No devuelve nada.

**Deberías ver:**

```text
[200, 400]
```

- `nums` y `originales` son dos nombres de la misma lista: la función cambió **tu** lista. Pasa lo mismo con `.append`, `.sort()` o `del lista[i]`.

## El valor por defecto se crea una sola vez

Un **valor por defecto** es el que toma un parámetro si no lo pasas al llamar: en `def registra(evento, log=[])`, si no das `log`, vale `[]`.

**Haz (celda 2.4):**

```python
def registra(evento, log=[]):
    log.append(evento)
    return log

print(registra("inicio"))
print(registra("fin"))
```

**Qué hace cada línea:**

- `def registra(evento, log=[]):` — `log` tiene como valor por defecto una lista vacía. Las dos llamadas de abajo no pasan `log`: usan ese valor.
- `log.append(evento)` y `return log` — agrega el evento a esa lista y la devuelve.

**Deberías ver:**

```text
['inicio']
['inicio', 'fin']
```

- La segunda llamada ve el `'inicio'` de la primera: el valor por defecto se crea **una vez, cuando corre el `def`**, y todas las llamadas comparten esa misma lista.

**Al revisar código de IA, busca:**

- `def f(x=[])` o `def f(x={})`: un valor por defecto mutable, compartido entre llamadas.
- Una función que hace `.append(`, `.sort()` o `lista[i] =` sobre lo que recibió como parámetro.

**Al pedírselo a la IA, dile:**

- «No modifiques la entrada: devuelve una nueva.»
- «Nada de valores por defecto mutables.»

::: problem {#py-dentro-alias title="La tabla original salió ordenada"}
Un compañero ordena `ventas` dentro de una función, para calcular la mediana. Al final, la tabla original del reporte sale ordenada, y nadie la ordenó a propósito. ¿Qué pasó?
:::

::: hint {of="py-dentro-alias"}
¿Cuántas listas hay: la del reporte y la de la función, o una sola?
:::

::: answer {of="py-dentro-alias"}
- Hay una sola lista, con dos nombres: el del reporte y el parámetro de la función.
- `.sort()` cambia esa lista en su lugar; por eso el reporte la ve ordenada.
- Arreglo: `sorted(ventas)` devuelve otra lista ordenada y deja la original como estaba.
:::

Sigue con [[el-gil]]: por qué cuatro hilos calculando tardan casi lo mismo que uno.

> [!NOTE]
> **Si sólo recuerdas una cosa:** `=` pone otro nombre al mismo objeto; si es mutable, los dos ven el cambio.
