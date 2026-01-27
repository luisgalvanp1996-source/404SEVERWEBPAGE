from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.config import TOKEN
# Comandos Admin
from bot.commands_admin import (
    cancelar,
    completar,
    pedidos,
    texto_admin
    )
# Comandos Básicos
from bot.commands_basic import (
    help_cmd
)
# Comandos cliente
from bot.commands_client import (
    start,
    nuevo,
    lista,
    enviar,
    catalogo
)

# Callbacks inline
from bot.callbacks import catalogo_callback


def run_bot():
    app = Application.builder().token(TOKEN).build()

    # =========================
    # COMANDOS
    # =========================
    # Comandos Cliente
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuevo", nuevo))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("catalogo", catalogo))

    # Comandos Básicos
    app.add_handler(CommandHandler("help", help_cmd))

    # Comandos Admin
    app.add_handler(CommandHandler("pedidos", pedidos))
    app.add_handler(CommandHandler("cancelar", cancelar))
    app.add_handler(CommandHandler("completar", completar))
    app.add_handler(CommandHandler("texto_admin", texto_admin))



    # =========================
    # CALLBACKS (INLINE BUTTONS)
    # =========================
    app.add_handler(CallbackQueryHandler(catalogo_callback))

    print("🤖 Bot de telegram corriendo...")
    app.run_polling()
