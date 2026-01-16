#commands_basic.py

from bot.config import EMOJI_CART

async def start(update, context):
    await update.message.reply_text(
        f"{EMOJI_CART} Bot de lista del súper\nUsa /help"
    )

async def help_cmd(update, context):
    await update.message.reply_text(
        "/nuevo - Nuevo pedido\n"
        "/catalogo - Ver productos\n"
        "/lista - Ver pedido\n"
        "/enviar - Enviar pedido\n"
        "/help - Ayuda"
    )
