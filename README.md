# Clasificación de discurso de odio en comunidades de Reddit

Prototipo académico de apoyo a revisión humana para el PC4 UPN. Clasifica Odio, Ofensivo y Neutro; compara modelos y registra anotaciones. El corpus incluido es sintético: no acredita resultados sobre Reddit real ni prevalencia por generaciones.

## Entrega del Sprint 1

[Paquete de entrega y evidencias](docs/sprint1/README.md): plan de desarrollo, Scrum, backlog, DoD, ramas, seguridad y guía del incremento. Periodo 14–20 de septiembre de 2026; fecha académica pendiente.

## Instalación y pruebas

En Windows, desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

El panel usa únicamente ejecuciones completas. Si no se selecciona ninguna, permite una demostración explícita de reglas, con limitaciones de contexto. Nunca reemplaza silenciosamente un modelo faltante por otro.

## Tres subsistemas y herramienta interna

El sistema principal tiene Clasificación, Reportes e Historial. Reportes contiene evaluación y exploración del corpus. Guardar en Historial está desactivado inicialmente; al activarlo se conserva el texto procesado, fecha, modelo, categoría, tiempo y probabilidad cuando existe en `private/history.sqlite3`. Los registros persisten al reiniciar. No hay aislamiento por usuario ni cifrado; revisar datos personales antes de guardar y mantener uso local.

Anotación es auxiliar del equipo, fuera de la navegación principal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8502
```

Esta separación no equivale a autenticación.

## Ejecución local de demostración

```powershell
.\.venv\Scripts\python.exe train_models.py
```

Entrena reglas, regresión logística y SVM sobre 72 ejemplos sintéticos, en una carpeta nueva dentro de `runs/`. Selecciona por validación antes de evaluar prueba. Guarda el corpus minimizado, particiones por hilo, modelos, predicciones, errores, métricas por clase y subgrupo, intervalos bootstrap, matrices, casos funcionales y versiones del entorno.

La separación busca 70/15/15 aproximadamente, con hilos indivisibles y presencia de las tres clases. No estima prevalencia y puede rechazar corpus con pocos hilos por clase.

Para incluir el Transformer multilingüe:

```powershell
.\.venv\Scripts\python.exe train_models.py --include-transformer --epochs 3
```

Esta opción descarga XLM-RoBERTa y requiere recursos de entrenamiento considerablemente mayores. El checkpoint se guarda con su tokenizador y metadatos; el panel lo carga exclusivamente desde esa carpeta local. La prueba automatizada usa una arquitectura diminuta inicializada localmente para verificar el ajuste y la persistencia: no demuestra calidad del modelo multilingüe real.

## Datos reales y anotación

1. Obtener y revisar la autorización o licencia antes de adquirir datos. Este repositorio no extrae datos de Reddit.
2. Guardar entrada y evidencia en `private/`. Preparar un manifiesto a partir de `docs/procedencia.example.json` con valores reales.
3. Importar el corpus a una ruta nueva:

```powershell
.\.venv\Scripts\python.exe corpus.py private/entrada.csv private/corpus_v1.csv --manifest private/procedencia.json
```

La entrada requiere `subreddit`, `id_hilo`, `tipo_contenido`, `origen` y `texto_original` o `texto_limpio`; para datos reales también `fecha`. Orígenes: `reddit_autorizado`, `licenciado` o `sintetico`. Se generan identificadores internos y se conservan solo campos permitidos. Para un corpus de otro dominio, revisar antes la delimitación del proyecto.

4. Resolver casos marcados `revision_idioma`, documentar quién revisó idioma y privacidad y fijar esa versión del archivo antes de anotar. El enmascaramiento automático no garantiza anonimato.
5. Abrir la herramienta interna `annotation_app.py` y cargar **exactamente ese archivo** en Anotación. Dos evaluadores trabajan de manera independiente; un tercero adjudica. El registro se guarda en `private/annotations.sqlite3`. Consultar `docs/manual_anotacion.md`.
6. Entrenar con el mismo archivo original que se cargó para anotar (su hash identifica las anotaciones, no utilizar el CSV exportado con otro hash):

```powershell
.\.venv\Scripts\python.exe train_models.py --data private/corpus_v1.csv --manifest private/procedencia.json --annotation-db private/annotations.sqlite3 --include-transformer
```

El entrenamiento recupera las etiquetas finales de la base de anotación. El registro de autorización es una comprobación documental, no una verificación jurídica. No publicar este panel con datos restringidos: está previsto para uso local y no autentica códigos de evaluador.

## Archivos y evidencia

- `corpus.py`: validación, detección de idioma y minimización.
- `annotations.py`: anotación, adjudicación, kappa y V de Aiken.
- `experiment.py`: particiones, métricas, bootstrap y subgrupos.
- `train_models.py`: ejecuciones independientes y selección por validación.
- `model_registry.py`: carga explícita de artefactos.
- `app.py`: Clasificación, Reportes (incluye corpus) e Historial.
- `annotation_app.py`: herramienta interna de anotación separada.
- `history_store.py`: historial local de consultas guardadas voluntariamente.
- `maintenance.py`: respaldo y restauración verificables de SQLite.
- `tests/`: pruebas automatizadas y casos funcionales propuestos.
- `docs/cumplimiento_pc4.md`: requisitos implementados y evidencia pendiente.

Los resultados históricos se mantienen en sus carpetas anteriores; no son la evidencia de una nueva evaluación. `runs/` y `private/` están excluidos de Git. Cada ejecución registra `requirements.lock.txt`; instalarlo en un entorno compatible permite recuperar las versiones probadas.

## Referencias de implementación

- [XLM-RoBERTa](https://huggingface.co/FacebookAI/xlm-roberta-base)
- [Persistencia de modelos Transformers](https://huggingface.co/docs/transformers/main_classes/model)

La inclusión de herramientas no sustituye la autorización, el muestreo probabilístico, la anotación humana, el juicio de especialistas o la validación experimental establecidos en el Word.
