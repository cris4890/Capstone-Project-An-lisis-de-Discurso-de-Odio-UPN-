# Registros de ejecución y control

## Cambios

| ID | Cambio | Evidencia | Estado |
|---|---|---|---|
| C01 | Tres subsistemas, corpus dentro de Reportes y Anotación separada | Aceptación del usuario y código | Aceptado por el usuario; sin validación docente acreditada. |
| C02 | Sprint del 14 al 20 de septiembre de 2026 | Fechas del usuario y hora de Lima | Entrega académica pendiente. |
| C03 | Configuración local y respaldo verificable | Configuración, mantenimiento y pruebas | Implementado para uso local. |
| C04 | Ramas y revisión automática | `.github/` y estrategia | Preparado localmente; nube no acreditada. |

## Incidencias y limitaciones

| ID | Descripción | Tratamiento | Estado |
|---|---|---|---|
| I01 | Pruebas esperaban la navegación anterior | Actualizar a tres subsistemas y ejecutar | Corregido; ver evidencia. |
| I02 | Historial y Anotación separada sin verificación después de una interrupción | Pruebas de guardado, persistencia y acceso separado | Verificado en suite actual. |
| I03 | Reglas confunden menciones neutrales con odio | Mantener aviso y casos funcionales | Limitación abierta; no habilita moderación autónoma. |
| I04 | Corpus autorizado y validación humana ausentes | Preparar acceso y conservar modo sintético | Dependencia externa. |
| I05 | Fecha académica y ceremonias sin evidencia | Campos pendientes para completar con hechos | Pendiente del equipo. |
| I06 | Autenticación, conservación real y recuperación externa pendientes | Restringir demostración a local/sintética | Pendiente antes de producción. |

## Corrección detectada durante la verificación

I07: la primera prueba de respaldo encontró que una conexión SQLite quedaba abierta y bloqueaba la limpieza temporal en Windows. Se corrigió el cierre explícito de conexiones en mantenimiento, anotación e historial. La suite se repite después del cambio; el resultado final y su hora quedan en las evidencias.

## Evidencia técnica

Consultar `evidencias/pruebas.xml`, `evidencias/resumen_pruebas.json` y `evidencias/repositorio.json`. Sus tiempos son duración de verificaciones, no horas trabajadas por estudiantes.

## Formularios pendientes

### Planning

Fecha y asistentes: pendiente. Capacidad y horas comprometidas: pendiente. Ratificación del Sprint Goal y tareas S1-01 a S1-10: pendiente.

### Seguimiento

| Fecha real | Integrante | Tarea | Resultado o bloqueo | Siguiente acción | Horas reales |
|---|---|---|---|---|---|
| Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | No registradas |

### Review

Fecha, asistentes y commit demostrado: por completar. Criterios aceptados/rechazados y observaciones del equipo/docente: pendientes. Entrega académica: pendiente.

### Retrospectiva

Qué funcionó, qué mejorar y acción con responsable y fecha: completar con valoración real del equipo. No dar por realizadas reuniones o aprobaciones para completar formalmente este archivo.
