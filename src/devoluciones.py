"""Devoluciones de productos vendidos (S8)."""
import productos
import facturacion
import caja


def devolver(numero, codigo, cantidad):
    """Devuelve unidades de una factura: reintegra stock, actualiza factura y caja."""
    numero = productos.validar_numero(numero, "El número de factura", entero=True)
    cantidad = productos.validar_numero(cantidad, "La cantidad", entero=True)
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    if caja.obtener_sesion_abierta() is None:
        raise ValueError("Debe abrir la caja para hacer devoluciones.")

    ventas = facturacion.cargar_ventas()
    factura = facturacion.buscar_factura(ventas, numero)
    if factura is None:
        raise ValueError("La factura no existe.")

    linea = buscar_linea(factura, codigo)
    if linea is None:
        raise ValueError("Ese producto no está en la factura.")
    if cantidad > linea["cantidad"] - linea["devuelto"]:
        raise ValueError("No se pueden devolver más unidades de las vendidas.")

    reembolso = facturacion.calcular_reembolso(factura, linea["precio"], cantidad)
    linea["devuelto"] += cantidad
    facturacion.actualizar_estado(factura)

    lista = productos.cargar_productos()
    if codigo in lista:
        lista[codigo]["stock"] += cantidad
        productos.guardar_productos(lista)
    facturacion.guardar_ventas(ventas)
    caja.registrar_movimiento("devolucion", reembolso, f"Factura {numero}")
    return reembolso


def buscar_linea(factura, codigo):
    """Busca el producto dentro del detalle de una factura."""
    for linea in factura["detalle"]:
        if linea["codigo"] == codigo:
            return linea
    return None
