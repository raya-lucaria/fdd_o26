---
id: parcial-terminal-a
title: "Parcial 2 · Terminal y regex · Examen A"
nav_title: "Examen A"
summary: "El examen A de terminal y expresiones regulares, pregunta por pregunta, con la respuesta explicada debajo: la regex de una contraseña, cinco comandos y diez rutas absolutas y relativas."
status: ready
estimated_time: 15m
tags: [examen, parcial, terminal, bash, regex, rutas]
---

# Parcial 2 · Terminal y regex · Examen A

**[PDF del examen A, sin respuestas](../../_assets/parcial-terminal-a.pdf)** · 15 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. La regex se probó contra los ejemplos y contra casos de borde, y cada `mv` se corrió en un árbol de carpetas igual al del enunciado.

## Pregunta 1 · La contraseña de una cerradura (2.5 puntos)

::: problem {#pta-1 title="1 · Escribe la regex"}
Escribe una regex que valide claves de **8 a 12 caracteres**, formadas **únicamente por letras mayúsculas y dígitos**. Deben:

- comenzar con una letra;
- terminar con dos dígitos;
- contener al menos tres letras y tres dígitos en total;
- no repetir un mismo carácter en posiciones consecutivas.

Válida: `AB3C4D56`. Inválidas: `ABBC3456`, `ABCDEF12`.
:::

::: answer {of="pta-1"}
Hay dos respuestas correctas. Las dos se probaron con los ejemplos y con casos de borde.

**Con lo que vimos en el curso (`grep -E`).** Una regex sola de `grep -E` no puede contar «al menos tres letras» **y además** «al menos tres dígitos» en cualquier orden. Pero cuatro filtros encadenados sí, y cada uno revisa una regla:

```bash
grep -E '^[A-Z][A-Z0-9]{5,9}[0-9]{2}$' claves.txt |
  grep -E '([A-Z].*){3}' |
  grep -E '([0-9].*){3}' |
  grep -Ev '(.)\1'
```

| Filtro | Qué exige |
|---|---|
| `^[A-Z][A-Z0-9]{5,9}[0-9]{2}$` | La **forma**: empieza con letra, termina con dos dígitos, sólo mayúsculas y dígitos, y de 8 a 12 caracteres, porque 1 + 5 + 2 = 8 y 1 + 9 + 2 = 12 |
| `([A-Z].*){3}` | Una mayúscula, lo que sea, y eso tres veces: **al menos tres letras** |
| `([0-9].*){3}` | **Al menos tres dígitos** |
| `-Ev '(.)\1'` | `(.)` captura un carácter y `\1` exige el mismo otra vez: eso es **una repetición consecutiva**. La `-v` **quita** esas líneas |

**En una sola regex** (`grep -P`, Python o JavaScript, no `grep -E`):

```text
^(?=(.*[A-Z]){3})(?=(.*[0-9]){3})(?!.*(.)\3)[A-Z][A-Z0-9]{5,9}[0-9]{2}$
```

`(?=…)` y `(?!…)` son **revisiones** que miran la clave sin consumirla: «más adelante hay…» y «más adelante **no** hay…». Hacen lo mismo que los tres últimos filtros. El curso no las enseñó, así que no se exigían.

**Contra los ejemplos:**

- `AB3C4D56` pasa.
- `ABBC3456` cae en el último filtro, por la `BB`.
- `ABCDEF12` cae en el de tres dígitos: sólo tiene dos.

**Cuidado:**

- `\d` **no funciona en `grep -E`**: busca una `d` literal, y no avisa. Usa `[0-9]`.
- `.` en lugar de `[A-Z0-9]` acepta minúsculas y símbolos.

**Crédito parcial.** La forma sola, `^[A-Z][A-Z0-9]{5,9}[0-9]{2}$`, ya resuelve longitud, inicio, final y alfabeto, que es la mayor parte del ejercicio.
:::

**Repasa:** [[cuantas-veces|Cuántas veces]], [[taquigrafia-perl|La taquigrafía de Perl]] y [[grupos-y-captura|Grupos y captura]].

## Pregunta 2 · El comando de cada acción (2.5 puntos, 0.5 cada uno)

Por ejemplo, `mv` es el comando para mover.

::: problem {#pta-2a title="a · Copiar"}
Comando para copiar.
:::

::: answer {of="pta-2a"}
**`cp`**, de *copy*. `cp origen destino` copia un archivo. Para una carpeta completa hace falta `cp -r`.
:::

::: problem {#pta-2b title="b · Ver los últimos comandos"}
Comando para ver los últimos comandos ejecutados en la terminal.
:::

::: answer {of="pta-2b"}
**`history`**. Lista los comandos que la shell guardó, numerados. `history | tail` muestra sólo los últimos, y `!n` vuelve a correr el número `n`. También valía `fc -l`.
:::

::: problem {#pta-2c title="c · El directorio actual"}
Comando para conocer la dirección o directorio actual donde te encuentras.
:::

::: answer {of="pta-2c"}
**`pwd`**, de *print working directory*. Imprime la ruta absoluta de donde estás. También valía `echo $PWD`.
:::

::: problem {#pta-2d title="d · Crear un archivo vacío"}
Comando para crear un archivo vacío.
:::

::: answer {of="pta-2d"}
**`touch`**. Si el archivo no existe, lo crea vacío. Si ya existe, sólo le actualiza la fecha y no borra nada.

**También valía** `> archivo` o `: > archivo`. Ojo: esos dos sí **vacían** un archivo que ya existía. Es la diferencia que importa entre ellos y `touch`.
:::

::: problem {#pta-2e title="e · Agregar la salida a un archivo"}
Comando para agregar (*append*) la salida estándar a un archivo.
:::

::: answer {of="pta-2e"}
**`>>`**. `comando >> archivo` agrega la salida **al final** del archivo, y lo crea si no existe. No confundir con `>`, que **sobrescribe**. Técnicamente es un operador de redirección, no un comando; se aceptaba igual.
:::

**Repasa:** [[archivos-y-comandos|Archivos y comandos]] y [[flujos-procesos-y-herramientas|Historial, tuberías y herramientas]].

## Pregunta 3 · Rutas absolutas y relativas (5 puntos, 1 cada escenario)

Quieres mover `runas.dat` a la carpeta `leyendell/`.

```text
/                              (directorio raíz)
├── home/
│   └── altus_plateau/
│       └── leyendell/         ← DESTINO
└── var/
    └── log/
        └── cofres/
            └── runas.dat      ← ORIGEN
```

Una ruta **absoluta** empieza en `/` y no depende de dónde estés. Una **relativa** empieza desde el directorio actual; `..` sube un nivel.

| # | Directorio actual | Ruta de origen | Ruta de destino |
|---|---|---|---|
| 1 | `/` | Absoluta | Absoluta |
| 2 | `/home/altus_plateau/leyendell/` | Relativa | Absoluta |
| 3 | `/var/log/` | Absoluta | Relativa |
| 4 | `/home/altus_plateau/` | Relativa | Absoluta |
| 5 | `/var/log/` | Relativa | Relativa |

::: problem {#pta-3-1 title="Escenario 1 · Estás en /, absoluta → absoluta"}
Escribe el `mv`.
:::

::: answer {of="pta-3-1"}
```bash
mv /var/log/cofres/runas.dat /home/altus_plateau/leyendell/
```

Las dos rutas empiezan en `/`, así que da igual dónde estés.
:::

::: problem {#pta-3-2 title="Escenario 2 · Estás en leyendell/, relativa → absoluta"}
Escribe el `mv`.
:::

::: answer {of="pta-3-2"}
```bash
mv ../../../var/log/cofres/runas.dat /home/altus_plateau/leyendell/
```

Desde `leyendell/` hay que subir **tres** niveles para llegar a `/`: `leyendell` → `altus_plateau` → `home` → `/`. Luego se baja por `var/log/cofres/`.

**Error típico:** contar dos `..`. Cuenta las carpetas entre donde estás y la raíz. El destino, aunque es donde ya estás, se pide absoluto; `.` sería la versión relativa.
:::

::: problem {#pta-3-3 title="Escenario 3 · Estás en /var/log/, absoluta → relativa"}
Escribe el `mv`.
:::

::: answer {of="pta-3-3"}
```bash
mv /var/log/cofres/runas.dat ../../home/altus_plateau/leyendell/
```

Para el destino, desde `/var/log/` subes dos niveles (`log` → `var` → `/`) y bajas por `home/altus_plateau/leyendell/`.
:::

::: problem {#pta-3-4 title="Escenario 4 · Estás en /home/altus_plateau/, relativa → absoluta"}
Escribe el `mv`.
:::

::: answer {of="pta-3-4"}
```bash
mv ../../var/log/cofres/runas.dat /home/altus_plateau/leyendell/
```

Desde `/home/altus_plateau/` subes dos niveles hasta `/` y bajas por `var/log/cofres/`.

**También vale** el destino `leyendell/` o `./leyendell/`, pero son relativos, y aquí se pedía absoluto.
:::

::: problem {#pta-3-5 title="Escenario 5 · Estás en /var/log/, relativa → relativa"}
Escribe el `mv`.
:::

::: answer {of="pta-3-5"}
```bash
mv cofres/runas.dat ../../home/altus_plateau/leyendell/
```

El origen está **debajo** de donde estás: basta `cofres/runas.dat` (o `./cofres/runas.dat`). El destino es el mismo del escenario 3.

**Error típico:** escribir `/cofres/runas.dat`. La `/` inicial la vuelve absoluta, y `/cofres` no existe.
:::

**Cómo comprobar cualquiera:** antes del `mv`, corre `ls` con la misma ruta. Si `ls ../../var/log/cofres/runas.dat` lo encuentra, la ruta está bien.

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]] y [[archivos-y-comandos|Archivos y comandos]].
