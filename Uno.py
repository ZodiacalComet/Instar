import random
import asyncio
import discord

class CardColor:
    red = "r"
    blue = "b"
    green = "g"
    yellow = "y"
    black = "b"

class CardType:
    reverse = "reverse"
    skip = "skip"
    draw_two = "draw two"

    wild = "wild"
    draw_four = "draw four"

color_cards = [
    CardColor.red,
    CardColor.blue,
    CardColor.green,
    CardColor.yellow
]

numb_cards = [ str(numb) for numb in range(0, 10) ]
numb_cards.extend(numb_cards)

special_cards = [
    CardType.reverse,
    CardType.skip,
    CardType.draw_two
]

special_cards.extend(special_cards)

wild_cards = [
    CardType.wild,
    CardType.draw_four
]

for _ in range(0,2):
    wild_cards.extend(wild_cards)

def embed_gui(d_client, player_obj):
    embed = discord.Embed(
        description = "Empty"
    )

    embed.set_author(name="UNO GUI", icon_url=d_client.user.avatar_url)
    embed.set_thumbnail(url=player_obj.user.avatar_url)
    embed.add_field(name="Table", value="Empty", inline=False)
    embed.add_field(name="Your Hand", value=player_obj.gui_hand, inline=False)
    embed.set_footer(text=f"Of {player_obj.user}", icon_url=player_obj.user.avatar_url)

    return embed

class Card:
    "UNO Card Controller"
    def __init__(self, c_type, c_color, player_amt):
        self.type = c_type
        self.color = c_color

    def __str__(self):
        return f"{self.color} {self.type}"

class Table:
    "UNO Table Controller"
    def __init__(self, player_amt):
        self.deck = []
        self.played_cards = []

        for color in color_cards:
            for numb in numb_cards:
                self.deck.append( Card(numb, color, player_amt) )

            for special in special_cards:
                self.deck.append( Card(special, color, player_amt) )

        for wild in wild_cards:
            self.deck.append( Card(wild, CardColor.black, player_amt) )

        for _ in range(0, random.randint(4, 8) ):
            random.shuffle(self.deck)

        for i in range(0, len(self.deck)):
            if self.deck[i].type in numb_cards:
                self.played_cards.append(self.deck[i])
                self.deck.pop(i)
                break

class Player:
    "UNO Player Controller"
    def __init__(self, user, gui, channel, role, table_ref):
        self.user = user
        self.gui = gui
        self.channel = channel
        self.role = role
        self.table = table_ref

        self.hand = []

        for _ in range(0, 7):
            self.hand.append( self.table.deck[0] )
            self.table.deck.pop(0)

    @property
    def gui_hand(self):
        return [ str(card) for card in self.hand ]

class Game:
    "UNO Master Class"
    def __init__(self, user_lst, channel_lst, gui_lst, role_lst):
        self.players = []
        self.table = Table(len(user_lst))

        for i in range(0, len(user_lst)):
            self.players.append( Player(user_lst[i], gui_lst[i], channel_lst[i], role_lst[i], self.table) )