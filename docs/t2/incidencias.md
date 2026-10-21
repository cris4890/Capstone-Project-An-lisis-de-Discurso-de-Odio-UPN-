# Incidencias, correcciones y límites de T2

| ID | Hallazgo | Corrección y comprobación | Estado |
|---|---|---|---|
| T2-01 | La preparación sintética generaba UUID aleatorios y podía cambiar grupos/particiones entre ejecuciones. | UUID5 determinista solo para sintéticos. Reproducción sobre base en `evidencias/reproduccion_ids_base.json`; regresión de IDs y particiones. Para datos reales se conservan IDs aleatorios. | Corregido |
| T2-02 | La carga directa de CSV para entrenar no revisaba todos los metadatos ni duplicados normalizados. | Validación estricta compartida, sin eliminación silenciosa de filas del corpus anotado; pruebas de campos, origen, etiquetas y duplicados. | Corregido |
| T2-03 | La preparación podía descartar copias de un texto sin advertir etiquetas contradictorias. | Rechazo de contradicciones antes de deduplicar; comparación normalizada. | Corregido |
| T2-04 | El flujo anterior no distinguía una propuesta sintética de un corpus con anotaciones completas. | `--synthetic-mode exploratory/reviewed`; revisión pendiente visible; modo revisado exige base del hash exacto. | Corregido técnicamente; revisión real pendiente |
| T2-05 | No existía una barrera automática contra incorporar los 30 KPI en el corpus de desarrollo. | Rechazo de coincidencias normalizadas antes de dividir y entrenar; test de rechazo sin crear ejecución. | Corregido para coincidencias exactas normalizadas; paráfrasis no cubiertas |
| T2-06 | `process_and_save` sobrescribía salidas; el CLI de corpus no protegía un informe de calidad existente. | Comprobación previa de destinos y rutas distintas; regresión de preservación del sidecar. | Corregido |
| T2-07 | Clasificador limitado: piloto histórico 18/30; reglas exploratorias no detectan Odio en test. | Métricas nuevas separadas y advertencias preservadas. No se cambian reglas para memorizar el KPI. | Abierto, calidad predictiva |
| T2-08 | Paquete recibido después de la primera publicación. Sus comandos no incluían el modo de entrenamiento; fechas sin validar y escritura antes de comprobar manifiesto. | Script y plantilla integrados; prevalidación de destinos, fechas, particiones y KPI; instrucciones actualizadas sin eludir HU-03. | Corregido; pruebas en `test_paquete_t2.py` |
| T2-09 | XLM-RoBERTa no está disponible en la caché local inspeccionada. | Prueba de ajuste/guardado/carga diminuta ejecutada en suite; entrenamiento exploratorio limitado a reglas y clásicos. No se descargó ni entrenó el checkpoint completo en esta entrega. | Comparación multilingüe pendiente |

## Seguridad y riesgos

Se mantienen uso local, CORS/XSRF, minimización, SQL parametrizado, guardado voluntario,
backup/restauración y exclusión de archivos privados. Las pruebas no acreditan cifrado
en producción, autenticación, roles ni backup externo. No se publican modelos pickle
de terceros ni bases con datos privados. Cargar solo artefactos locales de confianza.

La autorización de uso sintético elimina el bloqueo por acceso a Reddit para T2;
no elimina los riesgos de etiquetas inconsistentes, muestra pequeña, sesgo del generador
y sobreajuste. No se atribuye representatividad a comunidades simuladas. La revisión
humana y el alcance del futuro paper se documentan por separado.

No se modificaron las métricas históricas del piloto. Una comparación favorable
en validación no garantiza mejor exactitud en test. Las funcionalidades y su calidad
predictiva se evalúan por separado, sin ocultar ninguno de los dos resultados.
