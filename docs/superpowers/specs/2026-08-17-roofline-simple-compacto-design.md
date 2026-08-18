# Roofline simple y compacto

## Problema

La sección actual acumuló explicaciones y el SVG repite una tarjeta de cuentas ya presente en el texto. El gráfico alcanza 835 px en móvil y 1,600 px en escritorio. Aunque las cifras son correctas, la repetición, las siglas y la escala visual dificultan descubrir la idea principal.

## Decisión

Reescribir la sección completa en lugar de añadir otro bloque. Eliminar contenido redundante aunque sea técnicamente correcto. La explicación tendrá una sola progresión y el SVG será únicamente una gráfica compacta.

## Progresión

1. Empezar con `C[0] = A[0] + B[0]`.
2. Recordar que un número FP32 ocupa 4 bytes.
3. Contar 4 bytes de `A`, 4 de `B` y 4 de `C`: 12 bytes para una suma.
4. Escalar a 1,000 posiciones: 12,000 bytes y 1,000 sumas.
5. Expresar la intuición en palabras: se mueven muchos datos para hacer poco cálculo.
6. Presentar `1/12 ≈ 0.083 FLOP/byte` como abreviatura de esa oración.
7. Calcular el límite de memoria con hardware docente de 100 GB/s.
8. Comparar 8.3 GFLOPS de memoria con 2,000 GFLOPS de cómputo mediante una tabla de tres filas.
9. Definir `min` como “escoger el número menor”.
10. Mostrar la fórmula general al final como resumen opcional.

## Visual

Eliminar la tarjeta numérica del SVG. Crear una gráfica horizontal de aproximadamente 350–450 px de alto con sólo tres mensajes visibles:

- suma: `0.083 FLOP/byte`;
- techo alimentado por memoria: `8.3 GFLOPS`;
- conclusión: `limita memoria` porque `8.3 < 2,000`.

El quiebre de 20 FLOP/byte puede permanecer como referencia secundaria, explicado en una frase. El SVG tendrá dimensiones intrínsecas, texto legible en móvil, formas además de color, `title`, `desc`, alt y fallback equivalentes.

## Limpieza

- Eliminar la tarjeta duplicada, encabezados mecánicos “Operación/Bytes/FLOP” y párrafos repetidos.
- No usar cocina, “ejemplo de juguete” ni metáforas nuevas.
- No repetir definiciones de FLOP/FLOPS ya dadas en la sección anterior.
- Mantener la advertencia sobre tráfico mínimo y techo del modelo en una nota breve al final.
- Conservar las cifras y unidades verificadas; simplificar su presentación, no su exactitud.

## Verificación

Las pruebas exigirán el recorrido de un elemento, la escala a 1,000, la tabla comparativa, la definición verbal de `min`, ausencia de la tarjeta SVG y altura intrínseca máxima de 900 px para relación 2×. Chromium deberá medir un diagrama visible, sin overflow, de no más de 450 px de alto a 390 px de viewport.
