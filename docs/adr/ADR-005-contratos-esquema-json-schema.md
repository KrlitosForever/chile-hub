# ADR-005: Contratos de esquema como JSON Schema

**Fecha:** 2026-06-18
**Estado:** accepted
**Decision:** Cada dataset tiene un contrato de esquema en formato JSON, almacenado en `contracts/datasets/{dataset}.schema.json`. La verificacion contra estos contratos se ejecuta como parte del pipeline de build y verifica tipos, claves primarias, columnas de ancho fijo y cobertura.

## Contexto

chile-hub mantiene 15 datasets que se publican en multiples formatos: Parquet, DuckDB, SQLite, JSON y Excel. Cada formato tiene reglas distintas de tipado y representacion. Para garantizar que todos los formatos sean conformes y que los cambios de esquema sean detectados temprano, se necesita una fuente unica de verdad para la estructura de cada dataset.

Inicialmente, las validaciones de esquema estaban dispersas en `src/validation.py` como funciones Python independientes. Cada funcion verificaba columnas, tipos y cardinalidades con logica ad-hoc. Esto funcionaba pero tenia desventajas: no habia una definicion declarativa del esquema, no era posible generar documentacion automaticamente, y cualquier cambio de esquema requeria modificar codigo Python en lugar de un archivo de configuracion.

En `contracts/datasets/` existen actualmente 15 archivos `.schema.json`, uno por dataset. Cada contrato define `dataset`, `primary_key`, `required_columns`, `column_types`, `nullable_columns`, `fixed_width_columns`, `expected_record_count`, `coverage_policy` y `publish_outputs`. Por ejemplo, `contracts/datasets/comunas.schema.json` declara que `codigo_comuna` es string de 5 caracteres, clave primaria, y que se esperan 346 registros con cobertura total.

La funcion `verify_dataset_contract()` en `scripts/verify_pipeline.py` lee cada contrato y verifica contra el Parquet real: tipos de columna, unicidad de clave primaria, ancho de columnas fijas, y cantidad de registros esperados. Se invoca desde `verify_schema_contracts()` que itera sobre todos los datasets del catalogo.

Ademas, `load_schema_contract()` en `src/build_dev_db.py` carga el contrato durante el build para incrustar metadatos de esquema en `pipeline_metadata.json`, lo que permite la deteccion de cambios breaking entre builds mediante `_compute_dataset_change_severity()`.

## Decision

Se decidio que cada dataset debe tener un contrato JSON Schema con la siguiente estructura minima:

```json
{
  "dataset": "nombre_dataset",
  "primary_key": ["columna_pk"],
  "required_columns": ["col1", "col2"],
  "column_types": { "col1": "string", "col2": "integer" },
  "nullable_columns": [],
  "fixed_width_columns": { "codigo_comuna": 5 },
  "expected_record_count": 346,
  "coverage_policy": "full",
  "publish_outputs": ["parquet", "json"]
}
```

Estos contratos se verifican en dos momentos:

1. **Durante el build** (`src/build_dev_db.py`): `load_schema_contract()` carga el contrato para incrustar `contract_primary_key`, `contract_required_columns`, `contract_column_types` y `contract_nullable_columns` en los metadatos enriquecidos de cada dataset. Esto alimenta el changelog de esquema entre builds consecutivos.
2. **Durante la verificacion** (`scripts/verify_pipeline.py`): `verify_schema_contracts()` lee cada contrato, carga el Parquet correspondiente, y ejecuta `verify_dataset_contract()` que verifica tipos, claves, ancho fijo, cobertura y outputs esperados. Cualquier discrepancia causa `SystemExit`.

Los cambios de esquema detectados por comparacion de contratos se clasifican en severidades: `major` (cambio de clave primaria, columna requerida eliminada, cambio de tipo incompatible), `minor` (nuevas columnas opcionales) y `patch` (cambios en cardinalidad de registros).

## Consecuencias

- Positivas: Los contratos son declarativos y legibles por humanos y maquinas. La verificacion contra tipos reales de Polars detecta discrepancias entre el contrato y los datos publicados. El changelog de esquema entre builds permite identificar cambios breaking automaticamente. Los contratos pueden generar documentacion y codigo de validacion en otros lenguajes.
- Negativas: El contrato debe mantenerse sincronizado manualmente con el extractor y la logica de transformacion. Si se anade una columna en el extractor pero no se actualiza el contrato, la verificacion fallara. Algunas validaciones complejas (sumas de cohortes demograficas, rangos de porcentajes) no se pueden expresar en el contrato y permanecen en `src/validation.py`, creando dos fuentes de verdad parciales.

## Alternativas consideradas

- **Validacion solo en Python ad-hoc** (como existia originalmente) -- Se descarto porque mezclaba definicion de esquema con logica de validacion, dificultando la auditoria y la generacion de documentacion. Sin contratos declarativos, detectar cambios breaking entre releases requeria diff manual de los DataFrames.
- **JSON Schema draft-07 completo con validacion via `jsonschema`** -- Se descarto porque el schema de Polars/Parquet es mas sencillo que un JSON Schema completo. Los tipos de Polars (String, Int64, Float64, Date, Boolean) no se mapean uno a uno con JSON Schema. El formato propio de chile-hub es mas expresivo para las necesidades del proyecto (ancho fijo, cobertura esperada, outputs).
- **Protocol Buffers / Avro / Arrow Schema** -- Se descarto porque anade una dependencia de compilacion y complica el tooling. JSON es universal, no requiere compilacion, y es directamente legible en el repositorio.
