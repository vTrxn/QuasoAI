import os
import logging
from groq import AsyncGroq
from sqlalchemy.orm import Session
from typing import List, Optional
import database
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class QuasoBrain:
    def __init__(self):
        self.client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
        self.model = "llama-3.3-70b-versatile"
        self.system_persona = """Eres 'Quaso', un analista de mercado de hardware de alto nivel y experto en Machine Learning radicado en Colombia.
Tu estilo de comunicación es corporativo, directo, muy inteligente y altamente técnico, pero accesible.
NUNCA uses saludos robóticos como 'Hola, soy un asistente virtual'. Eres un experto financiero y de hardware.
Responde siempre usando un formato profesional, usando viñetas si es necesario, y un lenguaje persuasivo orientado a datos."""

    async def chat(self, prompt: str) -> dict:
        """Permite hablar con el bot dinámicamente sin comandos pre-establecidos."""
        if not self.client:
            return {"error": "GROQ API Key no configurada."}
        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_persona},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=800
            )
            return {"response": completion.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error en QuasoBrain Chat: {e}")
            return {"error": str(e)}

    async def interpret_prediction(self, prediction_data: dict) -> dict:
        """Toma los fríos datos del ML y los convierte en un informe profesional de mercado."""
        if not self.client:
            return {"error": "GROQ API Key no configurada."}
            
        context = f"""
DATOS TÉCNICOS DEL MODELO DE MACHINE LEARNING:
Componente: {prediction_data.get('name', 'Desconocido')}
Precio Actual: ${prediction_data.get('current_price', 0):,.0f} COP
Precio Estimado (7 días): ${prediction_data.get('predicted_price', 0):,.0f} COP
Variación Porcentual: {prediction_data.get('pct_change', 0):+.2f}%
Tendencia Matemática: {prediction_data.get('trend', 'Desconocida')}
Nivel de Confianza del Modelo: {prediction_data.get('confidence', 'Desconocida')}
Puntos de datos usados: {prediction_data.get('data_points', 0)}
"""
        user_prompt = f"""El motor de regresión log-lineal ha arrojado los siguientes resultados predictivos para este componente. 
Redacta un informe ejecutivo (máximo 3 párrafos cortos) interpretando estos datos para el cliente. 
¿Debería comprar ahora o esperar? ¿Qué significa este porcentaje de variación en el mercado real? 
Usa un tono analítico e incluye los datos financieros explícitamente. No uses markdown de título (#).

{context}"""

        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_persona},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=600
            )
            return {
                "interpretation": completion.choices[0].message.content,
                "raw_data": prediction_data
            }
        except Exception as e:
            logger.error(f"Error en ML Interpretation: {e}")
            return {"error": str(e)}

    async def get_market_insight(self, component_name: str, db: Session) -> dict:
        """
        Analiza un componente específico usando datos históricos reales de la DB y la lógica de Intelligence Service.
        """
        if not self.client:
            return {"error": "GROQ_API_KEY no configurada."}

        component = db.query(database.Component).filter(database.Component.name == component_name).first()
        if not component:
            return {"error": "Componente no encontrado en la base de datos."}

        import intelligence_service
        latest_price_entry = db.query(database.PriceHistory).join(database.ProductListing).filter(
            database.ProductListing.component_id == component.id
        ).order_by(database.PriceHistory.timestamp.desc()).first()
        
        current_price = latest_price_entry.price if latest_price_entry else 0

        historical_prices = intelligence_service.get_historical_data(db, component.id, days=30)
        avg_price = sum(historical_prices) / len(historical_prices) if historical_prices else current_price
        
        intel = intelligence_service.analyze_listing(db, component.id, current_price)
        traffic_light = intel["traffic_light"]
        glitch = intel["glitch"]
        
        trend_str = f"{traffic_light['color']} {traffic_light['recommendation']}"

        user_prompt = f"""DATOS ACTUALES DEL COMPONENTE '{component_name}':
- Categoría: {component.category}
- Precio Actual: ${current_price:,.0f} COP
- Precio Promedio (30 días): ${avg_price:,.0f} COP
- Estado del Semáforo (Algoritmo Quaso): {traffic_light['status']} ({traffic_light['recommendation']})
- Glitch/Anomalía Detectada: {'Sí, caída del ' + str(glitch.get('drop_percentage', 0)) + '%' if glitch.get('is_glitch') else 'No'}

Haz un análisis profundo del panorama actual de este producto. 
¿Es competitivo frente a otras opciones (como Intel vs AMD, o equivalentes en GPU)?
Debes usar la decisión de la IA algorítmica (Estado del Semáforo y Glitches) como base absoluta de tu veredicto: COMPRA FUERTE, MANTENER, o EVITAR."""

        try:
            completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_persona},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.6,
                max_tokens=600
            )
            
            return {
                "component_name": component_name,
                "price_trend": trend_str,
                "ai_insight": completion.choices[0].message.content,
                "avg_price": avg_price,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error en QuasoBrain: {e}")
            return {"error": str(e)}

# Instancia global
brain = QuasoBrain()

