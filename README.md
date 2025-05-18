# Analisis de restaurante "El Campesino"

## 1. Como funciona?
 El programa (`analisis.py`) se encarga generar gráficos para las siguientes preguntas de un año especifico:

 * ¿Cuáles fueron los platillos más pedidos en un año específico?
 * ¿Qué días hay mayor demanda?
 * ¿Cuánto se vende al mes?
 * (faltan añadir 3)

Los gráficos resultantes son almacenados en la carpeta (`Gráficos_Resultados`) en formato png

## 2. Prerrequsitos del programa:

Antes de ejecutar este programa, asegúrate de tener instalado lo siguiente:

### Postgresql (con el servidor instalado y corriendo)

- Si no lo tienes puedes seguir los pasos de [postgresql.org](https://www.postgresql.org/download/)
 
### Entorno de Python

- Python 3.8 o superior  
Puedes descargarlo desde [python.org](https://www.python.org/).

### Librerías necesarias

- Pandas
- Matplotlib
- Psycopg2

Instálalas usando `pip` si estas usando un entorno de linux (recomendado):

```bash
pip install pandas matplotlib psycopg2
```

Si no usa:

```bash
pip install pandas matplotlib psycopg2-binary
```

## 3. Como utilizar el programa?

### 3.2 Primero clona el repositorio usando `git`:

```bash
git clone https://github.com/MaxArayaE/Araya-Toledo-Grupo9-INFO133.git
cd Araya-Toledo-Grupo9-INFO133
```
### 3.3 Editar credenciales:

clona el archivo `.env_credenciales` y nombralo `.env`, en el modifica a tus datos, para acceder a la bd:

* DB_HOST="localhost"
* DB_PORT="5432"
* DB_NAME="midb"
* DB_USER="miusuario"
* DB_PASSWORD="miclave"


