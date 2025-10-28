from typing import List, Optional

import pyodbc
from dotenv import load_dotenv
from db.database import get_db_connection
from dto.ParteDTO import ParteImprimirPDF, ParteRecibidoPost
from entities.LineaPedido import LineaPedidoPost
from entities.User import User
from entities.partesmo.ParteMO import ParteMO
from pdf_manager import fill_parte_obra_pymupdf
from fastapi import HTTPException

load_dotenv()


def test_connection():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        return cursor.fetchall()
    finally:
        conn.close()  # Asegúrate de cerrar la conexión


def get_partes_mo_db(ff: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql_query = sql_query = """
                                SELECT pmo.*,
                              mo.*
                       FROM partes_mano_obra AS pmo
                                JOIN
                            manos_partes_interm AS mpi ON pmo.idParte = mpi.idParteMO
                                JOIN
                            mano_de_obra AS mo ON mpi.idManoObra = mo.idManoObra
                       WHERE pmo.idParteERP = ?
                       ORDER BY pmo.idParteERP DESC;
                                """
        # IMPORTANTE: El parámetro 'ff' debe pasarse como una tupla o lista.
        # En este caso, como es un solo parámetro, se recomienda una tupla de un solo elemento.
        cur.execute(sql_query, (ff,))

        rows = cur.fetchall()
        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in rows]
        print(data)
        return data
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None
    finally:
        conn.close()
