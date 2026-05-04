import requests
import logging
import os
import time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import database
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MLApiService:
    def __init__(self, site_id: str = "MCO"):
        self.site_id = site_id
        self.base_url = f"https://api.mercadolibre.com/sites/{self.site_id}/search"
        self.token_url = "https://api.mercadolibre.com/oauth/token"
        self.client_id = os.getenv("ML_CLIENT_ID")
        self.client_secret = os.getenv("ML_CLIENT_SECRET")
        self._access_token = os.getenv("ML_ACCESS_TOKEN")
        self._token_expires_at = 0

    def _refresh_access_token(self):
        """
        Obtiene un nuevo access token usando el Client ID y Client Secret (OAuth Client Credentials).
        Nota: Para la búsqueda pública de ML, a veces se requiere el flujo de 'Client Credentials'.
        """
        if not self.client_id or not self.client_secret:
            logger.warning("ML_CLIENT_ID o ML_CLIENT_SECRET no configurados. Intentando sin auth.")
            return

        logger.info("Solicitando nuevo Access Token a Mercado Libre...")
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(self.token_url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            self._access_token = data.get("access_token")
            # El token suele durar 6 horas (21600 seg)
            self._token_expires_at = time.time() + data.get("expires_in", 21600) - 60 # 1 min de margen
            logger.info("Access Token obtenido con éxito.")
        except Exception as e:
            logger.error(f"Error al refrescar el token de ML: {e}")

    @property
    def access_token(self):
        if not self._access_token or time.time() > self._token_expires_at:
            self._refresh_access_token()
        return self._access_token

    def fetch_products(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Busca productos en Mercado Libre usando la API oficial.
        """
        params = {
            "q": query,
            "limit": limit
        }
        
        headers = {
            "User-Agent": "QuasoDataEngine/1.0",
            "Accept": "application/json"
        }
        
        token = self.access_token
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 403:
                logger.error(f"Error 403: Acceso prohibido. Detalles: {response.text}")
                return []
                
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logger.error(f"Error fetching from ML API: {e}")
            return []

    def process_and_save(self, db: Session, results: List[Dict], category: str):
        """
        Procesa los resultados de la API y los guarda en la base de datos.
        """
        store = db.query(database.Store).filter(database.Store.name == "MercadoLibre").first()
        if not store:
            store = database.Store(name="MercadoLibre", domain="mercadolibre.com.co")
            db.add(store)
            db.flush()

        new_items_count = 0
        for item in results:
            try:
                name = item.get("title")
                price = item.get("price")
                url = item.get("permalink")
                currency = item.get("currency_id", "COP")

                if not name or not price or not url:
                    continue

                component = db.query(database.Component).filter(database.Component.name == name).first()
                if not component:
                    component = database.Component(name=name, category=category)
                    db.add(component)
                    db.flush()

                listing = db.query(database.ProductListing).filter(database.ProductListing.url == url).first()
                if not listing:
                    listing = database.ProductListing(component_id=component.id, store_id=store.id, url=url)
                    db.add(listing)
                    db.flush()

                new_price = database.PriceHistory(
                    listing_id=listing.id, 
                    price=float(price),
                    currency=currency,
                    timestamp=datetime.utcnow()
                )
                db.add(new_price)
                new_items_count += 1

            except Exception as e:
                logger.error(f"Error processing item {item.get('id')}: {e}")
                continue
        
        db.commit()
        return new_items_count

ml_api_service = MLApiService()
