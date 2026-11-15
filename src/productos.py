"""Catálogo y mantenimiento de productos (S1 y S2)."""
import datos

ARCHIVO = "productos.json"


def cargar_productos():
    """Devuelve un diccionario {codigo: producto}."""
    return datos.cargar(ARCHIVO, {})


def guardar_productos(lista):
    datos.guardar(ARCHIVO, lista)


def validar_numero(valor, nombre, entero=False):
    """Convierte a número y verifica que no sea negativo."""
    try:
        numero = int(valor) if entero else float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser un número{' entero' if entero else ''}.")
    if numero < 0:
        raise ValueError(f"{nombre} no puede ser negativo.")
    return numero


def validar_texto(valor, nombre):
    """Verifica que un campo obligatorio no esté vacío."""
    valor = str(valor).strip()
    if valor == "":
        raise ValueError(f"{nombre} es obligatorio.")
    return valor


def registrar_producto(codigo, nombre, categoria, precio_compra, precio_venta, stock, minimo):
    """Crea un producto nuevo (rechaza códigos repetidos)."""
    codigo = validar_texto(codigo, "El código")
    nombre = validar_texto(nombre, "El nombre")
    categoria = validar_texto(categoria, "La categoría")
    precio_compra = validar_numero(precio_compra, "El precio de compra")
    precio_venta = validar_numero(precio_venta, "El precio de venta")
    stock = validar_numero(stock, "El stock", entero=True)
    minimo = validar_numero(minimo, "El stock mínimo", entero=True)

    lista = cargar_productos()
    if codigo in lista:
        raise ValueError(f"Ya existe un producto con el código {codigo}.")
    lista[codigo] = {
        "codigo": codigo, "nombre": nombre, "categoria": categoria,
        "precio_compra": precio_compra, "precio_venta": precio_venta,
        "stock": stock, "minimo": minimo, "activo": True,
    }
    guardar_productos(lista)
    return lista[codigo]


def obtener_producto(codigo):
    """Busca un producto por código; si no existe avisa con un error."""
    lista = cargar_productos()
    if codigo not in lista:
        raise ValueError(f"No existe el producto {codigo}.")
    return lista[codigo]


def editar_producto(codigo, nombre, categoria, precio_compra, precio_venta, minimo):
    """Edita los datos de un producto (el stock se cambia en inventario)."""
    lista = cargar_productos()
    if codigo not in lista:
        raise ValueError(f"No existe el producto {codigo}.")
    producto = lista[codigo]
    producto["nombre"] = validar_texto(nombre, "El nombre")
    producto["categoria"] = validar_texto(categoria, "La categoría")
    producto["precio_compra"] = validar_numero(precio_compra, "El precio de compra")
    producto["precio_venta"] = validar_numero(precio_venta, "El precio de venta")
    producto["minimo"] = validar_numero(minimo, "El stock mínimo", entero=True)
    guardar_productos(lista)
    return producto


def buscar_productos(texto=""):
    """Devuelve los productos cuyo código, nombre o categoría contengan el texto."""
    texto = texto.strip().lower()
    resultado = []
    for producto in cargar_productos().values():
        if texto in (producto["codigo"] + producto["nombre"] + producto["categoria"]).lower():
            resultado.append(producto)
    return resultado


def desactivar_producto(codigo):
    """Marca un producto como inactivo (no se borra, para conservar el historial)."""
    lista = cargar_productos()
    if codigo not in lista:
        raise ValueError(f"No existe el producto {codigo}.")
    lista[codigo]["activo"] = False
    guardar_productos(lista)
