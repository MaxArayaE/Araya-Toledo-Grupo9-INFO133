import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from tabulate import tabulate
from generar_datos_esquema import crear_esquema_y_datos

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# ---------------------- CRUD RESERVAS ----------------------

def crear_reserva():
    print("\n--- CREAR RESERVA ---")

    es_nuevo = input("¿El cliente es nuevo? (s/n): ").strip().lower()
    if es_nuevo == 's':
        print("Ingrese los datos del nuevo cliente:")
        nombre = input("Nombre y Apellido: ").strip()

        # Verificar si el cliente ya existe por nombre
        cursor.execute(
            '''SELECT "Id_cliente" FROM "Clientes" WHERE LOWER(TRIM("Nombre_cliente")) = LOWER(TRIM(%s))''',
            (nombre,)
        )
        cliente_existente = cursor.fetchone()

        if cliente_existente:
            id_cliente = cliente_existente[0]
            print(f"Cliente ya registrado. Usando ID existente: {id_cliente}")
        else:
            # Validar número de teléfono
            while True:
                telefono = input("Teléfono (ej: +56912345678): ").strip()
                if len(telefono) == 12 and telefono.startswith("+569") and telefono[1:].isdigit():
                    break
                print("Teléfono inválido. Debe tener el formato +569XXXXXXXX.")

            correo = input("Correo (ej: ejemplo@correo.com): ").strip()

            # Obtener el siguiente Id_cliente
            cursor.execute('SELECT COALESCE(MAX("Id_cliente"), 0) + 1 FROM "Clientes"')
            id_cliente = cursor.fetchone()[0]

            cursor.execute(
                '''INSERT INTO "Clientes" ("Id_cliente", "Nombre_cliente", "Telefono_cliente", "Correo_cliente")
                   VALUES (%s, %s, %s, %s)''',
                (id_cliente, nombre, telefono, correo)
            )
            conn.commit()
            print(f"Cliente creado con ID: {id_cliente}")
    else:
        id_cliente = input("ID del cliente existente: ").strip()

    fecha = input("Fecha de la reserva (formato YYYY-MM-DD): ").strip()

    # Obtener mesas disponibles para la fecha
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

    # Mostrar estados posibles
    print("\nOpciones de estado:")
    cursor.execute('SELECT * FROM "EstadoReserva"')
    for estado in cursor.fetchall():
        print(f'{estado[0]}: {estado[1]}')

    id_estado = input("ID del estado de la reserva (ej: 1 para 'Pendiente'): ").strip()
    cantidad_personas = input("Cantidad de personas (ej: 4): ").strip()

    # Obtener el siguiente Id_reserva
    cursor.execute('SELECT COALESCE(MAX("Id_reserva"), 0) + 1 FROM "Reservas"')
    id_reserva = cursor.fetchone()[0]

    cursor.execute(
        '''INSERT INTO "Reservas" 
           ("Id_reserva", "Id_cliente", "Id_mesa", "Id_estado", "Fecha", "Cantidad_personas")
           VALUES (%s, %s, %s, %s, %s, %s)''',
        (id_reserva, id_cliente, id_mesa, id_estado, fecha, cantidad_personas)
    )
    conn.commit()
    print(f"Reserva creada exitosamente con ID: {id_reserva}")


def leer_reservas():
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

def actualizar_reserva():
    id_reserva = input("ID de la reserva a actualizar: ")
    nueva_fecha = input("Nueva fecha (YYYY-MM-DD): ")
    nuevo_estado = input("Nuevo ID de estado: ")

    cursor.execute(
        '''UPDATE "Reservas"
           SET "Fecha" = %s, "Id_estado" = %s
           WHERE "Id_reserva" = %s''',
        (nueva_fecha, nuevo_estado, id_reserva)
    )
    conn.commit()
    print("Reserva actualizada.")

def eliminar_reserva():
    id_reserva = input("ID de la reserva a eliminar: ")

    cursor.execute(
        '''DELETE FROM "Reservas"
           WHERE "Id_reserva" = %s''',
        (id_reserva,)
    )
    conn.commit()
    print("Reserva eliminada.")

# ---------------------- CRUD VENTAS ----------------------

def crear_venta():
    print("\n--- CREAR VENTA ---")

    # Mostrar métodos de pago
    print("\nMétodos de Pago:")
    cursor.execute('SELECT "Id_metodo", "Metodo" FROM "MetodoPago" ORDER BY "Id_metodo"')
    for mid, metodo in cursor.fetchall():
        print(f"{mid}: {metodo}")
    id_metodo = input("Selecciona el ID del método de pago: ").strip()

    # Mostrar garzones
    print("\nGarzones disponibles:")
    cursor.execute('SELECT "Id_garzon", "Nombre_garzon" FROM "Garzones" ORDER BY "Id_garzon"')
    for gid, nombre in cursor.fetchall():
        print(f"{gid}: {nombre}")
    id_garzon = input("Selecciona el ID del garzón: ").strip()

    fecha = input("Fecha (YYYY-MM-DD): ").strip()

    # Mostrar mesas disponibles para esa fecha
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


    # Obtener nuevo ID de venta
    cursor.execute('SELECT COALESCE(MAX("Id_ventas"), 0) + 1 FROM "Ventas"')
    id_venta = cursor.fetchone()[0]

    # Insertar venta con total y propina en 0
    cursor.execute(
        '''INSERT INTO "Ventas" ("Id_ventas", "Id_metodo", "Id_garzon", "Fecha", "Propina", "Total_venta")
           VALUES (%s, %s, %s, %s, %s, %s)''',
        (id_venta, id_metodo, id_garzon, fecha, 0, 0)
    )
    conn.commit()
    print(f"Venta creada con ID: {id_venta}")

    total_venta = 0

    # Obtener último ID de pedido
    cursor.execute('SELECT COALESCE(MAX("Id_pedido"), 0) FROM "Pedidos"')
    id_pedido_actual = cursor.fetchone()[0]

    while True:
        # Mostrar platillos
        print("\nPlatillos disponibles:")
        cursor.execute('SELECT "Id_platillo", "Nombre" FROM "Platillos" ORDER BY "Id_platillo"')
        for id_plato, nombre in cursor.fetchall():
            print(f"{id_plato}: {nombre}")

        id_platillo = input("Selecciona ID del platillo: ").strip()
        cantidad = int(input("Cantidad del platillo: "))

        # Verificar existencia y precio del platillo
        cursor.execute('SELECT "Precio" FROM "Platillos" WHERE "Id_platillo" = %s', (id_platillo,))
        resultado = cursor.fetchone()
        if not resultado:
            print("Platillo no encontrado. Intenta nuevamente.")
            continue

        precio_unitario = resultado[0]
        subtotal = precio_unitario * cantidad
        total_venta += subtotal
        id_pedido_actual += 1

        # Insertar pedido
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

    # Calcular propina y total final
    propina = round(total_venta * 0.10)
    total_final = total_venta + propina

    # Actualizar la venta
    cursor.execute(
        '''UPDATE "Ventas"
           SET "Total_venta" = %s, "Propina" = %s
           WHERE "Id_ventas" = %s''',
        (total_final, propina, id_venta)
    )
    conn.commit()

    print(f"\nVenta actualizada con éxito.")
    print(f"Total Venta: ${total_venta} + Propina 10% (${propina}) = ${total_final}")

def leer_ventas():
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


def actualizar_venta():
    id_venta = input("ID de la venta a actualizar: ")
    nueva_propina = input("Nueva propina: ")
    nuevo_total = input("Nuevo total: ")

    cursor.execute(
        '''UPDATE "Ventas"
           SET "Propina" = %s, "Total_venta" = %s
           WHERE "Id_ventas" = %s''',
        (nueva_propina, nuevo_total, id_venta)
    )
    conn.commit()
    print("Venta actualizada.")

def eliminar_venta():
    id_venta = input("ID de la venta a eliminar: ")

    cursor.execute(
        '''DELETE FROM "Ventas"
           WHERE "Id_ventas" = %s''',
        (id_venta,)
    )
    conn.commit()
    print("Venta eliminada.")

# ---------------------- MENÚ ----------------------

def menu():
    contador = 0
    while True:
        print("\n--- MENÚ CRUD ---")
        print("1. Crear Reserva")
        print("2. Leer Reservas")
        print("3. Actualizar Reserva")
        print("4. Eliminar Reserva")
        print("5. Crear Venta")
        print("6. Leer Ventas")
        print("7. Actualizar Venta")
        print("8. Eliminar Venta")
        print("9. Generar esquema y datos aleatorios")
        print("10. Salir")


        opcion = input("Selecciona una opción: ")

        if opcion == '1' and contador == 1:
            crear_reserva()
        elif opcion == '2' and contador == 1:
            leer_reservas()
        elif opcion == '3' and contador == 1:
            actualizar_reserva()
        elif opcion == '4' and contador == 1:
            eliminar_reserva()
        elif opcion == '5' and contador == 1:
            crear_venta()
        elif opcion == '6' and contador == 1:
            leer_ventas()
        elif opcion == '7' and contador == 1:
            actualizar_venta()
        elif opcion == '8' and contador == 1:
            eliminar_venta()
        elif opcion == '9' and contador == 0:
            if contador == 0:
                crear_esquema_y_datos()
                contador +=1
            else:
                print("Ya se generaron los datos una vez")
        elif opcion == '10':
            break
        else:
            print("Opción inválida. O debe utilizar la opcion número 9 una sola vez")

    cursor.close()
    conn.close()
    print("Conexión cerrada. ¡Hasta luego!")


if __name__ == "__main__":
    menu()
