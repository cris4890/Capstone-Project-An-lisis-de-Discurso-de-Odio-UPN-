# Estado del paquete Sprint 2 — 19/10/2026

Versión funcional verificada: `2812f2321d8ae05bbe0326c417605933477ed41f`.
Los commits posteriores de este paquete completan documentación y capturas.

| Solicitud | Evidencia y estado |
|---|---|
| 1. Cronometraje E2E | 30 registros reales de clic a resultado en `evidencias/e2e_navegador.json`. Media 0,280 s. Falta medir una sesión operativa equivalente a la manual, con ingreso y revisión, para comparar productividad integral. |
| 2. Anexo KPI | `evidencias/anexo_kpi.csv`, fuentes, cálculos y auditoría. El Excel original se conserva localmente sin modificar. |
| 3. Matriz de confusión | CSV y PNG; 18/30 aciertos, 12 errores, recall de Odio 0 %. |
| 4–5. GitHub y PR | Rama `codex/sprint2-evidencias`, commits nuevos y [PR 1](https://github.com/cris4890/Capstone-Project-An-lisis-de-Discurso-de-Odio-UPN-/pull/1). |
| 6. Pruebas actuales | 105 aprobadas localmente (26,75 s) y en GitHub Actions (39,29 s). Las 74 mencionadas anteriormente no son el inventario actual. |
| 7. Clasificación de pruebas | 77 unitarias, 21 de integración, 7 de sistema. La aceptación formal no se cuenta como prueba automática. |
| 8. Trazabilidad | `trazabilidad.md`: requisito, prueba, resultado y evidencia. |
| 9–10. Incidencias y riesgos | `calidad_seguridad.md`, incluido el 60 % del piloto y sus falsos negativos. |
| 11. Review | `review_demostracion.md`: sesión preparada; faltan fecha efectiva, participantes y decisiones reales. |
| 12. Capturas | `capturas/`: clasificación, resultado T003, historial, reportes, pruebas publicadas y Actions. |
| 13. Seguridad | Controles implementados y pendientes diferenciados en `calidad_seguridad.md`. |
| 14–16. Capítulos y numeración | Borradores VII, VIII, IX, X y XI incorporados a la copia actualizada de PC8; texto reutilizable en `capitulos.md`. |
| 17. Índices | Índices general, de tablas y de figuras actualizados en Word; numeración de tablas corregida. |
| 18. Sustentación | Recorrido y criterios en `review_demostracion.md`; pendiente ensayo del equipo y aceptación. |
| 19–20. Alcance | Producto funcional y validación científica se informan por separado. No se declara 100 % del proyecto. |

## Ejecución remota

[GitHub Actions, ejecución 39360493812](https://github.com/cris4890/Capstone-Project-An-lisis-de-Discurso-de-Odio-UPN-/actions/runs/39360493812):
resultado **success**, commit `2812f23`, suite **105 passed in 39.29s**.
Metadatos completos: `evidencias/github_actions.json`.
GitHub muestra una advertencia de compatibilidad de Node para las acciones existentes; no impidió la ejecución.

## Entregables locales y límites

La copia `private/entregables/PC8_Sprint2_actualizado.docx` conserva el informe original
y agrega resultados y limitaciones. No se publica automáticamente el Word completo ni
el Excel original; las evidencias sintéticas y documentación del proyecto sí están en la rama.

La auditoría detectó doce diferencias entre D y J en la hoja HateDetect.
El anexo conserva ambos valores y utiliza las predicciones reproducidas, sin cambiar
la clave para ocultar errores. No se corrigió el clasificador en esta medición.

Continúan pendientes el corpus autorizado, anotación real, entrenamiento definitivo,
evaluación independiente, comparabilidad operativa completa y Review con aceptación humana.
