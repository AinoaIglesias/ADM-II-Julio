# Prácticas ADM y trabajo final 2025

Ainoa Iglesias Dailva, alu0101164403@ull.edu.es

Análisi de Datos Masivos, Segunda parte

Junio, 2025
______________________________________________________________________________

Este repositorio contiene el desarrollo de las tareas prácticas de la asignatura Análisis de Datos, del Máster en Ingeniería Informática.

El objetivo principal es construir, paso a paso, un entorno de análisis y visualización de datos flexible y extensible. A lo largo de las prácticas se aplican técnicas de preprocesado, visualización, análisis exploratorio, representación geográfica y aprendizaje automático, trabajando con diversos conjuntos de datos.

### Prácticas Visualización de Datos

- **Tarea 0**: Selección de datasets y transformación de datos con pandas.

- **Tarea 1**: Desarrollo de un framework genérico de visualización basado en el patrón de diseño Estrategia.

- **Tarea 2**: Comparación entre múltiples grupos, nuevas representaciones gráficas y uso de un segundo dataset.

- **Tarea 3**: Visualización de distribuciones con Seaborn, análisis comparativo, conversión del framework en servicio web y propuesta de aplicación.

- **Tarea 4**: Representación geográfica con mapas y aplicación de algoritmos de machine learning (clasificación, regresión, clustering).

### Tecnologías utilizadas

- Python, Pandas, Matplotlib, Seaborn, Plotly, Bokeh, Folium, GeoPandas

- Scikit-learn, Dash / Flask (para servidor web)

- Jupyter Notebooks

- Git y GitHub para control de versiones y documentación

### Qué esperar de este análisis**

Análisis exploratorio

- Distribución geográfica de los accidentes (por estado, ciudad, región).

- Evolución temporal (accidentes por año, mes, día de la semana, hora).

- Severidad de los accidentes a lo largo del tiempo o por lugar.

Relación con el clima

- ¿Los accidentes graves ocurren más con lluvia o niebla?

- ¿Cómo afecta la visibilidad a la frecuencia de accidentes?

Duración y ubicación

- ¿En qué lugares se producen accidentes más largos?

- Comparación entre ciudades o estados.

Para machine learning (más adelante)

- Clasificación: predecir la severidad del accidente.

- Regresión: predecir la duración del accidente.

- Clustering: agrupar accidentes similares según ubicación, clima y severidad.

_________________________________________________________________________________
## Tarea 0

** *Ejecutar el notebook tarea0_exploracion.ipynb* **

**Objetivos**

1. Descargar el dataset.

2. Cargarlo y explorar con Pandas.

3. Realizar una transformación/limpieza inicial que nos prepare los datos para análisis posteriores.


Este dataset contiene información de accidentes de tráfico ocurridos en Estados Unidos entre febrero de 2016 y marzo de 2023. Los datos han sido recopilados desde diversas fuentes como APIs gubernamentales, departamentos de transporte y sensores de tráfico.

- Archivo principal: US_Accidents_March23.csv

- Tamaño: ~3 GB

- Registros: ~7.8 millones

- Columnas: 47

- Web de descarga: [Kaggle](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents)

| Columna                                               | Descripción                              |
| ----------------------------------------------------- | ---------------------------------------- |
| `ID`                                                  | Identificador único del accidente        |
| `Severity`                                            | Gravedad del accidente (1 a 4)           |
| `Start_Time`, `End_Time`                              | Fecha y hora de inicio/fin del accidente |
| `Street`, `City`, `State`, `Zipcode`, `Country`       | Localización                             |
| `Latitude`, `Longitude`                               | Coordenadas geográficas                  |
| `Temperature(F)`, `Humidity(%)`, `Visibility(mi)`     | Condiciones meteorológicas               |
| `Weather_Condition`, `Wind_Direction`, `Pressure(in)` | Variables meteorológicas adicionales     |
| `Amenity`, `Bump`, `Crossing`, `Junction`, etc.       | Características del lugar (booleanos)    |
| `Distance(mi)`                                        | Distancia afectada por el accidente      |
| `Description`                                         | Texto descriptivo del evento             |


Para facilitar el análisis se eliminará las columnas que no sean relevantes para el análisis o que contengan una gran cantidad de nulos.

*** Columnas útiles: ***

- ID: Identificador único de accidente.

- Severity: Para analizar el impacto en el tráfico.
    - 4 valores únicos [1, 2, 3, 4] siendo 1 menos grave (poco retraso) y 4 el mas grave (retraso largo del trafico).

- Start_Time / End_Time: Para estudiar la hora del día y cómo puede influir en la ocurrencia de accidentes.

- City, Street, State, Zipcode: Para analizar accidentes según la ubicación geográfica (zonas, regiones).

- Weather_Condition, Temperature(F), Wind_Chill(F), Humidity(%), Pressure(pulgadas), Visibility(millas), Wind_Speed(mph), Precipitation(pulgadas): Estos son datos del clima que podrían influir en los accidentes.

- Amenity, Bump, Crossing, Give_Way, Junction, No_Exit, Railway, Roundabout, Station, Stop, Traffic_Calming, Traffic_Signal, Turning_Loop: Estos son indicadores de condiciones específicas de la vía que podrían ser útiles para estudiar cómo afectan a los accidentes.

- Sunrise_Sunset: momento del día que ocurrió el accidente basado en atardecer y anochecer (dia/noche).

- Distance(mi): Longitud de carretera afectada.