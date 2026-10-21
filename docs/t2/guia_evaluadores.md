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

La concordancia, matriz y distribuciones de etiquetas permanecen ocultas para A
y B mientras cualquiera tenga unidades pendientes. Se habilitan para ambos sólo
después de completar las dos revisiones, para no condicionar decisiones.

## Adjudicador E3

1. Esperar a que A y B terminen los mismos 72 textos.
2. Elegir E3 e ingresar su código. El panel calcula Cohen's Kappa sobre las
   decisiones originales, antes de adjudicar.
3. Revisar únicamente los desacuerdos mostrados. Los consensos no pueden ser
   reemplazados por E3.
4. Registrar clase final, grupo objetivo cuando corresponda y justificación.
5. Exportar sólo cuando no falten anotaciones ni adjudicaciones. Guardar el CSV
   final con un nombre nuevo; no modificar la base ni el CSV fuente.

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
