import psycopg2
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Variables globales para la conexión y el cursor de la base de datos
conn = None
cur = None

# --- Funciones Auxiliares para la Conexión a la Base de Datos ---
def connect_db():
    """Establece la conexión a la base de datos PostgreSQL."""
    global conn, cur
    load_dotenv() # Carga las variables de entorno desde el archivo .env
    datos_bd = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    try:
        conn = psycopg2.connect(**datos_bd)
        cur = conn.cursor()
        print("Conexión a la base de datos establecida.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        sys.exit(1) # Sale del script si la conexión falla

def close_db():
    """Cierra la conexión a la base de datos."""
    global conn, cur
    if cur:
        cur.close()
    if conn:
        conn.close()
        print("Conexión a la base de datos cerrada.")

# --- Operaciones CRUD para la tabla Reservas ---

def create_reserva():
    """Permite al usuario crear una nueva reserva."""
    print("\n--- Crear Nueva Reserva ---")
    try:
        # Pide al usuario los datos de la nueva reserva
        fecha_str = input("Ingrese Fecha y Hora (YYYY-MM-DD HH:MM:SS): ")
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S') # Convierte el string a objeto datetime
        id_cliente = int(input("Ingrese ID del Cliente: "))
        id_mesa = int(input("Ingrese ID de la Mesa: "))
        cantidad_personas = int(input("Ingrese Cantidad de Personas: "))
        # Se usa un ID de estado fijo (4) basado en los datos CSV de ejemplo.
        id_estado = 4 

        # Ejecuta la sentencia SQL INSERT
        cur.execute(
            "INSERT INTO Reservas (Id_cliente, Id_mesa, Id_estado, Fecha, Cantidad_personas) VALUES (%s, %s, %s, %s, %s)",
            (id_cliente, id_mesa, id_estado, fecha, cantidad_personas)
        )
        conn.commit() # Confirma los cambios en la base de datos
        print("Reserva creada exitosamente.")
    except ValueError:
        print("Error: Entrada inválida. Asegúrese de ingresar números para IDs y cantidad de personas, y el formato de fecha 'YYYY-MM-DD HH:MM:SS' para la fecha.")
    except Exception as e:
        print(f"Error al crear reserva: {e}")
        conn.rollback() # Revierte los cambios si hay un error

def read_reservas():
    """Muestra todas las reservas existentes en la base de datos."""
    print("\n--- Lista de Reservas ---")
    try:
        # Selecciona todas las reservas, ordenadas por fecha
        cur.execute("SELECT Id_reserva, Id_cliente, Id_mesa, Id_estado, Fecha, Cantidad_personas FROM Reservas ORDER BY Fecha DESC")
        reservas = cur.fetchall() # Obtiene todos los resultados

        if not reservas:
            print("No hay reservas registradas.")
            return

        # Imprime el encabezado de la tabla
        print("{:<10} {:<12} {:<10} {:<10} {:<20} {:<18}".format("ID Reserva", "ID Cliente", "ID Mesa", "ID Estado", "Fecha", "Personas"))
        print("-" * 80)
        # Imprime cada reserva
        for reserva in reservas:
            # Formatea la fecha para mostrarla claramente
            fecha_formateada = reserva[4].strftime('%Y-%m-%d %H:%M:%S') if isinstance(reserva[4], datetime) else str(reserva[4])
            print("{:<10} {:<12} {:<10} {:<10} {:<20} {:<18}".format(
                reserva[0], reserva[1], reserva[2], reserva[3],
                fecha_formateada,
                reserva[5]
            ))
    except Exception as e:
        print(f"Error al leer reservas: {e}")

def update_reserva():
    """Permite al usuario actualizar una reserva existente por su ID."""
    print("\n--- Actualizar Reserva ---")
    try:
        id_reserva = int(input("Ingrese ID de la Reserva a actualizar: "))
        # Busca la reserva para mostrar los valores actuales y verificar su existencia
        cur.execute("SELECT Id_cliente, Id_mesa, Cantidad_personas, Id_estado, Fecha FROM Reservas WHERE Id_reserva = %s", (id_reserva,))
        reserva = cur.fetchone()
        if not reserva:
            print("Reserva no encontrada.")
            return

        # Desempaqueta los valores actuales de la reserva
        current_id_cliente, current_id_mesa, current_cantidad_personas, current_id_estado, current_fecha = reserva
        # Formatea la fecha actual para mostrarla
        current_fecha_str = current_fecha.strftime('%Y-%m-%d %H:%M:%S') if isinstance(current_fecha, datetime) else str(current_fecha)

        print(f"Reserva actual - Cliente: {current_id_cliente}, Mesa: {current_id_mesa}, Personas: {current_cantidad_personas}, Estado: {current_id_estado}, Fecha: {current_fecha_str}")
        print("Deje en blanco los campos que no desea actualizar para mantener el valor actual.")

        # Pide nuevos valores, permitiendo dejar en blanco
        new_id_cliente = input(f"Nuevo ID del Cliente (actual: {current_id_cliente}): ")
        new_id_mesa = input(f"Nuevo ID de la Mesa (actual: {current_id_mesa}): ")
        new_cantidad_personas = input(f"Nueva Cantidad de Personas (actual: {current_cantidad_personas}): ")
        new_id_estado = input(f"Nuevo ID de Estado (actual: {current_id_estado}): ")
        new_fecha_str = input(f"Nueva Fecha y Hora (YYYY-MM-DD HH:MM:SS) (actual: {current_fecha_str}): ")

        updates = []
        params = []
        # Construye la sentencia UPDATE dinámicamente
        if new_id_cliente:
            updates.append("Id_cliente = %s")
            params.append(int(new_id_cliente))
        if new_id_mesa:
            updates.append("Id_mesa = %s")
            params.append(int(new_id_mesa))
        if new_cantidad_personas:
            updates.append("Cantidad_personas = %s")
            params.append(int(new_cantidad_personas))
        if new_id_estado:
            updates.append("Id_estado = %s")
            params.append(int(new_id_estado))
        if new_fecha_str:
            updates.append("Fecha = %s")
            params.append(datetime.strptime(new_fecha_str, '%Y-%m-%d %H:%M:%S'))

        if updates:
            params.append(id_reserva) # Agrega el ID de la reserva al final de los parámetros
            cur.execute(f"UPDATE Reservas SET {', '.join(updates)} WHERE Id_reserva = %s", tuple(params))
            conn.commit()
            print("Reserva actualizada exitosamente.")
        else:
            print("No se realizaron cambios.")
    except ValueError:
        print("Error: Entrada inválida. Asegúrese de ingresar números para IDs y cantidad de personas, y el formato de fecha correcto.")
    except Exception as e:
        print(f"Error al actualizar reserva: {e}")
        conn.rollback()

def delete_reserva():
    """Permite al usuario eliminar una reserva por su ID."""
    print("\n--- Eliminar Reserva ---")
    try:
        id_reserva = int(input("Ingrese ID de la Reserva a eliminar: "))
        # Ejecuta la sentencia DELETE y retorna el ID eliminado
        cur.execute("DELETE FROM Reservas WHERE Id_reserva = %s RETURNING Id_reserva", (id_reserva,))
        deleted_id = cur.fetchone()
        if deleted_id:
            conn.commit()
            print(f"Reserva con ID {deleted_id[0]} eliminada exitosamente.")
        else:
            print("Reserva no encontrada.")
    except ValueError:
        print("Error: Entrada inválida. Ingrese un número para el ID.")
    except Exception as e:
        print(f"Error al eliminar reserva: {e}")
        conn.rollback()

# --- Operaciones CRUD para la tabla Garzones ---

def create_garzon():
    """Permite al usuario crear un nuevo garzón."""
    print("\n--- Crear Nuevo Garzón ---")
    try:
        nombre_garzon = input("Ingrese Nombre del Garzón: ")
        telefono_garzon = input("Ingrese Teléfono del Garzón: ")
        correo_garzon = input("Ingrese Correo del Garzón: ")

        cur.execute(
            "INSERT INTO Garzones (Nombre_garzon, Telefono_garzon, Correo_garzon) VALUES (%s, %s, %s)",
            (nombre_garzon, telefono_garzon, correo_garzon)
        )
        conn.commit()
        print("Garzón creado exitosamente.")
    except Exception as e:
        print(f"Error al crear garzón: {e}")
        conn.rollback()

def read_garzones():
    """Muestra todos los garzones existentes en la base de datos."""
    print("\n--- Lista de Garzones ---")
    try:
        cur.execute("SELECT Id_garzon, Nombre_garzon, Telefono_garzon, Correo_garzon FROM Garzones ORDER BY Nombre_garzon ASC")
        garzones = cur.fetchall()
        if not garzones:
            print("No hay garzones registrados.")
            return

        print("{:<10} {:<25} {:<15} {:<25}".format("ID Garzón", "Nombre", "Teléfono", "Correo"))
        print("-" * 80)
        for garzon in garzones:
            print("{:<10} {:<25} {:<15} {:<25}".format(garzon[0], garzon[1], garzon[2], garzon[3]))
    except Exception as e:
        print(f"Error al leer garzones: {e}")

def update_garzon():
    """Permite al usuario actualizar un garzón existente por su ID."""
    print("\n--- Actualizar Garzón ---")
    try:
        id_garzon = int(input("Ingrese ID del Garzón a actualizar: "))
        cur.execute("SELECT Nombre_garzon, Telefono_garzon, Correo_garzon FROM Garzones WHERE Id_garzon = %s", (id_garzon,))
        garzon = cur.fetchone()
        if not garzon:
            print("Garzón no encontrado.")
            return

        current_nombre, current_telefono, current_correo = garzon

        print(f"Garzón actual - Nombre: {current_nombre}, Teléfono: {current_telefono}, Correo: {current_correo}")
        print("Deje en blanco los campos que no desea actualizar para mantener el valor actual.")

        new_nombre_garzon = input(f"Nuevo Nombre del Garzón (actual: {current_nombre}): ")
        new_telefono_garzon = input(f"Nuevo Teléfono del Garzón (actual: {current_telefono}): ")
        new_correo_garzon = input(f"Nuevo Correo del Garzón (actual: {current_correo}): ")

        updates = []
        params = []
        # Construye la sentencia UPDATE dinámicamente
        if new_nombre_garzon: # Si el usuario ingresó algo (no dejó en blanco)
            updates.append("Nombre_garzon = %s")
            params.append(new_nombre_garzon)
        if new_telefono_garzon:
            updates.append("Telefono_garzon = %s")
            params.append(new_telefono_garzon)
        if new_correo_garzon:
            updates.append("Correo_garzon = %s")
            params.append(new_correo_garzon)

        if updates:
            params.append(id_garzon)
            cur.execute(f"UPDATE Garzones SET {', '.join(updates)} WHERE Id_garzon = %s", tuple(params))
            conn.commit()
            print("Garzón actualizado exitosamente.")
        else:
            print("No se realizaron cambios.")
    except ValueError:
        print("Error: Entrada inválida. Ingrese un número para el ID.")
    except Exception as e:
        print(f"Error al actualizar garzón: {e}")
        conn.rollback()

def delete_garzon():
    """Permite al usuario eliminar un garzón por su ID."""
    print("\n--- Eliminar Garzón ---")
    try:
        id_garzon = int(input("Ingrese ID del Garzón a eliminar: "))
        cur.execute("DELETE FROM Garzones WHERE Id_garzon = %s RETURNING Id_garzon", (id_garzon,))
        deleted_id = cur.fetchone()
        if deleted_id:
            conn.commit()
            print(f"Garzón con ID {deleted_id[0]} eliminado exitosamente.")
        else:
            print("Garzón no encontrado.")
    except ValueError:
        print("Error: Entrada inválida. Ingrese un número para el ID.")
    except Exception as e:
        print(f"Error al eliminar garzón: {e}")
        conn.rollback()

# --- Función para Cargar Datos de Prueba ---

def generate_and_load_dummy_data():
    """Genera y carga datos de prueba para Reservas y Ventas."""
    print("\n--- Cargando Datos de Prueba Automáticamente (500 por mes en 3 años) ---")
    num_records_per_month = 500
    num_years = 3

    # Rangos de IDs para datos dummy
    client_ids = list(range(1, 501)) # Suponiendo 500 clientes
    table_ids = list(range(1, 21))    # Suponiendo 20 mesas
    # Id_estado: 4 (Completada) es un ejemplo. En un sistema real, esto se mapearía a una tabla.
    reservation_statuses = [4] 
    # Id_metodo: 1-5 (Efectivo, Crédito, Débito, Transferencia, Otro) son ejemplos.
    payment_methods = list(range(1, 6)) 
    
    # Intenta obtener los IDs de garzones existentes; si no hay, usa un rango dummy.
    waiter_ids = []
    try:
        cur.execute("SELECT Id_garzon FROM Garzones")
        waiter_ids = [row[0] for row in cur.fetchall()]
        if not waiter_ids:
            print("Advertencia: No hay garzones en la base de datos. Generando IDs de garzón dummy (1-10) para las ventas.")
            waiter_ids = list(range(1, 11)) 
    except Exception as e:
        print(f"Error al obtener IDs de garzones: {e}. Generando IDs de garzón dummy (1-10) para las ventas.")
        waiter_ids = list(range(1, 11))


    current_year = datetime.now().year
    # Inicia la generación de datos 3 años antes del año actual
    start_date_generation = datetime(current_year - num_years + 1, 1, 1, 0, 0, 0)

    total_reservas_inserted = 0
    total_sales_inserted = 0

    print(f"Generando datos desde el {start_date_generation.year} hasta el {current_year}...")

    try:
        for year_offset in range(num_years):
            for month in range(1, 13):
                # Calcula el inicio y fin del mes actual para la generación de fechas
                current_month_start = datetime(start_date_generation.year + year_offset, month, 1, 0, 0, 0)
                if month == 12:
                    current_month_end = datetime(start_date_generation.year + year_offset, month, 31, 23, 59, 59)
                else:
                    current_month_end = datetime(start_date_generation.year + year_offset, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

                # Generar Reservas
                for _ in range(num_records_per_month):
                    # Genera un día aleatorio dentro del mes
                    random_day = random.randint(1, (current_month_end - current_month_start).days + 1)
                    random_hour = random.randint(10, 22) # Horario de restaurante de 10 AM a 10 PM
                    random_minute = random.choice([0, 15, 30, 45])
                    random_second = random.randint(0, 59)
                    
                    random_date_time = datetime(
                        current_month_start.year,
                        current_month_start.month,
                        random_day,
                        random_hour,
                        random_minute,
                        random_second
                    )

                    # Asegura que la fecha generada esté dentro del mes y año objetivo
                    if random_date_time.month != month or random_date_time.year != (start_date_generation.year + year_offset):
                         continue

                    id_cliente = random.choice(client_ids)
                    id_mesa = random.choice(table_ids)
                    cantidad_personas = random.randint(1, 10)
                    id_estado = random.choice(reservation_statuses)

                    cur.execute(
                        "INSERT INTO Reservas (Id_cliente, Id_mesa, Id_estado, Fecha, Cantidad_personas) VALUES (%s, %s, %s, %s, %s)",
                        (id_cliente, id_mesa, id_estado, random_date_time, cantidad_personas)
                    )
                    total_reservas_inserted += 1

                # Generar Ventas
                for _ in range(num_records_per_month):
                    random_day = random.randint(1, (current_month_end - current_month_start).days + 1)
                    random_hour = random.randint(10, 23) # Horario de ventas un poco más amplio
                    random_minute = random.choice([0, 15, 30, 45])
                    random_second = random.randint(0, 59)

                    random_date_time = datetime(
                        current_month_start.year,
                        current_month_start.month,
                        random_day,
                        random_hour,
                        random_minute,
                        random_second
                    )
                    
                    # Asegura que la fecha generada esté dentro del mes y año objetivo
                    if random_date_time.month != month or random_date_time.year != (start_date_generation.year + year_offset):
                         continue

                    id_metodo = random.choice(payment_methods)
                    # Usa un ID de garzón válido; si no hay garzones, se usará el fallback 1
                    id_garzon = random.choice(waiter_ids) if waiter_ids else 1 
                    propina = random.randint(0, 5000) # Propina en pesos (ejemplo)
                    total_venta = round(random.uniform(10000, 100000), 2) # Total de venta (ejemplo)

                    cur.execute(
                        "INSERT INTO Ventas (Id_metodo, Id_garzon, Fecha, Propina, Total_venta) VALUES (%s, %s, %s, %s, %s)",
                        (id_metodo, id_garzon, random_date_time, propina, total_venta)
                    )
                    total_sales_inserted += 1

        conn.commit() # Confirma todas las inserciones al final
        print(f"Carga de datos de prueba completada.")
        print(f"Total de reservas insertadas: {total_reservas_inserted}")
        print(f"Total de ventas insertadas: {total_sales_inserted}")
    except Exception as e:
        print(f"Error al cargar datos de prueba: {e}")
        conn.rollback() # Revierte todo si hay un error

# --- Funciones de Menú ---

def display_menu():
    """Muestra el menú principal de la aplicación."""
    print("\n--- Menú de Gestión de Restaurantes ---")
    print("1. CRUD de Reservas")
    print("2. CRUD de Garzones")
    print("3. Cargar Datos de Prueba Automáticamente")
    print("4. Salir")

def display_crud_menu(entity_name):
    """Muestra el submenú CRUD para una entidad específica."""
    print(f"\n--- Menú CRUD para {entity_name} ---")
    print("1. Crear")
    print("2. Leer")
    print("3. Actualizar")
    print("4. Eliminar")
    print("5. Volver al Menú Principal")

def main_menu():
    """Función principal que maneja el flujo del menú."""
    connect_db() # Establece la conexión a la base de datos al inicio
    while True:
        display_menu() # Muestra el menú principal
        choice = input("Seleccione una opción: ")

        if choice == '1':
            # Submenú para Reservas
            while True:
                display_crud_menu("Reservas")
                crud_choice = input("Seleccione una operación CRUD para Reservas: ")
                if crud_choice == '1':
                    create_reserva()
                elif crud_choice == '2':
                    read_reservas()
                elif crud_choice == '3':
                    update_reserva()
                elif crud_choice == '4':
                    delete_reserva()
                elif crud_choice == '5':
                    break # Vuelve al menú principal
                else:
                    print("Opción inválida. Intente de nuevo.")
        elif choice == '2':
            # Submenú para Garzones
            while True:
                display_crud_menu("Garzones")
                crud_choice = input("Seleccione una operación CRUD para Garzones: ")
                if crud_choice == '1':
                    create_garzon()
                elif crud_choice == '2':
                    read_garzones()
                elif crud_choice == '3':
                    update_garzon()
                elif crud_choice == '4':
                    delete_garzon()
                elif crud_choice == '5':
                    break # Vuelve al menú principal
                else:
                    print("Opción inválida. Intente de nuevo.")
        elif choice == '3':
            # Carga automática de datos de prueba
            generate_and_load_dummy_data()
        elif choice == '4':
            print("Saliendo del sistema. ¡Hasta luego!")
            close_db() # Cierra la conexión a la base de datos antes de salir
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    # La ejecución del script comienza aquí
    main_menu()
