import base64
import datetime
from dto.ParteDTO import ParteRecibidoPost, ParteImprimirPDF
import os


def handle_signature(parte: ParteImprimirPDF | ParteRecibidoPost):
    firma = parte.firma
    if not firma:
        return

    if "," in firma:
        header, encoded_data = firma.split(",", 1)
    else:
        encoded_data = firma

    try:
        decoded_image_data = base64.b64decode(encoded_data)
        # Using a relative path 'firmas/' might be fragile if CWD changes, but consistent with original code.
        # Ideally this should use an absolute path from config.
        nombre_firma = (
            str(parte.idParteERP)
            + "_"
            + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            + "_signature.png"
        )

        # Ensure directory exists? Original code assumed it does.
        # import os
        # os.makedirs("firmas", exist_ok=True)
        if not os.path.exists("firmas"):
            os.makedirs("firmas")

        with open("firmas/" + nombre_firma, "wb") as f:
            f.write(decoded_image_data)
            parte.pdf = nombre_firma
            return parte
    except Exception as e:
        print(f"Error al decodificar la firma: {e}")
