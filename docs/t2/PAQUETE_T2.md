# Procedimiento del paquete recibido

Se revisaron `preparar_corpus_t2.py`, README, plantilla, protocolo Word y log incluidos en `HateDetect_Paquete_Corpus_T2_Listo.zip`. El log aportado describe pruebas simuladas previas con 18 ejemplos; no se presenta como una ejecución del repositorio actual. El protocolo es material de trabajo, no un acta de aprobación. No se adopta su estimación histórica del 88,89 % como porcentaje comprobado de T2.

El script original se integró en la raíz con estas correcciones: fechas ISO válidas y cronológicas, prevalidación de todos los destinos antes de escribir, comprobación del corpus mediante los validadores compartidos, exclusión del piloto KPI y verificación de que la partición por hilo es viable. La plantilla original está en `Plantilla_Registro_Comentarios_T2.csv`.

## Uso

```powershell
.\.venv\Scripts\python.exe preparar_corpus_t2.py exportar --salida private/t2_revision_paquete_v1.csv
```

Exporta los 72 textos y etiquetas propuestas. Autor, fechas, revisor y etiqueta validada permanecen vacíos y la decisión es `pendiente`. Mantener este registro en `private/`, excluido de Git. Si no se conoce la autoría original, no atribuirla al equipo: crear comentarios propios o documentar su procedencia real y acordar el alcance con el profesor.

Completar únicamente información real. Fechas en `YYYY-MM-DD`, revisor distinto del autor, justificación y decisión explícita. Guardar una versión nueva antes de validar:

```powershell
.\.venv\Scripts\python.exe preparar_corpus_t2.py validar --entrada private/t2_revision_paquete_v2.csv --salida private/t2_preparado_v2.csv
```

Una hoja incompleta produce auditoría `NO_APTO_PARA_ENTRENAR` y salida 2; no crea corpus ni manifiesto. Una hoja formalmente completa genera corpus minimizado y manifiesto de **revisión declarada, no autenticada**. El mínimo de 18 ejemplos y 5 por clase es técnico, no una justificación estadística. Se comprueba además la partición real.

## Compatibilidad con HU-03 y entrenamiento

La hoja del paquete registra un revisor; no sustituye las dos anotaciones y adjudicación del sistema. Abrir la herramienta y cargar el CSV preparado exacto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8503
```

Completar las dos anotaciones y resolver discrepancias; conservar la base SQLite utilizada. Después:

```powershell
.\.venv\Scripts\python.exe train_models.py --data private/t2_preparado_v2.csv --synthetic-mode reviewed --annotation-db private/annotations.sqlite3 --output runs/t2_revisado_v2
```

La ruta SQLite debe ser la real utilizada en la herramienta; no crear otra vacía ni copiar identidades de ejemplos. La base vincula etiquetas al hash del CSV exacto. Cambiarlo requiere revisión del nuevo archivo. No se importan automáticamente firmas ni decisiones de una persona como si fueran dos evaluadores. Para experimentar sin revisión, usar explícitamente `--synthetic-mode exploratory`; sus resultados se identificarán como demostración.

El comando antiguo del paquete `train_models.py --data ...` ya no basta: se exige el modo explícito. El Transformer sigue siendo opcional en el comando (`--include-transformer --epochs 3`), pero pendiente de la comparación exigida por HU-04 mientras el alcance no se modifique formalmente.
