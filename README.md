# 🏦 Banking Medallion Data Platform & Anomaly Detection

Pipeline de ingeniería de datos y detección de anomalías basado en la **Arquitectura Medallón** (Bronze, Silver, Gold), simulando infraestructura de **Google Cloud Platform (GCS)** de forma local mediante **Floci** y gestionado con **Terraform**.

## 🛠️ Stack Tecnológico
- **Infraestructura como Código (IaC):** Terraform
- **Cloud Storage Emulator:** Floci (simulador local de GCP)
- **Data Pipeline:** Python (Pandas, Google Cloud SDK)
- **Machine Learning:** Scikit-Learn (Isolation Forest para scoring de anomalías)
- **Visualización / BI:** Streamlit & Plotly
- **Containerización:** Docker

## 🏛️ Arquitectura Medallón
1. **Bronze Layer:** Ingesta de eventos transaccionales crudos en formato JSON.
2. **Silver Layer:** Normalización, deduplicación, tipado estricto y enriquecimiento de variables de negocio.
3. **Gold Layer:** Agregación de KPIs por usuario y scoring no supervisado de fraude con `IsolationForest`.

## 🚀 Ejecución Rápida
1. Iniciar emulador local de GCS.
2. Desplegar buckets:
   ```bash
   cd infra && terraform init && terraform apply -auto-approve

Ejecutar pipeline unificado:

python src/run_pipeline.py

Lanzar dashboard analítico:

streamlit run src/app_dashboard.py

#### 3. Inicializar el repositorio y hacer el commit

En PowerShell:

git init
git add .
git commit -m "feat: initial commit with medallion architecture, terraform infra and streamlit dashboard"