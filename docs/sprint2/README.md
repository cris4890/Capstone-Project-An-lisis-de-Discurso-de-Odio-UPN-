# Sprint 2 Evidencias del producto y piloto

Preparación técnica del 19 de octubre de 2026. Rama `codex/sprint2-evidencias`, base `92c470d`. La fecha de preparación no acredita la celebración de una Review.

## Estado verificable

- [Estado de los veinte puntos y pendientes](estado_entrega.md).
- [Resultados y clasificación de pruebas](RESULTADOS.md).
- [Protocolo de medición y auditoría del Excel](protocolo_kpi.md).
- [Matriz requisito a prueba](trazabilidad.md).
- [Incidencias, riesgos y seguridad](calidad_seguridad.md).
- [Review preparada y guion de sustentación](review_demostracion.md).
- [Borrador de resultados y compromiso ético](capitulos.md).
- [Anexo completo de 30 casos](evidencias/anexo_kpi.csv), [errores](evidencias/errores.csv) y [matriz de confusión](evidencias/matriz_confusion.png).

El producto es un prototipo local funcional. No se acredita el 100 % del proyecto, aceptación formal, autorización de corpus real ni validación científica final. El piloto sigue mostrando fallos de calidad predictiva.

## Reproducción

```powershell
.\.venv\Scripts\python.exe -m pytest -q -o junit_family=xunit1 --junitxml=docs/sprint2/evidencias/pruebas.xml
.\.venv\Scripts\python.exe tools/evaluar_sprint2.py
```

La prueba histórica de 74 casos creció hasta 103 antes de este Sprint. Se ejecuta la suite vigente completa; no se excluyen casos para mantener un número antiguo. Los casos de aceptación humana no se marcan aprobados por el resultado de pytest.

El script de evaluación conserva los tiempos de inferencia en un campo distinto a E2E. Las entradas manuales proceden de la ficha aportada por el usuario y se mantienen con su procedencia; los datos originales permanecen en una copia privada. `evidencias/version.json` identifica las fuentes probadas mediante SHA256.

## Capturas

Las capturas en `capturas/` proceden del navegador real. La instancia de demostración usa puerto 8502 e historial aislado. El puerto 8501 y el historial habitual no se utilizaron para guardar los casos del piloto.

## Pendientes externos

Registrar participantes, fecha real y decisiones de Review; confirmar independencia de la clave y límites del cronometraje manual; repetir un proceso completo con ingreso y supervisión humana comparables; completar corpus autorizado, anotación real, entrenamiento definitivo y evaluación independiente.
