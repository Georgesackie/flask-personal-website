import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    """Data Access Layer for managing projects database operations"""
    
    def __init__(self, db_path='projects.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                image_file_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_all_projects(self):
        """Retrieve all projects from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        projects = cursor.fetchall()
        
        conn.close()
        return projects
    
    def get_project_by_id(self, project_id):
        """Retrieve a specific project by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = cursor.fetchone()
        
        conn.close()
        return project
    
    def add_project(self, title, description, image_file_name):
        """Add a new project to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects (title, description, image_file_name)
            VALUES (?, ?, ?)
        ''', (title, description, image_file_name))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def update_project(self, project_id, title, description, image_file_name):
        """Update an existing project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE projects 
            SET title = ?, description = ?, image_file_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, description, image_file_name, project_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_project(self, project_id):
        """Delete a project from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def project_exists(self, project_id):
        """Check if a project exists by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM projects WHERE id = ?', (project_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
