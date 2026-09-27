import os
import io
import requests
import pandas as pd
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from sklearn.ensemble import IsolationForest

# Endpoint configurable por variable de entorno
endpoint = os.getenv("FLOCI_ENDPOINT", "http://localhost:4588").rstrip("/")

client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": endpoint}
)

silver_bucket = client.bucket("bank-medallion-silver")
gold_bucket = client.bucket("bank-medallion-gold")

blobs = list(silver_bucket.list_blobs())
if not blobs:
    print("No se encontraron archivos en Silver.")
    exit()

latest_blob = sorted(blobs, key=lambda b: b.name, reverse=True)[0]
print(f"Leyendo desde Silver: {latest_blob.name}")

# Descarga directa vía API REST para evitar redirecciones a localhost en Docker
download_url = f"{endpoint}/storage/v1/b/{silver_bucket.name}/o/{latest_blob.name}?alt=media"
response = requests.get(download_url)
df = pd.read_csv(io.StringIO(response.text))

# Detección de anomalías con Machine Learning
features = df[["amount", "hour_of_day"]]
model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly_score"] = model.fit_predict(features)
df["is_fraud_suspect"] = df["anomaly_score"] == -1

# Agregación de KPIs
gold_summary = df.groupby("user_id").agg(
    total_spent=("amount", "sum"),
    avg_ticket=("amount", "mean"),
    total_transactions=("transaction_id", "count"),
    fraud_alerts=("is_fraud_suspect", "sum")
).reset_index()

# Guardar en Gold
output_scored = latest_blob.name.replace("cleaned_", "gold_scored_")
gold_bucket.blob(output_scored).upload_from_string(df.to_csv(index=False), content_type="text/csv")

output_summary = latest_blob.name.replace("cleaned_", "gold_user_kpis_")
gold_bucket.blob(output_summary).upload_from_string(gold_summary.to_csv(index=False), content_type="text/csv")

print("Exito desde Docker: Guardados en Gold:")
print(f" - Detalle con scoring: {output_scored} ({df['is_fraud_suspect'].sum()} sospechas)")
print(f" - KPIs por usuario: {output_summary}")