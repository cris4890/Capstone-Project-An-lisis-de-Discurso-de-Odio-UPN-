# Reglas de contexto v2

La demostración y las nuevas ejecuciones usan ContextRuleBasedClassifier, versión 2.0. RuleBasedClassifier se conserva sin cambios: las ejecuciones antiguas y sus métricas no se actualizan retrospectivamente. Seleccionar sprint1_entrega sigue cargando su modelo histórico; para probar v2, seleccionar Demostración de reglas.

## Cambios

Las menciones de grupos por sí solas ya no activan Odio. Se reconocen patrones limitados de exclusión, deshumanización y violencia vinculados con ciertos grupos en español e inglés. Se contemplan negaciones explícitas, algunas citas denunciadas y separación entre oraciones o cláusulas de contraste. Los insultos sin ataque identitario reconocido se clasifican como Ofensivo.

Casos corregidos: «las personas de religion catolica no deben opinar» → Odio; «Los refugiados merecen respeto» → Neutro. Los tests incluyen variantes de negación, citas y un segundo ataque después de una frase neutral o de denuncia.

## Alcance de la evidencia

Los casos de regresión se utilizan para desarrollar estas reglas; no son una evaluación independiente. No acreditan precisión sobre Reddit ni comprensión general del lenguaje. Las reglas tienen vocabulario y estructuras acotados; pueden omitir ataques o malinterpretar citas y negaciones complejas. La etiqueta Neutro puede significar ausencia de un patrón reconocido, no garantía de ausencia de odio. Se mantiene la revisión humana y no se genera un porcentaje de confianza.

Los artefactos históricos se conservaron. Esta mejora no entrena el Transformer, no utiliza datos reales y no reetiqueta las respuestas de los evaluadores.

## Verificación realizada

Suite completa: 74 pruebas aprobadas. En los 24 ejemplos preexistentes de tests/functional_cases.csv, la versión histórica acertó 11 y v2 acertó 19. Es una comprobación funcional local, no una estimación de desempeño real ni un conjunto de prueba independiente acreditado. Comparación conservada en private/verificacion_funcional/comparacion_reglas_v2.csv.

Persisten cinco errores: denuncia sin comillas («Decir que los inmigrantes son una plaga es racista»), dos exclusiones de alquiler por etnia y dos ataques con ortografía deliberadamente alterada. Deben conservarse como limitaciones abiertas; no presentar la suite de regresión aprobada como ausencia de errores semánticos.
