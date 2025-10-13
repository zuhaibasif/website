-- HT Booking System Database Implementation
-- Created for the HT online booking system

-- Drop existing tables if they exist
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS cities;

-- Create cities table
CREATE TABLE cities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create routes table
CREATE TABLE routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    from_city_id INT NOT NULL,
    to_city_id INT NOT NULL,
    mode ENUM('air', 'coach', 'train') NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    standard_fare DECIMAL(10,2) NOT NULL,
    business_fare DECIMAL(10,2) NOT NULL,
    available_seats INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_city_id) REFERENCES cities(id),
    FOREIGN KEY (to_city_id) REFERENCES cities(id)
);

-- Create bookings table
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    route_id INT NOT NULL,
    reference VARCHAR(10) NOT NULL UNIQUE,
    journey_date DATE NOT NULL,
    passengers INT NOT NULL,
    class_type ENUM('standard', 'business') NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    class_upgrade DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

-- Insert sample cities
INSERT INTO cities (name) VALUES
('London'),
('Manchester'),
('Bristol'),
('Glasgow'),
('Newcastle'),
('Cardiff'),
('Edinburgh'),
('Portsmouth'),
('Dundee'),
('Southampton'),
('Birmingham'),
('Aberdeen');

-- Insert sample routes
INSERT INTO routes (from_city_id, to_city_id, mode, departure_time, arrival_time, standard_fare, business_fare, available_seats) VALUES
(1, 2, 'air', '08:00:00', '09:00:00', 150.00, 300.00, 130),
(1, 2, 'coach', '10:00:00', '14:00:00', 40.00, 80.00, 45),
(1, 2, 'train', '09:30:00', '11:30:00', 60.00, 120.00, 250),
(3, 4, 'air', '11:00:00', '12:00:00', 200.00, 400.00, 130),
(3, 4, 'coach', '13:00:00', '19:00:00', 50.00, 100.00, 45),
(5, 3, 'air', '14:00:00', '15:00:00', 180.00, 360.00, 130),
(5, 3, 'train', '15:30:00', '18:30:00', 70.00, 140.00, 250),
(6, 7, 'air', '16:00:00', '17:00:00', 220.00, 440.00, 130),
(6, 7, 'coach', '18:00:00', '23:00:00', 45.00, 90.00, 45);

-- Insert sample admin user
INSERT INTO users (first_name, last_name, email, phone, password, is_admin) VALUES
('Admin', 'User', 'admin@horizontravels.com', '07123456789', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpR1IOBYsQJmHy', TRUE);

-- Create Discounts table
CREATE TABLE Discounts (
    discount_id INT PRIMARY KEY AUTO_INCREMENT,
    min_days INT NOT NULL,
    max_days INT NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL,
    CONSTRAINT chk_days CHECK (min_days <= max_days),
    CONSTRAINT chk_percentage CHECK (discount_percentage >= 0 AND discount_percentage <= 100)
);

-- Create CancellationRules table
CREATE TABLE CancellationRules (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    min_days INT NOT NULL,
    max_days INT NOT NULL,
    charge_percentage DECIMAL(5,2) NOT NULL,
    CONSTRAINT chk_cancel_days CHECK (min_days <= max_days),
    CONSTRAINT chk_charge_percentage CHECK (charge_percentage >= 0 AND charge_percentage <= 100)
);

-- Insert sample data for Discounts
INSERT INTO Discounts (min_days, max_days, discount_percentage) VALUES
(80, 90, 25.00),
(60, 79, 15.00),
(45, 59, 10.00),
(0, 44, 0.00);

-- Insert sample data for CancellationRules
INSERT INTO CancellationRules (min_days, max_days, charge_percentage) VALUES
(60, 999, 0.00),
(30, 59, 40.00),
(0, 29, 100.00);

INSERT INTO bookings (user_id, route_id, reference, journey_date, passengers, class_type, base_price, class_upgrade, discount, total_price, status)
VALUES
(1, 1, 'BK123456', '2025-05-15', 2, 'standard', 100.00, 0.00, 20.00, 180.00, 'confirmed');

-- Create indexes for better performance
CREATE INDEX idx_routes_cities ON routes(from_city_id, to_city_id);

-- Create views for common queries
CREATE VIEW available_journeys AS
SELECT
    r.id,
    c1.name AS departure_city,
    c2.name AS arrival_city,
    r.mode,
    r.departure_time,
    r.arrival_time,
    r.available_seats - COALESCE(SUM(b.passengers), 0) as available_seats,
    CASE r.mode
        WHEN 'air' THEN r.standard_fare
        WHEN 'coach' THEN r.business_fare
        WHEN 'train' THEN r.standard_fare
    END as base_fare
FROM routes r
JOIN cities c1 ON r.from_city_id = c1.id
JOIN cities c2 ON r.to_city_id = c2.id
LEFT JOIN bookings b ON r.id = b.route_id AND b.status = 'confirmed'
GROUP BY r.id;

-- Create stored procedure for booking creation
DELIMITER //
CREATE PROCEDURE create_booking(
    IN p_user_id INT,
    IN p_route_id INT,
    IN p_class_type VARCHAR(10),
    IN p_passengers INT,
    IN p_journey_date DATE
)
BEGIN
    DECLARE v_base_fare DECIMAL(10,2);
    DECLARE v_total_price DECIMAL(10,2);
    DECLARE v_discount_percentage DECIMAL(5,2);
    DECLARE v_days_advance INT;

    -- Get base fare
    SELECT
        CASE r.mode
            WHEN 'air' THEN r.standard_fare
            WHEN 'coach' THEN r.business_fare
            WHEN 'train' THEN r.standard_fare
        END *
        CASE p_class_type
            WHEN 'business' THEN 2
            ELSE 1
        END
    INTO v_base_fare
    FROM routes r
    WHERE r.id = p_route_id;

    -- Calculate days in advance
    SET v_days_advance = DATEDIFF(p_journey_date, CURRENT_DATE);

    -- Get discount percentage
    SELECT discount_percentage INTO v_discount_percentage
    FROM Discounts
    WHERE v_days_advance BETWEEN min_days AND max_days;

    -- Calculate total price
    SET v_total_price = v_base_fare * p_passengers * (1 - COALESCE(v_discount_percentage, 0) / 100);

    -- Insert booking
    INSERT INTO bookings (
        user_id, route_id, reference, journey_date, passengers, class_type,
        base_price, class_upgrade, discount, total_price
    ) VALUES (
        p_user_id, p_route_id, UUID(), p_journey_date, p_passengers, p_class_type,
        v_base_fare, 0, v_base_fare * p_passengers * COALESCE(v_discount_percentage, 0) / 100,
        v_total_price
    );
END //
DELIMITER ;

-- Create trigger to update seat availability
DELIMITER //
CREATE TRIGGER after_booking_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    DECLARE v_class_type VARCHAR(10);
    DECLARE v_passengers INT;

    SET v_class_type = NEW.class_type;
    SET v_passengers = NEW.passengers;

    -- Update available seats in routes table
    UPDATE routes
    SET
        available_seats = CASE
            WHEN v_class_type = 'business' THEN available_seats - v_passengers
            ELSE available_seats
        END
    WHERE id = NEW.route_id;
END //
DELIMITER ;