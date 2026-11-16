"""Interfaz gráfica con Tkinter. Una pestaña por pantalla."""
import tkinter as tk
from tkinter import ttk, messagebox
import productos
import inventario
import ventas
import devoluciones
import reportes
import caja


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Sistema de Supermercado")
        raiz.geometry("950x650")
        self.carrito = {}
        self.pestanas = ttk.Notebook(raiz)
        self.pestanas.pack(fill="both", expand=True)
        self.crear_pantalla_productos()
        self.crear_pantalla_inventario()
        self.crear_pantalla_venta()
        self.crear_pantalla_devoluciones()
        self.crear_pantalla_reportes()
        self.crear_pantalla_caja()
        self.refrescar_todo()

    # ---------------- utilidades ----------------
    def nueva_pestana(self, titulo):
        marco = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(marco, text=titulo)
        return marco

    def crear_campos(self, marco, etiquetas, fila_inicial=0):
        """Crea una etiqueta + caja de texto por cada nombre. Devuelve {nombre: Entry}."""
        campos = {}
        for i, texto in enumerate(etiquetas):
            ttk.Label(marco, text=texto).grid(row=fila_inicial + i, column=0, sticky="w", pady=2)
            entrada = ttk.Entry(marco, width=25)
            entrada.grid(row=fila_inicial + i, column=1, padx=5, pady=2)
            campos[texto] = entrada
        return campos

    def crear_tabla(self, marco, columnas, fila, ancho_columnas=4):
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=10)
        for columna in columnas:
            tabla.heading(columna, text=columna)
            tabla.column(columna, width=110)
        tabla.grid(row=fila, column=0, columnspan=ancho_columnas, sticky="nsew", pady=8)
        return tabla

    def leer(self, campos, nombre):
        return campos[nombre].get().strip()

    def limpiar(self, campos):
        for entrada in campos.values():
            entrada.delete(0, tk.END)

    def poner(self, campos, nombre, valor):
        campos[nombre].delete(0, tk.END)
        campos[nombre].insert(0, str(valor))

    def ejecutar(self, accion, mensaje_ok=None):
        """Ejecuta una acción mostrando los errores al usuario. Devuelve (ok, resultado)."""
        try:
            resultado = accion()
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return False, None
        else:
            if mensaje_ok:
                messagebox.showinfo("Listo", mensaje_ok)
            return True, resultado
        finally:
            self.refrescar_todo()

    def refrescar_todo(self):
        """Actualiza todas las tablas y textos de la aplicación."""
        self.llenar_tabla_productos()
        self.llenar_alertas()
        self.llenar_carrito()
        self.actualizar_estado_caja()

    # ---------------- pantalla 1: productos ----------------
    def crear_pantalla_productos(self):
        marco = self.nueva_pestana("Productos")
        etiquetas = ["Código", "Nombre", "Categoría", "Precio compra",
                     "Precio venta", "Stock inicial", "Stock mínimo"]
        self.campos_prod = self.crear_campos(marco, etiquetas)
        botones = ttk.Frame(marco)
        botones.grid(row=0, column=2, rowspan=7, padx=15)
        ttk.Button(botones, text="Registrar", command=self.registrar_producto).pack(fill="x", pady=2)
        ttk.Button(botones, text="Editar", command=self.editar_producto).pack(fill="x", pady=2)
        ttk.Button(botones, text="Desactivar", command=self.desactivar_producto).pack(fill="x", pady=2)
        ttk.Button(botones, text="Limpiar", command=lambda: self.limpiar(self.campos_prod)).pack(fill="x", pady=2)

        ttk.Label(marco, text="Buscar").grid(row=7, column=0, sticky="w")
        self.buscador = ttk.Entry(marco, width=25)
        self.buscador.grid(row=7, column=1)
        ttk.Button(marco, text="Buscar", command=self.llenar_tabla_productos).grid(row=7, column=2)
        columnas = ("Código", "Nombre", "Categoría", "Compra", "Venta", "Stock", "Mínimo", "Activo")
        self.tabla_prod = self.crear_tabla(marco, columnas, 8, 3)
        self.tabla_prod.bind("<<TreeviewSelect>>", self.seleccionar_producto)

    def llenar_tabla_productos(self):
        self.tabla_prod.delete(*self.tabla_prod.get_children())
        for p in productos.buscar_productos(self.buscador.get()):
            self.tabla_prod.insert("", tk.END, values=(
                p["codigo"], p["nombre"], p["categoria"], p["precio_compra"],
                p["precio_venta"], p["stock"], p["minimo"], "Sí" if p["activo"] else "No"))

    def seleccionar_producto(self, evento):
        seleccion = self.tabla_prod.selection()
        if not seleccion:
            return
        v = self.tabla_prod.item(seleccion[0])["values"]
        nombres = ["Código", "Nombre", "Categoría", "Precio compra",
                   "Precio venta", "Stock inicial", "Stock mínimo"]
        for nombre, valor in zip(nombres, v):
            self.poner(self.campos_prod, nombre, valor)

    def registrar_producto(self):
        c = self.campos_prod
        ok, _ = self.ejecutar(lambda: productos.registrar_producto(
            self.leer(c, "Código"), self.leer(c, "Nombre"), self.leer(c, "Categoría"),
            self.leer(c, "Precio compra"), self.leer(c, "Precio venta"),
            self.leer(c, "Stock inicial"), self.leer(c, "Stock mínimo")), "Producto registrado.")
        if ok:
            self.limpiar(c)

    def editar_producto(self):
        c = self.campos_prod
        self.ejecutar(lambda: productos.editar_producto(
            self.leer(c, "Código"), self.leer(c, "Nombre"), self.leer(c, "Categoría"),
            self.leer(c, "Precio compra"), self.leer(c, "Precio venta"),
            self.leer(c, "Stock mínimo")), "Producto actualizado.")

    def desactivar_producto(self):
        codigo = self.leer(self.campos_prod, "Código")
        if messagebox.askyesno("Confirmar", f"¿Desactivar el producto {codigo}?"):
            self.ejecutar(lambda: productos.desactivar_producto(codigo), "Producto desactivado.")

    # ---------------- pantalla 2: inventario ----------------
    def crear_pantalla_inventario(self):
        marco = self.nueva_pestana("Inventario")
        self.campos_inv = self.crear_campos(marco, ["Código", "Cantidad"])
        ttk.Button(marco, text="Registrar entrada", command=self.entrada_stock).grid(row=0, column=2, padx=5)
        ttk.Button(marco, text="Registrar salida", command=self.salida_stock).grid(row=1, column=2, padx=5)
        ttk.Label(marco, text="Alertas de stock bajo:").grid(row=2, column=0, sticky="w", pady=10)
        self.lista_alertas = tk.Listbox(marco, width=80, height=15)
        self.lista_alertas.grid(row=3, column=0, columnspan=3, sticky="nsew")

    def entrada_stock(self):
        c = self.campos_inv
        self.ejecutar(lambda: inventario.registrar_entrada(self.leer(c, "Código"), self.leer(c, "Cantidad")),
                      "Entrada registrada.")

    def salida_stock(self):
        c = self.campos_inv
        self.ejecutar(lambda: inventario.registrar_salida(self.leer(c, "Código"), self.leer(c, "Cantidad")),
                      "Salida registrada.")

    def llenar_alertas(self):
        self.lista_alertas.delete(0, tk.END)
        for p in inventario.productos_con_alerta():
            self.lista_alertas.insert(tk.END, f"{p['codigo']} - {p['nombre']}: stock {p['stock']} (mínimo {p['minimo']})")

    # ---------------- pantalla 3: venta ----------------
    def crear_pantalla_venta(self):
        marco = self.nueva_pestana("Venta")
        self.campos_venta = self.crear_campos(
            marco, ["Código", "Cantidad", "Descuento %", "Impuesto %", "Pago recibido"])
        self.poner(self.campos_venta, "Descuento %", 0)
        self.poner(self.campos_venta, "Impuesto %", ventas.IMPUESTO_POR_DEFECTO)
        botones = ttk.Frame(marco)
        botones.grid(row=0, column=2, rowspan=5, padx=15)
        ttk.Button(botones, text="Agregar", command=self.agregar_carrito).pack(fill="x", pady=2)
        ttk.Button(botones, text="Cambiar cantidad", command=self.cambiar_cantidad).pack(fill="x", pady=2)
        ttk.Button(botones, text="Quitar", command=self.quitar_carrito).pack(fill="x", pady=2)
        ttk.Button(botones, text="COBRAR", command=self.cobrar).pack(fill="x", pady=8)
        self.tabla_carrito = self.crear_tabla(
            marco, ("Código", "Nombre", "Cantidad", "Precio", "Subtotal"), 5, 3)
        self.etiqueta_total = ttk.Label(marco, text="Total: 0", font=("Arial", 14, "bold"))
        self.etiqueta_total.grid(row=6, column=0, columnspan=3, sticky="w")

    def agregar_carrito(self):
        c = self.campos_venta
        self.ejecutar(lambda: ventas.agregar_al_carrito(
            self.carrito, self.leer(c, "Código"), self.leer(c, "Cantidad")))

    def cambiar_cantidad(self):
        c = self.campos_venta
        self.ejecutar(lambda: ventas.modificar_cantidad(
            self.carrito, self.leer(c, "Código"), self.leer(c, "Cantidad")))

    def quitar_carrito(self):
        self.ejecutar(lambda: ventas.quitar_del_carrito(self.carrito, self.leer(self.campos_venta, "Código")))

    def llenar_carrito(self):
        self.tabla_carrito.delete(*self.tabla_carrito.get_children())
        filas, subtotal = ventas.detalle_carrito(self.carrito)
        for fila in filas:
            self.tabla_carrito.insert("", tk.END, values=fila)
        try:
            cobro = ventas.calcular_cobro(
                subtotal, self.leer(self.campos_venta, "Descuento %") or 0,
                self.leer(self.campos_venta, "Impuesto %") or 0)
        except ValueError:
            self.etiqueta_total.config(text=f"Subtotal: {subtotal} (revise descuento/impuesto)")
        else:
            self.etiqueta_total.config(text=f"Subtotal: {subtotal}  |  Total a pagar: {cobro['total']}")

    def cobrar(self):
        c = self.campos_venta
        ok, resultado = self.ejecutar(lambda: ventas.realizar_venta(
            self.carrito, self.leer(c, "Descuento %") or 0,
            self.leer(c, "Impuesto %") or 0, self.leer(c, "Pago recibido")))
        if ok:
            factura, cambio = resultado
            messagebox.showinfo("Venta realizada",
                                f"Factura Nº {factura['numero']}\nTotal: {factura['total']}\nCambio: {cambio}")
            self.carrito.clear()
            self.poner(c, "Pago recibido", "")
            self.refrescar_todo()

    # ---------------- pantalla 4: devoluciones ----------------
    def crear_pantalla_devoluciones(self):
        marco = self.nueva_pestana("Devoluciones")
        self.campos_dev = self.crear_campos(marco, ["Nº de factura", "Código del producto", "Cantidad"])
        ttk.Button(marco, text="Devolver", command=self.hacer_devolucion).grid(row=0, column=2, padx=10)

    def hacer_devolucion(self):
        c = self.campos_dev
        ok, reembolso = self.ejecutar(lambda: devoluciones.devolver(
            self.leer(c, "Nº de factura"), self.leer(c, "Código del producto"), self.leer(c, "Cantidad")))
        if ok:
            messagebox.showinfo("Devolución", f"Devolver al cliente: {reembolso}")

    # ---------------- pantalla 5: reportes ----------------
    def crear_pantalla_reportes(self):
        marco = self.nueva_pestana("Reportes")
        self.campos_rep = self.crear_campos(marco, ["Desde (AAAA-MM-DD)", "Hasta (AAAA-MM-DD)"])
        ttk.Button(marco, text="Consultar", command=self.consultar_reporte).grid(row=0, column=2, padx=10)
        self.texto_reporte = tk.Text(marco, width=80, height=20)
        self.texto_reporte.grid(row=2, column=0, columnspan=3, pady=10)

    def consultar_reporte(self):
        c = self.campos_rep
        ok, texto = self.ejecutar(lambda: reportes.generar_reporte(
            self.leer(c, "Desde (AAAA-MM-DD)"), self.leer(c, "Hasta (AAAA-MM-DD)")))
        if ok:
            self.texto_reporte.delete("1.0", tk.END)
            self.texto_reporte.insert(tk.END, texto)

    # ---------------- pantalla 6: caja ----------------
    def crear_pantalla_caja(self):
        marco = self.nueva_pestana("Caja")
        self.etiqueta_caja = ttk.Label(marco, text="", font=("Arial", 12, "bold"))
        self.etiqueta_caja.grid(row=0, column=0, columnspan=3, sticky="w", pady=5)
        self.campos_caja = self.crear_campos(
            marco, ["Saldo inicial", "Monto movimiento", "Descripción", "Efectivo declarado"], 1)
        ttk.Button(marco, text="Abrir caja", command=self.abrir_caja).grid(row=1, column=2, padx=10)
        ttk.Button(marco, text="Registrar ingreso", command=lambda: self.mover_caja("ingreso")).grid(row=2, column=2)
        ttk.Button(marco, text="Registrar retiro", command=lambda: self.mover_caja("retiro")).grid(row=3, column=2)
        ttk.Button(marco, text="Cerrar caja", command=self.cerrar_caja).grid(row=4, column=2, padx=10)

    def actualizar_estado_caja(self):
        sesion = caja.obtener_sesion_abierta()
        if sesion is None:
            self.etiqueta_caja.config(text="Caja CERRADA")
        else:
            self.etiqueta_caja.config(
                text=f"Caja ABIERTA - efectivo esperado: {caja.calcular_esperado(sesion)}")

    def abrir_caja(self):
        self.ejecutar(lambda: caja.abrir_caja(self.leer(self.campos_caja, "Saldo inicial") or 0),
                      "Caja abierta.")

    def mover_caja(self, tipo):
        c = self.campos_caja
        self.ejecutar(lambda: caja.registrar_movimiento(
            tipo, self.leer(c, "Monto movimiento"), self.leer(c, "Descripción")), "Movimiento registrado.")

    def cerrar_caja(self):
        ok, resultado = self.ejecutar(lambda: caja.cerrar_caja(self.leer(self.campos_caja, "Efectivo declarado")))
        if ok:
            esperado, declarado, diferencia = resultado
            messagebox.showinfo("Cierre de caja",
                                f"Esperado: {esperado}\nDeclarado: {declarado}\nDiferencia: {diferencia}")
