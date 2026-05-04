from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import database
import ai_service

app = FastAPI(title="Smart Analytics SaaS API")

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

class HardwareDataIn(BaseModel):
    component_name: str
    category: str
    price: float
    store: str
    url: str

class HardwareDataOut(HardwareDataIn):
    id: int
    scraped_at: str

    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Smart Analytics SaaS API is running"}

@app.post("/api/webhook/ingest")
def ingest_data(data: List[HardwareDataIn], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Webhook for n8n to push scraped data"""
    for item in data:
        db_item = database.HardwareData(**item.dict())
        db.add(db_item)
    
    db.commit()
    
    # Trigger AI analysis in background for the first item as a demo
    if data:
        background_tasks.add_task(process_ai_analysis, data[0].component_name, data[0].price, db)

    return {"status": "success", "inserted": len(data)}

def process_ai_analysis(component_name: str, current_price: float, db: Session):
    # Get last 5 prices for context
    history = db.query(database.HardwareData).filter(database.HardwareData.component_name == component_name).order_by(database.HardwareData.scraped_at.desc()).limit(5).all()
    history_prices = [h.price for h in history]
    
    result = ai_service.analyze_price_trend(component_name, current_price, history_prices)
    
    analysis = database.AIAnalysis(
        component_name=component_name,
        analysis_text=result["analysis_text"],
        sentiment=result["sentiment"]
    )
    db.add(analysis)
    db.commit()

@app.get("/api/hardware", response_model=List[HardwareDataOut])
def get_hardware_data(db: Session = Depends(get_db)):
    """Get all hardware data for dashboard"""
    items = db.query(database.HardwareData).order_by(database.HardwareData.scraped_at.desc()).limit(100).all()
    # Convert datetime to string for Pydantic
    for item in items:
        item.scraped_at = item.scraped_at.isoformat()
    return items

@app.get("/api/analysis")
def get_ai_analysis(db: Session = Depends(get_db)):
    """Get latest AI analysis for dashboard"""
    items = db.query(database.AIAnalysis).order_by(database.AIAnalysis.created_at.desc()).limit(10).all()
    return items
