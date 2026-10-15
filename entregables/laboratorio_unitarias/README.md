# Laboratorio de diez pruebas unitarias

Actualizado el 14 de octubre de 2026. Resultados de ejecución local; GitHub Actions ejecuta su propia comprobación.

| Caso | Entrada | Esperado | Observado | Estado |
| --- | --- | --- | --- | --- |
| PU01 | '  Hola   mundo  ' | Hola mundo | Hola mundo | PASÓ |
| PU02 | Escribe a persona@example.com | Escribe a [EMAIL] | Escribe a [EMAIL] | PASÓ |
| PU03 | Llámame al +51 999 123 456 | Llámame al [PHONE] | Llámame al [PHONE] | PASÓ |
| PU04 | 12345 | '' | '' | PASÓ |
| PU05 | Eres un idiota. | Ofensivo | Ofensivo | PASÓ |
| PU06 | ['Odio', 'Neutro', 'Ofensivo', 'Odio'] | {'Odio': 2, 'Ofensivo': 1, 'Neutro': 1} | {'Odio': 2, 'Ofensivo': 1, 'Neutro': 1} | PASÓ |
| PU07 | Odio=3; total=10 | 30 % | 30 % | PASÓ |
| PU08 | Violento | ValueError: Etiqueta inválida | ValueError: Etiqueta inválida | PASÓ |
| PU09 | VP=6; FP=2 | 75 % | 75 % | PASÓ |
| PU10 | 0.20; 0.30; 0.40 segundos | 0.30 segundos | 0.30 segundos | PASÓ |

## Evidencias

- [Ejecución inicial](evidencias/01_correcto.txt): 10 aprobadas.
- [Fallo controlado](evidencias/02_fallo_controlado.txt): 9 aprobadas y PU10 fallida (suma sin dividir).
- [Restauración](evidencias/03_restaurado.txt): 10 aprobadas.
- [Suite completa](evidencias/suite_completa.txt): 103 pruebas, 0 fallos y 0 errores.
- [Informe Word](Informe_pruebas_unitarias_HateDetect.docx) y [matriz CSV](evidencias/matriz_final.csv).

## Probar otras entradas

Desde la raíz del repositorio, modifica las variables de entrada y el resultado esperado en `tests/test_laboratorio_unitarias.py`. Luego ejecuta:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_laboratorio_unitarias.py -v
```

Para una sola prueba añade, por ejemplo, `-k test_p10_tiempo_promedio`. pytest no solicita datos interactivamente: los casos son reproducibles y sus entradas están en el archivo.

PU01–PU05 usan la limpieza y el clasificador de reglas existentes. PU06–PU10 usan el nuevo módulo `report_calculations.py`, todavía sin conexión a la interfaz. Los porcentajes se expresan de 0 a 100 y los tiempos en segundos.

El promedio de PU10 usa tiempos de ejemplo; no mide el rendimiento real. Las comprobaciones de entradas negativas, vacías y no finitas están separadas en `tests/test_report_calculations.py`.

El laboratorio no modifica cómo se selecciona el modelo del sistema. Tampoco corrige los falsos negativos del clasificador.

## Reproducir las tres fases

```powershell
.\.venv\Scripts\python.exe tools/ejecutar_laboratorio.py
```

La mutación afecta únicamente una copia temporal y se comprueba la integridad de los originales. Usa `--output otra_carpeta` para conservar reportes previos.

GitHub Actions ejecuta la suite y las tres fases. Los reportes automáticos se descargan desde el artefacto `resultados-pruebas`; no reemplazan automáticamente estos registros locales.
