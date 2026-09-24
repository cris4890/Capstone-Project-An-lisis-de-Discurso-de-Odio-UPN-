# Prueba local de Doccano

Doccano 1.8.4 instalado en un entorno Python 3.10 separado del clasificador.
Solo datos sinteticos. No reemplaza aun la herramienta interna.

## Abrir y probar

1. Abrir http://127.0.0.1:8001 en el navegador del equipo.
2. Consultar las claves en `private/doccano/accesos.json`, fuera de Git.
3. Entrar como `evaluador_a` y abrir su proyecto. Hay 12 comentarios sin decisiones precargadas.
4. Seleccionar **Odio**, **Ofensivo** o **Neutro**.
5. En **Comments**, escribir un comentario con este formato:

   Objetivo: grupo atacado, o No aplica

   Justificacion: motivo de la categoria elegida

6. Confirmar la unidad. Si falta contexto, dejarla sin confirmar.
7. Cerrar sesion. Una segunda persona entra como `evaluador_b` para anotar independientemente. No usar la cuenta coordinador para la evaluacion independiente.

`coordinador` puede revisar ambos proyectos. Las cuentas son para la prueba local; no se asignan a personas reales ni acreditan anotaciones humanas.

Si el servidor se detuvo: ejecutar `powershell -File tools/doccano/iniciar.ps1` desde la raiz del proyecto.

## Resultado comprobado

- HTTP 200 en la pagina inicial y escucha limitada a 127.0.0.1:8001.
- Siete verificaciones API aprobadas: rechazo anonimo, acceso propio, rechazo al otro proyecto, guardado de clase y comentario, aislamiento de comentarios y reversion de decisiones tecnicas.
- Las decisiones usadas por las pruebas fueron revertidas. No se calculo kappa ni se fingieron anotaciones humanas.
- Exportacion local de 24 registros (12 por evaluador), con etiquetas, comentarios, identificadores y estado de confirmacion, inicialmente vacios.
- El navegador integrado bloqueo la apertura; la interfaz visual no se verifico en esta sesion. Las comprobaciones de funcionamiento se realizaron mediante HTTP y API.

## Limitacion importante

En esta version los comentarios se comparten entre miembros del mismo proyecto, incluso con anotacion colaborativa desactivada. Por eso hay **dos proyectos separados**, con los mismos identificadores de comentario y un evaluador distinto en cada uno. Se comprobo que un evaluador no accede al proyecto del otro.

Objetivo y justificacion se capturan como texto en Comments, no como campos obligatorios independientes. Doccano no obliga a completarlos antes de confirmar. Es necesaria una validacion adicional antes de aceptar el corpus. No afirmar que cumple todo el protocolo de investigacion por instalarlo.

## Exportar sin perder justificaciones

Desde la raiz:

```powershell
private/doccano/venv/Scripts/python.exe tools/doccano/export_pilot.py
```

Salida: `private/doccano/exportacion_piloto.jsonl`. El adaptador consulta la base local y conserva comentarios con autor y fecha por evaluador; no depende de que la exportacion estandar incluya todos esos campos. No entrena modelos ni adjudica desacuerdos. Tras la prueba humana se debe validar completitud, calcular acuerdo previo a adjudicacion y resolver diferencias con un tercer evaluador antes de integrar los datos al corpus.

## Reproducir instalacion

```powershell
uv venv --python 3.10 private/doccano/venv
uv pip sync --python private/doccano/venv/Scripts/python.exe tools/doccano/requirements.lock.txt
private/doccano/venv/Scripts/python.exe tools/doccano/local.py init
private/doccano/venv/Scripts/python.exe tools/doccano/prepare_pilot.py
```

El servidor usa un adaptador de arranque para limitar la escucha a localhost. Los datos, secretos, accesos y logs quedan en private. Docker se intento iniciar pero no estuvo disponible; la prueba usa Python. No se modificaron las dependencias de la aplicacion principal.

Para importaciones y exportaciones estandar mediante la interfaz, Doccano necesita ademas su cola de tareas: `private/doccano/venv/Scripts/python.exe tools/doccano/local.py task --concurrency 1`. Durante la preparacion se inicio y se verifico el estado ready; no se probo una carga de archivos desde la interfaz.

Referencia de instalacion: https://doccano.github.io/doccano/install_and_upgrade_doccano/
