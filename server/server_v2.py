import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from flask import Flask, request, jsonify, Response
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB

from framework.datasource            import CSVDataSource
from framework.processor             import DataProcessor
from framework.cleaner               import Cleaner, TypeOnlyCleaner
from framework.strategy.bar          import BarChartStrategy
from framework.strategy.line         import LineChartStrategy
from framework.strategy.histogram    import HistogramStrategy
from framework.strategy.boxplot      import BoxplotStrategy
from framework.strategy.correlograma import CorrelogramaStrategy
from framework.strategy.scatter      import ScatterStrategy
from framework.model                 import BasePipelineModel, KMeansClustering, LogisticClassification, LinearRegressionModel


app = Flask(__name__)

# — Globals —
df: pd.DataFrame = pd.DataFrame()
processor = DataProcessor()
cleaner   = Cleaner(
    date_cols=None,             # autodetección de columnas fecha
    strategy_numeric="mean",
    strategy_categorical="fill",
    drop_empty_const=True,
    null_threshold=0.7
)

# --------------------- Endpoints ----------------- #

# CARGA DATASET Y LIMPIEZA
@app.route("/load_dataset", methods=["POST"])
def load_dataset():
    """
    Espera JSON: { "path": "<ruta_a_csv>" }
    1) Carga con CSVDataSource
    2) Limpia con Cleaner por defecto
    3) Convierte fechas autodetectadas
    4) Actualiza `df` global
    Responde con preview, columnas, tipos y log.
    """
    global df
    try:
        data = request.get_json() or {}
        path = data.get("path")
        if not path or not os.path.isfile(path):
            return jsonify(error=f"Fichero no encontrado: {path}"), 400

        # 1) Cargar dataset
        src = CSVDataSource(path)
        df_new = src.load()

        # 2) Limpiar
        df_new = cleaner.clean(df_new)

        # 3) Fechas y variables temporales
        for c in df_new.columns:
            if any(pat in c.lower() for pat in ("date","time","fecha")):
                df_new[c] = pd.to_datetime(df_new[c], errors="coerce")
        if "Start_Time" in df_new.columns:
            st = df_new["Start_Time"]
            df_new["Hour"] = st.dt.hour
            df_new["Weekday"] = st.dt.dayofweek
            df_new["Month"] = st.dt.month

        # 4) Actualizar global
        df = df_new

        # 5) Preparar respuesta
        preview_df = df.head(10).copy()
        # Convertir datetime a strings ISO
        for col in preview_df.select_dtypes(include=["datetime64[ns]"]):
            preview_df[col] = preview_df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")
        preview_records = preview_df.to_dict(orient="records")

        cols = processor.get_columns(df)
        dtypes = processor.get_dtypes(df)
        log = df.attrs.get("cleaning_log", [])

        return jsonify({
            "preview":       preview_records,
            "columns":       cols,
            "dtypes":        dtypes,
            "cleaning_log":  log
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify(error=str(e)), 500
# IProcessor
@app.route("/columns", methods=["GET"])
def get_columns():
    return jsonify(columns=processor.get_columns(df))

@app.route("/dtypes", methods=["GET"])
def get_dtypes():
    return jsonify(dtypes=processor.get_dtypes(df))

@app.route("/info", methods=["GET"])
def get_info():
    return jsonify(info=processor.get_info(df))

@app.route("/null_percentages", methods=["GET"])
def get_null_percentages():
    return jsonify(null_percentages=processor.get_null_percentages(df))

@app.route("/unique_counts", methods=["GET"])
def get_unique_counts():
    return jsonify(unique_counts=processor.get_unique_counts(df))

@app.route("/unique_values", methods=["GET"])
def get_unique_values():
    n = request.args.get("n", default=20, type=int)
    return jsonify(unique_values=processor.get_unique_values(df, n))

@app.route("/descriptive_stats", methods=["GET"])
def get_descriptive_stats():
    """
    Devuelve las estadísticas descriptivas (df.describe()).
    Para mantenerlo ligero, lo devolvemos como JSON de dict-of-dicts.
    """
    stats_df = processor.get_descriptive_stats(df)
    return jsonify(descriptive_stats=stats_df.to_dict())


# ICleaner cambio tipo de columna
@app.route("/convert_types", methods=["POST"])
def convert_types():
    """
    Espera JSON:
      { "dtype_map": { "station": "category", "CO": "float32", … } }
    Aplica TypeOnlyCleaner sobre el df global, actualiza df y devuelve:
      - el nuevo tipo de datos de todas las columnas
      - el cleaning_log con los mensajes de conversión
    """
    global df

    data = request.get_json() or {}
    dtype_map = data.get("dtype_map", {})
    if not dtype_map:
        return jsonify(error="Debes enviar un 'dtype_map' no vacío"), 400

    caster = TypeOnlyCleaner(dtype_map=dtype_map)
    df = caster.clean(df)  # reasignamos el df global tipado

    # Preparamos la respuesta
    dtypes = processor.get_dtypes(df)
    log    = df.attrs.get("cleaning_log", [])

    return jsonify({
        "message":      "Tipos actualizados correctamente",
        "dtypes":       dtypes,
        "cleaning_log": log
    })

# IPlotStrategy
strategies = {
    "Barra":        BarChartStrategy(),
    "Línea":        LineChartStrategy(),
    "Histograma":   HistogramStrategy(),
    "Boxplot":      BoxplotStrategy(),
    "Correlograma": CorrelogramaStrategy(),
    "Scatter":      ScatterStrategy(),
}

@app.route("/graficar", methods=["POST"])
def graficar():
    data = request.get_json() or {}
    tipo = data.get("tipo")
    strat = strategies.get(tipo)
    if strat is None:
        return jsonify(error=f"Tipo '{tipo}' no soportado"), 400

    # Cogemos copia para no modificar el global
    d = df.copy()

    # Parámetros comunes
    grupo    = data.get("grupo")
    select   = data.get("seleccion_grupos", [])  # aquí vendrán las estaciones a mostrar
    # Si hay selección y columna de grupo válida, filtramos
    if grupo and select:
        if grupo not in d.columns:
            return jsonify(error=f"Columna de grupo '{grupo}' no existe"), 400
        d = d[d[grupo].isin(select)]

    # --- Ahora, según el tipo, armamos kwargs para la estrategia ---
    if tipo == "Scatter":
        x_col = data["columna_x"]
        y_col = data["columna_y"]
        agr_f = data.get("agrupacion_grupo_fecha", "Ninguna")
        # (… aquí tu lógica original de scatter con agrupación de fechas en el grupo si hace falta …)
        kwargs = {"x_col": x_col, "y_col": y_col, "grupo": grupo}

    elif tipo == "Histograma":
        kwargs = {"y_col": data["columna_y"]}

    elif tipo == "Boxplot":
        kwargs = {"y_col": data["columna_y"], "grupo": grupo}

    elif tipo == "Correlograma":
        kwargs = {}

    else:  # Barra o Línea
        x_col = data["columna_x"]
        y_col = data.get("columna_y")
        agg   = data.get("agregacion")
        # 1) Agrupación de fechas en eje X
        agr_x = data.get("agrupacion_fecha", "Ninguna")
        if agr_x!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[x_col]):
            if agr_x=="Anual":
                d[x_col] = d[x_col].dt.to_period("Y").astype(str)
            elif agr_x=="Mensual":
                d[x_col] = d[x_col].dt.to_period("M").astype(str)
            else:
                d[x_col] = d[x_col].dt.date.astype(str)
        # Quitar filas donde la agrupación temporal dio NaT o cadena vacía
        d = d[d[x_col].notnull()]
        # 2) Agrupación de fechas en el grupo (por si quieres agrupar un group datetime)
        agr_g = data.get("agrupacion_grupo_fecha", "Ninguna")
        if grupo and agr_g!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[grupo]):
            if agr_g=="Anual":
                d[grupo] = d[grupo].dt.to_period("Y").astype(str)
            elif agr_g=="Mensual":
                d[grupo] = d[grupo].dt.to_period("M").astype(str)
            else:
                d[grupo] = d[grupo].dt.date.astype(str)

        kwargs = {
            "x_col":      x_col,
            "y_col":      y_col,
            "agregacion": agg,
            "grupo":      grupo
        }

    # Generar el PNG
    try:
        img = strat.plot(d, **kwargs)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify(error=str(e)), 500

    return Response(img, mimetype="image/png")

#- Modelos algoritmos de aprendizaje
rf_model = BasePipelineModel(
    estimator=RandomForestRegressor(),
    param_grid={
        'estimator__n_estimators': [50, 100],
        'estimator__max_depth': [None, 10]
    },
    preprocess_config={'numeric': [], 'categorical': []},
    use_grid_search=True,
    scoring='r2'
)

svm_model = BasePipelineModel(
    estimator=SVC(),
    param_grid={
        'estimator__C': [0.1, 1, 10],
        'estimator__kernel': ['linear', 'rbf']
    },
    preprocess_config={'numeric': [], 'categorical': []},
    use_grid_search=True,
    scoring='accuracy'
)

# — Modelos de aprendizaje —
features = ["Temperature(F)", "Humidity(%)", "Visibility(mi)",
            "Wind_Speed(mph)", "Precipitation(in)", "Hour", "Weekday", "Month"]

models = {
    # Regresión y SVM que ya tenías
    "regression_rf": BasePipelineModel(
        estimator=RandomForestRegressor(random_state=42),
        param_grid={"estimator__n_estimators": [50,100], "estimator__max_depth": [5,10]},
        preprocess_config={"numeric": features}, use_grid_search=True,
        scoring="r2"
    ),
    "classification_svm": BasePipelineModel(
        estimator=SVC(probability=True, random_state=42),
        param_grid={"estimator__C": [0.1,1,10], "estimator__kernel": ["rbf","linear"]},
        preprocess_config={"numeric": features}, use_grid_search=True,
        scoring="accuracy"
    ),

    # **Nuevos modelos de clasificación**
    "knn": BasePipelineModel(
        estimator=KNeighborsClassifier(),
        param_grid={"estimator__n_neighbors": [3,5,7]},
        preprocess_config={"numeric": features}, use_grid_search=True,
        scoring="recall"   # priorizamos recall
    ),
    "tree": BasePipelineModel(
        estimator=DecisionTreeClassifier(random_state=42),
        param_grid={"estimator__max_depth": [5,10,15]},
        preprocess_config={"numeric": features}, use_grid_search=True,
        scoring="recall"
    ),
    "nb": BasePipelineModel(
        estimator=GaussianNB(),
        preprocess_config={"numeric": features},  # NB no necesita grid search
        use_grid_search=False
    ),

    # Tus otros modelos
    "linear_reg": LinearRegressionModel(),
    "logistic": LogisticClassification(),
    "clustering_kmeans": KMeansClustering(n_clusters=4)
}


@app.route("/train_model", methods=["POST"])
def train_model():
    data = request.get_json() or {}
    name = data.get("model_name")
    features = data.get("features", [])
    target = data.get("target")
    if name not in models:
        return jsonify(error=f"Modelo '{name}' no soportado"), 400
    if df.empty:
        return jsonify(error="Dataset no cargado"), 400
    X = df[features]
    y = df[target] if target else None
    model = models[name]
    try:
        model.fit(X, y)
    except Exception as e:
        return jsonify(error=str(e)), 500
    return jsonify(message=f"Modelo '{name}' entrenado correctamente")

@app.route("/evaluate_model", methods=["POST"])
def evaluate_model():
    data = request.get_json() or {}
    name = data.get("model_name")
    features = data.get("features", [])
    target = data.get("target")
    if name not in models:
        return jsonify(error=f"Modelo '{name}' no soportado"), 400
    X = df[features]
    y = df[target] if target else None
    results = models[name].evaluate(X, y)
    return jsonify(results)

@app.route("/predict_model", methods=["POST"])
def predict_model():
    data = request.get_json() or {}
    name = data.get("model_name")
    features = data.get("features", [])
    if name not in models:
        return jsonify(error=f"Modelo '{name}' no soportado"), 400
    X = df[features]
    preds = models[name].predict(X).tolist()
    return jsonify(predictions=preds)


if __name__ == "__main__":
    app.run(debug=True)
