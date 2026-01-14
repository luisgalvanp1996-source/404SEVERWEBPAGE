# helpers.py

def subtotal(lista):
    return round(sum(item["precio"] for item in lista), 2)
