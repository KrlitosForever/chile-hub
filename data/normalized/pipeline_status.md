# chile-hub pipeline status

- `generated_at_utc`: `2026-05-31T22:17:30.175286+00:00`

| Dataset | Source | Mode | Detail | Freshness | Coverage | Records | Validation | Warnings |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- | :--- |
| `comunas` | SUBDERE | `fallback` | `embedded_sample` | `fresh (1.87h / 2160h)` | `partial` | 18 | `ok` | comunas source_mode is fallback; coverage is limited by design |
| `indicadores` | Banco Central de Chile (via mindicador.cl) | `live` | `public_api` | `fresh (2.26h / 72h)` | `not_applicable` | 375 | `ok` | none |
| `provincias` | SUBDERE | `fallback` | `embedded_sample` | `fresh (1.87h / 2160h)` | `partial` | 11 | `ok` | none |
| `regiones` | SUBDERE | `fallback` | `embedded_sample` | `fresh (1.87h / 2160h)` | `partial` | 11 | `ok` | none |

## comunas

- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `coverage`: `Cobertura parcial: 18/346 filas respecto del baseline esperado.`
- `fields`: `codigo_region, nombre_region, abreviatura, codigo_provincia, nombre_provincia, codigo_comuna, nombre_comuna, nombre_comuna_clean, latitud_cabecera, longitud_cabecera, poblacion_estimada`
- `notes`: bcn_fetch_error: Failed to perform, curl: (52) Empty reply from server. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.; fallback_due_to_missing_remote_file
- `warnings`: comunas source_mode is fallback; coverage is limited by design

## indicadores

- `refreshed_at_utc`: `2026-05-31T20:01:54.399040+00:00`
- `freshness`: `fresh (2.26h / 72h)`
- `coverage`: `Sin baseline de cobertura por cardinalidad para esta capa.`
- `fields`: `fecha, codigo_indicador, valor`
- `indicator_codes`: `dolar, euro, ipc, uf, utm`
- `warnings`: none

## provincias

- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `coverage`: `Cobertura parcial: 11/56 filas respecto del baseline esperado.`
- `fields`: `codigo_region, nombre_region, codigo_provincia, nombre_provincia`
- `notes`: bcn_fetch_error: Failed to perform, curl: (52) Empty reply from server. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.; fallback_due_to_missing_remote_file
- `warnings`: none

## regiones

- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `coverage`: `Cobertura parcial: 11/16 filas respecto del baseline esperado.`
- `fields`: `codigo_region, nombre_region`
- `notes`: bcn_fetch_error: Failed to perform, curl: (52) Empty reply from server. See https://curl.se/libcurl/c/libcurl-errors.html first for more details.; fallback_due_to_missing_remote_file
- `warnings`: none
