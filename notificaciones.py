"""Servicio de notificaciones del sistema de biblioteca.

Define una clase abstracta ServicioNotificaciones y dos implementaciones
concretas: NotificacionEmail y NotificacionSMS. Las notificaciones son
simuladas (imprimen en consola) para no requerir configuracion externa.
"""

from abc import ABC, abstractmethod

from usuario import Usuario


class ServicioNotificaciones(ABC):
    """Clase base abstracta para cualquier canal de notificaciones."""

    @abstractmethod
    def notificar(self, usuario: Usuario, mensaje: str) -> None:
        """Envia una notificacion al usuario por el canal correspondiente.

        Args:
            usuario: Usuario destinatario.
            mensaje: Contenido de la notificacion.
        """


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
    
    def notificar(self, usuario, mensaje):
        canal = usuario.canal_notificacion       # mira la preferencia
        servicio = self._servicios[canal]        # escoge el servicio
        servicio.notificar(usuario, mensaje)     # delega la notificacion