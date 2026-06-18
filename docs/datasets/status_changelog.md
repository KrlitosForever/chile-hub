# Estado y registro de cambios de datasets

## Descripción

Artefactos legibles por máquina para monitorear la salud del hub sin leer todos los reportes Markdown.

## Artefactos

- `data/normalized/dataset_status.json`: estado actual por dataset.
- `data/normalized/dataset_changelog.json`: cambios entre el build actual y el metadata normalizado anterior, cuando existe.

## Campos principales

`dataset_status.json` incluye `validation_status`, `source_mode`, `freshness`, `record_count`, `expected_record_count`, `coverage_status`, `redistribution_status`, `refreshed_at_utc`, `warnings` y `recommended_action`.

`dataset_changelog.json` incluye deltas de filas, campos agregados/removidos, cambios de modo de fuente, frescura y validación.

## Uso

```python
from chile_hub import ChileHub

hub = ChileHub()
status = hub.dataset_status()
changelog = hub.dataset_changelog()
```

## Registro de cambios

- v1: Artefactos agregados al bundle y expuestos por API/CLI.
