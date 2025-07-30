import msal, requests, base64, os, json
from dotenv import load_dotenv

load_dotenv()


# 'joana@krystaline.es']


def get_access_token():
    """
    Obtiene un token de acceso para la API de Microsoft Graph
    usando el flujo de credenciales de cliente.
    """
    app = msal.ConfidentialClientApplication(
        os.getenv('CLIENT_ID'),
        authority=f"https://login.microsoftonline.com/{os.getenv('TENANT_ID')}",
        client_credential=os.getenv('CLIENT_SECRET')
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception(f"Fallo al adquirir el token: {result.get('error')}, {result.get('error_description')}")


def send_email_with_attachment(file_path, filename):
    """
    Envía un correo electrónico con un archivo adjunto utilizando Microsoft Graph API.
    """
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Leer y codificar el archivo a Base64
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no existe en la ruta: {file_path}")

    with open(file_path, 'rb') as f:
        file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')

    to_recipients_list = []
    recipient_emails_str = os.getenv('RECIPIENT_EMAILS')
    if recipient_emails_str:
        try:
            # Replace single quotes with double quotes for valid JSON
            parsed_emails = json.loads(recipient_emails_str.replace("'", '"'))
            for email in parsed_emails:
                to_recipients_list.append({
                    'emailAddress': {
                        'address': email
                    }
                })
        except json.JSONDecodeError:
            print(f"Error decoding RECIPIENT_EMAILS: {recipient_emails_str}. Ensure it's a valid JSON array string.")
            return  # Or raise an error
    else:
        print("RECIPIENT_EMAILS is not set in the .env file.")
        return  # Or raise an error

    email_data = {
        'message': {
            'subject': os.getenv('SUBJECT'),
            'body': {
                'contentType': 'HTML',  # Puedes usar 'Text' o 'HTML'
                'content': os.getenv('BODY_CONTENT')
            },
            'toRecipients': to_recipients_list,
            'attachments': [
                {
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': filename,
                    'contentType': os.getenv('ATTACHMENT_CONTENT_TYPE'),
                    'contentBytes': encoded_content
                }
            ]
        },
        'saveToSentItems': True  # Guarda una copia en la carpeta de elementos enviados
    }

    # URL para enviar el correo (desde el usuario especificado en SENDER_EMAIL)
    send_mail_url = f'https://graph.microsoft.com/v1.0/users/{os.getenv('SENDER_EMAIL')}/sendMail'

    try:
        response = requests.post(send_mail_url, headers=headers, data=json.dumps(email_data))
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        print("Correo enviado exitosamente!")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el correo: {e}")
        if response is not None:
            print(f"Código de estado: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
