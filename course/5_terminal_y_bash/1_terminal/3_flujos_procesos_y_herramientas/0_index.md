---
id: flujos-procesos-y-herramientas
title: "Flujos, procesos y herramientas"
nav_title: "Flujos y procesos"
summary: "Conecta programas, separa errores y reconoce procesos con herramientas por plataforma."
status: ready
estimated_time: 15m
tags: [terminal, pipes, procesos, stdin, stdout, stderr]
prerequisites: [archivos-y-comandos]
---

# Flujos, procesos y herramientas

Un proceso es un programa que está ejecutándose. La shell conecta tres flujos: **stdin** (entrada), **stdout** (salida normal) y **stderr** (mensajes de error). Separarlos permite conservar resultados y diagnosticar fallas.

::: definition {#tres-flujos title="Tres caminos de texto"}
Por defecto, un programa lee desde stdin y escribe tanto stdout como stderr en la terminal. `>` redirige stdout y reemplaza un archivo; `>>` agrega stdout al final; `2>` redirige stderr; `2>&1` envía stderr al mismo destino que stdout en ese punto de la línea.
:::

## Redirecciones reproducibles

::: example {#salida-y-error-separados title="Guarda resultado y diagnóstico"}
El bloque prepara sus archivos antes de usarlos y luego separa un error esperado.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' 'Beto' 'Ana' > nombres.txt
printf '%s\n' 'faltó una columna' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
ls nombres.txt > reportes/salida.txt 2> reportes/errores-ls.txt
ls inexistente > reportes/salida-vacia.txt 2> reportes/errores-ls.txt
cat reportes/errores-ls.txt
```

El segundo `ls` no encuentra ese nombre: stdout queda en `salida-vacia.txt` y su diagnóstico queda en `errores-ls.txt`.
:::

Para registrar salida y error juntos, redirige en este orden: `comando > reporte.txt 2>&1`. `2>&1` copia el destino actual de stdout; si lo inviertes, no se comporta igual.

## Tuberías y decisiones

El símbolo `|` entrega stdout de un programa como stdin del siguiente. `tee` muestra la salida y a la vez la guarda. `&&` ejecuta la segunda orden solo si la primera tuvo éxito; `||` la ejecuta solo si la primera falló. Después de un comando, `$?` contiene su estado: `0` suele significar éxito.

::: example {#cuenta-y-registra-nombres title="Transforma una entrada preparada"}
El ejemplo crea la entrada antes de ordenarla y contar repeticiones.

```bash
mkdir -p "$HOME/fdd/terminal-lab/reportes"
cd "$HOME/fdd/terminal-lab"
printf '%s\n' 'Ana' 'Beto' 'Ana' > nombres.txt
printf '%s\n' 'faltó una columna' > errores.txt
printf '%s\n' 'contenido con espacio' > 'dos palabras.txt'
set -o pipefail
sort nombres.txt | uniq -c | tee reportes/conteos.txt
estado=$?
set +o pipefail
printf 'Estado de la tubería: %s\n' "$estado"
if test "$estado" -eq 0; then
    printf '%s\n' 'reporte creado'
else
    printf '%s\n' 'revisa el reporte'
fi
```

`sort` junta iguales antes de que `uniq -c` pueda contarlos. `tee` conserva una copia legible en `reportes/conteos.txt`. `set -o pipefail` hace que la tubería falle si falla cualquiera de sus programas; luego el ejemplo guarda `$?` en `estado` antes de apagar esa opción y ramificar. Puedes usar `&&` y `||` para encadenar acciones por éxito o fallo, pero guarda el estado primero si quieres examinar el resultado del comando anterior.
:::

::: example {#predice-antes-de-ejecutar title="Predice los flujos"}
Sin ejecutarlos, anota qué verá la terminal y qué quedará en cada archivo para estas líneas. Después pruébalas en tu laboratorio.

```bash
ls inexistente > salida 2> errores
ls inexistente | wc -l
printf '%s\n' Ana Beto Ana | sort | uniq -c
```

Recuerda: una tubería mueve stdout, no stderr.
:::

::: problem {#redireccion-error-prediccion title="¿Dónde quedó el error?"}
Tras ejecutar `ls inexistente > salida 2> errores`, ¿qué esperas encontrar en `salida`, en `errores` y en la terminal?
:::

::: hint {of="redireccion-error-prediccion"}
`>` trata la salida normal; el `2` nombra el flujo de diagnóstico.
:::

::: answer {of="redireccion-error-prediccion"}
`salida` queda vacío porque `ls` no pudo listar el nombre. `errores` contiene el diagnóstico de que no existe. La terminal no muestra ese mensaje porque stderr fue redirigido.
:::

::: problem {#tuberia-no-cuenta-errores title="Una tubería no absorbe stderr"}
¿Por qué `ls inexistente | wc -l` normalmente imprime `0` como conteo, aunque el mensaje de error sigue siendo visible en la terminal?
:::

::: hint {of="tuberia-no-cuenta-errores"}
Identifica qué flujo entra a `wc -l` y cuál permanece conectado a la terminal.
:::

::: answer {of="tuberia-no-cuenta-errores"}
La tubería pasa stdout de `ls` a stdin de `wc`. Como no hubo nombres listados, `wc -l` cuenta cero líneas. El diagnóstico viaja por stderr, que no entra en la tubería y por eso se ve en la terminal.
:::

::: problem {#ordenar-antes-de-contar title="Agrupa antes de contar"}
¿Qué efecto tiene `sort | uniq -c` sobre una entrada con tres líneas `Ana`, `Beto`, `Ana`, y por qué importa el orden?
:::

::: hint {of="ordenar-antes-de-contar"}
`uniq` cuenta grupos consecutivos, no todas las apariciones dispersas.
:::

::: answer {of="ordenar-antes-de-contar"}
`sort` ordena las líneas para que las dos apariciones de `Ana` queden juntas; luego `uniq -c` imprime un conteo de 2 para `Ana` y 1 para `Beto`. Sin ordenar, nombres iguales separados no formarían un mismo grupo.
:::

## Procesos y herramientas disponibles

`ps` muestra una instantánea de procesos; `ps aux` suele dar una lista más amplia. `htop` es un visor interactivo: si está instalado, sales con `q`. `fastfetch` resume el sistema si está disponible. Antes de instalar o ejecutar una herramienta opcional, pregunta si existe:

```bash
command -v htop
command -v fastfetch
ps
```

`Ctrl-C` envía una interrupción al proceso que ocupa la terminal, por ejemplo un comando que sigue esperando entrada. Normalmente vuelve al prompt; no deshace una operación que ya terminó ni elimina archivos.

::: problem {#ctrl-c-interrumpe-primer-plano title="Interrumpe, no deshace"}
Ejecutas un programa que sigue esperando y pulsas `Ctrl-C`. ¿Qué efecto esperas y qué no puedes concluir sobre cambios que el programa hubiera hecho antes?
:::

::: hint {of="ctrl-c-interrumpe-primer-plano"}
Distingue entre detener el proceso actual y revertir acciones pasadas.
:::

::: answer {of="ctrl-c-interrumpe-primer-plano"}
La shell solicita interrumpir el proceso en primer plano y normalmente recupera el prompt. No es un botón de deshacer: cualquier salida o cambio completado antes de la interrupción puede permanecer.
:::

## Tarjetas por plataforma

| Plataforma | Herramientas y regla de cuidado |
|---|---|
| Ubuntu | `apt` consulta e instala paquetes. `sudo` ejecuta **una** orden con privilegios elevados y puede pedir tu contraseña; úsalo solo cuando entiendas la orden y el origen del paquete. Por ejemplo, revisa primero `apt search htop`; si tu docente o documentación oficial te indicó instalarlo, `sudo apt install htop`. |
| WSL2 con Ubuntu | Dentro de la distribución usa las mismas órdenes de Ubuntu; lo instalado afecta esa distribución Linux, no todas las aplicaciones de Windows. |
| macOS | `brew` administra paquetes si ya está instalado. Compruébalo con `command -v brew`; busca con `brew search htop` y revisa el resultado antes de decidir instalar. |

`apt`, `brew`, `htop` y `fastfetch` son herramientas opcionales: entender los flujos anteriores no depende de tenerlas instaladas.

Para cerrar la práctica aplicada, abre [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) y consulta la entrega oficial **“Bandit: investiga la terminal en los niveles 0–5”** en el curso. Usarás el mismo hábito de leer el prompt, pedir ayuda y distinguir salida de errores.
