import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from flask import Flask, request, jsonify, Response
import pandas as pd

from framework.datasource            import CSVDataSource
from framework.processor             import DataProcessor
from framework.cleaner               import Cleaner, TypeOnlyCleaner
from framework.strategy.bar          import BarChartStrategy
from framework.strategy.line         import LineChartStrategy
from framework.strategy.histogram    import HistogramStrategy
from framework.strategy.boxplot      import BoxplotStrategy
from framework.strategy.correlograma import CorrelogramaStrategy
from framework.strategy.scatter      import ScatterStrategy

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

    data = request.get_json() or {}
    path = data.get("path")
    if not path or not os.path.isfile(path):
        return jsonify(error=f"Fichero no encontrado: {path}"), 400

    # 1) Cargar
    src = CSVDataSource(path)
    df_new = src.load()

    # 2) Limpiar
    df_new = cleaner.clean(df_new)

    # 3) Convertir fechas autodetectadas
    for c in df_new.columns:
        if any(pat in c.lower() for pat in ("date", "fecha")):
            df_new[c] = pd.to_datetime(df_new[c], errors="coerce")

    # 4) Actualizar global
    df = df_new

    # Preparar respuesta
    preview = df.head(10).to_dict(orient="records")
    cols    = processor.get_columns(df)
    dtypes  = processor.get_dtypes(df)
    log     = df.attrs.get("cleaning_log", [])

    return jsonify({
        "preview":       preview,
        "columns":       cols,
        "dtypes":        dtypes,
        "cleaning_log":  log
    })

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



if __name__ == "__main__":
    app.run(debug=True)
