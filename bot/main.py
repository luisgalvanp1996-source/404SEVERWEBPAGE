from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.config.config import TOKEN

# COMANDOS ADMIN

from bot.commands.commands_admin import (
    panel_admin,
    pendientes,
    nuevo_trabajo,
    seleccionar_cliente,
    seleccionar_equipo,
    seleccionar_tipo,
    crear_trabajo,
    texto_admin
)
# COMANDOS BÁSICOS

from bot.commands.commands_basic import (
    start,
    help_cmd
)

# COMANDOS CLIENTE

from bot.commands.commands_client import (
    nuevo,
    lista,
    enviar,
    catalogo
)

# CALLBACKS INLINE

from bot.templates.callbacks import catalogo_callback

#######################################################################################

def run_bot():

    app = Application.builder().token(TOKEN).build()

    # COMANDOS CLIENTE

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nuevo", nuevo))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("catalogo", catalogo))

    # COMANDOS BÁSICOS

    app.add_handler(CommandHandler("help", help_cmd))

    # COMANDOS ADMIN

    app.add_handler(CommandHandler("admin", panel_admin))
    app.add_handler(CommandHandler("texto_admin", texto_admin))

    # CALLBACKS INLINE

    app.add_handler(
        CallbackQueryHandler(catalogo_callback)
    )

    # MENSAJES DE TEXTO

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            texto_admin
        )
    )

    print("🤖 Bot de Telegram corriendo...")

    app.run_polling()


if __name__ == "__main__":
    run_bot()