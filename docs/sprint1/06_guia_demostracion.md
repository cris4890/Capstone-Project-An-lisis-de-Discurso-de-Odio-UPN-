# Guía de demostración y aceptación

## Preparación

Abrir terminal en la raíz del proyecto. Usar Python 3.13 y las versiones verificadas.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir http://127.0.0.1:8501 en el equipo. Para generar reportes en una instalación nueva:

```powershell
.\.venv\Scripts\python.exe train_models.py
```

Se genera una ejecución nueva con datos sintéticos para reglas, regresión logística y SVM. No descarga ni entrena Transformer sin la opción explícita correspondiente.

## Secuencia

1. Comprobar las únicas tres secciones: Clasificación, Reportes e Historial.
2. En Clasificación y Demostración de reglas, ingresar «Hola, gracias por ayudar». Se espera Neutro, latencia y texto procesado.
3. Mantener Guardar en Historial desactivado y comprobar que la consulta no fue conservada.
4. Clasificar «Gracias u/ejemplo» activando Guardar en Historial.
5. En Historial, encontrar «Gracias [USER]», fecha UTC, categoría y modelo. Probar filtro y búsqueda.
6. En Reportes, revisar Evaluación de modelos y Exploración del corpus. Seleccionar una ejecución completa para las métricas. Explicar la advertencia cuando no incluye Transformer.
7. Declarar que el corpus es sintético y que sus proporciones no representan Reddit.
8. Mostrar «Apoyo a los inmigrantes» como limitación de reglas, no como acierto.
9. Para Anotación, abrir la herramienta auxiliar por separado, sin cuarta sección principal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run annotation_app.py --server.address 127.0.0.1 --server.port 8502
```

## Evidencia manual del equipo

Conservar capturas sintéticas, commit demostrado, pruebas y observaciones de Review. Evitar datos personales o cuentas privadas en capturas. Recargar la aplicación para mostrar persistencia del historial guardado.

No afirmar permiso de Reddit, entrenamiento final de XLM-RoBERTa, kappa humano, precisión científica, seguridad multiusuario o aprobación del docente: requieren evidencia adicional.
