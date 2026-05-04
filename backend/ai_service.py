import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq") # groq, anthropic, or perplexity
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def analyze_data(component_name: str, current_value: float, history: list[float], category: str = "Hardware") -> dict:
    prompt = f"""
    Eres un analista experto en el mercado de {category}.
    Analiza el valor actual de '{component_name}': {current_value}.
    Historial reciente de valores: {history}.
    
    Tu tarea:
    1. Identifica tendencias (alza, baja, estabilidad) del componente.
    2. Si conoces componentes similares o de la competencia, realiza una breve comparación de valor (ej. vs AMD o Nvidia).
    3. Detecta anomalías si las hay.
    4. Proporciona una recomendación accionable (Comprar, Esperar, Vender).
    
    Formato de respuesta:
    RESUMEN: [Tu análisis comparativo en max 3 frases]
    SENTIMIENTO: [Positivo/Negativo/Neutral]
    RECOMENDACION: [Acción sugerida]
    """
    
    if AI_PROVIDER == "groq" and GROQ_API_KEY:
        return _analyze_with_groq(prompt)
    elif AI_PROVIDER == "perplexity" and PERPLEXITY_API_KEY:
        return _analyze_with_perplexity(prompt)
    else:
        # Mock for development
        return {
            "analysis_text": f"Análisis Mock para {component_name}: La tendencia parece estable a {current_value}. Historial: {history}.",
            "sentiment": "Neutral",
            "recommendation": "Esperar"
        }

def _analyze_with_groq(prompt: str) -> dict:
    client = Groq(api_key=GROQ_API_KEY)
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            max_tokens=200
        )
        return _parse_response(completion.choices[0].message.content)
    except Exception as e:
        return {"analysis_text": f"Error Groq: {str(e)}", "sentiment": "Neutral", "recommendation": "Error"}

def _analyze_with_perplexity(prompt: str) -> dict:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-small-online",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return _parse_response(data["choices"][0]["message"]["content"])
    except Exception as e:
        return {"analysis_text": f"Error Perplexity: {str(e)}", "sentiment": "Neutral", "recommendation": "Error"}

def _parse_response(text: str) -> dict:
    # Simple parser for the expected format
    res = {"analysis_text": text, "sentiment": "Neutral", "recommendation": "N/A"}
    
    if "SENTIMIENTO:" in text:
        parts = text.split("SENTIMIENTO:")
        res["analysis_text"] = parts[0].replace("RESUMEN:", "").strip()
        
        remaining = parts[1].split("RECOMENDACION:")
        res["sentiment"] = remaining[0].strip()
        if len(remaining) > 1:
            res["recommendation"] = remaining[1].strip()
            
    return res
