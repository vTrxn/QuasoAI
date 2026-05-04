import sys
import os
import logging
from datetime import datetime, timedelta
import random

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el path del backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import database

def get_realistic_history(base_price, days=60):
    """
    Genera un historial de precios realista para ML.
    Simula una tendencia con ruido y algunos eventos de 'oferta'.
    """
    history = []
    current_price = base_price
    
    # Tendencia base: ligera depreciación o fluctuación de mercado (±0.2% diario)
    trend = random.uniform(-0.002, 0.001) 
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=(days - i))
        
        # Fluctuación aleatoria diaria (volatilidad)
        volatility = random.uniform(-0.01, 0.01)
        current_price *= (1 + trend + volatility)
        
        # Simular ofertas relámpago (5% de probabilidad de un drop del 10-15%)
        final_price = current_price
        if random.random() < 0.05:
            final_price *= random.uniform(0.85, 0.95)
            
        history.append((final_price, date))
    
    return history

def massive_seed():
    db = database.SessionLocal()
    try:
        # 1. Tienda
        ml = db.query(database.Store).filter(database.Store.name == "MercadoLibre").first()
        if not ml:
            ml = database.Store(name="MercadoLibre", domain="mercadolibre.com.co")
            db.add(ml)
            db.flush()

        # 2. Dataset Extendido (Más hardware y más variado)
        hardware_list = [
            # CPUs Intel
            {"name": "Intel Core i9-14900K", "cat": "CPU", "brand": "Intel", "price": 2800000},
            {"name": "Intel Core i7-14700K", "cat": "CPU", "brand": "Intel", "price": 2100000},
            {"name": "Intel Core i5-14600K", "cat": "CPU", "brand": "Intel", "price": 1550000},
            {"name": "Intel Core i7-13700K", "cat": "CPU", "brand": "Intel", "price": 1850000},
            {"name": "Intel Core i5-13400F", "cat": "CPU", "brand": "Intel", "price": 950000},
            {"name": "Intel Core i3-12100F", "cat": "CPU", "brand": "Intel", "price": 450000},
            
            # CPUs AMD
            {"name": "AMD Ryzen 9 7950X3D", "cat": "CPU", "brand": "AMD", "price": 3100000},
            {"name": "AMD Ryzen 7 7800X3D Box", "cat": "CPU", "brand": "AMD", "price": 1950000},
            {"name": "AMD Ryzen 9 7900X", "cat": "CPU", "brand": "AMD", "price": 2200000},
            {"name": "AMD Ryzen 5 7600X", "cat": "CPU", "brand": "AMD", "price": 1100000},
            {"name": "AMD Ryzen 7 5800X3D", "cat": "CPU", "brand": "AMD", "price": 1600000},
            {"name": "AMD Ryzen 5 5600G", "cat": "CPU", "brand": "AMD", "price": 650000},
            
            # GPUs NVIDIA Serie 40
            {"name": "NVIDIA RTX 4090 ASUS ROG Strix", "cat": "GPU", "brand": "ASUS", "price": 9500000},
            {"name": "NVIDIA RTX 4080 Super MSI Expert", "cat": "GPU", "brand": "MSI", "price": 5800000},
            {"name": "NVIDIA RTX 4070 Ti Super Gigabyte Gaming", "cat": "GPU", "brand": "Gigabyte", "price": 4300000},
            {"name": "NVIDIA RTX 4070 Super MSI Gaming X", "cat": "GPU", "brand": "MSI", "price": 3400000},
            {"name": "NVIDIA RTX 4060 Ti EVGA SC", "cat": "GPU", "brand": "EVGA", "price": 2100000},
            {"name": "NVIDIA RTX 4060 MSI Ventus 2X", "cat": "GPU", "brand": "MSI", "price": 1550000},
            
            # GPUs NVIDIA Serie 30
            {"name": "NVIDIA RTX 3090 Ti Founders Edition", "cat": "GPU", "brand": "NVIDIA", "price": 5500000},
            {"name": "NVIDIA RTX 3090 MSI Gaming Trio", "cat": "GPU", "brand": "MSI", "price": 4500000},
            {"name": "NVIDIA RTX 3080 Ti Zotac Trinity", "cat": "GPU", "brand": "Zotac", "price": 3800000},
            {"name": "NVIDIA RTX 3080 ASUS ROG Strix", "cat": "GPU", "brand": "ASUS", "price": 3200000},
            {"name": "NVIDIA RTX 3070 Ti MSI Suprim X", "cat": "GPU", "brand": "MSI", "price": 2400000},
            {"name": "NVIDIA RTX 3070 EVGA FTW3", "cat": "GPU", "brand": "EVGA", "price": 2100000},
            {"name": "NVIDIA RTX 3060 Ti ASUS TUF", "cat": "GPU", "brand": "ASUS", "price": 1750000},
            {"name": "NVIDIA RTX 3060 Gigabyte Windforce", "cat": "GPU", "brand": "Gigabyte", "price": 1450000},
            {"name": "NVIDIA RTX 3050 MSI Ventus 2X", "cat": "GPU", "brand": "MSI", "price": 1100000},
            
            # GPUs AMD Radeon
            {"name": "AMD Radeon RX 7900 XTX", "cat": "GPU", "brand": "AMD", "price": 5200000},
            {"name": "AMD Radeon RX 7900 XT Sapphire Nitro", "cat": "GPU", "brand": "Sapphire", "price": 4400000},
            {"name": "AMD Radeon RX 7800 XT PowerColor Hellhound", "cat": "GPU", "brand": "PowerColor", "price": 2800000},
            {"name": "AMD Radeon RX 7700 XT ASRock Steel Legend", "cat": "GPU", "brand": "ASRock", "price": 2200000},
            {"name": "AMD Radeon RX 7600 Sapphire Pulse", "cat": "GPU", "brand": "Sapphire", "price": 1400000},
            {"name": "AMD Radeon RX 6700 XT MSI Mech", "cat": "GPU", "brand": "MSI", "price": 1650000},
            
            # RAM
            {"name": "Corsair Vengeance DDR5 32GB (2x16GB) 6000MHz", "cat": "RAM", "brand": "Corsair", "price": 650000},
            {"name": "G.Skill Trident Z5 RGB 32GB DDR5 6400MHz", "cat": "RAM", "brand": "G.Skill", "price": 780000},
            {"name": "Kingston FURY Beast 16GB DDR4 3200MHz", "cat": "RAM", "brand": "Kingston", "price": 220000},
            {"name": "TeamGroup T-Force Delta RGB 32GB DDR4 3600MHz", "cat": "RAM", "brand": "TeamGroup", "price": 450000},
            
            # Almacenamiento (SSD)
            {"name": "Samsung 990 Pro 2TB NVMe Gen4", "cat": "Storage", "brand": "Samsung", "price": 950000},
            {"name": "WD Black SN850X 1TB NVMe", "cat": "Storage", "brand": "WD", "price": 520000},
            {"name": "Crucial P3 1TB NVMe Gen3", "cat": "Storage", "brand": "Crucial", "price": 280000},
            {"name": "Kingston A400 480GB SATA", "cat": "Storage", "brand": "Kingston", "price": 140000},
            
            # Motherboards
            {"name": "ASUS ROG Maximus Z790 Hero", "cat": "Motherboard", "brand": "ASUS", "price": 2600000},
            {"name": "MSI MAG B650 Tomahawk WiFi", "cat": "Motherboard", "brand": "MSI", "price": 1150000},
            {"name": "Gigabyte X670E AORUS Master", "cat": "Motherboard", "brand": "Gigabyte", "price": 2100000},
            {"name": "ASRock B550 Steel Legend", "cat": "Motherboard", "brand": "ASRock", "price": 750000},
            {"name": "ASUS Prime B760M-A WiFi", "cat": "Motherboard", "brand": "ASUS", "price": 680000},
            
            # Monitors
            {"name": "Samsung Odyssey G7 32\" 240Hz", "cat": "Monitor", "brand": "Samsung", "price": 2900000},
            {"name": "LG UltraGear 27GP850-B", "cat": "Monitor", "brand": "LG", "price": 1650000},
            {"name": "ASUS TUF Gaming VG249Q", "cat": "Monitor", "brand": "ASUS", "price": 950000},
            {"name": "Alienware AW3423DW QD-OLED", "cat": "Monitor", "brand": "Dell", "price": 5500000},
            {"name": "Gigabyte M27Q 170Hz QHD", "cat": "Monitor", "brand": "Gigabyte", "price": 1450000},
            
            # PSUs
            {"name": "Corsair RM850x 80+ Gold", "cat": "PSU", "brand": "Corsair", "price": 620000},
            {"name": "EVGA SuperNOVA 750 G6", "cat": "PSU", "brand": "EVGA", "price": 550000},
            {"name": "SeaSonic FOCUS GX-1000", "cat": "PSU", "brand": "SeaSonic", "price": 850000},
            {"name": "XPG Pylon 650W 80+ Bronze", "cat": "PSU", "brand": "XPG", "price": 280000},
        ]

        total_components = 0
        total_prices = 0
        
        for item in hardware_list:
            # Crear o buscar componente
            comp = db.query(database.Component).filter(database.Component.name == item["name"]).first()
            if not comp:
                comp = database.Component(name=item["name"], category=item["cat"], brand=item["brand"])
                db.add(comp)
                db.flush()
            
            # Crear listing (Simulado para que ML tenga de dónde agarrar)
            url = f"https://articulo.mercadolibre.com.co/MCO-{item['name'].replace(' ', '-').lower()}"
            listing = db.query(database.ProductListing).filter(database.ProductListing.url == url).first()
            if not listing:
                listing = database.ProductListing(component_id=comp.id, store_id=ml.id, url=url)
                db.add(listing)
                db.flush()

            # Añadir historial de precios REALISTA (60 días de data por componente)
            history_data = get_realistic_history(item["price"], days=60)
            for price_val, timestamp in history_data:
                hist = database.PriceHistory(
                    listing_id=listing.id,
                    price=float(round(price_val, -2)), # Redondear a cientos para realismo
                    currency="COP",
                    timestamp=timestamp
                )
                db.add(hist)
                total_prices += 1
            
            total_components += 1
        
        db.commit()
        logger.info(f"✅ Éxito: Se han añadido {total_components} componentes con {total_prices} registros de historial.")
    except Exception as e:
        logger.error(f"Error en seed masivo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Asegurar que DATABASE_URL use la ruta correcta si se corre desde la raíz
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "sqlite:///./backend/sql_app.db"
    massive_seed()
