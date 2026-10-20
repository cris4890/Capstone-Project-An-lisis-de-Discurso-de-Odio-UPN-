# Borrador para incorporar al informe

## VII Resultados evaluación operativa y económica

La ficha KPI-PILOTO-001 del 4 de octubre de 2026 contiene 30 textos sintéticos, la clasificación manual y una clave de referencia. El registro manual suma 203,84 segundos, con 28 aciertos y 2 errores: 93,33 % de exactitud. Su tiempo medio es 6,795 segundos y ocho casos se completaron dentro de 60 segundos acumulados. La clave se utiliza como referencia de trabajo; no se acredita independencia de su elaboración ni cegamiento del evaluador.

En la repetición del 19 de octubre de 2026, las reglas v2 de HateDetect acertaron 18 casos y fallaron 12, igual que el registro histórico. Los diez casos de Odio fueron clasificados Neutro, por lo que el recall de Odio es 0 %. Dos casos Ofensivos, T014 y T029, también se clasificaron Neutro. Los diez textos Neutros coincidieron con la referencia. Esta muestra es balanceada por diseño y no representa prevalencia ni distribución real de Reddit.

La medición E2E del navegador comprendió el clic de envío, el procesamiento y la aparición del resultado, con dos frames como aproximación a su renderizado. Las 30 ventanas sumaron 8,407 segundos, con media de 0,280 segundos. No incluyen ingreso del texto, revisión humana, intervalos entre envíos ni guardado. La capacidad derivada de esas ventanas, 214,11 textos por minuto, y la cobertura acumulada de 30/30 no acreditan productividad integral frente al proceso manual. No se infiere ahorro salarial, retorno de inversión ni superioridad operativa causal.

La auditoría detectó 12 discrepancias entre las columnas D y J de la hoja Prueba HateDetect. El resumen del archivo original referencia D, que coincide con la clave; J coincide con el registro original de predicciones. El anexo conserva ambas columnas y emplea salidas verificadas, evitando reportar un 100 % artificial. El archivo original se conserva sin modificaciones y con hash de procedencia.

La suite vigente obtuvo 105 casos aprobados: 77 unitarios, 21 de integración y 7 de sistema mediante AppTest. Se verificaron además treinta envíos y un guardado en el navegador real. Ninguno de estos resultados sustituye la aceptación formal de los participantes en una Review. El crecimiento desde las 74 pruebas históricas refleja cambios del laboratorio y dos comprobaciones de activación de la instrumentación.

Las principales limitaciones son el tamaño pequeño, el carácter sintético, una única repetición por texto, el conocimiento previo de los casos, la ausencia de una referencia independiente, un único entorno local y límites temporales distintos para manual y sistema. Los intervalos entre envíos incluyen pausas de inspección, por lo que no se emplean como una sesión continua de productividad. Antes de conclusiones científicas se requiere corpus autorizado, anotación independiente, conjunto reservado y entrenamiento definitivo del Transformer y demás candidatos.

## VIII Conclusiones y trabajo pendiente

HateDetect demuestra un recorrido funcional de clasificación, guardado voluntario, historial y reportes. La calidad predictiva del piloto es insuficiente para automatizar decisiones: los falsos negativos de odio siguen abiertos. La verificación técnica del producto y la validación científica se reportan por separado.

Se recomienda corregir los defectos con regresiones explícitas, evitando adaptar la evaluación final a los treinta textos conocidos. Deben completarse autorización y anotación del corpus real, comparación reservada de modelos, medición operativa equivalente, controles de producción y aceptación formal. No se asigna 100 % de avance ni un porcentaje global sin denominador trazable.

## IX Compromiso ético

El equipo se compromete a utilizar únicamente datos autorizados o licenciados para la finalidad declarada. Los ejemplos de esta entrega son sintéticos. La disponibilidad pública de contenido no se toma como autorización automática para cualquier uso. Las condiciones de acceso, entrenamiento, redistribución y conservación se verificarán antes de incorporar un corpus real.

La privacidad exige minimizar los campos, enmascarar identificadores directos y revisar la identificación indirecta por contexto. Las inferencias del historial no se convierten en etiquetas validadas. El código compartido no debe contener credenciales ni bases privadas. La eliminación acordada es el 30 de diciembre de 2026, incluyendo copias y derivados sujetos a conservación; cualquier plazo más restrictivo de la autorización aplicable debe respetarse.

Se documentarán sesgos por idioma, comunidad, clase y expresión. Pertenecer a r/Millennials o r/GenZ no demuestra edad o identidad generacional. Los modelos pueden confundir negaciones, citas, ironía y expresiones identitarias; las métricas agregadas se acompañarán de resultados por clase y ejemplos de error.

Las salidas apoyan la revisión humana y no producen sanciones automáticas. Los falsos positivos pueden atribuir injustamente odio a una expresión; los falsos negativos pueden dejar pasar ataques. El equipo mantendrá un registro de incidencias, una vía de revisión y trazabilidad de correcciones. La responsabilidad por las decisiones permanece en las personas que revisan el contexto.

La comunicación de resultados distinguirá observaciones, supuestos, simulaciones y evidencia pendiente. Se conservará el hallazgo del 60 % y el recall de Odio de 0 %, sin sustituir errores por etiquetas esperadas. No se afirmará aprobación ética institucional, revisión de especialistas o aceptación académica hasta disponer de evidencia. Este texto es un compromiso propuesto para ratificación del equipo, no una constancia de aprobación externa.

## X Referencias

Mantener las referencias del informe base y las fuentes de datos del anexo. No se han incorporado referencias bibliográficas inventadas.

## XI Anexos

Anexo KPI con treinta textos, clave, manual, salidas originales, repetición y tiempos E2E; matriz de confusión; inventario y JUnit de pruebas; trazabilidad; incidencias y riesgos; protocolo E2E; Review preparada; capturas reales; versión y hashes. La copia original del Excel se conserva de forma privada.
