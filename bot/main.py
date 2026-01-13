from telegram.ext import Application, CommandHandler
import os
import shutil
import psutil
import requests
import logging
from dotenv import load_dotenv

# ======================
# LOGGING
# ======================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ======================
# CONFIGURACIÓN
# ======================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]

FLASK_API_BASE = os.getenv("FLASK_API_BASE", "http://127.0.0.1:5000/api")
FLASK_API_KEY = os.getenv("FLASK_API_KEY", "")

HEADERS = {
    "X-API-KEY": FLASK_API_KEY
} if FLASK_API_KEY else {}

# ======================
# HELPERS
# ======================

def bytes_a_gb(bytes_val):
    return round(bytes_val / (1024 ** 3), 2)

def es_admin(update):
    return update.effective_user.id in ADMIN_IDS

def log_comando(update, nombre):
    user = update.effective_user
    logger.info(
        f"Comando /{nombre} | user_id={user.id} | username={user.username}"
    )

# ======================
# COMANDOS BÁSICOS
# ======================

async def start(update, context):
    log_comando(update, "start")
    await update.message.reply_text(
        "🤖 Bot activo correctamente\nUsa /help"
    )

async def help_cmd(update, context):
    log_comando(update, "help")
    await update.message.reply_text("""
🤖 *Comandos disponibles*

/start   - Iniciar bot
/help    - Ayuda
/disk    - Espacio en discos
/ram     - Uso de memoria RAM
/cpu     - Uso de CPU
/status  - Estado API Flask

🔐 *Admin*
/restart - Reinicio lógico (ejemplo)
""", parse_mode="Markdown")

# ======================
# SISTEMA
# ======================

async def disk(update, context):
    log_comando(update, "disk")
    mensaje = "💾 *Espacio en discos*\n\n"

    for letra in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        ruta = f"{letra}:\\"
        if os.path.exists(ruta):
            total, usado, libre = shutil.disk_usage(ruta)
            mensaje += (
                f"*{letra}:*\n"
                f"  Total: {bytes_a_gb(total)} GB\n"
                f"  Libre: {bytes_a_gb(libre)} GB\n\n"
            )

    await update.message.reply_text(mensaje, parse_mode="Markdown")

async def ram(update, context):
    log_comando(update, "ram")
    mem = psutil.virtual_memory()

    await update.message.reply_text(
        f"🧠 *Memoria RAM*\n\n"
        f"Total: {bytes_a_gb(mem.total)} GB\n"
        f"Usada: {bytes_a_gb(mem.used)} GB\n"
        f"Libre: {bytes_a_gb(mem.available)} GB\n"
        f"Uso: {mem.percent}%",
        parse_mode="Markdown"
    )

async def cpu(update, context):
    log_comando(update, "cpu")
    uso = psutil.cpu_percent(interval=1)
    nucleos = psutil.cpu_count(logical=True)

    await update.message.reply_text(
        f"⚙️ *CPU*\n\n"
        f"Núcleos: {nucleos}\n"
        f"Uso actual: {uso}%",
        parse_mode="Markdown"
    )

# ======================
# FLASK API
# ======================

async def status(update, context):
    log_comando(update, "status")
    try:
        r = requests.get(f"{FLASK_API_BASE}/status", headers=HEADERS, timeout=5)
        data = r.json()

        await update.message.reply_text(
            f"🟢 *Flask API*\n\n"
            f"Estado: {data.get('status')}\n"
            f"Servidor: {data.get('server', 'N/A')}",
            parse_mode="Markdown"
        )
    except Exception:
        logger.exception("Error al consultar Flask API")
        await update.message.reply_text("🔴 Error al contactar API")

# ======================
# ADMIN
# ======================

async def restart(update, context):
    log_comando(update, "restart")
    if not es_admin(update):
        logger.warning(f"Acceso denegado a restart | user_id={update.effective_user.id}")
        await update.message.reply_text("⛔ No tienes permisos")
        return

    await update.message.reply_text("♻️ Reinicio solicitado (lógica pendiente)")
    logger.info("Reinicio autorizado")

# ======================
# MAIN
# ======================

def main():
    logger.info("Iniciando bot de Telegram...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("disk", disk))
    app.add_handler(CommandHandler("ram", ram))
    app.add_handler(CommandHandler("cpu", cpu))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("restart", restart))

    logger.info("🤖 Bot corriendo y esperando comandos")
    app.run_polling()

if __name__ == "__main__":
    main()
