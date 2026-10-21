# Protocolo y auditoría del piloto

## Fuentes y correspondencia

30 textos sintéticos T001 a T030, 15 en español y 15 en inglés. La ficha del usuario declara KPI-PILOTO-001, fecha 04/10/2026, reglas v2 y ventana de cobertura de un minuto. Su SHA256 queda en `evidencias/auditoria_excel.json`. Se cotejaron ID y texto antes de importar. Neutral se normaliza a Neutro, sin modificar la categoría semántica.

Se preserva la ejecución histórica de inferencia en `piloto_historico.json`. La columna D de Prueba HateDetect discrepa de J en 12 filas; D coincide con la clave y alimenta el resumen, lo que inflaría los aciertos. J coincide con las salidas históricas. El anexo conserva D y J para auditar la discrepancia; las predicciones se toman de la ejecución reproducida y del navegador, no de D.

La clave del Excel se usa como referencia aportada; no se afirma que sea un gold standard independiente. El proceso manual reporta 28 aciertos de 30 y 203,84 segundos. No se reconstruye ni inventa cegamiento del evaluador.

## Repetición E2E del 19 de octubre

Instrumentación activada únicamente con `CAPSTONE_E2E=1`. Instancia local en 127.0.0.1:8502, reglas v2, historial desactivado durante los 30 envíos. Mismo orden T001 a T030, una repetición por texto; aplicación cargada antes de empezar. El primer caso no se descarta.

El inicio se toma con performance.now en el evento clic capturado del botón Clasificar. El final se toma cuando aparece un marcador nuevo después de la predicción y del texto procesado, más dos requestAnimationFrame. Esto ofrece una aproximación al resultado renderizado, no una medida de percepción humana. La automatización espera un contador nuevo antes del siguiente envío; los identificadores de resultado evitan confundir salidas anteriores.

No incluye preparación, pegado del texto, revisión humana ni guardado en Historial. No se usan los tiempos del controlador remoto ni el tiempo de model.predict como sustitutos de E2E. La instrumentación añade una pequeña carga y no representa un ensayo de carga concurrente.

## KPI y límites comparativos

- Exactitud = aciertos / 30; error = fallos / 30.
- Tiempo medio = suma de tiempos válidos / casos medidos.
- Capacidad sobre ventanas cronometradas = 60 × casos / suma de tiempos. No es productividad de un flujo humano completo.
- Cobertura en un minuto = casos cuyo tiempo acumulado no supera 60 / 30, con orden fijo. No equivale a recall.
- Las ventanas manuales y E2E tienen límites distintos. Se muestran juntas de forma descriptiva, pero no se afirma una mejora causal, ahorro salarial o superioridad operativa integral.

Para una comparación definitiva: fijar el inicio y fin comunes, incluir ingreso y revisión cuando formen parte del trabajo, registrar interrupciones, alternar orden para controlar aprendizaje y repetir con varias personas y muestras reservadas. La Review y el protocolo deben aprobarse antes de la evaluación final.

## Activar la instrumentación

```powershell
$env:CAPSTONE_E2E='1'
$env:CAPSTONE_HISTORY_DB='private/sprint2/history.sqlite3'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1
```

La instrumentación no envía información a terceros y solo retiene números, categoría e identificadores en memoria de la pestaña. El anexo E2E se exporta desde el panel visible. No registra texto en el estado de medición. Al cerrar la pestaña se pierde ese estado.
