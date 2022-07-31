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
    if(message.author.bot):
        return
    all_triggers = []
    trigger_found = False
    responses = []
    serverID = message.guild.id
    #serverID = 897499735970152559
    # Getting all triggers
    query = """
    SELECT value
    FROM tr_groups
    JOIN triggersresponses
    ON tr_groups.ID = triggersresponses.groupFK
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
                SELECT groupFK
                FROM tr_groups
                JOIN triggersresponses
                ON tr_groups.ID = triggersresponses.groupFK
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
                FROM tr_groups
                JOIN triggersresponses
                ON tr_groups.ID = triggersresponses.groupFK
                WHERE serverId='insert_server_id'
                AND type='response'
                AND groupFK='insert_response_id';
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
                FROM tr_groups
                JOIN triggersresponses
                ON tr_groups.ID = triggersresponses.groupFK
                WHERE serverId='insert_server_id'
                AND type='response'
                AND groupFK='insert_response_id';
                """
                query = query.replace("insert_server_id",str(serverID))
                query = query.replace("insert_response_id",str(responseID))
                results = read_query(connection, query)
                for result in results:
                    result = list(result)
                    result = result[0]
                    response_name = result
                print(responses)
                if len(responses) == 1:
                    chosen_response = responses[0]
                else:
                    chosen_response = random.choice(responses)
                formatted_response = discord.Embed(title=response_name,description=chosen_response,color=0x800080)
                await message.reply(embed=formatted_response, mention_author=True)
    await client.process_commands(message)

@client.command()
async def add(ctx):
    serverID = ctx.guild.id
    is_correct = False
    continue_adding = True
    group_triggers = []
    tick = '✅'
    cross = '❎'
    valid_reactions = ['✅', '❎']
    def tick_check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in valid_reactions
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    # Step 1: Responses
    embed = discord.Embed(
        title="Step 1: Naming Trigger/Response Group",
        description="""
        What name do you want to give to this trigger/response group?
        You'll be able to use this name to search for this trigger/response group to edit its triggers and responses.
        """,
        color=0x800080
    )
    await ctx.send(embed=embed)
    while is_correct == False:
        user_response = await client.wait_for("message", check=check)
        embed = discord.Embed(
            description=("Is this the right name?" + "\n\n'" + user_response.content + "'"),
            color=0x800080
        )
        react_msg = await ctx.send(embed=embed)
        await react_msg.add_reaction(tick)
        await react_msg.add_reaction(cross)
        reaction, user = await client.wait_for('reaction_add', check=tick_check)
        if str(reaction.emoji) == tick:
            group_name = user_response.content
            is_correct = True
        if str(reaction.emoji) == cross:
            embed = discord.Embed(
                description="Enter your new name.",
                color=0x800080
            )
            await ctx.send(embed=embed)
    # Step 2: Asking for response
    is_correct = False
    embed = discord.Embed(
        title="Step 2: Response",
        description="What response do you want QuickQuestions to give?",
        color=0x800080
    )
    await ctx.send(embed=embed)
    while is_correct == False:
        user_response = await client.wait_for("message", check=check)
        embed = discord.Embed(
            description=("Is this the right response? This will appear every time a key word/phrase is mentioned:" + "\n\n'" + user_response.content + "'"),
            color=0x800080
        )
        react_msg = await ctx.send(embed=embed)
        await react_msg.add_reaction(tick)
        await react_msg.add_reaction(cross)
        reaction, user = await client.wait_for('reaction_add', check=tick_check)
        if str(reaction.emoji) == tick:
            bot_response = user_response.content
            is_correct = True
        if str(reaction.emoji) == cross:
            embed = discord.Embed(
                description="Enter your new response.",
                color=0x800080
            )
            await ctx.send(embed=embed)
    # Step 3: Asking for key words/phrases
    is_correct = False
    embed = discord.Embed(
        title="Step 3: Adding Triggers",
        description="""
        What words and phrases do you want QuickQuestions to give this response to?
        Enter your first key word/phrase, and you'll be prompted to add more if you want to.
        You'll be able to add to and change these words/phrases later.
        """,
        color=0x800080
    )
    await ctx.send(embed=embed)
    while is_correct == False:
        while continue_adding == True:
            response = await client.wait_for("message", check=check)
            group_triggers.append(response.content)
            embed = discord.Embed(
                description="Add another key word/phrase?",
                color=0x800080
            )
            react_msg = await ctx.send(embed=embed)
            await react_msg.add_reaction(tick)
            await react_msg.add_reaction(cross)
            reaction, user = await client.wait_for('reaction_add', check=tick_check)
            if str(reaction.emoji) == tick:
                embed = discord.Embed(
                    description="Enter your new key word/phrase.",
                    color=0x800080
                )
                await ctx.send(embed=embed)
            if str(reaction.emoji) == cross:
                continue_adding = False    
        trigger_check_list = """"""
        for trigger in group_triggers:
            trigger_check_list += ("\n'"+trigger+"'")
        embed = discord.Embed(
            description=("To confirm, these are all the words/phrases you want QuickQuestions to respond to:\n" + trigger_check_list + "\n\nIs this correct?"),
            color=0x800080
        )
        react_msg = await ctx.send(embed=embed)
        await react_msg.add_reaction(tick)
        await react_msg.add_reaction(cross)
        reaction, user = await client.wait_for('reaction_add', check=tick_check)
        if str(reaction.emoji) == tick:
            embed=discord.Embed(
                title=group_name,
                color=0x800080
            )
            embed.set_author(name="All done!")
            embed.add_field(
                name="QuickQuestions will now respond to these phrases:",
                value=trigger_check_list,
                inline=False
            )
            embed.add_field(
                name="By saying this:",
                value=("'"+bot_response+"'"),
                inline=False
            )
            await ctx.send(embed=embed)
            is_correct = True
        if str(reaction.emoji) == cross:
            embed = discord.Embed(
                    description="Enter your new key word/phrase.",
                    color=0x800080
            )
            await ctx.send(embed=embed)
            continue_adding = True
    query = "INSERT INTO tr_groups (serverId, name) VALUES ('insert_server_id', 'insert_group_name')"
    query = query.replace("insert_server_id",str(serverID))
    query = query.replace("insert_group_name",str(group_name))
    execute_query(connection, query)
    query = """
    SELECT ID
    FROM tr_groups
    WHERE serverId='insert_server_id'
    AND name='insert_group_name';
    """
    query = query.replace("insert_server_id",str(serverID))
    query = query.replace("insert_group_name",str(group_name))
    results = read_query(connection, query)
    for result in results:
        result = list(result)
        result = result[0]
        groupID = result
    for trigger in group_triggers:
        query = "INSERT INTO triggersresponses (groupFK, value, type) VALUES (insert_group_id, 'insert_value', 'trigger')"
        query = query.replace("insert_group_id",str(groupID))
        query = query.replace("insert_value",str(trigger))
        execute_query(connection, query)
    query = "INSERT INTO triggersresponses (groupFK, value, type) VALUES (insert_group_id, 'insert_value', 'response')"
    query = query.replace("insert_group_id",str(groupID))
    query = query.replace("insert_value",str(bot_response))
    execute_query(connection, query)

client.run(api_token)