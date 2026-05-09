from typing import List, Optional

from excepciones import DatosInvalidosError
from multa import Multa
from recursos import Recurso
from usuario import Usuario


class GestorMultas:
    """Calcula, genera y registra las multas asociadas a los usuarios
    cuando devuelven un recurso con retraso.
    """

    def __init__(self) -> None:
        self._multas: List[Multa] = []
        self._contador = 0

    def calcular_valor(self, recurso: Recurso, 
                       dias_retraso: int) -> float:
        if dias_retraso < 0:
            raise DatosInvalidosError(
                "Los dias de retraso no pueden ser negativos."
            )
        return float(recurso.MULTA_DIARIA * dias_retraso)

    def generar_multa(self,usuario: Usuario,recurso: Recurso,
        prestamo_id: str,dias_retraso: int,) -> Optional[Multa]:
        
        valor = self.calcular_valor(recurso, dias_retraso)
        if valor == 0:
            return None

        self._contador += 1
        identificador = f"M{self._contador:04d}"
        multa = Multa(
            identificador=identificador,
            usuario_id=usuario.identificacion,
            prestamo_id=prestamo_id,
            valor=valor,
        )
        self._multas.append(multa)
        usuario.multas_pendientes = usuario.multas_pendientes + valor
        return multa

    def multas_de_usuario(self, usuario: Usuario) -> List[Multa]:
        return [
            m for m in self._multas
            if m.usuario_id == usuario.identificacion
        ]