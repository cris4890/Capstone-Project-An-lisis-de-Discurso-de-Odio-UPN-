# Reporte del piloto de anotación

En la aplicación principal, abrir **Reportes → Anotación y acuerdo**. Se mantienen los tres subsistemas; esta vista es parte de Reportes.

La vista carga cierres locales de `private/doccano/cierres/`, verifica los hashes de los archivos y busca la comparación original mediante el hash registrado en la adjudicación. Si la comparación no está disponible, no muestra sus métricas. Si faltan todos los cierres, muestra un estado vacío.

El piloto actual contiene 50 categorías finales: 27 Neutro, 10 Ofensivo y 13 Odio. Se resolvieron 44 unidades por coincidencia de categorías originales y seis por adjudicación reportada de E3, con fecha comunicada del 22 de septiembre de 2026.

El acuerdo inicial usa 49 pares: 44 coincidencias, 5 desacuerdos y kappa 0,828791. La respuesta inicialmente ambigua se excluye. Las revisiones posteriores no se usan para recalcular ese indicador.

Los textos son sintéticos. Se conserva la asistencia en redacción y estructuración de objetivos; identidad e independencia de los participantes no están autenticadas por el sistema. Los objetivos de las 44 coincidencias no se consideran adjudicados por el mero acuerdo de categorías.

La descarga JSONL conserva las decisiones originales y la adjudicación de cada caso cuando existe. Esta vista es de consulta: no modifica Doccano, no envía información a terceros y no inicia entrenamiento. Los archivos privados no se incluyen automáticamente en el repositorio.
