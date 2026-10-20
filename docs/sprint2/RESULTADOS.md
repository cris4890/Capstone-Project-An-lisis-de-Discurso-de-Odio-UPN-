# Resultados verificados de Sprint 2

Piloto: 18/30 aciertos; exactitud 60%.

Referencia de trabajo sintética; no es evaluación científica final.

| Clase | Soporte | FP | FN | Recall |
| --- | ---: | ---: | ---: | ---: |
| Odio | 10 | 0 | 10 | 0.0% |
| Ofensivo | 10 | 0 | 2 | 80.0% |
| Neutro | 10 | 12 | 0 | 100.0% |

Tiempos E2E registrados en navegador: 30/30.
Los tiempos de inferencia no se usan como tiempo total ni se comparan directamente con el proceso manual.
Clasificación manual y tiempos: ficha aportada del 04/10/2026. No se acredita cegamiento ni equivalencia del intervalo cronometrado.
Cobertura de respuesta = casos con resultado / casos enviados; no equivale a recall ni exactitud.

Suite: 105 casos; aprobados: 105.

| Tipo | Casos |
| --- | ---: |
| unitaria | 77 |
| integracion | 21 |
| sistema | 7 |
| aceptacion | 0 |

Aceptación formal: pendiente de Review humana; no se deduce de pytest.

Tiempo E2E medio observado: 0.280 s. Total de ventanas medidas: 8.407 s.
Medición clic a marcador de resultado y dos frames. Excluye lectura, preparación del texto y revisión humana; no equivale al tiempo total del trabajo manual.

Manual: 203.84 s, media 6.795 s, 28/30 aciertos, 8/30 antes de 60 s acumulados.
La capacidad calculada sobre ventanas E2E es descriptiva; excluye intervalos entre casos, ingreso y revisión. No se presenta como mejora causal de productividad.
