import streamlit as st
import pandas as pd
import requests

#st.set_page_config(layout="wide")
st.title("Visualización de Datos Masivos")

# --- Preview y log ---
@st.cache_data
def get_preview():
    r = requests.get("http://localhost:5000/dataset_limpio")
    return pd.DataFrame(r.json()) if r.ok else pd.DataFrame()

@st.cache_data
def get_log():
    r = requests.get("http://localhost:5000/resumen_limpieza")
    return r.json().get("log", [])

@st.cache_data
def get_columns():
    r = requests.get("http://localhost:5000/columnas")
    return r.json().get("columns", [])

# --- Carga de datos por defecto o subida ---
uploaded_file = st.file_uploader(
    "Sube tu propio CSV para analizar",
    type="csv",
    help="Si no subes nada, se usará el dataset por defecto del servidor."
)
if uploaded_file is not None:
    if st.button("Limpiar y usar este dataset"):
        files = {"file": uploaded_file}
        resp = requests.post("http://localhost:5000/upload", files=files)
        if resp.ok:
            st.success("Dataset cargado y limpiado correctamente ✅")
            # invalidamos caches
            get_preview.clear()
            get_log.clear()
            get_columns.clear()
            st.info("Por favor, recarga la página para ver el nuevo dataset.")
            st.stop()
        else:
            err = resp.json().get("error", resp.text)
            st.error(f"No se pudo subir el fichero: {err}")

# --- Después de cargar / recargar ---
df   = get_preview()
cols = get_columns()

st.subheader("Vista previa del dataset limpiado")
st.dataframe(df)

st.subheader("Detalles limpieza")
with st.expander("Ver detalles"):
    for l in get_log():
        st.markdown(f"- {l}")

# --- Parámetros de la gráfica ---
chart_type = st.selectbox("Tipo de gráfico", [
    "Barra", "Línea", "Histograma+KDE",
    "Boxplot", "Correlograma", "Scatter"
])

# A partir de aquí tu código de selección de ejes, grupos, etc
# recordando usar siempre `cols` para poblar los selectboxes:

if chart_type == "Histograma+KDE":
    num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    col_h    = st.selectbox("Variable para Histograma+KDE", num_cols)
    if st.button("Generar Histograma+KDE"):
        payload = {"tipo": "Histograma+KDE", "columna_y": col_h}
        r = requests.post("http://localhost:5000/graficar", json=payload)
        if r.ok:
            st.image(r.content, use_container_width=True)
        else:
            st.error(r.json().get("error"))

elif chart_type == "Boxplot":
    num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    col_b    = st.selectbox("Variable para Boxplot", num_cols)
    grp      = st.selectbox("Agrupar Boxplot por (opcional)", ["(Sin)"]+cols)
    if st.button("Generar Boxplot"):
        payload = {"tipo": "Boxplot", "columna_y": col_b, "grupo": None if grp=="(Sin)" else grp}
        r = requests.post("http://localhost:5000/graficar", json=payload)
        if r.ok:
            st.image(r.content, use_container_width=True)
        else:
            st.error(r.json().get("error"))

elif chart_type == "Correlograma":
    st.markdown("**Correlograma**: correlación entre todas las variables numéricas")
    if st.button("Generar Correlograma"):
        payload = {"tipo": "Correlograma"}
        r = requests.post("http://localhost:5000/graficar", json=payload)
        if r.ok:
            st.image(r.content, use_container_width=True)
        else:
            st.error(r.json().get("error"))

elif chart_type == "Scatter":
    col_x = st.selectbox("Eje X", cols, key="sx")
    col_y = st.selectbox("Eje Y", cols, key="sy")
    grp   = st.selectbox("Columna de grupo (opcional)", ["(Sin)"]+cols, key="sg")
    sel   = []; agr_g = "Ninguna"
    if grp!="(Sin)":
        if any(tok in grp.lower() for tok in ("date","fecha")):
            agr_g = st.selectbox("Agrupar fechas grupo", ["Anual","Mensual","Diaria"], key="sgf")
        vals = requests.get(
            "http://localhost:5000/valores_unicos",
            params={"col":grp, "agrup":agr_g}
        ).json().get("values",[])
        sel = st.multiselect(f"Seleccionar {grp}", vals, default=vals[:5], key="sms")
    if st.button("Generar Scatter"):
        payload = {
            "tipo": "Scatter",
            "columna_x": col_x,
            "columna_y": col_y,
            "grupo": None if grp=="(Sin)" else grp,
            "agrupacion_grupo_fecha": agr_g,
            "seleccion_grupos": sel
        }
        r = requests.post("http://localhost:5000/graficar", json=payload)
        if r.ok:
            st.image(r.content, use_container_width=True)
        else:
            try: msg = r.json().get("error")
            except: msg = r.text
            st.error(f"Error al generar Scatter: {msg}")

else:  # Barra / Línea
    column_x   = st.selectbox("Eje X", cols, key="bx")
    column_y   = st.selectbox("Eje Y", cols, key="by")
    agg_option = st.selectbox("¿Qué mostrar en Y?", ["Conteo","Media","Suma"], key="bagg")

    fecha_cols = [c for c in cols if "date" in c.lower() or "fecha" in c.lower()]
    agrup_x = "Ninguna"
    if column_x in fecha_cols:
        agrup_x = st.selectbox("Agrupar fechas X", ["Ninguna","Anual","Mensual","Diaria"], key="bfx")

    group_col      = st.selectbox("Agrupar por (opcional)", ["(Sin agrupación)"]+cols, key="bgrp")
    agrup_g        = "Ninguna"
    seleccion_grps = []
    if group_col != "(Sin agrupación)":
        if any(tok in group_col.lower() for tok in ("date","fecha")):
            agrup_g = st.selectbox("Agrupar fechas grupo", ["Anual","Mensual","Diaria"], key="bfg")
        vals = requests.get(
            "http://localhost:5000/valores_unicos",
            params={"col": group_col, "agrup": agrup_g}
        ).json().get("values", [])
        seleccion_grps = st.multiselect(f"Seleccionar valores de '{group_col}'", vals, default=vals[:5], key="bms")

    if st.button("Generar gráfico", key="bgen"):
        payload = {
            "tipo": chart_type,
            "columna_x": column_x,
            "columna_y": column_y,
            "agregacion": agg_option,
            "agrupacion_fecha": agrup_x,
            "grupo": None if group_col=="(Sin agrupación)" else group_col,
            "agrupacion_grupo_fecha": agrup_g,
            "seleccion_grupos": seleccion_grps
        }
        r = requests.post("http://localhost:5000/graficar", json=payload)
        if r.ok:
            st.image(r.content, use_container_width=True)
        else:
            st.error(r.json().get("error"))
