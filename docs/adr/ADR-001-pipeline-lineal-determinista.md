# ADR-001: Pipeline lineal determinista con fallo estridente

**Fecha:** 2026-06-18
**Estado:** accepted
**Decision:** El pipeline aborta inmediatamente si alguna validacion falla. No se publican datos corruptos ni parcialmente validados.

## Contexto

chile-hub ejecuta un pipeline de transformacion de datos que va desde la extraccion desde fuentes oficiales hasta la publicacion de artefactos normalizados. El pipeline esta disenado como una secuencia lineal de etapas: extract, build, verify, test y publish. Cada etapa depende del exito completo de la anterior.

La validacion de datos ocurre en multiples puntos del pipeline. En `src/build_dev_db.py`, las funciones del modulo `src/validation.py` verifican integridad referencial (codigos CUT que referencian comunas inexistentes), cardinalidad (346 comunas esperadas), tipos de datos, valores negativos en columnas financieras, y sumas consistentes en cohortes demograficas. En `scripts/verify_pipeline.py` se ejecutan verificaciones de contratos de esquema, manifiestos de artefactos, salud del hub, y politicas de publicacion. El pipeline CI/CD en `.github/workflows/pipeline-check.yml` orquesta todo: tras el build ejecuta `verify_pipeline.py` con perfil `readiness` o `publication`, y luego corre la suite de tests con `pytest`.

## Decision

Se decidio que cualquier error de validacion debe detener el pipeline de forma estridente e inmediata. El mecanismo principal es `raise SystemExit(1)` con un mensaje descriptivo, tanto en las validaciones dentro de `src/build_dev_db.py` (funcion `validate_metadata_schema`, escritura del ZIP) como en `scripts/verify_pipeline.py` (funcion `fail()`). No existen codigos de retorno graduales ni modo "best-effort" que permita publicar datasets con errores conocidos. Un unico dataset con validacion fallida bloquea toda la publicacion.

El pipeline CI/CD refleja esta decision: el job `build-and-test` ejecuta `verify_pipeline.py --profile readiness` incluso en PRs, y solo si todas las verificaciones pasan se considera el pipeline exitoso. El perfil `publication` anade restricciones aun mas estrictas (modo live obligatorio, frescura al dia, sin fallback permitido).

## Consecuencias

- Positivas: Los consumidores reciben datos garantizadamente validos. No hay riesgo de que un dataset con errores de integridad referencial llegue al bundle publico. El sistema de tipos de `polars` detecta discrepancias de esquema temprano. Los mensajes de error son descriptivos e indican exactamente que fallo y donde.
- Negativas: El pipeline es fragil ante problemas transitorios en las fuentes. Un extractor que devuelve 345 comunas en lugar de 346 (por ejemplo, por un cambio temporal en la API de BCN) detiene toda la publicacion. La unica via de recuperacion automatica para datasets con modo `live` problematico es el modo `fallback`, pero si el fallback tampoco cumple las validaciones el pipeline falla igual. Recuperarse requiere intervencion manual: corregir la fuente, ajustar el extractor, o actualizar datos de respaldo.

## Alternativas consideradas

- **Pipeline con validaciones debiles (warnings sin fallo)** -- Se descarto porque la naturaleza de los datos (oficiales, usables en contextos legales o administrativos) exige integridad. Un warning en `resultados_educacionales` no evita que datos con cardinalidad incorrecta se publiquen en el bundle ZIP.
- **Validacion por dataset independiente** -- Permitir que datasets correctos se publiquen aunque otros fallen. Se descarto porque los datasets estan vinculados por codigos CUT; un dataset corrupto contaminaria las capas derivadas como `perfil_territorial_comunal` y romperia joins entre datasets.
- **Degradacion gradual con cuarentena** -- Mover automaticamente datasets fallidos a un carril de cuarentena. Se descarto por complejidad: el sistema actual de `publication_track` ya separa `stable_publishable` de `candidate`, y anadir una cuarentena automatica no aportaria valor frente a la supervision manual del mantenedor.
