#storage.py


listas_super = {}

def get_lista(user_id):
    return listas_super.setdefault(user_id, [])

def get_lista2(user_id):
    return listas_super.setdefault(user_id, [])
