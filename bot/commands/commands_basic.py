#commands_basic.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


from bot.config.config import ADMIN_IDS,EMOJI_ERR
from bot.config.routes import registrar_usuario

async def start(update, context):
    user = update.effective_user

    try:
        data = registrar_usuario(update)
        tipo_usuario = data["data"]["tipo_usuario"]

        if tipo_usuario == "ADMIN":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➕ Nuevo trabajo",
                        callback_data="admin:nuevo"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📋 Trabajos pendientes",
                        callback_data="admin:pendientes"
                    )
                ]
            ]

            await update.message.reply_text(
                "🔧 *Panel de administración*\n\n"
                "Selecciona una opción:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        else:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "📋 Mis trabajos",
                        callback_data="cliente:trabajos"
                    )
                ]
            ]

            await update.message.reply_text(
                "👋 ¡Hola!\n\n"
                "Desde aquí puedes consultar el estado de tus trabajos.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception:
        await update.message.reply_text(
            f"{EMOJI_ERR} No pude conectar con el servidor.\n"
            "Intenta nuevamente en unos momentos."
        )




async def help_cmd(update, context):

    user_id = update.effective_user.id

    if user_id in ADMIN_IDS:

        await update.message.reply_text(
            "🔧 *Ayuda — Administrador*\n\n"
            "📋 *Trabajos*\n"
            "/nuevo - Registrar un nuevo trabajo\n"
            "/lista - Ver trabajos registrados\n\n"
            "⚙️ *Administración*\n"
            "/admin - Abrir panel de administración\n\n"
            "ℹ️ /help - Mostrar esta ayuda",
            parse_mode="Markdown"
        )

    else:

        await update.message.reply_text(
            "👋 *Ayuda*\n\n"
            "📋 *Mis trabajos*\n"
            "/lista - Consultar tus trabajos y su estado\n\n"
            "ℹ️ /help - Mostrar esta ayuda",
            parse_mode="Markdown"
        )