import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from tabulate import tabulate
from generar_datos_esquema import ejecutar_creacion_y_carga_datos 


conn = None
cursor = None

def base_datos_tiene_datos():
    global cursor, conn 

    if cursor is None or conn is None or conn.closed:
        print("Error: Conexión a la base de datos no inicializada o cerrada.")
        return False

    tablas_clave = ["Clientes", "Reservas", "Ventas"]
    for tabla in tablas_clave:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{tabla}"')
            if cursor.fetchone()[0] > 0:
                return True 
        except psycopg2.errors.UndefinedTable:
            print(f"Advertencia: La tabla '{tabla}' no existe. Asumiendo que no hay datos aún.")
            conn.rollback()
            continue
        except Exception as e:
            print(f"Error inesperado al verificar la tabla '{tabla}': {e}")
            conn.rollback()
            return False 

    return False

def _obtener_siguiente_id(tabla, columna_id):

    global cursor # Usamos el cursor global
    cursor.execute(f'SELECT COALESCE(MAX("{columna_id}"), 0) + 1 FROM "{tabla}"')
    return cursor.fetchone()[0]

# ---------------------- CRUD RESERVAS ----------------------

def crear_reserva():
    print("\n--- CREAR RESERVA ---")
    global cursor, conn

    try:
        es_nuevo = input("¿El cliente es nuevo? (s/n): ").strip().lower()
        id_cliente = None

        if es_nuevo == 's':
            print("Ingrese los datos del nuevo cliente:")
            nombre = input("Nombre y Apellido: ").strip()

            cursor.execute(
                '''SELECT "Id_cliente" FROM "Clientes" WHERE LOWER(TRIM("Nombre_cliente")) = LOWER(TRIM(%s))''',
                (nombre,)
            )
            cliente_existente = cursor.fetchone()

            if cliente_existente:
                id_cliente = cliente_existente[0]
                print(f"Cliente ya registrado. Usando ID existente: {id_cliente}")
            else:
                while True:
                    telefono = input("Teléfono (ej: +56912345678): ").strip()
                    if len(telefono) == 12 and telefono.startswith("+569") and telefono[1:].isdigit():
                        break
                    print("Teléfono inválido. Debe tener el formato +569XXXXXXXX.")

                correo = input("Correo (ej: ejemplo@correo.com): ").strip()

                id_cliente = _obtener_siguiente_id("Clientes", "Id_cliente")
                cursor.execute(
                    '''INSERT INTO "Clientes" ("Id_cliente", "Nombre_cliente", "Telefono_cliente", "Correo_cliente")
                       VALUES (%s, %s, %s, %s)''',
                    (id_cliente, nombre, telefono, correo)
                )
                conn.commit()
                print(f"Cliente creado con ID: {id_cliente}")
        else:
            id_cliente = input("ID del cliente existente: ").strip()

        fecha_str = input("Fecha de la reserva (formato YYYY-MM-DD): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            print("Formato de fecha inválido. Inténtalo de nuevo (YYYY-MM-DD).")
            return

        cursor.execute('''
            SELECT "N_Mesa" FROM "Mesas"
            WHERE "N_Mesa" NOT IN (
                SELECT "Id_mesa" FROM "Reservas"
                WHERE "Fecha" = %s AND "Id_estado" IN (1, 2)
            )
            ORDER BY "N_Mesa"
        ''', (fecha,))
        mesas_disponibles = cursor.fetchall()

        if not mesas_disponibles:
            print("No hay mesas disponibles para esa fecha.")
            return

        print("Mesas disponibles para esa fecha:", [m[0] for m in mesas_disponibles])
        id_mesa = input("Selecciona una mesa disponible (ej: 3): ").strip()

        print("\nOpciones de estado:")
        cursor.execute('SELECT * FROM "EstadoReserva"')
        for estado in cursor.fetchall():
            print(f'{estado[0]}: {estado[1]}')

        id_estado = input("ID del estado de la reserva (ej: 1 para 'Pendiente'): ").strip()
        cantidad_personas = input("Cantidad de personas (ej: 4): ").strip()

        id_reserva = _obtener_siguiente_id("Reservas", "Id_reserva")

        cursor.execute(
            '''INSERT INTO "Reservas"
               ("Id_reserva", "Id_cliente", "Id_mesa", "Id_estado", "Fecha", "Cantidad_personas")
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (id_reserva, id_cliente, id_mesa, id_estado, fecha, cantidad_personas)
        )
        conn.commit()
        print(f"Reserva creada exitosamente con ID: {id_reserva}")
    except Exception as e:
        print(f"Error al crear reserva: {e}")
        conn.rollback()

def leer_reservas():
    global cursor, conn
    try:
        cursor.execute('''
            SELECT R."Id_reserva", C."Nombre_cliente", R."Fecha", R."Cantidad_personas", R."Id_mesa", E."Estado"
            FROM "Reservas" R
            JOIN "Clientes" C ON R."Id_cliente" = C."Id_cliente"
            JOIN "EstadoReserva" E ON R."Id_estado" = E."Id_estado"
            ORDER BY R."Fecha" ASC
        ''')
        resultados = cursor.fetchall()
        headers = ["ID Reserva", "Cliente", "Fecha", "Personas", "Mesa", "Estado"]
        print("\nReservas registradas:\n")
        print(tabulate(resultados, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Error al leer reservas: {e}")
        conn.rollback()

def actualizar_reserva():
    global cursor, conn
    try:
        id_reserva = input("ID de la reserva a actualizar: ")
        nueva_fecha_str = input("Nueva fecha (YYYY-MM-DD): ")
        try:
            nueva_fecha = datetime.strptime(nueva_fecha_str, '%Y-%m-%d').date()
        except ValueError:
            print("Formato de fecha inválido. Inténtalo de nuevo (YYYY-MM-DD).")
            return

        print("\nOpciones de estado:")
        cursor.execute('SELECT * FROM "EstadoReserva"')
        for estado in cursor.fetchall():
            print(f'{estado[0]}: {estado[1]}')
        nuevo_estado = input("Nuevo ID de estado: ")

        cursor.execute(
            '''UPDATE "Reservas"
               SET "Fecha" = %s, "Id_estado" = %s
               WHERE "Id_reserva" = %s''',
            (nueva_fecha, nuevo_estado, id_reserva)
        )
        conn.commit()
        print("Reserva actualizada.")
    except Exception as e:
        print(f"Error al actualizar reserva: {e}")
        conn.rollback()

def eliminar_reserva():
    global cursor, conn
    try:
        id_reserva = input("ID de la reserva a eliminar: ")

        cursor.execute(
            '''DELETE FROM "Reservas"
               WHERE "Id_reserva" = %s''',
            (id_reserva,)
        )
        conn.commit()
        print("Reserva eliminada.")
    except Exception as e:
        print(f"Error al eliminar reserva: {e}")
        conn.rollback()

# ---------------------- CRUD VENTAS ----------------------

def crear_venta():
    print("\n--- CREAR VENTA ---")
    global cursor, conn

    try:
        print("\nMétodos de Pago:")
        cursor.execute('SELECT "Id_metodo", "Metodo" FROM "MetodoPago" ORDER BY "Id_metodo"')
        for mid, metodo in cursor.fetchall():
            print(f"{mid}: {metodo}")
        id_metodo = input("Selecciona el ID del método de pago: ").strip()

        print("\nGarzones disponibles:")
        cursor.execute('SELECT "Id_garzon", "Nombre_garzon" FROM "Garzones" ORDER BY "Id_garzon"')
        for gid, nombre in cursor.fetchall():
            print(f"{gid}: {nombre}")
        id_garzon = input("Selecciona el ID del garzón: ").strip()

        fecha_str = input("Fecha (YYYY-MM-DD): ").strip()
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            print("Formato de fecha inválido. Inténtalo de nuevo (YYYY-MM-DD).")
            return

        print("\nMesas disponibles para esa fecha:")
        cursor.execute('''
            SELECT "N_Mesa"
            FROM "Mesas"
            WHERE "N_Mesa" NOT IN (
                SELECT "Id_mesa"
                FROM "Reservas"
                WHERE "Fecha" = %s AND "Id_estado" IN (1, 2)
            )
            ORDER BY "N_Mesa"
        ''', (fecha,))
        mesas = cursor.fetchall()

        if not mesas:
            print("No hay mesas disponibles para esa fecha. No se puede crear la venta.")
            return

        for mesa in mesas:
            print(f"Mesa {mesa[0]}")
        id_mesa = input("Selecciona el número de mesa: ").strip()

        id_venta = _obtener_siguiente_id("Ventas", "Id_ventas")

        cursor.execute(
            '''INSERT INTO "Ventas" ("Id_ventas", "Id_metodo", "Id_garzon", "Fecha", "Propina", "Total_venta")
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (id_venta, id_metodo, id_garzon, fecha, 0, 0)
        )
        conn.commit()
        print(f"Venta creada con ID: {id_venta}")

        total_venta_acumulado = 0
        id_pedido_actual = _obtener_siguiente_id("Pedidos", "Id_pedido") -1

        while True:
            print("\nPlatillos disponibles:")
            cursor.execute('SELECT "Id_platillo", "Nombre" FROM "Platillos" ORDER BY "Id_platillo"')
            for id_plato, nombre in cursor.fetchall():
                print(f"{id_plato}: {nombre}")

            id_platillo = input("Selecciona ID del platillo: ").strip()
            cantidad = int(input("Cantidad del platillo: "))

            cursor.execute('SELECT "Precio" FROM "Platillos" WHERE "Id_platillo" = %s', (id_platillo,))
            resultado = cursor.fetchone()
            if not resultado:
                print("Platillo no encontrado. Intenta nuevamente.")
                continue

            precio_unitario = resultado[0]
            subtotal = precio_unitario * cantidad
            total_venta_acumulado += subtotal
            id_pedido_actual += 1

            cursor.execute(
                '''INSERT INTO "Pedidos" ("Id_pedido", "Id_venta", "Id_mesa", "Id_platillo", "Cantidad_platillo", "Subtotal")
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (id_pedido_actual, id_venta, id_mesa, id_platillo, cantidad, subtotal)
            )
            conn.commit()
            print(f"Pedido agregado: Subtotal = ${subtotal}")

            agregar_mas = input("¿Agregar otro pedido para esta mesa? (s/n): ").strip().lower()
            if agregar_mas != 's':
                break

        propina = round(total_venta_acumulado * 0.10)
        total_final = total_venta_acumulado + propina

        cursor.execute(
            '''UPDATE "Ventas"
               SET "Total_venta" = %s, "Propina" = %s
               WHERE "Id_ventas" = %s''',
            (total_final, propina, id_venta)
        )
        conn.commit()

        print(f"\nVenta actualizada con éxito.")
        print(f"Total Venta: ${total_venta_acumulado} + Propina 10% (${propina}) = ${total_final}")
    except Exception as e:
        print(f"Error al crear venta: {e}")
        conn.rollback() 

def leer_ventas():
    global cursor, conn 
    try:
        cursor.execute('''
            SELECT V."Id_ventas", V."Fecha", V."Total_venta", V."Propina", M."Metodo", G."Nombre_garzon"
            FROM "Ventas" V
            JOIN "MetodoPago" M ON V."Id_metodo" = M."Id_metodo"
            JOIN "Garzones" G ON V."Id_garzon" = G."Id_garzon"
            ORDER BY V."Fecha" ASC
        ''')
        resultados = cursor.fetchall()
        headers = ["ID Venta", "Fecha", "Total", "Propina", "Método de Pago", "Garzón"]
        print("\nVentas registradas:\n")
        print(tabulate(resultados, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Error al leer ventas: {e}")
        conn.rollback()

def actualizar_venta():
    global cursor, conn
    try:
        id_venta = input("ID de la venta a actualizar: ")
        

        cursor.execute('SELECT "Total_venta" FROM "Ventas" WHERE "Id_ventas" = %s', (id_venta,))
        venta_existente = cursor.fetchone()
        if not venta_existente:
            print(f"Error: No se encontró la venta con ID {id_venta}.")
            return

        try:
            nueva_propina = float(input("Nueva propina (ej: 1500.00): "))
            nuevo_total = float(input("Nuevo total (ej: 15000.00): "))
        except ValueError:
            print("Entrada inválida. Asegúrate de ingresar números para propina y total.")
            return

        cursor.execute(
            '''UPDATE "Ventas"
               SET "Propina" = %s, "Total_venta" = %s
               WHERE "Id_ventas" = %s''',
            (nueva_propina, nuevo_total, id_venta)
        )
        conn.commit()
        print("Venta actualizada.")
    except Exception as e:
        print(f"Error al actualizar venta: {e}")
        conn.rollback()

def eliminar_venta():
    global cursor, conn 
    try:
        id_venta = input("ID de la venta a eliminar: ")

        cursor.execute('''DELETE FROM "Pedidos" WHERE "Id_venta" = %s''', (id_venta,))
        cursor.execute('''DELETE FROM "Ventas" WHERE "Id_ventas" = %s''', (id_venta,))
        conn.commit()
        print(f"Venta con ID {id_venta} y sus pedidos asociados han sido eliminados.")
    except Exception as e:
        print(f"Error al eliminar venta: {e}")
        conn.rollback()

# ---------------------- MENÚ ----------------------

def menu():
    while True:
        # La verificación de datos debe estar aquí para que el menú se actualice dinámicamente
        tiene_datos = base_datos_tiene_datos()

        print("\n--- MENÚ CRUD ---")
        print("1. Crear Reserva")
        print("2. Leer Reservas")
        print("3. Actualizar Reserva")
        print("4. Eliminar Reserva")
        print("5. Crear Venta")
        print("6. Leer Ventas")
        print("7. Actualizar Venta")
        print("8. Eliminar Venta")
        # Mostrar mensaje más claro para la opción 9
        if not tiene_datos:
            print("9. Generar esquema y datos aleatorios (Requiere si no hay datos)")
        else:
            print("9. Generar esquema y datos aleatorios (Ya hay datos existentes)")
        print("10. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == '9':
            if not tiene_datos:
                print("\nGenerando esquema y datos aleatorios...")
                # Llama a la función de tu archivo separado, pasándole conn y cursor
                # La función en generar_datos_esquema.py debe retornar True/False para indicar éxito
                if ejecutar_creacion_y_carga_datos(cursor, conn):
                    print("Esquema y datos generados con éxito. El menú se actualizará para permitir operaciones CRUD.")
                else:
                    print("Fallo en la generación de esquema y datos. Revisa los errores anteriores.")
            else:
                print("Los datos ya existen. No puedes volver a generar el esquema (opción 9).")
        elif opcion == '10':
            print("Saliendo del programa.")
            break # Sale del bucle while para finalizar el programa
        elif not tiene_datos:
            # Si no hay datos y la opción no es '9' o '10', se restringe el acceso.
            print("Debes generar el esquema y los datos primero (opción 9) para usar esta opción.")
        else:
            # Si hay datos, permite el acceso a las funciones CRUD.
            if opcion == '1':
                crear_reserva()
            elif opcion == '2':
                leer_reservas()
            elif opcion == '3':
                actualizar_reserva()
            elif opcion == '4':
                eliminar_reserva()
            elif opcion == '5':
                crear_venta()
            elif opcion == '6':
                leer_ventas()
            elif opcion == '7':
                actualizar_venta()
            elif opcion == '8':
                eliminar_venta()
            else:
                print("Opción inválida. Por favor, selecciona una opción del 1 al 10.")

    print("Finalizando el menú...")

if __name__ == "__main__":
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Credenciales_ENV', '.env')
        load_dotenv(dotenv_path)
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor = conn.cursor()
        print("Conexión a la base de datos establecida.")

        menu()

    except Exception as e:
        print(f"Error crítico al iniciar la aplicación: {e}")
    finally:
        if cursor is not None:
            try:
                cursor.close()
                print("Cursor cerrado.")
            except Exception as e:
                print(f"Error al cerrar el cursor: {e}")
        if conn is not None:
            try:
                conn.close()
                print("Conexión a la base de datos cerrada.")
            except Exception as e:
                print(f"Error al cerrar la conexión: {e}")