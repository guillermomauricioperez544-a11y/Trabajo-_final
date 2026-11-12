"""Control de caja: apertura, movimientos y cierre (S10)."""
from datetime import datetime
import datos
import productos

ARCHIVO = "caja.json"
ENTRADAS = ("venta", "ingreso")      # suman efectivo
SALIDAS = ("devolucion", "retiro")   # restan efectivo


def cargar_caja():
    return datos.cargar(ARCHIVO, {"sesiones": []})


def obtener_sesion_abierta():
    """Devuelve la sesión abierta o None si no hay."""
    for sesion in cargar_caja()["sesiones"]:
        if sesion["estado"] == "abierta":
            return sesion
    return None


def abrir_caja(saldo_inicial):
    """Abre una sesión de caja con un saldo inicial."""
    saldo = productos.validar_numero(saldo_inicial, "El saldo inicial")
    informacion = cargar_caja()
    if obtener_sesion_abierta() is not None:
        raise ValueError("Ya hay una caja abierta.")
    sesion = {
        "id": len(informacion["sesiones"]) + 1,
        "fecha_apertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "saldo_inicial": saldo, "movimientos": [],
        "estado": "abierta", "valor_esperado": None, "valor_declarado": None,
    }
    informacion["sesiones"].append(sesion)
    datos.guardar(ARCHIVO, informacion)
    return sesion


def registrar_movimiento(tipo, monto, descripcion=""):
    """Agrega un movimiento (venta, devolucion, ingreso o retiro) a la caja abierta."""
    if tipo not in ENTRADAS + SALIDAS:
        raise ValueError("Tipo de movimiento inválido.")
    monto = productos.validar_numero(monto, "El monto")
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    informacion = cargar_caja()
    for sesion in informacion["sesiones"]:
        if sesion["estado"] == "abierta":
            sesion["movimientos"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": tipo, "monto": monto, "descripcion": descripcion})
            datos.guardar(ARCHIVO, informacion)
            return
    raise ValueError("Debe abrir la caja primero.")


def calcular_esperado(sesion):
    """Efectivo que debería haber: saldo inicial + entradas - salidas."""
    total = sesion["saldo_inicial"]
    for mov in sesion["movimientos"]:
        if mov["tipo"] in ENTRADAS:
            total += mov["monto"]
        else:
            total -= mov["monto"]
    return round(total, 2)


def cerrar_caja(valor_declarado):
    """Cierra la caja y devuelve (esperado, declarado, diferencia)."""
    declarado = productos.validar_numero(valor_declarado, "El efectivo declarado")
    informacion = cargar_caja()
    for sesion in informacion["sesiones"]:
        if sesion["estado"] == "abierta":
            esperado = calcular_esperado(sesion)
            sesion["valor_esperado"] = esperado
            sesion["valor_declarado"] = declarado
            sesion["diferencia"] = round(declarado - esperado, 2)
            sesion["estado"] = "cerrada"
            sesion["fecha_cierre"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datos.guardar(ARCHIVO, informacion)
            return esperado, declarado, sesion["diferencia"]
    raise ValueError("No hay una caja abierta.")