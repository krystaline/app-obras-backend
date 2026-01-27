from db.db_queries import update_idParteERP
from fastapi import APIRouter, HTTPException, status
from dto.ParteDTO import ParteRecibidoPost
from db.db_queries import create_parte
from utils.files import handle_signature

router = APIRouter(prefix="/api/partes", tags=["nuevo"])


@router.post("/crearNUEVO", status_code=status.HTTP_201_CREATED)
def crear_parte_nuevo_flujo(parte: ParteRecibidoPost):
    print(f"Recibida petición para crear parte: {parte.idParteAPP}")

    # Interacción por terminal solicitada
    try:
        # cambiar por:
        # cuando yo meto el parte en la bd lo hago sin idParteERP
        #  luego axium mete el parte en su bd o me tira exception
        #   falseo llamada? necesito tiempo para que se actualice
        #  una vez puesto el id, necesito saberlo. ¿Cómo?
        #  y ya el funcionamiento es el que tiene que ser.
        #
        input_id = input(
            f"Introduce el ID ERP para el parte APP {parte.idParteAPP} (Enter para usar 0): "
        )
        if not input_id:
            input_id = 0
        else:
            input_id = int(input_id)

        parte.idParteERP = input_id
        print(f"Asignado idParteERP: {parte.idParteERP}")

        # Procesar firma y crear parte (reutilizando lógica existente)
        handle_signature(parte)
        create_parte(parte)
        update_idParteERP(parte)

        return {"message": "OK", "idParteERP": parte.idParteERP}

    except ValueError:
        print("Entrada no válida en terminal.")
        raise HTTPException(
            status_code=500, detail="Error interno: Entrada de terminal inválida"
        )
    except Exception as e:
        print(f"Error al crear parte: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear el parte: {e}")
