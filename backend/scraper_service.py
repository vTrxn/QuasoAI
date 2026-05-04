import requests
import json
import re
import time
import random
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PriceExtractor:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def extract_from_url(self, url: str) -> Dict:
        """
        Visita la URL e intenta extraer Nombre y Precio.
        """
        # Evitar buscar en páginas de listados si Tavily las devuelve
        if "/listado." in url or "/p/" not in url and "mercadolibre" in url:
            if "/articulo.mercadolibre" not in url:
                return {"error": "URL de listado ignorada, solo proceso productos individuales."}

        try:
            # Pequeño delay aleatorio para parecer humano
            time.sleep(random.uniform(0.5, 1.5))
            
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": "https://www.google.com/"
            }

            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 429:
                return {"error": "Bloqueo por exceso de peticiones (429)."}
                
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # 1. Intentar JSON-LD
            data = self._extract_json_ld(soup)
            if data and data.get("price") and data.get("price") > 0:
                logger.info(f"Éxito con JSON-LD en {url}")
                return data
            
            # 2. Fallbacks específicos
            if "mercadolibre" in url:
                return self._scrape_mercadolibre(soup)
            elif "ktronix" in url or "alkosto" in url:
                return self._scrape_ktronix(soup)
            elif "tauret" in url:
                return self._scrape_tauret(soup)
            elif "clonesyperifericos" in url:
                return self._scrape_clones(soup)
                
            return {"error": "Estructura de tienda no reconocida."}
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {"error": f"Error de conexión: {str(e)}"}

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                if not script.string: continue
                data = json.loads(script.string)
                
                # Manejar listas de objetos
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if item.get("@type") == "Product" or "Product" in str(item.get("@type")):
                        name = item.get("name")
                        offers = item.get("offers")
                        price = None
                        
                        if isinstance(offers, dict):
                            price = offers.get("price")
                        elif isinstance(offers, list) and len(offers) > 0:
                            price = offers[0].get("price")
                        
                        if price:
                            # Limpiar precio de strings raros
                            price_val = str(price).replace("$", "").replace(" ", "").replace("\xa0", "")
                            return {"name": name, "price": float(price_val)}
            except:
                continue
        return None

    def _scrape_mercadolibre(self, soup: BeautifulSoup) -> Dict:
        # Selector meta (más estable)
        price_meta = soup.find("meta", itemprop="price")
        name_meta = soup.find("meta", {"name": "twitter:title"}) or soup.find("meta", property="og:title")
        
        if price_meta and name_meta:
            return {
                "name": name_meta.get("content").split("|")[0].strip(),
                "price": float(price_meta.get("content"))
            }
        
        # Fallback a clases CSS comunes en ML
        price_span = soup.select_one(".ui-pdp-price__second-line .andes-money-amount__fraction")
        name_h1 = soup.select_one(".ui-pdp-title")
        
        if price_span and name_h1:
            price_text = price_span.get_text().replace(".", "").replace(",", "")
            return {
                "name": name_h1.get_text().strip(),
                "price": float(price_text)
            }
            
        return {"error": "ML: No se encontró el precio en la página del producto."}

    def _scrape_ktronix(self, soup: BeautifulSoup) -> Dict:
        # Ktronix usa data attributes a veces
        price_element = soup.select_one(".price") or soup.select_one("[data-price-amount]")
        name_tag = soup.select_one("h1")
        
        if price_element:
            price_text = re.sub(r'[^\d]', '', price_element.get_text())
            if price_text:
                return {
                    "name": name_tag.get_text().strip() if name_tag else "Producto Ktronix",
                    "price": float(price_text)
                }
        return {"error": "Ktronix/Alkosto: Estructura no detectada."}

    def _scrape_tauret(self, soup: BeautifulSoup) -> Dict:
        price_tag = soup.select_one(".price-current") or soup.select_one(".product-price") or soup.select_one(".money")
        name_tag = soup.select_one(".product-title") or soup.select_one("h1")
        if price_tag:
            price_text = re.sub(r'[^\d]', '', price_tag.get_text())
            if price_text:
                return {
                    "name": name_tag.get_text().strip() if name_tag else "Producto Tauret",
                    "price": float(price_text)
                }
        return {"error": "Tauret: Estructura no detectada."}

    def _scrape_clones(self, soup: BeautifulSoup) -> Dict:
        price_tag = soup.select_one(".price-amount") or soup.select_one(".woocommerce-Price-amount")
        name_tag = soup.select_one(".product_title") or soup.select_one("h1")
        if price_tag:
            price_text = re.sub(r'[^\d]', '', price_tag.get_text())
            return {
                "name": name_tag.get_text().strip() if name_tag else "Producto Clones",
                "price": float(price_text)
            }
        return {"error": "Clones y Periféricos: Estructura no detectada."}

# Instancia global
scraper = PriceExtractor()
