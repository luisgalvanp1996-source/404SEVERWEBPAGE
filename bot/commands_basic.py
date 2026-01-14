#commands_basic.py

from bot.config import EMOJI_CART

async def start(update, context):
    await update.message.reply_text(
        f"{EMOJI_CART} Bot de lista del súper\nUsa /help"
    )

async def help_cmd(update, context):
    await update.message.reply_text("""
🛒 *Lista del súper*

/nuevo   - Nueva lista
/lista   - Ver artículos
/total   - Subtotal
/limpiar - Vaciar lista

➕ Para agregar:
`articulo precio` 
Ejemplo:
pan 35
""", parse_mode="Markdown")
