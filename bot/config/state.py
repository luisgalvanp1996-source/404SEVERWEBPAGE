def set_admin_action(context, action):
    context.user_data["admin_action"] = action


def get_admin_action(context):
    return context.user_data.get("admin_action")


def clear_admin_action(context):
    context.user_data.pop("admin_action", None)


# =========================================================
# FORMULARIO ADMIN
# =========================================================

def set_admin_form(context, form):
    context.user_data["admin_form"] = form


def get_admin_form(context):
    return context.user_data.setdefault(
        "admin_form",
        {}
    )


def update_admin_form(context, key, value):
    form = get_admin_form(context)
    form[key] = value


def clear_admin_form(context):
    context.user_data.pop("admin_form", None)