import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from flask import Flask, request, jsonify, send_file
from io import BytesIO
import pandas as pd
from framework.strategy.bar import BarChartStrategy
from framework.strategy.line import LineChartStrategy
from framework.utils.cleaner import clean_dataset

# Ajusta la ruta a tu repo real
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)

# 1) Cargo y limpio
raw_df = pd.read_csv("datasets/madrid_2001_2018_calidad_aire.csv")
df = clean_dataset(raw_df, strategy_numeric="mean", strategy_categorical="fill", drop_cols=True)

# 2) Convierto automáticamente todas las columnas de fecha a datetime
for c in df.columns:
    if "date" in c.lower() or "fecha" in c.lower():
        df[c] = pd.to_datetime(df[c], errors="coerce")

# 3) Preview y log
@app.route("/dataset_limpio", methods=["GET"])
def preview():
    return df.head(10).to_json(orient="records")

# 2) Columnas  
@app.route("/columnas", methods=["GET"])
def columnas():
    return jsonify(columns=df.columns.tolist())

# 3) Resumen de limpieza
@app.route("/resumen_limpieza", methods=["GET"])
def log():
    return jsonify({"log": df.attrs.get("cleaning_log", [])})

# 4) Valores únicos + agrupación opcional de fechas
@app.route("/valores_unicos", methods=["GET"])
def valores_unicos():
    col   = request.args.get("col")
    agrup = request.args.get("agrup", "Ninguna")
    if col not in df.columns:
        return jsonify({"error":"Columna no válida"}), 400

    tmp = df[[col]].copy()
    # si piden agrupar fechas y es columna datetime:
    if agrup != "Ninguna" and pd.api.types.is_datetime64_any_dtype(tmp[col]):
        if agrup == "Anual":
            tmp[col] = tmp[col].dt.to_period("Y").astype(str)
        elif agrup == "Mensual":
            tmp[col] = tmp[col].dt.to_period("M").astype(str)
        else:  # Diaria
            tmp[col] = tmp[col].dt.date.astype(str)

    vals = sorted(tmp[col].dropna().unique().tolist())
    return jsonify({"values": vals})

# 5) Estrategias
strategies = {
    "Barra": BarChartStrategy(),
    "Línea": LineChartStrategy()
}

# 6) Generar gráfico
@app.route("/graficar", methods=["POST"])
def graficar():
    data = request.get_json()
    tipo                   = data["tipo"]
    x_col                  = data["columna_x"]
    y_col                  = data["columna_y"]
    agregacion             = data["agregacion"]
    agrupacion_fecha       = data.get("agrupacion_fecha", "Ninguna")
    grupo                  = data.get("grupo")  # p.ej. "station"
    agrup_grupo_fecha      = data.get("agrupacion_grupo_fecha", "Ninguna")
    seleccion_grupos       = data.get("seleccion_grupos") or []

    # validaciones básicas
    if tipo not in strategies:
        return jsonify({"error":"Tipo no soportado"}), 400
    if x_col not in df.columns or (agregacion!="Conteo" and y_col not in df.columns):
        return jsonify({"error":"Columnas no válidas"}), 400

    d = df.copy()

    # 6.1) Agrupo eje X si es fecha
    if agrupacion_fecha!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[x_col]):
        if agrupacion_fecha=="Anual":
            d[x_col] = d[x_col].dt.to_period("Y").astype(str)
        elif agrupacion_fecha=="Mensual":
            d[x_col] = d[x_col].dt.to_period("M").astype(str)
        else:
            d[x_col] = d[x_col].dt.date.astype(str)

    # 6.2) Filtrar por grupo si aplica (sin convertir non-dates a str)
    if grupo and seleccion_grupos:
        # si agrupo fechas en la columna de grupo, convierto primero
        if agrup_grupo_fecha!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[grupo]):
            if agrup_grupo_fecha=="Anual":
                d[grupo] = d[grupo].dt.to_period("Y").astype(str)
            elif agrup_grupo_fecha=="Mensual":
                d[grupo] = d[grupo].dt.to_period("M").astype(str)
            else:
                d[grupo] = d[grupo].dt.date.astype(str)
        # en caso CONTRARIO ***no*** tocamos el dtype de d[grupo]
        d = d[d[grupo].isin(seleccion_grupos)]

    # 6.3) Llamo a la estrategia
    buf = BytesIO()
    try:
        strategies[tipo].plot(d, x_col, y_col, buf, agregacion, grupo=grupo)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__=="__main__":
    app.run(debug=True)
