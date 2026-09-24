# Revisión funcional previa al corpus real

## Resultado

Los flujos verificados de Clasificación, Reportes e Historial funcionan con datos sintéticos. Esto acredita funcionamiento del prototipo, no precisión ni validez científica sobre Reddit real.

## Comprobaciones

- Suite existente: 40 pruebas aprobadas. Incluye minimización, procedencia, separación por hilo, selección por validación, anotación y adjudicación, historial opcional, respaldo/restauración y prueba técnica de un Transformer local diminuto.
- Dos pruebas de regresión nuevas aprobadas individualmente: historial dañado sin sobrescribir evidencia; ejecución JSON inválida con recuperación hacia la demostración.
- Comprobación adicional con Streamlit AppTest sobre sprint1_entrega: carga del modelo seleccionado, clasificación, tres pestañas de Reportes, filtro de comunidad y búsqueda sin resultados, sin excepciones.
- El historial de pruebas usa archivos temporales; no se modificaron las anotaciones de Doccano ni se entrenaron nuevos modelos.

## Correcciones

El historial ahora muestra un aviso controlado si no puede leerse la base, conservando el archivo original. Una ejecución con JSON ilegible u origen desconocido muestra un aviso y permite seleccionar otra ejecución. Esta comprobación no constituye validación exhaustiva del esquema de todos los artefactos de una ejecución.

## Límites y pendientes

La primera revisión utilizó AppTest. Posteriormente se inspeccionaron en navegador integrado, a 1280 × 720 y tema oscuro: Clasificación con resultado Neutro, Evaluación de modelos de sprint1_entrega, Exploración del corpus, Anotación y acuerdo e Historial vacío. Las tarjetas de resultados son legibles y no reproducen el problema previo de texto claro sobre fondo blanco. El historial con registros sigue respaldado por las pruebas automatizadas; no se guardaron registros de prueba en el historial del usuario durante la inspección visual. No se verificaron en esta inspección tema claro ni pantalla móvil.

Mejora pendiente de presentación: sustituir encabezados técnicos en inglés de las tablas de evaluación por etiquetas comprensibles en español. La tabla de métricas requiere desplazamiento horizontal en el ancho inspeccionado.

La ejecución sintética no incluye el entrenamiento completo del Transformer previsto en PC4. El corpus autorizado, la evaluación bilingüe real y las comparaciones entre comunidades siguen pendientes de permisos y datos. Los UUID y el enmascaramiento automático no garantizan anonimización completa del texto libre.

El piloto de 50 textos sigue siendo sintético, con asistencia documentada. No se ha convertido en corpus real ni incorporado automáticamente al entrenamiento.

## Continuación: recorrido funcional y errores de las reglas

Dos pruebas adicionales aprobadas en tests/test_functional_journey.py: entrada vacía sin guardado, clasificación y guardado voluntario, búsqueda y filtro de categoría sin alterar registros, filtros combinados de comunidad e idioma y búsqueda literal sin resultados. Se utilizó un historial temporal; no se alteró el historial del usuario. El navegador integrado no estuvo disponible durante esta continuación, por lo que estas comprobaciones se realizaron con AppTest.

Se reprodujeron cuatro casos sintéticos de diagnóstico. Resultado: la exclusión religiosa «las personas de religion catolica no deben opinar» produjo Neutro, aunque el manual la encuadra como Odio; «Los refugiados merecen respeto» produjo Odio, aunque corresponde Neutro. «Eres un idiota» produjo Ofensivo y el agradecimiento produjo Neutro. No es una muestra representativa ni una métrica de desempeño. Evidencia local: private/verificacion_funcional/casos_reglas.json.

La interfaz funciona en estos recorridos, pero la línea base tiene errores semánticos tanto de omisión como de falsa alarma. La detección por palabras aisladas no implementa adecuadamente el criterio de contexto del manual. No se modificaron las reglas ni las métricas históricas en esta comprobación. Una revisión de reglas debe versionarse y evaluarse con casos de negación, citas, menciones neutrales y ataques, preservando las ejecuciones anteriores.

Actualización posterior: se implementó la versión 2 en context_rules.py, integrada en la demostración y nuevas ejecuciones. Corrige los dos casos diagnosticados y conserva la clase histórica. Suite: 74 pruebas aprobadas; comparación funcional local: 19/24 aciertos frente a 11/24 anteriores, con cinco errores pendientes. Véase reglas_contexto_v2.md para límites y evidencia.
