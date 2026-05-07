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
    def __init__(self, codigo: str, titulo: str, autor: str) -> None:
        if not codigo or not codigo.strip():
            raise DatosInvalidosError("El codigo no puede estar vacio.")
        if not titulo or not titulo.strip():
            raise DatosInvalidosError("El titulo no puede estar vacio.")
        if not autor or not autor.strip():
            raise DatosInvalidosError("El autor no puede estar vacio.")

        self.codigo = codigo.strip()
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.disponible = True

    # De acuerdo a la variable de clase, cada tipo de recurso tiene una tarifa de multa diaria diferente
    @abstractmethod
    def calcular_multa(self, dias_retraso: int) -> float:
        """Calcula la multa segun los dias de retraso.

        Cada subclase implementa su propia tarifa diaria.

        Args:
            dias_retraso: Numero de dias de retraso (debe ser >= 0).

        Returns:
            Valor de la multa en pesos colombianos.
        """

    @abstractmethod
    def dias_prestamo_permitido(self) -> int:
        """Devuelve los dias maximos de prestamo segun el tipo."""

    def to_dict(self) -> dict:
        """Convertir diccionario para guardarlo en JSON."""
        return {
            "tipo": self.__class__.__name__,
            "codigo": self.codigo,
            "titulo": self.titulo,
            "autor": self.autor,
            "disponible": self.disponible,
        }

    def __str__(self) -> str:
        estado = "disponible" if self.disponible else "prestado"
        return f"[{self.codigo}] {self.titulo} - {self.autor} ({estado})"


class Libro(Recurso):
    def __init__(self,codigo: str, titulo: str, autor: str, paginas: int,) -> None:
        super().__init__(codigo, titulo, autor)
        
        if not isinstance(paginas, int) or paginas <= 0:
            raise DatosInvalidosError(
                "El numero de paginas debe ser un entero positivo."
            )
        
        self.paginas = paginas

    def calcular_multa(self, dias_retraso: int) -> float:
        if dias_retraso < 0:
            raise DatosInvalidosError(
                "Los dias de retraso no pueden ser negativos.")
        return float(dias_retraso * MULTA_DIARIA_LIBRO)

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_LIBRO

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["paginas"] = self.paginas
        return datos


class Revista(Recurso):
    def __init__(self,codigo: str, titulo: str, 
                 autor: str, numero_edicion: int,) -> None:
        super().__init__(codigo, titulo, autor)

        if not isinstance(numero_edicion, int) or numero_edicion <= 0:
            raise DatosInvalidosError(
                "El numero de edicion debe ser un entero positivo."
            )
        
        self.numero_edicion = numero_edicion

    def calcular_multa(self, dias_retraso: int) -> float:
        if dias_retraso < 0:
            raise DatosInvalidosError("Los dias de retraso no pueden ser negativos.")
        return float(dias_retraso * MULTA_DIARIA_REVISTA)

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_REVISTA

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["numero_edicion"] = self.numero_edicion
        return datos


class AudioLibro(Recurso):

    def __init__(self,codigo: str,titulo: str,
                 autor: str,duracion_minutos: int,) -> None:
        super().__init__(codigo, titulo, autor)

        if not isinstance(duracion_minutos, int) or duracion_minutos <= 0:
            raise DatosInvalidosError(
                "La duracion debe ser un entero positivo en minutos."
            )
        
        self.duracion_minutos = duracion_minutos

    def calcular_multa(self, dias_retraso: int) -> float:
        if dias_retraso < 0:
            raise DatosInvalidosError("Los dias de retraso no pueden ser negativos.")
        return float(dias_retraso * MULTA_DIARIA_AUDIOLIBRO)

    def dias_prestamo_permitido(self) -> int:
        return DIAS_PRESTAMO_AUDIOLIBRO

    def to_dict(self) -> dict:
        datos = super().to_dict()
        datos["duracion_minutos"] = self.duracion_minutos
        return datos
