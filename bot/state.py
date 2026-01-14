def set_admin_action(context, action):
    context.user_data["admin_action"] = action

def clear_admin_action(context):
    context.user_data.pop("admin_action", None)

def get_admin_action(context):
    return context.user_data.get("admin_action")
