from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.config import TOKEN

# Comandos cliente
from bot.commands_client import (
    start,
    nuevo,
    lista,
    enviar,
    catalogo,
    help_cmd
)

# Callbacks inline
from bot.callbacks import catalogo_callback


def run_bot():
    app = Application.builder().token(TOKEN).build()

    # =========================
    # COMANDOS
    # =========================
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuevo", nuevo))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("catalogo", catalogo))
    app.add_handler(CommandHandler("help", help_cmd))

    # =========================
    # CALLBACKS (INLINE BUTTONS)
    # =========================
    app.add_handler(CallbackQueryHandler(catalogo_callback))

    print("🤖 Bot de pedidos corriendo...")
    app.run_polling()
