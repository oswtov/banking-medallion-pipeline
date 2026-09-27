import io
import json
import pandas as pd
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

# 1. Configurar cliente apuntando a Floci
client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": "http://localhost:4588"}
)

bronze_bucket = client.bucket("bank-medallion-bronze")
silver_bucket = client.bucket("bank-medallion-silver")

# 2. Descargar el archivo más reciente de Bronce
blobs = list(bronze_bucket.list_blobs())
if not blobs:
    print("No se encontraron archivos en Bronce.")
    exit()

latest_blob = sorted(blobs, key=lambda b: b.name, reverse=True)[0]
print(f"Procesando: {latest_blob.name}")

raw_data = json.loads(latest_blob.download_as_text())
df = pd.DataFrame(raw_data)

# 3. Limpieza y Enriquecimiento (Silver)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["amount"] = df["amount"].astype(float)
df.drop_duplicates(subset=["transaction_id"], inplace=True)
df["is_high_value"] = df["amount"] > 2000.0
df["hour_of_day"] = df["timestamp"].dt.hour

# 4. Guardar en Silver como CSV estándar
csv_data = df.to_csv(index=False)
output_name = latest_blob.name.replace(".json", ".csv").replace("raw_", "cleaned_")
silver_blob = silver_bucket.blob(output_name)
silver_blob.upload_from_string(csv_data, content_type="text/csv")

print(f"Exito: {len(df)} registros procesados y guardados en Silver como {output_name}.")