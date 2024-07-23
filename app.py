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
    next_page_url = next_page.find('a')['href'] if next_page else None 
    
    return quotes, next_page_url

def get_author_info(author_url):
    response = requests.get(BASE_URL + author_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author_info = soup.find('div', class_='author-details').text.strip()
    return author_info

def main():
    all_quotes = []
    url = BASE_URL + '/page/1/'
    
    while url:
        quotes, next_page_url = get_quotes_from_page(url)
        all_quotes.extend(quotes)
        url = BASE_URL + next_page_url if next_page_url else None
    
    for quote in all_quotes:
        author_url = '/author/' + '-'.join(quote['author'].split()) + '/'
        quote['author_info'] = get_author_info(author_url)
    
    # Imprimir o guardar las citas obtenidas
    for quote in all_quotes:
        print(f"Frase: {quote['text']}")
        print(f"Autor: {quote['author']}")
        print(f"Tags: {', '.join(quote['tags'])}")
        print(f"Info Autor: {quote['author_info']}")
        print('-' * 80)

if __name__ == "__main__":
    main()
