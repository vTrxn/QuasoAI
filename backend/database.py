import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/quaso")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class HardwareData(Base):
    __tablename__ = "hardware_data"

    id = Column(Integer, primary_key=True, index=True)
    component_name = Column(String, index=True)
    category = Column(String) # CPU, GPU, RAM
    price = Column(Float)
    store = Column(String)
    url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    component_name = Column(String, index=True)
    analysis_text = Column(String)
    sentiment = Column(String) # Positive, Negative, Neutral (e.g., price dropping is positive)
    recommendation = Column(String, nullable=True) # Buy, Wait, Sell
    is_alert = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
