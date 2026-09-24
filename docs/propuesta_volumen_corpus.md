# Propuesta de volumen y esfuerzo de anotación

Estado: propuesta de 1.770 registros descartada por carga de trabajo. Se conserva como antecedente, no como plan vigente. El usuario acordó planificar aproximadamente 768 registros de referencia de PC4 y una semana de anotación independiente por A/B, más adjudicación y revisión. El tamaño definitivo depende de la población accesible. Entrega: 2 de diciembre de 2026.

## Lo establecido y lo propuesto

PC4 propone aproximadamente 384 unidades por comunidad para la muestra probabilística y permite ampliar el corpus de desarrollo. No fija un número adicional para entrenamiento. El redondeo superior del límite de su fórmula es 385 por comunidad; el valor definitivo se recalcula con la población accesible.

Propuesta de planificación: hasta 1.770 registros únicos anotados, distribuidos así:

| Uso | r/Millennials | r/GenZ | Total de referencia |
|---|---:|---:|---:|
| Muestra probabilística reservada para evaluación final y comparación descriptiva | 385 | 385 | 770 |
| Desarrollo: entrenamiento y validación | 500 | 500 | 1.000 |
| Total | 885 | 885 | 1.770 |

Las cuotas de desarrollo son objetivos de planificación, sujetos a disponibilidad y permisos. No son un mínimo científico demostrado. No se fijan cuotas artificiales iguales por idioma o etiqueta: contar primero su disponibilidad. Una eventual ampliación dirigida para clases minoritarias pertenece al desarrollo; no debe alterar las proporciones de la muestra probabilística.

Este volumen es el de textos seleccionados para anotar, no un límite ya establecido de filas consultadas en la plataforma. La solicitud debe distinguir el conteo del marco accesible de la exportación mínima necesaria para anotación.

## Separación propuesta y decisión metodológica pendiente

Propuesta: reservar los 770 registros de referencia para evaluación final, y repartir los 1.000 de desarrollo en aproximadamente 800 para entrenamiento y 200 para validación. Mantener todos los registros de un hilo en un solo conjunto. El marco de desarrollo excluirá los hilos seleccionados para evaluación; documentar el procedimiento y sus efectos sobre la cobertura. La selección probabilística requiere conservar probabilidades de inclusión y ponderaciones cuando corresponda.

Esta separación difiere del 70/15/15 propuesto en PC4 y necesita aceptación y actualización metodológica explícitas antes de aplicarse. No se modifica el código de partición ni PC4 con este documento. Los tamaños son aproximados porque se respetarán los grupos por hilo. Si se conserva 70/15/15, habrá que definir por separado qué muestra sustenta las estimaciones descriptivas y qué subconjunto queda intacto para prueba; no presentar todo el corpus como prueba independiente.

No consultar etiquetas ni resultados de prueba para elegir modelos, ampliar clases o ajustar hiperparámetros. La suficiencia del desarrollo se examinará con validación, distribución de clases/idiomas y evolución del desempeño al aumentar datos de entrenamiento. No se garantiza desempeño adecuado de modelos clásicos o Transformer por alcanzar esta cantidad.

## Esfuerzo calculado

Supuesto de planificación, por medir con textos reales autorizados: entre uno y dos minutos por registro para leer, seleccionar clase, identificar objetivo y escribir motivo.

- Cada evaluador A/B: 1.770 decisiones; aproximadamente 29,5–59 horas.
- A y B juntos: 3.540 decisiones; aproximadamente 59–118 horas.
- Repartido en cuatro semanas de anotación: aproximadamente 7,4–14,8 horas semanales por evaluador.
- E3: carga adicional variable por desacuerdos y casos ambiguos; no está incluida en las cifras anteriores. Tampoco incluyen preparación, pausas ni correcciones de calidad.

El piloto sintético asistido no permite asumir ese ritmo para textos reales. Medir primero el tiempo con un lote de desarrollo de 50–100 textos autorizados, sin tocar la muestra final. Si el ritmo, las autorizaciones o el calendario no permiten completar el volumen, revisar el alcance con el asesor y declarar sus límites.

## Siguiente decisión

Confirmar si A y B pueden dedicar aproximadamente 8–15 horas semanales durante cuatro semanas a la anotación. El tiempo disponible después de obtener acceso puede ser menor. Hasta confirmar capacidad y diseño, mantener esta cantidad como propuesta y no como compromiso en una solicitud enviada.
