"""Pruebas automáticas. Ejecutar con:  python src/pruebas.py
Cada prueba usa una carpeta temporal, así no se tocan los datos reales."""
import os
import shutil
import tempfile
import unittest

import datos
import productos
import inventario
import ventas
import facturacion
import devoluciones
import reportes
import caja


class PruebasSupermercado(unittest.TestCase):

    def setUp(self):
        self.carpeta_original = datos.CARPETA
        datos.CARPETA = tempfile.mkdtemp()
        productos.registrar_producto("P1", "Arroz", "Granos", 1000, 1500, 10, 3)
        productos.registrar_producto("P2", "Leche", "Lácteos", 800, 1200, 5, 2)
        caja.abrir_caja(10000)

    def tearDown(self):
        shutil.rmtree(datos.CARPETA)
        datos.CARPETA = self.carpeta_original

    # ----- pruebas exitosas -----
    def test_01_registrar_producto(self):
        """Un producto válido se guarda correctamente."""
        self.assertIn("P1", productos.cargar_productos())

    def test_02_buscar_producto(self):
        """La búsqueda encuentra por nombre."""
        self.assertEqual(len(productos.buscar_productos("arr")), 1)

    def test_03_entrada_inventario(self):
        """Una entrada suma al stock."""
        self.assertEqual(inventario.registrar_entrada("P1", 5), 15)

    def test_04_alerta_stock_minimo(self):
        """Se emite alerta cuando el stock llega al mínimo."""
        inventario.registrar_salida("P2", 3)
        self.assertEqual(len(inventario.productos_con_alerta()), 1)

    def test_05_venta_correcta(self):
        """Una venta crea factura, baja el stock y calcula el cambio."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 2)
        factura, cambio = ventas.realizar_venta(carrito, 0, 0, 5000)
        self.assertEqual(factura["total"], 3000)
        self.assertEqual(cambio, 2000)
        self.assertEqual(productos.obtener_producto("P1")["stock"], 8)

    def test_06_descuento_e_impuesto(self):
        """El cobro aplica descuento e impuesto."""
        cobro = ventas.calcular_cobro(1000, 10, 19)
        self.assertEqual(cobro["total"], 1071.0)

    def test_07_devolucion_parcial(self):
        """Una devolución parcial actualiza factura, inventario y caja."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 4)
        ventas.realizar_venta(carrito, 0, 0, 6000)
        devoluciones.devolver(1, "P1", 1)
        factura = facturacion.cargar_ventas()[0]
        self.assertEqual(factura["estado"], "devolucion parcial")
        self.assertEqual(productos.obtener_producto("P1")["stock"], 7)

    def test_08_persistencia(self):
        """Los datos siguen ahí al volver a leer los archivos."""
        productos.registrar_producto("P3", "Pan", "Panadería", 100, 200, 1, 1)
        self.assertIn("P3", datos.cargar("productos.json", {}))

    def test_09_cierre_con_diferencia(self):
        """El cierre muestra la diferencia exacta entre esperado y declarado."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 2)
        ventas.realizar_venta(carrito, 0, 0, 3000)
        esperado, declarado, diferencia = caja.cerrar_caja(12500)
        self.assertEqual(esperado, 13000)
        self.assertEqual(diferencia, -500)

    def test_10_reporte(self):
        """El reporte cuenta ingresos y unidades vendidas."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P2", 2)
        ventas.realizar_venta(carrito, 0, 0, 2400)
        lista = facturacion.cargar_ventas()
        self.assertEqual(reportes.calcular_ingresos(lista), 2400)
        self.assertEqual(reportes.contar_unidades(lista), 2)

    # ----- pruebas que deben fallar -----
    def test_11_producto_duplicado(self):
        """Un código repetido se rechaza sin alterar los datos."""
        with self.assertRaises(ValueError):
            productos.registrar_producto("P1", "Otro", "X", 1, 2, 1, 1)
        self.assertEqual(productos.obtener_producto("P1")["nombre"], "Arroz")

    def test_12_valor_negativo(self):
        """Los precios negativos se rechazan."""
        with self.assertRaises(ValueError):
            productos.registrar_producto("P9", "Malo", "X", -5, 2, 1, 1)

    def test_13_vender_mas_del_stock(self):
        """No se puede agregar más de lo disponible; no se crea factura."""
        with self.assertRaises(ValueError):
            ventas.agregar_al_carrito({}, "P2", 99)
        self.assertEqual(len(facturacion.cargar_ventas()), 0)

    def test_14_pago_insuficiente(self):
        """Un pago menor al total se rechaza y el stock no cambia."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 2)
        with self.assertRaises(ValueError):
            ventas.realizar_venta(carrito, 0, 0, 100)
        self.assertEqual(productos.obtener_producto("P1")["stock"], 10)

    def test_15_devolver_de_mas(self):
        """No se pueden devolver más unidades de las vendidas."""
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 1)
        ventas.realizar_venta(carrito, 0, 0, 1500)
        with self.assertRaises(ValueError):
            devoluciones.devolver(1, "P1", 2)

    def test_16_factura_inexistente(self):
        """Devolver de una factura que no existe da error."""
        with self.assertRaises(ValueError):
            devoluciones.devolver(99, "P1", 1)

    def test_17_vender_sin_caja(self):
        """Sin caja abierta no se puede vender."""
        caja.cerrar_caja(10000)
        carrito = {}
        ventas.agregar_al_carrito(carrito, "P1", 1)
        with self.assertRaises(ValueError):
            ventas.realizar_venta(carrito, 0, 0, 5000)

    def test_18_fecha_invalida(self):
        """Una fecha mal escrita se rechaza en reportes."""
        with self.assertRaises(ValueError):
            reportes.ventas_por_fecha("hoy", "2026-01-01")


if __name__ == "__main__":
    unittest.main(verbosity=2)