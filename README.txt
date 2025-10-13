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