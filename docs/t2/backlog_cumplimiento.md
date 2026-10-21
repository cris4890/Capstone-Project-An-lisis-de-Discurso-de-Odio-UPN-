# HU-01 a HU-06: cumplimiento funcional de T2

Se conservan los identificadores originales de S3 y el backlog de Sprint 1.
Los controles F de esta matriz desglosan criterios, **no crean historias nuevas**.
El alcance sintético del curso fue comunicado por el solicitante el 21/10/2026.
No se impone recolección de Reddit real a T2. No consta aceptación formal de esta entrega.

## Historias y criterios actuales

| Historia | Criterios de aceptación para T2 | Estado y evidencia | Pendiente |
|---|---|---|---|
| HU-01 Datos permitidos y procedencia | Exportar los 72 existentes, distinguir origen sintético y propuestas, validar estructura y conservar revisión pendiente. | Parcial: `synthetic_corpus.py`, `corpus_72/procedencia.json`, nuevas pruebas. | ZIP integrado; pendiente revisión humana y confirmación de autoría cuando corresponda. No falta un recolector de Reddit para T2. |
| HU-02 Minimización e identificación | Enmascarar identificadores, excluir originales, detectar duplicados y mantener IDs reproducibles del corpus sintético. | Implementación local comprobada; pruebas de limpieza, duplicados, IDs y persistencia. | Revisión humana del contenido antes de declararlo corpus revisado. No equivale a anonimato universal. |
| HU-03 Manual, anotación y adjudicación | Dos anotaciones por unidad, motivo obligatorio, objetivo en Odio, tercero para desacuerdos, exportación bloqueada si incompleta. | Funciones implementadas y probadas con fixtures. Historia parcial como entrega del corpus T2. | Ejecutar la revisión real de los 72; no reutilizar adjudicaciones de otro corpus ni completar registros artificialmente. |
| HU-04 Comparación de modelos | Train/validation/test sin hilos ni duplicados compartidos; seleccionar en validación; entrenar, persistir y cargar reglas, clásicos y Transformer. | Parcial: ejecución real con reglas, logística y SVM; prueba local diminuta del Transformer. | Ejecutar comparación con XLM-RoBERTa sobre el corpus T2. No se eliminó ese criterio sin autorización. |
| HU-05 Clasificación | Entrada válida devuelve una de tres clases y modelo; probabilidad solo si existe, errores explícitos; guardado voluntario e historial. | Implementación funcional comprobada mediante AppTest y carga de modelos entrenados. | Aceptación formal del equipo/docente. La calidad predictiva sigue limitada; no usar para sanción automática. |
| HU-06 Reportes | Métricas por clase, errores, matrices, subgrupos y filtros sobre ejecuciones disponibles, con origen y límites visibles. | Implementación funcional comprobada para los tres modelos ejecutados. | Aceptación formal y resultados del Transformer cuando se ejecute HU-04. No se requiere estimar prevalencia real para T2. |

En términos de implementación local, HU-02, HU-05 y las funciones de HU-06 están
comprobadas; HU-01, HU-03 y HU-04 conservan pendientes de entrega o ejecución.
Ninguna historia se declara formalmente aceptada por el profesor a partir de pytest.

## Matriz funcional

| Control | Historia / fuente | Resultado verificable | Prueba / evidencia | Estado técnico |
|---|---|---|---|---|
| F01 Exportar corpus para revisión | HU-01 | 72 filas; propuestas separadas, revisores vacíos, hashes y revisión pendiente | `test_export_is_blinded_pending_and_never_overwritten`, `corpus_72/` | Comprobado |
| F02 Validar entradas | HU-01/HU-02 | Campos, clases, idioma declarado, origen, comunidad, tipo, duplicados e IDs inválidos rechazados | `test_invalid_prepared_fields_are_rejected`, `test_missing_columns_are_rejected`, `test_mixed_origins_and_duplicate_ids_rejected` | Comprobado |
| F03 Minimizar y conservar versiones | HU-02 | Textos minimizados, sin sobrescribir corpus ni archivos de calidad | `test_prepare_excludes_raw_and_deduplicates`, `test_preprocessing_cannot_overwrite_sidecar` | Comprobado |
| F04 Anotar y adjudicar | HU-03 | Roles A/B/E3 inmutables por corpus; progreso independiente; sólo desacuerdos visibles para E3; consensos inalterables; exportación bloqueada si está incompleta | `test_annotation_phase3.py`, `test_anotations_and_adjudication`, `test_consensus_cannot_be_adjudicated_or_overwritten` | Comprobado con fixtures; revisión humana pendiente |
| F05 Entrenar con revisión registrada | HU-03/HU-04 | Exige base existente y revisión completa del hash exacto; modo exploratorio separado | `test_training_requires_explicit_synthetic_mode_and_existing_annotations`, `test_reviewed_training_requires_complete_annotation_record` | Barreras comprobadas; corpus humano pendiente |
| F06 Aislar particiones y KPI | HU-04 | 50/11/11; hilos indivisibles, textos normalizados únicos, 0 coincidencias exactas normalizadas con los 30 KPI | `test_synthetic_ids_and_partitions_repeat_across_preparations`, `test_training_cannot_accept_kpi_case`, `exploratorio_72/partitions.csv` | Comprobado; paráfrasis requieren revisión |
| F07 Entrenar clásicos y seleccionar | HU-04 | Reglas, logística y SVM ejecutados; selección anterior al test por Macro-F1 de validación | `exploratorio_72/run.json`, `selection.json`, `test_selection_uses_validation_only` | Comprobado, exploratorio |
| F08 Entrenar Transformer multilingüe | HU-04 | Ajuste y persistencia probados con arquitectura diminuta local | `test_transformer_local_training_roundtrip` | Parcial: no ejecución de XLM-RoBERTa T2 |
| F09 Cargar modelos | HU-04/HU-05 | Artefactos clásicos cargados; sin reemplazo silencioso de modelos ausentes | `test_exploratory_training_models_and_report_ui`, `test_registry_does_not_fallback` | Comprobado |
| F10 Clasificar y mostrar alcance | HU-05 | Categoría, modelo y tiempo; puntuación solo si está disponible; modo exploratorio visible | `test_exploratory_training_models_and_report_ui`, `test_context_regressions` | Comprobado; errores predictivos abiertos |
| F11 Métricas y gráficos | HU-06 | Tres modelos, matrices, errores, intervalos y subgrupos mostrados | `test_exploratory_training_models_and_report_ui`, `exploratorio_72/` | Comprobado |
| F12 Explorar corpus | HU-06 | Comunidad, idioma y búsqueda literal | `test_corpus_filters_and_literal_search` | Comprobado |
| F13 Guardado voluntario | HU-05/S5 | Desactivado inicialmente; persiste solo al solicitarlo | `test_three_subsystems_and_optional_history` | Comprobado |
| F14 Historial y filtros | HU-05/S5 | Persistencia, consulta, búsqueda y categoría | `test_save_search_and_filter_history` | Comprobado |
| F15 Respaldo y restauración | RNF/S5 | SQLite consistente, integridad y rechazo de sobrescritura o ZIP corrupto | `test_backup_restore_preserves_records_and_does_not_overwrite`, `test_corrupt_archive_rejected_without_destination` | Comprobado localmente |
| F16 Seguridad local | RNF/S5 | 127.0.0.1, XSRF/CORS, minimización, exclusión de privados | `test_local_server_defaults`, pruebas de historial y seguridad | Comprobado dentro de ese alcance |

## Condiciones para acreditar el 100 %

No se declara 100 %. El ZIP está integrado; falta completar la revisión humana
del corpus y ejecutar el componente Transformer exigido por HU-04, además de la
aceptación efectiva del alcance. Si el profesor reduce explícitamente HU-04 a modelos
clásicos para T2, debe registrarse esa decisión; no se presume.

La matriz permite revisar cada criterio con evidencia; no se convierte el porcentaje
de tests aprobados en porcentaje del proyecto. Para el futuro paper siguen vigentes
datos reales de Reddit con acceso permitido, muestreo justificado, anotación, test
independiente y evaluación científica. No son requisitos nuevos para T2.
