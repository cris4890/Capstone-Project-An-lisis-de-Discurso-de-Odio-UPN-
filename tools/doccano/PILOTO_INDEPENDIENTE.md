# Piloto independiente de 50 comentarios

Objetivo: comprobar el procedimiento de anotación y detectar ambigüedades del manual con una muestra sintética. No acredita rendimiento en Reddit, representatividad ni acuerdo humano hasta completar y verificar el proceso.

## Acceso

- Persona A: cuenta `evaluador_a`, proyecto **Independiente 50 v1 - evaluador_a**, http://127.0.0.1:8001/projects/3/dataset
- Persona B: cuenta `evaluador_b`, proyecto **Independiente 50 v1 - evaluador_b**, http://127.0.0.1:8001/projects/4/dataset
- Claves existentes en `private/doccano/accesos.json`. No compartir las claves de las otras cuentas ni la cuenta coordinador con evaluadores. El responsable entrega únicamente la cuenta asignada a cada persona.

La aplicación solo está disponible en este equipo. Pueden usarla por turnos cerrando sesión entre evaluadores. No activar acceso por red como parte de este piloto.

## Antes de empezar

Elegir dos personas distintas y registrar sus códigos, versión del manual y fechas reales de participación en un registro privado. Ambos deben comprender los textos en español e inglés. Leer las instrucciones dentro del proyecto y el manual. No consultar las anotaciones de la otra persona, modelos o soluciones sugeridas.

## En cada comentario

1. Leer el texto sin inferir datos del autor.
2. Seleccionar una categoría del manual: Odio, Ofensivo o Neutro.
3. Registrar un comentario con dos campos: `Objetivo: ...` y `Justificacion: ...`. Usar No aplica si no hay grupo o atributo atacado.
4. Confirmar solo cuando categoría y explicación estén completas.
5. Si falta contexto, registrar la duda y dejar sin confirmar. No forzar el 100 %.

## Al terminar

Avisar cuando ambas personas hayan terminado o registrado sus dudas. La exportación y validación ya están disponibles mediante `./tools/doccano/importar.ps1`: consultan exclusivamente los proyectos del manifiesto `private/doccano/independiente.json` (3 y 4 en este piloto). No usar el exportador de la práctica anterior (`export_pilot.py` usa proyectos 1 y 2). Cada ejecución conserva una instantánea nueva y un informe; ver `docs/doccano_importacion.md`.

Revisar campos vacíos y conservar las decisiones originales. Calcular acuerdo de clases y kappa sobre pares válidos anteriores a adjudicación, reportando tamaño, exclusiones, distribución y matriz de desacuerdos. Comparar también diferencias en el grupo objetivo. La meta del manual es kappa ≥ 0,70, no una garantía ni un resultado ya obtenido.

Un tercer evaluador deberá resolver los desacuerdos y justificar su decisión en una etapa posterior. No corregir las etiquetas originales para aumentar artificialmente el acuerdo. Si se cambia el manual o la muestra, crear una versión nueva.

La muestra y su hash se conservan en private; el generador no proporciona respuestas de referencia. Las 12 anotaciones guiadas previas quedan excluidas de esta evaluación.
