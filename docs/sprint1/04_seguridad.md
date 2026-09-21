# Plan de seguridad integral

## Alcance

El plan cubre datos, aplicación e infraestructura del prototipo local. La entrega usa datos sintéticos. No habilita publicación en Internet ni carga de datos reales sin resolver permisos, acceso, conservación y revisión ética. El historial no está cifrado ni aislado por usuario.

## Activos y responsables de seguimiento

| Activo | Clasificación | Responsable según roles S3 | Tratamiento |
|---|---|---|---|
| Código y documentación | Compartible tras revisión | Erick | Git y revisión de cambios. |
| Ejemplos sintéticos | Demostración | Crisdel | Declarar origen y límites. |
| Corpus real y autorización | Restringido | Crisdel | Campos mínimos, acceso limitado y plazo autorizado. |
| Anotaciones e historial | Local restringido | Jeanpierre / Crisdel | No versionar; respaldo controlado; no usarlos como etiquetas sin revisión. |
| Credenciales | Secreto | Titular de cuenta | Fuera del código, capturas y respaldos generales. |
| Incidentes | Gestión restringida | Erick / Sintia | Registrar hechos sin copiar datos personales. |

## Datos

- Verificar origen, permiso de entrenamiento, periodo y conservación antes de importar datos reales.
- Eliminar campos innecesarios y usar identificadores internos aleatorios. El hash de un archivo demuestra integridad, no anonimato de usuarios.
- Enmascarar menciones, enlaces, correos y teléfonos; revisar manualmente nombres y contexto identificable.
- Mantener archivos restringidos en `private/` y considerar `runs/` potencialmente sensible; ambos excluidos de Git.
- Separar corpus, anotaciones e inferencias de Historial.
- Guardar Historial solo al activar la opción y tras revisar el texto.

## Aplicación

- `.streamlit/config.toml` fija escucha en `127.0.0.1`, CORS y protección XSRF habilitados, y carga máxima de 10 MB.
- Escuchar localmente reduce exposición de red; no impide acceso de personas o procesos con acceso al equipo.
- No hay autenticación multiusuario. Los códigos de anotador no son contraseñas ni acreditan independencia.
- Mostrar entradas como texto y utilizar consultas parametrizadas en SQLite.
- Cargar únicamente artefactos controlados por el equipo. Los modelos serializados de terceros pueden ser inseguros.
- No ejecutar sanciones ni presentar probabilidades sin calibrar como certeza.

## Infraestructura y accesos

Usar una cuenta del sistema operativo controlada, bloquear sesión y mantener actualizaciones. El responsable debe verificar permisos del directorio y evitar sincronizar datos privados con servicios no autorizados. Son procedimientos: no se afirma haber cambiado ACL, cifrado discos o auditado el equipo.

Antes de uso compartido, implementar identidad y autorización por función, revisar cifrado, transporte y auditoría. Cambiar la escucha a `0.0.0.0` no sustituye un despliegue seguro.

## Respaldos y restauración

`maintenance.py` genera un snapshot SQLite consistente, manifiesto SHA-256 y ZIP. Verifica integridad al restaurar y exige destino nuevo, sin sobrescribir bases existentes. El ZIP no está cifrado; necesita las mismas restricciones que los datos originales.

Procedimiento: respaldar al cerrar sesiones con cambios relevantes y registrar fecha, responsable y hash. Probar restauración antes de entregar. Para pérdida del equipo, disponer una copia adicional en destino institucional autorizado; esa copia externa no se ha configurado ni realizado. Objetivo propuesto: perder como máximo una sesión y recuperar dentro de la siguiente jornada; validar con el equipo.

```powershell
.\.venv\Scripts\python.exe maintenance.py backup --database private/history.sqlite3 --output private/backups/historial-AAAAMMDD.zip
.\.venv\Scripts\python.exe maintenance.py restore --archive private/backups/historial-AAAAMMDD.zip --database private/restaurado/history.sqlite3
```

Ejecutar solo si la base existe. Las pruebas usan bases temporales sintéticas; no equivalen a respaldar datos reales. Conservar el original hasta verificar la recuperación.

## Conservación y eliminación

La autorización de datos reales debe fijar fecha límite. Comprobarla antes de cada nuevo uso. El historial sintético puede mantenerse para la Review; la fecha definitiva de eliminación la acordará el equipo porque la entrega académica sigue pendiente.

Al vencer un plazo o recibirse una solicitud válida: identificar corpus, copias y artefactos afectados; detener uso; obtener decisión del responsable; eliminar conforme al protocolo y registrar archivo, fecha y ejecutor sin reproducir contenido. Revisar respaldos. No hay purga automática y no se eliminaron datos del usuario en esta entrega. Sin plazo y responsables definidos no se habilita almacenamiento real.

## Incidentes

1. Registrar detección, activo e impacto sin divulgar contenido.
2. Contener: detener aplicación o uso del artefacto y limitar acceso.
3. Evaluar copias, alcance y credenciales; revocar las expuestas.
4. Corregir y probar regresión o restauración.
5. Comunicar al equipo y responsables institucionales conforme al protocolo aplicable.
6. Cerrar con evidencia y decisión del responsable.

Prioridad crítica: exposición de datos o ejecución no confiable. Alta: corrupción, pérdida o fuga experimental. Media: defectos sin esos impactos. Usar `05_registros.md`.

## Criterios y límites

Se verifican minimización, guardado voluntario, persistencia, respaldo íntegro, restauración sin sobrescritura y configuración local. No constituyen auditoría de seguridad ni certificación legal. Autenticación, cifrado, recuperación externa y eliminación aplicada quedan pendientes antes de producción o datos reales.
