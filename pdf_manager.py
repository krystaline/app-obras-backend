import fitz  # PyMuPDF is imported as 'fitz'
from pydantic import BaseModel
from datetime import date
from typing import List, Optional

from dto.ParteDTO import ParteImprimirPDF


# Example data to fill the PDF

def fill_parte_obra_pymupdf(template_pdf_path: str, output_pdf_path: str, data: ParteImprimirPDF):
    try:
        # Open the existing PDF document
        doc = fitz.open(template_pdf_path)
        page = doc[0]  # Get the first page (index 0)

        # --- Font and Color setup for PyMuPDF ---
        font_name = "helv"
        font_size_general = 10
        font_size_table = 9
        text_color = (0.15, 0.55, 0.7)

        # --- Fill Header Information ---
        if data.nParte is not None:
            # Ensure it's a string
            page.insert_text(fitz.Point(80, 49), str(data.nParte),
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        if data.proyecto is not None:
            page.insert_text(fitz.Point(80, 64), str(data.proyecto),
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        if data.idoferta is not None:
            # Ensure it's a string
            page.insert_text(fitz.Point(80, 81.5), str(data.idoferta),
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        if data.jefe_equipo is not None:
            page.insert_text(fitz.Point(105, 99.3), data.jefe_equipo,
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        if data.telefono is not None:
            page.insert_text(fitz.Point(80, 114.5), data.telefono,
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        # --- Fill Table Data ---
        table_start_y = 163
        row_height = 19
        col_x_actividades = 60
        col_x_cant = 480
        col_x_unid = 530

        if data.lineas:
            for i, activity in enumerate(data.lineas):
                if i >= 15:
                    break
                current_y = table_start_y + (i * row_height)

                # Actividades column
                # 'descripcion' is the correct attribute for the description
                if activity.descripcion is not None:
                    page.insert_text(fitz.Point(col_x_actividades, current_y), activity.descripcion,
                                     fontsize=font_size_table, fontname=font_name, color=text_color)

                # Cant. column
                # Use 'unidades_puestas_hoy' and convert to string
                if activity.cantidad is not None:
                    page.insert_text(fitz.Point(col_x_cant, current_y), str(activity.cantidad),
                                     fontsize=font_size_table, fontname=font_name, color=text_color)

                # Unid. column
                # Use 'medida' and it should already be a string
                if activity.unidadMedida is not None:
                    page.insert_text(fitz.Point(col_x_unid, current_y), activity.unidadMedida,
                                     fontsize=font_size_table, fontname=font_name, color=text_color)

        # --- Fill "Comentarios:" ---
        comments_rect = fitz.Rect(40, 600, 550, 700)
        if data.comentarios is not None:
            page.insert_textbox(comments_rect, data.comentarios,
                                fontsize=font_size_general, fontname=font_name, color=text_color)

        # --- Fill Other Fields (Fecha, Contacto Obra) ---
        if data.fecha is not None:
            page.insert_text(fitz.Point(100, 750), data.fecha,
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        if data.contacto_obra is not None:
            page.insert_text(fitz.Point(300, 750), data.contacto_obra,
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        # --- Signatures ---
        if data.signature is not None:
            page.insert_text(fitz.Point(100, 770), "Signed by Client",
                             fontsize=font_size_general, fontname=font_name, color=text_color)

        doc.save(output_pdf_path, garbage=3, deflate=True)
        doc.close()
        print(f"PDF filled successfully using PyMuPDF! Output file: {output_pdf_path}")

    except FileNotFoundError:
        print(
            f"Error: Template PDF not found at '{template_pdf_path}'. Please ensure the PDF is in the same directory or provide the full path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
