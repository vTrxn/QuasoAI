import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class SearchService:
    def __init__(self):
        # Google Config
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_cx = os.getenv("GOOGLE_SEARCH_CX")
        
        # Tavily Config (Bypass)
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        # Tiendas objetivo en Colombia
        self.target_domains = [
            "mercadolibre.com.co",
            "ktronix.com",
            "tauretcomputadores.com",
            "alkosto.com",
            "clonesyperifericos.com"
        ]

    def find_products(self, query: str) -> List[str]:
        """
        Busca un componente y devuelve una lista de URLs.
        Prioriza Tavily si está disponible para evitar errores de Google.
        """
        if self.tavily_api_key:
            return self._find_with_tavily(query)
        else:
            return self._find_with_google(query)

    def _find_with_tavily(self, query: str) -> List[str]:
        print(f"🔍 Buscando con Tavily: {query}")
        url = "https://api.tavily.com/search"
        
        # Optimizamos el query para tiendas de Colombia
        site_restriction = " OR ".join(self.target_domains)
        full_query = f"{query} price Colombia in ({site_restriction})"
        
        payload = {
            "api_key": self.tavily_api_key,
            "query": full_query,
            "search_depth": "advanced",
            "include_domains": self.target_domains,
            "max_results": 5
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            links = [result["url"] for result in data.get("results", [])]
            return links
        except Exception as e:
            print(f"Error en búsqueda Tavily: {e}")
            return []

    def _find_with_google(self, query: str) -> List[str]:
        if not self.google_api_key:
            return []
            
        print(f"🔍 Buscando con Google: {query}")
        site_restriction = " OR ".join([f"site:{domain}" for domain in self.target_domains])
        full_query = f"{query} ({site_restriction})"
        
        params = {
            "key": self.google_api_key,
            "cx": self.google_cx,
            "q": full_query,
            "num": 5
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()
            data = response.json()
            return [item["link"] for item in data.get("items", [])]
        except Exception as e:
            print(f"Error en búsqueda Google: {e}")
            return []

search_service = SearchService()
