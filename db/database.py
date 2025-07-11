import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = f'DRIVER={os.getenv('SQLS_NATIVE')};' \
                    f'SERVER={'localhost'},{1433};' \
                    f'DATABASE={'master'};' \
                    f'UID={'sa'};' \
                    f'PWD={os.getenv("CU_MSSQL_SA_PASSWORD")};' \
                    f'TrustServerCertificate=Yes;'


def get_db_connection():
    """Establece y devuelve una nueva conexión a la base de datos."""
    try:
        conn = pyodbc.connect(CONNECTION_STRING, autocommit=True)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error de conexión a la base de datos: {sqlstate}")
        print(f"Detalles del error: {ex}")
        # Considera re-lanzar la excepción o manejarla de forma más robusta
        raise ConnectionError(f"No se pudo conectar a la base de datos: {ex}")

# Prueba de conexión (opcional, para depuración inicial)
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchall()
        conn.close()
        print("Conexión a la base de datos exitosa!")
        return result
    except Exception as e:
        print(f"Fallo la prueba de conexión a la base de datos: {e}")
        return None