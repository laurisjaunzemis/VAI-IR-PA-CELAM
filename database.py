import sqlite3
import os
from contextlib import contextmanager

DATABASE_NAME = "carpooling.db"

def create_tables():
    """Create database tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create rides table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver TEXT NOT NULL,
            phone TEXT NOT NULL,
            start_location TEXT NOT NULL,
            end_location TEXT NOT NULL,
            time TEXT NOT NULL,
            available_seats INTEGER NOT NULL
        )
        ''')
        
        # Create passengers table (for future extensions)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ride_id INTEGER NOT NULL,
            passenger_name TEXT NOT NULL,
            FOREIGN KEY (ride_id) REFERENCES rides (id)
        )
        ''')
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        # If we get a database error, create a new database
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Initialize database when module is imported
create_tables()