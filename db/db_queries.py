import os
from datetime import datetime

import psycopg2
import pyodbc
from dotenv import load_dotenv
from dto.ParteDTO import ParteDTO, ParteRecibidoPost
from entities.LineaPedido import LineaPedidoDTO, LineaPedidoPost

load_dotenv()

connection_string = f'DRIVER={os.getenv('SQLS_NATIVE')};' \
                    f'SERVER={'localhost'},{1433};' \
                    f'DATABASE={'master'};' \
                    f'UID={'sa'};' \
                    f'PWD={os.getenv("CU_MSSQL_SA_PASSWORD")};' \
                    f'TrustServerCertificate=Yes;'
conn = pyodbc.connect(connection_string, autocommit=True)


def test_connection():
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    return cursor.fetchall()


def create_parte(parte: LineaPedidoPost):
    print(parte)
    return None


def create_lineas(lineas: list):
    for linea in lineas:
        create_linea(linea)
    return None


def create_linea(linea: LineaPedidoDTO):
    sql_query = """
                INSERT INTO pers_partes_certificacion_lineas(idparte, idoferta, titulo, idlinea,
                                                             descriparticulo, cantidad, unidadmedica, certificado,
                                                             fechainsertupdate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """

    current_time = datetime.now()
    values = (
        linea.id_parte,
        linea.id_oferta,
        #  linea.capitulo,
        linea.descripcion,
        linea.id,
        #  linea.idArticulo,
        linea.descripcion,
        linea.unidades_puestas_hoy,  # unidad medida
        linea.unidades_totales,  # unidades oferta
        0,
        current_time
    )
    cur = conn.cursor()

    try:
        cur.execute(sql_query, values)
        # If you're using a connection object directly:
        # connection.commit() # Don't forget to commit the changes if you're not in an auto-commit mode
        print("Linea inserted successfully!")
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        print(f"Error inserting linea: {e}")
        # connection.rollback() # Rollback in case of an error

    return linea
