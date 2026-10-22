# Mostrar los KPI en la sustentación

Abrir **Reportes → KPI del piloto**. La vista está disponible incluso en Demostración de reglas y muestra la evidencia histórica de 30 comentarios de Sprint 2, independientemente de la ejecución de entrenamiento seleccionada.

Incluye exactitud manual (28/30; 93,33 %), exactitud HateDetect (18/30; 60 %), errores, tiempos, capacidad por ventanas medidas, cobertura y detalle de casos. Se ofrecen las fuentes originales en CSV y JSON, no PDF. No se modifican los archivos de evidencia al abrir esta pantalla.

El tiempo medio manual es 6,795 segundos y el E2E de HateDetect 0,280 segundos. Sus límites de medición difieren: el E2E excluye ingreso, revisión humana y guardado. No presentar esta diferencia como ahorro laboral demostrado. La referencia del piloto es provisional y no constituye un estándar independiente.

La vista no analiza el Historial ni recalcula KPI al guardar nuevos comentarios. La evaluación de modelos entrenados continúa en su pestaña propia.

Fuentes: `docs/sprint2/evidencias/kpi.json`, `anexo_kpi.csv` y `docs/sprint2/protocolo_kpi.md`. Las pruebas verifican correspondencia de aciertos, rechazo de evidencia inconsistente, acceso sin entrenamiento y aviso ante ausencia de archivos.
