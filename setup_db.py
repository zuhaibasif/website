import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'  # Change this to your MySQL root password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS ht_booking")
            print("Database 'ht_booking' created successfully")
            
            # Switch to the database
            cursor.execute("USE ht_booking")
            
            # Update root user authentication method
            cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'")
            cursor.execute("FLUSH PRIVILEGES")
            print("Root user authentication updated successfully")
            
            connection.commit()
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    setup_database() 