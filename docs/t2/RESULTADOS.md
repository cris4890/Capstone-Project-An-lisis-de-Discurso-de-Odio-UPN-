# HateDetect: verificación del alcance T2

Fecha de actualización: 21 de octubre de 2026. `main` verificado en `f6fe5e7`, integración del [Pull Request #2](https://github.com/cris4890/Capstone-Project-An-lisis-de-Discurso-de-Odio-UPN-/pull/2). Su GitHub Actions posterior finalizó correctamente. Las cifras históricas siguientes pertenecen al PR #2 y no se reinterpretan como revisión humana.

## Cambios entregados

- `preparar_corpus_t2.py`, `tests/test_paquete_t2.py`, plantilla y `PAQUETE_T2.md`: integración del ZIP recibido, fechas válidas, prevalidación de destinos, exclusión KPI y compatibilidad con el entrenamiento y HU-03. Exportación real en `private/t2_revision_paquete_v1.csv`, pendiente y excluida de Git.
- `synthetic_corpus.py`: exportación de 72 comentarios, plantilla sin revisión inventada, procedencia y hashes; validación y exclusión de los 30 casos KPI por texto normalizado.
- `corpus.py`: identificadores sintéticos estables, detección de etiquetas contradictorias y validación estricta de campos, idioma, origen, etiquetas y duplicados.
- `data_pipeline.py`: protección contra sobrescritura de corpus y evidencias.
- `experiment.py`: detección normalizada de duplicados antes de particionar.
- `train_models.py`: modos exploratorio/revisado; revisión mediante registros de anotación asociados al archivo exacto; bloqueo de corpus inválidos y del piloto reservado.
- `app.py`: presentación explícita del carácter exploratorio y estado de revisión.
- `tests/test_synthetic_corpus.py` y `tests/conftest.py`: 26 casos nuevos y clasificación de pruebas.
- `README.md`, backlog original y `docs/t2/`: procedimiento, matriz funcional, incidencias, corpus exportado y evidencias nuevas. No se modificaron métricas históricas ni documentos privados de tesis.

## Pruebas ejecutadas

| Ejecución | Resultado | Evidencia en `evidencias/` |
|---|---|---|
| Base antes de cambios | 105 aprobadas, 60,80 s | `pruebas_base.xml`, `.txt` |
| Nuevas pruebas iniciales | 25 aprobadas, 18,21 s | `pruebas_corpus.xml`, `.txt` |
| Primera regresión completa | 130 aprobadas, 26,96 s | `pruebas_final.xml`, `.txt` |
| Ruta positiva de entrenamiento revisado, aislada | 1 aprobada, 9,94 s; incluida después en regresión | salida de ejecución y caso correspondiente en XML final |
| Versión anterior al ZIP | 131 aprobadas, 29,65 s | `pruebas_version_131.xml`, `.txt` |
| Integración del ZIP | 11 aprobadas, 11,34 s | `paquete_zip_pruebas.xml`, `.txt` |
| Versión final con ZIP | **142 aprobadas, 0 fallidas, 0 omitidas; 34,51 s** | `pruebas_version_142.xml`, `.txt` |
| Laboratorio inicial | 10 aprobadas | `laboratorio/resumen.json` |
| Fallo deliberado en copia temporal | 9 aprobadas y 1 fallo esperado | `laboratorio/resumen.json` |
| Laboratorio restaurado | 10 aprobadas; fuentes originales intactas | `laboratorio/resumen.json` |

El inventario final contiene **96 unitarias, 38 de integración y 8 de sistema** en [inventario_pruebas_142.csv](evidencias/inventario_pruebas_142.csv). Las pruebas de sistema usan Streamlit AppTest, no un navegador real. La aceptación humana formal no se sustituye por pytest. Las identidades FIXTURE de los tests son datos simulados temporales, no revisión del equipo.

Se comprobaron clasificación y carga de modelos, reportes, navegación, guardado voluntario, búsqueda y filtros del historial, anotación y adjudicación, persistencia, partición, entrenamiento clásico, circuito Transformer diminuto local, respaldo/restauración e integridad y configuración local. Los detalles requisito → prueba → resultado están en [la matriz](backlog_cumplimiento.md).

## Entrenamiento exploratorio ejecutado

72 propuestas del generador, **pendientes de revisión humana**. Particiones por hilo: 50 entrenamiento, 11 validación, 11 prueba. Semilla y particiones registradas en `evidencias/exploratorio_72/`. Ninguna coincidencia normalizada con los 30 textos KPI; el control no detecta paráfrasis ni garantiza independencia científica del generador.

| Modelo | Macro-F1 validación | Exactitud prueba | Macro-F1 prueba | Recall Odio prueba |
|---|---:|---:|---:|---:|
| Reglas | 0,5556 | 63,64 % | 0,5333 | 0 % |
| Regresión logística | 0,6857 | 54,55 % | 0,5357 | 75 % |
| SVM | 0,6857 | 54,55 % | 0,4722 | 75 % |

Se seleccionó regresión logística por validación (empate con SVM resuelto por el orden estable de candidatos), antes de evaluar prueba. No se eligió por el resultado del test. Se ejecutaron 500 remuestreos bootstrap; resultados y matrices se conservan. Los modelos serializados están localmente en `runs/t2_20261021_exploratorio/`, excluidos de Git; se regeneran con el comando indicado abajo.

Esta ejecución demuestra funcionamiento técnico, no calidad científica definitiva. Son solo 11 ejemplos de prueba con etiquetas propuestas por el generador. El **60 % histórico del piloto KPI permanece intacto**, en otro conjunto y contexto; no se reemplaza por estas métricas. El recall 0 de Odio de las reglas continúa siendo una limitación visible.

No se entrenó XLM-RoBERTa completo: no estaba disponible su checkpoint local. El test con Transformer diminuto verifica el circuito, no satisface la comparación final de HU-04.

## Estado de las historias y pendientes

Se conservaron HU-01 a HU-06, sin historias duplicadas. HU-02, HU-05 y HU-06 tienen implementación local comprobada dentro del alcance descrito; aceptación formal pendiente. HU-01 y HU-03 son parciales por la revisión humana de los 72 casos. HU-04 es parcial por la comparación Transformer pendiente. Véanse criterios individuales y evidencias en el backlog actualizado.

La Fase 3 agrega controles probados para roles A/B/E3, reanudación y progreso por
evaluador, desacuerdos exclusivos, consenso inmutable, Kappa previo y exportación
condicionada. Esto mejora el flujo, pero no cambia el estado parcial de HU-01/HU-03:
Jeanpierre y Erick aún deben revisar los 72 textos y Crisdel debe resolver los
desacuerdos reales. La aceptación académica también continúa pendiente.

Verificación local actualizada de la Fase 3: **150 pruebas aprobadas, 0 fallidas**
en 35,57 s. El conteo incluye las 142 pruebas heredadas y 8 casos nuevos de roles,
progreso, reanudación, independencia, normalización de objetivos, desacuerdos,
concordancia y condiciones de exportación. No se modifica el inventario histórico
de 142 pruebas del PR #2.

**No se acredita el 100 % de T2**: falta revisar humanamente el corpus, completar la comparación exigida por HU-04 o registrar una modificación aprobada de ese alcance, y realizar la aceptación formal. La autorización para datos sintéticos se registra como comunicación del solicitante; no se inventó un acta del profesor. Reddit no bloquea T2 según esa autorización; permanece como requisito metodológico del futuro paper.

Seguridad verificada solo en entorno local: minimización, guardado voluntario, escucha local, XSRF/CORS, respaldo y restauración. Autenticación de personas, cifrado productivo y respaldo externo no se declaran implementados.

## Ejecutar la versión

Desde la raíz del repositorio, en PowerShell:

```powershell
git switch codex/t2-corpus-sintetico
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Entrenamiento de demostración en una carpeta NUEVA (se rechaza sobrescribir):

```powershell
.\.venv\Scripts\python.exe train_models.py --data docs/t2/corpus_72/corpus_exploratorio.csv --synthetic-mode exploratory --output runs/t2_nueva_demostracion --bootstrap 500
```

Procedimiento completo de exportación, revisión y anotación: [README T2](README.md). El PR se publica para revisión del solicitante, sin fusión automática; el resultado remoto de GitHub Actions se consulta en sus checks y artefactos.
