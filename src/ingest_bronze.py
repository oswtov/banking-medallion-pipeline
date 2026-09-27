import os
import json
import random
import uuid
from datetime import datetime, timezone, timedelta
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage

endpoint = os.getenv("FLOCI_ENDPOINT", "http://localhost:4588").rstrip("/")

client = storage.Client(
    project="floci-local",
    credentials=AnonymousCredentials(),
    client_options={"api_endpoint": endpoint}
)

bucket = client.bucket("bank-medallion-bronze")

categories = ["Supermercado", "Restaurante", "Gasolinera", "Electrónica", "Transferencia", "Retiro ATM"]
merchants = ["Amazon", "Uber", "Walmart", "Starbucks", "Apple", "ATM Local"]
locations = ["CCS", "MAD", "MIA", "BOG", "NYC"]

now = datetime.now(timezone.utc)
transactions = []

for _ in range(200):
    # Distribución temporal aleatoria en las últimas 24 horas
    random_minutes = random.randint(0, 1440)
    tx_time = now - timedelta(minutes=random_minutes)
    
    # Simular montos típicos con anomalías ocasionales
    if random.random() < 0.05:
        amount = round(random.uniform(2500.0, 5000.0), 2)
    else:
        amount = round(random.uniform(5.0, 450.0), 2)

    tx = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": f"USR_{random.randint(1000, 1050)}",
        "amount": amount,
        "timestamp": tx_time.isoformat(),
        "category": random.choice(categories),
        "merchant": random.choice(merchants),
        "channel": random.choice(["WEB", "APP", "POS", "ATM"]),
        "location": random.choice(locations)
    }
    transactions.append(tx)

file_id = now.strftime("%Y%m%d_%H%M%S")
blob_name = f"raw_transactions_{file_id}.json"
blob = bucket.blob(blob_name)
blob.upload_from_string(json.dumps(transactions), content_type="application/json")

print(f"Exito: Se cargaron {len(transactions)} transacciones realistas en Bronze ({blob_name}).")