from flask import Flask, render_template, request, redirect, url_for, flash
import os
from DAL import DatabaseManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database manager
db_manager = DatabaseManager()

@app.route('/')
def home():
    """Home page route"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.route('/resume')
def resume():
    """Resume page route"""
    return render_template('resume.html')

@app.route('/projects')
def projects():
    """Projects page route"""
    # Get all projects from database
    projects_data = db_manager.get_all_projects()
    return render_template('projects.html', projects=projects_data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with form handling"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')
        message = request.form.get('message', '').strip()
        
        # Basic validation
        errors = []
        
        if not first_name or len(first_name) < 2:
            errors.append('Please enter a valid first name (at least 2 characters)')
        
        if not last_name or len(last_name) < 2:
            errors.append('Please enter a valid last name (at least 2 characters)')
        
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            # Flash errors and return to contact page
            for error in errors:
                flash(error, 'error')
            return render_template('contact.html')
        else:
            # Form is valid, redirect to thank you page
            flash('Thank you for your message!', 'success')
            return redirect(url_for('thank_you'))
    
    return render_template('contact.html')

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    """Add new project page route"""
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        image_file_name = request.form.get('imageFileName', '').strip()
        
        # Basic validation
        errors = []
        
        if not title or len(title) < 3:
            errors.append('Please enter a valid project title (at least 3 characters)')
        
        if not description or len(description) < 10:
            errors.append('Please enter a detailed description (at least 10 characters)')
        
        if not image_file_name:
            errors.append('Please enter an image file name')
        
        if errors:
            # Flash errors and return to add project page
            for error in errors:
                flash(error, 'error')
            return render_template('add_project.html')
        else:
            # Add project to database
            try:
                project_id = db_manager.add_project(title, description, image_file_name)
                flash(f'Project "{title}" added successfully!', 'success')
                return redirect(url_for('projects'))
            except Exception as e:
                flash(f'Error adding project: {str(e)}', 'error')
                return render_template('add_project.html')
    
    return render_template('add_project.html')

@app.route('/thankyou')
def thank_you():
    """Thank you page route"""
    return render_template('thankyou.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return app.send_static_file(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
