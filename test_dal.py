import unittest
import os
import tempfile
import sqlite3
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from DAL import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for the DatabaseManager class"""
    
    def setUp(self):
        """Set up test database"""
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.db_path)
        
    def tearDown(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_database_initialization(self):
        """Test that database initializes correctly"""
        # Check if the database file was created
        self.assertTrue(os.path.exists(self.db_path))
        
        # Check if the projects table was created
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        table_exists = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(table_exists)
        self.assertEqual(table_exists[0], 'projects')
    
    def test_add_project(self):
        """Test adding a new project"""
        title = "Test Project"
        description = "This is a test project description"
        image_file_name = "test_image.jpg"
        
        project_id = self.db_manager.add_project(title, description, image_file_name)
        
        # Check that project was added and ID was returned
        self.assertIsInstance(project_id, int)
        self.assertGreater(project_id, 0)
        
        # Verify the project was actually added
        project = self.db_manager.get_project_by_id(project_id)
        self.assertIsNotNone(project)
        self.assertEqual(project[1], title)  # title is at index 1
        self.assertEqual(project[2], description)  # description is at index 2
        self.assertEqual(project[3], image_file_name)  # image_file_name is at index 3
    
    def test_get_all_projects(self):
        """Test retrieving all projects"""
        # Add some test projects
        self.db_manager.add_project("Project 1", "Description 1", "image1.jpg")
        self.db_manager.add_project("Project 2", "Description 2", "image2.jpg")
        self.db_manager.add_project("Project 3", "Description 3", "image3.jpg")
        
        # Get all projects
        projects = self.db_manager.get_all_projects()
        
        # Check that we got all projects
        self.assertEqual(len(projects), 3)
        
        # Check that projects are ordered by created_at DESC (newest first)
        self.assertEqual(projects[0][1], "Project 3")  # Most recent
        self.assertEqual(projects[1][1], "Project 2")
        self.assertEqual(projects[2][1], "Project 1")  # Oldest
    
    def test_get_project_by_id(self):
        """Test retrieving a specific project by ID"""
        # Add a test project
        project_id = self.db_manager.add_project("Test Project", "Test Description", "test.jpg")
        
        # Retrieve the project
        project = self.db_manager.get_project_by_id(project_id)
        
        # Check that the correct project was retrieved
        self.assertIsNotNone(project)
        self.assertEqual(project[0], project_id)  # ID
        self.assertEqual(project[1], "Test Project")  # title
        self.assertEqual(project[2], "Test Description")  # description
        self.assertEqual(project[3], "test.jpg")  # image_file_name
    
    def test_get_nonexistent_project(self):
        """Test retrieving a project that doesn't exist"""
        project = self.db_manager.get_project_by_id(999)
        self.assertIsNone(project)
    
    def test_update_project(self):
        """Test updating an existing project"""
        # Add a test project
        project_id = self.db_manager.add_project("Original Title", "Original Description", "original.jpg")
        
        # Update the project
        new_title = "Updated Title"
        new_description = "Updated Description"
        new_image = "updated.jpg"
        
        success = self.db_manager.update_project(project_id, new_title, new_description, new_image)
        
        # Check that update was successful
        self.assertTrue(success)
        
        # Verify the project was updated
        project = self.db_manager.get_project_by_id(project_id)
        self.assertEqual(project[1], new_title)
        self.assertEqual(project[2], new_description)
        self.assertEqual(project[3], new_image)
    
    def test_update_nonexistent_project(self):
        """Test updating a project that doesn't exist"""
        success = self.db_manager.update_project(999, "Title", "Description", "image.jpg")
        self.assertFalse(success)
    
    def test_delete_project(self):
        """Test deleting a project"""
        # Add a test project
        project_id = self.db_manager.add_project("To Delete", "Description", "image.jpg")
        
        # Verify project exists
        project = self.db_manager.get_project_by_id(project_id)
        self.assertIsNotNone(project)
        
        # Delete the project
        success = self.db_manager.delete_project(project_id)
        
        # Check that deletion was successful
        self.assertTrue(success)
        
        # Verify project no longer exists
        project = self.db_manager.get_project_by_id(project_id)
        self.assertIsNone(project)
    
    def test_delete_nonexistent_project(self):
        """Test deleting a project that doesn't exist"""
        success = self.db_manager.delete_project(999)
        self.assertFalse(success)
    
    def test_project_exists(self):
        """Test checking if a project exists"""
        # Add a test project
        project_id = self.db_manager.add_project("Test Project", "Description", "image.jpg")
        
        # Check that project exists
        exists = self.db_manager.project_exists(project_id)
        self.assertTrue(exists)
        
        # Check that non-existent project doesn't exist
        exists = self.db_manager.project_exists(999)
        self.assertFalse(exists)
    
    def test_database_connection(self):
        """Test database connection"""
        conn = self.db_manager.get_connection()
        self.assertIsNotNone(conn)
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()
    
    def test_multiple_operations(self):
        """Test multiple database operations in sequence"""
        # Add multiple projects
        id1 = self.db_manager.add_project("Project 1", "Description 1", "img1.jpg")
        id2 = self.db_manager.add_project("Project 2", "Description 2", "img2.jpg")
        
        # Update one project
        self.db_manager.update_project(id1, "Updated Project 1", "Updated Description 1", "updated_img1.jpg")
        
        # Delete one project
        self.db_manager.delete_project(id2)
        
        # Check final state
        projects = self.db_manager.get_all_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0][1], "Updated Project 1")
        
        # Check that deleted project doesn't exist
        self.assertFalse(self.db_manager.project_exists(id2))
        self.assertTrue(self.db_manager.project_exists(id1))

if __name__ == '__main__':
    unittest.main()
