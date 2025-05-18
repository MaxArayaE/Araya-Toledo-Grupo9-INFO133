import psycopg2
import matplotlib.pyplot as plt
import pandas
import os
import sys
from dotenv import load_dotenv

def main(anno):
    print(f"Analizando el año {anno}")

    #Se cargan los datos del .env
    load_dotenv()

    datos_bd={ 
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        }

    #Conección a la Base de Datos.
    conn = psycopg2.connect(**datos_bd)
    
    platillosMasSolicitados(anno, conn)
    diasDeMayorDemanda(anno, conn)
    ventaPromedioMensual(anno, conn)
    
    conn.close()

#Esta función recibe el año deseado y la conección a la base de datos, retorna un gráfico de barras con las estadísticas de cada platillo pedido en el año
def platillosMasSolicitados(anno, conn):
    #Se crea el cursor para manipular las consultas
    cursor = conn.cursor()

    consulta = '''
    SELECT P."Nombre", SUM(H."Cantidad") AS total_pedidos
    FROM "Hechos_Ordenes" H
    JOIN "Platillos" P ON H."Id_platillo" = P."Id_platillo"
    WHERE EXTRACT(YEAR FROM H."Fecha") = %s
    GROUP BY P."Nombre"
    ORDER BY total_pedidos DESC;
    '''
    #Se le dice a la bd que ejecute el script
    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()

    #Se cierra el cursor
    cursor.close()

    #Se asegura de que existan datos para el año solicitado
    if not resultados:
        print(f"No se encontraron pedidos para el año {anno}.")
        return

    # Convertir resultados a DataFrame
    df = pandas.DataFrame(resultados, columns=["Platillo", "Cantidad"])

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.bar(df["Platillo"], df["Cantidad"], color="salmon")
    plt.title(f"Platillos más solicitados en {anno}")
    plt.xlabel("Platillo")
    plt.ylabel("Cantidad Pedida")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    #Guardado de la Imagen
    guardado = os.path.join('Gráficos_Resultados', f'Analisis_platillos_más_pedidos_{anno}')
    plt.savefig(guardado)
    plt.close()

#Esta función recibe el año deseado y la conección a la base de datos, retorna un gráfico de torta con el porcentaje de demanda de los días en el año
def diasDeMayorDemanda(anno, conn):
    #Se crea el cursor para manipular las consultas
    cursor = conn.cursor()

    consulta = '''
    SELECT EXTRACT(DOW FROM "Fecha") AS dia_semana
    FROM "Hechos_Ordenes"
    WHERE EXTRACT(YEAR FROM "Fecha") = %s;
    '''
    #Se le dice a la bd que ejecute el script
    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()

    #Se cierra el cursor
    cursor.close()

    #Se asegura que existan datos para el año solicitado
    if not resultados:
        print(f"No se encontraron pedidos para el año {anno}.")
        return

    # Convertir resultados a DataFrame
    df = pandas.DataFrame(resultados, columns=["dia_semana"])

    #Se le asigna un ID al día
    mapeo_dias = {
        0: "Domingo",
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado"
    }
    df["nombre_dia"] = df["dia_semana"].map(mapeo_dias)

    # Contar la frecuencia de cada día de la semana
    conteo_dias = df["nombre_dia"].value_counts()

    # Crear el gráfico de torta
    plt.figure(figsize=(8, 8))
    plt.pie(conteo_dias, labels=None, autopct='%1.1f%%', startangle=140)
    plt.title(f"Días de mayor demanda en {anno}")
    plt.axis('equal')

    #Guía de colores en la imagen
    plt.legend(conteo_dias.index, title="Días de la Semana", loc="best")
    plt.tight_layout()

    # Guardado de la Imagen
    guardado = os.path.join('Gráficos_Resultados', f'Analisis_dias_de_mayor_demanda_{anno}')
    plt.savefig(guardado)
    plt.close()

def ventaPromedioMensual(anno, conn):
    query = f"""
        SELECT 
            EXTRACT(MONTH FROM "Fecha") AS mes,
            AVG("Total") AS venta_promedio
        FROM 
            "Hechos_Ordenes"
        WHERE 
            EXTRACT(YEAR FROM "Fecha") = %s
        GROUP BY 
            mes
        ORDER BY 
            mes;
    """

    df = pandas.read_sql(query, conn, params=(anno,))

    # Nombres de los meses para mejor presentación
    meses = [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun", 
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.plot(df["mes"], df["venta_promedio"], marker='o', linestyle='-', color='teal')
    plt.xticks(df["mes"], [meses[int(m) - 1] for m in df["mes"]])
    plt.title(f"Venta Promedio Mensual en {anno}")
    plt.xlabel("Mes")
    plt.ylabel("Venta Promedio ($)")
    plt.grid(True)
    plt.tight_layout()
    
    # Guardado de la Imagen
    guardado = os.path.join('Gráficos_Resultados', f'Analisis_venta_Por_mes_{anno}')
    plt.savefig(guardado)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Por favor, proporciona un año como argumento.")
    else:
        anio_param = sys.argv[1]
        main(anio_param)
