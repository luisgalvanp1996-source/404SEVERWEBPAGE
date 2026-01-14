from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.config import TOKEN
from bot.commands_basic import start, help_cmd
from bot.commands_super import (
    nuevo, listar, total_cmd, limpiar, agregar_item
)

def main():
    app = Application.builder().token(TOKEN).build()

    # Básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    # Súper
    app.add_handler(CommandHandler("nuevo", nuevo))
    app.add_handler(CommandHandler("lista", listar))
    app.add_handler(CommandHandler("total", total_cmd))
    app.add_handler(CommandHandler("limpiar", limpiar))

    # Texto libre
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, agregar_item)
    )

    print("🛒 Bot del súper corriendo")
    app.run_polling()

if __name__ == "__main__":
    main()
