import sys
import os
import pyodbc
from datetime import datetime
from dotenv import load_dotenv
from db.database import CONNECTION_STRING

# Add the project root to sys.path to allow imports from db module
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)


load_dotenv()


def get_erp_connection():
    """Establece conexión con la base de datos ERP (Remota)."""
    try:
        conn = pyodbc.connect(CONNECTION_STRING, autocommit=False)
        return conn
    except pyodbc.Error as ex:
        print(f"Error conectando al ERP: {ex}")
        raise


def insertar_parte_en_erp(parte_datos: dict) -> int:
    """
    Inserta datos en el ERP (pers_partes_app) y recupera el ID generado (idParteERP).
    """
    conn = get_erp_connection()
    cursor = conn.cursor()

    try:
        # Se omite idParteERP en el INSERT para que el trigger/identity lo genere.
        query = """
        INSERT INTO pers_partes_app (
            idParteAPP, idOferta, revision, capitulo, titulo, 
            idlinea, idarticulo, descriparticulo, cantidad, 
            unidadmedida, certificado, fechainsertupdate, cantidad_total, pathCapitulo
        )
        OUTPUT INSERTED.idParteERP
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            parte_datos.get("idParteAPP", "123456"),
            parte_datos.get("idOferta", 100),
            parte_datos.get("revision", 1),
            parte_datos.get("capitulo", "CAP-01"),
            parte_datos.get("titulo", "Titulo Test"),
            parte_datos.get("idlinea", 1),
            parte_datos.get("idarticulo", "ART-001"),
            parte_datos.get("descriparticulo", "Articulo de Prueba"),
            parte_datos.get("cantidad", 10.0),
            parte_datos.get("unidadmedida", "mts"),
            parte_datos.get("certificado", 0),
            parte_datos.get("fechainsertupdate", datetime.now()),
            parte_datos.get("cantidad_total", 100.0),
            parte_datos.get("pathCapitulo", "10001000"),
        )

        print("Ejecutando INSERT en pers_partes_app...")
        cursor.execute(query, values)

        row = cursor.fetchone()
        if row:
            nuevo_id = row[0]
            print(f"Inserción exitosa. Nuevo idParteERP: {nuevo_id}")
            conn.commit()
            return nuevo_id
        else:
            # En caso de que no devuelva nada (pero no falle)
            conn.rollback()
            raise Exception("La inserción no devolvió ningún idParteERP.")

    except Exception as e:
        conn.rollback()
        print(f"Error en inserción ERP: {e}")
        # Aquí es donde capturaríamos el error del trigger si falla
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Datos de prueba
    prueba_datos = {
        "idParteAPP": "TEST-UUID-1234",
        "idOferta": 8888,
        "revision": 1,
        "capitulo": "TEST",
        "descriparticulo": "PRUEBA TRIGGER",
        "cantidad": 5.0,
    }

    print("Iniciando prueba de inserción en ERP (pers_partes_app)...")
    try:
        erp_id = insertar_parte_en_erp(prueba_datos)
        print(f"PRUEBA COMPLETADA. ID obtenido: {erp_id}")
    except Exception as e:
        print(f"PRUEBA FALLIDA: {e}")
