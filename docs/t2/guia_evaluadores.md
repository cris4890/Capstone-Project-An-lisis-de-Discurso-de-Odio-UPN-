# Guía de revisión humana del corpus sintético

Esta guía prepara el trabajo; no afirma que Jeanpierre, Erick o Crisdel ya hayan
anotado, aprobado o adjudicado ejemplos. La base se guarda únicamente en
`private/annotations.sqlite3`, excluida de Git.

## Inicio

```powershell
.\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8503
```

Cargar `docs/t2/corpus_72/corpus_para_anotar.csv`. El archivo contiene 72 textos
y no muestra las propuestas del generador. No cargar `corpus_exploratorio.csv`.
Cada persona debe conservar su código privado y usar siempre el mismo:

- rol A: Jeanpierre;
- rol B: Erick;
- rol E3: Crisdel, exclusivamente para adjudicación.

Los códigos identifican registros locales, pero no autentican legalmente a la
persona. El primer código usado en cada rol queda vinculado al hash exacto del
CSV y no puede sustituirse desde el panel.

## Evaluadores A y B

1. Elegir el rol propio e ingresar el código correspondiente.
2. Revisar ID, idioma y texto sin consultar `propuestas_generador.csv` ni las
   respuestas de la otra persona.
3. Seleccionar Odio, Ofensivo o Neutro. Para Odio, registrar el grupo o atributo
   objetivo. Escribir siempre una justificación concreta.
4. Guardar. Una decisión guardada no se sobrescribe.
5. Usar la barra y los contadores para continuar hasta 72/72. Al volver a abrir
   el panel con el mismo CSV y código, sólo aparecerán los pendientes.
6. Cuando el contador marque 72/72, abrir **Acuerdo y exportación** y descargar
   el paquete individual JSON. El paquete contiene el rol, un identificador
   seudónimo, el hash del corpus, IDs, etiquetas, grupos, justificaciones,
   versión del manual y fechas. No contiene el código privado ni los textos.
   El seudónimo se genera aleatoriamente una sola vez, se guarda sólo en la base
   local y se reutiliza para ese evaluador, rol y corpus; no se deriva del código.

La concordancia, matriz y distribuciones de etiquetas permanecen ocultas para A
y B mientras cualquiera tenga unidades pendientes. Se habilitan para ambos sólo
después de completar las dos revisiones, para no condicionar decisiones.

## Trabajo desde dos computadoras

Jeanpierre y Erick deben usar una copia local de la aplicación y del mismo CSV;
cada computadora conserva su propia `private/annotations.sqlite3`. No se debe
sincronizar una base SQLite mediante OneDrive, Google Drive, carpetas de red u
otro mecanismo de escritura compartida.

1. Confirmar por un canal humano que Jeanpierre trabaja como A y Erick como B.
2. Comparar en ambas computadoras el SHA-256 del CSV:

   ```powershell
   (Get-FileHash -Algorithm SHA256 docs/t2/corpus_72/corpus_para_anotar.csv).Hash
   ```

3. Cada persona completa 72/72 y entrega únicamente su paquete JSON por el medio
   privado acordado. Debe conservar su base local y una copia del paquete.
4. En la computadora central, guardar los dos paquetes fuera de Git y ejecutar,
   eligiendo una ruta de salida que todavía no exista:

   ```powershell
   .\.venv\Scripts\python.exe consolidate_annotations.py `
     --corpus docs/t2/corpus_72/corpus_para_anotar.csv `
     --package-a private/intercambio/anotaciones_A.json `
     --package-b private/intercambio/anotaciones_B.json `
     --output private/annotations_central.sqlite3
   ```

   La importación se cancela antes de crear la base si hay corrupción, hash o
   IDs distintos, duplicados, roles incorrectos o una revisión que no tenga una
   anotación válida para cada uno de los 72 IDs. Nunca sobrescribe el destino ni
   modifica las bases de origen.
5. Abrir la aplicación sobre la base central nueva, sin reemplazar la base local:

   ```powershell
   $env:HATEDETECT_ANNOTATION_DB = "private/annotations_central.sqlite3"
   .\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8503
   ```

Un SHA-256 detecta cambios y confirma que todos usaron los mismos bytes, pero no
autentica la identidad humana ni demuestra quién realizó la revisión. Por eso la
entrega de cada paquete exige confirmación real de la persona responsable. El
panel debe permanecer limitado a `127.0.0.1`; no se publica ni se abre a la red.

## Adjudicador E3

1. Esperar a que A y B terminen los mismos 72 textos.
2. Elegir E3 e ingresar su código. El panel calcula Cohen's Kappa sobre las
   decisiones originales, antes de adjudicar.
3. Revisar únicamente los desacuerdos mostrados. Los consensos no pueden ser
   reemplazados por E3.
4. Registrar clase final, grupo objetivo cuando corresponda y justificación.
5. Exportar sólo cuando no falten anotaciones ni adjudicaciones. Guardar el CSV
   final con un nombre nuevo; no modificar la base ni el CSV fuente.

En una base consolidada, E3 debe registrarse antes de habilitar el CSV final.
Cohen's Kappa se calcula sobre las 144 anotaciones originales importadas (72 de
A y 72 de B), nunca sobre decisiones adjudicadas. La tabla original no se
sobrescribe: E3 escribe en una tabla separada y sólo puede decidir desacuerdos
reales de clase o grupo objetivo. El CSV final se habilita únicamente cuando A y
B están completos y todos esos desacuerdos tienen decisión E3.

En corpus con roles registrados, la exportación acepta exclusivamente las
anotaciones vinculadas a A y B. Las bases de pilotos anteriores que no poseen la
tabla de roles mantienen la compatibilidad con su par histórico de evaluadores.

## Evidencias para cerrar HU-01 y HU-03

- Hash SHA-256 del `corpus_para_anotar.csv` revisado y `procedencia.json`.
- Constancia real de 72/72 para A y 72/72 para B, sin publicar sus códigos.
- Informe JSON de Cohen's Kappa previo a la adjudicación.
- Cantidad real de desacuerdos y constancia de que todos fueron adjudicados por E3.
- Hash del CSV final exportado y respaldo privado de la base SQLite.
- Revisión humana de idioma, anonimización y ausencia de datos identificables.
- Aceptación real del equipo/docente según el procedimiento académico aplicable.

Pytest demuestra controles del software; no sustituye ninguna de estas evidencias
humanas. Para el futuro paper aún se requieren datos reales obtenidos legítimamente,
muestreo documentado, revisión ética y evaluación científica independiente.
