import streamlit as st
import pandas as pd
import requests

#st.set_page_config(layout="wide")
st.title("Visualización de Datos Masivos")

# 1) Preview y log
@st.cache_data
def get_preview():
    r = requests.get("http://localhost:5000/dataset_limpio")
    return pd.DataFrame(r.json()) if r.ok else pd.DataFrame()

@st.cache_data
def get_log():
    r = requests.get("http://localhost:5000/resumen_limpieza")
    return r.json().get("log", [])

df = get_preview()
st.subheader("Vista previa del dataset limpiado")
st.dataframe(df)

st.subheader("Detalles limpieza")
with st.expander("Ver detalles"):
    for l in get_log():
        st.markdown(f"- {l}")

# 2) Traer columnas completas
cols = requests.get("http://localhost:5000/columnas").json().get("columns", [])

# Parámetros de la gráfica
chart_type  = st.selectbox("Tipo de gráfico", ["Barra","Línea"])
column_x    = st.selectbox("Eje X", df.columns)
column_y    = st.selectbox("Eje Y", df.columns)
agg_option  = st.selectbox("¿Qué mostrar en Y?", ["Conteo","Media","Suma"])

# Agrupación de fechas en eje X
fecha_cols = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()]
if column_x in fecha_cols:
    agrupacion_fecha = st.selectbox("Agrupar fechas X", ["Ninguna","Anual","Mensual","Diaria"])
else:
    agrupacion_fecha = "Ninguna"

# Agrupación por columna adicional
group_col        = st.selectbox("Agrupar por (opcional)", ["(Sin agrupación)"] + list(df.columns))
group_date_agg   = "Ninguna"
seleccion_grupos = []

if group_col != "(Sin agrupación)":
    # Si la columna de grupo es fecha, elegimos nivel
    if any(tok in group_col.lower() for tok in ("date","fecha")):
        group_date_agg = st.selectbox("Agrupar fechas del grupo", ["Anual","Mensual","Diaria"])
    # Pedimos al servidor sus valores únicos ya agrupados
    r = requests.get(
        "http://localhost:5000/valores_unicos",
        params={"col": group_col, "agrup": group_date_agg}
    )
    valores = r.json().get("values", []) if r.ok else []
    seleccion_grupos = st.multiselect(
        f"Seleccionar valores de '{group_col}'",
        valores,
        default=valores[:5]
    )

# Enviar petición
if st.button("Generar gráfico"):
    payload = {
        "tipo": chart_type,
        "columna_x": column_x,
        "columna_y": column_y,
        "agregacion": agg_option,
        "agrupacion_fecha": agrupacion_fecha,
        "grupo": None if group_col=="(Sin agrupación)" else group_col,
        "agrupacion_grupo_fecha": group_date_agg,
        "seleccion_grupos": seleccion_grupos
    }
    resp = requests.post("http://localhost:5000/graficar", json=payload)
    if resp.ok:
        st.image(resp.content, use_container_width=True)
    else:
        st.error(f"Error al generar el gráfico: {resp.json().get('error')}")
