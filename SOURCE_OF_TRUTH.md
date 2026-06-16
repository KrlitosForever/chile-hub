# SOURCE_OF_TRUTH.md — Master Navigation Index

Read this first. Then follow the pointers. Do not read full files cold.

---

## What this repo is

`chile-hub` is a curated, reproducible data layer over official Chilean public datasets.
It runs an extract → build → validate → publish pipeline that produces Parquet, DuckDB,
JSON, and ZIP artefacts consumable in a single line of code, plus a static landing page
and a Python CLI/API (`ChileHub`). The goal is fewer, cleaner, trustworthy datasets —
not comprehensive coverage.

---

## Document ownership

| Document | Owns | When to read |
|---|---|---|
| **`SOURCE_OF_TRUTH.md`** ← you are here | Navigation index, invariants summary, file + task map | Always first — ~70 lines |
| **`AGENTS.md`** | Full pipeline rules, legal policy, 7-step dataset-adding workflow, CI/CD jobs, antipatterns, code conventions | Adding a dataset · debugging pipeline · legal questions · CI changes |
| **`CLAUDE.md`** | Shell commands, CodeGraph navigation, source map with line anchors, type/convention quick reference | Running commands · navigating large files · looking up types |

---

## 5 non-negotiable invariants

1. **CUT codes are fixed-length strings** — `"01"` (region), `"011"` (province), `"01101"` (commune). Never int.
2. **Fail loudly** — `raise SystemExit(...)` on validation errors. Never silent warnings for bad data.
3. **`data/raw/` is append-only** — audit snapshots. Never modify after writing.
4. **`nombre_comuna_clean` must exist** — lowercase, no accents, no `ñ`. Join key for fuzzy text matching.
5. **Paths always relative to `__file__`** — never CWD-relative (`"data"`); breaks in CI.

→ Full invariant details with code examples: **`AGENTS.md §4`**

---

## File map — scope your reads

```
src/
├── extractors/
│   ├── base.py                    BaseExtractor ABC — 57 lines, read whole
│   └── {name}_extractor.py        One file per dataset, extends BaseExtractor
├── validation.py                  ALL validate_*() — 248 lines, read whole
├── build_dev_db.py                ~2 300 lines — scope reads:
│   L27-35   imports from validation.py
│   L1610+   validations = {…} block (where validators are called)
├── pipeline_status_utils.py       Report builders (health, catalog, redistribution)
└── chile_hub.py                   ~1 400 lines — scope reads:
    L26      ChileHub class definition
    L26-150  Full public API surface

data/
├── raw/        Audit snapshots — append-only, never edit
├── staging/    {dataset}.csv + {dataset}.metadata.json — pipeline inputs
└── normalized/ Generated artefacts — NEVER edit manually; always regenerate

tests/
├── test_chile_hub.py        Requires data/normalized/ — run `make build` first
├── test_extractors.py       No normalized data required
└── test_pipeline_logic.py   No normalized data required
```

---

## Common tasks → where to look

| Task | Go to |
|---|---|
| Run full pipeline | `CLAUDE.md` → **Essential commands** → `make refresh` |
| Run one step | `CLAUDE.md` → `make extract` / `make build` / `make test` |
| Add a new dataset | **`AGENTS.md §5`** — 7-step checklist |
| Write a `validate_*()` function | `src/validation.py` — then import in `build_dev_db.py` |
| Understand CI/CD jobs | **`AGENTS.md §9`** |
| Check legal redistribution status of a source | **`AGENTS.md §6`** |
| Check what antipatterns to avoid | **`AGENTS.md §10`** |
| Navigate large files without cold-reading | `CLAUDE.md` → **CodeGraph** section |
| Find where a symbol is defined | `codegraph find <name>` or `grep -n "def <name>" src/` |
| Read ChileHub public API | `src/chile_hub.py L26-150` |
| Read all validation logic | `src/validation.py` (248 lines — safe to read whole) |
| Read extractor contract | `src/extractors/base.py` (57 lines — safe to read whole) |

---

## Pipeline flow (one-glance summary)

```
make extract        →  data/staging/{dataset}.{csv,metadata.json}  +  data/raw/
make build          →  data/normalized/  (Parquet, DuckDB, JSON, ZIP, manifests)
make verify         →  integrity check (SHA-256, record counts, schema)
make test           →  pytest (reads normalized/ — does NOT run pipeline)
make verify-landing →  Playwright smoke tests against index.html
```

**One command for everything:** `make refresh` runs all five in order + lint + format-check.
