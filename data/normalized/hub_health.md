# chile-hub health summary

- `generated_at_utc`: `2026-06-17T17:29:16.338743+00:00`
- `overall_status`: `warn`
- `dataset_count`: `14`
- `ok_count`: `9`
- `warn_count`: `5`
- `error_count`: `0`
- `live_count`: `10`
- `fallback_count`: `4`
- `stale_count`: `0`
- `publishable_count`: `14`
- `review_terms_count`: `0`
- `unknown_reuse_count`: `0`
- `degraded_count`: `0`
- `degradation_warning_count`: `4`
- `partial_coverage_count`: `1`
- `unknown_coverage_count`: `0`
- `drifted_count`: `5`
- `warning_count`: `6`
- `top_issue`: `finanzas_municipales` (freshness=fresh, drift=drifted, warnings=1)
- `top_issue_reason`: finanzas_municipales source_mode is fallback; review before publication
- `top_issue_action`: Revisar warnings operativos del dataset antes de consumirlo en producción.
- `top_issue_summary`: finanzas_municipales: finanzas_municipales source_mode is fallback; review before publication [source_detail=curated_fallback_pending_direct_export; warnings=1; freshness=fresh; drift=drifted; action=Revisar warnings operativos del dataset antes de consumirlo en producción.]

| Dataset | Severity | Mode | Freshness | Coverage | Drift | Publishability | Degradation | Validation | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | ---: |
| `censo_comunal` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `censo_hogares_viviendas` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `comunas` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `comunas_enriquecidas` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `distritos_electorales` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `establecimientos_educacionales` | `ok` | `live` | `fresh` | `not_applicable` | `healthy` | `ready` | `none` | `ok` | 0 |
| `establecimientos_salud` | `ok` | `live` | `fresh` | `not_applicable` | `healthy` | `ready` | `none` | `ok` | 0 |
| `finanzas_municipales` | `warn` | `fallback` | `fresh` | `not_applicable` | `drifted` | `ready` | `warning` | `ok` | 1 |
| `indicadores` | `warn` | `live` | `fresh` | `not_applicable` | `drifted` | `ready` | `warning` | `ok` | 2 |
| `indicadores_urbanos_siedu` | `warn` | `fallback` | `fresh` | `partial` | `drifted` | `ready` | `warning` | `ok` | 2 |
| `perfil_territorial_comunal` | `warn` | `fallback` | `fresh` | `full` | `drifted` | `ready` | `none` | `ok` | 0 |
| `provincias` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `regiones` | `ok` | `live` | `fresh` | `full` | `healthy` | `ready` | `none` | `ok` | 0 |
| `resultados_educacionales` | `warn` | `fallback` | `fresh` | `not_applicable` | `drifted` | `ready` | `warning` | `ok` | 1 |
