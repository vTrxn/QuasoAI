import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We fall back to a mock if no API key is provided
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

def analyze_price_trend(component_name: str, price: float, historical_prices: list[float]) -> dict:
    if not client:
        return {
            "analysis_text": f"Mock Analysis: The price of {component_name} is currently ${price}. No API key configured.",
            "sentiment": "Neutral"
        }
    
    prompt = f"Analyze the current price of {component_name} (${price}) considering these past prices: {historical_prices}. Is it a good time to buy? Keep the analysis short (max 3 sentences). Also, provide a sentiment: 'Positive' (good to buy), 'Negative' (bad to buy), or 'Neutral'."
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a hardware market expert. Format your response EXACTLY as: 'Analysis: [your analysis] | Sentiment: [Positive/Negative/Neutral]'"
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
            max_tokens=150
        )
        
        response_text = chat_completion.choices[0].message.content
        parts = response_text.split("| Sentiment:")
        
        analysis = parts[0].replace("Analysis:", "").strip()
        sentiment = parts[1].strip() if len(parts) > 1 else "Neutral"
        
        return {
            "analysis_text": analysis,
            "sentiment": sentiment
        }
    except Exception as e:
        return {
            "analysis_text": f"Error analyzing data: {str(e)}",
            "sentiment": "Neutral"
        }
