---
id: que-es-python
title: "Qué es Python"
nav_title: "Qué es Python"
summary: "Python encuentra un error de tipo hasta que su línea corre, y un except que no hace nada lo esconde: por eso una venta puede desaparecer sin aviso."
status: ready
estimated_time: 15m
tags: [cpython, typeerror, except, bytecode, dis]
prerequisites: [python-por-dentro]
---

# Qué es Python

**Página 1 de 5 · Python por dentro**

Meta: saber en qué momento encuentra Python los errores, y cómo un `except` puede esconderlos.

**En `revisa_esto.py`:** esto explica el síntoma 1.

## En corto

- **CPython es el programa que ejecuta tu código**: el `python` que instala uv.
- **Un error de tipo aparece cuando su línea corre**; uno de sintaxis, antes de correr cualquier línea de ese archivo.
- **Un `except` que no hace nada esconde el error**: el programa sigue y no avisa.

Todo el código de esta página va en `por_dentro.ipynb`, dentro de tu carpeta `estudiantes/<tu-login>/09_python/por_dentro/` (la armaste con el ritual de [[python-por-dentro]]). Cada Haz tiene en el notebook un título con su número y una celda vacía debajo: pega el código ahí y córrela con Shift+Enter. De funciones, aquí va lo justo para leer los ejemplos; DataCamp las enseña a fondo.

## Una función en 30 segundos

**Haz (celda 1.0):**

```python
def doble(x):
    return x * 2

doble(21)
```

**Qué hace cada línea:**

- `def doble(x):` / `return x * 2` — define una función llamada `doble`. `x` es su **parámetro**: el nombre que recibe el valor que le pases. La línea con sangría (4 espacios) es parte de la función: devuelve `x` por dos.
- `doble(21)` — **llama** a la función: la ejecuta con `x` valiendo `21`. En un notebook, el valor de la última línea de la celda se muestra solo.

**Deberías ver:**

```text
42
```

- Definir la función no imprime nada; el `42` sale de la llamada. Si ves `IndentationError`, la sangría quedó distinta: 4 espacios antes de `return`.

## El error de tipo espera a que su línea corra

**Haz (celda 1.1):**

```python
def precio_final(precio, descuento):
    if descuento > 0:
        return precio * (1 - descuento)
    return precio + " sin descuento"
```

**Qué hace cada línea:**

- `def precio_final(precio, descuento):` / `if descuento > 0:` — una función con dos parámetros; la **rama** de arriba (el bloque con sangría) corre sólo si hay descuento.
- `return precio * (1 - descuento)` — con descuento `0.1`, devuelve el 90 % del precio.
- `return precio + " sin descuento"` — la otra rama: suma un número y un texto. Ésta es la línea mala.

**Deberías ver:** nada; la celda no imprime. Python **aceptó** la función con la línea mala adentro: no la revisó por tipos.

**Haz (celda 1.2):**

```python
precio_final(100, 0.1)
```

**Qué hace cada línea:**

- `precio_final(100, 0.1)` — llama a la función con precio `100` y descuento de 10 %.

**Deberías ver:**

```text
90.0
```

- Funciona. La línea mala no corrió: con `0.1` la función sale por la primera rama.

**Haz (celda 1.3):** esta celda **falla a propósito**. El cuadro rojo es lo que debe salir.

```python
precio_final(100, 0)
```

**Qué hace cada línea:**

- `precio_final(100, 0)` — la misma función con descuento `0`: ahora `descuento > 0` es falso y corre la otra rama.

**Deberías ver:** (el `In[…]` cambia según cuántas celdas hayas corrido)

```text
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
Cell In[4], line 1
----> 1 precio_final(100, 0)

Cell In[2], line 4, in precio_final(precio, descuento)
      1 def precio_final(precio, descuento):
      2     if descuento > 0:
      3         return precio * (1 - descuento)
----> 4     return precio + " sin descuento"

TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

- La flecha `---->` señala la línea 4, la que sólo corre con descuento `0`. Un **error de tipo** (`TypeError`) sale cuando una operación recibe datos que no sabe combinar: aquí un entero (`int`) más un texto (`str`). Python lo descubre **al correr esa línea**, no antes.
- Un **caso borde** es una entrada en el límite: `0`, una lista vacía, `None`, una fila mal escrita. Ahí viven las ramas que nadie probó.

## Un `except` que no hace nada lo esconde

**Haz (celda 1.4):**

```python
try:
    precio_final(100, 0)
except Exception:
    pass
print("terminé sin errores")
```

**Qué hace cada línea:**

- `try:` / `precio_final(100, 0)` — `try` intenta el bloque con sangría: aquí, la misma llamada que falló en la celda 1.3.
- `except Exception:` / `pass` — si algo falla en el `try`, corre este bloque: atrapa cualquier error común (`Exception` los abarca casi todos) y `pass` es «no hagas nada»: ni lo imprime ni lo guarda. Al final, `print(…)` imprime el mensaje.

**Deberías ver:**

```text
terminé sin errores
```

- El `TypeError` ocurrió igual que en la celda 1.3, y **no dejó rastro**: el precio de esa venta no se calculó. **Éste es el síntoma 1** de `revisa_esto.py`: una venta no aparece en el total, sin aviso.

## Python traduce primero y ejecuta después

::: figure {#py-interprete title="Cuándo encuentra Python cada error"}
![Una fila de cajas de izquierda a derecha: tu_script.py, luego compila (traduce el archivo a bytecode), luego el bytecode (una lista de instrucciones simples), luego la máquina virtual (la parte de CPython que ejecuta esas instrucciones) y al final el resultado. Bajo compila, una marca dice: errores de sintaxis, aquí, antes de correr. Bajo la máquina virtual, otra marca dice: errores de tipo, aquí, al correr.](../_assets/py-interprete.svg)
:::

**CPython** es el programa, escrito en C, que corre tu código. Python primero **compila** tu archivo (lo traduce a **bytecode**, una lista de instrucciones simples) y luego lo ejecuta. Los errores de sintaxis salen al compilar; los de tipo, al ejecutar.

| Error | Cuándo sale | Ejemplo |
|---|---|---|
| De sintaxis (`SyntaxError`) | Al compilar: no corre **ninguna** línea | falta un `:` o un paréntesis |
| De tipo (`TypeError`) | Al correr **esa** línea, y sólo si corre | la celda 1.3 |

Por eso la celda 1.1 no se quejó: la línea 4 está bien escrita. Lo que no corrió, no está probado.

— Hasta aquí en clase; lo demás es lectura —

## Lectura · El intérprete es un programa que puedes ver

**Haz (celda 1.5):**

```python
import sys, platform
from pathlib import Path
print(sys.version)
print(platform.python_implementation())
print(Path(sys.executable).relative_to(Path.cwd()))
```

**Qué hace cada línea:**

- `import sys, platform` / `from pathlib import Path` — traen de la biblioteca estándar `sys` (datos del intérprete), `platform` (datos de la máquina) y `Path` (rutas de archivos).
- `print(sys.version)` / `print(platform.python_implementation())` — la versión exacta de Python que corre esta celda, y qué programa la corre.
- `print(Path(sys.executable).relative_to(Path.cwd()))` — `sys.executable` es la ruta del intérprete; `relative_to(Path.cwd())` la muestra desde tu carpeta actual, así la salida no publica la carpeta de tu máquina.

**Deberías ver:** (la fecha y el compilador pueden cambiar)

```text
3.14.0 (main, Oct 28 2025, 12:13:17) [Clang 20.1.4 ]
CPython
.venv/bin/python3
```

- `3.14.` y un número: la versión que fijó `.python-version`; el último número puede ser otro. `CPython`: el intérprete es un programa más, el que uv bajó.
- `.venv/bin/python3`: corre el del ambiente del proyecto (eso imprime Linux). `.venv/bin/python` es el mismo archivo con otro nombre; en Windows sale `.venv\Scripts\python.exe`. Si sale `ValueError`, el kernel no es el de `.venv`: revisa el kernel en [[python-por-dentro]].

## Lectura · Tu código se vuelve bytecode

**Haz (celda 1.6):**

```python
import dis

def suma(a, b):
    return a + b

dis.dis(suma)
```

**Qué hace cada línea:**

- `def suma(a, b):` / `return a + b` — una función que suma sus dos parámetros.
- `import dis` / `dis.dis(suma)` — `dis` (de *disassemble*) imprime las instrucciones en que CPython tradujo `suma`: las que corre, una por una, su **máquina virtual** (la parte de CPython que ejecuta el bytecode).

**Deberías ver:** (recortado a propósito: sólo las líneas de `a + b`, hasta `BINARY_OP`)

```text
  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
              BINARY_OP                0 (+)
```

- `BINARY_OP 0 (+)` es la suma. **No dice de qué tipo**: `+` no sabe si sumará números o textos hasta que corre.
- `__pycache__/` guarda el bytecode de los módulos que importas (no del script que corres directo). No va a git.

### Qué es el bytecode, y por qué existe

El **bytecode** es una lista de instrucciones simples que CPython genera a partir de tu código **antes** de correrlo. No es código de máquina: no lo ejecuta el procesador, lo ejecuta la **máquina virtual** de CPython, un ciclo que lee una instrucción, la hace y pasa a la siguiente.

**Por qué no correr el texto directo:** analizar el texto de un programa (dónde empieza cada palabra, qué significa cada paréntesis) es caro. Traducirlo **una vez** a instrucciones simples, y ejecutar ésas, es más rápido. Y el mismo bytecode corre en cualquier sistema donde exista CPython. Python lo hace así desde sus primeras versiones (1991); los `.pyc` de `__pycache__/` guardan esa traducción para no repetirla.

**No es invento de Python.** La idea viene del *p-code* de UCSD Pascal (finales de los 70) y la usan, entre otros:

| Lenguaje | Su bytecode | Desde |
|---|---|---|
| Java | archivos `.class`, que corre la JVM | 1995 |
| C# y .NET | CIL | 2002 |
| Ruby | YARV | 1.9, 2007 |
| Navegadores | WebAssembly | 2017 |

**Cómo funciona: una pila.** La máquina virtual de CPython trabaja con una **pila**, una lista donde las instrucciones ponen valores arriba y los sacan de arriba. Así corre `suma(2, 3)` (la salida completa de `dis` agrega `RESUME`, que sólo marca el inicio, y `RETURN_VALUE`):

| Instrucción | Qué hace | La pila queda |
|---|---|---|
| `LOAD_FAST_BORROW_LOAD_FAST_BORROW (a, b)` | pone `a` y `b` en la pila: dos cargas de variables locales juntas en una instrucción (3.14) | `2, 3` |
| `BINARY_OP (+)` | saca los dos de arriba, los suma y pone el resultado | `5` |
| `RETURN_VALUE` | saca el de arriba y lo regresa | vacía; `suma` regresa `5` |

- **El bytecode no lleva tipos**: `BINARY_OP (+)` es la misma instrucción para números y para textos. Por eso Python no te avisa de un error de tipo antes de correr la línea.
- Desde 3.11 (2022, PEP 659) la máquina virtual **se especializa**: si un `BINARY_OP` siempre ve enteros, lo cambia por una versión sólo para enteros, más rápida. Fue lo que hizo a 3.11 notablemente más rápido.
- Desde 3.13 (2024, PEP 744) hay un **JIT** experimental: traduce el bytecode que más se repite a código de máquina.

**Haz (celda 1.7):**

```python
print(suma(2, 3))
print(suma("hola, ", "mundo"))
print(suma(2, "3"))
```

**Qué hace cada línea:**

- `suma(2, 3)` / `suma("hola, ", "mundo")` — el mismo bytecode con dos números (los suma) y con dos textos (los pega).
- `suma(2, "3")` — un número y un texto: falla **a propósito**.

**Deberías ver:** (recortado: del cuadro rojo queda la última línea)

```text
5
hola, mundo
…
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

- Tres llamadas, una sola instrucción `BINARY_OP`. El tipo se decide al correr: por eso el error también.

## Lectura · De dónde viene

Guido van Rossum lo empezó en 1989; la versión 0.9.0 salió en febrero de 1991.

| Año | Qué pasó | Por qué te importa |
|---|---|---|
| 2008-12-03 | Python 3 rompe compatibilidad con Python 2 | `print "x"` es `SyntaxError` en Python 3: si la IA te lo da, es Python 2 |
| 2020-01-01 | Python 2 deja de recibir arreglos (la última, 2.7.18, salió en abril de 2020) | Código de Python 2 ya no recibe parches de seguridad |
| Desde 3.9 (2020) | Una versión nueva cada octubre (PEP 602) | La versión decide qué sintaxis existe |
| 3.13 (2024) · 3.14 (2025) | Build sin GIL: experimental en 3.13; soportado pero opcional en 3.14. La 3.15 sale el 2026-10-09 | El GIL se explica en [[el-gil]] |

**Al revisar código de IA, busca:**

- `except Exception: pass` o un `except:` solo: un error que nunca verás.
- Un `if` cuyas ramas no recorre ningún ejemplo que te dio.

**Al pedírselo a la IA, dile:**

- «Uso Python 3.14 con uv.»
- «Dame un caso de prueba por cada rama, incluidos los casos borde.»

::: problem {#py-dentro-rama title="Tres ejemplos que pasan"}
La IA te jura que su función funciona: la corrió con tres ejemplos. ¿Qué te falta saber antes de creerle?
:::

::: hint {of="py-dentro-rama"}
¿Por qué ramas del `if` pasaron esos tres ejemplos?
:::

::: answer {of="py-dentro-rama"}
- Las ramas que ningún ejemplo recorrió no están probadas.
- Un error de tipo sólo sale cuando su línea corre: puede estar ahí, esperando.
- Arreglo: pide un caso de prueba por rama, con los casos borde (`0`, vacío, `None`).
:::

Sigue con [[nombres-y-objetos]]: por qué la segunda región de `revisa_esto.py` lista clientes de la primera.

> [!NOTE]
> **Si sólo recuerdas una cosa:** un error de tipo sale hasta que su línea corre: lo que no corrió, no está probado.
