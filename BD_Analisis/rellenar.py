import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

datos_bd={ 
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        }

CSV_FOLDER = "Datos de la BD"
SCHEMA_FILE = "Restaurante.sql"

conn = psycopg2.connect(**datos_bd)

def ejecutar_esquema(conn):
 cursor = conn.cursor()
 with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
    esquema_sql = f.read()
    try:
        for statement in esquema_sql.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement + ';')
            conn.commit()
    except Exception as e:
        print(f"Error ejecutando esquema: {e}")
        conn.rollback()
 cursor.close()


def insertar_csv(conn, archivo_csv):
    nombre_tabla = os.path.splitext(os.path.basename(archivo_csv))[0]

    df = pd.read_csv(archivo_csv)
    if df.empty:
        print(f"Archivo '{archivo_csv}' está vacío. Saltando...")
        return

    columnas = ','.join([f'"{col}"' for col in df.columns])
    valores = [tuple(x) for x in df.to_numpy()]
    placeholders = ','.join(['%s'] * len(df.columns))

    query = f'INSERT INTO "{nombre_tabla}" ({columnas}) VALUES ({placeholders})'

    cursor = conn.cursor()
    try:
        cursor.executemany(query, valores)
        print(f"Datos insertados en '{nombre_tabla}'.")
        conn.commit()
    except Exception as e:
        print(f"Error al insertar en '{nombre_tabla}': {e}")
        conn.rollback()
    cursor.close()

# Orden correcto basado en claves foráneas
orden_tablas = [
    "Clientes",
    "Mesas",
    "Reservas",
    "Platillos",
    "MetodoPago",
    "EstadoReserva",
    "Hechos_Ordenes"
]

# Ejecutar flujo completo
if os.path.exists(SCHEMA_FILE):
    ejecutar_esquema(conn)

for tabla in orden_tablas:
    archivo_csv = os.path.join(CSV_FOLDER, f"{tabla}.csv")
    if os.path.exists(archivo_csv):
        insertar_csv(conn, archivo_csv)
    else:
        print(f"No se encontró CSV para la tabla '{tabla}'.")

conn.close()
print("Proceso completado y conexión cerrada.")