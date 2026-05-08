"""Persistencia de objetos a archivos JSON.

Guarda las colecciones del sistema (recursos, usuarios, prestamos
y multas) en archivos JSON. Aisla la logica de I/O del resto del
sistema (principio Single Responsibility).
"""

import json
import os
from typing import List

from excepciones import PersistenciaError
from multa import Multa
from prestamo import Prestamo
from recursos import Recurso
from usuario import Usuario


class RepositorioBiblioteca:
    """Repositorio que persiste la biblioteca en archivos JSON."""

    def __init__(self, carpeta_data: str = "data") -> None:
        os.makedirs(carpeta_data, exist_ok=True)
        self._ruta_recursos = os.path.join(carpeta_data, "recursos.json")
        self._ruta_usuarios = os.path.join(carpeta_data, "usuarios.json")
        self._ruta_prestamos = os.path.join(carpeta_data, "prestamos.json")
        self._ruta_multas = os.path.join(carpeta_data, "multas.json")

    def guardar_recursos(self, recursos: List[Recurso]) -> None:
        """Guarda una lista de recursos en formato JSON."""
        self._guardar(self._ruta_recursos, recursos, "recursos")

    def guardar_usuarios(self, usuarios: List[Usuario]) -> None:
        """Guarda una lista de usuarios en formato JSON."""
        self._guardar(self._ruta_usuarios, usuarios, "usuarios")

    def guardar_prestamos(self, prestamos: List[Prestamo]) -> None:
        """Guarda una lista de prestamos en formato JSON."""
        self._guardar(self._ruta_prestamos, prestamos, "prestamos")

    def guardar_multas(self, multas: List[Multa]) -> None:
        """Guarda una lista de multas en formato JSON."""
        self._guardar(self._ruta_multas, multas, "multas")

    @staticmethod
    def _guardar(ruta: str, objetos: list, nombre: str) -> None:
        """Serializa una lista de objetos y la escribe a un archivo JSON."""
        try:
            datos = [o.to_dict() for o in objetos]
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo guardar {nombre}: {error}"
            ) from error