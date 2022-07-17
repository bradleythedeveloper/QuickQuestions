import discord
from discord.ext import commands
from secret.config import get_api_token

api_token = get_api_token()
client = commands.Bot(command_prefix='qq!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def test(ctx, *, arg):
    await ctx.send(arg)

@client.command()
async def add(ctx):
    await ctx.send('What response do you want QuickQuestions to give?')
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    is_correct = "n"
    # Waiting for new message
    while is_correct == "n":
        response = await client.wait_for("message", check=check)
        await ctx.send("Is this the right response? This will appear every time a key word/phrase is mentioned:")
        await ctx.send(response.content)
        await ctx.send("Type y or n to respond.")
        is_correct = await client.wait_for("message", check=check)
        is_correct = is_correct.content.lower()
    
        while is_correct not in ("y","n"):
            await ctx.send("Please enter y (yes) or n (no).")
            is_correct = await client.wait_for("message", check=check)
            is_correct = is_correct.content.lower()

        if is_correct == "y":
            await ctx.send("Awesome!")
        else:
            await ctx.send("Let's try again: what response do you want QuickQuestions to give?")

    await ctx.send("Next step!")
    
client.run(api_token)