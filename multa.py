
from datetime import date

from excepciones import DatosInvalidosError


class Multa:
    def __init__(self,identificador: str,usuario_id: str,
                 prestamo_id: str,valor: float,fecha_generacion: date = None,) -> None: # type: ignore
        
        if not identificador or not identificador.strip():
            raise DatosInvalidosError("El identificador no puede estar vacio.")
        if not usuario_id or not usuario_id.strip():
            raise DatosInvalidosError("El usuario_id no puede estar vacio.")
        if not prestamo_id or not prestamo_id.strip():
            raise DatosInvalidosError("El prestamo_id no puede estar vacio.")
        if valor < 0:
            raise DatosInvalidosError(
                "El valor de la multa no puede ser negativo."
            )

        self._identificador = identificador.strip()
        self._usuario_id = usuario_id.strip()
        self._prestamo_id = prestamo_id.strip()
        self._valor = float(valor)
        self._fecha_generacion = (
            fecha_generacion if fecha_generacion else date.today()
        )

    @property
    def identificador(self) -> str:
        return self._identificador

    @property
    def usuario_id(self) -> str:
        return self._usuario_id

    @property
    def prestamo_id(self) -> str:
        return self._prestamo_id

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def fecha_generacion(self) -> date:
        return self._fecha_generacion

    def to_dict(self) -> dict:
        return {
            "identificador": self._identificador,
            "usuario_id": self._usuario_id,
            "prestamo_id": self._prestamo_id,
            "valor": self._valor,
            "fecha_generacion": self._fecha_generacion.isoformat(),
        }

    def __str__(self) -> str:
        return (
            f"Multa {self._identificador} - usuario {self._usuario_id} "
            f"valor ${self._valor:,.0f}"
        )

