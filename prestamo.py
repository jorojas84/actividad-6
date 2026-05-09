from datetime import date, timedelta

from excepciones import (
    DatosInvalidosError,
    PrestamoYaDevueltoError,
    RecursoNoDisponibleError,
    UsuarioConMultasError,
)
from recursos import Recurso
from usuario import Usuario


class Prestamo:
    """Representa el prestamo de un recurso a un usuario.

    Calcula la fecha de devolucion esperada aplicando el factor de extension
    del usuario sobre los dias permitidos del recurso, y controla el estado
    de devolucion y los dias de retraso.
    """

    def __init__(self,identificador: str,usuario: Usuario,
        recurso: Recurso,fecha_prestamo: date) -> None:

        if not recurso.disponible:
            raise RecursoNoDisponibleError(
                f"El recurso {recurso.codigo} no esta disponible para prestamo."
            )
        if usuario.multas_pendientes > 0:
            raise UsuarioConMultasError(
                f"El usuario {usuario.identificacion} tiene multas pendientes."
            )

        self._identificador = identificador
        self._usuario = usuario
        self._recurso = recurso
        self._fecha_prestamo = fecha_prestamo if fecha_prestamo else date.today()

        # Calcula los dias de prestamo aplicando el factor del usuario.
        dias_efectivos = int(recurso.DIAS_PRESTAMO * usuario.factor_extension)
        self._fecha_devolucion_esperada = self._fecha_prestamo + timedelta(
            days=dias_efectivos
        )

        self._fecha_devolucion_real = None
        self._devuelto = False

        # Marca el recurso como prestado.
        recurso.disponible = False

    def dias_retraso(self, fecha_devolucion: date) -> int:
        fecha = fecha_devolucion if fecha_devolucion else date.today()
        retraso = (fecha - self._fecha_devolucion_esperada).days
        return max(0, retraso)

    def devolver(self) -> int:
        if self._devuelto:
            raise PrestamoYaDevueltoError(
                f"El prestamo {self._identificador} ya fue devuelto."
            )

        self._fecha_devolucion_real = date.today()
        retraso = self.dias_retraso(self._fecha_devolucion_real)

        self._recurso.disponible = True
        self._devuelto = True
        return retraso

    def to_dict(self) -> dict:
        return {
            "identificador": self._identificador,
            "usuario_id": self._usuario.identificacion,
            "recurso_codigo": self._recurso.codigo,
            "fecha_prestamo": self._fecha_prestamo.isoformat(),
            "fecha_devolucion_esperada": self._fecha_devolucion_esperada.isoformat(),
            "fecha_devolucion_real": (
                self._fecha_devolucion_real.isoformat()
                if self._fecha_devolucion_real
                else None
            ),
            "devuelto": self._devuelto,
        }

    def __str__(self) -> str:
        estado = "devuelto" if self._devuelto else "activo"
        return (
            f"Prestamo {self._identificador} - {self._recurso.titulo} "
            f"a {self._usuario.nombre} ({estado} - Fecha prestamo: {self._fecha_prestamo}, "
            f"Fecha devolucion esperada: {self._fecha_devolucion_esperada})"
        )
    
    @property
    def identificador(self) -> str:
        return self._identificador

    @property
    def usuario(self) -> Usuario:
        return self._usuario

    @property
    def recurso(self) -> Recurso:
        return self._recurso

    @property
    def fecha_prestamo(self) -> date:
        return self._fecha_prestamo

    @property
    def fecha_devolucion_esperada(self) -> date:
        return self._fecha_devolucion_esperada

    @fecha_devolucion_esperada.setter
    def fecha_devolucion_esperada(self, valor: date) -> None:
        if not isinstance(valor, date):
            raise DatosInvalidosError(
                "fecha_devolucion_esperada debe ser un objeto date."
            )
        self._fecha_devolucion_esperada = valor

    @property
    def fecha_devolucion_real(self) -> date:
        return self._fecha_devolucion_real # type: ignore

    @property
    def devuelto(self) -> bool:
        return self._devuelto