import discord
from discord.ext import commands
import asyncio

from config import instar_token

client = commands.Bot(command_prefix="i!", case_insensitive=True)

@client.event
async def on_ready():
    print("Connected and ready to play!")

client.run(instar_token)