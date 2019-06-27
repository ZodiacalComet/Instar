import json

# Getting the token from json file
with open("./token.json", "r") as f:
    json_data = json.load(f)

instar_token = json_data["token"]

instar_info = """Hello, I'm Instar.
I was made with **Python 3.7.3** using the known API wrapper for Discord made by **Danny**, discord.py.
https://github.com/Rapptz/discord.py

The amateur programmer that thought he could do a game of UNO in a Discord Bot for the **Discord Hack Week #1** is the one that goes by the Discord tag of **ZodiacalComet#6636**. ~~So you now know who to search for to revolt against.~~

There is also some people that took a moment of their time to test if the mess of a code worked! And for that, my coder is grateful.

\t> Soon""".expandtabs(2)

# Uno Config
category_name = "UNO | Game"

seat_amount = 6
channel_names = [f"uno-seat-{numb}" for numb in range(1, seat_amount + 1)]
role_names = [f"{numb} | UNO Seat Access" for numb in range(1, seat_amount + 1)]

# Function

def format_time(seconds):
    out = ""

    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)

    if h > 0:
        out += f"{h}h"
    out += f"{m}m{s}s"

    return out
