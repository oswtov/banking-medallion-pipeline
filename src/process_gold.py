import os
import io
import requests
import pandas as pd
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from sklearn.ensemble import IsolationForest

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

download_url = f"{endpoint}/storage/v1/b/{silver_bucket.name}/o/{latest_blob.name}?alt=media"
response = requests.get(download_url)
df = pd.read_csv(io.StringIO(response.text))

# --- MOTOR DE DECISIÓN HÍBRIDO ---
# 1. Componente ML: Isolation Forest sobre monto y hora
features = df[["amount", "hour_of_day"]]
model = IsolationForest(contamination=0.04, random_state=42)
df["ml_anomaly_score"] = model.fit_predict(features)
df["ml_flag"] = df["ml_anomaly_score"] == -1

# 2. Componente Heurístico: Reglas Duras de Negocio
# Regla A: Operaciones nocturnas de alto monto (0 a 5 hrs > $2,000)
rule_night_high = (df["hour_of_day"].between(0, 5)) & (df["amount"] > 2000.0)
# Regla B: Retiros ATM fuera de horario habitual con monto elevado (> $1,000)
rule_atm_risk = (df["category"] == "Retiro ATM") & (df["amount"] > 1000.0)

df["rule_flag"] = rule_night_high | rule_atm_risk

# 3. Matriz de Decisión
def decide_action(row):
    if row["rule_flag"]:
        return "DECLINED_BY_POLICY"
    if row["ml_flag"]:
        return "CHALLENGE_2FA"
    return "APPROVED"

df["decision"] = df.apply(decide_action, axis=1)
df["is_fraud_suspect"] = df["decision"].isin(["DECLINED_BY_POLICY", "CHALLENGE_2FA"])

# KPIs por usuario
gold_summary = df.groupby("user_id").agg(
    total_spent=("amount", "sum"),
    avg_ticket=("amount", "mean"),
    total_transactions=("transaction_id", "count"),
    fraud_alerts=("is_fraud_suspect", "sum")
).reset_index()

# Guardar resultados
output_scored = latest_blob.name.replace("cleaned_", "gold_scored_")
gold_bucket.blob(output_scored).upload_from_string(df.to_csv(index=False), content_type="text/csv")

output_summary = latest_blob.name.replace("cleaned_", "gold_user_kpis_")
gold_bucket.blob(output_summary).upload_from_string(gold_summary.to_csv(index=False), content_type="text/csv")

print("Exito: Motor hibrido ejecutado en Gold:")
print(f" - Decisiones: {dict(df['decision'].value_counts())}")