import discord
from discord.ext import commands
from secret.config import get_api_token, get_service_key_path
import firebase_admin
from firebase_admin import credentials, firestore

api_token = get_api_token()
service_key = get_service_key_path()

client = commands.Bot(command_prefix='qq!')
continue_adding = True
id_available = False
cred = credentials.Certificate(service_key)
firebase_admin.initialize_app(cred)
db = firestore.client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='your messages :3'))

@client.event
async def on_message(message):
    serverId = message.guild.id
    await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):
    emoji = reaction.emoji

    if user.bot:
        return

@client.command()
async def test(ctx, *, arg):
    await ctx.send(arg)

@client.command()
async def add(ctx):
    is_correct = False
    continue_adding = True
    keyphrases = []
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
    # Waiting for new message
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
        title="Step 2: Responses",
        description="What response do you want QuickQuestions to give?",
        color=0x800080
    )
    await ctx.send(embed=embed)
    # Waiting for new message
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

    # Step 2: Asking for key words/phrases
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
            keyphrases.append(response.content)
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
        for phrase in keyphrases:
            trigger_check_list += ("\n'"+phrase+"'")
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
    
client.run(api_token)