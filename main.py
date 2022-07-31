import discord
from discord.ext import commands
from discord.utils import find
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import mysql.connector
from mysql.connector import Error
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

api_token = get_api_token()

client = commands.Bot(command_prefix='qq!')
continue_adding = True
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

@client.event
async def on_message(message):
    #if(message.author.bot):
        #return
    all_triggers = []
    trigger_found = False
    responses = []
    #serverID = message.guild.id
    serverID = 897499735970152559
    # Getting all triggers
    query = """
    SELECT value
    FROM actions
    JOIN triggersresponses
    ON actions.ID = triggersresponses.actionFK
    WHERE serverId='insert_server_id'
    AND type='trigger'; 
    """
    query = query.replace("insert_server_id",str(serverID))
    results = read_query(connection, query)
    for result in results:
        result = list(result)
        result = result[0]
        all_triggers.append(result)
    for trigger in all_triggers:
        if trigger_found == False:
            if trigger in message.content:
                trigger_found = True
                # Getting the response ID from the trigger
                query = """
                SELECT actionFK
                FROM actions
                JOIN triggersresponses
                ON actions.ID = triggersresponses.actionFK
                WHERE serverId='insert_server_id'
                AND type='trigger'
                AND value='insert_trigger'; 
                """
                query = query.replace("insert_server_id",str(serverID))
                query = query.replace("insert_trigger",str(trigger))
                results = read_query(connection, query)
                for result in results:
                    result = list(result)
                    result = result[0]
                    responseID = result
                # Getting a response
                query = """
                SELECT value
                FROM actions
                JOIN triggersresponses
                ON actions.ID = triggersresponses.actionFK
                WHERE serverId='insert_server_id'
                AND type='response'
                AND actionFK='insert_response_id';
                """
                query = query.replace("insert_server_id",str(serverID))
                query = query.replace("insert_response_id",str(responseID))
                results = read_query(connection, query)
                for result in results:
                    result = list(result)
                    result = result[0]
                    responses.append(result)
                # Getting the response's name
                query = """
                SELECT DISTINCT name
                FROM actions
                JOIN triggersresponses
                ON actions.ID = triggersresponses.actionFK
                WHERE serverId='insert_server_id'
                AND type='response'
                AND actionFK='insert_response_id';
                """
                query = query.replace("insert_server_id",str(serverID))
                query = query.replace("insert_response_id",str(responseID))
                results = read_query(connection, query)
                for result in results:
                    result = list(result)
                    result = result[0]
                    response_name = result
                chosen_response = random.choice(responses)
                formatted_response = discord.Embed(title=response_name,description=chosen_response,color=0x800080)
                await message.reply(embed=formatted_response, mention_author=True)
    await client.process_commands(message)

@client.command()
async def textback(ctx, *, arg):
    await ctx.send(arg)

client.run(api_token)