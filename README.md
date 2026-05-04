# Quaso: Plataforma de Inteligencia de Datos Automatizada

Quaso es una solución integral diseñada para la recopilación, procesamiento y visualización de datos de manera automatizada. Permite a los usuarios realizar un seguimiento de temas de interés (como precios de hardware, estadísticas de mercado o rendimiento de palabras clave) mediante flujos de trabajo inteligentes y análisis potenciados por Inteligencia Artificial.

##  Arquitectura del Proyecto

El sistema está compuesto por cuatro pilares fundamentales, interconectados para ofrecer una experiencia profesional y escalable:

1.  **Automatización de Datos (El Motor):** Utiliza **n8n** para la creación de flujos de trabajo (cron jobs) que recolectan datos diariamente a través de web scraping o consumo de APIs externas.
2.  **Backend y Procesamiento de IA (El Cerebro):** Desarrollado con **FastAPI**. Se encarga de la limpieza de datos y la integración con APIs de IA (como Claude o Perplexity) para generar insights, detectar anomalías y analizar sentimientos.
3.  **Base de Datos y Autenticación (La Bóveda):** Gestión segura con **PostgreSQL** y **Supabase**, manejando la autenticación de usuarios (Auth) y el almacenamiento relacional de históricos y predicciones.
4.  **Frontend (La Cara):** Interfaz moderna y rápida construida con **React (Vite)** y **TypeScript**. Dashboard interactivo con visualizaciones dinámicas (Recharts/Chart.js) para interpretar los datos de forma clara.

##  Tecnologías Principales

*   **Backend:** FastAPI, Python, SQLAlchemy, Groq/Claude API.
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS (o Vanilla CSS), Recharts.
*   **Automatización:** n8n.
*   **Base de Datos:** PostgreSQL (Supabase).
*   **Infraestructura:** Docker, Docker Compose.

##  Instalación y Uso Local

### Requisitos Previos

*   Docker y Docker Compose.
*   Node.js (para desarrollo de frontend).
*   Python 3.12+ (para desarrollo de backend).

### Inicio Rápido

Para levantar todos los servicios (Backend, Frontend, n8n) utilizando Docker:

```bash
chmod +x start_local.sh
./start_local.sh
```

##  Estructura del Repositorio

*   `/backend`: Código fuente del servidor FastAPI y servicios de IA.
*   `/frontend`: Aplicación cliente en React.
*   `/n8n`: Configuraciones y flujos de trabajo para la automatización.
*   `docker-compose.yml`: Orquestación de contenedores.

---
Desarrollado con ❤️ por [vTrxn](https://github.com/vTrxn)
