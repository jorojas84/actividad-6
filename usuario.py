from abc import ABC

from excepciones import DatosInvalidosError

FACTOR_EXTENSION_ESTUDIANTE = 1.0
TIPOS_DOCENTE_Y_FACTOR = {"De Planta": 2.0, "Catedratico": 0.5}

class Usuario(ABC):
    def __init__(self,identificacion: str, nombre: str, 
                 email: str, telefono: str, canal_notificacion: str) -> None:

        if not identificacion or not identificacion.strip():
            raise DatosInvalidosError("La identificacion no puede estar vacia.")
        if not nombre or not nombre.strip():
            raise DatosInvalidosError("El nombre no puede estar vacio.")
        if not email or "@" not in email:
            raise DatosInvalidosError("El email es invalido.")
        if not telefono or not telefono.strip():
            raise DatosInvalidosError("El telefono no puede estar vacio.")
        if canal_notificacion not in ("email", "sms"):
            raise DatosInvalidosError(
                "El canal debe ser 'email' o 'sms'.")

        self._identificacion = identificacion.strip()
        self._nombre = nombre.strip()
        self._email = email.strip()
        self._telefono = telefono.strip()
        self._canal_notificacion = canal_notificacion
        self._multa_pendiente = 0.0
        self._factor_extension = 0.0  # Se asigna en subclases

    def to_dict(self) -> dict:
        return {
            "tipo": self.__class__.__name__,
            "identificacion": self._identificacion,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "multas_pendientes": self._multa_pendiente,
        }

    def __str__(self) -> str:
        return f"[{self._identificacion}] {self._nombre} ({self._email})"

    @property
    def identificacion(self) -> str:
        return self._identificacion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def email(self) -> str:
        return self._email

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def multas_pendientes(self) -> float:
        return self._multa_pendiente
    
    @property
    def factor_extension(self) -> float:
        return self._factor_extension
    
    @multas_pendientes.setter
    def multas_pendientes(self, valor: float) -> None:
        if valor < 0:
            raise DatosInvalidosError("Las multas no pueden ser negativas.")
        self._multa_pendiente = valor

    @property
    def canal_notificacion(self) -> str:
        return self._canal_notificacion
    

class Estudiante(Usuario):
    def __init__(self,identificacion: str, nombre: str, 
                 email: str,telefono: str,codigo: str,carrera: str, canal_notificacion: str) -> None:
        super().__init__(identificacion, nombre, email, telefono, canal_notificacion)

        if not codigo or not codigo.strip():
            raise DatosInvalidosError("El codigo no puede estar vacio.")
        if not carrera or not carrera.strip():
            raise DatosInvalidosError("La carrera no puede estar vacia.")
        
        
        self._codigo = codigo.strip()
        self._carrera = carrera.strip()
        self._factor_extension = FACTOR_EXTENSION_ESTUDIANTE

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["codigo"] = self._codigo
        datos["carrera"] = self._carrera
        return datos


class Docente(Usuario):
    def __init__(self,identificacion: str,nombre: str,
                 email: str, telefono: str, tipo: str, canal_notificacion: str) -> None:
        super().__init__(identificacion, nombre, email, telefono, canal_notificacion)

        if tipo not in TIPOS_DOCENTE_Y_FACTOR:
            raise DatosInvalidosError(
                "El tipo de docente debe ser 'De Planta' o 'Catedratico'.")
        
        self._tipo = tipo
        self._factor_extension = TIPOS_DOCENTE_Y_FACTOR[tipo]

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["tipo"] = self._tipo
        return datos