import discord
from discord.ext import commands
import asyncio

from config import instar_token, category_name, seat_amount, channel_names, role_names, inverse_lst

import Uno
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
        user_lst = [ctx.author]
        join_msg = "join"

        await ctx.send(f"**{ctx.author}** has started a game of UNO, but they need at least two players.\n"
                        f"If you want to join this game, say `{join_msg}`.")

        for _ in range(0, seat_amount):
            def join_check(m):
                return m.content.lower() == join_msg and m.channel == ctx.channel #and m.author not in user_lst

            try:
                r = await self.client.wait_for("message", check=join_check, timeout=10.0)
            except asyncio.TimeoutError:
                break
            else:
                user_lst.append(r.author)
                await ctx.send(f"**{r.author}** has joined the game!")

        if len(user_lst) < 2:
            await ctx.send("Seems like there is no one else that wants to play right now!")
            return

        await ctx.send("Wait while I prepare the game...")

        channels_lst = []
        gui_lst = []
        roles_lst = []

        categories = ctx.guild.categories
        for i in range(0, len(categories)):
            if category_name == categories[i].name:
                channels_lst = categories[i].text_channels
                break

        for channel in channels_lst:
            gui_lst.append( await channel.send("Placeholder") )

        roles = ctx.guild.roles
        for i in range(0, len(roles)):
            if roles[i].name in role_names:
                roles_lst.append(roles[i])

        roles_lst = inverse_lst(roles_lst)

        UnoGame = Uno.Game(user_lst, channels_lst, gui_lst, roles_lst)

        async def update_gui(client, game_obj):
            for player in game_obj.players:
                await player.gui.edit(content="", embed= Uno.embed_gui(client, player) )

        await update_gui(self.client, UnoGame)

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