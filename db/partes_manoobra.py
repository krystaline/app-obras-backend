from typing import List, Optional


from dotenv import load_dotenv
from db.database import get_db_connection


load_dotenv()


def test_connection():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchall()
    finally:
        conn.close()  # Asegúrate de cerrar la conexión


def get_partes_mo_db(idParteERP: int):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # 1. Obtener los partes cabecera
        sql_partes = """
            SELECT pmo.idParteAPP, pmo.idParteERP, pmo.creation_date as fecha, pmo.estado
            FROM partes_mano_obra pmo
            WHERE pmo.idParteERP = ?
            ORDER BY pmo.creation_date DESC
        """
        cur.execute(sql_partes, (idParteERP,))
        partes_rows = cur.fetchall()

        partes_result = []
        columns_partes = [column[0] for column in cur.description]

        for row in partes_rows:
            parte_dict = dict(zip(columns_partes, row))
            id_parte_mo = parte_dict["idParteAPP"]

            # --- Obtener Actividades (Mano de Obra) ---
            sql_actividades = """
                SELECT mo.accion as nombre
                FROM mano_de_obra mo
                JOIN manos_partes_interm mpi ON mo.idManoObra = mpi.idManoObra
                WHERE mpi.idParteMO = ?
            """
            cur.execute(sql_actividades, (id_parte_mo,))
            actividades_rows = cur.fetchall()
            actividades = [{"nombre": r[0]} for r in actividades_rows]

            # --- Obtener Materiales ---
            sql_materiales = """
                SELECT m.id, m.idArticulo, m.descripcion, m.cantidad, m.lote
                FROM materiales m
                JOIN partes_materiales_interm pmi ON m.id = pmi.idMaterial
                WHERE pmi.idParteMO = ?
            """
            # Nota: Asumo que la tabla de materiales se llama 'materiales' y tiene esos campos.
            # Si los materiales se guardan en otra tabla o si 'Materiales' en ParteMO.py es diferente, ajustar.
            # Viendo ParteMO.py, Materiales tiene: idArticulo, descripcion, cantidad, precio, lote, id.

            cur.execute(sql_materiales, (id_parte_mo,))
            materiales_rows = cur.fetchall()
            cols_mat = [c[0] for c in cur.description]
            materiales = [dict(zip(cols_mat, r)) for r in materiales_rows]

            # Construir el DTO
            dto = {
                "idParteMO": id_parte_mo,
                "fecha": str(parte_dict["fecha"]),  # Convertir a string si es date
                "vehiculo": "Vehiculo Peq.",  # TODO: De donde sale el vehiculo? No lo veo en la tabla pmo. Pongo placeholder o busco si hay tabla vehiculos.
                "actividades": actividades,
                "materiales": materiales,
                "estado": parte_dict["estado"],
            }
            partes_result.append(dto)

        return partes_result

    except Exception as ex:
        print(f"Error al obtener partes MO: {ex}")
        return []
    finally:
        conn.close()
