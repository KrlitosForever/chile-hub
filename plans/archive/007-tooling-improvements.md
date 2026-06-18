# Plan 007: Mejoras de tooling — pre-commit, editorconfig, make refresh, uv.lock, CI cache, guarda de versión de Python

> **Instrucciones para el ejecutor**: Sigue este plan paso a paso. Ejecuta cada
> comando de verificación y confirma el resultado esperado antes de pasar al
> siguiente paso. Si ocurre algo de la sección "Condiciones de detención", detente e
> informa — no improvises. Al terminar, actualiza la fila de estado de este plan
> en `plans/README.md`.

> **Verificación de desviación (ejecutar primero)**:
> `git diff --stat ba2f434..HEAD -- Makefile .pre-commit-config.yaml pyproject.toml .gitignore uv.lock .github/workflows/pipeline-check.yml`
> Si alguno de estos archivos cambió desde que se escribió este plan, compara los
> extractos de "Estado actual" con el código real antes de proceder; si hay
> discrepancia, trátalo como una condición de detención.

## Estado

- **Prioridad**: P1
- **Esfuerzo**: S
- **Riesgo**: BAJO
- **Depende de**: 004 (dev-requirements.txt debe existir con ruff)
- **Categoría**: dx
- **Planificado en**: commit `ba2f434`, 2026-06-13
- **Resuelto**: 2026-06-18 — `.editorconfig`, instalación de pre-commit en `make bootstrap`, lint/format en `make refresh`, y cache de pip en CI están presentes. `uv.lock` no está versionado.

## Por qué es importante

Seis mejoras de tooling de bajo esfuerzo que en conjunto eliminan fricción
diaria de desarrollo:

1. **Pre-commit nunca se instala**: el archivo `.pre-commit-config.yaml`
   existe pero `make bootstrap` no ejecuta `pre-commit install`. Los hooks
   solo corren en CI.
2. **Sin `.editorconfig`**: desarrolladores con distintos editores pueden
   introducir inconsistencias de indentación, fin de línea, o encoding.
3. **`make refresh` no corre lint**: el ciclo principal de desarrollo omite
   verificaciones de estilo que solo se descubren en CI.
4. **`uv.lock` vacío**: 8 líneas sin dependencias reales. Genera confusión
   sobre cuál es el package manager real del proyecto.
5. **CI landing job sin pip cache**: ~20 segundos extra por ejecución instalando
   playwright desde cero.
6. **`make bootstrap` no valida versión de Python**: si el sistema tiene
   Python < 3.13, falla con errores crípticos de pip en vez de un mensaje
   claro.

## Estado actual

### pre-commit no instalado

- `Makefile:62-66` (`bootstrap`) no incluye `pre-commit install`:

```makefile
bootstrap:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	$(VENV_DIR)/bin/python -m pip install -r requirements.txt
	$(VENV_DIR)/bin/python -m playwright install chromium
```

- `.pre-commit-config.yaml` existe con ruff-check, ruff-format,
  trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict.

### Sin .editorconfig

No existe archivo `.editorconfig` en la raíz del proyecto.

### make refresh sin lint

```makefile
# Makefile:109
refresh: extract build verify test verify-landing
```

vs.

```makefile
# Makefile:107
check: build verify test verify-landing lint format-check
```

### uv.lock vacío

```toml
# uv.lock (completo, 8 líneas)
version = 1
requires-python = ">=3.13"

[[package]]
name = "chile-hub"
version = "0.1.0"
source = { virtual = "." }
```

### CI landing job sin pip cache

```yaml
# .github/workflows/pipeline-check.yml:131-135
- name: Set up Python
  uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    # Falta: cache: pip, cache-dependency-path: requirements.txt
```

Comparar con el job `build-and-test` (líneas 67-70) que SÍ tiene `cache: pip`.

### Bootstrap sin validación de versión de Python

`Makefile:62` usa `python3` sin verificar que sea ≥ 3.13.

## Comandos que necesitarás

| Propósito | Comando | Esperado al éxito |
|-----------|---------|-------------------|
| Bootstrap | `make bootstrap` | exit 0 |
| Lint check | `make lint` | exit 0 |
| Format check | `make format-check` | exit 0 |
| Pipeline completo | `make refresh` | exit 0 (ahora incluye lint + format-check) |
| Ejecutar pre-commit | `.venv/bin/python -m pre_commit run --all-files` | exit 0 |

## Alcance

**In scope** (archivos a crear o modificar):
- `Makefile` — agregar pre-commit install a bootstrap, lint/format a refresh,
  guarda de versión de Python, y eliminar targets redundantes
- `.editorconfig` — **CREAR** nuevo archivo
- `.pre-commit-config.yaml` — agregar hooks de seguridad
- `.gitignore` — agregar `.ruff_cache/`
- `uv.lock` — regenerar o eliminar
- `.github/workflows/pipeline-check.yml` — agregar cache al job landing

**Out of scope** (NO tocar):
- `requirements.txt` o `dev-requirements.txt` — ya modificados en plan 004.
- `src/` — sin cambios de código.
- `pyproject.toml` — la migración completa a pyproject.toml es un plan
  futuro separado.

## Pasos

### Paso 1: Agregar pre-commit install a make bootstrap

Agregar `pre-commit` a `dev-requirements.txt` (plan 004) y luego en
`make bootstrap`:

```makefile
bootstrap:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	$(VENV_DIR)/bin/python -m pip install -r requirements.txt
	$(VENV_DIR)/bin/python -m pip install -r dev-requirements.txt
	$(VENV_DIR)/bin/python -m playwright install chromium
	$(VENV_DIR)/bin/python -m pre_commit install
```

**Verificar**: `make bootstrap` → instala el hook de pre-commit en
`.git/hooks/pre-commit`. `git commit --dry-run` debería mostrar que los hooks
se ejecutarían.

### Paso 2: Crear .editorconfig

Crear `.editorconfig` en la raíz:

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{json,yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

**Verificar**: El archivo existe en la raíz. `make lint` → exit 0 (ruff no debería
reportar problemas de estilo nuevos).

### Paso 3: Agregar lint y format-check a make refresh

```makefile
refresh: extract build verify test verify-landing lint format-check
```

**Verificar**: `make refresh` → ejecuta lint y format-check después de los
smoke tests. Si el código actual tiene violaciones de estilo, `make refresh`
fallará — en ese caso, corregir las violaciones con `make lint-fix` y
`make format` primero, luego reintentar.

### Paso 4: Agregar hooks de seguridad a pre-commit

En `.pre-commit-config.yaml`, bajo el repo `pre-commit-hooks`, agregar:

```yaml
- id: detect-private-keys
- id: check-added-large-files
  args: ['--maxkb=500']
- id: check-json
```

**Verificar**: `.venv/bin/python -m pre_commit run --all-files` → exit 0.
No debería encontrar claves privadas ni archivos grandes en el repo actual.

### Paso 5: Agregar .ruff_cache a .gitignore

Agregar la línea `.ruff_cache/` en `.gitignore`, junto a `.mypy_cache/`.

**Verificar**: `git status` no muestra `.ruff_cache/` como untracked.

### Paso 6: Resolver uv.lock

Dos opciones:

**Opción A (recomendada)**: Eliminar `uv.lock` ya que el proyecto usa pip
como package manager (`Makefile`, CI, instrucciones). Agregar `uv.lock` a
`.gitignore`.

**Opción B**: Si se prefiere mantener uv como alternativa, regenerar con
`uv lock` (requiere tener uv instalado).

**Verificar**: Opción A: `uv.lock` no existe en el working tree. Opción B:
`uv.lock` contiene todas las dependencias de `requirements.txt`.

### Paso 7: Agregar pip cache al job landing de CI

En `.github/workflows/pipeline-check.yml`, job `landing`, agregar:

```yaml
- name: Set up Python
  uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: pip
    cache-dependency-path: requirements.txt
```

**Verificar**: El job `landing` ahora tiene `cache: pip` igual que `build-and-test`.

### Paso 8: Agregar guarda de versión de Python en bootstrap

Al inicio de `make bootstrap`:

```makefile
bootstrap:
	@python3 -c "import sys; v=sys.version_info; ok=v>=(3,13); sys.exit(0 if ok else f'Python 3.13+ requerido, se encontró {v.major}.{v.minor}')"
	python3 -m venv $(VENV_DIR)
	...
```

**Verificar**: En un sistema con Python 3.13+, `make bootstrap` procede
normalmente. En un sistema con Python 3.12 o anterior, `make bootstrap`
falla inmediatamente con un mensaje claro.

## Plan de pruebas

- `make bootstrap` debe completar sin errores.
- `.venv/bin/python -m pre_commit run --all-files` → exit 0.
- `make refresh` → exit 0 (incluye lint + format-check).
- `make lint` → exit 0.
- `make format-check` → exit 0.
- Verificar que `.editorconfig` es reconocido por VS Code (abrir un archivo
  .py y confirmar que la indentación es 4 espacios).

## Criterios de finalización

- [ ] `make bootstrap` ejecuta `pre-commit install` y valida Python ≥ 3.13
- [ ] `.editorconfig` existe en la raíz con la configuración especificada
- [ ] `make refresh` incluye `lint format-check` en su secuencia
- [ ] `.pre-commit-config.yaml` tiene `detect-private-keys`,
      `check-added-large-files`, y `check-json`
- [ ] `.gitignore` incluye `.ruff_cache/`
- [ ] `uv.lock` fue eliminado o regenerado correctamente
- [ ] `.github/workflows/pipeline-check.yml` job `landing` tiene `cache: pip`
- [ ] `.venv/bin/python -m pre_commit run --all-files` → exit 0
- [ ] `make lint` → exit 0
- [ ] `make format-check` → exit 0

## Condiciones de detención

Detente e informa (no improvises) si:

- Los archivos en "Estado actual" no coinciden con los extractos.
- `make bootstrap` falla por alguna de las adiciones.
- `make refresh` falla por violaciones de lint/format existentes (corregir
  con `make lint-fix && make format` y reintentar).
- `pre-commit run --all-files` encuentra falsos positivos que no se pueden
  resolver razonablemente.
- El cambio en CI no se puede verificar localmente (no hay entorno de CI).
  En ese caso, reportar los cambios planeados y marcarlos como no verificados.

## Notas de mantenimiento

- Los hooks de pre-commit se ejecutan automáticamente en `git commit`. Si un
  desarrollador necesita saltarlos temporalmente: `git commit --no-verify`.
- `.editorconfig` es respetado por VS Code (con extensión EditorConfig),
  PyCharm, vim, y Emacs. Cada editor necesita su plugin correspondiente.
- La eliminación de `uv.lock` es reversible. Si en el futuro el proyecto
  migra a uv como package manager principal, se regenera con `uv lock`.
- El cache de pip en CI usa el hash de `requirements.txt` como clave. Si las
  dependencias cambian, el cache se invalida automáticamente.
