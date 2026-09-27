import os
import sys
import subprocess
import time

def run_step(script_name, description):
    print(f"\n{'='*60}")
    print(f">> Iniciando: {description} ({script_name})")
    print(f"{'='*60}")
    start = time.time()
    result = subprocess.run([sys.executable, os.path.join("src", script_name)], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[ERROR] en el paso {script_name}:\n{result.stderr}")
        sys.exit(1)
        
    print(result.stdout.strip())
    print(f">> Completado en {round(time.time() - start, 2)}s")

if __name__ == "__main__":
    print("\n--- INICIANDO PIPELINE MEDALLON BANCARIO COMPLETO ---")
    run_step("ingest_bronze.py", "1. Ingesta Cruda a Bronce")
    run_step("process_silver.py", "2. Limpieza y Enriquecimiento a Silver")
    run_step("process_gold.py", "3. Analitica y Scoring ML a Gold")
    print(f"\n{'='*60}")
    print("PIPELINE EJECUTADO EXITOSAMENTE DE PRINCIPIO A FIN")
    print(f"{'='*60}\n")