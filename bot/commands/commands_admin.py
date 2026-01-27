from bot.database.api import post, get, refresh
from bot.config.state import set_admin_action, get_admin_action, clear_admin_action
from bot.config.config import ADMIN_IDS, EMOJI_OK, EMOJI_ERR

def es_admin(update):
    return update.effective_user.id in ADMIN_IDS



async def pedidos(update, context):
    if not es_admin(update):
        await update.message.reply_text("⛔ No autorizado")
        return

    try:
        data = get("/bot/pedidos/pendientes")
    except Exception:
        await update.message.reply_text("❌ Error consultando pedidos")
        return

    if not data:
        await update.message.reply_text("📭 No hay pedidos pendientes")
        return

    msg = "📦 *Pedidos pendientes*\n\n"

    for pedido_id, items in data.items():
        msg += f"*Pedido #{pedido_id}*\n{data[pedido_id][0]['usuario']['nombre']} {data[pedido_id][0]['usuario']['apellido']} (@{data[pedido_id][0]['usuario']['username']})\n"
        for i in items:
            msg += f"- {i['producto']} {i['variante']} x{i['cantidad']}\n"
        msg += "\n"

    await update.message.reply_text(msg, parse_mode="Markdown")



async def completar(update, context):
    if not es_admin(update):
        return

    set_admin_action(context, "completar")
    await update.message.reply_text("✏️ Escribe el ID del pedido a COMPLETAR")


async def cancelar(update, context):
    if not es_admin(update):
        return

    set_admin_action(context, "cancelar")
    await update.message.reply_text("✏️ Escribe el ID del pedido a CANCELAR")


async def texto_admin(update, context):
    action = get_admin_action(context)
    if not action:
        return

    pedido_id = update.message.text.strip()

    if not pedido_id.isdigit():
        await update.message.reply_text("❌ ID inválido")
        return

    post("/bot/pedido/cerrar", {
        "id_pedido": int(pedido_id)
    })

    clear_admin_action(context)

    await update.message.reply_text(
        f"{EMOJI_OK} Pedido {pedido_id} actualizado ({action})"
    )
