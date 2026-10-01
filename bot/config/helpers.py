# Archivo de herramientas donde podras guardar funciones que se usen en varios lugares del bot
#  por ejemplo para calcular el subtotal de una lista de productos

#def subtotal(lista):
#    return round(sum(item["precio"] for item in lista), 2)

def subtotal(lista):
    return round(sum(item["precio"] for item in lista), 2)