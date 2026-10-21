# Sprint Backlog y Definition of Done

## Sprint Goal

Disponer de entorno reproducible, requisitos trazables, planificación y seguridad documentadas, y demostrar Clasificación, Reportes e Historial con datos sintéticos.

Periodo: 14–20 de septiembre de 2026. Entrega académica pendiente. Este backlog organiza alcance y evidencia disponibles; no se presenta como acta de Planning realizada el día 14.

## Product Backlog priorizado

Actualización de alcance T2 (21/10/2026): el solicitante comunica que el profesor
autorizó comentarios sintéticos del equipo para desarrollar y evaluar durante el
curso. Reddit real deja de ser condición de esta entrega; permanece en el alcance
del futuro paper. Esto no certifica revisión humana de los 72 ejemplos ni aceptación
de las historias. Se conservan HU-01 a HU-06, sin duplicarlas. El Sprint Backlog
inferior conserva el registro histórico. Estado actual y evidencias: [T2](../t2/backlog_cumplimiento.md).

| Historia S3 | Prioridad | Resultado esperado | Estado |
|---|---|---|---|
| HU-01 | Alta | Preparar corpus sintético permitido para T2 y documentar procedencia; Reddit autorizado para futuro paper. | Parcial: exportación y validación disponibles; revisión humana y ZIP anunciado pendientes. |
| HU-02 | Alta | Minimizar datos e identificarlos internamente. | Implementación local comprobable; revisión humana de privacidad pendiente. |
| HU-03 | Alta | Manual y anotación independiente. | Herramientas implementadas; revisión del corpus T2 pendiente. |
| HU-04 | Alta | Comparar reglas, clásicos y Transformer. | Parcial: entrenamiento clásico exploratorio; comparación con XLM-RoBERTa pendiente. |
| HU-05 | Alta | Clasificar y mostrar puntuación cuando exista. | Implementación local; aceptación formal pendiente. Historial se sustenta además en S5 y Sprint 6 de S3. |
| HU-06 | Media | Métricas, errores y pruebas por idioma/comunidad. | Reportes implementados para ejecuciones disponibles; aceptación formal pendiente. |

## Sprint Backlog

Los responsables corresponden a seguimiento según S3; no certifican autoría de la ejecución asistida.

| ID | Prioridad | Historia | Criterio de aceptación | Responsable | Evidencia y estado |
|---|---|---|---|---|---|
| S1-01 | Alta | Todas | Entorno ejecuta pruebas y registra versiones exactas. | Crisdel | Lockfile y pruebas; técnico verificado. |
| S1-02 | Alta | Todas | Cambios identificables por rama y commit. | Erick | Git local y documento de ramas; ver registro. |
| S1-03 | Alta | Todas | Backlog priorizado, responsables y DoD definidos. | Sintia | Este documento; capacidad del equipo por ratificar. |
| S1-04 | Alta | Todas | Requisitos relacionados con funciones y evidencia. | Sintia / Jeanpierre | Matriz inferior; aceptación pendiente. |
| S1-05 | Alta | HU-01 | Preparar solicitud sin iniciar extracción no autorizada. | Crisdel | `07_preparacion_datos.md`; envío pendiente. |
| S1-06 | Alta | HU-03 | Manual define clases, independencia y adjudicación. | Jeanpierre | `../manual_anotacion.md`; especialistas pendientes. |
| S1-07 | Alta | HU-02 | Seguridad cubre datos, app, infraestructura e incidentes. | Erick / Jeanpierre | `04_seguridad.md`, configuración y respaldo. |
| S1-08 | Alta | HU-05 / S5 | Clasificar y guardar opcionalmente una inferencia consultable. | Crisdel / Jeanpierre | Pruebas de interfaz e historial. |
| S1-09 | Media | HU-06 / S5 | Reportes integra evaluación y corpus. | Jeanpierre | Pruebas y ejecución demostrativa. |
| S1-10 | Alta | Todas | Conservar evidencia, incidencias y guía de demostración. | Erick / Jeanpierre | Evidencias; Review pendiente. |

## Trazabilidad

Se conserva el prefijo del documento: los códigos RF/RNF no son equivalentes entre fuentes.

| Referencia | Función | Aceptación técnica y límite |
|---|---|---|
| PC4 RF-01 / S3 HU-01 / PDF RF-01 | Procedencia | Rechazar datos reales sin evidencia; no acredita permiso ni extracción. |
| PC4 RF-02 / S3 HU-02 / PDF RF-02 | Minimización | Enmascarar casos de prueba y excluir originales; no garantiza anonimato completo. PDF usa hashes de usuarios: diferencia por armonizar. |
| PC4 RF-03 / PDF RF-03 | Preprocesamiento | Preservar contexto y rechazar duplicados antes de separar. |
| PC4 RF-04 / S3 HU-03 / PDF RF-04 | Anotación | Dos evaluadores, adjudicación y kappa; faltan anotaciones reales y preetiquetado. |
| PC4 RF-05 / S3 HU-04 | Modelos | Guardar/cargar artefactos y seleccionar en validación; Transformer real pendiente. |
| PC4 RF-06 y RF-07 / S3 HU-06 | Reportes | Métricas por clase, errores y subgrupos; corpus sintético no estima prevalencia. |
| S3 HU-05 / S5 Clasificación | Inferencia | Texto válido produce categoría; confianza solo cuando disponible. |
| S5 Historial / S3 Sprint 6 | Registro | Guardado opcional y persistencia de texto procesado, modelo y resultado. |
| PC4 RNF-01 / PDF RNF-06 | Reproducibilidad | Semillas, particiones, versiones y hashes; repetición científica independiente pendiente. |
| PC4 RNF-02 y RNF-06 / PDF RNF-02 y RNF-03 | Privacidad | Configuración local y respaldo íntegro; no acredita autenticación o cumplimiento legal. |
| PC4 RNF-03 / PDF RF-04 | Trazabilidad | Registrar corpus, evaluador y decisión; identidad real no autenticada. |
| PC4 RNF-04 / PDF RF-05 | Métricas | Precisión, recall y F1 de tres clases; sin umbral arbitrario de exactitud. |
| PC4 RNF-05 / S5 Seguridad | Revisión humana | Sin sanciones ni eliminación automática. |
| PDF RNF-01, RNF-04 y RNF-05 | Calidad | Latencia, errores, módulos y pruebas documentados; sin máximo de tiempo inventado. |

## Definition of Done

| Criterio | Evidencia | Situación |
|---|---|---|
| Código ejecutable | Suite sin fallos sobre la versión entregada. | Ver resumen de pruebas. |
| Funciones aceptables | Clasificación, Reportes e Historial comprobados. | Evidencia automatizada. |
| Datos protegidos | Pruebas sintéticas y guardado minimizado. | Casos probados; no anonimato universal. |
| Documentación | Plan, ramas, seguridad, uso y límites. | Paquete de esta carpeta. |
| Versionado | Rama y commit identificables. | Ver registro; nube evaluada por separado. |
| Reproducibilidad | Lockfile, comandos, semillas y particiones. | Entorno y ejecución demostrativa. |
| Sin defectos críticos del incremento | No impedir demostración local sintética. | No habilita producción ni datos reales. |
| Revisión y aceptación | Fecha, asistentes y resultado de Review. | Pendiente del equipo/docente. |

No confundir «terminado técnicamente para demostración» con «aceptado por el equipo». No marcar ceremonias o aprobaciones sin evidencia.
