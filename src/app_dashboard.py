import io
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

st.set_page_config(page_title="Banking Medallion & Fraud Dashboard", layout="wide")
st.title("🏦 Panel de Control Analítico - Arquitectura Medallón")

endpoint = "http://localhost:4588"
client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": endpoint}
)

gold_bucket = client.bucket("bank-medallion-gold")
blobs = list(gold_bucket.list_blobs())

if not blobs:
    st.warning("No hay datos en la capa Gold.")
    st.stop()

# Cargar dataset de scoring y KPIs
scored_blob = sorted([b for b in blobs if "gold_scored" in b.name], key=lambda b: b.name, reverse=True)[0]
kpi_blob = sorted([b for b in blobs if "user_kpis" in b.name], key=lambda b: b.name, reverse=True)[0]

res_scored = requests.get(f"{endpoint}/storage/v1/b/{gold_bucket.name}/o/{scored_blob.name}?alt=media")
df_scored = pd.read_csv(io.StringIO(res_scored.text))

res_kpis = requests.get(f"{endpoint}/storage/v1/b/{gold_bucket.name}/o/{kpi_blob.name}?alt=media")
df_kpis = pd.read_csv(io.StringIO(res_kpis.text))

# Métricas principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transacciones Totales", len(df_scored))
col2.metric("Volumen Total", f"${df_scored['amount'].sum():,.2f}")
col3.metric("Ticket Promedio", f"${df_scored['amount'].mean():,.2f}")
col4.metric("Alertas de Fraude (ML)", int(df_scored["is_fraud_suspect"].sum()))

# Gráficos
c1, c2 = st.columns(2)

with c1:
    st.subheader("Distribución de Transacciones vs Detección ML")
    fig_scatter = px.scatter(
        df_scored,
        x="hour_of_day",
        y="amount",
        color="is_fraud_suspect",
        color_discrete_map={True: "crimson", False: "royalblue"},
        labels={"hour_of_day": "Hora del Día", "amount": "Monto ($)", "is_fraud_suspect": "Alerta Fraude"},
        hover_data=["user_id", "category", "merchant"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with c2:
    st.subheader("Gasto Acumulado por Categoría")
    df_cat = df_scored.groupby("category")["amount"].sum().reset_index()
    fig_bar = px.bar(df_cat, x="category", y="amount", color="category")
    st.plotly_chart(fig_bar, use_container_width=True)

# Tabla de sospechas
st.subheader("🚨 Detalle de Transacciones Sospechosas Identificadas")
st.dataframe(df_scored[df_scored["is_fraud_suspect"] == True][["transaction_id", "user_id", "amount", "hour_of_day", "category", "merchant", "location"]])