---
id: parcial-terminal-b
title: "Parcial 2 · Terminal y regex · Examen B"
nav_title: "Examen B"
summary: "El examen B de terminal y expresiones regulares, pregunta por pregunta, con la respuesta explicada debajo: la regex del importe de una factura, cinco comandos y diez rutas absolutas y relativas."
status: ready
estimated_time: 15m
tags: [examen, parcial, terminal, bash, regex, rutas]
---

# Parcial 2 · Terminal y regex · Examen B

**[PDF del examen B, sin respuestas](../../_assets/parcial-terminal-b.pdf)** · 15 minutos · 10 puntos · sin apuntes

Cada pregunta tiene su respuesta debajo, **plegada**. Contesta primero en una hoja y luego ábrela para calificarte. La regex se probó con `grep -E` contra los ejemplos y contra casos de borde, y cada `mv` se corrió en un árbol de carpetas igual al del enunciado.

## Pregunta 1 · El importe de una factura (2.5 puntos)

::: problem {#ptb-1 title="1 · Escribe la regex"}
Escribe una regex que valide cantidades entre **0,01 €** y **999.999,99 €**. Debe:

- exigir dos decimales, separados con coma;
- usar puntos para separar miles;
- exigir exactamente un espacio antes de `€`.

No admite ceros iniciales, signos, ni cantidades cuya parte entera tenga más de tres cifras sin punto.

Válidas: `0,50 €`, `12.345,67 €`. Inválidas: `0,00 €`, `012,50 €`, `1234,56 €`.
:::

::: answer {of="ptb-1"}
```text
^(0,(0[1-9]|[1-9][0-9])|[1-9][0-9]{0,2}(\.[0-9]{3})?,[0-9]{2}) €$
```

La idea es separar **dos casos**: lo que empieza con `0` y lo que empieza con otro dígito. Así se evitan a la vez los ceros iniciales y el `0,00`.

| Pieza | Qué exige |
|---|---|
| `^` … ` €$` | La cantidad completa, y al final exactamente un espacio y `€` |
| `0,(0[1-9]\|[1-9][0-9])` | **Caso 1, menos de un euro**: `0,` y unos centavos que no sean `00`. `0[1-9]` cubre de `01` a `09`, y `[1-9][0-9]` de `10` a `99` |
| `[1-9][0-9]{0,2}` | **Caso 2**: de 1 a 3 cifras que **no empiezan en 0**. Eso cubre de 1 a 999, y descarta `012` |
| `(\.[0-9]{3})?` | Opcionalmente, **un** grupo de miles: un punto y exactamente tres cifras. Una sola vez, así que el máximo es `999.999` |
| `,[0-9]{2}` | La coma y exactamente dos decimales |

**Por qué cada inválida falla:**

- `0,00 €`: empieza con `0`, así que sólo puede entrar por el caso 1, y ahí `00` no está permitido.
- `012,50 €`: empieza con `0` pero no sigue una coma; el caso 2 no acepta un `0` al inicio.
- `1234,56 €`: después de `[1-9][0-9]{0,2}` (máximo tres cifras) tiene que venir un punto o la coma, y viene un `4`.

**También rechaza:** `1.000.000,00 €` (dos grupos de miles), `-5,50 €` (signo), `5,5 €` (un decimal) y `5,50€` (sin espacio).

**Cómo probarla.** `grep -E` imprime sólo las válidas:

```bash
printf '0,50 €\n12.345,67 €\n0,00 €\n012,50 €\n1234,56 €\n' |
  grep -E '^(0,(0[1-9]|[1-9][0-9])|[1-9][0-9]{0,2}(\.[0-9]{3})?,[0-9]{2}) €$'
```

**También vale:**

- `\d` en lugar de `[0-9]`, en Python o JavaScript. En `grep -E`, `\d` **no** funciona: busca una `d` literal.
- Con una revisión que descarte el `0,00` (`grep -P`, Python): `^(?!0,00 )(0|[1-9][0-9]{0,2}(\.[0-9]{3})?),[0-9]{2} €$`. El curso no enseñó `(?!…)`, así que no se exigía.

**Errores típicos:**

- Olvidar escapar el punto. `.` sin `\` es **cualquier carácter**, y aceptaría `12x345,67 €`.
- Poner `[0-9]{1,3}` al inicio. Deja pasar `012`.
:::

**Repasa:** [[piezas-de-un-patron|Las piezas de un patrón]], [[cuantas-veces|Cuántas veces]] y [[grupos-y-captura|Grupos y captura]].

## Pregunta 2 · El comando de cada acción (2.5 puntos, 0.5 cada uno)

Por ejemplo, `mv` es el comando para mover.

::: problem {#ptb-2a title="a · Permisos de administrador"}
Comando para dar permisos de administrador.
:::

::: answer {of="ptb-2a"}
**`sudo`**, de *superuser do*. Va antes de otro comando y lo corre como administrador, después de pedirte tu contraseña. Ejemplo: `sudo apt update`.

Úsalo sólo cuando el comando lo necesita, porque toca el sistema. Si el prompt termina en `#` en lugar de `$`, ya eres administrador.
:::

::: problem {#ptb-2b title="b · Ver los últimos comandos"}
Comando para ver los últimos comandos ejecutados en la terminal.
:::

::: answer {of="ptb-2b"}
**`history`**. `history | tail` muestra los últimos, y `Ctrl-R` busca hacia atrás en el historial. También valía `fc -l`.
:::

::: problem {#ptb-2c title="c · Borrar un directorio completo"}
Comando para borrar un directorio completo.
:::

::: answer {of="ptb-2c"}
**`rm -r carpeta`**. La `-r` (recursivo) borra la carpeta con todo lo de adentro.

**Hay que distinguir dos respuestas:**

- **`rmdir carpeta`** sólo borra una carpeta **vacía**. Si tiene algo, se niega. Es la versión segura, y la que se practicó en clase.
- **`rm -r`** sí borra «completo». Agregarle `-f` (`rm -rf`) quita además las preguntas. No hay papelera: lo borrado no se recupera.

Como la pregunta dice «completo», la respuesta exacta es `rm -r`. `rmdir` se aceptaba si se aclaraba que sólo sirve vacía.
:::

::: problem {#ptb-2d title="d · Borrar un archivo"}
Comando para borrar un archivo.
:::

::: answer {of="ptb-2d"}
**`rm archivo`**. Con `rm -i` pide confirmación antes de borrar, que es como se practicó en clase.
:::

::: problem {#ptb-2e title="e · Sobrescribir un archivo con la salida"}
Comando para copiar y sobrescribir la salida estándar en un archivo.
:::

::: answer {of="ptb-2e"}
**`>`**. `comando > archivo` reemplaza el contenido del archivo con la salida, y lo crea si no existe. No confundir con `>>`, que **agrega** al final. Es un operador de redirección, no un comando; se aceptaba igual.
:::

**Repasa:** [[archivos-y-comandos|Archivos y comandos]] y [[flujos-procesos-y-herramientas|Historial, tuberías y herramientas]].

## Pregunta 3 · Rutas absolutas y relativas (5 puntos, 1 cada escenario)

Quieres mover `archivo.txt` a la carpeta `backups/`.

```text
/                              (directorio raíz)
├── home/
│   └── liurna/
│       └── raya_lucaria/
│           └── archivo.txt    ← ORIGEN
└── var/
    └── log/
        └── backups/           ← DESTINO
```

Una ruta **absoluta** empieza en `/` y no depende de dónde estés. Una **relativa** empieza desde el directorio actual; `..` sube un nivel.

| # | Directorio actual | Ruta de origen | Ruta de destino |
|---|---|---|---|
| 1 | `/` | Absoluta | Absoluta |
| 2 | `/home/liurna/raya_lucaria/` | Relativa | Absoluta |
| 3 | `/var/log/` | Absoluta | Relativa |
| 4 | `/home/liurna/` | Relativa | Absoluta |
| 5 | `/var/log/` | Relativa | Relativa |

::: problem {#ptb-3-1 title="Escenario 1 · Estás en /, absoluta → absoluta"}
Escribe el `mv`.
:::

::: answer {of="ptb-3-1"}
```bash
mv /home/liurna/raya_lucaria/archivo.txt /var/log/backups/
```

Las dos empiezan en `/`: funcionan desde cualquier lado.
:::

::: problem {#ptb-3-2 title="Escenario 2 · Estás en raya_lucaria/, relativa → absoluta"}
Escribe el `mv`.
:::

::: answer {of="ptb-3-2"}
```bash
mv archivo.txt /var/log/backups/
```

El archivo está **justo donde estás**, así que su ruta relativa es sólo su nombre. También vale `./archivo.txt`.
:::

::: problem {#ptb-3-3 title="Escenario 3 · Estás en /var/log/, absoluta → relativa"}
Escribe el `mv`.
:::

::: answer {of="ptb-3-3"}
```bash
mv /home/liurna/raya_lucaria/archivo.txt backups/
```

`backups/` está **debajo** de `/var/log/`: basta su nombre. También vale `./backups/`.
:::

::: problem {#ptb-3-4 title="Escenario 4 · Estás en /home/liurna/, relativa → absoluta"}
Escribe el `mv`.
:::

::: answer {of="ptb-3-4"}
```bash
mv raya_lucaria/archivo.txt /var/log/backups/
```

Desde `/home/liurna/` el archivo está una carpeta abajo, en `raya_lucaria/`.
:::

::: problem {#ptb-3-5 title="Escenario 5 · Estás en /var/log/, relativa → relativa"}
Escribe el `mv`.
:::

::: answer {of="ptb-3-5"}
```bash
mv ../../home/liurna/raya_lucaria/archivo.txt backups/
```

Para el origen subes dos niveles (`log` → `var` → `/`) y bajas por `home/liurna/raya_lucaria/`. El destino es el del escenario 3.

**Error típico:** `../home/…`. Con un solo `..` llegas a `/var`, y ahí no hay `home`.
:::

**Cómo comprobar cualquiera:** antes del `mv`, corre `ls` con la misma ruta. Si `ls ../../home/liurna/raya_lucaria/archivo.txt` lo encuentra, la ruta está bien.

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]] y [[archivos-y-comandos|Archivos y comandos]].
