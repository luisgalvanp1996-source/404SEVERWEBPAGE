from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.api import get, post
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
    # PRODUCTO SELECCIONADO
    # =========================
    if data.startswith("producto:"):
        slug = data.split(":")[1]

        resp = get(f"/bot/catalogo/{slug}")

        if not resp or resp.get("ok") is not True:
            await query.message.reply_text(
                f"{EMOJI_ERR} Error al cargar el producto"
            )
            return

        producto = resp["data"]
        variantes = producto.get("variantes", [])

        keyboard = []
        for v in variantes:
            keyboard.append([
                InlineKeyboardButton(
                    f"{producto['emoji']} {v}",
                    callback_data=f"variante:{slug}:{v}"
                )
            ])

        await query.message.reply_text(
            f"{producto['emoji']} *{producto['nombre']}*\n\nSelecciona una variante:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    # =========================
    # VARIANTE SELECCIONADA
    # =========================
    if data.startswith("variante:"):
        _, slug, variante = data.split(":")

        resp = post("/bot/pedido/item", {
            "id_pedido": pedido_id,
            "producto": slug,
            "variante": variante,
            "cantidad": 1
        })

        if not resp or resp.get("ok") is not True:
            await query.message.reply_text(
                f"{EMOJI_ERR} Error al agregar el producto"
            )
            return

        await query.message.reply_text(
            f"{EMOJI_OK} {slug.capitalize()} ({variante}) agregado al pedido\n\n"
            f"📋 /catalogo — Ver más productos\n"
            f"🧾 /lista — Ver pedido\n"
            f"📤 /enviar — Enviar pedido"
        )
