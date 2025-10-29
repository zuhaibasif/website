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
2. Set up environment variables (optional):
   ```
   # Windows PowerShell
   $env:FLASK_APP="run.py"
   $env:FLASK_ENV="development"
   
   # Linux/Mac
   export FLASK_APP=run.py
   export FLASK_ENV=development
   ```
3. Run the Flask application:
   - Windows: python run.py
   - Mac/Linux: python3 run.py
4. Open your web browser and go to: http://localhost:5000

Development Workflow
------------------
1. Code Organization:
   - Models go in app/models/
   - Routes go in app/routes/
   - Business logic in app/services/
   - Helper functions in app/utils/
   
2. Adding New Features:
   - Create new route file in app/routes/
   - Add models if needed in app/models/
   - Write corresponding tests
   - Register blueprint in __init__.py
   
3. Testing:
   - Run unit tests: pytest tests/unit/
   - Run integration tests: pytest tests/integration/
   - Check coverage: pytest --cov=app
   
4. Code Quality:
   - Follow PEP 8 style guide
   - Use type hints where possible
   - Document functions and classes
   - Handle errors appropriately

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
1. Unit Tests (tests/unit/):
   - Written using pytest framework
   - Test coverage for core functionality:
     * User authentication (test_auth.py)
     * Booking logic (test_booking.py)
     * Admin functions (test_admin.py)
   - Run tests with: pytest tests/unit/

2. Integration Tests (tests/integration/):
   - End-to-end testing with pytest-flask
   - Database integration using test fixtures
   - API endpoint testing
   - Run tests with: pytest tests/integration/

3. Manual Testing:
   - User flow testing through all booking processes
   - Cross-browser compatibility testing
   - Mobile responsiveness verification

4. Security Testing:
   - Session management verification
   - Input validation testing
   - Authentication bypass attempts
   - SQL injection prevention checks
   - Regular security audits with safety check

5. Database Testing:
   - Data integrity checks
   - Transaction rollback verification
   - Concurrent booking handling
   - Migration testing

6. Error Handling:
   - Form validation testing
   - Edge case scenarios
   - Error message verification

7. Load Testing:
   - Using Locust for performance testing
   - Simulated user behavior
   - Concurrent user load testing
   - Run with: locust -f tests/load/locustfile.py

Continuous Integration (CI)
-------------------------
Project uses GitHub Actions for CI/CD pipeline:

1. Test Workflow (.github/workflows/test.yml):
   ```yaml
   name: Tests
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       services:
         mysql:
           image: mysql:8.0
           env:
             MYSQL_DATABASE: ht_booking_test
             MYSQL_ROOT_PASSWORD: root
           ports:
             - 3306:3306
       
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.8'
         
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             pip install pytest pytest-cov pytest-flask locust safety
         
         - name: Run security checks
           run: safety check
         
         - name: Run unit tests
           run: pytest tests/unit/ --cov=app
         
         - name: Run integration tests
           run: pytest tests/integration/
         
         - name: Upload coverage report
           uses: codecov/codecov-action@v1
   ```

2. CI Pipeline includes:
   - Automated testing on every push and pull request
   - Security vulnerability scanning
   - Code coverage reporting
   - Database integration testing
   - Performance benchmarking

3. Development Workflow:
   - Create feature branch
   - Write tests for new features
   - Submit pull request
   - CI runs all checks
   - Code review and merge

4. Test Configuration:
   - pytest.ini for test settings
   - conftest.py for shared fixtures
   - .coveragerc for coverage settings

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
```
horizon-travels/
├── app/
│   ├── __init__.py          # Application factory and extensions
│   ├── models/
│   │   └── models.py        # Database models (User, Booking)
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   ├── booking.py      # Booking management routes
│   │   ├── admin.py        # Admin panel routes
│   │   └── main.py         # Main/index routes
│   ├── services/
│   │   ├── email.py        # Email service
│   │   └── payment.py      # Payment processing
│   ├── utils/
│   │   ├── config.py       # Configuration classes
│   │   ├── decorators.py   # Custom decorators
│   │   └── error_handlers.py # Error handling
│   └── templates/          # Jinja2 templates
├── static/                 # Static assets
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── load/             # Load tests
├── run.py                # Application entry point
├── requirements.txt      # Dependencies
└── ht_booking.sql       # Database schema

Database Setup
-------------
1. Make sure you have MySQL installed
2. Create a new database named 'ht_booking'
3. Import the database schema:
   mysql -u your_username -p ht_booking < ht_booking.sql