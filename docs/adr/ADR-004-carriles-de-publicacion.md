# ADR-004: Sistema de carriles de publicacion (stable_publishable vs candidate)

**Fecha:** 2026-06-18
**Estado:** accepted
**Decision:** Los datasets se clasifican en dos carriles de publicacion: `stable_publishable` (incluidos en el bundle publico y el ZIP de distribucion) y `candidate` (excluidos del bundle hasta que maduren y tengan un extractor live funcional).

## Contexto

chile-hub define 15 datasets de fuentes oficiales chilenas. No todos tienen el mismo nivel de madurez: algunos tienen extractores live completamente implementados y datos frescos (ej. `regiones`, `indicadores`), otros solo disponen de datos de respaldo curados manualmente (fallback), y algunos son capas derivadas que dependen de datasets upstream aun no publicables.

El archivo `data/source_registry.json` es la fuente unica de configuracion de cada dataset. En la version 1.4.0 se introdujeron los campos `publication_track` y `public_bundle_eligible` para gobernar este comportamiento. Actualmente, 4 datasets estan en carril `candidate`:

- `finanzas_municipales` -- extractor live `fallback_only`, datos SINIM/SUBDERE en respaldo
- `resultados_educacionales` -- extractor live `fallback_only`, datos MINEDUC en respaldo
- `indicadores_urbanos_siedu` -- extractor live `fallback_only`, datos INE/SIEDU en respaldo
- `perfil_territorial_comunal` -- capa derivada, depende de datasets upstream candidate

Los datasets `candidate` tienen `public_bundle_eligible: false`, lo que significa que el script `scripts/package_publishable_bundle.py` y la funcion `build_publishable_artifact_index()` en `src/build_dev_db.py` los excluyen del manifiesto de artefactos publicables y del ZIP de distribucion.

La funcion `verify_publication_policy()` en `scripts/verify_pipeline.py` valida reglas estrictas: los datasets `stable_publishable` deben tener `source_mode=live`, frescura "fresh" y extractor implementado. Los datasets `candidate` no pueden aparecer en el manifiesto de artefactos. Los datasets derivados heredan el estado no-publicable de sus upstreams.

## Decision

Se decidio un sistema de dos carriles con reglas de validacion automatizadas:

- **`stable_publishable`**: Incluido en `hub_bundle.json` y en el ZIP publico. Requiere `maturity_status=stable`, `live_ready=true`, extractor implementado o derivado de fuentes estables. La publicacion falla si el dataset opera en modo `fallback` cuando su `fallback_policy` es `allowed_for_dev_blocked_for_publication`.
- **`candidate`**: Excluido del bundle publico pero listado de forma transparente en `hub_bundle.json` bajo `candidate_datasets` con metadatos de madurez y accion recomendada. Permite `maturity_status=candidate`, `experimental` o `deprecated`. No requiere extractor live.

La exclusion es a nivel de manifiesto de artefactos: la funcion `build_publishable_artifact_index()` en `src/build_dev_db.py` itera sobre el registry y solo incluye datasets con `public_bundle_eligible=true`. La validacion en `verify_source_registry()` verifica que los datasets `candidate` tengan `public_bundle_eligible=false` y que los `stable_publishable` tengan `public_bundle_eligible=true`.

## Consecuencias

- Positivas: Los consumidores del bundle publico reciben solo datasets maduros y verificados. Los datasets en desarrollo son visibles en los metadatos del hub (con su estado y accion recomendada) pero no contaminan el ZIP de distribucion. El sistema permite una progresion gradual: un dataset pasa de `experimental` a `candidate` y finalmente a `stable_publishable` cuando su extractor live esta listo.
- Negativas: Los consumidores que necesitan datos candidate (ej. finanzas municipales para un analisis regional) deben extraerlos directamente del repositorio o ejecutar el pipeline localmente. El cambio de carril requiere una actualizacion manual de `source_registry.json` y un nuevo release del paquete. La capa derivada `perfil_territorial_comunal` permanecera en `candidate` mientras cualquiera de sus 9 upstreams lo este, creando una dependencia en cascada.

## Alternativas consideradas

- **Un solo carril con todos los datasets incluidos** -- Se descarto porque datos en fallback sin extractor live no deberian distribuirse como oficiales. Publicar `finanzas_municipales` con datos de respaldo de 2023 daria una falsa impresion de actualidad.
- **Tres carriles (stable, candidate, experimental)** -- Se descarto porque `experimental` es un `maturity_status` dentro del carril `candidate`, no un carril separado. La granularidad adicional se maneja via el campo `maturity_status` en el registry.
- **Exclusion por configuracion externa (variables de entorno, flags CLI)** -- Se descarto porque la politica de publicacion debe ser determinista y verificable en CI, no dependiente de configuracion del entorno de ejecucion.
