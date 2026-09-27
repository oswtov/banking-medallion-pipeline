import json
import random
import uuid
from datetime import datetime, timezone
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

# 1. Configurar cliente apuntando a Floci con credenciales anónimas
client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": "http://localhost:4588"}
)

# 2. Generar transacciones sintéticas
categories = ["Supermercado", "Restaurante", "Transferencia", "Gasolinera", "Electrónica", "Retiro ATM"]
merchants = ["Amazon", "Walmart", "Starbucks", "Uber", "Apple Store", "ATM Local"]

transactions = []
for _ in range(200):
    tx = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": f"USR_{random.randint(1000, 1050)}",
        "amount": round(random.uniform(5.0, 3500.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": random.choice(categories),
        "merchant": random.choice(merchants),
        "channel": random.choice(["WEB", "APP", "POS", "ATM"]),
        "location": random.choice(["CCS", "MIA", "MAD", "BOG", "NYC"])
    }
    transactions.append(tx)

# 3. Subir el archivo JSON crudo al bucket Bronce
bucket = client.bucket("bank-medallion-bronze")
blob_name = f"raw_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
blob = bucket.blob(blob_name)
blob.upload_from_string(json.dumps(transactions, indent=2), content_type="application/json")

print(f"Exito: Se cargaron {len(transactions)} transacciones crudas en el bucket Bronce ({blob_name}).")