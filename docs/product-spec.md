# Especificación del producto chile-hub

## Resumen

`chile-hub` es una capa de acceso curada, versionada y fácil de consumir para datos chilenos de fuentes abiertas o legalmente reutilizables.

## Principio

El valor del producto no es "tener todos los datos chilenos".

El valor es reducir el tiempo, la ambigüedad y la tasa de fracaso involucrados en encontrar, limpiar, entender, unir, versionar y consumir conjuntos de datos chilenos fiables.

## Viabilidad

El proyecto es viable si se mantiene acotado en su modelo operativo y amplio solo en su visión a largo plazo.

No es viable como:

- una promesa de cubrir todos los conjuntos de datos relevantes en Chile
- un portal con mucho scraping y licencias poco claras
- un producto centrado en tableros con bases de datos débiles

Es viable como:

- un repositorio de capas de datos de alto valor
- un marco de ingesta y normalización repetible
- un catálogo orientado a la confianza con procedencia, advertencias y ejemplos

## Compensaciones fundamentales

- Amplitud vs mantenibilidad: más temas aumentan el atractivo pero también multiplican los procesos frágiles.
- Frescura vs fiabilidad: la automatización diaria es útil solo cuando la fuente es lo suficientemente estable como para justificarla.
- Comodidad vs claridad legal: republicar mejora la usabilidad pero nunca debe adelantarse a los permisos de la fuente.
- Superficie de API vs costo operativo: los archivos versionados son más baratos de mantener que una API siempre activa.
- Uniformidad vs veracidad: no todas las fuentes pueden cumplir el mismo estándar de calidad, por lo que los niveles de confianza deben ser explícitos.

## Política de automatización

No todos los conjuntos de datos pertenecen al mismo nivel de automatización.

### Nivel A: totalmente automatizable

Útil para:

- API estables
- CSV/JSON/Parquet legibles por máquina
- esquemas predecibles
- reutilización legal clara

Comportamiento esperado:

- actualización programada
- verificaciones de esquema
- salidas deterministas

### Nivel B: semiautomatizable

Útil para:

- archivos Excel con desviación manual periódica
- archivos estables con cambios ocasionales de esquema
- conjuntos de datos que necesitan reglas de normalización mantenidas a mano

Comportamiento esperado:

- ingesta mayormente automatizada
- revisión manual ante desviaciones de esquema
- pruebas más rigurosas y comportamiento de respaldo

### Nivel C: investigación o manual

Útil para:

- PDF
- scraping HTML frágil
- derechos poco claros
- patrones de publicación inestables

Comportamiento esperado:

- no incluir en el MVP
- documentar como investigación futura

## Criterios de admisión de conjuntos de datos

Un conjunto de datos debería ingresar a `chile-hub` solo si obtiene una buena puntuación en la mayoría de los siguientes criterios:

1. Resuelve un problema recurrente del usuario.
2. Tiene un fuerte valor de unión entre conjuntos de datos.
3. Proviene de una fuente estable e inspeccionable.
4. Tiene condiciones de reutilización claras o manejables.
5. Puede actualizarse a un costo razonable.
6. Produce salidas útiles sin herramientas personalizadas.
7. Ayuda a demostrar la diferenciación del producto.

## Prioridad de usuario inicial

### Principal

- desarrolladores que construyen software chileno
- analistas o equipos de BI que preparan repetidamente datos de referencia chilenos

### Secundario

- periodistas, investigadores y equipos de tecnología cívica

Los usuarios no técnicos de hojas de cálculo importan, pero deberían recibir servicio a través de exportaciones y plantillas, en lugar de ser el centro de diseño principal del MVP.

## Recomendación de MVP

El MVP debería demostrar que `chile-hub` puede convertir datos públicos chilenos desordenados en componentes confiables.

### Incluido en el MVP

- capa base territorial: región, provincia, comuna, códigos estandarizados, nombres seguros para búsqueda
- indicadores económicos diarios: UF, USD, EUR, UTM e indicadores similares de alto reúso
- una capa transversal adicional elegida por criterios de admisión, no solo por intuición

Buenos candidatos para la tercera capa:

- directorios de establecimientos o institucionales con fuerte potencial de unión
- resultados electorales con identificadores oficiales estables
- resúmenes de finanzas o presupuestos municipales si el acceso y las licencias son limpios

### Explícitamente excluido del MVP

- cobertura universal de "todos los datos chilenos"
- tableros complejos
- una API pública que deba mantenerse en línea 24/7
- scraping frágil como la promesa central del producto
- fuentes con condiciones de redistribución poco claras

## Modos de consumo

### Imprescindible

- archivos planos versionados: CSV, JSON, Parquet
- base de datos analítica local: DuckDB
- exportación SQLite
- documentación con ejemplos copiables

### Deseable después del MVP

- paquete auxiliar de Python
- interfaz de búsqueda más completa
- índice de archivos alojado o catálogo de versiones

### Generalmente excesivo para el MVP

- API REST
- autenticación
- suite de tableros interactivos

## Modelo de confianza

Cada capa de datos debería publicar:

- fuente
- método de acceso
- frecuencia de actualización
- notas legales
- esquema
- reglas de normalización
- advertencias conocidas
- marca de tiempo de actualización
- nivel de confianza

## Definición de éxito

El MVP tiene éxito si un usuario técnico puede:

1. descubrir un conjunto de datos rápidamente
2. entender si es confiable
3. cargarlo en una línea
4. unirlo con sus propios datos sin trabajo de limpieza

## Siguiente paso inmediato

Construye el repositorio en torno a un catálogo visible de capas de datos y una rúbrica de admisión estricta antes de expandir la cobertura de fuentes.
