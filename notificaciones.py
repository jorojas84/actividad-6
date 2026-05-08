from abc import ABC, abstractmethod
from datetime import date
from typing import List

from gestor_prestamos import GestorPrestamos
from prestamo import Prestamo
from usuario import Usuario


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
    
    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        canal = usuario.canal_notificacion       # mira la preferencia
        servicio = self._servicios[canal]        # escoge el servicio
        servicio.notificar(usuario, mensaje)     # delega la notificacion

class ServicioRecordatorios:
    def __init__(
        self,gestor_prestamos: GestorPrestamos,
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