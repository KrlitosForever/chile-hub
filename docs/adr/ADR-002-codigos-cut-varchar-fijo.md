# ADR-002: Codigos CUT como VARCHAR de largo fijo

**Fecha:** 2026-06-18
**Estado:** accepted
**Decision:** Todos los codigos territoriales CUT (Codigo Unico Territorial) se almacenan como string de largo fijo -- region "01" (2 caracteres), provincia "011" (3 caracteres), comuna "01101" (5 caracteres) -- nunca como entero numerico.

## Contexto

Los codigos CUT (Codigo Unico Territorial) son el sistema oficial de identificacion geografica de Chile. Cada region, provincia y comuna tiene un codigo numerico de 2, 3 y 5 digitos respectivamente. El codigo de comuna "01101" corresponde a la comuna de Iquique en la region de Tarapaca: los primeros 2 digitos son la region ("01"), los 3 primeros son la provincia ("011"), y los 5 completos son la comuna ("01101").

Estos codigos son la clave primaria que vincula los 15 datasets del catalogo. La mayoria de los datasets incluyen `codigo_comuna` como columna de join, y varios requieren integridad referencial contra la tabla maestra de comunas. En `src/validation.py`, funciones como `validate_finanzas_municipales`, `validate_establecimientos_salud` y `validate_distritos_electorales` verifican que `codigo_comuna` tenga exactamente 5 caracteres mediante `_invalid_fixed_length_count()`.

Ademas, el dataset `comunas` incluye el campo `nombre_comuna_clean` para busqueda difusa: el nombre de la comuna en lowercase, sin tildes ni caracteres especiales. Esto permite busquedas textuales insensibles a mayusculas o acentos, complementando la clave primaria CUT.

## Decision

Se decidio que todos los codigos CUT se almacenan exclusivamente como cadenas de texto (tipo `string` en Polars, `TEXT` en DuckDB/SQLite) con largos fijos validados por contrato:

- `codigo_region`: string de 2 caracteres (ej. "01", "13")
- `codigo_provincia`: string de 3 caracteres (ej. "011", "131")
- `codigo_comuna`: string de 5 caracteres (ej. "01101", "13101")

Los contratos JSON Schema en `contracts/datasets/*.schema.json` definen `fixed_width_columns` con estos largos. Por ejemplo, `contracts/datasets/comunas.schema.json` declara `"codigo_comuna": 5`. La funcion `verify_dataset_contract()` en `scripts/verify_pipeline.py` verifica que todas las filas cumplan el ancho exacto. Cualquier violacion detiene el pipeline con `SystemExit`.

El campo `nombre_comuna_clean` se genera durante la normalizacion aplicando lowercase y eliminacion de tildes, y se incluye como columna requerida en el contrato de `comunas`.

## Consecuencias

- Positivas: Los joins entre datasets son deterministicos y no sufren problemas de truncamiento de ceros a la izquierda (un entero `1101` vs el string `"01101"`). La validacion de longitud fija es simple y robusta. Los codigos se pueden usar directamente en URL de fuentes oficiales que esperan el formato string. La busqueda por `nombre_comuna_clean` permite encontrar "iquique" escribiendo "Iquique" o "IQUIQUE".
- Negativas: Los codigos como string ocupan mas espacio en disco que como enteros (5 bytes vs 2-4 bytes). Las columnas CUT no se pueden usar en operaciones aritmeticas (innecesario para claves). Existe riesgo de confusion si un consumidor convierte automaticamente el string a entero y pierde los ceros a la izquierda.

## Alternativas consideradas

- **Codigos como entero smallint** -- Se descarto porque un entero pierde los ceros a la izquierda ("01" -> 1), rompiendo la compatibilidad con fuentes oficiales y con sistemas externos que esperan el formato string. Requiere padding constante en cada join.
- **Codigos como string sin validacion de largo** -- Se descarto porque permitiria datos corruptos como "123" o "123456" que no corresponden a ningun CUT real. El ancho fijo es parte del contrato de datos.
- **Codigos como CHAR en SQL y string en Parquet** -- Equivalente funcional a la decision actual. Se eligio `string` de Polars como tipo unico porque es el formato portable entre todos los formatos de salida (Parquet, DuckDB, SQLite, JSON, Excel).
