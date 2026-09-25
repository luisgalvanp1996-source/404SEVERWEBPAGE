#archivo con los comandos de administración del bot 

from bot.database.api import post, get
from bot.config.config import ADMIN_IDS, EMOJI_OK, EMOJI_ERR
from bot.config.state import (
    set_admin_action,
    get_admin_action,
    clear_admin_action,
    get_admin_form,
    update_admin_form,
    clear_admin_form
)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# =========================================================
# 🔐 SEGURIDAD
# =========================================================

def es_admin(update):
    return update.effective_user.id in ADMIN_IDS


# =========================================================
# 🔧 PANEL ADMIN
# =========================================================

async def panel_admin(update, context):
    if not es_admin(update):
        await update.message.reply_text(
            "⛔ No autorizado"
        )
        return

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
        ],
        [
            InlineKeyboardButton(
                "👥 Clientes",
                callback_data="admin:clientes"
            )
        ]
    ]

    await update.message.reply_text(
        "🔧 *Administración*\n\n"
        "Selecciona una opción:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# =========================================================
# 📋 TRABAJOS PENDIENTES
# =========================================================

async def pendientes(update, context):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    try:
        data = get("/bot/trabajos/pendientes")

        trabajos = data.get("data", [])

        if not trabajos:
            await update.callback_query.message.reply_text(
                "📭 No hay trabajos pendientes."
            )
            return

        keyboard = []

        for trabajo in trabajos:
            texto = (
                f"{trabajo['folio']} · "
                f"{trabajo['estatus']}"
            )

            keyboard.append([
                InlineKeyboardButton(
                    texto,
                    callback_data=(
                        f"admin:trabajo:"
                        f"{trabajo['id_trabajo']}"
                    )
                )
            ])

        await update.callback_query.message.reply_text(
            "📋 *Trabajos pendientes*\n\n"
            "Selecciona un trabajo:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    except Exception:
        await update.callback_query.message.reply_text(
            f"{EMOJI_ERR} No pude consultar los trabajos."
        )


# =========================================================
# ➕ NUEVO TRABAJO
# =========================================================

async def nuevo_trabajo(update, context):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    clear_admin_form(context)

    set_admin_action(
        context,
        "nuevo_trabajo_cliente"
    )

    try:
        data = get("/bot/clientes")

        clientes = data.get("data", [])

        keyboard = []

        for cliente in clientes:
            keyboard.append([
                InlineKeyboardButton(
                    cliente["nombre"],
                    callback_data=(
                        f"admin:cliente:"
                        f"{cliente['id_cliente']}"
                    )
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "➕ Crear cliente",
                callback_data="admin:cliente:nuevo"
            )
        ])

        await update.callback_query.message.reply_text(
            "👤 *Cliente*\n\n"
            "Selecciona el cliente:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    except Exception:
        await update.callback_query.message.reply_text(
            f"{EMOJI_ERR} No pude cargar los clientes."
        )


# =========================================================
# 👤 CLIENTE SELECCIONADO
# =========================================================

async def seleccionar_cliente(update, context, id_cliente):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    update_admin_form(
        context,
        "id_cliente",
        int(id_cliente)
    )

    try:
        data = get(
            f"/bot/clientes/{id_cliente}/equipos"
        )

        equipos = data.get("data", [])

        keyboard = []

        for equipo in equipos:
            nombre = equipo.get("nombre_equipo")

            if not nombre:
                partes = [
                    equipo.get("tipo"),
                    equipo.get("marca"),
                    equipo.get("modelo")
                ]

                nombre = " ".join(
                    str(x)
                    for x in partes
                    if x
                )

            keyboard.append([
                InlineKeyboardButton(
                    f"💻 {nombre}",
                    callback_data=(
                        f"admin:equipo:"
                        f"{equipo['id_equipo']}"
                    )
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "➕ Sin equipo / trabajo de software",
                callback_data="admin:equipo:none"
            )
        ])

        await update.callback_query.message.reply_text(
            "💻 *Equipo*\n\n"
            "Selecciona el equipo relacionado con el trabajo:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    except Exception:
        await update.callback_query.message.reply_text(
            f"{EMOJI_ERR} No pude cargar los equipos."
        )


# =========================================================
# 💻 EQUIPO SELECCIONADO
# =========================================================

async def seleccionar_equipo(update, context, id_equipo):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    if id_equipo == "none":
        update_admin_form(
            context,
            "id_equipo",
            None
        )
    else:
        update_admin_form(
            context,
            "id_equipo",
            int(id_equipo)
        )

    set_admin_action(
        context,
        "nuevo_trabajo_tipo"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🖥️ Mantenimiento",
                callback_data="admin:tipo:Mantenimiento"
            )
        ],
        [
            InlineKeyboardButton(
                "💻 Reparación",
                callback_data="admin:tipo:Reparación"
            )
        ],
        [
            InlineKeyboardButton(
                "⚙️ Instalación / Configuración",
                callback_data="admin:tipo:Instalación"
            )
        ],
        [
            InlineKeyboardButton(
                "🪟 Software / Windows",
                callback_data="admin:tipo:Software"
            )
        ],
        [
            InlineKeyboardButton(
                "🔧 Hardware",
                callback_data="admin:tipo:Hardware"
            )
        ],
        [
            InlineKeyboardButton(
                "📝 Otro",
                callback_data="admin:tipo:Otro"
            )
        ]
    ]

    await update.callback_query.message.reply_text(
        "🔧 *Tipo de trabajo*\n\n"
        "Selecciona el tipo:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# =========================================================
# 🔧 TIPO SELECCIONADO
# =========================================================

async def seleccionar_tipo(update, context, tipo):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    update_admin_form(
        context,
        "tipo_trabajo",
        tipo
    )

    set_admin_action(
        context,
        "nuevo_trabajo_descripcion"
    )

    await update.callback_query.message.reply_text(
        "📝 *Descripción*\n\n"
        "Escribe qué trabajo se realizará.\n\n"
        "Ejemplo:\n"
        "Instalar Windows 11 y dejar el equipo listo para usar.",
        parse_mode="Markdown"
    )


# =========================================================
# 💾 CREAR TRABAJO
# =========================================================

async def crear_trabajo(context):
    form = get_admin_form(context)

    try:
        data = post(
            "/bot/trabajo",
            {
                "id_cliente": form["id_cliente"],
                "id_equipo": form.get("id_equipo"),
                "tipo_trabajo": form["tipo_trabajo"],
                "descripcion": form.get("descripcion"),
                "observaciones": form.get("observaciones"),
                "requisitos": form.get("requisitos"),
                "id_usuario_tg": context.user_data.get(
                    "id_usuario_tg"
                )
            }
        )

        clear_admin_form(context)
        clear_admin_action(context)

        return data

    except Exception:
        return None


# =========================================================
# ✏️ TEXTO ADMIN
# =========================================================

async def texto_admin(update, context):
    if not es_admin(update):
        return

    action = get_admin_action(context)

    if not action:
        return

    texto = update.message.text.strip()

    # =====================================================
    # NUEVO CLIENTE - NOMBRE
    # =====================================================

    if action == "nuevo_cliente_nombre":

        update_admin_form(
            context,
            "cliente_nombre",
            texto
        )

        set_admin_action(
            context,
            "nuevo_cliente_telefono"
        )

        await update.message.reply_text(
            "📱 *Teléfono*\n\n"
            "Escribe el teléfono del cliente.\n\n"
            "Si no deseas registrarlo, escribe:\n"
            "`ninguno`",
            parse_mode="Markdown"
        )

        return

    # =====================================================
    # NUEVO CLIENTE - TELÉFONO
    # =====================================================

    if action == "nuevo_cliente_telefono":

        if texto.lower() == "ninguno":
            texto = None

        update_admin_form(
            context,
            "cliente_telefono",
            texto
        )

        set_admin_action(
            context,
            "nuevo_cliente_correo"
        )

        await update.message.reply_text(
            "📧 *Correo electrónico*\n\n"
            "Escribe el correo del cliente.\n\n"
            "Si no deseas registrarlo, escribe:\n"
            "`ninguno`",
            parse_mode="Markdown"
        )

        return

    # =====================================================
    # NUEVO CLIENTE - CORREO
    # =====================================================

    if action == "nuevo_cliente_correo":

        if texto.lower() == "ninguno":
            texto = None

        update_admin_form(
            context,
            "cliente_correo",
            texto
        )

        set_admin_action(
            context,
            "nuevo_cliente_observaciones"
        )

        await update.message.reply_text(
            "📌 *Observaciones del cliente*\n\n"
            "Escribe alguna observación importante sobre el cliente.\n\n"
            "Si no hay ninguna, escribe:\n"
            "`ninguna`",
            parse_mode="Markdown"
        )

        return

    # =====================================================
    # NUEVO CLIENTE - OBSERVACIONES
    # =====================================================

    if action == "nuevo_cliente_observaciones":

        if texto.lower() == "ninguna":
            texto = None

        update_admin_form(
            context,
            "cliente_observaciones",
            texto
        )

        form = get_admin_form(context)

        keyboard = [
            [
                InlineKeyboardButton(
                    "💾 Crear cliente",
                    callback_data="admin:cliente:crear"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancelar",
                    callback_data="admin:cancelar"
                )
            ]
        ]

        mensaje = (
            "👤 *Revisar cliente*\n\n"
            f"Nombre: {form.get('cliente_nombre')}\n"
            f"📱 Teléfono: "
            f"{form.get('cliente_telefono') or 'Ninguno'}\n"
            f"📧 Correo: "
            f"{form.get('cliente_correo') or 'Ninguno'}\n"
            f"📌 Observaciones: "
            f"{form.get('cliente_observaciones') or 'Ninguna'}\n"
        )

        await update.message.reply_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        set_admin_action(
            context,
            "nuevo_cliente_confirmar"
        )

        return

    # =====================================================
    # DESCRIPCIÓN
    # =====================================================

    if action == "nuevo_trabajo_descripcion":

        update_admin_form(
            context,
            "descripcion",
            texto
        )

        set_admin_action(
            context,
            "nuevo_trabajo_observaciones"
        )

        await update.message.reply_text(
            "📌 *Observaciones*\n\n"
            "Escribe las observaciones importantes.\n\n"
            "Si no hay ninguna, escribe:\n"
            "`ninguna`",
            parse_mode="Markdown"
        )

        return

    # =====================================================
    # OBSERVACIONES
    # =====================================================

    if action == "nuevo_trabajo_observaciones":

        if texto.lower() == "ninguna":
            texto = None

        update_admin_form(
            context,
            "observaciones",
            texto
        )

        set_admin_action(
            context,
            "nuevo_trabajo_requisitos"
        )

        await update.message.reply_text(
            "📋 *Requisitos*\n\n"
            "¿Hay algo que el cliente deba proporcionar?\n\n"
            "Ejemplo:\n"
            "Contraseña de Windows y licencia.\n\n"
            "Si no hay requisitos, escribe:\n"
            "`ninguno`",
            parse_mode="Markdown"
        )

        return

    # =====================================================
    # REQUISITOS
    # =====================================================

    if action == "nuevo_trabajo_requisitos":

        if texto.lower() == "ninguno":
            texto = None

        update_admin_form(
            context,
            "requisitos",
            texto
        )

        form = get_admin_form(context)

        keyboard = [
            [
                InlineKeyboardButton(
                    "💾 Crear trabajo",
                    callback_data="admin:trabajo:crear"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancelar",
                    callback_data="admin:cancelar"
                )
            ]
        ]

        mensaje = (
            "📋 *Revisar trabajo*\n\n"
            f"👤 Cliente ID: {form['id_cliente']}\n"
            f"💻 Equipo ID: "
            f"{form.get('id_equipo') or 'Sin equipo'}\n"
            f"🔧 Tipo: {form['tipo_trabajo']}\n\n"
            f"📝 {form.get('descripcion')}\n\n"
            f"📌 Observaciones: "
            f"{form.get('observaciones') or 'Ninguna'}\n\n"
            f"📋 Requisitos: "
            f"{form.get('requisitos') or 'Ninguno'}\n"
        )

        await update.message.reply_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        set_admin_action(
            context,
            "nuevo_trabajo_confirmar"
        )

        return

# =========================================================
# 👤 NUEVO CLIENTE
# =========================================================

async def nuevo_cliente(update, context):
    if not es_admin(update):
        await update.callback_query.answer(
            "⛔ No autorizado"
        )
        return

    # No limpiamos el formulario porque este cliente
    # se está creando desde un nuevo trabajo.

    set_admin_action(
        context,
        "nuevo_cliente_nombre"
    )

    await update.callback_query.message.reply_text(
        "👤 *Nuevo cliente*\n\n"
        "Escribe el nombre del cliente:",
        parse_mode="Markdown"
    )

# =========================================================
# 💾 GUARDAR CLIENTE
# =========================================================


async def guardar_cliente(context):
    form = get_admin_form(context)

    try:
        resultado = post(
            "/bot/cliente",
            {
                "nombre": form.get("cliente_nombre"),
                "telefono": form.get("cliente_telefono"),
                "correo": form.get("cliente_correo"),
                "observaciones": form.get("cliente_observaciones")
            }
        )

        if not resultado or resultado.get("ok") is not True:
            return None

        return resultado

    except Exception:
        return None