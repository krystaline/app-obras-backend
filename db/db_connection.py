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
# conn = psycopg2.connect(database=os.getenv("PGDATABSE"),
#                         user=os.getenv("PGUSER"),
#                         host=os.getenv("PGHOST"),
#                         password=os.getenv("PGPASSWORD"),
#                         port=os.getenv('PGPORT'))
#


SQLS_NATIVE = "{ODBC Driver 18 for SQL server}"
SQLERP_HOST = "192.168.0.21"
SQLERP_DB = "KRYSTALINE"
SQLERP_PORT = 61310
SQLERP_UID = "sa"
SQLERP_PWD = "03071997aA"

connection_string = f'DRIVER={SQLS_NATIVE};' \
                    f'SERVER={SQLERP_HOST},{SQLERP_PORT};' \
                    f'DATABASE={SQLERP_DB};' \
                    f'UID={SQLERP_UID};' \
                    f'PWD={SQLERP_PWD};' \
                    f'TrustServerCertificate=Yes;'
conn = pyodbc.connect(connection_string, autocommit=True)


def get_all_partes():
    return []


def get_lineas():
    try:
        cursor = conn.cursor()
        sql_query = """
                    select ocl.IdOferta              as ocl_IdOferta,
                           ocl.idlinea               as ocl_idlinea,
                           ocl.revision              as ocl_revision,
                           max(occ.SerieOferta)      as occ_SerieOferta,
                           max(occ.revision)         as occ_revision,
                           max(occ.idempresa)        as occ_idempresa,
                           max(occ.añonum)           as occ_añonum,
                           max(occ.numoferta)        as occ_numoferta,
                           max(occ.descrip)          as occ_descrip,
                           max(occ.idestado)         as occ_idestado,
                           max(occ.idproyecto)       as occ_idproyecto,
                           max(cd.idcliente)         as cd_idcliente,
                           max(cd.Cliente)           as cd_Cliente,
                           ocl.IdArticulo            as ocl_IdArticulo,
                           max(ocl.Descrip)          as ocl_Descrip,
                           max(ocl.Cantidad)         as ocl_Cantidad,
                           max(ocl.PesoNeto)         as ocl_PesoNeto,
                           max(ocl.NumBultos)        as ocl_NumBultos,
                           max(ocl.UnidadesPres)     as ocl_UnidadesPres,
                           ppcl.IdParte              as ppcl_IdParte,
                           max(ppcl.Capitulo)        as ppcl_Capitulo,
                           max(ppcl.IdArticulo)      as ppcl_IdArticulo,
                           max(ppcl.DescripArticulo) as ppcl_DescripArticulo,
                           max(ppcl.cantidad)        as ppcl_cantidad,
                           max(ppcl.UnidadMedida)    as ppcl_UnidadMedida, isnull (max(cast (ppcl.Certificado as int)), 0) as ppcl_Certificado
                    from
                        ofertas_cli_cabecera occ
                        inner join
                        Clientes_Datos cd
                    on
                        occ.IdCliente = cd.IdCliente
                        inner JOIN
                        Ofertas_Cli_Lineas ocl
                        on
                        occ.IdOferta = ocl.IdOferta
                        left outer JOIN
                        pers_Partes_Certificacion_Lineas ppcl
                        on
                        (ocl.IdOferta = ppcl.IdOferta and ocl.IdArticulo = ppcl.IdArticulo) or ppcl.IdOferta is null
                    group by
                        ocl.IdOferta, ocl.idlinea, ocl.revision, ocl.IdArticulo, ppcl.IdParte, ppcl.IdArticulo
                    order BY
                        ppcl.IdParte, isnull (max(cast (ppcl.Certificado as int)), 0)
                        desc, ocl.IdOferta, ocl.idlinea, ocl.revision
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
                    SELECT cast(occ.idOferta as int) as idOferta,
                           occ.Fecha                 as fecha,
                           cd.Cliente                as cliente,
                           occ.idProyecto,
                           occ.Descrip               as descripcion,
                           occ.Observaciones         as observaciones,
                           status = 'activa'
                    FROM ofertas_cli_cabecera occ \
                             join Clientes_Datos cd on occ.idCliente = cd.IdCliente
                    where idProyecto is not null
                      AND occ.idCliente <> '00381'
                    order by occ.idProyecto desc \
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
    try:
        cursor = conn.cursor()
        sql_query = """
                    select ocl.IdOferta              as ocl_IdOferta, \
                           ocl.idlinea               as ocl_idlinea, \
                           ocl.revision              as ocl_revision, \
                           max(occ.SerieOferta)      as occ_SerieOferta, \
                           max(occ.revision)         as occ_revision, \
                           max(occ.idempresa)        as occ_idempresa, \
                           max(occ.añonum)           as occ_añonum, \
                           max(occ.numoferta)        as occ_numoferta, \
                           max(occ.descrip)          as occ_descrip, \
                           max(occ.idestado)         as occ_idestado, \
                           max(occ.idproyecto)       as occ_idproyecto, \
                           max(cd.idcliente)         as cd_idcliente, \
                           max(cd.Cliente)           as cd_Cliente, \
                           ocl.IdArticulo            as ocl_IdArticulo, \
                           max(ocl.Descrip)          as ocl_Descrip, \
                           max(ocl.Cantidad)         as ocl_Cantidad, \
                           max(ocl.PesoNeto)         as ocl_PesoNeto, \
                           max(ocl.NumBultos)        as ocl_NumBultos, \
                           max(ocl.UnidadesPres)     as ocl_UnidadesPres, \
                           ppcl.IdParte              as ppcl_IdParte, \
                           max(ppcl.Capitulo)        as ppcl_Capitulo, \
                           max(ppcl.IdArticulo)      as ppcl_IdArticulo, \
                           max(ppcl.DescripArticulo) as ppcl_DescripArticulo, \
                           max(ppcl.cantidad)        as ppcl_cantidad, \
                           max(ppcl.UnidadMedida)    as ppcl_UnidadMedida, isnull (max(cast (ppcl.Certificado as int)), 0) as ppcl_Certificado
                    from
                        ofertas_cli_cabecera occ
                        inner join
                        Clientes_Datos cd
                    on
                        occ.IdCliente = cd.IdCliente
                        inner JOIN
                        Ofertas_Cli_Lineas ocl
                        on
                        occ.IdOferta = ocl.IdOferta
                        left outer JOIN
                        pers_Partes_Certificacion_Lineas ppcl
                        on
                        (ocl.IdOferta = ppcl.IdOferta and ocl.IdArticulo = ppcl.IdArticulo) or ppcl.IdOferta is null
                    group by
                        ocl.IdOferta, ocl.idlinea, ocl.revision, ocl.IdArticulo, ppcl.IdParte, ppcl.IdArticulo
                    order BY
                        ppcl.IdParte, isnull (max(cast (ppcl.Certificado as int)), 0) \
                        desc, ocl.IdOferta, ocl.idlinea, ocl.revision \
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


def get_num_parte():
    cursor = conn.cursor()
    sql_query = """
                select MAX(ppcl.IdParte) from pers_Partes_Certificacion_Lineas ppcl 
                """
    cursor.execute(sql_query)
    return cursor.fetchval()
