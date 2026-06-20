# chile-hub provenance report

- `generated_at_utc`: `2026-06-20T02:40:01.612344+00:00`
- `dataset_count`: `15`
- `live_count`: `15`
- `fallback_count`: `0`

| Dataset | Source | Mode | Detail | Refreshed | Freshness | Warnings | Reuse |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| `regiones` | BCN ArcGIS | `live` | `bcn_arcgis` | `2026-06-18T18:30:46.224469+00:00` | `fresh (32.15h / 2160h)` | 0 | `open-attribution` |
| `provincias` | BCN ArcGIS | `live` | `bcn_arcgis` | `2026-06-18T18:30:46.224469+00:00` | `fresh (32.15h / 2160h)` | 0 | `open-attribution` |
| `comunas` | BCN ArcGIS | `live` | `bcn_arcgis` | `2026-06-18T18:30:46.224469+00:00` | `fresh (32.15h / 2160h)` | 0 | `open-attribution` |
| `comunas_enriquecidas` | BCN ArcGIS | `live` | `bcn_arcgis` | `2026-06-18T18:30:46.224469+00:00` | `fresh (32.15h / 2160h)` | 0 | `open-attribution` |
| `indicadores` | Banco Central de Chile (via mindicador.cl) | `live` | `public_api_with_published_backfill` | `2026-06-18T18:31:12.577138+00:00` | `fresh (32.15h / 72h)` | 1 | `open-attribution` |
| `censo_comunal` | Instituto Nacional de Estadisticas - Censo 2024 | `live` | `official_xlsx` | `2026-06-18T18:31:13.357597+00:00` | `fresh (32.15h / 87600h)` | 0 | `open-attribution` |
| `establecimientos_salud` | Ministerio de Salud - Establecimientos de Salud | `live` | `datos_gob_csv` | `2026-06-18T18:31:17.917347+00:00` | `fresh (32.15h / 1080h)` | 0 | `open-attribution` |
| `establecimientos_educacionales` | Ministerio de Educación - Directorio Oficial de Establecimientos | `live` | `mineduc_datos_abiertos_rar` | `2026-06-18T18:31:18.746651+00:00` | `fresh (32.15h / 8760h)` | 0 | `open-attribution` |
| `censo_hogares_viviendas` | Instituto Nacional de Estadisticas - Censo 2024 | `live` | `official_xlsx` | `2026-06-18T18:31:14.037287+00:00` | `fresh (32.15h / 87600h)` | 0 | `open-attribution` |
| `distritos_electorales` | BCN / Biblioteca del Congreso Nacional de Chile | `live` | `bcn_electoral_mapping_generated` | `2026-06-18T18:31:18.060258+00:00` | `fresh (32.15h / 87600h)` | 0 | `open-attribution` |
| `finanzas_municipales` | SINIM - SUBDERE | `live` | `curated_fallback_pending_direct_export` | `2026-06-18T18:31:19.105129+00:00` | `fresh (32.15h / 8760h)` | 0 | `public-api-review-terms` |
| `resultados_educacionales` | Centro de Estudios MINEDUC - Rendimiento 2024 | `live` | `mineduc_rendimiento_2024_rar_agregado_por_comuna` | `2026-06-19T20:29:47.137487+00:00` | `fresh (6.17h / 8760h)` | 0 | `open-attribution` |
| `indicadores_urbanos_siedu` | INE - Sistema de Indicadores y Estándares de Desarrollo Urbano | `live` | `ine_siedu_xlsm_cinco_mediciones_2018_2022` | `2026-06-20T00:14:18.604878+00:00` | `fresh (2.43h / 8760h)` | 1 | `open-attribution` |
| `perfil_territorial_comunal` | chile-hub | `live` | `derived_from_validated_chile_hub_layers` | `2026-06-20T02:40:01.610543+00:00` | `fresh (0.0h / 1080h)` | 0 | `open-attribution` |
| `empresas` | Ministerio de Economia, Fomento y Turismo - Registro de Empresas y Sociedades (RES) | `live` | `datos_gob_cl_ckan_api` | `2026-06-18T18:36:53.298827+00:00` | `fresh (32.05h / 1080h)` | 3 | `open-attribution` |

## regiones

- `source_name`: BCN ArcGIS
- `source_url`: https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0/query
- `source_mode`: `live`
- `source_detail`: `bcn_arcgis`
- `refreshed_at_utc`: `2026-06-18T18:30:46.224469+00:00`
- `freshness`: `fresh (32.15h / 2160h)`
- `warning_count`: `0`
- `diagnostic_summary`: bcn_skipped_null_code_records: 1
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/regiones.md`

## provincias

- `source_name`: BCN ArcGIS
- `source_url`: https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0/query
- `source_mode`: `live`
- `source_detail`: `bcn_arcgis`
- `refreshed_at_utc`: `2026-06-18T18:30:46.224469+00:00`
- `freshness`: `fresh (32.15h / 2160h)`
- `warning_count`: `0`
- `diagnostic_summary`: bcn_skipped_null_code_records: 1
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/provincias.md`

## comunas

- `source_name`: BCN ArcGIS
- `source_url`: https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0/query
- `source_mode`: `live`
- `source_detail`: `bcn_arcgis`
- `refreshed_at_utc`: `2026-06-18T18:30:46.224469+00:00`
- `freshness`: `fresh (32.15h / 2160h)`
- `warning_count`: `0`
- `diagnostic_summary`: bcn_skipped_null_code_records: 1
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/comunas.md`

## comunas_enriquecidas

- `source_name`: BCN ArcGIS
- `source_url`: https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0/query
- `source_mode`: `live`
- `source_detail`: `bcn_arcgis`
- `refreshed_at_utc`: `2026-06-18T18:30:46.224469+00:00`
- `freshness`: `fresh (32.15h / 2160h)`
- `warning_count`: `0`
- `diagnostic_summary`: bcn_skipped_null_code_records: 1
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/comunas_enriquecidas.md`

## indicadores

- `source_name`: Banco Central de Chile (via mindicador.cl)
- `source_url`: https://mindicador.cl/api
- `source_mode`: `live`
- `source_detail`: `public_api_with_published_backfill`
- `refreshed_at_utc`: `2026-06-18T18:31:12.577138+00:00`
- `freshness`: `fresh (32.15h / 72h)`
- `warning_count`: `1`
- `diagnostic_summary`: indicadores live refresh reused last published artifact for missing codes: ipc
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/indicadores.md`

## censo_comunal

- `source_name`: Instituto Nacional de Estadisticas - Censo 2024
- `source_url`: https://censo2024.ine.gob.cl/wp-content/uploads/2025/03/D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx
- `source_mode`: `live`
- `source_detail`: `official_xlsx`
- `refreshed_at_utc`: `2026-06-18T18:31:13.357597+00:00`
- `freshness`: `fresh (32.15h / 87600h)`
- `warning_count`: `0`
- `diagnostic_summary`: age_bands_derived_from_quinquennial_groups
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/censo_comunal.md`

## establecimientos_salud

- `source_name`: Ministerio de Salud - Establecimientos de Salud
- `source_url`: https://datos.gob.cl/dataset/3bf4cf7c-f638-4735-9a01-f65faae4beca/resource/2c44d782-3365-44e3-aefb-2c8b8363a1bc/download/establecimientos_20260616.csv
- `source_mode`: `live`
- `source_detail`: `datos_gob_csv`
- `refreshed_at_utc`: `2026-06-18T18:31:17.917347+00:00`
- `freshness`: `fresh (32.15h / 1080h)`
- `warning_count`: `0`
- `diagnostic_summary`: Sin observaciones operativas.
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/establecimientos_salud.md`

## establecimientos_educacionales

- `source_name`: Ministerio de Educación - Directorio Oficial de Establecimientos
- `source_url`: https://datosabiertos.mineduc.cl/wp-content/uploads/2025/11/Directorio-Oficial-EE-2025.rar
- `source_mode`: `live`
- `source_detail`: `mineduc_datos_abiertos_rar`
- `refreshed_at_utc`: `2026-06-18T18:31:18.746651+00:00`
- `freshness`: `fresh (32.15h / 8760h)`
- `warning_count`: `0`
- `diagnostic_summary`: Sin observaciones operativas.
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/establecimientos_educacionales.md`

## censo_hogares_viviendas

- `source_name`: Instituto Nacional de Estadisticas - Censo 2024
- `source_url`: https://censo2024.ine.gob.cl/wp-content/uploads/2025/03/V1_Viviendas-y-hogares-censados.xlsx
- `source_mode`: `live`
- `source_detail`: `official_xlsx`
- `refreshed_at_utc`: `2026-06-18T18:31:14.037287+00:00`
- `freshness`: `fresh (32.15h / 87600h)`
- `warning_count`: `0`
- `diagnostic_summary`: Sin observaciones operativas.
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/censo_hogares_viviendas.md`

## distritos_electorales

- `source_name`: BCN / Biblioteca del Congreso Nacional de Chile
- `source_url`: https://www.bcn.cl/siit/observatorio/ley20840
- `source_mode`: `live`
- `source_detail`: `bcn_electoral_mapping_generated`
- `refreshed_at_utc`: `2026-06-18T18:31:18.060258+00:00`
- `freshness`: `fresh (32.15h / 87600h)`
- `warning_count`: `0`
- `diagnostic_summary`: Sin observaciones operativas.
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/distritos_electorales.md`

## finanzas_municipales

- `source_name`: SINIM - SUBDERE
- `source_url`: https://datos.sinim.gov.cl/datos_municipales.php
- `source_mode`: `live`
- `source_detail`: `curated_fallback_pending_direct_export`
- `refreshed_at_utc`: `2026-06-18T18:31:19.105129+00:00`
- `freshness`: `fresh (32.15h / 8760h)`
- `warning_count`: `0`
- `diagnostic_summary`: official_landing_snapshot_saved
- `reuse_status`: `public-api-review-terms`
- `documentation`: `docs/datasets/finanzas_municipales.md`

## resultados_educacionales

- `source_name`: Centro de Estudios MINEDUC - Rendimiento 2024
- `source_url`: https://datosabiertos.mineduc.cl/wp-content/uploads/2025/04/Rendimiento_2024.rar
- `source_mode`: `live`
- `source_detail`: `mineduc_rendimiento_2024_rar_agregado_por_comuna`
- `refreshed_at_utc`: `2026-06-19T20:29:47.137487+00:00`
- `freshness`: `fresh (6.17h / 8760h)`
- `warning_count`: `0`
- `diagnostic_summary`: privacy_safe_comuna_year_aggregation
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/resultados_educacionales.md`

## indicadores_urbanos_siedu

- `source_name`: INE - Sistema de Indicadores y Estándares de Desarrollo Urbano
- `source_url`: https://www.ine.gob.cl/docs/default-source/sistema-de-indicadores-y-estandares-de-desarrollo-urbano/indicadores/actualizaci%C3%B3n-2019/matriz-siedu-publicacion.xlsm
- `source_mode`: `live`
- `source_detail`: `ine_siedu_xlsm_cinco_mediciones_2018_2022`
- `refreshed_at_utc`: `2026-06-20T00:14:18.604878+00:00`
- `freshness`: `fresh (2.43h / 8760h)`
- `warning_count`: `1`
- `diagnostic_summary`: indicadores_urbanos_siedu has intentionally partial urban coverage
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/indicadores_urbanos_siedu.md`

## perfil_territorial_comunal

- `source_name`: chile-hub
- `source_url`: https://github.com/cortega26/chile-hub
- `source_mode`: `live`
- `source_detail`: `derived_from_validated_chile_hub_layers`
- `refreshed_at_utc`: `2026-06-20T02:40:01.610543+00:00`
- `freshness`: `fresh (0.0h / 1080h)`
- `warning_count`: `0`
- `diagnostic_summary`: derived_dataset
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/perfil_territorial_comunal.md`

## empresas

- `source_name`: Ministerio de Economia, Fomento y Turismo - Registro de Empresas y Sociedades (RES)
- `source_url`: https://datos.gob.cl/dataset/registro-de-empresas-y-sociedades
- `source_mode`: `live`
- `source_detail`: `datos_gob_cl_ckan_api`
- `refreshed_at_utc`: `2026-06-18T18:36:53.298827+00:00`
- `freshness`: `fresh (32.05h / 1080h)`
- `warning_count`: `3`
- `diagnostic_summary`: found 1 RUTs with non-standard format (not validated)
- `reuse_status`: `open-attribution`
- `documentation`: `docs/datasets/empresas.md`
