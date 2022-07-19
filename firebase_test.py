import discord
from discord.ext import commands
from secret.config import get_api_token, get_service_key_path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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
    serverId = str(message.guild.id)
    serverName = message.guild.name
    doc_ref = db.collection(serverId).document(u'server_info')
    doc_ref.set({
        u'serverName': serverName,
        u'ignored': True
    })

@client.command()
async def get_response(ctx):
    serverId = str(ctx.message.guild.id)
    docs = db.collection(serverId).where(u'ignored', u'!=', True).stream()
    for doc in docs:
        await ctx.send(f'{doc.id} => {doc.to_dict()}')

client.run(api_token)