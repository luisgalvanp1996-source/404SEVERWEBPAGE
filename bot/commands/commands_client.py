from bot.database.api import post, get
from bot.config.config import EMOJI_OK, EMOJI_ERR
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# =========================================================
# 👤 USUARIO
# =========================================================

def registrar_usuario(update):
    user = update.effective_user

    return post("/bot/usuario", {
        "id_usuario_tg": user.id,
        "username": user.username,
        "nombre": user.first_name,
        "apellido": user.last_name
    })


# =========================================================
# 🤖 START
# =========================================================

async def start(update, context):
    try:
        data = registrar_usuario(update)

        # IMPORTANTE:
        # registrar_usuario es síncrona porque api.py utiliza requests.
        # El resultado se obtiene directamente.

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

    except Exception as e:
        await update.message.reply_text(
            f"{EMOJI_ERR} No pude conectar con el servidor.\n"
            f"Intenta nuevamente en unos momentos."
        )


# =========================================================
# 📋 MIS TRABAJOS
# =========================================================

async def mis_trabajos(update, context):
    user = update.effective_user

    try:
        usuario = get(f"/bot/usuario/{user.id}")

        if not usuario or usuario.get("ok") is not True:
            await update.message.reply_text(
                f"{EMOJI_ERR} No se encontró tu usuario."
            )
            return

        id_cliente = usuario["data"].get("id_cliente")

        if not id_cliente:
            await update.message.reply_text(
                "ℹ️ Todavía no tienes trabajos registrados."
            )
            return

        data = get(
            f"/bot/cliente/{id_cliente}/trabajos"
        )

        trabajos = data.get("data", [])

        if not trabajos:
            await update.message.reply_text(
                "📭 No tienes trabajos registrados."
            )
            return

        keyboard = []

        for trabajo in trabajos:
            keyboard.append([
                InlineKeyboardButton(
                    f"{trabajo['folio']} · {trabajo['estatus']}",
                    callback_data=f"cliente:trabajo:{trabajo['id_trabajo']}"
                )
            ])

        await update.message.reply_text(
            "📋 *Mis trabajos*\n\n"
            "Selecciona un trabajo:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    except Exception:
        await update.message.reply_text(
            f"{EMOJI_ERR} No pude consultar tus trabajos."
        )


# =========================================================
# 🔎 DETALLE DE TRABAJO
# =========================================================

async def detalle_trabajo(update, context, id_trabajo):
    try:
        data = get(
            f"/bot/trabajo/{id_trabajo}"
        )

        if not data or data.get("ok") is not True:
            await update.callback_query.message.reply_text(
                f"{EMOJI_ERR} Trabajo no encontrado."
            )
            return

        trabajo = data["data"]

        mensaje = (
            f"📋 *{trabajo['folio']}*\n\n"
            f"📌 Estado: *{trabajo['estatus']}*\n"
            f"🔧 Tipo: {trabajo['tipo_trabajo']}\n\n"
        )

        if trabajo.get("descripcion"):
            mensaje += (
                f"📝 *Descripción*\n"
                f"{trabajo['descripcion']}\n\n"
            )

        if trabajo.get("fecha_registro"):
            mensaje += (
                f"📅 Registrado: "
                f"{trabajo['fecha_registro'][:10]}\n"
            )

        await update.callback_query.message.reply_text(
            mensaje,
            parse_mode="Markdown"
        )

    except Exception:
        await update.callback_query.message.reply_text(
            f"{EMOJI_ERR} No pude consultar el trabajo."
        )


# =========================================================
# 🆕 NUEVO
# =========================================================

async def nuevo(update, context):
    await update.message.reply_text(
        "🔧 La creación de trabajos se realizará desde "
        "el panel de administración."
    )


# =========================================================
# 📋 LISTA
# =========================================================

async def lista(update, context):
    await mis_trabajos(update, context)


# =========================================================
# 📤 ENVIAR
# =========================================================

async def enviar(update, context):
    await update.message.reply_text(
        "ℹ️ Esta función ya no está disponible."
    )


# =========================================================
# 📦 CATÁLOGO
# =========================================================

async def catalogo(update, context):
    await update.message.reply_text(
        "ℹ️ El catálogo ya no está disponible."
    )