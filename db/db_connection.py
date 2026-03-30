import pyodbc
from dotenv import load_dotenv
from db.database import get_db_connection  # Importa la función de conexión

load_dotenv()


def get_linea_por_oferta(idOferta: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Revisa el nombre de tu tabla y columnas
        sql_query = """ SELECT *
                        FROM vw_lineas_oferta
                        WHERE ocl_idOferta = ?
                          and ocl_idArticulo like 'MO%' """
        cursor.execute(sql_query, idOferta)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        print("###")
        print("YO SOY EL QUE PETO")
        print(data)
        print("YO NO SOY EL QUE PETO")
        print("###")

        return data
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}")
        print(f"Error details: {ex}")
        return None
    finally:
        conn.close()


def get_nuevas_lineas():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # pinga
        # vw_lineas_oferta
        sql_query = """ SELECT *
                        FROM vw_lineas_oferta
                        where ocl_idArticulo like 'MO%'"""
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        # print(data[-1])
        return data
    except pyodbc.Error as ex:
        print(ex.args[0])
        print(ex.args[1])
    finally:
        conn.close()


def get_lineas():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # pinga
        # vw_lineas_oferta
        sql_query = """ SELECT *
                        FROM vw_lineas_oferta
                        where ocl_idArticulo like 'MO%'"""
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        # print(data)
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
        # hecho OK
        sql_query = """ SELECT *
                        FROM ofertas
                        where revision = 1
                        ORDER BY idOferta DESC """
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        lineas = get_lineas()
        ids_con_lineas = {
            str(linea["ocl_IdOferta"])
            for linea in lineas
            if linea.get("ocl_IdOferta") is not None
        }
        ofertas_filtradas = [
            oferta
            for oferta in data
            if str(oferta.get("idOferta", "")) in ids_con_lineas
        ]

        return ofertas_filtradas
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
        sql_query = """ SELECT MAX(CAST(idParteAPP AS INTEGER))
                        FROM pers_partes_app """
        cursor.execute(sql_query)
        return cursor.fetchval()
    finally:
        conn.close()


def get_lineas_enriquecidas(idOferta: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = """ SELECT
              v.*,
              p.idParteAPP,
              p.idLinea,
              p.cantidad,
              p.certificado,
              p.fechainsertupdate,
              p.idParteERP,
              p.cantidad
            FROM dbo.vw_lineas_oferta v
            LEFT JOIN Partes.dbo.pers_partes_app p
              ON v.ocl_IdOferta = p.idOferta
              AND v.ocl_idlinea = p.idLinea
              where v.ocl_IdOferta = ?
            ORDER BY v.ocl_IdOferta, v.ocl_idlinea, p.idParteAPP; """
        cursor.execute(sql_query, idOferta)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        print("### AQUÍ ESTÁ EL enriched ###")
        print(data)
        print("###")
        return data
    finally:
        conn.close()


def get_lineas_enriquecidas_por_parte(idParteAPP: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = """ SELECT
              v.ocl_idLinea as id,
              v.ocl_Descrip as descripcion,
              v.ocl_UnidadesPres as cantidad,
              v.ocl_tipoUnidad as unidadMedida,
              v.ocl_IdOferta as ocl_IdOferta,
              p.idParteAPP as idParteAPP,
              p.idLinea as IdLinea,
              p.idParteERP as idParteERP
            FROM dbo.vw_lineas_oferta v
            LEFT JOIN Partes.dbo.pers_partes_app p
              ON v.ocl_IdOferta = p.idOferta
              AND v.ocl_idlinea = p.idLinea
              where p.idParteAPP = ?
            ORDER BY v.ocl_IdOferta, v.ocl_idlinea, p.idParteAPP; """
        cursor.execute(sql_query, idParteAPP)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        return data
    finally:
        conn.close()
