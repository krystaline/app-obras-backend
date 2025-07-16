import msal, requests, base64, os, json

TENANT_ID = 'd0fbdbb8-b41b-4c4a-af4a-1ef369dcccaa'
CLIENT_ID = '7562f532-b3df-4051-841b-a5c6bbf51300'
CLIENT_SECRET = 'maG8Q~Vvuen5d5kYPqH.Gsb_DfnHe8BzNk43hc-B'  # mailer_secret

SENDER_EMAIL = 'obras_noresponder@krystaline.es'  # Correo desde el que se enviará (debe tener permisos)
SUBJECT = 'PDF Parte obra generado'
BODY_CONTENT = 'Este correo ha sido generado y enviado automáticamente.\n No responder.'
ATTACHMENT_CONTENT_TYPE = 'application/pdf'  # Tipo MIME del archivo (ej. 'text/plain', 'image/png', 'application/pdf')

RECIPIENT_EMAILS = ['alessandro.volta@krystaline.es', 'paulabrotonsrequena15@gmail.com']


# 'joana@krystaline.es']


def get_access_token():
    """
    Obtiene un token de acceso para la API de Microsoft Graph
    usando el flujo de credenciales de cliente.
    """
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
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
    for email in RECIPIENT_EMAILS:
        to_recipients_list.append({
            'emailAddress': {
                'address': email
            }
        })
    email_data = {
        'message': {
            'subject': SUBJECT,
            'body': {
                'contentType': 'HTML',  # Puedes usar 'Text' o 'HTML'
                'content': BODY_CONTENT
            },
            'toRecipients': to_recipients_list,
            'attachments': [
                {
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': filename,
                    'contentType': ATTACHMENT_CONTENT_TYPE,
                    'contentBytes': encoded_content
                }
            ]
        },
        'saveToSentItems': True  # Guarda una copia en la carpeta de elementos enviados
    }

    # URL para enviar el correo (desde el usuario especificado en SENDER_EMAIL)
    send_mail_url = f'https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail'

    try:
        response = requests.post(send_mail_url, headers=headers, data=json.dumps(email_data))
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        print("Correo enviado exitosamente!")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el correo: {e}")
        if response is not None:
            print(f"Código de estado: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
