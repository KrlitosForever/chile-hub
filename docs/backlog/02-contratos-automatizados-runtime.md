# [02] Validacion de contratos JSON Schema en runtime

**Scorecard:** `docs/backlog/scorecard.md`
**Estado:** Pendiente
**Impacto:** Alto
**Esfuerzo estimado:** Medio
**Riesgo:** Bajo
**Target:** Q3 2026

---

## Problema que resuelve

ChileHub tiene **15 contratos JSON Schema** en `contracts/datasets/*.schema.json`
(ver `comunas.schema.json` como ejemplo: define primary_key, column_types,
fixed_width_columns, expected_record_count, coverage_policy). Sin embargo, estos
contratos solo se usan en `scripts/verify_pipeline.py`, un script independiente
que no forma parte del flujo normal de la libreria.

Como resultado:

1. Un usuario que carga un dataset via `ChileHub.load_polars('comunas')` obtiene
   datos sin ninguna garantía de que cumplan el contrato.
2. El pipeline de build (`build_dev_db.py`) ejecuta validaciones ad-hoc via
   `src/validation.py` (14 funciones `validate_*`) que estan duplicadas respecto
   a los contratos JSON Schema.
3. No hay forma de que un usuario verifique la integridad de un dataset en tiempo
   de carga sin ejecutar `scripts/verify_pipeline.py` manualmente.

---

## Evidencia actual

### Contratos existentes (no usados en runtime)

- **`contracts/datasets/comunas.schema.json`**: define primary_key `["codigo_comuna"]`,
  column_types (`codigo_region: string`, etc.), fixed_width_columns
  (`codigo_region: 2`, `codigo_comuna: 5`), expected_record_count: 346,
  coverage_policy: "full".
- **14 contratos adicionales** en `contracts/datasets/*.schema.json`:
  `censo_comunal`, `censo_hogares_viviendas`, `comunas_enriquecidas`,
  `distritos_electorales`, `empresas`, `establecimientos_educacionales`,
  `establecimientos_salud`, `finanzas_municipales`, `indicadores`,
  `indicadores_urbanos_siedu`, `perfil_territorial_comunal`, `provincias`,
  `regiones`, `resultados_educacionales`.

### Verificacion solo en script independiente

- **`scripts/verify_pipeline.py`**, funcion `verify_dataset_contract()` (linea 115):
  verifica required_columns, column_types, primary_key, fixed_width_columns,
  coverage_policy y publish_outputs.
- **`verify_schema_contracts()`** (linea 167): itera el catalogo y llama a
  `verify_dataset_contract` para cada dataset.
- **Uso**: solo se ejecuta manualmente via `python scripts/verify_pipeline.py`.

### Validacion duplicada en `src/validation.py`

- `validate_comunas()` (linea 46): verifica unicidad de `codigo_comuna` y conteo
  de filas — logica que ya esta en el contrato JSON Schema como primary_key y
  expected_record_count.
- Patron similar en las otras 13 funciones `validate_*`.
- **`load_schema_contract()` en `build_dev_db.py`** (linea 723): carga el contrato
  pero solo se usa internamente en `build_dataset_quality()` (linea 1651) para
  puntuar calidad, no para validar en runtime.

---

## Propuesta de implementacion

### Paso 1: Crear `ChileHub.validate_dataset()` en `core.py`

Agregar metodo publico en `src/chile_hub/core.py` (junto a `load_polars` en linea 211):

```python
def validate_dataset(self, dataset_name: str) -> dict[str, Any]:
    """Valida un dataset contra su contrato JSON Schema."""
    contract_path = self.root_dir / "contracts" / "datasets" / f"{dataset_name}.schema.json"
    if not contract_path.exists():
        raise ChileHubError(f"Schema contract not found for '{dataset_name}'")
    contract = json.loads(contract_path.read_text())
    df = self.load_polars(dataset_name)
    return verify_dataset_contract(dataset_name, contract, df, self.get_dataset(dataset_name).get("outputs", {}))
```

**Referencia:** `load_polars()` esta en core.py linea 211. El metodo `root_dir` se
deriva en linea 28: `ROOT_DIR = Path(__file__).resolve().parents[2]`.

### Paso 2: Agregar parametro `validate=True` a `load_polars()`

Modificar `load_polars()` (linea 211-213) para aceptar `validate: bool = False`:

```python
def load_polars(self, dataset_name: str, validate: bool = False) -> pl.DataFrame:
    if validate:
        self.validate_dataset(dataset_name)
    path = self.get_output_path(dataset_name, "parquet")
    return pl.read_parquet(path)
```

### Paso 3: Migrar logica de verify_dataset_contract de script a libreria

Mover `verify_dataset_contract()` y `_contract_type()` de `scripts/verify_pipeline.py`
(lineas 100-164) a `src/chile_hub/core.py` o a un nuevo `src/chile_hub/validation.py`.

**Importante:** Mantener `scripts/verify_pipeline.py` funcional haciendo que importe
la funcion desde la libreria (retrocompatibilidad).

### Paso 4: Agregar comando CLI `chile-hub validate`

Agregar un subparser en `build_parser()` (`src/chile_hub/core.py`, linea 1247):

```
validate_parser = subparsers.add_parser("validate", help="Validar dataset contra su contrato")
validate_parser.add_argument("dataset", help="Nombre del dataset a validar")
validate_parser.add_argument(
    "--format",
    choices=["json", "text"],
    default="text",
    help="Formato de salida",
)
```

Implementar en `_main()` similar a otros comandos (ej. `check-sources` en linea 1541).

### Paso 5: Escribir tests

Agregar tests en `tests/test_validation.py`:
- Test que `validate_dataset('comunas')` pasa con datos actuales.
- Test que `validate_dataset('comunas')` falla si se corrompe el parquet.
- Test que `load_polars('comunas', validate=True)` llama a validate_dataset.
- Test que `chile-hub validate comunas` funciona desde CLI.

---

## Criterio de aceptacion

1. `ChileHub.validate_dataset('comunas')` retorna un dict con `{"dataset": "comunas",
   "status": "ok", "errors": []}` cuando los datos cumplen el contrato.
2. `ChileHub.validate_dataset('comunas')` retorna `status: "error"` con lista de
   errores si el parquet esta corrupto o faltan columnas.
3. `load_polars('comunas', validate=True)` ejecuta validacion antes de retornar
   el DataFrame (o lanza excepcion si falla).
4. `chile-hub validate comunas` imprime resultado en JSON o texto legible.
5. `scripts/verify_pipeline.py` sigue funcionando (importa desde libreria).
6. Todos los tests nuevos y existentes pasan.

---

## Dependencias

- `contracts/datasets/*.schema.json` deben estar actualizados y reflejar la
  estructura real de cada dataset. Verificar especialmente datasets en fallback
  donde el schema puede diferir (ej. `comunas` en fallback tiene 18 filas vs 346).
- Tests existentes en `tests/test_validation.py` sirven como base.

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|:-------|:-----------:|:-------:|:-----------|
| Contrato desactualizado respecto al dataset real | Media | Alto | Agregar CI job que ejecute `validate` sobre todos los datasets post-build |
| Performance: validar contrato cada vez que se carga | Baja | Medio | `validate=False` por defecto; el usuario opta explicitamente |
| Contrato muy estricto para datasets en fallback | Media | Medio | El contrato debe reflejar el estado real: ajustar `expected_record_count` para fallback |

---

## Notas de disenio

### Decision: validacion sincrona en `load_polars`

Se evaluo una alternativa asincrona (background validation thread) pero se descarto
porque complica la API. La validacion de ~15 datasets toma < 1 segundo, aceptable
para uso sincrono.

### Migracion progresiva

No se requiere refactorizar `src/validation.py` inmediatamente. Las 14 funciones
`validate_*` pueden coexistir con la validacion por contrato. A futuro, las
validaciones ad-hoc se pueden migrar a extensiones del JSON Schema.

### Integracion con `build_dev_db.py`

`build_dev_db.py` ya tiene `load_schema_contract()` (linea 723). Una vez migrada
la validacion, el pipeline de build podria usar `validate_dataset()` en vez de
llamar a las funciones de `src/validation.py` directamente.
