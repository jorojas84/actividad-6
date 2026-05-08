from datetime import date, timedelta

from excepciones import (
    BibliotecaError,
    RecursoNoDisponibleError,
    UsuarioConMultasError,
)
from gestor_multas import GestorMultas
from gestor_prestamos import GestorPrestamos
from notificaciones import RouterNotificaciones, RecordatorioVenceHoy
from recursos import AudioLibro, Libro, Revista
from repository import RepositorioBiblioteca
from usuario import Docente, Estudiante


def separador(titulo: str) -> None:
    print("\n" + "-" * 60)
    print(f" {titulo}")
    print("-" * 60)


def main() -> None:
    # --- Inicializacion de gestores ---
    gestor_multas = GestorMultas()
    gestor_prestamos = GestorPrestamos(gestor_multas)
    router = RouterNotificaciones()
    recordatorios = RecordatorioVenceHoy(gestor_prestamos, router)
    repositorio = RepositorioBiblioteca()

    # --- Creacion de recursos ---
    separador("Registro de recursos")
    recursos = [
        Libro("L001", "Cien anos de soledad", "Gabriel Garcia Marquez", 432),
        Libro("L002", "El Quijote", "Miguel de Cervantes", 863),
        Revista("R001", "National Geographic", "Varios", 250),
        AudioLibro("A001", "1984", "George Orwell", 660),
    ]
    for r in recursos:
        print(f"  + {r}")

    # --- Registro de usuarios ---
    separador("Registro de usuarios")
    usuarios = [
        Estudiante(
            identificacion="1001",
            nombre="Ana Lopez",
            email="ana@uni.edu",
            codigo="EST001",
            carrera="Ingenieria de Sistemas",
            telefono="3001112233",
            canal_notificacion="email",
        ),
        Docente(
            identificacion="2001",
            nombre="Carlos Perez",
            email="carlos@uni.edu",
            telefono="3004445566",
            tipo="De Planta",
            canal_notificacion="sms",
        ),
    ]
    for u in usuarios:
        print(f"  + {u}  (factor extension: {u.factor_extension})")

    estudiante, docente = usuarios

    # --- Crear prestamos ---
    separador("Creacion de prestamos")
    # p1 se crea con fecha en el pasado para que llegue vencido y genere multa.
    p1 = gestor_prestamos.crear_prestamo(
        estudiante, recursos[0], date.today() - timedelta(days=20)
    )
    p2 = gestor_prestamos.crear_prestamo(docente, recursos[2])
    # p3 se crea con fecha en el pasado para que venza hoy y dispare el
    # RecordatorioVenceHoy (audiolibro: 30 dias * factor 1.0 = 30 dias).
    p3 = gestor_prestamos.crear_prestamo(
        estudiante, recursos[3], date.today() - timedelta(days=30)
    )
    print(f"  + {p1}")
    print(f"  + {p2}")
    print(f"  + {p3}")

    # --- Intento de prestamo de recurso ya prestado ---
    separador("Intento de prestamo invalido")
    try:
        gestor_prestamos.crear_prestamo(docente, recursos[0])
    except RecursoNoDisponibleError as error:
        print(f"  ! Error capturado: {error}")

    # --- Devolucion ---
    separador("Devolucion")
    dias_retraso, multa = gestor_prestamos.devolver_prestamo(p1.identificador)
    print(f"  Dias de retraso: {dias_retraso}")

    if multa:
        print(f"  + {multa}")

    # --- Intento de nuevo prestamo con multa pendiente ---
    separador("Intento de prestamo con multas pendientes")
    try:
        gestor_prestamos.crear_prestamo(estudiante, recursos[1])
    except UsuarioConMultasError as error:
        print(f"  ! Error capturado: {error}")

    # --- Recordatorios de vencimiento ---
    separador("Servicio de recordatorios")
    por_vencer = recordatorios.revisar_y_notificar()
    print(f"  Prestamos notificados: {len(por_vencer)}")

    # --- Persistencia ---
    separador("Persistencia en JSON")
    try:
        repositorio.guardar_recursos(recursos)
        repositorio.guardar_usuarios(usuarios)
        repositorio.guardar_prestamos(gestor_prestamos.prestamos_activos()
                                      + [p1])
        repositorio.guardar_multas(gestor_multas.multas_de_usuario(estudiante))
        repositorio.guardar_notificaciones(router.historial())
        print("  Datos guardados en la carpeta 'data/'.")
    except BibliotecaError as error:
        print(f"  ! Error de persistencia: {error}")

    separador("Fin de la demostracion")


if __name__ == "__main__":
    main()
