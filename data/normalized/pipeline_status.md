# chile-hub pipeline status

- `generated_at_utc`: `2026-05-31T16:57:14.689748+00:00`

| Dataset | Source | Mode | Detail | Freshness | Records | Validation | Warnings |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- | :--- |
| `comunas` | BCN ArcGIS | `live` | `bcn_arcgis` | `fresh (17.63h / 2160h)` | 346 | `ok` | none |
| `indicadores` | mindicador.cl | `live` | `public_api` | `fresh (17.63h / 72h)` | 5 | `ok` | none |
| `provincias` | BCN ArcGIS | `live` | `bcn_arcgis` | `fresh (17.63h / 2160h)` | 56 | `ok` | none |
| `regiones` | BCN ArcGIS | `live` | `bcn_arcgis` | `fresh (17.63h / 2160h)` | 16 | `ok` | none |

## comunas

- `refreshed_at_utc`: `2026-05-30T23:19:27.748102+00:00`
- `freshness`: `fresh (17.63h / 2160h)`
- `fields`: `codigo_region, nombre_region, abreviatura, codigo_provincia, nombre_provincia, codigo_comuna, nombre_comuna, nombre_comuna_clean, latitud_cabecera, longitud_cabecera, poblacion_estimada`
- `notes`: bcn_skipped_null_code_records: 1; bcn_supplemented_missing_comunas: 1
- `warnings`: none

## indicadores

- `refreshed_at_utc`: `2026-05-30T23:19:28.799272+00:00`
- `freshness`: `fresh (17.63h / 72h)`
- `fields`: `fecha, codigo_indicador, valor`
- `indicator_codes`: `dolar, euro, ipc, uf, utm`
- `warnings`: none

## provincias

- `refreshed_at_utc`: `2026-05-30T23:19:27.748102+00:00`
- `freshness`: `fresh (17.63h / 2160h)`
- `fields`: `codigo_region, nombre_region, codigo_provincia, nombre_provincia`
- `notes`: bcn_skipped_null_code_records: 1; bcn_supplemented_missing_comunas: 1
- `warnings`: none

## regiones

- `refreshed_at_utc`: `2026-05-30T23:19:27.748102+00:00`
- `freshness`: `fresh (17.63h / 2160h)`
- `fields`: `codigo_region, nombre_region`
- `notes`: bcn_skipped_null_code_records: 1; bcn_supplemented_missing_comunas: 1
- `warnings`: none
