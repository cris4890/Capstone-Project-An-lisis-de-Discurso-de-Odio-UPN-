# Matriz de trazabilidad de requisitos

Clasificación técnica por pytest en tests/conftest.py. El detalle de cada parametrización, su tipo y resultado está en evidencias/inventario_pruebas.csv; JUnit es la evidencia de ejecución. La aprobación de pruebas no certifica el cumplimiento completo del requisito.

| Requisito | Prueba representativa | Tipo | Resultado y límite | Evidencia |
| --- | --- | --- | --- | --- |
| RF-01 Procedencia autorizada | test_real_data_requires_evidence | Integración | Valida barrera de importación; autorización real pendiente | pruebas.xml |
| RF-02 Minimización | test_minimization_and_context; PU02 y PU03 | Unitaria | Enmascaramiento comprobado; identificación indirecta requiere revisión | pruebas.xml |
| RF-03 Preparación y particiones | test_prepare_excludes_raw_and_deduplicates; test_group_split_reproducible | Integración | Flujo sintético verificado | pruebas.xml |
| RF-04 Anotación | test_anotations_and_adjudication | Integración | Persistencia y adjudicación probadas; independencia real no autenticada | pruebas.xml |
| RF-05 Clasificación | test_context_regressions; piloto T001–T030 | Unitaria y sistema real | Pruebas programadas y piloto tienen propósitos distintos; piloto 12 fallos | errores.csv y e2e_navegador.json |
| RF-05 Transformer | test_transformer_local_training_roundtrip | Integración | Modelo diminuto local de prueba, no Transformer definitivo validado | pruebas.xml |
| RF-06 Métricas | test_metrics_counts_and_missing_class | Unitaria | Cálculos verificados; calidad predictiva insuficiente en piloto | pruebas.xml y matriz_confusion.csv |
| RF-07 Comunidades y reportes | test_corpus_filters_and_literal_search | Sistema con AppTest | Filtros sintéticos; no muestreo real ni prevalencia | pruebas.xml, capturas/reportes.png |
| Historial voluntario | test_save_search_and_filter_history | Sistema con AppTest y navegador | Persistencia, búsqueda y filtros; guardado real aislado | pruebas.xml, capturas/historial.png |
| RNF-01 Reproducibilidad | test_group_split_reproducible; test_bootstrap_deterministic | Integración y unitaria | Semillas y hashes; evaluación científica pendiente | pruebas.xml, version.json |
| RNF-02 Seguridad local | test_local_server_defaults; test_backup_restore_preserves_records_and_does_not_overwrite | Unitaria e integración | Alcance local; autenticación/cifrado productivo/backup externo pendientes | pruebas.xml, calidad_seguridad.md |
| RNF-03 Trazabilidad | test_closure_rejects_modified_evidence | Integración | Integridad comprobada; no acredita identidad de evaluadores | pruebas.xml |
| RNF-04 Desempeño | piloto 30 y medición navegador | Sistema real | 60 % de exactitud; ventana E2E medida una vez por caso | metricas.json, e2e_navegador.json |
| RNF-05 Supervisión humana | AC-01 a AC-06 | Aceptación | Pendiente de sesión y decisiones reales | review_demostracion.md |

Las pruebas de integración incluyen almacenamiento, restauración y ciclo de entrenamiento/carga. No se presentan esos recorridos como unitarios. AppTest no equivale a un navegador ni acredita latencia E2E. No hay pruebas de carga/JMeter en esta ejecución.
