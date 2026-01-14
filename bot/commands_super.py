#commands_super.py

from bot.storage import get_lista
from bot.helpers import subtotal
from bot.config import EMOJI_ADD, EMOJI_TRASH, EMOJI_MONEY

async def nuevo(update, context):
    user_id = update.effective_user.id
    get_lista(user_id).clear()
    await update.message.reply_text("🆕 Lista nueva iniciada")

async def listar(update, context):
    lista = get_lista(update.effective_user.id)

    if not lista:
        await update.message.reply_text("📭 La lista está vacía")
        return

    msg = "🧾 *Tu lista*\n\n"
    for i, item in enumerate(lista, 1):
        msg += f"{i}. {item['item']} - ${item['precio']:.2f}\n"

    msg += f"\nSubtotal: *${subtotal(lista):.2f}*"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def total_cmd(update, context):
    lista = get_lista(update.effective_user.id)
    await update.message.reply_text(
        f"{EMOJI_MONEY} Subtotal: ${subtotal(lista):.2f}"
    )

async def limpiar(update, context):
    get_lista(update.effective_user.id).clear()
    await update.message.reply_text(f"{EMOJI_TRASH} Lista limpiada")

async def agregar_item(update, context):
    texto = update.message.text.strip()

    partes = texto.rsplit(" ", 1)
    if len(partes) != 2:
        return

    item, precio = partes
    try:
        precio = float(precio)
    except ValueError:
        return

    lista = get_lista(update.effective_user.id)
    lista.append({"item": item, "precio": precio})

    await update.message.reply_text(
        f"{EMOJI_ADD} {item} - ${precio:.2f}\nSubtotal: ${subtotal(lista):.2f}"
    )
