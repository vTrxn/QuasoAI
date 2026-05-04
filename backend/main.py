import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import database
import ai_service
import ai_brain
import scraper_service
import search_service
import ml_api_service
import ml_service
import intelligence_service
from urllib.parse import urlparse

app = FastAPI(title="Quaso: Data Architecture Engine")

# Inicializar Base de Datos
database.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URLIngest(BaseModel):
    url: str
    category: Optional[str] = "Hardware"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Quaso Data Architecture Engine is running"}

@app.post("/api/ingest/url")
def ingest_by_url(payload: URLIngest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Recibe una URL, extrae los datos automáticamente y los guarda en la estructura relacional.
    """
    url = payload.url
    domain = urlparse(url).netloc.replace("www.", "")
    
    # 1. Identificar o crear la tienda
    store = db.query(database.Store).filter(database.Store.domain.contains(domain)).first()
    if not store:
        store = database.Store(name=domain.split('.')[0].capitalize(), domain=domain)
        db.add(store)
        db.flush()

    # 2. Extraer datos en tiempo real
    data = scraper_service.scraper.extract_from_url(url)
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])

    # 3. Identificar o crear el componente
    component = db.query(database.Component).filter(database.Component.name == data["name"]).first()
    if not component:
        component = database.Component(name=data["name"], category=payload.category)
        db.add(component)
        db.flush()

    # 4. Identificar o crear el listing
    listing = db.query(database.ProductListing).filter(database.ProductListing.url == url).first()
    if not listing:
        listing = database.ProductListing(component_id=component.id, store_id=store.id, url=url)
        db.add(listing)
        db.flush()

    # 5. Guardar historial de precio
    current_trm = intelligence_service.get_current_trm()
    new_price = database.PriceHistory(listing_id=listing.id, price=data["price"], trm_value=current_trm)
    db.add(new_price)
    
    db.commit()
    
    # Evaluar Inteligencia de Datos
    intel = intelligence_service.analyze_listing(db, component.id, data["price"])
    if intel["glitch"].get("is_glitch") or intel["traffic_light"]["status"] == "Green":
        # Disparar alerta en background
        background_tasks.add_task(send_push_alert, component.name, data["price"], url, intel)

    # 6. Disparar análisis de IA en background
    background_tasks.add_task(process_ai_analysis, component.id, data["price"], db)

    return {
        "status": "success",
        "product": data["name"],
        "price": data["price"],
        "store": store.name
    }

@app.post("/api/discover")
def discover_and_ingest(query: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Busca productos en Google, visita cada link, extrae precios y guarda en la DB.
    """
    links = search_service.search_service.find_products(query)
    if not links:
        return {"status": "no_results", "message": "No se encontraron links para esta búsqueda."}

    results = []
    for url in links:
        try:
            # Reutilizamos la lógica de ingesta por URL para cada link encontrado
            res = ingest_by_url(URLIngest(url=url), background_tasks, db)
            results.append(res)
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})

    return {"status": "completed", "processed": len(results), "details": results}

@app.post("/api/discover/ml")
def discover_ml(query: str, category: str = "Hardware", db: Session = Depends(get_db)):
    """
    Busca productos directamente en la API de Mercado Libre e ingesta los resultados.
    """
    results = ml_api_service.ml_api_service.fetch_products(query)
    
    # Manejo de errores específicos
    if not results:
        # Podríamos verificar si es un error 403 o simplemente no hay resultados
        # Por ahora, damos una respuesta informativa
        return {
            "status": "error_or_empty", 
            "message": "No se obtuvieron resultados. Esto puede deberse a un bloqueo de IP (403) o a que no hay productos para esta búsqueda.",
            "action_required": "Si el problema persiste, añade un 'ML_ACCESS_TOKEN' válido al archivo .env para evitar bloqueos.",
            "link": "https://developers.mercadolibre.com.co/"
        }
    
    count = ml_api_service.ml_api_service.process_and_save(db, results, category)
    
    return {
        "status": "success",
        "message": f"Se procesaron {len(results)} productos, {count} fueron guardados/actualizados.",
        "query": query,
        "category": category
    }

def send_push_alert(component_name: str, price: float, url: str, intel: dict):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("ALERT_CHAT_ID")
    if not token or not chat_id:
        return
        
    status = intel["traffic_light"]
    msg = f"🚨 **ALERTA QUASO** 🚨\n\n"
    msg += f"🖥️ **{component_name}**\n"
    msg += f"💰 Precio Actual: ${price:,.0f} COP\n"
    
    if intel["glitch"].get("is_glitch"):
        glitch = intel["glitch"]
        msg += f"⚠️ **GLITCH DETECTADO:** Caída del {glitch['drop_percentage']}% respecto a la media de ${glitch['avg_price']:,.0f} COP.\n"
    
    msg += f"🚦 Estado: {status['color']} {status['recommendation']}\n\n"
    msg += f"🔗 [Ver Producto]({url})"
    
    tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    try:
        import requests
        requests.post(tg_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending push alert: {e}")

@app.get("/api/intelligence/{component_id}")
def get_component_intelligence(component_id: int, db: Session = Depends(get_db)):
    """Retorna la inteligencia de datos (Semáforo, Glitches, TRM) para un componente."""
    component = db.query(database.Component).filter(database.Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Componente no encontrado")
        
    latest_price_entry = db.query(database.PriceHistory).join(database.ProductListing).filter(
        database.ProductListing.component_id == component_id
    ).order_by(database.PriceHistory.timestamp.desc()).first()
    
    if not latest_price_entry:
        return {"status": "no_data"}
        
    intel = intelligence_service.analyze_listing(db, component_id, latest_price_entry.price)
    
    # Estimación de sobreprecio asumiendo un MSRP base falso por ahora (ej. el promedio / trm)
    # En un sistema real, sacaríamos el MSRP de la BD
    avg_price_cop = sum(intelligence_service.get_historical_data(db, component_id)) / max(1, len(intelligence_service.get_historical_data(db, component_id)))
    estimated_msrp = (avg_price_cop / intel["trm"]) / 1.25 if intel["trm"] > 0 else 0
    
    overprice_data = intelligence_service.calculate_overprice(intel["trm"], estimated_msrp, latest_price_entry.price)
    
    return {
        "component_name": component.name,
        "current_price": latest_price_entry.price,
        "traffic_light": intel["traffic_light"],
        "glitch_hunter": intel["glitch"],
        "trm_correlation": {
            "current_trm": intel["trm"],
            "estimated_msrp_usd": estimated_msrp,
            "overprice_analysis": overprice_data
        }
    }

@app.get("/api/components/dashboard")
def get_dashboard_components(db: Session = Depends(get_db)):
    """Retorna una lista de componentes con su estado de inteligencia actual para el Dashboard."""
    components = db.query(database.Component).all()
    results = []
    
    for comp in components:
        latest_price = db.query(database.PriceHistory).join(database.ProductListing).filter(
            database.ProductListing.component_id == comp.id
        ).order_by(database.PriceHistory.timestamp.desc()).first()
        
        if not latest_price:
            continue
            
        intel = intelligence_service.analyze_listing(db, comp.id, latest_price.price)
        
        # Get historical prices for the sparkline chart
        historical_prices = intelligence_service.get_historical_data(db, comp.id, days=30)
        # Format for recharts sparkline
        history_chart = [{"price": p} for p in historical_prices] if historical_prices else [{"price": latest_price.price}]

        results.append({
            "id": comp.id,
            "name": comp.name,
            "category": comp.category,
            "current_price": latest_price.price,
            "traffic_light": intel["traffic_light"],
            "glitch_hunter": intel["glitch"],
            "history": history_chart
        })
        
    return results

def process_ai_analysis(component_id: int, current_price: float, db: Session):
    # Lógica de análisis similar a la anterior pero adaptada a la nueva DB
    component = db.query(database.Component).filter(database.Component.id == component_id).first()
    if not component: return

    # Obtener historial para este componente a través de sus listings
    history = db.query(database.PriceHistory).join(database.ProductListing).filter(
        database.ProductListing.component_id == component_id
    ).order_by(database.PriceHistory.timestamp.desc()).limit(10).all()
    
    history_prices = [h.price for h in history]
    
    result = ai_service.analyze_data(component.name, current_price, history_prices, component.category)
    
    analysis = database.AIAnalysis(
        component_id=component_id,
        analysis_text=result["analysis_text"],
        sentiment=result["sentiment"],
        recommendation=result.get("recommendation")
    )
    db.add(analysis)
    db.commit()

@app.get("/api/ai/analyze/{component_id}")
async def analyze_component_with_brain(component_id: int, db: Session = Depends(get_db)):
    """
    Usa el 'Cerebro' de Quaso para analizar un componente basándose en datos reales de la DB.
    """
    component = db.query(database.Component).filter(database.Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Componente no encontrado")
    
    insight = await ai_brain.brain.get_market_insight(component.name, db)
    return insight

@app.get("/api/latest")
def get_all_components(db: Session = Depends(get_db)):
    """
    Retorna la lista de todos los componentes registrados para facilitar el uso de /analyze en Telegram.
    """
    return db.query(database.Component).all()

@app.get("/api/prices/latest")
def get_latest_prices(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(database.PriceHistory).join(database.ProductListing).join(database.Component)
    if category:
        query = query.filter(database.Component.category == category)
    
    items = query.order_by(database.PriceHistory.timestamp.desc()).limit(50).all()
    
    results = []
    for item in items:
        results.append({
            "name": item.listing.component.name,
            "category": item.listing.component.category,
            "price": item.price,
            "store": item.listing.store.name,
            "url": item.listing.url,
            "date": item.timestamp.isoformat()
        })
    return results

@app.get("/api/ai/predict/{component_id}")
def predict_price(component_id: int, db: Session = Depends(get_db)):
    """
    Predice el precio futuro de un componente usando Machine Learning (Linear Regression).
    """
    prediction = ml_service.get_prediction(db, component_id)
    return prediction

class ChatMessage(BaseModel):
    message: str

@app.post("/api/ai/chat")
async def chat_with_brain(payload: ChatMessage):
    """
    Habla dinámicamente con Quaso sin comandos estáticos.
    """
    response = await ai_brain.brain.chat(payload.message)
    return response

@app.get("/api/ai/predict_interpret/{component_id}")
async def interpret_predicted_price(component_id: int, db: Session = Depends(get_db)):
    """
    Genera una interpretación avanzada de los resultados del modelo de ML usando la IA.
    """
    prediction = ml_service.get_prediction(db, component_id)
    if "error" in prediction:
        return prediction
        
    interpretation = await ai_brain.brain.interpret_prediction(prediction)
    return interpretation
