from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.api import get, post
from bot.config.config import EMOJI_OK, EMOJI_ERR

from bot.commands.commands_admin import (
    es_admin,
    nuevo_trabajo,
    pendientes,
    seleccionar_cliente,
    seleccionar_equipo,
    seleccionar_tipo,
    crear_trabajo
)

from bot.commands.commands_client import (
    mis_trabajos,
    detalle_trabajo
)

from bot.config.state import (
    clear_admin_form,
    clear_admin_action
)


async def catalogo_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    # =========================================================
    # ADMIN
    # =========================================================

    if data == "admin:nuevo":
        await nuevo_trabajo(update, context)
        return

    if data == "admin:pendientes":
        await pendientes(update, context)
        return

    if data.startswith("admin:cliente:"):

        valor = data.split(":", 2)[2]

        if valor == "nuevo":
            await query.message.reply_text(
                "👤 *Nuevo cliente*\n\n"
                "Esta parte la conectaremos después.",
                parse_mode="Markdown"
            )
            return

        await seleccionar_cliente(
            update,
            context,
            int(valor)
        )
        return

    if data.startswith("admin:equipo:"):

        valor = data.split(":", 2)[2]

        await seleccionar_equipo(
            update,
            context,
            valor
        )
        return

    if data.startswith("admin:tipo:"):

        tipo = data.split(":", 2)[2]

        await seleccionar_tipo(
            update,
            context,
            tipo
        )
        return

    # =========================================================
    # CREAR TRABAJO
    # =========================================================

    if data == "admin:trabajo:crear":

        if not es_admin(update):
            await query.message.reply_text(
                "⛔ No autorizado"
            )
            return

        resultado = await crear_trabajo(context)

        if not resultado or resultado.get("ok") is not True:
            await query.message.reply_text(
                f"{EMOJI_ERR} No se pudo crear el trabajo."
            )
            return

        trabajo = resultado["data"]

        await query.message.reply_text(
            f"{EMOJI_OK} *Trabajo creado*\n\n"
            f"📋 Folio: *{trabajo['folio']}*\n"
            f"📌 Estado: *{trabajo['estatus']}*",
            parse_mode="Markdown"
        )

        return

    # =========================================================
    # CANCELAR FORMULARIO
    # =========================================================

    if data == "admin:cancelar":

        clear_admin_form(context)
        clear_admin_action(context)

        await query.message.reply_text(
            "❌ Creación de trabajo cancelada."
        )

        return

    # =========================================================
    # DETALLE TRABAJO ADMIN
    # =========================================================

    if data.startswith("admin:trabajo:"):

        id_trabajo = data.split(":", 2)[2]

        try:
            resp = get(
                f"/bot/trabajo/{id_trabajo}"
            )

            if not resp or resp.get("ok") is not True:
                await query.message.reply_text(
                    f"{EMOJI_ERR} Trabajo no encontrado."
                )
                return

            trabajo = resp["data"]

            mensaje = (
                f"📋 *{trabajo['folio']}*\n\n"
                f"📌 Estado: *{trabajo['estatus']}*\n"
                f"🔧 Tipo: {trabajo['tipo_trabajo']}\n"
                f"👤 Cliente ID: {trabajo['id_cliente']}\n"
                f"💻 Equipo ID: "
                f"{trabajo['id_equipo'] or 'Sin equipo'}\n\n"
            )

            if trabajo.get("descripcion"):
                mensaje += (
                    f"📝 *Descripción*\n"
                    f"{trabajo['descripcion']}\n\n"
                )

            if trabajo.get("observaciones"):
                mensaje += (
                    f"📌 *Observaciones*\n"
                    f"{trabajo['observaciones']}\n\n"
                )

            if trabajo.get("requisitos"):
                mensaje += (
                    f"📋 *Requisitos*\n"
                    f"{trabajo['requisitos']}\n"
                )

            await query.message.reply_text(
                mensaje,
                parse_mode="Markdown"
            )

        except Exception:
            await query.message.reply_text(
                f"{EMOJI_ERR} Error consultando el trabajo."
            )

        return

    # =========================================================
    # CLIENTE → MIS TRABAJOS
    # =========================================================

    if data == "cliente:trabajos":

        await mis_trabajos(update, context)

        return

    # =========================================================
    # CLIENTE → DETALLE TRABAJO
    # =========================================================

    if data.startswith("cliente:trabajo:"):

        id_trabajo = data.split(":", 2)[2]

        await detalle_trabajo(
            update,
            context,
            int(id_trabajo)
        )

        return

    # =========================================================
    # CALLBACK DESCONOCIDO
    # =========================================================

    await query.message.reply_text(
        f"{EMOJI_ERR} Acción no reconocida."
    )