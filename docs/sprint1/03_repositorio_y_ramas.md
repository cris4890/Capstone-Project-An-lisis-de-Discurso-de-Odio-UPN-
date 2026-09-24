# Repositorio y estrategia de ramas

## Estado

Remoto configurado: https://github.com/cris4890/Capstone-Project-An-lisis-de-Discurso-de-Odio-UPN-

Se comprobó su configuración local. No acredita permisos, privacidad, sincronización ni protecciones de GitHub. El commit de partida es `1b1707f`; la rama inicial fue `main`.

## Flujo propuesto para el equipo y aplicado localmente a esta entrega

- `main`: versión integrada apta para demostrar.
- `codex/sprint1-entrega`: incremento y documentación de esta entrega.
- Futuras ramas cortas: `codex/s1-<tarea>` o `codex/correccion-<tema>`, con un objetivo por cambio.
- No se añade `develop`: no es necesario para este alcance.
- Integrar a `main` mediante solicitud de integración, pruebas y revisión de otro integrante.
- Commits con problema y resultado identificables; prefijos `feat`, `fix`, `docs` o `test`.

La rama y el commit local se registran en las evidencias. Revisión obligatoria y protección remota son normas por configurar en GitHub, no controles ya acreditados.

## Secuencia

1. Seleccionar tarea y criterio de aceptación.
2. Actualizar base y crear rama de trabajo.
3. Implementar, documentar y ejecutar `python -m pytest -q`.
4. Revisar diferencias y archivos a incluir; crear commit.
5. Publicar la rama cuando corresponda y abrir solicitud con `.github/pull_request_template.md`.
6. Adjuntar tarea, pruebas, documentación y límites.
7. Obtener revisión e integrar cuando se cumpla la DoD.

`.github/workflows/tests.yml` define pruebas en futuras publicaciones y solicitudes. Su existencia no demuestra que GitHub Actions haya ejecutado el flujo.

## Contenido versionable

Código, pruebas sintéticas, documentos, configuración sin secretos y versiones exactas. Excluir entornos, credenciales, bases locales, respaldos, corpus restringidos y ejecuciones sensibles. Los modelos y datos sintéticos históricos ya versionados se conservan; sus modificaciones preexistentes no se incorporan automáticamente a esta entrega.

Antes de publicar, comprobar `private/`, `runs/`, `.env` y `.streamlit/secrets.toml`. Revisar también archivos ya seguidos: `.gitignore` no retira datos de la historia. Una credencial expuesta debe revocarse, además de corregir el repositorio.

## Recuperación y aprobación

Corregir con nuevos commits o `git revert` tras analizar impacto. No usar `reset --hard` ni sobrescribir trabajo ajeno. Etiquetar una versión final después de la Review, sin presentar etiquetas propuestas como aprobación académica.

El administrador debe confirmar acceso del equipo, visibilidad apropiada, revisión requerida, controles de estado y protección de `main`. Conservar evidencia cuando se configure.
