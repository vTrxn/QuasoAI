import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    domain = Column(String) # p.ej. mercadolibre.com.co

class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True) # GPU, CPU, Periféricos
    brand = Column(String, nullable=True)

class ProductListing(Base):
    __tablename__ = "product_listings"
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    url = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    
    component = relationship("Component")
    store = relationship("Store")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("product_listings.id"))
    price = Column(Float)
    currency = Column(String, default="COP")
    trm_value = Column(Float, nullable=True) # Para el análisis de Data Science
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    listing = relationship("ProductListing")

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("components.id"))
    analysis_text = Column(String)
    sentiment = Column(String)
    recommendation = Column(String)
    is_alert = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Semilla de tiendas conocidas
    stores = [
        {"name": "MercadoLibre", "domain": "mercadolibre.com.co"},
        {"name": "Ktronix", "domain": "ktronix.com"},
        {"name": "Tauret", "domain": "tauretcomputadores.com"},
        {"name": "Alkosto", "domain": "alkosto.com"}
    ]
    for s in stores:
        if not db.query(Store).filter(Store.name == s["name"]).first():
            db.add(Store(**s))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
