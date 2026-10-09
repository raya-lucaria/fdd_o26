# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Una venta no aparece en el total, sin aviso
Línea: 43
Por qué pasa: El monto de Carla Ríos viene en ventas.csv como "1,200.00". La coma de miles hace que float(fila["monto"]) lance un ValueError, pero esa línea está dentro de un try y el except Exception: pass atrapa el error y no hace nada con él: ni lo imprime ni lo guarda. La fila se pierde, el script sigue, y Carla no aparece en norte ni en los puntajes. Es la idea de la página 1: el error ocurre hasta que esa línea corre, y un except que no hace nada lo esconde.
Qué le pedirías a la IA: Que conserve el try/except, pero que nunca use pass: cada fila que no se pueda leer debe reportarse con su número de línea, el valor que falló y el motivo. Que atrape ValueError y no Exception en general, y que el monto puede traer caracteres especiales(coma) o letras, caracteres que no los acepta float.

## Error 2

Síntoma: La segunda región lista clientes de la primera
Línea: 25
Por qué pasa: La función clientes tiene vistos=[] como valor por defecto. Esa lista se crea una sola vez, cuando corre el def, y no en cada llamada. Como main() llama clientes(de_region) sin pasar vistos, las tres regiones usan la misma lista: centro deja ahí a sus clientes, y norte y sur los reciben y agregan los suyos encima. Es la idea de la página 2: una lista es mutable, y varios usos apuntan al mismo objeto.
Qué le pedirías a la IA: Que no use valores por defecto mutables como vistos=[]; que el valor por defecto sea None y que la lista se cree dentro de la función (if vistos is None: vistos = []), para que cada llamada tenga su propia lista. Y que ninguna función modifique lo que recibe.

## Error 3

Síntoma: «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido
Línea: 59
Por qué pasa: La función puntaje calcula en Python puro, y con el GIL sólo un hilo ejecuta código Python a la vez. Los hilos del ThreadPoolExecutor no calculan al mismo tiempo: se turnan, así que tardan lo mismo que el for de uno por uno, o un poco más. En mi máquina salió 1.27 s con hilos y 1.07 s sin hilos. Es la idea de la página 3: los hilos sirven cuando el programa espera, no cuando calcula.
Qué le pedirías a la IA: Decirle  qué tipo de trabajo es: puntaje calcula (CPU), en Python 3.14 con GIL, así que debe usar ProcessPoolExecutor con la guarda if __name__ == "__main__":. Que use hilos sólo para tareas que esperan (red, disco o una API), y que mida el tiempo en lugar de prometerlo en un comentario.

## Error 4

Síntoma: Un descuento de 0 se cobró como 5%
Línea: 39
Por qué pasa: Beto Peña en norte tiene descuento 0 en ventas.csv. La línea if not descuento: trata el 0.0 como falso, igual que a None o a un texto vacío, así que entra al if y le asigna el descuento por defecto de 0.05. Por eso norte da 325.12 en vez de 336.73. Es la idea de la página 4: if not x no distingue un 0 válido de un dato faltante.
Qué le pedirías a la IA: Que un 0 es un valor válido (sin descuento) y que use is None para detectar el dato faltante, no if not x.

## Error 5

Síntoma: La contabilidad está en centavos; comparar el total sin redondear con == falla
Línea: 76
Por qué pasa: La línea if total == TOTAL_CONTABILIDAD: compara el total con todos sus decimales contra 2722.27, y == exige igualdad exacta. Los montos se leen como float desde el principio y se multiplican por el descuento y el IVA, así que el total acumula decimales de más: aunque se corrigieran los errores 1 y 4, daría algo como 2722.270020 y seguiría diciendo que NO cuadra. El print de arriba sí lo redondea con .2f, por eso en pantalla se vería igual. Es la idea de la página 4: el dinero no va en float y 0.1 + 0.2 == 0.3 da False.
Qué le pedirías a la IA: Que maneje los montos con Decimal, nunca float, y que compare el total redondeado a centavos contra Decimal("2722.27").
