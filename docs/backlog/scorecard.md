# Scorecard de Mejoras Estratégicas — ChileHub

**Ultima actualizacion:** 2026-06-18
**Revision semanal:** viernes
**Version del proyecto:** v1.5.0 (Alpha)
**Estado general:** En desarrollo activo

---

## Resumen ejecutivo

ChileHub (v1.5.0 Alpha) es una libreria Python open-source que cura, normaliza, valida
y publica ~15 datasets oficiales de Chile. El proyecto se encuentra en etapa temprana:
el modulo `build_dev_db.py` concentra 3206 lineas (God module), la validacion de
contratos JSON Schema existe pero solo se ejecuta en `scripts/verify_pipeline.py`
(fuera del pipeline principal), los nombres de dataset se pasan como strings magicos
sin constantes tipadas, 4 datasets operan en modo fallback no estabilizado, y la
landing page no muestra el estado operativo en tiempo real.

Las 5 mejoras que siguen atacan estos puntos en orden de impacto estrategico.

---

## Scorecard

| # | Mejora | Impacto | Esfuerzo | Riesgo | Estado | Target | Dependencias |
|:--:|:---|:--:|:--:|:--:|:---|:---|:---|
| 1 | Refactorizar `build_dev_db.py` en modulos `src/builders/` | Alto | Alto | Medio | Pendiente | Q3 2026 | Tests de validacion existentes (`tests/test_pipeline_logic.py`) |
| 2 | Validacion de contratos JSON Schema en runtime | Alto | Medio | Bajo | Pendiente | Q3 2026 | Quick win tests (`tests/test_validation.py`) |
| 3 | Constantes de datasets como enum (`Dataset`) | Medio | Medio | Bajo | Pendiente | Q3 2026 | — |
| 4 | Estabilizacion de datasets en modo fallback | Alto | Alto | Medio | Pendiente | Q3 2026 | Acceso a fuentes origen (URLs externas) |
| 5 | Dashboard publico de salud operativa del hub | Medio | Medio | Bajo | Pendiente | Q4 2026 | #4 completado (para no mostrar falsos positivos) |

---

## Metricas de avance

| # | Mejora | Disenio | Prototipo | Implementacion | Tests | Documentacion | Despliegue |
|:--:|:---|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | Refactor `build_dev_db.py` | 0% | 0% | 0% | 0% | 0% | 0% |
| 2 | Validacion contratos runtime | 0% | 0% | 0% | 0% | 0% | 0% |
| 3 | Constantes datasets | 0% | 0% | 0% | 0% | 0% | 0% |
| 4 | Estabilizacion fallbacks | 0% | 0% | 0% | 0% | 0% | 0% |
| 5 | Dashboard salud | 0% | 0% | 0% | 0% | 0% | 0% |

**Progreso total:** 0% (5/5 mejoras sin iniciar)

---

## Revisiones semanales

### Semana 1 — 2026-06-18
- Scorecard creado. Pendiente de planificacion.
- Proxima revision: 2026-06-25

### Semana 2 — (placeholder)
### Semana 3 — (placeholder)
### Semana 4 — (placeholder)

---

## Archivos de backlog

| # | Archivo |
|:--:|:---|
| 1 | `docs/backlog/01-refactor-build-dev-db.md` |
| 2 | `docs/backlog/02-contratos-automatizados-runtime.md` |
| 3 | `docs/backlog/03-constantes-de-datasets.md` |
| 4 | `docs/backlog/04-estabilizacion-fallbacks.md` |
| 5 | `docs/backlog/05-dashboard-publico-salud.md` |
