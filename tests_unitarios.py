import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
from flask import Flask
from models import db, Quote

# Importa las funciones a probar
from app import (
    get_quotes_from_page,
    get_author_info,
    clean_text,
    is_valid_quote,
    remove_duplicates,
    fetch_quote,
    BASE_URL,
    SESSION
)

class TestQuoteScraper(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_clean_text(self):
        """Verifica que la función clean_text elimine correctamente los espacios extra y los saltos de línea."""
        self.assertEqual(clean_text("  Hello,   World!  "), "Hello, World!")
        self.assertEqual(clean_text("\n\nTest\t\tString\n"), "Test String")

    def test_is_valid_quote(self):
        """Comprueba que la función is_valid_quote identifique correctamente las citas válidas e inválidas."""
        self.assertTrue(is_valid_quote({'text': 'Test', 'author': 'Author'}))
        self.assertFalse(is_valid_quote({'text': '', 'author': 'Author'}))
        self.assertFalse(is_valid_quote({'text': 'Test', 'author': ''}))

    def test_remove_duplicates(self):
        """Asegura que la función remove_duplicates elimine correctamente las citas duplicadas."""
        quotes = [
            {'text': 'Quote1', 'author': 'Author1'},
            {'text': 'Quote1', 'author': 'Author1'},
            {'text': 'Quote2', 'author': 'Author2'}
        ]
        result = remove_duplicates(quotes)
        self.assertEqual(len(result), 2)
        self.assertIn({'text': 'Quote1', 'author': 'Author1'}, result)
        self.assertIn({'text': 'Quote2', 'author': 'Author2'}, result)

    @patch('app.SESSION.get')
    def test_get_quotes_from_page(self, mock_get):
        """Usa un mock para simular la respuesta de una página web y verifica que get_quotes_from_page extraiga correctamente las citas y la URL de la siguiente página."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <div class="quote">
                <span class="text">Quote1</span>
                <small class="author">Author1</small>
                <a class="tag">Tag1</a>
                <a class="tag">Tag2</a>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
        </html>
        '''
        mock_get.return_value = mock_response

        quotes, next_page = get_quotes_from_page(BASE_URL)
        
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]['text'], 'Quote1')
        self.assertEqual(quotes[0]['author'], 'Author1')
        self.assertEqual(quotes[0]['tags'], ['Tag1', 'Tag2'])
        self.assertEqual(next_page, '/page/2/')

    @patch('app.SESSION.get')
    def test_get_author_info(self, mock_get):
        """usa un mock para verificar que get_author_info extraiga correctamente la información del autor."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <div class="author-details">Author biography</div>
        </html>
        '''
        mock_get.return_value = mock_response

        author_info = get_author_info('/author/test-author/')
        
        self.assertEqual(author_info, 'Author biography')

    @patch('app.SESSION.get')
    def test_fetch_quote(self, mock_get):
        """ Verifica que fetch_quote obtenga correctamente una cita aleatoria."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <div class="quote">
                <span class="text">Random Quote</span>
                <small class="author">Random Author</small>
            </div>
        </html>
        '''
        mock_get.return_value = mock_response

        quote = fetch_quote()
        
        self.assertEqual(quote['text'], 'Random Quote')
        self.assertEqual(quote['author'], 'Random Author')

if __name__ == '__main__':
    unittest.main()