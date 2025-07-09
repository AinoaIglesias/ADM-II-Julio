import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from flask import Flask, request, jsonify, Response
import pandas as pd

from framework.cleaner import Cleaner
from framework.strategy.bar import BarChartStrategy
from framework.strategy.line import LineChartStrategy
from framework.strategy.histogram import HistogramStrategy
from framework.strategy.boxplot import BoxplotStrategy
from framework.strategy.correlograma import CorrelogramaStrategy
from framework.strategy.scatter import ScatterStrategy

app = Flask(__name__)

# --- 1) Cargo y limpio dataset inicial ---
raw_df = pd.read_csv("datasets/madrid_2001_2018_calidad_aire.csv")
cleaner = Cleaner(
    strategy_numeric="mean",
    strategy_categorical="fill",
    drop_cols=True,
    null_threshold=0.7
)
df = cleaner.clean(raw_df)

# convierto todas las columnas fecha
for c in df.columns:
    if "date" in c.lower() or "fecha" in c.lower():
        df[c] = pd.to_datetime(df[c], errors="coerce")

# --- Endpoints de datos estáticos ---
@app.route("/dataset_limpio")
def preview():
    return df.head(10).to_json(orient="records")

@app.route("/columnas")
def columnas():
    return jsonify(columns=df.columns.tolist())

@app.route("/resumen_limpieza")
def resumen():
    return jsonify(log=df.attrs.get("cleaning_log", []))

@app.route("/valores_unicos")
def valores_unicos():
    col   = request.args.get("col")
    agrup = request.args.get("agrup", "Ninguna")
    if col not in df.columns:
        return jsonify(error="Columna no válida"), 400

    tmp = df[[col]].copy()
    if agrup!="Ninguna" and pd.api.types.is_datetime64_any_dtype(tmp[col]):
        if agrup=="Anual":
            tmp[col] = tmp[col].dt.to_period("Y").astype(str)
        elif agrup=="Mensual":
            tmp[col] = tmp[col].dt.to_period("M").astype(str)
        else:
            tmp[col] = tmp[col].dt.date.astype(str)

    vals = sorted(tmp[col].dropna().unique())
    return jsonify(values=vals)

# --- Subida de nuevo CSV ---
@app.route("/upload", methods=["POST"])
def upload_dataset():
    global df
    f = request.files.get("file")
    if not f:
        return jsonify(error="No se ha enviado ningún fichero"), 400

    try:
        raw = pd.read_csv(f)
    except Exception as e:
        return jsonify(error=f"No se pudo leer CSV: {e}"), 400

    new_df = cleaner.clean(raw)
    for c in new_df.columns:
        if "date" in c.lower() or "fecha" in c.lower():
            new_df[c] = pd.to_datetime(new_df[c], errors="coerce")

    df = new_df
    return jsonify(message="Dataset cargado y limpiado",
                   log=df.attrs.get("cleaning_log", []))


# --- Estrategias disponibles ---
strategies = {
    "Barra":         BarChartStrategy(),
    "Línea":         LineChartStrategy(),
    "Histograma":    HistogramStrategy(),
    "Boxplot":       BoxplotStrategy(),
    "Correlograma":  CorrelogramaStrategy(),
    "Scatter":       ScatterStrategy(),
}

# --- Generar gráfico ---
@app.route("/graficar", methods=["POST"])
def graficar():
    data = request.get_json()
    tipo = data.get("tipo")
    strat = strategies.get(tipo)
    if not strat:
        return jsonify(error=f"Tipo '{tipo}' no soportado"), 400

    # hacemos copia para manipular agrupaciones / filtros
    d = df.copy()

    # Filtrado / agrupaciones previas según tipo
    # Scatter: filtro por grupo
    if tipo == "Scatter":
        x_col = data["columna_x"]
        y_col = data["columna_y"]
        grupo = data.get("grupo")
        agr_f = data.get("agrupacion_grupo_fecha", "Ninguna")
        sel   = data.get("seleccion_grupos", [])

        if grupo and sel:
            if agr_f!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[grupo]):
                if agr_f=="Anual":
                    d[grupo] = d[grupo].dt.to_period("Y").astype(str)
                elif agr_f=="Mensual":
                    d[grupo] = d[grupo].dt.to_period("M").astype(str)
                else:
                    d[grupo] = d[grupo].dt.date.astype(str)
            d = d[d[grupo].isin(sel)]

        args = {
            "x_col": x_col,
            "y_col": y_col,
            "grupo": grupo
        }

    # Histograma & KDE
    elif tipo in ("Histograma"):
        y_col = data.get("columna_y")
        args = {"y_col": y_col}

    # Boxplot
    elif tipo == "Boxplot":
        y_col = data.get("columna_y")
        grupo = data.get("grupo")
        args = {"y_col": y_col, "grupo": grupo}

    # Correlograma
    elif tipo == "Correlograma":
        args = {}

    # Barra / Línea
    else:
        x_col = data["columna_x"]
        y_col = data.get("columna_y")
        agg   = data["agregacion"]
        grupo = data.get("grupo")
        # posible agrupación de fechas en eje X
        agr_x = data.get("agrupacion_fecha", "Ninguna")
        if agr_x!="Ninguna" and pd.api.types.is_datetime64_any_dtype(d[x_col]):
            if agr_x=="Anual":
                d[x_col] = d[x_col].dt.to_period("Y").astype(str)
            elif agr_x=="Mensual":
                d[x_col] = d[x_col].dt.to_period("M").astype(str)
            else:
                d[x_col] = d[x_col].dt.date.astype(str)

        args = {
            "x_col": x_col,
            "y_col": y_col,
            "agregacion": agg,
            "grupo": grupo
        }

    try:
        img_bytes = strat.plot(d, **args)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify(error=str(e)), 500

    return Response(img_bytes, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
