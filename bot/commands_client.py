from bot.api import post, get
from bot.config import EMOJI_CART, EMOJI_OK, EMOJI_ERR
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def start(update, context):
    user = update.effective_user
    

    # Registrar usuario (idempotente)
    post("/bot/usuario", {
        "id_usuario_tg": user.id,
        "username": user.username,
        "nombre": user.first_name,
        "apellido": user.last_name
    })

    await update.message.reply_text(
        f"{EMOJI_CART} Bienvenido!\nUsa /help para ver ayuda"
    )


async def nuevo(update, context):
    user = update.effective_user

    # 🔒 ASEGURAR USUARIO ANTES DEL PEDIDO (FIX FK)
    post("/bot/usuario", {
        "id_usuario_tg": user.id,
        "username": user.username,
        "nombre": user.first_name,
        "apellido": user.last_name
    })

    # Crear pedido
    data = post("/bot/pedido", {
        "id_usuario_tg": user.id
    })

    context.user_data["pedido_id"] = data["id_pedido"]

    await update.message.reply_text(
        f"{EMOJI_OK} Pedido creado\nID: {data['id_pedido']}\n"
        f"Usa /catalogo para ver productos"
    )


async def lista(update, context):
    pedido_id = context.user_data.get("pedido_id")

    if not pedido_id:
        await update.message.reply_text(f"{EMOJI_ERR} No tienes pedido activo")
        return

    data = get(f"/bot/pedido/{pedido_id}")

    if not data["items"]:
        await update.message.reply_text("📭 Pedido vacío")
        return

    msg = "📦 *Tu pedido*\n\nUsa /enviar para enviar el pedido\n" f"Usa /catalogo para ver más productos\n\n"
    for i in data["items"]:
        msg += f"- {i['producto']} ({i['variante']}) x{i['cantidad']}\n"
        


    await update.message.reply_text(msg, parse_mode="Markdown")


async def enviar(update, context):
    pedido_id = context.user_data.get("pedido_id")

    if not pedido_id:
        await update.message.reply_text(f"{EMOJI_ERR} No hay pedido")
        return

    post("/bot/pedido/cerrar", {
        "id_pedido": pedido_id
    })

    context.user_data.pop("pedido_id", None)

    await update.message.reply_text(
        f"{EMOJI_OK} Pedido enviado, gracias!"
    )


async def catalogo(update, context):
    keyboard = [
        [
            InlineKeyboardButton("🍰 Cheesecake", callback_data="producto_cheesecake")
        ]
    ]

    await update.message.reply_text(
        "📋 *Catálogo*\n\nSelecciona un producto:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )



