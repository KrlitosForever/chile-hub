# chile-hub drift report

- `generated_at_utc`: `2026-05-31T22:17:30.175286+00:00`
- `dataset_count`: `4`
- `drifted_count`: `3`
- `healthy_count`: `1`
- `fallback_count`: `3`
- `partial_coverage_count`: `3`
- `degraded_count`: `3`

| Dataset | Drift | Mode | Coverage | Degradation | Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `regiones` | `drifted` | `fallback` | `partial` | `degraded` | Recuperar comunas live para restaurar cobertura derivada completa. |
| `provincias` | `drifted` | `fallback` | `partial` | `degraded` | Recuperar comunas live para restaurar cobertura derivada completa. |
| `comunas` | `drifted` | `fallback` | `partial` | `degraded` | Reintentar extractores o restaurar la fuente territorial primaria. |
| `indicadores` | `healthy` | `live` | `not_applicable` | `none` | Ninguna. |

## regiones

- `drift_status`: `drifted`
- `source_mode`: `fallback`
- `coverage`: `Cobertura parcial: 11/16 filas respecto del baseline esperado.`
- `degradation`: Capa derivada desde comunas en fallback; cardinalidad reducida a 11 filas.
- `recommended_action`: Recuperar comunas live para restaurar cobertura derivada completa.

## provincias

- `drift_status`: `drifted`
- `source_mode`: `fallback`
- `coverage`: `Cobertura parcial: 11/56 filas respecto del baseline esperado.`
- `degradation`: Capa derivada desde comunas en fallback; cardinalidad reducida a 11 filas.
- `recommended_action`: Recuperar comunas live para restaurar cobertura derivada completa.

## comunas

- `drift_status`: `drifted`
- `source_mode`: `fallback`
- `coverage`: `Cobertura parcial: 18/346 filas respecto del baseline esperado.`
- `degradation`: Cobertura territorial parcial: 18 comunas disponibles desde fallback embebido.
- `recommended_action`: Reintentar extractores o restaurar la fuente territorial primaria.

## indicadores

- `drift_status`: `healthy`
- `source_mode`: `live`
- `coverage`: `Sin baseline de cobertura por cardinalidad para esta capa.`
- `degradation`: Sin degradación operativa detectada en este build.
- `recommended_action`: Ninguna.
