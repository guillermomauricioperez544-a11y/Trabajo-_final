"""Reportes de ventas (S9)."""
from datetime import datetime
import facturacion


def convertir_fecha(texto):
    """Convierte 'AAAA-MM-DD' en fecha; avisa si el formato es incorrecto."""
    try:
        return datetime.strptime(texto.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")


def ventas_por_fecha(desde, hasta):
    """Facturas entre dos fechas (incluidas)."""
    inicio = convertir_fecha(desde)
    fin = convertir_fecha(hasta)
    if inicio > fin:
        raise ValueError("La fecha inicial no puede ser mayor que la final.")
    resultado = []
    for factura in facturacion.cargar_ventas():
        if inicio <= convertir_fecha(factura["fecha"][:10]) <= fin:
            resultado.append(factura)
    return resultado


def calcular_ingresos(ventas):
    """Total vendido menos lo devuelto."""
    total = 0
    for factura in ventas:
        total += factura["total"]
        for linea in factura["detalle"]:
            total -= facturacion.calcular_reembolso(factura, linea["precio"], linea["devuelto"])
    return round(total, 2)


def contar_unidades(ventas):
    """Unidades vendidas (sin contar las devueltas)."""
    total = 0
    for factura in ventas:
        for linea in factura["detalle"]:
            total += linea["cantidad"] - linea["devuelto"]
    return total


def productos_mas_vendidos(ventas, cuantos=5):
    """Lista [(nombre, unidades)] ordenada de mayor a menor."""
    conteo = {}
    for factura in ventas:
        for linea in factura["detalle"]:
            neto = linea["cantidad"] - linea["devuelto"]
            conteo[linea["nombre"]] = conteo.get(linea["nombre"], 0) + neto
    ordenado = sorted(conteo.items(), key=lambda par: par[1], reverse=True)
    return ordenado[:cuantos]


def generar_reporte(desde, hasta):
    """Texto listo para mostrar en pantalla."""
    ventas = ventas_por_fecha(desde, hasta)
    lineas = [f"Facturas: {len(ventas)}",
              f"Ingresos netos: {calcular_ingresos(ventas)}",
              f"Unidades vendidas: {contar_unidades(ventas)}",
              "", "Más vendidos:"]
    for nombre, unidades in productos_mas_vendidos(ventas):
        lineas.append(f"  - {nombre}: {unidades}")
    return "\n".join(lineas)
