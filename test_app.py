import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db_manager

class TestFlaskApp(unittest.TestCase):
    """Test cases for the Flask application"""
    
    def setUp(self):
        """Set up test client and configure testing"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create a temporary database for testing
        self.db_fd, self.app.config['DATABASE'] = tempfile.mkstemp()
        
    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])
    
    def test_home_route(self):
        """Test the home page route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_about_route(self):
        """Test the about page route"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_resume_route(self):
        """Test the resume page route"""
        response = self.client.get('/resume')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_projects_route(self):
        """Test the projects page route"""
        response = self.client.get('/projects')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_contact_get_route(self):
        """Test the contact page GET route"""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_contact_post_valid_data(self):
        """Test contact form with valid data"""
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'confirmPassword': 'password123',
            'message': 'This is a test message'
        }
        response = self.client.post('/contact', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message!', response.data)
    
    def test_contact_post_invalid_data(self):
        """Test contact form with invalid data"""
        data = {
            'firstName': 'J',  # Too short
            'lastName': 'D',   # Too short
            'email': 'invalid-email',  # Invalid email
            'password': '123',  # Too short
            'confirmPassword': '456',  # Doesn't match
            'message': 'Test'  # Too short
        }
        response = self.client.post('/contact', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid first name', response.data)
    
    def test_add_project_get_route(self):
        """Test the add project page GET route"""
        response = self.client.get('/add_project')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    @patch('app.db_manager.add_project')
    def test_add_project_post_valid_data(self, mock_add_project):
        """Test add project form with valid data"""
        mock_add_project.return_value = 1
        
        data = {
            'title': 'Test Project',
            'description': 'This is a detailed test project description',
            'imageFileName': 'test_image.jpg'
        }
        response = self.client.post('/add_project', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_add_project.assert_called_once_with('Test Project', 'This is a detailed test project description', 'test_image.jpg')
    
    def test_add_project_post_invalid_data(self):
        """Test add project form with invalid data"""
        data = {
            'title': 'TP',  # Too short
            'description': 'Short',  # Too short
            'imageFileName': ''  # Empty
        }
        response = self.client.post('/add_project', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid project title', response.data)
    
    def test_thank_you_route(self):
        """Test the thank you page route"""
        response = self.client.get('/thankyou')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_static_file_route(self):
        """Test serving static files"""
        # This will test the static file serving route
        response = self.client.get('/static/css/styles.css')
        # The file might not exist, but the route should be accessible
        self.assertIn(response.status_code, [200, 404])
    
    def test_app_initialization(self):
        """Test that the app initializes correctly"""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    
    def test_database_manager_initialization(self):
        """Test that the database manager initializes correctly"""
        self.assertIsNotNone(db_manager)
        self.assertEqual(db_manager.db_path, 'projects.db')

if __name__ == '__main__':
    unittest.main()
