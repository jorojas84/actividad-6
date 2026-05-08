import json
import os
import shutil
import tempfile
import unittest
from datetime import date, timedelta

from excepciones import (
    DatosInvalidosError,
    PrestamoYaDevueltoError,
    RecursoNoDisponibleError,
    UsuarioConMultasError,
)
from gestor_multas import GestorMultas
from gestor_prestamos import GestorPrestamos
from multa import Multa
from notificaciones import RouterNotificaciones
from prestamo import Prestamo
from recursos import AudioLibro, Libro, Revista
from repository import RepositorioBiblioteca
from usuario import Docente, Estudiante


class TestRecursos(unittest.TestCase):
    def test_crear_libro_valido(self):
        libro = Libro("L001", "El Quijote", "Cervantes", 800)
        self.assertEqual(libro.codigo, "L001")
        self.assertEqual(libro.titulo, "El Quijote")
        self.assertTrue(libro.disponible)
        self.assertEqual(libro.DIAS_PRESTAMO, 15)

    def test_libro_paginas_invalidas(self):
        with self.assertRaises(DatosInvalidosError):
            Libro("L001", "Titulo", "Autor", 0)
        with self.assertRaises(DatosInvalidosError):
            Libro("L001", "Titulo", "Autor", -5)

    def test_codigo_vacio_lanza_error(self):
        with self.assertRaises(DatosInvalidosError):
            Libro("", "Titulo", "Autor", 100)
        with self.assertRaises(DatosInvalidosError):
            Libro("   ", "Titulo", "Autor", 100)

    def test_revista_valida(self):
        revista = Revista("R001", "Nat Geo", "Varios", 250)
        self.assertEqual(revista.DIAS_PRESTAMO, 7)

    def test_audiolibro_duracion_invalida(self):
        with self.assertRaises(DatosInvalidosError):
            AudioLibro("A001", "Titulo", "Autor", 0)

    def test_setter_disponible_valida_tipo(self):
        libro = Libro("L001", "T", "A", 100)
        with self.assertRaises(DatosInvalidosError):
            libro.disponible = "si"  # type: ignore

    def test_polimorfismo_to_dict(self):
        # to_dict cambia segun el tipo (polimorfismo).
        libro = Libro("L001", "T", "A", 100)
        revista = Revista("R001", "T", "A", 5)
        self.assertIn("paginas", libro.to_dict())
        self.assertIn("numero_edicion", revista.to_dict())
        self.assertEqual(libro.to_dict()["tipo"], "Libro")


class TestUsuarios(unittest.TestCase):
    def test_estudiante_valido(self):
        est = Estudiante(
            "1001", "Ana", "ana@u.edu", "EST1",
            "Sistemas", "3001112233", "email",
        )
        self.assertEqual(est.factor_extension, 1.0)

    def test_docente_factores(self):
        planta = Docente("2001", "Juan", "j@u.edu", "300", "De Planta", "email")
        catedra = Docente("2002", "Luis", "l@u.edu", "300", "Catedratico", "sms")
        self.assertEqual(planta.factor_extension, 2.0)
        self.assertEqual(catedra.factor_extension, 0.5)

    def test_email_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Estudiante("1", "A", "sinarroba", "C", "X", "300", "email")

    def test_canal_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Estudiante("1", "A", "a@a.com", "C", "X", "300", "whatsapp")

    def test_tipo_docente_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Docente("1", "A", "a@a.com", "300", "Ocasional", "email")

    def test_setter_multas_no_negativas(self):
        est = Estudiante("1", "A", "a@a.com", "C", "X", "300", "email")
        with self.assertRaises(DatosInvalidosError):
            est.multas_pendientes = -100


class TestPrestamo(unittest.TestCase):
    def setUp(self):
        self.libro = Libro("L001", "Titulo", "Autor", 100)
        self.estudiante = Estudiante(
            "1001", "Ana", "ana@u.edu", "EST1",
            "Sistemas", "300", "email",
        )

    def test_crear_prestamo_marca_no_disponible(self):
        Prestamo("P001", self.estudiante, self.libro, date.today())
        self.assertFalse(self.libro.disponible)

    def test_prestamo_de_recurso_no_disponible(self):
        Prestamo("P001", self.estudiante, self.libro, date.today())
        otro = Estudiante("2", "B", "b@a.com", "C", "X", "300", "email")
        with self.assertRaises(RecursoNoDisponibleError):
            Prestamo("P002", otro, self.libro, date.today())

    def test_prestamo_usuario_con_multas(self):
        self.estudiante.multas_pendientes = 5000
        with self.assertRaises(UsuarioConMultasError):
            Prestamo("P001", self.estudiante, self.libro, date.today())

    def test_devolver_libera_recurso(self):
        p = Prestamo("P001", self.estudiante, self.libro, date.today())
        p.devolver()
        self.assertTrue(self.libro.disponible)
        self.assertTrue(p.devuelto)

    def test_doble_devolucion_lanza_error(self):
        p = Prestamo("P001", self.estudiante, self.libro, date.today())
        p.devolver()
        with self.assertRaises(PrestamoYaDevueltoError):
            p.devolver()

    def test_dias_retraso(self):
        p = Prestamo("P001", self.estudiante, self.libro, date.today())
        p.fecha_devolucion_esperada = date.today() - timedelta(days=3)
        self.assertEqual(p.dias_retraso(date.today()), 3)

    def test_factor_extension_docente(self):
        # Docente de planta tiene factor 2.0 -> 30 dias para libro
        docente = Docente("2", "C", "c@a.com", "300", "De Planta", "email")
        p = Prestamo("P001", docente, self.libro, date.today())
        dias = (p.fecha_devolucion_esperada - p.fecha_prestamo).days
        self.assertEqual(dias, 30)

    def test_setter_fecha_devolucion_valida_tipo(self):
        p = Prestamo("P001", self.estudiante, self.libro, date.today())
        with self.assertRaises(DatosInvalidosError):
            p.fecha_devolucion_esperada = "2026-01-01"  # type: ignore


class TestGestorPrestamos(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorPrestamos()
        self.libro = Libro("L001", "T", "A", 100)
        self.estudiante = Estudiante(
            "1", "Ana", "a@a.com", "C", "X", "300", "email",
        )

    def test_crear_prestamo_genera_id(self):
        p = self.gestor.crear_prestamo(self.estudiante, self.libro)
        self.assertEqual(p.identificador, "P0001")

    def test_devolver_prestamo_inexistente(self):
        with self.assertRaises(DatosInvalidosError):
            self.gestor.devolver_prestamo("PXXX")

    def test_prestamos_activos(self):
        self.gestor.crear_prestamo(self.estudiante, self.libro)
        self.assertEqual(len(self.gestor.prestamos_activos()), 1)
        self.gestor.devolver_prestamo("P0001")
        self.assertEqual(len(self.gestor.prestamos_activos()), 0)


class TestGestorMultas(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorMultas()
        self.libro = Libro("L001", "T", "A", 100)
        self.estudiante = Estudiante(
            "1", "Ana", "a@a.com", "C", "X", "300", "email",
        )

    def test_calcular_valor(self):
        self.assertEqual(self.gestor.calcular_valor(self.libro, 5), 5000.0)

    def test_calcular_valor_negativo(self):
        with self.assertRaises(DatosInvalidosError):
            self.gestor.calcular_valor(self.libro, -1)

    def test_generar_multa_acumula_en_usuario(self):
        self.gestor.generar_multa(self.estudiante, self.libro, "P0001", 3)
        self.assertEqual(self.estudiante.multas_pendientes, 3000.0)

    def test_generar_multa_sin_retraso_retorna_none(self):
        multa = self.gestor.generar_multa(
            self.estudiante, self.libro, "P0001", 0,
        )
        self.assertIsNone(multa)


class TestCalculoFechasYMultas(unittest.TestCase):
    """Matriz de combinaciones tipo_usuario x tipo_recurso.

    Verifica que:
      - dias_efectivos = int(recurso.DIAS_PRESTAMO * usuario.factor_extension)
      - fecha_devolucion_esperada = fecha_prestamo + dias_efectivos
      - valor_multa = recurso.MULTA_DIARIA * dias_retraso (no depende del usuario)
    """

    def setUp(self):
        self.hoy = date(2026, 5, 8)
        self.estudiante = Estudiante(
            "1001", "Ana", "a@a.com", "EST", "Ing", "300", "email",
        )
        self.docente_planta = Docente(
            "2001", "Juan", "j@a.com", "300", "De Planta", "email",
        )
        self.docente_catedra = Docente(
            "2002", "Luis", "l@a.com", "300", "Catedratico", "sms",
        )

    def _hacer_libro(self, codigo="L"):
        return Libro(codigo, "T", "A", 100)

    def _hacer_revista(self, codigo="R"):
        return Revista(codigo, "T", "A", 1)

    def _hacer_audiolibro(self, codigo="AL"):
        return AudioLibro(codigo, "T", "A", 60)

    # --- Estudiante (factor 1.0) ---
    def test_fecha_estudiante_libro(self):
        p = Prestamo("P1", self.estudiante, self._hacer_libro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=15))

    def test_fecha_estudiante_revista(self):
        p = Prestamo("P1", self.estudiante, self._hacer_revista(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=7))

    def test_fecha_estudiante_audiolibro(self):
        p = Prestamo("P1", self.estudiante, self._hacer_audiolibro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=30))

    # --- Docente De Planta (factor 2.0) ---
    def test_fecha_docente_planta_libro(self):
        p = Prestamo("P1", self.docente_planta, self._hacer_libro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=30))

    def test_fecha_docente_planta_revista(self):
        p = Prestamo("P1", self.docente_planta, self._hacer_revista(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=14))

    def test_fecha_docente_planta_audiolibro(self):
        p = Prestamo("P1", self.docente_planta, self._hacer_audiolibro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=60))

    # --- Docente Catedratico (factor 0.5) ---
    def test_fecha_docente_catedra_libro(self):
        # 15 * 0.5 = 7.5 -> int() trunca a 7
        p = Prestamo("P1", self.docente_catedra, self._hacer_libro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=7))

    def test_fecha_docente_catedra_revista(self):
        # 7 * 0.5 = 3.5 -> int() trunca a 3
        p = Prestamo("P1", self.docente_catedra, self._hacer_revista(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=3))

    def test_fecha_docente_catedra_audiolibro(self):
        p = Prestamo("P1", self.docente_catedra, self._hacer_audiolibro(), self.hoy)
        self.assertEqual(p.fecha_devolucion_esperada, self.hoy + timedelta(days=15))

    # --- Multas por recurso (no dependen del usuario) ---
    def test_multa_libro_por_dia(self):
        gestor = GestorMultas()
        self.assertEqual(gestor.calcular_valor(self._hacer_libro(), 1), 1000.0)
        self.assertEqual(gestor.calcular_valor(self._hacer_libro(), 7), 7000.0)

    def test_multa_revista_por_dia(self):
        gestor = GestorMultas()
        self.assertEqual(gestor.calcular_valor(self._hacer_revista(), 1), 500.0)
        self.assertEqual(gestor.calcular_valor(self._hacer_revista(), 4), 2000.0)

    def test_multa_audiolibro_por_dia(self):
        gestor = GestorMultas()
        self.assertEqual(gestor.calcular_valor(self._hacer_audiolibro(), 1), 1500.0)
        self.assertEqual(gestor.calcular_valor(self._hacer_audiolibro(), 3), 4500.0)

    def test_multa_no_depende_del_tipo_de_usuario(self):
        # La multa diaria es del recurso, no del usuario.
        gestor = GestorMultas()
        libro = self._hacer_libro()
        valor_est = gestor.calcular_valor(libro, 5)
        valor_doc = gestor.calcular_valor(libro, 5)
        self.assertEqual(valor_est, valor_doc)
        self.assertEqual(valor_est, 5000.0)


class TestNotificaciones(unittest.TestCase):
    def test_router_envia_por_canal_correcto(self):
        router = RouterNotificaciones()
        est_email = Estudiante("1", "A", "a@a.com", "C", "X", "300", "email")
        est_sms = Estudiante("2", "B", "b@a.com", "C", "X", "300", "sms")
        # Solo verificamos que no lanza error (impresion por consola).
        router.notificar(est_email, "test")
        router.notificar(est_sms, "test")


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = RepositorioBiblioteca(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_guardar_recursos_crea_json_valido(self):
        recursos = [Libro("L001", "T", "A", 100)]
        self.repo.guardar_recursos(recursos)
        ruta = os.path.join(self.tmp, "recursos.json")
        self.assertTrue(os.path.exists(ruta))
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["codigo"], "L001")
        self.assertEqual(datos[0]["tipo"], "Libro")

    def test_guardar_usuarios(self):
        usuarios = [
            Estudiante("1", "A", "a@a.com", "C", "X", "300", "email"),
        ]
        self.repo.guardar_usuarios(usuarios)
        ruta = os.path.join(self.tmp, "usuarios.json")
        self.assertTrue(os.path.exists(ruta))


if __name__ == "__main__":
    unittest.main(verbosity=2)
