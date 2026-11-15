"""Entradas, salidas y alertas de stock (S3)."""
import productos


def registrar_entrada(codigo, cantidad):
    """Suma unidades al stock."""
    cantidad = productos.validar_numero(cantidad, "La cantidad", entero=True)
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    lista = productos.cargar_productos()
    if codigo not in lista:
        raise ValueError(f"No existe el producto {codigo}.")
    lista[codigo]["stock"] += cantidad
    productos.guardar_productos(lista)
    return lista[codigo]["stock"]


def registrar_salida(codigo, cantidad):
    """Resta unidades al stock (por ejemplo, mercancía dañada)."""
    cantidad = productos.validar_numero(cantidad, "La cantidad", entero=True)
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    lista = productos.cargar_productos()
    if codigo not in lista:
        raise ValueError(f"No existe el producto {codigo}.")
    if cantidad > lista[codigo]["stock"]:
        raise ValueError("No hay suficiente stock para esa salida.")
    lista[codigo]["stock"] -= cantidad
    productos.guardar_productos(lista)
    return lista[codigo]["stock"]


def productos_con_alerta():
    """Productos activos con stock menor o igual al mínimo."""
    alertas = []
    for producto in productos.cargar_productos().values():
        if producto["activo"] and producto["stock"] <= producto["minimo"]:
            alertas.append(producto)
    return alertas
