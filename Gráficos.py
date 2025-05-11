import psycopg2
import matplotlib.pyplot as plt
import pandas
import os

def main():
    #Conección a la Base de Datos, En caso de ser usado en tú computador, cambia las credenciales de abajo
    conn = psycopg2.connect(host="172.27.162.97", dbname="restaurantes", user="maxaraya", password="maximox12", port="5432")
    
    platillosMasSolicitados(2025, conn)
    diasDeMayorDemanda(2025,conn)
    
    #Se cierra la conección a la base de datos
    conn.close()

#Esta función recibe el año deseado y la conección a la base de datos, retorna un gráfico de barras con las estadísticas de cada platillo pedido en el año
def platillosMasSolicitados(año, conn):
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
    cursor.execute(consulta, (año,))
    resultados = cursor.fetchall()

    #Se cierra el cursor
    cursor.close()

    #Se asegura de que existan datos para el año solicitado
    if not resultados:
        print(f"No se encontraron pedidos para el año {año}.")
        return

    # Convertir resultados a DataFrame
    df = pandas.DataFrame(resultados, columns=["Platillo", "Cantidad"])

    # Graficar
    plt.figure(figsize=(10, 6))
    plt.bar(df["Platillo"], df["Cantidad"], color="salmon")
    plt.title(f"Platillos más solicitados en {año}")
    plt.xlabel("Platillo")
    plt.ylabel("Cantidad Pedida")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    #Guardado de la Imagen
    guardado = os.path.join('Gráficos_Resultados', 'Platillos_Más_Pedidos')
    plt.savefig(guardado)
    plt.close()

#Esta función recibe el año deseado y la conección a la base de datos, retorna un gráfico de torta con el porcentaje de demanda de los días en el año
def diasDeMayorDemanda(año, conn):
    #Se crea el cursor para manipular las consultas
    cursor = conn.cursor()

    consulta = '''
    SELECT EXTRACT(DOW FROM "Fecha") AS dia_semana
    FROM "Hechos_Ordenes"
    WHERE EXTRACT(YEAR FROM "Fecha") = %s;
    '''
    #Se le dice a la bd que ejecute el script
    cursor.execute(consulta, (año,))
    resultados = cursor.fetchall()

    #Se cierra el cursor
    cursor.close()

    #Se asegura que existan datos para el año solicitado
    if not resultados:
        print(f"No se encontraron pedidos para el año {año}.")
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
    plt.title(f"Días de mayor demanda en {año}")
    plt.axis('equal')

    #Guía de colores en la imagen
    plt.legend(conteo_dias.index, title="Días de la Semana", loc="best")
    plt.tight_layout()

    # Guardado de la Imagen
    guardado = os.path.join('Gráficos_Resultados', 'Dias_De_Mayor_Demanda')
    plt.savefig(guardado)
    plt.close()

if __name__ == "__main__":
    main()
