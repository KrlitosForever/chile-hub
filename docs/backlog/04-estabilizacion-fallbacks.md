# [04] Estabilizacion de datasets en modo fallback

**Scorecard:** `docs/backlog/scorecard.md`
**Estado:** Pendiente
**Impacto:** Alto
**Esfuerzo estimado:** Alto
**Riesgo:** Medio
**Target:** Q3 2026

---

## Problema que resuelve

Cuatro datasets operan actualmente en **modo fallback**: `finanzas_municipales`,
`resultados_educacionales`, `indicadores_urbanos_siedu` y `perfil_territorial_comunal`.
Esto significa que:

1. Los datos provienen de fuentes embebidas o estaticas en vez de los extractores
   en vivo (`source_mode == "fallback"`).
2. La cardinalidad de los datasets es limitada: por ejemplo, `comunas` en fallback
   usa 18 filas (linea 65 de `src/validation.py`: `FALLBACK_COMUNAS_COUNT = 18`)
   versus 346 en modo live.
3. Los metadatos indican "impact: Valores provenientes de fallback local; no
   representan el ultimo snapshot live" (linea 583 de `build_dev_db.py`).
4. La cobertura y frescura no se pueden garantizar, lo que degrada la confianza
   del hub en su conjunto.

---

## Evidencia actual

### Datasets afectados

1. **`finanzas_municipales`**
   - Extract: `src/extractors/sinim_finanzas_extractor.py`
   - Fuente: datos abiertos SINIM (Subdere)
   - Contrato: `contracts/datasets/finanzas_municipales.schema.json`
   - Estado actual: fallback (extractor no produce datos vivos consistentemente)

2. **`resultados_educacionales`**
   - Extract: `src/extractors/mineduc_resultados_extractor.py`
   - Fuente: MINEDUC (Ministerio de Educacion)
   - Contrato: `contracts/datasets/resultados_educacionales.schema.json`
   - Estado actual: fallback

3. **`indicadores_urbanos_siedu`**
   - Extract: `src/extractors/siedu_extractor.py`
   - Fuente: SIEDU (Sistema de Indicadores de Educacion)
   - Contrato: `contracts/datasets/indicadores_urbanos_siedu.schema.json`
   - Estado actual: fallback

4. **`perfil_territorial_comunal`**
   - Extract: no tiene extractor propio; es dataset derivado (linea 2035 de
     `build_dev_db.py`: `build_perfil_territorial_comunal()`)
   - Fuente: depende de otros 9 datasets como upstreams
     (linea 3093: nota "upstreams: comunas,censo_comunal,...")
   - Estado actual: fallback cuando cualquiera de sus upstreams esta en fallback
     (lineas 3070-3086 de `build_dev_db.py`)

### Logica de fallback en build_dev_db.py

- Lineas 3070-3086: `source_mode` se determina como `"live"` solo si todos los
  metadatos de upstreams tienen `source_mode == "live"`, caso contrario `"fallback"`.
- Linea 562-583 en `build_degradation()`: cuando `source_mode == "fallback"`,
  se anade advertencia "desde fallback embebido".
- Linea 670: `build_drift()` considera fallback como estado degradado.

### Validacion en modo fallback

- `src/validation.py`, linea 64-69: `validate_comunas()` trata `FALLBACK_COMUNAS_COUNT`
  (18 filas) distinto de `EXPECTED_LIVE_COMUNAS_COUNT` (346 filas). Validacion
  especifica segun modo.

---

## Propuesta de implementacion

### Paso 1: Diagnosticar causa raiz de cada fallback

Para cada dataset fallback, determinar por que el extractor no produce datos vivos:

1. **finanzas_municipales**: probar `src/extractors/sinim_finanzas_extractor.py`
   independientemente. Verificar si la API SINIM ha cambiado (URL, formato,
   autenticacion).
2. **resultados_educacionales**: probar `src/extractors/mineduc_resultados_extractor.py`.
   Verificar disponibilidad del sitio de MINEDUC y formato de datos.
3. **indicadores_urbanos_siedu**: probar `src/extractors/siedu_extractor.py`.
   Verificar API SIEDU.
4. **perfil_territorial_comunal**: estabilizar upstreams primero; si todos los
   upstreams estan live, este dataset es live automaticamente.

**Entregable:** Reporte por dataset con causa raiz y solucion identificada.

**Esfuerzo:** 1 sprint (2 semanas)

### Paso 2: Reparar o reemplazar extractores rotos

Para cada extractor:
1. Si la API cambio: actualizar URLs, parametros y parseo.
2. Si la fuente dejo de estar disponible: buscar fuente alternativa oficial
   (ej. datos.gob.cl, ministerio respectivo).
3. Si no hay fuente alternativa: documentar en el propio dataset y considerar
   degradacion a `candidate` (ver criterio abajo).

**Esfuerzo:** 2-3 sprints (4-6 semanas) dependiendo de la complejidad de cada fuente.

### Paso 3: Implementar health checks automaticos de extractores

Agregar a `src/chile_hub/core.py` (o `pipeline_status_utils.py`) un mecanismo de
health check que ejecute cada extractor en modo prueba y reporte si produce
datos validos. Integrar con `chile-hub check-sources` (core.py linea 768).

**Referencia:** `check_sources()` en core.py linea 768 ya verifica conectividad
HTTP de las fuentes. Extender para ejecutar extractor en modo dry-run.

### Paso 4: Definir politica de degradacion a candidate

Si un dataset no se estabiliza en 3 meses desde la fecha del scorecard (i.e., antes
de 2026-09-18), se degrada de "active" a "candidate":

1. **Candidatos no aparecen en landing page** como datasets disponibles.
2. **Candidatos no se incluyen en el bundle publicable**.
3. **Candidatos generan warning en `chile-hub list`**.
4. **Documentacion se actualiza** para marcar el dataset como "no mantenido".

Documentar criterio en `docs/dataset-inclusion-criteria.md`.

### Paso 5: Verificacion final y cierre

Para cada dataset estabilizado:
1. Extractor produce datos vivos en CI.
2. Validacion contra contrato JSON Schema pasa.
3. `source_mode` es `"live"` en pipeline_metadata.
4. `fallback_count` en hub_health baja en 1.

---

## Criterio de aceptacion

1. Al menos 2 de los 4 datasets fallback pasan a `source_mode: "live"`.
2. `chile-hub check-sources --format table` muestra los 4 extractores como
   `online` con codigo 200.
3. `hub_health.json` reporta `fallback_count` reducido.
4. Los extractores estabilizados tienen tests en `tests/test_extractors.py`
   que verifican que producen datos con las columnas esperadas.
5. Si un dataset no se estabiliza en 3 meses, se degrada a candidate
   siguiendo la politica documentada.

---

## Dependencias

- Acceso a redes externas (APIs de gobierno chileno, ministerios).
- Posible coordinacion con mantenedores de las fuentes oficiales.
- `check_sources()` en core.py linea 768 para verificacion de conectividad.
- `scripts/verify_pipeline.py` para validacion post-estabilizacion.

---

## Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|:-------|:-----------:|:-------:|:-----------|
| La fuente oficial dejo de publicar el dataset | Alta | Alto | Buscar fuente alternativa (datos.gob.cl, archivo CKAN); si no existe, degradar a candidate |
| El extractor necesita cambios profundos (nueva API, autenticacion) | Media | Alto | Documentar requisitos de autenticacion; considerar contribucion externa |
| El upstream de perfil_territorial_comunal nunca se estabiliza | Alta | Medio | Desacoplar `build_perfil_territorial_comunal()` para que acepte mix de upstreams live/fallback |
| No hay capacidad para mantener 4 extractores simultaneamente | Media | Medio | Priorizar por impacto de datos: finanzas_municipales > resultados_educacionales > siedu > perfil_territorial |

---

## Notas de disenio

### Decision: no reescribir extractores desde cero

A menos que la API haya cambiado drasticamente, se prefiere parchar los extractores
existentes sobre reescribirlos. Los extractores actuales estan en `src/extractors/`
y tienen estructura consistente (herencia de `base.py`).

### Politica de degradacion

La degradacion a candidate no es un castigo, sino una señal honesta para los
usuarios: "este dataset no tiene mantenimiento activo". Un dataset candidate
puede volver a active si alguien lo adopta y estabiliza.

### Dataset perfil_territorial_comunal

Este dataset es especial porque no tiene extractor propio. Su estabilizacion
depende de que todos sus upstreams esten en live. Si solo algunos upstreams se
estabilizan, `perfil_territorial_comunal` seguira en fallback. En ese caso,
considerar dividirlo en sub-datasets independientes o hacer que acepte
upstreams en modo mixto.

### Referencia a la logica actual

La linea 583 de `build_dev_db.py` muestra el mensaje exacto de impacto para
fallback: `"impact": "Valores provenientes de fallback local; no representan
el ultimo snapshot live."`. Al estabilizar, este mensaje debe desaparecer y el
`degradation_status` pasar a `"none"`.
