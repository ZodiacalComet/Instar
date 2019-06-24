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

    @commands.group(invoke_without_command=True)
    async def uno(self, ctx):
        await ctx.send("[Help Command]")

    @uno.command(name="howto")
    async def _howto(self, ctx):
        await ctx.send("[Instructions]")

    @uno.command(name="start")
    async def _start(self, ctx):
        await ctx.send("[Start sequence]")

    @_start.before_invoke
    async def prepare_server(self, ctx):
        await ctx.send("[Prepare server]")

client = commands.Bot(command_prefix="i!", case_insensitive=True)

@client.event
async def on_ready():
    print("Connected and ready to play!")

client.add_cog(GameCog(client))
client.run(instar_token)