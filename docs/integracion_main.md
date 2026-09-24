# Integración con la rama principal

Se integró el avance cb9db95 con el cambio de interfaz HateDetect de main (5dd2b07). El único conflicto de contenido fue app.py.

La resolución mantiene los tres subsistemas verificados, la selección de ejecuciones, las reglas v2, el historial persistente opcional y los reportes basados en evidencias. Incorpora la marca HateDetect y la información del proyecto en la barra lateral.

No se conserva la presentación de porcentajes fijos de confianza ni el historial precargado del diseño de main: no provenían de las inferencias actuales. Tampoco se copia su CSS que ocultaba los controles de navegación y fijaba fondos claros; se mantiene el estilo compatible con el tema ya revisado. La interfaz resultante no es una réplica exacta de aquel mockup. El commit original sigue en la historia del merge para consultar y recuperar sus decisiones de diseño.

Los datos privados, credenciales y ejecuciones locales permanecen excluidos de Git.
