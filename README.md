# Menú CRUD de restaurante "El Campesino"

## 1. Como funciona?
Es un display de menu en terminal, tendras una opción por función CRUD sobre Reservas y ventas del restaurante. 

## 2. Prerrequsitos del programa:

Antes de ejecutar este programa, asegúrate de tener instalado lo siguiente:

### Postgresql (con el servicio iniciado y corriendo)

- Si no lo tienes puedes seguir los pasos de [postgresql.org](https://www.postgresql.org/download/)

### Entorno de Python

- Python 3.8 o superior  
  Puedes descargarlo desde [python.org](https://www.python.org/).

### Librerías necesarias

- tabulate
- Psycopg2
- Python-dotenv

Instálalas usando `pip`, si estas usando un entorno de windows:

```bash
pip install tabulate  python-dotenv psycopg2-binary
```

Si no, puedes usar:

```bash
pip install tabulate python-dotenv psycopg2
```

## 3. Preparar la Base de Datos

### 3.1 Iniciar y crear BD postgresql

Con postgresql instalado y en tu entorno a eleccion, ejecuta los siguientes comandos:

```bash
sudo service postgresql start
sudo -u postgres psql
```

En la terminal de postgresql, borra y cambia los parametros entre <> a tu eleccion:

```bash
CREATE USER <nombre_usuario> WITH PASSWORD <'contraseña_segura'>;
CREATE DATABASE <mibasededatos> OWNER <nombre_usuario>;
```

### Ejemplo

```bash
CREATE USER admin WITH PASSWORD 12345;
CREATE DATABASE restaurante OWNER admin;
```

### 3.2 Clona el repositorio usando `git`:

```bash
git clone https://github.com/MaxArayaE/Araya-Toledo-Grupo9-INFO133.git
cd Araya-Toledo-Grupo9-INFO133
```

### 3.3 Editar credenciales:

Clona el archivo `.env_credenciales` y nombralo `.env`, en él modifica a tus datos con los que creaste la base de datos, para acceder a ella con el programa:

- DB_HOST="localhost"
- DB_PORT="5432"
- DB_NAME="midb"
- DB_USER="miusuario"
- DB_PASSWORD="miclave"

### 4 menu_app.py

Este script inicializa el menú y podras empezar a usarlo.
Asegurate de utilizar laopción 9 del menú primeramente para generar los datos en la BD

Ingresa la opción que quieras utilizar del menú en el terminal y estás listo.
