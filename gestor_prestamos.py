from datetime import date
from typing import List

from excepciones import DatosInvalidosError
from prestamo import Prestamo
from recursos import Recurso
from usuario import Usuario


class GestorPrestamos:
    def __init__(self) -> None:
        self._prestamos: List[Prestamo] = []
        self._contador = 0

    def crear_prestamo(self,usuario: Usuario,
                       recurso: Recurso,) -> Prestamo:
        self._contador += 1
        identificador = f"P{self._contador:04d}"
        prestamo = Prestamo(identificador, usuario, recurso, date.today())
        self._prestamos.append(prestamo)
        return prestamo

    def devolver_prestamo(self, prestamo_id: str) -> int:
        prestamo = self._buscar_prestamo(prestamo_id)
        if prestamo is None:
            raise DatosInvalidosError(
                f"No existe el prestamo {prestamo_id}.")
        return prestamo.devolver()

    def prestamos_activos(self) -> List[Prestamo]:
        return [p for p in self._prestamos if not p.devuelto]

    def prestamos_de_usuario(self, usuario: Usuario) -> List[Prestamo]:
        return [
            p for p in self._prestamos
            if p.usuario.identificacion == usuario.identificacion
        ]

    def _buscar_prestamo(self, prestamo_id: str) -> Prestamo:
        for p in self._prestamos:
            if p.identificador == prestamo_id:
                return p
        return None # type: ignore