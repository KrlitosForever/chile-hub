# chile-hub provenance report

- `generated_at_utc`: `2026-05-31T22:17:30.175286+00:00`
- `dataset_count`: `4`
- `live_count`: `1`
- `fallback_count`: `3`

| Dataset | Source | Mode | Detail | Refreshed | Freshness | Reuse |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `regiones` | SUBDERE | `fallback` | `embedded_sample` | `2026-05-31T20:25:25.852270+00:00` | `fresh (1.87h / 2160h)` | `open-attribution` |
| `provincias` | SUBDERE | `fallback` | `embedded_sample` | `2026-05-31T20:25:25.852270+00:00` | `fresh (1.87h / 2160h)` | `open-attribution` |
| `comunas` | SUBDERE | `fallback` | `embedded_sample` | `2026-05-31T20:25:25.852270+00:00` | `fresh (1.87h / 2160h)` | `open-attribution` |
| `indicadores` | Banco Central de Chile (via mindicador.cl) | `live` | `public_api` | `2026-05-31T20:01:54.399040+00:00` | `fresh (2.26h / 72h)` | `open-attribution` |

## regiones

- `source_name`: SUBDERE
- `source_url`: https://www.subdere.gov.cl/sites/default/files/documentos/cut_2018_0.xls
- `source_mode`: `fallback`
- `source_detail`: `embedded_sample`
- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/regiones.md`

## provincias

- `source_name`: SUBDERE
- `source_url`: https://www.subdere.gov.cl/sites/default/files/documentos/cut_2018_0.xls
- `source_mode`: `fallback`
- `source_detail`: `embedded_sample`
- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/provincias.md`

## comunas

- `source_name`: SUBDERE
- `source_url`: https://www.subdere.gov.cl/sites/default/files/documentos/cut_2018_0.xls
- `source_mode`: `fallback`
- `source_detail`: `embedded_sample`
- `refreshed_at_utc`: `2026-05-31T20:25:25.852270+00:00`
- `freshness`: `fresh (1.87h / 2160h)`
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/comunas.md`

## indicadores

- `source_name`: Banco Central de Chile (via mindicador.cl)
- `source_url`: https://mindicador.cl/api
- `source_mode`: `live`
- `source_detail`: `public_api`
- `refreshed_at_utc`: `2026-05-31T20:01:54.399040+00:00`
- `freshness`: `fresh (2.26h / 72h)`
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/indicadores.md`
