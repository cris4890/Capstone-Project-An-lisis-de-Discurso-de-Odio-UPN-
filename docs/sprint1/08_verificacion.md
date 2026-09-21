# Verificación del incremento

Resultado: **23 pruebas, 0 fallos y 0 errores**. Tiempo de suite: 18.352 segundos. No representa horas de trabajo del equipo.

## Evidencia

- `evidencias/pruebas.xml`: resultado automatizado.
- `evidencias/resumen_pruebas.json`: resumen y hora de verificación.
- `evidencias/experimento_sintetico.json`: metadatos y métricas sin textos del corpus.
- `evidencias/repositorio.json`: rama y estado local de referencia.

## Funciones verificadas

Navegación de tres subsistemas, guardado voluntario, minimización y persistencia del Historial, herramienta de anotación separada, métricas y reportes de una ejecución guardada, particiones por hilo, reglas de anotación, carga de artefactos, respaldo/restauración y configuración local.

La prueba de Transformer entrena una arquitectura diminuta inicializada localmente. No acredita ajuste fino ni calidad de XLM-RoBERTa sobre datos reales.

## Ejecución demostrativa

Corpus sintético de 72 registros. Particiones: {'train': 50, 'validation': 11, 'test': 11}. Selección mediante `validation_macro_f1`. Transformer incluido: no.

| Modelo | Macro-F1 de validación | Macro-F1 de prueba |
|---|---:|---:|
| Línea base de reglas | 1.0000 | 1.0000 |
| TF-IDF + LogisticRegression | 0.6190 | 0.9153 |
| TF-IDF + LinearSVC | 0.6190 | 0.9153 |

Los resultados describen esta muestra sintética pequeña. No permiten estimar prevalencia, superioridad general ni desempeño real en Reddit. Las pruebas funcionales conservan fallos conocidos de las reglas.

## Cierre

Incremento técnicamente verificado para demostración local. Review, aprobación del equipo/docente y entrega académica continúan pendientes. Publicación en GitHub y controles remotos no se acreditan mediante pruebas locales.
