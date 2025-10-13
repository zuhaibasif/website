from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps
import uuid
import io
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Set session to expire after 7 days

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/ht_booking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # This will log all SQL statements

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    from_routes = db.relationship('Route', foreign_keys='Route.from_city_id', backref='from_city', lazy=True)
    to_routes = db.relationship('Route', foreign_keys='Route.to_city_id', backref='to_city', lazy=True)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    from_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    to_city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    mode = db.Column(db.Enum('air', 'coach', 'train'), nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    arrival_time = db.Column(db.Time, nullable=False)
    standard_fare = db.Column(db.Numeric(10, 2), nullable=False)
    business_fare = db.Column(db.Numeric(10, 2), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='route', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    reference = db.Column(db.String(10), unique=True, nullable=False)
    journey_date = db.Column(db.Date, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    class_type = db.Column(db.Enum('standard', 'business'), nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    class_upgrade = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database
def init_db():
    with app.app_context():
        try:
            # Create all tables
            db.create_all()

            # Check if we need to add initial data
            if not City.query.first():
                # Add cities
                cities = [
                    City(name='Newcastle'),
                    City(name='Bristol'),
                    City(name='Glasgow'),
                    City(name='Manchester'),
                    City(name='Portsmouth'),
                    City(name='Dundee'),
                    City(name='Edinburgh'),
                    City(name='Cardiff'),
                    City(name='Southampton'),
                    City(name='Birmingham'),
                    City(name='Aberdeen'),
                    City(name='London')
                ]
                db.session.add_all(cities)

                # Add routes
                air_routes = [
                    # Air Routes (Mon-Fri)
                    Route(
                        from_city_id=1, to_city_id=2, mode='air',
                        departure_time=datetime.strptime('17:45', '%H:%M').time(),
                        arrival_time=datetime.strptime('19:00', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Newcastle to Bristol
                    Route(
                        from_city_id=2, to_city_id=3, mode='air',
                        departure_time=datetime.strptime('08:40', '%H:%M').time(),
                        arrival_time=datetime.strptime('09:45', '%H:%M').time(),
                        standard_fare=110, business_fare=220, available_seats=130
                    ),  # Bristol to Glasgow
                    Route(
                        from_city_id=3, to_city_id=1, mode='air',
                        departure_time=datetime.strptime('14:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('15:45', '%H:%M').time(),
                        standard_fare=110, business_fare=220, available_seats=130
                    ),  # Glasgow to Newcastle
                    Route(
                        from_city_id=1, to_city_id=4, mode='air',
                        departure_time=datetime.strptime('16:15', '%H:%M').time(),
                        arrival_time=datetime.strptime('17:05', '%H:%M').time(),
                        standard_fare=80, business_fare=160, available_seats=130
                    ),  # Newcastle to Manchester
                    Route(
                        from_city_id=4, to_city_id=2, mode='air',
                        departure_time=datetime.strptime('18:25', '%H:%M').time(),
                        arrival_time=datetime.strptime('19:30', '%H:%M').time(),
                        standard_fare=80, business_fare=160, available_seats=130
                    ),  # Manchester to Bristol
                    Route(
                        from_city_id=2, to_city_id=4, mode='air',
                        departure_time=datetime.strptime('06:20', '%H:%M').time(),
                        arrival_time=datetime.strptime('07:20', '%H:%M').time(),
                        standard_fare=80, business_fare=160, available_seats=130
                    ),  # Bristol to Manchester
                    Route(
                        from_city_id=5, to_city_id=6, mode='air',
                        departure_time=datetime.strptime('12:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('14:00', '%H:%M').time(),
                        standard_fare=120, business_fare=240, available_seats=130
                    ),  # Portsmouth to Dundee
                    Route(
                        from_city_id=6, to_city_id=5, mode='air',
                        departure_time=datetime.strptime('10:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('12:00', '%H:%M').time(),
                        standard_fare=120, business_fare=240, available_seats=130
                    ),  # Dundee to Portsmouth
                    Route(
                        from_city_id=7, to_city_id=8, mode='air',
                        departure_time=datetime.strptime('18:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('20:00', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Edinburgh to Cardiff
                    Route(
                        from_city_id=9, to_city_id=4, mode='air',
                        departure_time=datetime.strptime('12:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('13:30', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Southampton to Manchester
                    Route(
                        from_city_id=4, to_city_id=9, mode='air',
                        departure_time=datetime.strptime('19:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('20:30', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Manchester to Southampton
                    Route(
                        from_city_id=10, to_city_id=1, mode='air',
                        departure_time=datetime.strptime('17:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('17:45', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Birmingham to Newcastle
                    Route(
                        from_city_id=1, to_city_id=10, mode='air',
                        departure_time=datetime.strptime('07:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('07:45', '%H:%M').time(),
                        standard_fare=90, business_fare=180, available_seats=130
                    ),  # Newcastle to Birmingham
                    Route(
                        from_city_id=11, to_city_id=5, mode='air',
                        departure_time=datetime.strptime('08:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('09:30', '%H:%M').time(),
                        standard_fare=100, business_fare=200, available_seats=130
                    )  # Aberdeen to Portsmouth
                ]

                coach_routes = [
                    Route(
                        from_city_id=1, to_city_id=2, mode='coach',
                        departure_time=datetime.strptime('17:45', '%H:%M').time(),
                        arrival_time=datetime.strptime('03:45', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Newcastle to Bristol
                    Route(
                        from_city_id=2, to_city_id=3, mode='coach',
                        departure_time=datetime.strptime('08:40', '%H:%M').time(),
                        arrival_time=datetime.strptime('17:20', '%H:%M').time(),
                        standard_fare=28, business_fare=56, available_seats=45
                    ),  # Bristol to Glasgow
                    Route(
                        from_city_id=3, to_city_id=1, mode='coach',
                        departure_time=datetime.strptime('14:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('06:30', '%H:%M').time(),
                        standard_fare=28, business_fare=56, available_seats=45
                    ),  # Glasgow to Newcastle
                    Route(
                        from_city_id=1, to_city_id=4, mode='coach',
                        departure_time=datetime.strptime('16:15', '%H:%M').time(),
                        arrival_time=datetime.strptime('00:35', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Newcastle to Manchester
                    Route(
                        from_city_id=4, to_city_id=2, mode='coach',
                        departure_time=datetime.strptime('18:25', '%H:%M').time(),
                        arrival_time=datetime.strptime('06:05', '%H:%M').time(),
                        standard_fare=20, business_fare=40, available_seats=45
                    ),  # Manchester to Bristol
                    Route(
                        from_city_id=2, to_city_id=4, mode='coach',
                        departure_time=datetime.strptime('06:20', '%H:%M').time(),
                        arrival_time=datetime.strptime('14:20', '%H:%M').time(),
                        standard_fare=20, business_fare=40, available_seats=45
                    ),  # Bristol to Manchester
                    Route(
                        from_city_id=7, to_city_id=8, mode='coach',
                        departure_time=datetime.strptime('18:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('10:00', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Edinburgh to Cardiff
                    Route(
                        from_city_id=9, to_city_id=4, mode='coach',
                        departure_time=datetime.strptime('12:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('04:00', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Southampton to Manchester
                    Route(
                        from_city_id=4, to_city_id=9, mode='coach',
                        departure_time=datetime.strptime('19:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('11:00', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Manchester to Southampton
                    Route(
                        from_city_id=10, to_city_id=1, mode='coach',
                        departure_time=datetime.strptime('17:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('01:00', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Birmingham to Newcastle
                    Route(
                        from_city_id=1, to_city_id=10, mode='coach',
                        departure_time=datetime.strptime('07:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('15:00', '%H:%M').time(),
                        standard_fare=23, business_fare=46, available_seats=45
                    ),  # Newcastle to Birmingham
                    Route(
                        from_city_id=4,  # Newcastle
                        to_city_id=3,    # Bristol
                        mode='coach',
                        departure_time=datetime.strptime('17:45', '%H:%M').time(),
                        arrival_time=datetime.strptime('03:45', '%H:%M').time(),
                        standard_fare=23.00,
                        business_fare=46.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=3,  # Bristol
                        to_city_id=7,    # Glasgow
                        mode='coach',
                        departure_time=datetime.strptime('08:40', '%H:%M').time(),
                        arrival_time=datetime.strptime('17:20', '%H:%M').time(),
                        standard_fare=28.00,
                        business_fare=56.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=7,  # Glasgow
                        to_city_id=4,    # Newcastle
                        mode='coach',
                        departure_time=datetime.strptime('14:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('06:30', '%H:%M').time(),
                        standard_fare=25.00,
                        business_fare=50.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=4,  # Newcastle
                        to_city_id=2,    # Manchester
                        mode='coach',
                        departure_time=datetime.strptime('16:15', '%H:%M').time(),
                        arrival_time=datetime.strptime('00:35', '%H:%M').time(),
                        standard_fare=25.00,
                        business_fare=50.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=2,  # Manchester
                        to_city_id=3,    # Bristol
                        mode='coach',
                        departure_time=datetime.strptime('18:25', '%H:%M').time(),
                        arrival_time=datetime.strptime('06:05', '%H:%M').time(),
                        standard_fare=20.00,
                        business_fare=40.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=3,  # Bristol
                        to_city_id=2,    # Manchester
                        mode='coach',
                        departure_time=datetime.strptime('06:20', '%H:%M').time(),
                        arrival_time=datetime.strptime('14:20', '%H:%M').time(),
                        standard_fare=20.00,
                        business_fare=40.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=6,  # Edinburgh
                        to_city_id=5,    # Cardiff
                        mode='coach',
                        departure_time=datetime.strptime('18:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('10:00', '%H:%M').time(),
                        standard_fare=23.00,
                        business_fare=46.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=10,  # Southampton
                        to_city_id=2,     # Manchester
                        mode='coach',
                        departure_time=datetime.strptime('12:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('04:00', '%H:%M').time(),
                        standard_fare=23.00,
                        business_fare=46.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=2,   # Manchester
                        to_city_id=10,    # Southampton
                        mode='coach',
                        departure_time=datetime.strptime('19:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('11:00', '%H:%M').time(),
                        standard_fare=23.00,
                        business_fare=46.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=11,  # Birmingham
                        to_city_id=4,     # Newcastle
                        mode='coach',
                        departure_time=datetime.strptime('17:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('01:00', '%H:%M').time(),
                        standard_fare=25.00,
                        business_fare=50.00,
                        available_seats=45
                    ),
                    Route(
                        from_city_id=4,   # Newcastle
                        to_city_id=11,    # Birmingham
                        mode='coach',
                        departure_time=datetime.strptime('07:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('15:00', '%H:%M').time(),
                        standard_fare=25.00,
                        business_fare=50.00,
                        available_seats=45
                    )
                ]

                # Train routes
                train_routes = [
                    # Existing route
                    Route(
                        from_city_id=3,  # Bristol
                        to_city_id=4,    # Newcastle
                        mode='train',
                        departure_time=datetime.strptime('12:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('15:30', '%H:%M').time(),
                        standard_fare=200.00,
                        business_fare=400.00,
                        available_seats=250
                    ),
                    # New train routes
                    Route(
                        from_city_id=4,  # Newcastle
                        to_city_id=3,    # Bristol
                        mode='train',
                        departure_time=datetime.strptime('17:45', '%H:%M').time(),
                        arrival_time=datetime.strptime('23:00', '%H:%M').time(),
                        standard_fare=225.00,
                        business_fare=450.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=3,  # Bristol
                        to_city_id=7,    # Glasgow
                        mode='train',
                        departure_time=datetime.strptime('08:40', '%H:%M').time(),
                        arrival_time=datetime.strptime('14:05', '%H:%M').time(),
                        standard_fare=275.00,
                        business_fare=550.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=7,  # Glasgow
                        to_city_id=4,    # Newcastle
                        mode='train',
                        departure_time=datetime.strptime('14:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('19:45', '%H:%M').time(),
                        standard_fare=250.00,
                        business_fare=500.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=4,  # Newcastle
                        to_city_id=2,    # Manchester
                        mode='train',
                        departure_time=datetime.strptime('16:15', '%H:%M').time(),
                        arrival_time=datetime.strptime('21:20', '%H:%M').time(),
                        standard_fare=250.00,
                        business_fare=500.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=2,  # Manchester
                        to_city_id=3,    # Bristol
                        mode='train',
                        departure_time=datetime.strptime('18:25', '%H:%M').time(),
                        arrival_time=datetime.strptime('23:55', '%H:%M').time(),
                        standard_fare=200.00,
                        business_fare=400.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=3,  # Bristol
                        to_city_id=2,    # Manchester
                        mode='train',
                        departure_time=datetime.strptime('06:20', '%H:%M').time(),
                        arrival_time=datetime.strptime('11:40', '%H:%M').time(),
                        standard_fare=200.00,
                        business_fare=400.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=6,  # Edinburgh
                        to_city_id=5,    # Cardiff
                        mode='train',
                        departure_time=datetime.strptime('18:30', '%H:%M').time(),
                        arrival_time=datetime.strptime('23:30', '%H:%M').time(),
                        standard_fare=225.00,
                        business_fare=450.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=10,  # Southampton
                        to_city_id=2,     # Manchester
                        mode='train',
                        departure_time=datetime.strptime('12:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('17:30', '%H:%M').time(),
                        standard_fare=225.00,
                        business_fare=450.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=2,   # Manchester
                        to_city_id=10,    # Southampton
                        mode='train',
                        departure_time=datetime.strptime('19:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('00:30', '%H:%M').time(),
                        standard_fare=225.00,
                        business_fare=450.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=11,  # Birmingham
                        to_city_id=4,     # Newcastle
                        mode='train',
                        departure_time=datetime.strptime('17:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('22:15', '%H:%M').time(),
                        standard_fare=250.00,
                        business_fare=500.00,
                        available_seats=250
                    ),
                    Route(
                        from_city_id=4,   # Newcastle
                        to_city_id=11,    # Birmingham
                        mode='train',
                        departure_time=datetime.strptime('07:00', '%H:%M').time(),
                        arrival_time=datetime.strptime('12:15', '%H:%M').time(),
                        standard_fare=250.00,
                        business_fare=500.00,
                        available_seats=250
                    )
                ]

                # Combine all routes
                routes = air_routes + coach_routes + train_routes
                db.session.add_all(routes)

                # Add an admin user
                admin = User(
                    first_name='Admin',
                    last_name='User',
                    email='admin@horizontravels.com',
                    phone='+441234567890',
                    password=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin)

                db.session.commit()
                print("Database initialized with sample data!")
            else:
                print("Database already contains data.")

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

# Call init_db when the application starts
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/destinations')
def destinations():
    mode = request.args.get('mode', 'all')
    routes = Route.query.all()
    cities = City.query.all()
    return render_template('destinations.html', routes=routes, cities=cities, mode=mode)

@app.route('/booking')
def booking():
    # Fetch all cities and routes from the database
    cities = City.query.all()
    routes = Route.query.all()

    # Convert cities to a list of names
    city_names = [city.name for city in cities]

    # Organize routes by mode and city pairs
    routes_data = {
        'air': {},
        'coach': {},
        'train': {}
    }

    # Map city IDs to names for route processing
    city_map = {city.id: city.name for city in cities}

    for route in routes:
        from_city_name = city_map[route.from_city_id]
        to_city_name = city_map[route.to_city_id]

        # Create a key for the route in the format "from-to"
        route_key = f"{from_city_name}-{to_city_name}"

        # Add route details to the appropriate mode
        routes_data[route.mode][route_key] = {
            'from': from_city_name,
            'to': to_city_name,
            'fare': float(route.standard_fare),
            'business_fare': float(route.business_fare),
            'departure': route.departure_time.strftime('%H:%M'),
            'arrival': route.arrival_time.strftime('%H:%M'),
            'days': 'Mon-Fri' if route.mode == 'air' else 'Sat-Thurs' if route.mode == 'coach' else 'All week',
            'available': True
        }

    # Pass cities and routes data to the template
    return render_template('booking.html', cities=city_names, routes=routes_data)

# Update the booking route to ensure correct fare and timetable logic is applied
@app.route('/api/booking', methods=['POST'], endpoint='api_booking')
def create_booking():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Please login to make a booking'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Retrieve form data
        from_city = data.get('from')
        to_city = data.get('to')
        travel_mode = data.get('travel_mode')
        journey_date = data.get('departure_date')
        passengers = data.get('passengers')
        class_type = data.get('seat_class')

        # Validate required fields
        if not all([from_city, to_city, travel_mode, journey_date, passengers, class_type]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Find the route based on from, to, and travel_mode
        from_city_obj = City.query.filter_by(name=from_city).first()
        to_city_obj = City.query.filter_by(name=to_city).first()
        if not from_city_obj or not to_city_obj:
            return jsonify({'error': 'Invalid city names'}), 400

        route = Route.query.filter_by(
            from_city_id=from_city_obj.id,
            to_city_id=to_city_obj.id,
            mode=travel_mode
        ).first()

        if not route:
            return jsonify({'error': 'No route found for the selected cities and travel mode'}), 404

        # Check available seats
        existing_bookings = Booking.query.filter_by(
            route_id=route.id,
            journey_date=datetime.strptime(journey_date, '%Y-%m-%d').date()
        ).all()
        total_booked_seats = sum(booking.passengers for booking in existing_bookings)

        if (total_booked_seats + int(passengers)) > route.available_seats:
            return jsonify({'error': 'Not enough seats available for this route'}), 400

        # Calculate pricing based on mode and route
        base_price = float(route.business_fare if class_type == 'business' else route.standard_fare)

        # Apply discounts based on booking date
        try:
            journey_date_obj = datetime.strptime(journey_date, '%Y-%m-%d').date()
            days_in_advance = (journey_date_obj - datetime.now().date()).days
            discount_percentage = 0
            if days_in_advance >= 80:
                discount_percentage = 0.25
            elif days_in_advance >= 60:
                discount_percentage = 0.15
            elif days_in_advance >= 45:
                discount_percentage = 0.10
        except ValueError:
            return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

        class_upgrade = 0  # Already accounted for in business_fare
        discount = base_price * int(passengers) * discount_percentage
        total_price = (base_price * int(passengers)) - discount

        # Generate unique reference number
        while True:
            reference = str(uuid.uuid4())[:8].upper()
            if not Booking.query.filter_by(reference=reference).first():
                break

        # Create the booking
        booking = Booking(
            user_id=session['user_id'],
            route_id=route.id,
            reference=reference,
            journey_date=datetime.strptime(journey_date, '%Y-%m-%d').date(),
            passengers=int(passengers),
            class_type=class_type,
            base_price=base_price,
            class_upgrade=class_upgrade,
            discount=discount,
            total_price=total_price
        )

        db.session.add(booking)
        db.session.commit()

        return jsonify({
            'success': True,
            'redirect': url_for('booking_confirmation', booking_id=booking.id)
        })

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid value: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/booking-confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('booking-confirmation.html', booking=booking, now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)

            if not all([email, password]):
                return jsonify({'error': 'Email and password are required'}), 400

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                if remember:
                    session.permanent = True
                return jsonify({
                    'redirect': url_for('user_dashboard' if not user.is_admin else 'admin')
                })

            return jsonify({'error': 'Invalid email or password'}), 401
        except Exception as e:
            return jsonify({'error': f'Error during login: {str(e)}'}), 500

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')
            user_type = data.get('user_type')

            if not all([first_name, last_name, email, phone, password]):
                return jsonify({'error': 'All fields are required'}), 400

            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already registered'}), 400

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=generate_password_hash(password),
                is_admin=(user_type == 'admin')
            )

            db.session.add(user)
            db.session.commit()

            return jsonify({
                'redirect': url_for('login')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error during registration: {str(e)}'}), 500

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user-dashboard')
@login_required
def user_dashboard():
    user = User.query.get_or_404(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.journey_date.desc()).all()

    # Get upcoming and past bookings
    today = datetime.now().date()
    upcoming_bookings = [b for b in bookings if b.journey_date >= today and b.status != 'cancelled']
    past_bookings = [b for b in bookings if b.journey_date < today or b.status == 'cancelled']

    return render_template('user-dashboard.html',
                          user=user,
                          bookings=bookings,
                          upcoming_bookings=upcoming_bookings,
                          past_bookings=past_bookings)

@app.route('/admin')
@admin_required
def admin():
    # Fetch all bookings
    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    # Fetch all routes and cities for journey management
    all_routes = Route.query.all()
    all_cities = City.query.all()

    # Fetch all users for user management
    all_users = User.query.all()

    # Get statistics
    total_bookings = Booking.query.filter(
        Booking.created_at >= datetime.now() - timedelta(days=30)
    ).count()

    revenue = db.session.query(db.func.sum(Booking.total_price)).filter(
        Booking.created_at >= datetime.now() - timedelta(days=30)
    ).scalar() or 0

    new_users = User.query.filter(
        User.created_at >= datetime.now() - timedelta(days=30)
    ).count()

    # Get popular route
    popular_route = db.session.query(
        Route, db.func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Route.id).order_by(db.desc('booking_count')).first()

    stats = {
        'total_bookings': total_bookings,
        'revenue': float(revenue),
        'new_users': new_users,
        'popular_route': f"{popular_route[0].from_city.name}-{popular_route[0].to_city.name}" if popular_route else "N/A",
        'popular_route_bookings': popular_route[1] if popular_route else 0
    }

    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()

    # Get sales by journey type
    sales_by_type = {}
    for mode in ['air', 'coach', 'train']:
        total = db.session.query(db.func.sum(Booking.total_price)).filter(
            Booking.route.has(mode=mode),
            Booking.created_at >= datetime.now() - timedelta(days=30)
        ).scalar() or 0
        sales_by_type[mode] = round((float(total) / float(revenue)) * 100 if revenue else 0, 1)

    # Get top routes by revenue
    top_routes = db.session.query(
        Route,
        db.func.sum(Booking.total_price).label('revenue')
    ).join(Booking).group_by(Route.id).order_by(db.desc('revenue')).limit(3).all()

    # Get top customers
    top_customers = db.session.query(
        User,
        db.func.count(Booking.id).label('bookings')
    ).join(Booking).group_by(User.id).order_by(db.desc('bookings')).limit(3).all()

    return render_template('admin.html',
        stats=stats,
        recent_bookings=recent_bookings,
        sales_by_type=sales_by_type,
        top_routes=top_routes,
        top_customers=top_customers,
        all_bookings=all_bookings,
        all_routes=all_routes,
        all_cities=all_cities,
        all_users=all_users
    )

@app.route('/admin/reports')
@admin_required
def admin_reports():
    report_type = request.args.get('report_type', 'monthly-sales')
    period = request.args.get('period', '30')
    period = int(period)

    # Generate report data based on type and period
    report_data = {}

    if report_type == 'monthly-sales':
        # Monthly sales report
        sales_data = db.session.query(
            db.func.date_format(Booking.created_at, '%Y-%m-%d').label('date'),
            db.func.sum(Booking.total_price).label('revenue')
        ).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by('date').order_by('date').all()

        report_data['labels'] = [item[0] for item in sales_data]
        report_data['values'] = [float(item[1]) for item in sales_data]
        report_data['title'] = f'Sales for the Last {period} Days'

    elif report_type == 'journey-sales':
        # Journey sales report
        journey_data = db.session.query(
            Route.mode,
            db.func.sum(Booking.total_price).label('revenue')
        ).join(Booking).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by(Route.mode).all()

        report_data['labels'] = [item[0].capitalize() for item in journey_data]
        report_data['values'] = [float(item[1]) for item in journey_data]
        report_data['title'] = f'Sales by Journey Type for the Last {period} Days'

    elif report_type == 'top-customers':
        # Top customers report
        customer_data = db.session.query(
            User.first_name,
            User.last_name,
            db.func.count(Booking.id).label('bookings'),
            db.func.sum(Booking.total_price).label('spent')
        ).join(Booking).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by(User.id).order_by(db.desc('spent')).limit(10).all()

        report_data['customers'] = [{
            'name': f"{item[0]} {item[1]}",
            'bookings': item[2],
            'spent': float(item[3])
        } for item in customer_data]
        report_data['title'] = f'Top Customers for the Last {period} Days'

    elif report_type == 'profit-loss':
        # Profit/loss by route
        route_data = db.session.query(
            Route.id,
            City.name.label('from_city'),
            db.func.count(Booking.id).label('bookings'),
            db.func.sum(Booking.total_price).label('revenue')
        ).join(Booking).join(City, Route.from_city_id == City.id).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by(Route.id, City.name).order_by(db.desc('revenue')).all()

        report_data['routes'] = [{
            'id': item[0],
            'from_city': item[1],
            'bookings': item[2],
            'revenue': float(item[3])
        } for item in route_data]
        report_data['title'] = f'Route Performance for the Last {period} Days'

    return render_template('admin.html',
                          report_type=report_type,
                          period=period,
                          report_data=report_data,
                          active_tab='reports')

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get_or_404(session['user_id'])

    # Get form data
    user.first_name = request.form.get('first_name')
    user.last_name = request.form.get('last_name')
    user.email = request.form.get('email')
    user.phone = request.form.get('phone')

    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session['user_id'])

    # Get form data
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Validate current password
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('user_dashboard'))

    # Validate new password
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('user_dashboard'))

    # Update password
    user.password = generate_password_hash(new_password)
    db.session.commit()

    flash('Password updated successfully', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/cancel-booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if user owns the booking or is admin
    if booking.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Unauthorized', 'error')
        return redirect(url_for('user_dashboard'))

    # Check if booking is already cancelled
    if booking.status == 'cancelled':
        flash('This booking is already cancelled', 'error')
        return redirect(url_for('user_dashboard' if not session.get('is_admin') else 'admin'))

    # Calculate cancellation fee
    days_to_journey = (booking.journey_date - datetime.now().date()).days
    cancellation_fee = 0
    refund_amount = float(booking.total_price)

    if days_to_journey <= 30:
        cancellation_fee = float(booking.total_price)  # 100% fee
        refund_amount = 0
    elif days_to_journey <= 60:
        cancellation_fee = float(booking.total_price) * 0.4  # 40% fee
        refund_amount = float(booking.total_price) * 0.6

    # Update booking status
    booking.status = 'cancelled'
    db.session.commit()

    # Show appropriate message based on refund amount
    if refund_amount > 0:
        flash(f'Booking cancelled successfully. A refund of £{refund_amount:.2f} will be processed.', 'success')
    else:
        flash('Booking cancelled successfully. No refund will be issued due to late cancellation.', 'success')

    # Redirect to appropriate page
    if request.method == 'POST' and 'HTTP_REFERER' in request.environ:
        # If coming from booking confirmation page, redirect back there
        if f'/booking-confirmation/{booking_id}' in request.environ['HTTP_REFERER']:
            return redirect(url_for('booking_confirmation', booking_id=booking_id))

    return redirect(url_for('user_dashboard' if not session.get('is_admin') else 'admin'))

@app.route('/admin/add-journey', methods=['POST'])
@admin_required
def add_journey():
    try:
        # Get form data
        from_city_id = request.form.get('from_city_id')
        to_city_id = request.form.get('to_city_id')
        mode = request.form.get('mode')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        standard_fare = request.form.get('standard_fare')
        business_fare = request.form.get('business_fare')
        available_seats = request.form.get('available_seats')

        # Validate data
        if from_city_id == to_city_id:
            flash('From and To cities cannot be the same', 'error')
            return redirect(url_for('admin'))

        # Create new route
        new_route = Route(
            from_city_id=from_city_id,
            to_city_id=to_city_id,
            mode=mode,
            departure_time=datetime.strptime(departure_time, '%H:%M').time(),
            arrival_time=datetime.strptime(arrival_time, '%H:%M').time(),
            standard_fare=standard_fare,
            business_fare=business_fare,
            available_seats=available_seats
        )

        db.session.add(new_route)
        db.session.commit()

        flash('Journey added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding journey: {str(e)}', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/edit-journey/<int:route_id>', methods=['POST'])
@admin_required
def edit_journey(route_id):
    try:
        route = Route.query.get_or_404(route_id)

        # Update route data
        route.from_city_id = request.form.get('from_city_id')
        route.to_city_id = request.form.get('to_city_id')
        route.mode = request.form.get('mode')
        route.departure_time = datetime.strptime(request.form.get('departure_time'), '%H:%M').time()
        route.arrival_time = datetime.strptime(request.form.get('arrival_time'), '%H:%M').time()
        route.standard_fare = request.form.get('standard_fare')
        route.business_fare = request.form.get('business_fare')
        route.available_seats = request.form.get('available_seats')

        db.session.commit()
        flash('Journey updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating journey: {str(e)}', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/delete-journey/<int:route_id>', methods=['POST'])
@admin_required
def delete_journey(route_id):
    try:
        route = Route.query.get_or_404(route_id)

        # Check if route has bookings
        if route.bookings:
            flash('Cannot delete journey with existing bookings', 'error')
            return redirect(url_for('admin'))

        db.session.delete(route)
        db.session.commit()
        flash('Journey deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting journey: {str(e)}', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/manage-user/<int:user_id>', methods=['POST'])
@admin_required
def manage_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        action = request.form.get('action')

        if action == 'reset_password':
            # Reset password to default
            user.password = generate_password_hash('password123')
            db.session.commit()
            flash(f'Password reset for {user.email}', 'success')

        elif action == 'toggle_admin':
            # Toggle admin status
            user.is_admin = not user.is_admin
            db.session.commit()
            flash(f'Admin status updated for {user.email}', 'success')

        elif action == 'delete':
            # Check if user has bookings
            if user.bookings:
                flash('Cannot delete user with existing bookings', 'error')
                return redirect(url_for('admin'))

            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error managing user: {str(e)}', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/export-report', methods=['POST'])
@admin_required
def export_report():
    report_type = request.form.get('report_type')
    period = int(request.form.get('period', 30))

    # Create CSV data based on report type
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'monthly-sales':
        # Monthly sales report
        writer.writerow(['Date', 'Revenue'])

        sales_data = db.session.query(
            db.func.date_format(Booking.created_at, '%Y-%m-%d').label('date'),
            db.func.sum(Booking.total_price).label('revenue')
        ).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by('date').order_by('date').all()

        for item in sales_data:
            writer.writerow([item[0], float(item[1])])

    elif report_type == 'journey-sales':
        # Journey sales report
        writer.writerow(['Journey Type', 'Revenue'])

        journey_data = db.session.query(
            Route.mode,
            db.func.sum(Booking.total_price).label('revenue')
        ).join(Booking).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by(Route.mode).all()

        for item in journey_data:
            writer.writerow([item[0].capitalize(), float(item[1])])

    elif report_type == 'top-customers':
        # Top customers report
        writer.writerow(['Customer', 'Bookings', 'Total Spent'])

        customer_data = db.session.query(
            User.first_name,
            User.last_name,
            db.func.count(Booking.id).label('bookings'),
            db.func.sum(Booking.total_price).label('spent')
        ).join(Booking).filter(
            Booking.created_at >= datetime.now() - timedelta(days=period)
        ).group_by(User.id).order_by(db.desc('spent')).limit(10).all()

        for item in customer_data:
            writer.writerow([f"{item[0]} {item[1]}", item[2], float(item[3])])

    # Create response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{report_type}_{period}days.csv'
    )

@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        cities = City.query.all()
        city_names = [city.name for city in cities]
        return jsonify({'cities': city_names})
    except Exception as e:
        return jsonify({'error': f'Error fetching cities: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)