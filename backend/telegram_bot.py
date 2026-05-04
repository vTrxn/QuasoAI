import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar .env del padre si existe, si no del actual
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
API_URL = f"http://{BACKEND_HOST}:8000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /start recibido de {update.effective_user.username}")
    status_msg = await update.message.reply_text("Iniciando mi sistema cognitivo...")
    try:
        user_name = update.effective_user.first_name
        prompt = f"El usuario {user_name} acaba de iniciar el bot por primera vez. Preséntate brevemente como el Cerebro Quaso, el experto en hardware e IA. Menciona que puedes analizar el mercado (/analyze <id>), predecir precios con ML (/predict <id>), buscar ofertas (/search <query>) y que también pueden simplemente hablarte o preguntarte cualquier duda del mercado tecnológico."
        
        def call_chat():
            return requests.post(f"{API_URL}/api/ai/chat", json={"message": prompt}, timeout=20)
            
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_chat)
        
        if response.status_code == 200:
            data = response.json()
            await status_msg.edit_text(data.get("response", "Error leyendo IA."), parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ Error conectando con el cerebro de Quaso.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error de IA: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Mensaje recibido: {user_text}")
    
    # Enviar acción de 'escribiendo...'
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        def call_chat():
            return requests.post(f"{API_URL}/api/ai/chat", json={"message": user_text}, timeout=30)
            
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_chat)
        
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(data.get("response", "Error procesando el mensaje."))
        else:
            await update.message.reply_text("❌ Mis servidores cognitivos están saturados en este momento.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error de red con IA: {str(e)}")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/search <producto>`")
        return
    
    query = " ".join(context.args)
    status_msg = await update.message.reply_text(f"🔍 Buscando '{query}' en Mercado Libre Colombia...")
    
    try:
        def call_ml():
            return requests.post(f"{API_URL}/api/discover/ml?query={query}", timeout=60)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_ml)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                await status_msg.edit_text("😔 No encontré resultados en Mercado Libre.")
                return
            msg = f"✅ **Resultados para: {query}**\n\n"
            for item in data[:5]:
                msg += f"🔹 **{item['name']}**\n"
                msg += f"💰 ${item['price']:,.0f} COP\n"
                msg += f"🔗 [Ver en ML]({item['url']})\n\n"
            await status_msg.edit_text(msg, disable_web_page_preview=True)
        else:
            await status_msg.edit_text(f"⚠️ Error en la API de Mercado Libre: {response.status_code}")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error de conexión: {str(e)}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/analyze <id_del_componente>`\nTip: Usa `/latest` para ver los IDs.")
        return
    
    comp_id = context.args[0]
    status_msg = await update.message.reply_text(f"🧠 Consultando mis registros históricos y evaluando el componente #{comp_id}...")
    
    try:
        def call_brain():
            return requests.get(f"{API_URL}/api/ai/analyze/{comp_id}", timeout=60)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_brain)
        
        if response.status_code == 200:
            data = response.json()
            msg = f"🤖 **Veredicto Quaso: {data['component_name']}**\n\n"
            msg += f"{data['ai_insight']}\n\n"
            msg += f"📊 **Tendencia Macro:** {data['price_trend']}\n"
            try:
                await status_msg.edit_text(msg, parse_mode='Markdown')
            except Exception as markdown_error:
                logger.warning(f"Markdown parsing failed, sending raw text: {markdown_error}")
                await status_msg.edit_text(msg)
        else:
            await status_msg.edit_text("❌ No pude analizar ese componente. ¿El ID es correcto?")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error en el Cerebro: {str(e)}")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: `/predict <id_del_componente>`")
        return
    
    comp_id = context.args[0]
    status_msg = await update.message.reply_text(f"📉 Entrenando modelo ML en tiempo real para el componente #{comp_id} e interpretando resultados...")
    
    try:
        def call_ml_interpret():
            return requests.get(f"{API_URL}/api/ai/predict_interpret/{comp_id}", timeout=40)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, call_ml_interpret)
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                await status_msg.edit_text(f"⚠️ {data['error']}")
                return
                
            msg = f"🔮 Predicción y Análisis ML\n\n"
            msg += f"{data.get('interpretation', 'No se pudo generar la interpretación.')}\n"
            await status_msg.edit_text(msg)
        else:
            await status_msg.edit_text("❌ Error al calcular la predicción.")
    except Exception as e:
        await status_msg.edit_text(f"❌ Error de conexión ML: {str(e)}")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Consultando últimos componentes")
    try:
        response = requests.get(f"{API_URL}/api/latest", timeout=10)
        
        if response.status_code == 200:
            items = response.json()
            if not items:
                await update.message.reply_text("Aún no hay componentes registrados.")
                return

            res = "🚀 Componentes en DB (Usa el ID para /analyze o /predict):\n\n"
            for item in items[:15]:
                comp_id = item.get('id', '?')
                name = item.get('name', 'Desconocido')
                res += f"ID: {comp_id} | {name}\n"
            
            await update.message.reply_text(res)
        else:
            await update.message.reply_text("⚠️ No pude obtener la lista de componentes.")
    except Exception as e:
        await update.message.reply_text(f"Error de conexión: {e}")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = f"🔔 **Suscripción a Alertas Quaso** 🔔\n\n"
    msg += f"Tu `CHAT_ID` es: `{chat_id}`\n\n"
    msg += f"Para recibir alertas automáticas (Glitches y Semáforo Verde), asegúrate de que tu archivo `.env` en el backend contenga esta línea:\n"
    msg += f"`ALERT_CHAT_ID={chat_id}`\n\n"
    msg += "Reinicia el backend si acabas de agregarlo."
    await update.message.reply_text(msg, parse_mode='Markdown')

def run_bot():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN no configurado.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("latest", latest))
    app.add_handler(CommandHandler("subscribe", subscribe))
    
    # Manejador de texto generico (conversacional)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info(f"Bot Quaso iniciado en {API_URL} con Token: {TELEGRAM_TOKEN[:10]}...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
n_bot()
