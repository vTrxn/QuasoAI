import os
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import Component, PriceHistory, ProductListing

# --- Inteligencia de Datos: El Cerebro ---

def get_current_trm() -> float:
    """
    Obtiene el valor actual de la TRM (Tasa Representativa del Mercado) USD a COP.
    """
    try:
        # Usar una API pública gratuita para la tasa de cambio USD -> COP
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        return data["rates"]["COP"]
    except Exception as e:
        print(f"Error fetching TRM: {e}")
        return 4000.0  # Fallback TRM

def get_historical_data(db: Session, component_id: int, days: int = 30):
    """Obtiene el historial de precios de un componente de los últimos N días."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(PriceHistory).join(ProductListing).filter(
        ProductListing.component_id == component_id,
        PriceHistory.timestamp >= cutoff_date
    ).order_by(PriceHistory.timestamp.asc()).all()
    
    if not history:
        return []
    return [h.price for h in history]

def evaluate_price_traffic_light(db: Session, component_id: int, current_price: float) -> dict:
    """
    Algoritmo 'Semáforo' (Buy, Wait, Average)
    Verde (Comprar): El precio actual es al menos un 10% menor que el promedio de los últimos 30 días.
    Rojo (Esperar): El precio actual es al menos un 10% mayor que el promedio.
    Amarillo (Promedio): El precio está dentro del rango normal.
    """
    prices = get_historical_data(db, component_id, days=30)
    
    if not prices or len(prices) < 3:
        return {"status": "Yellow", "recommendation": "Promedio / Sin datos suficientes", "color": "🟡"}
        
    avg_price = sum(prices) / len(prices)
    
    if current_price <= avg_price * 0.90:
        return {"status": "Green", "recommendation": "Comprar - Buen precio", "color": "🟢"}
    elif current_price >= avg_price * 1.10:
        return {"status": "Red", "recommendation": "Esperar - Precio alto", "color": "🔴"}
    else:
        return {"status": "Yellow", "recommendation": "Promedio - Precio normal", "color": "🟡"}

def detect_glitch(db: Session, component_id: int, current_price: float) -> dict:
    """
    Cazador de Glitches: Detecta una caída extrema de precio (> 50% de la media semanal).
    """
    prices = get_historical_data(db, component_id, days=7)
    
    if not prices or len(prices) < 2:
        return {"is_glitch": False}
        
    avg_price = sum(prices) / len(prices)
    
    # Si el precio baja un 50% o más de la media de la última semana, es un glitch.
    if current_price <= avg_price * 0.50:
        return {
            "is_glitch": True, 
            "drop_percentage": round((1 - (current_price / avg_price)) * 100, 2),
            "avg_price": avg_price
        }
        
    return {"is_glitch": False}

def calculate_overprice(trm_value: float, estimated_msrp_usd: float, current_price_cop: float) -> dict:
    """
    Calcula si el producto está sobrepreciado en Colombia vs su precio MSRP original.
    Asumimos un sobrecosto normal del 25% por importación/impuestos.
    """
    fair_price_cop = estimated_msrp_usd * trm_value * 1.25
    overprice_pct = ((current_price_cop - fair_price_cop) / fair_price_cop) * 100
    
    if overprice_pct > 20:
        return {"status": "Inflated", "message": f"Inflado injustificadamente por vendedor local (+{overprice_pct:.1f}%)"}
    elif overprice_pct < -10:
        return {"status": "Bargain", "message": "Ganga por debajo del MSRP global."}
    else:
        return {"status": "Fair", "message": "Precio justo acorde a TRM e impuestos."}

def analyze_listing(db: Session, component_id: int, current_price: float):
    """Orquesta el análisis de datos de un nuevo listing y devuelve los resultados."""
    traffic_light = evaluate_price_traffic_light(db, component_id, current_price)
    glitch_data = detect_glitch(db, component_id, current_price)
    
    # Para la correlación TRM, en la DB deberíamos tener MSRP. Como no lo tenemos, 
    # podemos hacer un estimado simple (precio actual en COP / TRM) para uso futuro,
    # o si se añade MSRP al modelo de datos.
    current_trm = get_current_trm()
    
    # Enviar alerta push si es Glitch o Verde (simulado, acá puede disparar async al bot de TG)
    # Retorna la inteligencia generada
    return {
        "traffic_light": traffic_light,
        "glitch": glitch_data,
        "trm": current_trm
    }
