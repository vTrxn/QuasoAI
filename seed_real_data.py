import sys
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el path del backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import database

def seed_real_data():
    db = database.SessionLocal()
    try:
        # 1. Asegurar tiendas
        ml = db.query(database.Store).filter(database.Store.name == "MercadoLibre").first()
        if not ml:
            ml = database.Store(name="MercadoLibre", domain="mercadolibre.com.co")
            db.add(ml)
            db.flush()

        # 2. Datos realistas de hardware para Colombia (Precios en COP)
        data = [
            {
                "name": "NVIDIA RTX 4060 MSI Ventus 2X",
                "category": "GPU",
                "brand": "MSI",
                "prices": [1650000, 1620000, 1590000], # Historial para el Cerebro
                "url": "https://articulo.mercadolibre.com.co/MCO-rtx4060"
            },
            {
                "name": "AMD Ryzen 7 7800X3D Box",
                "category": "CPU",
                "brand": "AMD",
                "prices": [1950000, 1980000, 2050000],
                "url": "https://articulo.mercadolibre.com.co/MCO-7800x3d"
            },
            {
                "name": "Corsair Vengeance DDR5 32GB (2x16GB) 6000MHz",
                "category": "RAM",
                "brand": "Corsair",
                "prices": [580000, 560000, 550000],
                "url": "https://articulo.mercadolibre.com.co/MCO-ddr5-32gb"
            }
        ]

        for item in data:
            # Crear componente
            comp = db.query(database.Component).filter(database.Component.name == item["name"]).first()
            if not comp:
                comp = database.Component(name=item["name"], category=item["category"], brand=item["brand"])
                db.add(comp)
                db.flush()
            
            # Crear listing
            listing = db.query(database.ProductListing).filter(database.ProductListing.url == item["url"]).first()
            if not listing:
                listing = database.ProductListing(component_id=comp.id, store_id=ml.id, url=item["url"])
                db.add(listing)
                db.flush()

            # Añadir historial de precios
            for i, p in enumerate(item["prices"]):
                hist = database.PriceHistory(
                    listing_id=listing.id,
                    price=float(p),
                    currency="COP",
                    timestamp=datetime.utcnow()
                )
                db.add(hist)
        
        db.commit()
        logger.info("✅ Base de datos poblada con éxito con datos realistas para entrenamiento.")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_data()
