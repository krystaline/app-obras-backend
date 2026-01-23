import requests
import json
import datetime


def test_nuevo_endpoint():
    url = "http://localhost:8082/partes/crearNUEVO"

    # Mock data with ID APP 100
    mock_parte = {
        "idOferta": 1,
        "idParteERP": None,  # Should be filled by terminal input
        "idParteAPP": 100,
        "firma": "",
        "lineas": [],
        "comentarios": "Test nuevo flujo",
        "proyecto": "Proyecto Test",
        "oferta": 123,
        "telefono": "555-0101",
        "fecha": str(datetime.date.today()),
        "contactoObra": "Contacto Test",
        "jefeEquipo": "Jefe Test",
        "pdf": "",
    }

    print(f"Sending POST to {url}...")
    print("PLEASE CHECK SERVER TERMINAL FOR INPUT PROMPT!")

    try:
        response = requests.post(
            url, json=mock_parte, timeout=60
        )  # High timeout for manual input
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.json()}")

        if response.status_code == 200:
            print("PASS: Endpoint execution successful")
        else:
            print("FAIL: Endpoint returned error")

    except Exception as e:
        print(f"FAIL: {e}")


if __name__ == "__main__":
    test_nuevo_endpoint()
