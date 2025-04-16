import streamlit as st
import pandas as pd
import re

# ----------------------------
# CARGAR CSV DESDE GITHUB
# ----------------------------
st.title("📦 PREBOOKS KOMET")

# ⚠️ Reemplazá esta URL con la URL RAW de tu archivo en GitHub
csv_url = "https://raw.githubusercontent.com/JessPaez/LOCACIONES/refs/heads/main/PEDIDOS_SC.csv"
csv_url_compras = "https://raw.githubusercontent.com/JessPaez/LOCACIONES/refs/heads/main/COMPRAS.csv"

try:
    # Cargar datos y parsear la columna de fechas directamente
    df = pd.read_csv(csv_url, parse_dates=["Farm Shi"])
    df_compras = pd.read_csv(csv_url_compras).fillna("")

    # ----------------------------
    # LIMPIEZA Y TRANSFORMACIONES
    # ----------------------------

    def reparar_fecha(valor):
        try:
            day, month = valor.split("-")
            if month == "abr":
                return pd.to_datetime(f"2025-04-{day.zfill(2)}")
            elif month == "may":
                return pd.to_datetime(f"2025-05-{day.zfill(2)}")
            else:
                return pd.to_datetime(valor)
        except:
            return pd.NaT

    if df["Farm Shi"].dtype == object:
        df["Farm Shi"] = df["Farm Shi"].apply(reparar_fecha)

    # Separar variedad y largo
    def separar(product_cm):
        product_cm = str(product_cm)
        match = re.search(r"(\d+)\s*cm*$", product_cm)
        if match:
            largo = match.group(1)
            product = re.sub(r"\s*\d+\s*cm*$", "", product_cm).strip()
            return pd.Series([product, largo])
        else:
            return pd.Series([product_cm, "S.E."])

    df[["Product", "Largo"]] = df["Product"].apply(separar)
    df_compras[["VARIETY","Largo"]] = df_compras["VARIETY"].apply(separar)

    # Agrupar
    df = df.groupby(["Farm Shi", "Product", "Cod", "Largo"], as_index=False).sum()
    df = df.sort_values(by=["Farm Shi", "Product", "Largo"]).reset_index(drop=True)

    # Mostrar fechas sin hora
    df["Farm Shi"] = df["Farm Shi"].dt.date

    # Reordenar columnas para mostrar 'Largo' después de 'Product'
    columnas_ordenadas = ["Farm Shi", "Product", "Largo", "Cod", "Total Units"]
    df = df[columnas_ordenadas]
    columnas_compras = ['VARIETY', 'Largo' ,'WELY', 'FROS', 'NATIVE', 'GUAISA', 'FLVE', 'ROPR', 'ROSU',
       'DIND', 'POTR', 'ALIA', 'ATTA', 'DYAN', 'NEVA', 'STRO']
    df_compras = df_compras[columnas_compras]

    # ----------------------------
    # FILTROS
    # ----------------------------
    st.sidebar.header("🔎 Filtros")

    fecha_filtro = st.sidebar.date_input("📅 Fecha exacta:")
    variedad_filtro = st.sidebar.text_input("🌸 Variedad :", value="")
    cod_opcion = st.sidebar.selectbox("🏷️ Código:", options=["AMBOS", "FDB", "LOC"])
    filtro = df.copy()
    filtro_compras = df_compras.copy()

    if fecha_filtro:
        filtro = filtro[filtro["Farm Shi"] == fecha_filtro]

    if variedad_filtro:
        filtro = filtro[filtro["Product"].str.contains(variedad_filtro, case=False, na=False)]
        filtro_compras = filtro_compras[filtro_compras["VARIETY"].str.contains(variedad_filtro, case=False, na=False)]

    if cod_opcion != "AMBOS":
        filtro = filtro[filtro["Cod"] == cod_opcion]
    
    # Detectar columnas con al menos un dato válido (no NaN)
    columnas_validas = filtro_compras.columns[filtro_compras.notna().any()].tolist()

    # Filtrar el DataFrame para mostrar solo columnas con datos
    filtro_visible = filtro_compras[columnas_validas]

    # ----------------------------
    # RESULTADOS
    # ----------------------------
    st.subheader("📋 Resultados del filtro")

    if filtro.empty:
        st.warning("No hay resultados para los filtros seleccionados.")
    else:
        st.dataframe(filtro)
        st.subheader("🛒 Compras")
        st.dataframe(filtro_visible)

except Exception as e:
    st.error(f"❌ Error al cargar el archivo desde GitHub: {e}")

