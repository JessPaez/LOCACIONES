import streamlit as st
import pandas as pd
import re

# ----------------------------
# CARGAR CSV DESDE GITHUB
# ----------------------------
st.title("📦 Filtrado interactivo de pedidos")

# ⚠️ Reemplazá esta URL con la URL RAW de tu archivo en GitHub
csv_url = "https://raw.githubusercontent.com/JessPaez/LOCACIONES/refs/heads/main/PEDIDOS_SC.csv"

try:
    # Cargar datos y parsear la columna de fechas directamente
    df = pd.read_csv(csv_url, parse_dates=["Farm Shi"])

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

    # Agrupar
    df = df.groupby(["Farm Shi", "Product", "Cod", "Largo"], as_index=False).sum()
    df = df.sort_values(by=["Farm Shi", "Product", "Largo"]).reset_index(drop=True)

    # Mostrar fechas sin hora
    df["Farm Shi"] = df["Farm Shi"].dt.date

    # Reordenar columnas para mostrar 'Largo' después de 'Product'
    columnas_ordenadas = ["Farm Shi", "Product", "Largo", "Cod", "Total Units"]
    df = df[columnas_ordenadas]

    # ----------------------------
    # FILTROS
    # ----------------------------
    st.sidebar.header("🔎 Filtros")

    fecha_filtro = st.sidebar.date_input("📅 Fecha exacta:")
    variedad_filtro = st.sidebar.text_input("🌸 Variedad (texto parcial):", value="Rose")
    cod_opcion = st.sidebar.selectbox("🏷️ Código:", options=["AMBOS", "FDB", "LOC"])

    filtro = df.copy()

    if fecha_filtro:
        filtro = filtro[filtro["Farm Shi"] == fecha_filtro]

    if variedad_filtro:
        filtro = filtro[filtro["Product"].str.contains(variedad_filtro, case=False, na=False)]

    if cod_opcion != "AMBOS":
        filtro = filtro[filtro["Cod"] == cod_opcion]

    # ----------------------------
    # RESULTADOS
    # ----------------------------
    st.subheader("📋 Resultados del filtro")

    if filtro.empty:
        st.warning("No hay resultados para los filtros seleccionados.")
    else:
        st.dataframe(filtro)

        st.download_button(
            label="⬇️ Descargar resultado en Excel",
            data=filtro.to_excel(index=False),
            file_name="resultado_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"❌ Error al cargar el archivo desde GitHub: {e}")
