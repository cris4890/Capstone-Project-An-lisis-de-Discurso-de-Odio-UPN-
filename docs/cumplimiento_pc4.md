# Matriz de cumplimiento del PC4

Esta matriz distingue implementación técnica, pruebas locales y evidencia de investigación pendiente. No certifica cumplimiento legal ni calidad predictiva con datos reales.

| Requisito | Implementación actual | Evidencia pendiente |
|---|---|---|
| RF-01 Datos autorizados | Importación de CSV con declaración de origen, fechas, condiciones y archivo de evidencia | Autorización real y adquisición por el mecanismo concedido; no hay recolector Reddit |
| RF-02 Minimización | Campos permitidos, usuarios/enlaces/correos/teléfonos enmascarados, UUID internos y exportaciones sin originales | Revisión humana de datos personales indirectos; retiro controlado de archivos históricos si procede |
| RF-03 Preprocesamiento | Unicode, emojis compuestos, vacíos, duplicados, bots declarados y detección de idioma | Revisión documentada de idiomas dudosos y metadatos de bots verificados |
| RF-04 Anotación | Panel y SQLite para dos evaluadores, grupo, justificación y adjudicación | Anotaciones humanas reales y manual validado |
| RF-05 Modelos | Reglas, regresión logística, SVM; ajuste y persistencia de XLM-RoBERTa configurados | Entrenamiento y evaluación del Transformer multilingüe en el corpus validado |
| RF-06 Métricas | Por clase, balanceada, matrices, errores por unidad, bootstrap por hilo y pruebas funcionales | Evaluación final sobre muestra independiente real |
| RF-07 Comunidades | Frecuencias filtrables y desempeño por comunidad, idioma y tipo | Muestreo probabilístico, intervalos de prevalencia y contraste estadístico justificado |
| RNF-01 Reproducibilidad | Semillas, particiones, hashes, parámetros de estimadores guardados, versiones exactas y entorno por ejecución | Reproducción independiente; registrar revisiones exactas de pesos externos para una corrida definitiva |
| RNF-02 Privacidad | Exportación mínima; carpetas privadas excluidas de Git; uso local documentado | Autenticación multiusuario, permisos institucionales y política aplicada de eliminación |
| RNF-03 Trazabilidad | Corpus identificado por SHA-256, evaluadores, fechas, versión del manual y decisiones no sobrescritas | Verificación de identidad e independencia real de evaluadores |
| RNF-04 Métricas por clase | Precisión, recall, F1, soporte, FP, FN, FPR y FNR | Calidad predictiva suficiente según criterios acordados |
| RNF-05 Supervisión humana | Predicciones orientativas; sin sanciones; advertencias sobre probabilidades | Validación de uso con usuarios |
| RNF-06 Condiciones de uso | Evidencia requerida en importación y entrenamiento real; no realiza scraping | Revisión institucional, autorizaciones y cumplimiento de los plazos |

## Compromisos metodológicos

- Separación por hilo: implementada con objetivo aproximado 70/15/15. La restricción de grupos puede impedir proporciones exactas. La selección de partición usa tamaños y etiquetas, nunca desempeño del modelo.
- Selección del modelo: Macro-F1 de validación; decisión guardada antes de predecir prueba.
- Kappa: piloto sintético con respuestas reportadas de A y B, 49 pares originales y kappa 0,828791; seis casos con adjudicación reportada de E3. No acredita independencia humana autenticada ni validación de un corpus real. Ver `reporte_anotacion.md` y `corpus_piloto.md`.
- V de Aiken: función disponible; faltan valoraciones de especialistas.
- Pruebas funcionales: 24 casos bilingües propuestos, pendientes de validación humana; sus fallos se reportan, no se ocultan.
- Rendimiento: tiempos y asignaciones de memoria de Python. La medida no incluye toda la memoria nativa ni GPU.
- Probabilidades: se muestran cuando el modelo las ofrece; reglas y SVM sin calibración no inventan probabilidades.
- Muestreo, controles éticos, gestión Scrum y diagramas UML: requieren trabajo documental y evidencia del equipo; no se dan por cumplidos mediante código.

## Conservación de trabajo anterior

Los datos, modelos e imágenes preexistentes de `data/`, `models/` y `metrics/` se conservaron. El panel nuevo no presenta esos resultados como evaluación actual. Las nuevas ejecuciones van a `runs/` y no sobrescriben una carpeta existente.


## Complemento S3 y S5

El usuario aceptó Clasificación, Reportes e Historial como tres subsistemas. La exploración del corpus se integra en Reportes y Anotación es una herramienta interna separada. Historial se implementa con guardado voluntario y persistencia local de texto procesado y metadatos; no convierte inferencias en anotaciones humanas.

Ver [paquete Sprint 1](sprint1/README.md) para backlog, DoD, seguridad y pruebas. Acceso multiusuario, conservación aplicada de datos reales y respaldo externo siguen pendientes. Los Word/PDF originales no se modificaron ni se les atribuye aprobación docente.
