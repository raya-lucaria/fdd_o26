# Dashboard Seaborn de modelos de IA

## Propósito

Sustituir las doce láminas SVG artesanales del dashboard por seis figuras producidas con Seaborn/Matplotlib. La ruta principal debe permitir comparar modelos sin comprimir decenas de observaciones, ejes, leyendas y etiquetas dentro de una tarjeta pequeña.

El ledger YAML y `tools/ai_model_dashboard.py` continúan siendo la fuente de verdad. Sólo cambia la capa de visualización y la forma de presentar las comparaciones.

## Decisiones de diseño

- Usar scatterplots por año. No unir modelos diferentes con líneas, porque una línea sugeriría una trayectoria continua inexistente.
- Usar escala logarítmica cuando la magnitud cubra varios órdenes y escribir ticks humanos: `1B`, `100B`, `10 kW`, `$1M`.
- Codificar evidencia con color y forma redundantes: `FACT`, `DERIVED`, `ESTIMATE` y `SCENARIO`.
- Etiquetar directamente sólo 4–6 casos seleccionados por figura: extremos, modelos actuales o ejemplos docentes. La tabla conserva todos los modelos.
- Mostrar rangos estimados con barras o bandas, nunca sólo con un punto medio.
- Usar una figura por fila en móvil y un ancho cómodo en escritorio. Ninguna figura se agrupa dentro de una galería de miniaturas.
- Exportar SVG por defecto mediante `savefig`. Se permite PNG de alta resolución cuando el render vectorial resulte menos legible; ambos formatos deben conservar alt text, crédito y una tabla equivalente.

## Las seis figuras

1. **Parámetros por año.** Total y activo en paneles o marcas claramente separadas. Explica dense frente a MoE.
2. **Trabajo de entrenamiento.** FLOP de entrenamiento con rangos estimados y ausencia explícita para modelos cerrados.
3. **Hardware de entrenamiento.** Dos paneles: aceleradores concurrentes y valor de reemplazo accelerator-only. No mezcla accelerator-hours en el mismo eje; esa cifra queda en tabla/anexo.
4. **Memoria de inferencia.** Dos paneles: bytes del artefacto o piso de pesos y número mínimo de H100 por capacidad. Distingue artefacto real de piso teórico.
5. **Potencia y CAPEX de inferencia.** Dos paneles construidos sobre el mismo escenario de capacidad: TDP accelerator-only y CAPEX accelerator-only. No representa pared, servidor, SLA ni precio API.
6. **Pareto de inferencia.** CAPEX mínimo del escenario frente a capacidad general ECI. Muestra intervalos, frontera segura/posible y nombres de todos los candidatos elegibles.

No se dibuja un Pareto de entrenamiento vacío. Una nota explica que no existe intersección exacta entre las cuatro flotas documentadas y las variantes ECI elegibles.

## Tablas y narración

Cada figura tiene inmediatamente después:

- una conclusión de una o dos frases;
- una tabla compacta con los modelos visibles o los extremos relevantes;
- un enlace al anexo opcional para el corpus completo.

La tabla maestra segmentada de 39 modelos permanece. El anexo conserva estados, confianza, fórmulas, rangos, fuentes y tablas reconstruibles; se actualiza para corresponder a seis figuras, no doce.

## Arquitectura

- Crear un generador Seaborn/Matplotlib que consuma exclusivamente las series puras de `tools/ai_model_dashboard.py`.
- Mantener separadas preparación de datos, selección de etiquetas, estilo y escritura del archivo.
- Fijar tema, dimensiones, DPI, tipografías, orden, semillas y metadatos para obtener salidas deterministas.
- Eliminar el generador SVG manual cuando las seis nuevas figuras y sus pruebas lo sustituyan completamente.
- Retirar los doce assets anteriores sólo después de confirmar que no tienen consumidores.

## Accesibilidad y móvil

- Tamaño tipográfico renderizado mínimo de 16 px en el ancho útil móvil.
- Paleta con contraste y codificación redundante por forma/trazo.
- Alt text que describa ejes, escala, tendencias, rangos y casos destacados.
- Tabla equivalente para lectores de pantalla y para auditoría numérica.
- Sin etiquetas superpuestas, recortes, texto carácter por carácter ni scroll horizontal a 390 px.

## Verificación

- TDD para el contrato de seis figuras, selección de series, ausencia de líneas entre modelos, rangos y estados.
- Regeneración determinista y comparación de hashes.
- Pruebas de que los seis embeds sustituyen por completo a los doce anteriores.
- Suite completa de `tools/`.
- Raya `validate`, `build` y `artifacts inspect`.
- Chromium a 390×844 y 1440×900 para ruta principal y anexo.
- Revisión adversarial matemática, visual, pedagógica/ADHD y de release.
- Publicación en `main`, monitoreo de Pages y verificación directa de las seis figuras en producción.

## Criterio de éxito

Un lector debe poder responder, sin ampliar la imagen: qué mide cada eje, qué modelos son extremos, qué cifras son publicadas o inferidas y qué conclusión permite —o no permite— cada comparación.
