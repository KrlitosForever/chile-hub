# [03] Constantes de datasets como enumeracion (`Dataset`)

**Scorecard:** `docs/backlog/scorecard.md`
**Estado:** Pendiente
**Impacto:** Medio
**Esfuerzo estimado:** Medio
**Riesgo:** Bajo
**Target:** Q3 2026

---

## Problema que resuelve

Los nombres de dataset se pasan como **strings magicos** en todo el codigo base.
Esto causa:

1. **Errores silenciosos por typos**: `chile-hub show comuna` (sin 's') falla con
   mensaje de error, pero un typo en codigo interno puede pasar desapercibido.
2. **Sin autocompletado en IDE**: no hay un tipo que permita al editor sugerir
   nombres validos.
3. **Dificultad para refactorizar**: cambiar el nombre de un dataset requiere
   buscar y reemplazar en multiples archivos.
4. **Sin lugar centralizado para metadata**: informacion como "este dataset es
   Tier A", "su policy de frescura es X" esta desperdigada en `DATASET_CATALOG_CONFIG`
   (build_dev_db.py, linea 71-420) y en `Dataset` (no existe como tipo).

---

## Evidencia actual

### Strings magicos en toda la base

- **`src/chile_hub/core.py`**: `list_datasets()` (linea 189) retorna `entry["dataset"]`
  como strings; `get_dataset()` (linea 192) recibe `dataset_name: str`.
- **`src/chile_hub/cli.py`**: todos los subcomandos (`show`, `path`, `export`, etc.)
  reciben `dataset` como `str` sin tipado nominal.
- **`src/build_dev_db.py`**: `DATASET_CATALOG_CONFIG` (lineas 71-420) usa nombres
  como keys de dict: `"regiones"`, `"provincias"`, `"comunas"`, etc. La funcion
  `enrich_dataset_metadata()` (linea 696) itera sobre estas keys como strings.
- **`src/validation.py`**: 14 funciones `validate_*` nombradas con el dataset:
  `validate_comunas()`, `validate_regiones()`, etc. No hay un tipo compartido.
- **`scripts/verify_pipeline.py`**: linea 192: `catalog_names = {entry.get("dataset") ...}`
  como conjunto de strings.

### Validadores registrados en diccionario

- **`scripts/check_validation_registration.py`**: probablemente mantiene un
  mapeo `{nombre_string: funcion_validate}`. Sin el enum, este mapeo es fragil.

---

## Propuesta de implementacion

### Paso 1: Crear enum `Dataset` en `src/chile_hub/datasets.py`

Archivo nuevo `src/chile_hub/datasets.py`:

```python
from __future__ import annotations

import enum
from typing import Final


class Dataset(str, enum.Enum):
    """Enumeracion de todos los datasets curados por ChileHub.

    Uso:
        >>> Dataset.COMUNAS
        <Dataset.COMUNAS: 'comunas'>
        >>> Dataset.from_string('comunas')
        <Dataset.COMUNAS: 'comunas'>
    """

    REGIONES = "regiones"
    PROVINCIAS = "provincias"
    COMUNAS = "comunas"
    COMUNAS_ENRIQUECIDAS = "comunas_enriquecidas"
    INDICADORES = "indicadores"
    CENSO_COMUNAL = "censo_comunal"
    CENSO_HOGARES_VIVIENDAS = "censo_hogares_viviendas"
    ESTABLECIMIENTOS_SALUD = "establecimientos_salud"
    ESTABLECIMIENTOS_EDUCACIONALES = "establecimientos_educacionales"
    DISTRITOS_ELECTORALES = "distritos_electorales"
    FINANZAS_MUNICIPALES = "finanzas_municipales"
    RESULTADOS_EDUCACIONALES = "resultados_educacionales"
    INDICADORES_URBANOS_SIEDU = "indicadores_urbanos_siedu"
    EMPRESAS = "empresas"
    PERFIL_TERRITORIAL_COMUNAL = "perfil_territorial_comunal"

    @classmethod
    def from_string(cls, name: str) -> Dataset:
        """Resuelve un string a Dataset, con sugerencias si no coincide."""
        try:
            return cls(name)
        except ValueError:
            matches = get_close_matches(name, [m.value for m in cls], n=1)
            hint = f" Quizas quisiste decir '{matches[0]}'." if matches else ""
            raise ValueError(f"Dataset '{name}' no es valido.{hint}")

    @classmethod
    def values(cls) -> list[str]:
        return [m.value for m in cls]
```

### Paso 2: Actualizar API publica para aceptar `str | Dataset`

- `ChileHub.get_dataset()`: cambiar firma de `dataset_name: str` a
  `dataset_name: str | Dataset` y resolver con `Dataset.from_string()`.
- `ChileHub.load_polars()`: mismo cambio.
- `ChileHub.get_output_path()`: mismo cambio.
- `ChileHub.example_usage()`: mismo cambio.
- Mantener compatibilidad hacia atras: `Dataset` hereda de `str`, asi que
  `Dataset.COMUNAS` se puede pasar donde antes iba `"comunas"`.

### Paso 3: Actualizar CLI para resolver dataset a `Dataset`

En `src/chile_hub/cli.py`, en los comandos que reciben `dataset` como argumento
(show, path, example, export, artifacts), convertir el string a `Dataset` y
mostrar error claro si no coincide.

### Paso 4: Refactorizar `DATASET_CATALOG_CONFIG` (opcional, futuro)

A futuro, `DATASET_CATALOG_CONFIG` en `build_dev_db.py` podria pasar de
`dict[str, dict]` a `dict[Dataset, dict]`, pero esto requiere cambiar todas las
iteraciones. Dejarlo como `dict[str, dict]` por ahora y resolver con
`.value` donde sea necesario.

### Paso 5: Actualizar tests

- Test que `Dataset.from_string('comunas')` retorna `Dataset.COMUNAS`.
- Test que `Dataset.from_string('comuna')` lanza ValueError con sugerencia.
- Test que `hub.get_dataset(Dataset.COMUNAS)` funciona igual que
  `hub.get_dataset('comunas')`.
- Test que `load_polars(Dataset.REGIONES)` funciona.

---

## Criterio de aceptacion

1. `from chile_hub.datasets import Dataset` funciona.
2. `Dataset.from_string('comunas')` retorna `Dataset.COMUNAS`.
3. `Dataset.from_string('comuna')` lanza `ValueError` con sugerencia.
4. `hub.get_dataset(Dataset.COMUNAS)` retorna el mismo resultado que
   `hub.get_dataset('comunas')`.
5. `hub.load_polars(Dataset.REGIONES)` carga el dataset correctamente.
6. `chile-hub show comunas` sigue funcionando (input string se resuelve internamente).
7. Tests existentes pasan sin cambios.
8. `mypy --strict` no reporta errores de tipo nuevos en los modulos modificados.

---

## Dependencias

- Ninguna externa. Depende solo de la libreria estandar (`enum`).

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|:-------|:-----------:|:-------:|:-----------|
| Romper API publica si alguien pasa `str` y esperabamos `Dataset` | Baja | Alto | `Dataset` hereda de `str`, asi que `Dataset.COMUNAS` es compatible con cualquier codigo que espera un string |
| Olvidar actualizar un lugar que usa strings | Media | Bajo | CI con `mypy` detectara lugares donde el tipo es `str` pero deberia ser `str | Dataset` |
| El enum se desincroniza si se agrega un dataset | Baja | Medio | Agregar checklist de PR: "Si agregas un dataset, agregalo al enum `Dataset`" |

---

## Notas de disenio

### Decision: `class Dataset(str, enum.Enum)`

Heredar de `str` permite que `Dataset.COMUNAS` sea un string "comunas" en runtime,
lo que garantiza compatibilidad total con codigo legacy que espera `str`. Es el
patron recomendado por Python para enumeraciones que representan strings.

### Decision: archivo separado `src/chile_hub/datasets.py`

En vez de incluir el enum en `core.py` o `__init__.py`, se crea un archivo
dedicado para:
1. Evitar importaciones circulares (tanto `core.py` como `build_dev_db.py`
   pueden importarlo).
2. Mantener la enumeracion cerca de la metadata del dataset.
3. Permitir que herramientas externas importen solo el enum sin cargar toda
   la libreria.

### Alternativa considerada: `typing.Literal[...]`

Se considero `Literal["regiones", "provincias", ...]` como type alias, pero se
descarto porque:
1. No permite iteracion en runtime.
2. No tiene metodo `from_string()` con sugerencias.
3. No se puede usar en un `if type(x) is Dataset`.
