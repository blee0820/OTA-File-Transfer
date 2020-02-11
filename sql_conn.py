import mysql.connector
import os
import sys

from mysql.connector import Error, MySQLConnection
from sql_conn_dbconfig import read_db_config

"""
Establishes connection with MySQL server then
runs a SQL command to retrieve requested info
"""

def connector(cam_id):
    try:
        # call read_db_config() to initiaite a connection with database
        # using provided .ini file
        db_config = read_db_config()
        conn = None
        print("")
        print('Connecting to MySQL Database')
        # db_config returned as dictionary - unpacked using double asterisk **
        conn = MySQLConnection(**db_config)
        
        if conn.is_connected():
            print('Connection to MySQL Database established')
            print("")
            print('Starting SQL query...')         
            try:
                # open file to read necessary SQL commands
                f = open(os.path.join(sys.path[0], 'sql.txt'), 'r')
                if f.mode == 'r':
                    sql = f.read()
            except FileNotFoundError as ffe:
                print(ffe)
                sys.exit(1)
            query = sql
            
            # run SQL commands and retrieve requested info
            cursor = conn.cursor()
            cursor.execute(query, (cam_id,))
            data = cursor.fetchone()
            print("SQL commands successfully queried")
            cam_info = {
                    'cam_id': data[0],
                    'camera_IP': data[1],
                    'camera_pw': data[2],
                    'last_hb_time_date': data[3]
                    }
            return cam_info
        else:
            print('Connection failed')
    except Error as error:
        print(error)
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
            print('Connection to MySQL Database terminated.')
            print("")

if __name__ == '__main__':
    connector(cam_id)