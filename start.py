import discord
from discord.ext import commands
import asyncio

from config import instar_token, category_name, seat_amount, channel_names, role_names

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

        if category_name in [c.name for c in ctx.guild.categories]:
            return

        guild_roles = ctx.guild.roles
        game_roles = []

        for role in role_names:
            for i in range(0, len(guild_roles)):
                if role == guild_roles[i].name:
                    await guild_roles[i].delete()
                    break
            
            game_roles.append( await ctx.guild.create_role(name=role) )

        await ctx.send("[Prepare server]")

        perms = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        
        game_category = await ctx.guild.create_category_channel(category_name, overwrites=perms, reason="For the game of UNO.")

        for i in range(0, seat_amount):
            channel_perms = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                game_roles[i]: discord.PermissionOverwrite(read_messages=True)
            }

            await game_category.create_text_channel(channel_names[i], overwrites=channel_perms)

    @uno.command(name="reset")
    async def _reset(self, ctx):
        guild_roles = ctx.guild.roles

        for role in role_names:
            for i in range(0, len(guild_roles)):
                if role == guild_roles[i].name:
                    await guild_roles[i].delete(reason="Reset")
                    break

        guild_channels = ctx.guild.text_channels

        for channel in channel_names:
            for i in range(0, len(guild_channels)):
                if channel == guild_channels[i].name:
                    await guild_channels[i].delete(reason="Reset")
                    break

        guild_categories = ctx.guild.categories

        for i in range(0, len(guild_categories)):
            if category_name == guild_categories[i].name:
                await guild_categories[i].delete(reason="Reset")
                break

        await ctx.send("Everything uno-related has been deleted!")

client = commands.Bot(command_prefix="i.", case_insensitive=True)

@client.event
async def on_ready():
    print("Connected and ready to play!")

client.add_cog(GameCog(client))
client.run(instar_token)