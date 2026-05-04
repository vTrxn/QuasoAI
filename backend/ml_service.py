import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import database

class PricePredictor:
    def __init__(self, db: Session):
        self.db = db

    def predict_component_price(self, component_id: int, days_ahead: int = 7):
        # Obtener historial de precios
        history = self.db.query(database.PriceHistory).join(database.ProductListing).filter(
            database.ProductListing.component_id == component_id
        ).all()

        if len(history) < 2:
            return {
                "error": "No hay suficientes datos para predecir.",
                "current_price": history[0].price if history else None
            }

        # Preparar datos para pandas
        data = [
            {"timestamp": h.timestamp.timestamp(), "price": h.price}
            for h in history
        ]
        df = pd.DataFrame(data)
        
        # Entrenar modelo (usamos log de precio para evitar valores negativos y capturar tendencias porcentuales)
        X = df[['timestamp']].values
        y = np.log(df['price'].values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predecir futuro
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        future_timestamp = future_date.timestamp()
        
        # Convertir de vuelta desde log
        prediction_log = model.predict([[future_timestamp]])[0]
        prediction = np.exp(prediction_log)
        
        # Calcular tendencia (pendiente sobre el precio real)
        last_price = df['price'].values[-1]
        diff = prediction - last_price
        pct_change = (diff / last_price) * 100
        
        trend = "ESTABLE ⚖️"
        if pct_change > 0.5: trend = "ALCISTA 📈"
        elif pct_change < -0.5: trend = "BAJISTA 📉"
        
        return {
            "name": history[0].listing.component.name,
            "current_price": float(last_price),
            "predicted_price": float(prediction),
            "trend": trend,
            "pct_change": float(pct_change),
            "days_ahead": days_ahead,
            "data_points": len(history),
            "confidence": "Baja ⚠️" if len(history) < 10 else "Media 🛡️" if len(history) < 40 else "Alta ✅"
        }

def get_prediction(db: Session, component_id: int):
    predictor = PricePredictor(db)
    return predictor.predict_component_price(component_id)
