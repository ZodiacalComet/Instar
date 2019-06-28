import discord
from discord.ext import commands
import asyncio
import datetime

from config import instar_token, instar_info, category_name, seat_amount, channel_names, role_names, format_time

import Uno

class OccupiedUNOSeats(commands.CheckFailure):
    pass

def check_seats():
    async def predictate(ctx):
        category = discord.utils.get(ctx.guild.categories, name=category_name)

        if category:
            for channel in category.text_channels:
                msg = await channel.history().flatten()

                if len(msg) > 0:
                    raise OccupiedUNOSeats("There is already a game on progress right now! Wait until it ends")
        return True
    return commands.check(predictate)

class GameCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True, manage_emojis=True, manage_roles=True, manage_messages=True)
    @check_seats()
    async def start(self, ctx):
        user_lst = [ctx.author]
        join_msg = "join"

        # Join Stage

        await ctx.send(f"**{ctx.author}** has started a game of UNO, but they need at least two players.\n"
                        f"If you want to join this game, say `{join_msg}`.")

        for _ in range(1, seat_amount):
            def join_check(m):
                return m.content.lower() == join_msg and m.channel == ctx.channel and m.author not in user_lst

            try:
                r = await self.client.wait_for("message", check=join_check, timeout=30.0)
            except asyncio.TimeoutError:
                break
            else:
                user_lst.append(r.author)
                await ctx.send(f"**{r.author}** has joined the game!")

        if len(user_lst) < 2:
            await ctx.send("Seems like there is no one else that wants to play right now!")
            return

        # Preparation Stage

        wait_msg = await ctx.send("Wait while I prepare the game...")

        emoji_dict = {}
        gui_lst = []
        roles_lst = []

        async with ctx.channel.typing():
            for key, name in Uno.emojis.items():
                emoji = discord.utils.get(ctx.guild.emojis, name=name)
                if emoji:
                    emoji_dict[key] = str(emoji)

            channels_lst = discord.utils.get(ctx.guild.categories, name=category_name).text_channels

            for channel in channels_lst:
                await channel.send( Uno.game_help(emoji_dict) )
                gui_lst.append( await channel.send("[Placeholder]") )

            for name in role_names:
                role = discord.utils.get(ctx.guild.roles, name=name)
                roles_lst.append(role)

            UnoGame = Uno.Game(user_lst, channels_lst, gui_lst, roles_lst, emoji_dict)

            await Uno.update_gui(self.client, UnoGame)

            for user, role in UnoGame.player_roles():
                await user.add_roles(role, reason="To give access to their UNO seat.")
            
        cancel_game = False

        await wait_msg.edit(content="Game ready to start!")
        game_start_time = datetime.datetime.now()

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
                        await r.delete(delay=2.0)

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
                await player.channel.send("You lost your turn!", delete_after=5.0)

                if top_card.is_draw_two:
                    player.draw_card(2)

                if top_card.is_draw_four:
                    player.draw_card(4)

            if UnoGame.table.top_played_card.is_wild:
                wild_instruction = await player.channel.send( Uno.wild_help(emoji_dict) )

                while True:
                    try:
                        c = await self.client.wait_for("message", check=response_check, timeout=60.0)
                        color = c.content.lower()
                        await c.delete(delay=2.0)

                    except asyncio.TimeoutError:
                        cancel_game = True
                        break

                    else:
                        if UnoGame.table.top_played_card.change_color(color):
                            break
                        else:
                            await player.channel.send("That isn't a valid color!", delete_after=5.0)

                await wild_instruction.delete(delay=1.0)

            if UnoGame.table.top_played_card.do_reverse:
                UnoGame.reverse()

                for channel in channels_lst:
                    await channel.send(f"**{player.user}** has reversed the turns!", delete_after=5.0)

            if player.do_penalize():
                for channel in channels_lst:
                    await channel.send(f"**{player.user}** has been penalized for no calling UNO!", delete_after=5.0)

            if cancel_game:
                for channel in channels_lst:
                    await channel.send(f"Seems like **{player.user}** isn't there.\nThe game has been cancelled!")

                await ctx.send("The game has been cancelled!")
                break
            
            if player.hand_size == 0:
                for channel in channels_lst:
                    await channel.send(f"**{player.user}** doesn't have any cards left! **They won this game of UNO!**")

                game_time = datetime.datetime.now() - game_start_time
                await ctx.send(f"**{player.user}** has won the game of UNO!\nGame time: **{format_time(game_time.total_seconds())}**")
                break

            top_card.deactivate()

            UnoGame.next_turn()
            await Uno.update_gui(self.client, UnoGame)

    @start.before_invoke
    async def prepare_server(self, ctx):
        if category_name in [c.name for c in ctx.guild.categories]:
                return

        async with ctx.channel.typing():
            for name in Uno.emojis.values():
                with open(f"{name}.png", "rb") as image:
                    await ctx.guild.create_custom_emoji(name=name, image=image.read())
            
            game_roles = []

            for role in role_names:
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

    @start.after_invoke
    async def clean_up(self, ctx):
        await asyncio.sleep(5)
        
        category = discord.utils.get(ctx.guild.categories, name=category_name)

        for channel in category.text_channels:
            for user in channel.members:
                for role in user.roles:
                    if role.name in role_names:
                        await user.remove_roles(role, reason="Cleaning up")

            await channel.purge()

    @commands.command()
    @commands.has_permissions(manage_channels=True, manage_emojis=True, manage_roles=True)
    @commands.bot_has_permissions(manage_channels=True, manage_emojis=True, manage_roles=True)
    async def reset(self, ctx):
        async with ctx.channel.typing():
            for name in Uno.emojis.values():
                emoji = discord.utils.get(ctx.guild.emojis, name=name)
                if emoji:
                    await emoji.delete(reason="Reset")
            
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

    @commands.command()
    async def info(self, ctx):
        await ctx.send(instar_info)

client = commands.Bot(command_prefix="uno.", case_insensitive=True)

client.remove_command("help")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("uno.start | uno.reset | uno.info"))
    print("Connected and ready to play!")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, OccupiedUNOSeats):
        await ctx.send(error)

    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Yikes! Seems like I don't have the necessary permissions to do my work, sorry.\n"
                        + f"I'm missing the following permission{'s' if len(error.missing_perms) > 1 else ''}: "
                        + ", ".join([ f"`{perm.replace('_', ' ').title()}`" for perm in error.missing_perms ]) )

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You are not authorized to use that!")

    else:
        print(error)

@client.check
async def block_dms(ctx):
    return ctx.guild is not None

client.add_cog(GameCog(client))
client.run(instar_token)