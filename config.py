import json

# Getting the token from json file
with open("./token.json", "r") as f:
    json_data = json.load(f)

instar_token = json_data["token"]

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
