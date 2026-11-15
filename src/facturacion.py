"""Facturas e historial de ventas (S7)."""
from datetime import datetime
import datos

ARCHIVO = "ventas.json"


def cargar_ventas():
    """Devuelve la lista de facturas."""
    return datos.cargar(ARCHIVO, [])


def guardar_ventas(lista):
    datos.guardar(ARCHIVO, lista)


def siguiente_numero(lista):
    """Número consecutivo de la próxima factura."""
    if len(lista) == 0:
        return 1
    return lista[-1]["numero"] + 1


def crear_factura(carrito, productos, descuento, impuesto, subtotal, total):
    """Arma una factura y la guarda en el historial."""
    lista = cargar_ventas()
    detalle = []
    for codigo, cantidad in carrito.items():
        detalle.append({
            "codigo": codigo, "nombre": productos[codigo]["nombre"],
            "cantidad": cantidad, "precio": productos[codigo]["precio_venta"],
            "devuelto": 0})
    factura = {
        "numero": siguiente_numero(lista),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detalle": detalle, "subtotal": subtotal,
        "descuento": descuento, "impuestos": impuesto,
        "total": total, "estado": "emitida"}
    lista.append(factura)
    guardar_ventas(lista)
    return factura


def buscar_factura(lista, numero):
    """Busca una factura por número; devuelve None si no existe."""
    for factura in lista:
        if factura["numero"] == numero:
            return factura
    return None


def calcular_reembolso(factura, precio, cantidad):
    """Valor a devolver por 'cantidad' unidades, con descuento e impuesto de esa factura."""
    valor = cantidad * precio * (1 - factura["descuento"] / 100) * (1 + factura["impuestos"] / 100)
    return round(valor, 2)


def actualizar_estado(factura):
    """Cambia el estado según cuántas unidades se han devuelto."""
    vendidas = sum(linea["cantidad"] for linea in factura["detalle"])
    devueltas = sum(linea["devuelto"] for linea in factura["detalle"])
    if devueltas == 0:
        factura["estado"] = "emitida"
    elif devueltas < vendidas:
        factura["estado"] = "devolucion parcial"
    else:
        factura["estado"] = "devuelta"
