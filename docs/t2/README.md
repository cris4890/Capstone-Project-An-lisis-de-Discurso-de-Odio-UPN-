# HateDetect: entrega técnica T2 con corpus sintético

Fecha de actualización: 21/10/2026. Base verificada: `main`, commit `f6fe5e7`.
Rama de desarrollo: `codex/fase3-validacion-corpus`. No fusionar sin revisión del usuario.

## Alcance

El solicitante informó que el profesor autorizó datos sintéticos creados por el equipo
para el curso. Se registra esa comunicación; no se inventan nombre, firma, fecha de
aprobación del profesor ni actas. Reddit real, permisos de acceso y evaluación científica
independiente se conservan para el futuro paper, sin bloquear por sí solos T2.

Los 72 ejemplos ya existentes se exportan para revisión. Que el software valide un CSV
no significa que sus etiquetas hayan sido revisadas. El piloto KPI histórico de 30 casos
permanece separado y conserva sus 18 aciertos, 12 errores y 60 % de exactitud.

El ZIP recibido se integró en `preparar_corpus_t2.py`, con su plantilla y correcciones
de fechas, protección de archivos y exclusión KPI. Véase [el procedimiento actualizado](PAQUETE_T2.md).
`synthetic_corpus.py` conserva la exportación minimizada y la validación común.

## Preparar y revisar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m synthetic_corpus exportar --output private/t2_revision_v1
.\.venv\Scripts\python.exe -m synthetic_corpus validar private/t2_revision_v1/corpus_para_anotar.csv --sin-etiquetas
.\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8503
```

La exportación crea:

| Archivo | Uso |
|---|---|
| corpus_para_anotar.csv | 72 textos minimizados, IDs estables y etiquetas vacías; cargar este archivo exacto en la herramienta de anotación. |
| propuestas_generador.csv | Etiquetas originales propuestas, separadas para no mostrarlas al anotador independiente. |
| corpus_exploratorio.csv | Etiquetas del generador; únicamente demostración técnica hasta revisión. |
| plantilla_revision.csv | Hoja de apoyo con evaluador, fecha, motivo y clase vacíos; todos los estados pendientes. No es un importador de decisiones. |
| procedencia.json | Hashes de archivos y generador, conteos, hora real de exportación y revisión pendiente. No contiene autores o revisores inventados. |

Revisar idioma y contenido antes de fijar la versión a anotar. Las comunidades son
escenarios simulados, no publicaciones obtenidas de Reddit ni edades de personas.
La validación acepta `es/en`, tres clases, comunidades del proyecto, IDs únicos,
origen sintético y campos obligatorios. Detecta duplicados normalizados y etiquetas
contradictorias. La detección lingüística y el enmascaramiento no sustituyen revisión humana.

En la herramienta, Jeanpierre (A) y Erick (B) registran clases y motivos de forma
independiente; Crisdel (E3) ve y resuelve exclusivamente desacuerdos. Los códigos quedan
vinculados al hash del corpus, hay progreso individual persistente y Cohen's Kappa se
calcula antes de adjudicar. No copiar propuestas para simular independencia. Las marcas
de tiempo corresponden al registro efectivo. Véase [la guía](guia_evaluadores.md).
Modificar el CSV después cambia su hash: debe fijarse otra versión y revisarla.

## Entrenar y abrir el sistema

Demostración exploratoria, sin revisión acreditada:

```powershell
.\.venv\Scripts\python.exe train_models.py --data private/t2_revision_v1/corpus_exploratorio.csv --synthetic-mode exploratory --output runs/t2_exploratorio_v1 --bootstrap 500
```

Con anotaciones completas del CSV exacto cargado en el panel:

```powershell
.\.venv\Scripts\python.exe train_models.py --data private/t2_revision_v1/corpus_para_anotar.csv --synthetic-mode reviewed --annotation-db private/annotations.sqlite3 --output runs/t2_revisado_v1
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Seleccionar la ejecución nueva en la barra lateral. Probar Clasificación, Reportes e
Historial. El guardado es voluntario. Las ejecuciones exploratorias muestran su alcance.
La identidad de los evaluadores no se autentica; el modo revisado acredita registros
completos en la base local, no aprobación del profesor.

`--include-transformer --epochs 3` incorpora XLM-RoBERTa; requiere descargar el modelo
y recursos adicionales: acceso al checkpoint, conectividad o caché local, memoria y
tiempo de cómputo. La prueba diminuta local de persistencia no equivale a entrenar
ese checkpoint multilingüe sobre el corpus T2. No se sustituyó por BERT inglés ni se
atribuyeron resultados de un modelo a otro.

## Particiones y límites

Se forman train/validation/test por hilo, con las tres clases y balance aproximado.
Los IDs sintéticos son deterministas para que la preparación no cambie las particiones.
TF-IDF se ajusta solo en train; el modelo se elige por Macro-F1 de validation antes de
evaluar test. El Transformer también elige época en validation. No se ajustan reglas
ni hiperparámetros usando los 30 KPI.

El control de coincidencias KPI normaliza Unicode, espacios, datos enmascarados y
mayúsculas. No identifica todas las paráfrasis ni convierte ejemplos conocidos en una
muestra independiente. El corpus pequeño y las etiquetas propuestas limitan las métricas.
Se conserva el clasificador de reglas y sus errores históricos.

## Verificación

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -m integracion -q
.\.venv\Scripts\python.exe -m pytest -m sistema -q
.\.venv\Scripts\python.exe -m pytest tests/test_synthetic_corpus.py -q
```

La suite completa incluye los marcadores; no es necesario ejecutarlos de nuevo para
contar dos veces sus resultados. GitHub Actions ejecuta la suite y el laboratorio.
Ver [resultados](RESULTADOS.md), [matriz funcional](backlog_cumplimiento.md) y
[registro de errores](incidencias.md). `private/` y `runs/` siguen excluidos de Git.
No se publican bases privadas, credenciales, firmas ni registros reales de anotadores.
