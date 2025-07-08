import datetime

# import psycopg2
import os
from os import getenv

import pyodbc
from dotenv import load_dotenv
import json
# from psycopg2.extras import RealDictCursor

from entities.Project import ProyectoObra

load_dotenv()

connection_string = f'DRIVER={os.getenv('SQLS_NATIVE')};' \
                    f'SERVER={'localhost'},{1433};' \
                    f'DATABASE={'master'};' \
                    f'UID={'sa'};' \
                    f'PWD={os.getenv("CU_MSSQL_SA_PASSWORD")};' \
                    f'TrustServerCertificate=Yes;'
conn = pyodbc.connect(connection_string, autocommit=True)


def get_all_partes():
    return []


def get_linea_por_oferta(idOferta: int):
    try:
        cursor = conn.cursor()
        sql_query = """ select * from ofertas_cli_cabecera where ocl_idOferta = ? """
        cursor.execute(sql_query, idOferta)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names from the cursor description
        columns = [column[0] for column in cursor.description]

        # Convert rows to a list of dictionaries for easier access
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))


        return data


    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None

def get_lineas():
    try:
        cursor = conn.cursor()
        sql_query = """
                    select *
                    from ofertas_cli_cabecera \
                    """
        cursor.execute(sql_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names from the cursor description
        columns = [column[0] for column in cursor.description]

        # Convert rows to a list of dictionaries for easier access
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))


        return data

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None


def get_ofertas():
    try:
        cursor = conn.cursor()
        sql_query = """
                    SELECT *
                    from ofertas_app_v2
                    order by idOferta desc \
                    """
        cursor.execute(sql_query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Get column names from the cursor description
        columns = [column[0] for column in cursor.description]

        # Convert rows to a list of dictionaries for easier access
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        return data

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None


def load_db():
    get_ofertas()


def get_num_parte():
    cursor = conn.cursor()
    sql_query = """
                select max(cast(IdParte as integer))
                from pers_partes_app \
                    
                """
    cursor.execute(sql_query)
    return cursor.fetchval()
