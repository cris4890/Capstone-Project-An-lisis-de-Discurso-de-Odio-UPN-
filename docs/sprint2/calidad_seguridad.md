# Registro de incidencias riesgos y seguridad

Actualización técnica 19/10/2026. Los estados corresponden a evidencia disponible, no a aceptación del profesor.

## Incidencias

| ID | Hallazgo | Evidencia | Severidad | Estado y acción |
| --- | --- | --- | --- | --- |
| INC-01 | 12 errores de 30, exactitud 60 % | metricas.json y errores.csv | Alta | Abierto. Preservar baseline; mejorar reglas/modelo y evaluar muestra reservada |
| INC-02 | Los 10 casos de Odio se predicen Neutro; recall de Odio 0 % | matriz_confusion.csv | Alta | Abierto. No usar para moderación autónoma; revisión humana obligatoria |
| INC-03 | T014 y T029 ofensivos se predicen Neutro | errores.csv | Media | Abierto. Incorporar regresiones al plan de corrección sin entrenar sobre prueba final |
| INC-04 | La interfaz llamaba tiempo de respuesta a la inferencia | diff de app.py; capturas | Media | Corregido técnicamente: etiqueta Tiempo de inferencia y alcance explícito; E2E separado |
| INC-05 | Excel usa categorías D que discrepan de J en 12 filas | auditoria_excel.json | Alta | Corregido en el anexo derivado; original preservado sin modificación |
| INC-06 | Se comparaban microsegundos de inferencia con trabajo manual | protocolo_kpi.md | Alta | E2E medido; comparabilidad integral sigue pendiente |
| INC-07 | Informe cita 74 pruebas y avance ≥70 % sin denominador verificable | PC8 proporcionado | Media | Actualizar número real y sustituir porcentaje por alcance verificable |

## Riesgos

| ID | Riesgo | Evidencia y tratamiento | Estado |
| --- | --- | --- | --- |
| R01 | Baja calidad predictiva | Ya materializado en piloto: 60 % y 0 % recall Odio. Mantener revisión humana, ampliar corpus autorizado y evaluación reservada | Alto, abierto |
| R02 | Sobreestimar productividad | Límites temporales distintos; reportar resultados descriptivos y repetir protocolo comparable | Alto, abierto |
| R03 | Sesgo de selección y aprendizaje | 30 casos sintéticos conocidos, balanceados por diseño; no extrapolar prevalencia ni desempeño real | Alto, abierto |
| R04 | Retraso de autorización/corpus | No hay evidencia de corpus real final autorizado; planificar alternativa licenciada compatible | Alto, abierto |
| R05 | Pérdida o acceso indebido al equipo | SQLite y ZIP locales sin cifrado; cuenta del equipo y respaldo externo no verificados | Alto, abierto |
| R06 | Aceptación no documentada | Preparar Review, registrar decisiones reales sin completar firmas o asistentes por inferencia | Medio, abierto |

## Controles implementados y comprobables

Escucha local 127.0.0.1; CORS y XSRF habilitados; límite de subida de 10 MB; guardado voluntario; enmascaramiento de usuarios, URL, correo y teléfono; consultas SQLite parametrizadas; exclusión de private/ y runs/ de Git; backup local consistente y restauración sin sobrescritura verificados con datos de prueba. Ver tests/test_security.py y tests/test_workflow.py.

No se acreditan autenticación multiusuario, autorización por roles, TLS productivo, cifrado de SQLite o ZIP, backup externo, revisión de ACL ni purga automática. No se añaden marcas de completado a controles solo planificados.

La fecha de eliminación acordada por el usuario es el 30 de diciembre de 2026 y la entrega el 2 de diciembre de 2026. Deben abarcar copias, exportaciones y artefactos derivados sujetos a autorización. No se han eliminado datos durante esta tarea. Una autorización con un plazo menor prevalece para sus datos.
