"""Carrito, cobro y validaciones de venta (S4, S5 y S6)."""
import productos
import facturacion
import caja

IMPUESTO_POR_DEFECTO = 19  # porcentaje; cámbienlo según su país


def validar_porcentaje(valor, nombre):
    numero = productos.validar_numero(valor, nombre)
    if numero > 100:
        raise ValueError(f"{nombre} no puede ser mayor que 100.")
    return numero


def agregar_al_carrito(carrito, codigo, cantidad):
    """Agrega unidades de un producto al carrito (diccionario codigo -> cantidad)."""
    cantidad = productos.validar_numero(cantidad, "La cantidad", entero=True)
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    producto = productos.obtener_producto(codigo)
    if not producto["activo"]:
        raise ValueError("El producto está desactivado.")
    nueva = carrito.get(codigo, 0) + cantidad
    if nueva > producto["stock"]:
        raise ValueError(f"Solo hay {producto['stock']} unidades disponibles.")
    carrito[codigo] = nueva


def modificar_cantidad(carrito, codigo, cantidad):
    """Cambia la cantidad de un producto que ya está en el carrito."""
    cantidad = productos.validar_numero(cantidad, "La cantidad", entero=True)
    if codigo not in carrito:
        raise ValueError("Ese producto no está en el carrito.")
    if cantidad == 0:
        del carrito[codigo]
        return
    if cantidad > productos.obtener_producto(codigo)["stock"]:
        raise ValueError("No hay suficiente stock.")
    carrito[codigo] = cantidad


def quitar_del_carrito(carrito, codigo):
    if codigo not in carrito:
        raise ValueError("Ese producto no está en el carrito.")
    del carrito[codigo]


def detalle_carrito(carrito):
    """Devuelve (filas, subtotal). Cada fila: (codigo, nombre, cantidad, precio, subtotal)."""
    lista = productos.cargar_productos()
    filas = []
    subtotal = 0
    for codigo, cantidad in carrito.items():
        producto = lista[codigo]
        parcial = round(cantidad * producto["precio_venta"], 2)
        filas.append((codigo, producto["nombre"], cantidad, producto["precio_venta"], parcial))
        subtotal += parcial
    return filas, round(subtotal, 2)


def calcular_cobro(subtotal, descuento, impuesto):
    """Aplica descuento (%) e impuesto (%) y devuelve el desglose."""
    descuento = validar_porcentaje(descuento, "El descuento")
    impuesto = validar_porcentaje(impuesto, "El impuesto")
    valor_descuento = round(subtotal * descuento / 100, 2)
    base = subtotal - valor_descuento
    valor_impuesto = round(base * impuesto / 100, 2)
    return {"subtotal": subtotal, "descuento": valor_descuento,
            "impuesto": valor_impuesto, "total": round(base + valor_impuesto, 2)}


def calcular_cambio(total, pago):
    """Calcula el cambio; rechaza pagos insuficientes."""
    pago = productos.validar_numero(pago, "El pago")
    if pago < total:
        raise ValueError("El pago es insuficiente.")
    return round(pago - total, 2)


def realizar_venta(carrito, descuento, impuesto, pago):
    """Valida todo primero y solo después modifica stock, factura y caja."""
    if len(carrito) == 0:
        raise ValueError("El carrito está vacío.")
    if caja.obtener_sesion_abierta() is None:
        raise ValueError("Debe abrir la caja antes de vender.")
    lista = productos.cargar_productos()
    for codigo, cantidad in carrito.items():
        if codigo not in lista or cantidad > lista[codigo]["stock"]:
            raise ValueError(f"No hay stock suficiente de {codigo}.")

    _, subtotal = detalle_carrito(carrito)
    cobro = calcular_cobro(subtotal, descuento, impuesto)
    cambio = calcular_cambio(cobro["total"], pago)

    # Todo es válido: ahora sí se guardan los cambios
    factura = facturacion.crear_factura(
        carrito, lista, float(descuento), float(impuesto), subtotal, cobro["total"])
    for codigo, cantidad in carrito.items():
        lista[codigo]["stock"] -= cantidad
    productos.guardar_productos(lista)
    caja.registrar_movimiento("venta", cobro["total"], f"Factura {factura['numero']}")
    return factura, cambio
