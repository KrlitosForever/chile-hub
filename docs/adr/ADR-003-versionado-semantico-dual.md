# ADR-003: Versionado semantico dual (software + datos)

**Fecha:** 2026-06-18
**Estado:** accepted
**Decision:** El paquete Python usa SemVer estricto (pyproject.toml como fuente unica). Los datos se actualizan independientemente sin cambiar la version del paquete. La frescura de datos se monitorea por separado mediante metadatos de pipeline.

## Contexto

chile-hub es tanto una libreria Python como un conjunto de datos publicados. Cambios en el codigo (nuevos extractores, cambios de esquema, refactors de la API publica) compiten con cambios en los datos (nuevas fuentes, actualizaciones diarias de indicadores, censos decenales). Mezclar ambos tipos de cambio en un unico numero de version crea ambiguedad: un incremento de minor podria significar "se anadio un nuevo dataset" o "cambio la API del SDK".

La fuente unica de version es `pyproject.toml` (`project.version`). `src/chile_hub/__init__.py` lee la version dinamicamente desde `pyproject.toml` en desarrollo, o desde los metadatos de la rueda PyPI en instalacion. `python-semantic-release` automatiza los bumps de version basandose en Conventional Commits, usando `tool.semantic_release.version_toml` para escribir en `pyproject.toml`. Los commits de datos llevan el prefijo `chore(data):` y se excluyen del changelog de release mediante `exclude_commit_patterns`.

Los datos normalizados residen en `data/normalized/` e incluyen `pipeline_metadata.json` con su propia marca de tiempo `generated_at_utc`. La frescura de cada dataset se controla mediante `freshness_policy` con `max_age_hours` especifico (72h para indicadores diarios, 10 anos para censo, 90 dias para capas estables). El pipeline CI/CD publica actualizaciones de datos diariamente mediante el job `publish` en el workflow `pipeline-check.yml`.

## Decision

Se decidio un modelo de versionado dual:

1. **Version del paquete (SemVer clasico):** `pyproject.toml` define la version del software. `python-semantic-release` incrementa major para cambios incompatibles en la API publica o en los contratos de esquema, minor para nuevas funcionalidades (nuevos datasets, nuevos extractores), y patch para correcciones. Los cambios en datos exclusivamente (actualizaciones diarias de indicadores) NO producen bump de version.
2. **Frescura de datos (independiente):** Cada dataset tiene su propia linea de tiempo de actualizacion, registrada en `refreshed_at_utc` dentro de su metadata. El sistema de `freshness_policy` compara la hora de actualizacion contra `max_age_hours` para determinar si los datos estan "fresh", "stale" o "unknown". Esto se refleja en los reportes `hub_health.json`, `provenance_report.json` y `drift_report.json`.
3. **Bundle publico congelado:** El ZIP publico en GitHub Releases se genera con una version del paquete concreta. Aunque los datos se actualicen a diario via CI, la version del ZIP corresponde a la del release. Los datos intermedios se consideran "snapshots de desarrollo" hasta el proximo tag.

## Consecuencias

- Positivas: Los consumidores de la libreria Python no reciben bumps de version espurios por actualizaciones de datos. Los cambios de esquema (que si rompen compatibilidad) quedan correctamente señalados como major. El changelog se mantiene legible sin ruido de commits `chore(data):`. La frescura es monitoreable dataset por dataset.
- Negativas: La version del paquete no refleja la antigueedad de los datos. Un usuario con `chile-hub==1.5.0` puede tener datos de hace meses si no ejecuta el pipeline. La solucion es que los datos se distribuyen como artefactos fuera del wheel (via GitHub Releases o el sitio publico), no dentro del paquete pip.

## Alternativas consideradas

- **Calendario semantico (ej. 2026.06.18)** -- Se descarto porque no comunica la gravedad de los cambios. Un cambio de esquema breaking seria indistinguible de una actualizacion diaria de datos.
- **Version unica que incluye datos (ej. 1.5.0+data20260618)** -- Se descarto porque complica el tooling de `python-semantic-release` y no es compatible con el formato de version PEP 440 usado por PyPI.
- **Dos numeros de version separados (pyproject.toml + data/VERSION)** -- Se descarto porque el consumidor tendria que revisar dos numeros para saber si su instalacion esta al dia. El modelo de frescura por dataset es mas granular y util.
