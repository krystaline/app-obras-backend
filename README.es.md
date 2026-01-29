# App Obras Backend

## Descripción General
Este es el repositorio backend para el proyecto **App Obras** de **Krystaline**. Proporciona una API robusta para gestionar partes de trabajo, ofertas, mano de obra y trabajadores.

La aplicación está construida con **FastAPI** e interactúa con una base de datos SQL utilizando **PyODBC**.

## Características
- **Gestión de Partes de Trabajo**: Crear, actualizar y recuperar partes de trabajo.
- **Generación de PDF**: Generar automáticamente informes PDF para los partes de trabajo utilizando plantillas.
- **Ofertas y Líneas**: Gestionar ofertas de proyectos y sus líneas asociadas.
- **Gestión de Mano de Obra**: Realizar seguimiento de horas de trabajo y asignaciones.
- **Gestión de Trabajadores**: Gestionar detalles y asignaciones de los trabajadores.
- **Soporte Multimedia**: Manejar subida de imágenes y asociaciones.

## Tecnologías
- **Lenguaje**: Python 3.9+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Driver de Base de Datos**: [pyodbc](https://github.com/mkleehammer/pyodbc)
- **Procesamiento de PDF**: `pymupdf` (probablemente usado para rellenar/manipular PDFs)
- **Servidor**: Uvicorn

## Requisitos Previos
- Python 3.9 o superior.
- Controlador ODBC para SQL Server (ej. ODBC Driver 17/18 for SQL Server) instalado en el sistema.
- Acceso a la base de datos SQL objetivo.

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url_del_repositorio>
   cd app-obras-backend
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuración de Entorno**
   Crea un archivo `.env` en el directorio raíz. Puedes copiar la estructura de un ejemplo o asegurarte de que contiene las credenciales de base de datos necesarias:
   ```env
   # Variables de ejemplo (ajustar según uso real)
   DB_SERVER=tu_direccion_servidor
   DB_NAME=nombre_de_tu_base_de_datos
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   ```

## Ejecución de la Aplicación

Inicia el servidor de desarrollo con:

```bash
python main.py
```
O directamente vía `uvicorn`:
```bash
uvicorn main:app --host 0.0.0.0 --port 8082 --reload
```

La aplicación estará disponible en `http://localhost:8082`.

## Documentación de la API
La documentación interactiva de la API es generada automáticamente por FastAPI y está disponible en:
- **Swagger UI**: [http://localhost:8082/docs](http://localhost:8082/docs)
- **ReDoc**: [http://localhost:8082/redoc](http://localhost:8082/redoc)

## Estructura del Proyecto
```
app-obras-backend/
├── db/                 # Conexión a base de datos y consultas
├── dependencies.py     # Dependencias de la API (ej. autenticación)
├── dto/                # Objetos de Transferencia de Datos (modelos Pydantic)
├── entities/           # Definiciones de entidades de base de datos
├── routers/            # Manejadores de rutas de la API (endpoints)
│   ├── partes.py       # Endpoints de partes de trabajo
│   ├── ofertas.py      # Endpoints de ofertas
│   ├── workers.py      # Endpoints de trabajadores
│   └── ...
├── utils/              # Funciones de utilidad
├── main.py             # Punto de entrada de la aplicación
└── requirements.txt    # Dependencias del proyecto
```

## Autenticación
La API utiliza autenticación basada en cabeceras. Las peticiones deben incluir cabeceras `User` y `Authorization` válidas:
- `User`: El ID del usuario.
- `Authorization`: `Bearer <token>`

## Licencia
Uso interno exclusivo - Krystaline.
