import requests
import random
import time
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/webhook/ingest"

components = [
    {"name": "NVIDIA RTX 4080 Super", "category": "GPU", "base_price": 1100},
    {"name": "NVIDIA RTX 4070 Ti", "category": "GPU", "base_price": 850},
    {"name": "AMD Radeon RX 7900 XTX", "category": "GPU", "base_price": 950},
    {"name": "Intel Core i9-14900K", "category": "CPU", "base_price": 580},
    {"name": "AMD Ryzen 7 7800X3D", "category": "CPU", "base_price": 380},
]

def generate_historical_data():
    print("Generando datos históricos...")
    for comp in components:
        data_batch = []
        # Generar 10 días de datos para cada componente
        for i in range(10, 0, -1):
            date = (datetime.utcnow() - timedelta(days=i)).isoformat()
            # Simular fluctuación de precio
            price = comp["base_price"] * (1 + random.uniform(-0.1, 0.05))
            
            # En el último día, forzar una caída para probar la alerta en uno de ellos
            if i == 1 and comp["name"] == "NVIDIA RTX 4080 Super":
                price = comp["base_price"] * 0.75 # 25% de caída
            
            data_batch.append({
                "component_name": comp["name"],
                "category": comp["category"],
                "price": round(price, 2),
                "store": "Tech Store Alpha",
                "url": "https://example.com/product"
            })
        
        try:
            response = requests.post(API_URL, json=data_batch)
            print(f"Enviados datos para {comp['name']}: {response.status_code}")
        except Exception as e:
            print(f"Error enviando datos: {e}")

if __name__ == "__main__":
    generate_historical_data()
