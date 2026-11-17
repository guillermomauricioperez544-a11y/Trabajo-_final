# Sistema de Supermercado (Programación I)

Ejecutar:   python src/main.py
Pruebas:    python src/pruebas.py

## Contenido inicial de los JSON (carpeta data/)
- productos.json -> {}
- ventas.json    -> []
- caja.json      -> {"sesiones": []}

## División sugerida para 3 personas
- Persona 1: datos.py, productos.py, inventario.py, pruebas.py
- Persona 2: ventas.py, facturacion.py, devoluciones.py, caja.py
- Persona 3: reportes.py, interfaz.py, main.py

## Flujo de uso
1. Pestaña Caja -> abrir caja.  2. Productos -> registrar.  3. Venta -> agregar y cobrar.
