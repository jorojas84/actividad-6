from datetime import date
from typing import List, Optional, Tuple

from excepciones import DatosInvalidosError
from gestor_multas import GestorMultas
from multa import Multa
from prestamo import Prestamo
from recursos import Recurso
from usuario import Usuario


class GestorPrestamos:
    """Coordina el ciclo de vida de los prestamos: creacion, devolucion y
    consulta. Delega la generacion de multas en un GestorMultas.
    """

    def __init__(self, gestor_multas: GestorMultas) -> None:
        self._prestamos: List[Prestamo] = []
        self._contador = 0
        self._gestor_multas = gestor_multas

    def crear_prestamo(self,usuario: Usuario,
                       recurso: Recurso,
                       fecha_prestamo: date = None) -> Prestamo:  # type: ignore
        identificador = f"P{self._contador + 1:04d}"
        prestamo = Prestamo(identificador, usuario, recurso,
                            fecha_prestamo or date.today())
        self._contador += 1
        self._prestamos.append(prestamo)
        return prestamo

    def devolver_prestamo(
        self, prestamo_id: str
    ) -> Tuple[int, Optional[Multa]]:
        prestamo = self._buscar_prestamo(prestamo_id)
        if prestamo is None:
            raise DatosInvalidosError(
                f"No existe el prestamo {prestamo_id}.")
        dias_retraso = prestamo.devolver()
        multa = self._gestor_multas.generar_multa(
            usuario=prestamo.usuario,
            recurso=prestamo.recurso,
            prestamo_id=prestamo.identificador,
            dias_retraso=dias_retraso,
        )
        return dias_retraso, multa

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