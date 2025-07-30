from typing import List, Optional
from dotenv import load_dotenv
from db.database import get_db_connection
from dto.ParteDTO import ParteImprimirPDF, ParteRecibidoPost
from entities.LineaPedido import LineaPedidoPost
from entities.User import User
from pdf_manager import fill_parte_obra_pymupdf

load_dotenv()


def test_connection():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        return cursor.fetchall()
    finally:
        conn.close()  # Asegúrate de cerrar la conexión


def create_parte(parte: ParteRecibidoPost):
    print(parte)
    conn = get_db_connection()
    try:
        crear_parte_app(conn, parte)  # Pasa la conexión
        for linea in parte.lineas:
            # NO LLAMAR crear_parte_app(parte) aquí de nuevo
            handle_pers_partes(conn, parte, linea)  # Pasa la conexión
            # handle_ofertas_cli(parte, linea) # Si necesitas esto, también pasa la conexión y ajusta
            # TODO crearia un nuevo ofertacli si tengo lineas adicionales
            update_ppl(conn, linea)  # Pasa la conexión
        conn.commit()  # Asegúrate de hacer commit si autocommit es False o si manejas transacciones
    except Exception as e:
        print(f"Error al crear el parte completo: {e}")
        conn.rollback()  # Rollback en caso de error
        raise  # Re-lanza la excepción para que FastAPI pueda manejarla
    finally:
        conn.close()
    return parte


def get_parte_pdf(idParte: int) -> Optional[dict]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Asegúrate que los nombres de las columnas coincidan con ParteImprimirPDF
        # O usa AS para renombrar
        q = """
            SELECT nParte,
                   proyecto,
                   oferta,
                   jefe_equipo,
                   telefono,
                   fecha,
                   contacto_obra,
                   comentarios,
                   firma,
                   idoferta
            FROM tabla_partes_sin_nombre_app
            WHERE nParte = ? \
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
                INSERT INTO tabla_partes_sin_nombre_app(idoferta, pdf, nParte, proyecto, oferta, jefe_equipo, telefono,
                                                        fecha, contacto_obra, comentarios, firma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """
    # Asegúrate que el campo 'firma' en tu modelo coincide con el de la DB
    # parte.signature es el campo de Pydantic, que se mapea a 'firma' en la DB
    # parte.fecha puede necesitar ser convertido a string si la DB lo espera como string,
    # aunque lo ideal es que lo guardes como DATE o DATETIME en la DB.
    values = (
        parte.idoferta, None, parte.nParte, parte.proyecto, parte.oferta, parte.jefe_equipo, parte.telefono,
        parte.fecha, parte.contacto_obra, parte.comentarios, parte.firma  # Asegúrate de usar parte.signature
    )

    try:
        cur.execute(sql_query, values)
        print("Datos insertados correctamente en tabla_partes_sin_nombre_app!")
        # No necesitas commit si autocommit=True en la conexión
        return parte
    except Exception as e:
        print(f"Error al crear el parte (app): {e}")
        raise  # Re-lanza para que la transacción principal pueda hacer rollback


# Recibe la conexión como argumento
def update_ppl(conn, linea: LineaPedidoPost):
    cur = conn.cursor()
    print()
    print()
    print("linea (para update_ppl): ")
    print(linea)
    sql_query = """
                UPDATE ofertas_cli_cabecera
                SET ppcl_IdParte         = ?,
                    ppcl_cantidad        = ?, -- Asegúrate que el campo en DB se llama 'ppcl_cantidad'
                    ppcl_DescripArticulo = ?,
                    ppcl_IdArticulo      = ?
                WHERE ocl_idOferta = ?
                  AND ocl_descrip = ?
                  AND ocl_IdArticulo = ? \
                """
    # **Ajusta los valores para que coincidan con los campos de LineaPedidoPost y las columnas de tu DB**
    values = (
        linea.id_parte,
        linea.unidades_puestas_hoy + linea.cantidad,  # Esto debería ser la cantidad puesta hoy
        linea.descripcion,
        linea.idArticulo,

        linea.id_oferta,
        linea.descripcion,
        linea.idArticulo,
    )

    try:
        cur.execute(sql_query, values)
        print("Linea actualizada correctamente en ofertas_cli_cabecera!")
    except Exception as e:
        print(f"Error al actualizar linea en ofertas_cli_cabecera: {e}")
        raise


# Recibe la conexión como argumento
def handle_pers_partes(conn, parte: ParteRecibidoPost, linea: LineaPedidoPost):
    cur = conn.cursor()
    sql_query = """
                INSERT INTO pers_partes_app(idparte, idoferta, revision, capitulo, titulo, idlinea, idarticulo,
                                            descriparticulo, cantidad, unidadmedida, certificado, fechainsertupdate,
                                            cantidad_total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                """
    # Ajusta los valores para que coincidan con los campos de LineaPedidoPost y las columnas de tu DB
    values = (
        parte.nParte,  # Usa nParte del ParteImprimirPDF
        parte.idoferta,
        1,  # revision, si es un valor fijo
        linea.capitulo,  # del DTO LineaPedidoPost
        "Titulo del Capitulo",  # Si es fijo o viene de alguna parte
        linea.id,  # id de la linea (LineaPedidoPost)
        linea.idArticulo,
        linea.descripcion,
        linea.unidades_puestas_hoy,  # Asumo que es 'cantidad' en pers_partes_app
        linea.medida,  # Asumo que es 'unidadMedida' en pers_partes_app
        linea.ya_certificado,
        "fecha de hoy",
        linea.unidades_totales,
    )

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
            SELECT IdLinea         AS id,
                   DescripArticulo AS descripcion,
                   cantidad        AS cantidad,
                   UnidadMedida    AS unidadMedida
            FROM pers_partes_app
            WHERE idparte = ? \
            """
        cur.execute(q, (parteId,))
        rows = cur.fetchall()

        data = []
        columns = [column[0] for column in cur.description]  # Obtiene los nombres de las columnas (con AS)
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
    output_filename = f"{parte.oferta}_{parte.nParte}.pdf"
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
    columns = [column[0] for column in cur.description]  # Obtiene los nombres de las columnas (con AS)
    for row in rows:
        data.append(dict(zip(columns, row)))
    return data
