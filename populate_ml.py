import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el path del backend para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import database
from ml_api_service import ml_api_service

def run_population():
    db = database.SessionLocal()
    categories = {
        "GPU": ["tarjeta grafica rtx 4060", "rtx 4070", "rx 7800 xt"],
        "CPU": ["procesador ryzen 7 7800x3d", "intel i5 13600k", "ryzen 5 5600x"],
        "RAM": ["memoria ram ddr5 32gb", "ddr4 16gb corsair"],
        "SSD": ["disco ssd m.2 1tb", "samsung 980 pro"]
    }

    total_added = 0
    try:
        for category, queries in categories.items():
            for query in queries:
                logger.info(f"🔍 Buscando {query} en categoría {category}...")
                results = ml_api_service.fetch_products(query)
                if results:
                    count = ml_api_service.process_and_save(db, results, category)
                    logger.info(f"✅ Se agregaron/actualizaron {count} productos para '{query}'")
                    total_added += count
                else:
                    logger.warning(f"⚠️ No se obtuvieron resultados para '{query}'")
        
        logger.info(f"🚀 Proceso completado. Total de registros procesados: {total_added}")
    finally:
        db.close()

if __name__ == "__main__":
    run_population()
