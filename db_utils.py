# Description: This file contains the functions to connect and close the connection to the database.

import mysql.connector

def get_db_connection():
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='CTMEU',
        autocommit=True
    )
    return db_connection

def close_db_connection(conn):
    if conn.is_connected():
        conn.close()
        print('Database connection closed')
