# Prácticas ADM y trabajo final 2025

Ainoa Iglesias Dailva, alu0101164403@ull.edu.es

Análisi de Datos Masivos, Segunda parte

Junio, 2025
______________________________________________________________________________

streamlit run client/app.py --server.maxUploadSize=3072

python server/server_V2.py   

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

*Ejecutar el notebook tarea0_exploracion.ipynb*

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

**Columnas útiles:**

- ID: Identificador único de accidente.

- Severity: Para analizar el impacto en el tráfico.
    - 4 valores únicos [1, 2, 3, 4] siendo 1 menos grave (poco retraso) y 4 el mas grave (retraso largo del trafico).

- Start_Time / End_Time: Para estudiar la hora del día y cómo puede influir en la ocurrencia de accidentes.

- City, Street, State, Zipcode: Para analizar accidentes según la ubicación geográfica (zonas, regiones).

- Weather_Condition, Temperature(F), Wind_Chill(F), Humidity(%), Pressure(pulgadas), Visibility(millas), Wind_Speed(mph), Precipitation(pulgadas): Estos son datos del clima que podrían influir en los accidentes.

- Amenity, Bump, Crossing, Give_Way, Junction, No_Exit, Railway, Roundabout, Station, Stop, Traffic_Calming, Traffic_Signal, Turning_Loop: Estos son indicadores de condiciones específicas de la vía que podrían ser útiles para estudiar cómo afectan a los accidentes.

- Sunrise_Sunset: momento del día que ocurrió el accidente basado en atardecer y anochecer (dia/noche).

- Distance(mi): Longitud de carretera afectada.


_________________________________________________________________________________
## Tarea 1

*Ejecutar python .\framework\visualizations\main.py*

**Objetivos**

1. Separar fuente de datos de la representación.

2. Aplicar el patrón Estrategia para elegir diferentes formas de visualizar los datos.

3. Tener al menos dos representaciones distintas.


**Diseño**

```bash
visual/
├── __init__.py
├── main.py                  # Ejecuta todo
├── source.py                # Carga datasets (de cualquier tipo)
├── strategy.py              # Estrategias reutilizables
└── config.py                # Parámetros externos: qué columnas usar, qué estrategias aplicar
```

**Interpretación de las gráficas generadas**

![barras estados](/images/image-2.png)

California (CA) tiene la mayor cantidad de accidentes (>1.6 millones). Le siguen Florida (FL) y Texas (TX). Esto podría tener que ver con densidad de población o tamaño del estado entre otras cosas.

![histograma temperatura](/images/image.png)

La mayoria de accidentes se centran entre los 10 y 30 grados centígrados que son temperaturas normales por lo que no nos da mucha información.

Sin embargo vemos que a altas temperaturas no hay muchos accidentes al contrario que en las bajas temperaturas, por lo que podría interpretarse que a bajas temperaturas es mas habitual sufrir accidentes que en altas temperaturas (tal vez por el estado de las carreteras, nieve, hielo, niebla...)

![histograma humedad](/images/image-1.png)

Distribución casi ascendente, destacando el máximo en el 85-90%

En este caso parece que si hay una clara relación entre numero de accidentes y humedad, La mayor humedad puede deberse al clima de la región o clima del momento (lluvia) por lo que podría verse una relación entre dias lluviosos y accidentes. Habría que anañizar los datos de días lluviosos.


![accidentes por mes y año](/images/image-5.png)

Todos los años parece que hay menos accidentes en verano lo que podría relacionarse con lo que vimos antes de la humedad y temperatura, menor humedad y mas temperatura equivalía a menos accidentes. 

Destacan algunas anomalías. Por ejemplo en abril de 2022 hubo un mayor numero de accidentes en comaración al resto de años. En 2020 hubo un descenso en los accidentes bastante grande pero creció enormemente en invierno, esto podría deberse a consecuencia de la pamdemia.

![temperatura media por dia](/images/image-4.png)



_________________________________________________________________________________
## Tarea 2

*Ejecutar python .\framework\visualizations\main.py*

**Objetivos**

1. Incorpora la posibilidad de comparar múltiples grupos mediante la selección previa de los elementos a comparar.

2. Añadir un segundo dataset