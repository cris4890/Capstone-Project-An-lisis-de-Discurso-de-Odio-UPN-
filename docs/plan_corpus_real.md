# Preparación del corpus real de las dos comunidades

Estado: plan de trabajo; no acredita acceso concedido ni recolección realizada. Revisión: 23 de septiembre de 2026.

## Alcance respaldado por los documentos

PC4, delimitación y sección 3.6, establece r/Millennials y r/GenZ, publicaciones y comentarios en español e inglés, y un intervalo autorizado dentro de 2025–2026. No fija fechas exactas. S3 mantiene ese alcance y condiciona la extracción a autorización; S5 no establece otro tamaño de muestra. El Plan de Gestión, páginas 4–5, mantiene ambas comunidades y la anotación doble.

Los 50 registros sintéticos ya anotados sirven para probar el flujo. No sustituyen una muestra real ni deben atribuirse a estas comunidades.

## Tamaño y diseño

PC4 propone confianza del 95 %, p=0.50 y error de 0.05, con referencia aproximada de 384 unidades por comunidad (768 en total). Para cada comunidad, una vez conocido su número de registros elegibles N:

`n = techo(N * 1.96² * 0.5 * 0.5 / (0.05² * (N - 1) + 1.96² * 0.5 * 0.5))`

Corrección de precisión: el límite para población muy grande es 384.16; redondeado hacia arriba da 385 por comunidad, 770 en total. Mantener 384 como aproximación del documento, no como mínimo exacto universal. La fórmula dimensiona una estimación de proporciones bajo sus supuestos; no garantiza suficientes ejemplos de odio ni precisión del clasificador, y la dependencia entre comentarios de un hilo requiere atención adicional.

Propuesta de ejecución:

1. Delimitar una misma ventana temporal disponible para ambas comunidades, dentro de 2025–2026. Registrar la versión de datos, consulta y exclusiones.
2. Contar la población accesible elegible por comunidad, idioma, tipo de contenido y periodo. Excluir eliminados, duplicados y textos no utilizables; documentar cada criterio.
3. Calcular n por comunidad. Distribuir la muestra dentro de cada comunidad por idioma y, si procede, periodo, registrando probabilidades de inclusión y semilla. No inventar registros en español si su disponibilidad es baja; informar la limitación y acordar cualquier ajuste metodológico.
4. Mantener separada la muestra probabilística para comparaciones descriptivas del corpus ampliado para desarrollo. Si se toman cantidades iguales por comunidad, una estimación conjunta requiere ponderar por las poblaciones correspondientes.
5. Realizar anotación independiente A/B con etiqueta, objetivo y motivo; calcular kappa antes de adjudicar. Resolver desacuerdos con E3 conservando los originales. El piloto sintético asistido no demuestra concordancia sobre contenido real.
6. Separar entrenamiento, validación y prueba por hilo, sin filtraciones entre conjuntos. Seleccionar modelos con validación; consultar prueba solo al cierre. Balancear únicamente entrenamiento. Reservar suficientes casos de prueba; los 770 de referencia no son automáticamente 770 casos de prueba si se reparten entre conjuntos.

## Ruta de acceso y efecto sobre la implementación

El programa oficial RFR describe acceso mediante BigQuery Analytics Hub, con datos históricos y un retraso de seis meses. Por eso no se debe dar por hecho que PRAW será la vía ni que todo 2026 estará disponible. La ventana exacta dependerá de la versión autorizada. El adaptador de entrada debe implementarse cuando se conozcan el esquema y los permisos concedidos. [Programa RFR](https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program).

La solicitud necesita correo institucional, patrocinador universitario y aprobación ética o exención. Cada persona que acceda a datos fuente debe solicitar acceso individual. La exportación a Doccano y el tratamiento local deben consultarse expresamente. [Programa RFR](https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program).

El uso para entrenamiento necesita aprobación expresa; no basta crear credenciales. Debe abarcar los modelos previstos y los resultados que se desea conservar. [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy).

## Datos mínimos y seguridad propuesta

Conservar solo texto necesario, comunidad, idioma, tipo de contenido, fecha necesaria para el periodo y UUID de unidad/hilo. No guardar nombres de usuarios ni inferir edades. Los UUID no impiden que un texto literal sea localizable: aplicar revisión de datos personales y restringir el acceso al texto.

Mantener la trazabilidad necesaria para actualizar eliminaciones en un entorno restringido y solo si está autorizada. No publicar el corpus, credenciales ni citas identificables. Acordar fecha de eliminación y tratamiento de derivados con la institución y Reddit; actualizar consultas antes de publicar y documentar las eliminaciones. [Programa RFR](https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program).

## Datos acordados el 23 de septiembre de 2026

- Solicitante: Jeanpierre Amilcar Casimiro Guerra; correo institucional registrado en el borrador de solicitud.
- Evaluador A: Jeanpierre Amilcar Casimiro Guerra.
- Evaluador B: Erick Daniel Carbajal Quiñonez; [correo institucional en copia privada].
- Adjudicador E3: Crisdel Aldemir Gonzales Canales; [correo institucional en copia privada].
- Correos de B y E3 completados con los códigos proporcionados por el usuario y el dominio institucional previamente indicado (@upn.pe); no se ha verificado su funcionamiento.
- Asignación confirmada por el usuario para el corpus real. A y B anotarán independientemente; E3 resolverá desacuerdos con motivo documentado. Esta asignación no modifica retrospectivamente la autoría registrada del piloto.
- Periodo solicitado de publicaciones: 1 de enero–31 de diciembre de 2025, sujeto a disponibilidad y autorización.
- Planificación del trabajo restante: desde el 23 de septiembre de 2026; entrega el 2 de diciembre de 2026, según la corrección más reciente del usuario. El plazo desde el 23 de septiembre es de diez semanas.
- Punto de revisión de viabilidad: 6 de octubre. Si el acceso sigue pendiente, revisar el alcance con el asesor sin presentar datos sintéticos como resultados reales.
- Profesor patrocinador: por confirmar.
- Acceso a datos fuente: únicamente Jeanpierre, Erick y Crisdel, condicionado a sus permisos individuales.
- Acceso solicitado: tan pronto se autorice; la urgencia no fija una fecha garantizada de concesión.
- Conservación: eliminación como máximo el 30 de diciembre de 2026, según indicación del usuario. Eliminar antes si los datos dejan de ser necesarios o el permiso impone un plazo menor. Después de la entrega del 2 de diciembre, conservar únicamente mientras exista una necesidad académica justificada y permitida.
- La eliminación abarcará originales, exportaciones, texto en Doccano, respaldos y temporales bajo control del equipo. Revisar anotaciones y modelos derivados según el permiso; no asumir conservación autorizada. Conservar únicamente código sin datos reales, ejemplos sintéticos e informes agregados no identificables permitidos, junto con registro de eliminación sin texto fuente. Este es un compromiso documentado, no una eliminación ejecutada ni programada automáticamente.

## Información por confirmar antes de solicitar

- Docente patrocinador y correo institucional.
- Documento de aprobación ética o exención emitido por la instancia competente.
- Evaluar con los datos accesibles si se necesita ampliar el desarrollo. Por ahora se planifica la referencia de aproximadamente 768 registros de PC4, sin comprometer la ampliación a 1.770. Una semana para anotación independiente A/B (unos 110 registros diarios por persona), más tiempo de adjudicación y revisión; medir el esfuerzo real al comenzar.

Con esos datos se completa el borrador asociado. Si el acceso o entrenamiento no se autorizan, una fuente alternativa exige revisar formalmente el alcance; no se reemplazan silenciosamente las dos comunidades.

## Aclaración sobre entrenamiento

PC4 define una referencia aproximada de 768 unidades para la muestra probabilística y propone una partición por hilo de 70 % entrenamiento, 15 % validación y 15 % prueba. Si se aplicara a 768 registros sin ampliación, serían aproximadamente 538, 115 y 115, respectivamente; los tamaños exactos dependen de los grupos por hilo. El documento permite ampliar el corpus de desarrollo, pero no fija una cantidad adicional. La suficiencia para entrenar no está demostrada por la fórmula de muestreo: debe evaluarse con la distribución de etiquetas e idiomas, errores y resultados de validación, sin usar la prueba para decidir ampliaciones.
