import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

def run_etl():
   
    conn_source = None
    cursor_source = None
    conn_target = None
    cursor_target = None

    try:
        
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Credenciales_ENV', '.env')
        load_dotenv(dotenv_path)

        print("Conectando a la base de datos de origen...")
        conn_source = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME_SOURCE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor_source = conn_source.cursor()
        print("Conexión a la BD de origen establecida.")

       
        print("Conectando a la base de datos de destino...")
        conn_target = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME_TARGET"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cursor_target = conn_target.cursor()
        print("Conexión a la BD de destino establecida.")

        
        print("\n--- Fase 1: Limpiando y Creando el Esquema en la BD de Destino desde Restaurante.sql ---")

        
        current_dir = os.path.dirname(__file__) 
        schema_file_path = os.path.join(current_dir, '..', 'BD_analisis', 'Restaurante.sql')

        print(f"Cargando esquema desde: {schema_file_path}")

        target_schema_sql = None
       
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252']

        for encoding in encodings_to_try:
            try:
                with open(schema_file_path, 'r', encoding=encoding) as f:
                    target_schema_sql = f.read()
                print(f"Archivo de esquema '{schema_file_path}' leído exitosamente con encoding '{encoding}'.")
                break 
            except UnicodeDecodeError:
                print(f"Error de decodificación con encoding '{encoding}' para '{schema_file_path}'. Intentando con el siguiente...")
            except FileNotFoundError:
                print(f"Error: El archivo de esquema SQL no se encontró en {schema_file_path}")
                raise 
            except Exception as e:
                
                print(f"Error inesperado al intentar leer '{schema_file_path}' con encoding '{encoding}': {e}")
                raise 

        if target_schema_sql is None:
            raise Exception("No se pudo leer el archivo de esquema SQL con ninguna de las codificaciones intentadas.")

        cursor_target.execute(target_schema_sql)
        conn_target.commit()
        print("Esquema de destino creado/limpiado exitosamente.")

        print("\n--- Fase 2: Cargando Tablas de Dimensión ---")

        print("Cargando dimensión Clientes...")
        cursor_source.execute('SELECT "Id_cliente", "Nombre_cliente", "Telefono_cliente", "Correo_cliente" FROM "Clientes"')
        clientes_data = cursor_source.fetchall()
        for row in clientes_data:
            cursor_target.execute(
                '''INSERT INTO "Clientes" ("Id_cliente", "Nombre", "Telefono", "Correo") VALUES (%s, %s, %s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargados {len(clientes_data)} clientes.")

        print("Cargando dimensión Platillos...")
        cursor_source.execute('SELECT "Id_platillo", "Nombre", "Precio", "Descripcion" FROM "Platillos"')
        platillos_data = cursor_source.fetchall()
        for row in platillos_data:
            cursor_target.execute(
                '''INSERT INTO "Platillos" ("Id_platillo", "Nombre", "Precio", "Descripcion") VALUES (%s, %s, %s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargados {len(platillos_data)} platillos.")


        print("Cargando dimensión MetodoPago...")
        cursor_source.execute('SELECT "Id_metodo", "Metodo" FROM "MetodoPago"')
        metodo_pago_data = cursor_source.fetchall()
        for row in metodo_pago_data:
            cursor_target.execute(
                '''INSERT INTO "MetodoPago" ("Id_metodo", "Metodo") VALUES (%s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargados {len(metodo_pago_data)} métodos de pago.")

        print("Cargando dimensión EstadoReserva...")
        cursor_source.execute('SELECT "Id_estado", "Estado" FROM "EstadoReserva"')
        estado_reserva_data = cursor_source.fetchall()
        for row in estado_reserva_data:
            cursor_target.execute(
                '''INSERT INTO "EstadoReserva" ("Id_estado", "Estado") VALUES (%s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargados {len(estado_reserva_data)} estados de reserva.")

        print("Cargando dimensión Reservas...")
        cursor_source.execute('SELECT "Id_reserva", "Fecha", "Cantidad_personas" FROM "Reservas"')
        reservas_data = cursor_source.fetchall()
        for row in reservas_data:
            cursor_target.execute(
                '''INSERT INTO "Reservas" ("Id_reserva", "Fecha", "Cantidad") VALUES (%s, %s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargadas {len(reservas_data)} reservas como dimensión.")

        print("Cargando dimensión Mesas...")
        cursor_source.execute('''
            SELECT M."N_Mesa", M."Capacidad", U."Ubicacion_local"
            FROM "Mesas" M
            JOIN "Ubicaciones" U ON M."Ubicacion" = U."Id_ubicacion"
        ''')
        mesas_data = cursor_source.fetchall()
        for row in mesas_data:
            cursor_target.execute(
                '''INSERT INTO "Mesas" ("N_Mesa", "Capacidad", "Ubicacion") VALUES (%s, %s, %s)''',
                row
            )
        conn_target.commit()
        print(f"Cargadas {len(mesas_data)} mesas (con ubicación transformada).")

        print("\n--- Fase 3: Cargando Tabla de Hechos (Hechos_Ordenes) ---")


        fact_orders_sql = """
            SELECT
                V."Fecha" AS Fecha,
                R."Id_cliente" AS Id_cliente,
                P."Id_mesa" AS N_Mesa,
                R."Id_reserva" AS Id_reserva,
                P."Id_platillo" AS Id_platillo,
                P."Cantidad_platillo" AS Cantidad,
                PL."Precio" AS Precio_unitario,
                P."Subtotal" AS Total,
                V."Id_metodo" AS Id_metodo,
                R."Id_estado" AS Id_estado
            FROM
                "Pedidos" P
            JOIN
                "Ventas" V ON P."Id_venta" = V."Id_ventas"
            JOIN
                "Platillos" PL ON P."Id_platillo" = PL."Id_platillo"
            JOIN
                "Reservas" R ON R."Id_mesa" = P."Id_mesa" AND R."Fecha" = V."Fecha"
        """

        cursor_source.execute(fact_orders_sql)
        hechos_ordenes_data = cursor_source.fetchall()

        for row in hechos_ordenes_data:
            cursor_target.execute(
                '''INSERT INTO "Hechos_Ordenes"
                   ("Fecha", "Id_cliente", "N_Mesa", "Id_reserva", "Id_platillo",
                    "Cantidad", "Precio_unitario", "Total", "Id_metodo", "Id_estado")
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                row 
            )
        conn_target.commit()
        print(f"Cargados {len(hechos_ordenes_data)} registros en Hechos_Ordenes.")

        print("\n¡Proceso ETL completado exitosamente!")

    except psycopg2.Error as e:
        print(f"Error de base de datos durante el ETL: {e}")
        if conn_source:
            conn_source.rollback()
        if conn_target:
            conn_target.rollback()
    except Exception as e:
        print(f"Ocurrió un error inesperado durante el ETL: {e}")
        if conn_source:
            conn_source.rollback()
        if conn_target:
            conn_target.rollback()
    finally:
        print("\nCerrando conexiones a las bases de datos...")
        if cursor_source:
            cursor_source.close()
        if conn_source:
            conn_source.close()
        if cursor_target:
            cursor_target.close()
        if conn_target:
            conn_target.close()
        print("Conexiones cerradas.")

if __name__ == "__main__":
    run_etl()