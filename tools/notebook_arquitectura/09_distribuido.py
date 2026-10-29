# %% [markdown]
# ## 9.1 · Relojes locales: restar marcas no mide la latencia
#
# **Qué se va a ver.** Dos componentes, A y B, tienen cada uno su propio reloj
# local. El reloj de B marca **40 ms menos** que el tiempo real (está atrasado).
# A envía un mensaje a B; el mensaje tarda **20 ms** en llegar (valor supuesto
# del ejemplo). Cada componente anota la hora de **su** reloj: A al enviar, B
# al recibir.
#
# Es una simulación con enteros en milisegundos, no una medición: no usa el
# reloj real de tu máquina. Lo que importa es la cuenta, y es exacta:
#
# - envío en A: tiempo real 100 ms, marca de A = 100
# - llegada a B: tiempo real 120 ms, marca de B = 120 − 40 = 80
# - resta de marcas: 80 − 100 = **−20 ms**
#
# La resta es negativa: «el mensaje llegó antes de enviarse». No es un error
# del programa; es que la resta mezcla dos relojes. Vale
# `latencia + desfase = 20 + (−40) = −20`. Sin conocer el desfase (y su
# incertidumbre) la resta no dice cuánto tardó el mensaje.

# %%
# celda 9.1
LATENCIA_MS = 20          # supuesto: lo que tarda el mensaje en tiempo real
DESFASE_B_MS = -40        # supuesto: el reloj de B marca 40 ms menos que el real


class Componente:
    """Un componente con reloj local = tiempo real + desfase."""

    def __init__(self, nombre, desfase_ms):
        self.nombre = nombre
        self.desfase_ms = desfase_ms

    def marca(self, real_ms):
        return real_ms + self.desfase_ms


a = Componente("A", 0)
b = Componente("B", DESFASE_B_MS)

envio_real = 100                       # A envía en el instante real 100 ms
llegada_real = envio_real + LATENCIA_MS

marca_a = a.marca(envio_real)          # lo que A anota
marca_b = b.marca(llegada_real)        # lo que B anota

print(f"A anota al enviar : {marca_a} ms  (reloj de A)")
print(f"B anota al recibir: {marca_b} ms  (reloj de B)")
print(f"resta de marcas   : {marca_b} - {marca_a} = {marca_b - marca_a} ms")
print(f"latencia real     : {llegada_real - envio_real} ms (la conocemos sólo porque simulamos)")
print(f"latencia + desfase: {LATENCIA_MS} + ({DESFASE_B_MS}) = {LATENCIA_MS + DESFASE_B_MS} ms")
assert (marca_a, marca_b, marca_b - marca_a) == (100, 80, -20)

# %% [markdown]
# ### Salida esperada de la celda 9.1
#
# Los valores son exactos porque es una simulación con enteros:
#
# - A anota 100 ms y B anota 80 ms.
# - La resta de marcas da **−20 ms** (negativa).
# - La latencia real es 20 ms y `latencia + desfase` también da −20 ms.
#
# **Lectura.** La diferencia entre marcas de dos máquinas no es la latencia. El
# orden de eventos entre máquinas se reconstruye con **mensajes** («A envía,
# luego B recibe»), no comparando relojes. Si al ejecutar la celda no ves el
# −20, revisa que no hayas cambiado `DESFASE_B_MS` o `LATENCIA_MS`.
