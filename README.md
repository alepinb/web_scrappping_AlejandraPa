# Quotes App

## Descripción
Quotes App es una aplicación para obtener, procesar y mostrar citas célebres desde [Quotes to Scrape](https://quotes.toscrape.com). Utiliza Flask para la lógica del backend, SQLAlchemy para la base de datos, BeautifulSoup para el scraping web y Streamlit para la interfaz de usuario.

## Instalación

### Requisitos
- Python 3.6 o superior
- pip (gestor de paquetes de Python)

Clonar el repositorio
```bash
git clone https://github.com/tuusuario/quotes-app.git
cd quotes-app

### Crear y activar un entorno virtual
python -m venv env
source env/bin/activate  # En Windows usa: env\Scripts\activate

### Instalar las dependencias
pip install -r requirements.txt

### Configurar la base de datos
flask db init
flask db migrate -m "Inicializar base de datos"
flask db upgrade

### Ejecutar la aplicación
python app.py

Esto:
Inicializará el contexto de la aplicación.
Creará las tablas en la base de datos si no existen.
Obtendrá todas las citas de la web y las insertará en la base de datos.

### Usar la aplicación Streamlit
streamlit run app.py

### Estructura del Proyecto
quotes-app/
├── app.py             # Archivo principal de la aplicación
├── models.py          # Modelos de la base de datos
├── tests_unitarios.py # Pruebas unitarias
├── requirements.txt   # Dependencias del proyecto
├── app.log            # Archivo de log de la aplicación
└── README.md          # Este archivo

### Autores
Alejandra Piñango - Desarrollador Principal - (https://github.com/alepinb)

### Recursos Adicionales
Documentación de Flask
Documentación de SQLAlchemy
Documentación de BeautifulSoup
Documentación de Streamlit

### Explicación del Código

#### 1. **Configuración de logging**

Se establece la configuración de logging para registrar eventos importantes y errores en un archivo y en la consola.

#### 2. **Aplicación Flask**

Se configura la aplicación Flask y la base de datos utilizando SQLAlchemy.

#### 3. **Scraping con BeautifulSoup**

Se utilizan funciones para obtener citas y la información de los autores desde la web de manera concurrente utilizando `ThreadPoolExecutor`.

#### 4. **Optimización de la Sesión HTTP**

Se utiliza una sesión global de `requests` para reutilizar las conexiones HTTP y mejorar el rendimiento.

#### 5. **Limpieza y Validación de Datos**

Funciones para limpiar el texto, validar citas y eliminar duplicados.

#### 6. **Interfaz de Usuario con Streamlit**

Una interfaz sencilla para mostrar citas aleatorias mediante Streamlit.
