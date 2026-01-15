from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.api import post
from bot.config import EMOJI_OK, EMOJI_ERR


async def catalogo_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data
    pedido_id = context.user_data.get("pedido_id")

    # 🔒 Validar pedido activo
    if not pedido_id:
        await query.message.reply_text(
            f"{EMOJI_ERR} No tienes un pedido activo.\nUsa /nuevo primero."
        )
        return

    # =========================
    # PRODUCTO: CHEESECAKE
    # =========================
    if data == "producto_cheesecake":
        keyboard = [
            [
                InlineKeyboardButton("🍰 Fresa", callback_data="cheesecake_fresa"),
                InlineKeyboardButton("🍰 Chocolate", callback_data="cheesecake_chocolate")
            ]
        ]

        await query.message.reply_text(
            "🍰 *Cheesecake*\n\nSelecciona una variante:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # =========================
    # VARIANTES
    # =========================
    if data in ("cheesecake_fresa", "cheesecake_chocolate"):
        variante = "Fresa" if data.endswith("fresa") else "Chocolate"

        resp = post("/bot/pedido/item", {
            "id_pedido": pedido_id,
            "producto": "Cheesecake",
            "variante": variante,
            "cantidad": 1
        })

        if not resp or resp.get("ok") is not True:
            await query.message.reply_text(
                f"{EMOJI_ERR} Error al agregar el producto"
            )
            return

        await query.message.reply_text(
            f"{EMOJI_OK} Cheesecake ({variante}) agregado al pedido\n"
            f"Usa /catalogo para ver más productos\n"
            f"Usa /lista para ver tu pedido\n"
            f"O usa /enviar para enviar el pedido"
        )
