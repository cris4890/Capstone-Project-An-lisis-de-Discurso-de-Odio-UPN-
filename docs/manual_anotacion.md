# Manual de anotación versión 1.0

Borrador operativo pendiente de revisión por tres a cinco especialistas. Las etiquetas y ejemplos deben validarse antes de utilizarlos como evidencia de investigación.

## Unidad y contexto

Anotar una publicación o comentario con el contexto mínimo autorizado. El subreddit no demuestra edad, generación ni atributos personales. Si el contexto es insuficiente, no inventar una etiqueta: dejar pendiente y solicitar revisión del responsable del corpus.

## Categorías

- **Odio:** ataque, amenaza, deshumanización o exclusión hacia una persona o grupo por un atributo protegido o socialmente vulnerable. Registrar el grupo o atributo atacado y una justificación.
- **Ofensivo:** insulto o agresión verbal sin fundamento claro en un atributo protegido. Ejemplo: «Eres un idiota».
- **Neutro:** no satisface las condiciones anteriores. Incluye críticas legítimas, menciones identitarias y denuncias del odio. Ejemplo: «Los refugiados merecen respeto».

La presencia de una palabra identitaria no acredita odio. Distinguir las palabras del autor de una cita, su negación o un contraargumento. Examinar sarcasmo, amenazas, términos reapropiados y variantes ortográficas. No atribuir intención cuando no exista evidencia textual suficiente.

## Procedimiento independiente

1. El responsable prepara un corpus minimizado y conserva su versión. Cada hilo recibe un identificador interno aleatorio.
2. Dos evaluadores distintos anotan sin consultar la decisión del otro ni predicciones automáticas. Usan códigos de evaluador, no nombres personales.
3. Ambos registran clase, grupo objetivo cuando corresponde y justificación. La primera decisión no se sobrescribe.
4. Un tercer evaluador adjudica los desacuerdos de clase o grupo objetivo y documenta el motivo. Para cambiar el manual o reanotar, abrir una nueva versión del corpus; conservar la anterior según el protocolo.
5. Calcular kappa sobre los pares anteriores a la adjudicación. Reportar tamaño, distribución y matriz de desacuerdos. Meta operativa: kappa ≥ 0,70. Si no se alcanza, revisar definiciones y repetir piloto; la herramienta no convierte automáticamente el resultado en una aprobación metodológica.
6. Exportar el corpus final solo después de completar dos anotaciones por unidad y resolver desacuerdos.

## Piloto y especialistas

Organizar un piloto de 50–100 unidades o aproximadamente el 10 % si es viable. Medir tiempo de anotación y casos sin contexto. Solicitar a 3–5 especialistas valoraciones de claridad, pertinencia y coherencia; la función `aiken_v` calcula V de Aiken con puntuaciones reales de 1 a 5. Conservar comentarios cualitativos y la versión validada. No rellenar valoraciones o acuerdos ficticios.

## Privacidad y acceso

El enmascaramiento automático no detecta todos los nombres, direcciones o detalles identificables. Revisar los textos antes de su inclusión. Mantener evidencias y base de anotación en `private/`, excluida de Git, con acceso limitado en el sistema operativo. El panel es local y no autentica identidades: no constituye un sistema multiusuario protegido para publicación en Internet.
