import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random



NOMBRES_CLIENTES = ["Juan", "Ana", "Carlos", "María", "Pedro", "Lucía", "Jorge", "Camila"]
APELLIDOS = ["Pérez", "González", "Rodríguez", "López", "Soto", "Vega"]
GARZONES = [
    (1,"Juan Pérez","+56 9 11112222","juan.perez@email.com"),
    (2,"María Soto","+56 9 33334444","maria.soto@email.com"),
    (3,"Carlos Rojas","+56 9 55556666","carlos.rojas@email.com"),
    (4,"Ana Díaz","+56 9 77778888","ana.diaz@email.com"),
    (5,"Pedro Gómez","+56 9 99990000","pedro.gomez@email.com"),
    (6,"Carolina Ruiz","+56 9 12123434","carolina.ruiz@email.com"),
    (7,"Felipe Torres","+56 9 56567878","felipe.torres@email.com"),
    (8,"Sofía Morales","+56 9 90901212","sofia.morales@email.com"),
    (9,"Javier Castro","+56 9 34345656","javier.castro@email.com"),
    (10,"Laura Vidal","+56 9 78789090","laura.vidal@email.com")
]
UBICACIONES = [
    (1, "Primer piso"), (2, "Segundo piso"), (3, "Terraza")
]
MESAS = [
    (1, 4, 1), (2, 2, 1), (3, 6, 1), (4, 8, 1), (5, 4, 1), (6, 2, 1), (7, 10, 1), (8, 4, 1), (9, 6, 1), (10, 2, 1),
    (11, 4, 2), (12, 6, 2), (13, 8, 2), (14, 4, 2), (15, 2, 2), (16, 10, 2), (17, 4, 2), (18, 6, 2), (19, 2, 2),
    (20, 4, 3), (21, 6, 3), (22, 8, 3), (23, 4, 3), (24, 2, 3), (25, 10, 3)
]
ESTADOS_RESERVA = [
    (1, "Pendiente"), (2, "Confirmada"), (3, "Cancelada"), (4, "Completada")
]
METODOS_PAGO =[
    (1,"Efectivo"), (2,"Tarjeta de Crédito"), (3,"Tarjeta de Débito"), (4,"Transferencia")
]
PLATILLOS = [
    (1, "Pastel de Choclo", 10500, "Tradicional pastel de choclo con pino de carne y cubierto con una suave pasta de choclo."),
    (2, "Empanada de Pino", 3500, "Clásica empanada de pino con carne cebolla huevo duro y aceituna."),
    (3, "Cazuela de Vacuno", 9800, "Contundente cazuela con trozos de carne de vacuno papas zapallo choclo y arroz."),
    (4, "Completo Italiano", 4200, "Hot dog chileno con tomate palta y mayonesa."),
    (5, "Lomo a lo Pobre", 13500, "Jugoso lomo de vacuno acompañado de papas fritas cebolla caramelizada y dos huevos fritos."),
    (6, "Curanto en Olla", 15000, "Preparación sureña con mariscos carne papas y chapaleles cocinado en olla."),
    (7, "Carbonada", 8900, "Sopa espesa con carne papas zanahoria zapallo y trozos de fideos."),
    (8, "Charquicán", 9200, "Guiso con carne zapallo papa choclo arvejas y porotos verdes."),
    (9, "Porotos con Riendas", 8500, "Plato típico con porotos longaniza y tallarines."),
    (10, "Chupe de Jaiba", 11500, "Exquisito guiso cremoso de jaiba con queso derretido."),
    (11, "Paila Marina", 12000, "Variedad de mariscos frescos en un caldo aromático."),
    (12, "Congrio Frito", 14000, "Fresco congrio frito acompañado de ensalada chilena o papas cocidas."),
    (13, "Milanesa con Puré", 9900, "Tierna milanesa de vacuno apanada servida con cremoso puré de papas."),
    (14, "Arrollado Huaso", 7500, "Carne de cerdo enrollada con condimentos típica de la cocina chilena."),
    (15, "Sopaipillas con Pebre", 2500, "Deliciosas sopaipillas fritas perfectas para acompañar con pebre casero."),
    (16, "Ensalada Chilena", 4000, "Ensalada fresca de tomate y cebolla en pluma aderezada con aceite y cilantro."),
    (17, "Papas Fritas", 3000, "Porción de crujientes papas fritas."),
    (18, "Chorrillana", 16000, "Gran plato para compartir con papas fritas cebolla frita carne en tiras huevos y longaniza."),
    (19, "Asado de Tira", 18000, "Corte de carne tierno y jugoso cocinado a la parrilla."),
    (20, "Merluza Austral Frita", 12500, "Merluza austral fresca y frita ideal para un plato marino.")
]

# Modifica la función para que reciba 'cursor' y 'conn'
def ejecutar_creacion_y_carga_datos(cursor, conn): # <-- Ahora recibe cursor y conn
    print("\n--- Generando esquema y datos aleatorios ---")
    try:
        # Asegúrate de que Restaurante_transaccional.sql usa CREATE TABLE IF NOT EXISTS
        with open("BD_Transaccional/Restaurante_transaccional.sql", "r", encoding="utf-8") as f:
            cursor.execute(f.read())
        # conn.commit() # El commit se hace al final de la función si todo va bien

        for id_u, nombre in UBICACIONES:
            cursor.execute('''INSERT INTO "Ubicaciones" ("Id_ubicacion", "Ubicacion_local") VALUES (%s, %s)''', (id_u, nombre))

        for n_mesa, capacidad, ubicacion in MESAS:
            cursor.execute('''INSERT INTO "Mesas" ("N_Mesa", "Capacidad", "Ubicacion") VALUES (%s, %s, %s)''', (n_mesa, capacidad, ubicacion))

        for id_estado, nombre_estado in ESTADOS_RESERVA:
            cursor.execute('''INSERT INTO "EstadoReserva" ("Id_estado", "Estado") VALUES (%s, %s)''', (id_estado, nombre_estado))

        for id_metodo, metodo in METODOS_PAGO:
            cursor.execute('''INSERT INTO "MetodoPago" ("Id_metodo", "Metodo") VALUES (%s, %s)''', (id_metodo, metodo))

        for Id_garzon, Nombre_garzon, Telefono_garzon, Correo_garzon in GARZONES:
            cursor.execute('''INSERT INTO "Garzones" ("Id_garzon", "Nombre_garzon", "Telefono_garzon", "Correo_garzon")
                             VALUES (%s, %s, %s, %s)''', (Id_garzon, Nombre_garzon, Telefono_garzon, Correo_garzon))

        for id_p, nombre, precio, descripcion in PLATILLOS:
            cursor.execute('''INSERT INTO "Platillos" ("Id_platillo", "Nombre", "Precio", "Descripcion") VALUES (%s, %s, %s, %s)''',
                           (id_p, nombre, precio, descripcion))

        for i in range(1, 51):
            nombre = f"{random.choice(NOMBRES_CLIENTES)} {random.choice(APELLIDOS)}"
            telefono = f"+569{random.randint(10000000, 99999999)}"
            correo = f"{nombre.replace(' ', '.').lower()}@gmail.com"
            cursor.execute('''INSERT INTO "Clientes" ("Id_cliente", "Nombre_cliente", "Telefono_cliente", "Correo_cliente") VALUES (%s, %s, %s, %s)''', (i, nombre, telefono, correo))

        id_reserva = 1
        id_venta = 1
        id_pedido = 1
        fechas = [datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900)) for _ in range(500)]

        for fecha in sorted(fechas):
            cliente = random.randint(1, 50)
            mesa = random.randint(1, 25)
            estado = random.randint(1, 4)
            cantidad = random.randint(1, 6)

            cursor.execute('''INSERT INTO "Reservas" ("Id_reserva", "Id_cliente", "Id_mesa", "Id_estado", "Fecha", "Cantidad_personas")
                             VALUES (%s, %s, %s, %s, %s, %s)''', (id_reserva, cliente, mesa, estado, fecha.date(), cantidad))

            metodo = random.randint(1, len(METODOS_PAGO))
            garzon = random.randint(1, len(GARZONES))
            total = 0
            cursor.execute('''INSERT INTO "Ventas" ("Id_ventas", "Id_metodo", "Id_garzon", "Fecha", "Propina", "Total_venta")
                             VALUES (%s, %s, %s, %s, %s, %s)''', (id_venta, metodo, garzon, fecha.date(), 0, 0))

            for _ in range(random.randint(1, 3)):
                platillo = random.randint(1, 20)
                cantidad_p = random.randint(1, 3)
                cursor.execute('SELECT "Precio" FROM "Platillos" WHERE "Id_platillo" = %s', (platillo,))
                precio = cursor.fetchone()[0]
                subtotal = precio * cantidad_p
                total += subtotal

                cursor.execute('''INSERT INTO "Pedidos" ("Id_pedido", "Id_venta", "Id_mesa", "Id_platillo", "Cantidad_platillo", "Subtotal")
                                 VALUES (%s, %s, %s, %s, %s, %s)''',
                               (id_pedido, id_venta, mesa, platillo, cantidad_p, subtotal))
                id_pedido += 1

            propina = round(total * 0.10)
            cursor.execute('''UPDATE "Ventas" SET "Total_venta" = %s, "Propina" = %s WHERE "Id_ventas" = %s''', (total + propina, propina, id_venta))

            id_reserva += 1
            id_venta += 1

        conn.commit() # <--- ¡CRUCIAL! Confirma todos los cambios en la DB aquí.
        print("\nEsquema creado e información aleatoria insertada.")
        return True # Indica éxito

    except psycopg2.errors.UndefinedTable:
        # Esto no debería ocurrir si el SQL crea las tablas, pero si pasa, es un error grave.
        print("Error: Una tabla esperada no existe después de intentar crear el esquema. Revisa tu SQL.")
        conn.rollback()
        return False
    except psycopg2.errors.DuplicateTable as e:
        print(f"Advertencia: Las tablas ya existen. No se recreó el esquema. {e}")
        conn.rollback() # Limpiar transacción si se intentó algo
        return False
    except Exception as e:
        print(f"Error al crear el esquema o insertar datos: {e}")
        conn.rollback() # Deshace cambios y limpia la transacción en caso de error.
        return False
