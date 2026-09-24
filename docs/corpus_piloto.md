# Corpus de revisión del piloto

El cierre actual resuelve 50 categorías. La exportación de revisión conserva texto, idioma, categoría, motivos originales de A y B y los campos finales adjudicados cuando existen. No convierte coincidencia de categoría en acuerdo de objetivo.

```powershell
python pilot_corpus.py private/doccano/cierres/20260923T001952Z private/doccano/independiente_muestra.jsonl private/doccano/corpus_revision_v1
```

La carpeta de salida debe ser nueva. La ejecución existente está en `private/doccano/corpus_revision_v1` y contiene `corpus_revision.jsonl` y `calidad.json` con hashes. No se modificaron los registros de Doccano ni las evaluaciones originales.

## Resultado

- 50 categorías completas.
- 6 objetivos y motivos finales adjudicados por E3 según confirmación del usuario.
- 44 objetivos finales no ratificados como campo único; se conservan los motivos originales sin seleccionar arbitrariamente uno como definitivo.
- Muestra sintética sin hilos, fechas de publicaciones ni comunidades reales. No se asignan esos metadatos ficticiamente.
- Paquete de revisión no apto para entrenamiento bajo el flujo de investigación actual. No se ha entrenado ningún modelo con estas respuestas.

Para avanzar hacia el corpus final se debe comprobar el acuerdo de objetivos de las 44 unidades, resolver diferencias si existen y aplicar el procedimiento de obtención autorizada a datos reales. Este piloto sirve como evidencia de funcionamiento y aprendizaje del procedimiento.

## Consolidación editorial v2

La revisión de los 44 objetivos no detectó destinatarios incompatibles: 13 coincidencias literales, 30 equivalencias de redacción y una precisión editorial del mismo destinatario. La versión `private/doccano/corpus_revision_v2` incorpora esos objetivos e identifica su origen como normalización asistida, sin atribuirlos a nuevas decisiones independientes de A, B o E3.

Las 50 categorías y objetivos quedan estructurados para la demostración. Los seis casos adjudicados conservan el motivo final de E3; los otros 44 conservan ambos motivos originales y no inventan una justificación conjunta. `objetivos_por_ratificar: 0` en la versión v2 cuenta campos sin estructurar, no certifica una ratificación humana nueva; la procedencia de cada campo se registra por separado.

El paquete se descarga desde Reportes → Anotación y acuerdo. El sistema comprueba que corresponda al cierre seleccionado y que su contenido coincida con el hash registrado. Las restricciones metodológicas para entrenamiento permanecen. El siguiente avance de investigación es definir y conseguir una fuente de datos reales autorizada, no repetir la adjudicación de este piloto.
