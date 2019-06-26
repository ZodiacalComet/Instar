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

        # Join Stage

        await ctx.send(f"**{ctx.author}** has started a game of UNO, but they need at least two players.\n"
                        f"If you want to join this game, say `{join_msg}`.")

        for _ in range(1, seat_amount):
            def join_check(m):
                return m.content.lower() == join_msg and m.channel == ctx.channel and m.author not in user_lst

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

        # Preparation Stage

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
            await channel.send(Uno.game_help_msg)
            gui_lst.append( await channel.send("Placeholder") )

        roles = ctx.guild.roles
        for i in range(0, len(roles)):
            if roles[i].name in role_names:
                roles_lst.append(roles[i])

        roles_lst = inverse_lst(roles_lst)

        UnoGame = Uno.Game(user_lst, channels_lst, gui_lst, roles_lst)

        await Uno.update_gui(self.client, UnoGame)

        for user, role in UnoGame.player_roles():
            await user.add_roles(role, reason="To give access to their UNO seat.")

        cancel_game = False

        # Game Phase

        while True:
            player = UnoGame.actual_player
            top_card = UnoGame.table.top_played_card
            
            def response_check(m):
                return m.channel == player.channel and m.author == player.user

            if not top_card.do_skip:
                await player.channel.send(f"It's your turn, **{player.user}**!", delete_after=10.0)

                while True:
                    try:
                        r = await self.client.wait_for("message", check=response_check, timeout=120.0)
                        response = r.content.lower()
                        await r.delete(delay=1.0)

                    except asyncio.TimeoutError:
                        cancel_game = True
                        break

                    else:
                        if response == Uno.uno_call_cmd and player.called_uno == False:
                            if player.call_uno():
                                for channel in channels_lst:
                                    await channel.send(f"**{player.user}** has called UNO!", delete_after=5.0)
                            else:
                                await player.channel.send("You can't call UNO right now!", delete_after=5.0)

                        elif player.play(response):
                            break

                        else:
                            await player.channel.send("Action invalid!", delete_after=5.0)
            else:

                if top_card.is_draw_two:
                    player.draw_card(2)

                if top_card.is_draw_four:
                    player.draw_card(4)

            if UnoGame.table.top_played_card.is_wild:
                wild_instruction = await player.channel.send(Uno.wild_help_msg)

                while True:
                    try:
                        c = await self.client.wait_for("message", check=response_check, timeout=60.0)
                        color = c.content.lower()
                        await c.delete(delay=1.0)

                    except asyncio.TimeoutError:
                        cancel_game = True
                        break

                    else:
                        if UnoGame.table.top_played_card.change_color(color):
                            break
                        else:
                            await player.channel.send("Action invalid!", delete_after=5.0)

                await wild_instruction.delete(delay=1.0)

            if player.do_penalize():
                for channel in channels_lst:
                    await channel.send(f"**{player.user}** has been penalized for no calling UNO!", delete_after=5.0)

            if cancel_game:
                for channel in channels_lst:
                    await channel.send(f"Seems like **{player.user}** isn't there.\nThe game has been canceled!", delete_after=5.0)
                break
            
            if player.hand_size == 0:
                for channel in channels_lst:
                    await channel.send(f"**{player.user}** doesn't have any cards left! **They won this game of UNO!**", delete_after=5.0)
                await ctx.send(f"**{player.user}** has won the game of UNO!")
                break

            top_card.deactivate()

            UnoGame.next_turn()
            await Uno.update_gui(self.client, UnoGame)

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

        await ctx.send("Everything UNO-related has been deleted!")

client = commands.Bot(command_prefix="i.", case_insensitive=True)

@client.event
async def on_ready():
    print("Connected and ready to play!")

client.add_cog(GameCog(client))
client.run(instar_token)