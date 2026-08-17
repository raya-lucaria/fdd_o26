# Arquitectura visual y accesible — Diseño

## Propósito

Convertir la unidad de arquitectura en un guion docente visual de 90 minutos que una persona sin experiencia pueda enseñar y estudiar. Cada concepto seguirá intuición, ejemplo de juguete, visual, explicación, fórmula y caso real. Los detalles útiles permanecen, pero tablas, listas y diagramas reemplazan secuencias densas de prosa.

## Recorrido

El índice ofrece una ruta de 90 minutos y contenido opcional. Compute introduce instrucciones y luego anida programa, threads, cores y SIMD. Memoria sigue físicamente un dato y compara latencias por órdenes de magnitud. Paralelismo conecta movimiento y cálculo mediante Roofline y termina con potencia frente a energía. IA comienza con diez parámetros y escala hasta modelos actuales, separando inferencia, entrenamiento, memoria, comunicación, energía y costo.

## Sistema visual

Los SVG usan fondo oscuro, cian para movimiento, verde para rutas útiles, ámbar para costo/espera y violeta para cómputo. Tendrán `title`, `desc`, tipografía móvil legible, alt específico, pie y fallback textual. Se crearán visuales para threads/cores/SIMD, latencia/throughput, rutas CPU/GPU, jerarquía de memoria, Roofline anotado, escala energética, bytes por precisión, dense/MoE y prefill/decode. Las tablas deberán caber o desplazarse sin ampliar el documento.

## Evidencia cuantitativa

Toda cifra se etiqueta `FACT`, `DERIVED` o `ESTIMATE`. Los modelos cerrados muestran `no divulgado` y sólo rangos cuando existe un supuesto auditable. Los abiertos aportan parámetros y cálculos reproducibles. Una columna de confianza distingue fuente primaria, derivación y estimación. No se convierten precio API, calidad, FLOPS, potencia o parámetros en un ranking común.

## Límites

La única entrega continúa siendo ver tres videos; el notebook queda como recurso. No se modifica la práctica final. La página de IA puede crecer para contener material seleccionable, pero la ruta principal completa queda marcada para 90 minutos. El resultado debe validar en Raya, pasar pruebas y funcionar sin overflow ni recursos rotos en Chromium móvil y escritorio.
