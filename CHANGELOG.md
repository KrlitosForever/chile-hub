# Changelog

This project uses Conventional Commits and `python-semantic-release` to generate
release notes for PyPI releases.

Data-only refresh commits such as `chore(data): daily refresh [skip ci]` do not
represent software releases and are intentionally excluded from release notes.

## 1.1.0 - 2026-06-17

### Added

- Added four new public dataset surfaces: `finanzas_municipales`,
  `resultados_educacionales`, `indicadores_urbanos_siedu`, and derived
  `perfil_territorial_comunal`.
- Added extractor, staging metadata, centralized validation, normalized
  Parquet/JSON, DuckDB, SQLite, Excel, catalog, provenance, redistribution,
  health, bundle, CI, and docs integration for the new layers.
- Added machine-readable operational artifacts `dataset_status.json` and
  `dataset_changelog.json`.
- Added `ChileHub.dataset_status()`, `ChileHub.dataset_changelog()`, and matching
  CLI commands `chile-hub dataset-status` and `chile-hub dataset-changelog`.

### Changed

- Expanded the active catalog from 10 to 14 datasets.
- Updated the landing smoke tests and top-issue expectations so fallback layers
  can become the correctly surfaced operational priority.

### Notes

- `finanzas_municipales`, `resultados_educacionales`, and
  `indicadores_urbanos_siedu` currently build in `fallback` mode until stable
  direct live exports are configured. `make verify` passes; `make verify-live`
  is expected to reject those layers until live extraction is completed.

## 1.0.1 - 2026-06-17

### Added

- Added `pytest-cov` to the development toolchain, with local `make coverage`
  support and CI coverage reporting for the `src/` package.
- Updated development and release tooling pins to their latest compatible stable
  versions, including `build`, `pre-commit`, `pytest-cov`, and
  `python-semantic-release`.

### Fixed

- Restored Python 3.10 runtime compatibility by replacing Python 3.11-only
  `datetime.UTC` usage with `datetime.timezone.utc`.
- Fixed the PyPI release workflow so `python-semantic-release` skips its
  internal build step and the pinned job environment performs the package build.
