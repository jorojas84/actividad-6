from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List

from gestor_prestamos import GestorPrestamos
from prestamo import Prestamo
from usuario import Usuario


class Notificacion:
    def __init__(self, identificador: str, usuario_id: str, canal: str,
                 mensaje: str, fecha: datetime) -> None:
        self._identificador = identificador
        self._usuario_id = usuario_id
        self._canal = canal
        self._mensaje = mensaje
        self._fecha = fecha

    def to_dict(self) -> dict:
        return {
            "identificador": self._identificador,
            "usuario_id": self._usuario_id,
            "canal": self._canal,
            "mensaje": self._mensaje,
            "fecha": self._fecha.isoformat(),
        }


class ServicioNotificaciones(ABC):

    @abstractmethod
    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        pass

class NotificacionEmail(ServicioNotificaciones):
    """Servicio simulado de notificaciones por correo electronico."""

    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        print(f"[EMAIL] Para: {usuario.email} | {mensaje}")


class NotificacionSMS(ServicioNotificaciones):
    """Servicio simulado de notificaciones por mensaje de texto."""

    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        print(f"[SMS] Para: {usuario.telefono} | {mensaje}")

class RouterNotificaciones:
    def __init__(self):
        self._servicios = {
            "email": NotificacionEmail(),
            "sms": NotificacionSMS(),
        }
        self._historial: List[Notificacion] = []
        self._contador = 0

    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        canal = usuario.canal_notificacion       # mira la preferencia
        servicio = self._servicios[canal]        # escoge el servicio
        servicio.notificar(usuario, mensaje)     # delega la notificacion

        self._contador += 1
        self._historial.append(Notificacion(
            identificador=f"N{self._contador:04d}",
            usuario_id=usuario.identificacion,
            canal=canal,
            mensaje=mensaje,
            fecha=datetime.now(),
        ))

    def historial(self) -> List[Notificacion]:
        return list(self._historial)

class RecordatorioVenceHoy:
    def __init__(self,gestor_prestamos: GestorPrestamos,
                 router: RouterNotificaciones,) -> None:
        self._gestor_prestamos = gestor_prestamos
        self._router = router

    def revisar_y_notificar(self) -> List[Prestamo]:
        hoy = date.today()
        por_vencer: List[Prestamo] = []

        for prestamo in self._gestor_prestamos.prestamos_activos():
            if prestamo.fecha_devolucion_esperada == hoy:
                self._router.notificar(
                    prestamo.usuario,
                    f"Recordatorio: hoy vence la devolucion del recurso "
                    f"'{prestamo.recurso.titulo}'. Por favor devuelvalo hoy."
                )
                por_vencer.append(prestamo)

        return por_vencer