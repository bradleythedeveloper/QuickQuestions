import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import mysql.connector
from mysql.connector import Error
import pandas as pd
from secret.config import get_sql_root_pw, get_api_token, get_service_key_path

pw = get_sql_root_pw()

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

connection = create_db_connection("localhost", "root", pw, "test")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

create_actions_table = """
    CREATE TABLE actions(
        ID INT PRIMARY KEY AUTO_INCREMENT,
        serverId VARCHAR(18) NOT NULL,
        name VARCHAR(255) NOT NULL,
        action TEXT NOT NULL,
        type ENUM("trigger","response")
    );
    """
execute_query(connection, create_actions_table)


