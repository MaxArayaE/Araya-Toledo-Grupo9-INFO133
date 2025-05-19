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
    
    #Crea carpeta si no existe, para guardar los gráficos
    os.makedirs(f'Gráficos_Resultados_{anno}', exist_ok=True)

    #Conección a la Base de Datos.
    conn = psycopg2.connect(**datos_bd)
    
    platillosMasSolicitados(anno, conn)
    diasDeMayorDemanda(anno, conn)
    ventaPromedioMensual(anno, conn)
    ingresosPorPlatillo(anno, conn)
    ingresosPorMetodoPago(anno, conn)
    promedioMensualPersonasPorReserva(anno, conn)
    
    
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
    
    #Guardado de la imagen
    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_platillos_más_solicitados_año_{anno}.png')
    plt.savefig(guardado)
    plt.close()

    print(f"Gráfico guardado en: {guardado}")

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
    
    #Guardado de la imagen
    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_día_mayor_demanda_{anno}.png')
    plt.savefig(guardado)
    plt.close()

    print(f"Gráfico guardado en: {guardado}")

def ventaPromedioMensual(anno, conn):

    #Se habre el cursor a la conexión
    cursor = conn.cursor()
    consulta = """
        SELECT EXTRACT(MONTH FROM "Fecha") AS mes, AVG("Total") AS venta_promedio
        FROM "Hechos_Ordenes"
        WHERE EXTRACT(YEAR FROM "Fecha") = %s
        GROUP BY mes
        ORDER BY mes;
    """
    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()
    cursor.close()

    #Nos aseguramos de la existencia de datos
    if not resultados:
        print(f"No se encontraron pedidos para el año {anno}.")
        return
    
    #Se genera el dataframe de los datos
    df = pandas.DataFrame(resultados, columns=["mes", "venta_promedio"])

    #Mapeo de los meses del año
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    #Generamos el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df["mes"], df["venta_promedio"], marker='o', linestyle='-', color='teal')
    plt.xticks(df["mes"], [meses[int(m) - 1] for m in df["mes"]])
    plt.title(f"Venta Promedio Mensual en {anno}")
    plt.xlabel("Mes")
    plt.ylabel("Venta Promedio ($)")
    plt.grid(True)
    plt.tight_layout()
    
    #Guardado de la imagen
    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_venta_Por_mes_{anno}.png')
    plt.savefig(guardado)
    plt.close()

    print(f"Gráfico guardado en: {guardado}")

def promedioMensualPersonasPorReserva(anno, conn):
    cursor = conn.cursor()
    consulta = """
        SELECT DATE_TRUNC('month', "Fecha") AS mes, AVG("Cantidad") AS promedio_personas
        FROM "Reservas"
        WHERE EXTRACT(YEAR FROM "Fecha") = %s
        GROUP BY mes
        ORDER BY mes;
    """
    
    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()
    cursor.close()

    if not resultados:
        print(f"No se encontraron reservas para el año {anno}.")
        return

    df = pandas.DataFrame(resultados, columns=["mes", "promedio_personas"])
    
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    plt.figure(figsize=(10, 6))
    plt.plot(range(len(df)), df["promedio_personas"], marker='o', linestyle='-', color='darkorange')
    plt.xticks(ticks=range(len(df)), labels=[meses[m.month - 1] for m in df["mes"]])
    plt.title(f"Promedio Mensual de Personas por Reserva en {anno}")
    plt.xlabel("Mes")
    plt.ylabel("Promedio de Personas")
    plt.grid(True)
    plt.tight_layout()

    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_promedio_Personas_Reserva_Mensual_{anno}.png')
    plt.savefig(guardado)
    plt.close()
    
    print(f"Gráfico guardado en: {guardado}")

def ingresosPorMetodoPago(anno, conn):
    cursor = conn.cursor()
    consulta = """
        SELECT mp."Metodo", SUM(ho."Total") AS total_ingresos
        FROM "Hechos_Ordenes" ho
        JOIN "MetodoPago" mp ON ho."Id_metodo" = mp."Id_metodo"
        WHERE EXTRACT(YEAR FROM ho."Fecha") = %s
        GROUP BY mp."Metodo"
        ORDER BY total_ingresos DESC;
    """
    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()
    cursor.close()

    if not resultados:
        print(f"No se encontraron ingresos para el año {anno}.")
        return

    # Crear DataFrame con nombres de método de pago
    df = pandas.DataFrame(resultados, columns=["Método de Pago", "Ingresos"])

    # Gráfico de barras horizontales
    plt.figure(figsize=(10, 6))
    bars = plt.barh(df["Método de Pago"], df["Ingresos"], color="mediumseagreen")

    # Título y etiquetas
    plt.title(f"Ingresos por Método de Pago en {anno}")
    plt.xlabel("Ingresos ($)")
    plt.ylabel("Método de Pago")
    plt.grid(axis='x', linestyle='--', alpha=0.5)

    # Etiquetas eje X con formato chileno
    max_val = df["Ingresos"].max()
    pasos = 5
    ticks = [int(max_val * i / pasos) for i in range(pasos + 1)]
    etiquetas = [f"${x:,.0f}".replace(",", ".") for x in ticks]
    plt.xticks(ticks, etiquetas)

    # Mostrar valores dentro de las barras
    for bar in bars:
        width = bar.get_width()
        etiqueta = f"${width:,.0f}".replace(",", ".")
        plt.text(width * 0.98, bar.get_y() + bar.get_height() / 2,
                 etiqueta, ha="right", va="center", color="white", fontsize=10, fontweight="bold")

    plt.tight_layout()

    # Guardar el gráfico
    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_ingresos_Por_Metodo_Pago_{anno}.png')
    plt.savefig(guardado)
    plt.close()

    print(f"Gráfico guardado en: {guardado}")

def ingresosPorPlatillo(anno, conn):
    cursor = conn.cursor()

    consulta = '''
    SELECT P."Nombre", SUM(H."Cantidad" * H."Precio_unitario") AS ingresos
    FROM "Hechos_Ordenes" H
    JOIN "Platillos" P ON H."Id_platillo" = P."Id_platillo"
    WHERE EXTRACT(YEAR FROM H."Fecha") = %s
    GROUP BY P."Nombre"
    ORDER BY ingresos DESC;
    '''

    cursor.execute(consulta, (anno,))
    resultados = cursor.fetchall()
    cursor.close()

    if not resultados:
        print(f"No se encontraron ingresos para el año {anno}.")
        return

    df = pandas.DataFrame(resultados, columns=["Platillo", "Ingresos"])
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df["Platillo"], df["Ingresos"], color="green")
    plt.title(f"Ingresos por platillo en {anno}")
    plt.xlabel("Platillo")
    plt.ylabel("Ingresos ($)")
    plt.xticks(rotation=45, ha="right")

    #Mostrar precios con $ y puntos en el eje Y
    plt.ticklabel_format(style='plain', axis='y')
    max_val = df["Ingresos"].max()
    pasos = 5
    yticks = [int(max_val * i / pasos) for i in range(pasos + 1)]
    ylabels = [f"${x:,.0f}".replace(",", ".") for x in yticks]
    plt.yticks(yticks, ylabels)

    #Mostrar valores dentro de cada barra (en vertical)
    for bar in bars:
        height = bar.get_height()
        etiqueta = f"${height:,.0f}".replace(",", ".")
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height * 0.5,
            etiqueta,
            ha='center',
            va='center',
            rotation=90,
            color='white',
            fontsize=9,
            fontweight='bold'
        )

    plt.tight_layout()
    
    #Guardado del Gráfico
    guardado = os.path.join(f'Gráficos_Resultados_{anno}', f'Analisis_ingresos_por_platillo_{anno}.png')
    plt.savefig(guardado)
    plt.close()
    
    print(f"Gráfico guardado en: {guardado}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Por favor, proporciona un año como argumento.")
    else:
        anio_param = sys.argv[1]
        main(anio_param)
