#storage.py

# Cada usuario tiene su lista
listas_super = {}

def get_lista(user_id):
    return listas_super.setdefault(user_id, [])
