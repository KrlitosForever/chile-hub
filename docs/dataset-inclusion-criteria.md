# Criterios para incluir datasets

`chile-hub` crece por criterios, no por acumulación. Una capa nueva debe aumentar
el valor del hub sin comprometer trazabilidad, legalidad, mantenibilidad ni la
confianza de quienes consumen los artefactos publicados.

## Criterios bloqueantes

Una propuesta no entra al roadmap si falla cualquiera de estos puntos:

| Criterio | Pregunta | Decisión |
|:---|:---|:---|
| Reúso legal | Tiene licencia abierta, permisos claros o amparo público sin restricción explícita? | Si no, se rechaza o queda como referencia externa. |
| Fuente inspeccionable | Existe API, CSV, XLSX, ZIP, JSON o descarga estable? | Si solo requiere scraping HTML frágil, se rechaza. |
| Estabilidad | El esquema y la URL son razonablemente estables? | Si cambia sin aviso, queda como investigación. |
| Datos no personales | Evita padrones, datos sensibles o identificadores personales protegidos? | Si hay riesgo de Ley 19.628, se rechaza. |
| Validación posible | Se puede validar cardinalidad, claves, tipos o rangos? | Si no se puede verificar, no se publica. |

## Criterios de prioridad

Los datasets que pasan los bloqueantes se ordenan por:

1. Dolor de usuario recurrente y documentado.
2. Valor de cruce con `codigo_comuna`, `codigo_region` u otro identificador estable.
3. Utilidad transversal para desarrolladores, analistas, periodistas o civic-tech.
4. Bajo costo operacional de refresco y monitoreo.
5. Claridad de esquema, campos y frecuencia esperada.
6. Capacidad de publicarse en formatos ya soportados: Parquet, DuckDB, SQLite, JSON o Excel.
7. Diferenciación: reduce limpieza repetida que cada usuario haría por su cuenta.

## Estados de decisión

| Estado | Significado |
|:---|:---|
| `accepted` | Pasa criterios y tiene prioridad suficiente para plan de implementación. |
| `needs-research` | Puede ser valioso, pero falta confirmar licencia, fuente, esquema o costo. |
| `deferred` | Es válido, pero no desplaza mejoras de robustez o capas más demandadas. |
| `rejected` | Falla un criterio bloqueante o no encaja con el propósito del hub. |

## Razones comunes de rechazo

- La fuente no permite redistribución o tiene términos ambiguos.
- El dato contiene información personal, sensible o electoral individual.
- La única fuente disponible es HTML frágil sin descarga estructurada.
- El dataset no cruza con la DPA ni aporta un identificador estable.
- El costo de mantenimiento excede el beneficio para una capa pública curada.
- La propuesta duplica una capa existente sin mejorar cobertura, calidad o uso.

## Cómo proponer una capa

Abre un issue usando la plantilla `Dataset request` e incluye:

- URL oficial de la fuente.
- Estado de licencia o términos de reúso.
- Caso de uso concreto que desbloquea.
- Claves de cruce esperadas.
- Frecuencia de actualización y riesgos de mantenimiento.
- Ejemplo mínimo de columnas esperadas si ya las conoces.

Si la propuesta todavía es exploratoria, usa GitHub Discussions antes de pedir
integración al catálogo mantenido.
