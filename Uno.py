import random
import asyncio
import discord

class CardColor:
    red = "r"
    blue = "b"
    green = "g"
    yellow = "y"
    black = "black"

class CardType:
    reverse = "reverse"
    skip = "skip"
    draw_two = "draw two"

    wild = "wild"
    draw_four = "draw four"

draw_card_cmd = "draw"
uno_call_cmd = "uno"

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

emojis = {
    CardColor.red: "UNO_Red_Card",
    CardColor.blue: "UNO_Blue_Card",
    CardColor.green: "UNO_Green_Card",
    CardColor.yellow: "UNO_Yellow_Card",
    CardColor.black: "UNO_Black_Card",
    CardType.reverse: "UNO_Reverse_Icon",
    CardType.skip: "UNO_Skip_Icon",
    CardType.draw_two: "UNO_Draw_Two_Icon",
    CardType.draw_four: "UNO_Draw_Four_Icon",
    CardType.wild: "UNO_Wild_Icon"
}

def embed_gui(d_client, player_obj, game_obj):
    embed = discord.Embed(
        description = game_obj.turn_gui
    )

    embed.set_author(name="UNO Game", icon_url=d_client.user.avatar_url)
    embed.set_thumbnail(url=player_obj.user.avatar_url)
    embed.add_field(name="Table", value=f"{game_obj.table.top_played_card} - Cards left on deck: {game_obj.table.deck_size}", inline=False)
    embed.add_field(name="Your Hand", value=player_obj.gui_hand, inline=False)
    embed.set_footer(text=f"Of {player_obj.user}", icon_url=player_obj.user.avatar_url)

    if player_obj == game_obj.actual_player:
        embed.add_field(name="Play suggestions", value=player_obj.play_suggestions, inline=False)

    return embed

async def update_gui(client, game_obj):
    for player in game_obj.players:
        await player.gui.edit(content="", embed= embed_gui(client, player, game_obj) )

def game_help(emoji_dict):
    return f"""In order to play a card you need to send a message in the following format: `<color> <type>`.
**<color>:** Which can only be `{CardColor.red}` ({emoji_dict[CardColor.red] if CardColor.red in emoji_dict else CardColor.red}), `{CardColor.blue}` ({emoji_dict[CardColor.blue] if CardColor.blue in emoji_dict else CardColor.blue}), `{CardColor.green}` ({emoji_dict[CardColor.green] if CardColor.green in emoji_dict else CardColor.green}), `{CardColor.yellow}` ({emoji_dict[CardColor.yellow] if CardColor.yellow in emoji_dict else CardColor.yellow})
**<type>:** Just as it can be seen in your hand; `{numb_cards[5]}`, `{numb_cards[0]}`, `{numb_cards[9]}`. Where:
\t> {emoji_dict[CardType.reverse] if CardType.reverse in emoji_dict else CardType.reverse} is `{CardType.reverse}`
\t> {emoji_dict[CardType.skip] if CardType.skip in emoji_dict else CardType.skip} is `{CardType.skip}`
\t> {emoji_dict[CardType.wild] if CardType.wild in emoji_dict else CardType.wild} is `{CardType.wild}`
\t> {emoji_dict[CardType.draw_two] if CardType.draw_two in emoji_dict else CardType.draw_two} is `{CardType.draw_two}`
\t> {emoji_dict[CardType.draw_four] if CardType.draw_four in emoji_dict else CardType.draw_four} is `{CardType.draw_four}`

In the case of the wild cards ({emoji_dict[CardColor.black] if CardColor.black in emoji_dict else CardColor.black}) there is no need to specify `<color>`, so to play them you would use `{CardType.wild}` ({emoji_dict[CardType.wild] if CardType.wild in emoji_dict else CardType.wild}) and `{CardType.draw_four}` ({emoji_dict[CardType.draw_four] if CardType.draw_four in emoji_dict else CardType.draw_four}).

If you wish to draw a card, use `{draw_card_cmd}`, and if you want to call uno, use `{uno_call_cmd}`.""".expandtabs(2)

def wild_help(emoji_dict):
    return f"""You have placed a wild card ({emoji_dict[CardColor.black] if CardColor.black in emoji_dict else CardColor.black}) on the table, you now have to decide which of the following colors it'll convert to.
\t> `{CardColor.red}` for {emoji_dict[CardColor.red] if CardColor.red in emoji_dict else CardColor.red}
\t> `{CardColor.blue}` for {emoji_dict[CardColor.blue] if CardColor.blue in emoji_dict else CardColor.blue}
\t> `{CardColor.green}` for {emoji_dict[CardColor.green] if CardColor.green in emoji_dict else CardColor.green}
\t> `{CardColor.yellow}` for {emoji_dict[CardColor.yellow] if CardColor.yellow in emoji_dict else CardColor.yellow}""".expandtabs(2)

class Card:
    "UNO Card Controller"
    def __init__(self, c_type, c_color, player_amt, emoji_dict):
        self.type = c_type
        self.color = c_color
        self.player_amt = player_amt
        self.emoji_dict = emoji_dict

        self.do_reverse = True if self.type == CardType.reverse else False
        self.is_draw_two = True if self.type == CardType.draw_two else False
        self.is_draw_four = True if self.type == CardType.draw_four else False

        self.do_skip = True if self.type in [CardType.skip, CardType.draw_two, CardType.draw_four] else False

        if self.type == CardType.reverse and self.player_amt == 2:
            self.do_skip = True

    @property
    def is_wild(self):
        return True if self.color == CardColor.black else False

    def change_color(self, color):
        if color in color_cards:
            self.color = color
            return True
        return False

    def deactivate(self):
        self.do_skip = False
        self.do_reverse = False

    def reset(self):
        if self.type == CardType.reverse:
            self.do_reverse = True
        if self.type in [CardType.skip, CardType.draw_two, CardType.draw_four]:
            self.do_skip = True
        if self.type in [CardType.wild, CardType.draw_four]:
            self.color = CardColor.black
        if self.type == CardType.reverse and self.player_amt == 2:
            self.do_skip = True

    @property
    def play_cmd(self):
        if self.color == CardColor.black:
            return f"{self.type}"
        return f"{self.color} {self.type}"

    def __str__(self):
        return f"{self.emoji_dict[self.color] if self.color in self.emoji_dict else self.color} {self.emoji_dict[self.type] if self.type in self.emoji_dict else self.type}"

class Table:
    "UNO Table Controller"
    def __init__(self, player_amt, emoji_dict):
        self.deck = []
        self.played_cards = []

        for color in color_cards:
            for numb in numb_cards:
                self.deck.append( Card(numb, color, player_amt, emoji_dict) )

            for special in special_cards:
                self.deck.append( Card(special, color, player_amt, emoji_dict) )

        for wild in wild_cards:
            self.deck.append( Card(wild, CardColor.black, player_amt, emoji_dict) )

        for _ in range(0, random.randint(4, 8) ):
            random.shuffle(self.deck)

        for i in range(0, len(self.deck)):
            if self.deck[i].type in numb_cards:
                self.played_cards.append(self.deck[i])
                self.deck.pop(i)
                break

    @property
    def top_played_card(self):
        return self.played_cards[0]

    @property
    def deck_size(self):
        return len(self.deck)

    def reshuffle(self):
        for _ in range(1, len(self.played_cards) ):
            self.played_cards[1].reset()
            self.deck.append( self.played_cards[1] )
            self.played_cards.pop(1)

        for _ in range(0, random.randint(4, 8) ):
            random.shuffle(self.deck)

    def place_card(self, card):
        self.played_cards.insert(0, card)

    def can_draw_play(self):
        return self.deck[0].color == self.top_played_card.color or self.deck[0].type == self.top_played_card.type or self.deck[0].color == CardColor.black

    def draw_play(self):
        self.place_card( self.deck[0] )
        self.deck.pop(0)

        if self.deck_size == 0:
            self.reshuffle()

class Player:
    "UNO Player Controller"
    def __init__(self, user, gui, channel, role, table_ref, emoji_dict):
        self.user = user
        self.gui = gui
        self.channel = channel
        self.role = role
        self.table = table_ref
        self.emoji_dict = emoji_dict

        self.hand = []
        self.called_uno = False

        for _ in range(0, 7):
            self.hand.append( self.table.deck[0] )
            self.table.deck.pop(0)

    @property
    def hand_size(self):
        return len(self.hand)

    @property
    def gui_hand(self):
        h = []
        
        for color in [CardColor.red, CardColor.blue, CardColor.green, CardColor.yellow, CardColor.black]:
            l = []

            for card in self.hand:
                if card.color == color:
                    l.append(self.emoji_dict[card.type] if card.type in self.emoji_dict else card.type)

            if len(l) > 0:
                h.append( f"{self.emoji_dict[color] if color in self.emoji_dict else color}: " + ", ".join(l) )

        return "\n".join(h)

    @property
    def play_suggestions(self):
        s = []

        for card in self.hand:
            if len(s) > 9:
                break
            
            if card.color == self.table.top_played_card.color or card.type == self.table.top_played_card.type or card.color == CardColor.black:
                s.append( card.play_cmd )

        if len(s) == 0:
            return f"You cannot play any of your cards, use `{draw_card_cmd}` to get a new one."

        return " | ".join([ f"`{cmd}`" for cmd in s ])

    def draw_card(self, amount=1):
        for _ in range(0, amount):
            self.hand.append(self.table.deck[0])
            self.table.deck.pop(0)

            if self.table.deck_size == 0:
                self.table.reshuffle()

        self.called_uno = False if self.called_uno == True else False

    def call_uno(self):
        if self.hand_size == 2:
            for card in self.hand:
                if card.type == self.table.top_played_card.type or card.color == self.table.top_played_card.color or card.color == CardColor.black:
                    self.called_uno = True
                    return True
        return False

    def do_penalize(self):
        if self.hand_size == 1 and self.called_uno == False:
            self.draw_card(3)
            return True
        return False

    def play(self, cmd):
        if cmd == draw_card_cmd:
            if self.table.can_draw_play():
                self.table.draw_play()
            else:
                self.draw_card()
            return True

        for i in range(0, len(self.hand)):
            if cmd == self.hand[i].play_cmd:
                if self.hand[i].color == self.table.top_played_card.color or self.hand[i].type == self.table.top_played_card.type or self.hand[i].color == CardColor.black:
                    self.table.place_card(self.hand[i])
                    self.hand.pop(i)
                    return True
        return False

class Game:
    "UNO Master Class"
    def __init__(self, user_lst, channel_lst, gui_lst, role_lst, emoji_dict):
        self.players = []
        self.table = Table(len(user_lst), emoji_dict)

        self.current_index = 0
        self.max_index = len(user_lst) - 1
        self.is_reverse = False

        for i in range(0, len(user_lst)):
            self.players.append( Player(user_lst[i], gui_lst[i], channel_lst[i], role_lst[i], self.table, emoji_dict) )

    def player_roles(self):
        return [ (player.user, player.role) for player in self.players ]

    @property
    def actual_player(self):
        return self.players[self.current_index]

    @property
    def turn_gui(self):
        t = []

        for i in range(0, len(self.players)):
            b = "**" if i == self.current_index else ""
            t.append(f"{b}{self.players[i].user} ({self.players[i].hand_size}){b}")

        sep = "<" if self.is_reverse else ">"
        return f" {sep} ".join(t)

    def reverse(self):
        self.is_reverse = True if not self.is_reverse else False

    def next_turn(self):
        if self.is_reverse:
            self.current_index -= 1
        else:
            self.current_index += 1

        if self.current_index > self.max_index:
            self.current_index = 0
        elif self.current_index < 0:
            self.current_index = self.max_index
