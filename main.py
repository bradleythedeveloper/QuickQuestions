import discord
from secret.config import get_api_token

client = discord.Client()
api_token = get_api_token()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if message.content.startswith('qq!add'):
        await message.channel.send('What response do you want QuickQuestions to give?')
        
        
    if 'when' in message.content:
        await message.channel.send('Keyword found in message')
    
client.run(api_token)
