from fastapi import APIRouter, HTTPException, status
from dto.ParteDTO import ParteRecibidoPost
from db.db_queries import create_parte
from utils.files import handle_signature

router = APIRouter(prefix="/api/partes", tags=["nuevo"])


@router.post("/crearNUEVO", status_code=status.HTTP_201_CREATED)
def crear_parte_nuevo_flujo(parte: ParteRecibidoPost):
    print(f"Recibida petición para crear parte: {parte.idParteAPP}")

    print("me lo salto porque funciona y quiero probar")
    return True

    try:
        # esto lo tengo que quitar, no hace falta esperar, está como "breakpoint"
        input_id = input(
            f"Introduce el ID ERP para el parte APP {parte.idParteAPP} (NO SIRVE DE NADA, SOLO PARA IR CON CALMA): "
        )
        if not input_id:
            input_id = 0
        else:
            input_id = int(input_id)

        # Procesar firma y crear parte (reutilizando lógica existente)
        handle_signature(parte)
        create_parte(parte)

        return {"message": "OK", "idParteERP": parte.idParteERP}

    except ValueError:
        print("Entrada no válida en terminal.")
        raise HTTPException(
            status_code=500, detail="Error interno: Entrada de terminal inválida"
        )
    except Exception as e:
        print(f"Error al crear parte: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear el parte: {e}")
