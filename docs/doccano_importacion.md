# Importación y validación de Doccano

Desde la raíz del proyecto, ejecutar en PowerShell:

```powershell
./tools/doccano/importar.ps1
```

El proceso consulta exclusivamente los proyectos del manifiesto `private/doccano/independiente.json`. Conserva cada ejecución en una carpeta nueva bajo `private/doccano/importaciones/`:

- `snapshot.json`: copia de ambas evaluaciones, textos, metadatos, autores, identificadores, marcas temporales, confirmaciones, manifiesto y muestra original.
- `validacion.json`: registros normalizados, incidencias por unidad, resumen y pares disponibles para comparar.
- `informe.md`: resumen legible.

La extracción utiliza el entorno aislado de Doccano. La validación utiliza el entorno del clasificador, sin añadir Django a sus dependencias. No modifica proyectos, etiquetas o comentarios. No escribe en el corpus de entrenamiento ni adjudica decisiones. Las importaciones previas se conservan.

## Controles

Se comprueba el hash y tamaño de la muestra, correspondencia de texto e identificador, pertenencia de evaluador y proyecto, y ausencia de registros duplicados. Cada evaluación necesita una categoría válida, confirmación y un único comentario con Objetivo y Justificación no vacíos. Los comentarios múltiples requieren revisión en lugar de seleccionar el último automáticamente.

Para Odio se señalan objetivos explícitamente no identificados o no aplicables. Es un control de completitud, no una decisión sobre la corrección de la categoría. Una revisión humana debe resolver las interpretaciones. No se reemplazan categorías del evaluador por predicciones.

La asistencia de redacción declarada en los comentarios se conserva y cuenta por separado. La herramienta no puede certificar la independencia de las personas. Las diferencias textuales entre objetivos se listan como candidatas a revisión, no como desacuerdos semánticos confirmados.

## Estado comprobado

Evaluador A: 50 registros, 47 estructuralmente válidos. Una decisión ambigua sin confirmar y dos objetivos sin identificar requieren revisión. Los 50 comentarios incluyen declaración de asistencia de redacción. Evaluador B: 50 unidades todavía sin respuesta en la instantánea verificada. Cero pares válidos para comparar.

El acuerdo y kappa permanecen sin calcular hasta cerrar ambas evaluaciones y revisar las exclusiones y el tipo de asistencia. La aceptación de un registro por este validador no equivale a una etiqueta científica definitiva ni habilita entrenamiento. Las 12 respuestas de práctica anteriores están excluidas.

## Pruebas

Ocho pruebas automatizadas cubren preservación de evidencia, asistencia, hash, duplicados, pertenencia, textos distintos, ausencia del segundo evaluador, objetivos sin resolver, comentarios múltiples y justificación vacía. Ejecutar `python -m pytest -q tests/test_doccano_import.py`.
