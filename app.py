import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"

def get_quotes_from_page(url):
    response = requests.get(url)   #se hace una petición HTTP GET a la URL proporcionada usando la biblioteca requests. La respuesta contiene el código HTML de la página solicitada.
    soup = BeautifulSoup(response.text, 'html.parser')   #Analiza el contenido HTML obtenido y crea un objeto BeautifulSoup que se puede usar para buscar y extraer datos del HTML de manera eficiente
    
    quotes = [] #Esta lista se usará para almacenar diccionarios que contienen información sobre cada cita encontrada en la página.

    for quote_div in soup.find_all('div', class_='quote'):    #encuentra todos los elementos <div> que tienen la clase quote. En cada iteración, el elemento se almacena en la variable quote_div.
        text = quote_div.find('span', class_='text').text     #busca el primer elemento <span> con la clase text dentro del quote_div. .text extrae el contenido de texto de este elemento <span>, que es la cita en sí.
        author = quote_div.find('small', class_='author').text #busca el primer elemento <small> con la clase author. .text saca el contenido de texto de este elemento <small>
        tags = [tag.text for tag in quote_div.find_all('a', class_='tag')]  #busca todos los elementos <a> con la clase tag dentro del quote_div. La expresión [tag.text for tag in quote_div.find_all('a', class_='tag')] es una lista por comprensión que itera sobre cada elemento <a> encontrado y extrae su contenido de texto (tag.text).
        quotes.append({
            'text': text,
            'author': author,
            'tags': tags
        })

    """El fragmento de código de arriba recorre todas las citas en una página web (representadas por elementos <div> con la clase quote), 
extrae el texto de la cita, el nombre del autor y las etiquetas asociadas, y almacena esta información en una lista de diccionarios. 
Cada diccionario en la lista quotes contiene la información completa de una cita"""
    
    next_page = soup.find('li', class_='next')   #buscar el primer elemento <li> que tenga la clase next en el documento HTML analizado. Este elemento <li> generalmente contiene el enlace a la siguiente página de citas.
    next_page_url = next_page.find('a')['href'] if next_page else None  #busca el primer elemento <a> dentro del elemento <li> encontrado previamente (next_page). Este elemento <a> representa el enlace a la siguiente página. 
                                                                        #['href'] accede al atributo href del elemento <a>, que contiene la URL relativa de la siguiente página.
    return quotes, next_page_url

def get_author_info(author_url):
    response = requests.get(BASE_URL + author_url)  #Realiza una solicitud HTTP GET a la URL completa para obtener la página web del autor.
    soup = BeautifulSoup(response.text, 'html.parser')    #Utiliza BeautifulSoup para analizar el contenido HTML de la respuesta. response.text contiene el HTML de la página, y 'html.parser' es el analizador que se usa para interpretar el HTML.
    author_info = soup.find('div', class_='author-details').text.strip()  #Busca un elemento <div> en el HTML con la clase 'author-details', que se supone contiene la información del autor.
                                                                          #.text.strip(): Extrae el texto del elemento <div> y elimina los espacios en blanco al principio y al final del texto.
    return author_info

def clean_text(text):
    """Limpia el texto eliminando espacios adicionales y saltos de línea."""
    return text.strip().replace('\n', ' ').replace('\r', '')

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


def main():
    all_quotes = []
    url = BASE_URL + '/page/1/'
    
    while url:
        quotes, next_page_url = get_quotes_from_page(url)   #Llama a la función get_quotes_from_page pasando la URL actual. Esta función debería devolver dos cosas: quotes: Una lista de citas obtenidas de la página actual. y next_page_url: La URL de la siguiente página, si existe.
        all_quotes.extend(quotes)           #Agrega las citas obtenidas a la lista all_quotes.

        # Limpiar y validar citas
        for quote in quotes:
            quote['text'] = clean_text(quote['text'])
            quote['author'] = clean_text(quote['author'])
            quote['tags'] = [clean_text(tag) for tag in quote['tags']]
            if is_valid_quote(quote):
                all_quotes.append(quote)


        url = BASE_URL + next_page_url if next_page_url else None

    # Eliminar duplicados
    all_quotes = remove_duplicates(all_quotes)
    
    for quote in all_quotes:
        author_url = '/author/' + '-'.join(quote['author'].split()) + '/' #Construye la URL del autor. quote['author']: Obtiene el nombre del autor de la cita. quote['author'].split(): Divide el nombre del autor en una lista de palabras (suponiendo que el nombre está separado por espacios).
                                                                          # '-'.join(...): Une las palabras con guiones (-) para formar la parte de la URL correspondiente al autor.
                                                                          # Finalmente, se añade '/author/' al principio y '/ al final para construir la URL completa del autor.
        quote['author_info'] = get_author_info(author_url)                # Llama a la función get_author_info con la URL del autor y guarda la información del autor en el campo 'author_info' de la cita.
    
    # Imprimir o guardar las citas obtenidas
    for quote in all_quotes:
        print(f"Frase: {quote['text']}")
        print(f"Autor: {quote['author']}")
        print(f"Tags: {', '.join(quote['tags'])}")
        print(f"Info Autor: {quote['author_info']}")
        print('-' * 80)

if __name__ == "__main__":
    main()
