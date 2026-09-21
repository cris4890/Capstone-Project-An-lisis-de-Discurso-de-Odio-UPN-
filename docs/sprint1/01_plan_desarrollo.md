# Plan de desarrollo de software

Proyecto: Análisis y Clasificación Automática del Discurso de Odio en Comunidades de Reddit Asociadas a Millennials y Generación Z mediante Machine Learning y Procesamiento de Lenguaje Natural.

## Objetivo y alcance

Preparar entorno, organización, requisitos, seguridad y procedimientos de datos del Sprint 1, y demostrar un prototipo local de Clasificación, Reportes e Historial. El prototipo utiliza ejemplos sintéticos. La investigación final requiere corpus autorizado, anotación independiente y evaluación aún no acreditados. No se promete que el Transformer superará a los modelos clásicos.

## Periodo

- Inicio: 14 de septiembre de 2026.
- Cierre técnico previsto: 20 de septiembre de 2026, hora de Lima.
- Duración: siete días calendario incluyendo inicio y fin, indicada por el usuario.
- Entrega académica: pendiente de definición.

S3 proponía sprints de dos semanas. Se registra esta diferencia para Sprint 1; las fechas siguientes no se inventan. El inicio describe el periodo indicado, no acredita actividades ni reuniones realizadas el día 14. Las evidencias técnicas se generaron durante desarrollo asistido y no se atribuyen como horas individuales ejecutadas por los estudiantes.

## Organización funcional aceptada

| Subsistema | Función |
|---|---|
| Clasificación | Ingreso de texto, preprocesamiento, categoría, latencia y probabilidad cuando exista. Guardado opcional. |
| Reportes | Métricas y comparación de modelos; exploración del corpus como vista interna. |
| Historial | Consulta de inferencias guardadas con texto procesado, fecha, modelo y resultado. No es un dataset anotado. |

Anotación es una herramienta interna separada (`annotation_app.py`), fuera de la navegación principal. No constituye un cuarto subsistema ni implica autenticación.

## Metodología Scrum

Cada tarea se relaciona con historia, criterio de aceptación y evidencia. Primero se verifica un flujo mínimo; después se completan datos, anotación y modelos. Los roles proceden de S3:

| Rol | Integrante | Responsabilidad de seguimiento |
|---|---|---|
| Product Owner | Sintia Julissa Truyenque Perales | Priorizar backlog y revisar aceptación. |
| Scrum Master | Erick Daniel Carbajal Quiñonez | Coordinar seguimiento, impedimentos y revisión. |
| Desarrollo de Datos y ML/NLP | Crisdel Aldemir Gonzales Canales | Datos, preprocesamiento y modelos. |
| Pruebas, calidad y evaluación | Jeanpierre Amilcar Casimiro Guerra | Pruebas, métricas y evidencia. |

Esta asignación no certifica que cada integrante haya ejecutado las tareas registradas.

### Eventos

- Planning: acordar Sprint Goal, tareas y capacidad; registrar asistentes y fecha reales.
- Daily: revisar avance, siguiente tarea e impedimentos durante el sprint.
- Review: demostrar el incremento y registrar criterios aceptados o rechazados.
- Retrospectiva: acordar una mejora con responsable y fecha.

Los formatos están en `05_registros.md`. No hay evidencia suficiente para declarar realizadas estas ceremonias.

## Plan de entregas

Se usa S3 como referencia operativa de esta entrega, sin sustituir silenciosamente el cronograma del PDF. La armonización general debe ratificarse con el equipo.

| Sprint | Objetivo | Condición de cierre |
|---|---|---|
| 1 | Entorno, backlog, requisitos, preparación de acceso, manual e incremento local | Evidencias técnicas y documentación; revisión del equipo registrada. |
| 2 | Obtención autorizada y preparación del corpus | Procedencia, periodo, idioma y minimización verificados. |
| 3 | Piloto y anotación | Dos evaluadores, adjudicación y kappa reportado; revisar si no alcanza 0,70. |
| 4 | Reglas, regresión logística y SVM | Particiones por hilo y selección en validación. |
| 5 | Transformer multilingüe | Ajuste documentado y comparación en validación; test reservado. |
| 6 | Integración | Modelos seleccionados integrados y pruebas de aceptación. |
| 7 | Evaluación final | Mismo test, errores, límites y documentación final. |

Funciones adelantadas no equivalen a cerrar sprints posteriores: faltan sus datos y evidencias científicas.

## Arquitectura

Streamlit sirve la interfaz local. `corpus.py` valida CSV/Parquet y `data_pipeline.py` limpia texto. `annotations.py` registra anotaciones en SQLite. `experiment.py` y `train_models.py` separan por hilo, seleccionan en validación y evalúan. `model_registry.py` carga artefactos de una ejecución. `history_store.py` mantiene inferencias fuera del corpus. `maintenance.py` respalda SQLite y comprueba integridad.

## Recursos

Se utilizan el equipo local y herramientas existentes; no se contrató infraestructura ni cómputo de pago. S/ 0 es el desembolso incremental confirmado, no el costo total del proyecto. Las horas reales del equipo no están acreditadas: deben registrarse sin estimarlas retrospectivamente como si fueran mediciones.

## Riesgos prioritarios

| Riesgo | Respuesta | Estado |
|---|---|---|
| Acceso a datos no concedido | Preparar solicitud; alternativa licenciada con revisión de alcance. | Pendiente externo. |
| Identificación por texto | Minimización y revisión manual. | Control automático parcial. |
| Clasificación equivocada | Limitaciones visibles, revisión humana y casos funcionales. | Reglas tienen limitaciones conocidas. |
| Fuga entre particiones | Agrupar por hilo y rechazar duplicados. | Pruebas automatizadas. |
| Pérdida de archivos | Versionar y probar restauración. | Herramienta y pruebas locales. |
| Documentos contradictorios | Registrar diferencias y acordar por contenido. | Armonización pendiente. |
