"""Lectura y escritura de archivos JSON (persistencia)."""
import json
import os

# Carpeta "data" que está junto a la carpeta "src"
CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def ruta(nombre):
    """Devuelve la ruta completa de un archivo dentro de data/."""
    return os.path.join(CARPETA, nombre)


def cargar(nombre, defecto):
    """Lee un JSON. Si no existe o está vacío, devuelve 'defecto'."""
    try:
        with open(ruta(nombre), "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
        if contenido == "":
            return defecto
        resultado = json.loads(contenido)
    except FileNotFoundError:
        return defecto
    except json.JSONDecodeError:
        raise ValueError(f"El archivo {nombre} está dañado.")
    if not isinstance(resultado, type(defecto)):
        if not resultado:
            return defecto
        raise ValueError(f"El archivo {nombre} tiene un formato incorrecto.")
    return resultado


def guardar(nombre, informacion):
    """Guarda un JSON de forma segura: primero un archivo temporal y
    solo si todo salió bien se reemplaza el original."""
    os.makedirs(CARPETA, exist_ok=True)
    temporal = ruta(nombre) + ".tmp"
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(informacion, archivo, indent=4, ensure_ascii=False)
    except (OSError, TypeError) as error:
        raise ValueError(f"No se pudo guardar {nombre}: {error}")
    else:
        os.replace(temporal, ruta(nombre))
    finally:
        if os.path.exists(temporal):
            os.remove(temporal)
