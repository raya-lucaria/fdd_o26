# Roofline numérico para principiantes

## Objetivo

Reemplazar la analogía de cocina y el ejemplo de juguete de la sección Roofline por una explicación numérica, realista y trazable para lectores sin experiencia previa.

## Secuencia pedagógica

1. Presentar `C[i] = A[i] + B[i]` para 1,000 valores FP32.
2. Recordar que FP32 ocupa 4 bytes.
3. Contar por separado 4,000 bytes leídos de `A`, 4,000 de `B` y 4,000 escritos en `C`.
4. Contar 1,000 sumas como 1,000 FLOP.
5. Derivar `1,000 FLOP / 12,000 bytes = 0.083 FLOP/byte`.
6. Aplicar un hardware docente de 100 GB/s y 2 TFLOPS: la memoria puede alimentar 8.3 GFLOPS, muy por debajo de los 2,000 GFLOPS de cómputo.
7. Introducir `min` como la selección del menor de esos dos límites.
8. Contrastar con multiplicación matricial por bloques, donde reutilizar datos eleva las operaciones obtenidas por byte.
9. Presentar la fórmula general sólo después de completar las cuentas.

## Presentación visual

Actualizar `roofline-lite.svg` para mostrar los mismos valores del texto: suma vectorial en la zona limitada por memoria, punto de quiebre y multiplicación por bloques cerca del techo de cómputo. El texto alternativo y la lectura visual repetirán la conclusión esencial sin depender del color.

## Límites y lenguaje

- Eliminar cocina, ingredientes y la frase “ejemplo de juguete”.
- Distinguir datos movidos, operaciones realizadas y tasa posible.
- Mostrar la cancelación de unidades: `(byte/s) × (FLOP/byte) = FLOP/s`.
- Aclarar que el tráfico calculado es un mínimo simplificado y que cachés, asignación y escrituras pueden añadir bytes.
- No presentar el hardware docente como benchmark de un producto.

## Verificación

Las pruebas editoriales deben exigir las cuentas de 12,000 bytes, 1,000 FLOP, 0.083 FLOP/byte y 8.3 GFLOPS, además de rechazar la analogía de cocina en la sección. Después se ejecutarán la suite completa, Raya validate/build/inspect y una revisión de Chromium móvil y escritorio antes de publicar.
