import datetime
import uuid
from typing import List, Optional
from dotenv import load_dotenv
from psycopg2._psycopg import cursor
from pyodbc import Error
from exceptions import DatabaseError

from db.database import get_db_connection
from dto.ParteDTO import ParteImprimirPDF, ParteRecibidoPost
from entities.LineaPedido import LineaPedidoPost
from entities.User import User
from entities.partesmo.ParteMO import (
    ParteMORecibir,
    Materiales,
    Desplazamiento,
    ManoDeObra,
)
from pdf_manager import fill_parte_obra_pymupdf
from fastapi import HTTPException

load_dotenv()


def test_connection():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchall()
    finally:
        conn.close()  # Asegúrate de cerrar la conexión


def get_lineas_con_oferta(idOferta: int) -> List[dict]:
    conn = get_db_connection()
    try:
        sql_query = """
                    SELECT *
                    FROM pers_partes_app
                    WHERE idOferta = ?
                    """
        cursor = conn.cursor()
        cursor.execute(sql_query, (idOferta,))
        rows = cursor.fetchall()

        data = []
        if rows:
            columns = [description[0] for description in cursor.description]
            for row in rows:
                data.append(dict(zip(columns, row)))
        return data
    except Exception as e:
        print(f"Error al obtener partes por oferta {idOferta}: {e}")
        return []
    finally:
        conn.close()


def get_cantidad_realizada(conn, idOferta: int, idLinea: int) -> float:
    sql_query = """
                SELECT SUM(cantidad)
                FROM pers_partes_app
                WHERE idOferta = ?
                  AND idLinea = ?
                """
    cursor = conn.cursor()
    cursor.execute(sql_query, (idOferta, idLinea))
    result = cursor.fetchone()
    if result and result[0] is not None:
        return float(result[0])
    return 0.0


def create_parte(parte: ParteRecibidoPost):
    print(parte)
    conn = get_db_connection()
    try:
        crear_parte_app(conn, parte)  # Pasa la conexión
        for linea in parte.lineas:
            # ACTUALIZACIÓN:
            # En lugar de comprobar si existe linea en Ofertas y crearla (duplicando),
            # confiamos en pers_partes_app para el histórico.
            # Aqui solo actualizamos el acumulado en Lineas_Oferta para referencia.

            handle_pers_partes(conn, parte, linea)

            # 1. Obtenemos lo realizado TOTAL (incluyendo lo que acabamos de insertar en handle_pers_partes?
            #    Ah espera, handle_pers_partes hace insert. Si lo llamamos antes, get_cantidad_realizada lo verá si estamos en la misma tx?
            #    Normalmente sí, si la isolation level lo permite.
            #    Para asegurar, sumamos la linea actual a lo que retorne get_cantidad_realizada (si esta excluye la actual)
            #    O simplemente calculamos: acumulado_anterior + actual.

            # Mejor consultamos la base, asumiendo Read Uncommitted o que nuestra insert es visible.
            # Si no, sumamos manualmente.

            total_realizado = get_cantidad_realizada(
                conn, parte.idOferta, linea.id_linea
            )
            # handle_pers_partes ya insertó, así que total_realizado debería incluirlo si la tx lo ve.
            # Asumimos que sí por ser misma conexión.

            print(f"Total realizado para linea {linea.id_linea}: {total_realizado}")

            update_linea_cumulative(conn, linea, total_realizado)

        conn.commit()  # Asegúrate de hacer commit si autocommit es False o si manejas transacciones
    except Exception as e:
        print(f"Error al crear el parte completo: {e}")
        conn.rollback()  # Rollback en caso de error
        raise  # Re-lanza la excepción para que FastAPI pueda manejarla
    finally:
        conn.close()
    return parte


def update_idParteERP(parte: ParteRecibidoPost):
    conn = get_db_connection()
    try:
        sql_query = """
                    UPDATE Lineas_Oferta
                    SET ppcl_IdParte = ?
                    WHERE idParteAPP = ? \
                    """
        cursor = conn.cursor()
        cursor.execute(sql_query, (parte.idParteERP, parte.idParteAPP))
        conn.commit()
    except Exception as e:
        print(f"Error al actualizar el parte (app): {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def get_parte_pdf(idParte: int) -> Optional[dict]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Asegúrate que los nombres de las columnas coincidan con ParteImprimirPDF
        # O usa AS para renombrar
        q = """
            SELECT P.idParteERP,
                   P.idParteAPP,
                   P.proyecto,
                   P.oferta,
                   P.jefe_equipo,
                   P.telefono,
                   P.fecha,
                   P.contacto_obra,
                   P.comentarios,
                   P.firma,
                   P.idOferta,
                   O.idProyecto
            FROM partes_app_obra P
            LEFT JOIN Ofertas O ON P.idOferta = O.idOferta
            WHERE P.idParteAPP = ? \
            """
        cur.execute(q, (idParte,))
        parte_data_row = cur.fetchone()

        if parte_data_row:
            columns = [description[0] for description in cur.description]
            # Convierte la fila en un diccionario usando los nombres de las columnas
            parte_data = dict(zip(columns, parte_data_row))
            print(parte_data)
            return parte_data
        else:
            return None
    except Exception as e:
        print(f"Error al obtener parte (pdf) para idParte {idParte}: {e}")
        return None


# Recibe la conexión como argumento
def crear_parte_app(conn, parte: ParteRecibidoPost):
    cur = conn.cursor()
    sql_query = """
                INSERT INTO partes_app_obra(idOferta, pdf, idParteAPP, proyecto, oferta, jefe_equipo, telefono,
                                                        fecha, contacto_obra, comentarios, firma, revsion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """
    # Asegúrate que el campo 'firma' en tu modelo coincide con el de la DB
    # parte.signature es el campo de Pydantic, que se mapea a 'firma' en la DB
    # parte.fecha puede necesitar ser convertido a string si la DB lo espera como string,
    # aunque lo ideal es que lo guardes como DATE o DATETIME en la DB.
    values = (
        parte.idOferta,
        None,
        parte.idParteAPP,
        parte.proyecto,
        parte.oferta,
        parte.jefe_equipo,
        parte.telefono,
        parte.fecha,
        parte.contacto_obra,
        parte.comentarios,
        parte.firma,  # Asegúrate de usar parte.signature
        parte.revision,
    )

    try:
        cur.execute(sql_query, values)
        print("Datos insertados correctamente en partes_app_obra!")
        # No necesitas commit si autocommit=True en la conexión
        return parte
    except Exception as e:
        print(f"Error al crear el parte (app): {e}")
        raise  # Re-lanza para que la transacción principal pueda hacer rollback


# Recibe la conexión como argumento


# Recibe la conexión como argumento
def update_linea_cumulative(conn, linea: LineaPedidoPost, total_realizado: float):
    cur = conn.cursor()
    # Actualizamos Lineas_Oferta.
    # NO tocamos idParteApp necesariamente para evitar conflictos,
    # o lo actualizamos al "último" (last write wins).
    # Actualizamos ppcl_cantidad con el TOTAL realizado.

    # Asumimos que idLinea y idOferta son la clave.

    sql_query = """
                UPDATE Lineas_Oferta
                SET ppcl_cantidad        = ?,
                idParteAPP = ? 
                WHERE ocl_idOferta = ?
                  AND ocl_idlinea = ?
                """
    # Si quisieramos guardar el último parte: , idParteApp = ?
    # Pero el usuario indicó problemas con esto. Lo más seguro es actualizar solo la cantidad.

    values = (total_realizado, linea.idParteAPP, linea.id_oferta, linea.id_linea)

    try:
        cur.execute(sql_query, values)
        if cur.rowcount == 0:
            # Fallback si por alguna razón ocl_idlinea no matchea (legacy data?)
            # Intentamos con description y idArticulo como hacía antes
            print("No se actualizó por ID, intentando fallback legacy...")
            sql_fallback = """
                UPDATE Lineas_Oferta
                SET ppcl_cantidad = ?
                WHERE ocl_idOferta = ?
                  AND ocl_Descrip = ?
                  AND ocl_IdArticulo = ?
            """
            cur.execute(
                sql_fallback,
                (total_realizado, linea.id_oferta, linea.descripcion, linea.idArticulo),
            )

        print("Linea actualizada correctamente en Lineas_Oferta (Acumulado)!")
    except Exception as e:
        print(f"Error al actualizar linea en Lineas_Oferta: {e}")
        # No hacemos raise para no interrumpir el flujo principal, ya que pers_partes_app es lo importante ahora.
        # Pero es bueno loguearlo.


# Recibe la conexión como argumento
def handle_pers_partes(conn, parte: ParteRecibidoPost, linea: LineaPedidoPost):
    cur = conn.cursor()
    sql_query = """
                INSERT INTO pers_partes_app(idParteAPP, idOferta, revision, capitulo, titulo, idlinea, idarticulo,
                                            descriparticulo, cantidad, unidadmedida, certificado, fechainsertupdate,
                                            cantidad_total, revision)
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """
    # Ajusta los valores para que coincidan con los campos de LineaPedidoPost y las columnas de tu DB
    values = (
        parte.idParteAPP,
        parte.idOferta,
        1,  # revision, si es un valor fijo
        linea.capitulo,  # del DTO LineaPedidoPost
        "Titulo del Capitulo",  # Si es fijo o viene de alguna parte
        linea.id_linea,  # id de la linea (LineaPedidoPost)
        linea.idArticulo,
        linea.descripcion,
        linea.unidades_puestas_hoy,  # Asumo que es 'cantidad' en pers_partes_app
        linea.medida,  # Asumo que es 'unidadMedida' en pers_partes_app
        linea.ya_certificado,
        parte.fecha,
        linea.unidades_totales,
        parte.revision,
    )
    # linea nueva, capitulo 99999
    try:
        cur.execute(sql_query, values)
        print("Linea insertada correctamente en pers_partes_app!")
    except Exception as e:
        print(f"Error al insertar linea en pers_partes_app: {e}")
        raise


def get_lineas_pdf(parteId: int) -> List[dict]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Asegúrate que los AS coincidan EXACTAMENTE con los nombres de campo en LineaPedidoPDF
        q = """
            SELECT  id,
                    IdLinea         AS id_linea,
                    DescripArticulo AS descripcion,
                    cantidad        AS cantidad,
                    UnidadMedida    AS unidadMedida
            FROM pers_partes_app
            WHERE idParteAPP = ? \
            """
        cur.execute(q, (parteId,))
        rows = cur.fetchall()

        data = []
        columns = [
            column[0] for column in cur.description
        ]  # Obtiene los nombres de las columnas (con AS)
        for row in rows:
            data.append(dict(zip(columns, row)))
        return data
    except Exception as e:
        print(f"Error al obtener líneas para parteId {parteId}: {e}")
        return []
    finally:
        conn.close()


def create_pdf_file(parte: ParteImprimirPDF):
    # Asegúrate que el path de la plantilla sea correcto
    # Y el nombre del archivo de salida
    template_path = "parte-obra_vacio.pdf"
    output_filename = f"{parte.oferta}_{parte.idParteERP}.pdf"
    fill_parte_obra_pymupdf(template_path, output_filename, parte)


def asginar_trabajadores_bd(idParte: int, workers: List[User]):
    query = """INSERT INTO workers_partes (idParte, idTrabajador, nombreTrabajador)
               VALUES (?, ?, ?)"""
    try:
        for w in workers:
            con = get_db_connection()
            con.execute(query, (idParte, w.id, w.name))
    except Exception as e:
        print(f"Error al asignar trabajadores a parte: {e}")
        return False

    return True


def get_trabajadores_parte(idParte: int):
    query = """SELECT idTrabajador, nombreTrabajador
               FROM workers_partes
               WHERE idParte = ?"""
    con = get_db_connection()
    cur = con.cursor()
    cur.execute(query, (idParte,))
    rows = cur.fetchall()

    data = []
    columns = [
        column[0] for column in cur.description
    ]  # Obtiene los nombres de las columnas (con AS)
    for row in rows:
        data.append(dict(zip(columns, row)))
    return data


def subir_imagen(idOferta: int, imagen: str):
    query = """ INSERT INTO imagenes_obras (obra_id, image_name)
                values (?, ?)"""

    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute(query, (idOferta, imagen))

    except Exception as e:
        print(f"Error al subir imagen: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al crear el parte de obra: {e}"
        )

    return {"message": "Imagen subida exitosamente asociada a ." + str(idOferta) + ""}


def get_imagenes_por_oferta(idOferta):
    query = """SELECT image_name
               FROM imagenes_obras
               WHERE obra_id = ?"""
    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute(query, (idOferta,))
        rows = cur.fetchall()
        images = [row[0] for row in rows]
        print(rows)
        return images
    except Exception as e:
        print(f"Error al obtener imagenes por oferta: {e}")
    return []


def solicitar_numero_ERP():
    input_id = input(
        "Introduce el ID ERP para el parte APP de mano obra (Enter para usar 0 y salir): "
    )
    if not input_id:
        input_id = 0
    else:
        input_id = int(input_id)

    return input_id


def get_desplazamiento_from_vehiculo(idVehiculo: int):
    query = """SELECT id
               FROM desplazamientos
               WHERE vehiculo_id = ?"""
    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute(query, (idVehiculo,))
        rows = cur.fetchone()
        return rows[0]
    except Exception as e:
        print(f"Error al obtener desplazamientos por vehiculo: {e}")
    return []


def crear_parte_mo_bd(parte: ParteMORecibir):
    conn = get_db_connection()
    sql_query = """INSERT INTO partes_mano_obra (idTrabajador, idParteERP, idParteAPP, idProyecto, estado, observaciones,
                                                 creation_date, update_time, firma_trabajador, idOferta)
                   values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor = conn.cursor()
    # Generar ID Parte APP (UUID)
    idParteAPP = str(uuid.uuid4())

    idParteERP = solicitar_numero_ERP()

    # Valores para la tabla principal
    valores_insertar = (
        parte.usuario,
        idParteERP,
        idParteAPP,  # Usamos el UUID generado como idParteAPP
        parte.idProyecto,
        "pendiente",
        parte.comentarios,
        datetime.datetime.strptime(parte.fecha, "%Y-%m-%d").date(),
        datetime.datetime.strptime(parte.fecha, "%Y-%m-%d").date(),
        "data",  # FIRMA POR IMPLEMENTAR si va sin firmar va NULL
        parte.idOferta,
    )
    print(valores_insertar)

    try:
        # Usamos idParteAPP para todas las relaciones intermedias
        for row in parte.materiales:
            print("materiales")
            # insertar_materiales (si es necesario) pero sobre todo la relación intermedia
            insertar_materiales(idParteAPP, row, conn)
            print("OK")

        for row in parte.desplazamientos:
            print("desplazamientos")
            insertar_desplazamiento(row, conn)
            # Obtener el ID del desplazamiento real (asociado al vehículo)
            id_desplazamiento = get_desplazamiento_from_vehiculo(
                int(row.id)
            )  # row.id es vehiculo_id aquí

            if id_desplazamiento:
                desplazamientos_intermedios(idParteAPP, id_desplazamiento, conn)
                print("OK")
            else:
                print(f"Error: No se encontró desplazamiento para vehiculo {row.id}")

        for row in parte.manosdeobra:
            print("manosdeobra")
            insertar_manos(row, conn)
            manos_intermedias(idParteAPP, row, conn)
            print("OK")

        cursor.execute(sql_query, valores_insertar)
        conn.commit()  # Importante: commit si no es autocommit

        return {"message": "OK", "idParteAPP": idParteAPP}

    except Error as ex:
        conn.rollback()
        sqlstate = ex.args[0] if ex.args else "Unknown"
        print(f"Database error: {sqlstate}")
        raise DatabaseError(f"Error creating Parte MO: {ex}")
    except Exception as ex:
        conn.rollback()
        raise DatabaseError(f"Unexpected error creating Parte MO: {ex}")
    finally:
        conn.close()
        # TODO: meterle lo de que avise cuando está creado (devuelve 200 OK y bla bla bla)


def insertar_desplazamiento(desplazamiento: Desplazamiento, conn):
    sql_query = """ INSERT INTO desplazamientos(vehiculo_id, kilometros, creation_date, update_date) values (?,?,?,?) """
    cursor = conn.cursor()

    try:
        cursor.execute(
            sql_query,
            (
                desplazamiento.id,
                desplazamiento.distancia,
                datetime.datetime.now(),
                datetime.datetime.now(),
            ),
        )
    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")
    return {"message": "desplazamiento insertado OK"}


def insertar_manos(m: ManoDeObra, conn):
    sql_query = """INSERT INTO mano_de_obra(idManoObra, accion, unidades, creation_date, update_date)
                   VALUES (?, ?, ?, ?, ?)"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            sql_query,
            (
                m.idManoObra,
                m.accion,
                m.unidades,
                datetime.datetime.now(),
                datetime.datetime.now(),
            ),
        )
        return {"message": "mano de obra inserado OK"}
    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")
    return {"error": "mano de obra NO insertado"}


def insertar_materiales(idParte: str, mat: Materiales, conn):
    sql_query = """INSERT INTO partes_materiales_interm (idMaterial, idParteMO)
                   values (?, ?)"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query, (mat.id, idParte))
    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")

    return ""


def manos_intermedias(idParte: str, mo: ManoDeObra, conn):
    sql_query = """INSERT INTO manos_partes_interm (idManoObra, idParteMO, creation_date, update_time)
                   values (?, ?, ?, ?)"""
    cursor = conn.cursor()
    try:
        print(mo.idManoObra, type(mo.idManoObra))
        print(idParte, type(idParte))
        cursor.execute(
            sql_query,
            (mo.idManoObra, idParte, datetime.datetime.now(), datetime.datetime.now()),
        )
    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")

    return ""


def desplazamientos_intermedios(idParte: str, idDesplazamiento: int, conn):
    sql_query = """INSERT INTO desplazamientos_partes_interm (idDesplazamiento, idParteMO)
                   values (?, ?)"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query, (idDesplazamiento, idParte))

    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")

    return ""


def get_materiales_db():
    sql_query = """SELECT *
                   FROM materiales"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql_query)

    rows = cur.fetchall()
    try:
        data = []
        columns = [
            column[0] for column in cur.description
        ]  # Obtiene los nombres de las columnas (con AS)
        for row in rows:
            data.append(dict(zip(columns, row)))

        return data

    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")
        return None


def get_vehiculos_db():
    sql_query = """SELECT *
                   FROM vehiculos"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql_query)

    rows = cur.fetchall()
    try:
        data = []
        columns = [
            column[0] for column in cur.description
        ]  # Obtiene los nombres de las columnas (con AS)
        for row in rows:
            data.append(dict(zip(columns, row)))

        return data

    except Exception as e:
        sqlstate = e.args[0]
        print(f"Database error: {sqlstate}")
        return None
