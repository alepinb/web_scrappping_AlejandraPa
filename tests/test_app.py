import unittest
import sys
import os

# Agregar el directorio raíz al path de importación
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch, MagicMock
from app import get_quotes_from_page, get_author_info, clean_text, is_valid_quote, remove_duplicates, get_all_quotes, insert_quotes_to_db
from models import db, Quote
from flask import Flask

class TestApp(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Configurar la aplicación y la base de datos para pruebas."""
        cls.app = Flask(__name__)
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        cls.app.config['TESTING'] = True
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.init_app(cls.app)
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Limpiar después de las pruebas."""
        db.drop_all()
        cls.app_context.pop()
    
    def setUp(self):
        """Configurar el entorno para cada prueba."""
        self.client = self.app.test_client()

    def test_get_quotes_from_page(self):
        """Prueba la función get_quotes_from_page."""
        with patch('app.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = '''
            <div class="quote">
                <span class="text">"Sample quote"</span>
                <small class="author">John Doe</small>
                <a class="tag">inspirational</a>
            </div>
            <li class="next"><a href="/page/2/">next</a></li>
            '''
            mock_get.return_value = mock_response
            
            quotes, next_page_url = get_quotes_from_page('https://quotes.toscrape.com/page/1/')
            
            self.assertEqual(len(quotes), 1)
            self.assertEqual(quotes[0]['text'], '"Sample quote"')
            self.assertEqual(quotes[0]['author'], 'John Doe')
            self.assertEqual(quotes[0]['tags'], ['inspirational'])
            self.assertEqual(next_page_url, '/page/2/')

    def test_get_author_info(self):
        """Prueba la función get_author_info."""
        with patch('app.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = '<div class="author-details">Author bio</div>'
            mock_get.return_value = mock_response
            
            author_info = get_author_info('/author/john-doe/')
            
            self.assertEqual(author_info, 'Author bio')

    def test_clean_text(self):
        """Prueba la función clean_text."""
        dirty_text = '  Hello World! \n'
        clean = clean_text(dirty_text)
        self.assertEqual(clean, 'Hello World!')

    def test_is_valid_quote(self):
        """Prueba la función is_valid_quote."""
        valid_quote = {'text': 'Some quote', 'author': 'Some author'}
        invalid_quote = {'text': '', 'author': 'Some author'}
        
        self.assertTrue(is_valid_quote(valid_quote))
        self.assertFalse(is_valid_quote(invalid_quote))

    def test_remove_duplicates(self):
        """Prueba la función remove_duplicates."""
        quotes = [
            {'text': 'Quote 1', 'author': 'Author 1'},
            {'text': 'Quote 2', 'author': 'Author 2'},
            {'text': 'Quote 1', 'author': 'Author 1'}
        ]
        unique_quotes = remove_duplicates(quotes)
        self.assertEqual(len(unique_quotes), 2)

    @patch('app.get_quotes_from_page')
    @patch('app.get_author_info')
    def test_get_all_quotes(self, mock_get_author_info, mock_get_quotes_from_page):
        """Prueba la función get_all_quotes."""
        mock_get_quotes_from_page.return_value = (
            [{'text': 'Quote', 'author': 'Author', 'tags': ['tag']}], '/page/2/'
        )
        mock_get_author_info.return_value = 'Author info'
        
        quotes = get_all_quotes()
        self.assertGreater(len(quotes), 0)
        self.assertEqual(quotes[0]['author_info'], 'Author info')

    @patch('app.db.session')
    def test_insert_quotes_to_db(self, mock_session):
        """Prueba la función insert_quotes_to_db."""
        quotes = [
            {'text': 'Quote', 'author': 'Author', 'tags': ['tag'], 'author_info': 'Info'}
        ]
        insert_quotes_to_db(quotes)
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
