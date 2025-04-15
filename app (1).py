import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime

# ----------------------------
# FUNCIONES
# ----------------------------

def limpiar_fecha(fechas):
    fechas_limpias = []
    for f in fechas:
        try:
            day, month = f.split('-')
            if month == 'abr':
                fechas_limpias.append(f'2025-04-{day.zfill(2)}')
            elif month == 'may':
                fechas_limpias.append(f'2025-05-{day.zfill(2)}')
            else:
                fechas_limpias.append(f)
        except:
            fechas_limpias.append(f)
    return fechas_limpias

def separar(product_cm):
    product_cm = str(product_cm)
    match = re.search(r'(\d+)\s*cm*$', product_cm)
    if match:
        largo = match.group(1)
        product = re.sub(r'\s*\d+\s*cm*$', '', product_cm).strip()
        return pd.Series([product, largo])
    else:
        return pd.Series([product_cm, 'S.E.'])

# ----------------------------
# CARGA DE DATOS
# ----------------------------

st.title("📦 Filtrado interactivo de pedidos")

uploaded_file = st.file_uploader("📁 Carga tu archivo PEDIDOS_SC.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Limpiar fechas
    df['Farm Shi'] = limpiar_fecha(df['Farm Shi'])
    df['Farm Shi'] = pd.to_datetime(df['Farm Shi'], errors='coerce')

    # Separar Product y Largo
    df[['Product', 'Largo']] = df['Product'].apply(separar)

    # Agrupar datos
    df = df.groupby(['Farm Shi', 'Product', 'Cod', 'Largo'], as_index=False).sum()
    df = df.sort_values(by=['Farm Shi', 'Product', 'Largo']).reset_index(drop=True)

    # Reordenar columnas
    orden = ['Farm Shi', 'Product', 'Largo', 'Cod', 'Total Units']
    df = df.reindex(columns=orden)

    # ----------------------------
    # FILTROS
    # ----------------------------
    st.sidebar.header("🔎 Filtros")

    # Fecha
    fechas_unicas = df['Farm Shi'].dt.date.unique()
    fecha_filtro = st.sidebar.date_input("📅 Selecciona una fecha:", value=fechas_unicas[0] if len(fechas_unicas) > 0 else None)

    # Variedad
    variedad_filtro = st.sidebar.text_input("🌸 Variedad:", value="")

    # Cod
    cod_opcion = st.sidebar.selectbox("🏷️ Código:", options=["AMBOS", "FDB", "LOC"])

    # ----------------------------
    # APLICAR FILTROS
    # ----------------------------
    filtro = df.copy()

    if fecha_filtro:
        filtro = filtro[filtro['Farm Shi'].dt.date == fecha_filtro]

    if variedad_filtro:
        filtro = filtro[filtro['Product'].str.contains(variedad_filtro, case=False, na=False)]

    if cod_opcion != "AMBOS":
        filtro = filtro[filtro["Cod"] == cod_opcion]

    # ----------------------------
    # RESULTADO
    # ----------------------------
    st.subheader("📋 Resultados del filtro")
    if filtro.empty:
        st.warning("No hay resultados para los filtros seleccionados.")
    else:
        st.dataframe(filtro)

else:
    st.info("👈 Carga un archivo CSV para comenzar.")
