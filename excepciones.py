"""Excepciones para el sistema de biblioteca.

Define una serie de excepciones que permite atrapar errores
de forma clara segun el tipo de problema.
"""


class BibliotecaError(Exception):
    """Excepcion base para atrapar todos los errores del sistema de biblioteca.
    """


class DatosInvalidosError(BibliotecaError):
    """Se lanza cuando se intenta crear un objeto con datos invalidos."""


class RecursoNoDisponibleError(BibliotecaError):
    """Se lanza al intentar prestar un material que ya esta prestado."""


class UsuarioConMultasError(BibliotecaError):
    """Se lanza al intentar prestar a un usuario con multas pendientes."""


class PrestamoYaDevueltoError(BibliotecaError):
    """Se lanza al intentar devolver un prestamo que ya fue devuelto."""


class PersistenciaError(BibliotecaError):
    """Se lanza cuando hay un error al leer o escribir archivos JSON."""
