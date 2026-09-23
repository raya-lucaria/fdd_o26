# Registro de entregas — fdd_o26
Una fila por (PR, tarea), identificada sólo por `login` de GitHub; nunca nombres reales. Branch huérfana: no se mergea a `main`.
Columnas: `login,tarea` (branch asignada o `id` del YAML oficial; `desconocida` si no encaja), `pr`, `intento` (orden de apertura por login y tarea), `abierto` (timestamp UTC), `due`, `dias_tarde` (días de calendario de Ciudad de México después de `due`; vacío sin due).
`resultado`: `bien` (mergeado) | `mal` (abierto con `corregir-y-reenviar`) | `cerrada` (sin merge) | `pendiente` (abierto sin revisar); `motivo` neutro; `senales` etiquetas técnicas separadas por `;`.
`override` sólo por decisión del profesor; `revisado` = fecha (Ciudad de México) del último comentario del mantenedor, o del merge si no hubo comentario.
