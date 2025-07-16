import pyodbc
from dotenv import load_dotenv

from db.database import get_db_connection # Importa la función de conexión

load_dotenv()

def get_all_partes():
    # Implementar si es necesario, usando get_db_connection()
    return []


def get_linea_por_oferta(idOferta: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Revisa el nombre de tu tabla y columnas
        sql_query = """ SELECT * FROM ofertas_cli_cabecera WHERE ocl_idOferta = ? and ocl_idArticulo like 'MO%' """
        cursor.execute(sql_query, idOferta)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return data
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None
    finally:
        conn.close()

def get_lineas():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = """ SELECT * FROM ofertas_cli_cabecera where ocl_idArticulo like 'MO%'"""
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return data
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None
    finally:
        conn.close()


def get_ofertas():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = """ SELECT * FROM ofertas_app_v2 ORDER BY idOferta DESC """
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return data
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None
    finally:
        conn.close()

def load_db():
    get_ofertas()


def get_num_parte():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = """ SELECT MAX(CAST(IdParte AS INTEGER)) FROM pers_partes_app """
        cursor.execute(sql_query)
        return cursor.fetchval()
    finally:
        conn.close()