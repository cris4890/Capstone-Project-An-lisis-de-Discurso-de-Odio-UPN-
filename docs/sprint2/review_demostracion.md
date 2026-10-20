# Review de Sprint 2 y sustentación

Estado: preparada, no celebrada ni aceptada formalmente en esta evidencia.
Fecha de preparación: 19/10/2026. Fecha de sesión, participantes asistentes y aprobaciones: pendientes de registro por el equipo. No se asume que los autores del proyecto asistieron.
Versión: rama codex/sprint2-evidencias; hashes de fuentes en evidencias/version.json. Registrar el commit definitivo en el acta de la sesión.

## Criterios a revisar

| ID | Criterio | Evidencia técnica | Decisión humana |
| --- | --- | --- | --- |
| AC-01 | Clasificar un texto y mostrar modelo, categoría y alcance | captura de Clasificación; pruebas de sistema | Pendiente |
| AC-02 | Guardado voluntario y consulta en Historial | recorrido real con historial aislado; test_save_search_and_filter_history | Pendiente |
| AC-03 | Explorar Reportes y filtros sin inventar evaluaciones | captura de Reportes; test_corpus_filters_and_literal_search | Pendiente |
| AC-04 | Mostrar 12 errores y matriz del piloto sin ocultarlos | RESULTADOS.md y errores.csv | Pendiente |
| AC-05 | Distinguir inferencia y tiempo E2E | e2e_navegador.json, protocolo | Pendiente |
| AC-06 | Mostrar pruebas, versión y estado de CI | JUnit XML, rama y Pull Request | Pendiente |

Observaciones para la sesión: revisión humana, limitaciones de la muestra sintética, discrepancias del Excel, alcance de tiempos, datos autorizados pendientes y seguridad local.

## Guion de demostración

1. Abrir Clasificación y mostrar reglas v2, origen sintético y advertencias.
2. Ingresar “Gracias por compartir la información.” y mostrar categoría y tiempo de inferencia.
3. Mostrar T003 y explicar honestamente el falso negativo. No sustituirlo por un caso favorable.
4. Activar Guardar en Historial con un texto sintético, clasificar y verificar confirmación.
5. Abrir Historial, buscar el texto, filtrar categoría y explicar que una inferencia no es una etiqueta humana validada.
6. Abrir Reportes y Exploración del corpus. Mostrar que la evaluación de modelos exige una ejecución completa; no presentar resultados históricos como nuevos.
7. Abrir matriz de confusión y anexo KPI del Sprint. Explicar 28/30 manual y 18/30 HateDetect, y límites de la comparación temporal.
8. Ejecutar pytest y abrir el inventario por tipo. Mostrar un fallo didáctico solo en copia aislada si se solicita.
9. Abrir rama, commit, PR y Actions. Distinguir pruebas aprobadas de aceptación humana y de calidad predictiva.
10. Registrar observaciones y decisiones de los asistentes, sin afirmar cierre científico ni 100 % del proyecto.
