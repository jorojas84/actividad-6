from abc import ABC, abstractmethod

from excepciones import DatosInvalidosError


# Constantes para dias de prestamo y multas diarias por tipo de recurso
DIAS_PRESTAMO_LIBRO = 15
DIAS_PRESTAMO_REVISTA = 7
DIAS_PRESTAMO_AUDIOLIBRO = 30

# Multas diarias en pesos colombianos
MULTA_DIARIA_LIBRO = 1000      # COP por dia de retraso
MULTA_DIARIA_REVISTA = 500
MULTA_DIARIA_AUDIOLIBRO = 1500


class Recurso(ABC):
    """Clase base abstracta para los recursos de la biblioteca.

    Define los atributos comunes (codigo, titulo, autor, disponibilidad) y
    obliga a las subclases a implementar los dias de prestamo permitidos.
    """

    DIAS_PRESTAMO = 0  # Se define en subclases
    MULTA_DIARIA = 0   # Se define en subclases
    
    def __init__(self, codigo: str, titulo: str, autor: str) -> None:
        if not codigo or not codigo.strip():
            raise DatosInvalidosError("El codigo no puede estar vacio.")
        if not titulo or not titulo.strip():
            raise DatosInvalidosError("El titulo no puede estar vacio.")
        if not autor or not autor.strip():
            raise DatosInvalidosError("El autor no puede estar vacio.")

        self._codigo = codigo.strip()
        self._titulo = titulo.strip()
        self._autor = autor.strip()
        self._disponible = True

    @abstractmethod
    def dias_prestamo_permitido(self) -> int:
        """Devuelve los dias maximos de prestamo segun el tipo."""

    def to_dict(self) -> dict:
        """Convertir diccionario para guardarlo en JSON."""
        return {
            "tipo": self.__class__.__name__,
            "codigo": self._codigo,
            "titulo": self._titulo,
            "autor": self._autor,
            "disponible": self._disponible,
        }

    def __str__(self) -> str:
        estado = "disponible" if self._disponible else "prestado"
        return f"[{self._codigo}] {self._titulo} - {self._autor} ({estado})"
    
    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def autor(self) -> str:
        return self._autor

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise DatosInvalidosError("disponible debe ser True o False.")
        self._disponible = valor


class Libro(Recurso):
    """Recurso tipo libro, con un numero de paginas asociado."""

    DIAS_PRESTAMO = DIAS_PRESTAMO_LIBRO
    MULTA_DIARIA = MULTA_DIARIA_LIBRO

    def __init__(self,codigo: str, titulo: str, 
                 autor: str, paginas: int) -> None:
        super().__init__(codigo, titulo, autor)
        

        if not isinstance(paginas, int) or paginas <= 0:
            raise DatosInvalidosError(
                "El numero de paginas debe ser un entero positivo."
            )
        
        self._paginas = paginas
        

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_LIBRO

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["paginas"] = self._paginas
        return datos


class Revista(Recurso):
    """Recurso tipo revista, identificado por su numero de edicion."""

    DIAS_PRESTAMO = DIAS_PRESTAMO_REVISTA
    MULTA_DIARIA = MULTA_DIARIA_REVISTA

    def __init__(self,codigo: str, titulo: str, 
                 autor: str, numero_edicion: int,) -> None:
        super().__init__(codigo, titulo, autor)

        if not isinstance(numero_edicion, int) or numero_edicion <= 0:
            raise DatosInvalidosError(
                "El numero de edicion debe ser un entero positivo."
            )
        
        self._numero_edicion = numero_edicion

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_REVISTA

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["numero_edicion"] = self._numero_edicion
        return datos


class AudioLibro(Recurso):
    """Recurso tipo audiolibro, con duracion expresada en minutos."""

    DIAS_PRESTAMO = DIAS_PRESTAMO_AUDIOLIBRO
    MULTA_DIARIA = MULTA_DIARIA_AUDIOLIBRO

    def __init__(self,codigo: str,titulo: str,
                 autor: str,duracion_minutos: int,) -> None:
        super().__init__(codigo, titulo, autor)

        if not isinstance(duracion_minutos, int) or duracion_minutos <= 0:
            raise DatosInvalidosError(
                "La duracion debe ser un entero positivo en minutos."
            )
        
        self._duracion_minutos = duracion_minutos

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_AUDIOLIBRO

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["duracion_minutos"] = self._duracion_minutos
        return datos
