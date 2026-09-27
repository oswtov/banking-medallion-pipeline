import io
import json
import requests
import pandas as pd
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

endpoint = "http://localhost:4588"

client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": endpoint}
)

print("=" * 60)
print("1. CAPA BRONZE (JSON Crudo)")
print("=" * 60)
b_bucket = client.bucket("bank-medallion-bronze")
b_blob = sorted(list(b_bucket.list_blobs()), key=lambda b: b.name, reverse=True)[0]
res_b = requests.get(f"{endpoint}/storage/v1/b/{b_bucket.name}/o/{b_blob.name}?alt=media")
raw_sample = json.loads(res_b.text)[:2]
print(f"Archivo: {b_blob.name}")
print(json.dumps(raw_sample, indent=2))

print("\n" + "=" * 60)
print("2. CAPA SILVER (Limpio y Enriquecido)")
print("=" * 60)
s_bucket = client.bucket("bank-medallion-silver")
s_blob = sorted(list(s_bucket.list_blobs()), key=lambda b: b.name, reverse=True)[0]
res_s = requests.get(f"{endpoint}/storage/v1/b/{s_bucket.name}/o/{s_blob.name}?alt=media")
df_silver = pd.read_csv(io.StringIO(res_s.text))
print(f"Archivo: {s_blob.name}")
print(df_silver[["transaction_id", "user_id", "amount", "hour_of_day", "is_high_value"]].head(3))

print("\n" + "=" * 60)
print("3. CAPA GOLD (Métricas y Anomalías ML)")
print("=" * 60)
g_bucket = client.bucket("bank-medallion-gold")
g_blobs = list(g_bucket.list_blobs())

kpi_blob = [b for b in g_blobs if "user_kpis" in b.name][0]
res_kpi = requests.get(f"{endpoint}/storage/v1/b/{g_bucket.name}/o/{kpi_blob.name}?alt=media")
df_kpis = pd.read_csv(io.StringIO(res_kpi.text))
print(f"Archivo KPIs: {kpi_blob.name}")
print(df_kpis.sort_values(by="fraud_alerts", ascending=False).head(3))

scored_blob = [b for b in g_blobs if "gold_scored" in b.name][0]
res_scored = requests.get(f"{endpoint}/storage/v1/b/{g_bucket.name}/o/{scored_blob.name}?alt=media")
df_scored = pd.read_csv(io.StringIO(res_scored.text))
print(f"\nArchivo Scored: {scored_blob.name}")
print("Casos detectados como anomalía / sospecha de fraude:")
print(df_scored[df_scored["is_fraud_suspect"] == True][["user_id", "amount", "category", "hour_of_day", "anomaly_score"]].head(3))