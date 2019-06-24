import discord
from discord.ext import commands
import asyncio

from config import instar_token

class GameCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")


client = commands.Bot(command_prefix="i!", case_insensitive=True)

@client.event
async def on_ready():
    print("Connected and ready to play!")

client.add_cog(GameCog(client))

client.run(instar_token)