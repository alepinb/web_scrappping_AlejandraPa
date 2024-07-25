import requests
from bs4 import BeautifulSoup
from models import db, Quote
from flask import Flask
import logging
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,  # Puedes cambiar a DEBUG para más detalles
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Guardar logs en un archivo
        logging.StreamHandler()           # También mostrar logs en la consola
    ]
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quotes.db'
db.init_app(app)

BASE_URL = "https://quotes.toscrape.com"

# OPTIMIZACIÓN: Crear una sesión global para reutilizar conexiones HTTP
SESSION = requests.Session()

def get_quotes_from_page(url):
    logging.info(f"Requesting URL: {url}")
    try:
        response = SESSION.get(url)  # Usar la sesión global
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        soup = BeautifulSoup(response.text, 'html.parser')
        
        quotes = []

        for quote_div in soup.find_all('div', class_='quote'):
            try:
                text = quote_div.find('span', class_='text').text
                author = quote_div.find('small', class_='author').text
                tags = [tag.text for tag in quote_div.find_all('a', class_='tag')]
                quotes.append({
                    'text': clean_text(text),  # OPTIMIZACIÓN: Limpiar el texto inmediatamente
                    'author': clean_text(author),
                    'tags': [clean_text(tag) for tag in tags]
                })
            except AttributeError as e:
                logging.error(f"Error processing quote div: {e}")
        
        next_page = soup.find('li', class_='next')
        next_page_url = next_page.find('a')['href'] if next_page else None
        logging.info(f"Next page URL: {next_page_url}")
        return quotes, next_page_url
    except requests.RequestException as e:
        logging.error(f"Error requesting URL {url}: {e}")
        return [], None

def get_author_info(author_url):
    logging.info(f"Requesting author info from URL: {BASE_URL + author_url}")
    try:
        response = SESSION.get(BASE_URL + author_url)  # Usar la sesión global
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        author_info = soup.find('div', class_='author-details').text.strip()
        return clean_text(author_info)  # OPTIMIZACIÓN: Limpiar el texto inmediatamente
    except requests.RequestException as e:
        logging.error(f"Error requesting author info URL {BASE_URL + author_url}: {e}")
        return None
    except AttributeError as e:
        logging.error(f"Error processing author info page: {e}")
        return None

def clean_text(text):
    """Limpia el texto eliminando espacios adicionales y saltos de línea."""
    # OPTIMIZACIÓN: Simplificar la función de limpieza
    return ' '.join(text.strip().split())

def is_valid_quote(quote):
    """Valida que una cita tenga texto y autor."""
    return bool(quote['text']) and bool(quote['author'])

def remove_duplicates(quotes):
    """Elimina citas duplicadas basadas en el texto y el autor."""
    seen = set()
    unique_quotes = []
    for quote in quotes:
        identifier = (quote['text'], quote['author'])
        if identifier not in seen:
            seen.add(identifier)
            unique_quotes.append(quote)
    return unique_quotes

def get_all_quotes():
    """Obtiene todas las citas de todas las páginas"""
    all_quotes = []
    url = BASE_URL + '/page/1/'
    
    while url:
        quotes, next_page_url = get_quotes_from_page(url)
        all_quotes.extend(quotes)
        url = BASE_URL + next_page_url if next_page_url else None

    # Eliminar duplicados
    all_quotes = remove_duplicates(all_quotes)
    
    # Usar ThreadPoolExecutor para obtener información de autores concurrentemente
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_quote = {executor.submit(get_author_info, '/author/' + '-'.join(quote['author'].split()) + '/'): quote for quote in all_quotes}
        for future in as_completed(future_to_quote):
            quote = future_to_quote[future]
            try:
                quote['author_info'] = future.result()
            except Exception as exc:
                logging.error(f'Error getting author info for {quote["author"]}: {exc}')
                quote['author_info'] = None
    
    logging.info(f"Retrieved {len(all_quotes)} quotes.")
    return all_quotes

def insert_quotes_to_db(quotes):
    logging.info("Inserting quotes into database.")
    start_time = time.time()
    
    # Usar una única transacción para todas las inserciones
    with app.app_context():
        db.session.begin()
        try:
            for quote in quotes:
                tags = ', '.join(quote['tags'])
                new_quote = Quote(
                    text=quote['text'],
                    author=quote['author'],
                    tags=tags,
                    author_info=quote['author_info']
                )
                db.session.add(new_quote)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error inserting quotes: {e}")
        finally:
            db.session.close()
    
    end_time = time.time()
    logging.info(f"Quotes successfully inserted into the database. Time taken: {end_time - start_time:.2f} seconds")

def fetch_quote():
    try:
        response = SESSION.get(BASE_URL + '/random')  # Usar la sesión global
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        quote_div = soup.find('div', class_='quote')
        text = quote_div.find('span', class_='text').text
        author = quote_div.find('small', class_='author').text
        return {'text': clean_text(text), 'author': clean_text(author)}  # OPTIMIZACIÓN: Limpiar el texto inmediatamente
    except requests.RequestException as e:
        logging.error(f"Error requesting random quote: {e}")
        return None
    except AttributeError as e:
        logging.error(f"Error processing random quote page: {e}")
        return None

def streamlit_app():
    st.title("Quotes App")
    st.write("Esta aplicación muestra citas.")

    if st.button("Obtener una cita aleatoria"):
        quote = fetch_quote()
        if quote:
            st.write(f"Frase: {quote['text']}")
            st.write(f"Autor: {quote['author']}")
        else:
            st.write("No se pudo obtener una cita.")
  
if __name__ == "__main__":
    with app.app_context():
        logging.info("Initializing application context...")
        print("Iniciando el contexto de la aplicación...")
        db.create_all()  # Crear las tablas en la base de datos si no existen
        logging.info("Tables created in the database.")
        print("Tablas creadas en la base de datos.")
        all_quotes = get_all_quotes()
        print(f"Se obtuvieron {len(all_quotes)} citas.")
        insert_quotes_to_db(all_quotes)
        print("Citas insertadas en la base de datos.")
        logging.info("Script finished successfully.")

    # Ejecutar la aplicación de Streamlit
    streamlit_app()
