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
    # Step 1: Asking for response
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    await ctx.send('What response do you want QuickQuestions to give?')
    # Waiting for new message
    while is_correct == False:
        response = await client.wait_for("message", check=check)
        await ctx.send("Is this the right response? This will appear every time a key word/phrase is mentioned:")
        react_msg = await ctx.send("'"+response.content+"'")
        await react_msg.add_reaction(tick)
        await react_msg.add_reaction(cross)
        reaction, user = await client.wait_for('reaction_add', check=tick_check)
        if str(reaction.emoji) == tick:
            await ctx.send("Awesome!")
            is_correct = True
        if str(reaction.emoji) == cross:
            await ctx.send("Enter your new response.")
    await ctx.send("On to the next step.")

    # Step 2: Asking for key words/phrases
    is_correct = False
    
    await ctx.send('What words and phrases do you want QuickQuestions to give this response to?')
    await ctx.send("Enter your first key word/phrase, and you'll be prompted to add more if you want to.")
    await ctx.send("You'll be able to add to and change these words/phrases later.")
    while is_correct == False:
        while continue_adding == True:
            response = await client.wait_for("message", check=check)
            keyphrases.append(response.content)
            react_msg = await ctx.send("Add another key word/phrase?")
            await react_msg.add_reaction(tick)
            await react_msg.add_reaction(cross)
            reaction, user = await client.wait_for('reaction_add', check=tick_check)
            if str(reaction.emoji) == tick:
                await ctx.send("Enter your new key word/phrase.")
            if str(reaction.emoji) == cross:
                continue_adding = False    
        await ctx.send("To confirm, these are all the words/phrases you want QuickQuestions to respond to:")
        for phrase in keyphrases:
            await ctx.send("'"+phrase+"'")

        react_msg = await ctx.send("Is this correct?")
        await react_msg.add_reaction(tick)
        await react_msg.add_reaction(cross)
        reaction, user = await client.wait_for('reaction_add', check=tick_check)
        if str(reaction.emoji) == tick:
            await ctx.send("Awesome!")
            is_correct = True
        if str(reaction.emoji) == cross:
            await ctx.send("Enter your new key word/phrase.")
            continue_adding = True
    
client.run(api_token)