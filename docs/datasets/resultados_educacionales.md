# Resultados Educacionales

## Descripción

Resultados educacionales agregados por comuna y año desde publicaciones MINEDUC. Esta capa complementa `establecimientos_educacionales`, que es un directorio de establecimientos.

## Fuente y licencia

- Fuente: Centro de Estudios MINEDUC - Datos Abiertos
- URL: https://centroestudios.mineduc.cl/datos-abiertos/
- Licencia: CC-BY-3.0 Chile

## Schema

| Campo | Tipo | Descripción |
|---|---|---|
| `anio` | integer | Año del indicador. |
| `codigo_comuna` | string | Código CUT comunal de 5 caracteres. |
| `matricula_total` | integer | Matrícula total agregada. |
| `asistencia_promedio` | float | Asistencia promedio porcentual. |
| `tasa_aprobacion` | float | Porcentaje de aprobación. |
| `tasa_reprobacion` | float | Porcentaje de reprobación. |
| `tasa_retiro` | float | Porcentaje de retiro. |
| `establecimientos_reportados` | integer | Establecimientos considerados en el agregado. |

## Uso

```python
from chile_hub import ChileHub

hub = ChileHub()
df = hub.load_polars("resultados_educacionales")
```

```sql
SELECT anio, codigo_comuna, matricula_total
FROM 'data/normalized/resultados_educacionales.parquet';
```

## Limitaciones

La capa se publica solo agregada por comuna y año. No contiene registros de estudiantes ni información personal.

## Changelog

- v1: Dataset agregado con validación de porcentajes, conteos no negativos y privacidad por agregación.
