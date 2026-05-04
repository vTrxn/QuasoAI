import sys
import os

# Añadir el path del backend para importar database
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import database

def seed():
    db = database.SessionLocal()
    try:
        # Algunos componentes de hardware
        hardware = [
            {"component_name": "NVIDIA RTX 4070", "category": "GPU", "price": 599.99, "store": "Amazon", "url": "https://amazon.com/rtx4070"},
            {"component_name": "AMD Ryzen 7 7800X3D", "category": "CPU", "price": 389.00, "store": "Newegg", "url": "https://newegg.com/7800x3d"},
            {"component_name": "Corsair Vengeance 32GB DDR5", "category": "RAM", "price": 115.50, "store": "BestBuy", "url": "https://bestbuy.com/corsair-ddr5"}
        ]
        
        # Nuevos periféricos
        peripherals = [
            {"component_name": "Logitech G Pro X Superlight", "category": "Periféricos", "price": 129.00, "store": "Amazon", "url": "https://amazon.com/gprox"},
            {"component_name": "Razer Huntsman V3 Pro", "category": "Periféricos", "price": 249.99, "store": "Razer Store", "url": "https://razer.com/huntsman-v3"},
            {"component_name": "SteelSeries Arctis Nova Pro", "category": "Periféricos", "price": 349.00, "store": "SteelSeries", "url": "https://steelseries.com/arctis-nova"}
        ]
        
        for item in hardware + peripherals:
            db_item = database.HardwareData(**item)
            db.add(db_item)
        
        db.commit()
        print("✅ Base de datos alimentada con éxito con hardware y periféricos.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
