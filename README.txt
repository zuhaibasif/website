Horizon Travels - Travel Booking Website
=====================================

This is a Flask-based travel booking website that allows users to book various types of travel (air, coach, train) across the UK.

Prerequisites
------------
1. Python 3.8 or higher
2. pip (Python package installer)
3. A modern web browser (Chrome, Firefox, Safari, or Edge)

Installation
-----------
1. Open a terminal/command prompt
2. Navigate to the project directory
3. Create a virtual environment (recommended):
   - Windows: python -m venv venv
   - Mac/Linux: python3 -m venv venv
4. Activate the virtual environment:
   - Windows: venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate
5. Install required packages:
   pip install -r requirements.txt

Running the Application
---------------------
1. Make sure your virtual environment is activated
2. Run the Flask application:
   - Windows: python app.py
   - Mac/Linux: python3 app.py
3. Open your web browser and go to: http://localhost:5000

Features
--------
- User registration and login
- Browse travel destinations
- Book different types of travel (air, coach, train)
- View booking history
- Admin dashboard for managing bookings
- Generate reports and analytics

Architecture Decisions
--------------------
1. Framework Choice:
   - Flask was chosen for its lightweight nature and flexibility
   - Simple routing system and minimal boilerplate code
   - Easy integration with SQLAlchemy for database operations

2. Database:
   - MySQL for robust relational data storage
   - SQLAlchemy ORM for database abstraction and security
   - Normalized schema design to prevent data redundancy

3. Security Implementation:
   - Session-based authentication with 7-day expiration
   - Password hashing using Werkzeug's security functions
   - Custom decorators for route protection (login_required, admin_required)
   - CSRF protection through Flask's built-in features

4. Frontend Architecture:
   - Server-side rendering using Jinja2 templates
   - Separate CSS files for different themes (styles.css, styles-jalebi.css)
   - Minimal JavaScript usage for enhanced user experience

Trade-offs Made
-------------
1. Server-Side Rendering vs Single Page Application:
   - Chose server-side rendering for:
     * Faster initial page load
     * Better SEO capabilities
     * Simpler development process
   - Trade-off: Less dynamic user experience compared to SPAs

2. Session-Based vs JWT Authentication:
   - Implemented session-based auth for:
     * Simpler implementation
     * Better security for web-only applications
   - Trade-off: More server resources used for session storage

3. MySQL vs NoSQL:
   - Selected MySQL for:
     * Strong data consistency
     * Complex querying capabilities
     * Structured booking and user data
   - Trade-off: Less flexibility in schema changes

Testing Strategy
--------------
1. Manual Testing:
   - User flow testing through all booking processes
   - Cross-browser compatibility testing
   - Mobile responsiveness verification

2. Security Testing:
   - Session management verification
   - Input validation testing
   - Authentication bypass attempts
   - SQL injection prevention checks

3. Database Testing:
   - Data integrity checks
   - Transaction rollback verification
   - Concurrent booking handling

4. Error Handling:
   - Form validation testing
   - Edge case scenarios
   - Error message verification

Deployment Considerations
----------------------
1. Development Environment:
   - Local development using Flask's built-in server
   - Virtual environment for dependency isolation
   - Environment variables for sensitive configurations

2. Production Deployment:
   - Recommended to use:
     * Gunicorn/uWSGI as WSGI server
     * Nginx as reverse proxy
     * SSL/TLS certification for HTTPS
     * Environment-specific configuration files

3. Database Management:
   - Regular backups recommended
   - Consider connection pooling for production
   - Implement database migrations for updates

File Structure
-------------
- app.py: Main application file
- templates/: HTML templates
- static/: CSS, JavaScript, and image files
- requirements.txt: Python package dependencies
- ht_booking.sql: Database schema

Database Setup
-------------
1. Make sure you have MySQL installed
2. Create a new database named 'ht_booking'
3. Import the database schema:
   mysql -u your_username -p ht_booking < ht_booking.sql