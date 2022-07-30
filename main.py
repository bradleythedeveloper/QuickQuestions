import discord
from discord.ext import commands
from discord.utils import find
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import mysql.connector
from mysql.connector import Error
import pandas as pd
from secret.config import get_sql_root_pw, get_api_token, get_service_key_path
import random

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

connection = create_db_connection("localhost", "root", pw, "quickquestions")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def create_server_info(serverID):
    create_server_table = """
    CREATE TABLE server (
        response_id INT PRIMARY KEY,
        response_name VARCHAR(100),
        triggers SET(null),
        responses SET(null)
        );
    """
    create_server_table.replace("server",str(serverID))
    execute_query(connection, create_server_table)

api_token = get_api_token()

client = commands.Bot(command_prefix='qq!')
continue_adding = True
id_available = False
all_triggers = []
trigger_found = False
responses = []

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='your messages :3'))

@client.event
async def on_guild_join(guild):
    general = find(lambda x: 'general' in x.name,  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        message = await general.send('Hello {}!'.format(guild.name))
        serverID = message.guild.id
        # create_server_info(serverID)

@client.event
async def on_message(message):
    if(message.author.bot):
        return
    all_triggers = []
    trigger_found = False
    responses = []
    #serverID = message.guild.id
    serverID = 897499735970152559
    q1 = """
    SELECT value
    FROM actions
    JOIN triggersresponses
    ON actions.ID = triggersresponses.actionFK
    WHERE serverId='insert_server_id'
    AND type='trigger'; 
    """
    q1 = q1.replace("insert_server_id",str(serverID))
    results = read_query(connection, q1)
    for result in results:
        result = list(result)
        result = result[0]
        all_triggers.append(result)
    while trigger_found == False:
        for trigger in all_triggers:
            if trigger in message.content:
                q1 = """
                SELECT actionFK
                FROM actions
                JOIN triggersresponses
                ON actions.ID = triggersresponses.actionFK
                WHERE serverId='insert_server_id'
                AND type='trigger'
                AND value='insert_trigger'; 
                """
                q1 = q1.replace("insert_server_id",str(serverID))
                q1 = q1.replace("insert_trigger",str(trigger))
                results = read_query(connection, q1)
                for result in results:
                    result = list(result)
                    result = result[0]
                    responseID = result
                q1 = """
                SELECT value
                FROM actions
                JOIN triggersresponses
                ON actions.ID = triggersresponses.actionFK
                WHERE serverId='insert_server_id'
                AND type='response'
                AND actionFK='insert_response_id';
                """
                q1 = q1.replace("insert_server_id",str(serverID))
                q1 = q1.replace("insert_response_id",str(responseID))
                results = read_query(connection, q1)
                for result in results:
                    result = list(result)
                    result = result[0]
                    responses.append(result)
                chosen_response = random.choice(responses)
                await message.reply(chosen_response, mention_author=True)
                trigger_found = True
                break

client.run(api_token)