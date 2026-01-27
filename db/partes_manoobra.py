from typing import List, Optional


from dotenv import load_dotenv
from db.database import get_db_connection
from exceptions import DatabaseError


load_dotenv()


def test_connection():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchall()
    finally:
        conn.close()  # Asegúrate de cerrar la conexión


def get_partes_mo_db(idOferta: int, accessToken: str, user: str):
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # REHACER LA SELECT !?!?!?!?!?!

        # 1. Obtener la cabecera del parte que queremos
        sql_partes = """
            SELECT pmo.idParteAPP, pmo.idParteERP, pmo.creation_date as fecha, pmo.estado
            from partes_mano_obra pmo where pmo.idOferta = ?
            and pmo.idTrabajador = ?
            ORDER BY pmo.creation_date DESC
        """
        cur.execute(sql_partes, (idOferta, user))
        partes_rows = cur.fetchall()
        print(partes_rows)
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
            # Viendo ParteMO.py, Materiales tiene: idArticulo, descripcion, cantidad, lote, id.

            cur.execute(sql_materiales, (id_parte_mo,))
            materiales_rows = cur.fetchall()
            cols_mat = [c[0] for c in cur.description]
            materiales = [dict(zip(cols_mat, r)) for r in materiales_rows]

            # --- Obtener Desplazamientos --- TODO: configurar BD y query hacerlo todo :(
            sql_desplazamientos = """
                SELECT v.id, de_v.vehiculo_id, v.matricula, de_v.kilometros from vehiculos v 
join desplazamientos de_v on v.id = de_v.vehiculo_id 
join desplazamientos_partes_interm dpi on dpi.idDesplazamiento = de_v.id 
where dpi.idParteMO = ?
                
            """
            cur.execute(sql_desplazamientos, (id_parte_mo,))
            desplazamientos_rows = cur.fetchall()
            cols_desp = [c[0] for c in cur.description]
            desplazamientos = [dict(zip(cols_desp, r)) for r in desplazamientos_rows]

            # Formatear string de vehículos
            vehiculos_str = []
            for d in desplazamientos:
                matricula = d.get("matricula") or "Sin Matrícula"
                kms = d.get("kilometros")
                if kms is not None:
                    vehiculos_str.append(f"{matricula} - {kms}km")
                else:
                    vehiculos_str.append(f"{matricula}")

            vehiculo_final = ", ".join(vehiculos_str) if vehiculos_str else ""

            # Construir el DTO
            dto = {
                "idParteMO": id_parte_mo,
                "fecha": str(parte_dict["fecha"]),  # Convertir a string si es date
                "vehiculo": vehiculo_final,
                "actividades": actividades,
                "materiales": materiales,
                "estado": parte_dict["estado"],
            }
            partes_result.append(dto)
        print(partes_result)
        return partes_result

    except Exception as ex:
        print(f"Error al obtener partes MO: {ex}")
        raise DatabaseError(f"Error getting Partes MO: {ex}")
    finally:
        conn.close()
